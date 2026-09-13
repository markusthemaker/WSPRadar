"""Validated execution plans without UI or scientific-runtime dependencies."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass, fields, replace
from datetime import datetime


DECODE_FILTER_STRICT = "strict_code_1"
DECODE_FILTER_LEGACY = "legacy_no_code"


@dataclass(frozen=True, slots=True)
class AnalysisPlan(Mapping[str, object]):
    """One immutable plan shared by query preparation and result presentation.

    Mapping access preserves the existing consumer boundary, including omitted
    optional fields. ``title`` is presentation metadata and must remain outside
    scientific fingerprints. SQL is retained verbatim; validation checks the
    plan's explicit mode and provenance contract without interpreting its text.
    """

    id: str
    title: str
    analysis_kind: str
    result_family: str
    is_compare: bool
    is_sequential: bool
    response_format: str
    query: str
    decode_filter_mode: str
    is_local_median: bool | None = None
    absolute_mode: str | None = None
    absolute_method_version: str | None = None
    analysis_start_utc: datetime | None = None
    analysis_end_utc: datetime | None = None
    legacy_query: str | None = None
    legacy_decode_filter_mode: str | None = None

    def __post_init__(self) -> None:
        for field_name in ("id", "title", "analysis_kind", "result_family", "response_format"):
            field_value = getattr(self, field_name)
            if not isinstance(field_value, str) or not field_value.strip():
                raise ValueError(f"Analysis plan {field_name} must be a non-empty string")
        if not isinstance(self.query, str):
            raise TypeError("Analysis plan query must be a string")
        for field_name in ("is_compare", "is_sequential"):
            if not isinstance(getattr(self, field_name), bool):
                raise TypeError(f"Analysis plan {field_name} must be a boolean")
        if self.is_local_median is not None and not isinstance(self.is_local_median, bool):
            raise TypeError("Analysis plan is_local_median must be a boolean when present")
        if self.decode_filter_mode not in (DECODE_FILTER_STRICT, DECODE_FILTER_LEGACY):
            raise ValueError("Analysis plan decode_filter_mode is unsupported")
        if self.legacy_query is not None and not isinstance(self.legacy_query, str):
            raise TypeError("Analysis plan legacy_query must be a string when present")
        if self.legacy_query is None:
            if self.legacy_decode_filter_mode is not None:
                raise ValueError("Analysis plan legacy provenance requires legacy_query")
        elif self.legacy_decode_filter_mode != DECODE_FILTER_LEGACY:
            raise ValueError("Analysis plan legacy_query requires legacy_no_code provenance")

        if self.analysis_kind == "opportunity":
            if self.result_family != "performance" or self.is_compare or self.is_sequential:
                raise ValueError("Opportunity plans require non-comparison Performance semantics")
            if self.response_format != "parquet":
                raise ValueError("Opportunity plans require parquet responses")
            if self.is_local_median:
                raise ValueError("Opportunity plans cannot use Local Median")
            if self.absolute_mode not in ("TX", "RX"):
                raise ValueError("Opportunity plans require an explicit TX or RX absolute_mode")
            if not isinstance(self.absolute_method_version, str) or not self.absolute_method_version.strip():
                raise ValueError("Opportunity plans require absolute_method_version")
        elif self.analysis_kind == "comparison":
            if self.result_family != "benchmark" or not self.is_compare:
                raise ValueError("Comparison plans require Benchmark comparison semantics")
            if self.response_format != "csv":
                raise ValueError("Comparison plans require csv responses")
            if self.absolute_mode is not None or self.absolute_method_version is not None:
                raise ValueError("Comparison plans cannot carry Performance method metadata")
            if self.is_sequential and self.is_local_median:
                raise ValueError("Sequential comparison plans cannot use Local Median")
            if self.analysis_start_utc is None or self.analysis_end_utc is None:
                raise ValueError("Comparison plans require their analysis time window")
        else:
            raise ValueError("Analysis plan analysis_kind is unsupported")

        if self.analysis_start_utc is not None or self.analysis_end_utc is not None:
            if not isinstance(self.analysis_start_utc, datetime) or not isinstance(self.analysis_end_utc, datetime):
                raise TypeError("Analysis plan time boundaries must both be datetimes")
            if not self.analysis_start_utc < self.analysis_end_utc:
                raise ValueError("Analysis plan end must be after its start")

    @classmethod
    def from_mapping(cls, analysis: Mapping[str, object]) -> AnalysisPlan:
        """Validate one boundary mapping, or reuse an already validated plan."""
        if isinstance(analysis, cls):
            return analysis
        if not isinstance(analysis, Mapping):
            raise TypeError("Analysis plan must be a mapping")
        try:
            return cls(**analysis)
        except TypeError as exc:
            raise TypeError(f"Invalid analysis plan fields: {exc}") from exc

    def with_decode_filter_mode(self, decode_filter_mode: str) -> AnalysisPlan:
        """Restore selected decode provenance without changing the planned SQL."""
        if decode_filter_mode == self.decode_filter_mode:
            return self
        return replace(self, decode_filter_mode=decode_filter_mode)

    def for_legacy_query(self) -> AnalysisPlan:
        """Select the existing historical query without mutating the strict plan."""
        if not self.legacy_query:
            raise ValueError("Analysis plan has no legacy query to select")
        return replace(
            self,
            query=self.legacy_query,
            decode_filter_mode=self.legacy_decode_filter_mode,
        )

    def __getitem__(self, field_name: str) -> object:
        if field_name not in self.__dataclass_fields__:
            raise KeyError(field_name)
        field_value = getattr(self, field_name)
        if field_value is None:
            raise KeyError(field_name)
        return field_value

    def __iter__(self) -> Iterator[str]:
        return (
            plan_field.name
            for plan_field in fields(self)
            if getattr(self, plan_field.name) is not None
        )

    def __len__(self) -> int:
        return sum(1 for _field_name in self)
