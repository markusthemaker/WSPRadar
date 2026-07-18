"""Regression fixture integrity tests for WSPRadar prepared-result exports.

These tests intentionally start with package-level invariants. They make sure
golden demo exports stay complete and internally readable. A later test layer
can regenerate station tables and figures from the bundled parquet caches.
"""

from __future__ import annotations

import json
import struct
from pathlib import Path

import pandas as pd
import pytest


FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures"
TABLE_FILES = [
    "table_station_insights_current_segment.csv",
    "table_drilldown_selected_stations.csv",
    "table_drilldown_all_stations_current_segment.csv",
]
FIGURE_FILES = [
    "figure_map_highres.png",
    "figure_segment_insight.png",
    "figure_segment_temporal_evidence.png",
    "figure_selected_station_evidence.png",
]


def _fixture_dirs():
    if not FIXTURE_ROOT.exists():
        return []
    return [
        path for path in sorted(FIXTURE_ROOT.iterdir())
        if path.is_dir() and (path / "manifest.json").exists()
    ]


FIXTURES = _fixture_dirs()


def _read_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _assert_csv_metrics(path: Path, expected: dict):
    assert path.exists() == expected["exists"]
    if not expected["exists"]:
        return

    df = pd.read_csv(path, encoding="utf-8-sig")
    raw_df = pd.read_csv(path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    assert int(len(df)) == expected["rows"]
    assert list(df.columns) == expected["columns"]
    assert int(len(df.columns)) == expected["column_count"]

    for key, expected_value in expected.items():
        if key.startswith("sum_"):
            column = key.removeprefix("sum_")
            numeric = pd.to_numeric(df[column], errors="coerce").fillna(0)
            assert int(numeric.sum()) == expected_value
        elif key.startswith("non_null_of_"):
            column = key.removeprefix("non_null_of_")
            numeric = pd.to_numeric(df[column], errors="coerce").dropna()
            assert int(numeric.shape[0]) == expected_value
        elif key.startswith(("mean_of_", "median_of_", "min_of_", "max_of_")):
            stat_name, column = key.split("_of_", 1)
            numeric = pd.to_numeric(df[column], errors="coerce").dropna()
            if stat_name == "mean":
                actual = round(float(numeric.mean()), 3)
            elif stat_name == "median":
                actual = round(float(numeric.median()), 3)
            elif stat_name == "min":
                actual = round(float(numeric.min()), 3)
            else:
                actual = round(float(numeric.max()), 3)
            assert actual == pytest.approx(expected_value, abs=0.001)
        elif key.startswith("max_decimal_places_"):
            column = key.removeprefix("max_decimal_places_")
            assert _max_decimal_places(raw_df[column]) <= 1
        elif key.startswith("segment_") and key.endswith("_column"):
            assert expected_value in df.columns
        elif key.startswith("segment_") and key.endswith(("_mean", "_median", "_min", "_max")):
            prefix = key.rsplit("_", 1)[0]
            stat_name = key.rsplit("_", 1)[1]
            column = expected[f"{prefix}_column"]
            numeric = pd.to_numeric(df[column], errors="coerce").dropna()
            if stat_name == "mean":
                actual = round(float(numeric.mean()), 3)
            elif stat_name == "median":
                actual = round(float(numeric.median()), 3)
            elif stat_name == "min":
                actual = round(float(numeric.min()), 3)
            else:
                actual = round(float(numeric.max()), 3)
            assert actual == pytest.approx(expected_value, abs=0.001)
        elif key.startswith("segment_") and key.endswith("_non_null"):
            prefix = key.removesuffix("_non_null")
            column = expected[f"{prefix}_column"]
            numeric = pd.to_numeric(df[column], errors="coerce").dropna()
            assert int(numeric.shape[0]) == expected_value


def _assert_parquet_metrics(path: Path, expected: dict):
    assert path.exists() == expected["exists"]
    if not expected["exists"]:
        return

    df = pd.read_parquet(path)
    assert int(len(df)) == expected["rows"]
    assert list(df.columns) == expected["columns"]
    assert int(len(df.columns)) == expected["column_count"]


def _assert_figure_metrics(path: Path, expected: dict):
    assert path.exists() == expected["exists"]
    if not expected["exists"]:
        return

    assert path.stat().st_size > 0
    width, height = _png_dimensions(path)
    assert width > 0
    assert height > 0


def _png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    assert len(header) >= 24
    assert header.startswith(b"\x89PNG\r\n\x1a\n")
    return struct.unpack(">II", header[16:24])


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


def _format_fixture_summary(fixture_dir: Path, report: dict) -> str:
    lines = [f"\nRegression fixture: {fixture_dir.name}"]
    for block in report.get("blocks", []):
        lines.append(
            f"  {block.get('folder')}: {block.get('title')} | "
            f"segment {block.get('selected_distance')} / {block.get('selected_direction')} | "
            f"non-joint={block.get('show_non_joint')} | bin={block.get('evidence_time_bin')}"
        )
        for test in block.get("tests", []):
            if test.get("kind") == "table":
                lines.append(
                    f"    table {test.get('name')}: "
                    f"{test.get('rows')} rows, {test.get('column_count')} columns"
                )
            elif test.get("kind") == "analysis_cache":
                lines.append(
                    f"    parquet {test.get('name')}: "
                    f"{test.get('rows')} rows, {test.get('column_count')} columns"
                )
            elif test.get("kind") == "figure":
                lines.append(
                    f"    figure {test.get('name')}: {test.get('width')}x{test.get('height')} px"
                )
            for key, value in sorted((test.get("metrics") or {}).items()):
                if key.startswith(("segment_", "sum_", "mean_of_", "median_of_")):
                    lines.append(f"      {key}: {value}")
    return "\n".join(lines)


@pytest.mark.skipif(not FIXTURES, reason="No regression fixtures found under tests/regression/fixtures.")
@pytest.mark.parametrize("fixture_dir", FIXTURES, ids=lambda path: path.name)
def test_demo_fixture_package_integrity(fixture_dir: Path):
    manifest = _read_json(fixture_dir / "manifest.json")
    expected_metrics = _read_json(fixture_dir / "expected_metrics.json")
    regression_report = _read_json(fixture_dir / "regression_report.json")
    run_metadata = _read_json(fixture_dir / "config" / "run_metadata.json")

    assert (fixture_dir / "config" / "wspradar_config.config").exists()
    assert (fixture_dir / "regression_report.md").exists()
    assert run_metadata["export_signature"] == manifest["export_signature"]
    assert regression_report["export_signature"] == manifest["export_signature"]
    print(_format_fixture_summary(fixture_dir, regression_report))

    expected_block_folders = {
        block["folder"] for block in manifest.get("blocks", [])
        if block.get("folder")
    }
    assert expected_block_folders == set(expected_metrics.keys())

    for folder, block_metrics in expected_metrics.items():
        block_dir = fixture_dir / folder
        assert block_dir.exists() == block_metrics["exists"]
        if not block_metrics["exists"]:
            continue

        for table_name in TABLE_FILES:
            _assert_csv_metrics(block_dir / table_name, block_metrics["tables"][table_name])

        for figure_name in FIGURE_FILES:
            _assert_figure_metrics(block_dir / figure_name, block_metrics["figures"][figure_name])

        for parquet_name, parquet_metrics in block_metrics["analysis_caches"].items():
            _assert_parquet_metrics(block_dir / parquet_name, parquet_metrics)
