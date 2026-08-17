"""Prepared-results package structure regression tests."""

from contextlib import nullcontext
from copy import deepcopy
import io
import inspect
import json
import os
from pathlib import Path
from types import SimpleNamespace
import zipfile

import pandas as pd
import pytest

from config.delta_snr_outlier import (
    DeltaSnrOutlierDetectionPolicy,
)
from core import plot_engine
from core.analysis_context import AnalysisContext
from core.artifact_store import (
    SESSION_ARTIFACT_PATHS_KEY,
    register_session_artifact,
    session_artifact_path,
)
from i18n import T
from ui import results_export
from ui.inspector.outlier_export import (
    DeltaSnrOutlierExportTables,
    OUTLIER_EVENT_PATH_COLUMNS,
    OUTLIER_EVENT_PATHS_TABLE_FILENAME,
    OUTLIER_PAIRED_EVIDENCE_COLUMNS,
    OUTLIER_PAIRED_EVIDENCE_TABLE_FILENAME,
)
from ui.plots import (
    benchmark_evidence_figures,
    drilldown_zoom_figures,
    evidence_figures,
)


SUCCESS_SELECTED_FIGURE_EXPORTS = (
    (
        "figure_selected_station_snr_evidence.png",
        "render_segment_temporal_snr_export_figure",
        "selected_station_snr_evidence_figure_recipe",
        "figure_segment_temporal_snr_deviation.png",
        "segment_temporal_snr_deviation_figure_recipe",
    ),
    (
        "figure_selected_station_temporal_evidence.png",
        "render_segment_temporal_evidence_export_figure",
        "selected_station_temporal_evidence_figure_recipe",
        "figure_segment_temporal_evidence.png",
        "segment_temporal_evidence_figure_recipe",
    ),
)
OBSOLETE_SUCCESS_SELECTED_FIGURE_NAMES = (
    "figure_selected_station_chronological.png",
    "figure_selected_station_utc_hour_profile.png",
    "figure_selected_station_snr_distribution.png",
    "figure_selected_station_similar_stations.png",
)
COMPARE_COVERAGE_EXPORT_CASES = (
    (
        "figure_segment_temporal_coverage.png",
        "render_compare_temporal_coverage_export_figure",
        "segment_temporal_coverage_figure_recipe",
        "evidence_title",
        "Benchmark Temporal Evidence Coverage",
    ),
    (
        "figure_selected_station_coverage.png",
        "render_selected_compare_coverage_export_figure",
        "selected_station_coverage_figure_recipe",
        "evidence_title",
        "Selected Path Evidence Coverage",
    ),
)
DRILLDOWN_ZOOM_RENDER_CASES = (
    (
        "figure_drilldown_zoom_snr_evidence.png",
        "drilldown_zoom_performance_snr_figure_recipe",
        "render_drilldown_zoom_performance_snr_figure",
    ),
    (
        "figure_drilldown_zoom_temporal_evidence.png",
        "drilldown_zoom_performance_temporal_figure_recipe",
        "render_drilldown_zoom_performance_evidence_figure",
    ),
    (
        "figure_drilldown_zoom_delta_snr_evidence.png",
        "drilldown_zoom_benchmark_delta_snr_figure_recipe",
        "render_drilldown_zoom_benchmark_delta_snr_figure",
    ),
    (
        "figure_drilldown_zoom_coverage.png",
        "drilldown_zoom_benchmark_coverage_figure_recipe",
        "render_drilldown_zoom_benchmark_coverage_figure",
    ),
)
RETIRED_COMPARE_FIGURE_EXPORTS = (
    (
        "figure_segment_temporal_delta_change.png",
        "segment_temporal_delta_change_figure_recipe",
        "render_compare_delta_change_export_figure",
    ),
    (
        "figure_path_agreement_consistency.png",
        "path_agreement_consistency_figure_recipe",
        "render_compare_path_consistency_export_figure",
    ),
)


def _drilldown_zoom_metadata(
    *,
    start_utc="2026-07-01T03:00:00Z",
    end_utc="2026-07-01T06:00:00Z",
    option="3h",
    origin="manual",
    time_bin="native",
    outlier_candidate=None,
):
    """Build one valid exact focused-window export contract."""
    metadata = {
        "schema_version": results_export.DRILLDOWN_ZOOM_EXPORT_SCHEMA_VERSION,
        "station": {"callsign": "ok1fcx", "locator": "jn79"},
        "start_utc": start_utc,
        "end_utc": end_utc,
        "option": option,
        "origin": origin,
        "time_bin": time_bin,
        "resolution": drilldown_zoom_figures.DRILLDOWN_ZOOM_NATIVE_RESOLUTION,
        "aggregation": drilldown_zoom_figures.DRILLDOWN_ZOOM_NO_AGGREGATION,
        "layout_version": (
            drilldown_zoom_figures.DRILLDOWN_ZOOM_FIGURE_LAYOUT_VERSION
        ),
    }
    if outlier_candidate is not None:
        metadata["outlier_candidate"] = outlier_candidate
    return metadata


def _drilldown_zoom_outlier_candidate_metadata():
    """Build one exact detector-provenance record matching a plot overlay."""
    return {
        "request_token": "request-1",
        "detector_version": "detector-v1",
        "candidate_signature": "candidate-1",
        "representative_utc": "2026-07-01T06:02:00Z",
        "representative_delta_snr_db": 9.0,
        "event_start_utc": "2026-07-01T06:00:00Z",
        "event_end_utc": "2026-07-01T06:04:00Z",
        "pre_flank_start_utc": "2026-07-01T00:00:00Z",
        "pre_flank_end_utc": "2026-07-01T05:50:00Z",
        "post_flank_start_utc": "2026-07-01T06:14:00Z",
        "post_flank_end_utc": "2026-07-01T12:00:00Z",
        "local_baseline_db": 1.0,
        "pre_baseline_db": 0.5,
        "post_baseline_db": 1.5,
        "robust_spread_db": 2.0,
        "robust_spread_method": "mad",
        "robust_z": 4.5,
        "minimum_robust_z": 4.0,
        "minimum_departure_db": 6.0,
    }


def _delta_snr_outlier_export_contract(*, populated=True, empty=False):
    """Build valid canonical outlier tables and their registration metadata."""
    event_rows = []
    evidence_rows = []
    if not empty:
        event_rows = [
            {
                "event_id": "E0001",
                "combined_event_class": "spot_impulse",
                "event_first_evidence_utc": "2021-06-03T03:38:00Z",
                "event_last_evidence_utc": "2021-06-03T03:38:00Z",
                "cross_path_context": "path_specific",
                "departure_direction": "positive",
                "qualifying_path_count": 1,
                "path_event_id": "E0001-P01-01",
                "path_number": 1,
                "path_occurrence": 1,
                "path": "DC0DX (JO31LK)",
                "callsign": "DC0DX",
                "locator": "JO31LK",
                "direction": "ENE",
                "path_event_class": "spot_impulse",
                "path_first_evidence_utc": "2021-06-03T03:38:00Z",
                "path_last_evidence_utc": "2021-06-03T03:38:00Z",
                "paired_unit_type": "joint_spot",
                "paired_unit_count": 1,
                "first_to_last_span_minutes": 0.0,
                "median_evidence_interval_minutes": None,
                "largest_gap_minutes": None,
                "expected_local_delta_snr_db": 1.4,
                "observed_median_delta_snr_db": 6.4,
                "largest_single_unit_departure_db": 5.0,
                "path_robust_z_score": 6.745,
                "pre_event_baseline_delta_snr_db": 1.2,
                "post_event_baseline_delta_snr_db": 1.6,
                "absolute_pre_post_baseline_difference_db": 0.4,
                "agreeing_paired_unit_count": 1,
                "paired_unit_sign_agreement_fraction": 1.0,
                "decode_edge_warning": False,
                "decode_edge_warning_reason": None,
                "nearby_joint_unit_count": 2,
                "nearby_target_only_unit_count": 0,
                "nearby_reference_only_unit_count": 0,
            }
        ]
        evidence_rows = [
            {
                "event_id": "E0001",
                "event_first_evidence_utc": "2021-06-03T03:38:00Z",
                "event_last_evidence_utc": "2021-06-03T03:38:00Z",
                "path_event_id": "E0001-P01-01",
                "path": "DC0DX (JO31LK)",
                "callsign": "DC0DX",
                "locator": "JO31LK",
                "direction": "ENE",
                "path_event_class": "spot_impulse",
                "paired_unit_type": "joint_spot",
                "unit_sequence": 1,
                "utc": "2021-06-03T03:38:00Z",
                "target_snr_db": -24.0,
                "corrected_reference_snr_db": -30.4,
                "delta_snr_db": 6.4,
                "expected_local_delta_snr_db": 1.4,
                "departure_from_local_baseline_db": 5.0,
                "cycle_robust_z_score": 6.745,
                "meets_strong_anchor_gates": True,
                "reported_boundary": "start_and_end",
            }
        ]
    tables = DeltaSnrOutlierExportTables(
        event_paths=pd.DataFrame(event_rows, columns=OUTLIER_EVENT_PATH_COLUMNS),
        paired_evidence=pd.DataFrame(
            evidence_rows,
            columns=OUTLIER_PAIRED_EVIDENCE_COLUMNS,
        ),
    )
    populated_count = 1 if populated else 0
    metadata = {
        "schema_version": 1,
        "result_status": (
            "candidates"
            if not empty
            else "no_candidates"
            if populated
            else "insufficient_paired_evidence"
        ),
        "candidate_signature": "candidate-signature",
        "detection_resolution": "native-paired-unit",
        "event_count": 0 if empty else 1,
        "path_event_count": 0 if empty else 1,
        "unique_qualifying_path_count": 0 if empty else 1,
        "paired_evidence_row_count": 0 if empty else 1,
        "populated_paired_unit_count": populated_count,
        "evaluable_paired_unit_count": populated_count,
        "abstained_paired_unit_count": 0,
        "tables": {
            "event_paths": OUTLIER_EVENT_PATHS_TABLE_FILENAME,
            "paired_evidence": OUTLIER_PAIRED_EVIDENCE_TABLE_FILENAME,
        },
    }
    return tables, metadata


def _create_registered_export_artifacts(tmp_path, *, analysis_id="RX_ABS"):
    """Create one exact registered evidence/map artifact triplet for tests."""
    state = {"run_id": 17}
    artifact_paths = {
        artifact_kind: session_artifact_path(
            tmp_path,
            state,
            run_id=17,
            analysis_id=analysis_id,
            artifact_kind=artifact_kind,
        )
        for artifact_kind in ("spots", "map_stations", "map_segments")
    }
    for artifact_path in artifact_paths.values():
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_bytes(b"test artifact")
        register_session_artifact(state, artifact_path)
    return state, artifact_paths


def _map_export_test_block(artifact_paths):
    """Return one complete Success map-export recipe for artifact tests."""
    analysis_context = AnalysisContext(
        callsign="TARGET",
        qth="JN47",
        band="20m",
    )
    return {
        "analysis_id": "RX_ABS",
        "title": "RX Performance",
        "is_compare": False,
        "is_sequential": False,
        "analysis_kind": "opportunity",
        "map_context": {
            "parquet_path": str(artifact_paths["spots"]),
            "map_data_artifacts": {
                "schema_version": results_export.MAP_DATA_ARTIFACT_SCHEMA_VERSION,
                "analysis_id": "RX_ABS",
                "is_compare": False,
                "is_sequential": False,
                "analysis_kind": "opportunity",
                "station_rows_path": str(artifact_paths["map_stations"]),
                "segment_rows_path": str(artifact_paths["map_segments"]),
            },
            "start_t": "2026-07-01T00:00:00Z",
            "end_t": "2026-07-02T00:00:00Z",
            "max_peer_distance_km": 10000,
            "base_min_stations": 1,
            "lat_0": 50.0,
            "lon_0": 5.0,
            "analysis_context": analysis_context.to_dict(),
            "presentation_context": {
                "language": "en",
                "theme": "dark",
                "solar_label": "All",
            },
        },
    }


class _FooterColumn:
    """Minimal context-manager column used by footer rendering tests."""

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


class _FooterPopover(_FooterColumn):
    """Minimal open-state popover used by footer rendering tests."""

    def __init__(self, is_open=False):
        self.open = bool(is_open)


def test_selected_compare_bin_is_recorded_without_retired_view_metadata(monkeypatch):
    """Fingerprint the shared dual-panel bin without exporting dead toggle state."""
    monkeypatch.setattr(
        results_export,
        "st",
        SimpleNamespace(session_state={"lang": "en"}),
    )
    block = {
        "analysis_id": "RX_COMPARE",
        "mode_folder": results_export.BENCHMARK_EXPORT_FOLDER,
        "database_source": "wspr_live",
        "evidence_time_bin": "1h",
        "selected_evidence_figure_recipe": {
            "kind": "selected_benchmark_temporal",
        },
    }
    one_hour_blocks = {"RX_COMPARE": block}
    six_hour_blocks = {
        "RX_COMPARE": {
            **block,
            "evidence_time_bin": "6h",
        }
    }

    one_hour_metadata = results_export._build_run_metadata(
        one_hour_blocks,
        {"settings": {}},
    )
    six_hour_metadata = results_export._build_run_metadata(
        six_hour_blocks,
        {"settings": {}},
    )

    assert one_hour_metadata["result_blocks"][0]["evidence_time_bin"] == "1h"
    assert six_hour_metadata["result_blocks"][0]["evidence_time_bin"] == "6h"
    assert "selected_evidence_time_view" not in (
        one_hour_metadata["result_blocks"][0]
    )
    assert "selected_evidence_time_view" not in (
        six_hour_metadata["result_blocks"][0]
    )
    assert one_hour_metadata["export_signature"] != six_hour_metadata[
        "export_signature"
    ]


def test_show_zero_target_is_recorded_and_changes_export_signature(monkeypatch):
    """Invalidate prepared Success exports when zero-Target visibility changes."""
    monkeypatch.setattr(
        results_export,
        "st",
        SimpleNamespace(session_state={"lang": "en"}),
    )
    hidden_block = {
        "analysis_id": "RX_ABS",
        "mode_folder": results_export.PERFORMANCE_EXPORT_FOLDER,
        "database_source": "wspr_live",
        "show_zero_target": False,
    }
    shown_block = {**hidden_block, "show_zero_target": True}

    metadata = results_export._build_run_metadata(
        {"RX_ABS": shown_block},
        {"settings": {}},
    )

    assert metadata["result_blocks"][0]["show_zero_target"] is True
    assert results_export._export_signature(
        {"RX_ABS": hidden_block}
    ) != results_export._export_signature({"RX_ABS": shown_block})


def test_temporal_snr_render_version_changes_export_signature(monkeypatch):
    """Invalidate prepared ZIPs when temporal SNR rendering changes on reload."""
    blocks = {
        "RX_ABS": {
            "analysis_id": "RX_ABS",
            "mode_folder": results_export.PERFORMANCE_EXPORT_FOLDER,
            "database_source": "wspr_live",
        }
    }

    monkeypatch.setattr(results_export, "TEMPORAL_SNR_EXPORT_RENDER_VERSION", 2)
    version_two_signature = results_export._export_signature(blocks)
    monkeypatch.setattr(results_export, "TEMPORAL_SNR_EXPORT_RENDER_VERSION", 3)

    assert len(version_two_signature) == 64
    assert version_two_signature != results_export._export_signature(blocks)


def test_temporal_evidence_layout_version_changes_export_signature(monkeypatch):
    """Invalidate prepared ZIPs when the shared temporal layout changes."""
    blocks = {
        "RX_ABS": {
            "analysis_id": "RX_ABS",
            "mode_folder": results_export.PERFORMANCE_EXPORT_FOLDER,
            "database_source": "wspr_live",
        }
    }

    monkeypatch.setattr(results_export, "TEMPORAL_EVIDENCE_LAYOUT_VERSION", 1)
    version_one_signature = results_export._export_signature(blocks)
    monkeypatch.setattr(results_export, "TEMPORAL_EVIDENCE_LAYOUT_VERSION", 2)

    assert len(version_one_signature) == 64
    assert version_one_signature != results_export._export_signature(blocks)


def test_success_distance_render_version_changes_export_signature(monkeypatch):
    """Invalidate prepared ZIPs when Success distance rendering changes."""
    blocks = {
        "RX_ABS": {
            "analysis_id": "RX_ABS",
            "mode_folder": results_export.PERFORMANCE_EXPORT_FOLDER,
            "database_source": "wspr_live",
        }
    }

    monkeypatch.setattr(
        results_export,
        "PERFORMANCE_DISTANCE_EXPORT_RENDER_VERSION",
        2,
    )
    version_two_signature = results_export._export_signature(blocks)
    monkeypatch.setattr(
        results_export,
        "PERFORMANCE_DISTANCE_EXPORT_RENDER_VERSION",
        3,
    )

    assert len(version_two_signature) == 64
    assert version_two_signature != results_export._export_signature(blocks)

    compare_blocks = {
        "RX_COMPARE": {
            "analysis_id": "RX_COMPARE",
            "mode_folder": results_export.BENCHMARK_EXPORT_FOLDER,
            "database_source": "wspr_live",
        }
    }
    compare_signature = results_export._export_signature(compare_blocks)
    monkeypatch.setattr(
        results_export,
        "PERFORMANCE_DISTANCE_EXPORT_RENDER_VERSION",
        4,
    )
    assert compare_signature == results_export._export_signature(compare_blocks)


def test_temporal_iqr_band_alpha_changes_export_signature(monkeypatch):
    """Invalidate prepared ZIPs when configured IQR shading changes."""
    blocks = {
        "RX_COMPARE": {
            "analysis_id": "RX_COMPARE",
            "mode_folder": results_export.BENCHMARK_EXPORT_FOLDER,
            "database_source": "wspr_live",
        }
    }

    monkeypatch.setattr(results_export, "TEMPORAL_IQR_BAND_ALPHA", 0.10)
    ten_percent_signature = results_export._export_signature(blocks)
    monkeypatch.setattr(results_export, "TEMPORAL_IQR_BAND_ALPHA", 0.15)

    assert len(ten_percent_signature) == 64
    assert ten_percent_signature != results_export._export_signature(blocks)


def test_export_signature_is_path_free_and_tracks_artifact_changes(
    tmp_path,
    monkeypatch,
):
    """Hash private artifact locations while retaining artifact invalidation."""
    evidence_path = tmp_path / "private_raw_path_token.parquet"
    station_path = tmp_path / "private_station_path_token.parquet"
    segment_path = tmp_path / "private_segment_path_token.parquet"
    replacement_evidence_path = tmp_path / "replacement_raw_token.parquet"
    for artifact_path in (
        evidence_path,
        station_path,
        segment_path,
        replacement_evidence_path,
    ):
        artifact_path.write_bytes(b"artifact")
    map_context = {
        "parquet_path": str(evidence_path),
        "map_data_artifacts": {
            "schema_version": results_export.MAP_DATA_ARTIFACT_SCHEMA_VERSION,
            "analysis_id": "RX_ABS",
            "is_compare": False,
            "is_sequential": False,
            "analysis_kind": "opportunity",
            "station_rows_path": str(station_path),
            "segment_rows_path": str(segment_path),
        },
        "max_peer_distance_km": 10000,
    }
    block = {
        "analysis_id": "RX_ABS",
        "mode_folder": results_export.PERFORMANCE_EXPORT_FOLDER,
        "database_source": "wspr_live",
        "map_context": map_context,
    }
    blocks = {"RX_ABS": block}
    monkeypatch.setattr(
        results_export,
        "st",
        SimpleNamespace(session_state={"lang": "en"}),
    )

    signature = results_export._export_signature(blocks)
    metadata_text = json.dumps(
        results_export._build_run_metadata(blocks, {"settings": {}}),
        sort_keys=True,
    )

    assert len(signature) == 64
    assert int(signature, 16) >= 0
    for artifact_path in (evidence_path, station_path, segment_path):
        assert str(artifact_path) not in metadata_text
        assert artifact_path.name not in metadata_text

    path_changed_block = {
        **block,
        "map_context": {
            **map_context,
            "parquet_path": str(replacement_evidence_path),
        },
    }
    assert signature != results_export._export_signature(
        {"RX_ABS": path_changed_block}
    )

    os.utime(station_path, (1_000_000_000, 1_000_000_000))
    assert signature == results_export._export_signature(blocks)

    station_path.write_bytes(b"artifact changed")
    assert signature != results_export._export_signature(blocks)


def test_run_metadata_records_correction_mode_and_numeric_value(monkeypatch):
    """Preserve operator correction provenance beside its scientific value."""
    monkeypatch.setattr(
        results_export,
        "st",
        SimpleNamespace(session_state={"lang": "en"}),
    )
    metadata = results_export._build_run_metadata(
        {
            "RX_COMPARE": {
                "analysis_id": "RX_COMPARE",
                "mode_folder": results_export.BENCHMARK_EXPORT_FOLDER,
                "database_source": "wspr_live",
            }
        },
        {
            "settings": {
                "comparison_parameters": {
                    "mode": "hardware_ab",
                    "snr_correction_mode": "establish_offset",
                    "snr_correction_db": 0.0,
                }
            }
        },
    )

    assert metadata["benchmark_snr_correction_mode"] == "establish_offset"
    assert metadata["benchmark_snr_correction_db"] == 0.0


def test_run_metadata_records_only_the_canonical_absolute_time_window(monkeypatch):
    """Keep result metadata endpoints identical to the embedded config."""
    monkeypatch.setattr(
        results_export,
        "st",
        SimpleNamespace(session_state={"lang": "en"}),
    )
    time_selection = {
        "start_utc": "2026-07-01T00:00Z",
        "end_utc": "2026-07-02T00:00Z",
    }

    metadata = results_export._build_run_metadata(
        {
            "RX_ABS": {
                "analysis_id": "RX_ABS",
                "mode_folder": results_export.PERFORMANCE_EXPORT_FOLDER,
                "database_source": "wspr_live",
            }
        },
        {
            "settings": {
                "core_parameters": {
                    "time_selection": time_selection,
                },
            }
        },
    )

    assert metadata["time_window"] == time_selection


def test_run_metadata_rejects_mixed_database_sources(monkeypatch):
    monkeypatch.setattr(
        results_export,
        "st",
        SimpleNamespace(session_state={"lang": "en"}),
    )
    blocks = {
        "RX_COMP": {
            "analysis_id": "RX_COMP",
            "mode_folder": results_export.BENCHMARK_EXPORT_FOLDER,
            "database_source": "wspr_live",
        },
        "RX_ABS": {
            "analysis_id": "RX_ABS",
            "mode_folder": results_export.PERFORMANCE_EXPORT_FOLDER,
            "database_source": "wd2",
        },
    }

    with pytest.raises(ValueError, match="share one database source"):
        results_export._build_run_metadata(blocks, {"settings": {}})


def test_run_metadata_rejects_missing_database_provenance(monkeypatch):
    monkeypatch.setattr(
        results_export,
        "st",
        SimpleNamespace(session_state={"lang": "en"}),
    )

    with pytest.raises(ValueError, match="must record one database source"):
        results_export._build_run_metadata(
            {
                "RX_ABS": {
                    "analysis_id": "RX_ABS",
                    "mode_folder": results_export.PERFORMANCE_EXPORT_FOLDER,
                }
            },
            {"settings": {}},
        )


@pytest.mark.parametrize("is_prepared", (False, True))
def test_results_footer_always_renders_redundant_save_control(
    monkeypatch,
    is_prepared,
):
    """Keep Save Config beside both Prepare and Download Prepared states."""
    session_state = {}
    if is_prepared:
        session_state.update(
            {
                results_export.EXPORT_ZIP_SIGNATURE_KEY: "current-signature",
                results_export.EXPORT_ZIP_BYTES_KEY: b"zip",
                results_export.EXPORT_ZIP_FILENAME_KEY: "results.zip",
            }
        )
    captured = {
        "columns": None,
        "save_calls": [],
        "share_popovers": [],
        "downloads": [],
        "events": [],
    }
    fake_streamlit = SimpleNamespace(
        session_state=session_state,
        markdown=lambda body, **_kwargs: captured["events"].append(
            ("markdown", body)
        ),
        columns=lambda widths, **kwargs: (
            captured["events"].append(("columns", widths))
            or captured.update(columns=(widths, kwargs))
            or (_FooterColumn(), _FooterColumn(), _FooterColumn())
        ),
        popover=lambda *args, **kwargs: (
            captured["share_popovers"].append((args, kwargs))
            or _FooterPopover()
        ),
        button=lambda *_args, **_kwargs: False,
        download_button=lambda label, **kwargs: captured["downloads"].append(
            (label, kwargs)
        ),
    )
    monkeypatch.setattr(results_export, "st", fake_streamlit)
    monkeypatch.setattr(
        results_export,
        "_ensure_current_export_state",
        lambda: {"RX_ABS": {"mode_folder": results_export.PERFORMANCE_EXPORT_FOLDER}},
    )
    monkeypatch.setattr(
        results_export,
        "_export_signature",
        lambda _blocks: "current-signature",
    )
    monkeypatch.setattr(
        results_export,
        "render_config_save_control",
        lambda **kwargs: captured["save_calls"].append(kwargs),
    )

    results_export.render_download_all_results(T["en"])

    assert captured["columns"] == (
        [0.5, 0.25, 0.25],
        {"gap": "large", "vertical_alignment": "center"},
    )
    assert captured["save_calls"] == [
        {
            "popover_key": "config_save_results_trigger",
            "form_scope": "results",
        }
    ]
    assert bool(captured["downloads"]) is is_prepared
    assert captured["share_popovers"] == [
        (
            (T["en"]["btn_share_analysis"],),
            {
                "icon": ":material/share:",
                "type": "primary",
                "width": "stretch",
                "key": "share_analysis_results_trigger",
                "on_change": "rerun",
            },
        )
    ]
    heading_events = [
        (index, body)
        for index, (kind, body) in enumerate(captured["events"])
        if kind == "markdown"
        and "<h3 class='result-utility-title'>Download Evidence</h3>" in body
    ]
    assert len(heading_events) == 1
    columns_index = next(
        index
        for index, (kind, _value) in enumerate(captured["events"])
        if kind == "columns"
    )
    assert heading_events[0][0] < columns_index


def test_open_share_popover_builds_canonical_url_and_localized_browser_copy(
    monkeypatch,
):
    """Build Share Analysis content only for an open completed-result popover."""
    session_state = {
        "run_id": 42,
        "val_callsign": "dl1mks",
        "val_analysis_direction": "rx",
        "val_comp_mode": "hardware_ab",
        "val_band": "20m",
    }
    browser_calls = []
    build_calls = []
    fake_streamlit = SimpleNamespace(
        session_state=session_state,
        markdown=lambda *_args, **_kwargs: None,
        columns=lambda *_args, **_kwargs: (
            _FooterColumn(),
            _FooterColumn(),
            _FooterColumn(),
        ),
        button=lambda *_args, **_kwargs: False,
        download_button=lambda *_args, **_kwargs: None,
        popover=lambda *_args, **_kwargs: _FooterPopover(is_open=True),
    )
    monkeypatch.setattr(results_export, "st", fake_streamlit)
    monkeypatch.setattr(
        results_export,
        "_ensure_current_export_state",
        lambda: {
            "RX_COMPARE": {
                "mode_folder": results_export.BENCHMARK_EXPORT_FOLDER
            }
        },
    )
    monkeypatch.setattr(
        results_export,
        "_export_signature",
        lambda _blocks: "share-signature",
    )
    monkeypatch.setattr(
        results_export,
        "render_config_save_control",
        lambda **_kwargs: None,
    )
    monkeypatch.setattr(
        results_export,
        "build_share_url",
        lambda state: (
            build_calls.append(state)
            or "https://wspradar.org/?v=1&run=1#wspradar-results-inspection"
        ),
    )
    monkeypatch.setattr(
        results_export,
        "render_share_analysis_browser",
        lambda **kwargs: browser_calls.append(kwargs),
    )

    results_export.render_download_all_results(T["en"])

    assert build_calls == [session_state]
    assert browser_calls == [
        {
            "share_url": (
                "https://wspradar.org/?v=1&run=1"
                "#wspradar-results-inspection"
            ),
            "title": (
                "WSPRadar analysis: DL1MKS RX Hardware A/B on 20m"
            ),
            "message": T["en"]["share_analysis_message"],
            "labels": {
                "url_field": T["en"]["share_url_field"],
                "copy_link": T["en"]["share_copy_link"],
                "copied": T["en"]["share_copied"],
                "manual_copy": T["en"]["share_manual_copy"],
                "native_share": T["en"]["share_native"],
                "native_share_failed": T["en"]["share_native_failed"],
                "email": T["en"]["share_email"],
                "whatsapp": T["en"]["share_whatsapp"],
                "x": T["en"]["share_x"],
                "facebook": T["en"]["share_facebook"],
                "linkedin": T["en"]["share_linkedin"],
            },
            "key": "share_analysis_browser_42",
        }
    ]


def test_results_footer_omits_heading_without_exportable_results(monkeypatch):
    """Do not show an orphan Download Evidence section for an empty run."""
    markdown_calls = []
    monkeypatch.setattr(
        results_export,
        "st",
        SimpleNamespace(
            session_state={},
            markdown=lambda body, **_kwargs: markdown_calls.append(body),
        ),
    )
    monkeypatch.setattr(
        results_export,
        "_ensure_current_export_state",
        lambda: {},
    )

    results_export.render_download_all_results(T["en"])

    assert markdown_calls == []


def test_segment_temporal_figure_uses_its_distinct_export_recipe(monkeypatch):
    """Keep segment temporal and selected-station figure recipes independent."""
    temporal_recipe = {"kind": "segment_benchmark_temporal", "time_bin": "6h"}
    fake_figure = object()
    disposed_figures = []

    monkeypatch.setattr(
        evidence_figures,
        "render_segment_temporal_evidence_export_figure",
        lambda recipe: fake_figure if recipe is temporal_recipe else None,
    )
    monkeypatch.setattr(
        results_export,
        "figure_to_png_bytes",
        lambda figure, *, paper_theme: b"temporal-png"
        if figure is fake_figure and paper_theme
        else b"",
    )
    monkeypatch.setattr(
        results_export,
        "dispose_matplotlib_figure",
        disposed_figures.append,
    )

    rendered = results_export._render_inspector_png_for_block(
        {
            "segment_temporal_evidence_figure_recipe": temporal_recipe,
            "selected_evidence_figure_recipe": {"kind": "selected"},
        },
        "figure_segment_temporal_evidence.png",
    )

    assert rendered == b"temporal-png"
    assert disposed_figures == [fake_figure]


@pytest.mark.parametrize(
    ("figure_name", "recipe_key", "renderer_name"),
    DRILLDOWN_ZOOM_RENDER_CASES,
)
def test_drilldown_zoom_exports_dispatch_exact_registered_recipes(
    monkeypatch,
    figure_name,
    recipe_key,
    renderer_name,
):
    """Render each focused figure through its chronological-only adapter."""
    from ui.plots import drilldown_zoom_figures

    recipe = {"kind": recipe_key, "time_bin": "2m"}
    fake_figure = object()
    received_recipes = []
    disposed_figures = []
    monkeypatch.setattr(
        drilldown_zoom_figures,
        renderer_name,
        lambda received: received_recipes.append(received) or fake_figure,
    )
    monkeypatch.setattr(
        results_export,
        "figure_to_png_bytes",
        lambda figure, *, paper_theme: (
            b"focused-png" if figure is fake_figure and paper_theme else b""
        ),
    )
    monkeypatch.setattr(
        results_export,
        "dispose_matplotlib_figure",
        disposed_figures.append,
    )

    rendered = results_export._render_inspector_png_for_block(
        {recipe_key: recipe},
        figure_name,
    )

    assert rendered == b"focused-png"
    assert received_recipes == [recipe]
    assert disposed_figures == [fake_figure]


def test_high_resolution_compare_exports_receive_exact_registered_marker_recipes(
    monkeypatch,
):
    """Dispatch the same segment and selected candidate payloads to paper PNGs."""
    segment_markers = {"candidate_signature": "segment", "markers": [1]}
    selected_markers = {"candidate_signature": "selected", "markers": [2]}
    segment_recipe = {
        "kind": "segment_benchmark_temporal",
        "delta_snr_outlier_markers": segment_markers,
    }
    selected_recipe = {
        "kind": "selected_benchmark_temporal",
        "delta_snr_outlier_markers": selected_markers,
    }
    received_recipes = []
    figures = [object(), object()]
    monkeypatch.setattr(
        evidence_figures,
        "render_segment_temporal_evidence_export_figure",
        lambda recipe: received_recipes.append(recipe) or figures[0],
    )
    monkeypatch.setattr(
        evidence_figures,
        "render_selected_evidence_export_figure",
        lambda recipe: received_recipes.append(recipe) or figures[1],
    )
    monkeypatch.setattr(
        results_export,
        "figure_to_png_bytes",
        lambda figure, *, paper_theme: (
            b"segment" if figure is figures[0] else b"selected"
        )
        if paper_theme
        else b"",
    )
    monkeypatch.setattr(
        results_export,
        "dispose_matplotlib_figure",
        lambda _figure: None,
    )
    block = {
        "segment_temporal_evidence_figure_recipe": segment_recipe,
        "selected_evidence_figure_recipe": selected_recipe,
    }

    assert results_export._render_inspector_png_for_block(
        block,
        "figure_segment_temporal_evidence.png",
    ) == b"segment"
    assert results_export._render_inspector_png_for_block(
        block,
        "figure_selected_station_evidence.png",
    ) == b"selected"
    assert received_recipes == [segment_recipe, selected_recipe]
    assert received_recipes[0]["delta_snr_outlier_markers"] is segment_markers
    assert received_recipes[1]["delta_snr_outlier_markers"] is selected_markers


def test_export_marker_signature_tracks_payload_even_if_declared_hash_is_stale():
    """Invalidate prepared ZIP identity when exact marker coordinates change."""
    marker_recipe = {
        "schema_version": 2,
        "detector_version": "native-residual-episode-v1",
        "detection_resolution": "native-paired-unit",
        "candidate_count": 1,
        "candidate_signature": "declared-signature",
        "legend_label": "candidate",
        "markers": [
            {
                "callsign": "A1AAA",
                "locator": "AA00",
                "marker_utc_ns": 1_782_864_600_000_000_000,
                "marker_delta_snr_db": 7.5,
                "episode_start_utc_ns": 1_782_864_480_000_000_000,
                "episode_end_utc_ns": 1_782_864_720_000_000_000,
                "event_kind": "spot_impulse",
            }
        ],
    }
    first_recipe = {"delta_snr_outlier_markers": marker_recipe}
    changed_marker_recipe = {
        **marker_recipe,
        "markers": [
            {
                **marker_recipe["markers"][0],
                "marker_delta_snr_db": 8.0,
            }
        ],
    }
    second_recipe = {"delta_snr_outlier_markers": changed_marker_recipe}

    first_signature = results_export._delta_snr_outlier_recipe_signature(
        first_recipe
    )
    assert first_signature == {
        **{
            key: marker_recipe[key]
            for key in (
                "schema_version",
                "detector_version",
                "detection_resolution",
                "candidate_count",
                "candidate_signature",
                "legend_label",
            )
        },
        "detection_policy_signature": None,
        "markers": [
            {
                **marker_recipe["markers"][0],
                "detection_policy_signature": None,
            }
        ],
    }
    assert first_signature != (
        results_export._delta_snr_outlier_recipe_signature(second_recipe)
    )


@pytest.mark.parametrize(
    ("identity_key", "invalid_value"),
    [
        ("schema_version", 999),
        ("analysis_id", "TX_ABS"),
        ("is_compare", True),
        ("is_sequential", True),
        ("analysis_kind", "comparison"),
    ],
)
def test_map_export_rejects_mismatched_compact_artifact_identity(
    monkeypatch,
    identity_key,
    invalid_value,
):
    """Never reinterpret a compact aggregate under another scientific mode."""
    map_artifacts = {
        "schema_version": results_export.MAP_DATA_ARTIFACT_SCHEMA_VERSION,
        "analysis_id": "RX_ABS",
        "is_compare": False,
        "is_sequential": False,
        "analysis_kind": "opportunity",
        "station_rows_path": "map_stations_RX_ABS.parquet",
        "segment_rows_path": "map_segments_RX_ABS.parquet",
    }
    map_artifacts[identity_key] = invalid_value
    monkeypatch.setattr(
        results_export,
        "read_map_data_artifacts",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("Invalid map identity must fail before artifact reads")
        ),
    )
    block = {
        "analysis_id": "RX_ABS",
        "is_compare": False,
        "is_sequential": False,
        "analysis_kind": "opportunity",
        "map_context": {"map_data_artifacts": map_artifacts},
    }

    with pytest.raises(
        results_export.ExportArtifactUnavailableError,
        match="identity no longer matches",
    ):
        results_export._render_map_png_for_block(block)


@pytest.mark.parametrize(
    ("failure_mode", "expected_message"),
    [
        ("unregistered", "not registered"),
        ("out_of_scope", "outside the current session namespace"),
    ],
)
def test_map_export_registration_rejects_unowned_artifact_paths(
    tmp_path,
    monkeypatch,
    failure_mode,
    expected_message,
):
    """Reject compact map recipes not owned by the active UI session."""
    state, artifact_paths = _create_registered_export_artifacts(tmp_path)
    if failure_mode == "unregistered":
        rejected_path = artifact_paths["map_stations"].resolve()
        state[SESSION_ARTIFACT_PATHS_KEY] = [
            registered_path
            for registered_path in state[SESSION_ARTIFACT_PATHS_KEY]
            if Path(registered_path) != rejected_path
        ]
    else:
        outside_path = tmp_path / "outside" / "map_stations_RX_ABS.parquet"
        outside_path.parent.mkdir(parents=True)
        outside_path.write_bytes(b"outside")
        artifact_paths["map_stations"] = outside_path
        state[SESSION_ARTIFACT_PATHS_KEY].append(str(outside_path.resolve()))
    monkeypatch.setattr(
        results_export,
        "st",
        SimpleNamespace(session_state=state),
    )
    monkeypatch.setattr(results_export, "CACHE_DIR", tmp_path)

    with pytest.raises(ValueError, match=expected_message):
        results_export.register_map_export_context(
            analysis={
                "id": "RX_ABS",
                "title": "RX Performance",
                "is_compare": False,
                "is_sequential": False,
                "analysis_kind": "opportunity",
            },
            parquet_path=artifact_paths["spots"],
            map_data_paths=results_export.MapDataArtifactPaths(
                station_rows_path=artifact_paths["map_stations"],
                segment_rows_path=artifact_paths["map_segments"],
            ),
            start_t="2026-07-01T00:00:00Z",
            end_t="2026-07-02T00:00:00Z",
            max_peer_distance_km=10000,
            base_min_stations=1,
            lat_0=50.0,
            lon_0=5.0,
            analysis_context=SimpleNamespace(to_dict=lambda: {}),
            presentation_context=SimpleNamespace(
                language="en",
                theme="dark",
                solar_label="All",
            ),
            database_source="wspr_live",
        )


@pytest.mark.parametrize("failure_mode", ["deleted", "corrupt"])
def test_map_export_aborts_when_required_compact_aggregate_is_unusable(
    tmp_path,
    monkeypatch,
    failure_mode,
):
    """Never silently omit the map when its registered aggregate is unusable."""
    state, artifact_paths = _create_registered_export_artifacts(tmp_path)
    if failure_mode == "deleted":
        artifact_paths["map_segments"].unlink()
    monkeypatch.setattr(
        results_export,
        "st",
        SimpleNamespace(session_state=state),
    )
    monkeypatch.setattr(results_export, "CACHE_DIR", tmp_path)

    with pytest.raises(
        results_export.ExportArtifactUnavailableError,
        match="run the analysis again",
    ):
        results_export._render_map_png_for_block(
            _map_export_test_block(artifact_paths)
        )


def test_map_export_wraps_renderer_failure_as_actionable_artifact_error(
    tmp_path,
    monkeypatch,
):
    """Convert a compact-recipe render failure into the export UI contract."""
    state, artifact_paths = _create_registered_export_artifacts(tmp_path)
    monkeypatch.setattr(
        results_export,
        "st",
        SimpleNamespace(session_state=state),
    )
    monkeypatch.setattr(results_export, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(
        results_export,
        "read_map_data_artifacts",
        lambda *_args, **_kwargs: SimpleNamespace(marker="compact"),
    )
    monkeypatch.setattr(
        plot_engine,
        "render_map_figure",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            ValueError("invalid compact render recipe")
        ),
    )

    with pytest.raises(
        results_export.ExportArtifactUnavailableError,
        match="could not be rendered",
    ):
        results_export._render_map_png_for_block(
            _map_export_test_block(artifact_paths)
        )


def test_success_temporal_snr_figure_uses_its_separate_export_recipe(
    monkeypatch,
):
    """Render and dispose the standalone Success SNR-deviation export."""
    snr_recipe = {
        "kind": "opportunity_performance_temporal",
        "time_bin": "6h",
    }
    fake_figure = object()
    disposed_figures = []

    monkeypatch.setattr(
        evidence_figures,
        "render_segment_temporal_snr_export_figure",
        lambda recipe: fake_figure if recipe is snr_recipe else None,
    )
    monkeypatch.setattr(
        results_export,
        "figure_to_png_bytes",
        lambda figure, *, paper_theme: b"temporal-snr-png"
        if figure is fake_figure and paper_theme
        else b"",
    )
    monkeypatch.setattr(
        results_export,
        "dispose_matplotlib_figure",
        disposed_figures.append,
    )

    rendered = results_export._render_inspector_png_for_block(
        {
            "segment_temporal_snr_deviation_figure_recipe": snr_recipe,
            "segment_temporal_evidence_figure_recipe": {
                "kind": "opportunity_performance_temporal",
            },
        },
        "figure_segment_temporal_snr_deviation.png",
    )

    assert rendered == b"temporal-snr-png"
    assert disposed_figures == [fake_figure]


@pytest.mark.parametrize(
    (
        "figure_name",
        "renderer_name",
        "recipe_key",
        "title_key",
        "figure_title",
    ),
    COMPARE_COVERAGE_EXPORT_CASES,
)
def test_compare_coverage_figure_uses_its_registered_preview_recipe(
    monkeypatch,
    figure_name,
    renderer_name,
    recipe_key,
    title_key,
    figure_title,
):
    """Render each Compare export from the exact registered preview recipe."""
    recipe_kind = (
        benchmark_evidence_figures.BENCHMARK_SELECTED_PATH_COVERAGE_RECIPE_KIND
        if recipe_key == "selected_station_coverage_figure_recipe"
        else benchmark_evidence_figures.BENCHMARK_TEMPORAL_COVERAGE_RECIPE_KIND
    )
    recipe = {
        "kind": recipe_kind,
        "schema_version": 1,
        "time_bin": "6h",
        title_key: figure_title,
    }
    fake_figure = object()
    disposed_figures = []
    renderer_calls = []

    def render_coverage_recipe(received_recipe):
        renderer_calls.append(received_recipe)
        return fake_figure

    monkeypatch.setattr(
        benchmark_evidence_figures,
        renderer_name,
        render_coverage_recipe,
    )
    monkeypatch.setattr(
        results_export,
        "figure_to_png_bytes",
        lambda figure, *, paper_theme: b"compare-coverage-png"
        if figure is fake_figure and paper_theme
        else b"",
    )
    monkeypatch.setattr(
        results_export,
        "dispose_matplotlib_figure",
        disposed_figures.append,
    )

    rendered = results_export._render_inspector_png_for_block(
        {recipe_key: recipe},
        figure_name,
    )

    assert rendered == b"compare-coverage-png"
    assert renderer_calls == [recipe]
    assert renderer_calls[0] is recipe
    assert disposed_figures == [fake_figure]


@pytest.mark.parametrize(
    "figure_name",
    [
        export_case[0]
        for export_case in COMPARE_COVERAGE_EXPORT_CASES
    ],
)
def test_compare_coverage_export_omits_an_absent_recipe(
    figure_name,
):
    """Omit an inapplicable Compare figure instead of creating an empty file."""
    assert (
        results_export._render_inspector_png_for_block({}, figure_name)
        is None
    )


def test_retired_compare_figures_have_no_export_recipe_or_renderer_path():
    """Keep removed delta-change and path-consistency artifacts unreachable."""
    export_definitions = {
        (figure_name, recipe_key)
        for figure_name, recipe_key, _title_keys in (
            results_export.BENCHMARK_EVIDENCE_FIGURE_EXPORTS
        )
    }
    renderer_source = inspect.getsource(
        results_export._render_inspector_png_for_block
    )
    registration_parameters = inspect.signature(
        results_export.register_inspector_export
    ).parameters

    for figure_name, recipe_key, renderer_name in (
        RETIRED_COMPARE_FIGURE_EXPORTS
    ):
        assert (figure_name, recipe_key) not in export_definitions
        assert recipe_key not in registration_parameters
        assert renderer_name not in renderer_source
        assert (
            results_export._render_inspector_png_for_block(
                {recipe_key: {"kind": "retired"}},
                figure_name,
            )
            is None
        )


def test_register_inspector_export_keeps_compare_coverage_recipes_independent(
    monkeypatch,
):
    """Store both coverage recipes and fingerprint their stable identities."""
    blocks = {}
    recipes = {
        recipe_key: {
            "kind": (
                benchmark_evidence_figures.BENCHMARK_SELECTED_PATH_COVERAGE_RECIPE_KIND
                if recipe_key
                == "selected_station_coverage_figure_recipe"
                else benchmark_evidence_figures.BENCHMARK_TEMPORAL_COVERAGE_RECIPE_KIND
            ),
            "schema_version": 1,
            "time_bin": "6h",
            title_key: figure_title,
        }
        for (
            _figure_name,
            _renderer_name,
            recipe_key,
            title_key,
            figure_title,
        ) in COMPARE_COVERAGE_EXPORT_CASES
    }
    monkeypatch.setattr(
        results_export,
        "_ensure_current_export_state",
        lambda: blocks,
    )
    monkeypatch.setattr(
        results_export,
        "st",
        SimpleNamespace(session_state={"lang": "en"}),
    )

    results_export.register_inspector_export(
        analysis_id="RX_COMPARE",
        selected_segment="Full Range | All Directions",
        selected_distance="Full Range",
        selected_direction="All Directions",
        show_non_joint=False,
        evidence_time_bin="6h",
        segment_evidence_time_bin="6h",
        selected_stations=["OK1FCX (JN79)"],
        translations=T["en"],
        **recipes,
    )

    block = blocks["RX_COMPARE"]
    block.update(
        {
            "mode_folder": results_export.BENCHMARK_EXPORT_FOLDER,
            "database_source": "wspr_live",
        }
    )
    for recipe_key, recipe in recipes.items():
        assert block[recipe_key] is recipe

    metadata = results_export._build_run_metadata(
        blocks,
        {"settings": {}},
    )
    expected_descriptions = {
        figure_name: figure_title
        for (
            figure_name,
            _renderer_name,
            _recipe_key,
            _title_key,
            figure_title,
        ) in COMPARE_COVERAGE_EXPORT_CASES
    }
    assert metadata["result_blocks"][0]["benchmark_evidence_figures"] == (
        expected_descriptions
    )
    assert [
        recipe["filename"]
        for recipe in results_export._benchmark_evidence_recipe_signature(block)
    ] == list(expected_descriptions)
    assert len(metadata["export_signature"]) == 64
    without_selected_coverage = {
        "RX_COMPARE": {
            **block,
            "selected_station_coverage_figure_recipe": None,
        }
    }
    assert results_export._export_signature(blocks) != (
        results_export._export_signature(without_selected_coverage)
    )


def test_register_inspector_export_keeps_all_success_temporal_recipes_independent(
    monkeypatch,
):
    """Keep active-scope and selected-station canvases independently addressable."""
    blocks = {}
    evidence_recipe = {"kind": "opportunity_performance_temporal"}
    snr_recipe = {"kind": "opportunity_performance_temporal"}
    selected_evidence_recipe = {
        "kind": "opportunity_performance_temporal",
        "population_mode": "selected_station",
        "snr_representation": "actual_normalized_snr",
    }
    selected_snr_recipe = dict(selected_evidence_recipe)
    monkeypatch.setattr(
        results_export,
        "_ensure_current_export_state",
        lambda: blocks,
    )

    results_export.register_inspector_export(
        analysis_id="RX_ABS",
        selected_segment="Full Range | All Directions",
        selected_distance="Full Range",
        selected_direction="All Directions",
        show_non_joint=False,
        evidence_time_bin="3h",
        selected_stations=["OK1FCX (JN79)"],
        translations=T["en"],
        segment_temporal_evidence_figure_recipe=evidence_recipe,
        segment_temporal_snr_deviation_figure_recipe=snr_recipe,
        selected_station_snr_evidence_figure_recipe=selected_snr_recipe,
        selected_station_temporal_evidence_figure_recipe=(
            selected_evidence_recipe
        ),
    )

    block = blocks["RX_ABS"]
    assert block["segment_temporal_evidence_figure_recipe"] is (
        evidence_recipe
    )
    assert block[
        "segment_temporal_snr_deviation_figure_recipe"
    ] is snr_recipe
    assert block["selected_station_snr_evidence_figure_recipe"] is (
        selected_snr_recipe
    )
    assert block["selected_station_temporal_evidence_figure_recipe"] is (
        selected_evidence_recipe
    )
    assert block["selected_evidence_figure_recipe"] is None
    assert selected_snr_recipe is not selected_evidence_recipe


def test_register_inspector_export_replaces_and_clears_drilldown_zoom_state(
    monkeypatch,
):
    """Keep one exact mode-specific pair and remove stale focused artifacts."""
    stale_recipe = {"kind": "stale"}
    blocks = {
        "RX_ABS": {
            "analysis_id": "RX_ABS",
            "mode_folder": results_export.PERFORMANCE_EXPORT_FOLDER,
            "drilldown_zoom_metadata": {"stale": True},
            **{
                recipe_key: stale_recipe
                for recipe_key in results_export.DRILLDOWN_ZOOM_RECIPE_KEYS
            },
        }
    }
    snr_recipe = {
        "kind": "drilldown_zoom_performance_native_snr",
        "schema_version": 2,
        "layout_version": (
            drilldown_zoom_figures.DRILLDOWN_ZOOM_FIGURE_LAYOUT_VERSION
        ),
        "time_bin": "native",
        "resolution": drilldown_zoom_figures.DRILLDOWN_ZOOM_NATIVE_RESOLUTION,
        "aggregation": drilldown_zoom_figures.DRILLDOWN_ZOOM_NO_AGGREGATION,
        "snr_title": "Selected Station SNR Evidence, Time Window: x to y UTC",
    }
    temporal_recipe = {
        "kind": "opportunity_performance_temporal",
        "schema_version": 1,
        "time_bin": "2m",
        "evidence_title": (
            "Selected Station Temporal Evidence, Time Window: x to y UTC"
        ),
    }
    monkeypatch.setattr(
        results_export,
        "_ensure_current_export_state",
        lambda: blocks,
    )
    common_arguments = {
        "analysis_id": "RX_ABS",
        "selected_segment": "Full Range | All Directions",
        "selected_distance": "Full Range",
        "selected_direction": "All Directions",
        "show_non_joint": False,
        "evidence_time_bin": "3h",
        "selected_stations": ["OK1FCX (JN79)"],
        "translations": T["en"],
    }

    results_export.register_inspector_export(
        **common_arguments,
        drilldown_zoom_metadata=_drilldown_zoom_metadata(),
        drilldown_zoom_performance_snr_figure_recipe=snr_recipe,
        drilldown_zoom_performance_temporal_figure_recipe=temporal_recipe,
    )

    block = blocks["RX_ABS"]
    assert block["drilldown_zoom_metadata"] == {
        **_drilldown_zoom_metadata(),
        "station": {"callsign": "OK1FCX", "locator": "JN79"},
    }
    assert block["drilldown_zoom_performance_snr_figure_recipe"] is (
        snr_recipe
    )
    assert block["drilldown_zoom_performance_temporal_figure_recipe"] is (
        temporal_recipe
    )
    assert "drilldown_zoom_benchmark_delta_snr_figure_recipe" not in block
    assert "drilldown_zoom_benchmark_coverage_figure_recipe" not in block

    results_export.register_inspector_export(**common_arguments)

    assert "drilldown_zoom_metadata" not in block
    assert all(
        recipe_key not in block
        for recipe_key in results_export.DRILLDOWN_ZOOM_RECIPE_KEYS
    )


def test_drilldown_zoom_registration_rejects_invalid_or_incomplete_contracts():
    """Reject invalid bounds and a lone focused recipe before state mutation."""
    invalid_bounds = _drilldown_zoom_metadata(
        start_utc="2026-07-01T06:00:00Z",
        end_utc="2026-07-01T03:00:00Z",
    )
    with pytest.raises(ValueError, match="after start_utc"):
        results_export._validated_drilldown_zoom_registration(
            metadata=invalid_bounds,
            selected_station_count=1,
            performance_snr_recipe={"kind": "snr"},
            performance_temporal_recipe={"kind": "temporal"},
            benchmark_delta_snr_recipe=None,
            benchmark_coverage_recipe=None,
        )

    with pytest.raises(ValueError, match="both mode-specific"):
        results_export._validated_drilldown_zoom_registration(
            metadata=_drilldown_zoom_metadata(),
            selected_station_count=1,
            performance_snr_recipe={"kind": "snr"},
            performance_temporal_recipe=None,
            benchmark_delta_snr_recipe=None,
            benchmark_coverage_recipe=None,
        )

    performance_recipe_with_overlay = {
        "time_bin": "native",
        "resolution": drilldown_zoom_figures.DRILLDOWN_ZOOM_NATIVE_RESOLUTION,
        "aggregation": drilldown_zoom_figures.DRILLDOWN_ZOOM_NO_AGGREGATION,
        "layout_version": (
            drilldown_zoom_figures.DRILLDOWN_ZOOM_FIGURE_LAYOUT_VERSION
        ),
        "outlier_overlay": {"stale": True},
    }
    with pytest.raises(ValueError, match="cannot carry an outlier overlay"):
        results_export._validated_drilldown_zoom_registration(
            metadata=_drilldown_zoom_metadata(),
            selected_station_count=1,
            performance_snr_recipe=performance_recipe_with_overlay,
            performance_temporal_recipe={"kind": "temporal"},
            benchmark_delta_snr_recipe=None,
            benchmark_coverage_recipe=None,
        )


def test_benchmark_zoom_registration_requires_exact_outlier_overlay_provenance():
    """Bind the exported candidate record to the plotted detector guides."""
    candidate_metadata = _drilldown_zoom_outlier_candidate_metadata()
    overlay = drilldown_zoom_figures.build_drilldown_zoom_outlier_overlay_recipe(
        representative_utc=candidate_metadata["representative_utc"],
        representative_delta_snr_db=(
            candidate_metadata["representative_delta_snr_db"]
        ),
        qualifying_marker_times_utc=[
            candidate_metadata["representative_utc"]
        ],
        qualifying_marker_delta_snr_db=[
            candidate_metadata["representative_delta_snr_db"]
        ],
        candidate_start_utc=candidate_metadata["event_start_utc"],
        candidate_end_utc=candidate_metadata["event_end_utc"],
        native_evidence_unit_minutes=2.0,
        local_baseline_db=candidate_metadata["local_baseline_db"],
        pre_baseline_db=candidate_metadata["pre_baseline_db"],
        post_baseline_db=candidate_metadata["post_baseline_db"],
        pre_flank_start_utc=candidate_metadata["pre_flank_start_utc"],
        pre_flank_end_utc=candidate_metadata["pre_flank_end_utc"],
        post_flank_start_utc=candidate_metadata["post_flank_start_utc"],
        post_flank_end_utc=candidate_metadata["post_flank_end_utc"],
        robust_spread_db=candidate_metadata["robust_spread_db"],
        robust_spread_method=candidate_metadata["robust_spread_method"],
        minimum_robust_z=candidate_metadata["minimum_robust_z"],
        minimum_departure_db=candidate_metadata["minimum_departure_db"],
        labels={
            "marker": "Qualifying candidate unit",
            "focused_episode": "Focused episode",
            "local_baseline": "Expected local Delta SNR",
            "flank_baseline": "Pre/post flank baseline",
            "robust_z": "Robust-z guide |z| = {value:g}",
            "qualifying_robust_z": (
                "Robust-z qualifying threshold |z| = {value:g}"
            ),
            "absolute_departure": (
                "Absolute-departure gate (+/-{value:g} dB)"
            ),
        },
    )
    metric_recipe = (
        drilldown_zoom_figures.build_drilldown_zoom_benchmark_delta_snr_recipe(
            pd.DataFrame(
                {
                    "plot_time": pd.to_datetime(
                        [candidate_metadata["representative_utc"]],
                        utc=True,
                    ),
                    "metric": [
                        candidate_metadata["representative_delta_snr_db"]
                    ],
                }
            ),
            start_utc="2026-07-01T00:00:00Z",
            end_utc="2026-07-01T12:00:00Z",
            title="OK1FCX (JN79) - Time Window: 00:00 to 12:00 UTC",
            panel_title="Delta SNR over Time",
            x_label="Date/Time (UTC)",
            y_label="Delta SNR (dB)",
            empty_text="No paired evidence.",
            evidence_unit_label="Individual Joint Spot",
            is_sequential=False,
            outlier_overlay=overlay,
        )
    )
    metadata = _drilldown_zoom_metadata(
        start_utc="2026-07-01T00:00:00Z",
        end_utc="2026-07-01T12:00:00Z",
        option="outlier_focus",
        origin="outlier_focus",
        outlier_candidate=candidate_metadata,
    )

    validated, mode_folder = (
        results_export._validated_drilldown_zoom_registration(
            metadata=metadata,
            selected_station_count=1,
            performance_snr_recipe=None,
            performance_temporal_recipe=None,
            benchmark_delta_snr_recipe=metric_recipe,
            benchmark_coverage_recipe={"kind": "focused-coverage"},
        )
    )

    assert mode_folder == results_export.BENCHMARK_EXPORT_FOLDER
    assert (
        validated["outlier_candidate"]["candidate_signature"]
        == "candidate-1"
    )
    overlay_signature = (
        results_export._drilldown_zoom_outlier_overlay_signature(overlay)
    )
    assert overlay_signature["qualifying_marker_utc_ns"] == [
        int(pd.Timestamp(candidate_metadata["representative_utc"]).value)
    ]
    assert overlay_signature["qualifying_marker_delta_snr_db"] == [
        candidate_metadata["representative_delta_snr_db"]
    ]
    assert overlay_signature["qualifying_marker_count"] == 1
    assert overlay_signature["native_evidence_unit_width_ns"] == int(
        pd.Timedelta(minutes=2).value
    )

    mismatched_metadata = {
        **metadata,
        "outlier_candidate": {
            **candidate_metadata,
            "local_baseline_db": 1.25,
        },
    }
    with pytest.raises(ValueError, match="overlay disagrees"):
        results_export._validated_drilldown_zoom_registration(
            metadata=mismatched_metadata,
            selected_station_count=1,
            performance_snr_recipe=None,
            performance_temporal_recipe=None,
            benchmark_delta_snr_recipe=metric_recipe,
            benchmark_coverage_recipe={"kind": "focused-coverage"},
        )

    missing_visible_marker_recipe = deepcopy(metric_recipe)
    missing_visible_marker_recipe["outlier_overlay"][
        "qualifying_marker_utc_ns"
    ] = []
    missing_visible_marker_recipe["outlier_overlay"][
        "qualifying_marker_delta_snr_db"
    ] = []
    missing_visible_marker_recipe["outlier_overlay"][
        "qualifying_marker_count"
    ] = 0
    with pytest.raises(ValueError, match="visible representative"):
        results_export._validated_drilldown_zoom_registration(
            metadata=metadata,
            selected_station_count=1,
            performance_snr_recipe=None,
            performance_temporal_recipe=None,
            benchmark_delta_snr_recipe=missing_visible_marker_recipe,
            benchmark_coverage_recipe={"kind": "focused-coverage"},
        )

    invalid_band_recipe = deepcopy(metric_recipe)
    invalid_band_recipe["outlier_overlay"][
        "focused_episode_visual_start_utc_ns"
    ] += 1
    with pytest.raises(ValueError, match="focused-episode band"):
        results_export._validated_drilldown_zoom_registration(
            metadata=metadata,
            selected_station_count=1,
            performance_snr_recipe=None,
            performance_temporal_recipe=None,
            benchmark_delta_snr_recipe=invalid_band_recipe,
            benchmark_coverage_recipe={"kind": "focused-coverage"},
        )


def test_drilldown_zoom_metadata_and_recipe_contract_change_export_signature():
    """Fingerprint exact identity, bounds, origin, bin, layout, and titles."""
    base_block = {
        "analysis_id": "RX_ABS",
        "mode_folder": results_export.PERFORMANCE_EXPORT_FOLDER,
        "database_source": "wspr_live",
        "drilldown_zoom_metadata": results_export._validated_drilldown_zoom_metadata(
            _drilldown_zoom_metadata()
        ),
        "drilldown_zoom_performance_snr_figure_recipe": {
            "kind": "drilldown_zoom_performance_native_snr",
            "schema_version": 2,
            "layout_version": (
                drilldown_zoom_figures.DRILLDOWN_ZOOM_FIGURE_LAYOUT_VERSION
            ),
            "time_bin": "native",
            "resolution": (
                drilldown_zoom_figures.DRILLDOWN_ZOOM_NATIVE_RESOLUTION
            ),
            "aggregation": (
                drilldown_zoom_figures.DRILLDOWN_ZOOM_NO_AGGREGATION
            ),
            "snr_title": "SNR, Time Window: x to y UTC",
        },
        "drilldown_zoom_performance_temporal_figure_recipe": {
            "kind": "opportunity_performance_temporal",
            "schema_version": 1,
            "time_bin": "2m",
            "evidence_title": "Evidence, Time Window: x to y UTC",
        },
    }
    changed_bounds = {
        **base_block,
        "drilldown_zoom_metadata": results_export._validated_drilldown_zoom_metadata(
            _drilldown_zoom_metadata(
                start_utc="2026-07-01T04:00:00Z",
                end_utc="2026-07-01T07:00:00Z",
            )
        ),
    }
    changed_title = {
        **base_block,
        "drilldown_zoom_performance_snr_figure_recipe": {
            **base_block[
                "drilldown_zoom_performance_snr_figure_recipe"
            ],
            "snr_title": "Changed focused SNR title",
        },
    }

    base_signature = results_export._export_signature({"RX_ABS": base_block})
    assert base_signature != results_export._export_signature(
        {"RX_ABS": changed_bounds}
    )
    assert base_signature != results_export._export_signature(
        {"RX_ABS": changed_title}
    )


@pytest.mark.parametrize(
    ("language", "selected_stations", "expected_weighting"),
    [
        ("en", ["K1AAA (FN31)"], "Single selected path"),
        ("de", ["K1AAA (FN31)"], "Ein ausgewählter Funkweg"),
        ("en", [], None),
    ],
)
def test_register_inspector_export_localizes_selected_evidence_weighting(
    monkeypatch,
    language,
    selected_stations,
    expected_weighting,
):
    """Localize descriptive weighting without changing selected identities."""
    blocks = {}
    monkeypatch.setattr(
        results_export,
        "_ensure_current_export_state",
        lambda: blocks,
    )

    results_export.register_inspector_export(
        analysis_id="RX_COMPARE",
        selected_segment="Full Range | All Directions",
        selected_distance="Full Range",
        selected_direction="All Directions",
        show_non_joint=False,
        evidence_time_bin="3h",
        selected_stations=selected_stations,
        translations=T[language],
    )

    block = blocks["RX_COMPARE"]
    assert block["selected_stations"] == selected_stations
    assert block["selected_station_count"] == len(selected_stations)
    assert block["selected_evidence_weighting"] == expected_weighting
    assert "report_delta_snr_outlier_candidates" not in block
    assert "delta_snr_outlier_detector_version" not in block


def test_disabled_outlier_fields_do_not_change_result_metadata_or_signature(
    monkeypatch,
):
    """Keep disabled Compare and Performance export contracts unchanged."""
    monkeypatch.setattr(
        results_export,
        "st",
        SimpleNamespace(session_state={"lang": "en"}),
    )
    base_block = {
        "analysis_id": "RX_ABS",
        "mode_folder": "performance",
        "database_source": "wspr_live",
        "selected_stations": [],
    }
    false_field_block = {
        **base_block,
        "report_delta_snr_outlier_candidates": False,
        "delta_snr_outlier_detector_version": None,
    }

    assert results_export._export_signature(
        {"RX_ABS": base_block}
    ) == results_export._export_signature(
        {"RX_ABS": false_field_block}
    )

    metadata = results_export._build_run_metadata(
        {"RX_ABS": false_field_block},
        {
            "settings": {
                "advanced_parameters": {
                    "report_delta_snr_outlier_candidates": False
                }
            }
        },
    )
    assert (
        "report_delta_snr_outlier_candidates"
        not in metadata["thresholds_and_filters"]
    )
    assert (
        "report_delta_snr_outlier_candidates"
        not in metadata["result_blocks"][0]
    )
    assert (
        "delta_snr_outlier_detector_version"
        not in metadata["result_blocks"][0]
    )


def test_disabled_registration_strips_stale_markers_without_mutating_recipes(
    monkeypatch,
):
    """Make false an authoritative no-marker export boundary."""
    marker_payload = {
        "schema_version": 2,
        "detector_version": "stale-detector",
        "detection_resolution": "native-paired-unit",
        "candidate_count": 1,
        "candidate_signature": "stale-candidate",
        "markers": [{"callsign": "K1AAA", "locator": "FN31"}],
    }
    stale_segment_recipe = {
        "kind": "segment_benchmark_temporal",
        "time_bin": "3h",
        "delta_snr_outlier_markers": marker_payload,
    }
    stale_selected_recipe = {
        "kind": "selected_benchmark_temporal",
        "time_bin": "3h",
        "delta_snr_outlier_markers": marker_payload,
    }
    stale_tables, stale_metadata = _delta_snr_outlier_export_contract()
    disabled_blocks = {
        "RX_COMPARE": {
            "analysis_id": "RX_COMPARE",
            "delta_snr_outlier_export": stale_metadata,
            OUTLIER_EVENT_PATHS_TABLE_FILENAME: stale_tables.event_paths,
            OUTLIER_PAIRED_EVIDENCE_TABLE_FILENAME: (
                stale_tables.paired_evidence
            ),
        }
    }
    clean_blocks = {}
    pending_states = [disabled_blocks, clean_blocks]
    monkeypatch.setattr(
        results_export,
        "_ensure_current_export_state",
        lambda: pending_states.pop(0),
    )

    common_arguments = {
        "analysis_id": "RX_COMPARE",
        "selected_segment": "Full Range | All Directions",
        "selected_distance": "Full Range",
        "selected_direction": "All Directions",
        "show_non_joint": False,
        "evidence_time_bin": "3h",
        "selected_stations": [],
        "translations": T["en"],
    }
    results_export.register_inspector_export(
        **common_arguments,
        segment_temporal_evidence_figure_recipe=stale_segment_recipe,
        selected_evidence_figure_recipe=stale_selected_recipe,
        report_delta_snr_outlier_candidates=False,
        delta_snr_outlier_detector_version="stale-detector",
        delta_snr_outlier_detection_policy=DeltaSnrOutlierDetectionPolicy(
            minimum_departure_db=6.0,
        ),
    )
    results_export.register_inspector_export(
        **common_arguments,
        segment_temporal_evidence_figure_recipe={
            "kind": "segment_benchmark_temporal",
            "time_bin": "3h",
        },
        selected_evidence_figure_recipe={
            "kind": "selected_benchmark_temporal",
            "time_bin": "3h",
        },
    )

    disabled_block = disabled_blocks["RX_COMPARE"]
    assert "delta_snr_outlier_markers" not in disabled_block[
        "segment_temporal_evidence_figure_recipe"
    ]
    assert "delta_snr_outlier_markers" not in disabled_block[
        "selected_evidence_figure_recipe"
    ]
    assert "report_delta_snr_outlier_candidates" not in disabled_block
    assert "delta_snr_outlier_detector_version" not in disabled_block
    assert "delta_snr_outlier_detection_policy" not in disabled_block
    assert "delta_snr_outlier_export" not in disabled_block
    assert OUTLIER_EVENT_PATHS_TABLE_FILENAME not in disabled_block
    assert OUTLIER_PAIRED_EVIDENCE_TABLE_FILENAME not in disabled_block
    assert "delta_snr_outlier_markers" in stale_segment_recipe
    assert "delta_snr_outlier_markers" in stale_selected_recipe
    assert disabled_block["segment_temporal_evidence_figure_recipe"] is not (
        stale_segment_recipe
    )
    assert disabled_block["selected_evidence_figure_recipe"] is not (
        stale_selected_recipe
    )
    assert results_export._export_signature(disabled_blocks) == (
        results_export._export_signature(clean_blocks)
    )


def test_disabled_registration_strips_stale_zoom_outlier_context(
    monkeypatch,
):
    """Keep false authoritative for focused metadata and native overlays."""
    candidate_metadata = _drilldown_zoom_outlier_candidate_metadata()
    stale_overlay = (
        drilldown_zoom_figures.build_drilldown_zoom_outlier_overlay_recipe(
            representative_utc=candidate_metadata["representative_utc"],
            representative_delta_snr_db=(
                candidate_metadata["representative_delta_snr_db"]
            ),
            qualifying_marker_times_utc=[
                candidate_metadata["representative_utc"]
            ],
            qualifying_marker_delta_snr_db=[
                candidate_metadata["representative_delta_snr_db"]
            ],
            candidate_start_utc=candidate_metadata["event_start_utc"],
            candidate_end_utc=candidate_metadata["event_end_utc"],
            native_evidence_unit_minutes=2.0,
            local_baseline_db=candidate_metadata["local_baseline_db"],
            pre_baseline_db=candidate_metadata["pre_baseline_db"],
            post_baseline_db=candidate_metadata["post_baseline_db"],
            pre_flank_start_utc=candidate_metadata["pre_flank_start_utc"],
            pre_flank_end_utc=candidate_metadata["pre_flank_end_utc"],
            post_flank_start_utc=candidate_metadata[
                "post_flank_start_utc"
            ],
            post_flank_end_utc=candidate_metadata["post_flank_end_utc"],
            robust_spread_db=candidate_metadata["robust_spread_db"],
            robust_spread_method=candidate_metadata[
                "robust_spread_method"
            ],
            minimum_robust_z=candidate_metadata["minimum_robust_z"],
            minimum_departure_db=candidate_metadata[
                "minimum_departure_db"
            ],
            labels={
                "marker": "Qualifying candidate unit",
                "focused_episode": "Focused episode",
                "local_baseline": "Expected local Delta SNR",
                "flank_baseline": "Pre/post flank baseline",
                "robust_z": "Robust-z guide |z| = {value:g}",
                "qualifying_robust_z": (
                    "Robust-z qualifying threshold |z| = {value:g}"
                ),
                "absolute_departure": (
                    "Absolute-departure gate (+/-{value:g} dB)"
                ),
            },
        )
    )
    stale_metric_recipe = (
        drilldown_zoom_figures.build_drilldown_zoom_benchmark_delta_snr_recipe(
            pd.DataFrame(
                {
                    "plot_time": pd.to_datetime(
                        [candidate_metadata["representative_utc"]],
                        utc=True,
                    ),
                    "metric": [
                        candidate_metadata["representative_delta_snr_db"]
                    ],
                }
            ),
            start_utc="2026-07-01T00:00:00Z",
            end_utc="2026-07-01T12:00:00Z",
            title="OK1FCX (JN79) - Time Window: 00:00 to 12:00 UTC",
            panel_title="Delta SNR over Time",
            x_label="Date/Time (UTC)",
            y_label="Delta SNR (dB)",
            empty_text="No paired evidence.",
            evidence_unit_label="Individual Joint Spot",
            is_sequential=False,
            outlier_overlay=stale_overlay,
        )
    )
    stale_metadata = _drilldown_zoom_metadata(
        start_utc="2026-07-01T00:00:00Z",
        end_utc="2026-07-01T12:00:00Z",
        option="outlier_focus",
        origin="outlier_focus",
        outlier_candidate=candidate_metadata,
    )
    clean_metadata = dict(stale_metadata)
    clean_metadata.pop("outlier_candidate")
    stale_metric_recipe_before_registration = deepcopy(stale_metric_recipe)
    clean_metric_recipe = dict(stale_metric_recipe)
    clean_metric_recipe["outlier_overlay"] = None
    disabled_blocks = {
        "RX_COMPARE": {
            "analysis_id": "RX_COMPARE",
            "mode_folder": results_export.BENCHMARK_EXPORT_FOLDER,
        }
    }
    clean_blocks = deepcopy(disabled_blocks)
    pending_states = [disabled_blocks, clean_blocks]
    monkeypatch.setattr(
        results_export,
        "_ensure_current_export_state",
        lambda: pending_states.pop(0),
    )
    common_arguments = {
        "analysis_id": "RX_COMPARE",
        "selected_segment": "Full Range | All Directions",
        "selected_distance": "Full Range",
        "selected_direction": "All Directions",
        "show_non_joint": False,
        "evidence_time_bin": "3h",
        "selected_stations": ["OK1FCX (JN79)"],
        "translations": T["en"],
        "drilldown_zoom_benchmark_coverage_figure_recipe": {
            "kind": "focused-coverage"
        },
    }

    results_export.register_inspector_export(
        **common_arguments,
        drilldown_zoom_metadata=stale_metadata,
        drilldown_zoom_benchmark_delta_snr_figure_recipe=(
            stale_metric_recipe
        ),
        report_delta_snr_outlier_candidates=False,
    )
    results_export.register_inspector_export(
        **common_arguments,
        drilldown_zoom_metadata=clean_metadata,
        drilldown_zoom_benchmark_delta_snr_figure_recipe=(
            clean_metric_recipe
        ),
    )

    disabled_block = disabled_blocks["RX_COMPARE"]
    assert "outlier_candidate" not in disabled_block[
        "drilldown_zoom_metadata"
    ]
    assert disabled_block[
        "drilldown_zoom_benchmark_delta_snr_figure_recipe"
    ]["outlier_overlay"] is None
    assert "outlier_candidate" in stale_metadata
    assert stale_metric_recipe == stale_metric_recipe_before_registration
    assert disabled_block[
        "drilldown_zoom_benchmark_delta_snr_figure_recipe"
    ] is not stale_metric_recipe
    assert results_export._export_signature(disabled_blocks) == (
        results_export._export_signature(clean_blocks)
    )


def test_enabled_outlier_metadata_remains_presentation_only(monkeypatch):
    """Record detector identity per result block, not as a scientific filter."""
    monkeypatch.setattr(
        results_export,
        "st",
        SimpleNamespace(session_state={"lang": "en"}),
    )
    detector_version = "native-residual-episode-v1"
    _outlier_tables, outlier_metadata = _delta_snr_outlier_export_contract()
    metadata = results_export._build_run_metadata(
        {
            "RX_COMPARE": {
                "analysis_id": "RX_COMPARE",
                "mode_folder": "benchmark",
                "database_source": "wspr_live",
                "selected_stations": [],
                "report_delta_snr_outlier_candidates": True,
                "delta_snr_outlier_detector_version": detector_version,
                "delta_snr_outlier_export": outlier_metadata,
            }
        },
        {
            "settings": {
                "advanced_parameters": {
                    "report_delta_snr_outlier_candidates": True
                }
            }
        },
    )

    assert (
        "report_delta_snr_outlier_candidates"
        not in metadata["thresholds_and_filters"]
    )
    result_block = metadata["result_blocks"][0]
    assert result_block["report_delta_snr_outlier_candidates"] is True
    assert result_block["delta_snr_outlier_detector_version"] == detector_version
    assert result_block["delta_snr_outlier_export"] == outlier_metadata


@pytest.mark.parametrize(
    ("language", "expected_event_class", "expected_direction"),
    (
        ("en", "Spot impulse", "ENE"),
        ("de", "Spot-Impuls", "ONO"),
    ),
)
def test_outlier_export_tables_localize_without_mutating_canonical_values(
    language,
    expected_event_class,
    expected_direction,
):
    """Keep canonical registration stable while localizing analyst-facing CSVs."""
    tables, _metadata = _delta_snr_outlier_export_contract()
    source_event_paths = tables.event_paths.copy(deep=True)
    source_evidence = tables.paired_evidence.copy(deep=True)

    localized_event_paths = results_export._localized_outlier_export_table(
        tables.event_paths,
        T[language],
        expected_columns=OUTLIER_EVENT_PATH_COLUMNS,
    )
    localized_evidence = results_export._localized_outlier_export_table(
        tables.paired_evidence,
        T[language],
        expected_columns=OUTLIER_PAIRED_EVIDENCE_COLUMNS,
    )

    event_class_header = T[language][
        "col_export_outlier_combined_event_class"
    ]
    direction_header = T[language]["col_export_outlier_direction"]
    boundary_header = T[language]["col_export_outlier_reported_boundary"]
    assert localized_event_paths.loc[0, event_class_header] == (
        expected_event_class
    )
    assert localized_event_paths.loc[0, direction_header] == expected_direction
    assert localized_evidence.loc[0, direction_header] == expected_direction
    assert localized_evidence.loc[0, boundary_header] == T[language][
        "txt_export_outlier_boundary_start_and_end"
    ]
    assert tables.event_paths.equals(source_event_paths)
    assert tables.paired_evidence.equals(source_evidence)


@pytest.mark.parametrize("language", ("en", "de"))
def test_enabled_empty_outlier_tables_serialize_complete_localized_headers(
    language,
):
    """Export enabled no-candidate results as two header-only readable tables."""
    tables, metadata = _delta_snr_outlier_export_contract(empty=True)
    expected_schemas = (
        (tables.event_paths, OUTLIER_EVENT_PATH_COLUMNS),
        (tables.paired_evidence, OUTLIER_PAIRED_EVIDENCE_COLUMNS),
    )

    assert metadata["result_status"] == "no_candidates"
    for canonical_table, expected_columns in expected_schemas:
        localized_table = results_export._localized_outlier_export_table(
            canonical_table,
            T[language],
            expected_columns=expected_columns,
        )
        csv_text = results_export._dataframe_to_csv_bytes(
            localized_table,
            T[language],
        ).decode("utf-8-sig")
        expected_headers = [
            T[language][results_export.OUTLIER_EXPORT_COLUMN_TRANSLATION_KEYS[column]]
            for column in expected_columns
        ]
        assert list(localized_table.columns) == expected_headers
        assert csv_text.splitlines() == [",".join(expected_headers)]


def test_outlier_table_values_participate_in_export_signature():
    """Invalidate a prepared package when same-shaped evidence values change."""
    tables, metadata = _delta_snr_outlier_export_contract()
    base_block = {
        "analysis_id": "RX_COMPARE",
        "mode_folder": "benchmark",
        "database_source": "wspr_live",
        "report_delta_snr_outlier_candidates": True,
        "delta_snr_outlier_detector_version": "native-residual-episode-v7",
        "delta_snr_outlier_detection_policy": {
            "minimum_departure_db": 3.0,
            "minimum_robust_z": 4.0,
            "maximum_baseline_difference_db": 3.0,
        },
        "delta_snr_outlier_export": metadata,
        OUTLIER_EVENT_PATHS_TABLE_FILENAME: tables.event_paths,
        OUTLIER_PAIRED_EVIDENCE_TABLE_FILENAME: tables.paired_evidence,
    }
    changed_evidence = tables.paired_evidence.copy(deep=True)
    changed_evidence.loc[0, "delta_snr_db"] = 7.4
    changed_block = {
        **base_block,
        OUTLIER_PAIRED_EVIDENCE_TABLE_FILENAME: changed_evidence,
    }

    assert results_export._export_signature(
        {"RX_COMPARE": base_block}
    ) != results_export._export_signature(
        {"RX_COMPARE": changed_block}
    )


@pytest.mark.parametrize(
    "table_filename",
    (
        "table_station_insights_current_segment.csv",
        "table_drilldown_selected_stations.csv",
    ),
)
def test_interactive_table_values_participate_in_export_signature(
    table_filename,
):
    """Invalidate a prepared package when same-shaped visible rows change."""
    base_table = pd.DataFrame(
        {
            "UTC": ["2026-07-01T00:00:00Z"],
            "SNR": [-17.0],
        }
    )
    changed_table = base_table.copy(deep=True)
    changed_table.loc[0, "SNR"] = -8.0
    base_block = {
        "analysis_id": "RX_ABS",
        "mode_folder": "performance",
        "database_source": "wspr_live",
        table_filename: base_table,
    }
    changed_block = {
        **base_block,
        table_filename: changed_table,
    }

    assert results_export._export_signature(
        {"RX_ABS": base_block}
    ) != results_export._export_signature(
        {"RX_ABS": changed_block}
    )


@pytest.mark.parametrize("empty", (False, True))
def test_enabled_outlier_tables_are_packaged_with_status_and_no_double_correction(
    monkeypatch,
    empty,
):
    """Package populated or header-only tables without correcting Reference twice."""
    tables, outlier_metadata = _delta_snr_outlier_export_contract(empty=empty)
    run_id = 91
    state = {
        "run_id": run_id,
        results_export.EXPORT_RUN_ID_KEY: run_id,
        "lang": "en",
        results_export.EXPORT_STATE_KEY: {
            "RX_COMPARE": {
                "analysis_id": "RX_COMPARE",
                "title": "RX Benchmark",
                "mode_folder": results_export.BENCHMARK_EXPORT_FOLDER,
                "database_source": "wspr_live",
                "is_compare": True,
                "is_sequential": False,
                "selected_stations": [],
                "report_delta_snr_outlier_candidates": True,
                "delta_snr_outlier_detector_version": (
                    "native-residual-episode-v7"
                ),
                "delta_snr_outlier_detection_policy": {
                    "minimum_departure_db": 3.0,
                    "minimum_robust_z": 4.0,
                    "maximum_baseline_difference_db": 3.0,
                },
                "delta_snr_outlier_export": outlier_metadata,
                OUTLIER_EVENT_PATHS_TABLE_FILENAME: tables.event_paths,
                OUTLIER_PAIRED_EVIDENCE_TABLE_FILENAME: (
                    tables.paired_evidence
                ),
            }
        },
    }
    config_payload = {
        "format": "wspradar.config",
        "schema_version": 1,
        "settings": {
            "core_parameters": {
                "analysis_direction": "rx",
                "callsign": "ON4AWM0",
                "band": "160m",
                "time_selection": {
                    "start_utc": "2021-06-01T00:00Z",
                    "end_utc": "2021-06-05T00:00Z",
                },
            },
            "comparison_parameters": {
                "mode": "hardware_ab",
                "snr_correction_db": 1.6,
            },
            "advanced_parameters": {},
        },
    }
    monkeypatch.setattr(
        results_export,
        "st",
        SimpleNamespace(session_state=state),
    )
    monkeypatch.setattr(
        results_export,
        "build_config_payload",
        lambda: (
            json.dumps(config_payload).encode("utf-8"),
            "wspradar.config",
        ),
    )
    monkeypatch.setattr(
        results_export,
        "_render_map_png_for_block",
        lambda _block: b"map-png",
    )
    monkeypatch.setattr(
        results_export,
        "_render_inspector_png_for_block",
        lambda _block, _figure_name: None,
    )

    zip_bytes, zip_filename = results_export.build_results_zip(T["en"])
    export_root = zip_filename.removesuffix(".zip")
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        event_csv = archive.read(
            f"{export_root}/benchmark/{OUTLIER_EVENT_PATHS_TABLE_FILENAME}"
        ).decode("utf-8-sig")
        evidence_csv = archive.read(
            f"{export_root}/benchmark/{OUTLIER_PAIRED_EVIDENCE_TABLE_FILENAME}"
        ).decode("utf-8-sig")
        run_metadata = json.loads(
            archive.read(f"{export_root}/config/run_metadata.json")
        )

    expected_status = "no_candidates" if empty else "candidates"
    assert run_metadata["result_blocks"][0]["delta_snr_outlier_export"][
        "result_status"
    ] == expected_status
    assert len(event_csv.splitlines()) == (1 if empty else 2)
    assert len(evidence_csv.splitlines()) == (1 if empty else 2)
    corrected_reference_header = T["en"][
        "col_export_outlier_corrected_reference_snr_db"
    ]
    assert corrected_reference_header in evidence_csv.splitlines()[0]
    assert "Reference correction" not in evidence_csv.splitlines()[0]
    assert "spot_impulse" not in event_csv
    assert "spot_impulse" not in evidence_csv


@pytest.mark.parametrize(
    ("language", "expected_weighting"),
    (
        ("en", "Combined observation-weighted evidence"),
        ("de", "Kombinierte beobachtungsgewichtete Evidenz"),
    ),
)
def test_register_inspector_export_accepts_enabled_multi_station_evidence(
    monkeypatch,
    language,
    expected_weighting,
):
    """Retain exact enabled identities, weighting, detector, and recipes."""
    blocks = {}
    detection_policy = DeltaSnrOutlierDetectionPolicy(
        minimum_departure_db=3.5,
        minimum_robust_z=4.0,
        maximum_baseline_difference_db=2.0,
    )
    marker_recipe = {
        "kind": "selected_benchmark_temporal",
        "delta_snr_outlier_markers": {
            "schema_version": 2,
            "detector_version": "native-residual-episode-v1",
            "detection_resolution": "native-paired-unit",
            "candidate_count": 2,
            "candidate_signature": "selected-signature",
            "legend_label": "candidate",
            "markers": [
                {
                    "callsign": "K1AAA",
                    "locator": "FN31",
                    "marker_utc_ns": 1_788_134_400_000_000_000,
                    "marker_delta_snr_db": 8.0,
                    "episode_start_utc_ns": 1_788_134_280_000_000_000,
                    "episode_end_utc_ns": 1_788_134_520_000_000_000,
                    "event_kind": "spot_impulse",
                },
                {
                    "callsign": "K2BBB",
                    "locator": "FN32",
                    "marker_utc_ns": 1_788_138_000_000_000_000,
                    "marker_delta_snr_db": -7.5,
                    "episode_start_utc_ns": 1_788_137_640_000_000_000,
                    "episode_end_utc_ns": 1_788_138_480_000_000_000,
                    "event_kind": "short_burst",
                },
            ],
        },
    }
    outlier_tables, outlier_metadata = _delta_snr_outlier_export_contract()
    monkeypatch.setattr(
        results_export,
        "_ensure_current_export_state",
        lambda: blocks,
    )

    results_export.register_inspector_export(
        analysis_id="RX_COMPARE",
        selected_segment="Full Range | All Directions",
        selected_distance="Full Range",
        selected_direction="All Directions",
        show_non_joint=False,
        evidence_time_bin="3h",
        selected_stations=["K1AAA (FN31)", "K2BBB (FN32)"],
        translations=T[language],
        selected_evidence_figure_recipe=marker_recipe,
        allow_multiple_selected_stations=True,
        report_delta_snr_outlier_candidates=True,
        delta_snr_outlier_detector_version="native-residual-episode-v1",
        delta_snr_outlier_detection_policy=detection_policy,
        delta_snr_outlier_export_tables=outlier_tables,
        delta_snr_outlier_export_metadata=outlier_metadata,
    )

    block = blocks["RX_COMPARE"]
    assert block["selected_stations"] == [
        "K1AAA (FN31)",
        "K2BBB (FN32)",
    ]
    assert block["selected_station_count"] == 2
    assert block["selected_evidence_weighting"] == expected_weighting
    assert block["selected_evidence_figure_recipe"] is marker_recipe
    assert block["report_delta_snr_outlier_candidates"] is True
    assert block["delta_snr_outlier_detector_version"] == (
        "native-residual-episode-v1"
    )
    assert block["delta_snr_outlier_detection_policy"] == detection_policy.as_dict()
    assert block["delta_snr_outlier_export"] == outlier_metadata
    assert block[OUTLIER_EVENT_PATHS_TABLE_FILENAME].equals(
        outlier_tables.event_paths
    )
    assert block[OUTLIER_PAIRED_EVIDENCE_TABLE_FILENAME].equals(
        outlier_tables.paired_evidence
    )
    assert block[OUTLIER_EVENT_PATHS_TABLE_FILENAME] is not (
        outlier_tables.event_paths
    )
    assert block[OUTLIER_PAIRED_EVIDENCE_TABLE_FILENAME] is not (
        outlier_tables.paired_evidence
    )


def test_register_inspector_export_rejects_mismatched_outlier_joins_atomically(
    monkeypatch,
):
    """Reject same-shaped evidence that disagrees with its path-event row."""
    export_state_calls = []
    outlier_tables, outlier_metadata = _delta_snr_outlier_export_contract()
    outlier_tables.paired_evidence.loc[0, "direction"] = "NNE"
    monkeypatch.setattr(
        results_export,
        "_ensure_current_export_state",
        lambda: export_state_calls.append(True) or {},
    )

    with pytest.raises(ValueError, match="direction context"):
        results_export.register_inspector_export(
            analysis_id="RX_COMPARE",
            selected_segment="Full Range | All Directions",
            selected_distance="Full Range",
            selected_direction="All Directions",
            show_non_joint=False,
            evidence_time_bin="1h",
            selected_stations=[],
            translations=T["en"],
            report_delta_snr_outlier_candidates=True,
            delta_snr_outlier_detector_version=(
                "native-residual-episode-v7"
            ),
            delta_snr_outlier_export_tables=outlier_tables,
            delta_snr_outlier_export_metadata=outlier_metadata,
        )

    assert export_state_calls == []


@pytest.mark.parametrize(
    "selected_stations",
    [
        ["K1AAA (FN31)", "K2BBB (FN32)"],
        "K1AAA (FN31)",
    ],
)
def test_register_inspector_export_rejects_invalid_station_cardinality_atomically(
    monkeypatch,
    selected_stations,
):
    """Reject multi-station or malformed metadata before export-state access."""
    ensure_state_calls = []
    monkeypatch.setattr(
        results_export,
        "_ensure_current_export_state",
        lambda: ensure_state_calls.append(True) or {},
    )

    with pytest.raises(ValueError):
        results_export.register_inspector_export(
            analysis_id="RX_COMPARE",
            selected_segment="Full Range | All Directions",
            selected_distance="Full Range",
            selected_direction="All Directions",
            show_non_joint=False,
            evidence_time_bin="3h",
            selected_stations=selected_stations,
            translations=T["en"],
        )

    assert ensure_state_calls == []


def test_register_export_rejects_multi_selection_without_enabled_reporting(
    monkeypatch,
):
    """Keep the export boundary aligned with the Benchmark selection contract."""
    ensure_state_calls = []
    monkeypatch.setattr(
        results_export,
        "_ensure_current_export_state",
        lambda: ensure_state_calls.append(True) or {},
    )

    with pytest.raises(ValueError, match="require enabled Delta-SNR"):
        results_export.register_inspector_export(
            analysis_id="RX_COMPARE",
            selected_segment="Full Range | All Directions",
            selected_distance="Full Range",
            selected_direction="All Directions",
            show_non_joint=False,
            evidence_time_bin="3h",
            selected_stations=["K1AAA (FN31)", "K2BBB (FN32)"],
            translations=T["en"],
            allow_multiple_selected_stations=True,
            report_delta_snr_outlier_candidates=False,
        )

    assert ensure_state_calls == []


@pytest.mark.parametrize(
    ("language", "expected_suffix"),
    [
        ("en", " (Reference correction +1.3 dB)"),
        ("de", " (Referenzkorrektur +1.3 dB)"),
    ],
)
def test_reference_correction_csv_suffix_is_localized_without_mutating_source_headers(
    language,
    expected_suffix,
):
    """Localize the optional CSV annotation while retaining source field identity."""
    source_frame = pd.DataFrame(
        {
            "Reference SNR (dB)": [-10.04],
            "Target SNR (dB)": [-12.34],
        }
    )
    source_columns = list(source_frame.columns)

    localized_csv = results_export._dataframe_to_csv_bytes(
        source_frame,
        T[language],
        correction_db=1.34,
        reference_snr_header="Reference SNR (dB)",
    ).decode("utf-8-sig")
    uncorrected_csv = results_export._dataframe_to_csv_bytes(
        source_frame,
        T[language],
        correction_db=0.0,
        reference_snr_header="Reference SNR (dB)",
    ).decode("utf-8-sig")

    assert localized_csv.splitlines()[0] == (
        f"Reference SNR (dB){expected_suffix},Target SNR (dB)"
    )
    assert uncorrected_csv.splitlines()[0] == (
        "Reference SNR (dB),Target SNR (dB)"
    )
    assert list(source_frame.columns) == source_columns


def test_run_metadata_zip_preserves_literal_utf8_and_json_round_trip(
    monkeypatch,
):
    """Keep localized scientific metadata readable without losing JSON fidelity."""
    run_id = 73
    metadata_title = "RX Performance — ΔSNR evidence"
    state = {
        "run_id": run_id,
        results_export.EXPORT_RUN_ID_KEY: run_id,
        results_export.EXPORT_STATE_KEY: {
            "RX_ABS": {
                "analysis_id": "RX_ABS",
                "title": metadata_title,
                "mode_folder": results_export.PERFORMANCE_EXPORT_FOLDER,
                "database_source": "wspr_live",
                "is_compare": False,
                "is_sequential": False,
                "analysis_kind": "opportunity",
            }
        },
        "lang": "en",
    }
    config_payload = {
        "format": "wspradar.config",
        "schema_version": 1,
        "settings": {},
    }
    monkeypatch.setattr(
        results_export,
        "st",
        SimpleNamespace(session_state=state),
    )
    monkeypatch.setattr(
        results_export,
        "build_config_payload",
        lambda: (
            json.dumps(config_payload).encode("utf-8"),
            "wspradar.config",
        ),
    )
    monkeypatch.setattr(
        results_export,
        "_render_map_png_for_block",
        lambda _block: b"map-png",
    )
    monkeypatch.setattr(
        results_export,
        "_render_inspector_png_for_block",
        lambda _block, _figure_name: None,
    )
    monkeypatch.setattr(
        results_export,
        "_build_all_drilldown_for_block",
        lambda _block: pd.DataFrame(),
    )

    zip_bytes, zip_filename = results_export.build_results_zip(T["en"])

    export_root = zip_filename.removesuffix(".zip")
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        raw_metadata = archive.read(
            f"{export_root}/config/run_metadata.json"
        )

    decoded_metadata = raw_metadata.decode("utf-8")
    assert f'"title": "{metadata_title}"' in decoded_metadata
    parsed_metadata = json.loads(decoded_metadata)
    assert parsed_metadata["result_blocks"][0]["title"] == metadata_title


@pytest.mark.parametrize(
    ("figure_name", "renderer_name", "recipe_key", "_segment_name", "_segment_key"),
    SUCCESS_SELECTED_FIGURE_EXPORTS,
)
def test_success_selected_figure_export_dispatches_shared_renderer(
    monkeypatch,
    figure_name,
    renderer_name,
    recipe_key,
    _segment_name,
    _segment_key,
):
    """Dispatch each singleton Success recipe through its shared renderer."""
    recipe = {
        "kind": "opportunity_performance_temporal",
        "population_mode": "selected_station",
        "snr_representation": "actual_normalized_snr",
    }
    fake_figure = object()
    renderer_recipes = []
    disposed_figures = []

    monkeypatch.setattr(
        evidence_figures,
        renderer_name,
        lambda received_recipe: (
            renderer_recipes.append(received_recipe) or fake_figure
        ),
    )
    monkeypatch.setattr(
        results_export,
        "figure_to_png_bytes",
        lambda figure, *, paper_theme: (
            b"selected-success-png"
            if figure is fake_figure and paper_theme
            else b""
        ),
    )
    monkeypatch.setattr(
        results_export,
        "dispose_matplotlib_figure",
        disposed_figures.append,
    )

    rendered = results_export._render_inspector_png_for_block(
        {recipe_key: recipe},
        figure_name,
    )

    assert rendered == b"selected-success-png"
    assert renderer_recipes == [recipe]
    assert disposed_figures == [fake_figure]


@pytest.mark.parametrize(
    (
        "figure_name",
        "renderer_name",
        "recipe_key",
        "segment_figure_name",
        "segment_recipe_key",
    ),
    SUCCESS_SELECTED_FIGURE_EXPORTS,
)
def test_success_selected_png_matches_segment_temporal_dimensions_and_aspect(
    monkeypatch,
    figure_name,
    renderer_name,
    recipe_key,
    segment_figure_name,
    segment_recipe_key,
):
    """Keep selected exports physically aligned with their segment counterparts."""
    from core.matplotlib_runtime import create_agg_figure

    selected_recipe = {"population_mode": "selected_station"}
    segment_recipe = {"population_mode": "active_scope"}
    renderer_recipes = []

    def render_temporal_figure(received_recipe):
        """Return the shared temporal canvas while recording recipe routing."""
        renderer_recipes.append(received_recipe)
        return create_agg_figure(
            figsize=evidence_figures.SEGMENT_TEMPORAL_FIGURE_SIZE_INCHES,
            facecolor="black",
        )

    monkeypatch.setattr(
        evidence_figures,
        renderer_name,
        render_temporal_figure,
    )
    block = {
        recipe_key: selected_recipe,
        segment_recipe_key: segment_recipe,
    }

    selected_image_bytes = results_export._render_inspector_png_for_block(
        block,
        figure_name,
    )
    segment_image_bytes = results_export._render_inspector_png_for_block(
        block,
        segment_figure_name,
    )

    assert selected_image_bytes.startswith(b"\x89PNG\r\n\x1a\n")
    assert segment_image_bytes.startswith(b"\x89PNG\r\n\x1a\n")

    def png_dimensions(image_bytes):
        """Return the PNG IHDR width and height in pixels."""
        return (
            int.from_bytes(image_bytes[16:20], byteorder="big"),
            int.from_bytes(image_bytes[20:24], byteorder="big"),
        )

    selected_dimensions = png_dimensions(selected_image_bytes)
    segment_dimensions = png_dimensions(segment_image_bytes)
    assert selected_dimensions == segment_dimensions
    assert (
        selected_dimensions[0] / selected_dimensions[1]
        == pytest.approx(
            segment_dimensions[0] / segment_dimensions[1],
        )
    )
    assert renderer_recipes == [selected_recipe, segment_recipe]


@pytest.mark.parametrize(
    ("figure_name", "renderer_name", "_recipe_key", "_segment_name", "_segment_key"),
    SUCCESS_SELECTED_FIGURE_EXPORTS,
)
def test_success_selected_figure_export_is_absent_without_recipe(
    monkeypatch,
    figure_name,
    renderer_name,
    _recipe_key,
    _segment_name,
    _segment_key,
):
    """Skip every selected-Success PNG safely when no station is selected."""
    def fail_if_called(_recipe):
        raise AssertionError(
            "A selected-Success renderer must not receive a missing recipe."
        )

    monkeypatch.setattr(
        evidence_figures,
        renderer_name,
        fail_if_called,
    )

    assert results_export._render_inspector_png_for_block(
        {},
        figure_name,
    ) is None


def test_success_results_zip_records_selected_figures_and_context(
    monkeypatch,
):
    """Package both singleton Success views without a Compare result family."""
    run_id = 71
    state = {
        "run_id": run_id,
        results_export.EXPORT_RUN_ID_KEY: run_id,
        results_export.EXPORT_STATE_KEY: {},
        "lang": "en",
    }
    config_payload = {
        "format": "wspradar.config",
        "schema_version": 1,
        "settings": {
            "core_parameters": {
                "analysis_direction": "rx",
                "callsign": "TARGET",
                "band": "20m",
                "time_selection": {
                    "start_utc": "2026-07-01T00:00Z",
                    "end_utc": "2026-07-02T00:00Z",
                },
            },
            "comparison_parameters": {"mode": "none"},
            "advanced_parameters": {},
        },
    }
    selected_identities = ["OK1FCX (JN79)"]
    selected_label = "OK1FCX (JN79)"
    selected_context = (
        "OK1FCX (JN79) · 1,173 km · 91° E\n"
        "13,019 confirmed opportunities · Decode Rate 47.6% · "
        "Median Target SNR −15.0 dB"
    )
    figure_descriptions = {
        figure_name: f"{figure_name}: {selected_label}"
        for (
            figure_name,
            _renderer_name,
            _recipe_key,
            _segment_name,
            _segment_key,
        ) in SUCCESS_SELECTED_FIGURE_EXPORTS
    }
    selected_snr_recipe = {
        "kind": "opportunity_performance_temporal",
        "population_mode": "selected_station",
        "snr_representation": "actual_normalized_snr",
    }
    selected_temporal_recipe = dict(selected_snr_recipe)

    monkeypatch.setattr(
        results_export,
        "st",
        SimpleNamespace(session_state=state),
    )
    monkeypatch.setattr(
        results_export,
        "build_config_payload",
        lambda: (
            json.dumps(config_payload).encode("utf-8"),
            "wspradar.config",
        ),
    )
    results_export.register_inspector_export(
        analysis_id="RX_ABS",
        selected_segment="Full Range | All Directions",
        selected_distance="Full Range",
        selected_direction="All Directions",
        show_non_joint=False,
        evidence_time_bin="6h",
        selected_stations=selected_identities,
        translations=T["en"],
        selected_station_snr_evidence_figure_recipe=selected_snr_recipe,
        selected_station_temporal_evidence_figure_recipe=(
            selected_temporal_recipe
        ),
        selected_station_label=selected_label,
        selected_station_context_label=selected_context,
        selected_station_role="TX",
        selected_evidence_figure_descriptions=figure_descriptions,
    )
    success_block = state[results_export.EXPORT_STATE_KEY]["RX_ABS"]
    success_block.update(
        {
            "title": "RX Performance",
            "mode_folder": results_export.PERFORMANCE_EXPORT_FOLDER,
            "database_source": "wspr_live",
            "is_compare": False,
            "is_sequential": False,
            "analysis_kind": "opportunity",
            "performance_method_version": "opportunity-v1",
        }
    )
    rendered_figure_names = []
    selected_filenames = {
        figure_name
        for (
            figure_name,
            _renderer_name,
            _recipe_key,
            _segment_name,
            _segment_key,
        ) in SUCCESS_SELECTED_FIGURE_EXPORTS
    }

    def render_inspector_figure(block, figure_name):
        rendered_figure_names.append((block["analysis_id"], figure_name))
        if figure_name in selected_filenames:
            return f"{block['analysis_id']}:{figure_name}".encode("utf-8")
        return None

    monkeypatch.setattr(
        results_export,
        "_render_inspector_png_for_block",
        render_inspector_figure,
    )
    monkeypatch.setattr(
        results_export,
        "_render_map_png_for_block",
        lambda _block: b"map-png",
    )

    zip_bytes, zip_filename = results_export.build_results_zip(T["en"])

    export_root = zip_filename.removesuffix(".zip")
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        package_paths = set(archive.namelist())
        metadata = json.loads(
            archive.read(f"{export_root}/config/run_metadata.json")
        )

    success_selected_names = [
        figure_name
        for analysis_id, figure_name in rendered_figure_names
        if analysis_id == "RX_ABS"
        and figure_name.startswith("figure_selected_station_")
    ]
    expected_success_names = [
        figure_name
        for (
            figure_name,
            _renderer_name,
            _recipe_key,
            _segment_name,
            _segment_key,
        ) in SUCCESS_SELECTED_FIGURE_EXPORTS
    ]
    assert success_selected_names == expected_success_names
    assert not set(OBSOLETE_SUCCESS_SELECTED_FIGURE_NAMES).intersection(
        success_selected_names
    )
    for figure_name in expected_success_names:
        assert f"{export_root}/performance/{figure_name}" in package_paths
        assert f"{export_root}/benchmark/{figure_name}" not in package_paths
    for figure_name in OBSOLETE_SUCCESS_SELECTED_FIGURE_NAMES:
        assert f"{export_root}/performance/{figure_name}" not in package_paths
        assert f"{export_root}/benchmark/{figure_name}" not in package_paths
    assert (
        f"{export_root}/performance/figure_selected_station_evidence.png"
        not in package_paths
    )
    assert metadata["blocks_present"] == {
        "benchmark": False,
        "performance": True,
    }

    result_blocks = {
        block["analysis_id"]: block for block in metadata["result_blocks"]
    }
    success_metadata = result_blocks["rx_performance"]
    assert success_metadata["folder"] == "performance"
    assert success_metadata["result_mode"] == "performance"
    assert success_metadata["selected_stations"] == selected_identities
    assert success_metadata["selected_station_label"] == selected_label
    assert success_metadata["selected_station_context"] == selected_context
    assert success_metadata["selected_station_count"] == 1
    assert success_metadata["selected_station_role"] == "TX"
    assert success_metadata["selected_evidence_weighting"] == (
        "Single selected path"
    )
    assert success_metadata["selected_evidence_figures"] == figure_descriptions


@pytest.mark.parametrize(
    ("folder", "analysis_id", "recipe_entries", "expected_figures"),
    (
        (
            results_export.PERFORMANCE_EXPORT_FOLDER,
            "RX_ABS",
            {
                "drilldown_zoom_performance_snr_figure_recipe": {
                    "kind": "opportunity_performance_temporal",
                    "schema_version": 1,
                    "time_bin": "2m",
                    "snr_title": (
                        "Selected Station SNR Evidence OK1FCX (JN79), "
                        "Time Window: x to y UTC"
                    ),
                },
                "drilldown_zoom_performance_temporal_figure_recipe": {
                    "kind": "opportunity_performance_temporal",
                    "schema_version": 1,
                    "time_bin": "2m",
                    "evidence_title": (
                        "Selected Station Temporal Evidence OK1FCX (JN79), "
                        "Time Window: x to y UTC"
                    ),
                },
            },
            (
                "figure_drilldown_zoom_snr_evidence.png",
                "figure_drilldown_zoom_temporal_evidence.png",
            ),
        ),
        (
            results_export.BENCHMARK_EXPORT_FOLDER,
            "RX_COMPARE",
            {
                "drilldown_zoom_benchmark_delta_snr_figure_recipe": {
                    "kind": "selected_benchmark_temporal",
                    "schema_version": 1,
                    "time_bin": "2m",
                    "title": (
                        "Selected Station Evidence OK1FCX (JN79), "
                        "Time Window: x to y UTC"
                    ),
                },
                "drilldown_zoom_benchmark_coverage_figure_recipe": {
                    "kind": "benchmark_selected_path_coverage",
                    "schema_version": 1,
                    "time_bin": "2m",
                    "evidence_title": (
                        "Selected Path Evidence Coverage OK1FCX (JN79), "
                        "Time Window: x to y UTC"
                    ),
                },
            },
            (
                "figure_drilldown_zoom_delta_snr_evidence.png",
                "figure_drilldown_zoom_coverage.png",
            ),
        ),
    ),
)
def test_results_zip_conditionally_packages_drilldown_zoom_figures_and_metadata(
    monkeypatch,
    folder,
    analysis_id,
    recipe_entries,
    expected_figures,
):
    """Add both focused PNGs and their exact window inventory only when active."""
    run_id = 73
    metadata = results_export._validated_drilldown_zoom_metadata(
        _drilldown_zoom_metadata()
    )
    block = {
        "analysis_id": analysis_id,
        "title": "RX result",
        "mode_folder": folder,
        "database_source": "wspr_live",
        "is_compare": folder == results_export.BENCHMARK_EXPORT_FOLDER,
        "is_sequential": False,
        "selected_stations": ["OK1FCX (JN79)"],
        "selected_station_count": 1,
        "drilldown_zoom_metadata": metadata,
        **recipe_entries,
    }
    state = {
        "run_id": run_id,
        results_export.EXPORT_RUN_ID_KEY: run_id,
        results_export.EXPORT_STATE_KEY: {analysis_id: block},
        "lang": "en",
    }
    config_payload = {
        "format": "wspradar.config",
        "schema_version": 1,
        "settings": {
            "core_parameters": {
                "analysis_direction": "rx",
                "callsign": "TARGET",
                "band": "20m",
                "time_selection": {
                    "start_utc": "2026-07-01T00:00Z",
                    "end_utc": "2026-07-02T00:00Z",
                },
            },
            "comparison_parameters": {
                "mode": (
                    "hardware_ab"
                    if folder == results_export.BENCHMARK_EXPORT_FOLDER
                    else "none"
                )
            },
            "advanced_parameters": {},
        },
    }
    rendered_figure_names = []

    def render_inspector_figure(_block, figure_name):
        rendered_figure_names.append(figure_name)
        return b"focused-png" if figure_name in expected_figures else None

    monkeypatch.setattr(
        results_export,
        "st",
        SimpleNamespace(session_state=state),
    )
    monkeypatch.setattr(
        results_export,
        "build_config_payload",
        lambda: (
            json.dumps(config_payload).encode("utf-8"),
            "wspradar.config",
        ),
    )
    monkeypatch.setattr(
        results_export,
        "_render_map_png_for_block",
        lambda _block: b"map-png",
    )
    monkeypatch.setattr(
        results_export,
        "_render_inspector_png_for_block",
        render_inspector_figure,
    )

    zip_bytes, zip_filename = results_export.build_results_zip(T["en"])

    export_root = zip_filename.removesuffix(".zip")
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        package_paths = set(archive.namelist())
        run_metadata = json.loads(
            archive.read(f"{export_root}/config/run_metadata.json")
        )
    for figure_name in expected_figures:
        assert figure_name in rendered_figure_names
        assert f"{export_root}/{folder}/{figure_name}" in package_paths
    zoom_metadata = run_metadata["result_blocks"][0]["drilldown_zoom"]
    assert {
        key: zoom_metadata[key]
        for key in (
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
        )
    } == metadata
    assert tuple(zoom_metadata["figures"]) == expected_figures

    missing_figure_name = expected_figures[0]

    def render_incomplete_zoom(_block, figure_name):
        if figure_name == missing_figure_name:
            return None
        return b"focused-png" if figure_name in expected_figures else None

    monkeypatch.setattr(
        results_export,
        "_render_inspector_png_for_block",
        render_incomplete_zoom,
    )
    with pytest.raises(
        results_export.ExportArtifactUnavailableError,
        match="Required Drill-Down zoom export produced no image",
    ):
        results_export.build_results_zip(T["en"])

    block.pop("drilldown_zoom_metadata")
    for recipe_key in tuple(recipe_entries):
        block.pop(recipe_key)
    rendered_figure_names.clear()
    inactive_zip_bytes, inactive_zip_filename = results_export.build_results_zip(
        T["en"]
    )
    inactive_root = inactive_zip_filename.removesuffix(".zip")
    with zipfile.ZipFile(io.BytesIO(inactive_zip_bytes)) as archive:
        inactive_paths = set(archive.namelist())
        inactive_metadata = json.loads(
            archive.read(f"{inactive_root}/config/run_metadata.json")
        )
    assert not set(expected_figures).intersection(rendered_figure_names)
    assert all(
        f"{inactive_root}/{folder}/{figure_name}" not in inactive_paths
        for figure_name in expected_figures
    )
    assert "drilldown_zoom" not in inactive_metadata["result_blocks"][0]


def test_benchmark_results_zip_records_coverage_figures_in_stable_order(
    monkeypatch,
):
    """Package active Benchmark figures under stable presentation-order names."""
    run_id = 72
    state = {
        "run_id": run_id,
        results_export.EXPORT_RUN_ID_KEY: run_id,
        results_export.EXPORT_STATE_KEY: {},
        "lang": "en",
    }
    config_payload = {
        "format": "wspradar.config",
        "schema_version": 1,
        "settings": {
            "core_parameters": {
                "analysis_direction": "rx",
                "callsign": "TARGET",
                "band": "20m",
                "time_selection": {
                    "start_utc": "2026-07-01T00:00Z",
                    "end_utc": "2026-07-02T00:00Z",
                },
            },
            "comparison_parameters": {"mode": "hardware_ab"},
            "advanced_parameters": {},
        },
    }
    selected_identities = ["OK1FCX (JN79)"]
    selected_recipe = {
        "kind": "selected_benchmark_temporal",
    }
    coverage_recipes = {
        recipe_key: {
            "kind": (
                benchmark_evidence_figures.BENCHMARK_SELECTED_PATH_COVERAGE_RECIPE_KIND
                if recipe_key
                == "selected_station_coverage_figure_recipe"
                else benchmark_evidence_figures.BENCHMARK_TEMPORAL_COVERAGE_RECIPE_KIND
            ),
            "schema_version": 1,
            "time_bin": "6h",
            title_key: figure_title,
        }
        for (
            _figure_name,
            _renderer_name,
            recipe_key,
            title_key,
            figure_title,
        ) in COMPARE_COVERAGE_EXPORT_CASES
    }

    monkeypatch.setattr(
        results_export,
        "st",
        SimpleNamespace(session_state=state),
    )
    monkeypatch.setattr(
        results_export,
        "build_config_payload",
        lambda: (
            json.dumps(config_payload).encode("utf-8"),
            "wspradar.config",
        ),
    )
    results_export.register_inspector_export(
        analysis_id="RX_COMPARE",
        selected_segment="Full Range | All Directions",
        selected_distance="Full Range",
        selected_direction="All Directions",
        show_non_joint=False,
        evidence_time_bin="6h",
        selected_stations=selected_identities,
        translations=T["en"],
        selected_evidence_figure_recipe=selected_recipe,
        **coverage_recipes,
    )
    compare_block = state[results_export.EXPORT_STATE_KEY]["RX_COMPARE"]
    compare_block.update(
        {
            "title": "RX Benchmark",
            "mode_folder": results_export.BENCHMARK_EXPORT_FOLDER,
            "database_source": "wspr_live",
            "is_compare": True,
            "is_sequential": False,
            "analysis_kind": "comparison",
        }
    )

    rendered_figure_names = []
    packaged_compare_figures = {
        "figure_selected_station_evidence.png",
        *(
            export_case[0]
            for export_case in COMPARE_COVERAGE_EXPORT_CASES
        ),
    }

    def render_inspector_figure(block, figure_name):
        rendered_figure_names.append((block["analysis_id"], figure_name))
        if figure_name in packaged_compare_figures:
            return f"RX_COMPARE:{figure_name}".encode("utf-8")
        return None

    monkeypatch.setattr(
        results_export,
        "_render_inspector_png_for_block",
        render_inspector_figure,
    )
    monkeypatch.setattr(
        results_export,
        "_render_map_png_for_block",
        lambda _block: b"map-png",
    )

    zip_bytes, zip_filename = results_export.build_results_zip(T["en"])

    export_root = zip_filename.removesuffix(".zip")
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        package_paths = set(archive.namelist())
        metadata = json.loads(
            archive.read(f"{export_root}/config/run_metadata.json")
        )

    compare_figure_names = [
        figure_name
        for analysis_id, figure_name in rendered_figure_names
        if analysis_id == "RX_COMPARE"
    ]
    expected_compare_figure_names = [
        "figure_segment_insight.png",
        "figure_segment_temporal_evidence.png",
        "figure_segment_temporal_coverage.png",
        "figure_selected_station_evidence.png",
        "figure_selected_station_coverage.png",
    ]
    assert compare_figure_names == expected_compare_figure_names
    for figure_name in packaged_compare_figures:
        assert f"{export_root}/benchmark/{figure_name}" in package_paths
    for (
        success_figure_name,
        _renderer_name,
        _recipe_key,
        _segment_name,
        _segment_key,
    ) in SUCCESS_SELECTED_FIGURE_EXPORTS:
        assert f"{export_root}/benchmark/{success_figure_name}" not in package_paths
    for obsolete_figure_name in OBSOLETE_SUCCESS_SELECTED_FIGURE_NAMES:
        assert (
            f"{export_root}/benchmark/{obsolete_figure_name}"
            not in package_paths
        )
    for retired_figure_name, _recipe_key, _renderer_name in (
        RETIRED_COMPARE_FIGURE_EXPORTS
    ):
        assert retired_figure_name not in compare_figure_names
        assert (
            f"{export_root}/benchmark/{retired_figure_name}"
            not in package_paths
        )
    assert metadata["blocks_present"] == {
        "benchmark": True,
        "performance": False,
    }
    assert len(metadata["result_blocks"]) == 1
    compare_metadata = metadata["result_blocks"][0]
    assert compare_metadata["analysis_id"] == "rx_benchmark"
    assert compare_metadata["folder"] == "benchmark"
    assert compare_metadata["result_mode"] == "benchmark"
    assert compare_metadata["selected_stations"] == selected_identities
    assert compare_metadata["selected_station_count"] == 1
    assert compare_metadata["selected_evidence_weighting"] == (
        "Single selected path"
    )
    assert compare_metadata["benchmark_evidence_figures"] == {
        figure_name: figure_title
        for (
            figure_name,
            _renderer_name,
            _recipe_key,
            _title_key,
            figure_title,
        ) in COMPARE_COVERAGE_EXPORT_CASES
    }


def test_performance_export_uses_performance_folder_and_metadata(
    tmp_path,
    monkeypatch,
):
    """New Performance packages must not expose superseded result names."""
    state = {
        "run_id": 17,
        results_export.EXPORT_RUN_ID_KEY: 17,
        results_export.EXPORT_STATE_KEY: {},
        "lang": "en",
        "run_mode": "RX",
    }
    artifact_paths = {
        artifact_kind: session_artifact_path(
            tmp_path,
            state,
            run_id=17,
            analysis_id="RX_ABS",
            artifact_kind=artifact_kind,
        )
        for artifact_kind in ("spots", "map_stations", "map_segments")
    }
    for artifact_path in artifact_paths.values():
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_bytes(b"compact artifact")
        register_session_artifact(state, artifact_path)
    parquet_path = artifact_paths["spots"]
    config_payload = {
        "format": "wspradar.config",
        "schema_version": 1,
        "settings": {
            "core_parameters": {
                "analysis_direction": "rx",
                "callsign": "TARGET",
                "band": "20m",
                "time_selection": {
                    "start_utc": "2026-07-01T00:00Z",
                    "end_utc": "2026-07-02T00:00Z",
                },
            },
            "comparison_parameters": {"mode": "none"},
            "advanced_parameters": {"max_peer_distance_km": 10000},
        },
    }
    config_bytes = json.dumps(config_payload).encode("utf-8")

    monkeypatch.setattr(results_export, "st", SimpleNamespace(session_state=state))
    monkeypatch.setattr(results_export, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(
        results_export,
        "build_config_payload",
        lambda: (config_bytes, "wspradar.config"),
    )
    monkeypatch.setattr(results_export.ARTIFACT_STORE, "touch", lambda _path: True)
    monkeypatch.setattr(
        results_export.ARTIFACT_STORE,
        "lease",
        lambda _path: nullcontext(parquet_path),
    )
    results_export.register_map_export_context(
        analysis={
            "id": "RX_ABS",
            "title": "RX Performance",
            "is_compare": False,
            "is_sequential": False,
            "analysis_kind": "opportunity",
            "absolute_method_version": "opportunity-v1",
        },
        parquet_path=str(parquet_path),
        map_data_paths=results_export.MapDataArtifactPaths(
            station_rows_path=artifact_paths["map_stations"],
            segment_rows_path=artifact_paths["map_segments"],
        ),
        start_t="2026-07-01T00:00:00Z",
        end_t="2026-07-02T00:00:00Z",
        max_peer_distance_km=10000,
        base_min_stations=1,
        lat_0=50.0,
        lon_0=5.0,
        analysis_context=SimpleNamespace(to_dict=lambda: {}),
        presentation_context=SimpleNamespace(
            language="en",
            theme="light",
            solar_label="All",
        ),
        database_source="wd2",
    )
    success_block = state[results_export.EXPORT_STATE_KEY]["RX_ABS"]
    assert success_block["map_context"]["parquet_path"] == str(parquet_path)
    assert success_block["map_context"]["map_data_artifacts"] == {
        "schema_version": results_export.MAP_DATA_ARTIFACT_SCHEMA_VERSION,
        "analysis_id": "RX_ABS",
        "is_compare": False,
        "is_sequential": False,
        "analysis_kind": "opportunity",
        "station_rows_path": str(artifact_paths["map_stations"].resolve()),
        "segment_rows_path": str(artifact_paths["map_segments"].resolve()),
    }
    success_block["table_station_insights_current_segment.csv"] = pd.DataFrame(
        {"Peer": ["TEST"]}
    )
    success_block["table_drilldown_selected_stations.csv"] = pd.DataFrame()
    rendered_inspector_names = []

    def render_success_inspector_figure(_block, figure_name):
        rendered_inspector_names.append(figure_name)
        if figure_name == "figure_segment_temporal_snr_deviation.png":
            return b"temporal-snr-png"
        return None

    monkeypatch.setattr(
        results_export,
        "_render_inspector_png_for_block",
        render_success_inspector_figure,
    )
    monkeypatch.setattr(
        results_export,
        "_render_map_png_for_block",
        lambda _block: b"map-png",
    )

    zip_bytes, zip_filename = results_export.build_results_zip(T["en"])

    export_root = zip_filename.removesuffix(".zip")
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        package_paths = set(archive.namelist())
        metadata = json.loads(
            archive.read(f"{export_root}/config/run_metadata.json")
        )

    assert f"{export_root}/performance/analysis_cache.parquet" in package_paths
    assert f"{export_root}/config/wspradar_config.config" in package_paths
    assert f"{export_root}/performance/table_station_insights_current_segment.csv" in package_paths
    assert (
        f"{export_root}/performance/figure_segment_temporal_snr_deviation.png"
        in package_paths
    )
    assert "figure_segment_temporal_snr_deviation.png" in (
        rendered_inspector_names
    )
    assert rendered_inspector_names.index(
        "figure_segment_temporal_snr_deviation.png"
    ) < rendered_inspector_names.index(
        "figure_segment_temporal_evidence.png"
    )
    assert all("/absolute/" not in path for path in package_paths)
    assert metadata["blocks_present"] == {
        "benchmark": False,
        "performance": True,
    }
    assert metadata["database_source"] == "wd2"
    assert (
        metadata["thresholds_and_filters"]["max_peer_distance_km"] == 10000
    )
    assert metadata["result_blocks"][0]["analysis_id"] == "rx_performance"
    assert metadata["result_blocks"][0]["folder"] == "performance"
    assert metadata["result_blocks"][0]["result_mode"] == "performance"
    assert metadata["result_blocks"][0]["performance_method_version"] == (
        "opportunity-v1"
    )
    assert "absolute" not in json.dumps(metadata).casefold()


def test_success_map_export_reuses_compact_aggregate_without_raw_evidence_read(
    tmp_path,
    monkeypatch,
):
    """Rebuild the light export without materializing row-level evidence."""
    state = {"run_id": 17}
    artifact_paths = {
        artifact_kind: session_artifact_path(
            tmp_path,
            state,
            run_id=17,
            analysis_id="RX_ABS",
            artifact_kind=artifact_kind,
        )
        for artifact_kind in ("spots", "map_stations", "map_segments")
    }
    for artifact_path in artifact_paths.values():
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_bytes(b"compact artifact")
        register_session_artifact(state, artifact_path)
    monkeypatch.setattr(
        results_export,
        "st",
        SimpleNamespace(session_state=state),
    )
    monkeypatch.setattr(results_export, "CACHE_DIR", tmp_path)
    compact_map_data = SimpleNamespace(marker="compact map data")
    aggregate_read_calls = []
    render_calls = []
    disposed_figures = []
    fake_figure = object()

    def fake_read_map_data_artifacts(paths, **kwargs):
        aggregate_read_calls.append((paths, kwargs))
        return compact_map_data

    def fake_render_map_figure(*args, **kwargs):
        render_calls.append((args, kwargs))
        return SimpleNamespace(figure=fake_figure)

    monkeypatch.setattr(
        results_export,
        "read_map_data_artifacts",
        fake_read_map_data_artifacts,
    )
    monkeypatch.setattr(
        plot_engine,
        "render_map_figure",
        fake_render_map_figure,
    )
    monkeypatch.setattr(
        results_export,
        "figure_to_png_bytes",
        lambda figure, *, paper_theme: (
            b"map-png"
            if figure is fake_figure and paper_theme is False
            else b""
        ),
    )
    monkeypatch.setattr(
        results_export,
        "dispose_matplotlib_figure",
        disposed_figures.append,
    )
    analysis_context = AnalysisContext(
        callsign="TARGET",
        qth="JN47",
        band="20m",
    )
    block = {
        "analysis_id": "RX_ABS",
        "title": "RX Performance",
        "is_compare": False,
        "is_sequential": False,
        "analysis_kind": "opportunity",
        "map_context": {
            "parquet_path": str(artifact_paths["spots"]),
            "map_data_artifacts": {
                "schema_version": (
                    results_export.MAP_DATA_ARTIFACT_SCHEMA_VERSION
                ),
                "analysis_id": "RX_ABS",
                "is_compare": False,
                "is_sequential": False,
                "analysis_kind": "opportunity",
                "station_rows_path": str(artifact_paths["map_stations"]),
                "segment_rows_path": str(artifact_paths["map_segments"]),
            },
            "start_t": "2026-07-01T00:00:00Z",
            "end_t": "2026-07-02T00:00:00Z",
            "max_peer_distance_km": 10000,
            "base_min_stations": 1,
            "lat_0": 50.0,
            "lon_0": 5.0,
            "analysis_context": analysis_context.to_dict(),
            "presentation_context": {
                "language": "en",
                "theme": "dark",
                "solar_label": "All",
            },
        },
    }

    rendered = results_export._render_map_png_for_block(block)

    assert rendered == b"map-png"
    assert len(aggregate_read_calls) == 1
    aggregate_paths, aggregate_identity = aggregate_read_calls[0]
    assert aggregate_paths == results_export.MapDataArtifactPaths(
        station_rows_path=artifact_paths["map_stations"].resolve(),
        segment_rows_path=artifact_paths["map_segments"].resolve(),
    )
    assert aggregate_identity == {
        "analysis_id": "RX_ABS",
        "is_compare": False,
        "is_sequential": False,
        "analysis_kind": "opportunity",
    }
    assert len(render_calls) == 1
    positional, keyword = render_calls[0]
    assert positional == (compact_map_data,)
    assert keyword["title"] == "RX Performance"
    assert keyword["start_t"] == "2026-07-01T00:00:00Z"
    assert keyword["end_t"] == "2026-07-02T00:00:00Z"
    assert keyword["analysis_context"] == analysis_context
    assert keyword["presentation_context"].language == "en"
    assert keyword["presentation_context"].theme == "light"
    assert disposed_figures == [fake_figure]
