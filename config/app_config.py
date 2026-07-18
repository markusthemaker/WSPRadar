"""Application metadata, URLs, cache settings, and data limits."""

import os

APP_VERSION = "v0.97"
LOGO_URL = "https://raw.githubusercontent.com/markusthemaker/WSPRadar/main/img/WSPRadar-2x1.png"
APP_URL = "https://wspradar.streamlit.app"
DB_URL = "https://db1.wspr.live/"

CACHE_DIR = "./.wspr_cache"
CACHE_TTL_SEC = 3600
MAX_DAYS_HISTORY = 31

# WSPR.live transport guardrails. The read timeout is socket inactivity, not a
# total request-duration limit; byte ceilings apply to decompressed response data.
WSPR_HTTP_CONNECT_TIMEOUT_SEC = 10
WSPR_HTTP_READ_TIMEOUT_SEC = 60
WSPR_CSV_MAX_RESPONSE_BYTES = 64 * 1024 * 1024
WSPR_PARQUET_MAX_RESPONSE_BYTES = 64 * 1024 * 1024

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
