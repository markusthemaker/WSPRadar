import math

import pandas as pd

from core.compare_engine import aggregate_compare_map_data, compare_footer_counts


def _base_row(peer_sign="K1AAA", peer_grid="FN31aa"):
    return {
        "SegmentID": "[0-2500km] W",
        "dist_label": "[0-2500km]",
        "dir_name": "W",
        "r_min": 0.0,
        "r_max": 2500.0,
        "az_bucket": 12.0,
        "peer_sign": peer_sign,
        "peer_grid": peer_grid,
        "peer_lat": 41.5,
        "peer_lon": -72.5,
        "calc_dist": 1000.0,
        "calc_azimuth": 270.0,
    }


def test_simultaneous_compare_aggregation_preserves_joint_and_non_joint_counts():
    rows = []
    rows.append({**_base_row(), "has_u": 1, "has_r": 1, "snr_u_norm": -10.0, "snr_r_norm": -12.0})
    rows.append({**_base_row(), "has_u": 1, "has_r": 1, "snr_u_norm": -8.0, "snr_r_norm": -12.0})
    rows.append({**_base_row(), "has_u": 1, "has_r": 0, "snr_u_norm": -7.0, "snr_r_norm": None})
    rows.append({**_base_row("K2BBB", "EM10aa"), "has_u": 0, "has_r": 1, "snr_u_norm": None, "snr_r_norm": -20.0})

    df_plot, segs = aggregate_compare_map_data(
        pd.DataFrame(rows),
        is_sequential=False,
        min_spots=1,
        base_min_stations=1,
    )

    station = df_plot[df_plot["peer_sign"] == "K1AAA"].iloc[0]
    assert int(station["spot_count"]) == 2
    assert int(station["count_only_u"]) == 1
    assert int(station["count_only_r"]) == 0
    assert math.isclose(float(station["stat_val"]), 3.0, abs_tol=0.001)

    reference_only = df_plot[df_plot["peer_sign"] == "K2BBB"].iloc[0]
    assert int(reference_only["spot_count"]) == 0
    assert int(reference_only["count_only_u"]) == 0
    assert int(reference_only["count_only_r"]) == 1
    assert pd.isna(reference_only["stat_val"])

    segment = segs.iloc[0]
    assert math.isclose(float(segment["val"]), 3.0, abs_tol=0.001)
    assert int(segment["cnt"]) == 1
    assert int(segment["total_spots"]) == 2


def test_compare_footer_counts_preserve_async_spot_bucket_for_joint_stations():
    df_plot = pd.DataFrame([
        {
            "r_min": 0.0,
            "spot_count": 2,
            "count_only_u": 1,
            "count_only_r": 0,
        },
        {
            "r_min": 0.0,
            "spot_count": 0,
            "count_only_u": 0,
            "count_only_r": 1,
        },
        {
            "r_min": 2500.0,
            "spot_count": 4,
            "count_only_u": 0,
            "count_only_r": 0,
        },
    ])

    counts = compare_footer_counts(df_plot, max_dist_km=2500)

    assert counts["stat_joint"] == 1
    assert counts["stat_only_r"] == 1
    assert counts["stat_both_async"] == 0
    assert counts["spot_joint"] == 2
    assert counts["spot_both_async"] == 1
    assert counts["spot_only_r"] == 1
    assert counts["tot_stats"] == 2
    assert counts["tot_spots"] == 4


def test_sequential_compare_aggregation_preserves_joint_bin_threshold():
    rows = []
    rows.append({
        **_base_row(),
        "time": "2026-05-27 12:01:00+00:00",
        "is_me": 1,
        "stat_val": -10.0,
    })
    rows.append({
        **_base_row(),
        "time": "2026-05-27 12:03:00+00:00",
        "is_me": 0,
        "stat_val": -12.0,
    })
    rows.append({
        **_base_row(),
        "time": "2026-05-27 12:12:00+00:00",
        "is_me": 1,
        "stat_val": -8.0,
    })

    df_plot, segs = aggregate_compare_map_data(
        pd.DataFrame(rows),
        is_sequential=True,
        min_spots=1,
        base_min_stations=1,
        tx_ab_bin_minutes=8,
    )

    station = df_plot.iloc[0]
    assert int(station["joint_bins_count"]) == 1
    assert int(station["spot_count"]) == 2
    assert int(station["count_only_u"]) == 1
    assert int(station["count_only_r"]) == 0
    assert math.isclose(float(station["stat_val"]), 2.0, abs_tol=0.001)
    assert math.isclose(float(segs.iloc[0]["val"]), 2.0, abs_tol=0.001)
