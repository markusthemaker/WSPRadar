"""Structured data-fetch contracts shared by core and UI adapters."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


class FetchSource(str, Enum):
    """Identify whether rows came from a provider request or a cache tier."""

    WSPR_LIVE = "wspr.live"
    WD2 = "WD2"
    WD1 = "WD1"
    MEMORY_CACHE = "RAM cache"
    DISK_CACHE = "disk cache"

    @property
    def delivery_label(self) -> str:
        """Return the delivery tier without repeating database provenance."""
        if self in {
            FetchSource.WSPR_LIVE,
            FetchSource.WD2,
            FetchSource.WD1,
        }:
            return "database request"
        return self.value


class DatabaseSource(str, Enum):
    """Stable identifiers for the database that originated fetched rows."""

    WSPR_LIVE = "wspr_live"
    WD2 = "wd2"
    WD1 = "wd1"

    @property
    def display_name(self) -> str:
        """Return the concise operator-facing database label."""
        return {
            DatabaseSource.WSPR_LIVE: "wspr.live",
            DatabaseSource.WD2: "WD2",
            DatabaseSource.WD1: "WD1",
        }[self]


class FetchFailureScope(str, Enum):
    """Classify whether retrying another provider can plausibly help."""

    PROVIDER = "provider"
    CAPACITY = "capacity"
    REQUEST = "request"
    LOCAL = "local"


@dataclass(frozen=True)
class FetchError:
    """Machine-readable fetch failure with optional HTTP diagnostics."""

    code: str
    message: str
    status_code: int | None = None
    response_text: str = ""
    query: str = ""
    scope: FetchFailureScope = FetchFailureScope.REQUEST
    retry_after_seconds: float | None = None
    failure_stage: str = ""


@dataclass
class FetchResult:
    """Fetched rows with separate delivery-tier and database provenance."""

    dataframe: "pd.DataFrame | None" = None
    artifact_path: Path | None = None
    source: FetchSource = FetchSource.WSPR_LIVE
    error: FetchError | None = None
    database_source: DatabaseSource = DatabaseSource.WSPR_LIVE

    @property
    def database_hit(self) -> bool:
        """Return whether this result required a direct upstream request."""
        return self.source in {
            FetchSource.WSPR_LIVE,
            FetchSource.WD2,
            FetchSource.WD1,
        }

    @property
    def empty(self) -> bool:
        return self.dataframe is None or self.dataframe.empty
