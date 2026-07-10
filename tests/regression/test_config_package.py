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
    MAP_SCOPE_OPTIONS,
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


def test_demo_profile_dates_and_times_import_as_python_objects():
    for profile in DEMO_PROFILES.values():
        core_parameters = profile["core_parameters"]
        assert isinstance(core_parameters["start_d"], datetime.date)
        assert isinstance(core_parameters["end_d"], datetime.date)
        assert isinstance(core_parameters["start_t"], datetime.time)
        assert isinstance(core_parameters["end_t"], datetime.time)
