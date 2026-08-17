"""Native-resolution metric figures for focused Drill-Down evidence.

The focused metric panels deliberately do not reuse the selected-station
temporal-density recipe. One plotted point remains one retained scientific
evidence unit: a successful Performance opportunity, a simultaneous Joint
Spot, or a complete sequential Scheduled Pair. The companion outcome and
coverage figures keep their established aggregation and are adapted only to a
single chronological column.
"""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
import math

import matplotlib.dates as mdates
from matplotlib.artist import Artist
from matplotlib.transforms import blended_transform_factory
import numpy as np
import pandas as pd

from config import APP_VERSION
from core.evidence_statistics import _expanded_metric_limits
from core.matplotlib_runtime import create_agg_figure, synchronized_matplotlib
from ui.inspector.outlier_candidates import DELTA_SNR_OUTLIER_MAD_NORMALIZATION
from ui.plots.benchmark_evidence_figures import (
    render_selected_compare_coverage_export_figure,
)
from ui.plots.evidence_figures import (
    DELTA_SNR_OUTLIER_MARKER_SIZE,
    DELTA_SNR_OUTLIER_MARKER_ZORDER,
    METRIC_FIGURE_TITLE_FONTSIZE,
    METRIC_FONT_FAMILY,
    METRIC_FOOTER_FONTSIZE,
    _add_reference_snr_correction_footer,
    _apply_delta_snr_outlier_marker_style,
    _figure_footer_y,
    _figure_height_for_reference_correction,
    _place_metric_legend_top_right,
    _set_metric_axis_labels,
    _set_temporal_panel_title,
    _shift_figure_y_above_added_footer,
    _style_evidence_axis,
    render_segment_temporal_evidence_export_figure,
)
from ui.plots.temporal_layout import draw_temporal_unavailable_annotation


DRILLDOWN_ZOOM_FIGURE_LAYOUT_VERSION = 4
DRILLDOWN_ZOOM_NATIVE_RECIPE_SCHEMA_VERSION = 2
DRILLDOWN_ZOOM_OUTLIER_OVERLAY_SCHEMA_VERSION = 2

DRILLDOWN_ZOOM_PERFORMANCE_NATIVE_KIND = (
    "drilldown_zoom_performance_native_snr"
)
DRILLDOWN_ZOOM_BENCHMARK_NATIVE_KIND = (
    "drilldown_zoom_benchmark_native_delta_snr"
)
DRILLDOWN_ZOOM_NATIVE_RESOLUTION = "native-evidence-unit"
DRILLDOWN_ZOOM_NO_AGGREGATION = "none"

_NATIVE_RECIPE_KINDS = {
    DRILLDOWN_ZOOM_PERFORMANCE_NATIVE_KIND,
    DRILLDOWN_ZOOM_BENCHMARK_NATIVE_KIND,
}
_OUTLIER_OVERLAY_LABEL_FIELDS = {
    "marker",
    "focused_episode",
    "local_baseline",
    "flank_baseline",
    "robust_z",
    "qualifying_robust_z",
    "absolute_departure",
}
_NATIVE_FIGURE_CORRECTION_FOOTER_HEIGHT_INCHES = 0.3
_NATIVE_POINT_FACE_COLOR = "#c8f4ff"
_NATIVE_POINT_EDGE_COLOR = "#00384d"
_LOCAL_BASELINE_COLOR = "#ff5a5a"
_FLANK_BASELINE_COLOR = "#f4f7f8"
_ROBUST_Z_GUIDE_COLOR = "#ef5350"
_ROBUST_Z_GUIDE_ALPHA = 0.66
_ROBUST_Z_GUIDE_LINEWIDTH = 0.85
_ROBUST_Z_GUIDE_FONTSIZE = 9.5
_ABSOLUTE_DEPARTURE_COLOR = "#7ed957"
_ABSOLUTE_DEPARTURE_FONTSIZE = 9.5
_FOCUSED_EPISODE_FACE_COLOR = "#78909c"
_FOCUSED_EPISODE_ALPHA = 0.16
_FOCUSED_EPISODE_ZORDER = 0.6


def _artist_gid(artist: Artist) -> str:
    gid = artist.get_gid()
    return str(gid or "")


def _normalized_utc_timestamp(value, *, field: str) -> pd.Timestamp:
    """Return one timezone-aware UTC timestamp with a field-specific error."""
    try:
        timestamp = pd.Timestamp(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be a valid UTC timestamp.") from exc
    if pd.isna(timestamp):
        raise ValueError(f"{field} must be a valid UTC timestamp.")
    if timestamp.tzinfo is None:
        return timestamp.tz_localize("UTC")
    return timestamp.tz_convert("UTC")


def _normalized_window(start_utc, end_utc) -> tuple[pd.Timestamp, pd.Timestamp]:
    start = _normalized_utc_timestamp(start_utc, field="start_utc")
    end = _normalized_utc_timestamp(end_utc, field="end_utc")
    if end <= start:
        raise ValueError("Focused Drill-Down UTC bounds must define a positive window.")
    return start, end


def _required_text(value, *, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field} must be non-empty.")
    return text


def _finite_float(value, *, field: str, positive: bool = False) -> float:
    try:
        numeric_value = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be finite.") from exc
    if not math.isfinite(numeric_value) or (positive and numeric_value <= 0.0):
        qualifier = "positive and finite" if positive else "finite"
        raise ValueError(f"{field} must be {qualifier}.")
    return numeric_value


def _native_point_recipe(
    *,
    kind: str,
    point_times_utc,
    point_metrics_db,
    start_utc,
    end_utc,
    title,
    panel_title,
    x_label,
    y_label,
    empty_text,
    evidence_unit_label,
    evidence_unit_kind: str,
    reference_snr_correction_notice="",
    outlier_overlay=None,
) -> dict[str, object]:
    """Validate and own one unaggregated focused metric recipe."""
    if kind not in _NATIVE_RECIPE_KINDS:
        raise ValueError("Focused Drill-Down native recipe kind is unsupported.")
    window_start, window_end = _normalized_window(start_utc, end_utc)
    times = pd.Series(
        pd.to_datetime(point_times_utc, errors="coerce", utc=True),
        copy=False,
    ).astype("datetime64[ns, UTC]")
    metrics = pd.to_numeric(
        pd.Series(point_metrics_db, copy=False),
        errors="coerce",
    ).to_numpy(dtype=np.float64, copy=False)
    if len(times) != len(metrics):
        raise ValueError("Focused Drill-Down point UTC and metric arrays must align.")

    time_nanoseconds = times.astype("int64").to_numpy(
        dtype=np.int64,
        copy=False,
    )
    finite_mask = (
        ~np.asarray(pd.isna(times), dtype=bool)
        & np.isfinite(metrics)
        & (time_nanoseconds >= int(window_start.value))
        & (time_nanoseconds < int(window_end.value))
    )
    time_nanoseconds = time_nanoseconds[finite_mask]
    metrics = metrics[finite_mask]
    if len(time_nanoseconds):
        stable_order = np.argsort(time_nanoseconds, kind="stable")
        time_nanoseconds = time_nanoseconds[stable_order]
        metrics = metrics[stable_order]

    if outlier_overlay is not None:
        _validated_outlier_overlay(outlier_overlay)
    return {
        "kind": kind,
        "schema_version": DRILLDOWN_ZOOM_NATIVE_RECIPE_SCHEMA_VERSION,
        "layout_version": DRILLDOWN_ZOOM_FIGURE_LAYOUT_VERSION,
        "resolution": DRILLDOWN_ZOOM_NATIVE_RESOLUTION,
        "aggregation": DRILLDOWN_ZOOM_NO_AGGREGATION,
        "time_bin": "native",
        "start_utc_ns": int(window_start.value),
        "end_utc_ns": int(window_end.value),
        "point_utc_ns": np.asarray(time_nanoseconds, dtype=np.int64).copy(),
        "metric_db": np.asarray(metrics, dtype=np.float64).copy(),
        "point_count": int(len(metrics)),
        "evidence_unit_kind": _required_text(
            evidence_unit_kind,
            field="evidence_unit_kind",
        ),
        "title": _required_text(title, field="title"),
        "panel_title": _required_text(panel_title, field="panel_title"),
        "x_label": _required_text(x_label, field="x_label"),
        "y_label": _required_text(y_label, field="y_label"),
        "empty_text": _required_text(empty_text, field="empty_text"),
        "evidence_unit_label": _required_text(
            evidence_unit_label,
            field="evidence_unit_label",
        ),
        "reference_snr_correction_notice": str(
            reference_snr_correction_notice or ""
        ),
        "outlier_overlay": (
            deepcopy(dict(outlier_overlay))
            if outlier_overlay is not None
            else None
        ),
    }


def build_drilldown_zoom_performance_snr_recipe(
    selected_station_rows,
    *,
    start_utc,
    end_utc,
    title,
    panel_title,
    x_label,
    y_label,
    empty_text,
    evidence_unit_label,
) -> dict[str, object]:
    """Build one exact-cycle Performance SNR recipe from retained rows.

    A point is retained only when the canonical opportunity row is successful
    and carries a finite normalized Target SNR. Misses have no Target SNR and
    remain represented by the separate chronological outcome figure.
    """
    if selected_station_rows is None or selected_station_rows.empty:
        time_slots = pd.Series(dtype="float64")
        target_snr = pd.Series(dtype="float64")
    else:
        required_columns = {"time_slot", "hit", "target_snr"}
        if not required_columns.issubset(selected_station_rows.columns):
            missing = sorted(required_columns - set(selected_station_rows.columns))
            raise ValueError(
                "Focused Performance evidence is missing required columns: "
                + ", ".join(missing)
            )
        numeric_slots = pd.to_numeric(
            selected_station_rows["time_slot"], errors="coerce"
        )
        numeric_hits = pd.to_numeric(
            selected_station_rows["hit"], errors="coerce"
        )
        numeric_snr = pd.to_numeric(
            selected_station_rows["target_snr"], errors="coerce"
        )
        successful_mask = (
            numeric_slots.notna()
            & np.isfinite(numeric_slots)
            & numeric_slots.eq(np.floor(numeric_slots))
            & numeric_hits.gt(0)
            & numeric_snr.notna()
            & np.isfinite(numeric_snr)
        )
        time_slots = numeric_slots.loc[successful_mask].astype("int64")
        target_snr = numeric_snr.loc[successful_mask]
    cycle_times = pd.to_datetime(
        time_slots.to_numpy(dtype=np.int64, copy=False) * 120,
        unit="s",
        utc=True,
    )
    recipe = _native_point_recipe(
        kind=DRILLDOWN_ZOOM_PERFORMANCE_NATIVE_KIND,
        point_times_utc=cycle_times,
        point_metrics_db=target_snr,
        start_utc=start_utc,
        end_utc=end_utc,
        title=title,
        panel_title=panel_title,
        x_label=x_label,
        y_label=y_label,
        empty_text=empty_text,
        evidence_unit_label=evidence_unit_label,
        evidence_unit_kind="successful_opportunity",
    )
    recipe["snr_title"] = recipe["title"]
    return recipe


def build_drilldown_zoom_benchmark_delta_snr_recipe(
    evidence_df,
    *,
    start_utc,
    end_utc,
    title,
    panel_title,
    x_label,
    y_label,
    empty_text,
    evidence_unit_label,
    is_sequential,
    reference_snr_correction_notice="",
    outlier_overlay=None,
) -> dict[str, object]:
    """Build one native Joint-Spot or Scheduled-Pair Delta-SNR recipe."""
    if evidence_df is None or evidence_df.empty:
        plot_times = pd.Series(dtype="datetime64[ns, UTC]")
        metric_db = pd.Series(dtype="float64")
    else:
        required_columns = {"plot_time", "metric"}
        if not required_columns.issubset(evidence_df.columns):
            missing = sorted(required_columns - set(evidence_df.columns))
            raise ValueError(
                "Focused Benchmark evidence is missing required columns: "
                + ", ".join(missing)
            )
        plot_times = evidence_df["plot_time"]
        metric_db = evidence_df["metric"]
    return _native_point_recipe(
        kind=DRILLDOWN_ZOOM_BENCHMARK_NATIVE_KIND,
        point_times_utc=plot_times,
        point_metrics_db=metric_db,
        start_utc=start_utc,
        end_utc=end_utc,
        title=title,
        panel_title=panel_title,
        x_label=x_label,
        y_label=y_label,
        empty_text=empty_text,
        evidence_unit_label=evidence_unit_label,
        evidence_unit_kind=(
            "complete_scheduled_pair" if is_sequential else "joint_spot"
        ),
        reference_snr_correction_notice=reference_snr_correction_notice,
        outlier_overlay=outlier_overlay,
    )


def _optional_utc_interval(
    start_utc,
    end_utc,
    *,
    field: str,
) -> tuple[int, int] | None:
    if start_utc is None and end_utc is None:
        return None
    if start_utc is None or end_utc is None:
        raise ValueError(f"{field} requires both UTC bounds.")
    start = _normalized_utc_timestamp(start_utc, field=f"{field}_start_utc")
    end = _normalized_utc_timestamp(end_utc, field=f"{field}_end_utc")
    if end < start:
        raise ValueError(f"{field} end must not precede its start.")
    return int(start.value), int(end.value)


def _normalized_outlier_marker_arrays(
    marker_times_utc,
    marker_delta_snr_db,
) -> tuple[np.ndarray, np.ndarray]:
    """Validate, order, and own exact qualifying-unit marker coordinates."""
    try:
        times = pd.Series(
            pd.to_datetime(marker_times_utc, errors="coerce", utc=True),
            copy=False,
        ).astype("datetime64[ns, UTC]")
        metrics = pd.to_numeric(
            pd.Series(marker_delta_snr_db, copy=False),
            errors="coerce",
        ).to_numpy(dtype=np.float64, copy=False)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "Qualifying outlier marker coordinates must be one-dimensional."
        ) from exc
    if len(times) != len(metrics):
        raise ValueError(
            "Qualifying outlier marker UTC and Delta-SNR arrays must align."
        )
    if bool(pd.isna(times).any()) or not np.isfinite(metrics).all():
        raise ValueError("Qualifying outlier marker coordinates must be finite.")

    time_nanoseconds = times.astype("int64").to_numpy(
        dtype=np.int64,
        copy=False,
    )
    stable_order = np.argsort(time_nanoseconds, kind="stable")
    time_nanoseconds = time_nanoseconds[stable_order]
    metrics = metrics[stable_order]
    coordinates = list(zip(time_nanoseconds.tolist(), metrics.tolist()))
    if len(set(coordinates)) != len(coordinates):
        raise ValueError("Qualifying outlier marker coordinates must be unique.")
    return time_nanoseconds.copy(), metrics.copy()


def build_drilldown_zoom_outlier_overlay_recipe(
    *,
    representative_utc,
    representative_delta_snr_db,
    qualifying_marker_times_utc,
    qualifying_marker_delta_snr_db,
    candidate_start_utc,
    candidate_end_utc,
    native_evidence_unit_minutes,
    local_baseline_db,
    pre_baseline_db,
    post_baseline_db,
    pre_flank_start_utc,
    pre_flank_end_utc,
    post_flank_start_utc,
    post_flank_end_utc,
    robust_spread_db,
    robust_spread_method,
    minimum_robust_z,
    minimum_departure_db,
    labels,
) -> dict[str, object]:
    """Build exact markers, focus band, and guides for one focused episode.

    ``robust_spread_db`` is the detector's MAD-like scale. Modified robust-z
    boundaries therefore use ``spread * |z| / 0.6745``. They are descriptive
    detector guides, not confidence intervals or probability bands. Every
    supplied qualifying native unit is stored as an identically styled marker.
    The episode band adds half one native-unit width on either side purely for
    visibility; the renderer clips it to the Drill-Down window, so this visual
    padding does not redefine the detector's reported event duration.
    """
    representative = _normalized_utc_timestamp(
        representative_utc, field="representative_utc"
    )
    candidate_start = _normalized_utc_timestamp(
        candidate_start_utc, field="candidate_start_utc"
    )
    candidate_end = _normalized_utc_timestamp(
        candidate_end_utc, field="candidate_end_utc"
    )
    if candidate_end <= candidate_start:
        raise ValueError("Outlier candidate bounds must define a positive interval.")
    if not candidate_start <= representative < candidate_end:
        raise ValueError(
            "Outlier representative UTC must fall inside its candidate interval."
        )
    baseline_db = _finite_float(local_baseline_db, field="local_baseline_db")
    pre_baseline = _finite_float(pre_baseline_db, field="pre_baseline_db")
    post_baseline = _finite_float(post_baseline_db, field="post_baseline_db")
    marker_db = _finite_float(
        representative_delta_snr_db, field="representative_delta_snr_db"
    )
    marker_times_ns, marker_metrics_db = _normalized_outlier_marker_arrays(
        qualifying_marker_times_utc,
        qualifying_marker_delta_snr_db,
    )
    native_unit_minutes = _finite_float(
        native_evidence_unit_minutes,
        field="native_evidence_unit_minutes",
        positive=True,
    )
    native_unit_width_ns = int(
        round(native_unit_minutes * pd.Timedelta(minutes=1).value)
    )
    if native_unit_width_ns <= 0:
        raise ValueError("Native evidence-unit width must be positive.")
    spread_db = _finite_float(
        robust_spread_db, field="robust_spread_db", positive=True
    )
    robust_z_threshold = _finite_float(
        minimum_robust_z, field="minimum_robust_z", positive=True
    )
    departure_db = _finite_float(
        minimum_departure_db, field="minimum_departure_db", positive=True
    )
    method = _required_text(
        robust_spread_method, field="robust_spread_method"
    )
    if not isinstance(labels, Mapping):
        raise ValueError("Outlier overlay labels must be a mapping.")
    missing_labels = _OUTLIER_OVERLAY_LABEL_FIELDS - set(labels)
    if missing_labels:
        raise ValueError(
            "Outlier overlay labels are missing: "
            + ", ".join(sorted(missing_labels))
        )
    normalized_labels = {
        field: _required_text(labels[field], field=f"labels.{field}")
        for field in _OUTLIER_OVERLAY_LABEL_FIELDS
    }

    standard_z_values = [1.0, 2.0, 3.0]
    matching_standard_z = next(
        (
            z_value
            for z_value in standard_z_values
            if math.isclose(
                z_value,
                robust_z_threshold,
                rel_tol=0.0,
                abs_tol=1e-12,
            )
        ),
        None,
    )
    threshold_guide_z = (
        matching_standard_z
        if matching_standard_z is not None
        else robust_z_threshold
    )
    unique_z_values = sorted(
        standard_z_values
        + ([] if matching_standard_z is not None else [robust_z_threshold])
    )
    guide_boundaries = []
    for z_value in unique_z_values:
        offset_db = spread_db * z_value / DELTA_SNR_OUTLIER_MAD_NORMALIZATION
        is_threshold = math.isclose(
            z_value,
            threshold_guide_z,
            rel_tol=0.0,
            abs_tol=1e-12,
        )
        guide_template = normalized_labels[
            "qualifying_robust_z" if is_threshold else "robust_z"
        ]
        guide_boundaries.append(
            {
                "robust_z": float(z_value),
                "offset_db": float(offset_db),
                "lower_db": float(baseline_db - offset_db),
                "upper_db": float(baseline_db + offset_db),
                "is_qualification_threshold": is_threshold,
                "label": guide_template.format(value=z_value),
            }
        )

    pre_interval = _optional_utc_interval(
        pre_flank_start_utc, pre_flank_end_utc, field="pre_flank"
    )
    post_interval = _optional_utc_interval(
        post_flank_start_utc, post_flank_end_utc, field="post_flank"
    )
    return {
        "schema_version": DRILLDOWN_ZOOM_OUTLIER_OVERLAY_SCHEMA_VERSION,
        "normalization": float(DELTA_SNR_OUTLIER_MAD_NORMALIZATION),
        "representative_utc_ns": int(representative.value),
        "representative_delta_snr_db": marker_db,
        "qualifying_marker_utc_ns": marker_times_ns,
        "qualifying_marker_delta_snr_db": marker_metrics_db,
        "qualifying_marker_count": int(len(marker_times_ns)),
        "candidate_start_utc_ns": int(candidate_start.value),
        "candidate_end_utc_ns": int(candidate_end.value),
        "native_evidence_unit_width_ns": native_unit_width_ns,
        "focused_episode_visual_start_utc_ns": int(
            candidate_start.value - native_unit_width_ns // 2
        ),
        "focused_episode_visual_end_utc_ns": int(
            candidate_end.value
            - 1
            + (native_unit_width_ns - native_unit_width_ns // 2)
        ),
        "local_baseline_db": baseline_db,
        "pre_baseline_db": pre_baseline,
        "post_baseline_db": post_baseline,
        "pre_flank_utc_ns": pre_interval,
        "post_flank_utc_ns": post_interval,
        "robust_spread_db": spread_db,
        "robust_spread_method": method,
        "minimum_robust_z": robust_z_threshold,
        "minimum_departure_db": departure_db,
        "robust_z_guides": tuple(guide_boundaries),
        "absolute_departure_lower_db": float(baseline_db - departure_db),
        "absolute_departure_upper_db": float(baseline_db + departure_db),
        "labels": normalized_labels,
    }


def _validated_outlier_overlay(overlay) -> Mapping:
    """Validate renderer-facing detector guides, including their exact math."""
    if not isinstance(overlay, Mapping):
        raise ValueError("Focused outlier overlay must be a mapping.")
    if overlay.get("schema_version") != (
        DRILLDOWN_ZOOM_OUTLIER_OVERLAY_SCHEMA_VERSION
    ):
        raise ValueError("Unsupported focused outlier overlay schema.")
    normalization = _finite_float(
        overlay.get("normalization"),
        field="outlier_overlay.normalization",
        positive=True,
    )
    if not math.isclose(
        normalization,
        DELTA_SNR_OUTLIER_MAD_NORMALIZATION,
        rel_tol=0.0,
        abs_tol=1e-12,
    ):
        raise ValueError("Focused outlier overlay robust-z normalization changed.")
    baseline_db = _finite_float(
        overlay.get("local_baseline_db"),
        field="outlier_overlay.local_baseline_db",
    )
    spread_db = _finite_float(
        overlay.get("robust_spread_db"),
        field="outlier_overlay.robust_spread_db",
        positive=True,
    )
    minimum_robust_z = _finite_float(
        overlay.get("minimum_robust_z"),
        field="outlier_overlay.minimum_robust_z",
        positive=True,
    )
    departure_db = _finite_float(
        overlay.get("minimum_departure_db"),
        field="outlier_overlay.minimum_departure_db",
        positive=True,
    )
    for field in (
        "representative_delta_snr_db",
        "pre_baseline_db",
        "post_baseline_db",
    ):
        _finite_float(overlay.get(field), field=f"outlier_overlay.{field}")
    try:
        representative_ns = int(overlay["representative_utc_ns"])
        candidate_start_ns = int(overlay["candidate_start_utc_ns"])
        candidate_end_ns = int(overlay["candidate_end_utc_ns"])
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        raise ValueError("Focused outlier overlay UTC values are invalid.") from exc
    if not candidate_start_ns <= representative_ns < candidate_end_ns:
        raise ValueError("Focused outlier representative must lie in its interval.")
    try:
        marker_times_ns = np.asarray(
            overlay["qualifying_marker_utc_ns"],
            dtype=np.int64,
        )
        marker_metrics_db = np.asarray(
            overlay["qualifying_marker_delta_snr_db"],
            dtype=np.float64,
        )
        marker_count = int(overlay["qualifying_marker_count"])
        native_unit_width_ns = int(overlay["native_evidence_unit_width_ns"])
        visual_start_ns = int(overlay["focused_episode_visual_start_utc_ns"])
        visual_end_ns = int(overlay["focused_episode_visual_end_utc_ns"])
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        raise ValueError(
            "Focused outlier marker or episode-band values are invalid."
        ) from exc
    if (
        marker_times_ns.ndim != 1
        or marker_metrics_db.ndim != 1
        or len(marker_times_ns) != len(marker_metrics_db)
        or len(marker_times_ns) != marker_count
        or marker_count < 0
        or not np.isfinite(marker_metrics_db).all()
        or np.any(np.diff(marker_times_ns) < 0)
    ):
        raise ValueError("Focused qualifying-unit marker arrays are invalid.")
    marker_coordinates = list(
        zip(marker_times_ns.tolist(), marker_metrics_db.tolist())
    )
    if len(set(marker_coordinates)) != len(marker_coordinates):
        raise ValueError(
            "Focused qualifying-unit marker coordinates must be unique."
        )
    if native_unit_width_ns <= 0:
        raise ValueError("Focused native evidence-unit width must be positive.")
    expected_visual_start_ns = candidate_start_ns - native_unit_width_ns // 2
    expected_visual_end_ns = (
        candidate_end_ns
        - 1
        + (native_unit_width_ns - native_unit_width_ns // 2)
    )
    if (
        visual_start_ns != expected_visual_start_ns
        or visual_end_ns != expected_visual_end_ns
        or visual_end_ns <= visual_start_ns
    ):
        raise ValueError("Focused episode-band boundaries are inconsistent.")

    labels = overlay.get("labels")
    if not isinstance(labels, Mapping) or not _OUTLIER_OVERLAY_LABEL_FIELDS.issubset(
        labels
    ):
        raise ValueError("Focused outlier overlay labels are incomplete.")
    for field in _OUTLIER_OVERLAY_LABEL_FIELDS:
        _required_text(labels[field], field=f"outlier_overlay.labels.{field}")
    _required_text(
        overlay.get("robust_spread_method"),
        field="outlier_overlay.robust_spread_method",
    )

    guides = overlay.get("robust_z_guides")
    if not isinstance(guides, (list, tuple)) or not guides:
        raise ValueError("Focused outlier overlay requires robust-z guides.")
    threshold_count = 0
    for guide in guides:
        if not isinstance(guide, Mapping):
            raise ValueError("Focused robust-z guides must be mappings.")
        robust_z = _finite_float(
            guide.get("robust_z"),
            field="outlier_overlay.robust_z",
            positive=True,
        )
        expected_offset = spread_db * robust_z / normalization
        expected_values = {
            "offset_db": expected_offset,
            "lower_db": baseline_db - expected_offset,
            "upper_db": baseline_db + expected_offset,
        }
        for field, expected in expected_values.items():
            actual = _finite_float(
                guide.get(field), field=f"outlier_overlay.{field}"
            )
            if not math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12):
                raise ValueError("Focused robust-z guide boundaries are inconsistent.")
        _required_text(guide.get("label"), field="outlier_overlay.guide.label")
        if bool(guide.get("is_qualification_threshold")):
            if not math.isclose(
                robust_z,
                minimum_robust_z,
                rel_tol=0.0,
                abs_tol=1e-12,
            ):
                raise ValueError(
                    "Focused robust-z threshold guide does not match its gate."
                )
            threshold_count += 1
    if threshold_count != 1:
        raise ValueError(
            "Focused outlier overlay requires exactly one robust-z threshold guide."
        )
    expected_departure_bounds = (
        baseline_db - departure_db,
        baseline_db + departure_db,
    )
    actual_departure_bounds = (
        _finite_float(
            overlay.get("absolute_departure_lower_db"),
            field="outlier_overlay.absolute_departure_lower_db",
        ),
        _finite_float(
            overlay.get("absolute_departure_upper_db"),
            field="outlier_overlay.absolute_departure_upper_db",
        ),
    )
    if not all(
        math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12)
        for actual, expected in zip(
            actual_departure_bounds, expected_departure_bounds
        )
    ):
        raise ValueError("Focused absolute-departure guides are inconsistent.")
    for field in ("pre_flank_utc_ns", "post_flank_utc_ns"):
        interval = overlay.get(field)
        if interval is None:
            continue
        if not isinstance(interval, (list, tuple)) or len(interval) != 2:
            raise ValueError("Focused flank-baseline interval is invalid.")
        try:
            interval_start, interval_end = (int(interval[0]), int(interval[1]))
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("Focused flank-baseline UTC values are invalid.") from exc
        if interval_end < interval_start:
            raise ValueError("Focused flank-baseline interval is reversed.")
    return overlay


def _validated_native_recipe(recipe, *, expected_kind: str) -> Mapping:
    if not isinstance(recipe, Mapping):
        raise ValueError("Focused Drill-Down native recipe must be a mapping.")
    if recipe.get("kind") != expected_kind:
        raise ValueError("Focused Drill-Down native recipe kind is invalid.")
    if recipe.get("schema_version") != DRILLDOWN_ZOOM_NATIVE_RECIPE_SCHEMA_VERSION:
        raise ValueError("Unsupported focused Drill-Down native recipe schema.")
    if recipe.get("layout_version") != DRILLDOWN_ZOOM_FIGURE_LAYOUT_VERSION:
        raise ValueError("Focused Drill-Down native layout version is invalid.")
    if (
        recipe.get("resolution") != DRILLDOWN_ZOOM_NATIVE_RESOLUTION
        or recipe.get("aggregation") != DRILLDOWN_ZOOM_NO_AGGREGATION
    ):
        raise ValueError("Focused Drill-Down native resolution contract changed.")
    try:
        start_ns = int(recipe["start_utc_ns"])
        end_ns = int(recipe["end_utc_ns"])
        point_count = int(recipe["point_count"])
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        raise ValueError("Focused Drill-Down native recipe metadata is invalid.") from exc
    if end_ns <= start_ns or point_count < 0:
        raise ValueError("Focused Drill-Down native bounds or count are invalid.")
    point_times_ns = np.asarray(recipe.get("point_utc_ns", ()), dtype=np.int64)
    metric_db = np.asarray(recipe.get("metric_db", ()), dtype=np.float64)
    if (
        point_times_ns.ndim != 1
        or metric_db.ndim != 1
        or len(point_times_ns) != len(metric_db)
        or len(metric_db) != point_count
    ):
        raise ValueError("Focused Drill-Down native point arrays must align.")
    if (
        not np.isfinite(metric_db).all()
        or np.any(point_times_ns < start_ns)
        or np.any(point_times_ns >= end_ns)
        or np.any(np.diff(point_times_ns) < 0)
    ):
        raise ValueError("Focused Drill-Down native points are invalid.")
    for field in (
        "title",
        "panel_title",
        "x_label",
        "y_label",
        "empty_text",
        "evidence_unit_label",
        "evidence_unit_kind",
    ):
        _required_text(recipe.get(field), field=field)
    overlay = recipe.get("outlier_overlay")
    if overlay is not None:
        validated_overlay = _validated_outlier_overlay(overlay)
        marker_times_ns = np.asarray(
            validated_overlay["qualifying_marker_utc_ns"],
            dtype=np.int64,
        )
        marker_metrics_db = np.asarray(
            validated_overlay["qualifying_marker_delta_snr_db"],
            dtype=np.float64,
        )
        if np.any(marker_times_ns < start_ns) or np.any(marker_times_ns >= end_ns):
            raise ValueError(
                "Focused qualifying-unit markers must lie inside the Drill-Down "
                "window."
            )
        native_coordinates = set(
            zip(point_times_ns.tolist(), metric_db.tolist())
        )
        marker_coordinates = set(
            zip(marker_times_ns.tolist(), marker_metrics_db.tolist())
        )
        if not marker_coordinates.issubset(native_coordinates):
            raise ValueError(
                "Focused qualifying-unit markers must match native evidence "
                "points."
            )
        representative_ns = int(validated_overlay["representative_utc_ns"])
        if start_ns <= representative_ns < end_ns:
            representative_coordinate = (
                representative_ns,
                float(validated_overlay["representative_delta_snr_db"]),
            )
            if representative_coordinate not in marker_coordinates:
                raise ValueError(
                    "A visible focused representative must be included among "
                    "the qualifying-unit markers."
                )
        if (
            int(validated_overlay["focused_episode_visual_end_utc_ns"])
            <= start_ns
            or int(validated_overlay["focused_episode_visual_start_utc_ns"])
            >= end_ns
        ):
            raise ValueError(
                "Focused episode band must intersect the Drill-Down window."
            )
    return recipe


def _overlay_metric_values(overlay) -> np.ndarray:
    if overlay is None:
        return np.array([], dtype=np.float64)
    values = [
        overlay["local_baseline_db"],
        overlay["pre_baseline_db"],
        overlay["post_baseline_db"],
        overlay["absolute_departure_lower_db"],
        overlay["absolute_departure_upper_db"],
    ]
    values.extend(overlay["qualifying_marker_delta_snr_db"])
    for guide in overlay["robust_z_guides"]:
        values.extend([guide["lower_db"], guide["upper_db"]])
    return np.asarray(values, dtype=np.float64)


def _draw_outlier_overlay(
    axis,
    overlay,
    *,
    window_start_ns: int,
    window_end_ns: int,
) -> None:
    if overlay is None:
        return
    overlay = _validated_outlier_overlay(overlay)
    labels = overlay["labels"]

    band_start_ns = max(
        int(window_start_ns),
        int(overlay["focused_episode_visual_start_utc_ns"]),
    )
    band_end_ns = min(
        int(window_end_ns),
        int(overlay["focused_episode_visual_end_utc_ns"]),
    )
    if band_end_ns > band_start_ns:
        band_start = pd.Timestamp(
            band_start_ns,
            unit="ns",
            tz="UTC",
        ).tz_localize(None)
        band_end = pd.Timestamp(
            band_end_ns,
            unit="ns",
            tz="UTC",
        ).tz_localize(None)
        focused_episode_band = axis.axvspan(
            mdates.date2num(band_start.to_pydatetime()),
            mdates.date2num(band_end.to_pydatetime()),
            facecolor=_FOCUSED_EPISODE_FACE_COLOR,
            edgecolor="none",
            linewidth=0.0,
            alpha=_FOCUSED_EPISODE_ALPHA,
            label=labels["focused_episode"],
            zorder=_FOCUSED_EPISODE_ZORDER,
        )
        focused_episode_band.set_gid("drilldown-outlier-focused-episode")

    local_baseline = axis.axhline(
        float(overlay["local_baseline_db"]),
        color=_LOCAL_BASELINE_COLOR,
        linestyle="solid",
        linewidth=1.8,
        label=labels["local_baseline"],
        zorder=4.0,
    )
    local_baseline.set_gid("drilldown-outlier-local-baseline")

    flank_label_used = False
    for flank_name, baseline_field in (
        ("pre", "pre_baseline_db"),
        ("post", "post_baseline_db"),
    ):
        interval = overlay.get(f"{flank_name}_flank_utc_ns")
        if interval is None or int(interval[1]) <= int(interval[0]):
            continue
        flank_start = pd.Timestamp(
            int(interval[0]), unit="ns", tz="UTC"
        ).tz_localize(None)
        flank_end = pd.Timestamp(
            int(interval[1]), unit="ns", tz="UTC"
        ).tz_localize(None)
        baseline_artist = axis.hlines(
            float(overlay[baseline_field]),
            mdates.date2num(flank_start.to_pydatetime()),
            mdates.date2num(flank_end.to_pydatetime()),
            colors=_FLANK_BASELINE_COLOR,
            linestyles="dashed",
            linewidth=1.2,
            label=(
                labels["flank_baseline"] if not flank_label_used else "_nolegend_"
            ),
            zorder=4.1,
        )
        baseline_artist.set_gid(
            f"drilldown-outlier-{flank_name}-flank-baseline"
        )
        flank_label_used = True

    guide_transform = blended_transform_factory(axis.transAxes, axis.transData)
    for guide_index, guide in enumerate(overlay["robust_z_guides"]):
        for side, field in (("lower", "lower_db"), ("upper", "upper_db")):
            guide_artist = axis.axhline(
                float(guide[field]),
                color=_ROBUST_Z_GUIDE_COLOR,
                alpha=_ROBUST_Z_GUIDE_ALPHA,
                linestyle="dashed",
                linewidth=_ROBUST_Z_GUIDE_LINEWIDTH,
                zorder=2.0,
            )
            guide_artist.set_gid(
                f"drilldown-outlier-robust-z-{guide_index}-{side}"
            )
        guide_annotation = axis.text(
            0.005,
            float(guide["upper_db"]),
            str(guide["label"]),
            transform=guide_transform,
            color=_ROBUST_Z_GUIDE_COLOR,
            fontsize=_ROBUST_Z_GUIDE_FONTSIZE,
            fontfamily=METRIC_FONT_FAMILY,
            ha="left",
            va="bottom",
            bbox={
                "facecolor": "black",
                "edgecolor": "none",
                "alpha": 0.72,
                "pad": 0.8,
            },
            zorder=4.5,
        )
        guide_annotation.set_gid(
            f"drilldown-outlier-robust-z-{guide_index}-label"
        )

    departure_label = labels["absolute_departure"].format(
        value=float(overlay["minimum_departure_db"])
    )
    for side, field in (
        ("lower", "absolute_departure_lower_db"),
        ("upper", "absolute_departure_upper_db"),
    ):
        departure_artist = axis.axhline(
            float(overlay[field]),
            color=_ABSOLUTE_DEPARTURE_COLOR,
            alpha=0.82,
            linestyle="dashdot",
            linewidth=1.0,
            zorder=2.5,
        )
        departure_artist.set_gid(
            f"drilldown-outlier-absolute-departure-{side}"
        )
    departure_annotation = axis.text(
        0.005,
        float(overlay["absolute_departure_upper_db"]),
        departure_label,
        transform=guide_transform,
        color=_ABSOLUTE_DEPARTURE_COLOR,
        fontsize=_ABSOLUTE_DEPARTURE_FONTSIZE,
        fontfamily=METRIC_FONT_FAMILY,
        ha="left",
        va="bottom",
        bbox={
            "facecolor": "black",
            "edgecolor": "none",
            "alpha": 0.72,
            "pad": 0.8,
        },
        zorder=4.5,
    )
    departure_annotation.set_gid(
        "drilldown-outlier-absolute-departure-label"
    )

    marker_times_ns = np.asarray(
        overlay["qualifying_marker_utc_ns"],
        dtype=np.int64,
    )
    if len(marker_times_ns):
        marker_times = pd.to_datetime(
            marker_times_ns,
            unit="ns",
            utc=True,
        ).tz_convert(None)
        markers = axis.scatter(
            mdates.date2num(marker_times.to_pydatetime()),
            np.asarray(
                overlay["qualifying_marker_delta_snr_db"],
                dtype=np.float64,
            ),
            marker="*",
            s=DELTA_SNR_OUTLIER_MARKER_SIZE,
            label=labels["marker"],
            zorder=DELTA_SNR_OUTLIER_MARKER_ZORDER,
        )
        _apply_delta_snr_outlier_marker_style(markers)
        markers.set_gid("delta-snr-outlier-candidate-markers")


def _render_native_metric_figure(recipe, *, expected_kind: str):
    recipe = _validated_native_recipe(recipe, expected_kind=expected_kind)
    correction_notice = recipe.get("reference_snr_correction_notice", "")
    figure_height_inches = _figure_height_for_reference_correction(
        correction_notice,
        added_height_inches=_NATIVE_FIGURE_CORRECTION_FOOTER_HEIGHT_INCHES,
    )
    figure = create_agg_figure(
        figsize=(13.0, figure_height_inches), facecolor="black"
    )
    figure.subplots_adjust(
        left=0.075,
        right=0.965,
        bottom=_shift_figure_y_above_added_footer(0.15, figure_height_inches),
        top=_shift_figure_y_above_added_footer(0.82, figure_height_inches),
    )
    axis = figure.add_subplot(1, 1, 1)
    axis.set_gid("drilldown-native-chronological-axis")
    _style_evidence_axis(axis)

    point_times_ns = np.asarray(recipe["point_utc_ns"], dtype=np.int64)
    metric_db = np.asarray(recipe["metric_db"], dtype=np.float64)
    overlay = recipe.get("outlier_overlay")
    if len(point_times_ns):
        point_times = pd.to_datetime(
            point_times_ns, unit="ns", utc=True
        ).tz_convert(None)
        evidence_points = axis.scatter(
            mdates.date2num(point_times.to_pydatetime()),
            metric_db,
            s=26,
            color=_NATIVE_POINT_FACE_COLOR,
            edgecolors=_NATIVE_POINT_EDGE_COLOR,
            linewidths=0.55,
            label=recipe["evidence_unit_label"],
            zorder=5.0,
        )
        evidence_points.set_gid("drilldown-native-evidence-points")
    else:
        draw_temporal_unavailable_annotation(
            axis,
            recipe["empty_text"],
            artist_gid="drilldown-native-unavailable-annotation",
        )

    _draw_outlier_overlay(
        axis,
        overlay,
        window_start_ns=int(recipe["start_utc_ns"]),
        window_end_ns=int(recipe["end_utc_ns"]),
    )
    metric_extent_values = np.concatenate(
        [metric_db, _overlay_metric_values(overlay)]
    )
    if metric_extent_values.size:
        lower = float(np.min(metric_extent_values))
        upper = float(np.max(metric_extent_values))
        span = upper - lower
        padding = max(0.5, span * 0.06)
        limits = _expanded_metric_limits(
            lower - padding,
            upper + padding,
            center=(lower + upper) / 2.0,
        )
        if limits is not None:
            axis.set_ylim(*limits)

    window_start = pd.Timestamp(
        int(recipe["start_utc_ns"]), unit="ns", tz="UTC"
    ).tz_localize(None)
    window_end = pd.Timestamp(
        int(recipe["end_utc_ns"]), unit="ns", tz="UTC"
    ).tz_localize(None)
    axis.set_xlim(
        mdates.date2num(window_start.to_pydatetime()),
        mdates.date2num(window_end.to_pydatetime()),
    )
    date_locator = mdates.AutoDateLocator(minticks=4, maxticks=10)
    axis.xaxis.set_major_locator(date_locator)
    axis.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b\n%H:%M"))
    _set_temporal_panel_title(axis, recipe["panel_title"])
    _set_metric_axis_labels(
        axis, x_label=recipe["x_label"], y_label=recipe["y_label"]
    )
    if axis.get_legend_handles_labels()[0]:
        _place_metric_legend_top_right(axis)

    figure.suptitle(
        recipe["title"],
        color="white",
        fontweight="bold",
        fontsize=METRIC_FIGURE_TITLE_FONTSIZE,
        y=_shift_figure_y_above_added_footer(0.96, figure_height_inches),
    )
    _add_reference_snr_correction_footer(figure, correction_notice)
    figure.text(
        0.98,
        _figure_footer_y(figure),
        f"WSPRadar.org {APP_VERSION}",
        color="#888888",
        ha="right",
        fontsize=METRIC_FOOTER_FONTSIZE,
        fontfamily=METRIC_FONT_FAMILY,
    )
    setattr(
        figure,
        "_wspradar_drilldown_zoom_layout_version",
        DRILLDOWN_ZOOM_FIGURE_LAYOUT_VERSION,
    )
    setattr(
        figure,
        "_wspradar_drilldown_zoom_native_point_count",
        int(recipe["point_count"]),
    )
    return figure


def _expand_chronological_column(figure):
    """Remove folded-UTC panels and expand chronological axes in place."""
    if figure is None:
        return None
    all_axes = list(figure.axes)
    folded_axes = [axis for axis in all_axes if "folded" in _artist_gid(axis)]
    chronological_axes = [
        axis
        for axis in all_axes
        if "chronological" in _artist_gid(axis)
        and "colorbar" not in _artist_gid(axis)
    ]
    if not chronological_axes:
        raise ValueError(
            "Focused Drill-Down figures require chronological plot axes."
        )

    chronological_left = min(
        axis.get_position().x0 for axis in chronological_axes
    )
    colorbar_axes = [
        axis for axis in all_axes if "colorbar" in _artist_gid(axis)
    ]
    if colorbar_axes:
        chronological_right = min(
            axis.get_position().x0 for axis in colorbar_axes
        ) - 0.018
    elif folded_axes:
        chronological_right = max(
            axis.get_position().x1 for axis in folded_axes
        )
    else:
        chronological_right = max(
            axis.get_position().x1 for axis in chronological_axes
        )
    if chronological_right <= chronological_left:
        raise ValueError(
            "Focused Drill-Down chronological axes have invalid geometry."
        )

    for axis in chronological_axes:
        position = axis.get_position()
        axis.set_position(
            [
                chronological_left,
                position.y0,
                chronological_right - chronological_left,
                position.height,
            ],
            which="both",
        )

    folded_artists = [
        artist
        for artist in figure.findobj()
        if artist not in folded_axes and "folded" in _artist_gid(artist)
    ]
    for artist in folded_artists:
        try:
            artist.remove()
        except (NotImplementedError, ValueError):
            artist.set_visible(False)
    for axis in folded_axes:
        axis.remove()

    chronological_center = (chronological_left + chronological_right) / 2.0
    for artist in figure.findobj():
        gid = _artist_gid(artist)
        if "chronological" not in gid or "header" not in gid:
            continue
        if hasattr(artist, "set_x"):
            artist.set_x(chronological_center)
    setattr(
        figure,
        "_wspradar_drilldown_zoom_layout_version",
        DRILLDOWN_ZOOM_FIGURE_LAYOUT_VERSION,
    )
    return figure


@synchronized_matplotlib
def render_drilldown_zoom_performance_snr_figure(recipe):
    """Render focused Performance SNR at native opportunity resolution."""
    if isinstance(recipe, Mapping) and recipe.get("kind") == (
        DRILLDOWN_ZOOM_PERFORMANCE_NATIVE_KIND
    ):
        return _render_native_metric_figure(
            recipe, expected_kind=DRILLDOWN_ZOOM_PERFORMANCE_NATIVE_KIND
        )
    # Transitional compatibility for already-registered pre-v2 recipes.
    from ui.plots.evidence_figures import (
        render_segment_temporal_snr_export_figure,
    )

    return _expand_chronological_column(
        render_segment_temporal_snr_export_figure(recipe)
    )


@synchronized_matplotlib
def render_drilldown_zoom_performance_evidence_figure(recipe):
    """Render focused Performance outcomes as chronological panels only."""
    return _expand_chronological_column(
        render_segment_temporal_evidence_export_figure(recipe)
    )


@synchronized_matplotlib
def render_drilldown_zoom_benchmark_delta_snr_figure(recipe):
    """Render focused Benchmark Delta-SNR at native paired-unit resolution."""
    if isinstance(recipe, Mapping) and recipe.get("kind") == (
        DRILLDOWN_ZOOM_BENCHMARK_NATIVE_KIND
    ):
        return _render_native_metric_figure(
            recipe, expected_kind=DRILLDOWN_ZOOM_BENCHMARK_NATIVE_KIND
        )
    # Transitional compatibility for already-registered pre-v2 recipes.
    from ui.plots.evidence_figures import render_selected_evidence_export_figure

    return _expand_chronological_column(
        render_selected_evidence_export_figure(recipe)
    )


@synchronized_matplotlib
def render_drilldown_zoom_benchmark_coverage_figure(recipe):
    """Render focused Benchmark path coverage as one chronological panel."""
    return _expand_chronological_column(
        render_selected_compare_coverage_export_figure(recipe)
    )
