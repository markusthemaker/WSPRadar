"""Pass prepared inspector outputs to the existing lazy export registration.

The export contract, frame projections, and registration lifecycle are retained.
"""

import pandas as pd

from ui.inspector.outlier_candidates import DELTA_SNR_OUTLIER_DETECTOR_VERSION
from ui.export_payloads import (
    BenchmarkFigureRecipes,
    BenchmarkZoomExport,
    ExportSelection,
    ExportTables,
    InspectorExportPayload,
    OutlierExport,
    PerformanceFigureRecipes,
    PerformanceZoomExport,
)
from ui.results_export import register_inspector_export
from ui.result_hierarchy import remote_station_type


def opportunity_export_station_rows(display_station_table, *, export_column_renames):
    """Rename only visible Performance station rows into the export schema."""
    if display_station_table is None:
        return pd.DataFrame()
    return display_station_table.rename(columns=export_column_renames)


def register_performance_inspector_outputs(context, scope, selection, station_view,
                                         selected_view, prepared_segment,
                                         segment_temporal_export, *, preparation, language):
    display_model = prepared_segment.bundle["display_model"]
    filtered_export_station_table = opportunity_export_station_rows(
        station_view.export_station_table,
        export_column_renames=display_model["export_column_renames"],
    )
    all_drilldown_context = preparation.all_drilldown_context(
        context, station_view, prepared_segment, language=language,
    )
    register_inspector_export(
        InspectorExportPayload(
            analysis_id=context.analysis_id,
            family='performance',
            selection=ExportSelection(
                selected_segment=scope.selected_segment,
                selected_distance=scope.range_summary,
                selected_direction=scope.direction_summary,
                selected_ranges=list((scope.selected_ranges or (context.translations["opt_full_range"],))),
                selected_directions=list((scope.selected_directions or (context.translations["opt_all_dirs"],))),
                show_non_joint=False,
                show_zero_target=station_view.show_zero_target,
                evidence_time_bin=selected_view.selected_time_bin,
                segment_evidence_time_bin=(
                    segment_temporal_export or {}
                ).get("time_bin"),
                selected_stations=selected_view.selected_station_labels,
                selected_station_label=selected_view.selected_station_label_text,
                selected_station_context_label=selected_view.selected_station_context_text,
                selected_station_role=remote_station_type(context.analysis_id),
                selected_evidence_figure_descriptions=selected_view.selected_evidence_figure_descriptions,
            ),
            tables=ExportTables(
                station_insights_df=filtered_export_station_table,
                drilldown_selected_df=selected_view.drilldown_selected_df,
                all_drilldown_context=all_drilldown_context,
            ),
            figures=PerformanceFigureRecipes(
                segment_figure_recipe=prepared_segment.bundle["figure_recipe"],
                segment_temporal_evidence_figure_recipe=(
                    segment_temporal_export or {}
                ).get("export_recipe"),
                segment_temporal_snr_deviation_figure_recipe=(
                    segment_temporal_export or {}
                ).get("snr_export_recipe"),
                selected_evidence_figure_recipe=selected_view.selected_evidence_recipe,
                selected_station_snr_evidence_figure_recipe=selected_view.selected_station_snr_evidence_recipe,
                selected_station_temporal_evidence_figure_recipe=selected_view.selected_station_temporal_evidence_recipe,
            ),
            zoom=PerformanceZoomExport(
                drilldown_zoom_metadata=selected_view.drilldown_zoom_metadata,
                drilldown_zoom_performance_snr_figure_recipe=selected_view.drilldown_zoom_performance_snr_recipe,
                drilldown_zoom_performance_temporal_figure_recipe=selected_view.drilldown_zoom_performance_evidence_recipe,
            ) if (selected_view.drilldown_zoom_metadata is not None or selected_view.drilldown_zoom_performance_snr_recipe is not None or selected_view.drilldown_zoom_performance_evidence_recipe is not None) else None,
        ),
        translations=context.translations,
    )


def register_empty_inspector_outputs(context, scope, *, outlier_detection_policy,
                                     outlier_exports=None):
    is_outlier_reporting_enabled = outlier_detection_policy is not None
    delta_snr_outlier_export_tables, delta_snr_outlier_export_metadata = (
        outlier_exports if outlier_exports is not None else (None, None)
    )
    register_inspector_export(
        InspectorExportPayload(
            analysis_id=context.analysis_id,
            family=("benchmark" if context.is_compare else "performance"),
            selection=ExportSelection(
                selected_segment=scope.selected_segment,
                selected_distance=scope.range_summary,
                selected_direction=scope.direction_summary,
                selected_ranges=list(scope.selected_ranges) if scope.selected_ranges else [context.translations["opt_full_range"]],
                selected_directions=list(scope.selected_directions) if scope.selected_directions else [context.translations["opt_all_dirs"]],
                show_non_joint=False,
                evidence_time_bin=None,
                selected_stations=[],
                allow_multiple_selected_stations=is_outlier_reporting_enabled,
            ),
            tables=ExportTables(
                station_insights_df=pd.DataFrame(),
                drilldown_selected_df=pd.DataFrame(),
            ),
            figures=BenchmarkFigureRecipes() if context.is_compare else PerformanceFigureRecipes(),
            outliers=OutlierExport(
                delta_snr_outlier_detector_version=DELTA_SNR_OUTLIER_DETECTOR_VERSION
                if is_outlier_reporting_enabled
                else None,
                delta_snr_outlier_detection_policy=outlier_detection_policy
                if is_outlier_reporting_enabled
                else None,
                delta_snr_outlier_export_tables=delta_snr_outlier_export_tables
                if is_outlier_reporting_enabled
                else None,
                delta_snr_outlier_export_metadata=delta_snr_outlier_export_metadata
                if is_outlier_reporting_enabled
                else None,
            ) if is_outlier_reporting_enabled else None,
        ),
        translations=context.translations,
    )


def register_benchmark_inspector_outputs(context, scope, selection, station_view,
                                       selected_view, prepared_segment,
                                       segment_temporal_export, *, preparation,
                                       language, outlier_detection_policy):
    all_drilldown_context = preparation.all_drilldown_context(
        context, station_view, prepared_segment, language=language,
    )
    delta_snr_outlier_export_tables = None
    delta_snr_outlier_export_metadata = None
    if selection.is_outlier_reporting_enabled:
        delta_snr_outlier_export_tables, delta_snr_outlier_export_metadata = preparation.prepare_outlier_exports(
            prepared_segment.bundle.get("outlier_model"),
            prepared_segment.bundle.get("outlier_report_view_model"),
            is_sequential=context.is_sequential,
        )
    register_inspector_export(
        InspectorExportPayload(
            analysis_id=context.analysis_id,
            family='benchmark',
            selection=ExportSelection(
                selected_segment=scope.selected_segment,
                selected_distance=scope.range_summary,
                selected_direction=scope.direction_summary,
                selected_ranges=list(scope.selected_ranges) if scope.selected_ranges else [context.translations["opt_full_range"]],
                selected_directions=list(scope.selected_directions) if scope.selected_directions else [context.translations["opt_all_dirs"]],
                show_non_joint=station_view.show_non_joint,
                evidence_time_bin=(selected_view.selected_evidence_export or {}).get("time_bin"),
                segment_evidence_time_bin=(segment_temporal_export or {}).get("time_bin"),
                selected_stations=selected_view.selected_station_labels,
                allow_multiple_selected_stations=selection.is_outlier_reporting_enabled,
            ),
            tables=ExportTables(
                station_insights_df=station_view.export_station_table,
                drilldown_selected_df=selected_view.drilldown_selected_df,
                all_drilldown_context=all_drilldown_context,
            ),
            figures=BenchmarkFigureRecipes(
                segment_figure_recipe=prepared_segment.bundle["figure_recipe"],
                segment_temporal_evidence_figure_recipe=(
                    segment_temporal_export or {}
                ).get("export_recipe"),
                segment_temporal_snr_deviation_figure_recipe=(
                    segment_temporal_export or {}
                ).get("snr_export_recipe"),
                segment_temporal_coverage_figure_recipe=(
                    segment_temporal_export or {}
                ).get("coverage_export_recipe"),
                selected_evidence_figure_recipe=(selected_view.selected_evidence_export or {}).get("export_recipe"),
                selected_station_coverage_figure_recipe=(
                    selected_view.selected_evidence_export or {}
                ).get("coverage_export_recipe"),
                reference_snr_header=f'{prepared_segment.bundle["view_model"].reference_header} SNR (dB)',
            ),
            outliers=OutlierExport(
                delta_snr_outlier_detector_version=DELTA_SNR_OUTLIER_DETECTOR_VERSION
                if selection.is_outlier_reporting_enabled
                else None,
                delta_snr_outlier_detection_policy=outlier_detection_policy
                if selection.is_outlier_reporting_enabled
                else None,
                delta_snr_outlier_export_tables=delta_snr_outlier_export_tables,
                delta_snr_outlier_export_metadata=delta_snr_outlier_export_metadata,
            ) if selection.is_outlier_reporting_enabled else None,
            zoom=BenchmarkZoomExport(
                drilldown_zoom_metadata=selected_view.drilldown_zoom_metadata,
                drilldown_zoom_benchmark_delta_snr_figure_recipe=selected_view.drilldown_zoom_benchmark_delta_recipe,
                drilldown_zoom_benchmark_coverage_figure_recipe=selected_view.drilldown_zoom_benchmark_coverage_recipe,
            ) if (selected_view.drilldown_zoom_metadata is not None or selected_view.drilldown_zoom_benchmark_delta_recipe is not None or selected_view.drilldown_zoom_benchmark_coverage_recipe is not None) else None,
        ),
        translations=context.translations,
    )
