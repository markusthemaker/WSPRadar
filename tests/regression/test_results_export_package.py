"""Prepared-results package structure regression tests."""

from contextlib import nullcontext
import io
import json
from types import SimpleNamespace
import zipfile

import pandas as pd

from ui import results_export


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
    config_bytes = json.dumps({"config": {"callsign": "TARGET"}}).encode("utf-8")

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
        max_dist_km=22000,
        base_min_stations=1,
        lat_0=50.0,
        lon_0=5.0,
        analysis_context=SimpleNamespace(to_dict=lambda: {}),
        presentation_context=SimpleNamespace(
            language="en",
            theme="light",
            solar_label="All",
        ),
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
    assert f"{export_root}/success/table_station_insights_current_segment.csv" in package_paths
    assert all("/absolute/" not in path for path in package_paths)
    assert metadata["blocks_present"] == {"compare": False, "success": True}
    assert metadata["result_blocks"][0]["folder"] == "success"
    assert metadata["result_blocks"][0]["success_method_version"] == "opportunity-v1"
    assert "absolute" not in json.dumps(metadata).casefold()
