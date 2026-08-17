"""Pure tabular exports for optional Delta-SNR outlier findings."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from ui.inspector.outlier_candidates import (
    DELTA_SNR_OUTLIER_MAD_NORMALIZATION,
)
from ui.inspector.outlier_report import (
    DeltaSnrEpisodeCardViewModel,
    DeltaSnrOutlierReportViewModel,
)


if TYPE_CHECKING:
    from ui.inspector.outlier_candidates import (
        DeltaSnrOutlierCandidate,
        DeltaSnrOutlierModel,
        DeltaSnrOutlierReportEntry,
    )


OUTLIER_EXPORT_JOINT_SPOT = "joint_spot"
OUTLIER_EXPORT_COMPLETE_SCHEDULED_PAIR = "complete_scheduled_pair"
DELTA_SNR_OUTLIER_EXPORT_SCHEMA_VERSION = 1
OUTLIER_EVENT_PATHS_TABLE_FILENAME = (
    "table_delta_snr_outlier_event_paths.csv"
)
OUTLIER_PAIRED_EVIDENCE_TABLE_FILENAME = (
    "table_delta_snr_outlier_paired_evidence.csv"
)

OUTLIER_EXPORT_STATUS_INSUFFICIENT_PAIRED_EVIDENCE = (
    "insufficient_paired_evidence"
)
OUTLIER_EXPORT_STATUS_INSUFFICIENT_LOCAL_BASELINE = (
    "insufficient_local_baseline"
)
OUTLIER_EXPORT_STATUS_NO_CANDIDATES = "no_candidates"
OUTLIER_EXPORT_STATUS_CANDIDATES = "candidates"

OUTLIER_EVENT_PATH_COLUMNS = (
    "event_id",
    "combined_event_class",
    "event_first_evidence_utc",
    "event_last_evidence_utc",
    "cross_path_context",
    "departure_direction",
    "qualifying_path_count",
    "path_event_id",
    "path_number",
    "path_occurrence",
    "path",
    "callsign",
    "locator",
    "direction",
    "path_event_class",
    "path_first_evidence_utc",
    "path_last_evidence_utc",
    "paired_unit_type",
    "paired_unit_count",
    "first_to_last_span_minutes",
    "median_evidence_interval_minutes",
    "largest_gap_minutes",
    "expected_local_delta_snr_db",
    "observed_median_delta_snr_db",
    "largest_single_unit_departure_db",
    "path_robust_z_score",
    "pre_event_baseline_delta_snr_db",
    "post_event_baseline_delta_snr_db",
    "absolute_pre_post_baseline_difference_db",
    "agreeing_paired_unit_count",
    "paired_unit_sign_agreement_fraction",
    "decode_edge_warning",
    "decode_edge_warning_reason",
    "nearby_joint_unit_count",
    "nearby_target_only_unit_count",
    "nearby_reference_only_unit_count",
)

OUTLIER_PAIRED_EVIDENCE_COLUMNS = (
    "event_id",
    "event_first_evidence_utc",
    "event_last_evidence_utc",
    "path_event_id",
    "path",
    "callsign",
    "locator",
    "direction",
    "path_event_class",
    "paired_unit_type",
    "unit_sequence",
    "utc",
    "target_snr_db",
    "corrected_reference_snr_db",
    "delta_snr_db",
    "expected_local_delta_snr_db",
    "departure_from_local_baseline_db",
    "cycle_robust_z_score",
    "meets_strong_anchor_gates",
    "reported_boundary",
)


@dataclass(frozen=True)
class DeltaSnrOutlierExportTables:
    """Hold the two related analyst-facing outlier export tables."""

    event_paths: pd.DataFrame
    paired_evidence: pd.DataFrame


def _outlier_export_status(
    outlier_model: "DeltaSnrOutlierModel",
) -> str:
    """Classify one enabled detector result without inventing a finding row."""
    if int(outlier_model.populated_station_cycle_count) == 0:
        return OUTLIER_EXPORT_STATUS_INSUFFICIENT_PAIRED_EVIDENCE
    if int(outlier_model.evaluable_station_cycle_count) == 0:
        return OUTLIER_EXPORT_STATUS_INSUFFICIENT_LOCAL_BASELINE
    if not outlier_model.candidates:
        return OUTLIER_EXPORT_STATUS_NO_CANDIDATES
    return OUTLIER_EXPORT_STATUS_CANDIDATES


def build_delta_snr_outlier_export_metadata(
    outlier_model: "DeltaSnrOutlierModel",
    export_tables: DeltaSnrOutlierExportTables,
) -> dict[str, object]:
    """Describe enabled outlier tables once in canonical run metadata."""
    if outlier_model is None:
        raise ValueError("Delta-SNR outlier export metadata requires a model.")
    if not isinstance(export_tables, DeltaSnrOutlierExportTables):
        raise TypeError(
            "Delta-SNR outlier export metadata requires validated tables."
        )
    if tuple(export_tables.event_paths.columns) != OUTLIER_EVENT_PATH_COLUMNS:
        raise ValueError("Delta-SNR event-path export columns are invalid.")
    if (
        tuple(export_tables.paired_evidence.columns)
        != OUTLIER_PAIRED_EVIDENCE_COLUMNS
    ):
        raise ValueError("Delta-SNR paired-evidence export columns are invalid.")

    event_count = len(outlier_model.report_entries)
    path_event_count = len(outlier_model.candidates)
    paired_evidence_row_count = sum(
        int(candidate.paired_unit_count)
        for candidate in outlier_model.candidates
    )
    if len(export_tables.event_paths) != path_event_count:
        raise ValueError(
            "Delta-SNR event-path rows must match qualified path events."
        )
    if len(export_tables.paired_evidence) != paired_evidence_row_count:
        raise ValueError(
            "Delta-SNR paired-evidence rows must match qualified event units."
        )
    unique_qualifying_paths = {
        (
            candidate.station_identity.callsign,
            candidate.station_identity.locator,
        )
        for candidate in outlier_model.candidates
    }
    return {
        "schema_version": DELTA_SNR_OUTLIER_EXPORT_SCHEMA_VERSION,
        "result_status": _outlier_export_status(outlier_model),
        "candidate_signature": outlier_model.candidate_signature,
        "detection_resolution": outlier_model.detection_resolution,
        "event_count": event_count,
        "path_event_count": path_event_count,
        "unique_qualifying_path_count": len(unique_qualifying_paths),
        "paired_evidence_row_count": paired_evidence_row_count,
        "populated_paired_unit_count": int(
            outlier_model.populated_station_cycle_count
        ),
        "evaluable_paired_unit_count": int(
            outlier_model.evaluable_station_cycle_count
        ),
        "abstained_paired_unit_count": int(
            outlier_model.abstained_station_cycle_count
        ),
        "tables": {
            "event_paths": OUTLIER_EVENT_PATHS_TABLE_FILENAME,
            "paired_evidence": OUTLIER_PAIRED_EVIDENCE_TABLE_FILENAME,
        },
    }


def _utc_iso(timestamp: object) -> str:
    """Return one exact timezone-aware timestamp in stable ISO UTC form."""
    utc_timestamp = pd.Timestamp(timestamp)
    if pd.isna(utc_timestamp):
        raise ValueError("Delta-SNR outlier export timestamps must be valid.")
    if utc_timestamp.tzinfo is None:
        utc_timestamp = utc_timestamp.tz_localize("UTC")
    else:
        utc_timestamp = utc_timestamp.tz_convert("UTC")
    return utc_timestamp.isoformat().replace("+00:00", "Z")


def _inclusive_end_utc(half_open_end_utc: object) -> pd.Timestamp:
    """Convert the detector's positive half-open end into observed UTC."""
    end_utc = pd.Timestamp(half_open_end_utc)
    if end_utc.tzinfo is None:
        end_utc = end_utc.tz_localize("UTC")
    else:
        end_utc = end_utc.tz_convert("UTC")
    return end_utc - pd.Timedelta(nanoseconds=1)


def _finite_or_none(value: object) -> float | None:
    """Return a finite float or the CSV's explicit empty-cell state."""
    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return None
    return numeric_value if math.isfinite(numeric_value) else None


def _paired_unit_type(is_sequential: bool) -> str:
    """Return the canonical native-evidence code for later localization."""
    return (
        OUTLIER_EXPORT_COMPLETE_SCHEDULED_PAIR
        if is_sequential
        else OUTLIER_EXPORT_JOINT_SPOT
    )


def _ordered_report_cards(
    report_view_model: DeltaSnrOutlierReportViewModel,
) -> tuple[DeltaSnrEpisodeCardViewModel, ...]:
    """Return deterministic chronological card order for package-local IDs."""
    return tuple(
        sorted(
            report_view_model.cards,
            key=lambda card: (
                pd.Timestamp(card.report_entry.start_utc),
                pd.Timestamp(card.report_entry.end_utc),
                int(card.report_entry.episode_index),
                tuple(
                    (identity.callsign, identity.locator)
                    for identity in card.report_entry.station_identities
                ),
            ),
        )
    )


def _ordered_candidates(
    report_entry: "DeltaSnrOutlierReportEntry",
) -> tuple["DeltaSnrOutlierCandidate", ...]:
    """Return deterministic path-first, interval-second candidate order."""
    identity_order = {
        identity: index
        for index, identity in enumerate(report_entry.station_identities)
    }
    candidates = tuple(
        sorted(
            report_entry.candidates,
            key=lambda candidate: (
                identity_order.get(candidate.station_identity, len(identity_order)),
                candidate.station_identity.callsign,
                candidate.station_identity.locator,
                pd.Timestamp(candidate.start_utc),
            ),
        )
    )
    return candidates


def _candidate_evidence_rows(
    candidate: "DeltaSnrOutlierCandidate",
    card: DeltaSnrEpisodeCardViewModel,
):
    """Return exact chronological evidence rows for one candidate path."""
    rows = tuple(
        sorted(
            (
                row
                for row in card.evidence_rows
                if row.station_identity == candidate.station_identity
                and pd.Timestamp(row.evidence_utc) >= pd.Timestamp(candidate.start_utc)
                and pd.Timestamp(row.evidence_utc) < pd.Timestamp(candidate.end_utc)
            ),
            key=lambda row: pd.Timestamp(row.evidence_utc),
        )
    )
    if len(rows) != int(candidate.paired_unit_count):
        raise ValueError(
            "Delta-SNR export evidence rows must match the detector paired-unit count."
        )
    return rows


def _evidence_intervals_minutes(evidence_rows) -> tuple[float, ...]:
    """Return exact positive intervals between chronological evidence rows."""
    evidence_times = [pd.Timestamp(row.evidence_utc) for row in evidence_rows]
    return tuple(
        float((later - earlier) / pd.Timedelta(minutes=1))
        for earlier, later in zip(evidence_times, evidence_times[1:])
    )


def _cycle_robust_z(
    candidate: "DeltaSnrOutlierCandidate",
    residual_db: float | None,
) -> float | None:
    """Calculate the detector's modified z-score for one retained unit."""
    if residual_db is None:
        return None
    robust_spread_db = float(candidate.robust_spread_db)
    if not math.isfinite(robust_spread_db) or robust_spread_db <= 0.0:
        raise ValueError("Delta-SNR export requires a positive robust spread.")
    return DELTA_SNR_OUTLIER_MAD_NORMALIZATION * residual_db / robust_spread_db


def _meets_strong_anchor_gates(
    outlier_model: "DeltaSnrOutlierModel",
    candidate: "DeltaSnrOutlierCandidate",
    residual_db: float | None,
    robust_z: float | None,
) -> bool:
    """Evaluate the exact per-unit gates used to anchor reported boundaries."""
    if residual_db is None or robust_z is None:
        return False
    episode_sign = int(np.sign(candidate.median_anomaly_db))
    return bool(
        episode_sign != 0
        and int(np.sign(residual_db)) == episode_sign
        and abs(residual_db)
        >= outlier_model.detection_policy.minimum_departure_db
        and abs(robust_z) >= outlier_model.detection_policy.minimum_robust_z
    )


def _reported_boundary(sequence: int, count: int) -> str:
    """Return the canonical inclusive-boundary code for one retained unit."""
    if count == 1:
        return "start_and_end"
    if sequence == 1:
        return "start"
    if sequence == count:
        return "end"
    return ""


def _event_observed_bounds(
    card: DeltaSnrEpisodeCardViewModel,
) -> tuple[str, str]:
    """Derive inclusive event bounds from rows and validate detector sentinels."""
    if not card.evidence_rows:
        raise ValueError("Delta-SNR export event has no retained paired evidence.")
    evidence_times = tuple(
        pd.Timestamp(row.evidence_utc).tz_convert("UTC")
        for row in card.evidence_rows
    )
    first_evidence_utc = min(evidence_times)
    last_evidence_utc = max(evidence_times)
    report_entry = card.report_entry
    expected_first_utc = pd.Timestamp(report_entry.start_utc).tz_convert("UTC")
    expected_last_utc = _inclusive_end_utc(report_entry.end_utc)
    if (
        first_evidence_utc != expected_first_utc
        or last_evidence_utc != expected_last_utc
        or any(
            evidence_utc < expected_first_utc
            or evidence_utc >= pd.Timestamp(report_entry.end_utc).tz_convert("UTC")
            for evidence_utc in evidence_times
        )
    ):
        raise ValueError(
            "Delta-SNR export evidence bounds must match the detector's "
            "half-open report bounds."
        )
    return _utc_iso(first_evidence_utc), _utc_iso(last_evidence_utc)


def build_delta_snr_outlier_export_tables(
    outlier_model: "DeltaSnrOutlierModel",
    report_view_model: DeltaSnrOutlierReportViewModel,
    *,
    is_sequential: bool,
) -> DeltaSnrOutlierExportTables:
    """Build readable event-path and native paired-evidence export tables.

    IDs are deterministic within one prepared package. They are chronological
    aliases for joining these two tables and are not persistent identities
    across independently prepared analyses.
    """
    if outlier_model is None:
        raise ValueError("Delta-SNR outlier export requires a detector model.")
    if report_view_model is None:
        raise ValueError("Delta-SNR outlier export requires a report view model.")
    if len(report_view_model.cards) != len(outlier_model.report_entries):
        raise ValueError(
            "Delta-SNR outlier model and report view model must contain the "
            "same event count."
        )
    event_path_rows: list[dict[str, object]] = []
    paired_evidence_rows: list[dict[str, object]] = []
    paired_unit_type = _paired_unit_type(bool(is_sequential))

    for event_number, card in enumerate(
        _ordered_report_cards(report_view_model),
        start=1,
    ):
        event_id = f"E{event_number:04d}"
        report_entry = card.report_entry
        candidates = _ordered_candidates(report_entry)
        event_first_utc, event_last_utc = _event_observed_bounds(card)
        identity_order = {
            identity: index + 1
            for index, identity in enumerate(report_entry.station_identities)
        }
        path_occurrences: dict[object, int] = {}

        for candidate in candidates:
            identity = candidate.station_identity
            path_number = identity_order.get(identity)
            if path_number is None:
                raise ValueError(
                    "Delta-SNR export candidate path is absent from report order."
                )
            path_occurrence = path_occurrences.get(identity, 0) + 1
            path_occurrences[identity] = path_occurrence
            path_event_id = (
                f"{event_id}-P{path_number:02d}-{path_occurrence:02d}"
            )
            evidence_rows = _candidate_evidence_rows(candidate, card)
            intervals_minutes = _evidence_intervals_minutes(evidence_rows)
            path_first_utc = _utc_iso(evidence_rows[0].evidence_utc)
            path_last_utc = _utc_iso(evidence_rows[-1].evidence_utc)
            median_interval_minutes = (
                float(np.median(intervals_minutes))
                if intervals_minutes
                else None
            )
            event_path_rows.append(
                {
                    "event_id": event_id,
                    "combined_event_class": report_entry.event_kind,
                    "event_first_evidence_utc": event_first_utc,
                    "event_last_evidence_utc": event_last_utc,
                    "cross_path_context": report_entry.coherence_scope,
                    "departure_direction": report_entry.sign_agreement,
                    "qualifying_path_count": int(report_entry.flagged_station_count),
                    "path_event_id": path_event_id,
                    "path_number": path_number,
                    "path_occurrence": path_occurrence,
                    "path": identity.label,
                    "callsign": identity.callsign,
                    "locator": identity.locator,
                    "direction": candidate.direction_sector,
                    "path_event_class": candidate.event_kind,
                    "path_first_evidence_utc": path_first_utc,
                    "path_last_evidence_utc": path_last_utc,
                    "paired_unit_type": paired_unit_type,
                    "paired_unit_count": int(candidate.paired_unit_count),
                    "first_to_last_span_minutes": float(
                        (
                            pd.Timestamp(evidence_rows[-1].evidence_utc)
                            - pd.Timestamp(evidence_rows[0].evidence_utc)
                        )
                        / pd.Timedelta(minutes=1)
                    ),
                    "median_evidence_interval_minutes": median_interval_minutes,
                    "largest_gap_minutes": (
                        max(intervals_minutes) if intervals_minutes else None
                    ),
                    "expected_local_delta_snr_db": float(
                        candidate.station_baseline_db
                    ),
                    "observed_median_delta_snr_db": float(
                        candidate.episode_median_delta_snr_db
                    ),
                    "largest_single_unit_departure_db": float(
                        candidate.peak_anomaly_db
                    ),
                    "path_robust_z_score": float(candidate.robust_z),
                    "pre_event_baseline_delta_snr_db": float(
                        candidate.pre_baseline_db
                    ),
                    "post_event_baseline_delta_snr_db": float(
                        candidate.post_baseline_db
                    ),
                    "absolute_pre_post_baseline_difference_db": abs(
                        float(candidate.pre_baseline_db)
                        - float(candidate.post_baseline_db)
                    ),
                    "agreeing_paired_unit_count": int(
                        candidate.agreeing_paired_unit_count
                    ),
                    "paired_unit_sign_agreement_fraction": float(
                        candidate.paired_unit_sign_agreement_fraction
                    ),
                    "decode_edge_warning": bool(candidate.decode_edge_warning),
                    "decode_edge_warning_reason": (
                        candidate.decode_edge_warning_reason
                    ),
                    "nearby_joint_unit_count": int(
                        candidate.nearby_joint_unit_count
                    ),
                    "nearby_target_only_unit_count": int(
                        candidate.nearby_target_only_unit_count
                    ),
                    "nearby_reference_only_unit_count": int(
                        candidate.nearby_reference_only_unit_count
                    ),
                }
            )

            for unit_sequence, evidence_row in enumerate(evidence_rows, start=1):
                residual_db = _finite_or_none(evidence_row.residual_db)
                cycle_robust_z = _cycle_robust_z(candidate, residual_db)
                paired_evidence_rows.append(
                    {
                        "event_id": event_id,
                        "event_first_evidence_utc": event_first_utc,
                        "event_last_evidence_utc": event_last_utc,
                        "path_event_id": path_event_id,
                        "path": identity.label,
                        "callsign": identity.callsign,
                        "locator": identity.locator,
                        "direction": candidate.direction_sector,
                        "path_event_class": candidate.event_kind,
                        "paired_unit_type": paired_unit_type,
                        "unit_sequence": unit_sequence,
                        "utc": _utc_iso(evidence_row.evidence_utc),
                        "target_snr_db": _finite_or_none(
                            evidence_row.target_snr_db
                        ),
                        "corrected_reference_snr_db": _finite_or_none(
                            evidence_row.reference_snr_db
                        ),
                        "delta_snr_db": _finite_or_none(
                            evidence_row.delta_snr_db
                        ),
                        "expected_local_delta_snr_db": float(
                            evidence_row.local_baseline_db
                        ),
                        "departure_from_local_baseline_db": residual_db,
                        "cycle_robust_z_score": cycle_robust_z,
                        "meets_strong_anchor_gates": _meets_strong_anchor_gates(
                            outlier_model,
                            candidate,
                            residual_db,
                            cycle_robust_z,
                        ),
                        "reported_boundary": _reported_boundary(
                            unit_sequence,
                            len(evidence_rows),
                        ),
                    }
                )

    return DeltaSnrOutlierExportTables(
        event_paths=pd.DataFrame(
            event_path_rows,
            columns=OUTLIER_EVENT_PATH_COLUMNS,
        ),
        paired_evidence=pd.DataFrame(
            paired_evidence_rows,
            columns=OUTLIER_PAIRED_EVIDENCE_COLUMNS,
        ),
    )


__all__ = [
    "DELTA_SNR_OUTLIER_EXPORT_SCHEMA_VERSION",
    "DeltaSnrOutlierExportTables",
    "OUTLIER_EVENT_PATH_COLUMNS",
    "OUTLIER_EXPORT_COMPLETE_SCHEDULED_PAIR",
    "OUTLIER_EXPORT_JOINT_SPOT",
    "OUTLIER_PAIRED_EVIDENCE_COLUMNS",
    "OUTLIER_EVENT_PATHS_TABLE_FILENAME",
    "OUTLIER_PAIRED_EVIDENCE_TABLE_FILENAME",
    "build_delta_snr_outlier_export_metadata",
    "build_delta_snr_outlier_export_tables",
]
