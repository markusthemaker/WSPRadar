from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import threading
import time

import pytest

from config import WSPR_DATABASE_PROVIDERS
from core.analysis_admission import (
    AnalysisAdmissionController,
    AnalysisDuplicateRequest,
    AnalysisQueueFull,
    AnalysisQueueTimeout,
)
from core.provider_dispatch import ProviderDispatchController


class _ManualClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += float(seconds)


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


def test_identical_active_request_from_same_owner_is_rejected():
    controller = _controller(max_active=2)
    active = controller.acquire(owner="session-a", request_key="same-analysis")

    with pytest.raises(AnalysisDuplicateRequest):
        controller.acquire(owner="session-a", request_key="same-analysis")

    assert controller.counts() == (1, 0)
    active.release()


def test_identical_queued_request_from_same_owner_is_rejected():
    controller = _controller(max_active=1, max_queued=2)
    active = controller.acquire(owner="active", request_key="other-analysis")
    queued_started = threading.Event()

    def queued_worker():
        with controller.acquire(
            owner="session-a",
            request_key="same-analysis",
            on_wait=lambda _snapshot: queued_started.set(),
        ):
            return

    with ThreadPoolExecutor(max_workers=1) as executor:
        queued_future = executor.submit(queued_worker)
        assert queued_started.wait(timeout=1.0)
        with pytest.raises(AnalysisDuplicateRequest):
            controller.acquire(owner="session-a", request_key="same-analysis")
        assert controller.counts() == (1, 1)
        active.release()
        queued_future.result(timeout=1.0)

    assert controller.counts() == (0, 0)


def test_identical_demo_requests_from_different_sessions_are_independent():
    controller = _controller(max_active=2)
    first = controller.acquire(owner="session-a", request_key="demo-rx-europe")
    second = controller.acquire(owner="session-b", request_key="demo-rx-europe")

    assert controller.counts() == (2, 0)
    first.release()
    second.release()


def test_distinct_requests_from_same_session_are_not_deduplicated():
    controller = _controller(max_active=2)
    first = controller.acquire(owner="session-a", request_key="analysis-one")
    second = controller.acquire(owner="session-a", request_key="analysis-two")

    assert controller.counts() == (2, 0)
    first.release()
    second.release()


def test_request_can_run_again_after_its_prior_permit_is_released():
    controller = _controller()
    first = controller.acquire(owner="session-a", request_key="same-analysis")
    first.release()

    second = controller.acquire(owner="session-a", request_key="same-analysis")
    assert controller.counts() == (1, 0)
    second.release()


def test_external_capacity_waits_in_same_fifo_queue_without_using_active_slot():
    controller = _controller(max_active=1, max_queued=1)
    capacity_ready = threading.Event()
    capacity_released = threading.Event()
    waiting = threading.Event()

    class CapacityLease:
        def release(self):
            capacity_released.set()
            return True

    def reserve_capacity():
        return CapacityLease() if capacity_ready.is_set() else None

    def worker():
        with controller.acquire(
            owner="database-waiter",
            reserve_capacity=reserve_capacity,
            on_wait=lambda _snapshot: waiting.set(),
        ) as permit:
            assert permit.capacity_lease is not None
            assert controller.counts() == (1, 0)

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(worker)
        assert waiting.wait(timeout=1.0)
        assert controller.counts() == (0, 1)
        capacity_ready.set()
        future.result(timeout=1.0)

    assert capacity_released.is_set()
    assert controller.counts() == (0, 0)


def test_replacing_capacity_releases_old_and_final_leases_once():
    controller = _controller()
    releases = []

    class CapacityLease:
        def __init__(self, name):
            self.name = name
            self.released = False

        def release(self):
            if self.released:
                return False
            self.released = True
            releases.append(self.name)
            return True

    first_capacity = CapacityLease("first")
    permit = controller.acquire(
        owner="fallback-run",
        reserve_capacity=lambda: first_capacity,
    )
    second_capacity = CapacityLease("second")

    assert permit.replace_capacity_lease(second_capacity)
    assert releases == ["first"]
    permit.release()
    assert releases == ["first", "second"]


def test_stale_analysis_lease_releases_reserved_provider_capacity():
    clock = _ManualClock()
    provider = replace(WSPR_DATABASE_PROVIDERS[0], request_limit=4)
    provider_controller = ProviderDispatchController(
        (provider,),
        acquire_timeout_seconds=1.0,
        poll_interval_seconds=0.01,
        clock=clock,
    )
    admission_controller = AnalysisAdmissionController(
        max_active=1,
        max_queued=1,
        wait_timeout_seconds=10.0,
        lease_timeout_seconds=5.0,
        poll_interval_seconds=0.01,
        clock=clock,
    )
    permit = admission_controller.acquire(
        owner="stale-provider-run",
        reserve_capacity=lambda: provider_controller.try_acquire_run(
            {provider.key: 3}
        ),
    )
    assert provider_controller.snapshot(provider.key).reserved_requests == 3

    clock.advance(5.0)
    assert admission_controller.counts() == (0, 0)
    snapshot = provider_controller.snapshot(provider.key)
    assert snapshot.reserved_requests == 0
    assert snapshot.active_runs == 0
    assert permit.release() is False
