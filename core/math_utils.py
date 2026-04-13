"""
Mathematische Hilfsfunktionen (Geometrie, Astronomie, Zeit).
"""
import numpy as np
import math
import re  # Wichtig für die Rufzeichen-Validierung
import ephem
from datetime import datetime

# Strict allowlist for amateur-radio callsigns.
# Valid characters: A-Z, 0-9, and the portable/mobile suffix separator '/'.
# Length range: 3 (e.g. "W1A") to 15 (e.g. "VK2FXXX/MM") characters.
_CALLSIGN_RE = re.compile(r'^[A-Z0-9/]{3,15}$')

def is_valid_callsign(call: str) -> bool:
    """Returns True only if *call* consists solely of A-Z, 0-9, and '/' (3-15 chars).

    Used as a defense-in-depth guard before callsigns are interpolated into
    ClickHouse SQL queries to prevent SQL injection.
    """
    return bool(_CALLSIGN_RE.match(call.upper().strip()))

def locator_to_latlon(grid: str) -> tuple:
    """Konvertiert einen Maidenhead Locator (4 oder 6 Stellen) in Lat/Lon."""
    grid = grid.upper().strip()
    if len(grid) < 4: return 0.0, 0.0
    lon = -180.0 + (ord(grid[0]) - 65) * 20.0 + int(grid[2]) * 2.0
    lat = -90.0 + (ord(grid[1]) - 65) * 10.0 + int(grid[3]) * 1.0
    if len(grid) >= 6:
        lon += (ord(grid[4]) - 65) * (2.0 / 24.0) + (1.0 / 24.0)
        lat += (ord(grid[5]) - 65) * (1.0 / 24.0) + (1.0 / 48.0)
    else:
        lon += 1.0
        lat += 0.5
    return lat, lon

# LOCATOR VALIDATION (Defense-in-Depth)
_LOCATOR_RE = re.compile(r'^[A-Z]{2}[0-9]{2}([A-Z]{2})?$')

def is_valid_locator(loc: str) -> bool:
    """
    Returns True if the string is a valid 4- or 6-character Maidenhead locator 
    (e.g., 'JN37' or 'JN37AA'). Case-insensitive.
    """
    return bool(_LOCATOR_RE.match(loc.upper().strip()))

def is_valid_6char_locator(grid: str) -> bool:
    """Prüft, ob der Locator exakt 6 gültige Zeichen hat."""
    grid = grid.upper().strip()
    if len(grid) != 6: return False
    if not ('A' <= grid[0] <= 'R' and 'A' <= grid[1] <= 'R'): return False
    if not (grid[2].isdigit() and grid[3].isdigit()): return False
    if not ('A' <= grid[4] <= 'X' and 'A' <= grid[5] <= 'X'): return False
    return True

def get_solar_state(dt, lat, lon):
    """Berechnet den Sonnenstand (Tag, Nacht, Greyline) für eine gegebene Zeit und Koordinate."""
    obs = ephem.Observer()
    obs.lat = str(lat)
    obs.lon = str(lon)
    obs.date = dt.to_pydatetime()
    sun = ephem.Sun(obs)
    alt = np.degrees(sun.alt)
    if alt > 6: return 'day'
    elif alt < -6: return 'night'
    else: return 'grey'

def quantize_time(dt):
    """Quantisiert die Uhrzeit auf das nächste volle 15-Minuten Intervall für besseres DB-Caching."""
    minute = (dt.minute // 15) * 15
    return dt.replace(minute=minute, second=0, microsecond=0)

def calc_wilcoxon_from_paired_arrays(target_vals, ref_vals):
    """
    Calculates Wilcoxon p-value from two pre-paired lists of values.
    Used for Time-Binned Sequential TX Tests where samples are already aggregated pairs.
    """
    try:
        from scipy.stats import wilcoxon
        if len(target_vals) < 5 or len(target_vals) != len(ref_vals):
            return 1.0
        stat, p_value = wilcoxon(target_vals, ref_vals)
        return p_value
    except Exception:
        return 1.0