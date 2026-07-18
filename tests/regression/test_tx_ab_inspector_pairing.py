"""Regression coverage for scheduled TX A/B evidence and drill-down pairing."""

import pandas as pd

from core.tx_ab_schedule import assign_tx_ab_pair_columns
from i18n import T
from ui.inspector.drilldown import _build_drilldown_table
from ui.inspector.evidence_data import _build_evidence_points


def _scheduled_rows_for_two_receivers():
    """Return two receiver identities sharing one planned A/B pair."""
    rows = pd.DataFrame(
        {
            "peer_sign": ["K1AAA", "K1AAA", "K1AAA", "K2BBB", "K2BBB"],
            "peer_grid": ["FN31", "FN31", "FN31", "EM12", "EM12"],
            "time": pd.to_datetime(
                [
                    "2026-07-01T00:00:00Z",
                    "2026-07-01T00:00:00Z",
                    "2026-07-01T00:02:00Z",
                    "2026-07-01T00:00:00Z",
                    "2026-07-01T00:02:00Z",
                ],
                utc=True,
            ),
            "is_me": [1, 1, 0, 1, 0],
            "stat_val": [3.0, 5.0, 2.0, 20.0, 5.0],
            "snr": [-17.0, -15.0, -18.0, 0.0, -15.0],
            "power": [30, 30, 30, 30, 30],
            "RX Station": ["K1AAA", "K1AAA", "K1AAA", "K2BBB", "K2BBB"],
            "Locator": ["FN31", "FN31", "FN31", "EM12", "EM12"],
            "km": [500, 500, 500, 1200, 1200],
            "az": [270, 270, 270, 90, 90],
        }
    )
    return assign_tx_ab_pair_columns(
        rows,
        repeat_interval_minutes=10,
        target_start_minute_utc=0,
        reference_start_minute_utc=2,
    )


def test_periodic_evidence_pairs_each_receiver_identity_independently():
    """Do not combine observations from different receivers in one pair median."""
    station_rows = _scheduled_rows_for_two_receivers()
    identities = station_rows[["peer_sign", "peer_grid"]].drop_duplicates()

    evidence = _build_evidence_points(
        station_rows,
        identities,
        is_compare=True,
        is_sequential=True,
        tx_ab_repeat_interval_minutes=10,
        tx_ab_target_start_minute=0,
        tx_ab_reference_start_minute=2,
    )

    metrics_by_station = dict(zip(evidence["station"], evidence["metric"]))
    assert metrics_by_station == {"K1AAA": 2.0, "K2BBB": 15.0}


def test_periodic_drilldown_keeps_peer_identity_and_pair_delta_separate():
    """Show traceable peer rows without allowing cross-peer scheduled pairs."""
    station_rows = _scheduled_rows_for_two_receivers()
    selected_meta = station_rows[
        ["RX Station", "Locator", "km", "az"]
    ].drop_duplicates()

    drilldown, info = _build_drilldown_table(
        "",
        selected_meta,
        "RX Station",
        "Locator",
        "km",
        "az",
        analysis_id="TX_COMP",
        is_compare=True,
        is_sequential=True,
        show_non_joint=False,
        is_local_median=False,
        col_u_name="Setup A",
        ref_header="Setup B",
        t=T["en"],
        station_rows_df=station_rows,
        tx_ab_repeat_interval_minutes=10,
        tx_ab_target_start_minute=0,
        tx_ab_reference_start_minute=2,
    )

    assert info is None
    assert "RX Station" in drilldown.columns
    pair_delta_column = T["en"]["tbl_col_pair_delta"]
    deltas_by_station = {
        station: set(rows[pair_delta_column])
        for station, rows in drilldown.groupby("RX Station")
    }
    assert deltas_by_station == {
        "K1AAA": {"+2.0"},
        "K2BBB": {"+15.0"},
    }
