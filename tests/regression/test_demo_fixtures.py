"""Regression fixture integrity tests for WSPRadar prepared-result exports.

These tests intentionally start with package-level invariants. They make sure
golden demo exports stay complete and internally readable. A later test layer
can regenerate station tables and figures from the bundled parquet caches.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest


FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures"
TABLE_FILES = [
    "table_station_insights_current_segment.csv",
    "table_drilldown_selected_stations.csv",
    "table_drilldown_all_stations_current_segment.csv",
    "table_drilldown_all_stations_joint_only_current_segment.csv",
    "table_drilldown_all_stations_with_non_joint_current_segment.csv",
]
FIGURE_FILES = [
    "figure_map_highres.png",
    "figure_segment_insight.png",
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
    assert int(len(df)) == expected["rows"]
    assert list(df.columns) == expected["columns"]
    assert int(len(df.columns)) == expected["column_count"]


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

    assert path.stat().st_size == expected["bytes"]
    assert path.stat().st_size > 0


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
                    f"    figure {test.get('name')}: {test.get('bytes')} bytes"
                )
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
