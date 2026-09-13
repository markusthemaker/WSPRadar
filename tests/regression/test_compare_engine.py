import math

import pandas as pd
import pytest

from core.analysis_context import AnalysisContext, COMPARISON_HARDWARE_AB
from core.compare_engine import aggregate_compare_map_data, compare_footer_counts
from core.map_data import build_map_data_result
from core.presentation_context import PresentationContext
from core.result_diagnostics import BENCHMARK_NO_QUALIFYING_RESULT
from i18n import T
from ui.inspector.view_models import build_compare_inspector_view_model


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


def _identity_evidence_rows(
    *,
    is_sequential,
    peer_sign="K1AAA",
    peer_grid="JO31AA",
    paired_deltas_db=(),
    target_only_count=0,
    reference_only_count=0,
):
    """Build paired and disjoint one-sided evidence for one full peer identity."""
    evidence_rows = []
    observation_snrs = [(-12.0 + delta_db, -12.0) for delta_db in paired_deltas_db]
    observation_snrs.extend([(-10.0, None)] * target_only_count)
    observation_snrs.extend([(None, -12.0)] * reference_only_count)
    for observation_index, (target_snr_db, reference_snr_db) in enumerate(
        observation_snrs
    ):
        peer_fields = _base_row(peer_sign, peer_grid)
        pair_start_utc = pd.Timestamp("2026-05-27T12:00:00Z") + pd.Timedelta(
            minutes=10 * observation_index
        )
        if is_sequential:
            for role, snr_db, offset_minutes in (
                (1, target_snr_db, 0),
                (0, reference_snr_db, 2),
            ):
                if snr_db is not None:
                    evidence_rows.append({
                        **peer_fields,
                        "time": pair_start_utc + pd.Timedelta(minutes=offset_minutes),
                        "is_me": role,
                        "stat_val": snr_db,
                    })
        else:
            evidence_rows.append({
                **peer_fields,
                "time": pair_start_utc,
                "has_u": int(target_snr_db is not None),
                "has_r": int(reference_snr_db is not None),
                "snr_u_norm": target_snr_db,
                "snr_r_norm": reference_snr_db,
            })
    return evidence_rows


@pytest.mark.parametrize("is_sequential", [False, True])
@pytest.mark.parametrize("first_identity_depth", [1, 5])
@pytest.mark.parametrize(
    ("second_callsign", "second_locator"),
    [("K1AAA", "JO31AB"), ("K2BBB", "JO31AA")],
    ids=["same-callsign-different-full-locator", "different-callsign-same-locator"],
)
def test_compare_segment_support_counts_the_station_medians_it_weights(
    is_sequential, first_identity_depth, second_callsign, second_locator
):
    """Count each exact callsign/locator once, independent of evidence depth."""
    observations = pd.DataFrame(
        _identity_evidence_rows(
            is_sequential=is_sequential,
            paired_deltas_db=[2.0] * first_identity_depth,
        )
        + _identity_evidence_rows(
            is_sequential=is_sequential,
            peer_sign=second_callsign,
            peer_grid=second_locator,
            paired_deltas_db=[4.0],
        )
    )

    station_rows, segments = aggregate_compare_map_data(
        observations,
        is_sequential=is_sequential,
        min_spots=1,
        base_min_stations=2,
    )

    assert len(station_rows) == 2
    assert station_rows.set_index(["peer_sign", "peer_grid"])["stat_val"].to_dict() == {
        ("K1AAA", "JO31AA"): 2.0,
        (second_callsign, second_locator): 4.0,
    }
    assert sorted(station_rows["spot_count"]) == [1, first_identity_depth]
    assert len(segments) == 1
    segment = segments.iloc[0]
    assert float(segment["val"]) == pytest.approx(3.0)
    assert int(segment["cnt"]) == 2
    assert int(segment["total_spots"]) == first_identity_depth + 1
    footer_counts = compare_footer_counts(station_rows, max_dist_km=2500)
    assert footer_counts["stat_joint"] == int(segment["cnt"])
    assert footer_counts["spot_joint"] == first_identity_depth + 1

    stricter_station_rows, stricter_segments = aggregate_compare_map_data(
        observations,
        is_sequential=is_sequential,
        min_spots=1,
        base_min_stations=3,
    )

    assert stricter_segments.empty
    pd.testing.assert_frame_equal(stricter_station_rows, station_rows)


@pytest.mark.parametrize("is_sequential", [False, True])
def test_compare_station_evidence_floor_cannot_pool_locators_of_one_callsign(
    is_sequential,
):
    """Two below-floor identities cannot jointly qualify through their callsign."""
    observations = pd.DataFrame(
        _identity_evidence_rows(
            is_sequential=is_sequential,
            paired_deltas_db=[2.0],
            target_only_count=2,
        )
        + _identity_evidence_rows(
            is_sequential=is_sequential,
            peer_grid="JO31AB",
            paired_deltas_db=[4.0],
            reference_only_count=2,
        )
        + _identity_evidence_rows(
            is_sequential=is_sequential,
            peer_sign="K2BBB",
            paired_deltas_db=[6.0, 6.0],
        )
    )

    station_rows, segments = aggregate_compare_map_data(
        observations,
        is_sequential=is_sequential,
        min_spots=2,
        base_min_stations=1,
    )

    assert len(station_rows) == 3
    below_floor = station_rows[station_rows["peer_sign"] == "K1AAA"]
    assert len(below_floor) == 2
    assert below_floor["stat_val"].isna().all()
    assert (below_floor["spot_count"] == 0).all()
    assert int(segments.iloc[0]["cnt"]) == 1
    assert float(segments.iloc[0]["val"]) == pytest.approx(6.0)
    assert int(segments.iloc[0]["total_spots"]) == 2
    footer_counts = compare_footer_counts(station_rows, max_dist_km=2500)
    assert footer_counts["stat_joint"] == 1
    assert footer_counts["stat_only_u"] == 1
    assert footer_counts["stat_only_r"] == 1
    assert footer_counts["tot_stats"] == 3

    _, stricter_segments = aggregate_compare_map_data(
        observations,
        is_sequential=is_sequential,
        min_spots=2,
        base_min_stations=2,
    )
    assert stricter_segments.empty


@pytest.mark.parametrize("is_sequential", [False, True])
def test_compare_one_sided_identities_do_not_support_paired_segments(is_sequential):
    """Retain directional outcomes without increasing paired segment support."""
    observations = pd.DataFrame(
        _identity_evidence_rows(is_sequential=is_sequential, paired_deltas_db=[2.0])
        + _identity_evidence_rows(
            is_sequential=is_sequential, peer_grid="JO31AB", target_only_count=1
        )
        + _identity_evidence_rows(
            is_sequential=is_sequential, peer_grid="JO31AC", reference_only_count=1
        )
        + _identity_evidence_rows(
            is_sequential=is_sequential,
            peer_grid="JO31AD",
            target_only_count=1,
            reference_only_count=1,
        )
    )

    station_rows, segments = aggregate_compare_map_data(
        observations,
        is_sequential=is_sequential,
        min_spots=1,
        base_min_stations=1,
    )

    assert len(station_rows) == 4
    assert int(segments.iloc[0]["cnt"]) == 1
    assert float(segments.iloc[0]["val"]) == pytest.approx(2.0)
    assert int(segments.iloc[0]["total_spots"]) == 1
    footer_counts = compare_footer_counts(station_rows, max_dist_km=2500)
    assert footer_counts["stat_joint"] == 1
    assert footer_counts["stat_only_u"] == 1
    assert footer_counts["stat_only_r"] == 1
    assert footer_counts["stat_both_async"] == 1
    assert footer_counts["tot_stats"] == 4

    _, stricter_segments = aggregate_compare_map_data(
        observations,
        is_sequential=is_sequential,
        min_spots=1,
        base_min_stations=2,
    )
    assert stricter_segments.empty


@pytest.mark.parametrize("is_sequential", [False, True])
@pytest.mark.parametrize("language", ["en", "de"])
def test_compare_map_and_inspector_retain_same_callsign_at_two_full_locators(
    is_sequential, language
):
    """Recover the qualified map and preserve both identities in the Inspector."""
    observations = pd.DataFrame(
        _identity_evidence_rows(is_sequential=is_sequential, paired_deltas_db=[2.0])
        + _identity_evidence_rows(
            is_sequential=is_sequential, peer_grid="JO31AB", paired_deltas_db=[4.0]
        )
    )
    observations["peer_lat"] = observations["peer_grid"].map(
        {"JO31AA": 51.0 + 1.0 / 48.0, "JO31AB": 51.0 + 3.0 / 48.0}
    )
    observations["peer_lon"] = 6.0 + 1.0 / 24.0
    map_arguments = {
        "analysis_id": "TX_COMP" if is_sequential else "RX_COMP",
        "is_compare": True,
        "is_sequential": is_sequential,
        "analysis_kind": "comparison",
        "center_latitude": 48.0,
        "center_longitude": 11.0,
        "min_spots": 1,
        "min_opportunities": 5,
        "tx_ab_repeat_interval_minutes": 10,
        "tx_ab_target_start_minute": 0,
        "tx_ab_reference_start_minute": 2,
    }

    build_result = build_map_data_result(
        observations, base_min_stations=2, **map_arguments
    )

    assert build_result.diagnostic is None
    assert build_result.map_data is not None
    map_data = build_result.map_data
    assert len(map_data.segment_rows) == 1
    assert int(map_data.segment_rows.iloc[0]["cnt"]) == 2
    assert float(map_data.segment_rows.iloc[0]["val"]) == pytest.approx(3.0)
    inspector = build_compare_inspector_view_model(
        map_data.station_rows,
        analysis_id=map_arguments["analysis_id"],
        is_sequential=is_sequential,
        analysis_context=AnalysisContext(
            callsign="DL1MKS",
            reference_callsign="DL2ABC",
            comparison_mode=COMPARISON_HARDWARE_AB,
        ),
        presentation_context=PresentationContext(
            solar_label="", language=language, labels=T[language]
        ),
    )
    evidence_identities = inspector.build_evidence_identities()
    assert set(evidence_identities.itertuples(index=False, name=None)) == {
        ("K1AAA", "JO31AA"),
        ("K1AAA", "JO31AB"),
    }
    assert len(inspector.station_table) == 2
    footer_counts = compare_footer_counts(map_data.station_rows, max_dist_km=2500)
    assert footer_counts["stat_joint"] == len(evidence_identities) == 2

    rejected_result = build_map_data_result(
        observations, base_min_stations=3, **map_arguments
    )
    assert rejected_result.map_data is None
    assert rejected_result.diagnostic is not None
    assert rejected_result.diagnostic.reason == BENCHMARK_NO_QUALIFYING_RESULT


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


def test_simultaneous_compare_aggregation_respects_input_ownership():
    """Reuse a transferred raw frame without changing default nonmutation."""
    source = pd.DataFrame([
        {
            **_base_row(),
            "has_u": 1,
            "has_r": 1,
            "snr_u_norm": -10.04,
            "snr_r_norm": -12.04,
        },
        {
            **_base_row(),
            "has_u": 1,
            "has_r": 0,
            "snr_u_norm": -7.06,
            "snr_r_norm": None,
        },
    ])
    original = source.copy(deep=True)

    copied_station_rows, copied_segments = aggregate_compare_map_data(
        source,
        is_sequential=False,
        min_spots=1,
        base_min_stations=1,
    )

    pd.testing.assert_frame_equal(source, original)

    owned_source = original.copy(deep=True)
    owned_station_rows, owned_segments = aggregate_compare_map_data(
        owned_source,
        is_sequential=False,
        min_spots=1,
        base_min_stations=1,
        owns_input=True,
    )

    assert {
        "is_joint_spot",
        "is_u_spot",
        "is_r_spot",
        "spot_diff",
    }.issubset(owned_source.columns)
    assert float(owned_source.loc[0, "snr_u_norm"]) == -10.0
    pd.testing.assert_frame_equal(owned_station_rows, copied_station_rows)
    pd.testing.assert_frame_equal(owned_segments, copied_segments)


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


def test_four_minute_demo_schedule_counts_each_planned_pair():
    """Keep demo 09 on scheduled-pair rather than fixed-bin aggregation."""
    rows = [
        {**_base_row(), "time": "2026-05-27 12:00:00+00:00", "is_me": 1, "stat_val": -10.0},
        {**_base_row(), "time": "2026-05-27 12:02:00+00:00", "is_me": 0, "stat_val": -12.0},
        {**_base_row(), "time": "2026-05-27 12:04:00+00:00", "is_me": 1, "stat_val": -8.0},
        {**_base_row(), "time": "2026-05-27 12:06:00+00:00", "is_me": 0, "stat_val": -11.0},
    ]

    df_plot, segs = aggregate_compare_map_data(
        pd.DataFrame(rows),
        is_sequential=True,
        min_spots=1,
        base_min_stations=1,
        tx_ab_repeat_interval_minutes=4,
        tx_ab_target_start_minute=0,
        tx_ab_reference_start_minute=2,
    )

    station = df_plot.iloc[0]
    assert int(station["joint_pairs_count"]) == 2
    assert int(station["spot_count"]) == 2
    assert int(station["count_only_u"]) == 0
    assert int(station["count_only_r"]) == 0
    assert math.isclose(float(station["stat_val"]), 2.5, abs_tol=0.001)
    assert math.isclose(float(segs.iloc[0]["val"]), 2.5, abs_tol=0.001)


def test_periodic_sequential_compare_uses_micro_medians_and_counts_pairs():
    rows = [
        {
            **_base_row(),
            "time": "2026-05-27 12:00:00+00:00",
            "is_me": 1,
            "stat_val": -10.0,
        },
        {
            **_base_row(),
            "time": "2026-05-27 12:00:20+00:00",
            "is_me": 1,
            "stat_val": -8.0,
        },
        {
            **_base_row(),
            "time": "2026-05-27 12:02:00+00:00",
            "is_me": 0,
            "stat_val": -12.0,
        },
        {
            **_base_row(),
            "time": "2026-05-27 12:10:00+00:00",
            "is_me": 1,
            "stat_val": -6.0,
        },
        {
            **_base_row(),
            "time": "2026-05-27 12:22:00+00:00",
            "is_me": 0,
            "stat_val": -15.0,
        },
    ]

    station_rows, segments = aggregate_compare_map_data(
        pd.DataFrame(rows),
        is_sequential=True,
        min_spots=1,
        base_min_stations=1,
        tx_ab_repeat_interval_minutes=10,
        tx_ab_target_start_minute=0,
        tx_ab_reference_start_minute=2,
    )

    station = station_rows.iloc[0]
    assert int(station["joint_pairs_count"]) == 1
    assert int(station["spot_count"]) == 1
    assert int(station["count_only_u"]) == 1
    assert int(station["count_only_r"]) == 1
    assert int(station["target_decode_count"]) == 2
    assert math.isclose(float(station["stat_val"]), 3.0, abs_tol=0.001)
    assert math.isclose(float(segments.iloc[0]["val"]), 3.0, abs_tol=0.001)
