"""Typed, borrowed inputs to export registration.

These frozen records describe a registration draft. Nested recipes, tables, and
contexts remain borrowed from their producers; the export owner validates and
captures them before publication. Freezing a draft does not freeze its contents.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, fields
from typing import Any, Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from core.analysis_context import AnalysisContext
    from core.map_data_artifacts import MapDataArtifactPaths
    from core.presentation_context import PresentationContext
    from config.delta_snr_outlier import DeltaSnrOutlierDetectionPolicy
    from ui.inspector.outlier_export import DeltaSnrOutlierExportTables


ExportFamily = Literal["benchmark", "performance"]
FigureRecipe = Mapping[str, Any]


@dataclass(frozen=True, slots=True, kw_only=True)
class MapExportPayload:
    """Borrowed map inputs and completed scientific/source provenance."""

    analysis: Mapping[str, Any]
    parquet_path: Any
    map_data_paths: MapDataArtifactPaths
    start_t: Any
    end_t: Any
    max_peer_distance_km: float
    base_min_stations: int
    lat_0: float
    lon_0: float
    analysis_context: AnalysisContext
    presentation_context: PresentationContext
    database_source: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ExportSelection:
    """Resolved exported selection, distinct from automatic UI selection intent."""

    selected_segment: Any
    selected_distance: str
    selected_direction: str
    show_non_joint: bool
    evidence_time_bin: str | None
    selected_stations: Sequence[str] | None
    show_zero_target: bool = False
    segment_evidence_time_bin: str | None = None
    selected_ranges: Sequence[str] | None = None
    selected_directions: Sequence[str] | None = None
    selected_station_label: str | None = None
    selected_station_context_label: str | None = None
    selected_station_role: str | None = None
    selected_evidence_figure_descriptions: Mapping[str, str] | None = None
    allow_multiple_selected_stations: bool = False


@dataclass(frozen=True, slots=True, kw_only=True)
class ExportTables:
    """Borrowed displayed rows and the context for a later full evidence read."""

    station_insights_df: Any = None
    drilldown_selected_df: Any = None
    all_drilldown_context: Mapping[str, Any] | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class BenchmarkFigureRecipes:
    """Existing Benchmark recipes, retained individually for preview parity."""

    segment_figure_recipe: FigureRecipe | None = None
    segment_temporal_evidence_figure_recipe: FigureRecipe | None = None
    segment_temporal_snr_deviation_figure_recipe: FigureRecipe | None = None
    segment_temporal_coverage_figure_recipe: FigureRecipe | None = None
    selected_evidence_figure_recipe: FigureRecipe | None = None
    selected_station_coverage_figure_recipe: FigureRecipe | None = None
    reference_snr_header: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class PerformanceFigureRecipes:
    """Existing Performance recipes, including both selected-station figures."""

    segment_figure_recipe: FigureRecipe | None = None
    segment_temporal_evidence_figure_recipe: FigureRecipe | None = None
    segment_temporal_snr_deviation_figure_recipe: FigureRecipe | None = None
    selected_evidence_figure_recipe: FigureRecipe | None = None
    selected_station_snr_evidence_figure_recipe: FigureRecipe | None = None
    selected_station_temporal_evidence_figure_recipe: FigureRecipe | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class OutlierExport:
    """Enabled Benchmark reporting; empty reports still carry both tables."""

    delta_snr_outlier_detector_version: str
    delta_snr_outlier_detection_policy: DeltaSnrOutlierDetectionPolicy | None = None
    delta_snr_outlier_export_tables: DeltaSnrOutlierExportTables | None = None
    delta_snr_outlier_export_metadata: Mapping[str, Any] | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class BenchmarkZoomExport:
    """One Benchmark focus interval and its two existing figure recipes."""

    drilldown_zoom_metadata: Mapping[str, Any]
    drilldown_zoom_benchmark_delta_snr_figure_recipe: FigureRecipe | None
    drilldown_zoom_benchmark_coverage_figure_recipe: FigureRecipe | None


@dataclass(frozen=True, slots=True, kw_only=True)
class PerformanceZoomExport:
    """One Performance focus interval and its two existing figure recipes."""

    drilldown_zoom_metadata: Mapping[str, Any]
    drilldown_zoom_performance_snr_figure_recipe: FigureRecipe | None
    drilldown_zoom_performance_temporal_figure_recipe: FigureRecipe | None


@dataclass(frozen=True, slots=True, kw_only=True)
class InspectorExportPayload:
    """A result-family-specific draft for one atomic Inspector registration."""

    analysis_id: str
    family: ExportFamily
    selection: ExportSelection
    tables: ExportTables
    figures: BenchmarkFigureRecipes | PerformanceFigureRecipes
    outliers: OutlierExport | None = None
    zoom: BenchmarkZoomExport | PerformanceZoomExport | None = None

    def __post_init__(self) -> None:
        if self.family not in ("benchmark", "performance"):
            raise ValueError("Inspector export family must be 'benchmark' or 'performance'.")
        if not isinstance(self.selection, ExportSelection):
            raise TypeError("Inspector exports require an ExportSelection.")
        if not isinstance(self.tables, ExportTables):
            raise TypeError("Inspector exports require ExportTables.")
        figure_type, zoom_type = (
            (BenchmarkFigureRecipes, BenchmarkZoomExport)
            if self.family == "benchmark"
            else (PerformanceFigureRecipes, PerformanceZoomExport)
        )
        if not isinstance(self.figures, figure_type):
            raise TypeError("Inspector figure recipes must match the export family.")
        if self.zoom is not None and not isinstance(self.zoom, zoom_type):
            raise TypeError("Drill-Down zoom recipes must match the export family.")
        if self.outliers is not None:
            if not isinstance(self.outliers, OutlierExport):
                raise TypeError("Enabled outlier exports require an OutlierExport.")
            if self.family != "benchmark":
                raise ValueError("Delta-SNR outlier exports require Benchmark results.")

    def to_registration_values(self) -> dict[str, Any]:
        """Project the existing registration keywords without copying evidence.

        Optional registration defaults remain explicit here. The export owner's
        existing validator determines which optional keys appear in published
        blocks and serialized metadata.
        """
        registration_values = {
            "analysis_id": self.analysis_id,
            "segment_figure_recipe": None,
            "segment_temporal_evidence_figure_recipe": None,
            "segment_temporal_snr_deviation_figure_recipe": None,
            "segment_temporal_coverage_figure_recipe": None,
            "selected_evidence_figure_recipe": None,
            "selected_station_snr_evidence_figure_recipe": None,
            "selected_station_temporal_evidence_figure_recipe": None,
            "selected_station_coverage_figure_recipe": None,
            "reference_snr_header": None,
            "report_delta_snr_outlier_candidates": self.outliers is not None,
            "delta_snr_outlier_detector_version": None,
            "delta_snr_outlier_detection_policy": None,
            "delta_snr_outlier_export_tables": None,
            "delta_snr_outlier_export_metadata": None,
            "drilldown_zoom_metadata": None,
            "drilldown_zoom_performance_snr_figure_recipe": None,
            "drilldown_zoom_performance_temporal_figure_recipe": None,
            "drilldown_zoom_benchmark_delta_snr_figure_recipe": None,
            "drilldown_zoom_benchmark_coverage_figure_recipe": None,
        }
        for record in (self.selection, self.tables, self.figures, self.outliers, self.zoom):
            if record is not None:
                registration_values.update(
                    (record_field.name, getattr(record, record_field.name))
                    for record_field in fields(record)
                )
        return registration_values
