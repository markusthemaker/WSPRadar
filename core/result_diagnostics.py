"""Language-free diagnostics for completed analysis result availability."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


NO_SOURCE_ROWS = "no_source_rows"
SOURCE_ROWS_FILTERED_OUT = "source_rows_filtered_out"
PERFORMANCE_NO_ELIGIBLE_STATION = "performance_no_eligible_station"
PERFORMANCE_NO_QUALIFYING_SEGMENT = "performance_no_qualifying_segment"
BENCHMARK_NO_QUALIFYING_RESULT = "benchmark_no_qualifying_result"

RESULT_DIAGNOSTIC_REASONS = frozenset({
    NO_SOURCE_ROWS,
    SOURCE_ROWS_FILTERED_OUT,
    PERFORMANCE_NO_ELIGIBLE_STATION,
    PERFORMANCE_NO_QUALIFYING_SEGMENT,
    BENCHMARK_NO_QUALIFYING_RESULT,
})

_APPLIED_THRESHOLD_KEYS = frozenset({
    "min_confirmed_opportunities_per_peer",
    "min_joint_spots_per_station",
    "min_joint_stations_per_map_segment",
})
_MEASURED_COUNT_KEYS = frozenset({
    "source_row_count",
    "retained_row_count",
    "station_identity_count",
    "eligible_station_count",
    "maximum_confirmed_opportunities_per_station",
    "qualifying_segment_count",
    "maximum_stations_per_segment",
})


def _normalize_nonnegative_integer_mapping(
    values: Mapping[str, int] | None,
    *,
    allowed_keys: frozenset[str],
    field_name: str,
) -> tuple[tuple[str, int], ...]:
    """Return a stable immutable scalar mapping after strict validation."""
    if values is None:
        return ()
    if not isinstance(values, Mapping):
        raise TypeError(f"Result diagnostic {field_name} must be a mapping")
    unknown_keys = set(values).difference(allowed_keys)
    if unknown_keys:
        raise ValueError(
            f"Result diagnostic {field_name} contains unknown keys: "
            + ", ".join(sorted(unknown_keys))
        )
    normalized = []
    for key, value in values.items():
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(
                f"Result diagnostic {field_name}.{key} must be a "
                "non-negative integer"
            )
        normalized.append((str(key), int(value)))
    return tuple(sorted(normalized))


@dataclass(frozen=True)
class ResultDiagnostic:
    """One reproducible empty or partial-result reason with scalar evidence.

    The stored threshold names are canonical analysis fields. Measurements are
    deliberately limited to counts calculated by the scientific pipeline; the
    presentation layer must not infer additional counts from an empty artifact.
    """

    reason: str
    applied_thresholds: tuple[tuple[str, int], ...] = ()
    measured_counts: tuple[tuple[str, int], ...] = ()

    @classmethod
    def create(
        cls,
        reason: str,
        *,
        applied_thresholds: Mapping[str, int] | None = None,
        measured_counts: Mapping[str, int] | None = None,
    ) -> "ResultDiagnostic":
        normalized_reason = str(reason)
        if normalized_reason not in RESULT_DIAGNOSTIC_REASONS:
            raise ValueError(
                f"Unsupported result diagnostic reason: {normalized_reason}"
            )
        diagnostic = cls(
            reason=normalized_reason,
            applied_thresholds=_normalize_nonnegative_integer_mapping(
                applied_thresholds,
                allowed_keys=_APPLIED_THRESHOLD_KEYS,
                field_name="applied_thresholds",
            ),
            measured_counts=_normalize_nonnegative_integer_mapping(
                measured_counts,
                allowed_keys=_MEASURED_COUNT_KEYS,
                field_name="measured_counts",
            ),
        )
        diagnostic._validate_reason_contract()
        return diagnostic

    def _validate_reason_contract(self) -> None:
        """Reject incomplete or internally contradictory diagnostic evidence."""
        thresholds = dict(self.applied_thresholds)
        counts = dict(self.measured_counts)

        if self.reason == NO_SOURCE_ROWS:
            if counts.get("source_row_count") != 0:
                raise ValueError(
                    "no_source_rows requires source_row_count equal to zero"
                )
            return

        if self.reason == SOURCE_ROWS_FILTERED_OUT:
            if counts.get("source_row_count", 0) <= 0:
                raise ValueError(
                    "source_rows_filtered_out requires a positive source_row_count"
                )
            if counts.get("retained_row_count") != 0:
                raise ValueError(
                    "source_rows_filtered_out requires retained_row_count equal to zero"
                )
            return

        if self.reason == PERFORMANCE_NO_ELIGIBLE_STATION:
            required_thresholds = {"min_confirmed_opportunities_per_peer"}
            required_counts = {
                "station_identity_count",
                "eligible_station_count",
                "maximum_confirmed_opportunities_per_station",
            }
            if not required_thresholds.issubset(thresholds):
                raise ValueError(
                    "performance_no_eligible_station requires the applied "
                    "confirmed-opportunity threshold"
                )
            if not required_counts.issubset(counts):
                raise ValueError(
                    "performance_no_eligible_station requires station and "
                    "confirmed-opportunity measurements"
                )
            if counts["eligible_station_count"] != 0:
                raise ValueError(
                    "performance_no_eligible_station requires zero eligible stations"
                )
            if (
                counts["maximum_confirmed_opportunities_per_station"]
                >= thresholds["min_confirmed_opportunities_per_peer"]
            ):
                raise ValueError(
                    "performance_no_eligible_station maximum must be below "
                    "the applied threshold"
                )
            return

        if self.reason == PERFORMANCE_NO_QUALIFYING_SEGMENT:
            required_thresholds = {
                "min_confirmed_opportunities_per_peer",
                "min_joint_stations_per_map_segment",
            }
            required_counts = {
                "eligible_station_count",
                "qualifying_segment_count",
                "maximum_stations_per_segment",
            }
            if not required_thresholds.issubset(thresholds):
                raise ValueError(
                    "performance_no_qualifying_segment requires both applied "
                    "Performance thresholds"
                )
            if not required_counts.issubset(counts):
                raise ValueError(
                    "performance_no_qualifying_segment requires eligible-station "
                    "and segment measurements"
                )
            if counts["eligible_station_count"] <= 0:
                raise ValueError(
                    "performance_no_qualifying_segment requires eligible stations"
                )
            if counts["qualifying_segment_count"] != 0:
                raise ValueError(
                    "performance_no_qualifying_segment requires zero qualifying segments"
                )
            if (
                counts["maximum_stations_per_segment"]
                >= thresholds["min_joint_stations_per_map_segment"]
            ):
                raise ValueError(
                    "performance_no_qualifying_segment maximum must be below "
                    "the applied segment threshold"
                )
            return

        if self.reason == BENCHMARK_NO_QUALIFYING_RESULT:
            required_thresholds = {
                "min_joint_spots_per_station",
                "min_joint_stations_per_map_segment",
            }
            if not required_thresholds.issubset(thresholds):
                raise ValueError(
                    "benchmark_no_qualifying_result requires both applied "
                    "Benchmark thresholds"
                )
            if counts.get("qualifying_segment_count") != 0:
                raise ValueError(
                    "benchmark_no_qualifying_result requires zero qualifying segments"
                )

    @classmethod
    def from_dict(cls, values) -> "ResultDiagnostic":
        """Validate and restore one session-safe diagnostic dictionary."""
        if not isinstance(values, dict):
            raise TypeError("Result diagnostic snapshot must be a dictionary")
        if set(values) != {"reason", "applied_thresholds", "measured_counts"}:
            raise ValueError("Result diagnostic snapshot has an invalid shape")
        return cls.create(
            values["reason"],
            applied_thresholds=values["applied_thresholds"],
            measured_counts=values["measured_counts"],
        )

    def to_dict(self) -> dict:
        """Return one JSON-safe snapshot representation."""
        return {
            "reason": self.reason,
            "applied_thresholds": dict(self.applied_thresholds),
            "measured_counts": dict(self.measured_counts),
        }


def applied_thresholds_for_analysis(
    analysis,
    analysis_context,
) -> dict[str, int]:
    """Return configured evidence gates applicable to one analysis plan."""
    if analysis.get("analysis_kind") == "opportunity":
        threshold_names = (
            "min_confirmed_opportunities_per_peer",
            "min_joint_stations_per_map_segment",
        )
    elif analysis.get("is_compare"):
        threshold_names = (
            "min_joint_spots_per_station",
            "min_joint_stations_per_map_segment",
        )
    else:
        return {}

    thresholds = {}
    for threshold_name in threshold_names:
        threshold_value = getattr(analysis_context, threshold_name, None)
        if (
            not isinstance(threshold_value, bool)
            and isinstance(threshold_value, int)
            and threshold_value >= 0
        ):
            thresholds[threshold_name] = int(threshold_value)
    return thresholds
