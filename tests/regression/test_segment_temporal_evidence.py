"""Regression contracts for segment-scoped Compare temporal evidence."""

import pandas as pd

from ui.inspector import evidence_data


def test_segment_evidence_points_keep_only_qualifying_callsign_locator_identities(
    monkeypatch,
):
    """Use the segment histogram population rather than every matching callsign row."""
    segment_identities = pd.DataFrame(
        {
            "peer_sign": ["A1AAA", "B2BBB"],
            "peer_grid": ["AA00", "BB00"],
        }
    )
    parquet_rows = pd.DataFrame(
        {
            "peer_sign": ["A1AAA", "A1AAA", "B2BBB", "C3CCC"],
            "peer_grid": ["AA00", "ZZ99", "BB00", "CC00"],
            "time_slot": [100, 100, 101, 102],
            "has_u": [1, 1, 1, 1],
            "has_r": [1, 1, 1, 1],
            "snr_u_norm": [5.0, 50.0, -2.0, 7.0],
            "snr_r_norm": [2.0, -50.0, -1.0, 1.0],
        }
    )
    parquet_read = {}

    def read_parquet(_path, *, columns, filters):
        parquet_read["columns"] = columns
        parquet_read["filters"] = filters
        return parquet_rows[columns].copy()

    monkeypatch.setattr(evidence_data, "read_parquet_artifact", read_parquet)

    segment_points = evidence_data._build_segment_evidence_points(
        segment_identities,
        "segment.parquet",
        is_compare=True,
        is_sequential=False,
    )

    assert list(
        segment_points[["station", "grid", "metric"]].itertuples(
            index=False,
            name=None,
        )
    ) == [
        ("A1AAA", "AA00", 3.0),
        ("B2BBB", "BB00", -1.0),
    ]
    assert parquet_read["columns"] == [
        "peer_sign",
        "peer_grid",
        "time_slot",
        "has_u",
        "has_r",
        "snr_u_norm",
        "snr_r_norm",
    ]
    assert parquet_read["filters"] == [
        ("peer_sign", "in", ["A1AAA", "B2BBB"])
    ]
