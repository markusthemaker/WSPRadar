"""Data and figure contracts at the map science/presentation boundary."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from core.result_diagnostics import ResultDiagnostic


@dataclass
class MapData:
    """Pure map aggregates independent of language, labels, and theme."""

    station_rows: pd.DataFrame
    segment_rows: pd.DataFrame
    analysis_id: str
    is_compare: bool
    is_sequential: bool
    analysis_kind: str
    diagnostic: ResultDiagnostic | None = None


@dataclass
class MapFigure:
    """Rendered map presentation and the pure data used to create it."""

    figure: Any
    map_data: MapData
    footer_text: str


@dataclass(frozen=True)
class EmptyMapResult:
    """A diagnosed aggregate outcome that must not enter map presentation."""

    diagnostic: ResultDiagnostic


@dataclass(frozen=True)
class MapDataBuildResult:
    """Pure aggregate outcome before language or figure rendering."""

    map_data: MapData | None
    diagnostic: ResultDiagnostic | None = None
