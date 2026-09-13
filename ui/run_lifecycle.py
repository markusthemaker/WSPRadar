"""Named, dependency-light transitions for one session's analysis lifecycle.

The transition functions compose the existing result and submission owners.
They do not import scientific work, acquire data, or render exports. Input
adapters continue to own individual configuration values and widget state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Mapping, MutableMapping

if TYPE_CHECKING:
    from core.completed_run import CompletedRun

from ui.analysis_submission_state import (
    cancel_analysis_submission,
    handoff_analysis_submission,
)
from ui.inspector.selection_state import release_selected_station_state
from ui.result_state import (
    clear_prepared_result_state,
    clear_rendered_result_state,
    get_completed_run_snapshot,
    publish_completed_run_snapshot,
    reset_result_state,
)


@dataclass(frozen=True)
class RunInvalidationPolicy:
    """Specify which input intent survives retirement of completed evidence."""

    should_release_selected_stations: bool
    should_retire_demo_identity: bool
    should_retire_profile_context: bool


SCIENTIFIC_EDIT_POLICY = RunInvalidationPolicy(
    should_release_selected_stations=True,
    should_retire_demo_identity=True,
    should_retire_profile_context=False,
)
EXPERIMENT_DEFINITION_EDIT_POLICY = RunInvalidationPolicy(
    should_release_selected_stations=True,
    should_retire_demo_identity=True,
    should_retire_profile_context=True,
)
SHELL_RESET_POLICY = RunInvalidationPolicy(
    should_release_selected_stations=False,
    should_retire_demo_identity=False,
    should_retire_profile_context=False,
)


def retire_loaded_profile_context(
    session_state: MutableMapping[str, Any],
) -> None:
    """Detach profile metadata and save identity from a changed experiment."""
    session_state["val_config_profile"] = None
    session_state["loaded_config_profile"] = None
    session_state["guided_loaded_demo_profile"] = None
    session_state["guided_demo_metadata_open"] = False


def _invalidate_current_run(
    session_state: MutableMapping[str, Any],
    policy: RunInvalidationPolicy,
) -> None:
    """Cancel replacement work and retire evidence under one input policy."""
    had_current_result = bool(session_state.get("run_mode"))
    cancel_analysis_submission(session_state)
    session_state["run_mode"] = None
    if policy.should_retire_demo_identity:
        session_state["active_demo_profile"] = None
    if policy.should_retire_profile_context:
        retire_loaded_profile_context(session_state)
    if policy.should_release_selected_stations:
        release_selected_station_state(session_state)
    reset_result_state(session_state)
    if had_current_result:
        session_state["configuration_changed_since_run"] = True


def invalidate_scientific_run(
    session_state: MutableMapping[str, Any],
    *,
    experiment_definition_changed: bool = False,
) -> None:
    """Require an explicit Run after a scientific or experiment edit."""
    _invalidate_current_run(
        session_state,
        EXPERIMENT_DEFINITION_EDIT_POLICY
        if experiment_definition_changed
        else SCIENTIFIC_EDIT_POLICY,
    )


def reset_shell_run(session_state: MutableMapping[str, Any]) -> None:
    """Retire evidence for a shell action while retaining all input intent."""
    _invalidate_current_run(session_state, SHELL_RESET_POLICY)


def prepare_configuration_load(
    session_state: MutableMapping[str, Any],
) -> None:
    """Retire the replaced run before applying validated saved settings.

    The caller installs profile and station intent from the validated document.
    This transition neither guesses new values nor starts acquisition.
    """
    cancel_analysis_submission(session_state)
    session_state["active_demo_profile"] = None
    session_state["run_mode"] = None
    session_state["configuration_changed_since_run"] = False
    reset_result_state(session_state)


def initialize_analysis_run(
    session_state: MutableMapping[str, Any],
    *,
    run_mode: str,
    run_id: Any,
) -> None:
    """Replace old evidence after input validation, retaining the owned token."""
    if run_mode not in {"RX", "TX"}:
        raise ValueError("Analysis run mode must be RX or TX.")
    session_state["run_mode"] = run_mode
    session_state["run_id"] = run_id
    session_state["configuration_changed_since_run"] = False
    reset_result_state(session_state)


def change_presentation_language(
    session_state: MutableMapping[str, Any],
    *,
    language: str,
) -> None:
    """Relocalize committed evidence; unfinished work requires an explicit Run.

    The controller validates artifacts and refreshes localized export state on
    the next render. This callback does not scan, copy, or recreate evidence.
    """
    if language not in {"en", "de"}:
        raise ValueError("Presentation language must be en or de.")
    if session_state.get("lang") != language:
        clear_prepared_result_state(session_state)
    cancel_analysis_submission(session_state)
    session_state["lang"] = language
    if get_completed_run_snapshot(session_state) is None:
        session_state["run_mode"] = None


def commit_saved_profile_metadata(
    session_state: MutableMapping[str, Any],
    profile: dict[str, Any],
) -> bool:
    """Commit validated save metadata without retiring completed evidence.

    The config-save boundary validates the profile before calling this function.
    Draft edits never reach this transition. Identical metadata keeps the
    existing package; changed metadata retires only prepared ZIP state.
    """
    if session_state.get("val_config_profile") == profile:
        return False
    session_state["val_config_profile"] = profile
    clear_prepared_result_state(session_state)
    return True


def handoff_input_view_submission(
    session_state: MutableMapping[str, Any],
) -> str | None:
    """Transfer an active request while preserving scientific and result state."""
    if not session_state.get("run_mode"):
        return None
    return handoff_analysis_submission(
        session_state,
        request_source="input_view_change",
    )


def fail_analysis_run(
    session_state: MutableMapping[str, Any],
    *,
    retire_results: bool = False,
) -> None:
    """Stop rendering a failed run without releasing another script's token.

    Existing failure sites distinguish stopping an uncommitted attempt from
    retiring already staged artifacts. Their owning script remains responsible
    for the token-aware submission completion in its ``finally`` path.
    """
    session_state["run_mode"] = None
    if retire_results:
        reset_result_state(session_state)


def retire_unavailable_completed_run(
    session_state: MutableMapping[str, Any],
) -> None:
    """Retire missing or incompatible retained artifacts without acquisition."""
    fail_analysis_run(session_state, retire_results=True)


def begin_result_render(
    session_state: MutableMapping[str, Any],
    *,
    is_completed_rerender: bool = False,
) -> None:
    """Refresh registered presentation while retaining committed run provenance.

    Completed rerenders preserve the run's bounded inspector cache, focus, and
    export registry. The export owner invalidates a prepared package when its
    registered dependencies change; unchanged registrations permit reuse.
    """
    clear_rendered_result_state(
        session_state,
        preserve_inspector_cache=is_completed_rerender,
        preserve_export_state=is_completed_rerender,
    )


def publish_completed_analysis_run(
    session_state: MutableMapping[str, Any],
    snapshot: CompletedRun | Mapping[str, Any],
) -> None:
    """Commit completed evidence only after every analysis and inspector exists."""
    publish_completed_run_snapshot(session_state, snapshot)
