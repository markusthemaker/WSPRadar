from ui.analysis_submission_state import (
    SUBMISSION_PHASE_QUEUED,
    begin_analysis_submission,
    begin_main_analysis_submission,
    cancel_analysis_submission,
    claim_analysis_submission_request,
    finish_analysis_submission,
    get_analysis_submission,
    update_analysis_submission,
)


def test_submission_request_is_claimed_once_and_tracks_personal_queue_position():
    """Keep one session submission stable across Streamlit rerun boundaries."""
    session_state = {}

    token = begin_analysis_submission(
        session_state,
        request_source="main_button",
    )
    request = claim_analysis_submission_request(session_state)

    assert request is not None
    assert request.token == token
    assert request.source == "main_button"
    assert claim_analysis_submission_request(session_state) is None
    assert update_analysis_submission(
        session_state,
        token,
        phase=SUBMISSION_PHASE_QUEUED,
        position=7,
    )
    snapshot = get_analysis_submission(session_state)
    assert snapshot is not None
    assert snapshot.token == token
    assert snapshot.phase == SUBMISSION_PHASE_QUEUED
    assert snapshot.position == 7


def test_only_the_owning_script_can_finish_a_submission_token():
    """Prevent an interrupted older script from clearing a newer submission."""
    session_state = {}
    token = begin_analysis_submission(session_state)

    assert not update_analysis_submission(
        session_state,
        "older-token",
        phase=SUBMISSION_PHASE_QUEUED,
        position=1,
    )
    assert not finish_analysis_submission(session_state, "older-token")
    assert get_analysis_submission(session_state).token == token

    assert finish_analysis_submission(session_state, token)
    assert get_analysis_submission(session_state) is None


def test_second_begin_does_not_schedule_duplicate_execution():
    """Make a repeated UI callback a no-op while one submission is in flight."""
    session_state = {}
    token = begin_analysis_submission(session_state, request_source="demo")
    claimed = claim_analysis_submission_request(session_state)

    assert claimed is not None
    assert begin_analysis_submission(
        session_state,
        request_source="main_button",
    ) == token
    assert claim_analysis_submission_request(session_state) is None


def test_scientific_replacement_cancels_the_current_submission():
    """Let a parameter-changing callback make the Run action available again."""
    session_state = {}
    begin_analysis_submission(session_state, request_source="main_button")

    assert cancel_analysis_submission(session_state)
    assert get_analysis_submission(session_state) is None
    assert claim_analysis_submission_request(session_state) is None


def test_main_submission_does_not_mutate_demo_identity():
    """Keep an unchanged loaded profile attached to the main Run request."""
    session_state = {"active_demo_profile": "vanhamel_rx_calibration"}

    begin_main_analysis_submission(session_state)
    request = claim_analysis_submission_request(session_state)

    assert request is not None
    assert request.source == "main_button"
    assert session_state["active_demo_profile"] == "vanhamel_rx_calibration"
