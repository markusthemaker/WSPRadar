"""Human-approved Milazzo Performance cards P01-P10 as production contracts.

The complete raw capture and exact review configuration are mandatory. Tests
never query public providers or regenerate expectations. Card anchors are human
verified; the exhaustive independent ledger extends that reviewed coverage.
"""

from copy import deepcopy
import ast
import builtins
import io
from pathlib import Path
import socket
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest
import requests

from milazzo_human_reference import (
    HUMAN_REFERENCE_DIRECTORY, REVIEWED_CARD_IDS, assert_performance_reference,
    assert_reference_number, read_reference_json, replay_performance,
    verify_human_reference_files,
)


CARD_TESTS = {
    "P01": "test_p01_endpoint_witnesses_and_excluded_cycles",
    "P02": "test_p02_target_only_successes_count_once",
    "P03": "test_p03_successful_normalized_snr_ranks",
    "P04": "test_p04_map_uses_equal_station_weights",
    "P05": "test_p05_distance_rates_reach_and_snr",
    "P06": "test_p06_peer_reach_retains_zero_success_receivers",
    "P07": "test_p07_complete_chronological_bin",
    "P08": "test_p08_folded_denominators_empty_evidence_and_window_end",
    "P09": "test_p09_folded_snr_date_weighting_and_absent_iqr",
    "P10": "test_p10_station_baselines_final_deviations_and_rendered_marker",
}


def _reject_network(*args, **kwargs):
    """Fail on provider access instead of allowing a fixture refresh."""
    pytest.fail("The approved Milazzo regression must remain entirely offline")


@pytest.fixture(scope="module", autouse=True)
def verified_human_reference():
    """Verify approval and file hashes, then reject network use for this module."""
    verify_human_reference_files(HUMAN_REFERENCE_DIRECTORY)
    with pytest.MonkeyPatch.context() as guard:
        guard.setattr(requests.sessions.Session, "request", _reject_network)
        guard.setattr(socket, "create_connection", _reject_network)
        guard.setattr(socket.socket, "connect", _reject_network)
        guard.setattr(socket.socket, "connect_ex", _reject_network)
        yield


@pytest.fixture(scope="module")
def human_performance_run(verified_human_reference, tmp_path_factory):
    """Replay once while forbidding any access to approved expected results."""
    original_io_open = io.open
    original_builtin_open = builtins.open
    forbidden_names = {
        path.name for path in HUMAN_REFERENCE_DIRECTORY.iterdir()
        if "expected" in path.name or path.name in {
            "review_cards.json", "review_packet.pdf", "approval.json",
            "reviewed_expectations.json",
        }
    }

    def check_read_path(file):
        """Keep any frozen expectation outside the production replay inputs."""
        if isinstance(file, (str, bytes, Path)):
            candidate = Path(file.decode() if isinstance(file, bytes) else file).resolve()
            assert not (candidate.parent == HUMAN_REFERENCE_DIRECTORY.resolve()
                        and candidate.name in forbidden_names), (
                            "Production replay attempted to read its expected answer", candidate
                        )

    def guarded_io_open(file, *args, **kwargs):
        """Guard pathlib and explicit io readers before opening a file."""
        check_read_path(file)
        return original_io_open(file, *args, **kwargs)

    def guarded_builtin_open(file, *args, **kwargs):
        """Guard builtin readers used by pandas and other input adapters."""
        check_read_path(file)
        return original_builtin_open(file, *args, **kwargs)

    with pytest.MonkeyPatch.context() as guard:
        guard.setattr(io, "open", guarded_io_open)
        guard.setattr(builtins, "open", guarded_builtin_open)
        return replay_performance(
            HUMAN_REFERENCE_DIRECTORY, tmp_path_factory.mktemp("milazzo-human-performance"),
        )


@pytest.fixture(scope="module")
def approved_expectations(verified_human_reference):
    """Read immutable human-reviewed numbers only at the assertion boundary."""
    return read_reference_json(HUMAN_REFERENCE_DIRECTORY, "reviewed_expectations.json")


@pytest.fixture(scope="module")
def reviewed_cards(verified_human_reference):
    """Index the preserved cards for printed raw-report and baseline checks."""
    return {card["id"]: card for card in read_reference_json(
        HUMAN_REFERENCE_DIRECTORY, "review_cards.json",
    )}


def _selected_receiver_rows(run):
    """Select the card's exact callsign-plus-full-locator receiver identity."""
    return run.processed.loc[
        run.processed["peer_sign"].eq("VE6PDQ") & run.processed["peer_grid"].eq("DO34IR")
    ]


def _slot(utc):
    """Convert a literal reviewed UTC anchor to its two-minute cycle index."""
    return int(pd.Timestamp(utc).timestamp()) // 120


def _profile_index(profile, utc):
    """Locate an exact reviewed bin start in production figure coordinates."""
    return list(profile["time_edge_ns"][:-1]).index(pd.Timestamp(utc).value)


def _assert_fields(actual, expected, mapping, *, index=None):
    """Compare named production fields with independently reviewed scalars."""
    for production_field, approved_field in mapping.items():
        production_value = actual[production_field] if index is None else actual[production_field][index]
        assert_reference_number(production_value, expected[approved_field], approved_field)


def test_all_native_rows_stations_maps_and_profiles_match_independent_oracle(human_performance_run):
    """Verify the complete raw-derived oracle before focused reviewed anchors."""
    assert len(human_performance_run.source_rows) == 65647
    assert len(human_performance_run.processed) == 2478
    assert human_performance_run.strict_rows.empty
    assert_performance_reference(human_performance_run, HUMAN_REFERENCE_DIRECTORY)


def test_p01_endpoint_witnesses_and_excluded_cycles(human_performance_run, approved_expectations,
                                                   reviewed_cards):
    """P01: peer activity is distinct from Target activity; silence is unknown."""
    run = human_performance_run
    selected_rows = _selected_receiver_rows(run)
    cases = {
        "2010-12-19T14:06Z": (1, 1, 1, 0, 0),
        "2010-12-19T18:00Z": (0, 1, 0, 1, 0),
        "2010-12-19T13:58Z": (1, 0, 1, 0, 1),
    }
    sample_rows = []
    for utc, expected in cases.items():
        row, = selected_rows.loc[selected_rows["time_slot"].eq(_slot(utc))].to_dict("records")
        assert tuple(row[column] for column in (
            "target_seen", "external_seen", "hit", "miss", "target_only",
        )) == expected
        assert row["opportunity"] == 1
        sample_rows.append(row)
    for utc in ("2010-12-19T12:06Z", "2010-12-19T15:20Z"):
        assert not selected_rows["time_slot"].eq(_slot(utc)).any()
    anchors = approved_expectations["P01"]
    for column, anchor in (("hit", "example_hits"), ("miss", "example_misses"),
                           ("target_only", "example_target_only"),
                           ("opportunity", "example_opportunities")):
        assert sum(row[column] for row in sample_rows) == anchors[anchor]
    assert_reference_number(100 * sum(row["hit"] for row in sample_rows) / len(sample_rows),
                            anchors["example_rate_pct"], "P01 rate")
    # Every report printed on P01 is part of the raw production input, including
    # the two excluded-cycle witnesses that do not appear in processed output.
    report_ids = {int(row[0]) for row in reviewed_cards["P01"]["source_rows"]["rows"]}
    assert report_ids <= set(run.source_rows["id"])
    source = run.source_rows.set_index("id")
    assert source.loc[44618722, ["tx_sign", "rx_sign"]].tolist() == ["KP4MD", "VE6PDQ"]
    assert source.loc[44629351, ["tx_sign", "rx_sign"]].tolist() == ["KP4MD", "K6HX"]
    assert source.loc[44605242, ["tx_sign", "rx_sign"]].tolist() == ["WD6DBM", "VE6PDQ"]


def test_p02_target_only_successes_count_once(human_performance_run, approved_expectations):
    """P02: the 22 Target-only decodes are already inside 57/79."""
    selected = _selected_receiver_rows(human_performance_run)
    approved = approved_expectations["P02"]
    for column, anchor in (("hit", "hits"), ("miss", "misses"),
                           ("target_only", "target_only"), ("opportunity", "opportunities")):
        assert int(selected[column].sum()) == approved[anchor]
    assert len(selected) == approved["all_rows"]
    assert (selected.loc[selected["target_only"].eq(1), ["hit", "opportunity"]] == 1).all().all()
    summary = human_performance_run.recipes["selected_temporal"]["selected_station_summary"]
    _assert_fields(summary, approved, {
        "confirmed_opportunities": "opportunities", "successful_outcomes": "hits",
        "counter_outcomes": "misses", "success_rate_pct": "rate_pct",
    })


def test_p03_successful_normalized_snr_ranks(human_performance_run, approved_expectations,
                                            reviewed_cards):
    """P03: all 57 normalized successes, including Target-only, define SNR."""
    selected = _selected_receiver_rows(human_performance_run)
    successful = selected.loc[selected["hit"].eq(1)].sort_values(["target_snr", "time_slot"])
    approved = approved_expectations["P03"]
    assert len(successful) == approved["hit_count"]
    observed = successful["target_snr"]
    for actual, field in ((observed.median(), "median_db"), (observed.quantile(.25), "q1_db"),
                           (observed.quantile(.75), "q3_db"), (observed.min(), "minimum_db"),
                           (observed.max(), "maximum_db")):
        assert_reference_number(actual, approved[field], f"P03 {field}")
    source = human_performance_run.source_rows.set_index("id")
    for rank, report_id, *details in reviewed_cards["P03"]["source_rows"]["rows"]:
        report = source.loc[int(report_id)]
        row = successful.iloc[int(rank) - 1]
        assert row["time_slot"] == int(pd.Timestamp(report["time"]).timestamp()) // 120
        assert_reference_number(row["target_snr"], details[-1], f"P03 rank {rank}")
        assert_reference_number(row["target_snr"], report["snr"] - report["power"] + 30,
                                f"P03 normalization {report_id}")


def test_p04_map_uses_equal_station_weights(human_performance_run, approved_expectations):
    """P04: unequal station support must not replace equal station weighting."""
    segment, = human_performance_run.segments.loc[
        human_performance_run.segments["SegmentID"].eq("[0-2500km] E")
    ].to_dict("records")
    approved = approved_expectations["P04"]
    _assert_fields(segment, approved, {"cnt": "stations", "total_hits": "hits", "total_misses": "misses"})
    assert segment["val"] == round(approved["station_balanced_rate_pct"], 1)
    assert segment["pooled_rate_pct"] == round(approved["pooled_rate_pct"], 1)
    assert segment["val"] != segment["pooled_rate_pct"]


def test_p05_distance_rates_reach_and_snr(human_performance_run, approved_expectations):
    """P05: 1500-2000 km combines three distinct scientific measures."""
    recipe = human_performance_run.recipes["distance"]
    index = list(recipe["distance_edges_km"][:-1]).index(1500)
    _assert_fields(recipe, approved_expectations["P05"], {
        "distance_peer_reach_pct": "peer_reach_pct",
        "distance_station_balanced_rate_pct": "station_balanced_rate_pct",
        "distance_observation_level_rate_pct": "pooled_rate_pct",
        "distance_successful_snr_median_db": "median_db",
        "distance_successful_snr_interval_lower_db": "q1_db",
        "distance_successful_snr_interval_upper_db": "q3_db",
    }, index=index)
    assert recipe["distance_qualifying_station_counts"][index] == 3
    assert recipe["distance_successful_snr_station_counts"][index] == 3


def test_p06_peer_reach_retains_zero_success_receivers(human_performance_run, approved_expectations):
    """P06: two zero-Hit receivers remain in the six-receiver denominator."""
    recipe = human_performance_run.recipes["distance"]
    index = list(recipe["distance_edges_km"][:-1]).index(4000)
    _assert_fields(recipe, approved_expectations["P06"], {
        "distance_qualifying_station_counts": "qualifying_stations",
        "distance_target_station_counts": "reached_stations",
        "distance_peer_reach_pct": "peer_reach_pct", "distance_target_counts": "hits",
        "distance_counter_counts": "misses",
        "distance_observation_level_rate_pct": "pooled_rate_pct",
        "distance_station_balanced_rate_pct": "station_balanced_rate_pct",
    }, index=index)
    stations = human_performance_run.stations
    cohort = stations.loc[stations["eligible"] & stations["calc_dist"].ge(4000)
                          & stations["calc_dist"].lt(4500)]
    assert len(cohort.loc[cohort["hits"].eq(0)]) == 2


def test_p07_complete_chronological_bin(human_performance_run, approved_expectations):
    """P07: six Hits/three Misses and SNR statistics in 00:00-03:00 UTC."""
    profile = human_performance_run.recipes["selected_temporal"]["chronological_profiles"]["3h"]
    index = _profile_index(profile, "2010-12-20T00:00Z")
    _assert_fields(profile, approved_expectations["P07"], {
        "opportunity_success_counts": "hits", "opportunity_counter_counts": "misses",
        "station_balanced_rate_pct": "rate_pct", "observation_level_rate_pct": "rate_pct",
        "station_success_votes": "station_hit_vote", "station_counter_votes": "station_miss_vote",
        "snr_median_db": "median_db", "snr_q1_db": "q1_db", "snr_q3_db": "q3_db",
    }, index=index)
    assert profile["station_counts"][index] == 1
    assert profile["snr_value_counts"][index] == 6
    row, = _selected_receiver_rows(human_performance_run).loc[
        lambda frame: frame["time_slot"].eq(_slot("2010-12-20T01:48Z"))
    ].to_dict("records")
    assert (row["target_only"], row["hit"], row["target_snr"]) == (1, 1, -31)


def test_p08_folded_denominators_empty_evidence_and_window_end(human_performance_run,
                                                              approved_expectations):
    """P08: absent date-hours affect display support, never invent opportunities."""
    recipe = human_performance_run.recipes["selected_temporal"]
    folded = recipe["folded_profile"]
    approved = approved_expectations["P08"]
    for hour in (12, 20):
        for field, suffix in (("represented_utc_date_counts", "date_count"),
                              ("opportunity_counter_counts_per_utc_date", "mean_misses"),
                              ("station_average_support_per_utc_date", "mean_station_support")):
            assert_reference_number(folded[field][hour], approved[f"hour{hour}_{suffix}"],
                                    ("P08", hour, field))
        assert folded["opportunity_success_counts"][hour] == 0
        assert folded["observation_level_rate_pct"][hour] == 0
        assert folded["station_balanced_rate_pct"][hour] == 0
    chronological = recipe["chronological_profiles"]["1h"]
    for utc, misses, has_evidence in (("2010-12-19T12:00Z", 0, False),
                                     ("2010-12-20T12:00Z", 2, True)):
        index = _profile_index(chronological, utc)
        assert chronological["opportunity_success_counts"][index] == 0
        assert chronological["opportunity_counter_counts"][index] == misses
        assert chronological["station_counts"][index] == int(has_evidence)
        assert_reference_number(chronological["observation_level_rate_pct"][index],
                                0 if has_evidence else None, ("P08 rate", utc))
    assert chronological["time_edge_ns"][-1] == pd.Timestamp("2010-12-20T20:00Z").value
    assert pd.Timestamp("2010-12-20T20:00Z").value not in chronological["time_edge_ns"][:-1]


def test_p09_folded_snr_date_weighting_and_absent_iqr(human_performance_run,
                                                    approved_expectations):
    """P09: two date-hour medians give -25.5 dB, without a visible IQR."""
    from core.matplotlib_runtime import dispose_agg_figure
    from ui.plots.opportunity_figures import _render_opportunity_temporal_snr_figure

    recipe = human_performance_run.recipes["selected_temporal"]
    approved = approved_expectations["P09"]
    _assert_fields(recipe["folded_profile"], approved, {
        "snr_value_counts": "date_hour_count", "snr_median_db": "median_db",
        "snr_q1_db": "q1_db", "snr_q3_db": "q3_db",
    }, index=16)
    selected = _selected_receiver_rows(human_performance_run)
    hours = pd.to_datetime(selected["time_slot"] * 120, unit="s", utc=True).dt.hour
    pooled = selected.loc[selected["hit"].eq(1) & hours.eq(16), "target_snr"].median()
    assert_reference_number(pooled, approved["pooled_raw_median_db"], "P09 pooled counterexample")
    assert pooled != approved["median_db"]
    figure = _render_opportunity_temporal_snr_figure(recipe)
    try:
        folded_axis, = [axis for axis in figure.axes
                        if axis.get_gid() == "success-temporal-snr-folded-axis"]
        marker, = [line for line in folded_axis.lines
                   if line.get_gid() == "success-temporal-snr-bin-median"]
        assert_reference_number(marker.get_ydata()[16], approved["median_db"], "P09 rendered marker")
        has_iqr = any(artist.get_gid() == "temporal-bin-iqr-band"
                      for artist in folded_axis.collections)
        assert has_iqr is approved["iqr_visible"]
    finally:
        dispose_agg_figure(figure)


def test_p10_station_baselines_final_deviations_and_rendered_marker(human_performance_run,
                                                                  approved_expectations,
                                                                  reviewed_cards):
    """P10: nine receiver deviations produce the rendered +1.5 dB marker."""
    from core.matplotlib_runtime import dispose_agg_figure
    from ui.plots.opportunity_figures import (
        _prepare_success_snr_anomalies, _render_opportunity_temporal_snr_figure,
    )

    run = human_performance_run
    approved = approved_expectations["P10"]
    recipe = run.recipes["segment_temporal"]
    profile = recipe["chronological_profiles"]["3h"]
    index = _profile_index(profile, "2010-12-20T18:00Z")
    assert index == len(profile["time_ns"]) - 1
    _assert_fields(profile, approved, {
        "snr_station_value_counts": "contributing_stations",
        "snr_station_balanced_median_db": "median_db",
        "snr_station_balanced_q1_db": "q1_db", "snr_station_balanced_q3_db": "q3_db",
    }, index=index)
    qualified_identities = run.stations.loc[run.stations["eligible"], ["peer_sign", "peer_grid"]]
    qualified_rows = run.processed.merge(qualified_identities, on=["peer_sign", "peer_grid"],
                                         how="inner", validate="many_to_one")
    anomalies, baselines = _prepare_success_snr_anomalies(qualified_rows)
    baseline_lookup = baselines.set_index(["peer_sign", "peer_grid"])
    final_rows = anomalies.loc[anomalies["time_slot"].ge(_slot("2010-12-20T18:00Z"))]
    final_medians = final_rows.groupby(["peer_sign", "peer_grid"], observed=True)[
        ["target_snr", "snr_anomaly_db"]
    ].median()
    reviewed_contributors = reviewed_cards["P10"]["source_rows"]["rows"]
    assert len(final_medians) == len(reviewed_contributors) == approved["contributing_stations"]
    for identity, expected_baseline, expected_median, expected_deviation in reviewed_contributors:
        peer = tuple(identity.split(" / "))
        assert_reference_number(baseline_lookup.loc[peer, "station_baseline_snr_db"],
                                expected_baseline, ("P10 baseline", peer))
        assert_reference_number(final_medians.loc[peer, "target_snr"], expected_median,
                                ("P10 bin median", peer))
        assert_reference_number(final_medians.loc[peer, "snr_anomaly_db"], expected_deviation,
                                ("P10 deviation", peer))
    assert_reference_number(final_medians.loc[("VE6PDQ", "DO34IR"), "snr_anomaly_db"],
                            approved["ve6pdq_anomaly_db"], "P10 VE6PDQ")
    figure = _render_opportunity_temporal_snr_figure(recipe)
    try:
        chronological_axis, = [axis for axis in figure.axes
                               if axis.get_gid() == "success-temporal-snr-chronological-axis"]
        artists = {line.get_gid(): line for line in chronological_axis.lines}
        for gid, field in (("success-temporal-snr-bin-median", "median_db"),
                            ("temporal-bin-iqr-q1", "q1_db"), ("temporal-bin-iqr-q3", "q3_db")):
            assert_reference_number(artists[gid].get_ydata()[-1], approved[field], ("P10 rendered", field))
        assert np.asarray(artists["success-temporal-snr-baseline"].get_ydata()).tolist() == [0, 0]
    finally:
        dispose_agg_figure(figure)


@pytest.mark.parametrize("mutation", ["target_only_hit", "pooled_map", "pooled_folded_snr", "final_marker_sign"])
def test_independent_oracle_rejects_scientific_mutations(human_performance_run, mutation):
    """Demonstrate that real historical failure modes trip the shared oracle."""
    # Validate the unchanged baseline here as well, so selecting this test alone
    # cannot mistake an unrelated comparator failure for a detected mutation.
    assert_performance_reference(human_performance_run, HUMAN_REFERENCE_DIRECTORY)
    run = SimpleNamespace(**vars(human_performance_run))
    if mutation == "target_only_hit":
        run.processed = run.processed.copy()
        row_index = run.processed.index[run.processed["target_only"].eq(1)][0]
        run.processed.loc[row_index, "hit"] = 0
    elif mutation == "pooled_map":
        run.segments = run.segments.copy()
        selected = run.segments["SegmentID"].eq("[0-2500km] E")
        run.segments.loc[selected, "val"] = run.segments.loc[selected, "pooled_rate_pct"]
    else:
        run.recipes = deepcopy(run.recipes)
        if mutation == "pooled_folded_snr":
            run.recipes["selected_temporal"]["folded_profile"]["snr_median_db"][16] = -27
        else:
            run.recipes["segment_temporal"]["chronological_profiles"]["3h"][
                "snr_station_balanced_median_db"
            ][-1] = -1.5
    with pytest.raises(AssertionError):
        assert_performance_reference(run, HUMAN_REFERENCE_DIRECTORY)


def test_approved_card_coverage_is_complete(approved_expectations):
    """Keep every durable card-to-test-to-expectation link executable and exact."""
    assert set(CARD_TESTS) == {f"P{number:02}" for number in range(1, 11)}
    assert all(callable(globals()[test_name]) for test_name in CARD_TESTS.values())
    coverage = read_reference_json(HUMAN_REFERENCE_DIRECTORY, "coverage.json")
    assert coverage["schema_version"] == 1
    assert coverage["packet_id"] == "MR01" and coverage["packet_revision"] == 2
    assert set(coverage["cards"]) == REVIEWED_CARD_IDS
    nodes = [card["pytest_node"] for card in coverage["cards"].values()]
    assert len(nodes) == len(set(nodes))
    benchmark_module = Path(__file__).with_name("test_milazzo_reference.py")
    benchmark_functions = {
        function.name for function in ast.parse(benchmark_module.read_text(encoding="utf-8")).body
        if isinstance(function, ast.FunctionDef)
    }
    benchmark_expectations = read_reference_json(HUMAN_REFERENCE_DIRECTORY, "benchmark_expected.json")
    for card_id, contract in coverage["cards"].items():
        assert contract["expected_key"] == card_id
        if card_id in CARD_TESTS:
            assert contract["expected_file"] == "reviewed_expectations.json"
            assert card_id in approved_expectations
            assert contract["pytest_node"] == (
                "tests/regression/test_milazzo_human_performance.py::" + CARD_TESTS[card_id]
            )
        else:
            assert contract["expected_file"] == "benchmark_expected.json"
            assert card_id in benchmark_expectations
            module_name, function_name = contract["pytest_node"].split("::")
            assert module_name == "tests/regression/test_milazzo_reference.py"
            assert function_name.startswith(f"test_human_{card_id.lower()}_")
            assert function_name in benchmark_functions
