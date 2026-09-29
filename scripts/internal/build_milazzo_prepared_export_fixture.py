"""Build a reviewed, offline prepared-export snapshot from the Milazzo RX reference.

The source reference remains the independent scientific oracle. This derivative
fixture checks exported package integrity, not agreement with new observations.
No analysis, plotting, metadata or CSV export functions are replaced.
"""

from __future__ import annotations

import argparse
from contextlib import ExitStack
import hashlib
import io
import json
from pathlib import Path
import socket
import sys
from types import SimpleNamespace
from unittest.mock import patch
import zipfile

REPOSITORY = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY))
sys.path.insert(0, str(REPOSITORY / "tests" / "regression"))

import pandas as pd
import requests

from core.artifact_store import register_session_artifact, session_artifact_path
from core.compare_engine import compare_footer_counts
from core.map_data_artifacts import MapDataArtifactPaths, write_map_data_artifacts
from core.map_models import MapData
from core.presentation_context import PresentationContext
from i18n import T
from scripts.internal import build_regression_fixture_from_demo_folder as fixture_builder
from test_milazzo_reference import _calculate_run, _assert_native_units
from ui import results_export
from ui.config_io import apply_config_state_values, validate_config_document
from ui.export_payloads import (
    BenchmarkFigureRecipes, ExportSelection, ExportTables,
    InspectorExportPayload, MapExportPayload,
)
from ui.inspector.drilldown import _build_drilldown_table
from ui.plots.evidence_figures import (
    _segment_figure_export_recipe, _segment_temporal_evidence_export_recipe,
    _selected_evidence_export_recipe,
)

SOURCE = REPOSITORY / "tests/regression/reference_fixtures/milazzo_fig6_rx_v1"
FIXTURE_NAME = "milazzo_fig6_rx_prepared_export_v1"
OFFLINE_PROVENANCE = {
    "execution": "offline SQLite replay of frozen user-supplied wspr.rocks reports",
    "source_reference": "tests/regression/reference_fixtures/milazzo_fig6_rx_v1",
    "provider_queried": False,
    "database_source_field_meaning": (
        "wspr_live is the required production provider-enum value used by this offline "
        "export harness; it is not a claim that these supplied reports were obtained "
        "from wspr.live. The actual input provenance is the frozen source reference."
    ),
    "scope": "export package snapshot; not an independent scientific oracle or a full receiver-activity capture",
}


def reject_network(*_args, **_kwargs):
    raise RuntimeError("Prepared-export fixture creation must remain offline")


def temporal_labels(run):
    labels = T["en"]
    return {
        "analysis_start_t": run.configuration["start_utc"],
        "analysis_end_t": run.configuration["end_utc"],
        "reference_snr_correction_db": run.context.reference_snr_correction_db,
        "chronological_title": labels["fig_selected_compare_chronological_title"],
        "chronological_x_label": labels["fig_segment_chronological_x"],
        "chronological_unavailable_text": labels["fig_compare_chronological_unavailable"],
        "metric_axis_label": labels["tbl_col_delta_snr"],
        "folded_title": labels["fig_selected_compare_folded_title"],
        "folded_x_label": labels["fig_segment_utc_hour_x"],
        "folded_date_annotation": labels["fig_segment_dates_folded"].replace("{count}", "{utc_date_count}"),
        "density_label": labels["fig_relative_joint_spot_density"],
        "folded_unavailable_text": labels["fig_segment_folded_unavailable"],
        "median_focus_axis_label": labels["fig_compare_median_focus_axis"],
        "median_label": labels["fig_median_label"],
        "bin_median_label": labels["fig_temporal_bin_median"],
        "bin_iqr_label": labels["fig_temporal_bin_iqr"],
        "time_bin_options": ("3h",),
    }


def build_prepared_export(work_directory: Path):
    """Replay frozen observations and capture the actual production ZIP."""
    document = json.loads((SOURCE / "rx_reference.config").read_text(encoding="utf-8"))
    document["extensions"]["org.wspradar.fixture_provenance"] = OFFLINE_PROVENANCE
    benchmark = document["settings"]["results_view"]["benchmark"]
    benchmark.update({
        "show_non_joint": True,
        "segment_evidence_time_bin": "3h",
        "selected_stations": [{"callsign": "VE6PDQ", "locator": "DO34IR"}],
    })
    source_rows = pd.read_csv(SOURCE / "source_rows.csv", float_precision="round_trip")
    run = _calculate_run(source_rows, configuration_document=document)
    # The reference replay helper verifies the empty strict result before
    # executing the historical query. Preserve that actual selected provenance.
    assert run.strict_rows.empty
    run.analysis = run.analysis.for_legacy_query()
    expected = pd.read_csv(SOURCE / "expected_native_units.csv", float_precision="round_trip")
    _assert_native_units(run.units, expected)
    assert len(source_rows) == 86 and len(run.sql_rows) == 39
    assert int(run.sql_rows.has_u.sum() + run.sql_rows.has_r.sum()) == 44
    assert run.units.outcome.value_counts().to_dict() == {"target_only": 26, "joint": 5, "reference_only": 3}
    assert sorted(run.points.metric) == [7, 7, 8, 17, 22]
    state = {"lang": "en", "run_id": 1, "run_mode": "RX"}
    apply_config_state_values(validate_config_document(document), state)
    state["run_mode"] = "RX"
    state["run_id"] = 1
    cache_directory = work_directory / "cache"
    paths = {
        kind: session_artifact_path(cache_directory, state, run_id=1,
            analysis_id=run.analysis.id, artifact_kind=kind)
        for kind in ("spots", "map_stations", "map_segments")
    }
    paths["spots"].parent.mkdir(parents=True, exist_ok=True)
    run.processed.to_parquet(paths["spots"], index=False)
    map_data = MapData(run.stations, run.segment_rows, run.analysis.id,
        run.analysis.is_compare,  run.analysis.analysis_kind)
    map_paths = MapDataArtifactPaths(paths["map_stations"], paths["map_segments"])
    write_map_data_artifacts(map_data, map_paths)
    for artifact_path in paths.values():
        register_session_artifact(state, artifact_path)
    inspector = run.inspector
    selected_stations = inspector.station_table[
        inspector.station_table[inspector.locator_column].str.upper().eq("DO34IR")
    ]
    selected_points = run.points[run.points.grid.str.upper().eq("DO34IR")]
    assert len(selected_points) == 3 and sorted(selected_points.metric) == [7, 8, 22]
    drilldown, warning = _build_drilldown_table(
        str(paths["spots"]), selected_stations,
        inspector.station_column, inspector.locator_column,
        inspector.distance_column, inspector.azimuth_column,
        run.analysis.id,  True, False,
        inspector.target_name, inspector.reference_header, T["en"],
    )
    assert warning is None and not drilldown.empty
    labels = T["en"]
    footer = compare_footer_counts(run.stations, max_dist_km=run.context.max_peer_distance_km)
    segment_recipe = _segment_figure_export_recipe(
        title=run.analysis.title, selected_segment="Full Range | All Directions",
         station_values=run.stations.stat_val.dropna(),
        spot_values=run.points.metric,
        panel_labels=[inspector.target_only_label, labels["txt_joint"], labels["leg_both_async"], inspector.reference_only_label],
        panel_y_label=labels["fig_share_percent_axis"],
        decode_outcomes_title=labels["fig_decode_outcomes"],
        station_medians_title=labels["fig_station_medians_delta"],
        paired_evidence_title=labels["fig_joint_spot_delta"],
        metric_axis_label=labels["tbl_col_delta_snr"],
        median_label=labels["fig_median_label"], mean_label=labels["fig_mean_label"],
        no_data_label=labels["fig_no_data"],
        panel_station_counts=[footer[key] for key in ("stat_only_u", "stat_joint", "stat_both_async", "stat_only_r")],
        panel_spot_counts=[footer[key] for key in ("spot_only_u", "spot_joint", "spot_both_async", "spot_only_r")],
        panel_series_labels=[labels["lbl_results_stations"], labels["lbl_results_spots"]],
    )
    temporal_recipe = _segment_temporal_evidence_export_recipe(
        run.points, run.analysis.title, "3h", labels["fig_joint_spot_count"],
        **temporal_labels(run),
    )
    selected_recipe = _selected_evidence_export_recipe(
        selected_points, "VE6PDQ (DO34IR)", "3h",
        count_label=labels["fig_joint_spot_count"], **temporal_labels(run),
    )
    drilldown_context = {
        "station_meta_df": inspector.station_table,
        "station_col": inspector.station_column, "loc_col": inspector.locator_column,
        "km_col": inspector.distance_column, "az_col": inspector.azimuth_column,
        "analysis_id": run.analysis.id,
        "show_non_joint": True, "is_local_median": False,
        "col_u_name": inspector.target_name, "ref_header": inspector.reference_header,
        "target_callsign": run.context.callsign, "lang": "en",
    }
    with patch.object(results_export, "st", SimpleNamespace(session_state=state)), patch.object(results_export, "CACHE_DIR", cache_directory):
        results_export.register_map_export_context(MapExportPayload(
            analysis=run.analysis, parquet_path=paths["spots"], map_data_paths=map_paths,
            start_t=run.configuration["start_utc"], end_t=run.configuration["end_utc"],
            max_peer_distance_km=run.context.max_peer_distance_km,
            base_min_stations=run.context.min_joint_stations_per_map_segment,
            lat_0=run.latitude, lon_0=run.longitude,
            analysis_context=run.context,
            presentation_context=PresentationContext(solar_label="All", labels=labels),
            database_source="wspr_live",
        ))
        results_export.register_inspector_export(InspectorExportPayload(
            analysis_id=run.analysis.id, family="benchmark",
            selection=ExportSelection(
                selected_segment="Full Range | All Directions",
                selected_distance="Full Range", selected_direction="All Directions",
                show_non_joint=True, evidence_time_bin="3h", segment_evidence_time_bin="3h",
                selected_stations=["VE6PDQ (DO34IR)"],
            ),
            tables=ExportTables(station_insights_df=inspector.station_table,
                drilldown_selected_df=drilldown, all_drilldown_context=drilldown_context),
            figures=BenchmarkFigureRecipes(segment_figure_recipe=segment_recipe,
                segment_temporal_evidence_figure_recipe=temporal_recipe,
                selected_evidence_figure_recipe=selected_recipe,
                reference_snr_header=inspector.reference_header),
        ), translations=labels)
        package_bytes, filename = results_export.build_results_zip(labels)
    with zipfile.ZipFile(io.BytesIO(package_bytes)) as archive:
        for member in archive.infolist():
            destination = (work_directory / member.filename).resolve()
            if not destination.is_relative_to(work_directory.resolve()):
                raise ValueError("Unsafe exported member path")
        archive.extractall(work_directory)
    export_root = work_directory / filename.removesuffix(".zip")
    metadata_path = export_root / "config/run_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata["result_blocks"][0]["decode_filter_mode"] == "legacy_no_code"
    # Add an explicit qualification to the unzipped derivative package. The
    # production metadata and signature remain intact; no provider capture is
    # inferred from an enum with no offline member.
    metadata["fixture_provenance"] = OFFLINE_PROVENANCE
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return export_root


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-directory", type=Path, required=True)
    parser.add_argument("--fixtures-directory", type=Path, default=REPOSITORY / "tests/regression/fixtures")
    args = parser.parse_args()
    work_directory = args.work_directory.resolve()
    work_directory.mkdir(parents=True, exist_ok=False)
    with ExitStack() as guards:
        guards.enter_context(patch.object(requests.sessions.Session, "request", reject_network))
        guards.enter_context(patch.object(socket, "create_connection", reject_network))
        guards.enter_context(patch.object(socket.socket, "connect", reject_network))
        guards.enter_context(patch.object(socket.socket, "connect_ex", reject_network))
        export_root = build_prepared_export(work_directory)
        destination = fixture_builder.build_fixture(export_root, args.fixtures_directory, FIXTURE_NAME, False)
    metrics = json.loads((destination / "expected_metrics.json").read_text(encoding="utf-8"))
    assert set(metrics) == {"benchmark"}
    block = metrics["benchmark"]
    assert all(table["exists"] and table["rows"] > 0 for table in block["tables"].values())
    assert all(figure["exists"] for figure in block["figures"].values())
    assert len(block["analysis_caches"]) == 1
    assert next(iter(block["analysis_caches"].values()))["rows"] == 34
    manifest_path = destination / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["source_input_folder"] = "offline replay of tests/regression/reference_fixtures/milazzo_fig6_rx_v1"
    manifest["source_export_root"] = "production build_results_zip output; transient work directory omitted"
    manifest["source_file_sha256"] = {
        name: hashlib.sha256((SOURCE / name).read_bytes()).hexdigest()
        for name in ("source_rows.csv", "rx_reference.config", "expected_native_units.csv")
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Built prepared-export fixture: {destination}")
    print(json.dumps({"tables": block["tables"], "figures": block["figures"], "analysis_caches": block["analysis_caches"]}, indent=2))


if __name__ == "__main__":
    main()
