"""Prepared-results package structure regression tests."""

from contextlib import nullcontext
import io
import json
from types import SimpleNamespace
import zipfile

import pandas as pd
import pytest

from ui import results_export
from ui.plots import evidence_figures


class _FooterColumn:
    """Minimal context-manager column used by footer rendering tests."""

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


def test_selected_temporal_view_is_recorded_and_changes_export_signature(monkeypatch):
    """Prevent Chronological 1 h and folded 1 h exports from sharing a stale ZIP."""
    monkeypatch.setattr(
        results_export,
        "st",
        SimpleNamespace(session_state={"lang": "en"}),
    )
    block = {
        "analysis_id": "RX_COMPARE",
        "mode_folder": results_export.COMPARE_EXPORT_FOLDER,
        "database_source": "wspr_live",
        "evidence_time_bin": "1h",
        "selected_evidence_figure_recipe": {
            "temporal_view": "chronological",
        },
    }
    chronological_blocks = {"RX_COMPARE": block}
    folded_blocks = {
        "RX_COMPARE": {
            **block,
            "selected_evidence_figure_recipe": {
                "temporal_view": "utc_hour",
            },
        }
    }

    chronological_metadata = results_export._build_run_metadata(
        chronological_blocks,
        {"settings": {}},
    )
    folded_metadata = results_export._build_run_metadata(
        folded_blocks,
        {"settings": {}},
    )

    assert chronological_metadata["result_blocks"][0][
        "selected_evidence_time_view"
    ] == "chronological"
    assert folded_metadata["result_blocks"][0][
        "selected_evidence_time_view"
    ] == "utc_hour"
    assert chronological_metadata["export_signature"] != folded_metadata[
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
        "mode_folder": results_export.SUCCESS_EXPORT_FOLDER,
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
                "mode_folder": results_export.COMPARE_EXPORT_FOLDER,
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


def test_run_metadata_rejects_mixed_database_sources(monkeypatch):
    monkeypatch.setattr(
        results_export,
        "st",
        SimpleNamespace(session_state={"lang": "en"}),
    )
    blocks = {
        "RX_COMP": {
            "analysis_id": "RX_COMP",
            "mode_folder": results_export.COMPARE_EXPORT_FOLDER,
            "database_source": "wspr_live",
        },
        "RX_ABS": {
            "analysis_id": "RX_ABS",
            "mode_folder": results_export.SUCCESS_EXPORT_FOLDER,
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
                    "mode_folder": results_export.SUCCESS_EXPORT_FOLDER,
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
            or (_FooterColumn(), _FooterColumn())
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
        lambda: {"RX_ABS": {"mode_folder": results_export.SUCCESS_EXPORT_FOLDER}},
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

    results_export.render_download_all_results({})

    assert captured["columns"] == (
        [0.65, 0.35],
        {"gap": "large", "vertical_alignment": "center"},
    )
    assert captured["save_calls"] == [
        {
            "popover_key": "config_save_results_trigger",
            "form_scope": "results",
        }
    ]
    assert bool(captured["downloads"]) is is_prepared
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

    results_export.render_download_all_results({})

    assert markdown_calls == []


def test_segment_temporal_figure_uses_its_distinct_export_recipe(monkeypatch):
    """Keep segment temporal and selected-station figure recipes independent."""
    temporal_recipe = {"kind": "segment_compare_temporal", "time_bin": "6h"}
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


def test_success_export_uses_success_folder_and_metadata(tmp_path, monkeypatch):
    """New Success packages must not expose the superseded Absolute name."""
    parquet_path = tmp_path / "success_evidence.parquet"
    parquet_path.write_bytes(b"compact evidence")
    state = {
        "run_id": 17,
        results_export.EXPORT_RUN_ID_KEY: 17,
        results_export.EXPORT_STATE_KEY: {},
        "lang": "en",
        "run_mode": "RX",
    }
    config_payload = {
        "format": "wspradar.config",
        "schema_version": 1,
        "settings": {
            "core_parameters": {
                "analysis_direction": "rx",
                "callsign": "TARGET",
                "band": "20m",
                "time_selection": {"mode": "last_x", "hours": 24},
            },
            "comparison_parameters": {"mode": "none"},
            "advanced_parameters": {"max_peer_distance_km": 10000},
        },
    }
    config_bytes = json.dumps(config_payload).encode("utf-8")

    monkeypatch.setattr(results_export, "st", SimpleNamespace(session_state=state))
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
            "title": "RX Success",
            "is_compare": False,
            "is_sequential": False,
            "analysis_kind": "opportunity",
            "absolute_method_version": "opportunity-v1",
        },
        parquet_path=str(parquet_path),
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
    success_block["table_station_insights_current_segment.csv"] = pd.DataFrame(
        {"Peer": ["TEST"]}
    )
    success_block["table_drilldown_selected_stations.csv"] = pd.DataFrame()

    zip_bytes, zip_filename = results_export.build_results_zip()

    export_root = zip_filename.removesuffix(".zip")
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        package_paths = set(archive.namelist())
        metadata = json.loads(
            archive.read(f"{export_root}/config/run_metadata.json")
        )

    assert f"{export_root}/success/analysis_cache.parquet" in package_paths
    assert f"{export_root}/config/wspradar_config.config" in package_paths
    assert f"{export_root}/success/table_station_insights_current_segment.csv" in package_paths
    assert all("/absolute/" not in path for path in package_paths)
    assert metadata["blocks_present"] == {"compare": False, "success": True}
    assert metadata["database_source"] == "wd2"
    assert (
        metadata["thresholds_and_filters"]["max_peer_distance_km"] == 10000
    )
    assert metadata["result_blocks"][0]["folder"] == "success"
    assert metadata["result_blocks"][0]["success_method_version"] == "opportunity-v1"
    assert "absolute" not in json.dumps(metadata).casefold()
