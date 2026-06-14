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
import struct
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
SNR_METRIC_MARKERS = ("snr", "norm@1w", "\u0394", "delta", "micro-med", "bin \u0394")


def _is_snr_metric_column(column: str) -> bool:
    text = str(column).strip().lower()
    return any(marker in text for marker in SNR_METRIC_MARKERS)


def _is_rate_metric_column(column: str) -> bool:
    text = str(column).strip().lower()
    return "rate" in text and "%" in text


def _max_decimal_places(values: pd.Series) -> int:
    max_places = 0
    for raw_value in values.dropna().astype(str):
        value = raw_value.strip()
        if not value or value.lower() in {"none", "nan", "n/a"}:
            continue
        try:
            float(value)
        except ValueError:
            continue
        if "." in value:
            decimal = value.split(".", 1)[1].split("e", 1)[0].split("E", 1)[0]
            max_places = max(max_places, len(decimal.rstrip("0")) if decimal.rstrip("0") else 1)
    return max_places


def _metric_stats(numeric: pd.Series) -> dict[str, Any]:
    numeric = pd.to_numeric(numeric, errors="coerce").dropna()
    stats: dict[str, Any] = {"non_null": int(numeric.shape[0])}
    if numeric.empty:
        return stats
    stats.update({
        "mean": round(float(numeric.mean()), 3),
        "median": round(float(numeric.median()), 3),
        "min": round(float(numeric.min()), 3),
        "max": round(float(numeric.max()), 3),
    })
    return stats


def _primary_metric_column(table_name: str, columns: list[str]) -> str | None:
    if table_name == "table_station_insights_current_segment.csv":
        rate_candidates = [column for column in columns if _is_rate_metric_column(column)]
        if rate_candidates:
            return rate_candidates[-1]
        candidates = [
            column for column in columns
            if "median" in column.lower() and _is_snr_metric_column(column)
        ]
        return candidates[-1] if candidates else None

    if table_name.startswith("table_drilldown_"):
        delta_candidates = [
            column for column in columns
            if "\u0394 snr" in column.lower() or "delta snr" in column.lower()
        ]
        if delta_candidates:
            return delta_candidates[-1]
        norm_candidates = [column for column in columns if "norm@1w" in column.lower()]
        if norm_candidates:
            return norm_candidates[-1]
    return None


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


def _csv_metrics(path: Path, table_name: str) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False}

    df = pd.read_csv(path, encoding="utf-8-sig")
    raw_df = pd.read_csv(path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    metrics: dict[str, Any] = {
        "exists": True,
        "rows": int(len(df)),
        "columns": list(df.columns),
        "column_count": int(len(df.columns)),
    }

    for column in df.columns:
        text = str(column).strip()
        if (
            column in {"Joint Spots", "Spots"} or
            column.startswith("Only ") or
            any(text.endswith(f"({label})") for label in ("O", "H", "M", "T"))
        ):
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

    metric_columns = [
        column for column in df.columns
        if _is_snr_metric_column(column) or _is_rate_metric_column(column)
    ]
    metrics["snr_metric_columns"] = metric_columns
    for column in metric_columns:
        stats = _metric_stats(df[column])
        for stat_name, value in stats.items():
            metrics[f"{stat_name}_of_{column}"] = value
        metrics[f"max_decimal_places_{column}"] = _max_decimal_places(raw_df[column])

    primary_metric = _primary_metric_column(table_name, list(df.columns))
    if primary_metric:
        primary_stats = _metric_stats(df[primary_metric])
        prefix = "segment_station_metric" if table_name == "table_station_insights_current_segment.csv" else "segment_spot_metric"
        metrics[f"{prefix}_column"] = primary_metric
        for stat_name, value in primary_stats.items():
            metrics[f"{prefix}_{stat_name}"] = value

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


def _png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) < 24 or not header.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError(f"Not a readable PNG file: {path}")
    return struct.unpack(">II", header[16:24])


def _figure_metrics(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False}
    width, height = _png_dimensions(path)
    return {
        "exists": True,
        "width": int(width),
        "height": int(height),
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
        metrics["tables"][table_name] = _csv_metrics(block_folder / table_name, table_name)
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


def _table_test_description(table_name: str) -> str:
    descriptions = {
        "table_station_insights_current_segment.csv": "station insight table shape, columns, joint/spot sums and median columns",
        "table_drilldown_selected_stations.csv": "selected-station drill-down shape and columns",
        "table_drilldown_all_stations_current_segment.csv": "all-station current-segment drill-down shape and columns, including non-joint evidence where applicable",
    }
    return descriptions.get(table_name, "table shape and columns")


def _build_regression_report(
    manifest: dict[str, Any],
    expected_metrics: dict[str, Any],
) -> dict[str, Any]:
    blocks = []
    for block in manifest.get("blocks", []):
        folder = block["folder"]
        metrics = expected_metrics.get(folder, {})
        block_report = {
            "folder": folder,
            "analysis_id": block.get("analysis_id"),
            "title": block.get("title"),
            "mode": "compare" if block.get("is_compare") else "absolute",
            "is_sequential": block.get("is_sequential"),
            "analysis_kind": block.get("analysis_kind"),
            "absolute_method_version": block.get("absolute_method_version"),
            "selected_distance": block.get("selected_distance"),
            "selected_direction": block.get("selected_direction"),
            "show_non_joint": block.get("show_non_joint"),
            "evidence_time_bin": block.get("evidence_time_bin"),
            "analysis_cache_file": block.get("analysis_cache_file"),
            "tests": [],
        }

        for table_name, table_metrics in metrics.get("tables", {}).items():
            block_report["tests"].append({
                "kind": "table",
                "name": table_name,
                "description": _table_test_description(table_name),
                "exists": table_metrics.get("exists", False),
                "rows": table_metrics.get("rows", 0),
                "column_count": table_metrics.get("column_count", 0),
                "metrics": {
                    key: value for key, value in table_metrics.items()
                    if key.startswith(("sum_", "mean_of_", "median_of_", "segment_", "max_decimal_places_"))
                },
            })

        for figure_name, figure_metrics in metrics.get("figures", {}).items():
            block_report["tests"].append({
                "kind": "figure",
                "name": figure_name,
                "description": "PNG presence and readability",
                "exists": figure_metrics.get("exists", False),
                "width": figure_metrics.get("width", 0),
                "height": figure_metrics.get("height", 0),
            })

        for parquet_name, parquet_metrics in metrics.get("analysis_caches", {}).items():
            block_report["tests"].append({
                "kind": "analysis_cache",
                "name": parquet_name,
                "description": "parquet cache readability, row count, column count and schema",
                "exists": parquet_metrics.get("exists", False),
                "rows": parquet_metrics.get("rows", 0),
                "column_count": parquet_metrics.get("column_count", 0),
            })

        blocks.append(block_report)

    return {
        "fixture_name": manifest["fixture_name"],
        "app": manifest.get("app"),
        "version": manifest.get("version"),
        "export_signature": manifest.get("export_signature"),
        "built_utc": manifest.get("built_utc"),
        "scope": "fixture package integrity and exported evidence-shape regression",
        "blocks": blocks,
    }


def _markdown_row(values: list[Any]) -> str:
    return "| " + " | ".join(str(value) for value in values) + " |"


def _write_regression_report_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        f"# Regression Report: {report['fixture_name']}",
        "",
        f"- App: {report.get('app')}",
        f"- Version: {report.get('version')}",
        f"- Built UTC: {report.get('built_utc')}",
        f"- Scope: {report.get('scope')}",
        "",
    ]

    for block in report.get("blocks", []):
        lines.extend([
            f"## {block.get('folder')} - {block.get('title')}",
            "",
            f"- Mode: {block.get('mode')}",
            f"- Sequential: {block.get('is_sequential')}",
            f"- Segment: {block.get('selected_distance')} / {block.get('selected_direction')}",
            f"- Show Non-Joint: {block.get('show_non_joint')}",
            f"- Evidence bin: {block.get('evidence_time_bin')}",
            f"- Analysis cache: {block.get('analysis_cache_file')}",
            "",
            _markdown_row(["Kind", "Name", "Rows", "Columns", "Size", "Description"]),
            _markdown_row(["---", "---", "---:", "---:", "---:", "---"]),
        ])
        for test in block.get("tests", []):
            size_text = ""
            if test.get("width") and test.get("height"):
                size_text = f"{test.get('width')}x{test.get('height')}"
            lines.append(_markdown_row([
                test.get("kind"),
                test.get("name"),
                test.get("rows", ""),
                test.get("column_count", ""),
                size_text,
                test.get("description"),
            ]))
            metric_lines = []
            for key, value in sorted((test.get("metrics") or {}).items()):
                if key.startswith(("segment_", "sum_", "mean_of_", "median_of_")):
                    metric_lines.append(f"`{key}` = `{value}`")
            if metric_lines:
                lines.append(_markdown_row(["", "metrics", "", "", "", "<br>".join(metric_lines)]))
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


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
            "analysis_kind": block.get("analysis_kind"),
            "absolute_method_version": block.get("absolute_method_version"),
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
            "regression_report_json": "regression_report.json",
            "regression_report_markdown": "regression_report.md",
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
    regression_report = _build_regression_report(manifest, expected_metrics)
    _write_json(destination / "manifest.json", manifest)
    _write_json(destination / "expected_metrics.json", expected_metrics)
    _write_json(destination / "regression_report.json", regression_report)
    _write_regression_report_markdown(destination / "regression_report.md", regression_report)

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
