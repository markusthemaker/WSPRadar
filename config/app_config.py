"""Application metadata, URLs, cache settings, and data limits."""

import os


APP_VERSION = "v0.95"
LOGO_URL = "https://raw.githubusercontent.com/markusthemaker/WSPRadar/main/img/WSPRadar-2x1.png"
APP_URL = "https://wspradar.streamlit.app"
DB_URL = "https://db1.wspr.live/"

CACHE_DIR = "./.wspr_cache"
CACHE_TTL_SEC = 3600
MAX_DAYS_HISTORY = 31

# Process-wide admission limits for resource-intensive analysis runs.
ANALYSIS_MAX_CONCURRENT = 2
ANALYSIS_MAX_QUEUED = 10
ANALYSIS_QUEUE_WAIT_TIMEOUT_SEC = 600
ANALYSIS_ACTIVE_LEASE_TIMEOUT_SEC = 1800
ANALYSIS_QUEUE_POLL_INTERVAL_SEC = 0.5

# Per-session Segment Inspector cache limits. The cache retains compact station-level
# view models, figure recipes, and preview PNG bytes, never raw opportunity artifacts.
INSPECTOR_CACHE_MAX_BYTES = 5 * 1024 * 1024
INSPECTOR_CACHE_OPTIONS_MAX_ENTRIES = 2
INSPECTOR_CACHE_SEGMENT_MAX_ENTRIES = 4
INSPECTOR_CACHE_SELECTED_MAX_ENTRIES = 8
INSPECTOR_CACHE_PNG_MAX_ENTRIES = 12

os.makedirs(CACHE_DIR, exist_ok=True)
