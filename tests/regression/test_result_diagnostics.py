import pytest

from core.result_diagnostics import (
    NO_TARGET_MODE_EVIDENCE,
    PERFORMANCE_NO_ELIGIBLE_STATION,
    PERFORMANCE_NO_QUALIFYING_SEGMENT,
    ResultDiagnostic,
)


@pytest.mark.parametrize("source_row_count", [0, 10])
def test_no_target_mode_diagnostic_round_trips_empty_or_supporting_rows(source_row_count):
    diagnostic = ResultDiagnostic.create(
        NO_TARGET_MODE_EVIDENCE,
        measured_counts={"source_row_count": source_row_count},
    )
    assert ResultDiagnostic.from_dict(diagnostic.to_dict()) == diagnostic


def test_no_target_mode_diagnostic_requires_a_measured_source_count():
    with pytest.raises(ValueError, match="source_row_count"):
        ResultDiagnostic.create(NO_TARGET_MODE_EVIDENCE)


def test_result_diagnostic_round_trip_preserves_applied_thresholds_and_counts():
    diagnostic = ResultDiagnostic.create(
        PERFORMANCE_NO_ELIGIBLE_STATION,
        applied_thresholds={
            "min_confirmed_opportunities_per_peer": 5,
            "min_joint_stations_per_map_segment": 2,
        },
        measured_counts={
            "station_identity_count": 8,
            "eligible_station_count": 0,
            "maximum_confirmed_opportunities_per_station": 3,
        },
    )

    assert ResultDiagnostic.from_dict(diagnostic.to_dict()) == diagnostic


def test_no_eligible_diagnostic_rejects_missing_applied_minimum():
    with pytest.raises(ValueError, match="confirmed-opportunity threshold"):
        ResultDiagnostic.create(
            PERFORMANCE_NO_ELIGIBLE_STATION,
            measured_counts={
                "station_identity_count": 8,
                "eligible_station_count": 0,
                "maximum_confirmed_opportunities_per_station": 3,
            },
        )


def test_no_segment_diagnostic_rejects_a_maximum_that_meets_the_minimum():
    with pytest.raises(ValueError, match="maximum must be below"):
        ResultDiagnostic.create(
            PERFORMANCE_NO_QUALIFYING_SEGMENT,
            applied_thresholds={
                "min_confirmed_opportunities_per_peer": 5,
                "min_joint_stations_per_map_segment": 2,
            },
            measured_counts={
                "eligible_station_count": 3,
                "qualifying_segment_count": 0,
                "maximum_stations_per_segment": 2,
            },
        )
