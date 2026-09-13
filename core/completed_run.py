"""Immutable, dependency-light contracts for published analysis results.

Records contain metadata and artifact references, never DataFrames or figures.
The explicit dictionary codec preserves the version-2 session snapshot shape;
live artifact ownership and availability remain the controller's responsibility.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import math

from core.analysis_plan import DECODE_FILTER_LEGACY, DECODE_FILTER_STRICT
from core.fetch_models import DatabaseSource, FetchSource
from core.result_diagnostics import (
    BENCHMARK_NO_QUALIFYING_RESULT,
    NO_SOURCE_ROWS,
    PERFORMANCE_NO_ELIGIBLE_STATION,
    PERFORMANCE_NO_QUALIFYING_SEGMENT,
    SOURCE_ROWS_FILTERED_OUT,
    ResultDiagnostic,
)


COMPLETED_RUN_SNAPSHOT_SCHEMA_VERSION = 2
COMPLETED_RENDERABLE = "renderable"
COMPLETED_PREPARED_NO_DATA = "prepared_no_data"
COMPLETED_MAP_NO_DATA = "map_no_data"

_OUTCOME_DIAGNOSTIC_REASONS = {
    COMPLETED_RENDERABLE: frozenset({PERFORMANCE_NO_QUALIFYING_SEGMENT}),
    COMPLETED_PREPARED_NO_DATA: frozenset({NO_SOURCE_ROWS, SOURCE_ROWS_FILTERED_OUT}),
    COMPLETED_MAP_NO_DATA: frozenset({
        PERFORMANCE_NO_ELIGIBLE_STATION, BENCHMARK_NO_QUALIFYING_RESULT,
    }),
}
_DECODE_FILTER_MODES = frozenset({DECODE_FILTER_STRICT, DECODE_FILTER_LEGACY})


def _require_text(text, field_name: str) -> None:
    if not isinstance(text, str) or not text.strip():
        raise ValueError(f"Completed run {field_name} must be nonempty text")


def _require_fields(snapshot, required_fields: set[str], record_name: str) -> None:
    if not isinstance(snapshot, Mapping):
        raise TypeError(f"{record_name} must be a mapping")
    if set(snapshot) != required_fields:
        raise ValueError(f"{record_name} has an invalid field set")


@dataclass(frozen=True, slots=True)
class CompletedAnalysisIdentity:
    """The established language-free identity of one completed result block."""

    id: str
    analysis_kind: str
    is_compare: bool
    is_sequential: bool
    absolute_method_version: str | None

    def __post_init__(self) -> None:
        _require_text(self.id, "analysis.id")
        if type(self.is_compare) is not bool or type(self.is_sequential) is not bool:
            raise ValueError("Completed analysis mode flags must be booleans")
        if self.analysis_kind not in {"comparison", "opportunity"}:
            raise ValueError("Completed analysis kind is unsupported")
        if self.is_compare != (self.analysis_kind == "comparison"):
            raise ValueError("Completed analysis kind and comparison flag disagree")
        if self.is_sequential and not self.is_compare:
            raise ValueError("Completed sequential analysis must be a comparison")
        if self.absolute_method_version is not None:
            _require_text(self.absolute_method_version, "analysis.absolute_method_version")

    @classmethod
    def from_analysis(cls, analysis: Mapping) -> CompletedAnalysisIdentity:
        return cls(
            id=analysis["id"],
            analysis_kind=analysis["analysis_kind"],
            is_compare=analysis["is_compare"],
            is_sequential=analysis["is_sequential"],
            absolute_method_version=analysis.get("absolute_method_version"),
        )

    @classmethod
    def from_dict(cls, snapshot) -> CompletedAnalysisIdentity:
        _require_fields(snapshot, {
            "id", "analysis_kind", "is_compare", "is_sequential", "absolute_method_version",
        }, "Completed analysis identity")
        return cls(**snapshot)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "analysis_kind": self.analysis_kind,
            "is_compare": self.is_compare,
            "is_sequential": self.is_sequential,
            "absolute_method_version": self.absolute_method_version,
        }


@dataclass(frozen=True, slots=True)
class CompletedQueryFetch:
    """One executed query's decode policy, delivery tier and measured duration."""

    decode_filter_mode: str
    elapsed_seconds: float
    delivery_source: str

    def __post_init__(self) -> None:
        if self.decode_filter_mode not in _DECODE_FILTER_MODES:
            raise ValueError("Completed query decode policy is unsupported")
        if isinstance(self.elapsed_seconds, bool) or not isinstance(self.elapsed_seconds, (int, float)):
            raise ValueError("Completed query duration must be finite and nonnegative")
        try:
            elapsed_seconds = float(self.elapsed_seconds)
        except (ValueError, OverflowError) as exc:
            raise ValueError("Completed query duration must be finite and nonnegative") from exc
        if not math.isfinite(elapsed_seconds) or elapsed_seconds < 0:
            raise ValueError("Completed query duration must be finite and nonnegative")
        object.__setattr__(self, "elapsed_seconds", elapsed_seconds)
        object.__setattr__(self, "delivery_source", FetchSource(self.delivery_source).value)

    @classmethod
    def from_dict(cls, snapshot) -> CompletedQueryFetch:
        _require_fields(snapshot, {
            "decode_filter_mode", "elapsed_seconds", "delivery_source",
        }, "Completed query fetch")
        return cls(**snapshot)

    def to_dict(self) -> dict:
        return {
            "decode_filter_mode": self.decode_filter_mode,
            "elapsed_seconds": self.elapsed_seconds,
            "delivery_source": self.delivery_source,
        }


@dataclass(frozen=True, slots=True)
class CompletedAnalysis:
    """One validated outcome with its immutable provenance and artifact paths."""

    analysis: CompletedAnalysisIdentity
    outcome: str
    evidence_path: str | None
    station_rows_path: str | None
    segment_rows_path: str | None
    selected_decode_filter_mode: str
    query_fetches: tuple[CompletedQueryFetch, ...]
    diagnostic: ResultDiagnostic | None

    def __post_init__(self) -> None:
        if not isinstance(self.analysis, CompletedAnalysisIdentity):
            raise TypeError("Completed analysis requires a typed identity")
        if self.outcome not in _OUTCOME_DIAGNOSTIC_REASONS:
            raise ValueError("Completed analysis outcome is unsupported")
        if self.selected_decode_filter_mode not in _DECODE_FILTER_MODES:
            raise ValueError("Completed analysis decode policy is unsupported")
        if not isinstance(self.query_fetches, (list, tuple)) or not self.query_fetches:
            raise ValueError("Completed analysis requires a nonempty query trace")
        if not all(isinstance(fetch, CompletedQueryFetch) for fetch in self.query_fetches):
            raise TypeError("Completed analysis query trace must contain typed fetches")
        object.__setattr__(self, "query_fetches", tuple(self.query_fetches))
        if self.query_fetches[-1].decode_filter_mode != self.selected_decode_filter_mode:
            raise ValueError("Completed analysis decode policy must match its final query")
        paths = (self.evidence_path, self.station_rows_path, self.segment_rows_path)
        for field_name, path in zip(
            ("evidence_path", "station_rows_path", "segment_rows_path"), paths,
        ):
            if path is not None:
                _require_text(path, field_name)
        if self.outcome == COMPLETED_RENDERABLE:
            if any(path is None for path in paths):
                raise ValueError("Renderable completion requires all three artifact paths")
        elif self.outcome == COMPLETED_MAP_NO_DATA:
            if self.evidence_path is None or any(path is not None for path in paths[1:]):
                raise ValueError("Empty map completion requires only its evidence path")
        elif any(path is not None for path in paths):
            raise ValueError("Empty preparation completion cannot contain artifact paths")
        if self.diagnostic is not None:
            if not isinstance(self.diagnostic, ResultDiagnostic):
                raise TypeError("Completed analysis diagnostic must be a ResultDiagnostic")
            # Reconstruct at this ownership boundary: a directly constructed
            # ResultDiagnostic may otherwise contain mutable or invalid fields.
            diagnostic = ResultDiagnostic.from_dict(self.diagnostic.to_dict())
            if diagnostic.reason not in _OUTCOME_DIAGNOSTIC_REASONS[self.outcome]:
                raise ValueError("Completed analysis diagnostic does not match its outcome")
            object.__setattr__(self, "diagnostic", diagnostic)

    @property
    def artifact_paths_by_kind(self) -> dict[str, str]:
        """Return only the paths required by this outcome for live validation."""
        return {
            kind: path
            for kind, path in (
                ("spots", self.evidence_path),
                ("map_stations", self.station_rows_path),
                ("map_segments", self.segment_rows_path),
            )
            if path is not None
        }

    @classmethod
    def from_dict(cls, snapshot) -> CompletedAnalysis:
        _require_fields(snapshot, {
            "analysis", "outcome", "evidence_path", "station_rows_path",
            "segment_rows_path", "selected_decode_filter_mode", "query_fetches", "diagnostic",
        }, "Completed analysis")
        if not isinstance(snapshot["query_fetches"], (list, tuple)):
            raise TypeError("Completed query trace must be a list or tuple")
        diagnostic = snapshot["diagnostic"]
        return cls(
            analysis=CompletedAnalysisIdentity.from_dict(snapshot["analysis"]),
            outcome=snapshot["outcome"],
            evidence_path=snapshot["evidence_path"],
            station_rows_path=snapshot["station_rows_path"],
            segment_rows_path=snapshot["segment_rows_path"],
            selected_decode_filter_mode=snapshot["selected_decode_filter_mode"],
            query_fetches=tuple(CompletedQueryFetch.from_dict(fetch) for fetch in snapshot["query_fetches"]),
            diagnostic=ResultDiagnostic.from_dict(diagnostic) if diagnostic is not None else None,
        )

    def to_dict(self) -> dict:
        return {
            "analysis": self.analysis.to_dict(),
            "outcome": self.outcome,
            "evidence_path": self.evidence_path,
            "station_rows_path": self.station_rows_path,
            "segment_rows_path": self.segment_rows_path,
            "selected_decode_filter_mode": self.selected_decode_filter_mode,
            "query_fetches": tuple(fetch.to_dict() for fetch in self.query_fetches),
            "diagnostic": self.diagnostic.to_dict() if self.diagnostic is not None else None,
        }


@dataclass(frozen=True, slots=True)
class CompletedRun:
    """Final publication marker for one source-pinned, completely prepared run."""

    run_id: int
    request_fingerprint: str
    analysis_plan_fingerprint: str
    database_source: str
    analyses: tuple[CompletedAnalysis, ...]
    map_data_schema_version: int
    schema_version: int = COMPLETED_RUN_SNAPSHOT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != COMPLETED_RUN_SNAPSHOT_SCHEMA_VERSION:
            raise ValueError("Completed-run snapshot schema version is unsupported")
        if type(self.run_id) is not int or self.run_id < 0:
            raise ValueError("Completed run ID must be a nonnegative integer")
        if type(self.map_data_schema_version) is not int or self.map_data_schema_version < 1:
            raise ValueError("Completed map schema version must be a positive integer")
        _require_text(self.request_fingerprint, "request_fingerprint")
        _require_text(self.analysis_plan_fingerprint, "analysis_plan_fingerprint")
        object.__setattr__(self, "database_source", DatabaseSource(self.database_source).value)
        if not isinstance(self.analyses, (list, tuple)) or not self.analyses:
            raise ValueError("Completed run requires at least one analysis")
        if not all(isinstance(analysis, CompletedAnalysis) for analysis in self.analyses):
            raise TypeError("Completed run requires typed analysis records")
        object.__setattr__(self, "analyses", tuple(self.analyses))
        identities = [analysis.analysis.id for analysis in self.analyses]
        if len(set(identities)) != len(identities):
            raise ValueError("Completed analysis IDs must be distinct")

    @classmethod
    def from_dict(cls, snapshot) -> CompletedRun:
        if not isinstance(snapshot, Mapping):
            raise TypeError("Completed-run snapshot must be a mapping")
        if snapshot.get("schema_version") != COMPLETED_RUN_SNAPSHOT_SCHEMA_VERSION:
            raise ValueError("Completed-run snapshot schema version is unsupported")
        _require_fields(snapshot, {
            "schema_version", "map_data_schema_version", "run_id", "request_fingerprint",
            "analysis_plan_fingerprint", "database_source", "analyses",
        }, "Completed run")
        if not isinstance(snapshot["analyses"], (list, tuple)):
            raise TypeError("Completed run analyses must be a list or tuple")
        return cls(
            run_id=snapshot["run_id"],
            request_fingerprint=snapshot["request_fingerprint"],
            analysis_plan_fingerprint=snapshot["analysis_plan_fingerprint"],
            database_source=snapshot["database_source"],
            analyses=tuple(CompletedAnalysis.from_dict(analysis) for analysis in snapshot["analyses"]),
            map_data_schema_version=snapshot["map_data_schema_version"],
            schema_version=snapshot["schema_version"],
        )

    def to_dict(self) -> dict:
        """Serialize explicitly without copying scientific data or runtime state."""
        return {
            "schema_version": self.schema_version,
            "map_data_schema_version": self.map_data_schema_version,
            "run_id": self.run_id,
            "request_fingerprint": self.request_fingerprint,
            "analysis_plan_fingerprint": self.analysis_plan_fingerprint,
            "database_source": self.database_source,
            "analyses": tuple(analysis.to_dict() for analysis in self.analyses),
        }
