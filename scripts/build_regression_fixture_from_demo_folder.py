#!/usr/bin/env python
"""Build a WSPRadar regression fixture from an unzipped prepared-results export.

The input can be either:

- the export root itself, containing config/run_metadata.json, or
- a parent folder containing exactly one WSPRadar_export_* child.

The script copies the export into tests/regression/fixtures/<name> and writes
small summary metrics that tests can compare quickly before deeper regeneration
tests are added.
"""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE_ROOT = REPO_ROOT / "tests" / "regression" / "fixtures"
TABLE_FILES = [
    "table_station_insights_current_segment.csv",
    "table_drilldown_selected_stations.csv",
    "table_drilldown_all_stations_current_segment.csv",
]
FIGURE_FILES = [
    "figure_map_highres.png",
    "figure_segment_insight.png",
    "figure_selected_station_evidence.png",
]
BLOCK_FOLDERS = ["compare", "absolute"]


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")


def _find_export_root(input_folder: Path) -> Path:
    input_folder = input_folder.resolve()
    if (input_folder / "config" / "run_metadata.json").exists():
        return input_folder

    candidates = [
        child for child in input_folder.iterdir()
        if child.is_dir() and (child / "config" / "run_metadata.json").exists()
    ]
    if len(candidates) == 1:
        return candidates[0].resolve()
    if not candidates:
        raise FileNotFoundError(
            f"No WSPRadar export root found below {input_folder}. "
            "Expected config/run_metadata.json."
        )
    raise ValueError(
        f"More than one WSPRadar export root found below {input_folder}. "
        "Pass the intended export folder explicitly."
    )


def _fixture_name(input_folder: Path, export_root: Path, explicit_name: str | None) -> str:
    raw_name = explicit_name or input_folder.name or export_root.name
    safe = "".join(ch.lower() if ch.isalnum() else "_" for ch in raw_name.strip())
    safe = "_".join(part for part in safe.split("_") if part)
    if not safe:
        raise ValueError("Fixture name is empty after sanitizing.")
    return safe


def _safe_remove_fixture(destination: Path, fixture_root: Path) -> None:
    resolved_dest = destination.resolve()
    resolved_root = fixture_root.resolve()
    if resolved_dest == resolved_root or not resolved_dest.is_relative_to(resolved_root):
        raise ValueError(f"Refusing to remove path outside fixture root: {resolved_dest}")
    shutil.rmtree(resolved_dest)


def _copy_export_tree(export_root: Path, destination: Path) -> None:
    for name in ["config", "compare", "absolute"]:
        source = export_root / name
        if source.exists():
            shutil.copytree(source, destination / name)


def _csv_metrics(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False}

    df = pd.read_csv(path, encoding="utf-8-sig")
    metrics: dict[str, Any] = {
        "exists": True,
        "rows": int(len(df)),
        "columns": list(df.columns),
        "column_count": int(len(df.columns)),
    }

    for column in df.columns:
        if column in {"Joint Spots", "Spots"} or column.startswith("Only "):
            numeric = pd.to_numeric(df[column], errors="coerce").fillna(0)
            metrics[f"sum_{column}"] = int(numeric.sum())

    median_columns = [
        column for column in df.columns
        if "Median" in column and ("SNR" in column or "Delta" in column or "\u0394" in column)
    ]
    for column in median_columns:
        numeric = pd.to_numeric(df[column], errors="coerce").dropna()
        metrics[f"non_null_{column}"] = int(numeric.shape[0])
        if not numeric.empty:
            metrics[f"median_of_{column}"] = float(numeric.median())

    return metrics


def _parquet_metrics(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False}

    df = pd.read_parquet(path)
    return {
        "exists": True,
        "rows": int(len(df)),
        "columns": list(df.columns),
        "column_count": int(len(df.columns)),
    }


def _figure_metrics(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False}
    return {
        "exists": True,
        "bytes": int(path.stat().st_size),
    }


def _block_metrics(block_folder: Path) -> dict[str, Any]:
    metrics: dict[str, Any] = {
        "exists": block_folder.exists(),
        "tables": {},
        "figures": {},
        "analysis_caches": {},
    }
    if not block_folder.exists():
        return metrics

    for table_name in TABLE_FILES:
        metrics["tables"][table_name] = _csv_metrics(block_folder / table_name)
    for figure_name in FIGURE_FILES:
        metrics["figures"][figure_name] = _figure_metrics(block_folder / figure_name)
    for parquet_path in sorted(block_folder.glob("*.parquet")):
        metrics["analysis_caches"][parquet_path.name] = _parquet_metrics(parquet_path)

    return metrics


def _build_expected_metrics(destination: Path) -> dict[str, Any]:
    return {
        folder: _block_metrics(destination / folder)
        for folder in BLOCK_FOLDERS
        if (destination / folder).exists()
    }


def _build_manifest(
    fixture_name: str,
    input_folder: Path,
    export_root: Path,
    destination: Path,
) -> dict[str, Any]:
    run_metadata = _read_json(destination / "config" / "run_metadata.json")
    blocks = []
    for block in run_metadata.get("result_blocks", []):
        folder = block.get("folder")
        if folder not in BLOCK_FOLDERS:
            continue
        blocks.append({
            "analysis_id": block.get("analysis_id"),
            "title": block.get("title"),
            "folder": folder,
            "analysis_cache_file": block.get("analysis_cache_file"),
            "is_compare": block.get("is_compare"),
            "is_sequential": block.get("is_sequential"),
            "selected_distance": block.get("selected_distance"),
            "selected_direction": block.get("selected_direction"),
            "show_non_joint": block.get("show_non_joint"),
            "evidence_time_bin": block.get("evidence_time_bin"),
        })

    return {
        "fixture_name": fixture_name,
        "built_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source_input_folder": str(input_folder.resolve()),
        "source_export_root": str(export_root.resolve()),
        "app": run_metadata.get("app"),
        "version": run_metadata.get("version"),
        "export_signature": run_metadata.get("export_signature"),
        "blocks": blocks,
        "fixture_files": {
            "config": "config/wspradar_config.config",
            "run_metadata": "config/run_metadata.json",
            "expected_metrics": "expected_metrics.json",
        },
    }


def build_fixture(input_folder: Path, fixture_root: Path, name: str | None, force: bool) -> Path:
    export_root = _find_export_root(input_folder)
    fixture_name = _fixture_name(input_folder, export_root, name)
    destination = (fixture_root / fixture_name).resolve()

    if destination.exists():
        if not force:
            raise FileExistsError(
                f"Fixture already exists: {destination}. Re-run with --force to overwrite."
            )
        _safe_remove_fixture(destination, fixture_root)

    destination.mkdir(parents=True, exist_ok=False)
    _copy_export_tree(export_root, destination)

    required = [
        destination / "config" / "wspradar_config.config",
        destination / "config" / "run_metadata.json",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        _safe_remove_fixture(destination, fixture_root)
        raise FileNotFoundError(f"Export is missing required files: {missing}")

    manifest = _build_manifest(fixture_name, input_folder, export_root, destination)
    expected_metrics = _build_expected_metrics(destination)
    _write_json(destination / "manifest.json", manifest)
    _write_json(destination / "expected_metrics.json", expected_metrics)

    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("demo_folder", type=Path, help="Unzipped WSPRadar export folder or parent folder.")
    parser.add_argument("--name", help="Optional fixture name. Defaults to the demo folder name.")
    parser.add_argument(
        "--fixtures-dir",
        type=Path,
        default=DEFAULT_FIXTURE_ROOT,
        help="Destination fixture root. Defaults to tests/regression/fixtures.",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite an existing fixture with the same name.")
    args = parser.parse_args()

    fixture_root = args.fixtures_dir.resolve()
    fixture_root.mkdir(parents=True, exist_ok=True)
    destination = build_fixture(args.demo_folder, fixture_root, args.name, args.force)
    print(f"Built regression fixture: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
