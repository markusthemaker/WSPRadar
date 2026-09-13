"""Behavioral contracts for named, lightweight analysis-run transitions."""

from copy import deepcopy
from pathlib import Path
import subprocess
import sys

import pytest

from core.artifact_store import SESSION_ARTIFACT_PATHS_KEY
from ui.inspector import selection_state as inspector_selection
from ui import result_state, run_lifecycle
from ui.analysis_submission_state import (
    begin_analysis_submission,
    claim_analysis_submission_request,
    finish_analysis_submission,
    get_analysis_submission,
)


def _completed_session_state():
    """Provide owned result markers without constructing scientific fixtures."""
    return {
        "run_mode": "RX",
        "run_id": 71,
        "lang": "en",
        "active_demo_profile": "loaded-demo",
        "val_config_profile": {"id": "loaded-demo"},
        "loaded_config_profile": {"id": "loaded-demo"},
        "guided_loaded_demo_profile": "loaded-demo",
        "guided_demo_metadata_open": True,
        "val_results_selected_stations_compare": [
            {"callsign": "K1ABC", "locator": "FN42"},
        ],
        "val_results_selected_stations_absolute": [],
        "val_callsign": "N1TEST",
        result_state.COMPLETED_RUN_SNAPSHOT_KEY: object(),
        result_state.INSPECTOR_CACHE_STATE_KEY: object(),
        result_state.EXPORT_STATE_KEY: {"RX": {"analysis_id": "RX"}},
        result_state.EXPORT_RUN_ID_KEY: 71,
        result_state.EXPORT_ZIP_BYTES_KEY: b"prepared",
        result_state.ACTIVE_RUN_DATABASE_SOURCE_KEY: {
            "run_id": 71,
            "source_key": "wspr_live",
        },
    }


@pytest.mark.parametrize(
    "transition,expected_selection,expected_profile,expected_demo",
    [
        (run_lifecycle.invalidate_scientific_run, None, "loaded-demo", None),
        (
            lambda state: run_lifecycle.invalidate_scientific_run(
                state, experiment_definition_changed=True,
            ),
            None,
            None,
            None,
        ),
        (run_lifecycle.reset_shell_run, "retained", "loaded-demo", "loaded-demo"),
    ],
)
def test_invalidation_retires_evidence_under_explicit_input_policy(
    monkeypatch,
    transition,
    expected_selection,
    expected_profile,
    expected_demo,
):
    session_state = _completed_session_state()
    selected_stations = session_state["val_results_selected_stations_compare"]
    submission_token = begin_analysis_submission(session_state)
    retired_sessions = []
    monkeypatch.setattr(
        result_state,
        "retire_registered_session_artifacts",
        retired_sessions.append,
    )

    transition(session_state)

    assert retired_sessions == [session_state]
    assert session_state["run_mode"] is None
    assert session_state["run_id"] == 71
    assert session_state["val_callsign"] == "N1TEST"
    assert session_state["configuration_changed_since_run"] is True
    assert session_state["active_demo_profile"] == expected_demo
    assert session_state["guided_loaded_demo_profile"] == expected_profile
    if expected_profile is None:
        assert session_state["loaded_config_profile"] is None
        assert session_state["val_config_profile"] is None
        assert session_state["guided_demo_metadata_open"] is False
    else:
        assert session_state["loaded_config_profile"] == {"id": expected_profile}
    if expected_selection == "retained":
        assert session_state["val_results_selected_stations_compare"] is selected_stations
        assert session_state["val_results_selected_stations_absolute"] == []
    else:
        assert session_state["val_results_selected_stations_compare"] is None
        assert session_state["val_results_selected_stations_absolute"] is None
    assert result_state.COMPLETED_RUN_SNAPSHOT_KEY not in session_state
    assert result_state.INSPECTOR_CACHE_STATE_KEY not in session_state
    assert result_state.ACTIVE_RUN_DATABASE_SOURCE_KEY not in session_state
    assert result_state.EXPORT_ZIP_BYTES_KEY not in session_state
    assert session_state[result_state.EXPORT_STATE_KEY] == {}
    assert get_analysis_submission(session_state) is None
    assert finish_analysis_submission(session_state, submission_token) is False


def test_scientific_edit_while_idle_does_not_claim_a_completed_run_changed():
    session_state = {"run_mode": None, "configuration_changed_since_run": False}

    run_lifecycle.invalidate_scientific_run(session_state)

    assert session_state["configuration_changed_since_run"] is False


@pytest.mark.parametrize("has_completed_run", [False, True])
@pytest.mark.parametrize("language", ["en", "de"])
def test_language_transition_preserves_evidence_and_cancels_only_submission(
    monkeypatch, has_completed_run, language,
):
    session_state = _completed_session_state()
    owned_results = {
        state_key: session_state[state_key]
        for state_key in (
            result_state.COMPLETED_RUN_SNAPSHOT_KEY,
            result_state.INSPECTOR_CACHE_STATE_KEY,
            result_state.EXPORT_STATE_KEY,
            result_state.ACTIVE_RUN_DATABASE_SOURCE_KEY,
        )
    }
    submission_token = begin_analysis_submission(session_state)
    monkeypatch.setattr(
        run_lifecycle,
        "get_completed_run_snapshot",
        lambda state: owned_results[result_state.COMPLETED_RUN_SNAPSHOT_KEY]
        if has_completed_run
        else None,
    )

    run_lifecycle.change_presentation_language(session_state, language=language)

    assert session_state["lang"] == language
    assert session_state["run_mode"] == ("RX" if has_completed_run else None)
    assert session_state["run_id"] == 71
    assert session_state["active_demo_profile"] == "loaded-demo"
    assert session_state["val_callsign"] == "N1TEST"
    for state_key, owned_result in owned_results.items():
        assert session_state[state_key] is owned_result
    if language == "en":
        assert session_state[result_state.EXPORT_ZIP_BYTES_KEY] == b"prepared"
    else:
        assert result_state.EXPORT_ZIP_BYTES_KEY not in session_state
    assert get_analysis_submission(session_state) is None
    assert finish_analysis_submission(session_state, submission_token) is False


def test_input_view_handoff_preserves_completed_state_and_protects_new_token():
    session_state = _completed_session_state()
    completed_run = session_state[result_state.COMPLETED_RUN_SNAPSHOT_KEY]
    prior_token = begin_analysis_submission(session_state)

    replacement_token = run_lifecycle.handoff_input_view_submission(session_state)

    assert replacement_token and replacement_token != prior_token
    assert finish_analysis_submission(session_state, prior_token) is False
    assert get_analysis_submission(session_state).token == replacement_token
    assert session_state[result_state.COMPLETED_RUN_SNAPSHOT_KEY] is completed_run
    assert session_state["run_mode"] == "RX"
    claimed_request = claim_analysis_submission_request(session_state)
    assert claimed_request.source == "input_view_change"
    assert claimed_request.token == replacement_token


def test_idle_input_view_change_does_not_schedule_acquisition():
    session_state = {"run_mode": None}

    assert run_lifecycle.handoff_input_view_submission(session_state) is None
    assert get_analysis_submission(session_state) is None


def test_configuration_load_retires_run_without_rewriting_new_input_intent():
    session_state = _completed_session_state()
    selected_stations = session_state["val_results_selected_stations_compare"]
    begin_analysis_submission(session_state)

    run_lifecycle.prepare_configuration_load(session_state)

    assert session_state["run_mode"] is None
    assert session_state["active_demo_profile"] is None
    assert session_state["configuration_changed_since_run"] is False
    assert session_state["val_results_selected_stations_compare"] is selected_stations
    assert session_state["val_callsign"] == "N1TEST"
    assert result_state.COMPLETED_RUN_SNAPSHOT_KEY not in session_state
    assert get_analysis_submission(session_state) is None


def test_new_run_retires_old_evidence_without_replacing_submission_owner():
    session_state = _completed_session_state()
    submission_token = begin_analysis_submission(session_state)

    run_lifecycle.initialize_analysis_run(session_state, run_mode="TX", run_id=72)

    assert session_state["run_mode"] == "TX"
    assert session_state["run_id"] == 72
    assert session_state["configuration_changed_since_run"] is False
    assert session_state["active_demo_profile"] == "loaded-demo"
    assert result_state.COMPLETED_RUN_SNAPSHOT_KEY not in session_state
    assert get_analysis_submission(session_state).token == submission_token


@pytest.mark.parametrize("retire_results", [False, True])
def test_failure_retirement_does_not_release_the_owned_submission(retire_results):
    session_state = _completed_session_state()
    submission_token = begin_analysis_submission(session_state)

    run_lifecycle.fail_analysis_run(session_state, retire_results=retire_results)

    assert session_state["run_mode"] is None
    assert get_analysis_submission(session_state).token == submission_token
    assert (result_state.COMPLETED_RUN_SNAPSHOT_KEY in session_state) is not retire_results
    assert session_state["val_callsign"] == "N1TEST"


def test_unavailable_completed_run_requires_explicit_run_and_retires_artifacts():
    session_state = _completed_session_state()

    run_lifecycle.retire_unavailable_completed_run(session_state)

    assert session_state["run_mode"] is None
    assert result_state.COMPLETED_RUN_SNAPSHOT_KEY not in session_state
    assert result_state.INSPECTOR_CACHE_STATE_KEY not in session_state
    assert get_analysis_submission(session_state) is None


@pytest.mark.parametrize("is_completed_rerender", [False, True])
def test_result_render_preserves_exports_only_for_completed_rerenders(
    is_completed_rerender,
):
    session_state = _completed_session_state()
    submission_token = begin_analysis_submission(session_state)
    completed_run = session_state[result_state.COMPLETED_RUN_SNAPSHOT_KEY]
    export_registry = session_state[result_state.EXPORT_STATE_KEY]
    database_source = session_state[result_state.ACTIVE_RUN_DATABASE_SOURCE_KEY]
    registered_artifact_paths = ["retained-evidence.parquet"]
    session_state[SESSION_ARTIFACT_PATHS_KEY] = registered_artifact_paths
    session_state[result_state.EXPORT_ZIP_FILENAME_KEY] = "results.zip"
    session_state[result_state.EXPORT_ZIP_SIGNATURE_KEY] = "prepared-signature"
    session_state[inspector_selection.RESULTS_STATION_INSIGHTS_FOCUS_COMPARE_STATE_KEY] = {
        "run_id": 71,
        "scope_token": "retained-scope",
    }
    session_state[inspector_selection.RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY] = {
        "run_id": 71,
        "request_token": "retained-request",
    }
    cached_inspector_state = {
        state_key: session_state[state_key]
        for state_key in (
            result_state.INSPECTOR_CACHE_STATE_KEY,
            inspector_selection.RESULTS_STATION_INSIGHTS_FOCUS_COMPARE_STATE_KEY,
            inspector_selection.RESULTS_DRILLDOWN_FOCUS_COMPARE_STATE_KEY,
        )
    }

    run_lifecycle.begin_result_render(
        session_state,
        is_completed_rerender=is_completed_rerender,
    )

    assert session_state["run_mode"] == "RX"
    assert session_state["run_id"] == 71
    assert session_state[result_state.COMPLETED_RUN_SNAPSHOT_KEY] is completed_run
    assert session_state[result_state.ACTIVE_RUN_DATABASE_SOURCE_KEY] is database_source
    assert session_state[SESSION_ARTIFACT_PATHS_KEY] is registered_artifact_paths
    assert get_analysis_submission(session_state).token == submission_token
    assert session_state[result_state.EXPORT_RUN_ID_KEY] == 71
    if is_completed_rerender:
        assert session_state[result_state.EXPORT_STATE_KEY] is export_registry
        assert session_state[result_state.EXPORT_ZIP_BYTES_KEY] == b"prepared"
        assert session_state[result_state.EXPORT_ZIP_FILENAME_KEY] == "results.zip"
        assert session_state[result_state.EXPORT_ZIP_SIGNATURE_KEY] == "prepared-signature"
    else:
        assert session_state[result_state.EXPORT_STATE_KEY] == {}
        assert all(
            state_key not in session_state
            for state_key in result_state.PREPARED_RESULT_STATE_KEYS
        )
    for state_key, cached_state in cached_inspector_state.items():
        if is_completed_rerender:
            assert session_state[state_key] is cached_state
        else:
            assert state_key not in session_state


@pytest.mark.parametrize(
    "transition,arguments",
    [
        (run_lifecycle.initialize_analysis_run, {"run_mode": "other", "run_id": 72}),
        (run_lifecycle.change_presentation_language, {"language": "other"}),
    ],
)
def test_invalid_transition_input_does_not_mutate_session(transition, arguments):
    session_state = {"run_mode": "RX", "run_id": 71, "lang": "en"}
    unchanged_state = deepcopy(session_state)

    with pytest.raises(ValueError):
        transition(session_state, **arguments)

    assert session_state == unchanged_state


def test_completion_publishes_through_snapshot_owner_without_finishing_token(monkeypatch):
    session_state = {"run_mode": "RX", "run_id": 71}
    submission_token = begin_analysis_submission(session_state)
    completed_snapshot = object()
    published_snapshots = []
    monkeypatch.setattr(
        run_lifecycle,
        "publish_completed_run_snapshot",
        lambda state, snapshot: published_snapshots.append((state, snapshot)),
    )

    run_lifecycle.publish_completed_analysis_run(session_state, completed_snapshot)

    assert published_snapshots == [(session_state, completed_snapshot)]
    assert get_analysis_submission(session_state).token == submission_token


def test_run_lifecycle_import_does_not_load_scientific_or_rendering_runtime():
    project_root = Path(__file__).resolve().parents[2]
    forbidden_modules = (
        "streamlit", "pandas", "numpy", "requests", "matplotlib", "cartopy",
        "ui.run_controller", "ui.results_export", "ui.components.segment_inspector",
    )
    audit_script = (
        "import sys; import ui.run_lifecycle; "
        f"forbidden = {forbidden_modules!r}; "
        "loaded = [name for name in sys.modules "
        "if any(name == prefix or name.startswith(prefix + '.') for prefix in forbidden)]; "
        "assert not loaded, loaded"
    )
    completed_audit = subprocess.run(
        [sys.executable, "-c", audit_script],
        cwd=project_root,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert completed_audit.returncode == 0, completed_audit.stdout + completed_audit.stderr

@pytest.mark.parametrize("profile_changed", [False, True])
def test_saved_profile_commit_invalidates_only_changed_package_metadata(profile_changed):
    session_state = _completed_session_state()
    session_state[result_state.EXPORT_ZIP_FILENAME_KEY] = "results.zip"
    session_state[result_state.EXPORT_ZIP_SIGNATURE_KEY] = "signature"
    session_state[SESSION_ARTIFACT_PATHS_KEY] = ["retained.parquet"]
    token = begin_analysis_submission(session_state)
    original_profile = session_state["val_config_profile"]
    retained_state = {
        key: session_state[key]
        for key in (
            result_state.COMPLETED_RUN_SNAPSHOT_KEY,
            result_state.EXPORT_STATE_KEY,
            result_state.ACTIVE_RUN_DATABASE_SOURCE_KEY,
            result_state.INSPECTOR_CACHE_STATE_KEY,
            SESSION_ARTIFACT_PATHS_KEY,
            "loaded_config_profile",
            "val_results_selected_stations_compare",
        )
    }
    profile = dict(original_profile)
    if profile_changed:
        profile["title"] = {"en": "Saved description of this run"}

    changed = run_lifecycle.commit_saved_profile_metadata(session_state, profile)

    assert changed is profile_changed
    assert session_state["val_config_profile"] == profile
    assert session_state["val_config_profile"] is (profile if changed else original_profile)
    assert session_state["run_mode"] == "RX"
    assert session_state["run_id"] == 71
    assert session_state["active_demo_profile"] == "loaded-demo"
    assert get_analysis_submission(session_state).token == token
    assert "configuration_changed_since_run" not in session_state
    for key, retained in retained_state.items():
        assert session_state[key] is retained
    for key in result_state.PREPARED_RESULT_STATE_KEYS:
        assert (key in session_state) is not profile_changed
