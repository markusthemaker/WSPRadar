from pathlib import Path

import pandas as pd
import pytest

from core.map_data_artifacts import (
    MapDataArtifactPaths,
    read_map_data_artifacts,
    write_map_data_artifacts,
)
from core.map_models import MapData


def _opportunity_map_data() -> MapData:
    """Return the smallest valid compact Success-map aggregate pair."""
    station_rows = pd.DataFrame({
        "SegmentID": ["[0-2500km] N"],
        "dist_label": ["[0-2500km]"],
        "dir_name": ["N"],
        "r_min": [0.0],
        "r_max": [2500.0],
        "az_bucket": [0.0],
        "peer_sign": ["K1ABC"],
        "peer_grid": ["FN31"],
        "peer_lat": [41.5],
        "peer_lon": [-72.5],
        "calc_dist": [6000.0],
        "calc_azimuth": [300.0],
        "spot_count": [4],
        "stat_val": [75.0],
        "opportunities": [4],
        "hits": [3],
        "misses": [1],
        "target_only": [2],
        "target_observations": [5],
        "successful_snr_median": [-12.5],
        "eligible": [True],
        "rate_pct": [75.0],
    })
    segment_rows = pd.DataFrame({
        "SegmentID": ["[0-2500km] N"],
        "dist_label": ["[0-2500km]"],
        "dir_name": ["N"],
        "r_min": [0.0],
        "r_max": [2500.0],
        "az_bucket": [0.0],
        "val": [75.0],
        "cnt": [1],
    })
    return MapData(
        station_rows=station_rows,
        segment_rows=segment_rows,
        analysis_id="RX_ABS",
        is_compare=False,
        is_sequential=False,
        analysis_kind="opportunity",
    )


def _compare_map_data(*, is_sequential: bool) -> MapData:
    """Return a valid simultaneous or scheduled-pair Compare aggregate pair."""
    station_columns = {
        "SegmentID": ["[0-2500km] N"],
        "dist_label": ["[0-2500km]"],
        "dir_name": ["N"],
        "r_min": [0.0],
        "r_max": [2500.0],
        "az_bucket": [0.0],
        "peer_sign": ["K1ABC"],
        "peer_grid": ["FN31"],
        "peer_lat": [41.5],
        "peer_lon": [-72.5],
        "calc_dist": [6000.0],
        "calc_azimuth": [300.0],
        "spot_count": [4],
        "stat_val": [1.5],
        "count_only_u": [0],
        "count_only_r": [0],
    }
    if is_sequential:
        station_columns["joint_pairs_count"] = [4]
    segment_rows = pd.DataFrame({
        "SegmentID": ["[0-2500km] N"],
        "dist_label": ["[0-2500km]"],
        "dir_name": ["N"],
        "r_min": [0.0],
        "r_max": [2500.0],
        "az_bucket": [0.0],
        "val": [1.5],
        "cnt": [1],
    })
    return MapData(
        station_rows=pd.DataFrame(station_columns),
        segment_rows=segment_rows,
        analysis_id="TX_COMP" if is_sequential else "RX_COMP",
        is_compare=True,
        is_sequential=is_sequential,
        analysis_kind="comparison",
    )


def test_compact_map_artifacts_round_trip_without_presentation_state(tmp_path):
    """Persist only map aggregates and reconstruct their pure scientific model."""
    map_data = _opportunity_map_data()
    paths = MapDataArtifactPaths(
        station_rows_path=tmp_path / "map_stations.parquet",
        segment_rows_path=tmp_path / "map_segments.parquet",
    )

    write_map_data_artifacts(map_data, paths)
    restored = read_map_data_artifacts(
        paths,
        analysis_id="RX_ABS",
        is_compare=False,
        is_sequential=False,
        analysis_kind="opportunity",
    )

    pd.testing.assert_frame_equal(restored.station_rows, map_data.station_rows)
    pd.testing.assert_frame_equal(restored.segment_rows, map_data.segment_rows)
    assert restored.analysis_id == "RX_ABS"
    assert restored.analysis_kind == "opportunity"
    assert restored.is_compare is False


@pytest.mark.parametrize("is_sequential", [False, True])
def test_compact_compare_map_artifacts_round_trip(tmp_path, is_sequential):
    """Preserve both simultaneous-spot and scheduled-pair Compare schemas."""
    map_data = _compare_map_data(is_sequential=is_sequential)
    paths = MapDataArtifactPaths(
        station_rows_path=tmp_path / "map_stations.parquet",
        segment_rows_path=tmp_path / "map_segments.parquet",
    )

    write_map_data_artifacts(map_data, paths)
    restored = read_map_data_artifacts(
        paths,
        analysis_id=map_data.analysis_id,
        is_compare=True,
        is_sequential=is_sequential,
        analysis_kind="comparison",
    )

    pd.testing.assert_frame_equal(restored.station_rows, map_data.station_rows)
    pd.testing.assert_frame_equal(restored.segment_rows, map_data.segment_rows)
    assert restored.is_sequential is is_sequential


def test_compact_success_map_allows_a_valid_empty_segment_table(tmp_path):
    """Keep station evidence reusable when no sector meets the map threshold."""
    map_data = _opportunity_map_data()
    map_data.segment_rows = map_data.segment_rows.iloc[0:0].copy()
    paths = MapDataArtifactPaths(
        station_rows_path=tmp_path / "map_stations.parquet",
        segment_rows_path=tmp_path / "map_segments.parquet",
    )

    write_map_data_artifacts(map_data, paths)
    restored = read_map_data_artifacts(
        paths,
        analysis_id="RX_ABS",
        is_compare=False,
        is_sequential=False,
        analysis_kind="opportunity",
    )

    assert restored.segment_rows.empty
    assert list(restored.segment_rows.columns) == list(map_data.segment_rows.columns)


def test_compact_compare_map_rejects_an_empty_segment_table(tmp_path):
    """Preserve the builder invariant that renderable Compare has sector data."""
    map_data = _compare_map_data(is_sequential=False)
    map_data.segment_rows = map_data.segment_rows.iloc[0:0].copy()

    with pytest.raises(ValueError, match="must be non-empty"):
        write_map_data_artifacts(
            map_data,
            MapDataArtifactPaths(
                station_rows_path=tmp_path / "map_stations.parquet",
                segment_rows_path=tmp_path / "map_segments.parquet",
            ),
        )


def test_compact_map_artifact_pair_removes_first_write_when_second_fails(tmp_path):
    """Never leave a reusable-looking half-published aggregate pair."""
    map_data = _opportunity_map_data()
    paths = MapDataArtifactPaths(
        station_rows_path=tmp_path / "map_stations.parquet",
        segment_rows_path=tmp_path / "map_segments.parquet",
    )
    write_calls = []

    def fail_second_write(_frame, path):
        write_calls.append(Path(path))
        if len(write_calls) == 2:
            Path(path).write_bytes(b"published segment aggregate")
            raise OSError("simulated segment publication failure")
        Path(path).write_bytes(b"station aggregate")

    with pytest.raises(OSError, match="segment publication failure"):
        write_map_data_artifacts(
            map_data,
            paths,
            artifact_writer=fail_second_write,
            artifact_deleter=lambda path: Path(path).unlink(),
        )

    assert write_calls == [paths.station_rows_path, paths.segment_rows_path]
    assert not paths.station_rows_path.exists()
    assert not paths.segment_rows_path.exists()


def test_compact_map_artifact_read_rejects_incomplete_station_schema(tmp_path):
    """Reject a registered artifact whose columns cannot serve map consumers."""
    map_data = _opportunity_map_data()
    frames = {
        "stations": map_data.station_rows.drop(columns=["eligible"]),
        "segments": map_data.segment_rows,
    }
    paths = MapDataArtifactPaths(
        station_rows_path=tmp_path / "stations.parquet",
        segment_rows_path=tmp_path / "segments.parquet",
    )

    with pytest.raises(ValueError, match="eligible"):
        read_map_data_artifacts(
            paths,
            analysis_id="RX_ABS",
            is_compare=False,
            is_sequential=False,
            analysis_kind="opportunity",
            artifact_reader=lambda path: (
                frames["stations"]
                if Path(path) == paths.station_rows_path
                else frames["segments"]
            ),
        )
