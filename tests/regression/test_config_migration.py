"""Versioned JSON configuration document regression coverage."""

import json
from copy import deepcopy
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from config import (
    CONFIG_DOCUMENT_FORMAT,
    CONFIG_SCHEMA_VERSION,
    DEMO_PROFILES,
    prepare_config_document,
)
from i18n import T
from ui import config_io


def _valid_settings(
    *,
    analysis_direction="rx",
    comparison_mode="reference_station",
    time_mode="custom",
    tx_ab_method="simultaneous",
):
    """Return one valid grouped settings object for the requested active branches."""
    if time_mode == "last_x":
        time_selection = {"mode": "last_x", "hours": 24}
    else:
        time_selection = {
            "mode": "custom",
            "start_date": "2026-05-27",
            "end_date": "2026-05-28",
            "start_time_utc": "00:00",
            "end_time_utc": "00:00",
        }

    comparison_parameters = {"mode": comparison_mode}
    if comparison_mode != "none":
        comparison_parameters["snr_correction_db"] = 0.0
    if comparison_mode == "reference_station":
        comparison_parameters["reference_callsign"] = "DL2XYZ"
        comparison_parameters["reference_qth"] = "JO62"
    elif comparison_mode == "local_neighborhood":
        comparison_parameters.update(
            {
                "local_benchmark": "local_median",
                "neighborhood_radius_km": 100,
            }
        )
    elif comparison_mode == "hardware_ab" and analysis_direction == "rx":
        comparison_parameters.update(
            {
                "reference_callsign": "DL1MKS/P",
            }
        )
    elif comparison_mode == "hardware_ab":
        comparison_parameters["tx_ab_method"] = tx_ab_method
        if tx_ab_method == "simultaneous":
            comparison_parameters.update(
                {
                    "reference_callsign": "DL1MKS/P",
                }
            )
        else:
            comparison_parameters.update({
                "repeat_interval_minutes": 10,
                "target_start_minute": 0,
                "reference_start_minute": 2,
            })

    advanced_parameters = {
        "solar_state": "all",
        "map_scope_km": 22000,
        "exclude_special_callsigns": False,
        "exclude_moving_stations": False,
        "min_confirmed_opportunities_per_peer": 5,
        "min_joint_stations_per_map_segment": 1,
    }
    results_view = {
        "success": {
            "selected_ranges": "all",
            "selected_directions": "all",
            "show_zero_target": False,
            "station_evidence_time_bin": "3h",
            "selected_stations": None,
        }
    }
    if comparison_mode != "none":
        advanced_parameters["min_joint_spots_per_station"] = 1
        results_view["compare"] = {
                "selected_ranges": "all",
                "selected_directions": "all",
                "show_non_joint": False,
                "segment_evidence_time_bin": "auto",
                "station_evidence_time_bin": "3h",
                "station_evidence_temporal_view": "chronological",
                "selected_stations": None,
            }

    return {
        "core_parameters": {
            "analysis_direction": analysis_direction,
            "callsign": "DL1MKS",
            "qth": "JN37",
            "band": "20m",
            "time_selection": time_selection,
        },
        "comparison_parameters": comparison_parameters,
        "advanced_parameters": advanced_parameters,
        "results_view": results_view,
    }


def _config_document(settings=None, **overrides):
    """Build one current-schema document for focused reader tests."""
    document_settings = deepcopy(
        settings if settings is not None else _valid_settings()
    )
    document = {
        "format": CONFIG_DOCUMENT_FORMAT,
        "schema_version": CONFIG_SCHEMA_VERSION,
        "metadata": {},
        "settings": document_settings,
        "extensions": {},
    }
    document.update(overrides)
    return document


def test_current_config_document_validates_complete_settings():
    """Normalize every current field without relying on hidden file defaults."""
    config, warnings = config_io.validate_config_upload(
        json.dumps(_config_document()).encode("utf-8")
    )

    assert warnings == []
    assert config["callsign"] == "DL1MKS"
    assert config["qth"] == "JN37"
    assert config["start_date"].isoformat() == "2026-05-27"


def test_reference_station_accepts_an_explicit_different_reference_qth():
    """Keep Buddy comparisons geographically independent while matching QTH."""
    normalized = config_io.validate_config_document(_config_document())

    assert normalized["reference_callsign"] == "DL2XYZ"
    assert normalized["reference_qth"] == "JO62"


def test_hyphen_suffixes_normalize_across_config_callsign_inputs():
    """Normalize accepted Target, Reference, and selected-station suffixes."""
    settings = _valid_settings(comparison_mode="reference_station")
    settings["core_parameters"]["callsign"] = " dl1mks-1 "
    settings["comparison_parameters"]["reference_callsign"] = " dl2xyz-p "
    settings["results_view"]["success"]["selected_stations"] = [
        {"callsign": " k1abc-1 ", "locator": " fn31 "},
    ]

    normalized = config_io.validate_config_document(_config_document(settings))

    assert normalized["callsign"] == "DL1MKS-1"
    assert normalized["reference_callsign"] == "DL2XYZ-P"
    assert normalized["selected_stations_absolute"] == [
        {"callsign": "K1ABC-1", "locator": "FN31"},
    ]


def test_reference_station_requires_an_exact_grid4_reference_qth():
    """Keep the editable Buddy selector aligned with its grid-4 query scope."""
    settings = _valid_settings(comparison_mode="reference_station")
    settings["comparison_parameters"]["reference_qth"] = "JO62QM"

    with pytest.raises(ValueError, match="reference_qth.*4-character"):
        config_io.validate_config_document(_config_document(settings))


@pytest.mark.parametrize("analysis_direction", ["rx", "tx"])
def test_hardware_ab_rejects_a_serialized_reference_qth(analysis_direction):
    """Persist only the Target QTH from which Hardware grid-4 is derived."""
    settings = _valid_settings(
        analysis_direction=analysis_direction,
        comparison_mode="hardware_ab",
    )
    settings["comparison_parameters"]["reference_qth"] = "JO62"

    with pytest.raises(
        ValueError,
        match=r"Unknown settings\.comparison_parameters field.*reference_qth",
    ):
        config_io.validate_config_document(_config_document(settings))


@pytest.mark.parametrize(
    ("field_path", "invalid_value"),
    [
        (("core_parameters", "callsign"), True),
        (("core_parameters", "qth"), 1234),
        (("comparison_parameters", "reference_callsign"), False),
        (("comparison_parameters", "reference_qth"), ["JO62"]),
    ],
)
def test_identity_fields_reject_non_string_json_values(field_path, invalid_value):
    """Do not coerce JSON booleans, numbers, or arrays into identities."""
    settings = _valid_settings(comparison_mode="reference_station")
    section, field = field_path
    settings[section][field] = invalid_value

    with pytest.raises(ValueError, match=f"{field} must be a string"):
        config_io.validate_config_document(_config_document(settings))


@pytest.mark.parametrize(
    ("field_path", "unicode_value"),
    [
        (("core_parameters", "callsign"), "DL1\u00df"),
        (("core_parameters", "callsign"), "D\u01311ABC"),
        (("core_parameters", "qth"), "J\u013137"),
        (("comparison_parameters", "reference_callsign"), "DL2\ufb00"),
        (("comparison_parameters", "reference_qth"), "J\u212a37"),
    ],
)
def test_identity_validation_rejects_unicode_before_uppercase_expansion(
    field_path,
    unicode_value,
):
    """Reject confusables that Python uppercasing could turn into valid ASCII."""
    settings = _valid_settings(comparison_mode="reference_station")
    section, field = field_path
    settings[section][field] = unicode_value

    with pytest.raises(ValueError, match=f"{field} is not a valid"):
        config_io.validate_config_document(_config_document(settings))


def test_tx_hardware_v1_requires_explicit_method_without_legacy_fallback():
    """Keep the revised pre-production v1 contract strict and unambiguous."""
    settings = _valid_settings(
        analysis_direction="tx",
        comparison_mode="hardware_ab",
    )
    settings["comparison_parameters"].pop("tx_ab_method")

    with pytest.raises(ValueError, match="tx_ab_method"):
        config_io.validate_config_document(_config_document(settings))


def test_config_envelope_preparation_returns_an_independent_copy():
    """Prevent validation or later consumers from mutating the decoded input."""
    payload = _config_document()
    prepared = prepare_config_document(payload)

    prepared["settings"]["core_parameters"]["callsign"] = "F4WBN"

    assert payload["settings"]["core_parameters"]["callsign"] == "DL1MKS"


def test_two_hour_station_evidence_bins_round_trip_through_config_validation():
    """Keep the multi-day 2 h station-evidence choice saveable and reloadable."""
    settings = _valid_settings()
    settings["results_view"]["compare"]["station_evidence_time_bin"] = "2h"
    settings["results_view"]["success"]["station_evidence_time_bin"] = "2h"

    config, warnings = config_io.validate_config_upload(
        json.dumps(_config_document(settings)).encode("utf-8")
    )

    assert warnings == []
    assert config["station_evidence_time_bin_compare"] == "2h"
    assert config["station_evidence_time_bin_absolute"] == "2h"


def test_complete_result_view_state_round_trips_without_transient_row_ids():
    """Persist durable plot choices and ordered station identities per result."""
    settings = _valid_settings()
    settings["results_view"] = {
        "success": {
            "selected_ranges": ["[0-2500km]", "[2500-5000km]"],
            "selected_directions": ["N", "NNE"],
            "show_zero_target": True,
            "station_evidence_time_bin": "6h",
            "selected_stations": "all",
        },
        "compare": {
            "selected_ranges": ["[5000-10000km]"],
            "selected_directions": ["WNW", "NW"],
            "show_non_joint": True,
            "segment_evidence_time_bin": "12h",
            "station_evidence_time_bin": "2h",
            "station_evidence_temporal_view": "utc_hour",
            "selected_stations": [
                {"callsign": "F4WBN", "locator": "JN18"},
                {"callsign": "G0IDE", "locator": "IO83"},
            ],
        },
    }

    normalized = config_io.validate_config_document(_config_document(settings))

    assert normalized["selected_ranges_absolute"] == [
        "[0-2500km]",
        "[2500-5000km]",
    ]
    assert normalized["selected_directions_absolute"] == ["N", "NNE"]
    assert normalized["show_zero_target"] is True
    assert normalized["selected_stations_absolute"] == "all"
    assert normalized["selected_ranges_compare"] == ["[5000-10000km]"]
    assert normalized["selected_directions_compare"] == ["WNW", "NW"]
    assert normalized["segment_evidence_time_bin_compare"] == "12h"
    assert normalized["station_evidence_time_bin_compare"] == "2h"
    assert normalized["station_evidence_temporal_view_compare"] == "utc_hour"
    assert normalized["selected_stations_compare"] == [
        {"callsign": "F4WBN", "locator": "JN18"},
        {"callsign": "G0IDE", "locator": "IO83"},
    ]


def test_selected_station_validation_rejects_normalized_duplicate_identities():
    """Do not silently change authored station-selection order during loading."""
    settings = _valid_settings()
    settings["results_view"]["compare"]["selected_stations"] = [
        {"callsign": "f4wbn", "locator": "jn18"},
        {"callsign": "F4WBN", "locator": "JN18"},
    ]

    with pytest.raises(ValueError, match="duplicate station identity F4WBN/JN18"):
        config_io.validate_config_document(_config_document(settings))


def test_every_built_in_demo_uses_a_valid_current_config_document():
    """Validate the complete catalog through the same reader as uploaded files."""
    for profile in DEMO_PROFILES.values():
        normalized = config_io.validate_config_document(profile["configuration"])
        assert normalized["callsign"]


def test_future_config_schema_is_rejected_instead_of_guessed():
    """Require a newer application rather than silently defaulting new semantics."""
    payload = _config_document(schema_version=CONFIG_SCHEMA_VERSION + 1)

    with pytest.raises(ValueError, match="newer than the supported version"):
        config_io.validate_config_upload(json.dumps(payload).encode("utf-8"))


def test_current_schema_requires_all_settings_and_rejects_unknown_core_fields():
    """Keep scientific reproducibility explicit and route additions to extensions."""
    missing_settings = deepcopy(_valid_settings())
    del missing_settings["advanced_parameters"]["map_scope_km"]
    with pytest.raises(
        ValueError,
        match=r"Missing required settings\.advanced_parameters field.*map_scope_km",
    ):
        config_io.validate_config_document(_config_document(missing_settings))

    unknown_settings = deepcopy(_valid_settings())
    unknown_settings["core_parameters"]["future_setting"] = 17
    with pytest.raises(
        ValueError,
        match=r"Unknown settings\.core_parameters field.*future_setting",
    ):
        config_io.validate_config_document(_config_document(unknown_settings))


@pytest.mark.parametrize(
    ("prototype_field", "prototype_value"),
    [
        ("pairing_model", "periodic_starts"),
        ("legacy_bin_minutes", 8),
        ("target_wspr_frame", "frame_00_04_08"),
        ("reference_wspr_frame", "frame_02_06_10"),
        ("tx_ab_bin_minutes", 8),
    ],
)
def test_initial_tx_ab_contract_rejects_prototype_fields(
    prototype_field,
    prototype_value,
):
    """Keep unpublished pairing and fixed-bin fields out of public schema v1."""
    settings = _valid_settings(
        analysis_direction="tx",
        comparison_mode="hardware_ab",
        tx_ab_method="sequential",
    )
    settings["comparison_parameters"][prototype_field] = prototype_value

    with pytest.raises(
        ValueError,
        match=r"Unknown settings\.comparison_parameters field",
    ):
        config_io.validate_config_document(_config_document(settings))


@pytest.mark.parametrize("invalid_hours", ["24", 24.5, True])
def test_integer_settings_require_json_integers(invalid_hours):
    """Reject coercion or truncation that would hide a malformed config file."""
    settings = _valid_settings(time_mode="last_x")
    settings["core_parameters"]["time_selection"]["hours"] = invalid_hours

    with pytest.raises(ValueError, match="hours must be an integer"):
        config_io.validate_config_document(_config_document(settings))


def test_extensions_accept_non_core_future_metadata():
    """Allow namespaced additive data without weakening core settings validation."""
    payload = _config_document(
        extensions={"example.org/custom": {"operator_note": "portable test"}}
    )

    config = config_io.validate_config_document(payload)

    assert config["callsign"] == "DL1MKS"
    assert config["extensions"] == payload["extensions"]


def test_provenance_metadata_rejects_unknown_or_malformed_fields():
    """Keep writer provenance strict and route third-party data to extensions."""
    with pytest.raises(ValueError, match="Unknown metadata field.*operator_note"):
        config_io.validate_config_document(
            _config_document(metadata={"operator_note": "portable"})
        )

    with pytest.raises(ValueError, match="metadata.generator.version"):
        config_io.validate_config_document(
            _config_document(
                metadata={
                    "generator": {
                        "application": "WSPRadar.org",
                        "version": "",
                    }
                }
            )
        )


@pytest.mark.parametrize("invalid_json", [b'{"a": 1, "a": 2}', b'{"value": NaN}'])
def test_config_reader_rejects_non_standard_or_ambiguous_json(invalid_json):
    """Reject duplicate keys and non-finite numbers before semantic validation."""
    with pytest.raises(ValueError, match="duplicate JSON key|non-finite JSON number"):
        config_io.validate_config_upload(invalid_json)


def test_config_writer_round_trips_through_current_reader(monkeypatch):
    """Ensure every newly written document is immediately readable as version 1."""
    monkeypatch.setattr(
        config_io,
        "st",
        SimpleNamespace(
            session_state={"lang": "en", "val_analysis_direction": "rx"}
        ),
    )

    payload_bytes, filename = config_io.build_config_payload(title="Portable RX")
    config, warnings = config_io.validate_config_upload(payload_bytes)
    payload = json.loads(payload_bytes)

    assert warnings == []
    assert payload["schema_version"] == 1
    assert config["analysis_direction"] == "rx"
    assert config["band"] == "20m"
    assert payload["settings"]["core_parameters"]["time_selection"] == {
        "mode": "last_x",
        "hours": 24,
    }
    assert payload["settings"]["comparison_parameters"] == {"mode": "none"}
    assert "min_joint_spots_per_station" not in payload["settings"][
        "advanced_parameters"
    ]
    assert payload["settings"]["results_view"] == {
        "success": {
            "selected_ranges": "all",
            "selected_directions": "all",
            "show_zero_target": False,
            "station_evidence_time_bin": "3h",
            "selected_stations": None,
        }
    }
    assert list(payload) == [
        "format",
        "schema_version",
        "metadata",
        "profile",
        "settings",
        "extensions",
    ]
    assert payload["profile"]["title"] == {"en": "Portable RX"}
    assert filename == f"{payload['profile']['id']}.config"


def test_config_writer_preserves_other_localizations_and_extensions():
    """Re-saving edits only the current language and retains namespaced data."""
    session_state = {
        "lang": "de",
        "val_analysis_direction": "rx",
        "val_config_profile": {
            "id": "portable-rx",
            "title": {"en": "Portable RX", "de": "Alter Titel"},
            "description": {
                "en": "English description",
                "de": "Alte Beschreibung",
            },
        },
        "val_config_extensions": {
            "example.org/operator": {"note": "keep exactly"}
        },
    }

    payload_bytes, filename = config_io.build_config_payload(
        title="Neuer Titel",
        description="",
        profile_id=None,
        language="de",
        state=session_state,
        exported_utc=datetime(2026, 7, 17, 12, 30, tzinfo=timezone.utc),
    )
    payload = json.loads(payload_bytes)

    assert filename == "portable-rx.config"
    assert payload["profile"] == {
        "id": "portable-rx",
        "title": {"en": "Portable RX", "de": "Neuer Titel"},
        "description": {"en": "English description"},
    }
    assert payload["extensions"] == session_state["val_config_extensions"]
    assert payload["metadata"]["created_utc"] == "2026-07-17T12:30:00Z"


def test_resaving_an_unchanged_language_fallback_does_not_mislabel_it():
    """Do not copy untranslated fallback text into the active language slot."""
    session_state = {
        "lang": "en",
        "val_analysis_direction": "rx",
        "val_config_profile": {
            "id": "german-only",
            "title": {"de": "Deutsches Profil"},
            "description": {"de": "Deutsche Beschreibung"},
        },
    }

    payload_bytes, _ = config_io.build_config_payload(
        title="Deutsches Profil",
        description="Deutsche Beschreibung",
        profile_id="german-only",
        language="en",
        state=session_state,
    )

    assert json.loads(payload_bytes)["profile"] == session_state[
        "val_config_profile"
    ]


def test_noninteractive_export_writer_allows_a_profileless_config():
    """Embed runnable config in result exports without inventing user metadata."""
    session_state = {"lang": "en", "val_analysis_direction": "rx"}

    payload_bytes, filename = config_io.build_config_payload(
        state=session_state,
        exported_utc=datetime(2026, 7, 17, 12, 30, tzinfo=timezone.utc),
    )
    payload = json.loads(payload_bytes)

    assert "profile" not in payload
    assert list(payload) == [
        "format",
        "schema_version",
        "metadata",
        "settings",
        "extensions",
    ]
    assert filename == "WSPRadar_config_2026-07-17T1230Z.config"
    assert config_io.validate_config_upload(payload_bytes)[0][
        "analysis_direction"
    ] == "rx"


def test_last_x_writer_can_freeze_the_resolved_utc_analysis_window():
    """Offer exact replay without changing the normal relative Last-X option."""
    session_state = {
        "lang": "en",
        "val_analysis_direction": "tx",
        "val_time_mode": "Last X Hours",
        "val_hours": 24,
    }
    frozen_window = (
        datetime(2026, 7, 16, 10, 15, tzinfo=timezone.utc),
        datetime(2026, 7, 17, 10, 15, tzinfo=timezone.utc),
    )

    frozen_bytes, _ = config_io.build_config_payload(
        title="Frozen TX",
        frozen_time_window=frozen_window,
        state=session_state,
    )
    relative_bytes, _ = config_io.build_config_payload(
        title="Relative TX",
        state=session_state,
    )

    assert json.loads(frozen_bytes)["settings"]["core_parameters"][
        "time_selection"
    ] == {
        "mode": "custom",
        "start_date": "2026-07-16",
        "end_date": "2026-07-17",
        "start_time_utc": "10:15",
        "end_time_utc": "10:15",
    }
    assert json.loads(relative_bytes)["settings"]["core_parameters"][
        "time_selection"
    ] == {"mode": "last_x", "hours": 24}


def test_loading_active_only_config_resets_inactive_widget_state():
    """Prevent hidden values from the preceding session leaking into later modes."""
    normalized = config_io.validate_config_document(
        _config_document(
            _valid_settings(comparison_mode="none", time_mode="last_x")
        )
    )
    session_state = SimpleNamespace(
        lang="en",
        val_start_d="stale-date",
        val_end_d="stale-date",
        val_start_t="stale-time",
        val_end_t="stale-time",
        val_ref_callsign="STALE",
        val_ref_qth="AA00",
        val_ref_radius_km=250,
        val_tx_ab_method="sequential",
        val_min_spots=50,
        val_results_show_non_joint=True,
        val_results_show_zero_target=True,
        val_results_selected_ranges_compare=["[5000-10000km]"],
        val_results_selected_directions_compare=["NW"],
        val_results_selected_ranges_absolute=["[0-2500km]"],
        val_results_selected_directions_absolute=["N"],
        val_results_time_bin_compare="24h",
    )

    config_io.apply_config_state_values(normalized, session_state)

    assert session_state.val_ref_callsign == ""
    assert session_state.val_ref_qth == ""
    assert session_state.val_ref_radius_km == 100
    assert session_state.val_tx_ab_method == "simultaneous"
    assert session_state.val_min_spots == 1
    assert session_state.val_results_show_non_joint is None
    assert session_state.val_results_show_zero_target is False
    assert session_state.val_results_selected_ranges_compare == "all"
    assert session_state.val_results_selected_directions_compare == "all"
    assert session_state.val_results_selected_ranges_absolute == "all"
    assert session_state.val_results_selected_directions_absolute == "all"
    assert session_state.val_results_time_bin_compare is None
    assert session_state.val_results_segment_time_bin_compare == "auto"
    assert (
        session_state.val_results_station_temporal_view_compare
        == "chronological"
    )
    assert session_state.val_results_selected_stations_compare is None
    assert session_state.val_results_selected_stations_absolute is None


@pytest.mark.parametrize(
    (
        "analysis_direction",
        "comparison_mode",
        "tx_ab_method",
        "expected_comparison_fields",
    ),
    [
        ("rx", "none", "simultaneous", {"mode"}),
        (
            "rx",
            "reference_station",
            "simultaneous",
            {
                "mode",
                "reference_callsign",
                "reference_qth",
                "snr_correction_db",
            },
        ),
        (
            "rx",
            "local_neighborhood",
            "simultaneous",
            {
                "mode",
                "local_benchmark",
                "neighborhood_radius_km",
                "snr_correction_db",
            },
        ),
        (
            "rx",
            "hardware_ab",
            "simultaneous",
            {
                "mode",
                "reference_callsign",
                "snr_correction_db",
            },
        ),
        (
            "tx",
            "hardware_ab",
            "simultaneous",
            {
                "mode",
                "tx_ab_method",
                "reference_callsign",
                "snr_correction_db",
            },
        ),
        (
            "tx",
            "hardware_ab",
            "sequential",
            {
                "mode",
                "tx_ab_method",
                "repeat_interval_minutes",
                "target_start_minute",
                "reference_start_minute",
                "snr_correction_db",
            },
        ),
    ],
)
def test_comparison_modes_use_only_their_active_fields(
    analysis_direction,
    comparison_mode,
    tx_ab_method,
    expected_comparison_fields,
):
    """Keep each mode self-contained without persisting hidden mode state."""
    settings = _valid_settings(
        analysis_direction=analysis_direction,
        comparison_mode=comparison_mode,
        tx_ab_method=tx_ab_method,
    )

    normalized = config_io.validate_config_document(_config_document(settings))

    assert set(settings["comparison_parameters"]) == expected_comparison_fields
    assert normalized["benchmark_mode"] == comparison_mode
    if comparison_mode == "none":
        assert "min_joint_spots_per_station" not in settings["advanced_parameters"]
        assert set(settings["results_view"]) == {"success"}


@pytest.mark.parametrize(
    ("tx_ab_method", "expected_fields"),
    [
        (
            "simultaneous",
            {
                "mode",
                "tx_ab_method",
                "reference_callsign",
                "snr_correction_db",
            },
        ),
        (
            "sequential",
            {
                "mode",
                "tx_ab_method",
                "repeat_interval_minutes",
                "target_start_minute",
                "reference_start_minute",
                "snr_correction_db",
            },
        ),
    ],
)
def test_tx_hardware_writer_omits_inactive_method_fields(
    tx_ab_method,
    expected_fields,
):
    """Do not let hidden identity or schedule state affect saved TX A/B work."""
    state = {
        "val_analysis_direction": "tx",
        "val_comp_mode": T["en"]["opt_comp_self"],
        "val_callsign": "DL1MKS",
        "val_qth": "JN37",
        "val_ref_callsign": "DL1MKS/P",
        "val_ref_qth": "JO62",
        "val_tx_ab_method": tx_ab_method,
        "val_tx_ab_repeat_interval_minutes": 10,
        "val_tx_ab_target_start_minute": 0,
        "val_tx_ab_reference_start_minute": 2,
    }

    settings = config_io._settings_from_session_state(state, "en")

    assert set(settings["comparison_parameters"]) == expected_fields
    assert "reference_qth" not in settings["comparison_parameters"]
    config_io.normalize_config_settings(settings)


def test_time_modes_reject_fields_from_the_inactive_branch():
    """Serialize either relative hours or an absolute UTC range, never both."""
    settings = _valid_settings(time_mode="last_x")
    settings["core_parameters"]["time_selection"]["start_date"] = "2026-05-27"

    with pytest.raises(ValueError, match=r"Unknown .*time_selection field.*start_date"):
        config_io.validate_config_document(_config_document(settings))


def test_success_only_rejects_hidden_comparison_view_fields():
    """Reject comparison-only thresholds and view controls in Success-only mode."""
    settings = _valid_settings(comparison_mode="none")
    settings["advanced_parameters"]["min_joint_spots_per_station"] = 1

    with pytest.raises(
        ValueError,
        match=r"Unknown settings\.advanced_parameters field.*min_joint_spots_per_station",
    ):
        config_io.validate_config_document(_config_document(settings))

    settings = _valid_settings(comparison_mode="none")
    settings["results_view"]["compare"] = {
        "selected_ranges": "all",
        "selected_directions": "all",
        "show_non_joint": False,
        "segment_evidence_time_bin": "auto",
        "station_evidence_time_bin": "3h",
        "station_evidence_temporal_view": "chronological",
        "selected_stations": None,
    }
    with pytest.raises(
        ValueError,
        match=r"Unknown settings\.results_view field.*compare",
    ):
        config_io.validate_config_document(_config_document(settings))
