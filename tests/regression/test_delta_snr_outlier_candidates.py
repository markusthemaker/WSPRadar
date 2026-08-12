"""Regression contracts for native Delta-SNR episode-candidate detection."""

from dataclasses import FrozenInstanceError
import inspect

import numpy as np
import pandas as pd
import pandas.testing as pdt
import pytest

from config.delta_snr_outlier import (
    DEFAULT_DELTA_SNR_OUTLIER_DETECTION_POLICY,
    DELTA_SNR_OUTLIER_CONFIG_FIELD_TO_POLICY_FIELD,
    DELTA_SNR_OUTLIER_MAXIMUM_THRESHOLD,
    DELTA_SNR_OUTLIER_MINIMUM_THRESHOLD,
    DeltaSnrOutlierDetectionPolicy,
)
from ui.inspector import outlier_candidates


WALTER_IMPULSE_UTC = pd.Timestamp("2021-06-01T18:38:00Z")
WALTER_SECOND_IMPULSE_UTC = pd.Timestamp("2021-06-03T03:38:00Z")
ANALYSIS_START = WALTER_IMPULSE_UTC - pd.Timedelta(hours=8)
ANALYSIS_END = WALTER_IMPULSE_UTC + pd.Timedelta(hours=8)
DEFAULT_PRE_OFFSETS_MINUTES = (-300, -270, -240, -210, -180, -150, -120, -90)
DEFAULT_POST_OFFSETS_MINUTES = (90, 120, 150, 180, 210, 240, 270, 300)


def _path_units(
    callsign="DC0DX",
    locator="JO31LK",
    *,
    event_points=((0, 8.0),),
    anchor_utc=WALTER_IMPULSE_UTC,
    pre_offsets_minutes=DEFAULT_PRE_OFFSETS_MINUTES,
    post_offsets_minutes=DEFAULT_POST_OFFSETS_MINUTES,
    pre_baseline_db=3.0,
    post_baseline_db=None,
    identity_order=0,
    component_values_by_offset=None,
):
    """Build one path with supported flanks and native event observations."""
    post_baseline = (
        pre_baseline_db if post_baseline_db is None else post_baseline_db
    )
    component_values_by_offset = component_values_by_offset or {}
    rows = []

    def append_row(offset_minutes, delta_snr_db):
        target_snr_db, reference_snr_db = component_values_by_offset.get(
            offset_minutes,
            (-20.0, -20.0 - float(delta_snr_db)),
        )
        rows.append(
            {
                "peer_sign": callsign,
                "peer_grid": locator,
                "identity_order": identity_order,
                "evidence_utc": anchor_utc
                + pd.Timedelta(minutes=offset_minutes),
                "outcome": "joint",
                "metric": float(delta_snr_db),
                "paired_eligible": True,
                "target_snr_db": target_snr_db,
                "reference_snr_db": reference_snr_db,
            }
        )

    for offset_minutes in pre_offsets_minutes:
        append_row(offset_minutes, pre_baseline_db)
    for offset_minutes, delta_snr_db in event_points:
        append_row(offset_minutes, delta_snr_db)
    for offset_minutes in post_offsets_minutes:
        append_row(offset_minutes, post_baseline)
    return pd.DataFrame(rows)


def _one_sided_unit(
    outcome,
    *,
    offset_minutes=2,
    anchor_utc=WALTER_IMPULSE_UTC,
    callsign="DC0DX",
    locator="JO31LK",
    paired_eligible=True,
):
    """Build one retained one-sided comparison unit near a path episode."""
    if outcome not in {"target_only", "reference_only"}:
        raise ValueError("outcome must be target_only or reference_only")
    return pd.DataFrame(
        [
            {
                "peer_sign": callsign,
                "peer_grid": locator,
                "identity_order": 0,
                "evidence_utc": anchor_utc
                + pd.Timedelta(minutes=offset_minutes),
                "outcome": outcome,
                "metric": np.nan,
                "paired_eligible": paired_eligible,
                "target_snr_db": (
                    -18.0 if outcome == "target_only" else np.nan
                ),
                "reference_snr_db": (
                    -18.0 if outcome == "reference_only" else np.nan
                ),
            }
        ]
    )


def _detect(
    comparison_units,
    station_directions=None,
    *,
    analysis_start=ANALYSIS_START,
    analysis_end=ANALYSIS_END,
    cadence_minutes=2.0,
    detection_policy=DEFAULT_DELTA_SNR_OUTLIER_DETECTION_POLICY,
):
    """Run the native detector with one explicit cadence and UTC window."""
    return outlier_candidates.detect_delta_snr_outlier_candidates(
        comparison_units,
        analysis_start_utc=analysis_start,
        analysis_end_utc=analysis_end,
        station_directions=station_directions,
        paired_unit_cadence_minutes=cadence_minutes,
        detection_policy=detection_policy,
    )


def test_disabled_preparation_returns_before_detector_or_frame_access(monkeypatch):
    """Keep the optional presentation feature free when its toggle is off."""
    def fail_detector(*args, **kwargs):
        raise AssertionError("disabled outlier reporting called the detector")

    monkeypatch.setattr(
        outlier_candidates,
        "detect_delta_snr_outlier_candidates",
        fail_detector,
    )

    class PoisonPolicy:
        def __getattribute__(self, name):
            raise AssertionError(f"disabled preparation read policy field {name}")

    assert outlier_candidates.prepare_delta_snr_outlier_model(
        False,
        object(),
        analysis_start_utc=object(),
        analysis_end_utc=object(),
        detection_policy=PoisonPolicy(),
    ) is None


def test_default_detection_policy_is_immutable_named_and_stable():
    """Expose one dependency-light default policy for config and detector use."""
    policy = DEFAULT_DELTA_SNR_OUTLIER_DETECTION_POLICY

    assert policy.signature_tuple == (3.0, 4.0, 3.0)
    assert policy.as_dict() == {
        "minimum_departure_db": 3.0,
        "minimum_robust_z": 4.0,
        "maximum_baseline_difference_db": 3.0,
    }
    assert DELTA_SNR_OUTLIER_CONFIG_FIELD_TO_POLICY_FIELD == (
        (
            "delta_snr_outlier_minimum_departure_db",
            "minimum_departure_db",
        ),
        (
            "delta_snr_outlier_minimum_robust_z",
            "minimum_robust_z",
        ),
        (
            "delta_snr_outlier_maximum_baseline_difference_db",
            "maximum_baseline_difference_db",
        ),
    )
    assert tuple(DeltaSnrOutlierDetectionPolicy.__dataclass_fields__) == (
        "minimum_departure_db",
        "minimum_robust_z",
        "maximum_baseline_difference_db",
    )
    with pytest.raises(FrozenInstanceError):
        policy.minimum_departure_db = 6.0


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    (
        ("minimum_departure_db", 0.0),
        ("minimum_departure_db", -1.0),
        ("minimum_departure_db", np.nan),
        ("minimum_robust_z", np.inf),
        ("minimum_robust_z", "4.0"),
        ("minimum_robust_z", True),
        ("maximum_baseline_difference_db", -np.inf),
    ),
)
def test_detection_policy_rejects_non_positive_non_finite_or_non_numeric_values(
    field_name,
    invalid_value,
):
    """Reject invalid scientific thresholds at policy construction."""
    with pytest.raises(ValueError, match=field_name):
        DeltaSnrOutlierDetectionPolicy(**{field_name: invalid_value})


def test_detection_policy_preserves_precision_at_inclusive_central_bounds():
    """Accept exact shared bounds without rounding policy values."""
    minimum_policy = DeltaSnrOutlierDetectionPolicy(
        **{
            policy_field: DELTA_SNR_OUTLIER_MINIMUM_THRESHOLD
            for _config_field, policy_field in (
                DELTA_SNR_OUTLIER_CONFIG_FIELD_TO_POLICY_FIELD
            )
        }
    )
    maximum_policy = DeltaSnrOutlierDetectionPolicy(
        **{
            policy_field: DELTA_SNR_OUTLIER_MAXIMUM_THRESHOLD
            for _config_field, policy_field in (
                DELTA_SNR_OUTLIER_CONFIG_FIELD_TO_POLICY_FIELD
            )
        }
    )

    assert minimum_policy.signature_tuple == (0.1,) * 3
    assert maximum_policy.signature_tuple == (100.0,) * 3
    with pytest.raises(ValueError, match="minimum_departure_db"):
        DeltaSnrOutlierDetectionPolicy(minimum_departure_db=0.099)
    with pytest.raises(ValueError, match="minimum_robust_z"):
        DeltaSnrOutlierDetectionPolicy(minimum_robust_z=100.001)


@pytest.mark.parametrize(
    "legacy_field_name",
    (
        "spot_minimum_departure_db",
        "burst_minimum_departure_db",
        "sustained_minimum_departure_db",
        "spot_minimum_robust_z",
        "burst_minimum_robust_z",
        "sustained_minimum_robust_z",
    ),
)
def test_detection_policy_rejects_duration_specific_gate_fields(
    legacy_field_name,
):
    """Keep duration classes descriptive instead of policy dimensions."""
    with pytest.raises(TypeError, match="unexpected keyword argument"):
        DeltaSnrOutlierDetectionPolicy(**{legacy_field_name: 3.0})


def test_enabled_detector_requires_a_validated_detection_policy_object():
    """Do not interpret arbitrary mappings inside the scientific detector."""
    with pytest.raises(TypeError, match="DeltaSnrOutlierDetectionPolicy"):
        _detect(_path_units(), detection_policy={})


def test_detector_api_owns_native_resolution_independent_of_display_bins():
    """Do not let a selected plot aggregation redefine event detection."""
    detector_parameters = inspect.signature(
        outlier_candidates.detect_delta_snr_outlier_candidates
    ).parameters
    preparation_parameters = inspect.signature(
        outlier_candidates.prepare_delta_snr_outlier_model
    ).parameters

    assert "time_bin" not in detector_parameters
    assert "time_bin" not in preparation_parameters
    assert "paired_unit_cadence_minutes" in detector_parameters
    assert "detection_policy" in detector_parameters
    assert "detection_policy" in preparation_parameters

    model = _detect(_path_units())

    assert model.detection_resolution == (
        outlier_candidates.DELTA_SNR_OUTLIER_DETECTION_RESOLUTION
    )
    assert outlier_candidates.DELTA_SNR_OUTLIER_DETECTOR_VERSION == (
        "native-residual-episode-v7"
    )
    assert model.detection_resolution == "native-paired-unit"
    assert model.paired_unit_cadence_minutes == pytest.approx(2.0)
    assert model.detection_policy is DEFAULT_DELTA_SNR_OUTLIER_DETECTION_POLICY
    assert model.cache_token[:2] == (
        outlier_candidates.DELTA_SNR_OUTLIER_DETECTOR_VERSION,
        outlier_candidates.DELTA_SNR_OUTLIER_DETECTION_RESOLUTION,
    )


def test_duration_classification_is_descriptive_only():
    """Classify grouped duration without selecting qualification thresholds."""
    assert outlier_candidates._classify_episode(1, 0.0) == (
        outlier_candidates.OUTLIER_EVENT_SPOT_IMPULSE
    )
    assert outlier_candidates._classify_episode(3, 8.0) == (
        outlier_candidates.OUTLIER_EVENT_SHORT_BURST
    )
    assert outlier_candidates._classify_episode(3, 30.0) == (
        outlier_candidates.OUTLIER_EVENT_SUSTAINED_EXCURSION
    )


def test_shared_policy_applies_the_same_hard_gates_to_every_duration_class():
    """Do not weaken departure or robust-score gates for longer episodes."""
    cases = (
        (
            _path_units(event_points=((0, 6.2),)),
            outlier_candidates.OUTLIER_EVENT_SPOT_IMPULSE,
        ),
        (
            _path_units(event_points=((0, 6.2), (4, 6.2), (8, 6.2))),
            outlier_candidates.OUTLIER_EVENT_SHORT_BURST,
        ),
        (
            _path_units(
                event_points=tuple((offset, 6.2) for offset in range(0, 51, 10))
            ),
            outlier_candidates.OUTLIER_EVENT_SUSTAINED_EXCURSION,
        ),
    )
    strict_policy = DeltaSnrOutlierDetectionPolicy(
        minimum_departure_db=3.3,
        minimum_robust_z=4.0,
    )

    for comparison_units, expected_event_kind in cases:
        candidates = _detect(comparison_units).candidates
        assert len(candidates) == 1
        assert candidates[0].event_kind == expected_event_kind
        assert candidates[0].median_anomaly_db == pytest.approx(3.2)
        assert _detect(
            comparison_units,
            detection_policy=strict_policy,
        ).candidates == ()


def test_sub_one_db_shared_policy_can_seed_and_qualify_an_excursion():
    """Keep every accepted departure threshold effective during grouping."""
    comparison_units = _path_units(
        event_points=tuple((offset, 3.6) for offset in range(0, 51, 10))
    )
    sensitive_policy = DeltaSnrOutlierDetectionPolicy(
        minimum_departure_db=0.5,
        minimum_robust_z=0.5,
    )

    candidates = _detect(
        comparison_units,
        detection_policy=sensitive_policy,
    ).candidates

    assert len(candidates) == 1
    assert candidates[0].event_kind == (
        outlier_candidates.OUTLIER_EVENT_SUSTAINED_EXCURSION
    )
    assert candidates[0].median_anomaly_db == pytest.approx(0.6)


def test_custom_maximum_baseline_difference_controls_baseline_support():
    """Parameterize pre/post compatibility without weakening event gates."""
    comparison_units = _path_units(
        event_points=((0, 12.0),),
        pre_baseline_db=3.0,
        post_baseline_db=6.5,
    )

    assert _detect(comparison_units).candidates == ()
    permissive_policy = DeltaSnrOutlierDetectionPolicy(
        maximum_baseline_difference_db=4.0,
    )
    candidate = _detect(
        comparison_units,
        detection_policy=permissive_policy,
    ).candidates[0]

    assert candidate.pre_baseline_db == pytest.approx(3.0)
    assert candidate.post_baseline_db == pytest.approx(6.5)


def test_policy_changes_cache_and_marker_signatures_when_candidates_match():
    """Keep cache identity scientific even when two policies select alike."""
    comparison_units = _path_units(event_points=((0, 8.0),))
    custom_policy = DeltaSnrOutlierDetectionPolicy(
        maximum_baseline_difference_db=2.5,
    )

    default_model = _detect(comparison_units)
    custom_model = _detect(
        comparison_units,
        detection_policy=custom_policy,
    )

    assert default_model.candidates == custom_model.candidates
    assert custom_model.detection_policy is custom_policy
    assert default_model.detection_policy_signature != (
        custom_model.detection_policy_signature
    )
    assert default_model.candidate_signature != custom_model.candidate_signature
    assert default_model.cache_token != custom_model.cache_token
    default_recipe = default_model.marker_recipe()
    custom_recipe = custom_model.marker_recipe()
    assert default_recipe["schema_version"] == 3
    assert default_recipe["detection_policy_signature"] == (
        default_model.detection_policy_signature
    )
    assert default_recipe["markers"][0]["detection_policy_signature"] == (
        default_model.detection_policy_signature
    )
    assert default_recipe["candidate_signature"] != (
        custom_recipe["candidate_signature"]
    )


def test_walter_style_single_spot_impulse_uses_exact_cycle_and_components():
    """Detect the 18:38-style impulse without moving it to an hourly centre."""
    comparison_units = _path_units(
        event_points=((0, 8.0),),
        component_values_by_offset={0: (-19.0, -27.0)},
    )

    model = _detect(comparison_units)

    assert len(model.candidates) == 1
    candidate = model.candidates[0]
    assert candidate.station_identity.label == "DC0DX (JO31LK)"
    assert candidate.event_kind == outlier_candidates.OUTLIER_EVENT_SPOT_IMPULSE
    assert candidate.start_utc == WALTER_IMPULSE_UTC
    assert candidate.end_utc > candidate.start_utc
    assert candidate.representative_utc == WALTER_IMPULSE_UTC
    assert candidate.representative_delta_snr_db == pytest.approx(8.0)
    assert candidate.episode_median_delta_snr_db == pytest.approx(8.0)
    assert candidate.station_baseline_db == pytest.approx(3.0)
    assert candidate.pre_baseline_db == pytest.approx(3.0)
    assert candidate.post_baseline_db == pytest.approx(3.0)
    assert candidate.median_anomaly_db == pytest.approx(5.0)
    assert candidate.peak_anomaly_db == pytest.approx(5.0)
    assert candidate.paired_unit_count == 1
    assert candidate.agreeing_paired_unit_count == 1
    assert candidate.paired_unit_sign_agreement_fraction == pytest.approx(1.0)
    assert candidate.observed_span_minutes == pytest.approx(0.0)
    assert candidate.largest_gap_minutes == pytest.approx(0.0)
    assert candidate.path_effective_cadence_minutes == pytest.approx(30.0)
    assert candidate.maximum_episode_gap_minutes == pytest.approx(45.0)
    assert candidate.pre_flank_cell_count == 8
    assert candidate.post_flank_cell_count == 8
    assert candidate.robust_spread_method == "quantization-floor"
    assert candidate.robust_spread_db == pytest.approx(0.5)
    assert candidate.robust_z == pytest.approx(6.745)
    assert candidate.target_median_snr_db == pytest.approx(-19.0)
    assert candidate.target_baseline_db == pytest.approx(-20.0)
    assert candidate.target_anomaly_db == pytest.approx(1.0)
    assert candidate.reference_median_snr_db == pytest.approx(-27.0)
    assert candidate.reference_baseline_db == pytest.approx(-23.0)
    assert candidate.reference_anomaly_db == pytest.approx(-4.0)

    assert model.populated_station_cycle_count == len(comparison_units)
    assert 0 < model.evaluable_station_cycle_count < len(comparison_units)
    assert (
        model.evaluable_station_cycle_count
        + model.abstained_station_cycle_count
        == model.populated_station_cycle_count
    )
    assert len(model.report_entries) == 1
    assert model.report_entries[0].coherence_scope == (
        outlier_candidates.OUTLIER_SCOPE_PATH_SPECIFIC
    )

    marker_recipe = model.marker_recipe()
    assert marker_recipe["schema_version"] == 3
    assert marker_recipe["detection_resolution"] == "native-paired-unit"
    assert marker_recipe["candidate_count"] == 1
    marker = marker_recipe["markers"][0]
    assert pd.Timestamp(marker["marker_utc_ns"], unit="ns", tz="UTC") == (
        WALTER_IMPULSE_UTC
    )
    assert marker["marker_delta_snr_db"] == pytest.approx(8.0)
    assert marker["event_kind"] == "spot_impulse"


def test_walter_example_times_form_two_exact_same_path_impulses():
    """Retain both reported timestamps as separate native path episodes."""
    comparison_units = pd.concat(
        (
            _path_units(anchor_utc=WALTER_IMPULSE_UTC),
            _path_units(anchor_utc=WALTER_SECOND_IMPULSE_UTC),
        ),
        ignore_index=True,
    )

    model = _detect(
        comparison_units,
        analysis_start=pd.Timestamp("2021-05-22T19:20:00Z"),
        analysis_end=pd.Timestamp("2021-06-05T03:22:00Z"),
    )

    assert tuple(candidate.representative_utc for candidate in model.candidates) == (
        WALTER_IMPULSE_UTC,
        WALTER_SECOND_IMPULSE_UTC,
    )
    assert tuple(candidate.event_kind for candidate in model.candidates) == (
        outlier_candidates.OUTLIER_EVENT_SPOT_IMPULSE,
        outlier_candidates.OUTLIER_EVENT_SPOT_IMPULSE,
    )
    assert tuple(
        pd.Timestamp(marker["marker_utc_ns"], unit="ns", tz="UTC")
        for marker in model.marker_recipe()["markers"]
    ) == (WALTER_IMPULSE_UTC, WALTER_SECOND_IMPULSE_UTC)
    assert len(model.report_entries) == 2


def test_walter_second_sequence_resegments_and_trims_to_its_strong_anchor():
    """Keep the 03:38 peak while excluding its weaker trailing shoulder."""
    first_impulse_utc = pd.Timestamp("2021-06-03T03:06:00Z")
    comparison_units = _path_units(
        anchor_utc=first_impulse_utc,
        pre_baseline_db=1.4,
        event_points=(
            (-60, 0.4),
            (-42, 3.4),
            (0, 5.4),
            (32, 6.4),
            (44, 2.4),
            (60, 1.4),
            (78, 2.4),
        ),
        pre_offsets_minutes=tuple(range(-300, -99, 20)),
        post_offsets_minutes=tuple(range(118, 319, 20)),
    )

    model = _detect(
        comparison_units,
        analysis_start=pd.Timestamp("2021-05-22T19:20:00Z"),
        analysis_end=pd.Timestamp("2021-06-05T03:22:00Z"),
        cadence_minutes=20.0,
    )

    assert len(model.candidates) == 2
    first_candidate, second_candidate = model.candidates
    assert first_candidate.event_kind == (
        outlier_candidates.OUTLIER_EVENT_SPOT_IMPULSE
    )
    assert first_candidate.start_utc == first_impulse_utc
    assert first_candidate.representative_utc == first_impulse_utc
    assert first_candidate.paired_unit_count == 1
    assert first_candidate.station_baseline_db == pytest.approx(1.4)
    assert first_candidate.median_anomaly_db == pytest.approx(4.0)

    assert second_candidate.event_kind == (
        outlier_candidates.OUTLIER_EVENT_SPOT_IMPULSE
    )
    assert second_candidate.start_utc == WALTER_SECOND_IMPULSE_UTC
    assert second_candidate.end_utc == (
        WALTER_SECOND_IMPULSE_UTC + pd.Timedelta(nanoseconds=1)
    )
    assert second_candidate.representative_utc == WALTER_SECOND_IMPULSE_UTC
    assert second_candidate.paired_unit_count == 1
    assert second_candidate.observed_span_minutes == pytest.approx(0.0)
    assert second_candidate.largest_gap_minutes == pytest.approx(0.0)
    assert second_candidate.path_effective_cadence_minutes == pytest.approx(20.0)
    assert second_candidate.maximum_episode_gap_minutes == pytest.approx(30.0)
    assert second_candidate.station_baseline_db == pytest.approx(1.4)
    assert second_candidate.episode_median_delta_snr_db == pytest.approx(6.4)
    assert second_candidate.median_anomaly_db == pytest.approx(5.0)
    assert second_candidate.peak_anomaly_db == pytest.approx(5.0)
    assert second_candidate.robust_z == pytest.approx(6.745)


def test_positive_episode_warns_when_reference_is_missing_nearby():
    """Flag nearby Only Target as a non-causal positive decode-edge warning."""
    comparison_units = pd.concat(
        [_path_units(), _one_sided_unit("target_only")],
        ignore_index=True,
    )

    model = _detect(comparison_units)
    candidate = model.candidates[0]

    assert candidate.diagnostic_neighborhood_minutes == pytest.approx(45.0)
    assert candidate.nearby_joint_unit_count == 1
    assert candidate.nearby_target_only_unit_count == 1
    assert candidate.nearby_reference_only_unit_count == 0
    assert candidate.decode_edge_warning is True
    assert candidate.decode_edge_warning_reason == (
        outlier_candidates.OUTLIER_DECODE_EDGE_REFERENCE_MISSING_NEAR_POSITIVE_EPISODE
    )
    assert model.candidate_signature != _detect(
        _path_units()
    ).candidate_signature


def test_negative_episode_warns_when_target_is_missing_nearby():
    """Flag nearby Only Reference as a non-causal negative decode-edge warning."""
    comparison_units = pd.concat(
        [
            _path_units(event_points=((0, -2.0),)),
            _one_sided_unit("reference_only"),
        ],
        ignore_index=True,
    )

    candidate = _detect(comparison_units).candidates[0]

    assert candidate.median_anomaly_db == pytest.approx(-5.0)
    assert candidate.nearby_joint_unit_count == 1
    assert candidate.nearby_target_only_unit_count == 0
    assert candidate.nearby_reference_only_unit_count == 1
    assert candidate.decode_edge_warning is True
    assert candidate.decode_edge_warning_reason == (
        outlier_candidates.OUTLIER_DECODE_EDGE_TARGET_MISSING_NEAR_NEGATIVE_EPISODE
    )


def test_opposite_one_sided_outcome_does_not_raise_decode_edge_warning():
    """Retain nearby outcome counts without warning for the opposite sign."""
    comparison_units = pd.concat(
        [_path_units(), _one_sided_unit("reference_only")],
        ignore_index=True,
    )

    candidate = _detect(comparison_units).candidates[0]

    assert candidate.nearby_joint_unit_count == 1
    assert candidate.nearby_target_only_unit_count == 0
    assert candidate.nearby_reference_only_unit_count == 1
    assert candidate.decode_edge_warning is False
    assert candidate.decode_edge_warning_reason is None


def test_path_cadence_replaces_global_cadence_for_outcome_diagnostics():
    """Use observed path cadence rather than the detector's fallback cadence."""
    comparison_units = pd.concat(
        [
            _path_units(),
            _one_sided_unit("target_only", offset_minutes=25),
        ],
        ignore_index=True,
    )

    native_candidate = _detect(
        comparison_units,
        cadence_minutes=2.0,
    ).candidates[0]
    scheduled_candidate = _detect(
        comparison_units,
        cadence_minutes=20.0,
    ).candidates[0]

    assert native_candidate.path_effective_cadence_minutes == pytest.approx(30.0)
    assert scheduled_candidate.path_effective_cadence_minutes == pytest.approx(
        30.0
    )
    assert native_candidate.diagnostic_neighborhood_minutes == pytest.approx(
        45.0
    )
    assert scheduled_candidate.diagnostic_neighborhood_minutes == pytest.approx(
        45.0
    )
    assert native_candidate.nearby_target_only_unit_count == 1
    assert native_candidate.decode_edge_warning is True
    assert scheduled_candidate.nearby_target_only_unit_count == 1
    assert scheduled_candidate.decode_edge_warning is True
    assert native_candidate.decode_edge_warning_reason == (
        outlier_candidates.OUTLIER_DECODE_EDGE_REFERENCE_MISSING_NEAR_POSITIVE_EPISODE
    )
    assert scheduled_candidate.decode_edge_warning_reason == (
        outlier_candidates.OUTLIER_DECODE_EDGE_REFERENCE_MISSING_NEAR_POSITIVE_EPISODE
    )


def test_path_cadence_uses_retained_one_sided_outcomes_between_joint_units():
    """Include eligible one-sided outcomes when estimating observed cadence."""
    interleaved_offsets = (
        -285,
        -255,
        -225,
        -195,
        -165,
        -135,
        -105,
        105,
        135,
        165,
        195,
        225,
        255,
        285,
    )
    comparison_units = pd.concat(
        [
            _path_units(event_points=((0, 6.2), (20, 6.2), (40, 6.2))),
            *(
                _one_sided_unit("target_only", offset_minutes=offset)
                for offset in interleaved_offsets
            ),
        ],
        ignore_index=True,
    )

    candidate = _detect(comparison_units).candidates[0]

    assert candidate.path_effective_cadence_minutes == pytest.approx(15.0)
    assert candidate.maximum_episode_gap_minutes == pytest.approx(22.5)
    assert candidate.paired_unit_count == 3
    assert candidate.observed_span_minutes == pytest.approx(40.0)


@pytest.mark.parametrize("event_delta_snr_db", (5.9, 0.1))
def test_single_spot_below_shared_gates_does_not_qualify(
    event_delta_snr_db,
):
    """Apply the shared absolute gates to single cycles in both directions."""
    model = _detect(
        _path_units(event_points=((0, event_delta_snr_db),))
    )

    assert model.candidates == ()
    assert model.report_entries == ()
    assert model.evaluable_station_cycle_count > 0


def test_short_burst_qualifies_at_the_shared_episode_gates():
    """Qualify grouped evidence from its median against the shared gates."""
    model = _detect(
        _path_units(
            event_points=((0, 6.2), (4, 6.2), (8, 6.2)),
        )
    )

    assert len(model.candidates) == 1
    candidate = model.candidates[0]
    assert candidate.event_kind == (
        outlier_candidates.OUTLIER_EVENT_SHORT_BURST
    )
    assert candidate.paired_unit_count == 3
    assert candidate.observed_span_minutes == pytest.approx(8.0)
    assert candidate.largest_gap_minutes == pytest.approx(4.0)
    assert candidate.median_anomaly_db == pytest.approx(3.2)
    assert candidate.peak_anomaly_db == pytest.approx(3.2)
    assert abs(candidate.median_anomaly_db) >= (
        DEFAULT_DELTA_SNR_OUTLIER_DETECTION_POLICY.minimum_departure_db
    )
    assert candidate.robust_z == pytest.approx(4.3168)
    assert abs(candidate.robust_z) >= (
        DEFAULT_DELTA_SNR_OUTLIER_DETECTION_POLICY.minimum_robust_z
    )


def test_two_of_three_sign_coherence_remains_sufficient():
    """Accept the documented two-thirds agreement boundary inclusively."""
    model = _detect(
        _path_units(
            event_points=((0, 6.2), (4, 3.0), (8, 6.2)),
        )
    )

    assert outlier_candidates.DELTA_SNR_OUTLIER_MINIMUM_SIGN_AGREEMENT_FRACTION == (
        pytest.approx(2.0 / 3.0)
    )
    assert len(model.candidates) == 1
    candidate = model.candidates[0]
    assert candidate.event_kind == (
        outlier_candidates.OUTLIER_EVENT_SHORT_BURST
    )
    assert candidate.paired_unit_count == 3
    assert candidate.agreeing_paired_unit_count == 2
    assert candidate.paired_unit_sign_agreement_fraction == pytest.approx(
        2.0 / 3.0
    )


def test_duration_does_not_admit_a_sustained_excursion_below_shared_gates():
    """Do not weaken the common hard gates for a longer grouped candidate."""
    event_points = tuple((offset, 5.5) for offset in range(0, 51, 10))

    model = _detect(
        _path_units(event_points=event_points)
    )

    assert model.candidates == ()
    assert model.report_entries == ()
    assert model.evaluable_station_cycle_count > 0


def test_pa0o_like_sparse_excursion_retains_internal_neutral_bridge():
    """Retain one internal baseline return when qualifying evidence resumes."""
    event_points = (
        (0, 5.5),
        (20, 5.5),
        (42, 3.5),
        (62, 5.5),
        (82, 5.5),
        (102, 5.5),
        (122, 5.5),
        (142, 5.5),
    )
    comparison_units = _path_units(
        callsign="PA0O",
        locator="JO33HG",
        event_points=event_points,
        pre_offsets_minutes=(
            -300,
            -280,
            -258,
            -238,
            -216,
            -196,
            -174,
            -154,
            -132,
            -112,
            -90,
        ),
        post_offsets_minutes=(232, 252, 274, 294, 316, 336, 358, 378),
    )

    model = _detect(
        comparison_units,
        detection_policy=DeltaSnrOutlierDetectionPolicy(
            minimum_departure_db=2.0,
            minimum_robust_z=3.0,
        ),
    )

    assert len(model.candidates) == 1
    candidate = model.candidates[0]
    assert candidate.station_identity.label == "PA0O (JO33HG)"
    assert candidate.event_kind == (
        outlier_candidates.OUTLIER_EVENT_SUSTAINED_EXCURSION
    )
    assert candidate.start_utc == WALTER_IMPULSE_UTC
    assert candidate.end_utc > WALTER_IMPULSE_UTC + pd.Timedelta(minutes=142)
    assert candidate.paired_unit_count == 8
    assert candidate.agreeing_paired_unit_count == 8
    assert candidate.observed_span_minutes == pytest.approx(142.0)
    assert candidate.largest_gap_minutes == pytest.approx(22.0)
    assert candidate.path_effective_cadence_minutes == pytest.approx(20.0)
    assert candidate.maximum_episode_gap_minutes == pytest.approx(30.0)
    assert candidate.median_anomaly_db == pytest.approx(2.5)


def test_pa0o_like_excursion_trims_a_weak_leading_shoulder_only():
    """Trim weak leading evidence while retaining a bracketed weak cycle."""
    comparison_units = _path_units(
        callsign="PA0O",
        locator="JO33HG",
        event_points=(
            (0, 4.5),
            (20, 10.5),
            (38, 8.5),
            (60, 4.5),
            (82, 14.5),
        ),
    )
    strict_policy = DeltaSnrOutlierDetectionPolicy(
        minimum_departure_db=5.0,
        minimum_robust_z=4.0,
        maximum_baseline_difference_db=3.0,
    )

    candidate = _detect(
        comparison_units,
        detection_policy=strict_policy,
    ).candidates[0]

    assert candidate.station_identity.label == "PA0O (JO33HG)"
    assert candidate.event_kind == (
        outlier_candidates.OUTLIER_EVENT_SUSTAINED_EXCURSION
    )
    assert candidate.start_utc == WALTER_IMPULSE_UTC + pd.Timedelta(minutes=20)
    assert candidate.end_utc == (
        WALTER_IMPULSE_UTC
        + pd.Timedelta(minutes=82)
        + pd.Timedelta(nanoseconds=1)
    )
    assert candidate.paired_unit_count == 4
    assert candidate.observed_span_minutes == pytest.approx(62.0)
    assert candidate.largest_gap_minutes == pytest.approx(22.0)
    assert candidate.station_baseline_db == pytest.approx(3.0)
    assert candidate.episode_median_delta_snr_db == pytest.approx(9.5)
    assert candidate.median_anomaly_db == pytest.approx(6.5)
    assert candidate.peak_anomaly_db == pytest.approx(11.5)


def test_df2jp_like_excursion_trims_weak_leading_and_trailing_shoulders():
    """Anchor both boundaries without dropping weaker internal evidence."""
    residuals_db = (
        -2.0,
        -1.0,
        -2.0,
        -5.0,
        -4.0,
        -6.0,
        -7.0,
        -7.0,
        -5.0,
        -5.0,
        -5.0,
        -2.0,
        -3.0,
    )
    comparison_units = _path_units(
        callsign="DF2JP",
        locator="JO31FP",
        pre_baseline_db=9.8,
        event_points=tuple(
            (index * 10, 9.8 + residual_db)
            for index, residual_db in enumerate(residuals_db)
        ),
        pre_offsets_minutes=(-170, -160, -150, -140, -130, -120, -110, -100),
        post_offsets_minutes=(220, 230, 240, 250, 260, 270, 280, 290),
    )
    strict_policy = DeltaSnrOutlierDetectionPolicy(
        minimum_departure_db=5.0,
        minimum_robust_z=4.0,
        maximum_baseline_difference_db=3.0,
    )

    candidate = _detect(
        comparison_units,
        detection_policy=strict_policy,
    ).candidates[0]

    assert candidate.station_identity.label == "DF2JP (JO31FP)"
    assert candidate.event_kind == (
        outlier_candidates.OUTLIER_EVENT_SUSTAINED_EXCURSION
    )
    assert candidate.start_utc == WALTER_IMPULSE_UTC + pd.Timedelta(minutes=30)
    assert candidate.end_utc == (
        WALTER_IMPULSE_UTC
        + pd.Timedelta(minutes=100)
        + pd.Timedelta(nanoseconds=1)
    )
    assert candidate.paired_unit_count == 8
    assert candidate.observed_span_minutes == pytest.approx(70.0)
    assert candidate.largest_gap_minutes == pytest.approx(10.0)
    assert candidate.station_baseline_db == pytest.approx(9.8)
    assert candidate.episode_median_delta_snr_db == pytest.approx(4.8)
    assert candidate.median_anomaly_db == pytest.approx(-5.0)
    assert candidate.peak_anomaly_db == pytest.approx(-7.0)


def test_trimming_one_remaining_strong_anchor_reclassifies_as_impulse():
    """Describe one retained strong cycle as an impulse after trimming."""
    candidate = _detect(
        _path_units(event_points=((0, 4.0), (10, 8.0)))
    ).candidates[0]

    assert candidate.event_kind == outlier_candidates.OUTLIER_EVENT_SPOT_IMPULSE
    assert candidate.start_utc == WALTER_IMPULSE_UTC + pd.Timedelta(minutes=10)
    assert candidate.end_utc == (
        WALTER_IMPULSE_UTC
        + pd.Timedelta(minutes=10)
        + pd.Timedelta(nanoseconds=1)
    )
    assert candidate.paired_unit_count == 1
    assert candidate.observed_span_minutes == pytest.approx(0.0)
    assert candidate.largest_gap_minutes == pytest.approx(0.0)
    assert candidate.median_anomaly_db == pytest.approx(5.0)
    assert candidate.peak_anomaly_db == pytest.approx(5.0)


def test_two_supported_baseline_returns_split_same_sign_runs():
    """Treat two consecutive supported neutral units as an episode boundary."""
    comparison_units = _path_units(
        event_points=(
            (0, 6.2),
            (10, 6.2),
            (20, 3.4),
            (30, 3.3),
            (40, 6.2),
            (50, 6.2),
        ),
        pre_offsets_minutes=(-160, -150, -140, -130, -120, -110, -100, -90),
        post_offsets_minutes=(140, 150, 160, 170, 180, 190, 200, 210),
    )

    candidates = _detect(comparison_units).candidates

    assert len(candidates) == 2
    assert tuple(candidate.paired_unit_count for candidate in candidates) == (2, 2)
    assert candidates[0].end_utc < WALTER_IMPULSE_UTC + pd.Timedelta(minutes=20)
    assert candidates[1].start_utc == WALTER_IMPULSE_UTC + pd.Timedelta(
        minutes=40
    )


def test_material_sign_reversal_splits_adjacent_path_episodes():
    """Start a new episode immediately when a supported anomaly reverses sign."""
    comparison_units = _path_units(
        event_points=((0, 6.2), (10, 6.2), (20, -0.2), (30, -0.2)),
        pre_offsets_minutes=(-160, -150, -140, -130, -120, -110, -100, -90),
        post_offsets_minutes=(120, 130, 140, 150, 160, 170, 180, 190),
    )

    candidates = _detect(comparison_units).candidates

    assert len(candidates) == 2
    assert tuple(np.sign(candidate.median_anomaly_db) for candidate in candidates) == (
        1.0,
        -1.0,
    )
    assert tuple(candidate.paired_unit_count for candidate in candidates) == (2, 2)


def test_absolute_episode_gap_cap_splits_a_long_path_outage():
    """Do not let a sparse path cadence bridge an unobserved 50-minute outage."""
    comparison_units = _path_units(
        event_points=((0, 6.2), (30, 6.2), (80, 6.2), (110, 6.2)),
        post_offsets_minutes=(200, 230, 260, 290, 320, 350, 380, 410),
    )

    candidates = _detect(comparison_units).candidates

    assert len(candidates) == 2
    assert tuple(candidate.paired_unit_count for candidate in candidates) == (2, 2)
    assert all(
        candidate.path_effective_cadence_minutes == pytest.approx(30.0)
        for candidate in candidates
    )
    assert all(
        candidate.maximum_episode_gap_minutes == pytest.approx(45.0)
        for candidate in candidates
    )
    assert candidates[1].start_utc - candidates[0].end_utc > pd.Timedelta(
        minutes=49
    )


def test_whole_episode_is_excluded_from_its_refined_baseline():
    """Keep moderate shoulders out of the baseline around one strict peak."""
    event_points = (
        (0, 6.2),
        (10, 6.2),
        (20, 8.5),
        (30, 6.2),
        (40, 6.2),
    )

    candidate = _detect(
        _path_units(event_points=event_points)
    ).candidates[0]

    assert candidate.start_utc == WALTER_IMPULSE_UTC
    assert candidate.end_utc > WALTER_IMPULSE_UTC + pd.Timedelta(minutes=40)
    assert candidate.representative_utc == (
        WALTER_IMPULSE_UTC + pd.Timedelta(minutes=20)
    )
    assert candidate.paired_unit_count == 5
    assert candidate.observed_span_minutes == pytest.approx(40.0)
    assert candidate.pre_flank_cell_count == len(DEFAULT_PRE_OFFSETS_MINUTES)
    assert candidate.post_flank_cell_count == len(DEFAULT_POST_OFFSETS_MINUTES)
    assert candidate.pre_baseline_db == pytest.approx(3.0)
    assert candidate.post_baseline_db == pytest.approx(3.0)
    assert candidate.station_baseline_db == pytest.approx(3.0)
    assert candidate.episode_median_delta_snr_db == pytest.approx(6.2)
    assert candidate.median_anomaly_db == pytest.approx(3.2)
    assert candidate.peak_anomaly_db == pytest.approx(5.5)


def test_default_grouping_floor_retains_only_bracketed_one_db_evidence():
    """Keep weak internal continuity but trim weak outer shoulders."""
    event_points = (
        (0, 4.2),
        (10, 6.5),
        (20, 6.5),
        (30, 6.5),
        (40, 4.2),
    )

    candidate = _detect(
        _path_units(event_points=event_points)
    ).candidates[0]

    assert candidate.event_kind == (
        outlier_candidates.OUTLIER_EVENT_SHORT_BURST
    )
    assert candidate.paired_unit_count == 3
    assert candidate.start_utc == WALTER_IMPULSE_UTC + pd.Timedelta(minutes=10)
    assert candidate.end_utc == (
        WALTER_IMPULSE_UTC
        + pd.Timedelta(minutes=30)
        + pd.Timedelta(nanoseconds=1)
    )
    assert candidate.observed_span_minutes == pytest.approx(20.0)
    assert candidate.median_anomaly_db == pytest.approx(3.5)
    assert candidate.median_anomaly_db >= (
        DEFAULT_DELTA_SNR_OUTLIER_DETECTION_POLICY.minimum_departure_db
    )


def test_negative_burst_uses_symmetric_episode_gates():
    """Apply the same duration, effect, and score rules below the baseline."""
    positive_candidate = _detect(
        _path_units(event_points=((0, 6.2), (4, 6.2), (8, 6.2)))
    ).candidates[0]
    negative_candidate = _detect(
        _path_units(event_points=((0, -0.2), (4, -0.2), (8, -0.2)))
    ).candidates[0]

    assert negative_candidate.event_kind == positive_candidate.event_kind
    assert negative_candidate.median_anomaly_db == pytest.approx(
        -positive_candidate.median_anomaly_db
    )
    assert negative_candidate.peak_anomaly_db == pytest.approx(
        -positive_candidate.peak_anomaly_db
    )
    assert negative_candidate.robust_z == pytest.approx(
        -positive_candidate.robust_z
    )
    assert negative_candidate.agreeing_paired_unit_count == 3
    assert negative_candidate.paired_unit_sign_agreement_fraction == pytest.approx(
        1.0
    )
    assert _detect(
        _path_units(event_points=((0, -0.2), (4, -0.2), (8, -0.2)))
    ).report_entries[0].sign_agreement == "negative"


def test_path_local_gap_splits_runs_before_descriptive_classification():
    """Split on cadence, then apply the same gates to each resulting run."""
    model = _detect(
        _path_units(
            event_points=((0, 6.2), (10, 6.2), (30, 6.2)),
            pre_offsets_minutes=(-160, -150, -140, -130, -120, -110, -100, -90),
            post_offsets_minutes=(90, 100, 110, 120, 130, 140, 150, 160),
        )
    )

    assert len(model.candidates) == 2
    burst, impulse = model.candidates
    assert burst.event_kind == outlier_candidates.OUTLIER_EVENT_SHORT_BURST
    assert burst.paired_unit_count == 2
    assert burst.observed_span_minutes == pytest.approx(10.0)
    assert burst.largest_gap_minutes == pytest.approx(10.0)
    assert impulse.event_kind == outlier_candidates.OUTLIER_EVENT_SPOT_IMPULSE
    assert impulse.paired_unit_count == 1
    assert impulse.start_utc == WALTER_IMPULSE_UTC + pd.Timedelta(minutes=30)
    assert all(
        candidate.path_effective_cadence_minutes == pytest.approx(10.0)
        for candidate in model.candidates
    )
    assert all(
        candidate.maximum_episode_gap_minutes == pytest.approx(15.0)
        for candidate in model.candidates
    )


def test_observed_path_cadence_overrides_different_fallback_cadences():
    """Keep grouping identical when a path provides a robust cadence estimate."""
    comparison_units = _path_units(
        event_points=((0, 6.2), (10, 6.2), (30, 6.2))
    )

    native_candidate = _detect(
        comparison_units,
        cadence_minutes=2.0,
    ).candidates[0]
    scheduled_candidate = _detect(
        comparison_units,
        cadence_minutes=20.0,
    ).candidates[0]

    assert native_candidate.paired_unit_count == 3
    assert scheduled_candidate.paired_unit_count == 3
    assert native_candidate.path_effective_cadence_minutes == pytest.approx(30.0)
    assert scheduled_candidate.path_effective_cadence_minutes == pytest.approx(
        30.0
    )
    assert native_candidate.maximum_episode_gap_minutes == pytest.approx(45.0)
    assert scheduled_candidate.maximum_episode_gap_minutes == pytest.approx(
        45.0
    )
    assert native_candidate.event_kind == (
        outlier_candidates.OUTLIER_EVENT_SUSTAINED_EXCURSION
    )
    assert scheduled_candidate.observed_span_minutes == pytest.approx(30.0)
    assert scheduled_candidate.largest_gap_minutes == pytest.approx(20.0)
    assert scheduled_candidate.event_kind == (
        outlier_candidates.OUTLIER_EVENT_SUSTAINED_EXCURSION
    )


@pytest.mark.parametrize(
    ("pre_offsets", "post_offsets"),
    (
        (DEFAULT_PRE_OFFSETS_MINUTES, ()),
        ((), DEFAULT_POST_OFFSETS_MINUTES),
    ),
)
def test_missing_either_flank_leaves_the_impulse_unclassified(
    pre_offsets,
    post_offsets,
):
    """Require supported evidence on both sides of a proposed event."""
    comparison_units = _path_units(
        pre_offsets_minutes=pre_offsets,
        post_offsets_minutes=post_offsets,
    )

    model = _detect(comparison_units)

    assert model.candidates == ()
    assert model.report_entries == ()
    assert model.populated_station_cycle_count == len(comparison_units)
    assert model.evaluable_station_cycle_count == 0
    assert model.abstained_station_cycle_count == len(comparison_units)


def test_incompatible_pre_and_post_flanks_do_not_define_a_transient_baseline():
    """Do not relabel a persistent level change as a supported excursion."""
    comparison_units = _path_units(
        event_points=((0, 10.0),),
        pre_baseline_db=3.0,
        post_baseline_db=7.0,
    )

    model = _detect(comparison_units)

    assert model.candidates == ()
    assert model.report_entries == ()
    assert model.evaluable_station_cycle_count == 0
    assert model.abstained_station_cycle_count == len(comparison_units)


@pytest.mark.parametrize(
    ("directions", "expected_scope"),
    (
        (
            {("A1AAA", "AA11"): "W", ("B2BBB", "BB22"): "W"},
            outlier_candidates.OUTLIER_SCOPE_DIRECTIONALLY_COHERENT,
        ),
        (
            {("A1AAA", "AA11"): "W", ("B2BBB", "BB22"): "WNW"},
            outlier_candidates.OUTLIER_SCOPE_DIRECTIONALLY_COHERENT,
        ),
        (
            {("A1AAA", "AA11"): "W", ("B2BBB", "BB22"): "E"},
            outlier_candidates.OUTLIER_SCOPE_SCOPE_WIDE,
        ),
        (
            {("A1AAA", "AA11"): "W"},
            outlier_candidates.OUTLIER_SCOPE_MULTIPLE_PATHS,
        ),
    ),
)
def test_contemporaneous_same_sign_paths_receive_post_detection_context(
    directions,
    expected_scope,
):
    """Aggregate path episodes by time and sign, then describe direction breadth."""
    comparison_units = pd.concat(
        [
            _path_units("A1AAA", "AA11", identity_order=0),
            _path_units("B2BBB", "BB22", identity_order=1),
        ],
        ignore_index=True,
    )

    model = _detect(comparison_units, station_directions=directions)

    assert len(model.candidates) == 2
    assert len(model.report_entries) == 1
    report_entry = model.report_entries[0]
    assert report_entry.coherence_scope == expected_scope
    assert report_entry.contributing_station_count == 2
    assert report_entry.evaluable_station_count == 2
    assert report_entry.flagged_station_count == 2
    assert report_entry.segment_positive_station_count == 2
    assert report_entry.segment_negative_station_count == 0
    assert report_entry.segment_neutral_station_count == 0
    assert report_entry.segment_sign_agreement == "positive"
    assert report_entry.station_identities == (
        outlier_candidates.OutlierStationIdentity("A1AAA", "AA11"),
        outlier_candidates.OutlierStationIdentity("B2BBB", "BB22"),
    )


def test_opposite_sign_path_episodes_remain_separate_report_entries():
    """Do not turn simultaneous opposite movement into same-sign coherence."""
    comparison_units = pd.concat(
        [
            _path_units("A1AAA", "AA11", identity_order=0),
            _path_units(
                "B2BBB",
                "BB22",
                event_points=((0, -2.0),),
                identity_order=1,
            ),
        ],
        ignore_index=True,
    )

    model = _detect(comparison_units)

    assert len(model.candidates) == 2
    assert len(model.report_entries) == 2
    assert [entry.sign_agreement for entry in model.report_entries] == [
        "positive",
        "negative",
    ]
    assert all(entry.flagged_station_count == 1 for entry in model.report_entries)


def test_same_hour_but_noncontemporaneous_path_episodes_are_not_merged():
    """Retire the former UTC-hour card as an event-grouping boundary."""
    comparison_units = pd.concat(
        [
            _path_units("A1AAA", "AA11", identity_order=0),
            _path_units(
                "B2BBB",
                "BB22",
                anchor_utc=WALTER_IMPULSE_UTC + pd.Timedelta(minutes=20),
                identity_order=1,
            ),
        ],
        ignore_index=True,
    )

    model = _detect(comparison_units)

    assert len(model.candidates) == 2
    assert len(model.report_entries) == 2
    assert all(entry.flagged_station_count == 1 for entry in model.report_entries)
    assert model.report_entries[0].start_utc.hour == 18
    assert model.report_entries[1].start_utc.hour == 18


def test_marker_filtering_and_signatures_are_stable_under_row_order():
    """Fingerprint episode content deterministically and filter exact paths."""
    comparison_units = pd.concat(
        [
            _path_units("A1AAA", "AA11", identity_order=0),
            _path_units("B2BBB", "BB22", identity_order=1),
        ],
        ignore_index=True,
    )
    first_model = _detect(comparison_units)
    reversed_model = _detect(comparison_units.iloc[::-1].reset_index(drop=True))

    assert first_model.candidate_signature == reversed_model.candidate_signature
    assert first_model.cache_token == reversed_model.cache_token
    assert first_model.marker_recipe() == reversed_model.marker_recipe()

    filtered_recipe = first_model.marker_recipe(
        [{"callsign": "B2BBB", "locator": "BB22"}]
    )
    assert filtered_recipe["candidate_count"] == 1
    assert filtered_recipe["markers"][0]["callsign"] == "B2BBB"
    assert first_model.marker_recipe(
        [{"callsign": "C3CCC", "locator": "CC33"}]
    ) is None

    changed_units = comparison_units.copy(deep=True)
    changed_mask = (
        changed_units["peer_sign"].eq("B2BBB")
        & changed_units["evidence_utc"].eq(WALTER_IMPULSE_UTC)
    )
    changed_units.loc[changed_mask, "metric"] = 8.5
    assert _detect(changed_units).candidate_signature != (
        first_model.candidate_signature
    )


def test_detector_does_not_mutate_units_and_ignores_invalid_rows():
    """Protect retained comparison-unit ownership while validating input rows."""
    valid_units = _path_units()
    invalid_rows = pd.DataFrame(
        [
            {
                "peer_sign": "DC0DX",
                "peer_grid": "JO31LK",
                "identity_order": np.nan,
                "evidence_utc": WALTER_IMPULSE_UTC,
                "outcome": "joint",
                "metric": np.inf,
                "paired_eligible": True,
                "target_snr_db": np.nan,
                "reference_snr_db": np.nan,
            },
            {
                "peer_sign": None,
                "peer_grid": "JO31LK",
                "identity_order": np.nan,
                "evidence_utc": WALTER_IMPULSE_UTC,
                "outcome": "joint",
                "metric": -999.0,
                "paired_eligible": True,
                "target_snr_db": np.nan,
                "reference_snr_db": np.nan,
            },
            {
                "peer_sign": "!",
                "peer_grid": "JO31LK",
                "identity_order": 4,
                "evidence_utc": WALTER_IMPULSE_UTC,
                "outcome": "joint",
                "metric": 999.0,
                "paired_eligible": True,
                "target_snr_db": np.nan,
                "reference_snr_db": np.nan,
            },
            {
                "peer_sign": "DC0DX",
                "peer_grid": "JO31LK",
                "identity_order": 0,
                "evidence_utc": WALTER_IMPULSE_UTC,
                "outcome": "target_only",
                "metric": 999.0,
                "paired_eligible": True,
                "target_snr_db": np.nan,
                "reference_snr_db": np.nan,
            },
            {
                "peer_sign": "DC0DX",
                "peer_grid": "JO31LK",
                "identity_order": 0,
                "evidence_utc": ANALYSIS_END,
                "outcome": "joint",
                "metric": 999.0,
                "paired_eligible": True,
                "target_snr_db": np.nan,
                "reference_snr_db": np.nan,
            },
        ]
    )
    comparison_units = pd.concat([valid_units, invalid_rows], ignore_index=True)
    original_units = comparison_units.copy(deep=True)

    model = _detect(comparison_units)

    pdt.assert_frame_equal(comparison_units, original_units)
    assert len(model.candidates) == 1
    assert model.candidates[0].station_identity.label == "DC0DX (JO31LK)"
    assert model.populated_station_cycle_count == len(valid_units)


@pytest.mark.parametrize("drop_identity_order", (False, True))
def test_missing_identity_order_does_not_block_valid_detection(drop_identity_order):
    """Keep presentation ordering metadata outside the scientific requirement."""
    comparison_units = _path_units()
    if drop_identity_order:
        comparison_units = comparison_units.drop(columns="identity_order")
    else:
        comparison_units["identity_order"] = pd.Series(
            [pd.NA] * len(comparison_units),
            dtype="Int64",
        )

    model = _detect(comparison_units)

    assert len(model.candidates) == 1
    assert model.candidates[0].station_identity.label == "DC0DX (JO31LK)"


def test_empty_input_returns_native_zero_diagnostics():
    """Expose an enabled empty scope without fabricating cycle abstentions."""
    model = _detect(pd.DataFrame())

    assert model.detection_resolution == "native-paired-unit"
    assert model.candidates == ()
    assert model.report_entries == ()
    assert model.populated_station_cycle_count == 0
    assert model.evaluable_station_cycle_count == 0
    assert model.abstained_station_cycle_count == 0
    assert model.marker_recipe() is None


def test_nonempty_input_missing_scientific_columns_is_rejected():
    """Do not disguise an internal comparison-schema regression as no evidence."""
    with pytest.raises(
        ValueError,
        match=(
            "missing required columns: evidence_utc, metric, outcome, "
            "paired_eligible, peer_grid"
        ),
    ):
        _detect(pd.DataFrame({"peer_sign": ["DC0DX"]}))


def test_nonpositive_analysis_window_is_rejected():
    """Retain an actionable error for an invalid half-open UTC window."""
    with pytest.raises(ValueError, match="positive UTC window"):
        _detect(
            pd.DataFrame(),
            analysis_start=ANALYSIS_START,
            analysis_end=ANALYSIS_START,
        )


@pytest.mark.parametrize("cadence_minutes", (0, -1, np.nan, "invalid"))
def test_invalid_paired_unit_cadence_is_rejected(cadence_minutes):
    """Require an explicit finite positive native or Scheduled Pair cadence."""
    with pytest.raises(ValueError, match="cadence_minutes must be positive"):
        _detect(pd.DataFrame(), cadence_minutes=cadence_minutes)
