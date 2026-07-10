from concurrent.futures import ThreadPoolExecutor
import threading
import time

import pytest

from core.analysis_admission import (
    AnalysisAdmissionController,
    AnalysisQueueFull,
    AnalysisQueueTimeout,
)


def _controller(
    *,
    max_active=1,
    max_queued=2,
    wait_timeout_seconds=1.0,
    lease_timeout_seconds=5.0,
):
    return AnalysisAdmissionController(
        max_active=max_active,
        max_queued=max_queued,
        wait_timeout_seconds=wait_timeout_seconds,
        lease_timeout_seconds=lease_timeout_seconds,
        poll_interval_seconds=0.005,
    )


def _wait_for_counts(controller, expected, timeout=1.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if controller.counts() == expected:
            return
        time.sleep(0.005)
    assert controller.counts() == expected


def test_admission_is_fifo_and_never_exceeds_active_limit():
    controller = _controller()
    first = controller.acquire(owner="first")
    acquired_order = []
    release_second = threading.Event()

    def queued_worker(owner, release_event=None):
        with controller.acquire(owner=owner):
            acquired_order.append(owner)
            if release_event is not None:
                assert release_event.wait(timeout=1.0)

    with ThreadPoolExecutor(max_workers=2) as executor:
        second_future = executor.submit(queued_worker, "second", release_second)
        _wait_for_counts(controller, (1, 1))
        third_future = executor.submit(queued_worker, "third")
        _wait_for_counts(controller, (1, 2))

        first.release()
        _wait_for_counts(controller, (1, 1))
        assert acquired_order == ["second"]

        release_second.set()
        second_future.result(timeout=1.0)
        third_future.result(timeout=1.0)

    assert acquired_order == ["second", "third"]
    assert controller.counts() == (0, 0)


def test_bounded_queue_rejects_an_additional_request():
    controller = _controller(max_queued=1)
    active = controller.acquire(owner="active")
    queued_started = threading.Event()

    def queued_worker():
        with controller.acquire(
            owner="queued",
            on_wait=lambda _snapshot: queued_started.set(),
        ):
            return

    with ThreadPoolExecutor(max_workers=1) as executor:
        queued_future = executor.submit(queued_worker)
        assert queued_started.wait(timeout=1.0)
        with pytest.raises(AnalysisQueueFull):
            controller.acquire(owner="rejected")
        active.release()
        queued_future.result(timeout=1.0)

    assert controller.counts() == (0, 0)


def test_queue_timeout_removes_its_ticket():
    controller = _controller(max_queued=1, wait_timeout_seconds=0.03)
    active = controller.acquire(owner="active")

    with pytest.raises(AnalysisQueueTimeout):
        controller.acquire(owner="timed-out")

    assert controller.counts() == (1, 0)
    active.release()


def test_wait_callback_interruption_removes_its_ticket():
    controller = _controller(max_queued=1)
    active = controller.acquire(owner="active")

    def interrupt(_snapshot):
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        controller.acquire(owner="interrupted", on_wait=interrupt)

    assert controller.counts() == (1, 0)
    active.release()


def test_context_manager_releases_after_failure():
    controller = _controller()

    with pytest.raises(RuntimeError):
        with controller.acquire(owner="failing"):
            raise RuntimeError("analysis failed")

    assert controller.counts() == (0, 0)


def test_stale_active_lease_allows_the_next_request_to_progress():
    controller = _controller(
        wait_timeout_seconds=0.5,
        lease_timeout_seconds=0.03,
    )
    stale = controller.acquire(owner="stale")

    with controller.acquire(owner="replacement"):
        assert controller.counts() == (1, 0)

    assert stale.release() is False
    assert controller.counts() == (0, 0)


def test_touch_keeps_an_active_lease_registered():
    controller = _controller(lease_timeout_seconds=0.04)
    permit = controller.acquire(owner="heartbeat")

    time.sleep(0.025)
    assert permit.touch() is True
    time.sleep(0.025)
    assert controller.counts() == (1, 0)
    permit.release()

