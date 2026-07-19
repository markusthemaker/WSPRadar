"""Application metadata, URLs, cache settings, and data limits."""

import os
from dataclasses import dataclass

APP_VERSION = "v0.98"
LOGO_URL = "https://raw.githubusercontent.com/markusthemaker/WSPRadar/main/img/WSPRadar-2x1.png"
APP_URL = "https://wspradar.streamlit.app"


@dataclass(frozen=True)
class WsprDatabaseProviderConfig:
    """Describe one read-only WSPR ClickHouse source and its local safety policy."""

    key: str
    display_name: str
    url: str
    enabled: bool
    request_limit: int
    request_window_seconds: float
    circuit_failure_threshold: int
    rate_limit_cooldown_seconds: float
    failure_cooldown_seconds: float


# Priority is significant: the first eligible source is selected for a complete
# analysis run. WD limits are conservative application guardrails, not claims
# about undocumented upstream quotas.
WSPR_DATABASE_PROVIDERS = (
    WsprDatabaseProviderConfig(
        key="wspr_live",
        display_name="wspr.live",
        url="https://db1.wspr.live/",
        enabled=True,
        request_limit=20,
        request_window_seconds=60.0,
        circuit_failure_threshold=1,
        rate_limit_cooldown_seconds=60.0,
        failure_cooldown_seconds=30.0,
    ),
    WsprDatabaseProviderConfig(
        key="wd2",
        display_name="WD2",
        url="https://wd2.wsprdaemon.org/",
        enabled=True,
        request_limit=20,
        request_window_seconds=60.0,
        circuit_failure_threshold=1,
        rate_limit_cooldown_seconds=60.0,
        failure_cooldown_seconds=30.0,
    ),
    WsprDatabaseProviderConfig(
        key="wd1",
        display_name="WD1",
        url="https://wd1.wsprdaemon.org/",
        enabled=True,
        request_limit=20,
        request_window_seconds=60.0,
        circuit_failure_threshold=1,
        rate_limit_cooldown_seconds=60.0,
        failure_cooldown_seconds=30.0,
    ),
)

# Compatibility alias for code and integrations that still refer to the
# historical single-primary URL.
DB_URL = WSPR_DATABASE_PROVIDERS[0].url

CACHE_DIR = "./.wspr_cache"
# Standard query results and session evidence remain short-lived. Guided demos
# use fixed historical windows, so their raw query results receive a separate
# absolute freshness lifetime without extending on cache hits.
STANDARD_QUERY_CACHE_TTL_SEC = 3600
DEMO_QUERY_CACHE_TTL_SEC = 24 * 3600
SESSION_ARTIFACT_TTL_SEC = 3600

# Compatibility alias for integrations that still import the former shared
# cache TTL. Runtime cache policy uses the lifecycle-specific constants above.
CACHE_TTL_SEC = STANDARD_QUERY_CACHE_TTL_SEC
MAX_DAYS_HISTORY = 31

# WSPR transport guardrails. The read timeout is socket inactivity, not a
# total request-duration limit; byte ceilings apply to decompressed response data.
WSPR_HTTP_CONNECT_TIMEOUT_SEC = 10
WSPR_HTTP_READ_TIMEOUT_SEC = 60
WSPR_CSV_MAX_RESPONSE_BYTES = 64 * 1024 * 1024
WSPR_PARQUET_MAX_RESPONSE_BYTES = 64 * 1024 * 1024
WSPR_PROVIDER_ACQUIRE_TIMEOUT_SEC = 600
WSPR_PROVIDER_ACQUIRE_POLL_INTERVAL_SEC = 0.5

# Process-wide admission limits for resource-intensive analysis runs.
ANALYSIS_MAX_CONCURRENT = 2
ANALYSIS_MAX_QUEUED = 10
ANALYSIS_QUEUE_WAIT_TIMEOUT_SEC = 600
ANALYSIS_ACTIVE_LEASE_TIMEOUT_SEC = 1800
ANALYSIS_QUEUE_POLL_INTERVAL_SEC = 0.5

# Process-wide admission limits for high-resolution result ZIP preparation.
EXPORT_MAX_CONCURRENT = 1
EXPORT_MAX_QUEUED = 10
EXPORT_QUEUE_WAIT_TIMEOUT_SEC = 600
EXPORT_ACTIVE_LEASE_TIMEOUT_SEC = 1800
EXPORT_QUEUE_POLL_INTERVAL_SEC = 0.5

# Per-session Segment Inspector cache limits. The cache retains compact station-level
# view models, figure recipes, and preview PNG bytes, never raw opportunity artifacts.
INSPECTOR_CACHE_MAX_BYTES = 5 * 1024 * 1024
INSPECTOR_CACHE_OPTIONS_MAX_ENTRIES = 2
INSPECTOR_CACHE_SEGMENT_MAX_ENTRIES = 4
INSPECTOR_CACHE_SELECTED_MAX_ENTRIES = 8
INSPECTOR_CACHE_PNG_MAX_ENTRIES = 12

os.makedirs(CACHE_DIR, exist_ok=True)
