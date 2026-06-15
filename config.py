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
APP_VERSION = "v0.94"
LOGO_URL = "https://raw.githubusercontent.com/markusthemaker/WSPRadar/main/img/WSPRadar-2x1.png"
APP_URL = "https://wspradar.streamlit.app" 
DB_URL = "https://db1.wspr.live/"

# ==========================================
# CACHING & DATABASE LIMITS
# ==========================================
CACHE_DIR = "./.wspr_cache"
CACHE_TTL_SEC = 3600
MAX_DAYS_HISTORY = 31

# Cache-Ordner beim Import automatisch anlegen
os.makedirs(CACHE_DIR, exist_ok=True)

# ==========================================
# DEMO PROFILES (Guided Sandbox)
# ==========================================
DEMO_PROFILES = {
    "vanhamel_rx_calibration": {
        "label": {
            "en": "RX Comparison Calibration. (Dr. Jurgen Vanhamel, Dr. Walter Machiels, Dr. Hervé Lamy)",
            "de": "RX Comparison Calibration. (Dr. Jurgen Vanhamel, Dr. Walter Machiels, Dr. Hervé Lamy)",
        },
        "description": {
            "en": "Publication: Vanhamel, Machiels, Lamy - Using the WSPR Mode for Antenna Performance Evaluation and Propagation Assessment on the 160-m Band [Ref 6] - Chapter 4 - SNR Correction 1.2 dB",
            "de": "Publication: Vanhamel, Machiels, Lamy - Using the WSPR Mode for Antenna Performance Evaluation and Propagation Assessment on the 160-m Band [Ref 6] - Chapter 4 - SNR Correction 1.2 dB",
        },
        "run": {
            "run_mode": "RX",
        },
        "core_parameters": {
            "callsign": "ON4AWM0",
            "qth": "JO20OT",
            "band": "160m",
            "time_mode_key": "opt_custom",
            "start_d": datetime.date(2021, 2, 9),
            "end_d": datetime.date(2021, 2, 13),
            "start_t": dt_time(22, 0),
            "end_t": dt_time(5, 30),
        },
        "comparison": {
            "comp_mode_key": "opt_comp_buddy",
            "ref_callsign": "ON4AWM1",
            "reference_snr_correction_db": 0.0,
        },
        "advanced": {
            "exclude_special_callsigns": False,
            "exclude_moving_stations": False,
            "solar_key": "opt_solar_all",
            "max_dist": 22000,
            "min_joint_spots_per_station": 50,
            "min_joint_stations_per_segment": 1,
        },
        "results_view": {
            "show_non_joint": False,
            "station_evidence_time_bin_compare": "6h",
            "station_evidence_time_bin_absolute": "6h",
        },
    },

    "vanhamel_rx_buddy": {
        "label": {
            "en": "RX Antenna Comparison. Buddy Test. (Dr. Jurgen Vanhamel, Dr. Walter Machiels, Dr. Hervé Lamy)",
            "de": "RX Antenna Comparison. Buddy Test. (Dr. Jurgen Vanhamel, Dr. Walter Machiels, Dr. Hervé Lamy)",
        },
        "description": {
            "en": "Publication: Vanhamel, Machiels, Lamy - Using the WSPR Mode for Antenna Performance Evaluation and Propagation Assessment on the 160-m Band [Ref 6] - resembles Figure 6",
            "de": "Publication: Vanhamel, Machiels, Lamy - Using the WSPR Mode for Antenna Performance Evaluation and Propagation Assessment on the 160-m Band [Ref 6] - resembles Figure 6",
        },
        "run": {
            "run_mode": "RX",
        },
        "core_parameters": {
            "callsign": "ON4AWM0",
            "qth": "JO20OT",
            "band": "160m",
            "time_mode_key": "opt_custom",
            "start_d": datetime.date(2021, 5, 1),
            "end_d": datetime.date(2021, 5, 15),
            "start_t": dt_time(17, 24),
            "end_t": dt_time(7, 12),
        },
        "comparison": {
            "comp_mode_key": "opt_comp_buddy",
            "ref_callsign": "ON4AWM1",
            "reference_snr_correction_db": 1.2,
        },
        "advanced": {
            "exclude_special_callsigns": False,
            "exclude_moving_stations": False,
            "solar_key": "opt_solar_all",
            "max_dist": 22000,
            "min_joint_spots_per_station": 1,
            "min_joint_stations_per_segment": 1,
        },
        "results_view": {
            "show_non_joint": False,
            "station_evidence_time_bin_compare": "12h",
            "station_evidence_time_bin_absolute": "6h",
        },
    },


    "zander_tx_buddy": {
        "label": {
            "en": "TX Antenna Comparison. Buddy Test. (Dr. Jens Zander)",
            "de": "TX Antenna Comparison. Buddy Test. (Dr. Jens Zander)",
        },
        "description": {
            "en": "Publication: Zander - Simple HF antenna efficiency comparison using the WSPR system [Ref 7] - Figure 4",
            "de": "Publication: Zander - Simple HF antenna efficiency comparison using the WSPR system [Ref 7] - Figure 4",
        },
        "run": {
            "run_mode": "TX",
        },
        "core_parameters": {
            "callsign": "SK0WE/P",
            "qth": "JO97",
            "band": "20m",
            "time_mode_key": "opt_custom",
            "start_d": datetime.date(2022, 5, 21),
            "end_d": datetime.date(2022, 5, 21),
            "start_t": dt_time(9, 0),
            "end_t": dt_time(12, 0),
        },
        "comparison": {
            "comp_mode_key": "opt_comp_buddy",
            "ref_callsign": "SK0WE/1",
            "reference_snr_correction_db": 0.0,
        },
        "advanced": {
            "exclude_special_callsigns": False,
            "exclude_moving_stations": False,
            "solar_key": "opt_solar_all",
            "max_dist": 22000,
            "min_joint_spots_per_station": 1,
            "min_joint_stations_per_segment": 1,
        },
        "results_view": {
            "show_non_joint": False,
            "station_evidence_time_bin_compare": "15m",
            "station_evidence_time_bin_absolute": "15m",
        },
    },

    "milazzo_tx_buddy": {
        "label": {
            "en": "TX Antenna Comparison. Buddy Test. (Dr. Carol F. Milazzo)",
            "de": "TX Antenna Comparison. Buddy Test. (Dr. Carol F. Milazzo)",
        },
        "description": {
            "en": "Milazzo - Comparative Antenna Analysis with WSPR [Ref 8]. River City Amateur Radio Communication Society meeting Sacramento, California, March 1, 2011",
            "de": "Milazzo - Comparative Antenna Analysis with WSPR [Ref 8]. River City Amateur Radio Communication Society meeting Sacramento, California, March 1, 2011",
        },
        "run": {
            "run_mode": "TX",
        },
        "core_parameters": {
            "callsign": "KP4MD",
            "qth": "CM98",
            "band": "40m",
            "time_mode_key": "opt_custom",
            "start_d": datetime.date(2010, 12, 18),
            "end_d": datetime.date(2010, 12, 21),
            "start_t": dt_time(0, 0),
            "end_t": dt_time(0, 0),
        },
        "comparison": {
            "comp_mode_key": "opt_comp_buddy",
            "ref_callsign": "WB6RQN",
            "reference_snr_correction_db": 0.0,
        },
        "advanced": {
            "exclude_special_callsigns": False,
            "exclude_moving_stations": False,
            "solar_key": "opt_solar_all",
            "max_dist": 22000,
            "min_joint_spots_per_station": 1,
            "min_joint_stations_per_segment": 1,
        },
        "results_view": {
            "show_non_joint": False,
            "station_evidence_time_bin_compare": "3h",
            "station_evidence_time_bin_absolute": "3h",
        },
    },

    "rx_local_median_neighborhood": {
        "label": {
            "en": "RX Local Neighborhood Benchmark (Median)",
            "de": "RX Lokaler Nachbarschafts-Benchmark (Median)",
        },
        "description": {
            "en": "Runs an RX comparison against the local median neighborhood around DL1MKS on 20m.",
            "de": "Startet einen RX-Vergleich gegen die lokale Median-Nachbarschaft um DL1MKS auf 20m.",
        },
        "run": {
            "run_mode": "RX",
        },
        "core_parameters": {
            "callsign": "DL1MKS",
            "qth": "JN37",
            "band": "20m",
            "time_mode_key": "opt_custom",
            "start_d": datetime.date(2026, 4, 6),
            "end_d": datetime.date(2026, 4, 6),
            "start_t": dt_time(7, 0),
            "end_t": dt_time(23, 0),
        },
        "comparison": {
            "comp_mode_key": "opt_comp_radius",
            "local_benchmark_key": "opt_local_median",
            "ref_radius_km": 200,
            "reference_snr_correction_db": 0.0,
        },
        "advanced": {
            "exclude_special_callsigns": False,
            "exclude_moving_stations": False,
            "solar_key": "opt_solar_all",
            "max_dist": 22000,
            "min_joint_spots_per_station": 1,
            "min_joint_stations_per_segment": 1,
        },
        "results_view": {
            "show_non_joint": False,
            "station_evidence_time_bin_compare": "30m",
            "station_evidence_time_bin_absolute": "30m",
        },
    },
    

    "rx_calibration_ab": {
        "label": {
            "en": "RX Calibration A/B Test",
            "de": "RX-Kalibrierungs-A/B-Test",
        },
        "description": {
            "en": "Runs an RX hardware A/B calibration between DL1MKS and DL1MKS/P on 20m from May 27 through May 31, 2026.",
            "de": "Startet eine RX-Hardware-A/B-Kalibrierung zwischen DL1MKS und DL1MKS/P auf 20 m vom 27. bis 31. Mai 2026.",
        },
        "run": {
            "run_mode": "RX",
        },
        "core_parameters": {
            "callsign": "DL1MKS",
            "qth": "JN37",
            "band": "20m",
            "time_mode_key": "opt_custom",
            "last_hours": 24,
            "start_d": datetime.date(2026, 5, 27),
            "end_d": datetime.date(2026, 5, 31),
            "start_t": dt_time(13, 0),
            "end_t": dt_time(9, 45),
        },
        "comparison": {
            "comp_mode_key": "opt_comp_self",
            "local_benchmark_key": "opt_local_median",
            "ref_callsign": "DL2XYZ",
            "ref_radius_km": 100,
            "reference_snr_correction_db": 0.0,
            "self_test_mode_key": "opt_self_rx",
            "self_call_b": "DL1MKS/P",
            "target_wspr_frame_key": "opt_wspr_frame_00_04_08",
            "reference_wspr_frame_key": "opt_wspr_frame_02_06_10",
            "tx_ab_bin_minutes": 8,
        },
        "advanced": {
            "exclude_special_callsigns": False,
            "exclude_moving_stations": False,
            "solar_key": "opt_solar_all",
            "max_dist": 22000,
            "min_joint_spots_per_station": 1,
            "min_joint_stations_per_segment": 1,
        },
        "results_view": {
            "show_non_joint": False,
            "station_evidence_time_bin_compare": "3h",
            "station_evidence_time_bin_absolute": "3h",
        },
    },

    "rx_hardware_ab": {
        "label": {
            "en": "RX hardware A/B test",
            "de": "RX Hardware-A/B-Test",
        },
        "description": {
            "en": "Runs an RX A/B comparison between DL1MKS and DL1MKS/P on 20m.",
            "de": "Startet einen RX-A/B-Vergleich zwischen DL1MKS und DL1MKS/P auf 20m.",
        },
        "run": {
            "run_mode": "RX",
        },
        "core_parameters": {
            "callsign": "DL1MKS",
            "qth": "JN37",
            "band": "20m",
            "time_mode_key": "opt_custom",
            "start_d": datetime.date(2026, 4, 6),
            "end_d": datetime.date(2026, 4, 6),
            "start_t": dt_time(10, 0),
            "end_t": dt_time(23, 59),
        },
        "comparison": {
            "comp_mode_key": "opt_comp_self",
            "self_test_mode_key": "opt_self_rx",
            "self_call_b": "DL1MKS/P",
            "reference_snr_correction_db": 0.0,
        },
        "advanced": {
            "exclude_special_callsigns": False,
            "exclude_moving_stations": False,
            "solar_key": "opt_solar_all",
            "max_dist": 22000,
            "min_joint_spots_per_station": 1,
            "min_joint_stations_per_segment": 1,
        },
        "results_view": {
            "show_non_joint": False,
            "station_evidence_time_bin_compare": "30m",
            "station_evidence_time_bin_absolute": "30m",
        },
    },
    
    "tx_hardware_ab": {
        "label": {
            "en": "TX hardware A/B test",
            "de": "TX Hardware-A/B-Test",
        },
        "description": {
            "en": "Runs a sequential TX A/B comparison for DL1MKS on 20m using UTC WSPR frame starts 00/04/08 and 02/06/10.",
            "de": "Startet einen sequenziellen TX-A/B-Vergleich fuer DL1MKS auf 20m mit UTC-WSPR-Frame-Startminuten 00/04/08 und 02/06/10.",
        },
        "run": {
            "run_mode": "TX",
        },
        "core_parameters": {
            "callsign": "DL1MKS",
            "qth": "JN37",
            "band": "20m",
            "time_mode_key": "opt_custom",
            "start_d": datetime.date(2026, 3, 27),
            "end_d": datetime.date(2026, 3, 31),
            "start_t": dt_time(0, 0),
            "end_t": dt_time(0, 0),
        },
        "comparison": {
            "comp_mode_key": "opt_comp_self",
            "self_test_mode_key": "opt_self_tx",
            "target_wspr_frame_key": "opt_wspr_frame_00_04_08",
            "reference_wspr_frame_key": "opt_wspr_frame_02_06_10",
            "tx_ab_bin_minutes": 8,
            "reference_snr_correction_db": 0.0,
        },
        "advanced": {
            "exclude_special_callsigns": False,
            "exclude_moving_stations": False,
            "solar_key": "opt_solar_all",
            "max_dist": 22000,
            "min_joint_spots_per_station": 1,
            "min_joint_stations_per_segment": 1,
        },
        "results_view": {
            "show_non_joint": False,
            "station_evidence_time_bin_compare": "3h",
            "station_evidence_time_bin_absolute": "3h",
        },
    }
}

# ==========================================
# GEOSPATIAL CONSTANTS
# ==========================================
EARTH_RADIUS_KM = 6371.0
EARTH_RADIUS_M = 6371000.0
MAX_DYNAMIC_RADIUS_KM = 250  # Hard-Cap fuer die dynamische Referenz-Suche

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
ZOOMED_MAP_SCALE = 0.91

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
MAP_SCOPE_OPTIONS = [2500, 5000, 10000, 15000, 20000, 22000]
DIST_BINS = [0] + MAP_SCOPE_OPTIONS
THICK_RINGS = [5000, 10000, 15000, 20000]
THIN_RINGS = [2500, 22000]

# Scatter Plot Colors
COLOR_JOINT = "#00ff00"
COLOR_BOTH_ASYNC = "#ffbe33"
COLOR_ONLY_ME = "#cc00ff"
COLOR_ONLY_REF = "#ffffff"

# Frequenzbänder Mapping
BAND_MAP = {
    '160m':'1', '80m':'3', '60m':'5', '40m':'7', '30m':'10', 
    '20m':'14', '17m':'18', '15m':'21', '12m':'24', '10m':'28', 
    '6m':'50', '2m':'144', '70cm':'432', '23cm':'1296', 'All':''
}
