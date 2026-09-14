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
    AdmissionSnapshot,
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


def test_request_snapshot_reports_active_request_and_clears_after_release():
    controller = _controller()
    permit = controller.acquire(owner="session-a", request_key="same-analysis")

    assert controller.request_snapshot("session-a", "same-analysis") == AdmissionSnapshot(
        position=0,
        active=1,
        queued=0,
        max_active=1,
        max_queued=2,
    )
    assert controller.request_snapshot("session-a", "unknown-analysis") is None

    permit.release()

    assert controller.request_snapshot("session-a", "same-analysis") is None


def test_request_snapshot_tracks_queued_request_through_admission_and_release():
    controller = _controller(max_active=1, max_queued=2)
    active = controller.acquire(owner="active-session", request_key="active-analysis")
    queued_started = threading.Event()
    queued_admitted = threading.Event()
    release_queued = threading.Event()

    def queued_worker():
        with controller.acquire(
            owner="queued-session",
            request_key="queued-analysis",
            on_wait=lambda _snapshot: queued_started.set(),
        ):
            queued_admitted.set()
            assert release_queued.wait(timeout=1.0)

    with ThreadPoolExecutor(max_workers=1) as executor:
        queued_future = executor.submit(queued_worker)
        assert queued_started.wait(timeout=1.0)
        assert controller.request_snapshot(
            "queued-session",
            "queued-analysis",
        ) == AdmissionSnapshot(
            position=1,
            active=1,
            queued=1,
            max_active=1,
            max_queued=2,
        )

        active.release()
        assert queued_admitted.wait(timeout=1.0)
        assert controller.request_snapshot(
            "queued-session",
            "queued-analysis",
        ) == AdmissionSnapshot(
            position=0,
            active=1,
            queued=0,
            max_active=1,
            max_queued=2,
        )

        release_queued.set()
        queued_future.result(timeout=1.0)

    assert controller.request_snapshot("queued-session", "queued-analysis") is None


def test_duplicate_follower_waits_until_the_original_request_is_released():
    controller = _controller(max_active=1, max_queued=1)
    active = controller.acquire(owner="session-a", request_key="same-analysis")
    first_update = threading.Event()
    observed_snapshots = []

    def record_snapshot(snapshot):
        observed_snapshots.append(snapshot)
        first_update.set()

    def follow_original_request():
        controller.wait_for_request_completion(
            "session-a",
            "same-analysis",
            on_update=record_snapshot,
        )

    with ThreadPoolExecutor(max_workers=1) as executor:
        follower = executor.submit(follow_original_request)
        assert first_update.wait(timeout=1.0)
        assert not follower.done()

        active.release()
        follower.result(timeout=1.0)

    assert observed_snapshots[0].position == 0
    assert controller.request_snapshot("session-a", "same-analysis") is None


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


class _CountedCapacity:
    def __init__(self):
        self.release_count = 0

    def release(self):
        self.release_count += 1
        return self.release_count == 1


@pytest.mark.parametrize("initially_queued", [False, True])
def test_cache_preparation_does_not_block_permit_lifecycle_or_status(initially_queued):
    controller = _controller(max_active=2, wait_timeout_seconds=5.0)
    active = controller.acquire(owner="active", request_key="active-request")
    blocker = controller.acquire(owner="blocker") if initially_queued else None
    preparation_started = threading.Event()
    finish_preparation = threading.Event()
    capacity = _CountedCapacity()

    def prepare():
        preparation_started.set()
        assert finish_preparation.wait(timeout=5.0)

    def probe_active_lifecycle():
        assert active.touch()
        assert controller.counts()[0] == 1
        assert controller.request_snapshot("active", "active-request").position == 0
        assert active.release()
        assert controller.counts()[0] == 0

    with ThreadPoolExecutor(max_workers=2) as executor:
        candidate = executor.submit(
            controller.acquire,
            owner="candidate",
            prepare_capacity=prepare,
            reserve_capacity=lambda: capacity,
        )
        try:
            if blocker is not None:
                _wait_for_counts(controller, (2, 1))
                blocker.release()
            assert preparation_started.wait(timeout=1.0)
            # A failed assertion still unblocks the cache operation below, so a
            # regression cannot leave executor shutdown waiting indefinitely.
            executor.submit(probe_active_lifecycle).result(timeout=1.0)
        finally:
            finish_preparation.set()
            active.release()
            if blocker is not None:
                blocker.release()
        permit = candidate.result(timeout=1.0)
        permit.release()

    assert capacity.release_count == 1
    assert controller.counts() == (0, 0)


def test_initial_cache_preparation_keeps_admission_order_with_no_waiting_queue():
    controller = _controller(max_active=2, max_queued=0, wait_timeout_seconds=5.0)
    preparation_started = threading.Event()
    finish_preparation = threading.Event()
    follower_started = threading.Event()
    follower_reserved = threading.Event()
    reservations = []
    capacities = [_CountedCapacity(), _CountedCapacity()]

    def prepare():
        preparation_started.set()
        assert finish_preparation.wait(timeout=5.0)

    def reserve(index):
        reservations.append(index)
        if index == 1:
            follower_reserved.set()
        return capacities[index]

    def acquire_follower():
        follower_started.set()
        return controller.acquire(owner="second", reserve_capacity=lambda: reserve(1))

    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(
            controller.acquire,
            owner="first",
            prepare_capacity=prepare,
            reserve_capacity=lambda: reserve(0),
        )
        try:
            assert preparation_started.wait(timeout=1.0)
            second = executor.submit(acquire_follower)
            assert follower_started.wait(timeout=1.0)
            assert controller.counts() == (0, 0)
            assert not follower_reserved.wait(timeout=0.05)
        finally:
            finish_preparation.set()
        first_permit = first.result(timeout=1.0)
        second_permit = second.result(timeout=1.0)
        assert reservations == [0, 1]
        assert controller.counts() == (2, 0)
        first_permit.release()
        second_permit.release()

    assert [capacity.release_count for capacity in capacities] == [1, 1]


def test_preparing_queue_head_cannot_be_overtaken_or_reserve_follower_capacity():
    controller = _controller(max_queued=2, wait_timeout_seconds=5.0)
    active = controller.acquire(owner="active")
    preparation_started = threading.Event()
    finish_preparation = threading.Event()
    follower_reserved = threading.Event()
    first_capacity = _CountedCapacity()
    follower_capacity = _CountedCapacity()

    def prepare():
        preparation_started.set()
        assert finish_preparation.wait(timeout=5.0)

    def reserve_follower():
        follower_reserved.set()
        return follower_capacity

    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(
            controller.acquire,
            owner="first", request_key="first-request",
            prepare_capacity=prepare,
            reserve_capacity=lambda: first_capacity,
        )
        try:
            _wait_for_counts(controller, (1, 1))
            follower = executor.submit(
                controller.acquire, owner="follower", reserve_capacity=reserve_follower,
            )
            _wait_for_counts(controller, (1, 2))
            active.release()
            assert preparation_started.wait(timeout=1.0)
            assert controller.counts() == (0, 2)
            assert controller.request_snapshot("first", "first-request").position == 1
            assert not follower_reserved.is_set()
        finally:
            finish_preparation.set()
            active.release()
        first_permit = first.result(timeout=1.0)
        assert controller.counts() == (1, 1)
        assert not follower_reserved.is_set()
        first_permit.release()
        follower_permit = follower.result(timeout=1.0)
        follower_permit.release()

    assert first_capacity.release_count == follower_capacity.release_count == 1
    assert controller.counts() == (0, 0)


@pytest.mark.parametrize("initially_queued", [False, True])
@pytest.mark.parametrize("error_type", [RuntimeError, KeyboardInterrupt])
def test_preparation_failure_cleans_up_and_allows_another_request(initially_queued, error_type):
    controller = _controller(wait_timeout_seconds=5.0)
    active = controller.acquire(owner="active") if initially_queued else None
    reservations = []

    def prepare():
        raise error_type("interrupted preparation")

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(
            controller.acquire,
            owner="failed", request_key="request",
            prepare_capacity=prepare,
            reserve_capacity=lambda: reservations.append("unexpected"),
        )
        try:
            if active is not None:
                _wait_for_counts(controller, (1, 1))
                active.release()
            with pytest.raises(error_type, match="interrupted preparation"):
                future.result(timeout=1.0)
        finally:
            if active is not None:
                active.release()

    assert reservations == []
    assert controller.counts() == (0, 0)
    with controller.acquire(owner="failed", request_key="request"):
        assert controller.counts() == (1, 0)


@pytest.mark.parametrize("initially_queued", [False, True])
def test_expired_preparation_never_reserves_capacity(initially_queued):
    clock = _ManualClock()
    controller = AnalysisAdmissionController(
        max_active=1, max_queued=1, wait_timeout_seconds=1.0,
        lease_timeout_seconds=10.0, poll_interval_seconds=0.005, clock=clock,
    )
    active = controller.acquire(owner="active") if initially_queued else None
    preparation_started = threading.Event()
    finish_preparation = threading.Event()
    reservations = []

    def prepare():
        preparation_started.set()
        assert finish_preparation.wait(timeout=5.0)

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(
            controller.acquire,
            owner="expired", request_key="request",
            prepare_capacity=prepare,
            reserve_capacity=lambda: reservations.append("unexpected"),
        )
        try:
            if active is not None:
                _wait_for_counts(controller, (1, 1))
                active.release()
            assert preparation_started.wait(timeout=1.0)
            clock.advance(1.0)
            # Snapshot cleanup may remove a queued head during its cache read.
            assert controller.request_snapshot("expired", "request") is None
        finally:
            finish_preparation.set()
            if active is not None:
                active.release()
        with pytest.raises(AnalysisQueueTimeout):
            future.result(timeout=1.0)

    assert reservations == []
    assert controller.counts() == (0, 0)


def test_preparation_requires_an_atomic_reservation_callback():
    with pytest.raises(ValueError, match="requires reserve_capacity"):
        _controller().acquire(owner="invalid", prepare_capacity=lambda: None)


def test_prepared_unavailable_capacity_respects_zero_queue_limit():
    controller = _controller(max_queued=0)
    with pytest.raises(AnalysisQueueFull):
        controller.acquire(
            owner="unavailable", prepare_capacity=lambda: None,
            reserve_capacity=lambda: None,
        )
    assert controller.counts() == (0, 0)


def test_expired_initial_request_skips_cache_preparation_after_waiting_for_attempt():
    waiter_clock_read = threading.Event()

    class SignalingClock(_ManualClock):
        signal_waiter = False

        def __call__(self):
            current = super().__call__()
            if self.signal_waiter:
                waiter_clock_read.set()
            return current

    clock = SignalingClock()
    controller = AnalysisAdmissionController(
        max_active=2, max_queued=0, wait_timeout_seconds=1.0,
        lease_timeout_seconds=10.0, poll_interval_seconds=0.005, clock=clock,
    )
    preparation_started = threading.Event()
    finish_preparation = threading.Event()
    unexpected_operations = []

    def prepare_first():
        preparation_started.set()
        assert finish_preparation.wait(timeout=5.0)

    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(
            controller.acquire, owner="first", prepare_capacity=prepare_first,
            reserve_capacity=lambda: unexpected_operations.append("first reservation"),
        )
        try:
            assert preparation_started.wait(timeout=1.0)
            clock.signal_waiter = True
            waiter = executor.submit(
                controller.acquire,
                owner="waiter",
                prepare_capacity=lambda: unexpected_operations.append("late cache read"),
                reserve_capacity=lambda: unexpected_operations.append("late reservation"),
            )
            assert waiter_clock_read.wait(timeout=1.0)
            clock.advance(1.0)
        finally:
            finish_preparation.set()
        for future in (first, waiter):
            with pytest.raises(AnalysisQueueTimeout):
                future.result(timeout=1.0)

    assert unexpected_operations == []
    assert controller.counts() == (0, 0)
