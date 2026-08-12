"""Pure view-model preparation for compact Delta-SNR episode reports."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from ui.inspector.evidence_data import (
    COMPARE_OUTCOME_JOINT,
)


OUTLIER_UNAVAILABLE_VALUE = "—"

if TYPE_CHECKING:
    from ui.inspector.outlier_candidates import (
        DeltaSnrOutlierCandidate,
        DeltaSnrOutlierModel,
        DeltaSnrOutlierReportEntry,
        OutlierStationIdentity,
    )


@dataclass(frozen=True)
class DeltaSnrEpisodeEvidenceRow:
    """Describe one retained native evidence row shown inside an episode card."""

    evidence_utc: pd.Timestamp
    station_identity: "OutlierStationIdentity"
    direction_sector: str | None
    target_snr_db: float | None
    reference_snr_db: float | None
    delta_snr_db: float | None
    local_baseline_db: float
    residual_db: float | None


@dataclass(frozen=True)
class DeltaSnrEpisodeCardViewModel:
    """Pair one detector review entry with its compact native evidence rows."""

    report_entry: "DeltaSnrOutlierReportEntry"
    evidence_rows: tuple[DeltaSnrEpisodeEvidenceRow, ...]


@dataclass(frozen=True)
class DeltaSnrOutlierReportViewModel:
    """Hold compact episode cards without retaining the full comparison frame."""

    cards: tuple[DeltaSnrEpisodeCardViewModel, ...]


def _optional_finite_float(value: object) -> float | None:
    """Return one finite float or the explicit unavailable state."""
    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return None
    return numeric_value if np.isfinite(numeric_value) else None


def _normalized_comparison_units(comparison_units: pd.DataFrame) -> pd.DataFrame:
    """Normalize only columns required by the compact evidence view model."""
    columns = [
        "peer_sign",
        "peer_grid",
        "evidence_utc",
        "outcome",
        "paired_eligible",
        "target_snr_db",
        "reference_snr_db",
        "metric",
    ]
    if comparison_units is None or comparison_units.empty:
        return pd.DataFrame(columns=columns)
    required_columns = {
        "peer_sign",
        "peer_grid",
        "evidence_utc",
        "outcome",
        "paired_eligible",
        "metric",
    }
    missing_columns = sorted(required_columns - set(comparison_units.columns))
    if missing_columns:
        raise ValueError(
            "Delta-SNR report evidence is missing required columns: "
            + ", ".join(missing_columns)
            + "."
        )
    retained_columns = [
        column for column in columns if column in comparison_units.columns
    ]
    units = comparison_units.loc[
        comparison_units["paired_eligible"].fillna(False),
        retained_columns,
    ].copy()
    for optional_column in ("target_snr_db", "reference_snr_db"):
        if optional_column not in units.columns:
            units[optional_column] = np.nan
    units["evidence_utc"] = pd.to_datetime(
        units["evidence_utc"],
        utc=True,
        errors="coerce",
    )
    for numeric_column in ("target_snr_db", "reference_snr_db", "metric"):
        units[numeric_column] = pd.to_numeric(
            units[numeric_column],
            errors="coerce",
        )
    units["peer_sign"] = units["peer_sign"].astype(str).str.strip().str.upper()
    units["peer_grid"] = units["peer_grid"].astype(str).str.strip().str.upper()
    return units[
        units["evidence_utc"].notna()
        & units["peer_sign"].ne("")
        & units["peer_grid"].ne("")
        & units["outcome"].eq(COMPARE_OUTCOME_JOINT)
    ].reset_index(drop=True)


def _candidate_evidence_rows(
    candidate: "DeltaSnrOutlierCandidate",
    comparison_units: pd.DataFrame,
) -> tuple[DeltaSnrEpisodeEvidenceRow, ...]:
    """Retain only episode-member Joint rows for one qualifying path."""
    identity = candidate.station_identity
    candidate_units = comparison_units[
        comparison_units["peer_sign"].eq(identity.callsign)
        & comparison_units["peer_grid"].eq(identity.locator)
    ]
    if candidate_units.empty:
        return ()
    episode_start_utc = pd.Timestamp(candidate.start_utc).tz_convert("UTC")
    episode_end_utc = pd.Timestamp(candidate.end_utc).tz_convert("UTC")
    is_episode_joint = (
        candidate_units["outcome"].eq(COMPARE_OUTCOME_JOINT)
        & candidate_units["evidence_utc"].ge(episode_start_utc)
        & candidate_units["evidence_utc"].lt(episode_end_utc)
    )
    retained_units = candidate_units[is_episode_joint].sort_values(
        "evidence_utc"
    )
    rows = []
    for unit in retained_units.itertuples(index=False):
        target_snr_db = _optional_finite_float(unit.target_snr_db)
        reference_snr_db = _optional_finite_float(unit.reference_snr_db)
        delta_snr_db = _optional_finite_float(unit.metric)
        rows.append(
            DeltaSnrEpisodeEvidenceRow(
                evidence_utc=pd.Timestamp(unit.evidence_utc),
                station_identity=identity,
                direction_sector=candidate.direction_sector,
                target_snr_db=target_snr_db,
                reference_snr_db=reference_snr_db,
                delta_snr_db=delta_snr_db,
                local_baseline_db=float(candidate.station_baseline_db),
                residual_db=(
                    delta_snr_db - float(candidate.station_baseline_db)
                    if delta_snr_db is not None
                    else None
                ),
            )
        )
    return tuple(rows)


def build_delta_snr_outlier_report_view_model(
    outlier_model: "DeltaSnrOutlierModel",
    comparison_units: pd.DataFrame,
) -> DeltaSnrOutlierReportViewModel:
    """Build compact report cards without retaining unrelated comparison rows."""
    if outlier_model is None:
        raise ValueError("Delta-SNR report preparation requires a detector model.")
    normalized_units = _normalized_comparison_units(comparison_units)
    cards = []
    for report_entry in outlier_model.report_entries:
        path_order = {
            identity: index
            for index, identity in enumerate(report_entry.station_identities)
        }
        evidence_by_key = {}
        for candidate in report_entry.candidates:
            for evidence_row in _candidate_evidence_rows(
                candidate,
                normalized_units,
            ):
                key = (
                    evidence_row.evidence_utc.value,
                    evidence_row.station_identity,
                )
                evidence_by_key.setdefault(key, evidence_row)
        evidence_rows = tuple(
            sorted(
                evidence_by_key.values(),
                key=lambda evidence_row: (
                    evidence_row.evidence_utc,
                    path_order.get(evidence_row.station_identity, len(path_order)),
                ),
            )
        )
        cards.append(
            DeltaSnrEpisodeCardViewModel(
                report_entry=report_entry,
                evidence_rows=evidence_rows,
            )
        )
    return DeltaSnrOutlierReportViewModel(cards=tuple(cards))
