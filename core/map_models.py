"""Data and figure contracts at the map science/presentation boundary."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass
class MapData:
    """Pure map aggregates independent of language, labels, and theme."""

    station_rows: pd.DataFrame
    segment_rows: pd.DataFrame
    analysis_id: str
    is_compare: bool
    is_sequential: bool
    analysis_kind: str


@dataclass
class MapFigure:
    """Rendered map presentation and the pure data used to create it."""

    figure: Any
    map_data: MapData
    footer_text: str
