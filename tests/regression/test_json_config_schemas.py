"""Formal JSON Schema coverage for saved configs and built-in demo configs."""

from copy import deepcopy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker, ValidationError


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CONFIG_SCHEMA_PATH = REPOSITORY_ROOT / "config" / "wspradar-config.schema.json"
DEMO_CONFIGS_DIR = REPOSITORY_ROOT / "config" / "demos"


def _read_json(path):
    """Return one UTF-8 JSON document from ``path``."""
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def config_schema():
    """Return the checked Draft 2020-12 saved-config schema."""
    schema = _read_json(CONFIG_SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    return schema


@pytest.fixture(scope="module")
def config_validator(config_schema):
    """Return a saved-config validator with format checks enabled."""
    return Draft202012Validator(config_schema, format_checker=FormatChecker())


def _no_comparison_config():
    """Return a representative rolling-window config with no comparison."""
    return {
        "format": "wspradar.config",
        "schema_version": 1,
        "metadata": {
            "created_utc": "2026-07-14T20:15:00Z",
            "generator": {
                "application": "WSPRadar.org",
                "version": "1.0",
            },
        },
        "profile": {
            "id": "portable_test-8f3a21c0",
            "title": {
                "en": "Portable receiver test",
            },
            "description": {
                "en": "Saved setup and result-view state for a portable test.",
            },
        },
        "settings": {
            "core_parameters": {
                "analysis_direction": "rx",
                "callsign": "DL1MKS",
                "qth": "JN37",
                "band": "20m",
                "time_selection": {
                    "mode": "last_x",
                    "hours": 24,
                },
            },
            "comparison_parameters": {
                "mode": "none",
            },
            "advanced_parameters": {
                "solar_state": "all",
                "map_scope_km": 22000,
                "exclude_special_callsigns": False,
                "exclude_moving_stations": False,
                "min_confirmed_opportunities_per_peer": 5,
                "min_joint_stations_per_map_segment": 1,
            },
            "results_view": {
                "success": {
                    "selected_ranges": "all",
                    "selected_directions": "all",
                    "show_zero_target": False,
                    "station_evidence_time_bin": "3h",
                    "selected_stations": None,
                },
            },
        },
        "extensions": {
            "example.org/operator": {
                "note": "portable test",
            },
        },
    }


def _tx_hardware_ab_config():
    """Return a representative periodic-start TX hardware A/B config."""
    config = _no_comparison_config()
    settings = config["settings"]
    settings["core_parameters"]["analysis_direction"] = "tx"
    settings["core_parameters"]["time_selection"] = {
        "mode": "custom",
        "start_date": "2026-07-13",
        "end_date": "2026-07-14",
        "start_time_utc": "06:30",
        "end_time_utc": "23:45",
    }
    settings["comparison_parameters"] = {
        "mode": "hardware_ab",
        "repeat_interval_minutes": 10,
        "target_start_minute": 0,
        "reference_start_minute": 2,
        "snr_correction_db": 0.0,
    }
    settings["advanced_parameters"]["min_joint_spots_per_station"] = 1
    settings["results_view"] = {
        "success": {
            "selected_ranges": ["[0-2500km]"],
            "selected_directions": ["N", "NNE"],
            "show_zero_target": True,
            "station_evidence_time_bin": "3h",
            "selected_stations": [
                {
                    "callsign": "M7AEO",
                    "locator": "IO82",
                },
            ],
        },
        "compare": {
            "selected_ranges": ["[5000-10000km]"],
            "selected_directions": ["WNW", "NW"],
            "show_non_joint": False,
            "segment_evidence_time_bin": "auto",
            "station_evidence_time_bin": "3h",
            "station_evidence_temporal_view": "chronological",
            "selected_stations": [
                {
                    "callsign": "M7AEO",
                    "locator": "IO82",
                },
            ],
        },
    }
    return config


def test_formal_config_schema_identity_is_version_1(config_schema):
    """Keep the formal schema identity aligned with the current config version."""
    assert config_schema["$id"] == (
        "https://wspradar.org/schemas/v1/wspradar-config.schema.json"
    )
    assert config_schema["properties"]["schema_version"]["const"] == 1
    assert config_schema["properties"]["profile"]["$ref"] == "#/$defs/profile"
    assert list(config_schema["properties"]) == [
        "format",
        "schema_version",
        "metadata",
        "profile",
        "settings",
        "extensions",
    ]


def test_every_demo_is_an_ordinary_config_matching_the_formal_schema(
    config_validator,
):
    """Validate every demo directly against the sole saved-config schema."""
    demo_paths = sorted(
        DEMO_CONFIGS_DIR.glob("*.config"),
        key=lambda demo_path: demo_path.name,
    )

    assert demo_paths
    for demo_path in demo_paths:
        configuration = _read_json(demo_path)

        config_validator.validate(configuration)


@pytest.mark.parametrize(
    "configuration_factory",
    [
        _no_comparison_config,
        _tx_hardware_ab_config,
    ],
)
def test_representative_saved_configs_match_formal_schema(
    config_validator,
    configuration_factory,
):
    """Accept rolling/no-comparison and custom/TX-hardware saved documents."""
    config_validator.validate(configuration_factory())


def test_formal_schema_accepts_two_hour_station_evidence_bins(config_validator):
    """Keep the formal saved-config contract aligned with the multi-day UI."""
    config = _tx_hardware_ab_config()
    results_view = config["settings"]["results_view"]
    results_view["compare"]["station_evidence_time_bin"] = "2h"
    results_view["success"]["station_evidence_time_bin"] = "2h"

    config_validator.validate(config)


def test_formal_schema_accepts_null_all_and_explicit_empty_station_selections(
    config_validator,
):
    """Distinguish automatic, all-station, and explicit-empty intent."""
    config = _tx_hardware_ab_config()
    results_view = config["settings"]["results_view"]
    results_view["success"]["selected_stations"] = None
    results_view["compare"]["selected_stations"] = "all"

    config_validator.validate(config)

    results_view["compare"]["selected_stations"] = []
    config_validator.validate(config)


def test_profile_metadata_is_optional_for_an_ordinary_saved_config(config_validator):
    """Allow non-profile exports while demos and named saves carry a profile."""
    config = _no_comparison_config()
    config.pop("profile")

    config_validator.validate(config)


def test_profile_description_accepts_newlines_links_and_no_german_translation(
    config_validator,
):
    """Keep English-only rich demo metadata valid in the shared config schema."""
    config = _no_comparison_config()
    config["profile"]["title"] = {"en": "English-only title"}
    config["profile"]["description"] = {
        "en": "First line\n[Read the paper](https://example.org/paper)"
    }

    config_validator.validate(config)


def test_formal_schema_accepts_explicit_compare_temporal_choices(config_validator):
    """Accept durable segment bins and UTC-hour station evidence views."""
    config = _tx_hardware_ab_config()
    compare_view = config["settings"]["results_view"]["compare"]
    compare_view["segment_evidence_time_bin"] = "6h"
    compare_view["station_evidence_temporal_view"] = "utc_hour"

    config_validator.validate(config)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda config: config["settings"]["results_view"].pop("compare"),
        lambda config: config["settings"]["results_view"]["compare"].update(
            {"segment_evidence_time_bin": "4h"}
        ),
        lambda config: config["settings"]["results_view"]["compare"].update(
            {"station_evidence_temporal_view": "local_hour"}
        ),
        lambda config: config["settings"]["results_view"]["compare"].update(
            {"selected_ranges": []}
        ),
        lambda config: config["settings"]["results_view"]["compare"].update(
            {"selected_directions": ["LOCAL"]}
        ),
        lambda config: config["settings"]["results_view"]["success"].update(
            {"show_zero_target": "yes"}
        ),
        lambda config: config["settings"]["results_view"]["compare"].update(
            {"selected_stations": "visible"}
        ),
        lambda config: config["settings"]["results_view"]["compare"].update(
            {
                "selected_stations": [
                    {"callsign": "m7aeo", "locator": "IO82"},
                ]
            }
        ),
        lambda config: config["settings"]["results_view"]["compare"].update(
            {
                "selected_stations": [
                    {"callsign": "M7AEO", "locator": "IO82"},
                    {"callsign": "M7AEO", "locator": "IO82"},
                ]
            }
        ),
        lambda config: config["settings"]["results_view"].update(
            {"station_evidence_time_bin_compare": "3h"}
        ),
    ],
    ids=[
        "missing-compare-branch",
        "invalid-segment-bin",
        "invalid-temporal-view",
        "empty-segment-ranges",
        "invalid-segment-direction",
        "invalid-show-zero-target",
        "invalid-station-sentinel",
        "malformed-station-identity",
        "duplicate-station-identity",
        "legacy-flat-result-field",
    ],
)
def test_v1_nested_results_view_rejects_invalid_state(config_validator, mutate):
    """Reject incomplete, malformed, duplicate, or obsolete result-view state."""
    config = _tx_hardware_ab_config()
    mutate(config)

    with pytest.raises(ValidationError):
        config_validator.validate(config)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda config: config["profile"].update({"id": "Portable_Test"}),
        lambda config: config["profile"].update({"id": "portable-test-"}),
        lambda config: config["profile"].pop("title"),
        lambda config: config["profile"].update({"title": {}}),
        lambda config: config["profile"].update({"title": {"en": "   "}}),
        lambda config: config["profile"].update(
            {"title": {"english": "Portable receiver test"}}
        ),
        lambda config: config["profile"].update({"unknown": "not permitted"}),
    ],
    ids=[
        "uppercase-id",
        "trailing-separator-id",
        "missing-title",
        "empty-localized-title",
        "blank-localized-title",
        "invalid-language-tag",
        "unknown-profile-field",
    ],
)
def test_v1_profile_rejects_invalid_identity_or_localized_text(
    config_validator,
    mutate,
):
    """Keep profile IDs filename-safe and localized text non-empty."""
    config = _no_comparison_config()
    mutate(config)

    with pytest.raises(ValidationError):
        config_validator.validate(config)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda config: config["settings"]["core_parameters"]["time_selection"].update(
            {"start_date": "2026-07-14"}
        ),
        lambda config: config["settings"]["comparison_parameters"].update(
            {"reference_callsign": "SK0WE"}
        ),
        lambda config: config["settings"]["advanced_parameters"].update(
            {"min_joint_spots_per_station": 1}
        ),
        lambda config: config["settings"]["results_view"].update(
            {
                "compare": {
                    "selected_ranges": "all",
                    "selected_directions": "all",
                    "show_non_joint": False,
                    "segment_evidence_time_bin": "auto",
                    "station_evidence_time_bin": "3h",
                    "station_evidence_temporal_view": "chronological",
                    "selected_stations": None,
                }
            }
        ),
    ],
)
def test_inactive_fields_are_rejected(config_validator, mutate):
    """Forbid hidden time, comparison, advanced, and result-view values."""
    config = _no_comparison_config()
    mutate(config)
    with pytest.raises(ValidationError):
        config_validator.validate(config)


def test_hardware_ab_shape_must_match_analysis_direction(config_validator):
    """Reject TX schedule controls when the core direction is RX."""
    config = deepcopy(_tx_hardware_ab_config())
    config["settings"]["core_parameters"]["analysis_direction"] = "rx"
    with pytest.raises(ValidationError):
        config_validator.validate(config)


@pytest.mark.parametrize(
    "comparison_parameters",
    [
        {
            "mode": "hardware_ab",
            "repeat_interval_minutes": 8,
            "target_start_minute": 0,
            "reference_start_minute": 2,
            "snr_correction_db": 0.0,
        },
        {
            "mode": "hardware_ab",
            "repeat_interval_minutes": 10,
            "target_start_minute": 1,
            "reference_start_minute": 2,
            "snr_correction_db": 0.0,
        },
        {
            "mode": "hardware_ab",
            "repeat_interval_minutes": 10,
            "target_start_minute": 0,
            "reference_start_minute": 10,
            "snr_correction_db": 0.0,
        },
        {
            "mode": "hardware_ab",
            "repeat_interval_minutes": 10,
            "target_start_minute": 2,
            "reference_start_minute": 2,
            "snr_correction_db": 0.0,
        },
        {
            "mode": "hardware_ab",
            "pairing_model": "periodic_starts",
            "repeat_interval_minutes": 10,
            "target_start_minute": 0,
            "reference_start_minute": 2,
            "snr_correction_db": 0.0,
        },
        {
            "mode": "hardware_ab",
            "repeat_interval_minutes": 10,
            "target_start_minute": 0,
            "reference_start_minute": 2,
            "legacy_bin_minutes": 8,
            "snr_correction_db": 0.0,
        },
        {
            "mode": "hardware_ab",
            "target_wspr_frame": "frame_00_04_08",
            "reference_wspr_frame": "frame_02_06_10",
            "tx_ab_bin_minutes": 8,
            "snr_correction_db": 0.0,
        },
    ],
)
def test_tx_hardware_ab_schedule_contract_rejects_invalid_branches(
    config_validator,
    comparison_parameters,
):
    """Reject unsupported, overlapping, out-of-range, or mixed schedule fields."""
    config = _tx_hardware_ab_config()
    config["settings"]["comparison_parameters"] = comparison_parameters

    with pytest.raises(ValidationError):
        config_validator.validate(config)


@pytest.mark.parametrize(
    ("repeat_interval_minutes", "target_start_minute", "reference_start_minute"),
    [
        (4, 0, 2),
        (6, 4, 0),
        (10, 8, 0),
        (12, 10, 0),
        (20, 18, 0),
        (30, 28, 0),
        (60, 58, 0),
    ],
)
def test_periodic_tx_hardware_ab_accepts_every_supported_interval_and_phase_edge(
    config_validator,
    repeat_interval_minutes,
    target_start_minute,
    reference_start_minute,
):
    """Accept each supported repeat interval through its greatest valid phase."""
    config = _tx_hardware_ab_config()
    comparison = config["settings"]["comparison_parameters"]
    comparison["repeat_interval_minutes"] = repeat_interval_minutes
    comparison["target_start_minute"] = target_start_minute
    comparison["reference_start_minute"] = reference_start_minute

    config_validator.validate(config)
