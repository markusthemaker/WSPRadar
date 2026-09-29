"""Independent endpoint-participation contracts for RX and TX Performance.

The source reports and arithmetic below are authored by hand, not captured from
WSPRadar output. DL1TGT/JN37 is the Target RX in RX mode and the Target TX in TX
mode. K1AAA/FN31AA and K2BBB/FN31AA are peer TXs in RX and peer RXs in TX.

RX: peer TX -> Target RX directly confirms both endpoints. A report of that
same peer TX at K8EXT confirms the peer TX transmitted; a separate decode by
the Target RX establishes its listening activity in the same band and cycle.
TX: Target TX -> peer RX directly confirms both endpoints. K8EXT TX -> that
same peer RX confirms the peer RX listened; reception of the Target TX by any
receiver establishes Target TX activity in the same band and cycle.

The exact peer identity is callsign plus full locator. Merely observing that a
station transmits does not establish its listening activity, and merely seeing
it receive does not establish that it transmitted. No missing report is
invented as a Miss. The hand ledger explicitly exercises these asymmetries.

At minimum five opportunities, K1AAA has 5 H / 7 O and K2BBB has 2 H / 5 O.
Their Target-only successes are 2 each and are already included in H and O.
Equal-station rate = (5/7 + 2/5)/2 = 55.7142857143%; pooled = 7/12 = 58.3333%.
K1AAA successful normalized SNRs are [-30, -20, -10, 0, 10]: median -10,
quartiles -20/0, extrema -30/10. K2BBB has [-40, -20]: median -30.
"""

from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from reference_sql import execute_generated_sql

from core.analysis_context import AnalysisContext
from core.analysis_runner import apply_post_fetch_filters, build_analysis_batches
from core.map_data import build_map_data_result
from core.math_utils import locator_to_latlon
from core.opportunity_engine import (
    ABSOLUTE_METHOD_VERSION, OPPORTUNITY_DRILLDOWN_VIEW_COLUMNS,
    aggregate_opportunity_peers, opportunity_footer_counts,
)
from core.presentation_context import PresentationContext
from i18n import T
from ui.inspector.drilldown import _build_drilldown_table
from ui.inspector.presentation import success_figure_labels
from ui.inspector.view_models import build_opportunity_inspector_view_model
from ui.plots.drilldown_zoom_figures import build_drilldown_zoom_performance_snr_recipe
from ui.plots.opportunity_figures import (
    SUCCESS_SNR_REPRESENTATION_ACTUAL, SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION,
    _aggregate_success_distance_profile, _opportunity_temporal_recipe,
)


START_UTC = pd.Timestamp("2026-01-01T00:00:00Z")
END_UTC = pd.Timestamp("2026-01-02T00:10:00Z")
TARGET_CALLSIGN = "DL1TGT"
TARGET_LOCATOR = "JN37AA"
PEER_LOCATOR = "FN31AA"
IDENTITY_COLUMNS = ["time_slot", "peer_sign", "peer_grid"]


def _source_reports(mode):
    """Write physical TX -> RX reports with explicit endpoint roles.

    ``is_target_report`` means peer TX -> Target RX in RX mode, and
    Target TX -> peer RX in TX mode. Otherwise K8EXT is the external RX
    (RX mode) or external TX (TX mode); its report confirms the peer's
    transmitting or listening activity respectively.
    """
    reports = []

    def add(utc, peer, *, target, snr=-25, power=30, grid=PEER_LOCATOR,
            band=14, code=1, target_grid=TARGET_LOCATOR):
        analyzed_callsign = TARGET_CALLSIGN if target else "K8EXT"
        analyzed_locator = target_grid if target else "EM12AA"
        if mode == "RX":
            tx_sign, tx_loc = peer, grid
            rx_sign, rx_loc = analyzed_callsign, analyzed_locator
        else:
            tx_sign, tx_loc = analyzed_callsign, analyzed_locator
            rx_sign, rx_loc = peer, grid
        reports.append({
            "id": len(reports) + 1, "time": utc, "band": band, "code": code,
            "tx_sign": tx_sign, "tx_loc": tx_loc,
            "rx_sign": rx_sign, "rx_loc": rx_loc,
            "snr": snr, "power": power,
        })

    # A Target-only success. Strongest normalized report is -35-25+30=-30,
    # although -31 is the strongest raw SNR. Duplicate canonical identities
    # also span case/whitespace variants and must count only once.
    add("2026-01-01T00:00:00Z", "K1AAA", target=True, snr=-31, power=40)
    add("2026-01-01T00:00:15Z", "K1AAA", target=True, snr=-35, power=25)
    add("2026-01-01T00:00:30Z", " k1aaa ", target=True, snr=-36, power=25,
        grid=" fn31aa ")
    # An external report from a different full locator never confirms AA.
    add("2026-01-01T00:00:00Z", "K1AAA", target=False, grid="FN31AB")
    add("2026-01-01T00:00:00Z", "K2BBB", target=True, snr=-40)

    # Independently supported Hit, merged across a normalized peer identity.
    add("2026-01-01T00:02:00Z", "k1aaa", target=True, snr=-12, power=38,
        grid="fn31aa")
    add("2026-01-01T00:02:10Z", "K1AAA", target=False)
    add("2026-01-01T00:02:00Z", "K2BBB", target=False)
    add("2026-01-01T00:04:00Z", "K1AAA", target=True, snr=-10)
    add("2026-01-01T00:04:00Z", "K1AAA", target=False)

    # K9ACT is the peer TX heard by Target RX, or peer RX hearing Target TX.
    # That report establishes Target activity. External reports establish
    # K1AAA/K2BBB peer TX activity (RX) or their listening activity (TX).
    for utc in ("2026-01-01T00:06:00Z", "2026-01-02T00:04:00Z"):
        add(utc, "K9ACT", target=True, snr=-5, grid="FN31AC")
        add(utc, "K1AAA", target=False)
        add(utc, "K2BBB", target=False)
        add(utc, "K2BBB", target=False, snr=-15)  # Duplicate Miss support.

    add("2026-01-02T00:00:00Z", "K1AAA", target=True, snr=0)
    add("2026-01-02T00:00:00Z", "K1AAA", target=False)
    add("2026-01-02T00:00:00Z", "K2BBB", target=True, snr=-20)
    add("2026-01-02T00:02:00Z", "K1AAA", target=True, snr=10)

    # At 00:08 Target activity is known, but K1AAA's required peer-endpoint
    # activity is unknown. The opposite role is observed and is insufficient:
    # TX analysis: K1AAA TX -> K8OTH RX says nothing about K1AAA RX listening.
    # RX analysis: K8OTH TX -> K1AAA RX says nothing about K1AAA TX sending.
    add("2026-01-01T00:08:00Z", "K9ACT", target=True, grid="FN31AC")
    add("2026-01-01T00:08:00Z", "K8OTH", target=False, grid="FN31AD")
    if mode == "TX":
        reports[-1].update(tx_sign="K1AAA", tx_loc=PEER_LOCATOR)
    else:
        reports[-1].update(rx_sign="K1AAA", rx_loc=PEER_LOCATOR)

    # No valid same-band Target report at 01:00: neither a peer's external
    # report nor Target activity on another band/decode mode opens the gate.
    add("2026-01-01T01:00:00Z", "K5UNK", target=False)
    add("2026-01-01T01:00:00Z", "K6OFF", target=True, band=7)
    add("2026-01-01T01:00:00Z", "K7BAD", target=True, code=2)
    # Wrong Target grid cannot establish Target activity at 01:02.
    add("2026-01-01T01:02:00Z", "K6OFF", target=True, target_grid="JN38AA")
    add("2026-01-01T01:02:00Z", "K5UNK", target=False)
    # Reports in another band, decode mode, or the exclusive end are excluded.
    add("2026-01-01T00:00:00Z", "K6OFF", target=True, band=7)
    add("2026-01-01T00:00:00Z", "K7BAD", target=True, code=2)
    add("2026-01-02T00:10:00Z", "K0END", target=True)
    return pd.DataFrame.from_records(reports)


def _run_reference(mode, *, minimum=5, source_rows=None):
    """Run generated SQL and the production preparation/aggregation pipeline."""
    context = AnalysisContext(
        run_mode=mode, callsign=TARGET_CALLSIGN, qth=TARGET_LOCATOR, band="20m",
        min_confirmed_opportunities_per_peer=minimum,
    )
    presentation = PresentationContext(solar_label="All", labels=T["en"])
    latitude, longitude = locator_to_latlon(context.qth)
    analyses = build_analysis_batches(
        context, START_UTC, END_UTC, latitude, longitude, "AND band = '14'",
        presentation_context=presentation,
    )
    assert len(analyses) == 1
    analysis = analyses[0]
    sql_rows = execute_generated_sql(
        analysis.query, _source_reports(mode) if source_rows is None else source_rows,
    )
    processed, warning = apply_post_fetch_filters(
        sql_rows.copy(), analysis, context, latitude, longitude, T["en"],
    )
    assert warning is None
    map_result = build_map_data_result(
        processed, analysis_id=analysis.id, is_compare=analysis.is_compare,
         analysis_kind=analysis.analysis_kind,
        center_latitude=latitude, center_longitude=longitude,
        min_spots=1, min_opportunities=minimum, base_min_stations=1,


    )
    assert map_result.diagnostic is None
    stations = map_result.map_data.station_rows
    inspector = build_opportunity_inspector_view_model(
        stations, analysis_id=analysis.id, minimum_confirmed=minimum,
        presentation_context=presentation,
    )
    return SimpleNamespace(
        mode=mode, analysis=analysis, context=context, presentation=presentation,
        sql_rows=sql_rows, processed=processed, stations=stations,
        segments=map_result.map_data.segment_rows, inspector=inspector,
    )


@pytest.fixture(scope="module", params=["RX", "TX"], ids=["Target-RX-peer-TX", "Target-TX-peer-RX"])
def reference_run(request):
    """Share one independent source replay per explicitly named endpoint role."""
    return _run_reference(request.param)


def _peer_rows(reference_run, peer="K1AAA"):
    """Select one callsign/full-locator identity from processed evidence."""
    return reference_run.processed.loc[
        reference_run.processed["peer_sign"].eq(peer)
        & reference_run.processed["peer_grid"].eq(PEER_LOCATOR)
    ].sort_values("time_slot")


def test_generated_sql_and_production_processing_match_hand_endpoint_ledger(reference_run):
    """No expected flag/count/SNR is obtained from the production classifier."""
    assert ABSOLUTE_METHOD_VERSION == "opportunity-v3"
    assert reference_run.analysis.get("absolute_method_version") == "opportunity-v3"
    expected = pd.DataFrame([
        ("2026-01-01T00:00:00Z", 1, 0, -30, 1, 1, 0, 1, "H"),
        ("2026-01-01T00:02:00Z", 1, 1, -20, 1, 1, 0, 0, "H"),
        ("2026-01-01T00:04:00Z", 1, 1, -10, 1, 1, 0, 0, "H"),
        ("2026-01-01T00:06:00Z", 0, 1, None, 1, 0, 1, 0, "M"),
        ("2026-01-02T00:00:00Z", 1, 1, 0, 1, 1, 0, 0, "H"),
        ("2026-01-02T00:02:00Z", 1, 0, 10, 1, 1, 0, 1, "H"),
        ("2026-01-02T00:04:00Z", 0, 1, None, 1, 0, 1, 0, "M"),
    ], columns=[
        "utc", "target_seen", "external_seen", "target_snr", "opportunity",
        "hit", "miss", "target_only", "outcome",
    ])
    actual = _peer_rows(reference_run).copy()
    actual["utc"] = pd.to_datetime(actual["time_slot"] * 120, unit="s", utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    actual["outcome"] = actual["outcome"].astype(str)
    pd.testing.assert_frame_equal(
        actual[list(expected.columns)].reset_index(drop=True), expected,
        check_dtype=False,
    )
    assert not reference_run.processed.duplicated(IDENTITY_COLUMNS).any()
    assert len(reference_run.processed) == 17
    assert reference_run.processed[["opportunity", "hit", "miss", "target_only"]].sum().tolist() == [17, 10, 7, 7]
    assert set(reference_run.processed["peer_sign"]) == {"K1AAA", "K2BBB", "K9ACT", "K8OTH"}
    other_locator = reference_run.processed.query("peer_sign == 'K1AAA' and peer_grid == 'FN31AB'").iloc[0]
    assert (other_locator["target_seen"], other_locator["external_seen"], other_locator["hit"], other_locator["miss"]) == (0, 1, 0, 1)
    unknown_slot = int(pd.Timestamp("2026-01-01T00:08:00Z").timestamp() // 120)
    assert unknown_slot not in actual["time_slot"].tolist()


def test_unknown_endpoint_activity_never_becomes_a_miss(reference_run):
    """Even a preprocessed zero/zero row stays unknown and contributes nothing."""
    unknown = pd.DataFrame([{
        "time_slot": int(START_UTC.timestamp() // 120), "peer_sign": "K5UNK",
        "peer_grid": PEER_LOCATOR, "target_seen": 0, "external_seen": 0,
        "target_snr": np.nan,
    }])
    latitude, longitude = locator_to_latlon(TARGET_LOCATOR)
    processed, warning = apply_post_fetch_filters(
        pd.concat([reference_run.sql_rows, unknown], ignore_index=True),
        reference_run.analysis, reference_run.context, latitude, longitude, T["en"],
    )
    assert warning is None
    unknown_processed = processed.loc[processed["peer_sign"].eq("K5UNK")].iloc[0]
    assert unknown_processed[["opportunity", "hit", "miss", "target_only"]].tolist() == [0, 0, 0, 0]
    assert unknown_processed["outcome"] == ""
    unknown_peer = aggregate_opportunity_peers(processed, min_opportunities=1).query("peer_sign == 'K5UNK'").iloc[0]
    assert not unknown_peer["eligible"] and pd.isna(unknown_peer["rate_pct"])


def test_station_thresholds_map_insights_and_reach_include_target_only_once(reference_run):
    """Check fixed eligible populations, totals, weighting, reach and SNR."""
    eligible = reference_run.stations.loc[reference_run.stations["eligible"]].set_index("peer_sign")
    assert set(eligible.index) == {"K1AAA", "K2BBB"}
    assert eligible.loc["K1AAA", ["hits", "misses", "opportunities", "target_only", "target_observations"]].tolist() == [5, 2, 7, 2, 5]
    assert eligible.loc["K2BBB", ["hits", "misses", "opportunities", "target_only", "target_observations"]].tolist() == [2, 3, 5, 2, 2]
    assert eligible.loc["K1AAA", "successful_snr_median"] == -10
    assert eligible.loc["K2BBB", "successful_snr_median"] == -30
    at_six = aggregate_opportunity_peers(reference_run.processed, min_opportunities=6)
    assert at_six.loc[at_six["eligible"], "peer_sign"].tolist() == ["K1AAA"]
    inspector = reference_run.inspector
    assert (inspector.confirmed_station_count, inspector.target_station_count, inspector.zero_target_station_count) == (2, 2, 0)
    assert (inspector.target_count, inspector.counter_count, inspector.confirmed_opportunity_count) == (7, 5, 12)
    assert inspector.station_balanced_rate_pct == pytest.approx(55.714285714285715)
    assert inspector.observation_level_rate_pct == pytest.approx(58.333333333333336)
    assert inspector.median_opportunities_per_station == 6
    segment = reference_run.segments.iloc[0]
    assert len(reference_run.segments) == 1
    assert segment[["cnt", "total_hits", "total_misses", "total_opportunities", "total_target_only"]].tolist() == [2, 7, 5, 12, 4]
    assert segment["val"] == 55.7 and segment["pooled_rate_pct"] == 58.3
    assert opportunity_footer_counts(reference_run.stations, max_dist_km=22000) == {
        "stat_target": 2, "stat_counter_only": 0, "spot_target": 7,
        "spot_counter": 5, "tot_stats": 2, "tot_spots": 12,
    }
    _, distance_profile = _aggregate_success_distance_profile(reference_run.stations, [(0, 22000)])
    occupied = distance_profile.loc[distance_profile["qualifying_station_count"].gt(0)]
    assert len(occupied) == 1
    distance = occupied.iloc[0]
    assert distance["peer_reach_pct"] == 100
    assert distance["station_balanced_rate_pct"] == pytest.approx(55.714285714285715)
    assert distance["observation_level_rate_pct"] == pytest.approx(58.333333333333336)
    # The distance distribution weights two station medians (-30, -10),
    # rather than pooling seven successful raw reports.
    assert distance[["successful_snr_station_count", "successful_snr_median_db", "successful_snr_min_db", "successful_snr_max_db", "successful_snr_q1_db", "successful_snr_q3_db"]].tolist() == [2, -20, -30, -10, -25, -15]


def _temporal_recipe(reference_run, *, selected=False):
    """Use production profiles for the full eligible cohort or exact K1AAA path."""
    peers = reference_run.stations
    options = {}
    if selected:
        peers = peers.loc[peers["peer_sign"].eq("K1AAA") & peers["peer_grid"].eq(PEER_LOCATOR)]
        options = {
            "population_mode": SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION,
            "snr_representation": SUCCESS_SNR_REPRESENTATION_ACTUAL,
        }
    return _opportunity_temporal_recipe(
        "Independent endpoint evidence", "All", peers, reference_run.processed,
        START_UTC, END_UTC, reference_run.presentation.absolute_terms(reference_run.mode),
        figure_labels=success_figure_labels(T["en"], reference_run.analysis.id),
        time_bin_options=["24h"], time_bin_default="24h", **options,
    )


def test_chronological_and_folded_profiles_use_the_same_success_population(reference_run):
    """Keep direct successes in chronological counts and per-date folded support."""
    recipe = _temporal_recipe(reference_run)
    chronological = recipe["chronological_profiles"]["24h"]
    np.testing.assert_array_equal(chronological["target_counts"], [4, 3])
    np.testing.assert_array_equal(chronological["counter_counts"], [3, 2])
    np.testing.assert_array_equal(chronological["station_counts"], [2, 2])
    np.testing.assert_allclose(chronological["station_balanced_rate_pct"], [54.16666666666667, 58.33333333333333])
    np.testing.assert_allclose(chronological["observation_level_rate_pct"], [57.142857142857146, 60])
    folded = recipe["folded_profile"]
    assert folded["target_counts"][0] == 7
    assert folded["counter_counts"][0] == 5
    assert folded["opportunity_success_counts_per_utc_date"][0] == 3.5
    assert folded["opportunity_counter_counts_per_utc_date"][0] == 2.5
    assert folded["station_balanced_rate_pct"][0] == pytest.approx(55.714285714285715)
    assert folded["observation_level_rate_pct"][0] == pytest.approx(58.333333333333336)
    # Only K1AAA reaches the three-success station-relative SNR minimum.
    assert recipe["snr_baseline_station_count"] == 1


def test_selected_station_successful_snr_quartiles_and_folded_date_weighting(reference_run):
    """Check independently sorted successful SNRs and date-hour weighting."""
    recipe = _temporal_recipe(reference_run, selected=True)
    summary = recipe["selected_station_summary"]
    assert (summary["successful_outcomes"], summary["counter_outcomes"], summary["confirmed_opportunities"]) == (5, 2, 7)
    assert summary["success_rate_pct"] == pytest.approx(71.42857142857143)
    assert summary["successful_snr_median_db"] == -10
    chronological = recipe["chronological_profiles"]["24h"]
    np.testing.assert_array_equal(chronological["snr_value_counts"], [3, 2])
    np.testing.assert_allclose(chronological["snr_median_db"], [-20, 5])
    np.testing.assert_allclose(chronological["snr_q1_db"], [-25, 2.5])
    np.testing.assert_allclose(chronological["snr_q3_db"], [-15, 7.5])
    # Folding gives each date-hour median (-20 and +5) one vote.
    folded = recipe["folded_profile"]
    assert folded["snr_value_counts"][0] == 2
    assert folded["snr_median_db"][0] == -7.5
    assert folded["snr_q1_db"][0] == -13.75
    assert folded["snr_q3_db"][0] == -1.25
    assert chronological["snr_value_edges_db"][0] <= -30
    assert chronological["snr_value_edges_db"][-1] >= 10


def test_native_drilldown_recipe_includes_target_only_snr_and_current_method(reference_run):
    """Native points contain both direct-only successes and supported Hits."""
    recipe = build_drilldown_zoom_performance_snr_recipe(
        _peer_rows(reference_run), start_utc=START_UTC, end_utc=END_UTC,
        title="Independent native evidence", panel_title="Successful Target SNR",
        x_label="UTC", y_label="dB at 30 dBm", empty_text="No successful decode",
        evidence_unit_label="Successful peer-cycle",
    )
    assert recipe["performance_method_version"] == "opportunity-v3"
    assert recipe["point_count"] == 5
    np.testing.assert_array_equal(recipe["metric_db"], [-30, -20, -10, 0, 10])
    expected_times = pd.to_datetime([
        "2026-01-01T00:00:00Z", "2026-01-01T00:02:00Z", "2026-01-01T00:04:00Z",
        "2026-01-02T00:00:00Z", "2026-01-02T00:02:00Z",
    ], utc=True).as_unit("ns").asi8
    np.testing.assert_array_equal(recipe["point_utc_ns"], expected_times)


@pytest.mark.parametrize("mode", ["RX", "TX"], ids=["Target-RX-peer-TX", "Target-TX-peer-RX"])
def test_dates_with_only_target_only_successes_are_represented_in_folded_evidence(mode):
    """Two direct decodes independently establish both endpoints on two dates.

    RX: K1AAA peer TX -> DL1TGT Target RX; TX: DL1TGT Target TX -> K1AAA
    peer RX. There is no external supporting report on either date. The
    successful report itself confirms the TX transmitted and the RX listened.
    """
    source = _source_reports(mode)
    target_endpoint = "rx_sign" if mode == "RX" else "tx_sign"
    peer_endpoint = "tx_sign" if mode == "RX" else "rx_sign"
    source = source.loc[
        source[target_endpoint].eq(TARGET_CALLSIGN)
        & source[peer_endpoint].str.strip().str.upper().eq("K1AAA")
        & source["time"].isin([
            "2026-01-01T00:00:00Z", "2026-01-01T00:00:15Z",
            "2026-01-01T00:00:30Z", "2026-01-02T00:02:00Z",
        ])
    ]
    run = _run_reference(mode, minimum=1, source_rows=source)
    assert run.processed[["hit", "miss", "opportunity", "target_only"]].sum().tolist() == [2, 0, 2, 2]
    recipe = _temporal_recipe(run, selected=True)
    assert recipe["utc_date_count"] == 2
    chronological = recipe["chronological_profiles"]["24h"]
    np.testing.assert_array_equal(chronological["target_counts"], [1, 1])
    np.testing.assert_array_equal(chronological["snr_value_counts"], [1, 1])
    np.testing.assert_allclose(chronological["snr_median_db"], [-30, 10])
    folded = recipe["folded_profile"]
    assert folded["represented_utc_date_counts"][0] == 2
    assert folded["opportunity_success_counts_per_utc_date"][0] == 1
    assert folded["station_balanced_rate_pct"][0] == 100
    assert folded["observation_level_rate_pct"][0] == 100
    assert folded["snr_value_counts"][0] == 2
    assert folded["snr_median_db"][0] == -10


def test_station_and_projected_drilldown_exports_preserve_success_and_provenance(reference_run, tmp_path):
    """Pin canonical exported counts/SNR and direct-only success provenance."""
    inspector = reference_run.inspector
    station_export = inspector.build_export_station_table()
    terms = reference_run.presentation.absolute_terms(reference_run.mode)
    stations_by_name = station_export.set_index(inspector.export_station_column)
    assert stations_by_name[terms["target_column"]].to_dict() == {"K1AAA": 5, "K2BBB": 2}
    assert stations_by_name[terms["counter_column"]].to_dict() == {"K1AAA": 2, "K2BBB": 3}
    parquet_path = tmp_path / "independent_performance.parquet"
    reference_run.processed.to_parquet(parquet_path, index=False)
    selected = station_export.loc[station_export[inspector.export_station_column].eq("K1AAA")]
    drilldown, message = _build_drilldown_table(
        parquet_path, selected, inspector.export_station_column,
        inspector.export_locator_column, inspector.distance_column,
        inspector.azimuth_column, reference_run.analysis.id,
         False, False, TARGET_CALLSIGN, "", T["en"],
    )
    assert message is None
    assert len(drilldown) == 7
    assert drilldown[terms["target_column"]].sum() == 5
    assert drilldown[terms["counter_column"]].sum() == 2
    target_only = drilldown.loc[drilldown["Outcome"].eq("Target-only")]
    assert len(target_only) == 2
    assert target_only[terms["target_column"]].tolist() == [1, 1]
    snrs = drilldown["Target SNR (dB @ 30 dBm)"].dropna().sort_values().tolist()
    assert snrs == [-30, -20, -10, 0, 10]
    restored = pd.read_parquet(parquet_path, columns=list(OPPORTUNITY_DRILLDOWN_VIEW_COLUMNS))
    assert restored[["hit", "miss", "target_only"]].sum().tolist() == [10, 7, 7]
