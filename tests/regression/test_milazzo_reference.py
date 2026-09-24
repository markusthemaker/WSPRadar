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
from core.map_data import build_map_data_result
from core.math_utils import locator_to_latlon
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


REFERENCE_DIRECTORY = Path(__file__).parent / "reference_fixtures" / "milazzo_tx_reference_v1"
RX_REFERENCE_DIRECTORY = Path(__file__).parent / "reference_fixtures" / "milazzo_fig6_rx_v1"
PUBLICATION_DIRECTORY = Path(__file__).parent / "reference_fixtures" / "milazzo_publication_overlays_v1"
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


def test_demo_uses_correct_geographic_counts_and_unchanged_scientific_settings(reference_run):
    installed = json.loads((REPOSITORY_DIRECTORY / "config/demos/05_milazzo_tx_buddy.config").read_text(encoding="utf-8"))
    frozen_settings = _read_json("demo.config")["settings"]
    installed_settings = installed["settings"]
    for section in ("comparison_parameters", "advanced_parameters"):
        assert installed_settings[section] == frozen_settings[section]
    installed_core = installed_settings["core_parameters"]
    frozen_core = frozen_settings["core_parameters"]
    assert {key: value for key, value in installed_core.items() if key != "time_selection"} == {
        key: value for key, value in frozen_core.items() if key != "time_selection"
    }
    assert pd.Timestamp(installed_core["time_selection"]["start_utc"]) == PAPER_START_UTC
    assert pd.Timestamp(installed_core["time_selection"]["end_utc"]) == PAPER_END_UTC
    assert frozen_core["time_selection"] == {
        "start_utc": "2010-12-18T00:00Z", "end_utc": "2010-12-21T00:00Z",
    }
    assert reference_run.context.max_peer_distance_km == 5000
    assert reference_run.context.reference_snr_correction_db == 0
    description = installed["profile"]["description"]["en"]
    assert "45 Joint observations across 30 receivers and nine shared cycles" in description
    assert "mean **−3.96 dB** and median **−4 dB**" in description
    assert "1 Joint Spot, 56 Only KP4MD and 0 Only WB6RQN" in description
    assert "normalization to 1 W" in description and "ΔSNR = −2 dB" in description
    assert "Figure 7" in description and "printed direction is reversed" in description
    assert "have not yet been reconciled" not in description


def test_publication_window_demo_matches_the_independent_frozen_subpopulation(reference_run):
    installed = json.loads((REPOSITORY_DIRECTORY / "config/demos/05_milazzo_tx_buddy.config").read_text(encoding="utf-8"))
    publication_run = _calculate_run(reference_run.source_rows, configuration_document=installed)
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
            assert overlay.size == (2560, 1728)
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
