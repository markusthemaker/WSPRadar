"""Explicit contexts shared by Inspector preparation and presentation.

These records retain references to existing inputs. They neither discover
session state nor copy, cache, or prepare scientific evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


def validate_inspector_analysis_mode(*, analysis_kind, is_compare):
    """Return whether the mode is Performance and reject retired combinations."""
    if analysis_kind == "opportunity" and not is_compare:
        return True
    if analysis_kind == "comparison" and is_compare:
        return False
    raise ValueError(
        "Segment Inspector mode must be Performance "
        "(analysis_kind='opportunity', is_compare=False) or Benchmark "
        "(analysis_kind='comparison', is_compare=True)."
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class InspectorContext:
    """Completed analysis and presentation inputs for one fragment invocation."""

    analysis_id: str
    title: str
    is_compare: bool
    is_sequential: bool
    parquet_path: Any
    line1_str: str
    translations: Mapping[str, str]
    max_peer_distance_km: float
    analysis_context: Any
    presentation_context: Any
    analysis_kind: str
    run_id: int
    analysis_start_t: Any = None
    analysis_end_t: Any = None
    show_export_button: bool = False
    timing_collector: Any = None

    def __post_init__(self):
        validate_inspector_analysis_mode(
            analysis_kind=self.analysis_kind,
            is_compare=self.is_compare,
        )

    @property
    def is_opportunity(self) -> bool:
        return self.analysis_kind == "opportunity"

    @property
    def language(self) -> str:
        return self.presentation_context.language


@dataclass(frozen=True, slots=True, kw_only=True)
class InspectorScope:
    """Resolved scientific narrowing and its current presentation labels."""

    selected_ranges: tuple[str, ...]
    selected_directions: tuple[str, ...]
    range_summary: str
    direction_summary: str
    selected_segment: str
    active_scope_summary: str
    scope_token: str
    distance_scope_intervals: tuple[tuple[float, float], ...] = ()


@dataclass(frozen=True, slots=True, kw_only=True)
class ScopeControlsView:
    """Scope controls and the existing containers that receive segment views."""

    scope: InspectorScope
    level_two_container: Any
    scope_summary_placeholder: Any


@dataclass(frozen=True, slots=True, kw_only=True)
class StationInsightsView:
    """Rendered table selection references for lazy selected-station preparation."""

    displayed_table: Any
    export_station_table: Any
    full_station_table: Any
    selected_station_table: Any
    selected_rows: tuple[int, ...]
    station_column: str
    locator_column: str
    distance_column: str
    azimuth_column: str
    show_non_joint: bool
    level_three_container: Any
    show_zero_target: bool = False
