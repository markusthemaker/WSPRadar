"""Structured data-fetch contracts shared by core and UI adapters."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


class FetchSource(str, Enum):
    WSPR_LIVE = "wspr.live"
    MEMORY_CACHE = "RAM cache"
    DISK_CACHE = "disk cache"


@dataclass(frozen=True)
class FetchError:
    """Machine-readable fetch failure with optional HTTP diagnostics."""

    code: str
    message: str
    status_code: int | None = None
    response_text: str = ""
    query: str = ""


@dataclass
class FetchResult:
    """Fetched rows or artifact metadata plus source and structured failure state."""

    dataframe: "pd.DataFrame | None" = None
    artifact_path: Path | None = None
    source: FetchSource = FetchSource.WSPR_LIVE
    error: FetchError | None = None

    @property
    def database_hit(self) -> bool:
        return self.source == FetchSource.WSPR_LIVE

    @property
    def empty(self) -> bool:
        return self.dataframe is None or self.dataframe.empty
