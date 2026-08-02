import pytest

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
        result_state.ACTIVE_RUN_DATABASE_SOURCE_KEY: {
            "run_id": 42,
            "source_key": "wd2",
        },
        result_state.COMPLETED_RUN_SNAPSHOT_KEY: {
            "schema_version": result_state.COMPLETED_RUN_SNAPSHOT_SCHEMA_VERSION,
            "run_id": 42,
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
    assert result_state.ACTIVE_RUN_DATABASE_SOURCE_KEY not in session_state
    assert result_state.COMPLETED_RUN_SNAPSHOT_KEY not in session_state
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


def test_clear_rendered_result_state_preserves_database_source_binding():
    """A same-run refresh must drop stale recipes without changing provenance."""
    source_binding = {"run_id": 42, "source_key": "wd2"}
    completed_snapshot = {
        "schema_version": result_state.COMPLETED_RUN_SNAPSHOT_SCHEMA_VERSION,
        "run_id": 42,
    }
    session_state = {
        "run_id": 42,
        result_state.EXPORT_STATE_KEY: {"old": "recipe"},
        result_state.EXPORT_RUN_ID_KEY: 42,
        result_state.EXPORT_ZIP_BYTES_KEY: b"zip",
        result_state.INSPECTOR_CACHE_STATE_KEY: object(),
        result_state.ACTIVE_RUN_DATABASE_SOURCE_KEY: source_binding,
        result_state.COMPLETED_RUN_SNAPSHOT_KEY: completed_snapshot,
    }

    result_state.clear_rendered_result_state(session_state)

    assert session_state[result_state.EXPORT_STATE_KEY] == {}
    assert session_state[result_state.EXPORT_RUN_ID_KEY] == 42
    assert result_state.EXPORT_ZIP_BYTES_KEY not in session_state
    assert result_state.INSPECTOR_CACHE_STATE_KEY not in session_state
    assert session_state[result_state.ACTIVE_RUN_DATABASE_SOURCE_KEY] is source_binding
    assert (
        session_state[result_state.COMPLETED_RUN_SNAPSHOT_KEY]
        is completed_snapshot
    )


def test_completed_rerender_state_clear_preserves_versioned_inspector_cache():
    """Reuse compact Inspector models only for an already validated result."""
    inspector_cache = object()
    session_state = {
        "run_id": 42,
        result_state.EXPORT_STATE_KEY: {"old": "recipe"},
        result_state.EXPORT_ZIP_BYTES_KEY: b"zip",
        result_state.INSPECTOR_CACHE_STATE_KEY: inspector_cache,
    }

    result_state.clear_rendered_result_state(
        session_state,
        preserve_inspector_cache=True,
    )

    assert session_state[result_state.EXPORT_STATE_KEY] == {}
    assert result_state.EXPORT_ZIP_BYTES_KEY not in session_state
    assert (
        session_state[result_state.INSPECTOR_CACHE_STATE_KEY]
        is inspector_cache
    )


def test_completed_run_snapshot_publication_and_reads_are_copy_isolated():
    """Do not let later render code mutate the published completion marker."""
    session_state = {}
    snapshot = {
        "schema_version": result_state.COMPLETED_RUN_SNAPSHOT_SCHEMA_VERSION,
        "analyses": [{"outcome": "renderable"}],
    }

    result_state.publish_completed_run_snapshot(session_state, snapshot)
    snapshot["analyses"][0]["outcome"] = "changed by caller"
    restored = result_state.get_completed_run_snapshot(session_state)
    restored["analyses"][0]["outcome"] = "changed by reader"

    assert session_state[result_state.COMPLETED_RUN_SNAPSHOT_KEY]["analyses"] == [
        {"outcome": "renderable"}
    ]


def test_completed_run_snapshot_rejects_unknown_schema_versions():
    """Treat an incompatible result marker as unavailable, never reusable."""
    session_state = {
        result_state.COMPLETED_RUN_SNAPSHOT_KEY: {
            "schema_version": 999,
        }
    }

    assert result_state.get_completed_run_snapshot(session_state) is None
    with pytest.raises(ValueError, match="schema version"):
        result_state.publish_completed_run_snapshot(
            session_state,
            {"schema_version": 999},
        )


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
