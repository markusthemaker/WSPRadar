from pathlib import Path

import pandas as pd
import pytest

from core.analysis_context import AnalysisContext
from core.analysis_runner import apply_post_fetch_filters
from core.artifact_store import read_parquet_artifact, write_parquet_artifact
from core.map_data import build_map_data_result, map_preparation_columns
from core.map_data_artifacts import (
    MapDataArtifactPaths,
    read_map_data_artifacts,
    write_map_data_artifacts,
)
from core.map_models import MapData


def _processed_map_evidence(family, direction):
    """Exercise the production post-filter boundary before projecting map input."""
    is_compare = family != "performance"
    is_sequential = family == "scheduled"
    start = pd.Timestamp("2026-07-01T00:00:00Z")
    analysis = {
        "id": f"{direction}_{family}",
        "title": "Projection equivalence",
        "analysis_kind": "comparison" if is_compare else "opportunity",
        "is_compare": is_compare,
        "is_sequential": is_sequential,
        "analysis_start_utc": start,
        "analysis_end_utc": start + pd.Timedelta(hours=1),
    }
    rows = []
    for peer_sign, peer_grid, latitude, longitude in (
        ("K1AAA", "FN31AA", 41.02, -73.98),
        ("K1AAA", "FN31AB", 41.06, -73.98),
        ("DL2BBB", "JO62AA", 52.02, 12.02),
    ):
        peer = dict(peer_sign=peer_sign, peer_grid=peer_grid,
                    peer_lat=latitude, peer_lon=longitude)
        for cycle, (target_seen, reference_seen) in enumerate(
            ((1, 1), (1, 0), (0, 1), (1, 1))
        ):
            # Keep the cycle globally Target-active while other identities carry
            # Reference-only evidence through simultaneous synchronization.
            if peer_sign == "DL2BBB" and cycle == 2:
                target_seen = 1
            timestamp = start + pd.Timedelta(minutes=10 * cycle)
            if family == "performance":
                rows.append({
                    **peer, "time_slot": timestamp.value // 120_000_000_000,
                    "target_seen": target_seen, "external_seen": reference_seen,
                    "target_snr": -12.3 if target_seen else float("nan"),
                })
            elif is_sequential:
                for is_me, seen, offset, snr in (
                    (1, target_seen, 0, -12.3),
                    (0, reference_seen, 2, -15.7),
                ):
                    if seen:
                        rows.append({
                            **peer, "time": timestamp + pd.Timedelta(minutes=offset),
                            "is_me": is_me, "stat_val": snr,
                            "snr": snr, "power": 30.0,
                        })
            else:
                row = {
                    **peer, "time_slot": timestamp.value // 120_000_000_000,
                    "has_u": target_seen, "has_r": reference_seen,
                    "snr_u_norm": -12.3 if target_seen else float("nan"),
                    "snr_r_norm": -15.7 if reference_seen else float("nan"),
                    "best_ref_sign": "2 stations" if family == "local_median" else "DL3CCC",
                    "best_ref_dist": 2300.25,
                }
                if family == "local_median":
                    row["ref_detail_rows"] = "[('DL3CCC','JO62AB',2300.25,-15.7),('DL4DDD','JO62AC',2400.5,-15.7)]"
                rows.append(row)
    frame, warning = apply_post_fetch_filters(
        pd.DataFrame(rows), analysis,
        AnalysisContext(run_mode=direction, callsign="DL1MKS", qth="JN37"),
        47.0, 8.0, {"warn_no_data": "No data: {title}"},
    )
    assert warning is None
    return analysis, frame


@pytest.mark.parametrize("family,direction", [
    (family, direction)
    for family in ("performance", "reference", "local_median")
    for direction in ("RX", "TX")
] + [("scheduled", "TX")])
@pytest.mark.parametrize("minimum_support", [1, 4])
def test_projected_staged_evidence_preserves_complete_map_results(
    tmp_path, family, direction, minimum_support,
):
    """Narrow reads preserve identities, scientific aggregates and diagnostics."""
    analysis, evidence = _processed_map_evidence(family, direction)
    original_evidence = evidence.copy(deep=True)
    path = tmp_path / "evidence.parquet"
    write_parquet_artifact(evidence, path, index=False)
    original_bytes = path.read_bytes()
    full_frame = read_parquet_artifact(path)
    stored_evidence = full_frame.copy(deep=True)
    columns = map_preparation_columns(
        analysis_kind=analysis["analysis_kind"],
        is_compare=analysis["is_compare"],
        is_sequential=analysis["is_sequential"],
    )
    projected_frame = read_parquet_artifact(path, columns=list(columns))
    assert set(projected_frame.columns) == set(columns)
    assert len(projected_frame.columns) < len(full_frame.columns)
    if family == "local_median":
        assert "ref_detail_rows" not in projected_frame
        assert {"best_ref_sign", "best_ref_dist"}.issubset(projected_frame.columns)
    if family == "scheduled":
        assert "tx_ab_pair_id" in projected_frame
        assert "time" not in projected_frame
    kwargs = {
        "analysis_id": analysis["id"],
        "analysis_kind": analysis["analysis_kind"],
        "is_compare": analysis["is_compare"],
        "is_sequential": analysis["is_sequential"],
        "center_latitude": 47.0, "center_longitude": 8.0,
        "min_spots": minimum_support, "min_opportunities": minimum_support,
        "base_min_stations": minimum_support,
        "tx_ab_repeat_interval_minutes": 10,
        "tx_ab_target_start_minute": 0, "tx_ab_reference_start_minute": 2,
        "owns_input": True,
    }
    full_result = build_map_data_result(full_frame, **kwargs)
    projected_result = build_map_data_result(projected_frame, **kwargs)
    assert projected_result.diagnostic == full_result.diagnostic
    if full_result.map_data is None:
        assert projected_result.map_data is None
    else:
        pd.testing.assert_frame_equal(
            projected_result.map_data.station_rows,
            full_result.map_data.station_rows, check_exact=True,
        )
        pd.testing.assert_frame_equal(
            projected_result.map_data.segment_rows,
            full_result.map_data.segment_rows, check_exact=True,
        )
    # Inspectors and exports still read the complete, unchanged evidence file.
    pd.testing.assert_frame_equal(evidence, original_evidence, check_exact=True)
    pd.testing.assert_frame_equal(read_parquet_artifact(path), stored_evidence, check_exact=True)
    assert path.read_bytes() == original_bytes


@pytest.mark.parametrize("family", ["performance", "reference", "local_median", "scheduled"])
def test_map_projection_accepts_schema_correct_empty_evidence(tmp_path, family):
    analysis, evidence = _processed_map_evidence(family, "TX")
    empty_evidence = evidence.iloc[:0]
    path = tmp_path / "empty.parquet"
    write_parquet_artifact(empty_evidence, path, index=False)
    columns = map_preparation_columns(
        analysis_kind=analysis["analysis_kind"],
        is_compare=analysis["is_compare"],
        is_sequential=analysis["is_sequential"],
    )
    projected = read_parquet_artifact(path, columns=list(columns))
    full_frame = read_parquet_artifact(path)
    pd.testing.assert_frame_equal(projected, full_frame.loc[:, list(columns)], check_exact=True)


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
