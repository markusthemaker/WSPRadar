"""FIFO admission control for resource-intensive analysis runs."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import threading
import time
from typing import Callable
import uuid

from config import (
    ANALYSIS_ACTIVE_LEASE_TIMEOUT_SEC,
    ANALYSIS_MAX_CONCURRENT,
    ANALYSIS_MAX_QUEUED,
    ANALYSIS_QUEUE_POLL_INTERVAL_SEC,
    ANALYSIS_QUEUE_WAIT_TIMEOUT_SEC,
)


class AnalysisAdmissionError(RuntimeError):
    """Base class for admission failures that can be shown at the UI boundary."""


class AnalysisQueueFull(AnalysisAdmissionError):
    """Raised when the bounded waiting queue has no free position."""


class AnalysisQueueTimeout(AnalysisAdmissionError):
    """Raised when a queued request does not acquire capacity in time."""


class AnalysisDuplicateRequest(AnalysisAdmissionError):
    """Raised when one owner already has the same request active or queued."""


@dataclass(frozen=True)
class AdmissionSnapshot:
    """One immutable view of active and queued analysis capacity."""

    position: int
    active: int
    queued: int
    max_active: int
    max_queued: int


@dataclass
class _ActiveLease:
    owner: str
    request_key: str | None
    touched_at: float


@dataclass(frozen=True)
class _QueueTicket:
    token: str
    owner: str
    request_key: str | None
    deadline: float


class AnalysisPermit:
    """One active analysis lease released automatically by a context manager."""

    def __init__(self, controller: "AnalysisAdmissionController", token: str) -> None:
        self._controller = controller
        self._token = token
        self._released = False

    def touch(self) -> bool:
        """Refresh this permit's active lease when it is still registered."""
        if self._released:
            return False
        return self._controller.touch(self._token)

    def release(self) -> bool:
        """Release this permit once and wake the next queued request."""
        if self._released:
            return False
        self._released = True
        return self._controller.release(self._token)

    def __enter__(self) -> "AnalysisPermit":
        return self

    def __exit__(self, _exc_type, _exc_value, _traceback) -> None:
        self.release()


class AnalysisAdmissionController:
    """Bound active analyses and admit queued requests in FIFO order."""

    def __init__(
        self,
        *,
        max_active: int,
        max_queued: int,
        wait_timeout_seconds: float,
        lease_timeout_seconds: float,
        poll_interval_seconds: float,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if int(max_active) < 1:
            raise ValueError("max_active must be at least 1")
        if int(max_queued) < 0:
            raise ValueError("max_queued cannot be negative")
        if float(wait_timeout_seconds) <= 0:
            raise ValueError("wait_timeout_seconds must be positive")
        if float(lease_timeout_seconds) <= 0:
            raise ValueError("lease_timeout_seconds must be positive")
        if float(poll_interval_seconds) <= 0:
            raise ValueError("poll_interval_seconds must be positive")

        self.max_active = int(max_active)
        self.max_queued = int(max_queued)
        self.wait_timeout_seconds = float(wait_timeout_seconds)
        self.lease_timeout_seconds = float(lease_timeout_seconds)
        self.poll_interval_seconds = float(poll_interval_seconds)
        self._clock = clock
        self._condition = threading.Condition(threading.Lock())
        self._active: dict[str, _ActiveLease] = {}
        self._queue: deque[_QueueTicket] = deque()

    def _expire_stale_leases_unlocked(self, now: float) -> int:
        stale_tokens = [
            token
            for token, lease in self._active.items()
            if now - lease.touched_at >= self.lease_timeout_seconds
        ]
        for token in stale_tokens:
            self._active.pop(token, None)
        if stale_tokens:
            self._condition.notify_all()
        return len(stale_tokens)

    def _remove_ticket_unlocked(self, token: str) -> bool:
        for ticket in self._queue:
            if ticket.token == token:
                self._queue.remove(ticket)
                self._condition.notify_all()
                return True
        return False

    def _has_duplicate_unlocked(self, owner: str, request_key: str | None) -> bool:
        if request_key is None:
            return False
        return any(
            lease.owner == owner and lease.request_key == request_key
            for lease in self._active.values()
        ) or any(
            ticket.owner == owner and ticket.request_key == request_key
            for ticket in self._queue
        )

    def _snapshot_unlocked(self, token: str) -> AdmissionSnapshot:
        position = next(
            (index for index, ticket in enumerate(self._queue, start=1) if ticket.token == token),
            0,
        )
        return AdmissionSnapshot(
            position=position,
            active=len(self._active),
            queued=len(self._queue),
            max_active=self.max_active,
            max_queued=self.max_queued,
        )

    def acquire(
        self,
        *,
        owner: str,
        request_key: str | None = None,
        on_wait: Callable[[AdmissionSnapshot], None] | None = None,
    ) -> AnalysisPermit:
        """Acquire an active slot immediately or wait in the bounded FIFO queue."""
        token = uuid.uuid4().hex
        owner = str(owner)
        request_key = str(request_key) if request_key is not None else None
        now = self._clock()
        deadline = now + self.wait_timeout_seconds

        with self._condition:
            self._expire_stale_leases_unlocked(now)
            if self._has_duplicate_unlocked(owner, request_key):
                raise AnalysisDuplicateRequest(
                    "The same owner already has this request active or queued"
                )
            if len(self._active) < self.max_active and not self._queue:
                self._active[token] = _ActiveLease(
                    owner=owner,
                    request_key=request_key,
                    touched_at=now,
                )
                return AnalysisPermit(self, token)
            if len(self._queue) >= self.max_queued:
                raise AnalysisQueueFull("The analysis waiting queue is full")
            self._queue.append(_QueueTicket(
                token=token,
                owner=owner,
                request_key=request_key,
                deadline=deadline,
            ))
            self._condition.notify_all()

        last_snapshot = None
        try:
            while True:
                with self._condition:
                    now = self._clock()
                    self._expire_stale_leases_unlocked(now)
                    is_first = bool(self._queue and self._queue[0].token == token)
                    if is_first and len(self._active) < self.max_active:
                        self._queue.popleft()
                        self._active[token] = _ActiveLease(
                            owner=owner,
                            request_key=request_key,
                            touched_at=now,
                        )
                        self._condition.notify_all()
                        return AnalysisPermit(self, token)
                    if now >= deadline:
                        self._remove_ticket_unlocked(token)
                        raise AnalysisQueueTimeout("Timed out waiting for analysis capacity")
                    snapshot = self._snapshot_unlocked(token)
                    wait_seconds = min(self.poll_interval_seconds, max(deadline - now, 0.0))

                if on_wait is not None and snapshot != last_snapshot:
                    on_wait(snapshot)
                    last_snapshot = snapshot

                with self._condition:
                    self._condition.wait(timeout=wait_seconds)
        except BaseException:
            with self._condition:
                self._remove_ticket_unlocked(token)
            raise

    def touch(self, token: str) -> bool:
        """Refresh one active lease without changing queue order."""
        with self._condition:
            lease = self._active.get(token)
            if lease is None:
                return False
            lease.touched_at = self._clock()
            return True

    def release(self, token: str) -> bool:
        """Release one active lease or remove one abandoned queue ticket."""
        with self._condition:
            removed = self._active.pop(token, None) is not None
            removed = self._remove_ticket_unlocked(token) or removed
            if removed:
                self._condition.notify_all()
            return removed

    def counts(self) -> tuple[int, int]:
        """Return current active and queued counts for diagnostics and tests."""
        with self._condition:
            self._expire_stale_leases_unlocked(self._clock())
            return len(self._active), len(self._queue)


ANALYSIS_ADMISSION_GATE = AnalysisAdmissionController(
    max_active=ANALYSIS_MAX_CONCURRENT,
    max_queued=ANALYSIS_MAX_QUEUED,
    wait_timeout_seconds=ANALYSIS_QUEUE_WAIT_TIMEOUT_SEC,
    lease_timeout_seconds=ANALYSIS_ACTIVE_LEASE_TIMEOUT_SEC,
    poll_interval_seconds=ANALYSIS_QUEUE_POLL_INTERVAL_SEC,
)
