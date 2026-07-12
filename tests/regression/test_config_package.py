import datetime

from config import (
    ANALYSIS_ACTIVE_LEASE_TIMEOUT_SEC,
    ANALYSIS_MAX_CONCURRENT,
    ANALYSIS_MAX_QUEUED,
    ANALYSIS_QUEUE_POLL_INTERVAL_SEC,
    ANALYSIS_QUEUE_WAIT_TIMEOUT_SEC,
    APP_VERSION,
    BAND_MAP,
    DEFAULT_BAND,
    DEMO_PROFILES,
    EXPORT_ACTIVE_LEASE_TIMEOUT_SEC,
    EXPORT_MAX_CONCURRENT,
    EXPORT_MAX_QUEUED,
    EXPORT_QUEUE_POLL_INTERVAL_SEC,
    EXPORT_QUEUE_WAIT_TIMEOUT_SEC,
    MAP_SCOPE_OPTIONS,
    WSPR_CSV_MAX_RESPONSE_BYTES,
    WSPR_HTTP_CONNECT_TIMEOUT_SEC,
    WSPR_HTTP_READ_TIMEOUT_SEC,
    WSPR_PARQUET_MAX_RESPONSE_BYTES,
)


def test_config_package_exports_core_constants_and_demo_profiles():
    assert APP_VERSION.startswith("v")
    assert DEFAULT_BAND == "20m"
    assert BAND_MAP["20m"] == "14"
    assert "All" not in BAND_MAP
    assert MAP_SCOPE_OPTIONS[-1] == 22000
    assert "vanhamel_rx_calibration" in DEMO_PROFILES


def test_band_map_exposes_canonical_exact_wspr_bands_in_ui_order():
    expected_bands = {
        "LF": "-1",
        "MF": "0",
        "160m": "1",
        "80m": "3",
        "60m": "5",
        "40m": "7",
        "30m": "10",
        "22m": "13",
        "20m": "14",
        "17m": "18",
        "15m": "21",
        "12m": "24",
        "10m": "28",
        "8m": "40",
        "6m": "50",
        "4m": "70",
        "2m": "144",
        "70cm": "432",
        "23cm": "1296",
    }

    assert BAND_MAP == expected_bands
    assert list(BAND_MAP) == list(expected_bands)


def test_analysis_admission_settings_are_safe_and_exported():
    assert ANALYSIS_MAX_CONCURRENT >= 1
    assert ANALYSIS_MAX_QUEUED >= 0
    assert ANALYSIS_QUEUE_WAIT_TIMEOUT_SEC > 0
    assert ANALYSIS_ACTIVE_LEASE_TIMEOUT_SEC > ANALYSIS_QUEUE_POLL_INTERVAL_SEC > 0


def test_export_admission_settings_are_safe_and_exported():
    assert EXPORT_MAX_CONCURRENT == 1
    assert EXPORT_MAX_QUEUED == 10
    assert EXPORT_QUEUE_WAIT_TIMEOUT_SEC > 0
    assert EXPORT_ACTIVE_LEASE_TIMEOUT_SEC > EXPORT_QUEUE_POLL_INTERVAL_SEC > 0


def test_wspr_http_guardrails_are_safe_and_exported():
    assert 0 < WSPR_HTTP_CONNECT_TIMEOUT_SEC < WSPR_HTTP_READ_TIMEOUT_SEC
    assert WSPR_CSV_MAX_RESPONSE_BYTES >= 1024 * 1024
    assert WSPR_PARQUET_MAX_RESPONSE_BYTES >= 1024 * 1024


def test_demo_profile_dates_and_times_import_as_python_objects():
    for profile in DEMO_PROFILES.values():
        core_parameters = profile["core_parameters"]
        assert isinstance(core_parameters["start_d"], datetime.date)
        assert isinstance(core_parameters["end_d"], datetime.date)
        assert isinstance(core_parameters["start_t"], datetime.time)
        assert isinstance(core_parameters["end_t"], datetime.time)
