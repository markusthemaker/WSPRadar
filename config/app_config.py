"""Application metadata, URLs, cache settings, and data limits."""

import os


APP_VERSION = "v0.95"
LOGO_URL = "https://raw.githubusercontent.com/markusthemaker/WSPRadar/main/img/WSPRadar-2x1.png"
APP_URL = "https://wspradar.streamlit.app"
DB_URL = "https://db1.wspr.live/"

CACHE_DIR = "./.wspr_cache"
CACHE_TTL_SEC = 3600
MAX_DAYS_HISTORY = 31

os.makedirs(CACHE_DIR, exist_ok=True)
