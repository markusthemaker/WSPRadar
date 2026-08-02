"""Focused regression coverage for the human-readable public URL-v1 adapter."""

from copy import deepcopy
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

import pytest

from config import SEGMENT_DIRECTION_OPTIONS, SEGMENT_RANGE_OPTIONS
from ui import config_io, url_state
from ui.analysis_submission_state import claim_analysis_submission_request


class _SessionState(dict):
    """Provide Streamlit-style attribute access over a test dictionary."""

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as error:
            raise AttributeError(key) from error

    def __setattr__(self, key, value):
        self[key] = value


def _default_success_results():
    """Return the stable Performance result-view defaults."""
    return {
        "selected_ranges": "all",
        "selected_directions": "all",
        "show_zero_target": False,
        "segment_evidence_time_bin": "auto",
        "station_evidence_time_bin": "3h",
        "selected_stations": None,
    }


def _default_compare_results():
    """Return the stable Compare result-view defaults."""
    return {
        "selected_ranges": "all",
        "selected_directions": "all",
        "show_non_joint": False,
        "segment_evidence_time_bin": "auto",
        "station_evidence_time_bin": "3h",
        "selected_stations": None,
    }


def _settings_for_mode(
    case,
    *,
    target_callsign="DL1MKS",
    target_qth="JN37",
):
    """Return complete canonical settings for one public URL-v1 analysis case."""
    case_contracts = {
        "performance": {
            "direction": "rx",
            "comparison": {"mode": "none"},
        },
        "hardware_rx": {
            "direction": "rx",
            "comparison": {
                "mode": "hardware_ab",
                "reference_callsign": "DL1MKS/P",
                "snr_correction_mode": "no_offset",
                "snr_correction_db": 0.0,
            },
        },
        "hardware_tx_simultaneous": {
            "direction": "tx",
            "comparison": {
                "mode": "hardware_ab",
                "tx_ab_method": "simultaneous",
                "reference_callsign": "DL1MKS/P",
                "snr_correction_mode": "establish_offset",
                "snr_correction_db": 0.0,
            },
        },
        "hardware_tx_sequential": {
            "direction": "tx",
            "comparison": {
                "mode": "hardware_ab",
                "tx_ab_method": "sequential",
                "repeat_interval_minutes": 10,
                "target_start_minute": 0,
                "reference_start_minute": 2,
                "snr_correction_mode": "no_offset",
                "snr_correction_db": 0.0,
            },
        },
        "reference_station": {
            "direction": "rx",
            "comparison": {
                "mode": "reference_station",
                "reference_callsign": "DL2XYZ",
                "reference_qth": "JO62",
                "snr_correction_mode": "established_offset",
                "snr_correction_db": -1.5,
            },
        },
        "local_neighborhood": {
            "direction": "tx",
            "comparison": {
                "mode": "local_neighborhood",
                "local_benchmark": "local_best",
                "neighborhood_radius_km": 100,
                "snr_correction_mode": "established_offset",
                "snr_correction_db": 2.5,
            },
        },
    }
    contract = case_contracts[case]
    comparison = deepcopy(contract["comparison"])
    advanced = {
        "solar_state": "all",
        "max_peer_distance_km": 22000,
        "exclude_special_callsigns": False,
        "exclude_moving_stations": False,
        "min_confirmed_opportunities_per_peer": 5,
        "min_joint_stations_per_map_segment": 1,
    }
    results_view = {"success": _default_success_results()}
    if comparison["mode"] != "none":
        advanced["min_joint_spots_per_station"] = 1
        results_view["compare"] = _default_compare_results()
    return {
        "core_parameters": {
            "analysis_direction": contract["direction"],
            "callsign": target_callsign,
            "qth": target_qth,
            "band": "20m",
            "time_selection": {
                "start_utc": "2026-07-20T00:00Z",
                "end_utc": "2026-07-21T00:00Z",
            },
        },
        "comparison_parameters": comparison,
        "advanced_parameters": advanced,
        "results_view": results_view,
    }


@pytest.mark.parametrize(
    ("case", "expected_public_mode", "expected_internal_mode", "expected_direction"),
    [
        ("performance", "performance", "none", "rx"),
        ("hardware_rx", "hardware_ab", "hardware_ab", "rx"),
        (
            "hardware_tx_simultaneous",
            "hardware_ab",
            "hardware_ab",
            "tx",
        ),
        ("hardware_tx_sequential", "hardware_ab", "hardware_ab", "tx"),
        (
            "reference_station",
            "reference_station",
            "reference_station",
            "rx",
        ),
        (
            "local_neighborhood",
            "local_neighborhood",
            "local_neighborhood",
            "tx",
        ),
    ],
)
def test_each_analysis_case_round_trips_through_url_v1(
    case,
    expected_public_mode,
    expected_internal_mode,
    expected_direction,
):
    """Round-trip all six supported direction/design contracts canonically."""
    settings = _settings_for_mode(case)

    entries = url_state.build_query_from_settings(settings, include_run=True)
    query = url_state.build_query_string(entries)
    parsed_parameters = url_state.parse_url_query(dict(entries))
    normalized = url_state.build_config_from_url(parsed_parameters)

    assert dict(entries)["mode"] == expected_public_mode
    assert normalized["benchmark_mode"] == expected_internal_mode
    assert normalized["analysis_direction"] == expected_direction
    assert normalized["start_utc"].isoformat() == "2026-07-20T00:00:00+00:00"
    assert normalized["end_utc"].isoformat() == "2026-07-21T00:00:00+00:00"
    assert url_state.canonicalize_query(dict(entries)) == query

    session_state = _SessionState()
    config_io.apply_config_state_values(normalized, session_state)
    rebuilt_entries = url_state.build_query_from_state(
        session_state,
        include_run=True,
    )
    assert rebuilt_entries == entries


def test_url_v1_omits_every_stable_default_and_orders_required_fields():
    """Keep omitted-value semantics stable and output order deterministic."""
    entries = url_state.build_query_from_settings(
        _settings_for_mode("performance"),
        include_run=False,
    )

    assert entries == (
        ("v", "1"),
        ("direction", "rx"),
        ("callsign", "DL1MKS"),
        ("qth", "JN37"),
        ("band", "20m"),
        ("from", "2026-07-20T00:00Z"),
        ("to", "2026-07-21T00:00Z"),
        ("mode", "performance"),
    )
    assert tuple(key for key, _value in entries) == tuple(
        sorted(
            (key for key, _value in entries),
            key=url_state.URL_V1_PARAMETER_ORDER.index,
        )
    )


def test_performance_ui_defaults_are_explicit_against_url_v1_false_defaults():
    """Preserve old omitted URLs while encoding the new interactive defaults."""
    settings = _settings_for_mode("performance")
    settings["advanced_parameters"].update(
        {
            "exclude_special_callsigns": True,
            "exclude_moving_stations": True,
        }
    )

    entries = url_state.build_query_from_settings(settings, include_run=False)
    entry_map = dict(entries)
    normalized = url_state.build_config_from_url(
        url_state.parse_url_query(entry_map)
    )

    assert entry_map["exclude_special"] == "1"
    assert entry_map["exclude_moving"] == "1"
    assert normalized["exclude_special_callsigns"] is True
    assert normalized["exclude_moving_stations"] is True


def test_nondefault_fields_use_global_deterministic_parameter_order():
    """Place advanced and result values in the public contract's fixed order."""
    settings = _settings_for_mode("reference_station")
    settings["advanced_parameters"].update(
        {
            "solar_state": "night",
            "max_peer_distance_km": 20000,
            "exclude_special_callsigns": True,
            "exclude_moving_stations": True,
            "min_joint_spots_per_station": 4,
            "min_confirmed_opportunities_per_peer": 8,
            "min_joint_stations_per_map_segment": 3,
        }
    )
    settings["results_view"]["compare"].update(
        {
            "selected_ranges": [
                SEGMENT_RANGE_OPTIONS[2],
                SEGMENT_RANGE_OPTIONS[0],
            ],
            "selected_directions": ["NW", "N", "NNW"],
            "segment_evidence_time_bin": "1h",
            "station_evidence_time_bin": "2h",
            "selected_stations": [{"callsign": "K1ABC", "locator": "FN42"}],
            "show_non_joint": True,
        }
    )

    entries = url_state.build_query_from_settings(settings, include_run=True)
    entry_map = dict(entries)

    assert tuple(key for key, _value in entries) == tuple(
        key for key in url_state.URL_V1_PARAMETER_ORDER if key in entry_map
    )
    assert entry_map["ranges"] == "0-2500,5000-10000"
    assert entry_map["directions"] == "N,NW,NNW"
    assert entry_map["snr_correction_db"] == "-1.5"
    assert entry_map["max_distance_km"] == "20000"
    assert entry_map["selected_station"] == "K1ABC@FN42"
    assert entry_map["show_unpaired"] == "1"


def test_standard_encoding_escapes_slash_at_comma_and_timestamps():
    """Use the standard query encoder for every identity and list separator."""
    settings = _settings_for_mode(
        "hardware_rx",
        target_callsign="dl1mks",
        target_qth="jn37",
    )
    settings["comparison_parameters"]["reference_callsign"] = "dl1mks/p"
    settings["results_view"]["compare"].update(
        {
            "selected_ranges": [
                SEGMENT_RANGE_OPTIONS[1],
                SEGMENT_RANGE_OPTIONS[2],
            ],
            "selected_directions": ["NW", "N"],
            "selected_stations": [
                {"callsign": "k1abc/p", "locator": "fn42aa"},
            ],
        }
    )

    entries = url_state.build_query_from_settings(settings, include_run=True)
    query = url_state.build_query_string(entries)

    assert "callsign=DL1MKS" in query
    assert "reference=DL1MKS%2FP" in query
    assert "selected_station=K1ABC%2FP%40FN42AA" in query
    assert "ranges=2500-5000%2C5000-10000" in query
    assert "directions=N%2CNW" in query
    assert "from=2026-07-20T00%3A00Z" in query
    assert "/" not in query
    assert "@" not in query
    assert dict(parse_qsl(query))["selected_station"] == "K1ABC/P@FN42AA"


def test_explicit_station_deselection_round_trips_as_none():
    """Distinguish explicit deselection from omitted automatic selection."""
    settings = _settings_for_mode("hardware_rx")
    settings["results_view"]["compare"]["selected_stations"] = []

    entries = url_state.build_query_from_settings(settings, include_run=False)
    normalized = url_state.build_config_from_url(
        url_state.parse_url_query(dict(entries))
    )

    assert dict(entries)["selected_station"] == "none"
    assert normalized["selected_stations_compare"] == []


def test_omitted_station_retains_automatic_selection_intent():
    """Keep an omitted station distinct from the explicit ``none`` token."""
    settings = _settings_for_mode("hardware_rx")

    entries = url_state.build_query_from_settings(settings, include_run=False)
    normalized = url_state.build_config_from_url(
        url_state.parse_url_query(dict(entries))
    )

    assert "selected_station" not in dict(entries)
    assert normalized["selected_stations_compare"] is None


def test_performance_url_maps_only_the_active_result_branch():
    """Serialize the active Performance controls using unprefixed URL names."""
    settings = _settings_for_mode("performance")
    settings["results_view"]["success"].update(
        {
            "selected_ranges": [
                SEGMENT_RANGE_OPTIONS[3],
                SEGMENT_RANGE_OPTIONS[1],
            ],
            "selected_directions": ["SSW", "E"],
            "segment_evidence_time_bin": "2h",
            "station_evidence_time_bin": "2h",
            "selected_stations": [{"callsign": "K1ABC", "locator": "FN42"}],
            "show_zero_target": True,
        }
    )

    entries = url_state.build_query_from_settings(settings, include_run=False)
    entry_map = dict(entries)
    normalized = url_state.build_config_from_url(
        url_state.parse_url_query(entry_map)
    )

    assert entry_map["ranges"] == "2500-5000,10000-15000"
    assert entry_map["directions"] == "E,SSW"
    assert entry_map["segment_bin"] == "2h"
    assert entry_map["station_bin"] == "2h"
    assert entry_map["selected_station"] == "K1ABC@FN42"
    assert entry_map["show_zero"] == "1"
    assert "show_unpaired" not in entry_map
    assert "temporal_view" not in entry_map
    assert normalized["show_zero_target"] is True
    assert normalized["selected_stations_absolute"] == [
        {"callsign": "K1ABC", "locator": "FN42"},
    ]


def test_compare_url_maps_only_the_active_result_branch():
    """Ignore inactive Performance choices and round-trip Compare controls."""
    settings = _settings_for_mode("hardware_rx")
    settings["results_view"]["success"].update(
        {
            "selected_ranges": [SEGMENT_RANGE_OPTIONS[5]],
            "selected_directions": ["S"],
            "station_evidence_time_bin": "24h",
            "selected_stations": [{"callsign": "W1AAA", "locator": "FN31"}],
            "show_zero_target": True,
        }
    )
    settings["results_view"]["compare"].update(
        {
            "selected_ranges": [SEGMENT_RANGE_OPTIONS[1]],
            "selected_directions": ["NE"],
            "segment_evidence_time_bin": "6h",
            "station_evidence_time_bin": "1h",
            "selected_stations": [{"callsign": "K1ABC", "locator": "FN42"}],
            "show_non_joint": True,
        }
    )

    entries = url_state.build_query_from_settings(settings, include_run=False)
    entry_map = dict(entries)
    normalized = url_state.build_config_from_url(
        url_state.parse_url_query(entry_map)
    )

    assert entry_map["ranges"] == "2500-5000"
    assert entry_map["directions"] == "NE"
    assert entry_map["segment_bin"] == "6h"
    assert entry_map["station_bin"] == "1h"
    assert "temporal_view" not in entry_map
    assert entry_map["selected_station"] == "K1ABC@FN42"
    assert entry_map["show_unpaired"] == "1"
    assert "show_zero" not in entry_map
    assert normalized["selected_stations_compare"] == [
        {"callsign": "K1ABC", "locator": "FN42"},
    ]
    assert normalized["selected_stations_absolute"] is None
    assert normalized["show_zero_target"] is False


@pytest.mark.parametrize("legacy_temporal_view", ("chronological", "utc_hour"))
def test_compare_accepts_valid_legacy_temporal_view_as_a_noop(
    legacy_temporal_view,
):
    """Load old Compare links without restoring or re-emitting retired state."""
    settings = _settings_for_mode("hardware_rx")
    canonical_entries = dict(
        url_state.build_query_from_settings(settings, include_run=False)
    )
    legacy_entries = dict(canonical_entries)
    legacy_entries["temporal_view"] = legacy_temporal_view

    normalized = url_state.build_config_from_url(
        url_state.parse_url_query(legacy_entries)
    )
    canonical_normalized = url_state.build_config_from_url(
        url_state.parse_url_query(canonical_entries)
    )

    assert "station_evidence_temporal_view_compare" not in normalized
    assert normalized == canonical_normalized
    assert "temporal_view" not in canonical_entries


def test_compare_rejects_an_unknown_legacy_temporal_view():
    """Validate retired URL values before discarding the compatibility no-op."""
    entries = dict(
        url_state.build_query_from_settings(
            _settings_for_mode("hardware_rx"),
            include_run=False,
        )
    )
    entries["temporal_view"] = "local_hour"

    with pytest.raises(
        url_state.UrlStateError,
        match="temporal_view must be chronological or utc_hour",
    ):
        url_state.build_config_from_url(url_state.parse_url_query(entries))


@pytest.mark.parametrize(
    ("case", "inapplicable_key", "inapplicable_value"),
    [
        ("performance", "reference", "DL2XYZ"),
        ("performance", "min_joint_spots", "2"),
        ("performance", "temporal_view", "utc_hour"),
        ("performance", "show_unpaired", "1"),
        ("hardware_rx", "tx_ab_method", "simultaneous"),
        ("hardware_rx", "show_zero", "1"),
        ("hardware_tx_sequential", "reference", "DL2XYZ"),
        ("reference_station", "local_benchmark", "local_best"),
        ("local_neighborhood", "reference_qth", "JO62"),
    ],
)
def test_mode_inapplicable_parameters_are_rejected(
    case,
    inapplicable_key,
    inapplicable_value,
):
    """Reject inactive scientific and result branches instead of ignoring them."""
    entries = dict(
        url_state.build_query_from_settings(
            _settings_for_mode(case),
            include_run=False,
        )
    )
    entries[inapplicable_key] = inapplicable_value

    with pytest.raises(
        url_state.UrlStateError,
        match="not applicable",
    ):
        url_state.build_config_from_url(entries)


@pytest.mark.parametrize(
    ("key", "values"),
    [
        ("v", ["1", "1"]),
        ("callsign", ["DL1MKS", "DL2XYZ"]),
        ("selected_station", ["K1ABC@FN42", "none"]),
    ],
)
def test_duplicate_owned_query_parameters_are_rejected(key, values):
    """Reject duplicates before any canonical configuration is constructed."""
    query_values = {
        "v": "1",
        "unrelated": ["one", "two"],
        key: values,
    }

    with pytest.raises(
        url_state.UrlStateError,
        match="Duplicate WSPRadar query parameter",
    ):
        url_state.parse_url_query(query_values)


def test_duplicate_unrelated_parameters_are_ignored():
    """Leave duplicate browser parameters outside WSPRadar's ownership alone."""
    assert url_state.parse_url_query(
        {
            "v": "1",
            "utm_source": ["first", "second"],
        }
    ) == {"v": "1"}


@pytest.mark.parametrize("version", ["0", "2", "01", "future"])
def test_unsupported_url_versions_report_the_stable_error_category(version):
    """Reject every URL contract other than exact version 1."""
    with pytest.raises(url_state.UrlStateError) as error:
        url_state.parse_url_query({"v": version})

    assert error.value.code == "unsupported_version"


def test_missing_url_version_is_invalid():
    """Require an explicit version whenever any owned URL parameter is present."""
    with pytest.raises(url_state.UrlStateError) as error:
        url_state.parse_url_query({"direction": "rx"})

    assert error.value.code == "invalid"
    assert "Missing required URL parameter: v" in str(error.value)


@pytest.mark.parametrize("retired_key", ["hours", "anchor"])
def test_retired_owned_url_parameters_are_rejected(retired_key):
    """Keep relative time and query-based anchors outside the URL-v1 contract."""
    with pytest.raises(url_state.UrlStateError, match="Retired"):
        url_state.parse_url_query(
            {
                "v": "1",
                retired_key: "24",
            }
        )


@pytest.mark.parametrize("run_value", ["", "0", "true", "yes", "01"])
def test_run_flag_accepts_only_exact_one(run_value):
    """Keep replay opt-in strict and unambiguous."""
    with pytest.raises(url_state.UrlStateError, match="run must be exactly 1"):
        url_state.parse_url_query({"v": "1", "run": run_value})


@pytest.mark.parametrize(
    "selected_station",
    [
        "all",
        "K1ABC",
        "@FN42",
        "K1ABC@",
        "K1ABC@FN42@EXTRA",
        "K1ABC,K2XYZ@FN42",
        "INVALID!@FN42",
        "K1ABC@INVALID!",
    ],
)
def test_malformed_or_multiple_selected_station_values_are_rejected(
    selected_station,
):
    """Accept exactly one validated identity or the explicit ``none`` token."""
    entries = dict(
        url_state.build_query_from_settings(
            _settings_for_mode("hardware_rx"),
            include_run=False,
        )
    )
    entries["selected_station"] = selected_station

    with pytest.raises(url_state.UrlStateError):
        url_state.build_config_from_url(entries)


def test_serializer_rejects_more_than_one_station():
    """Never emit a public URL that combines multiple radio paths."""
    settings = _settings_for_mode("hardware_rx")
    settings["results_view"]["compare"]["selected_stations"] = [
        {"callsign": "K1ABC", "locator": "FN42"},
        {"callsign": "W1AAA", "locator": "FN31"},
    ]

    with pytest.raises(ValueError, match="at most one|exactly one"):
        url_state.build_query_from_settings(settings, include_run=False)


def test_invalid_hydration_does_not_partially_apply_configuration():
    """Record the rejected signature without mutating any editable config field."""
    valid_entries = dict(
        url_state.build_query_from_settings(
            _settings_for_mode("performance"),
            include_run=True,
        )
    )
    invalid_query = {key: [value] for key, value in valid_entries.items()}
    invalid_query["callsign"] = ["DL1MKS", "DL2XYZ"]
    session_state = {
        "sentinel": "preserved",
        "val_callsign": "ORIGINAL",
        "run_mode": "existing-result",
    }
    applied_configs = []
    submissions = []

    result = url_state.hydrate_initial_url_state(
        session_state,
        invalid_query,
        apply_config=lambda config, state: applied_configs.append((config, state)),
        submit_analysis=lambda *args, **kwargs: submissions.append((args, kwargs)),
    )

    assert result == url_state.UrlHydrationResult(
        was_processed=True,
        config_was_applied=False,
        replay_was_scheduled=False,
        error_code="invalid",
    )
    assert applied_configs == []
    assert submissions == []
    assert session_state["sentinel"] == "preserved"
    assert session_state["val_callsign"] == "ORIGINAL"
    assert session_state["run_mode"] == "existing-result"
    assert url_state.URL_HYDRATION_SIGNATURE_KEY in session_state
    assert session_state[url_state.URL_HYDRATION_ERROR_KEY]["code"] == "invalid"

    second_result = url_state.hydrate_initial_url_state(
        session_state,
        {key: [value] for key, value in valid_entries.items()},
        apply_config=lambda config, state: applied_configs.append((config, state)),
        submit_analysis=lambda *args, **kwargs: submissions.append((args, kwargs)),
    )
    assert second_result == url_state.UrlHydrationResult(False, False, False)
    assert applied_configs == []
    assert submissions == []


def test_valid_run_url_applies_and_schedules_replay_exactly_once():
    """Submit one URL replay and expose one matching results-anchor request."""
    entries = dict(
        url_state.build_query_from_settings(
            _settings_for_mode("hardware_rx"),
            include_run=True,
        )
    )
    query_values = {key: [value] for key, value in entries.items()}
    session_state = {}
    applied_calls = []
    submission_calls = []

    def apply_config(config, state):
        applied_calls.append(config)
        state["applied_callsign"] = config["callsign"]

    def submit_analysis(state, **kwargs):
        submission_calls.append((state, kwargs))
        return "submission-token"

    first_result = url_state.hydrate_initial_url_state(
        session_state,
        query_values,
        apply_config=apply_config,
        submit_analysis=submit_analysis,
    )
    second_result = url_state.hydrate_initial_url_state(
        session_state,
        query_values,
        apply_config=apply_config,
        submit_analysis=submit_analysis,
    )

    assert first_result == url_state.UrlHydrationResult(True, True, True)
    assert second_result == url_state.UrlHydrationResult(False, False, False)
    assert len(applied_calls) == 1
    assert session_state["applied_callsign"] == "DL1MKS"
    assert len(submission_calls) == 1
    assert submission_calls[0][0] is session_state
    assert submission_calls[0][1] == {"request_source": "url_replay"}
    assert url_state.consume_url_replay_navigation(session_state) is True
    assert url_state.consume_url_replay_navigation(session_state) is False


def test_default_replay_path_enters_existing_submission_lifecycle_once():
    """Create one claimable URL-replay request through the production lifecycle."""
    entries = dict(
        url_state.build_query_from_settings(
            _settings_for_mode("performance"),
            include_run=True,
        )
    )
    session_state = _SessionState()

    hydration = url_state.hydrate_initial_url_state(session_state, entries)
    first_request = claim_analysis_submission_request(session_state)
    second_request = claim_analysis_submission_request(session_state)
    repeated_hydration = url_state.hydrate_initial_url_state(
        session_state,
        entries,
    )

    assert hydration == url_state.UrlHydrationResult(True, True, True)
    assert first_request is not None
    assert first_request.source == "url_replay"
    assert second_request is None
    assert repeated_hydration == url_state.UrlHydrationResult(False, False, False)


def test_config_only_url_applies_once_without_submitting():
    """Hydrate a complete URL without treating omitted ``run`` as replay."""
    entries = dict(
        url_state.build_query_from_settings(
            _settings_for_mode("performance"),
            include_run=False,
        )
    )
    session_state = {}
    applied_calls = []
    submission_calls = []

    result = url_state.hydrate_initial_url_state(
        session_state,
        entries,
        apply_config=lambda config, _state: applied_calls.append(config),
        submit_analysis=lambda *args, **kwargs: submission_calls.append(
            (args, kwargs)
        ),
    )

    assert result == url_state.UrlHydrationResult(True, True, False)
    assert len(applied_calls) == 1
    assert submission_calls == []
    assert url_state.consume_url_replay_navigation(session_state) is False


def test_run_output_tracks_result_validity_but_not_result_view_edits():
    """Retain replay through view changes and remove it after scientific reset."""
    settings = _settings_for_mode("performance")
    normalized = config_io.normalize_config_settings(settings)
    session_state = _SessionState()
    config_io.apply_config_state_values(normalized, session_state)
    session_state["lang"] = "en"
    session_state["run_mode"] = "analysis"

    initial_entries = url_state.build_query_from_state(session_state)
    session_state["val_results_time_bin_absolute"] = "1h"
    result_view_entries = url_state.build_query_from_state(session_state)
    session_state["run_mode"] = None
    reset_entries = url_state.build_query_from_state(session_state)

    assert dict(initial_entries)["run"] == "1"
    assert dict(result_view_entries)["run"] == "1"
    assert dict(result_view_entries)["station_bin"] == "1h"
    assert "run" not in dict(reset_entries)


def test_share_url_uses_canonical_origin_owned_state_run_and_result_anchor():
    """Build a clean replay URL instead of copying unrelated browser state."""
    settings = _settings_for_mode("hardware_rx")
    settings["results_view"]["compare"]["selected_stations"] = [
        {"callsign": "K1ABC", "locator": "FN42"},
    ]
    normalized = config_io.normalize_config_settings(settings)
    session_state = _SessionState()
    config_io.apply_config_state_values(normalized, session_state)
    session_state.update(
        {
            "lang": "en",
            "run_mode": "analysis",
            "unrelated_browser_parameter": "must-not-leak",
        }
    )

    share_url = url_state.build_share_url(session_state)
    split_url = urlsplit(share_url)
    query_pairs = parse_qsl(split_url.query)

    assert split_url.scheme == "https"
    assert split_url.netloc == "wspradar.org"
    assert split_url.path == "/"
    assert split_url.fragment == "wspradar-results-inspection"
    assert query_pairs[0] == ("v", "1")
    assert query_pairs[1] == ("run", "1")
    assert dict(query_pairs)["selected_station"] == "K1ABC@FN42"
    assert "unrelated_browser_parameter" not in split_url.query
    assert not any(character.isspace() for character in share_url)


def test_direction_and_range_lists_parse_to_existing_canonical_order():
    """Normalize unordered public lists before applying them to result state."""
    entries = dict(
        url_state.build_query_from_settings(
            _settings_for_mode("performance"),
            include_run=False,
        )
    )
    entries["ranges"] = "15000-20000,0-2500,5000-10000"
    entries["directions"] = "NNW,NW,N"

    normalized = url_state.build_config_from_url(entries)

    assert normalized["selected_ranges_absolute"] == [
        SEGMENT_RANGE_OPTIONS[0],
        SEGMENT_RANGE_OPTIONS[2],
        SEGMENT_RANGE_OPTIONS[4],
    ]
    assert normalized["selected_directions_absolute"] == [
        direction
        for direction in SEGMENT_DIRECTION_OPTIONS
        if direction in {"N", "NW", "NNW"}
    ]


def test_app_hydrates_before_widgets_and_routes_replay_through_normal_submission():
    """Pin initial hydration, admitted replay, and post-run anchor synchronization."""
    repository_root = Path(__file__).resolve().parents[2]
    app_source = (repository_root / "app.py").read_text(encoding="utf-8")

    assert (
        app_source.index("init_session_state()")
        < app_source.index("set_reset_config(reset_time_window=False)")
        < app_source.index("hydrate_initial_url_state(")
        < app_source.index("t = T[st.session_state.lang]")
        < app_source.index("render_core_expander(t)")
    )
    assert (
        'submission_request.source in {"main_button", "url_replay"}'
        in app_source
    )
    assert (
        app_source.index("elif submission_snapshot is not None:")
        < app_source.index("if consume_url_replay_navigation(")
        < app_source.index("render_page_navigation_controller(")
        < app_source.index("render_current_url_synchronizer(")
        < app_source.index("render_documentation_section(")
    )
