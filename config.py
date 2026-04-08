"""
Zentrale Konfigurationsdatei für WSPRadar.
Enthält alle Konstanten, Farben, Bounding-Boxen und Grundeinstellungen.
"""
import os
import datetime
from datetime import time as dt_time

# ==========================================
# APP METADATA & URLs
# ==========================================
APP_VERSION = "v1.6"  
LOGO_URL = "https://raw.githubusercontent.com/markusthemaker/WSPRadar/main/img/WSPRadar-2x1.png"
APP_URL = "https://wspradar.streamlit.app" 
DB_URL = "https://db1.wspr.live/"

# ==========================================
# CACHING & DATABASE LIMITS
# ==========================================
CACHE_DIR = "./.wspr_cache"
CACHE_TTL_SEC = 3600
MAX_DAYS_HISTORY = 7

# Cache-Ordner beim Import automatisch anlegen
os.makedirs(CACHE_DIR, exist_ok=True)

# ==========================================
# DEMO PROFILES (Guided Sandbox)
# ==========================================
DEMO_PROFILES = {
    "radius": {
        "callsign": "DL1MKS",
        "qth": "JN37",
        "band": "20m",
        "start_d": datetime.date(2026, 3, 27),
        "end_d": datetime.date(2026, 3, 31),
        "start_t": dt_time(0, 0),
        "end_t": dt_time(0, 0),
        "ref_stations": 25
    },
    "buddy": {
        "callsign": "DL1MKS",
        "qth": "JN37",
        "band": "20m",
        "start_d": datetime.date(2026, 3, 27),
        "end_d": datetime.date(2026, 3, 31),
        "start_t": dt_time(0, 0),
        "end_t": dt_time(0, 0),
        "ref_callsign": ""  # Leer = Feld bleibt im UI offen für Nutzereingabe
    },
    "self_rx": {
        "callsign": "DL1MKS",
        "qth": "JN37",
        "band": "20m",
        "start_d": datetime.date(2026, 4, 6),
        "end_d": datetime.date(2026, 4, 6),
        "start_t": dt_time(10, 0),
        "end_t": dt_time(23, 59),
        "self_call_b": "DL1MKS/P"
    },
    "self_tx": {
        "callsign": "DL1MKS",
        "qth": "JN37",
        "band": "20m",
        "start_d": datetime.date(2026, 3, 27),
        "end_d": datetime.date(2026, 3, 31),
        "start_t": dt_time(0, 0),
        "end_t": dt_time(0, 0)
    }
}

# ==========================================
# GEOSPATIAL CONSTANTS
# ==========================================
EARTH_RADIUS_KM = 6371.0
EARTH_RADIUS_M = 6371000.0
MAX_DYNAMIC_RADIUS_KM = 250  # Hard-Cap für die dynamische Referenz-Suche

# ==========================================
# PLOT RENDERING SETTINGS
# ==========================================
PLOT_DPI = 150
FIG_SIZE = (12, 12.5)                  
MAP_BBOX = [0.0, 0.1, 0.9, 0.8]     
CBAR_BBOX = [0.88, 0.20, 0.02, 0.55]  
LEG_BBOX = (1.02, 0.90)               
TITLE_POS = (0.45, 0.95)             
COMPASS_LABEL_OFFSET = 0.97          

# Fonts
FONT_RINGS = 13                       
FONT_COMPASS = 13                     
FONT_POLES = 10                       
FONT_LEGEND = 13                      
FONT_CBAR = 13    
FONT_FOOTER = 10                    

# Azimuth & Segmente
AZIMUTH_STEP = 22.50
COMPASS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
DIST_BINS = [0, 2500, 5000, 7500, 10000, 15000, 20000, 22000]
THICK_RINGS = [5000, 10000, 15000, 20000]
THIN_RINGS = [2500, 7500]

# Scatter Plot Colors
COLOR_JOINT = "#00ff00"
COLOR_BOTH_ASYNC = "#ffbe33"
COLOR_ONLY_ME = "#cc00ff"
COLOR_ONLY_REF = "#ffffff"

# Frequenzbänder Mapping
BAND_MAP = {
    '160m':'1', '80m':'3', '60m':'5', '40m':'7', '30m':'10', 
    '20m':'14', '17m':'18', '15m':'21', '12m':'24', '10m':'28', 
    '6m':'50', 'All':''
}