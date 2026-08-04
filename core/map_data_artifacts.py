"""Versioned disk persistence for compact map-render aggregates."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import pandas as pd

from core.artifact_store import (
    ARTIFACT_STORE,
    read_parquet_artifact,
    write_parquet_artifact,
)
from core.map_data import validate_map_analysis_mode
from core.map_models import MapData


MAP_DATA_ARTIFACT_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class MapDataArtifactPaths:
    """Identify the two Parquet tables required to reconstruct one ``MapData``."""

    station_rows_path: Path
    segment_rows_path: Path


_COMMON_STATION_COLUMNS = frozenset({
    "SegmentID",
    "dist_label",
    "dir_name",
    "r_min",
    "r_max",
    "az_bucket",
    "peer_sign",
    "peer_grid",
    "peer_lat",
    "peer_lon",
    "calc_dist",
    "calc_azimuth",
    "spot_count",
    "stat_val",
})
_COMPARE_STATION_COLUMNS = frozenset({
    "count_only_u",
    "count_only_r",
})
_SEQUENTIAL_COMPARE_STATION_COLUMNS = frozenset({"joint_pairs_count"})
_OPPORTUNITY_STATION_COLUMNS = frozenset({
    "opportunities",
    "hits",
    "misses",
    "target_only",
    "target_observations",
    "successful_snr_median",
    "eligible",
    "rate_pct",
})
_COMMON_SEGMENT_COLUMNS = frozenset({
    "SegmentID",
    "dist_label",
    "dir_name",
    "r_min",
    "r_max",
    "az_bucket",
})
_NONEMPTY_SEGMENT_COLUMNS = frozenset({"val", "cnt"})


def _missing_columns(frame: pd.DataFrame, required_columns) -> list[str]:
    """Return required columns absent from one aggregate table."""
    return sorted(set(required_columns).difference(frame.columns))


def _validate_map_data_frames(
    station_rows: pd.DataFrame,
    segment_rows: pd.DataFrame,
    *,
    is_compare: bool,
    is_sequential: bool,
    analysis_kind: str,
) -> None:
    """Reject aggregate tables that cannot satisfy map and Inspector consumers."""
    is_opportunity = validate_map_analysis_mode(
        analysis_kind=analysis_kind,
        is_compare=is_compare,
    )
    if not isinstance(station_rows, pd.DataFrame) or station_rows.empty:
        raise ValueError("Map station aggregate must be a non-empty DataFrame")
    if not isinstance(segment_rows, pd.DataFrame):
        raise ValueError("Map segment aggregate must be a DataFrame")
    if not is_opportunity and segment_rows.empty:
        raise ValueError("Benchmark map segment aggregate must be non-empty")

    required_station_columns = set(_COMMON_STATION_COLUMNS)
    if is_opportunity:
        required_station_columns.update(_OPPORTUNITY_STATION_COLUMNS)
    else:
        required_station_columns.update(_COMPARE_STATION_COLUMNS)
        if is_sequential:
            required_station_columns.update(_SEQUENTIAL_COMPARE_STATION_COLUMNS)
    missing_station_columns = _missing_columns(
        station_rows,
        required_station_columns,
    )
    if missing_station_columns:
        raise ValueError(
            "Map station aggregate omitted required columns: "
            + ", ".join(missing_station_columns)
        )

    required_segment_columns = set(_COMMON_SEGMENT_COLUMNS)
    if not segment_rows.empty:
        required_segment_columns.update(_NONEMPTY_SEGMENT_COLUMNS)
    missing_segment_columns = _missing_columns(
        segment_rows,
        required_segment_columns,
    )
    if missing_segment_columns:
        raise ValueError(
            "Map segment aggregate omitted required columns: "
            + ", ".join(missing_segment_columns)
        )


def write_map_data_artifacts(
    map_data: MapData,
    paths: MapDataArtifactPaths,
    *,
    artifact_writer: Callable = write_parquet_artifact,
    artifact_deleter: Callable = ARTIFACT_STORE.delete,
) -> MapDataArtifactPaths:
    """Write each map table atomically and remove a partial pair on failure."""
    _validate_map_data_frames(
        map_data.station_rows,
        map_data.segment_rows,
        is_compare=map_data.is_compare,
        is_sequential=map_data.is_sequential,
        analysis_kind=map_data.analysis_kind,
    )
    station_rows_path = Path(paths.station_rows_path)
    segment_rows_path = Path(paths.segment_rows_path)
    if station_rows_path.resolve() == segment_rows_path.resolve():
        raise ValueError("Map station and segment artifacts require distinct paths")

    written_paths: list[Path] = []
    try:
        written_paths.append(station_rows_path)
        artifact_writer(map_data.station_rows, station_rows_path)
        written_paths.append(segment_rows_path)
        artifact_writer(map_data.segment_rows, segment_rows_path)
    except BaseException:
        for written_path in written_paths:
            try:
                artifact_deleter(written_path)
            except Exception:
                continue
        raise
    return paths


def read_map_data_artifacts(
    paths: MapDataArtifactPaths,
    *,
    analysis_id: str,
    is_compare: bool,
    is_sequential: bool,
    analysis_kind: str,
    artifact_reader: Callable = read_parquet_artifact,
) -> MapData:
    """Read and validate compact tables before reconstructing one ``MapData``."""
    station_rows = artifact_reader(Path(paths.station_rows_path))
    segment_rows = artifact_reader(Path(paths.segment_rows_path))
    _validate_map_data_frames(
        station_rows,
        segment_rows,
        is_compare=is_compare,
        is_sequential=is_sequential,
        analysis_kind=analysis_kind,
    )
    return MapData(
        station_rows=station_rows,
        segment_rows=segment_rows,
        analysis_id=str(analysis_id),
        is_compare=bool(is_compare),
        is_sequential=bool(is_sequential),
        analysis_kind=str(analysis_kind),
    )
