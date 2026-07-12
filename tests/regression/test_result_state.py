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
