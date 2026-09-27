"""Hand-checkable TX normalization, global activity gating and all-row retention.

Figure 6's 44 digitized markers reconcile with reciprocal RX observations;
Figure 7's 47 compact anchors reconcile with TX observations at common power.
All 120 overlay reports are checked separately against frozen source arithmetic.
Separate independent calculations protect TX selection and the supplied RX path.
"""

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import socket
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest
import requests

from reference_sql import execute_generated_sql

from config import BAND_MAP
from core.analysis_runner import (
    apply_post_fetch_filters, build_analysis_batches, should_retry_without_decode_filter,
)
from core.compare_engine import compare_footer_counts
from core.map_data import build_map_data_result
from core.math_utils import locator_to_latlon
from core.matplotlib_runtime import dispose_agg_figure
from core.presentation_context import PresentationContext
from i18n import T
from ui.analysis_context_adapter import build_analysis_context_from_session_state
from ui.config_io import apply_config_state_values, validate_config_document
from ui.inspector.drilldown import _build_drilldown_table
from ui.inspector.evidence_data import (
    _build_compare_unit_rows, _compare_joint_evidence_points,
    _retain_thresholded_compare_outcomes,
)
from ui.inspector.view_models import build_compare_inspector_view_model
from ui.plots.benchmark_evidence_figures import (
    _aggregate_compare_chronological_coverage, _prepare_compare_coverage_units,
)
from ui.plots.evidence_figures import (
    _segment_figure_export_recipe, render_segment_insight_export_figure,
)


REFERENCE_DIRECTORY = Path(__file__).parent / "reference_fixtures" / "milazzo_tx_reference_v1"
RX_REFERENCE_DIRECTORY = Path(__file__).parent / "reference_fixtures" / "milazzo_fig6_rx_v1"
PUBLICATION_DIRECTORY = Path(__file__).parent / "reference_fixtures" / "milazzo_publication_overlays_v1"
HUMAN_REFERENCE_DIRECTORY = Path(__file__).parent / "reference_fixtures" / "milazzo_human_review_v2"
REPOSITORY_DIRECTORY = Path(__file__).resolve().parents[2]
KEY_COLUMNS = ["time_slot", "peer_sign", "peer_grid"]
PAPER_START_UTC = pd.Timestamp("2010-12-19T12:00:00Z")
PAPER_END_UTC = pd.Timestamp("2010-12-20T20:00:00Z")
ENDPOINT_COLUMNS = [
    "direction", "series", "time_slot", "utc", "peer_grid", "sql_snr_at_30_dbm",
    "snr_at_37_dbm", "passes_target_active_gate",
]


def _read_json(filename):
    return json.loads((REFERENCE_DIRECTORY / filename).read_text(encoding="utf-8"))


def _read_csv(filename):
    return pd.read_csv(REFERENCE_DIRECTORY / filename, float_precision="round_trip")


def _utc_nanoseconds(timestamps):
    return pd.to_datetime(timestamps, utc=True).to_numpy(dtype="datetime64[ns]").astype(np.int64)


def _reject_network(*args, **kwargs):
    pytest.fail("The Milazzo reference is mandatory and entirely offline")


@pytest.fixture(scope="module", autouse=True)
def verified_reference_files():
    manifest = _read_json("manifest.json")
    assert manifest["schema_version"] == 1
    paths = [record["path"] for record in manifest["files"]]
    assert len(paths) == len(set(paths))
    assert {
        "README.md", "demo.config", "source_rows.csv", "source_rows.parquet",
        "capture_provenance.json", "expected_sql_rows.csv", "expected_retained_rows.csv",
        "expected_classified_groups.csv", "expected_source_ledger.csv",
        "expected_native_units.csv", "expected_paired_rows.csv", "expected_active_cycles.csv",
        "expected_station_rows.csv", "expected_coverage_3h.csv", "expected_summary.json",
        "publication_features.json", "publication_markers.csv", "publication_mapping.md",
        "publication_archive_reports.csv", "publication_mapping_candidates.csv",
        "user_kp4md_tx_reports.tsv", "user_wb6rqn_tx_40m_rows.csv",
    }.issubset(paths)
    for record in manifest["files"]:
        path = (REFERENCE_DIRECTORY / record["path"]).resolve()
        assert path.is_relative_to(REFERENCE_DIRECTORY.resolve())
        contents = path.read_bytes()
        assert len(contents) == record["bytes"], record["path"]
        assert hashlib.sha256(contents).hexdigest() == record["sha256"], record["path"]
    with pytest.MonkeyPatch.context() as guard:
        guard.setattr(requests.sessions.Session, "request", _reject_network)
        guard.setattr(socket, "create_connection", _reject_network)
        guard.setattr(socket.socket, "connect", _reject_network)
        guard.setattr(socket.socket, "connect_ex", _reject_network)
        yield


def _calculate_run(source_rows, *, max_distance_km=None, configuration_document=None):
    configuration = validate_config_document(
        _read_json("demo.config") if configuration_document is None else configuration_document
    )
    session_values = {"lang": "en"}
    apply_config_state_values(configuration, session_values)
    session_values["run_mode"] = configuration["analysis_direction"].upper()
    context = build_analysis_context_from_session_state(session_values)
    if max_distance_km is not None:
        context = replace(context, max_peer_distance_km=max_distance_km)
    latitude, longitude = locator_to_latlon(context.qth)
    presentation = PresentationContext(solar_label="All", labels=T["en"])
    analyses = build_analysis_batches(
        context, configuration["start_utc"], configuration["end_utc"], latitude, longitude,
        f"AND band = '{BAND_MAP[context.band]}'", presentation_context=presentation,
    )
    assert len(analyses) == 1
    analysis = analyses[0]
    strict_rows = execute_generated_sql(analysis.query, source_rows)
    assert strict_rows.empty and should_retry_without_decode_filter(strict_rows, analysis)
    sql_rows = execute_generated_sql(analysis.get("legacy_query"), source_rows)
    processed, warning = apply_post_fetch_filters(
        sql_rows.copy(), analysis, context, latitude, longitude, T["en"],
    )
    assert warning is None
    preparation = build_map_data_result(
        processed, analysis_id=analysis.id, is_compare=analysis.is_compare,
        is_sequential=analysis.is_sequential, analysis_kind=analysis.analysis_kind,
        center_latitude=latitude, center_longitude=longitude,
        min_spots=context.min_joint_spots_per_station,
        min_opportunities=context.min_confirmed_opportunities_per_peer,
        base_min_stations=context.min_joint_stations_per_map_segment,
        tx_ab_repeat_interval_minutes=context.tx_ab_repeat_interval_minutes,
        tx_ab_target_start_minute=context.tx_ab_target_start_minute,
        tx_ab_reference_start_minute=context.tx_ab_reference_start_minute,
    )
    assert preparation.diagnostic is None and preparation.map_data is not None
    stations = preparation.map_data.station_rows
    inspector = build_compare_inspector_view_model(
        stations, analysis_id=analysis.id, is_sequential=analysis.is_sequential,
        analysis_context=context, presentation_context=presentation,
    )
    units = _build_compare_unit_rows(
        processed, stations, analysis.is_sequential,
        paired_identity_df=inspector.build_evidence_identities(),
    )
    units = _retain_thresholded_compare_outcomes(units, stations)
    points = _compare_joint_evidence_points(units, require_paired_eligible=True)
    return SimpleNamespace(
        configuration=configuration, context=context, analysis=analysis,
        latitude=latitude, longitude=longitude, source_rows=source_rows,
        strict_rows=strict_rows, sql_rows=sql_rows, processed=processed,
        stations=stations, inspector=inspector, units=units, points=points,
        segment_rows=preparation.map_data.segment_rows,
    )


@pytest.fixture(scope="module")
def reference_run(verified_reference_files):
    return _calculate_run(_read_csv("source_rows.csv"))


def _assert_scientific_rows(actual, expected):
    pd.testing.assert_frame_equal(
        actual[list(expected.columns)].sort_values(KEY_COLUMNS).reset_index(drop=True),
        expected.sort_values(KEY_COLUMNS).reset_index(drop=True),
        check_dtype=False, check_exact=False, rtol=0, atol=1e-12,
    )


def _canonical_units(units):
    canonical = units.copy()
    canonical["time_slot"] = _utc_nanoseconds(canonical.evidence_utc) // 120_000_000_000
    canonical["delta_snr_db"] = canonical.metric
    return canonical.sort_values(KEY_COLUMNS).reset_index(drop=True)


def _assert_native_units(actual, expected):
    actual = _canonical_units(actual)
    expected = expected.sort_values(KEY_COLUMNS).reset_index(drop=True)
    for column in [*KEY_COLUMNS, "outcome"]:
        np.testing.assert_array_equal(actual[column], expected[column])
    for column in ("target_snr_db", "reference_snr_db", "delta_snr_db"):
        np.testing.assert_allclose(actual[column], expected[column], rtol=0, atol=1e-12, equal_nan=True)


def _outcome_counts(units):
    return units.outcome.value_counts().to_dict()


def test_demo_uses_figure6_rx_direction_and_preserves_other_scientific_settings(installed_rx_demo_run):
    installed = json.loads((REPOSITORY_DIRECTORY / "config/demos/05_milazzo_tx_buddy.config").read_text(encoding="utf-8"))
    frozen_settings = _read_json("demo.config")["settings"]
    installed_settings = installed["settings"]
    for section in ("comparison_parameters", "advanced_parameters"):
        assert installed_settings[section] == frozen_settings[section]
    installed_core = installed_settings["core_parameters"]
    frozen_core = frozen_settings["core_parameters"]
    assert {key: value for key, value in installed_core.items() if key not in {"time_selection", "analysis_direction"}} == {
        key: value for key, value in frozen_core.items() if key not in {"time_selection", "analysis_direction"}
    }
    assert installed["profile"]["id"] == "milazzo_tx_buddy"
    assert installed_core["analysis_direction"] == "rx"
    assert frozen_core["analysis_direction"] == "tx"
    assert pd.Timestamp(installed_core["time_selection"]["start_utc"]) == PAPER_START_UTC
    assert pd.Timestamp(installed_core["time_selection"]["end_utc"]) == PAPER_END_UTC
    assert frozen_core["time_selection"] == {
        "start_utc": "2010-12-18T00:00Z", "end_utc": "2010-12-21T00:00Z",
    }
    assert installed_rx_demo_run.context.run_mode == "RX"
    assert installed_rx_demo_run.context.max_peer_distance_km == 5000
    assert installed_rx_demo_run.context.reference_snr_correction_db == 0
    description = installed["profile"]["description"]["en"]
    assert "Figure 6" in description and "DO34IR" in description.upper() and "DO34" in description
    assert description.index("WSPRadar_Demo_Milazzo_Figure6.pdf") < description.index("WSPRadar_Demo_Milazzo_Figure7.pdf")
    assert "have not yet been reconciled" not in description


def test_tx_publication_window_matches_the_independent_frozen_subpopulation(reference_run):
    configuration = _read_json("demo.config")
    configuration["settings"]["core_parameters"]["time_selection"] = {
        "start_utc": PAPER_START_UTC.strftime("%Y-%m-%dT%H:%MZ"),
        "end_utc": PAPER_END_UTC.strftime("%Y-%m-%dT%H:%MZ"),
    }
    publication_run = _calculate_run(reference_run.source_rows, configuration_document=configuration)
    expected = _read_csv("expected_native_units.csv")
    timestamps = pd.to_datetime(expected.evidence_utc, utc=True)
    expected = expected[timestamps.ge(PAPER_START_UTC) & timestamps.lt(PAPER_END_UTC)]
    _assert_native_units(publication_run.units, expected)
    assert _outcome_counts(publication_run.units) == {"target_only": 988, "joint": 45, "reference_only": 21}
    selected = publication_run.units[publication_run.units.peer_sign.eq("VE6PDQ")]
    assert _outcome_counts(selected) == {"target_only": 56, "joint": 1}
    assert len(publication_run.points) == 45 and publication_run.points.plot_time.nunique() == 9
    assert publication_run.points.metric.median() == -4


def test_historical_code_zero_source_reaches_real_sql_through_permitted_fallback(reference_run):
    assert len(reference_run.source_rows) == 1992
    assert reference_run.source_rows.code.eq(0).all()
    assert reference_run.strict_rows.empty
    assert should_retry_without_decode_filter(reference_run.strict_rows, reference_run.analysis)
    assert not should_retry_without_decode_filter(reference_run.sql_rows, reference_run.analysis)
    _assert_scientific_rows(reference_run.sql_rows, _read_csv("expected_sql_rows.csv"))
    assert len(reference_run.sql_rows) == 1946


def test_portable_source_csv_preserves_the_original_capture(reference_run):
    captured = pd.read_parquet(REFERENCE_DIRECTORY / "source_rows.parquet")
    source = reference_run.source_rows
    assert list(captured.columns) == list(source.columns)
    for column in source.columns:
        if column == "time":
            np.testing.assert_array_equal(_utc_nanoseconds(captured[column]), _utc_nanoseconds(source[column]))
        else:
            np.testing.assert_array_equal(captured[column], source[column])


def test_supplied_tx_reports_match_all_89_captured_ve6pdq_reports(reference_run):
    attached = pd.read_csv(
        REFERENCE_DIRECTORY / "user_kp4md_tx_reports.tsv", sep="\t", encoding="utf-8-sig",
    )
    assert len(attached) == 90
    assert attached["mode"].eq("unknown").all()
    attached.columns = attached.columns.str.strip()
    attached = attached.rename(columns={"y-m-d utc": "utc"})
    attached = attached.loc[attached.MHz.between(7, 7.3, inclusive="neither")]
    inline = _read_csv("user_wb6rqn_tx_40m_rows.csv")
    assert len(attached) == 63 and len(inline) == 26
    supplied = pd.concat([attached, inline], ignore_index=True).rename(columns={
        "utc": "time", "txCall": "tx_sign", "txGrid": "tx_loc",
        "rxCall": "rx_sign", "rxGrid": "rx_loc", "SNR": "snr",
    })
    supplied["power"] = supplied.W.map({2: 33, 5: 37})
    assert supplied.power.notna().all()
    columns = ["time", "tx_sign", "tx_loc", "rx_sign", "rx_loc", "snr", "power"]
    expected = supplied[columns].copy()
    actual = reference_run.source_rows.loc[reference_run.source_rows.rx_sign.eq("VE6PDQ"), columns].copy()
    for reports in (expected, actual):
        reports["time"] = _utc_nanoseconds(reports.time)
    pd.testing.assert_frame_equal(
        actual.sort_values(columns).reset_index(drop=True),
        expected.sort_values(columns).reset_index(drop=True), check_dtype=False,
    )


def test_all_retained_groups_and_non_joint_units_match_independent_reference(reference_run):
    _assert_scientific_rows(reference_run.processed, _read_csv("expected_retained_rows.csv"))
    _assert_native_units(reference_run.units, _read_csv("expected_native_units.csv"))
    assert len(reference_run.processed) == len(reference_run.units) == 1135
    assert _outcome_counts(reference_run.units) == {"target_only": 1069, "joint": 45, "reference_only": 21}
    only_target = reference_run.units[reference_run.units.outcome.eq("target_only")]
    only_reference = reference_run.units[reference_run.units.outcome.eq("reference_only")]
    assert only_target.target_snr_db.notna().all() and only_target.reference_snr_db.isna().all()
    assert only_reference.reference_snr_db.notna().all() and only_reference.target_snr_db.isna().all()
    assert pd.concat([only_target, only_reference]).metric.isna().all()


def test_every_source_report_is_accounted_for_with_a_selection_reason(reference_run):
    ledger = _read_csv("expected_source_ledger.csv").sort_values("id").reset_index(drop=True)
    source = reference_run.source_rows.sort_values("id").reset_index(drop=True)
    assert len(ledger) == ledger.id.nunique() == len(source) == 1992
    for column in source.columns:
        if column == "time":
            np.testing.assert_array_equal(_utc_nanoseconds(ledger[column]), _utc_nanoseconds(source[column]))
        else:
            np.testing.assert_array_equal(ledger[column], source[column])
    np.testing.assert_array_equal(ledger.normalized_snr_db, source.snr - source.power + 30)
    np.testing.assert_array_equal(ledger.time_slot, _utc_nanoseconds(source.time) // 120_000_000_000)
    np.testing.assert_array_equal(ledger.peer_sign, source.rx_sign)
    np.testing.assert_array_equal(ledger.peer_grid, source.rx_loc)
    assert ledger.selection_reason.value_counts().to_dict() == {
        "retained": 1180, "excluded_target_inactive": 786, "excluded_distance": 26,
    }
    classified = _read_csv("expected_classified_groups.csv").sort_values(KEY_COLUMNS).reset_index(drop=True)
    actual = reference_run.sql_rows.sort_values(KEY_COLUMNS).reset_index(drop=True)
    active_cycles = set(actual.loc[actual.has_u.gt(0), "time_slot"])
    retained_keys = set(reference_run.processed[KEY_COLUMNS].itertuples(index=False, name=None))
    actual_keys = list(actual[KEY_COLUMNS].itertuples(index=False, name=None))
    reasons = [
        "excluded_target_inactive" if key[0] not in active_cycles else (
            "retained" if key in retained_keys else "excluded_distance"
        ) for key in actual_keys
    ]
    np.testing.assert_array_equal(reasons, classified.selection_reason)
    np.testing.assert_array_equal(actual[KEY_COLUMNS], classified[KEY_COLUMNS])
    np.testing.assert_array_equal(actual.time_slot.isin(active_cycles), classified.is_target_active)
    # Every raw report maps to its exact receiver/cycle group, including all
    # excluded and one-sided evidence; a count-only checksum cannot prove this.
    classified_index = classified.set_index(KEY_COLUMNS)
    for identity, reports in ledger.groupby(KEY_COLUMNS, sort=False):
        expected_group = classified_index.loc[identity]
        assert reports.selection_reason.eq(expected_group.selection_reason).all()
        assert reports.outcome.eq(expected_group.outcome).all()
        for endpoint, count_column, ids_column in (
            ("KP4MD", "has_u", "target_report_ids"),
            ("WB6RQN", "has_r", "reference_report_ids"),
        ):
            endpoint_reports = reports[reports.tx_sign.eq(endpoint)]
            assert len(endpoint_reports) == expected_group[count_column]
            expected_ids = set() if pd.isna(expected_group[ids_column]) else {
                int(float(value)) for value in str(expected_group[ids_column]).split(";")
            }
            assert set(endpoint_reports.id) == expected_ids


def test_each_global_activity_cycle_has_independently_recorded_target_witnesses(reference_run):
    expected = _read_csv("expected_active_cycles.csv")
    source = reference_run.source_rows
    targets = source[source.tx_sign.eq("KP4MD")].copy()
    targets["time_slot"] = _utc_nanoseconds(targets.time) // 120_000_000_000
    assert len(expected) == 179
    np.testing.assert_array_equal(expected.time_slot, sorted(targets.time_slot.unique()))
    for row in expected.itertuples():
        witnesses = targets[targets.time_slot.eq(row.time_slot)]
        assert len(witnesses) == row.target_witness_report_count
        assert set(witnesses.id) == {int(value) for value in row.target_witness_report_ids.split(";")}


def test_station_aggregation_keeps_non_joint_only_identities(reference_run):
    expected = _read_csv("expected_station_rows.csv").sort_values(["peer_sign", "peer_grid"]).reset_index(drop=True)
    actual = reference_run.stations.sort_values(["peer_sign", "peer_grid"]).reset_index(drop=True)
    assert len(actual) == len(expected) == 80
    np.testing.assert_array_equal(actual[["peer_sign", "peer_grid"]], expected[["peer_sign", "peer_grid"]])
    for actual_column, expected_column in (
        ("spot_count", "joint"), ("count_only_u", "target_only"),
        ("count_only_r", "reference_only"), ("stat_val", "median_delta_snr_db"),
    ):
        np.testing.assert_allclose(actual[actual_column], expected[expected_column], rtol=0, atol=1e-12, equal_nan=True)
    assert actual.spot_count.eq(0).sum() == 50


def test_power_normalization_and_the_single_ve6pdq_pair_are_hand_checkable(reference_run):
    points = reference_run.points
    selected = points[points.station.eq("VE6PDQ") & points.grid.eq("DO34ir")]
    assert len(selected) == 1
    assert selected.iloc[0].plot_time == pd.Timestamp("2010-12-20T00:22:00Z")
    assert selected.iloc[0].metric == (-13 - 37 + 30) - (-15 - 33 + 30) == -2
    raw = reference_run.source_rows.set_index("id")
    assert tuple(raw.loc[44698904, ["tx_sign", "snr", "power"]]) == ("KP4MD", -13, 37)
    assert tuple(raw.loc[44698905, ["tx_sign", "snr", "power"]]) == ("WB6RQN", -15, 33)
    units = reference_run.units[reference_run.units.peer_sign.eq("VE6PDQ") & reference_run.units.peer_grid.eq("DO34ir")]
    assert _outcome_counts(units) == {"target_only": 62, "joint": 1}
    assert len(points) == 45 and points.plot_time.nunique() == 9
    assert points.metric.median() == -4
    _assert_native_units(reference_run.units[reference_run.units.outcome.eq("joint")], _read_csv("expected_paired_rows.csv"))


def test_global_target_activity_preserves_reference_only_at_another_receiver(reference_run):
    witness_time = pd.Timestamp("2010-12-20T01:06:00Z")
    cycle = int(witness_time.timestamp()) // 120
    rows = reference_run.processed[reference_run.processed.time_slot.eq(cycle)]
    receiver = rows[rows.peer_sign.eq("W6II") & rows.peer_grid.eq("CN85nm")].iloc[0]
    assert receiver.has_u == 0 and receiver.has_r == 1
    target_witness = rows[rows.peer_sign.eq("K6HVI") & rows.peer_grid.eq("CN87vp")]
    assert len(target_witness) == 1 and target_witness.has_u.eq(1).all()
    assert receiver.snr_r_norm == -26 - 33 + 30 == -29
    # Remove all observed Target reports from this real cycle: no retained
    # Reference-only row may now imply an opportunity in that unknown cycle.
    changed = reference_run.sql_rows.copy()
    changed.loc[changed.time_slot.eq(cycle), "has_u"] = 0
    changed.loc[changed.time_slot.eq(cycle), "snr_u_norm"] = 0
    filtered, warning = apply_post_fetch_filters(
        changed, reference_run.analysis, reference_run.context,
        reference_run.latitude, reference_run.longitude, T["en"],
    )
    assert warning is None and not filtered.time_slot.eq(cycle).any()


def test_unobserved_target_cycles_are_excluded_not_counted_as_target_losses(reference_run):
    cycle = int(pd.Timestamp("2010-12-19T07:44:00Z").timestamp()) // 120
    rows = reference_run.sql_rows[reference_run.sql_rows.time_slot.eq(cycle)]
    assert not rows.empty and rows.has_u.eq(0).all()
    assert not reference_run.processed.time_slot.eq(cycle).any()
    ve6pdq = reference_run.source_rows[reference_run.source_rows.rx_sign.eq("VE6PDQ")]
    assert ve6pdq.tx_sign.value_counts().to_dict() == {"KP4MD": 63, "WB6RQN": 26}
    active = set(reference_run.sql_rows.loc[reference_run.sql_rows.has_u.gt(0), "time_slot"])
    excluded = ve6pdq[ve6pdq.tx_sign.eq("WB6RQN") & ~pd.Series(_utc_nanoseconds(ve6pdq.time) // 120_000_000_000, index=ve6pdq.index).isin(active)]
    assert len(excluded) == 25 and len(active) == 179


def test_five_thousand_km_scope_is_distinct_from_unrestricted_prose_counts(reference_run):
    unrestricted = _calculate_run(reference_run.source_rows, max_distance_km=22000)
    assert _outcome_counts(unrestricted.units) == {"target_only": 1093, "joint": 46, "reference_only": 21}
    assert len(unrestricted.units) - len(reference_run.units) == 25
    assert unrestricted.points.metric.median() == reference_run.points.metric.median() == -4


def test_publication_audit_accounts_for_all_ve6pdq_reports_before_and_after_gating(reference_run):
    # This checks completeness and linkage, not agreement with published SNRs.
    audited = _read_csv("publication_archive_reports.csv")
    source = reference_run.source_rows[reference_run.source_rows.rx_sign.eq("VE6PDQ")]
    assert len(audited) == audited.report_id.nunique() == len(source) == 89
    assert set(audited.report_id) == set(source.id)
    units = _canonical_units(reference_run.units).set_index(KEY_COLUMNS)
    for row in audited.itertuples():
        identity = (row.time_slot, row.rx_sign, row.rx_loc)
        if row.retained_outcome == "excluded_target_inactive":
            assert identity not in units.index
        else:
            assert units.loc[identity, "outcome"] == row.retained_outcome
    assert audited.retained_outcome.value_counts().to_dict() == {
        "target_only": 62, "joint": 2, "excluded_target_inactive": 25,
    }


def test_publication_time_candidates_include_every_non_joint_report_in_tolerance(reference_run):
    # Recompute every candidate set at the source-only digitization tolerance;
    # do not select the nearest report or fit an offset to force agreement.
    features = _read_json("publication_features.json")
    markers = _read_csv("publication_markers.csv")
    candidates = _read_csv("publication_mapping_candidates.csv")
    source = reference_run.source_rows[reference_run.source_rows.rx_sign.eq("VE6PDQ")]
    timestamps = pd.to_datetime(source.time, utc=True)
    tolerance = pd.Timedelta(minutes=features["readout_tolerances"]["minutes"])
    expected_keys = set()
    for marker in markers.itertuples():
        marker_id = f"{marker.series}_{marker.visible_marker_number:02d}"
        close = source[
            source.tx_sign.eq(marker.series)
            & timestamps.sub(pd.Timestamp(marker.utc_readout_approx)).abs().le(tolerance)
        ]
        expected_keys.update((marker_id, int(report_id)) for report_id in close.id)
    actual_keys = set(candidates[["marker_id", "report_id"]].itertuples(index=False, name=None))
    assert actual_keys == expected_keys
    assert len(candidates) == len(actual_keys) == 18
    assert candidates.mapping_status.eq("time_candidate_only_not_confirmed_match").all()
    assert candidates.retained_outcome.value_counts().to_dict() == {
        "target_only": 16, "excluded_target_inactive": 2,
    }


@pytest.mark.parametrize("show_non_joint", [True, False])
def test_drilldown_preserves_every_requested_native_row(reference_run, tmp_path, show_non_joint):
    parquet_path = tmp_path / "milazzo_processed.parquet"
    reference_run.processed.to_parquet(parquet_path, index=False)
    inspector = reference_run.inspector
    table, warning = _build_drilldown_table(
        str(parquet_path), inspector.station_table,
        inspector.station_column, inspector.locator_column,
        inspector.distance_column, inspector.azimuth_column,
        reference_run.analysis.id, False, show_non_joint, False,
        inspector.target_name, inspector.reference_header, T["en"],
    )
    assert warning is None
    actual = pd.DataFrame({
        "time_slot": _utc_nanoseconds(pd.to_datetime(table["Date/Time (UTC)"], format="%d-%b-%Y %H:%M:%S", utc=True)) // 120_000_000_000,
        "peer_sign": table["RX Station"], "peer_grid": table[inspector.locator_column],
        "target_snr_db": pd.to_numeric(table[f"{inspector.target_name} SNR (dB)"], errors="coerce"),
        "reference_snr_db": pd.to_numeric(table[f"{inspector.reference_header} SNR (dB)"], errors="coerce"),
        "delta_snr_db": pd.to_numeric(table[T["en"]["tbl_col_delta_snr"]], errors="coerce"),
    })
    expected = _read_csv("expected_native_units.csv" if show_non_joint else "expected_paired_rows.csv")
    _assert_scientific_rows(actual, expected[list(actual.columns)])
    assert len(table) == (1135 if show_non_joint else 45)


@pytest.mark.parametrize("scope", ["all", "VE6PDQ"])
def test_three_hour_coverage_preserves_non_joint_counts_and_weighting(reference_run, scope):
    units = reference_run.units
    if scope == "VE6PDQ":
        units = units[units.peer_sign.eq("VE6PDQ") & units.peer_grid.eq("DO34ir")]
    work, start, end = _prepare_compare_coverage_units(
        units, analysis_start_t=reference_run.configuration["start_utc"],
        analysis_end_t=reference_run.configuration["end_utc"],
    )
    actual = _aggregate_compare_chronological_coverage(work, start, end, "3h")
    expected = _read_csv("expected_coverage_3h.csv")
    expected = expected[expected.scope.eq(scope)].reset_index(drop=True)
    assert len(expected) == 24
    for actual_column, expected_column in (
        ("unit_target_counts", "target_only"), ("unit_joint_counts", "joint"),
        ("unit_reference_counts", "reference_only"), ("station_counts", "station_count"),
        ("outcome_joint_share_pct", "pooled_joint_share_pct"),
        ("station_joint_share_pct", "station_balanced_joint_share_pct"),
    ):
        np.testing.assert_allclose(actual[actual_column], expected[expected_column], rtol=0, atol=1e-12, equal_nan=True)
    np.testing.assert_array_equal(actual["time_edge_ns"][:-1], _utc_nanoseconds(expected.bin_start_utc))
    np.testing.assert_array_equal(actual["time_edge_ns"][1:], _utc_nanoseconds(expected.bin_end_utc))
    assert expected.native_units.sum() == len(units)
    assert np.sum(actual["unit_target_counts"]) == (1069 if scope == "all" else 62)


@pytest.fixture(scope="module")
def human_benchmark_run(verified_reference_files):
    """Replay the approved 32-hour setup without reading observed outputs."""
    from milazzo_human_reference import verify_human_reference_files

    verify_human_reference_files(HUMAN_REFERENCE_DIRECTORY)
    configuration = json.loads(
        (HUMAN_REFERENCE_DIRECTORY / "benchmark.config").read_text(encoding="utf-8")
    )
    source_rows = pd.read_csv(
        HUMAN_REFERENCE_DIRECTORY / "benchmark_source.csv", float_precision="round_trip",
    )
    return _calculate_run(source_rows, configuration_document=configuration)


@pytest.fixture(scope="module")
def human_benchmark_expected(human_benchmark_run):
    """Load reviewed anchors after their complete fixture integrity check."""
    return json.loads(
        (HUMAN_REFERENCE_DIRECTORY / "benchmark_expected.json").read_text(encoding="utf-8")
    )


@pytest.fixture(scope="module")
def human_benchmark_figure(human_benchmark_run):
    """Feed actual station, observation and footer outputs to the native figure."""
    run = human_benchmark_run
    labels = T["en"]
    footer = compare_footer_counts(run.stations, max_dist_km=run.context.max_peer_distance_km)
    recipe = _segment_figure_export_recipe(
        title="TX Benchmark: KP4MD vs. WB6RQN",
        selected_segment="Full Range | All Directions",
        is_sequential=run.analysis.is_sequential,
        station_values=run.stations.stat_val.dropna(),
        spot_values=run.points.metric,
        panel_labels=[
            run.inspector.target_only_label, labels["txt_joint"],
            labels["leg_both_async"], run.inspector.reference_only_label,
        ],
        panel_y_label=labels["fig_share_percent_axis"],
        decode_outcomes_title=labels["fig_decode_outcomes"],
        station_medians_title=labels["fig_station_medians_delta"],
        paired_evidence_title=labels["fig_joint_spot_delta"],
        metric_axis_label=labels["tbl_col_delta_snr"],
        median_label=labels["fig_median_label"],
        mean_label=labels["fig_mean_label"],
        no_data_label=labels["fig_no_data"],
        panel_station_counts=[
            footer[key] for key in ("stat_only_u", "stat_joint", "stat_both_async", "stat_only_r")
        ],
        panel_spot_counts=[
            footer[key] for key in ("spot_only_u", "spot_joint", "spot_both_async", "spot_only_r")
        ],
        panel_series_labels=[labels["lbl_results_stations"], labels["lbl_results_spots"]],
    )
    figure = render_segment_insight_export_figure(recipe)
    assert figure is not None
    try:
        yield SimpleNamespace(figure=figure, recipe=recipe, footer=footer)
    finally:
        dispose_agg_figure(figure)


def _assert_human_benchmark_pair(run, expected_pair):
    """Match B01's exact peer, locator and cycle before checking normalized SNR."""
    selected = run.units[
        run.units.peer_sign.eq(expected_pair["peer_sign"])
        & run.units.peer_grid.eq(expected_pair["peer_grid"])
        & run.units.evidence_utc.eq(pd.Timestamp(expected_pair["utc"]))
    ]
    assert len(selected) == 1
    pair = selected.iloc[0]
    assert pair.outcome == "joint"
    assert pair.target_snr_db == expected_pair["target_snr_db"]
    assert pair.reference_snr_db == expected_pair["reference_snr_db"]
    assert pair.metric == expected_pair["delta_snr_db"]


def test_human_benchmark_complete_native_population_matches_independent_support(human_benchmark_run):
    """Full independently computed support is broader than sampled human checks."""
    expected = pd.read_csv(
        HUMAN_REFERENCE_DIRECTORY / "benchmark_expected_native_units.csv",
        float_precision="round_trip",
    )
    _assert_native_units(human_benchmark_run.units, expected)
    assert len(expected) == 1054
    assert pd.Timestamp(human_benchmark_run.configuration["start_utc"]) == PAPER_START_UTC
    assert pd.Timestamp(human_benchmark_run.configuration["end_utc"]) == PAPER_END_UTC


def test_human_b01_normalized_pair_preserves_raw_provenance_and_direction(
    human_benchmark_run, human_benchmark_expected,
):
    """Protect the reviewed pair's power correction, source IDs and sign."""
    expected = human_benchmark_expected["B01"]
    _assert_human_benchmark_pair(human_benchmark_run, expected)
    reports = human_benchmark_run.source_rows.set_index("id")
    for role, callsign in (("target", "KP4MD"), ("reference", "WB6RQN")):
        report = reports.loc[expected[f"{role}_report_id"]]
        assert report.tx_sign == callsign
        assert report.rx_sign == expected["peer_sign"]
        assert report.rx_loc.upper() == expected["peer_grid"].upper()
        assert pd.Timestamp(report.time) == pd.Timestamp(expected["utc"])
        assert report.snr - report.power + 30 == expected[f"{role}_snr_db"]
    assert expected["delta_snr_db"] == expected["target_snr_db"] - expected["reference_snr_db"]


def test_human_b02_histogram_weighting_and_reviewed_positive_extreme(
    human_benchmark_figure, human_benchmark_expected,
):
    """Check station and Joint statistics through native bars and median lines."""
    for distribution, recipe_key, artist_gid in (
        ("station", "station_histogram", "station-median-histogram"),
        ("joint", "spot_histogram", "spot-metric-histogram"),
    ):
        expected = human_benchmark_expected["B02"][distribution]
        histogram = human_benchmark_figure.recipe[recipe_key]
        assert histogram["value_count"] == expected["count"]
        assert sum(histogram["counts"]) == expected["count"]
        assert histogram["mean"] == pytest.approx(expected["mean"], rel=0, abs=1e-12)
        assert histogram["median"] == expected["median"]
        selected_bin = np.isclose(histogram["centers"], expected["positive_extreme_db"])
        assert selected_bin.sum() == 1
        assert histogram["counts"][selected_bin].item() == expected["positive_extreme_count"]

        histogram_axes = [
            axis for axis in human_benchmark_figure.figure.axes
            if any(patch.get_gid() == artist_gid for patch in axis.patches)
        ]
        assert len(histogram_axes) == 1
        histogram_axis = histogram_axes[0]
        bars = [patch for patch in histogram_axis.patches if patch.get_gid() == artist_gid]
        positive_bars = [
            bar for bar in bars
            if np.isclose(bar.get_x() + bar.get_width() / 2, expected["positive_extreme_db"])
        ]
        assert len(positive_bars) == 1
        assert positive_bars[0].get_height() == pytest.approx(
            100 * expected["positive_extreme_count"] / expected["count"], rel=0, abs=1e-12,
        )
        assert sum(bar.get_height() for bar in bars) == pytest.approx(100)
        median_lines = [
            line for line in histogram_axis.lines
            if line.get_label().startswith(T["en"]["fig_median_label"] + " ")
        ]
        assert len(median_lines) == 1
        np.testing.assert_array_equal(median_lines[0].get_xdata(), [expected["median"]] * 2)


def test_human_b03_decode_outcomes_follow_station_history_and_separate_denominators(
    human_benchmark_run, human_benchmark_figure, human_benchmark_expected,
):
    """Preserve reviewed station-history categories and both plotted denominators."""
    expected = human_benchmark_expected["B03"]
    for expected_key, recipe_key, artist_gid, footer_key in (
        ("station_counts", "panel_station_counts", "decode-outcome-stations", "tot_stats"),
        ("observation_counts", "panel_spot_counts", "decode-outcome-spots", "tot_spots"),
    ):
        counts = expected[expected_key]
        assert human_benchmark_figure.recipe[recipe_key] == counts
        assert human_benchmark_figure.footer[footer_key] == sum(counts)
        bars = [
            patch for axis in human_benchmark_figure.figure.axes for patch in axis.patches
            if patch.get_gid() == artist_gid
        ]
        np.testing.assert_allclose(
            [bar.get_height() for bar in bars], np.asarray(counts) * 100 / sum(counts),
            rtol=0, atol=1e-12,
        )
    # A station with one Joint and 56 nonjoint observations contributes to the
    # Joint station category; its nonjoint observations contribute to Async.
    station = human_benchmark_run.stations[
        human_benchmark_run.stations.peer_sign.eq("VE6PDQ")
        & human_benchmark_run.stations.peer_grid.eq("DO34ir")
    ]
    assert len(station) == 1
    assert tuple(station.iloc[0][["spot_count", "count_only_u", "count_only_r"]]) == (1, 56, 0)
    outcome_axes = [
        axis for axis in human_benchmark_figure.figure.axes
        if any(patch.get_gid() == "decode-outcome-stations" for patch in axis.patches)
    ]
    assert len(outcome_axes) == 1
    assert [tick.get_text() for tick in outcome_axes[0].get_xticklabels()] == human_benchmark_figure.recipe["panel_labels"]
    annotations = [
        label.get_text() for label in outcome_axes[0].texts
        if label.get_gid() == "decode-outcome-percentage"
    ]
    assert annotations[1] == "39%" and annotations[5] == "4%" and annotations[6] == "73%"


def test_human_b04_map_segment_weights_station_medians_before_rounding(
    human_benchmark_run, human_benchmark_expected,
):
    """Distinguish the reviewed equal-station map statistic from pooled evidence."""
    expected = human_benchmark_expected["B04"]
    selected_segments = human_benchmark_run.segment_rows[
        human_benchmark_run.segment_rows.SegmentID.eq(expected["segment_id"])
    ]
    assert len(selected_segments) == 1
    segment = selected_segments.iloc[0]
    assert segment.val == expected["segment_value_db"]
    assert segment.cnt == expected["station_count"]
    assert segment.total_spots == expected["joint_count"]
    stations = human_benchmark_run.stations[
        human_benchmark_run.stations.SegmentID.eq(expected["segment_id"])
        & human_benchmark_run.stations.spot_count.gt(0)
    ]
    assert stations.set_index("peer_sign").stat_val.to_dict() == expected["station_medians_db"]
    assert stations.stat_val.median() == expected["unrounded_segment_median_db"]
    paired_identities = set(stations[["peer_sign", "peer_grid"]].itertuples(index=False, name=None))
    points = human_benchmark_run.points[
        [(station, grid) in paired_identities for station, grid in zip(
            human_benchmark_run.points.station, human_benchmark_run.points.grid,
        )]
    ]
    assert len(points) == expected["joint_count"]
    assert points.metric.median() == expected["pooled_median_db"]
    assert segment.val != points.metric.median()


def test_human_b01_rejects_changed_raw_power_after_complete_production_replay(
    human_benchmark_run, human_benchmark_expected,
):
    """Show the approved anchor detects a raw-power error propagated through SQL."""
    expected = human_benchmark_expected["B01"]
    changed_source = human_benchmark_run.source_rows.copy()
    changed_source.loc[changed_source.id.eq(expected["target_report_id"]), "power"] += 1
    configuration = json.loads(
        (HUMAN_REFERENCE_DIRECTORY / "benchmark.config").read_text(encoding="utf-8")
    )
    changed_run = _calculate_run(changed_source, configuration_document=configuration)
    with pytest.raises(AssertionError):
        _assert_human_benchmark_pair(changed_run, expected)
    changed_pair = changed_run.units[
        changed_run.units.peer_sign.eq(expected["peer_sign"])
        & changed_run.units.peer_grid.eq(expected["peer_grid"])
        & changed_run.units.evidence_utc.eq(pd.Timestamp(expected["utc"]))
    ].iloc[0]
    assert changed_pair.metric == expected["delta_snr_db"] - 1


def _read_rx_csv(filename):
    return pd.read_csv(RX_REFERENCE_DIRECTORY / filename, float_precision="round_trip")


@pytest.fixture(scope="module")
def rx_reference_run(verified_reference_files):
    manifest = json.loads((RX_REFERENCE_DIRECTORY / "manifest.json").read_text(encoding="utf-8"))
    required = {
        "README.md", "rx_reference.config", "source_rows.csv", "paper_markers.csv",
        "paper_features_original.json", "reconciliation.json", "user_kp4md_40m_rows.csv",
        "user_wb6rqn_reports.tsv", "expected_paper_matches.csv", "expected_sql_rows.csv",
        "expected_native_units.csv", "expected_paired_rows.csv", "expected_summary.json",
    }
    assert manifest["schema_version"] == 1
    paths = [record["path"] for record in manifest["files"]]
    assert len(paths) == len(set(paths)) and required.issubset(paths)
    for record in manifest["files"]:
        path = (RX_REFERENCE_DIRECTORY / record["path"]).resolve()
        assert path.is_relative_to(RX_REFERENCE_DIRECTORY.resolve())
        contents = path.read_bytes()
        assert len(contents) == record["bytes"]
        assert hashlib.sha256(contents).hexdigest() == record["sha256"], record["path"]
    configuration = json.loads((RX_REFERENCE_DIRECTORY / "rx_reference.config").read_text(encoding="utf-8"))
    return _calculate_run(_read_rx_csv("source_rows.csv"), configuration_document=configuration)


@pytest.fixture(scope="module")
def installed_rx_demo_run(rx_reference_run):
    configuration = json.loads(
        (REPOSITORY_DIRECTORY / "config/demos/05_milazzo_tx_buddy.config").read_text(encoding="utf-8")
    )
    return _calculate_run(rx_reference_run.source_rows, configuration_document=configuration)


def test_installed_rx_demo_replays_the_independent_figure6_path_evidence(installed_rx_demo_run):
    # This supplied VE6PDQ path proves exact pairing, not archive-wide RX counts
    # or the absence of Target activity on other transmitting paths.
    _assert_scientific_rows(installed_rx_demo_run.sql_rows, _read_rx_csv("expected_sql_rows.csv"))
    _assert_native_units(installed_rx_demo_run.units, _read_rx_csv("expected_native_units.csv"))
    assert _outcome_counts(installed_rx_demo_run.units) == {
        "target_only": 26, "joint": 5, "reference_only": 3,
    }
    assert installed_rx_demo_run.source_rows.tx_sign.eq("VE6PDQ").all()
    assert set(installed_rx_demo_run.source_rows.rx_sign) == {"KP4MD", "WB6RQN"}
    assert sorted(installed_rx_demo_run.points.metric) == [7, 7, 8, 17, 22]
    assert installed_rx_demo_run.points.metric.median() == 8
    assert installed_rx_demo_run.points.plot_time.nunique() == 5


def test_installed_rx_demo_preselection_preserves_full_locator_pair_populations(installed_rx_demo_run):
    from ui.inspector.selection_state import station_selection_default_rows

    configured_identities = installed_rx_demo_run.configuration["selected_stations_compare"]
    assert configured_identities == [{"callsign": "VE6PDQ", "locator": "DO34IR"}]
    selected_rows, missing_identities = station_selection_default_rows(
        installed_rx_demo_run.stations, "peer_sign", "peer_grid", configured_identities,
    )
    assert not missing_identities and len(selected_rows) == 1
    selected_station = installed_rx_demo_run.stations.iloc[selected_rows[0]]
    assert (selected_station.peer_sign, selected_station.peer_grid) == ("VE6PDQ", "DO34ir")
    pairs = _canonical_units(installed_rx_demo_run.units)
    pairs = pairs[pairs.outcome.eq("joint")]
    selected_pairs = pairs[
        pairs.peer_sign.eq(selected_station.peer_sign) & pairs.peer_grid.eq(selected_station.peer_grid)
    ]
    _assert_native_units(selected_pairs, _read_rx_csv("expected_paired_rows.csv").query("peer_grid == 'DO34ir'"))
    assert selected_pairs.delta_snr_db.tolist() == [8, 22, 7]
    assert selected_pairs.delta_snr_db.median() == 8
    other_locator_pairs = pairs[pairs.peer_sign.eq("VE6PDQ") & pairs.peer_grid.eq("DO34")]
    assert other_locator_pairs.delta_snr_db.tolist() == [17, 7]
    assert other_locator_pairs.delta_snr_db.median() == 12
    assert set(selected_pairs.time_slot).isdisjoint(other_locator_pairs.time_slot)


def _paper_matches_from_sql(sql_rows):
    """Recover report-scale SNR from each present endpoint at reported 5 W."""
    matches = []
    for marker in _read_rx_csv("paper_markers.csv").itertuples():
        timestamp = pd.Timestamp(marker.utc_readout_approx)
        has_column, snr_column = (
            ("has_u", "snr_u_norm") if marker.series == "KP4MD" else ("has_r", "snr_r_norm")
        )
        times = pd.to_datetime(sql_rows.time_slot * 120, unit="s", utc=True)
        candidates = sql_rows[
            sql_rows[has_column].gt(0) & times.sub(timestamp).abs().le(pd.Timedelta(minutes=4))
        ]
        assert len(candidates) == 1, (marker.series, marker.visible_marker_number)
        candidate = candidates.iloc[0]
        # SQL normalizes nominal 5 W / 37 dBm reports to 30 dBm. The paper
        # annotations are raw SNR; restore precisely 7 dB, not a fitted offset.
        assert candidate[snr_column] + 7 == marker.snr_db_approx
        matches.append((marker.series, candidate.time_slot, candidate.peer_grid))
    assert len(matches) == len(set(matches)) == 44
    return matches


def test_figure6_all_44_markers_reconcile_with_actual_rx_sql_components(rx_reference_run):
    _assert_scientific_rows(rx_reference_run.sql_rows, _read_rx_csv("expected_sql_rows.csv"))
    matches = _paper_matches_from_sql(rx_reference_run.sql_rows)
    assert sum(series == "KP4MD" for series, _, _ in matches) == 31
    assert sum(series == "WB6RQN" for series, _, _ in matches) == 13
    assert rx_reference_run.sql_rows[["has_u", "has_r"]].sum().sum() == 44
    assert len(rx_reference_run.sql_rows) == 39
    assert rx_reference_run.source_rows.tx_sign.eq("VE6PDQ").all()
    assert set(rx_reference_run.source_rows.rx_sign) == {"KP4MD", "WB6RQN"}


def test_rx_paper_match_ledger_preserves_exact_dates_values_and_report_provenance(rx_reference_run):
    expected = _read_rx_csv("expected_paper_matches.csv")
    source = rx_reference_run.source_rows.set_index("source_row_key")
    markers = _read_rx_csv("paper_markers.csv")
    assert len(expected) == expected.source_row_key.nunique() == 44
    assert expected.time_error_seconds.abs().max() == 120
    for match in expected.itertuples():
        report = source.loc[match.source_row_key]
        assert report.tx_sign == match.transmitter == "VE6PDQ"
        assert report.rx_sign == match.receiver
        assert report.tx_loc == match.transmitter_locator
        assert report.snr == match.report_snr_db == match.paper_snr_db
        assert pd.Timestamp(report.time) == pd.Timestamp(match.report_utc)
        marker_number = int(match.marker_id.rsplit("_", 1)[1])
        marker = markers[markers.series.eq(match.receiver) & markers.visible_marker_number.eq(marker_number)].iloc[0]
        assert marker.snr_db_approx == match.paper_snr_db
        assert pd.Timestamp(marker.utc_readout_approx) == pd.Timestamp(match.paper_utc)
        assert (pd.Timestamp(match.report_utc) - pd.Timestamp(match.paper_utc)).total_seconds() == match.time_error_seconds
    assert rx_reference_run.source_rows.code.isna().all()
    assert rx_reference_run.source_rows.power.eq(37).all()
    assert len(rx_reference_run.source_rows) == 86
    assert set(rx_reference_run.source_rows.band) == {3, 7, 10, 14}


def test_rx_path_subset_preserves_gate_nulls_and_five_hand_checked_pairs(rx_reference_run):
    _assert_native_units(rx_reference_run.units, _read_rx_csv("expected_native_units.csv"))
    assert _outcome_counts(rx_reference_run.units) == {"target_only": 26, "joint": 5, "reference_only": 3}
    pairs = rx_reference_run.units[rx_reference_run.units.outcome.eq("joint")]
    _assert_native_units(pairs, _read_rx_csv("expected_paired_rows.csv"))
    assert sorted(rx_reference_run.points.metric) == [7, 7, 8, 17, 22]
    assert rx_reference_run.points.metric.median() == 8
    assert rx_reference_run.units.loc[~rx_reference_run.units.outcome.eq("joint"), "metric"].isna().all()
    # These five discarded Reference reports are inactive only in this bounded
    # path subset. Other transmitters are absent from the supplied input.
    assert rx_reference_run.sql_rows.has_r.sum() - rx_reference_run.processed.has_r.sum() == 5


def test_rx_full_locator_identity_prevents_three_false_same_cycle_pairs(rx_reference_run):
    units = _canonical_units(rx_reference_run.units)
    overlay_reports = pd.read_csv(PUBLICATION_DIRECTORY / "figure6_sql_endpoint_reports.csv")
    for time in ("2010-12-19T23:24Z", "2010-12-19T23:46Z", "2010-12-20T10:46Z"):
        slot = int(pd.Timestamp(time).timestamp()) // 120
        cycle = units[units.time_slot.eq(slot)]
        assert set(cycle.peer_grid) == {"DO34", "DO34ir"}
        assert _outcome_counts(cycle) == {"target_only": 1, "reference_only": 1}
        assert cycle.delta_snr_db.isna().all()
        ringed_reports = overlay_reports[overlay_reports.time_slot.eq(slot)]
        assert len(ringed_reports) == 2 and ringed_reports.passes_target_active_gate.all()
    # A callsign-only merge would create eight pairs. It is not the full-locator
    # pairing contract, even when the coarse cell contains the finer locator.
    counts_by_cycle = rx_reference_run.sql_rows.groupby("time_slot")[["has_u", "has_r"]].sum()
    assert (counts_by_cycle.has_u.gt(0) & counts_by_cycle.has_r.gt(0)).sum() == 8


def test_figure6_rx_oracle_rejects_receiver_exchange_and_snr_offset(rx_reference_run):
    exchanged = rx_reference_run.sql_rows.copy()
    exchanged[["has_u", "has_r"]] = exchanged[["has_r", "has_u"]].to_numpy()
    exchanged[["snr_u_norm", "snr_r_norm"]] = exchanged[["snr_r_norm", "snr_u_norm"]].to_numpy()
    with pytest.raises(AssertionError):
        _paper_matches_from_sql(exchanged)
    shifted = rx_reference_run.sql_rows.copy()
    shifted.loc[shifted.has_u.gt(0), "snr_u_norm"] += 1
    with pytest.raises(AssertionError):
        _paper_matches_from_sql(shifted)


def test_published_direction_is_distinct_from_observed_rx_direction(rx_reference_run):
    facts = json.loads((RX_REFERENCE_DIRECTORY / "reconciliation.json").read_text(encoding="utf-8"))
    printed = json.loads((RX_REFERENCE_DIRECTORY / "paper_features_original.json").read_text(encoding="utf-8"))
    assert printed["receiver"] == facts["caption_claimed_receiver"] == "VE6PDQ"
    assert facts["matched_transmitter"] == "VE6PDQ"
    assert set(facts["matched_receivers"]) == {"KP4MD", "WB6RQN"}
    # Applying the caption's TX direction to these actual reciprocal reports
    # must find no eligible source observations, rather than fabricate a match.
    tx_query = _calculate_tx_query_for_supplied_rx_reports()
    assert execute_generated_sql(tx_query, rx_reference_run.source_rows).empty


def _calculate_tx_query_for_supplied_rx_reports():
    configuration = validate_config_document(_read_json("demo.config"))
    session_values = {"lang": "en"}
    apply_config_state_values(configuration, session_values)
    session_values["run_mode"] = "TX"
    context = build_analysis_context_from_session_state(session_values)
    latitude, longitude = locator_to_latlon(context.qth)
    analyses = build_analysis_batches(
        context, configuration["start_utc"], configuration["end_utc"], latitude, longitude,
        "AND band = '7'", presentation_context=PresentationContext(solar_label="All", labels=T["en"]),
    )
    return analyses[0].get("legacy_query")


@pytest.fixture(scope="module", autouse=True)
def verified_publication_files(verified_reference_files):
    manifest = json.loads((PUBLICATION_DIRECTORY / "manifest.json").read_text(encoding="utf-8"))
    paths = [record["path"] for record in manifest["files"]]
    assert manifest["schema_version"] == 1
    assert len(paths) == len(set(paths))
    assert {
        "paper_figure6.jpg", "paper_figure7.jpg", "figure6_rx_overlay.png", "figure7_tx_overlay.png",
        "figure7_paper_anchors.csv", "figure7_paper_features.json", "figure7_anchor_matches.csv",
        "figure6_anchor_matches.csv", "figure6_sql_endpoint_reports.csv", "figure7_sql_endpoint_reports.csv",
        "overlay_summary.json", "README.md",
    }.issubset(paths)
    for record in manifest["files"]:
        path = (PUBLICATION_DIRECTORY / record["path"]).resolve()
        assert path.is_relative_to(PUBLICATION_DIRECTORY.resolve())
        contents = path.read_bytes()
        assert len(contents) == record["bytes"], record["path"]
        assert hashlib.sha256(contents).hexdigest() == record["sha256"], record["path"]


def _publication_source_target_active_cycles(source_rows, direction):
    """Derive global native-cycle witnesses from source, before selecting a peer."""
    configuration = (
        json.loads((RX_REFERENCE_DIRECTORY / "rx_reference.config").read_text(encoding="utf-8"))
        if direction == "RX" else _read_json("demo.config")
    )
    core = configuration["settings"]["core_parameters"]
    station_column, locator_column = (
        ("rx_sign", "rx_loc") if direction == "RX" else ("tx_sign", "tx_loc")
    )
    timestamps = pd.to_datetime(source_rows.time, utc=True)
    selection = core["time_selection"]
    witnesses = source_rows[
        source_rows.band.eq(7)
        & timestamps.ge(pd.Timestamp(selection["start_utc"]))
        & timestamps.lt(pd.Timestamp(selection["end_utc"]))
        & source_rows[station_column].eq(core["callsign"])
        & source_rows[locator_column].str.upper().str.startswith(core["qth"].upper())
    ]
    return set(_utc_nanoseconds(witnesses.time) // 120_000_000_000)


def _assert_publication_gate_flags(reports, source_rows, direction):
    assert reports.passes_target_active_gate.dtype == bool
    cycles = _publication_source_target_active_cycles(source_rows, direction)
    np.testing.assert_array_equal(reports.passes_target_active_gate, reports.time_slot.isin(cycles))


def _publication_source_endpoints(source_rows, direction):
    """Independent row arithmetic, without importing the overlay builder."""
    times = pd.to_datetime(source_rows.time, utc=True)
    series_column, peer_column, grid_column = (
        ("rx_sign", "tx_sign", "tx_loc") if direction == "RX" else ("tx_sign", "rx_sign", "rx_loc")
    )
    selected = source_rows[
        source_rows.band.eq(7) & times.ge(PAPER_START_UTC) & times.lt(PAPER_END_UTC)
        & source_rows[peer_column].eq("VE6PDQ") & source_rows[series_column].isin(["KP4MD", "WB6RQN"])
    ].copy()
    reports = pd.DataFrame({
        "direction": direction, "series": selected[series_column],
        "time_slot": _utc_nanoseconds(selected.time) // 120_000_000_000,
        "utc": pd.to_datetime(selected.time, utc=True), "peer_grid": selected[grid_column],
        "sql_snr_at_30_dbm": selected.snr - selected.power + 30,
        "snr_at_37_dbm": selected.snr - selected.power + 37,
    })
    reports["passes_target_active_gate"] = reports.time_slot.isin(
        _publication_source_target_active_cycles(source_rows, direction)
    )
    assert not reports.duplicated(["series", "time_slot", "peer_grid"]).any()
    return reports.reset_index(drop=True)


def _publication_sql_endpoints(sql_rows, direction):
    active_cycles = set(sql_rows.loc[sql_rows.has_u.gt(0), "time_slot"])
    rows = sql_rows[sql_rows.peer_sign.eq("VE6PDQ")].copy()
    rows["utc"] = pd.to_datetime(rows.time_slot * 120, unit="s", utc=True)
    rows = rows[rows.utc.ge(PAPER_START_UTC) & rows.utc.lt(PAPER_END_UTC)]
    reports = []
    for series, has_column, snr_column in (
        ("KP4MD", "has_u", "snr_u_norm"), ("WB6RQN", "has_r", "snr_r_norm"),
    ):
        endpoint = rows.loc[rows[has_column].gt(0), ["time_slot", "utc", "peer_grid", snr_column]].copy()
        endpoint = endpoint.rename(columns={snr_column: "sql_snr_at_30_dbm"})
        endpoint["direction"] = direction
        endpoint["series"] = series
        endpoint["snr_at_37_dbm"] = endpoint.sql_snr_at_30_dbm + 7
        endpoint["passes_target_active_gate"] = endpoint.time_slot.isin(active_cycles)
        reports.append(endpoint)
    return pd.concat(reports, ignore_index=True)[ENDPOINT_COLUMNS]


def _assert_publication_endpoint_rows(actual, expected):
    def canonical(reports):
        reports = reports[ENDPOINT_COLUMNS].copy()
        reports["utc"] = _utc_nanoseconds(reports.utc)
        return reports.sort_values(["series", "time_slot", "peer_grid"]).reset_index(drop=True)
    pd.testing.assert_frame_equal(canonical(actual), canonical(expected), check_dtype=False, check_exact=True)


@pytest.mark.parametrize("direction,figure_number,run_fixture,counts,retained_reports", [
    ("RX", 6, "rx_reference_run", {"KP4MD": 31, "WB6RQN": 13}, 39),
    ("TX", 7, "reference_run", {"KP4MD": 57, "WB6RQN": 19}, 58),
])
def test_overlays_account_for_every_source_report_before_gating(
    request, direction, figure_number, run_fixture, counts, retained_reports,
):
    run = request.getfixturevalue(run_fixture)
    expected = _publication_source_endpoints(run.source_rows, direction)
    actual = _publication_sql_endpoints(run.sql_rows, direction)
    assert expected.series.value_counts().to_dict() == counts
    _assert_publication_endpoint_rows(actual, expected)
    # The saved overlay CSV is an audited application output, not the oracle.
    # Both it and today's SQL must match independent source-row arithmetic.
    plotted = pd.read_csv(PUBLICATION_DIRECTORY / f"figure{figure_number}_sql_endpoint_reports.csv")
    _assert_publication_endpoint_rows(plotted, expected)
    _assert_publication_gate_flags(plotted, run.source_rows, direction)
    retained = _publication_sql_endpoints(run.processed, direction)
    assert len(retained) == retained_reports < len(actual)
    _assert_publication_endpoint_rows(retained, expected[expected.passes_target_active_gate])


@pytest.mark.parametrize("direction,figure_number,run_fixture,retained_counts,matched_count", [
    ("RX", 6, "rx_reference_run", {"KP4MD": 31, "WB6RQN": 8}, 39),
    ("TX", 7, "reference_run", {"KP4MD": 57, "WB6RQN": 1}, 33),
])
def test_overlay_outer_rings_and_anchor_flags_use_exact_global_target_cycles(
    request, direction, figure_number, run_fixture, retained_counts, matched_count,
):
    run = request.getfixturevalue(run_fixture)
    reports = _publication_source_endpoints(run.source_rows, direction)
    assert reports[reports.passes_target_active_gate].series.value_counts().to_dict() == retained_counts
    anchors = pd.read_csv(PUBLICATION_DIRECTORY / f"figure{figure_number}_anchor_matches.csv")
    anchors["time_slot"] = _utc_nanoseconds(anchors.sql_utc) // 120_000_000_000
    _assert_publication_gate_flags(anchors, run.source_rows, direction)
    assert anchors.passes_target_active_gate.sum() == matched_count
    # The digitized paper time is only a graphical readout. Gate membership is
    # attached to the matched source cycle, independently of that readout.
    distorted_readout = anchors.copy()
    distorted_readout["paper_utc"] = pd.to_datetime(anchors.paper_utc, utc=True) + pd.Timedelta(minutes=4)
    _assert_publication_gate_flags(distorted_readout, run.source_rows, direction)


@pytest.mark.parametrize("direction,run_fixture", [("RX", "rx_reference_run"), ("TX", "reference_run")])
@pytest.mark.parametrize("mutation", ["retain_inactive", "drop_active", "exchange_same_count"])
def test_overlay_gate_oracle_rejects_incorrect_report_flags(request, direction, run_fixture, mutation):
    run = request.getfixturevalue(run_fixture)
    changed = _publication_source_endpoints(run.source_rows, direction)
    active = changed.index[changed.passes_target_active_gate][0]
    inactive = changed.index[~changed.passes_target_active_gate][0]
    if mutation in ("retain_inactive", "exchange_same_count"):
        changed.loc[inactive, "passes_target_active_gate"] = True
    if mutation in ("drop_active", "exchange_same_count"):
        changed.loc[active, "passes_target_active_gate"] = False
    with pytest.raises(AssertionError):
        _assert_publication_gate_flags(changed, run.source_rows, direction)


@pytest.mark.parametrize("direction,run_fixture", [("RX", "rx_reference_run"), ("TX", "reference_run")])
def test_overlay_builder_projects_current_pipeline_outputs_without_expected_inputs(request, direction, run_fixture, monkeypatch):
    from scripts import build_milazzo_publication_overlays as overlays

    run = request.getfixturevalue(run_fixture)
    changed = SimpleNamespace(**vars(run))
    changed.sql_rows = run.sql_rows.copy()
    changed.points = run.points.copy()
    changed.sql_rows.loc[changed.sql_rows.has_u.gt(0), "snr_u_norm"] += 2
    changed.points["metric"] += 2

    def reject_expected_reads(*args, **kwargs):
        pytest.fail("Overlay payload preparation must not read expected CSVs")

    with monkeypatch.context() as guard:
        guard.setattr(overlays.pd, "read_csv", reject_expected_reads)
        original_reports = overlays.sql_endpoint_reports(run, direction)
        changed_reports = overlays.sql_endpoint_reports(changed, direction)
        original_pairs = overlays.paired_evidence_points(run)
        changed_pairs = overlays.paired_evidence_points(changed)
    target = original_reports.series.eq("KP4MD")
    np.testing.assert_array_equal(changed_reports.loc[target, "snr_at_37_dbm"], original_reports.loc[target, "snr_at_37_dbm"] + 2)
    np.testing.assert_array_equal(changed_reports.loc[~target, "snr_at_37_dbm"], original_reports.loc[~target, "snr_at_37_dbm"])
    np.testing.assert_array_equal(changed_reports.passes_target_active_gate, original_reports.passes_target_active_gate)
    np.testing.assert_array_equal(changed_pairs.metric, original_pairs.metric + 2)
    # The lower panel is the production paired-eligibility projection. Removing
    # a plotted point there must remove it even if an earlier unit still exists.
    assert not original_pairs.empty
    removed = original_pairs.index[0]
    changed.points = run.points.drop(index=removed)
    assert len(overlays.paired_evidence_points(changed)) == len(original_pairs) - 1


@pytest.mark.parametrize("direction,run_fixture", [("RX", "rx_reference_run"), ("TX", "reference_run")])
def test_overlay_gate_rings_require_both_production_retention_and_inspector_outcome(request, direction, run_fixture):
    from scripts import build_milazzo_publication_overlays as overlays

    run = request.getfixturevalue(run_fixture)
    changed = SimpleNamespace(**vars(run))
    unit_times = pd.to_datetime(run.units.evidence_utc, utc=True)
    chosen = run.units[run.units.peer_sign.eq("VE6PDQ") & unit_times.ge(PAPER_START_UTC) & unit_times.lt(PAPER_END_UTC)].iloc[0]
    chosen_slot = int(pd.Timestamp(chosen.evidence_utc).timestamp()) // 120
    chosen_processed = run.processed.time_slot.eq(chosen_slot) & run.processed.peer_sign.eq(chosen.peer_sign) & run.processed.peer_grid.eq(chosen.peer_grid)
    assert chosen_processed.sum() == 1
    changed.processed = run.processed[~chosen_processed]
    with pytest.raises(ValueError, match="additional post-fetch exclusion"):
        overlays.sql_endpoint_reports(changed, direction)
    changed.processed = run.processed
    chosen_unit = run.units.evidence_utc.eq(chosen.evidence_utc) & run.units.peer_sign.eq(chosen.peer_sign) & run.units.peer_grid.eq(chosen.peer_grid)
    changed.units = run.units[~chosen_unit]
    with pytest.raises(ValueError, match="production Inspector units"):
        overlays.sql_endpoint_reports(changed, direction)


def _figure7_matches_from_source_bound_sql(sql_rows, source_rows):
    anchors = pd.read_csv(PUBLICATION_DIRECTORY / "figure7_paper_anchors.csv")
    source = _publication_source_endpoints(source_rows, "TX")
    actual = _publication_sql_endpoints(sql_rows, "TX").set_index(["series", "time_slot", "peer_grid"])
    assert actual.index.is_unique
    matches, identities = [], []
    for marker in anchors.itertuples():
        residual_seconds = (source.utc - pd.Timestamp(marker.paper_utc)).dt.total_seconds()
        nearby = source[source.series.eq(marker.series) & residual_seconds.abs().le(240)]
        # Resolve the paper identity from raw source values, never from the
        # production SNR being tested. SQL cannot change its own expected match.
        candidates = nearby[nearby.snr_at_37_dbm.eq(marker.paper_snr_db)]
        assert len(candidates) == 1, marker.marker_id
        report = candidates.iloc[0]
        identity = (report.series, report.time_slot, report.peer_grid)
        assert identity in actual.index, marker.marker_id
        calculated = actual.loc[identity]
        assert calculated.sql_snr_at_30_dbm + 7 == marker.paper_snr_db, marker.marker_id
        identities.append(identity)
        matches.append({
            "marker_id": marker.marker_id, "series": marker.series, "paper_utc": marker.paper_utc,
            "sql_utc": report.utc.isoformat(), "paper_snr_db": marker.paper_snr_db,
            "sql_snr_at_30_dbm": calculated.sql_snr_at_30_dbm,
            "sql_snr_at_37_dbm": calculated.snr_at_37_dbm,
            "time_error_seconds": round(residual_seconds.loc[report.name], 6),
            "snr_error_db": calculated.snr_at_37_dbm - marker.paper_snr_db,
            "nearby_time_candidates": len(nearby),
            "passes_target_active_gate": bool(report.passes_target_active_gate),
        })
    assert len(matches) == len(set(identities)) == 47
    return pd.DataFrame(matches)


def test_figure7_all_47_independent_paper_anchors_match_actual_tx_sql(reference_run):
    matched = _figure7_matches_from_source_bound_sql(reference_run.sql_rows, reference_run.source_rows)
    assert matched.series.value_counts().to_dict() == {"KP4MD": 32, "WB6RQN": 15}
    assert matched.snr_error_db.eq(0).all()
    assert matched.time_error_seconds.abs().max() <= 143.697
    assert matched.loc[matched.series.eq("KP4MD"), "paper_snr_db"].min() == -28
    ledger = pd.read_csv(PUBLICATION_DIRECTORY / "figure7_anchor_matches.csv")
    pd.testing.assert_frame_equal(matched, ledger, check_dtype=False, check_exact=False, rtol=0, atol=1e-9)


def test_publication_images_and_figure7_calibration_are_frozen(verified_publication_files):
    from PIL import Image
    features = json.loads((PUBLICATION_DIRECTORY / "figure7_paper_features.json").read_text())
    summary = json.loads((PUBLICATION_DIRECTORY / "overlay_summary.json").read_text())
    for number in (6, 7):
        source_path = PUBLICATION_DIRECTORY / f"paper_figure{number}.jpg"
        assert hashlib.sha256(source_path.read_bytes()).hexdigest() == summary["source_figures"][str(number)]["sha256"]
        with Image.open(source_path) as original:
            assert original.size == (1317, 656)
            original.verify()
    for filename in ("figure6_rx_overlay.png", "figure7_tx_overlay.png"):
        with Image.open(PUBLICATION_DIRECTORY / filename) as overlay:
            assert overlay.size == (3840, 2592)
            overlay.verify()
    assert features["figure_sha256"] == summary["source_figures"]["7"]["sha256"]
    gate = summary["target_active_gate"]
    assert gate["rule"] == "global_time_slot"
    assert pd.Timestamp(gate["plot_start_utc"]) == PAPER_START_UTC
    assert pd.Timestamp(gate["plot_end_utc_exclusive"]) == PAPER_END_UTC
    assert gate["sql_reports_retained"] == {"figure6": 39, "figure7": 58}
    assert gate["matched_anchors_retained"] == {"figure6": 39, "figure7": 33}
    assert features["matched_direction"] == "TX"
    assert features["printed_title"] == "WSPR 40m SNR from VE6PDQ"
    anchors = pd.read_csv(PUBLICATION_DIRECTORY / "figure7_paper_anchors.csv")
    assert anchors.marker_id.nunique() == len(anchors) == 47
    assert anchors.time_tolerance_seconds.eq(240).all() and anchors.snr_tolerance_db.eq(0.25).all()
    pixel_utc = PAPER_START_UTC + pd.to_timedelta((anchors.x_pixel - 78) * 1920 / 1086, unit="min")
    assert (pd.to_datetime(anchors.paper_utc, utc=True) - pixel_utc).dt.total_seconds().abs().max() < 0.0001
    np.testing.assert_array_equal(np.rint((104 - anchors.y_pixel) / 15), anchors.paper_snr_db)
    assert ((104 - anchors.y_pixel) / 15 - anchors.paper_snr_db).abs().max() < 0.25


def test_figure7_unplotted_and_overlapping_reports_are_kept_without_fabricating_pairs(reference_run):
    reports = _publication_sql_endpoints(reference_run.sql_rows, "TX")
    extra = reports[reports.series.eq("WB6RQN") & reports.utc.eq(pd.Timestamp("2010-12-19T13:38Z"))]
    assert len(extra) == 1
    assert extra.iloc[0].sql_snr_at_30_dbm == -9 and extra.iloc[0].snr_at_37_dbm == -2
    matches = _figure7_matches_from_source_bound_sql(reference_run.sql_rows, reference_run.source_rows)
    assert not (matches.series.eq("WB6RQN") & pd.to_datetime(matches.sql_utc, utc=True).eq(extra.iloc[0].utc)).any()
    close = reports[
        (reports.series.eq("KP4MD") & reports.utc.eq(pd.Timestamp("2010-12-20T10:34Z")))
        | (reports.series.eq("WB6RQN") & reports.utc.eq(pd.Timestamp("2010-12-20T10:36Z")))
    ]
    assert len(close) == 2 and close.snr_at_37_dbm.eq(-19).all()
    assert close.time_slot.nunique() == 2
    assert close.set_index("series").passes_target_active_gate.to_dict() == {"KP4MD": True, "WB6RQN": False}
    # The paper's four-minute matching tolerance must never turn the adjacent
    # 10:36 Reference cycle into a Target-active cycle witnessed at 10:34.
    wrongly_ringed = close.copy()
    wrongly_ringed["passes_target_active_gate"] = True
    with pytest.raises(AssertionError):
        _assert_publication_gate_flags(wrongly_ringed, reference_run.source_rows, "TX")
    native = _canonical_units(reference_run.units)
    assert not native.loc[native.peer_sign.eq("VE6PDQ") & native.time_slot.isin(close.time_slot), "outcome"].eq("joint").any()


@pytest.mark.parametrize("mutation", ["snr_shift", "wrong_reference_power", "exchange_series", "drop_anchor"])
def test_figure7_paper_oracle_rejects_broken_calculations(reference_run, mutation):
    changed = reference_run.sql_rows.copy()
    if mutation == "snr_shift":
        changed.loc[changed.has_u.gt(0), "snr_u_norm"] += 1
    elif mutation == "wrong_reference_power":
        changed.loc[changed.has_r.gt(0), "snr_r_norm"] -= 4
    elif mutation == "exchange_series":
        changed[["has_u", "has_r"]] = changed[["has_r", "has_u"]].to_numpy()
        changed[["snr_u_norm", "snr_r_norm"]] = changed[["snr_r_norm", "snr_u_norm"]].to_numpy()
    else:
        tail_slot = int(pd.Timestamp("2010-12-19T17:36Z").timestamp()) // 120
        changed = changed[~(changed.peer_sign.eq("VE6PDQ") & changed.time_slot.eq(tail_slot))]
    with pytest.raises(AssertionError):
        _figure7_matches_from_source_bound_sql(changed, reference_run.source_rows)


@pytest.mark.parametrize("run_fixture,direction,expected_metrics", [
    ("rx_reference_run", "RX", [7, 7, 8, 17, 22]),
    ("reference_run", "TX", [-2]),
])
def test_publication_joint_survival_guides_preserve_exact_frozen_endpoints(
    request, run_fixture, direction, expected_metrics,
):
    from scripts import build_milazzo_publication_overlays as overlays

    run = request.getfixturevalue(run_fixture)
    reports = overlays.sql_endpoint_reports(run, direction)
    pairs = overlays.paired_evidence_points(run)
    connections = overlays._joint_survival_connections(reports, pairs)
    expected_pairs = (
        _read_rx_csv("expected_paired_rows.csv") if direction == "RX"
        else _read_csv("expected_paired_rows.csv")
    )
    expected_pairs["utc"] = pd.to_datetime(expected_pairs.time_slot * 120, unit="s", utc=True)
    expected_pairs = expected_pairs[
        expected_pairs.peer_sign.eq("VE6PDQ")
        & expected_pairs.utc.ge(PAPER_START_UTC)
        & expected_pairs.utc.lt(PAPER_END_UTC)
    ].sort_values(["utc", "peer_grid"])
    # Frozen independently reviewed pair identities prevent linking nearby
    # unpaired reports or collapsing DO34 and DO34ir into one locator.
    expected_connections = [{
        "utc": pair.utc.isoformat(), "peer_grid": pair.peer_grid,
        "target_snr_at_37_dbm": pair.target_snr_db + 7,
        "reference_snr_at_37_dbm": pair.reference_snr_db + 7,
        "paired_delta_snr_db": pair.delta_snr_db,
    } for pair in expected_pairs.itertuples()]
    assert connections == expected_connections
    assert len(connections) == len(expected_metrics)
    assert sorted(connection["paired_delta_snr_db"] for connection in connections) == expected_metrics
    assert reports.passes_target_active_gate.sum() > 2 * len(connections)


@pytest.mark.parametrize("invalid_endpoint", [
    "missing", "duplicate", "different_full_locator", "gate_excluded", "different_delta",
])
def test_publication_joint_survival_guides_reject_unreconciled_endpoints(
    rx_reference_run, invalid_endpoint,
):
    from scripts import build_milazzo_publication_overlays as overlays

    reports = overlays.sql_endpoint_reports(rx_reference_run, "RX")
    pairs = overlays.paired_evidence_points(rx_reference_run).sort_values(["plot_time", "grid"]).iloc[[0]].copy()
    pair = pairs.iloc[0]
    selected_endpoint = (
        pd.to_datetime(reports.utc, utc=True).eq(pd.Timestamp(pair.plot_time))
        & reports.peer_grid.eq(pair.grid)
        & reports.series.eq("WB6RQN")
    )
    assert selected_endpoint.sum() == 1
    if invalid_endpoint == "missing":
        reports = reports.loc[~selected_endpoint].copy()
    elif invalid_endpoint == "duplicate":
        reports = pd.concat([reports, reports.loc[selected_endpoint]], ignore_index=True)
    elif invalid_endpoint == "different_full_locator":
        assert pair.grid == "DO34ir"
        reports.loc[selected_endpoint, "peer_grid"] = "DO34"
    elif invalid_endpoint == "gate_excluded":
        reports.loc[selected_endpoint, "passes_target_active_gate"] = False
    else:
        pairs["metric"] += 1
    with pytest.raises(ValueError, match="Joint survival"):
        overlays._joint_survival_connections(reports, pairs)


@pytest.mark.parametrize("run_fixture,expected_metrics,identity_count", [
    ("rx_reference_run", [7, 7, 8, 17, 22], 2),
    ("reference_run", [-2], 1),
])
def test_publication_native_temporal_recipe_preserves_path_population_and_exact_window(
    request, run_fixture, expected_metrics, identity_count,
):
    from matplotlib import dates as mdates
    from scripts import build_milazzo_publication_overlays as overlays
    from ui.plots.evidence_figures import _compare_temporal_profile_values

    run = request.getfixturevalue(run_fixture)
    points = overlays.paired_evidence_points(run)
    recipe = overlays._production_temporal_recipe(run)
    assert sorted(points.metric.tolist()) == expected_metrics
    assert points.station.eq("VE6PDQ").all()
    assert points.grid.nunique() == identity_count
    assert recipe["kind"] == "selected_benchmark_temporal"
    assert recipe["time_bin"] == "3h"
    assert recipe["selected_identity_count"] == identity_count
    assert recipe["analysis_start_utc_ns"] == PAPER_START_UTC.value
    assert recipe["analysis_end_utc_ns"] == PAPER_END_UTC.value
    assert recipe["reference_snr_correction_db"] == run.context.reference_snr_correction_db
    profiles = recipe["prepared_profiles"]
    counts, summaries, edges, centers = _compare_temporal_profile_values(
        profiles["chronological"]["3h"]
    )
    # Independently place every unchanged production pair in its displayed cell.
    # The last bin is two hours long; the selected window must not become 33 h.
    expected_edges = mdates.date2num([
        *(PAPER_START_UTC + pd.Timedelta(hours=3 * index) for index in range(11)),
        PAPER_END_UTC,
    ])
    np.testing.assert_allclose(edges, expected_edges, rtol=0, atol=1e-10)
    np.testing.assert_allclose(centers, (expected_edges[:-1] + expected_edges[1:]) / 2, rtol=0, atol=1e-10)
    expected_counts, _, _ = np.histogram2d(
        points.metric.to_numpy(),
        mdates.date2num(pd.to_datetime(points.plot_time, utc=True).to_numpy()),
        bins=(profiles["y_edges"], expected_edges),
    )
    np.testing.assert_array_equal(counts, expected_counts)
    expected_bin_counts = expected_counts.sum(axis=0)
    populated_bins = expected_bin_counts > 0
    np.testing.assert_array_equal(summaries.loc[populated_bins, "count"], expected_bin_counts[populated_bins])
    assert summaries.loc[~populated_bins, "count"].isna().all()
    assert int(counts.sum()) == len(expected_metrics)
    assert recipe["median_focus"]["median_db"] == np.median(expected_metrics)
    if run_fixture == "reference_run":
        assert len(run.points) == 45 > len(points) == 1
    else:
        assert set(points.grid) == {"DO34", "DO34ir"}


@pytest.mark.parametrize("run_fixture", ["rx_reference_run", "reference_run"])
def test_publication_native_temporal_recipe_excludes_other_peers_and_window_boundaries(request, run_fixture):
    from scripts import build_milazzo_publication_overlays as overlays
    from ui.plots.evidence_figures import _compare_temporal_profile_values

    run = request.getfixturevalue(run_fixture)
    original_recipe = overlays._production_temporal_recipe(run)
    selected_point = overlays.paired_evidence_points(run).iloc[[0]].copy()
    other_peer = selected_point.assign(station="OTHER", metric=101.0)
    before_window = selected_point.assign(plot_time=PAPER_START_UTC - pd.Timedelta(minutes=2), metric=102.0)
    at_exclusive_end = selected_point.assign(plot_time=PAPER_END_UTC, metric=103.0)
    changed = SimpleNamespace(**vars(run))
    changed.points = pd.concat([run.points, other_peer, before_window, at_exclusive_end], ignore_index=True)
    changed_recipe = overlays._production_temporal_recipe(changed)
    original_profile = original_recipe["prepared_profiles"]["chronological"]["3h"]
    changed_profile = changed_recipe["prepared_profiles"]["chronological"]["3h"]
    original_counts, original_summaries, original_edges, original_centers = _compare_temporal_profile_values(original_profile)
    changed_counts, changed_summaries, changed_edges, changed_centers = _compare_temporal_profile_values(changed_profile)
    np.testing.assert_array_equal(changed_counts, original_counts)
    pd.testing.assert_frame_equal(changed_summaries, original_summaries)
    np.testing.assert_array_equal(changed_edges, original_edges)
    np.testing.assert_array_equal(changed_centers, original_centers)
    assert changed_recipe["selected_identity_count"] == original_recipe["selected_identity_count"]
    assert changed_recipe["median_focus"] == original_recipe["median_focus"]


@pytest.mark.parametrize("direction", ["RX", "TX"])
def test_publication_underlay_extent_preserves_frozen_pixel_calibration(direction):
    from matplotlib import dates as mdates
    from scripts import build_milazzo_publication_overlays as overlays

    image_width, image_height = 1317, 656
    if direction == "RX":
        calibration = json.loads(
            (RX_REFERENCE_DIRECTORY / "paper_features_original.json").read_text(encoding="utf-8")
        )["calibration"]
        minutes_per_pixel = calibration["minutes_from_axis_start_per_x_pixel"]
        minutes_intercept = calibration["minutes_intercept"]
        db_per_pixel = calibration["snr_db_per_y_pixel"]
        db_intercept = calibration["snr_db_intercept"]
    else:
        # Independently frozen paper ticks: x=78..1164 spans exactly 32 h;
        # y=104..554 spans 0..-30 dB, with no report-derived adjustment.
        minutes_per_pixel = 1920 / (1164 - 78)
        minutes_intercept = -78 * minutes_per_pixel
        db_per_pixel = -30 / (554 - 104)
        db_intercept = -104 * db_per_pixel
    start_days = mdates.date2num(PAPER_START_UTC)
    expected_extent = (
        start_days + (minutes_intercept - .5 * minutes_per_pixel) / 1440,
        start_days + (minutes_intercept + (image_width - .5) * minutes_per_pixel) / 1440,
        db_intercept + (image_height - .5) * db_per_pixel,
        db_intercept - .5 * db_per_pixel,
    )
    extent = overlays._paper_image_extent((image_width, image_height), direction)
    np.testing.assert_allclose(extent, expected_extent, rtol=0, atol=1e-10)
    assert extent[0] < extent[1] and extent[2] < extent[3]

    pixel_x = np.array([78.0, 621.0, 1164.0])
    pixel_y = np.array([104.0, 297.0, 554.0])
    expected_minutes = minutes_intercept + pixel_x * minutes_per_pixel
    expected_snr = db_intercept + pixel_y * db_per_pixel
    endpoints = pd.DataFrame({
        "utc": PAPER_START_UTC + pd.to_timedelta(expected_minutes, unit="min"),
        "snr_at_37_dbm": expected_snr,
    })
    mapped_x, mapped_y = overlays.paper_coordinates(endpoints, direction)
    np.testing.assert_allclose(mapped_x, pixel_x, rtol=0, atol=1e-7)
    np.testing.assert_allclose(mapped_y, pixel_y, rtol=0, atol=1e-10)
    # imshow's upper-origin pixel centers must land on those same report
    # coordinates, including the half-pixel image boundary convention.
    restored_days = extent[0] + (mapped_x + .5) / image_width * (extent[1] - extent[0])
    restored_snr = extent[3] + (mapped_y + .5) / image_height * (extent[2] - extent[3])
    np.testing.assert_allclose(restored_days, start_days + expected_minutes / 1440, rtol=0, atol=1e-10)
    np.testing.assert_allclose(restored_snr, expected_snr, rtol=0, atol=1e-10)


@pytest.mark.parametrize("figure_number", [6, 7])
def test_publication_pdf_uses_three_panel_style_with_vector_evidence_and_linked_sources(
    figure_number, verified_publication_files,
):
    from pypdf import PdfReader
    from pypdf.generic import ContentStream
    from config.demo_pdf_headers import DEMO_PDF_HEADERS
    from scripts.demo_pdf_footer import DEMO_PDF_FOOTER_TEXT

    filename = f"WSPRadar_Demo_Milazzo_Figure{figure_number}.pdf"
    source_path = PUBLICATION_DIRECTORY / filename
    published_path = REPOSITORY_DIRECTORY / "static/reference_figures/milazzo_publication_overlays_v1" / filename
    assert published_path.read_bytes() == source_path.read_bytes()
    document = PdfReader(source_path)
    assert len(document.pages) == 1
    page = document.pages[0]
    assert float(page.mediabox.width) == pytest.approx(24 * 72)
    assert float(page.mediabox.height) == pytest.approx(16.2 * 72)
    assert float(page.mediabox.width) / float(page.mediabox.height) == pytest.approx(16 / 10.8)
    presentation = json.loads(
        (PUBLICATION_DIRECTORY / "overlay_summary.json").read_text(encoding="utf-8")
    )["presentation_checks"][f"figure{figure_number}"]
    assert presentation["panel_b_underlay"]["opacity"] == 1.0
    layout = presentation["layout_checks"]
    original_plot = np.array(layout["panel_a_plot_bounds"])
    reconstruction_plot = np.array(layout["panel_b_plot_bounds"])
    native_plot = np.array(layout["panel_c_plot_bounds"])
    density_scale = np.array(layout["panel_c_density_bounds"])
    # Stack reconstruction and native evidence on identical time coordinates;
    # retain the visible paper graph size, not its larger requested image box.
    np.testing.assert_allclose(native_plot[[0, 2, 3]], reconstruction_plot[[0, 2, 3]], rtol=0, atol=1e-10)
    np.testing.assert_allclose(native_plot[[2, 3]], original_plot[[2, 3]], rtol=0, atol=1e-10)
    assert native_plot[1] + native_plot[3] < reconstruction_plot[1]
    np.testing.assert_allclose(layout["panel_b_time_limits"], layout["panel_c_time_limits"], rtol=0, atol=1e-10)
    assert density_scale[0] == pytest.approx(layout["panel_a_legend_left"] + .5, abs=1e-10)
    np.testing.assert_allclose(density_scale[[1, 3]], native_plot[[1, 3]], rtol=0, atol=1e-10)
    connections = presentation["joint_survival_connections"]
    assert layout["joint_survival_guide_count"] == len(connections) == (5 if figure_number == 6 else 1)
    assert sorted(connection["paired_delta_snr_db"] for connection in connections) == (
        [7, 7, 8, 17, 22] if figure_number == 6 else [-2]
    )
    guide_endpoints = layout["joint_survival_guide_endpoints"]
    assert len(guide_endpoints) == len(connections)
    for guide in guide_endpoints:
        source_x, source_y = guide["source_figure_xy"]
        native_x, native_y = guide["native_figure_xy"]
        assert source_x == pytest.approx(native_x, abs=1e-10)
        assert reconstruction_plot[0] <= source_x <= reconstruction_plot[0] + reconstruction_plot[2]
        assert reconstruction_plot[1] <= source_y <= reconstruction_plot[1] + reconstruction_plot[3]
        assert native_plot[1] <= native_y <= native_plot[1] + native_plot[3]
    summary_legend = layout["panel_c_summary_legend_bounds"]
    exact_legend = layout["panel_c_exact_legend_bounds"]
    for legend in (summary_legend, exact_legend):
        assert legend[1] + legend[3] < native_plot[1]
        assert legend[0] >= native_plot[0] - 1e-10
        assert legend[0] + legend[2] <= native_plot[0] + native_plot[2] + 1e-10
    assert exact_legend[1] + exact_legend[3] < summary_legend[1]
    report_legend = layout["panel_b_series_legend_bounds"]
    gate_legend = layout["panel_b_gate_legend_bounds"]
    for legend in (report_legend, gate_legend):
        assert legend[1] + legend[3] < original_plot[1]
    assert gate_legend[1] + gate_legend[3] < report_legend[1]
    original_image = layout["panel_a_image_bounds"]
    direction_note = layout["direction_note_bounds"]
    assert direction_note[0] + direction_note[2] / 2 == pytest.approx(
        original_image[0] + original_image[2] / 2, abs=1e-10,
    )
    assert direction_note[1] + direction_note[3] < original_image[1]
    assert direction_note[1] > native_plot[1] + native_plot[3]
    header = DEMO_PDF_HEADERS[f"milazzo_figure{figure_number}"]
    text = "".join(page.extract_text().split())
    expected_phrases = (
        "WSPRadar.org reconstruction & comparison",
        header.descriptive_title,
        f"Referenced publication: {header.publication_authors}.",
        header.publication_title,
        f"Source figure: {header.source_figure}",
        header.publication_details,
        f"Demo: {header.demo_details}",
        "Panel A - Original image from publication",
        "Panel B - Reconstruction",
        "Panel C - WSPRadar view",
        DEMO_PDF_FOOTER_TEXT,
    )
    for phrase in expected_phrases:
        assert "".join(phrase.split()) in text, phrase
    assert document.metadata.author == DEMO_PDF_FOOTER_TEXT
    assert document.metadata.title.startswith("WSPRadar.org reconstruction & comparison:")
    links = {
        annotation.get_object().get("/A", {}).get("/URI")
        for annotation in page.get("/Annots", [])
    }
    assert {"https://wspradar.org", header.publication_url}.issubset(links)
    resources = page["/Resources"]
    fonts = [font.get_object() for font in resources["/Font"].values()]
    assert fonts and all(font["/Subtype"] == "/Type0" for font in fonts)
    assert any("DejaVuSans" in font["/BaseFont"] for font in fonts)
    for font in fonts:
        for descendant in font["/DescendantFonts"]:
            descriptor = descendant.get_object()["/FontDescriptor"]
            assert descriptor["/FontFile2"].get_data()
    images = [
        image.get_object()
        for image in resources["/XObject"].values()
        if image.get_object().get("/Subtype") == "/Image"
    ]
    assert images and any(image["/Width"] >= 500 and image["/Height"] >= 200 for image in images)
    operators = {operator for _, operator in ContentStream(page.get_contents(), document).operations}
    # Searchable text and stroked vector paths accompany the original raster;
    # an image-only export of the completed page cannot satisfy these checks.
    assert b"BT" in operators and (b"TJ" in operators or b"Tj" in operators)
    assert {b"m", b"c", b"S"}.issubset(operators)
