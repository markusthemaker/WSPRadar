"""Regression contracts for pure Delta-SNR outlier export tables."""

from dataclasses import replace

import pandas as pd
import pytest

from config.delta_snr_outlier import DeltaSnrOutlierDetectionPolicy
from ui.inspector.outlier_candidates import (
    DELTA_SNR_OUTLIER_DETECTION_RESOLUTION,
    DELTA_SNR_OUTLIER_DETECTOR_VERSION,
    DeltaSnrOutlierCandidate,
    DeltaSnrOutlierModel,
    DeltaSnrOutlierReportEntry,
    OutlierStationIdentity,
    detect_delta_snr_outlier_candidates,
)
from ui.inspector.outlier_export import (
    DELTA_SNR_OUTLIER_EXPORT_SCHEMA_VERSION,
    DeltaSnrOutlierExportTables,
    OUTLIER_EVENT_PATH_COLUMNS,
    OUTLIER_EVENT_PATHS_TABLE_FILENAME,
    OUTLIER_EXPORT_JOINT_SPOT,
    OUTLIER_PAIRED_EVIDENCE_COLUMNS,
    OUTLIER_PAIRED_EVIDENCE_TABLE_FILENAME,
    build_delta_snr_outlier_export_metadata,
    build_delta_snr_outlier_export_tables,
)
from ui.inspector.outlier_report import build_delta_snr_outlier_report_view_model


def _candidate(
    callsign,
    locator,
    evidence_times,
    delta_snr_values,
    *,
    event_kind="short_burst",
    direction="NNE",
    baseline_db=5.0,
    robust_spread_db=0.5,
):
    """Build one internally consistent path candidate for export tests."""
    timestamps = tuple(pd.Timestamp(value) for value in evidence_times)
    residuals = tuple(float(value) - baseline_db for value in delta_snr_values)
    median_delta_snr_db = float(pd.Series(delta_snr_values).median())
    median_residual_db = median_delta_snr_db - baseline_db
    agreeing_count = sum(
        residual > 0.0 if median_residual_db > 0.0 else residual < 0.0
        for residual in residuals
    )
    gaps = [
        float((later - earlier) / pd.Timedelta(minutes=1))
        for earlier, later in zip(timestamps, timestamps[1:])
    ]
    representative_index = max(
        range(len(residuals)),
        key=lambda index: abs(residuals[index]),
    )
    return DeltaSnrOutlierCandidate(
        station_identity=OutlierStationIdentity(callsign, locator),
        direction_sector=direction,
        event_kind=event_kind,
        start_utc=timestamps[0],
        end_utc=timestamps[-1] + pd.Timedelta(nanoseconds=1),
        baseline_anchor_start_utc=timestamps[0],
        baseline_anchor_end_utc=timestamps[-1],
        episode_guard_minutes=10.0,
        representative_utc=timestamps[representative_index],
        representative_delta_snr_db=float(
            delta_snr_values[representative_index]
        ),
        episode_median_delta_snr_db=median_delta_snr_db,
        station_baseline_db=baseline_db,
        pre_baseline_db=baseline_db - 0.2,
        post_baseline_db=baseline_db + 0.4,
        median_anomaly_db=median_residual_db,
        peak_anomaly_db=residuals[representative_index],
        mad_db=robust_spread_db,
        robust_spread_db=robust_spread_db,
        robust_spread_method="mad",
        robust_z=0.6745 * median_residual_db / robust_spread_db,
        pre_flank_cell_count=5,
        post_flank_cell_count=6,
        paired_unit_count=len(timestamps),
        agreeing_paired_unit_count=agreeing_count,
        paired_unit_sign_agreement_fraction=agreeing_count / len(timestamps),
        observed_span_minutes=float(
            (timestamps[-1] - timestamps[0]) / pd.Timedelta(minutes=1)
        ),
        largest_gap_minutes=max(gaps) if gaps else 0.0,
        target_median_snr_db=-10.0,
        target_baseline_db=-12.0,
        target_anomaly_db=2.0,
        reference_median_snr_db=-15.0,
        reference_baseline_db=-17.0,
        reference_anomaly_db=2.0,
        path_effective_cadence_minutes=2.0,
        maximum_episode_gap_minutes=15.0,
        diagnostic_neighborhood_minutes=15.0,
        nearby_joint_unit_count=len(timestamps) + 2,
        nearby_target_only_unit_count=1,
        nearby_reference_only_unit_count=2,
        decode_edge_warning=True,
        decode_edge_warning_reason="reference_missing_near_positive_episode",
    )


def _report_entry(*candidates, episode_index=0, event_kind=None, scope=None):
    """Build one cross-path entry without changing candidate measurements."""
    event_kinds = tuple(dict.fromkeys(c.event_kind for c in candidates))
    anomalies = [candidate.median_anomaly_db for candidate in candidates]
    sign = "positive" if all(value > 0 for value in anomalies) else "negative"
    return DeltaSnrOutlierReportEntry(
        episode_index=episode_index,
        start_utc=min(candidate.start_utc for candidate in candidates),
        end_utc=max(candidate.end_utc for candidate in candidates),
        event_kind=(
            event_kind
            or (event_kinds[0] if len(event_kinds) == 1 else "mixed_duration")
        ),
        coherence_scope=scope or (
            "path_specific" if len(candidates) == 1 else "multiple_paths"
        ),
        contributing_station_count=len(candidates) + 2,
        evaluable_station_count=len(candidates) + 1,
        candidates=tuple(candidates),
        median_signed_anomaly_db=float(pd.Series(anomalies).median()),
        maximum_absolute_anomaly_db=max(
            abs(candidate.peak_anomaly_db) for candidate in candidates
        ),
        maximum_anomaly_db=max(
            candidates,
            key=lambda candidate: abs(candidate.peak_anomaly_db),
        ).peak_anomaly_db,
        sign_agreement=sign,
        agreeing_count=len(candidates),
        segment_median_signed_anomaly_db=float(pd.Series(anomalies).median()),
        segment_sign_agreement=sign,
        segment_agreeing_count=len(candidates),
        segment_positive_station_count=(
            len(candidates) if sign == "positive" else 0
        ),
        segment_negative_station_count=(
            len(candidates) if sign == "negative" else 0
        ),
        segment_neutral_station_count=1,
        direction_sectors=tuple(
            dict.fromkeys(
                candidate.direction_sector for candidate in candidates
            )
        ),
        sector_summaries=(),
        station_identities=tuple(
            dict.fromkeys(
                candidate.station_identity for candidate in candidates
            )
        ),
    )


def _model(*entries):
    """Build a detector model with intentionally supplied report-entry order."""
    candidates = tuple(
        candidate for entry in entries for candidate in entry.candidates
    )
    return DeltaSnrOutlierModel(
        detector_version=DELTA_SNR_OUTLIER_DETECTOR_VERSION,
        detection_resolution=DELTA_SNR_OUTLIER_DETECTION_RESOLUTION,
        paired_unit_cadence_minutes=2.0,
        analysis_start_utc=min(entry.start_utc for entry in entries),
        analysis_end_utc=max(entry.end_utc for entry in entries),
        populated_station_cycle_count=len(candidates),
        evaluable_station_cycle_count=len(candidates),
        abstained_station_cycle_count=0,
        candidates=candidates,
        report_entries=tuple(entries),
        candidate_signature="export-test-signature",
        detection_policy=DeltaSnrOutlierDetectionPolicy(
            minimum_departure_db=3.0,
            minimum_robust_z=4.0,
            maximum_baseline_difference_db=3.0,
        ),
    )


def _comparison_units(*candidate_value_pairs):
    """Build exact canonical Joint rows with reconstructable SNR components."""
    rows = []
    for candidate, delta_snr_values in candidate_value_pairs:
        for evidence_utc, delta_snr_db in zip(
            pd.date_range(
                candidate.start_utc,
                candidate.end_utc - pd.Timedelta(nanoseconds=1),
                periods=candidate.paired_unit_count,
            ),
            delta_snr_values,
        ):
            reference_snr_db = -20.0
            rows.append(
                {
                    "peer_sign": candidate.station_identity.callsign,
                    "peer_grid": candidate.station_identity.locator,
                    "evidence_utc": evidence_utc,
                    "outcome": "joint",
                    "paired_eligible": True,
                    "target_snr_db": reference_snr_db + delta_snr_db,
                    "reference_snr_db": reference_snr_db,
                    "metric": delta_snr_db,
                }
            )
    return pd.DataFrame(rows)


def _export_tables(model, comparison_units):
    """Build the report view model once, then project both export tables."""
    report_view_model = build_delta_snr_outlier_report_view_model(
        model,
        comparison_units,
    )
    return build_delta_snr_outlier_export_tables(
        model,
        report_view_model,

    )


def _empty_model(*, populated, evaluable, abstained):
    """Build one enabled detector result without qualified candidates."""
    return DeltaSnrOutlierModel(
        detector_version=DELTA_SNR_OUTLIER_DETECTOR_VERSION,
        detection_resolution=DELTA_SNR_OUTLIER_DETECTION_RESOLUTION,
        paired_unit_cadence_minutes=2.0,
        analysis_start_utc=pd.Timestamp("2021-05-01T00:00:00Z"),
        analysis_end_utc=pd.Timestamp("2021-05-02T00:00:00Z"),
        populated_station_cycle_count=populated,
        evaluable_station_cycle_count=evaluable,
        abstained_station_cycle_count=abstained,
        candidates=(),
        report_entries=(),
        candidate_signature="empty-status-signature",
    )


def _header_only_tables():
    """Return both fixed export schemas without inventing finding rows."""
    return DeltaSnrOutlierExportTables(
        event_paths=pd.DataFrame(columns=OUTLIER_EVENT_PATH_COLUMNS),
        paired_evidence=pd.DataFrame(columns=OUTLIER_PAIRED_EVIDENCE_COLUMNS),
    )


def test_tables_are_readable_joinable_and_keep_only_path_class_in_evidence():
    """Duplicate human context while avoiding the redundant combined class."""
    burst_times = (
        "2021-06-03T03:38:00Z",
        "2021-06-03T03:40:00Z",
        "2021-06-03T03:42:00Z",
    )
    sustained_times = (
        "2021-06-03T03:40:00Z",
        "2021-06-03T04:10:00Z",
        "2021-06-03T04:40:00Z",
    )
    burst = _candidate(
        "DC0DX",
        "JO31LK",
        burst_times,
        (8.0, 6.0, 9.0),
        event_kind="short_burst",
        direction="ENE",
    )
    sustained = _candidate(
        "PA0O",
        "JO33HG",
        sustained_times,
        (9.0, 6.0, 8.0),
        event_kind="sustained_excursion",
        direction="NNE",
    )
    entry = _report_entry(
        burst,
        sustained,
        event_kind="mixed_duration",
        scope="directionally_coherent",
    )

    tables = _export_tables(
        _model(entry),
        _comparison_units(
            (burst, (8.0, 6.0, 9.0)),
            (sustained, (9.0, 6.0, 8.0)),
        ),

    )

    assert tuple(tables.event_paths.columns) == OUTLIER_EVENT_PATH_COLUMNS
    assert tuple(tables.paired_evidence.columns) == (
        OUTLIER_PAIRED_EVIDENCE_COLUMNS
    )
    assert tables.event_paths["event_id"].tolist() == ["E0001", "E0001"]
    assert tables.event_paths["path_event_id"].tolist() == [
        "E0001-P01-01",
        "E0001-P02-01",
    ]
    assert tables.event_paths["combined_event_class"].tolist() == [
        "mixed_duration",
        "mixed_duration",
    ]
    assert tables.event_paths["path_event_class"].tolist() == [
        "short_burst",
        "sustained_excursion",
    ]
    assert tables.event_paths["cross_path_context"].unique().tolist() == [
        "directionally_coherent"
    ]
    assert tables.event_paths["paired_unit_type"].unique().tolist() == [
        OUTLIER_EXPORT_JOINT_SPOT
    ]
    assert "combined_event_class" not in tables.paired_evidence.columns
    assert tables.paired_evidence["path"].unique().tolist() == [
        "DC0DX (JO31LK)",
        "PA0O (JO33HG)",
    ]
    assert tables.paired_evidence["direction"].unique().tolist() == [
        "ENE",
        "NNE",
    ]
    assert tables.paired_evidence["path_event_class"].unique().tolist() == [
        "short_burst",
        "sustained_excursion",
    ]
    assert set(tables.paired_evidence["path_event_id"]) == {
        "E0001-P01-01",
        "E0001-P02-01",
    }


def test_cycle_scores_strong_gates_and_inclusive_boundaries_are_exact():
    """Export exact detector math and distinguish retained weak interior rows."""
    evidence_times = (
        "2021-05-09T01:40:00Z",
        "2021-05-09T01:58:00Z",
        "2021-05-09T02:20:00Z",
    )
    delta_snr_values = (8.0, 6.0, 9.0)
    candidate = _candidate(
        "PA0O",
        "JO33HG",
        evidence_times,
        delta_snr_values,
        baseline_db=5.0,
        robust_spread_db=0.5,
    )
    entry = _report_entry(candidate)

    comparison_units = _comparison_units((candidate, delta_snr_values))
    comparison_units.loc[1, "evidence_utc"] = pd.Timestamp(evidence_times[1])
    tables = _export_tables(
        _model(entry),
        comparison_units,

    )

    summary = tables.event_paths.iloc[0]
    assert summary["event_first_evidence_utc"] == "2021-05-09T01:40:00Z"
    assert summary["event_last_evidence_utc"] == "2021-05-09T02:20:00Z"
    assert summary["path_first_evidence_utc"] == "2021-05-09T01:40:00Z"
    assert summary["path_last_evidence_utc"] == "2021-05-09T02:20:00Z"
    assert summary["paired_unit_type"] == OUTLIER_EXPORT_JOINT_SPOT
    assert summary["first_to_last_span_minutes"] == pytest.approx(40.0)
    assert summary["median_evidence_interval_minutes"] == pytest.approx(20.0)
    assert summary["largest_gap_minutes"] == pytest.approx(22.0)
    assert summary["absolute_pre_post_baseline_difference_db"] == (
        pytest.approx(0.6)
    )

    evidence = tables.paired_evidence
    assert evidence["utc"].tolist() == [
        "2021-05-09T01:40:00Z",
        "2021-05-09T01:58:00Z",
        "2021-05-09T02:20:00Z",
    ]
    assert evidence["departure_from_local_baseline_db"].tolist() == [
        3.0,
        1.0,
        4.0,
    ]
    assert evidence["cycle_robust_z_score"].tolist() == pytest.approx(
        [4.047, 1.349, 5.396]
    )
    assert evidence["meets_strong_anchor_gates"].tolist() == [True, False, True]
    assert evidence["reported_boundary"].tolist() == ["start", "", "end"]
    assert evidence["target_snr_db"].tolist() == [-12.0, -14.0, -11.0]
    assert evidence["corrected_reference_snr_db"].tolist() == [
        -20.0,
        -20.0,
        -20.0,
    ]


@pytest.mark.parametrize("departure_sign", [1.0, -1.0])
def test_tolerant_departure_export_matches_native_qualifying_units_without_rounding(
    departure_sign,

):
    """Keep raw dB values while exporting the detector's inclusive 0.01 dB gate."""
    anchor_utc = pd.Timestamp("2021-05-09T12:00:00Z")
    event_values = [
        departure_sign * value for value in (6.25, 5.995, 5.989, 5.99, 6.25)
    ]
    event_times = [anchor_utc + pd.Timedelta(minutes=2 * index) for index in range(5)]
    points = [
        (offset_minutes, 0.0)
        for offset_minutes in (-300, -270, -240, -210, -180, -150, -120, -90)
    ]
    points.extend((2 * index, value) for index, value in enumerate(event_values))
    points.extend(
        (offset_minutes, 0.0)
        for offset_minutes in (90, 120, 150, 180, 210, 240, 270, 300)
    )
    comparison_units = pd.DataFrame(
        [
            {
                "peer_sign": "PA0O",
                "peer_grid": "JO33HG",
                "evidence_utc": anchor_utc + pd.Timedelta(minutes=offset_minutes),
                "outcome": "joint",
                "paired_eligible": True,
                "target_snr_db": -20.0 + delta_snr_db,
                "reference_snr_db": -20.0,
                "metric": delta_snr_db,
            }
            for offset_minutes, delta_snr_db in points
        ]
    )
    original_units = comparison_units.copy(deep=True)
    policy = DeltaSnrOutlierDetectionPolicy(
        minimum_departure_db=6.0,
        minimum_robust_z=3.0,
        maximum_baseline_difference_db=3.0,
    )
    model = detect_delta_snr_outlier_candidates(
        comparison_units,
        analysis_start_utc=anchor_utc - pd.Timedelta(hours=8),
        analysis_end_utc=anchor_utc + pd.Timedelta(hours=8),
        paired_unit_cadence_minutes=2.0,
        detection_policy=policy,
    )

    assert len(model.candidates) == 1
    candidate = model.candidates[0]
    assert candidate.paired_unit_count == 5
    expected_qualifying_times = [event_times[index] for index in (0, 1, 3, 4)]
    assert [unit.evidence_utc for unit in candidate.qualifying_units] == (
        expected_qualifying_times
    )
    qualifying_recipe = model.qualifying_unit_marker_recipe()
    assert qualifying_recipe is not None
    assert qualifying_recipe["detector_version"] == "native-residual-episode-v8"
    assert qualifying_recipe["qualifying_unit_count"] == 4
    assert model.cache_token[0] == "native-residual-episode-v8"

    tables = _export_tables(model, comparison_units)
    evidence = tables.paired_evidence
    assert evidence["meets_strong_anchor_gates"].tolist() == [
        True, True, False, True, True
    ]
    assert pd.to_datetime(
        evidence.loc[evidence["meets_strong_anchor_gates"], "utc"],
        utc=True,
    ).tolist() == expected_qualifying_times
    assert evidence["delta_snr_db"].tolist() == event_values
    assert evidence["departure_from_local_baseline_db"].tolist() == event_values
    assert evidence["target_snr_db"].tolist() == [
        -20.0 + value for value in event_values
    ]
    assert evidence["corrected_reference_snr_db"].tolist() == [-20.0] * 5
    assert evidence["cycle_robust_z_score"].tolist() == [
        0.6745 * value / 0.5 for value in event_values
    ]
    assert tables.event_paths.iloc[0]["observed_median_delta_snr_db"] == (
        departure_sign * 5.995
    )
    assert evidence["paired_unit_type"].unique().tolist() == [
        OUTLIER_EXPORT_JOINT_SPOT
    ]
    assert tuple(tables.event_paths.columns) == OUTLIER_EVENT_PATH_COLUMNS
    assert tuple(evidence.columns) == OUTLIER_PAIRED_EVIDENCE_COLUMNS
    assert policy.signature_tuple == (6.0, 3.0, 3.0)
    assert policy.as_dict() == {
        "minimum_departure_db": 6.0,
        "minimum_robust_z": 3.0,
        "maximum_baseline_difference_db": 3.0,
    }
    metadata = build_delta_snr_outlier_export_metadata(model, tables)
    assert metadata["schema_version"] == 1
    assert metadata["result_status"] == "candidates"
    assert metadata["paired_evidence_row_count"] == 5
    pd.testing.assert_frame_equal(comparison_units, original_units)


@pytest.mark.parametrize("departure_sign", [1.0, -1.0])
def test_departure_tolerance_does_not_relax_export_robust_z_gate(departure_sign):
    """A tolerated dB departure still fails a robust-z score below its gate."""
    delta_snr_values = tuple(departure_sign * value for value in (8.0, 5.995, 8.0))
    candidate = _candidate(
        "PA0O",
        "JO33HG",
        (
            "2021-05-09T01:40:00Z",
            "2021-05-09T01:42:00Z",
            "2021-05-09T01:44:00Z",
        ),
        delta_snr_values,
        baseline_db=0.0,
        robust_spread_db=0.6745 * 5.995 / 2.995,
    )
    policy = DeltaSnrOutlierDetectionPolicy(
        minimum_departure_db=6.0,
        minimum_robust_z=3.0,
        maximum_baseline_difference_db=3.0,
    )
    model = replace(_model(_report_entry(candidate)), detection_policy=policy)
    tables = _export_tables(
        model,
        _comparison_units((candidate, delta_snr_values)),

    )

    evidence = tables.paired_evidence
    assert evidence["meets_strong_anchor_gates"].tolist() == [True, False, True]
    assert evidence.iloc[1]["cycle_robust_z_score"] == pytest.approx(
        departure_sign * 2.995
    )
    assert evidence["delta_snr_db"].tolist() == list(delta_snr_values)
    assert evidence["departure_from_local_baseline_db"].tolist() == list(
        delta_snr_values
    )


def test_impulse_is_one_joint_spot_with_start_and_end_boundary():
    """Represent one-unit evidence without inventing an interval or second row."""
    candidate = _candidate(
        "DC0DX",
        "JO31LK",
        ("2021-06-03T03:38:00Z",),
        (10.0,),
        event_kind="spot_impulse",
        direction="ENE",
    )
    tables = _export_tables(
        _model(_report_entry(candidate)),
        _comparison_units((candidate, (10.0,))),

    )

    assert tables.event_paths.iloc[0]["median_evidence_interval_minutes"] is None
    assert tables.event_paths.iloc[0]["largest_gap_minutes"] is None
    assert tables.paired_evidence.iloc[0]["reported_boundary"] == "start_and_end"
    assert tables.paired_evidence.iloc[0]["paired_unit_type"] == "joint_spot"


def test_event_ids_follow_chronology_not_supplied_tuple_order():
    """Keep package-local joins stable when caller entry order differs."""
    early = _candidate(
        "A1AAA",
        "AA00",
        ("2021-05-01T01:00:00Z",),
        (10.0,),
        event_kind="spot_impulse",
    )
    late = _candidate(
        "B2BBB",
        "BB11",
        ("2021-05-02T01:00:00Z",),
        (10.0,),
        event_kind="spot_impulse",
    )
    late_entry = _report_entry(late, episode_index=2)
    early_entry = _report_entry(early, episode_index=1)

    tables = _export_tables(
        _model(late_entry, early_entry),
        _comparison_units((early, (10.0,)), (late, (10.0,))),

    )

    assert tables.event_paths[["event_id", "callsign"]].values.tolist() == [
        ["E0001", "A1AAA"],
        ["E0002", "B2BBB"],
    ]


def test_repeated_same_path_intervals_receive_stable_occurrence_ids():
    """Keep distinct intervals on one path joinable without inventing paths."""
    first = _candidate(
        "PA0O",
        "JO33HG",
        ("2021-05-09T01:00:00Z", "2021-05-09T01:02:00Z"),
        (8.0, 9.0),
        event_kind="short_burst",
    )
    second = _candidate(
        "PA0O",
        "JO33HG",
        ("2021-05-09T01:20:00Z", "2021-05-09T01:22:00Z"),
        (9.0, 8.0),
        event_kind="short_burst",
    )
    entry = _report_entry(first, second, scope="path_specific")

    tables = _export_tables(
        _model(entry),
        _comparison_units((first, (8.0, 9.0)), (second, (9.0, 8.0))),

    )

    assert tables.event_paths["qualifying_path_count"].tolist() == [1, 1]
    assert tables.event_paths["path_number"].tolist() == [1, 1]
    assert tables.event_paths["path_occurrence"].tolist() == [1, 2]
    assert tables.event_paths["path_event_id"].tolist() == [
        "E0001-P01-01",
        "E0001-P01-02",
    ]
    assert tables.paired_evidence.groupby("path_event_id").size().to_dict() == {
        "E0001-P01-01": 2,
        "E0001-P01-02": 2,
    }
    assert tables.paired_evidence["event_first_evidence_utc"].unique().tolist() == [
        "2021-05-09T01:00:00Z"
    ]
    assert tables.paired_evidence["event_last_evidence_utc"].unique().tolist() == [
        "2021-05-09T01:22:00Z"
    ]


def test_empty_detector_model_keeps_both_csv_schemas():
    """Allow enabled no-finding exports to contain header-only CSV tables."""
    model = DeltaSnrOutlierModel(
        detector_version=DELTA_SNR_OUTLIER_DETECTOR_VERSION,
        detection_resolution=DELTA_SNR_OUTLIER_DETECTION_RESOLUTION,
        paired_unit_cadence_minutes=2.0,
        analysis_start_utc=pd.Timestamp("2021-05-01T00:00:00Z"),
        analysis_end_utc=pd.Timestamp("2021-05-02T00:00:00Z"),
        populated_station_cycle_count=0,
        evaluable_station_cycle_count=0,
        abstained_station_cycle_count=0,
        candidates=(),
        report_entries=(),
        candidate_signature="empty",
    )

    tables = _export_tables(
        model,
        pd.DataFrame(),

    )

    assert tables.event_paths.empty
    assert tables.paired_evidence.empty
    assert tuple(tables.event_paths.columns) == OUTLIER_EVENT_PATH_COLUMNS
    assert tuple(tables.paired_evidence.columns) == (
        OUTLIER_PAIRED_EVIDENCE_COLUMNS
    )


def test_missing_candidate_evidence_fails_instead_of_exporting_partial_trace():
    """Reject a summary/evidence mismatch rather than silently losing cycles."""
    candidate = _candidate(
        "PA0O",
        "JO33HG",
        ("2021-05-09T01:40:00Z", "2021-05-09T01:42:00Z"),
        (8.0, 9.0),
    )

    with pytest.raises(ValueError, match="bounds|paired-unit count"):
        _export_tables(
            _model(_report_entry(candidate)),
            _comparison_units((candidate, (8.0,))).iloc[:1],

        )


def test_candidate_metadata_reports_schema_filenames_and_all_counts():
    """Describe populated tables once without repeating metadata in CSV rows."""
    first = _candidate(
        "PA0O",
        "JO33HG",
        ("2021-05-09T01:00:00Z", "2021-05-09T01:02:00Z"),
        (8.0, 9.0),
    )
    second = _candidate(
        "PA0O",
        "JO33HG",
        ("2021-05-09T01:20:00Z", "2021-05-09T01:22:00Z"),
        (9.0, 8.0),
    )
    third = _candidate(
        "DC0DX",
        "JO31LK",
        ("2021-05-09T01:20:00Z",),
        (10.0,),
        event_kind="spot_impulse",
    )
    first_entry = _report_entry(first, second, scope="path_specific")
    second_entry = _report_entry(third, episode_index=1)
    model = _model(first_entry, second_entry)
    model = DeltaSnrOutlierModel(
        **{
            **model.__dict__,
            "populated_station_cycle_count": 12,
            "evaluable_station_cycle_count": 9,
            "abstained_station_cycle_count": 3,
            "candidate_signature": "candidate-metadata-signature",
        }
    )
    tables = _export_tables(
        model,
        _comparison_units(
            (first, (8.0, 9.0)),
            (second, (9.0, 8.0)),
            (third, (10.0,)),
        ),

    )

    metadata = build_delta_snr_outlier_export_metadata(model, tables)

    assert metadata == {
        "schema_version": DELTA_SNR_OUTLIER_EXPORT_SCHEMA_VERSION,
        "result_status": "candidates",
        "candidate_signature": "candidate-metadata-signature",
        "detection_resolution": DELTA_SNR_OUTLIER_DETECTION_RESOLUTION,
        "event_count": 2,
        "path_event_count": 3,
        "unique_qualifying_path_count": 2,
        "paired_evidence_row_count": 5,
        "populated_paired_unit_count": 12,
        "evaluable_paired_unit_count": 9,
        "abstained_paired_unit_count": 3,
        "tables": {
            "event_paths": OUTLIER_EVENT_PATHS_TABLE_FILENAME,
            "paired_evidence": OUTLIER_PAIRED_EVIDENCE_TABLE_FILENAME,
        },
    }


@pytest.mark.parametrize(
    ("populated", "evaluable", "abstained", "expected_status"),
    [
        (0, 0, 0, "insufficient_paired_evidence"),
        (8, 0, 8, "insufficient_local_baseline"),
        (8, 5, 3, "no_candidates"),
    ],
)
def test_header_only_metadata_preserves_enabled_empty_result_status(
    populated,
    evaluable,
    abstained,
    expected_status,
):
    """Distinguish three no-finding states without writing synthetic rows."""
    model = _empty_model(
        populated=populated,
        evaluable=evaluable,
        abstained=abstained,
    )

    metadata = build_delta_snr_outlier_export_metadata(
        model,
        _header_only_tables(),
    )

    assert metadata["result_status"] == expected_status
    assert metadata["event_count"] == 0
    assert metadata["path_event_count"] == 0
    assert metadata["unique_qualifying_path_count"] == 0
    assert metadata["paired_evidence_row_count"] == 0
    assert metadata["tables"] == {
        "event_paths": OUTLIER_EVENT_PATHS_TABLE_FILENAME,
        "paired_evidence": OUTLIER_PAIRED_EVIDENCE_TABLE_FILENAME,
    }


def test_metadata_rejects_unvalidated_table_container_and_schemas():
    """Reject missing table ownership and either fixed-schema mismatch."""
    model = _empty_model(populated=0, evaluable=0, abstained=0)

    with pytest.raises(TypeError, match="validated tables"):
        build_delta_snr_outlier_export_metadata(model, object())

    invalid_event_paths = _header_only_tables()
    invalid_event_paths.event_paths["unexpected"] = pd.Series(dtype="object")
    with pytest.raises(ValueError, match="event-path export columns"):
        build_delta_snr_outlier_export_metadata(model, invalid_event_paths)

    invalid_paired_evidence = _header_only_tables()
    invalid_paired_evidence.paired_evidence["unexpected"] = pd.Series(
        dtype="object"
    )
    with pytest.raises(ValueError, match="paired-evidence export columns"):
        build_delta_snr_outlier_export_metadata(model, invalid_paired_evidence)


def test_metadata_rejects_path_event_and_paired_evidence_count_mismatches():
    """Keep model counts inseparable from both exported table row counts."""
    candidate = _candidate(
        "PA0O",
        "JO33HG",
        ("2021-05-09T01:40:00Z", "2021-05-09T01:42:00Z"),
        (8.0, 9.0),
    )
    model = _model(_report_entry(candidate))
    tables = _export_tables(
        model,
        _comparison_units((candidate, (8.0, 9.0))),

    )

    missing_path_event = DeltaSnrOutlierExportTables(
        event_paths=tables.event_paths.iloc[0:0].copy(),
        paired_evidence=tables.paired_evidence.copy(),
    )
    with pytest.raises(ValueError, match="qualified path events"):
        build_delta_snr_outlier_export_metadata(model, missing_path_event)

    missing_paired_evidence = DeltaSnrOutlierExportTables(
        event_paths=tables.event_paths.copy(),
        paired_evidence=tables.paired_evidence.iloc[:-1].copy(),
    )
    with pytest.raises(ValueError, match="qualified event units"):
        build_delta_snr_outlier_export_metadata(model, missing_paired_evidence)
