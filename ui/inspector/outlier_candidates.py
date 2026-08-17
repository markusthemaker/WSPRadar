"""Optional presentation-side Delta-SNR episode-candidate preparation.

The detector consumes retained Benchmark comparison units only. It does not
alter canonical paired evidence, participate in the normal scientific result
path, or initiate provider work. Native paired units remain the event evidence;
short baseline-support cells exist only to estimate scalable local context.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from hashlib import sha256
import json
import math

import numpy as np
import pandas as pd

from config import COMPASS
from config.delta_snr_outlier import (
    DEFAULT_DELTA_SNR_OUTLIER_DETECTION_POLICY,
    DeltaSnrOutlierDetectionPolicy,
)
from core.input_validation import is_valid_callsign, is_valid_locator
from ui.inspector.evidence_data import (
    COMPARE_OUTCOME_JOINT,
    COMPARE_OUTCOME_REFERENCE_ONLY,
    COMPARE_OUTCOME_TARGET_ONLY,
)


DELTA_SNR_OUTLIER_DETECTOR_VERSION = "native-residual-episode-v7"
DELTA_SNR_OUTLIER_RECIPE_SCHEMA_VERSION = 3
DELTA_SNR_OUTLIER_QUALIFYING_UNIT_RECIPE_SCHEMA_VERSION = 1
DELTA_SNR_OUTLIER_DETECTION_RESOLUTION = "native-paired-unit"
DELTA_SNR_OUTLIER_BASELINE_CELL = "10min"
DELTA_SNR_OUTLIER_FLANK_WINDOW_HOURS = 6
DELTA_SNR_OUTLIER_MINIMUM_FLANK_CELLS = 4
DELTA_SNR_OUTLIER_PILOT_GUARD_MINUTES = 60
DELTA_SNR_OUTLIER_EPISODE_GUARD_MINUTES = 10
DELTA_SNR_OUTLIER_MINIMUM_MEMBER_ANOMALY_DB = 1.0
DELTA_SNR_OUTLIER_MINIMUM_SIGN_AGREEMENT_FRACTION = 2.0 / 3.0
DELTA_SNR_OUTLIER_SUSTAINED_MINIMUM_UNITS = 3
DELTA_SNR_OUTLIER_SUSTAINED_MINIMUM_SPAN_MINUTES = 30.0
DELTA_SNR_OUTLIER_DEFAULT_MAXIMUM_EPISODE_GAP_MINUTES = 15.0
DELTA_SNR_OUTLIER_MAXIMUM_EPISODE_GAP_CAP_MINUTES = 45.0
DELTA_SNR_OUTLIER_MINIMUM_PATH_CADENCE_INTERVALS = 2
DELTA_SNR_OUTLIER_SEGMENT_COHERENCE_MINUTES = 10.0
DELTA_SNR_OUTLIER_MAD_NORMALIZATION = 0.6745
DELTA_SNR_OUTLIER_QUANTIZATION_MAD_FLOOR_DB = 0.5
DELTA_SNR_OUTLIER_MAXIMUM_REFINEMENT_PASSES = 3

OUTLIER_EVENT_SPOT_IMPULSE = "spot_impulse"
OUTLIER_EVENT_SHORT_BURST = "short_burst"
OUTLIER_EVENT_SUSTAINED_EXCURSION = "sustained_excursion"
OUTLIER_EVENT_MIXED_DURATION = "mixed_duration"

OUTLIER_SCOPE_PATH_SPECIFIC = "path_specific"
OUTLIER_SCOPE_DIRECTIONALLY_COHERENT = "directionally_coherent"
OUTLIER_SCOPE_SCOPE_WIDE = "scope_wide"
OUTLIER_SCOPE_MULTIPLE_PATHS = "multiple_paths"

OUTLIER_DECODE_EDGE_REFERENCE_MISSING_NEAR_POSITIVE_EPISODE = (
    "reference_missing_near_positive_episode"
)
OUTLIER_DECODE_EDGE_TARGET_MISSING_NEAR_NEGATIVE_EPISODE = (
    "target_missing_near_negative_episode"
)


@dataclass(frozen=True, order=True)
class OutlierStationIdentity:
    """Identify one retained radio path independently of presentation labels."""

    callsign: str
    locator: str

    @property
    def label(self) -> str:
        """Return the established callsign-plus-locator display identity."""
        return f"{self.callsign} ({self.locator})"


@dataclass(frozen=True, order=True)
class DeltaSnrOutlierQualifyingUnit:
    """Retain one native unit that independently passes both outlier gates."""

    evidence_utc: pd.Timestamp
    delta_snr_db: float
    residual_db: float
    robust_z: float

    def __post_init__(self) -> None:
        """Normalize UTC and reject non-finite marker coordinates."""
        timestamp = pd.Timestamp(self.evidence_utc)
        if pd.isna(timestamp):
            raise ValueError("Qualifying-unit evidence_utc must be valid.")
        if timestamp.tzinfo is None:
            timestamp = timestamp.tz_localize("UTC")
        else:
            timestamp = timestamp.tz_convert("UTC")
        numeric_fields = {
            "delta_snr_db": self.delta_snr_db,
            "residual_db": self.residual_db,
            "robust_z": self.robust_z,
        }
        normalized_values: dict[str, float] = {}
        for field_name, field_value in numeric_fields.items():
            try:
                numeric_value = float(field_value)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Qualifying-unit {field_name} must be finite."
                ) from exc
            if not math.isfinite(numeric_value):
                raise ValueError(
                    f"Qualifying-unit {field_name} must be finite."
                )
            normalized_values[field_name] = numeric_value
        object.__setattr__(self, "evidence_utc", timestamp)
        for field_name, numeric_value in normalized_values.items():
            object.__setattr__(self, field_name, numeric_value)


@dataclass(frozen=True)
class DeltaSnrOutlierCandidate:
    """Describe one qualified same-path Delta-SNR episode."""

    station_identity: OutlierStationIdentity
    direction_sector: str | None
    event_kind: str
    start_utc: pd.Timestamp
    end_utc: pd.Timestamp
    baseline_anchor_start_utc: pd.Timestamp
    baseline_anchor_end_utc: pd.Timestamp
    episode_guard_minutes: float
    representative_utc: pd.Timestamp
    representative_delta_snr_db: float
    episode_median_delta_snr_db: float
    station_baseline_db: float
    pre_baseline_db: float
    post_baseline_db: float
    median_anomaly_db: float
    peak_anomaly_db: float
    mad_db: float
    robust_spread_db: float
    robust_spread_method: str
    robust_z: float
    pre_flank_cell_count: int
    post_flank_cell_count: int
    paired_unit_count: int
    agreeing_paired_unit_count: int
    paired_unit_sign_agreement_fraction: float
    observed_span_minutes: float
    largest_gap_minutes: float
    target_median_snr_db: float | None
    target_baseline_db: float | None
    target_anomaly_db: float | None
    reference_median_snr_db: float | None
    reference_baseline_db: float | None
    reference_anomaly_db: float | None
    path_effective_cadence_minutes: float = 0.0
    maximum_episode_gap_minutes: float = 0.0
    diagnostic_neighborhood_minutes: float = 0.0
    nearby_joint_unit_count: int = 0
    nearby_target_only_unit_count: int = 0
    nearby_reference_only_unit_count: int = 0
    decode_edge_warning: bool = False
    decode_edge_warning_reason: str | None = None
    qualifying_units: tuple[DeltaSnrOutlierQualifyingUnit, ...] = ()

    def __post_init__(self) -> None:
        """Keep nested qualifying evidence immutable and explicitly typed."""
        if not isinstance(self.qualifying_units, tuple):
            raise TypeError("candidate.qualifying_units must be a tuple.")
        if not all(
            isinstance(unit, DeltaSnrOutlierQualifyingUnit)
            for unit in self.qualifying_units
        ):
            raise TypeError(
                "candidate.qualifying_units must contain qualifying-unit records."
            )


@dataclass(frozen=True)
class DeltaSnrOutlierContextBounds:
    """Hold one exact clipped half-open Drill-Down context contract.

    The pre-flank interval mirrors the detector's inclusive outer and exclusive
    guard boundaries. The detector's post-flank interval is exclusive at the
    guard and inclusive at its outer boundary; adding one nanosecond to both
    boundaries expresses that same set as a conventional half-open interval.
    Empty boundary-clipped flanks therefore have equal start and end values.
    """

    context_start_utc: pd.Timestamp
    context_end_utc: pd.Timestamp
    pre_flank_start_utc: pd.Timestamp
    pre_flank_end_utc: pd.Timestamp
    post_flank_start_utc: pd.Timestamp
    post_flank_end_utc: pd.Timestamp


@dataclass(frozen=True)
class DeltaSnrOutlierSectorSummary:
    """Summarize contemporaneous path support in one compass sector."""

    direction_sector: str
    populated_station_count: int
    evaluable_station_count: int
    candidate_station_count: int
    median_signed_anomaly_db: float | None
    sign_agreement: str | None
    agreeing_count: int
    positive_station_count: int
    negative_station_count: int
    neutral_station_count: int


@dataclass(frozen=True)
class DeltaSnrOutlierReportEntry:
    """Summarize contemporaneous same-sign path episodes for one review card."""

    episode_index: int
    start_utc: pd.Timestamp
    end_utc: pd.Timestamp
    event_kind: str
    coherence_scope: str
    contributing_station_count: int
    evaluable_station_count: int
    candidates: tuple[DeltaSnrOutlierCandidate, ...]
    median_signed_anomaly_db: float
    maximum_absolute_anomaly_db: float
    maximum_anomaly_db: float
    sign_agreement: str
    agreeing_count: int
    segment_median_signed_anomaly_db: float
    segment_sign_agreement: str
    segment_agreeing_count: int
    segment_positive_station_count: int
    segment_negative_station_count: int
    segment_neutral_station_count: int
    direction_sectors: tuple[str, ...]
    sector_summaries: tuple[DeltaSnrOutlierSectorSummary, ...]
    station_identities: tuple[OutlierStationIdentity, ...]

    @property
    def flagged_station_count(self) -> int:
        """Return the number of unique flagged paths in this review episode."""
        return len(self.station_identities)


@dataclass(frozen=True)
class DeltaSnrOutlierModel:
    """Hold qualified path episodes, compact context, and marker preparation."""

    detector_version: str
    detection_resolution: str
    paired_unit_cadence_minutes: float
    analysis_start_utc: pd.Timestamp
    analysis_end_utc: pd.Timestamp
    populated_station_cycle_count: int
    evaluable_station_cycle_count: int
    abstained_station_cycle_count: int
    candidates: tuple[DeltaSnrOutlierCandidate, ...]
    report_entries: tuple[DeltaSnrOutlierReportEntry, ...]
    candidate_signature: str
    detection_policy: DeltaSnrOutlierDetectionPolicy = (
        DEFAULT_DELTA_SNR_OUTLIER_DETECTION_POLICY
    )

    @property
    def detection_policy_signature(self) -> str:
        """Fingerprint the qualification policy independently of candidates."""
        return _stable_signature(self.detection_policy.signature_tuple)

    @property
    def cache_token(self) -> tuple[str, str, str]:
        """Return the detector identity needed by Inspector and PNG cache keys."""
        return (
            self.detector_version,
            self.detection_resolution,
            self.candidate_signature,
        )

    def marker_recipe(
        self,
        station_identities: object = None,
    ) -> dict[str, object] | None:
        """Return exact representative marker coordinates for an optional subset."""
        selected_pairs = _normalized_identity_pairs(station_identities)
        selected_candidates = [
            candidate
            for candidate in self.candidates
            if selected_pairs is None
            or (
                candidate.station_identity.callsign,
                candidate.station_identity.locator,
            )
            in selected_pairs
        ]
        if not selected_candidates:
            return None
        detection_policy_signature = self.detection_policy_signature
        marker_payload = [
            {
                "callsign": candidate.station_identity.callsign,
                "locator": candidate.station_identity.locator,
                "marker_utc_ns": int(candidate.representative_utc.value),
                "marker_delta_snr_db": float(
                    candidate.representative_delta_snr_db
                ),
                "episode_start_utc_ns": int(candidate.start_utc.value),
                "episode_end_utc_ns": int(candidate.end_utc.value),
                "event_kind": candidate.event_kind,
                "detection_policy_signature": detection_policy_signature,
            }
            for candidate in selected_candidates
        ]
        return {
            "schema_version": DELTA_SNR_OUTLIER_RECIPE_SCHEMA_VERSION,
            "detector_version": self.detector_version,
            "detection_resolution": self.detection_resolution,
            "detection_policy_signature": detection_policy_signature,
            "candidate_count": len(marker_payload),
            "candidate_signature": _stable_signature(marker_payload),
            "markers": marker_payload,
        }

    def qualifying_unit_marker_recipe(
        self,
        station_identities: object = None,
        *,
        start_utc: object = None,
        end_utc: object = None,
    ) -> dict[str, object] | None:
        """Return every individually qualifying native-unit marker.

        The optional UTC restriction uses the same half-open ``[start, end)``
        convention as the completed analysis and Drill-Down focus. A stale
        model without the native qualifying-unit field safely contributes no
        recipe instead of inferring markers from all episode members.
        """
        if (
            self.detector_version != DELTA_SNR_OUTLIER_DETECTOR_VERSION
            or self.detection_resolution
            != DELTA_SNR_OUTLIER_DETECTION_RESOLUTION
        ):
            return None
        selected_pairs = _normalized_identity_pairs(station_identities)
        window_start, window_end = _optional_half_open_marker_window(
            start_utc=start_utc,
            end_utc=end_utc,
        )
        detection_policy_signature = self.detection_policy_signature
        marker_payload: list[dict[str, object]] = []
        marker_event_signatures: set[str] = set()
        marker_keys: dict[tuple[str, str, int, float], str] = {}
        for candidate in self.candidates:
            identity_pair = (
                candidate.station_identity.callsign,
                candidate.station_identity.locator,
            )
            if selected_pairs is not None and identity_pair not in selected_pairs:
                continue
            qualifying_units = _validated_candidate_qualifying_units(
                candidate,
                detection_policy=self.detection_policy,
            )
            if not qualifying_units:
                continue
            candidate_event_signature = _qualifying_candidate_event_signature(
                candidate,
                detection_policy_signature=detection_policy_signature,
            )
            for qualifying_unit in qualifying_units:
                if (
                    window_start is not None
                    and qualifying_unit.evidence_utc < window_start
                ):
                    continue
                if (
                    window_end is not None
                    and qualifying_unit.evidence_utc >= window_end
                ):
                    continue
                marker_key = (
                    identity_pair[0],
                    identity_pair[1],
                    int(qualifying_unit.evidence_utc.value),
                    float(qualifying_unit.delta_snr_db),
                )
                previous_event_signature = marker_keys.get(marker_key)
                if previous_event_signature is not None:
                    if previous_event_signature != candidate_event_signature:
                        raise ValueError(
                            "One qualifying native unit belongs to conflicting "
                            "outlier candidates."
                        )
                    continue
                marker_keys[marker_key] = candidate_event_signature
                marker_event_signatures.add(candidate_event_signature)
                marker_payload.append(
                    {
                        "callsign": identity_pair[0],
                        "locator": identity_pair[1],
                        "marker_utc_ns": marker_key[2],
                        "marker_delta_snr_db": marker_key[3],
                        "residual_db": float(qualifying_unit.residual_db),
                        "robust_z": float(qualifying_unit.robust_z),
                        "episode_start_utc_ns": int(candidate.start_utc.value),
                        "episode_end_utc_ns": int(candidate.end_utc.value),
                        "representative_utc_ns": int(
                            candidate.representative_utc.value
                        ),
                        "representative_delta_snr_db": float(
                            candidate.representative_delta_snr_db
                        ),
                        "event_kind": candidate.event_kind,
                        "candidate_event_signature": candidate_event_signature,
                        "detection_policy_signature": (
                            detection_policy_signature
                        ),
                    }
                )
        if not marker_payload:
            return None
        marker_payload.sort(
            key=lambda marker: (
                int(marker["marker_utc_ns"]),
                str(marker["callsign"]),
                str(marker["locator"]),
                float(marker["marker_delta_snr_db"]),
            )
        )
        return {
            "schema_version": (
                DELTA_SNR_OUTLIER_QUALIFYING_UNIT_RECIPE_SCHEMA_VERSION
            ),
            "detector_version": self.detector_version,
            "detection_resolution": self.detection_resolution,
            "detection_policy_signature": detection_policy_signature,
            "candidate_signature": self.candidate_signature,
            "candidate_count": len(marker_event_signatures),
            "qualifying_unit_count": len(marker_payload),
            "marker_signature": _stable_signature(marker_payload),
            "markers": marker_payload,
        }


def _normalized_utc_timestamp(value: object, *, field: str) -> pd.Timestamp:
    """Return one timezone-aware UTC timestamp or raise a field-specific error."""
    timestamp = pd.Timestamp(value)
    if pd.isna(timestamp):
        raise ValueError(f"{field} must be a valid UTC timestamp.")
    if timestamp.tzinfo is None:
        return timestamp.tz_localize("UTC")
    return timestamp.tz_convert("UTC")


def build_delta_snr_outlier_context_bounds(
    candidate: DeltaSnrOutlierCandidate,
    *,
    analysis_start_utc: object,
    analysis_end_utc: object,
) -> DeltaSnrOutlierContextBounds:
    """Return the detector's exact pre/event/post context clipped to analysis.

    All returned intervals use half-open ``[start, end)`` semantics so they can
    be applied directly to retained evidence and plot windows without moving a
    strong-anchor event or splitting an analysis-boundary observation.
    """
    if not isinstance(candidate, DeltaSnrOutlierCandidate):
        raise TypeError(
            "candidate must be a DeltaSnrOutlierCandidate."
        )
    analysis_start = _normalized_utc_timestamp(
        analysis_start_utc,
        field="analysis_start_utc",
    )
    analysis_end = _normalized_utc_timestamp(
        analysis_end_utc,
        field="analysis_end_utc",
    )
    if analysis_end <= analysis_start:
        raise ValueError("Outlier context requires a positive UTC window.")

    baseline_anchor_start = _normalized_utc_timestamp(
        candidate.baseline_anchor_start_utc,
        field="candidate.baseline_anchor_start_utc",
    )
    baseline_anchor_end = _normalized_utc_timestamp(
        candidate.baseline_anchor_end_utc,
        field="candidate.baseline_anchor_end_utc",
    )
    if baseline_anchor_end < baseline_anchor_start:
        raise ValueError(
            "Outlier baseline-anchor end must not precede its start."
        )
    if not (
        analysis_start <= baseline_anchor_start < analysis_end
        and analysis_start <= baseline_anchor_end < analysis_end
    ):
        raise ValueError(
            "Outlier baseline anchors must lie inside the supplied analysis window."
        )
    try:
        episode_guard_minutes = float(candidate.episode_guard_minutes)
    except (TypeError, ValueError) as exc:
        raise ValueError("Outlier episode guard must be positive.") from exc
    flank_minutes = float(DELTA_SNR_OUTLIER_FLANK_WINDOW_HOURS * 60)
    if (
        not math.isfinite(episode_guard_minutes)
        or episode_guard_minutes <= 0.0
        or episode_guard_minutes >= flank_minutes
    ):
        raise ValueError(
            "Outlier episode guard must be positive and shorter than the flank window."
        )

    flank_delta = pd.Timedelta(
        hours=DELTA_SNR_OUTLIER_FLANK_WINDOW_HOURS
    )
    guard_delta = pd.Timedelta(minutes=episode_guard_minutes)
    one_nanosecond = pd.Timedelta(nanoseconds=1)

    def clip_to_analysis(timestamp: pd.Timestamp) -> pd.Timestamp:
        return min(max(timestamp, analysis_start), analysis_end)

    pre_flank_start = clip_to_analysis(
        baseline_anchor_start - flank_delta
    )
    pre_flank_end = clip_to_analysis(
        baseline_anchor_start - guard_delta
    )
    post_flank_start = clip_to_analysis(
        baseline_anchor_end + guard_delta + one_nanosecond
    )
    post_flank_end = clip_to_analysis(
        baseline_anchor_end + flank_delta + one_nanosecond
    )
    return DeltaSnrOutlierContextBounds(
        context_start_utc=pre_flank_start,
        context_end_utc=post_flank_end,
        pre_flank_start_utc=pre_flank_start,
        pre_flank_end_utc=pre_flank_end,
        post_flank_start_utc=post_flank_start,
        post_flank_end_utc=post_flank_end,
    )


def _normalized_identity_pairs(
    station_identities: object,
) -> set[tuple[str, str]] | None:
    """Normalize an optional DataFrame, mapping sequence, or identity sequence."""
    if station_identities is None:
        return None
    if isinstance(station_identities, pd.DataFrame):
        if not {"peer_sign", "peer_grid"}.issubset(station_identities.columns):
            return set()
        identity_values = station_identities[
            ["peer_sign", "peer_grid"]
        ].itertuples(index=False, name=None)
    else:
        identity_values = station_identities

    normalized_pairs: set[tuple[str, str]] = set()
    for identity in identity_values:
        if isinstance(identity, OutlierStationIdentity):
            callsign, locator = identity.callsign, identity.locator
        elif isinstance(identity, Mapping):
            callsign = identity.get("callsign", identity.get("peer_sign"))
            locator = identity.get("locator", identity.get("peer_grid"))
        else:
            try:
                callsign, locator = identity
            except (TypeError, ValueError):
                continue
        callsign_text = str(callsign).strip().upper()
        locator_text = str(locator).strip().upper()
        if callsign_text and locator_text:
            normalized_pairs.add((callsign_text, locator_text))
    return normalized_pairs


def _stable_signature(payload: object) -> str:
    """Return a deterministic path-free signature for compact candidate data."""
    serialized = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")
    return sha256(serialized).hexdigest()


def _optional_half_open_marker_window(
    *,
    start_utc: object,
    end_utc: object,
) -> tuple[pd.Timestamp | None, pd.Timestamp | None]:
    """Normalize an optional complete half-open marker-filtering window."""
    if start_utc is None and end_utc is None:
        return None, None
    if start_utc is None or end_utc is None:
        raise ValueError(
            "Qualifying-unit marker filtering requires both start_utc and end_utc."
        )
    window_start = _normalized_utc_timestamp(
        start_utc,
        field="start_utc",
    )
    window_end = _normalized_utc_timestamp(
        end_utc,
        field="end_utc",
    )
    if window_end <= window_start:
        raise ValueError(
            "Qualifying-unit marker filtering requires a positive UTC window."
        )
    return window_start, window_end


def _qualifying_unit_signature_payload(
    qualifying_unit: DeltaSnrOutlierQualifyingUnit,
) -> dict[str, object]:
    """Return one JSON-safe exact qualifying-unit signature projection."""
    return {
        "evidence_utc_ns": int(qualifying_unit.evidence_utc.value),
        "delta_snr_db": float(qualifying_unit.delta_snr_db),
        "residual_db": float(qualifying_unit.residual_db),
        "robust_z": float(qualifying_unit.robust_z),
    }


def _validated_candidate_qualifying_units(
    candidate: DeltaSnrOutlierCandidate,
    *,
    detection_policy: DeltaSnrOutlierDetectionPolicy,
) -> tuple[DeltaSnrOutlierQualifyingUnit, ...]:
    """Validate exact strong anchors without inferring other episode members."""
    qualifying_units = getattr(candidate, "qualifying_units", ())
    if qualifying_units is None:
        return ()
    if not isinstance(qualifying_units, tuple):
        raise ValueError("Candidate qualifying units must use an immutable tuple.")
    if not qualifying_units:
        return ()
    candidate_start = _normalized_utc_timestamp(
        candidate.start_utc,
        field="candidate.start_utc",
    )
    candidate_end = _normalized_utc_timestamp(
        candidate.end_utc,
        field="candidate.end_utc",
    )
    representative_utc = _normalized_utc_timestamp(
        candidate.representative_utc,
        field="candidate.representative_utc",
    )
    candidate_sign = int(np.sign(float(candidate.median_anomaly_db)))
    robust_spread_db = float(candidate.robust_spread_db)
    if candidate_end <= candidate_start or candidate_sign == 0:
        raise ValueError("Candidate qualifying-unit bounds or sign are invalid.")
    if not math.isfinite(robust_spread_db) or robust_spread_db <= 0.0:
        raise ValueError("Candidate qualifying-unit robust spread is invalid.")

    previous_timestamp: pd.Timestamp | None = None
    representative_is_qualifying = False
    validated_units: list[DeltaSnrOutlierQualifyingUnit] = []
    for qualifying_unit in qualifying_units:
        if not isinstance(qualifying_unit, DeltaSnrOutlierQualifyingUnit):
            raise ValueError(
                "Candidate qualifying units contain an unsupported record."
            )
        timestamp = qualifying_unit.evidence_utc
        if not candidate_start <= timestamp < candidate_end:
            raise ValueError(
                "Candidate qualifying-unit time lies outside its episode."
            )
        if previous_timestamp is not None and timestamp <= previous_timestamp:
            raise ValueError(
                "Candidate qualifying units must be strictly chronological."
            )
        previous_timestamp = timestamp
        expected_residual_db = (
            qualifying_unit.delta_snr_db - float(candidate.station_baseline_db)
        )
        expected_robust_z = _robust_z(
            expected_residual_db,
            robust_spread_db,
        )
        if not math.isclose(
            qualifying_unit.residual_db,
            expected_residual_db,
            rel_tol=1e-12,
            abs_tol=1e-9,
        ) or not math.isclose(
            qualifying_unit.robust_z,
            expected_robust_z,
            rel_tol=1e-12,
            abs_tol=1e-9,
        ):
            raise ValueError(
                "Candidate qualifying-unit detector coordinates are inconsistent."
            )
        if (
            int(np.sign(qualifying_unit.residual_db)) != candidate_sign
            or abs(qualifying_unit.residual_db)
            < detection_policy.minimum_departure_db
            or abs(qualifying_unit.robust_z)
            < detection_policy.minimum_robust_z
        ):
            raise ValueError(
                "Candidate qualifying unit does not pass both configured gates."
            )
        if timestamp == representative_utc and math.isclose(
            qualifying_unit.delta_snr_db,
            float(candidate.representative_delta_snr_db),
            rel_tol=1e-12,
            abs_tol=1e-9,
        ):
            representative_is_qualifying = True
        validated_units.append(qualifying_unit)
    if not representative_is_qualifying:
        raise ValueError(
            "Candidate representative is missing from its qualifying native units."
        )
    return tuple(validated_units)


def _qualifying_candidate_event_signature(
    candidate: DeltaSnrOutlierCandidate,
    *,
    detection_policy_signature: str,
) -> str:
    """Fingerprint one path episode for focus-band/marker association."""
    return _stable_signature(
        {
            "callsign": candidate.station_identity.callsign,
            "locator": candidate.station_identity.locator,
            "event_kind": candidate.event_kind,
            "episode_start_utc_ns": int(candidate.start_utc.value),
            "episode_end_utc_ns": int(candidate.end_utc.value),
            "representative_utc_ns": int(candidate.representative_utc.value),
            "representative_delta_snr_db": float(
                candidate.representative_delta_snr_db
            ),
            "station_baseline_db": float(candidate.station_baseline_db),
            "robust_spread_db": float(candidate.robust_spread_db),
            "detection_policy_signature": detection_policy_signature,
            "qualifying_units": [
                _qualifying_unit_signature_payload(qualifying_unit)
                for qualifying_unit in candidate.qualifying_units
            ],
        }
    )


def _optional_finite(value: object) -> float | None:
    """Return one finite float or ``None`` for unavailable diagnostics."""
    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return None
    return numeric_value if math.isfinite(numeric_value) else None


def _candidate_signature(
    candidates: tuple[DeltaSnrOutlierCandidate, ...],
    detection_policy: DeltaSnrOutlierDetectionPolicy,
) -> str:
    """Fingerprint all path-episode values that affect report identity."""
    candidate_payload = [
        {
            "callsign": candidate.station_identity.callsign,
            "locator": candidate.station_identity.locator,
            "direction_sector": candidate.direction_sector,
            "event_kind": candidate.event_kind,
            "start_utc_ns": int(candidate.start_utc.value),
            "end_utc_ns": int(candidate.end_utc.value),
            "baseline_anchor_start_utc_ns": int(
                candidate.baseline_anchor_start_utc.value
            ),
            "baseline_anchor_end_utc_ns": int(
                candidate.baseline_anchor_end_utc.value
            ),
            "episode_guard_minutes": candidate.episode_guard_minutes,
            "representative_utc_ns": int(candidate.representative_utc.value),
            "representative_delta_snr_db": candidate.representative_delta_snr_db,
            "episode_median_delta_snr_db": (
                candidate.episode_median_delta_snr_db
            ),
            "station_baseline_db": candidate.station_baseline_db,
            "pre_baseline_db": candidate.pre_baseline_db,
            "post_baseline_db": candidate.post_baseline_db,
            "median_anomaly_db": candidate.median_anomaly_db,
            "peak_anomaly_db": candidate.peak_anomaly_db,
            "mad_db": candidate.mad_db,
            "robust_spread_db": candidate.robust_spread_db,
            "robust_spread_method": candidate.robust_spread_method,
            "robust_z": candidate.robust_z,
            "pre_flank_cell_count": candidate.pre_flank_cell_count,
            "post_flank_cell_count": candidate.post_flank_cell_count,
            "paired_unit_count": candidate.paired_unit_count,
            "agreeing_paired_unit_count": candidate.agreeing_paired_unit_count,
            "paired_unit_sign_agreement_fraction": (
                candidate.paired_unit_sign_agreement_fraction
            ),
            "observed_span_minutes": candidate.observed_span_minutes,
            "largest_gap_minutes": candidate.largest_gap_minutes,
            "target_median_snr_db": candidate.target_median_snr_db,
            "target_baseline_db": candidate.target_baseline_db,
            "target_anomaly_db": candidate.target_anomaly_db,
            "reference_median_snr_db": candidate.reference_median_snr_db,
            "reference_baseline_db": candidate.reference_baseline_db,
            "reference_anomaly_db": candidate.reference_anomaly_db,
            "path_effective_cadence_minutes": (
                candidate.path_effective_cadence_minutes
            ),
            "maximum_episode_gap_minutes": (
                candidate.maximum_episode_gap_minutes
            ),
            "diagnostic_neighborhood_minutes": (
                candidate.diagnostic_neighborhood_minutes
            ),
            "nearby_joint_unit_count": candidate.nearby_joint_unit_count,
            "nearby_target_only_unit_count": (
                candidate.nearby_target_only_unit_count
            ),
            "nearby_reference_only_unit_count": (
                candidate.nearby_reference_only_unit_count
            ),
            "decode_edge_warning": candidate.decode_edge_warning,
            "decode_edge_warning_reason": candidate.decode_edge_warning_reason,
            "qualifying_units": [
                _qualifying_unit_signature_payload(qualifying_unit)
                for qualifying_unit in candidate.qualifying_units
            ],
        }
        for candidate in candidates
    ]
    return _stable_signature(
        {
            "detection_policy": detection_policy.as_dict(),
            "candidates": candidate_payload,
        }
    )


def _direction_lookup(
    station_directions: Mapping[object, object] | None,
) -> dict[tuple[str, str], str]:
    """Normalize exact identity-to-compass-sector metadata."""
    if not station_directions:
        return {}
    normalized: dict[tuple[str, str], str] = {}
    for identity, direction in station_directions.items():
        try:
            callsign, locator = identity
        except (TypeError, ValueError):
            continue
        direction_text = str(direction).strip().upper()
        if direction_text not in COMPASS:
            continue
        normalized[(str(callsign).strip().upper(), str(locator).strip().upper())] = (
            direction_text
        )
    return normalized


def _robust_flank_spread(
    flank_residuals_db: np.ndarray,
) -> tuple[float, float, str]:
    """Return local MAD with IQR and quantization-aware scale fallbacks."""
    residual_median_db = float(np.median(flank_residuals_db))
    mad_db = float(
        np.median(np.abs(flank_residuals_db - residual_median_db))
    )
    if mad_db > 0.0:
        return mad_db, mad_db, "mad"
    q1_db, q3_db = np.percentile(
        flank_residuals_db,
        [25.0, 75.0],
        method="linear",
    )
    iqr_equivalent_mad_db = float(q3_db - q1_db) / 2.0
    if iqr_equivalent_mad_db > 0.0:
        return mad_db, iqr_equivalent_mad_db, "iqr-equivalent-mad"
    return (
        mad_db,
        DELTA_SNR_OUTLIER_QUANTIZATION_MAD_FLOOR_DB,
        "quantization-floor",
    )


def _robust_z(anomaly_db: float, robust_spread_db: float) -> float:
    """Calculate one finite modified z-score from a supported local scale."""
    if robust_spread_db <= 0.0:
        raise ValueError("Delta-SNR robust spread must be positive.")
    return DELTA_SNR_OUTLIER_MAD_NORMALIZATION * anomaly_db / robust_spread_db


def _sign_counts(anomaly_values: np.ndarray) -> tuple[int, int, int]:
    """Return positive, negative, and exact-neutral path counts."""
    return (
        int((anomaly_values > 0.0).sum()),
        int((anomaly_values < 0.0).sum()),
        int((anomaly_values == 0.0).sum()),
    )


def _sign_summary(anomaly_values: np.ndarray) -> tuple[str | None, int]:
    """Return directional agreement and its largest supporting sign count."""
    if anomaly_values.size == 0:
        return None, 0
    positive_count, negative_count, _neutral_count = _sign_counts(
        anomaly_values
    )
    if positive_count == 0 and negative_count == 0:
        return "neutral", 0
    if negative_count == 0:
        return "positive", positive_count
    if positive_count == 0:
        return "negative", negative_count
    return "mixed", max(positive_count, negative_count)


def _classify_episode(
    paired_unit_count: int,
    observed_span_minutes: float,
) -> str:
    """Classify grouped evidence by duration without changing qualification."""
    if paired_unit_count == 1:
        return OUTLIER_EVENT_SPOT_IMPULSE
    if (
        paired_unit_count >= DELTA_SNR_OUTLIER_SUSTAINED_MINIMUM_UNITS
        and observed_span_minutes
        >= DELTA_SNR_OUTLIER_SUSTAINED_MINIMUM_SPAN_MINUTES
    ):
        return OUTLIER_EVENT_SUSTAINED_EXCURSION
    return OUTLIER_EVENT_SHORT_BURST


def _path_effective_cadence_minutes(
    evidence_times: pd.DatetimeIndex,
    *,
    fallback_cadence_minutes: float,
) -> float:
    """Estimate normal path cadence while excluding outage-sized intervals."""
    unique_times = evidence_times.drop_duplicates().sort_values()
    if len(unique_times) < 2:
        return float(fallback_cadence_minutes)
    interval_minutes = (
        np.diff(unique_times.as_unit("ns").asi8)
        / pd.Timedelta(minutes=1).value
    )
    retained_intervals = interval_minutes[
        np.isfinite(interval_minutes)
        & (interval_minutes > 0.0)
        & (
            interval_minutes
            <= DELTA_SNR_OUTLIER_MAXIMUM_EPISODE_GAP_CAP_MINUTES
        )
    ]
    if (
        retained_intervals.size
        < DELTA_SNR_OUTLIER_MINIMUM_PATH_CADENCE_INTERVALS
    ):
        return float(fallback_cadence_minutes)
    return float(np.median(retained_intervals))


def _maximum_episode_gap_minutes(path_effective_cadence_minutes: float) -> float:
    """Scale same-path grouping to local evidence cadence with a hard cap."""
    return min(
        DELTA_SNR_OUTLIER_MAXIMUM_EPISODE_GAP_CAP_MINUTES,
        max(
            DELTA_SNR_OUTLIER_DEFAULT_MAXIMUM_EPISODE_GAP_MINUTES,
            float(path_effective_cadence_minutes) * 1.5,
        ),
    )


def _pilot_guard_minutes(effective_cadence_minutes: float) -> float:
    """Return a pilot exclusion wide enough for path-effective cadence."""
    return max(
        float(DELTA_SNR_OUTLIER_PILOT_GUARD_MINUTES),
        float(effective_cadence_minutes) * 2.0,
    )


def _episode_guard_minutes(effective_cadence_minutes: float) -> float:
    """Return the guard applied outside the complete provisional episode."""
    return max(
        float(DELTA_SNR_OUTLIER_EPISODE_GUARD_MINUTES),
        float(effective_cadence_minutes),
    )


def _group_signed_member_runs(
    times: pd.DatetimeIndex,
    member_signs: np.ndarray,
    supported_mask: np.ndarray,
    *,
    maximum_gap_minutes: float,
) -> tuple[tuple[int, int, int], ...]:
    """Group runs across one neutral until return, reversal, or outage."""
    if (
        len(times) != int(member_signs.size)
        or len(times) != int(supported_mask.size)
    ):
        raise ValueError(
            "Episode grouping requires aligned times, signs, and support."
        )
    maximum_gap = pd.Timedelta(minutes=maximum_gap_minutes)
    grouped: list[tuple[int, int, int]] = []
    active_start: int | None = None
    active_end: int | None = None
    active_sign = 0
    pending_supported_neutral: int | None = None

    def finish_active() -> None:
        nonlocal active_start, active_end, active_sign, pending_supported_neutral
        if active_start is not None and active_end is not None:
            grouped.append((active_start, active_end, active_sign))
        active_start = None
        active_end = None
        active_sign = 0
        pending_supported_neutral = None

    for index, sign in enumerate(member_signs.astype(np.int8, copy=False)):
        sign_value = int(sign)
        if active_start is None:
            if sign_value:
                active_start = index
                active_end = index
                active_sign = sign_value
            continue
        if times[index] - times[index - 1] > maximum_gap:
            finish_active()
            if sign_value:
                active_start = index
                active_end = index
                active_sign = sign_value
            continue
        if sign_value == active_sign:
            active_end = index
            pending_supported_neutral = None
            continue
        if sign_value == 0 and not bool(supported_mask[index]):
            continue
        if sign_value == 0 and pending_supported_neutral is None:
            pending_supported_neutral = index
            continue
        finish_active()
        if sign_value:
            active_start = index
            active_end = index
            active_sign = sign_value
    finish_active()
    return tuple(grouped)


def _flank_slices(
    cell_times: pd.DatetimeIndex,
    *,
    episode_start_utc: pd.Timestamp,
    episode_end_utc: pd.Timestamp,
    guard_minutes: float,
) -> tuple[slice, slice]:
    """Return bounded candidate-excluded pre/post baseline-cell slices."""
    cell_ns = cell_times.as_unit("ns").asi8
    flank_delta = pd.Timedelta(
        hours=DELTA_SNR_OUTLIER_FLANK_WINDOW_HOURS
    )
    guard_delta = pd.Timedelta(minutes=guard_minutes)
    pre_start = episode_start_utc - flank_delta
    pre_end = episode_start_utc - guard_delta
    post_start = episode_end_utc + guard_delta
    post_end = episode_end_utc + flank_delta
    pre_left = int(np.searchsorted(cell_ns, pre_start.value, side="left"))
    pre_right = int(np.searchsorted(cell_ns, pre_end.value, side="left"))
    post_left = int(np.searchsorted(cell_ns, post_start.value, side="right"))
    post_right = int(np.searchsorted(cell_ns, post_end.value, side="right"))
    return slice(pre_left, pre_right), slice(post_left, post_right)


def _supported_baseline(
    cell_times: pd.DatetimeIndex,
    cell_metrics_db: np.ndarray,
    *,
    episode_start_utc: pd.Timestamp,
    episode_end_utc: pd.Timestamp,
    guard_minutes: float,
    maximum_baseline_difference_db: float,
) -> tuple[float, float, float, np.ndarray, np.ndarray] | None:
    """Return compatible pre/post medians and their exact support arrays."""
    pre_slice, post_slice = _flank_slices(
        cell_times,
        episode_start_utc=episode_start_utc,
        episode_end_utc=episode_end_utc,
        guard_minutes=guard_minutes,
    )
    pre_values_db = cell_metrics_db[pre_slice]
    post_values_db = cell_metrics_db[post_slice]
    if (
        pre_values_db.size < DELTA_SNR_OUTLIER_MINIMUM_FLANK_CELLS
        or post_values_db.size < DELTA_SNR_OUTLIER_MINIMUM_FLANK_CELLS
    ):
        return None
    pre_baseline_db = float(np.median(pre_values_db))
    post_baseline_db = float(np.median(post_values_db))
    if (
        abs(post_baseline_db - pre_baseline_db)
        > maximum_baseline_difference_db
    ):
        return None
    station_baseline_db = float(
        np.median([pre_baseline_db, post_baseline_db])
    )
    return (
        pre_baseline_db,
        post_baseline_db,
        station_baseline_db,
        pre_values_db,
        post_values_db,
    )


def _optional_component_baseline(
    cell_values_db: np.ndarray,
    pre_slice: slice,
    post_slice: slice,
) -> float | None:
    """Return an equal-side component baseline when both flanks are available."""
    pre_values = cell_values_db[pre_slice]
    post_values = cell_values_db[post_slice]
    pre_values = pre_values[np.isfinite(pre_values)]
    post_values = post_values[np.isfinite(post_values)]
    if pre_values.size == 0 or post_values.size == 0:
        return None
    return float(np.median([np.median(pre_values), np.median(post_values)]))


def _pilot_baselines_by_cell(
    cell_times: pd.DatetimeIndex,
    cell_metrics_db: np.ndarray,
    *,
    guard_minutes: float,
    maximum_baseline_difference_db: float,
) -> np.ndarray:
    """Compute scalable pilot baselines once per short support cell."""
    if cell_times.empty:
        return np.asarray([], dtype=float)
    cell_delta = pd.Timedelta(DELTA_SNR_OUTLIER_BASELINE_CELL)
    flank_delta = pd.Timedelta(
        hours=DELTA_SNR_OUTLIER_FLANK_WINDOW_HOURS
    )
    guard_steps = int(pd.Timedelta(minutes=guard_minutes) // cell_delta)
    flank_steps = int(flank_delta // cell_delta)
    flank_support_steps = flank_steps - guard_steps
    if flank_support_steps <= 0:
        return np.full(cell_metrics_db.shape, np.nan, dtype=float)

    full_cell_times = pd.date_range(
        cell_times[0],
        cell_times[-1],
        freq=DELTA_SNR_OUTLIER_BASELINE_CELL,
    )
    full_metrics_db = np.full(len(full_cell_times), np.nan, dtype=float)
    original_cell_positions = (
        (cell_times - full_cell_times[0]) // cell_delta
    ).to_numpy(dtype=np.int64)
    full_metrics_db[original_cell_positions] = cell_metrics_db
    shift_steps = guard_steps + 1

    metric_series = pd.Series(full_metrics_db, copy=False)
    pre_source = metric_series.shift(shift_steps)
    pre_rolling = pre_source.rolling(
        flank_support_steps,
        min_periods=DELTA_SNR_OUTLIER_MINIMUM_FLANK_CELLS,
    )
    pre_medians_db = pre_rolling.median().to_numpy(dtype=float)
    pre_counts = pre_rolling.count().to_numpy(dtype=float)

    reversed_series = pd.Series(full_metrics_db[::-1], copy=False)
    post_source = reversed_series.shift(shift_steps)
    post_rolling = post_source.rolling(
        flank_support_steps,
        min_periods=DELTA_SNR_OUTLIER_MINIMUM_FLANK_CELLS,
    )
    post_medians_db = post_rolling.median().to_numpy(dtype=float)[::-1]
    post_counts = post_rolling.count().to_numpy(dtype=float)[::-1]

    supported_mask = (
        (pre_counts >= DELTA_SNR_OUTLIER_MINIMUM_FLANK_CELLS)
        & (post_counts >= DELTA_SNR_OUTLIER_MINIMUM_FLANK_CELLS)
        & np.isfinite(pre_medians_db)
        & np.isfinite(post_medians_db)
        & (
            np.abs(post_medians_db - pre_medians_db)
            <= maximum_baseline_difference_db
        )
    )
    full_baselines_db = np.full(len(full_cell_times), np.nan, dtype=float)
    full_baselines_db[supported_mask] = np.median(
        np.vstack(
            (
                pre_medians_db[supported_mask],
                post_medians_db[supported_mask],
            )
        ),
        axis=0,
    )
    return full_baselines_db[original_cell_positions]


def _refine_episode_bounds(
    station_times: pd.DatetimeIndex,
    station_metrics_db: np.ndarray,
    cell_times: pd.DatetimeIndex,
    cell_metrics_db: np.ndarray,
    *,
    initial_start_index: int,
    initial_end_index: int,
    episode_sign: int,
    maximum_gap_minutes: float,
    guard_minutes: float,
    maximum_baseline_difference_db: float,
) -> tuple[int, int, tuple[float, float, float, np.ndarray, np.ndarray]] | None:
    """Refine shoulders against a baseline excluding the complete episode."""
    maximum_gap = pd.Timedelta(minutes=maximum_gap_minutes)
    start_index = int(initial_start_index)
    end_index = int(initial_end_index)
    supported = None
    for _pass_index in range(DELTA_SNR_OUTLIER_MAXIMUM_REFINEMENT_PASSES):
        supported = _supported_baseline(
            cell_times,
            cell_metrics_db,
            episode_start_utc=station_times[start_index],
            episode_end_utc=station_times[end_index],
            guard_minutes=guard_minutes,
            maximum_baseline_difference_db=maximum_baseline_difference_db,
        )
        if supported is None:
            return None
        station_baseline_db = supported[2]
        changed = False
        if start_index > 0:
            previous_residual = (
                station_metrics_db[start_index - 1] - station_baseline_db
            )
            if (
                station_times[start_index] - station_times[start_index - 1]
                <= maximum_gap
                and np.sign(previous_residual) == episode_sign
                and abs(previous_residual)
                >= DELTA_SNR_OUTLIER_MINIMUM_MEMBER_ANOMALY_DB
            ):
                start_index -= 1
                changed = True
        if end_index + 1 < len(station_times):
            next_residual = station_metrics_db[end_index + 1] - station_baseline_db
            if (
                station_times[end_index + 1] - station_times[end_index]
                <= maximum_gap
                and np.sign(next_residual) == episode_sign
                and abs(next_residual)
                >= DELTA_SNR_OUTLIER_MINIMUM_MEMBER_ANOMALY_DB
            ):
                end_index += 1
                changed = True
        if not changed:
            return start_index, end_index, supported
    supported = _supported_baseline(
        cell_times,
        cell_metrics_db,
        episode_start_utc=station_times[start_index],
        episode_end_utc=station_times[end_index],
        guard_minutes=guard_minutes,
        maximum_baseline_difference_db=maximum_baseline_difference_db,
    )
    if supported is None:
        return None
    return start_index, end_index, supported


def _final_baseline_member_runs(
    station_times: pd.DatetimeIndex,
    station_metrics_db: np.ndarray,
    *,
    start_index: int,
    end_index: int,
    episode_sign: int,
    station_baseline_db: float,
    maximum_gap_minutes: float,
    minimum_member_anomaly_db: float,
) -> tuple[tuple[int, int], ...]:
    """Split one failed provisional group at final-baseline returns.

    Pilot grouping may bridge one supported neutral unit so moderate sustained
    evidence is not fragmented prematurely. Once the complete provisional
    group has supplied a candidate-excluded baseline, this stricter fallback
    retains only contiguous same-sign shoulders. It is used only when the
    complete group fails the unchanged qualification gates.
    """
    maximum_gap = pd.Timedelta(minutes=maximum_gap_minutes)
    member_runs: list[tuple[int, int]] = []
    active_start: int | None = None
    active_end: int | None = None

    def finish_active() -> None:
        nonlocal active_start, active_end
        if active_start is not None and active_end is not None:
            member_runs.append((active_start, active_end))
        active_start = None
        active_end = None

    for index in range(int(start_index), int(end_index) + 1):
        residual_db = float(station_metrics_db[index] - station_baseline_db)
        is_same_sign_member = (
            np.sign(residual_db) == episode_sign
            and abs(residual_db) >= minimum_member_anomaly_db
        )
        if not is_same_sign_member:
            finish_active()
            continue
        if (
            active_end is not None
            and station_times[index] - station_times[active_end]
            > maximum_gap
        ):
            finish_active()
        if active_start is None:
            active_start = index
        active_end = index
    finish_active()
    return tuple(member_runs)


def _component_episode_values(
    station_component_db: np.ndarray,
    cell_component_db: np.ndarray,
    *,
    start_index: int,
    end_index: int,
    pre_slice: slice,
    post_slice: slice,
) -> tuple[float | None, float | None, float | None]:
    """Return episode median, local baseline, and departure for one SNR side."""
    episode_values = station_component_db[start_index : end_index + 1]
    episode_values = episode_values[np.isfinite(episode_values)]
    episode_median = (
        float(np.median(episode_values)) if episode_values.size else None
    )
    baseline = _optional_component_baseline(
        cell_component_db,
        pre_slice,
        post_slice,
    )
    anomaly = (
        float(episode_median - baseline)
        if episode_median is not None and baseline is not None
        else None
    )
    return episode_median, baseline, anomaly


def _candidate_from_supported_episode(
    *,
    identity: OutlierStationIdentity,
    direction_sector: str | None,
    station_times: pd.DatetimeIndex,
    station_metrics_db: np.ndarray,
    station_target_db: np.ndarray,
    station_reference_db: np.ndarray,
    cell_times: pd.DatetimeIndex,
    cell_metrics_db: np.ndarray,
    cell_target_db: np.ndarray,
    cell_reference_db: np.ndarray,
    start_index: int,
    end_index: int,
    baseline_start_utc: pd.Timestamp,
    baseline_end_utc: pd.Timestamp,
    supported_baseline: tuple[
        float,
        float,
        float,
        np.ndarray,
        np.ndarray,
    ],
    episode_sign: int,
    path_effective_cadence_minutes: float,
    maximum_gap_minutes: float,
    episode_guard_minutes: float,
    detection_policy: DeltaSnrOutlierDetectionPolicy,
) -> DeltaSnrOutlierCandidate | None:
    """Apply unchanged qualification gates using one supported baseline."""
    (
        pre_baseline_db,
        post_baseline_db,
        station_baseline_db,
        pre_values_db,
        post_values_db,
    ) = supported_baseline
    episode_metrics_db = station_metrics_db[start_index : end_index + 1]
    episode_times = station_times[start_index : end_index + 1]
    residuals_db = episode_metrics_db - station_baseline_db
    paired_unit_count = int(residuals_db.size)
    observed_span_minutes = float(
        (episode_times[-1] - episode_times[0]) / pd.Timedelta(minutes=1)
    )
    gap_minutes = (
        np.diff(episode_times.as_unit("ns").asi8)
        / pd.Timedelta(minutes=1).value
    )
    largest_gap_minutes = float(np.max(gap_minutes)) if gap_minutes.size else 0.0
    event_kind = _classify_episode(
        paired_unit_count,
        observed_span_minutes,
    )
    if largest_gap_minutes > maximum_gap_minutes:
        return None

    episode_median_delta_snr_db = float(np.median(episode_metrics_db))
    median_anomaly_db = episode_median_delta_snr_db - station_baseline_db
    if np.sign(median_anomaly_db) != episode_sign:
        return None
    agreeing_paired_unit_count = int(
        ((residuals_db > 0.0) if episode_sign > 0 else (residuals_db < 0.0)).sum()
    )
    sign_agreement_fraction = agreeing_paired_unit_count / paired_unit_count
    flank_residuals_db = np.concatenate(
        (
            pre_values_db - pre_baseline_db,
            post_values_db - post_baseline_db,
        )
    )
    mad_db, robust_spread_db, robust_spread_method = _robust_flank_spread(
        flank_residuals_db
    )
    robust_z = _robust_z(median_anomaly_db, robust_spread_db)
    if (
        abs(median_anomaly_db)
        < detection_policy.minimum_departure_db
        or abs(robust_z) < detection_policy.minimum_robust_z
        or sign_agreement_fraction
        < DELTA_SNR_OUTLIER_MINIMUM_SIGN_AGREEMENT_FRACTION
    ):
        return None

    native_robust_z_scores = (
        DELTA_SNR_OUTLIER_MAD_NORMALIZATION
        * residuals_db
        / robust_spread_db
    )
    qualifying_unit_mask = (
        (np.sign(residuals_db) == episode_sign)
        & (
            np.abs(residuals_db)
            >= detection_policy.minimum_departure_db
        )
        & (
            np.abs(native_robust_z_scores)
            >= detection_policy.minimum_robust_z
        )
    )
    qualifying_unit_positions = np.flatnonzero(qualifying_unit_mask)
    qualifying_units = tuple(
        DeltaSnrOutlierQualifyingUnit(
            evidence_utc=episode_times[relative_index],
            delta_snr_db=float(episode_metrics_db[relative_index]),
            residual_db=float(residuals_db[relative_index]),
            robust_z=float(native_robust_z_scores[relative_index]),
        )
        for relative_index in qualifying_unit_positions
    )
    if not qualifying_units:
        return None

    representative_relative_index = int(
        qualifying_unit_positions[
            np.argmax(np.abs(residuals_db[qualifying_unit_positions]))
        ]
    )
    representative_index = start_index + representative_relative_index
    peak_anomaly_db = float(residuals_db[np.argmax(np.abs(residuals_db))])
    pre_slice, post_slice = _flank_slices(
        cell_times,
        episode_start_utc=baseline_start_utc,
        episode_end_utc=baseline_end_utc,
        guard_minutes=episode_guard_minutes,
    )
    target_median, target_baseline, target_anomaly = _component_episode_values(
        station_target_db,
        cell_target_db,
        start_index=start_index,
        end_index=end_index,
        pre_slice=pre_slice,
        post_slice=post_slice,
    )
    reference_median, reference_baseline, reference_anomaly = (
        _component_episode_values(
            station_reference_db,
            cell_reference_db,
            start_index=start_index,
            end_index=end_index,
            pre_slice=pre_slice,
            post_slice=post_slice,
        )
    )
    return DeltaSnrOutlierCandidate(
        station_identity=identity,
        direction_sector=direction_sector,
        event_kind=event_kind,
        start_utc=episode_times[0],
        end_utc=episode_times[-1] + pd.Timedelta(nanoseconds=1),
        baseline_anchor_start_utc=baseline_start_utc,
        baseline_anchor_end_utc=baseline_end_utc,
        episode_guard_minutes=float(episode_guard_minutes),
        representative_utc=station_times[representative_index],
        representative_delta_snr_db=float(
            station_metrics_db[representative_index]
        ),
        episode_median_delta_snr_db=episode_median_delta_snr_db,
        station_baseline_db=station_baseline_db,
        pre_baseline_db=pre_baseline_db,
        post_baseline_db=post_baseline_db,
        median_anomaly_db=median_anomaly_db,
        peak_anomaly_db=peak_anomaly_db,
        mad_db=mad_db,
        robust_spread_db=robust_spread_db,
        robust_spread_method=robust_spread_method,
        robust_z=robust_z,
        pre_flank_cell_count=int(pre_values_db.size),
        post_flank_cell_count=int(post_values_db.size),
        paired_unit_count=paired_unit_count,
        agreeing_paired_unit_count=agreeing_paired_unit_count,
        paired_unit_sign_agreement_fraction=sign_agreement_fraction,
        observed_span_minutes=observed_span_minutes,
        largest_gap_minutes=largest_gap_minutes,
        target_median_snr_db=target_median,
        target_baseline_db=target_baseline,
        target_anomaly_db=target_anomaly,
        reference_median_snr_db=reference_median,
        reference_baseline_db=reference_baseline,
        reference_anomaly_db=reference_anomaly,
        qualifying_units=qualifying_units,
        path_effective_cadence_minutes=float(
            path_effective_cadence_minutes
        ),
        maximum_episode_gap_minutes=float(maximum_gap_minutes),
    )


def _strong_anchor_trimmed_candidate(
    *,
    identity: OutlierStationIdentity,
    direction_sector: str | None,
    station_times: pd.DatetimeIndex,
    station_metrics_db: np.ndarray,
    station_target_db: np.ndarray,
    station_reference_db: np.ndarray,
    cell_times: pd.DatetimeIndex,
    cell_metrics_db: np.ndarray,
    cell_target_db: np.ndarray,
    cell_reference_db: np.ndarray,
    start_index: int,
    end_index: int,
    baseline_start_utc: pd.Timestamp,
    baseline_end_utc: pd.Timestamp,
    supported_baseline: tuple[
        float,
        float,
        float,
        np.ndarray,
        np.ndarray,
    ],
    episode_sign: int,
    path_effective_cadence_minutes: float,
    maximum_gap_minutes: float,
    episode_guard_minutes: float,
    detection_policy: DeltaSnrOutlierDetectionPolicy,
) -> DeltaSnrOutlierCandidate | None:
    """Qualify an interval, then anchor its bounds to individually strong units."""
    candidate_arguments = {
        "identity": identity,
        "direction_sector": direction_sector,
        "station_times": station_times,
        "station_metrics_db": station_metrics_db,
        "station_target_db": station_target_db,
        "station_reference_db": station_reference_db,
        "cell_times": cell_times,
        "cell_metrics_db": cell_metrics_db,
        "cell_target_db": cell_target_db,
        "cell_reference_db": cell_reference_db,
        "baseline_start_utc": baseline_start_utc,
        "baseline_end_utc": baseline_end_utc,
        "supported_baseline": supported_baseline,
        "episode_sign": episode_sign,
        "path_effective_cadence_minutes": path_effective_cadence_minutes,
        "maximum_gap_minutes": maximum_gap_minutes,
        "episode_guard_minutes": episode_guard_minutes,
        "detection_policy": detection_policy,
    }
    complete_candidate = _candidate_from_supported_episode(
        **candidate_arguments,
        start_index=start_index,
        end_index=end_index,
    )
    if complete_candidate is None:
        return None

    residuals_db = (
        station_metrics_db[start_index : end_index + 1]
        - supported_baseline[2]
    )
    robust_z_scores = (
        DELTA_SNR_OUTLIER_MAD_NORMALIZATION
        * residuals_db
        / complete_candidate.robust_spread_db
    )
    strong_anchor_mask = (
        (np.sign(residuals_db) == episode_sign)
        & (np.abs(residuals_db) >= detection_policy.minimum_departure_db)
        & (np.abs(robust_z_scores) >= detection_policy.minimum_robust_z)
    )
    strong_anchor_positions = np.flatnonzero(strong_anchor_mask)
    if strong_anchor_positions.size == 0:
        return None
    trimmed_start_index = start_index + int(strong_anchor_positions[0])
    trimmed_end_index = start_index + int(strong_anchor_positions[-1])
    if trimmed_start_index == start_index and trimmed_end_index == end_index:
        return complete_candidate
    return _candidate_from_supported_episode(
        **candidate_arguments,
        start_index=trimmed_start_index,
        end_index=trimmed_end_index,
    )


def _qualified_episode_candidates(
    *,
    identity: OutlierStationIdentity,
    direction_sector: str | None,
    station_times: pd.DatetimeIndex,
    station_metrics_db: np.ndarray,
    station_target_db: np.ndarray,
    station_reference_db: np.ndarray,
    cell_times: pd.DatetimeIndex,
    cell_metrics_db: np.ndarray,
    cell_target_db: np.ndarray,
    cell_reference_db: np.ndarray,
    start_index: int,
    end_index: int,
    episode_sign: int,
    path_effective_cadence_minutes: float,
    maximum_gap_minutes: float,
    episode_guard_minutes: float,
    detection_policy: DeltaSnrOutlierDetectionPolicy,
) -> tuple[tuple[DeltaSnrOutlierCandidate, ...], int | None]:
    """Qualify a refined group, rescuing disjoint cores only after it fails."""
    refined_episode = _refine_episode_bounds(
        station_times,
        station_metrics_db,
        cell_times,
        cell_metrics_db,
        initial_start_index=start_index,
        initial_end_index=end_index,
        episode_sign=episode_sign,
        maximum_gap_minutes=maximum_gap_minutes,
        guard_minutes=episode_guard_minutes,
        maximum_baseline_difference_db=(
            detection_policy.maximum_baseline_difference_db
        ),
    )
    if refined_episode is None:
        return (), None
    refined_start_index, refined_end_index, supported_baseline = refined_episode
    baseline_start_utc = station_times[refined_start_index]
    baseline_end_utc = station_times[refined_end_index]

    shared_candidate_arguments = {
        "identity": identity,
        "direction_sector": direction_sector,
        "station_times": station_times,
        "station_metrics_db": station_metrics_db,
        "station_target_db": station_target_db,
        "station_reference_db": station_reference_db,
        "cell_times": cell_times,
        "cell_metrics_db": cell_metrics_db,
        "cell_target_db": cell_target_db,
        "cell_reference_db": cell_reference_db,
        "baseline_start_utc": baseline_start_utc,
        "baseline_end_utc": baseline_end_utc,
        "supported_baseline": supported_baseline,
        "episode_sign": episode_sign,
        "path_effective_cadence_minutes": path_effective_cadence_minutes,
        "maximum_gap_minutes": maximum_gap_minutes,
        "episode_guard_minutes": episode_guard_minutes,
        "detection_policy": detection_policy,
    }
    complete_candidate = _strong_anchor_trimmed_candidate(
        **shared_candidate_arguments,
        start_index=refined_start_index,
        end_index=refined_end_index,
    )
    if complete_candidate is not None:
        return (complete_candidate,), refined_end_index

    minimum_member_anomaly_db = min(
        DELTA_SNR_OUTLIER_MINIMUM_MEMBER_ANOMALY_DB,
        detection_policy.minimum_departure_db,
    )
    member_runs = _final_baseline_member_runs(
        station_times,
        station_metrics_db,
        start_index=refined_start_index,
        end_index=refined_end_index,
        episode_sign=episode_sign,
        station_baseline_db=supported_baseline[2],
        maximum_gap_minutes=maximum_gap_minutes,
        minimum_member_anomaly_db=minimum_member_anomaly_db,
    )
    rescued_candidates: list[DeltaSnrOutlierCandidate] = []
    for member_start_index, member_end_index in member_runs:
        if (
            member_start_index == refined_start_index
            and member_end_index == refined_end_index
        ):
            continue
        member_candidate = _strong_anchor_trimmed_candidate(
            **shared_candidate_arguments,
            start_index=member_start_index,
            end_index=member_end_index,
        )
        if member_candidate is not None:
            rescued_candidates.append(member_candidate)
    if not rescued_candidates:
        return (), None
    return tuple(rescued_candidates), refined_end_index


def _eligible_outcome_diagnostic_units(
    comparison_units: pd.DataFrame,
    *,
    analysis_start_utc: pd.Timestamp,
    analysis_end_utc: pd.Timestamp,
) -> pd.DataFrame:
    """Return normalized retained outcomes eligible for episode diagnostics."""
    diagnostic_units = comparison_units.loc[
        comparison_units["paired_eligible"].fillna(False),
        ["peer_sign", "peer_grid", "evidence_utc", "outcome"],
    ].copy()
    diagnostic_units["evidence_utc"] = pd.to_datetime(
        diagnostic_units["evidence_utc"],
        utc=True,
        errors="coerce",
    )
    diagnostic_units = diagnostic_units[
        diagnostic_units["peer_sign"].notna()
        & diagnostic_units["peer_grid"].notna()
        & diagnostic_units["evidence_utc"].notna()
        & diagnostic_units["evidence_utc"].ge(analysis_start_utc)
        & diagnostic_units["evidence_utc"].lt(analysis_end_utc)
        & diagnostic_units["outcome"].isin(
            (
                COMPARE_OUTCOME_JOINT,
                COMPARE_OUTCOME_TARGET_ONLY,
                COMPARE_OUTCOME_REFERENCE_ONLY,
            )
        )
    ].copy()
    if diagnostic_units.empty:
        return diagnostic_units
    diagnostic_units["peer_sign"] = (
        diagnostic_units["peer_sign"].astype(str).str.strip().str.upper()
    )
    diagnostic_units["peer_grid"] = (
        diagnostic_units["peer_grid"].astype(str).str.strip().str.upper()
    )
    diagnostic_units = diagnostic_units[
        diagnostic_units["peer_sign"].ne("")
        & diagnostic_units["peer_grid"].ne("")
        & diagnostic_units["peer_sign"].map(is_valid_callsign)
        & diagnostic_units["peer_grid"].map(is_valid_locator)
    ]
    return (
        diagnostic_units.drop_duplicates(
            subset=["peer_sign", "peer_grid", "evidence_utc", "outcome"]
        )
        .sort_values(["peer_sign", "peer_grid", "evidence_utc", "outcome"])
        .reset_index(drop=True)
    )


def _with_nearby_outcome_diagnostics(
    candidate: DeltaSnrOutlierCandidate,
    diagnostic_units: pd.DataFrame,
) -> DeltaSnrOutlierCandidate:
    """Attach nearby retained-outcome counts without altering qualification."""
    neighborhood_minutes = candidate.maximum_episode_gap_minutes
    neighborhood = pd.Timedelta(minutes=neighborhood_minutes)
    nearby_units = diagnostic_units[
        diagnostic_units["peer_sign"].eq(candidate.station_identity.callsign)
        & diagnostic_units["peer_grid"].eq(candidate.station_identity.locator)
        & diagnostic_units["evidence_utc"].between(
            candidate.start_utc - neighborhood,
            candidate.end_utc + neighborhood,
            inclusive="both",
        )
    ]
    outcome_counts = nearby_units["outcome"].value_counts()
    nearby_joint_unit_count = int(
        outcome_counts.get(COMPARE_OUTCOME_JOINT, 0)
    )
    nearby_target_only_unit_count = int(
        outcome_counts.get(COMPARE_OUTCOME_TARGET_ONLY, 0)
    )
    nearby_reference_only_unit_count = int(
        outcome_counts.get(COMPARE_OUTCOME_REFERENCE_ONLY, 0)
    )
    warning_reason = None
    if (
        candidate.median_anomaly_db > 0.0
        and nearby_target_only_unit_count > 0
    ):
        warning_reason = (
            OUTLIER_DECODE_EDGE_REFERENCE_MISSING_NEAR_POSITIVE_EPISODE
        )
    elif (
        candidate.median_anomaly_db < 0.0
        and nearby_reference_only_unit_count > 0
    ):
        warning_reason = (
            OUTLIER_DECODE_EDGE_TARGET_MISSING_NEAR_NEGATIVE_EPISODE
        )
    return replace(
        candidate,
        diagnostic_neighborhood_minutes=float(neighborhood_minutes),
        nearby_joint_unit_count=nearby_joint_unit_count,
        nearby_target_only_unit_count=nearby_target_only_unit_count,
        nearby_reference_only_unit_count=nearby_reference_only_unit_count,
        decode_edge_warning=warning_reason is not None,
        decode_edge_warning_reason=warning_reason,
    )


def _coherence_scope(
    candidates: tuple[DeltaSnrOutlierCandidate, ...],
) -> str:
    """Classify path breadth without claiming statistical independence."""
    identities = tuple(
        dict.fromkeys(candidate.station_identity for candidate in candidates)
    )
    if len(identities) <= 1:
        return OUTLIER_SCOPE_PATH_SPECIFIC
    direction_by_identity = {
        candidate.station_identity: candidate.direction_sector
        for candidate in candidates
    }
    if any(
        direction_by_identity.get(identity) not in COMPASS
        for identity in identities
    ):
        return OUTLIER_SCOPE_MULTIPLE_PATHS
    sector_indexes = [
        COMPASS.index(str(direction_by_identity[identity]))
        for identity in identities
    ]
    compass_count = len(COMPASS)
    all_adjacent = all(
        min(
            (left_index - right_index) % compass_count,
            (right_index - left_index) % compass_count,
        )
        <= 1
        for left_index in sector_indexes
        for right_index in sector_indexes
    )
    return (
        OUTLIER_SCOPE_DIRECTIONALLY_COHERENT
        if all_adjacent
        else OUTLIER_SCOPE_SCOPE_WIDE
    )


def _sector_summaries(
    *,
    candidates: tuple[DeltaSnrOutlierCandidate, ...],
    contributing_directions: Mapping[OutlierStationIdentity, str | None],
    evaluation_anomalies: Mapping[OutlierStationIdentity, float],
) -> tuple[DeltaSnrOutlierSectorSummary, ...]:
    """Build direction summaries from one contemporaneous review interval."""
    candidate_counts: dict[str, int] = {}
    for candidate in candidates:
        if candidate.direction_sector in COMPASS:
            candidate_counts[str(candidate.direction_sector)] = (
                candidate_counts.get(str(candidate.direction_sector), 0) + 1
            )
    summaries: list[DeltaSnrOutlierSectorSummary] = []
    for direction_sector in COMPASS:
        populated_identities = {
            identity
            for identity, direction in contributing_directions.items()
            if direction == direction_sector
        }
        if not populated_identities:
            continue
        anomaly_values = np.asarray(
            [
                anomaly
                for identity, anomaly in evaluation_anomalies.items()
                if identity in populated_identities
            ],
            dtype=float,
        )
        sign_agreement, agreeing_count = _sign_summary(anomaly_values)
        positive_count, negative_count, neutral_count = _sign_counts(
            anomaly_values
        )
        summaries.append(
            DeltaSnrOutlierSectorSummary(
                direction_sector=direction_sector,
                populated_station_count=len(populated_identities),
                evaluable_station_count=int(anomaly_values.size),
                candidate_station_count=int(
                    candidate_counts.get(direction_sector, 0)
                ),
                median_signed_anomaly_db=(
                    float(np.median(anomaly_values))
                    if anomaly_values.size
                    else None
                ),
                sign_agreement=sign_agreement,
                agreeing_count=agreeing_count,
                positive_station_count=positive_count,
                negative_station_count=negative_count,
                neutral_station_count=neutral_count,
            )
        )
    return tuple(summaries)


def _group_contemporaneous_candidates(
    candidates: tuple[DeltaSnrOutlierCandidate, ...],
    *,
    coherence_tolerance_minutes: float,
) -> tuple[tuple[DeltaSnrOutlierCandidate, ...], ...]:
    """Group overlapping or nearby same-sign path episodes for context."""
    tolerance = pd.Timedelta(minutes=coherence_tolerance_minutes)
    grouped: list[tuple[DeltaSnrOutlierCandidate, ...]] = []
    for episode_sign in (1, -1):
        sign_candidates = sorted(
            (
                candidate
                for candidate in candidates
                if np.sign(candidate.median_anomaly_db) == episode_sign
            ),
            key=lambda candidate: (
                candidate.start_utc,
                candidate.end_utc,
                candidate.station_identity.callsign,
                candidate.station_identity.locator,
            ),
        )
        current: list[DeltaSnrOutlierCandidate] = []
        current_end: pd.Timestamp | None = None
        for candidate in sign_candidates:
            if current and current_end is not None:
                if candidate.start_utc > current_end + tolerance:
                    grouped.append(tuple(current))
                    current = []
                    current_end = None
            current.append(candidate)
            current_end = (
                candidate.end_utc
                if current_end is None
                else max(current_end, candidate.end_utc)
            )
        if current:
            grouped.append(tuple(current))
    return tuple(
        sorted(
            grouped,
            key=lambda group: (
                min(candidate.start_utc for candidate in group),
                -int(np.sign(group[0].median_anomaly_db)),
            ),
        )
    )


def _report_entries(
    candidates: tuple[DeltaSnrOutlierCandidate, ...],
    paired_units: pd.DataFrame,
    *,
    normalized_directions: Mapping[tuple[str, str], str],
    coherence_tolerance_minutes: float,
) -> tuple[DeltaSnrOutlierReportEntry, ...]:
    """Aggregate qualified path episodes into same-sign review cards."""
    grouped_candidates = _group_contemporaneous_candidates(
        candidates,
        coherence_tolerance_minutes=coherence_tolerance_minutes,
    )
    tolerance = pd.Timedelta(minutes=coherence_tolerance_minutes)
    entries: list[DeltaSnrOutlierReportEntry] = []
    for episode_index, episode_candidates in enumerate(grouped_candidates):
        start_utc = min(candidate.start_utc for candidate in episode_candidates)
        end_utc = max(candidate.end_utc for candidate in episode_candidates)
        context_start = start_utc - tolerance
        context_end = end_utc + tolerance
        context_units = paired_units[
            paired_units["evidence_utc"].between(
                context_start,
                context_end,
                inclusive="both",
            )
        ]
        contributing_identities = tuple(
            OutlierStationIdentity(str(callsign), str(locator))
            for callsign, locator in context_units[
                ["peer_sign", "peer_grid"]
            ].drop_duplicates().itertuples(index=False, name=None)
        )
        context_evaluations = context_units[
            np.isfinite(context_units["pilot_anomaly_db"].to_numpy(dtype=float))
        ]
        candidate_anomalies_by_identity: dict[
            OutlierStationIdentity,
            list[float],
        ] = {}
        for candidate in episode_candidates:
            candidate_anomalies_by_identity.setdefault(
                candidate.station_identity,
                [],
            ).append(candidate.median_anomaly_db)
        evaluation_anomalies = {
            identity: float(np.median(values))
            for identity, values in candidate_anomalies_by_identity.items()
        }
        representative_times_ns = np.asarray(
            [candidate.representative_utc.value for candidate in episode_candidates],
            dtype=np.int64,
        )
        nearest_evaluations: dict[
            OutlierStationIdentity,
            tuple[int, float],
        ] = {}
        for evaluation in context_evaluations.itertuples(index=False):
            evaluation_identity = OutlierStationIdentity(
                str(evaluation.peer_sign),
                str(evaluation.peer_grid),
            )
            if evaluation_identity in evaluation_anomalies:
                continue
            distance_ns = int(
                np.min(
                    np.abs(
                        representative_times_ns
                        - pd.Timestamp(evaluation.evidence_utc).value
                    )
                )
            )
            previous = nearest_evaluations.get(evaluation_identity)
            if previous is None or distance_ns < previous[0]:
                nearest_evaluations[evaluation_identity] = (
                    distance_ns,
                    float(evaluation.pilot_anomaly_db),
                )
        evaluation_anomalies.update(
            {
                identity: float(distance_and_anomaly[1])
                for identity, distance_and_anomaly in nearest_evaluations.items()
            }
        )
        contributing_directions = {
            identity: normalized_directions.get(
                (identity.callsign, identity.locator)
            )
            for identity in contributing_identities
        }
        segment_anomalies = np.asarray(
            list(evaluation_anomalies.values()),
            dtype=float,
        )
        segment_sign_agreement, segment_agreeing_count = _sign_summary(
            segment_anomalies
        )
        positive_count, negative_count, neutral_count = _sign_counts(
            segment_anomalies
        )
        candidate_anomalies = np.asarray(
            [candidate.median_anomaly_db for candidate in episode_candidates],
            dtype=float,
        )
        candidate_sign_agreement, candidate_agreeing_count = _sign_summary(
            candidate_anomalies
        )
        maximum_candidate = max(
            episode_candidates,
            key=lambda candidate: abs(candidate.peak_anomaly_db),
        )
        station_identities = tuple(
            dict.fromkeys(
                candidate.station_identity for candidate in episode_candidates
            )
        )
        direction_sectors = tuple(
            direction
            for direction in COMPASS
            if any(
                candidate.direction_sector == direction
                for candidate in episode_candidates
            )
        )
        event_kinds = tuple(
            dict.fromkeys(
                candidate.event_kind for candidate in episode_candidates
            )
        )
        entries.append(
            DeltaSnrOutlierReportEntry(
                episode_index=episode_index,
                start_utc=start_utc,
                end_utc=end_utc,
                event_kind=(
                    event_kinds[0]
                    if len(event_kinds) == 1
                    else OUTLIER_EVENT_MIXED_DURATION
                ),
                coherence_scope=_coherence_scope(episode_candidates),
                contributing_station_count=len(contributing_identities),
                evaluable_station_count=len(evaluation_anomalies),
                candidates=episode_candidates,
                median_signed_anomaly_db=float(
                    np.median(candidate_anomalies)
                ),
                maximum_absolute_anomaly_db=float(
                    abs(maximum_candidate.peak_anomaly_db)
                ),
                maximum_anomaly_db=float(maximum_candidate.peak_anomaly_db),
                sign_agreement=str(candidate_sign_agreement),
                agreeing_count=candidate_agreeing_count,
                segment_median_signed_anomaly_db=float(
                    np.median(segment_anomalies)
                ),
                segment_sign_agreement=str(segment_sign_agreement),
                segment_agreeing_count=segment_agreeing_count,
                segment_positive_station_count=positive_count,
                segment_negative_station_count=negative_count,
                segment_neutral_station_count=neutral_count,
                direction_sectors=direction_sectors,
                sector_summaries=_sector_summaries(
                    candidates=episode_candidates,
                    contributing_directions=contributing_directions,
                    evaluation_anomalies=evaluation_anomalies,
                ),
                station_identities=station_identities,
            )
        )
    return tuple(entries)


def _empty_model(
    analysis_start_utc: pd.Timestamp,
    analysis_end_utc: pd.Timestamp,
    *,
    paired_unit_cadence_minutes: float,
    detection_policy: DeltaSnrOutlierDetectionPolicy,
) -> DeltaSnrOutlierModel:
    """Return the enabled detector's immutable empty-result contract."""
    return DeltaSnrOutlierModel(
        detector_version=DELTA_SNR_OUTLIER_DETECTOR_VERSION,
        detection_resolution=DELTA_SNR_OUTLIER_DETECTION_RESOLUTION,
        paired_unit_cadence_minutes=paired_unit_cadence_minutes,
        analysis_start_utc=analysis_start_utc,
        analysis_end_utc=analysis_end_utc,
        populated_station_cycle_count=0,
        evaluable_station_cycle_count=0,
        abstained_station_cycle_count=0,
        candidates=(),
        report_entries=(),
        candidate_signature=_candidate_signature((), detection_policy),
        detection_policy=detection_policy,
    )


def prepare_delta_snr_outlier_model(
    enabled: bool,
    comparison_units: pd.DataFrame,
    *,
    analysis_start_utc: object,
    analysis_end_utc: object,
    station_directions: Mapping[object, object] | None = None,
    paired_unit_cadence_minutes: float = 2.0,
    detection_policy: DeltaSnrOutlierDetectionPolicy = (
        DEFAULT_DELTA_SNR_OUTLIER_DETECTION_POLICY
    ),
) -> DeltaSnrOutlierModel | None:
    """Return immediately when disabled; otherwise invoke the detector once."""
    if not enabled:
        return None
    return detect_delta_snr_outlier_candidates(
        comparison_units,
        analysis_start_utc=analysis_start_utc,
        analysis_end_utc=analysis_end_utc,
        station_directions=station_directions,
        paired_unit_cadence_minutes=paired_unit_cadence_minutes,
        detection_policy=detection_policy,
    )


def detect_delta_snr_outlier_candidates(
    comparison_units: pd.DataFrame,
    *,
    analysis_start_utc: object,
    analysis_end_utc: object,
    station_directions: Mapping[object, object] | None = None,
    paired_unit_cadence_minutes: float = 2.0,
    detection_policy: DeltaSnrOutlierDetectionPolicy = (
        DEFAULT_DELTA_SNR_OUTLIER_DETECTION_POLICY
    ),
) -> DeltaSnrOutlierModel:
    """Detect native-cycle residual episodes with one shared gate policy."""
    if not isinstance(detection_policy, DeltaSnrOutlierDetectionPolicy):
        raise TypeError(
            "detection_policy must be a DeltaSnrOutlierDetectionPolicy."
        )
    analysis_start = _normalized_utc_timestamp(
        analysis_start_utc,
        field="analysis_start_utc",
    )
    analysis_end = _normalized_utc_timestamp(
        analysis_end_utc,
        field="analysis_end_utc",
    )
    if analysis_end <= analysis_start:
        raise ValueError("Delta-SNR outlier detection requires a positive UTC window.")
    try:
        cadence_minutes = float(paired_unit_cadence_minutes)
    except (TypeError, ValueError) as exc:
        raise ValueError("paired_unit_cadence_minutes must be positive.") from exc
    if not math.isfinite(cadence_minutes) or cadence_minutes <= 0.0:
        raise ValueError("paired_unit_cadence_minutes must be positive.")
    empty_model = _empty_model(
        analysis_start,
        analysis_end,
        paired_unit_cadence_minutes=cadence_minutes,
        detection_policy=detection_policy,
    )
    required_scientific_columns = {
        "peer_sign",
        "peer_grid",
        "evidence_utc",
        "outcome",
        "metric",
        "paired_eligible",
    }
    if comparison_units is None or comparison_units.empty:
        return empty_model
    missing_scientific_columns = sorted(
        required_scientific_columns - set(comparison_units.columns)
    )
    if missing_scientific_columns:
        raise ValueError(
            "Delta-SNR comparison units are missing required columns: "
            + ", ".join(missing_scientific_columns)
            + "."
        )
    diagnostic_units = _eligible_outcome_diagnostic_units(
        comparison_units,
        analysis_start_utc=analysis_start,
        analysis_end_utc=analysis_end,
    )

    retained_columns = [
        "peer_sign",
        "peer_grid",
        "evidence_utc",
        "metric",
    ]
    for optional_column in (
        "identity_order",
        "target_snr_db",
        "reference_snr_db",
    ):
        if optional_column in comparison_units.columns:
            retained_columns.append(optional_column)
    paired_units = comparison_units.loc[
        comparison_units["outcome"].eq(COMPARE_OUTCOME_JOINT)
        & comparison_units["paired_eligible"].fillna(False),
        retained_columns,
    ].copy()
    for optional_column in (
        "identity_order",
        "target_snr_db",
        "reference_snr_db",
    ):
        if optional_column not in paired_units.columns:
            paired_units[optional_column] = np.nan
    paired_units["evidence_utc"] = pd.to_datetime(
        paired_units["evidence_utc"],
        utc=True,
        errors="coerce",
    )
    for numeric_column in (
        "metric",
        "identity_order",
        "target_snr_db",
        "reference_snr_db",
    ):
        paired_units[numeric_column] = pd.to_numeric(
            paired_units[numeric_column],
            errors="coerce",
        )
    finite_metric_mask = np.isfinite(
        paired_units["metric"].to_numpy(dtype=float)
    )
    paired_units = paired_units[
        paired_units["peer_sign"].notna()
        & paired_units["peer_grid"].notna()
        & paired_units["evidence_utc"].notna()
        & paired_units["metric"].notna()
        & finite_metric_mask
        & paired_units["evidence_utc"].ge(analysis_start)
        & paired_units["evidence_utc"].lt(analysis_end)
    ].copy()
    if paired_units.empty:
        return empty_model

    paired_units["peer_sign"] = (
        paired_units["peer_sign"].astype(str).str.strip().str.upper()
    )
    paired_units["peer_grid"] = (
        paired_units["peer_grid"].astype(str).str.strip().str.upper()
    )
    paired_units = paired_units[
        paired_units["peer_sign"].ne("")
        & paired_units["peer_grid"].ne("")
        & paired_units["peer_sign"].map(is_valid_callsign)
        & paired_units["peer_grid"].map(is_valid_locator)
    ].copy()
    if paired_units.empty:
        return empty_model

    paired_units = (
        paired_units.groupby(
            ["peer_sign", "peer_grid", "evidence_utc"],
            observed=True,
            sort=False,
        )
        .agg(
            metric=("metric", "median"),
            identity_order=("identity_order", "min"),
            target_snr_db=("target_snr_db", "median"),
            reference_snr_db=("reference_snr_db", "median"),
        )
        .reset_index()
    )
    paired_units["detector_row_index"] = np.arange(
        len(paired_units),
        dtype=np.int64,
    )
    paired_units["baseline_cell_start_utc"] = paired_units[
        "evidence_utc"
    ].dt.floor(DELTA_SNR_OUTLIER_BASELINE_CELL)
    normalized_directions = _direction_lookup(station_directions)
    identity_order_lookup: dict[tuple[str, str], tuple[int, float]] = {}
    for fallback_order, identity_row in enumerate(
        paired_units[
            ["peer_sign", "peer_grid", "identity_order"]
        ].drop_duplicates(subset=["peer_sign", "peer_grid"]).itertuples(index=False)
    ):
        identity_order = _optional_finite(identity_row.identity_order)
        identity_order_lookup[
            (str(identity_row.peer_sign), str(identity_row.peer_grid))
        ] = (
            (0, float(identity_order))
            if identity_order is not None
            else (1, float(fallback_order))
        )

    empty_diagnostic_units = diagnostic_units.iloc[0:0]
    diagnostic_units_by_identity = {
        (str(callsign), str(locator)): path_units.reset_index(drop=True)
        for (callsign, locator), path_units in diagnostic_units.groupby(
            ["peer_sign", "peer_grid"],
            observed=True,
            sort=False,
        )
    }
    candidates: list[DeltaSnrOutlierCandidate] = []
    pilot_anomalies_db = np.full(len(paired_units), np.nan, dtype=float)
    evaluable_cycle_count = 0

    for (callsign, locator), station_rows in paired_units.groupby(
        ["peer_sign", "peer_grid"],
        observed=True,
        sort=False,
    ):
        station_rows = station_rows.sort_values("evidence_utc").reset_index(drop=True)
        identity = OutlierStationIdentity(str(callsign), str(locator))
        path_diagnostic_units = diagnostic_units_by_identity.get(
            (identity.callsign, identity.locator),
            empty_diagnostic_units,
        )
        path_effective_cadence_minutes = _path_effective_cadence_minutes(
            pd.DatetimeIndex(path_diagnostic_units["evidence_utc"]),
            fallback_cadence_minutes=cadence_minutes,
        )
        maximum_gap_minutes = _maximum_episode_gap_minutes(
            path_effective_cadence_minutes
        )
        pilot_guard_minutes = _pilot_guard_minutes(
            path_effective_cadence_minutes
        )
        episode_guard_minutes = _episode_guard_minutes(
            path_effective_cadence_minutes
        )
        direction_sector = normalized_directions.get(
            (identity.callsign, identity.locator)
        )
        station_times = pd.DatetimeIndex(station_rows["evidence_utc"])
        station_metrics_db = station_rows["metric"].to_numpy(dtype=float)
        station_target_db = station_rows["target_snr_db"].to_numpy(dtype=float)
        station_reference_db = station_rows["reference_snr_db"].to_numpy(dtype=float)
        baseline_cells = (
            station_rows.groupby(
                "baseline_cell_start_utc",
                observed=True,
                sort=True,
            )
            .agg(
                metric=("metric", "median"),
                target_snr_db=("target_snr_db", "median"),
                reference_snr_db=("reference_snr_db", "median"),
            )
            .reset_index()
        )
        cell_times = pd.DatetimeIndex(baseline_cells["baseline_cell_start_utc"])
        cell_metrics_db = baseline_cells["metric"].to_numpy(dtype=float)
        cell_target_db = baseline_cells["target_snr_db"].to_numpy(dtype=float)
        cell_reference_db = baseline_cells[
            "reference_snr_db"
        ].to_numpy(dtype=float)
        if len(cell_times) < 2 * DELTA_SNR_OUTLIER_MINIMUM_FLANK_CELLS + 1:
            continue
        pilot_baselines_db = _pilot_baselines_by_cell(
            cell_times,
            cell_metrics_db,
            guard_minutes=pilot_guard_minutes,
            maximum_baseline_difference_db=(
                detection_policy.maximum_baseline_difference_db
            ),
        )
        cell_index_lookup = {
            timestamp: index for index, timestamp in enumerate(cell_times)
        }
        station_cell_indexes = np.fromiter(
            (
                cell_index_lookup[pd.Timestamp(timestamp)]
                for timestamp in station_rows["baseline_cell_start_utc"]
            ),
            dtype=np.int64,
            count=len(station_rows),
        )
        station_pilot_baselines_db = pilot_baselines_db[station_cell_indexes]
        supported_mask = np.isfinite(station_pilot_baselines_db)
        pilot_residuals_db = station_metrics_db - station_pilot_baselines_db
        evaluable_cycle_count += int(supported_mask.sum())
        detector_row_indexes = station_rows["detector_row_index"].to_numpy(
            dtype=np.int64
        )
        pilot_anomalies_db[
            detector_row_indexes[supported_mask]
        ] = pilot_residuals_db[supported_mask]
        member_signs = np.zeros(len(station_rows), dtype=np.int8)
        minimum_member_anomaly_db = min(
            DELTA_SNR_OUTLIER_MINIMUM_MEMBER_ANOMALY_DB,
            detection_policy.minimum_departure_db,
        )
        positive_members = supported_mask & (
            pilot_residuals_db
            >= minimum_member_anomaly_db
        )
        negative_members = supported_mask & (
            pilot_residuals_db
            <= -minimum_member_anomaly_db
        )
        member_signs[positive_members] = 1
        member_signs[negative_members] = -1
        provisional_groups = _group_signed_member_runs(
            station_times,
            member_signs,
            supported_mask,
            maximum_gap_minutes=maximum_gap_minutes,
        )
        consumed_through_index = -1
        for start_index, end_index, episode_sign in provisional_groups:
            if start_index <= consumed_through_index:
                continue
            episode_candidates, refined_end_index = _qualified_episode_candidates(
                identity=identity,
                direction_sector=direction_sector,
                station_times=station_times,
                station_metrics_db=station_metrics_db,
                station_target_db=station_target_db,
                station_reference_db=station_reference_db,
                cell_times=cell_times,
                cell_metrics_db=cell_metrics_db,
                cell_target_db=cell_target_db,
                cell_reference_db=cell_reference_db,
                start_index=start_index,
                end_index=end_index,
                episode_sign=episode_sign,
                path_effective_cadence_minutes=(
                    path_effective_cadence_minutes
                ),
                maximum_gap_minutes=maximum_gap_minutes,
                episode_guard_minutes=episode_guard_minutes,
                detection_policy=detection_policy,
            )
            if not episode_candidates or refined_end_index is None:
                continue
            consumed_through_index = max(
                consumed_through_index,
                refined_end_index,
            )
            candidates.extend(episode_candidates)

    ordered_candidates_without_diagnostics = tuple(
        sorted(
            candidates,
            key=lambda candidate: (
                candidate.start_utc,
                identity_order_lookup[
                    (
                        candidate.station_identity.callsign,
                        candidate.station_identity.locator,
                    )
                ],
                candidate.station_identity.callsign,
                candidate.station_identity.locator,
            ),
        )
    )
    ordered_candidates = tuple(
        _with_nearby_outcome_diagnostics(
            candidate,
            diagnostic_units_by_identity.get(
                (
                    candidate.station_identity.callsign,
                    candidate.station_identity.locator,
                ),
                empty_diagnostic_units,
            ),
        )
        for candidate in ordered_candidates_without_diagnostics
    )
    signature = _candidate_signature(ordered_candidates, detection_policy)
    paired_units["pilot_anomaly_db"] = pilot_anomalies_db
    coherence_tolerance_minutes = max(
        DELTA_SNR_OUTLIER_SEGMENT_COHERENCE_MINUTES,
        cadence_minutes / 2.0,
    )
    populated_cycle_count = len(paired_units)
    return DeltaSnrOutlierModel(
        detector_version=DELTA_SNR_OUTLIER_DETECTOR_VERSION,
        detection_resolution=DELTA_SNR_OUTLIER_DETECTION_RESOLUTION,
        paired_unit_cadence_minutes=cadence_minutes,
        analysis_start_utc=analysis_start,
        analysis_end_utc=analysis_end,
        populated_station_cycle_count=populated_cycle_count,
        evaluable_station_cycle_count=evaluable_cycle_count,
        abstained_station_cycle_count=(
            populated_cycle_count - evaluable_cycle_count
        ),
        candidates=ordered_candidates,
        report_entries=_report_entries(
            ordered_candidates,
            paired_units,
            normalized_directions=normalized_directions,
            coherence_tolerance_minutes=coherence_tolerance_minutes,
        ),
        candidate_signature=signature,
        detection_policy=detection_policy,
    )
