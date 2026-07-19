import json

import pytest

from config import (
    ANALYSIS_ACTIVE_LEASE_TIMEOUT_SEC,
    ANALYSIS_MAX_CONCURRENT,
    ANALYSIS_MAX_QUEUED,
    ANALYSIS_QUEUE_POLL_INTERVAL_SEC,
    ANALYSIS_QUEUE_WAIT_TIMEOUT_SEC,
    APP_VERSION,
    BAND_MAP,
    CONFIG_DOCUMENT_FORMAT,
    CONFIG_KEYS,
    CONFIG_SCHEMA_VERSION,
    DB_URL,
    DEFAULT_BAND,
    DEMO_QUERY_CACHE_TTL_SEC,
    DEMO_PROFILES,
    EXPORT_ACTIVE_LEASE_TIMEOUT_SEC,
    EXPORT_MAX_CONCURRENT,
    EXPORT_MAX_QUEUED,
    EXPORT_QUEUE_POLL_INTERVAL_SEC,
    EXPORT_QUEUE_WAIT_TIMEOUT_SEC,
    MAP_SCOPE_OPTIONS,
    SESSION_ARTIFACT_TTL_SEC,
    STANDARD_QUERY_CACHE_TTL_SEC,
    WSPR_CSV_MAX_RESPONSE_BYTES,
    WSPR_DATABASE_PROVIDERS,
    WSPR_HTTP_CONNECT_TIMEOUT_SEC,
    WSPR_HTTP_READ_TIMEOUT_SEC,
    WSPR_PARQUET_MAX_RESPONSE_BYTES,
    WSPR_PROVIDER_ACQUIRE_POLL_INTERVAL_SEC,
    WSPR_PROVIDER_ACQUIRE_TIMEOUT_SEC,
)
from config.demo_profiles import (
    DEMO_PROFILES_DIR,
    load_demo_profiles,
    prepare_demo_description_markdown,
    resolve_demo_profile_text,
)


EXPECTED_DEMO_FILENAMES = [
    "000_griffiths_squibb_fig3.config",
    "001_griffiths_squibb_fig6.config",
    "01_vanhamel_rx_calibration.config",
    "02_vanhamel_rx_buddy.config",
    "03_zander_tx_buddy.config",
    "04_zander_tx_buddy_experiment_b.config",
    "05_milazzo_tx_buddy.config",
    "06_rx_local_median_neighborhood.config",
    "07_rx_calibration_ab.config",
    "08_rx_hardware_ab.config",
    "09_tx_hardware_ab.config",
]
EXPECTED_DEMO_PROFILE_IDS = [
    "griffiths_squibb_fig3",
    "griffiths_squibb_fig6",
    "vanhamel_rx_calibration",
    "vanhamel_rx_buddy",
    "zander_tx_buddy",
    "zander_tx_buddy_experiment_b",
    "milazzo_tx_buddy",
    "rx_local_median_neighborhood",
    "rx_calibration_ab",
    "rx_hardware_ab",
    "tx_hardware_ab",
]


def _copy_demo_directory(destination):
    """Copy installed demo documents into an isolated test directory."""
    destination.mkdir()
    for source_path in DEMO_PROFILES_DIR.glob("*.config"):
        (destination / source_path.name).write_bytes(source_path.read_bytes())
    return destination


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


def test_cache_lifecycle_ttls_are_explicit_and_exported():
    """Keep ordinary artifacts at one hour and demo queries at one day."""
    assert STANDARD_QUERY_CACHE_TTL_SEC == 3600
    assert DEMO_QUERY_CACHE_TTL_SEC == 86400
    assert SESSION_ARTIFACT_TTL_SEC == 3600


def test_wspr_database_provider_priority_and_limits_are_explicit():
    """Keep the chosen primary/fallback order and local budgets auditable."""
    assert [provider.key for provider in WSPR_DATABASE_PROVIDERS] == [
        "wspr_live",
        "wd2",
        "wd1",
    ]
    assert [provider.display_name for provider in WSPR_DATABASE_PROVIDERS] == [
        "wspr.live",
        "WD2",
        "WD1",
    ]
    assert [provider.url for provider in WSPR_DATABASE_PROVIDERS] == [
        "https://db1.wspr.live/",
        "https://wd2.wsprdaemon.org/",
        "https://wd1.wsprdaemon.org/",
    ]
    assert all(provider.enabled for provider in WSPR_DATABASE_PROVIDERS)
    assert all(provider.request_limit == 20 for provider in WSPR_DATABASE_PROVIDERS)
    assert all(provider.request_window_seconds == 60.0 for provider in WSPR_DATABASE_PROVIDERS)
    assert all(
        provider.circuit_failure_threshold == 1
        for provider in WSPR_DATABASE_PROVIDERS
    )
    assert all(
        provider.rate_limit_cooldown_seconds == 60.0
        for provider in WSPR_DATABASE_PROVIDERS
    )
    assert all(
        provider.failure_cooldown_seconds == 30.0
        for provider in WSPR_DATABASE_PROVIDERS
    )
    assert WSPR_PROVIDER_ACQUIRE_TIMEOUT_SEC == 600
    assert WSPR_PROVIDER_ACQUIRE_POLL_INTERVAL_SEC == 0.5
    assert DB_URL == WSPR_DATABASE_PROVIDERS[0].url


def test_demo_configs_follow_filename_order_and_keep_canonical_settings():
    """Derive stable demo order from filenames and keep each config complete."""
    demo_paths = sorted(
        DEMO_PROFILES_DIR.glob("*.config"),
        key=lambda demo_path: demo_path.name,
    )

    assert [demo_path.name for demo_path in demo_paths] == EXPECTED_DEMO_FILENAMES
    assert list(DEMO_PROFILES) == EXPECTED_DEMO_PROFILE_IDS
    assert "Hervé" in DEMO_PROFILES["vanhamel_rx_calibration"]["label"]["en"]

    for expected_id, demo_path in zip(EXPECTED_DEMO_PROFILE_IDS, demo_paths):
        stored_configuration = json.loads(demo_path.read_text(encoding="utf-8"))
        profile = DEMO_PROFILES[expected_id]
        configuration = profile["configuration"]

        assert stored_configuration == configuration
        assert configuration["profile"]["id"] == expected_id
        assert profile["id"] == expected_id
        assert profile["label"] == configuration["profile"]["title"]
        assert profile["description"] == configuration["profile"]["description"]
        assert configuration["format"] == CONFIG_DOCUMENT_FORMAT
        assert configuration["schema_version"] == CONFIG_SCHEMA_VERSION
        assert set(configuration["settings"]) == CONFIG_KEYS


def test_demo_filenames_are_opaque_ordering_keys(tmp_path):
    """Accept arbitrary stems and order profiles only by complete filename."""
    demo_directory = tmp_path / "demos"
    demo_directory.mkdir()
    first_source = DEMO_PROFILES_DIR / "01_vanhamel_rx_calibration.config"
    second_source = DEMO_PROFILES_DIR / "02_vanhamel_rx_buddy.config"
    (demo_directory / "A first demo (chosen name).config").write_bytes(
        first_source.read_bytes()
    )
    (demo_directory / "z-last demo; also chosen.config").write_bytes(
        second_source.read_bytes()
    )

    loaded_profiles = load_demo_profiles(demo_directory)

    assert list(loaded_profiles) == [
        "vanhamel_rx_calibration",
        "vanhamel_rx_buddy",
    ]


def test_demo_english_metadata_supports_optional_german_and_markdown(tmp_path):
    """Use English in German mode and preserve config newlines and Markdown links."""
    demo_directory = _copy_demo_directory(tmp_path / "demos")
    demo_path = demo_directory / EXPECTED_DEMO_FILENAMES[0]
    payload = json.loads(demo_path.read_text(encoding="utf-8"))
    payload["profile"]["title"] = {"en": "English-only title"}
    payload["profile"]["description"] = {
        "en": "First line\n[Read the paper](https://example.org/paper)"
    }
    demo_path.write_text(
        json.dumps(payload, ensure_ascii=False),
        encoding="utf-8",
    )

    loaded_profile = load_demo_profiles(demo_directory)["griffiths_squibb_fig3"]
    profile_metadata = loaded_profile["configuration"]["profile"]
    resolved_title = resolve_demo_profile_text(
        profile_metadata,
        "title",
        "de",
    )
    resolved_description = resolve_demo_profile_text(
        profile_metadata,
        "description",
        "de",
    )

    assert resolved_title == "English-only title"
    assert resolved_description == (
        "First line\n[Read the paper](https://example.org/paper)"
    )
    assert prepare_demo_description_markdown(resolved_description) == (
        "First line  \n[Read the paper](https://example.org/paper)"
    )


@pytest.mark.parametrize("field", ["title", "description"])
def test_demo_directory_reader_requires_english_fallback_text(tmp_path, field):
    """Reject an installed demo that cannot fall back from missing German text."""
    demo_directory = _copy_demo_directory(tmp_path / "demos")
    demo_path = demo_directory / EXPECTED_DEMO_FILENAMES[0]
    payload = json.loads(demo_path.read_text(encoding="utf-8"))
    payload["profile"][field] = {"de": "Nur Deutsch"}
    demo_path.write_text(
        json.dumps(payload, ensure_ascii=False),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match=rf"profile\.{field}\.en"):
        load_demo_profiles(demo_directory)


def test_zander_experiment_b_demo_follows_experiment_a_with_expected_configuration():
    """Keep both Zander experiments adjacent and preserve Experiment B inputs."""
    profile_keys = list(DEMO_PROFILES)
    experiment_a_index = profile_keys.index("zander_tx_buddy")
    assert profile_keys[experiment_a_index + 1] == "zander_tx_buddy_experiment_b"
    assert "Experiment A" in DEMO_PROFILES["zander_tx_buddy"]["label"]["en"]

    experiment_b = DEMO_PROFILES["zander_tx_buddy_experiment_b"]
    assert "Experiment B" in experiment_b["label"]["en"]
    assert set(experiment_b) == {"id", "label", "description", "configuration"}
    settings = experiment_b["configuration"]["settings"]
    core_parameters = settings["core_parameters"]
    comparison_parameters = settings["comparison_parameters"]
    advanced_parameters = settings["advanced_parameters"]
    time_selection = core_parameters["time_selection"]

    assert core_parameters["analysis_direction"] == "tx"
    assert core_parameters["callsign"] == "SK0WE/B"
    assert core_parameters["qth"] == "JO89"
    assert core_parameters["band"] == "40m"
    assert time_selection == {
        "mode": "custom",
        "start_date": "2022-06-01",
        "end_date": "2022-06-10",
        "start_time_utc": "06:30",
        "end_time_utc": "23:45",
    }
    assert comparison_parameters == {
        "mode": "reference_station",
        "reference_callsign": "SK0WE",
        "snr_correction_db": 0.0,
    }
    assert advanced_parameters["map_scope_km"] == 2500
    assert advanced_parameters["min_confirmed_opportunities_per_peer"] == 1
    assert (
        DEMO_PROFILES["zander_tx_buddy"]["configuration"]["settings"]
        ["comparison_parameters"]["reference_callsign"]
        == "SK0WE/1"
    )


def test_tx_hardware_ab_demo_uses_scheduled_pair_science():
    """Keep the TX demo on the sole supported periodic schedule contract."""
    profile = DEMO_PROFILES["tx_hardware_ab"]
    assert "scheduled sequential" in profile["description"]["en"]
    assert "geplante sequenzielle" in profile["description"]["de"]
    assert profile["configuration"]["settings"]["comparison_parameters"] == {
        "mode": "hardware_ab",
        "repeat_interval_minutes": 4,
        "target_start_minute": 0,
        "reference_start_minute": 2,
        "snr_correction_db": 0.0,
    }


def test_demo_directory_reader_rejects_duplicate_profile_ids(tmp_path):
    """Prevent one config from silently replacing another profile."""
    demo_directory = _copy_demo_directory(tmp_path / "demos")
    first_profile_path = demo_directory / EXPECTED_DEMO_FILENAMES[0]
    duplicate_profile_path = demo_directory / "10_vanhamel_rx_calibration.config"
    duplicate_profile_path.write_bytes(first_profile_path.read_bytes())

    with pytest.raises(ValueError, match="Duplicate demo profile id"):
        load_demo_profiles(demo_directory)


def test_demo_directory_reader_rejects_unsupported_config_schema(tmp_path):
    """Fail explicitly when an installed demo requires a newer config reader."""
    demo_directory = _copy_demo_directory(tmp_path / "demos")
    demo_path = demo_directory / EXPECTED_DEMO_FILENAMES[0]
    payload = json.loads(demo_path.read_text(encoding="utf-8"))
    payload["schema_version"] += 1
    demo_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="newer than the supported version"):
        load_demo_profiles(demo_directory)


def test_demo_directory_reader_is_independent_from_working_directory(
    tmp_path,
    monkeypatch,
):
    """Resolve committed demo configs beside their loader, never from process CWD."""
    monkeypatch.chdir(tmp_path)

    assert list(load_demo_profiles()) == list(DEMO_PROFILES)
