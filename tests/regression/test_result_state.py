from datetime import datetime, timedelta, timezone

from ui import result_state


def test_reset_result_state_retires_artifacts_and_clears_all_run_caches(monkeypatch):
    """A lightweight reset must preserve the complete result lifecycle."""
    retired_states = []
    monkeypatch.setattr(
        result_state,
        "retire_registered_session_artifacts",
        lambda session_state: retired_states.append(session_state),
    )
    session_state = {
        "run_id": 42,
        result_state.EXPORT_STATE_KEY: {"old": "block"},
        result_state.EXPORT_RUN_ID_KEY: 11,
        result_state.EXPORT_ZIP_BYTES_KEY: b"zip",
        result_state.EXPORT_ZIP_FILENAME_KEY: "results.zip",
        result_state.EXPORT_ZIP_SIGNATURE_KEY: "signature",
        result_state.INSPECTOR_CACHE_STATE_KEY: object(),
        result_state.STABILITY_CACHE_STATE_KEY: {"old": "stability"},
        result_state.ACTIVE_RUN_TIME_WINDOW_KEY: {
            "run_id": 42,
            "start_utc": datetime(2026, 7, 16, tzinfo=timezone.utc),
            "end_utc": datetime(2026, 7, 17, tzinfo=timezone.utc),
        },
        result_state.ACTIVE_RUN_DATABASE_SOURCE_KEY: {
            "run_id": 42,
            "source_key": "wd2",
        },
        "unrelated": "preserved",
    }

    result_state.reset_result_state(session_state)

    assert retired_states == [session_state]
    assert session_state[result_state.EXPORT_STATE_KEY] == {}
    assert session_state[result_state.EXPORT_RUN_ID_KEY] == 42
    assert result_state.EXPORT_ZIP_BYTES_KEY not in session_state
    assert result_state.EXPORT_ZIP_FILENAME_KEY not in session_state
    assert result_state.EXPORT_ZIP_SIGNATURE_KEY not in session_state
    assert result_state.INSPECTOR_CACHE_STATE_KEY not in session_state
    assert result_state.STABILITY_CACHE_STATE_KEY not in session_state
    assert result_state.ACTIVE_RUN_TIME_WINDOW_KEY not in session_state
    assert result_state.ACTIVE_RUN_DATABASE_SOURCE_KEY not in session_state
    assert session_state["unrelated"] == "preserved"


def test_clear_prepared_result_state_does_not_clear_registered_blocks():
    """Prepared downloads can be invalidated without dropping result recipes."""
    session_state = {
        result_state.EXPORT_STATE_KEY: {"RX": "recipe"},
        result_state.EXPORT_ZIP_BYTES_KEY: b"zip",
        result_state.EXPORT_ZIP_FILENAME_KEY: "results.zip",
        result_state.EXPORT_ZIP_SIGNATURE_KEY: "signature",
    }

    result_state.clear_prepared_result_state(session_state)

    assert session_state[result_state.EXPORT_STATE_KEY] == {"RX": "recipe"}
    assert result_state.EXPORT_ZIP_BYTES_KEY not in session_state
    assert result_state.EXPORT_ZIP_FILENAME_KEY not in session_state
    assert result_state.EXPORT_ZIP_SIGNATURE_KEY not in session_state


def test_clear_rendered_result_state_preserves_run_binding_and_time_window():
    """A same-run refresh must drop stale recipes without changing provenance."""
    source_binding = {"run_id": 42, "source_key": "wd2"}
    time_window = {
        "run_id": 42,
        "start_utc": datetime(2026, 7, 16, tzinfo=timezone.utc),
        "end_utc": datetime(2026, 7, 17, tzinfo=timezone.utc),
    }
    session_state = {
        "run_id": 42,
        result_state.EXPORT_STATE_KEY: {"old": "recipe"},
        result_state.EXPORT_RUN_ID_KEY: 42,
        result_state.EXPORT_ZIP_BYTES_KEY: b"zip",
        result_state.INSPECTOR_CACHE_STATE_KEY: object(),
        result_state.STABILITY_CACHE_STATE_KEY: {"old": "stability"},
        result_state.ACTIVE_RUN_DATABASE_SOURCE_KEY: source_binding,
        result_state.ACTIVE_RUN_TIME_WINDOW_KEY: time_window,
    }

    result_state.clear_rendered_result_state(session_state)

    assert session_state[result_state.EXPORT_STATE_KEY] == {}
    assert session_state[result_state.EXPORT_RUN_ID_KEY] == 42
    assert result_state.EXPORT_ZIP_BYTES_KEY not in session_state
    assert result_state.INSPECTOR_CACHE_STATE_KEY not in session_state
    assert result_state.STABILITY_CACHE_STATE_KEY not in session_state
    assert session_state[result_state.ACTIVE_RUN_DATABASE_SOURCE_KEY] is source_binding
    assert session_state[result_state.ACTIVE_RUN_TIME_WINDOW_KEY] is time_window


def test_active_run_time_window_is_reused_only_for_its_matching_run():
    """Prevent a Last-X interval from drifting or leaking into a later run."""
    start_utc = datetime(2026, 7, 16, 10, 15, tzinfo=timezone.utc)
    end_utc = start_utc + timedelta(hours=24)
    session_state = {"run_id": 42}

    result_state.set_active_run_time_window(
        session_state,
        run_id=42,
        start_utc=start_utc,
        end_utc=end_utc,
    )

    assert result_state.get_active_run_time_window(session_state) == (
        start_utc,
        end_utc,
    )
    session_state["run_id"] = 43
    assert result_state.get_active_run_time_window(session_state) is None


def test_active_database_source_is_committed_only_for_its_matching_run():
    session_state = {"run_id": 42}

    result_state.set_active_run_database_source(
        session_state,
        run_id=42,
        source_key="wd2",
    )

    assert result_state.get_active_run_database_source(session_state) == "wd2"
    session_state["run_id"] = 43
    assert result_state.get_active_run_database_source(session_state) is None
