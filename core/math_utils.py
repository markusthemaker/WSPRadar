"""
Mathematische Hilfsfunktionen (Geometrie, Astronomie, Zeit).
"""
import numpy as np
import math

from core.input_validation import (
    is_valid_6char_locator,
    is_valid_callsign,
    is_valid_locator,
    normalize_ascii_upper,
)
from core.time_utils import quantize_time

def locator_to_latlon(grid: str) -> tuple:
    """Convert a validated four- or six-character Maidenhead locator to Lat/Lon."""
    stripped_grid = str(grid or "").strip()
    if not is_valid_locator(stripped_grid):
        raise ValueError("A valid 4- or 6-character Maidenhead locator is required.")
    grid = normalize_ascii_upper(stripped_grid)
    lon = -180.0 + (ord(grid[0]) - 65) * 20.0 + int(grid[2]) * 2.0
    lat = -90.0 + (ord(grid[1]) - 65) * 10.0 + int(grid[3]) * 1.0
    if len(grid) >= 6:
        lon += (ord(grid[4]) - 65) * (2.0 / 24.0) + (1.0 / 24.0)
        lat += (ord(grid[5]) - 65) * (1.0 / 24.0) + (1.0 / 48.0)
    else:
        lon += 1.0
        lat += 0.5
    return lat, lon

def get_solar_state(dt, lat, lon):
    """Berechnet den Sonnenstand (Tag, Nacht, Greyline) für eine gegebene Zeit und Koordinate."""
    import ephem

    obs = ephem.Observer()
    obs.lat = str(lat)
    obs.lon = str(lon)
    obs.date = dt.to_pydatetime()
    sun = ephem.Sun(obs)
    alt = np.degrees(sun.alt)
    if alt > 6: return 'day'
    elif alt < -6: return 'night'
    else: return 'grey'
