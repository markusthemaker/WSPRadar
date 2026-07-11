import datetime

from config import (
    ANALYSIS_ACTIVE_LEASE_TIMEOUT_SEC,
    ANALYSIS_MAX_CONCURRENT,
    ANALYSIS_MAX_QUEUED,
    ANALYSIS_QUEUE_POLL_INTERVAL_SEC,
    ANALYSIS_QUEUE_WAIT_TIMEOUT_SEC,
    APP_VERSION,
    BAND_MAP,
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
    assert BAND_MAP["20m"] == "14"
    assert MAP_SCOPE_OPTIONS[-1] == 22000
    assert "vanhamel_rx_calibration" in DEMO_PROFILES


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
