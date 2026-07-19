"""Process-local database selection, rolling budgets, and circuit state."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
import math
import threading
import time
from typing import Callable, Collection, Mapping

from config import (
    WSPR_DATABASE_PROVIDERS,
    WSPR_PROVIDER_ACQUIRE_POLL_INTERVAL_SEC,
    WSPR_PROVIDER_ACQUIRE_TIMEOUT_SEC,
    WsprDatabaseProviderConfig,
)
from core.fetch_models import DatabaseSource, FetchError, FetchFailureScope


class ProviderDispatchError(RuntimeError):
    """Base class for database-capacity and provider-selection failures."""


class NoProviderAvailable(ProviderDispatchError):
    """Raised when exclusions or configuration leave no usable provider."""


class ProviderAcquireTimeout(ProviderDispatchError):
    """Raised after bounded waiting cannot reserve a complete run."""


class ProviderRateLimitExceeded(ProviderDispatchError):
    """Raised when an unreserved request would exceed the local rolling budget."""


@dataclass(frozen=True)
class ProviderCapacitySnapshot:
    """Describe one wait for process-local upstream request capacity."""

    excluded_sources: tuple[str, ...]
    allowed_sources: tuple[str, ...]
    wait_seconds_remaining: float


@dataclass(frozen=True)
class ProviderStateSnapshot:
    """Expose immutable provider state for diagnostics and regression tests."""

    source_key: str
    requests_in_window: int
    reserved_requests: int
    active_runs: int
    consecutive_failures: int
    failure_generation: int
    recovery_generation: int
    circuit_open_seconds: float
    probe_in_flight: bool


@dataclass
class _ProviderState:
    request_started_at: deque[float] = field(default_factory=deque)
    reserved_requests: int = 0
    active_runs: int = 0
    consecutive_failures: int = 0
    failure_generation: int = 0
    recovery_generation: int = 0
    circuit_open_until: float = 0.0
    requires_probe: bool = False
    probe_in_flight: bool = False


class ProviderRunLease:
    """Reserve one provider for a complete analysis run.

    Reserved request slots become rolling-window timestamps only immediately
    before an actual HTTP attempt. Cache hits therefore consume no request
    budget, and unused reservations are returned when the lease is released.
    """

    def __init__(
        self,
        controller: "ProviderDispatchController",
        provider: WsprDatabaseProviderConfig,
        *,
        reserved_requests: int,
        is_probe: bool,
        skipped_sources: tuple[str, ...],
        failure_generation: int,
        recovery_generation: int,
    ) -> None:
        self._controller = controller
        self.provider = provider
        self.skipped_sources = skipped_sources
        self._remaining_reservations = int(reserved_requests)
        self._actual_requests = 0
        self._is_probe = bool(is_probe)
        self._failure_generation_at_acquire = int(failure_generation)
        self._recovery_generation_at_acquire = int(recovery_generation)
        self._released = False
        self._outcome_recorded = False

    @property
    def source_key(self) -> str:
        """Return the stable source identifier bound to this run."""
        return self.provider.key

    @property
    def actual_requests(self) -> int:
        """Return the number of HTTP attempts begun through this lease."""
        return self._actual_requests

    def consume_request(self) -> None:
        """Consume one request slot immediately before an HTTP attempt."""
        self._controller._consume_request(self)

    def report_success(self) -> None:
        """Close circuit state after a complete successful provider bundle."""
        if self._outcome_recorded:
            return
        self._outcome_recorded = True
        self._controller._record_success(self)

    def report_failure(self, error: FetchError) -> None:
        """Record one classified provider failure and open its circuit if needed."""
        if self._outcome_recorded:
            return
        self._outcome_recorded = True
        self._controller._record_failure(self, error)

    def release(self) -> bool:
        """Return unused reservations and release probe/run ownership once."""
        if self._released:
            return False
        self._released = True
        self._controller._release_lease(self)
        return True

    def __enter__(self) -> "ProviderRunLease":
        return self

    def __exit__(self, _exc_type, _exc_value, _traceback) -> None:
        self.release()


class ProviderDispatchController:
    """Select providers atomically using priority, budgets, and circuit state."""

    def __init__(
        self,
        providers: Collection[WsprDatabaseProviderConfig],
        *,
        acquire_timeout_seconds: float,
        poll_interval_seconds: float,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.providers = tuple(providers)
        if not self.providers:
            raise ValueError("At least one WSPR database provider is required")
        provider_keys = [provider.key for provider in self.providers]
        if len(provider_keys) != len(set(provider_keys)):
            raise ValueError("WSPR database provider keys must be unique")
        for provider in self.providers:
            if not all(
                isinstance(field_value, str) and field_value.strip()
                for field_value in (
                    provider.key,
                    provider.display_name,
                    provider.url,
                )
            ):
                raise ValueError("Provider key, display name, and URL are required")
            try:
                DatabaseSource(provider.key)
            except ValueError as exc:
                raise ValueError(
                    f"Unsupported WSPR database provider '{provider.key}'"
                ) from exc
            if not isinstance(provider.enabled, bool):
                raise TypeError("Provider enabled flags must be boolean")
            if type(provider.request_limit) is not int or provider.request_limit < 1:
                raise ValueError("Provider request limits must be positive")
            if not self._is_positive_finite_number(provider.request_window_seconds):
                raise ValueError("Provider request windows must be positive")
            if (
                type(provider.circuit_failure_threshold) is not int
                or provider.circuit_failure_threshold < 1
            ):
                raise ValueError("Provider circuit thresholds must be positive")
            if not self._is_positive_finite_number(
                provider.rate_limit_cooldown_seconds
            ):
                raise ValueError("Provider rate-limit cooldowns must be positive")
            if not self._is_positive_finite_number(provider.failure_cooldown_seconds):
                raise ValueError("Provider failure cooldowns must be positive")
        if not self._is_positive_finite_number(acquire_timeout_seconds):
            raise ValueError("Provider acquire timeout must be positive")
        if not self._is_positive_finite_number(poll_interval_seconds):
            raise ValueError("Provider poll interval must be positive")

        self.acquire_timeout_seconds = float(acquire_timeout_seconds)
        self.poll_interval_seconds = float(poll_interval_seconds)
        self._clock = clock
        self._condition = threading.Condition(threading.RLock())
        self._states = {
            provider.key: _ProviderState()
            for provider in self.providers
        }

    @staticmethod
    def _is_positive_finite_number(value) -> bool:
        """Return whether a configured duration is a finite positive scalar."""
        return (
            not isinstance(value, bool)
            and isinstance(value, (int, float))
            and math.isfinite(float(value))
            and float(value) > 0.0
        )

    def provider(self, source_key: str) -> WsprDatabaseProviderConfig:
        """Return one configured provider by stable key."""
        for provider in self.providers:
            if provider.key == source_key:
                return provider
        raise KeyError(f"Unknown WSPR database provider '{source_key}'")

    def _purge_request_window_unlocked(
        self,
        provider: WsprDatabaseProviderConfig,
        now: float,
    ) -> None:
        state = self._states[provider.key]
        cutoff = now - float(provider.request_window_seconds)
        while state.request_started_at and state.request_started_at[0] <= cutoff:
            state.request_started_at.popleft()

    @staticmethod
    def _normalized_source_filter(source_keys: Collection[str] | None) -> frozenset[str] | None:
        if source_keys is None:
            return None
        return frozenset(str(source_key) for source_key in source_keys)

    def _candidate_providers(
        self,
        *,
        excluded_sources: frozenset[str],
        allowed_sources: frozenset[str] | None,
    ) -> tuple[WsprDatabaseProviderConfig, ...]:
        return tuple(
            provider
            for provider in self.providers
            if provider.enabled
            and provider.key not in excluded_sources
            and (allowed_sources is None or provider.key in allowed_sources)
        )

    def try_acquire_run(
        self,
        required_requests_by_provider: Mapping[str, int],
        *,
        excluded_sources: Collection[str] = (),
        allowed_sources: Collection[str] | None = None,
    ) -> ProviderRunLease | None:
        """Atomically reserve the first eligible provider, or return ``None``.

        ``required_requests_by_provider`` is a conservative maximum for the
        complete strict/legacy analysis bundle after source-specific cache
        inspection. A value of zero permits cache-only reuse even while that
        provider's network circuit is cooling down.
        """
        excluded = frozenset(str(source) for source in excluded_sources)
        allowed = self._normalized_source_filter(allowed_sources)
        candidates = self._candidate_providers(
            excluded_sources=excluded,
            allowed_sources=allowed,
        )
        if not candidates:
            raise NoProviderAvailable("No untried WSPR database provider remains")

        permanently_oversized = True
        skipped_sources: list[str] = []
        with self._condition:
            now = self._clock()
            for provider in candidates:
                required_requests = int(required_requests_by_provider.get(provider.key, 0))
                if required_requests < 0:
                    raise ValueError("Required provider requests cannot be negative")
                if required_requests > provider.request_limit:
                    skipped_sources.append(provider.key)
                    continue
                permanently_oversized = False

                state = self._states[provider.key]
                self._purge_request_window_unlocked(provider, now)
                is_cache_only = required_requests == 0
                circuit_is_open = state.circuit_open_until > now
                probe_is_required = state.requires_probe and not circuit_is_open
                if not is_cache_only and (
                    circuit_is_open or (probe_is_required and state.probe_in_flight)
                ):
                    skipped_sources.append(provider.key)
                    continue

                occupied_requests = (
                    len(state.request_started_at) + state.reserved_requests
                )
                if occupied_requests + required_requests > provider.request_limit:
                    skipped_sources.append(provider.key)
                    continue

                is_probe = bool(not is_cache_only and probe_is_required)
                state.reserved_requests += required_requests
                state.active_runs += 1
                if is_probe:
                    state.probe_in_flight = True
                return ProviderRunLease(
                    self,
                    provider,
                    reserved_requests=required_requests,
                    is_probe=is_probe,
                    skipped_sources=tuple(skipped_sources),
                    failure_generation=state.failure_generation,
                    recovery_generation=state.recovery_generation,
                )

        if permanently_oversized:
            raise NoProviderAvailable(
                "One analysis run requires more requests than every eligible provider permits"
            )
        return None

    def acquire_run(
        self,
        required_requests_by_provider: (
            Mapping[str, int] | Callable[[], Mapping[str, int]]
        ),
        *,
        excluded_sources: Collection[str] = (),
        allowed_sources: Collection[str] | None = None,
        on_wait: Callable[[ProviderCapacitySnapshot], None] | None = None,
    ) -> ProviderRunLease:
        """Wait for a provider reservation within the configured deadline.

        A callable request plan is reevaluated on every poll so cache changes
        can make a waiting run eligible without consuming network capacity.
        """
        deadline = self._clock() + self.acquire_timeout_seconds
        excluded = tuple(sorted(str(source) for source in excluded_sources))
        allowed = (
            tuple(sorted(str(source) for source in allowed_sources))
            if allowed_sources is not None
            else tuple(provider.key for provider in self.providers if provider.enabled)
        )
        last_snapshot = None

        while True:
            current_required_requests = (
                required_requests_by_provider()
                if callable(required_requests_by_provider)
                else required_requests_by_provider
            )
            lease = self.try_acquire_run(
                current_required_requests,
                excluded_sources=excluded,
                allowed_sources=allowed,
            )
            if lease is not None:
                return lease

            now = self._clock()
            remaining = deadline - now
            if remaining <= 0:
                raise ProviderAcquireTimeout(
                    "Timed out waiting for WSPR database request capacity"
                )
            snapshot = ProviderCapacitySnapshot(
                excluded_sources=excluded,
                allowed_sources=allowed,
                wait_seconds_remaining=max(remaining, 0.0),
            )
            if on_wait is not None and snapshot != last_snapshot:
                on_wait(snapshot)
                last_snapshot = snapshot
            with self._condition:
                self._condition.wait(
                    timeout=min(self.poll_interval_seconds, max(remaining, 0.0))
                )

    def _consume_request(self, lease: ProviderRunLease) -> None:
        """Convert one reservation into an actual rolling-window request."""
        with self._condition:
            if lease._released:
                raise RuntimeError("Cannot use a released provider lease")
            provider = lease.provider
            state = self._states[provider.key]
            now = self._clock()
            self._purge_request_window_unlocked(provider, now)

            if lease._remaining_reservations <= 0:
                raise ProviderRateLimitExceeded(
                    f"No reserved request capacity remains for {provider.display_name}"
                )
            has_newer_failure = (
                state.failure_generation > lease._failure_generation_at_acquire
            )
            has_newer_recovery = (
                state.recovery_generation > lease._recovery_generation_at_acquire
            )
            if has_newer_recovery:
                raise ProviderRateLimitExceeded(
                    f"{provider.display_name} health changed after this run was admitted"
                )
            if has_newer_failure and (
                state.circuit_open_until > now or state.requires_probe
            ):
                raise ProviderRateLimitExceeded(
                    f"{provider.display_name} became unavailable after this run was admitted"
                )

            lease._remaining_reservations -= 1
            state.reserved_requests -= 1
            state.request_started_at.append(now)
            lease._actual_requests += 1
            self._condition.notify_all()

    def _record_success(self, lease: ProviderRunLease) -> None:
        """Close provider circuit state after a network-backed bundle succeeds."""
        if lease.actual_requests == 0:
            return
        with self._condition:
            state = self._states[lease.provider.key]
            if lease._is_probe:
                state.probe_in_flight = False
            if state.failure_generation != lease._failure_generation_at_acquire:
                self._condition.notify_all()
                return
            if state.consecutive_failures or state.requires_probe:
                state.recovery_generation += 1
            state.consecutive_failures = 0
            state.circuit_open_until = 0.0
            state.requires_probe = False
            self._condition.notify_all()

    def _record_failure(self, lease: ProviderRunLease, error: FetchError) -> None:
        """Open or advance circuit state for a classified provider failure."""
        if error.scope != FetchFailureScope.PROVIDER:
            return
        with self._condition:
            provider = lease.provider
            state = self._states[provider.key]
            if (
                state.recovery_generation
                != lease._recovery_generation_at_acquire
            ):
                if lease._is_probe:
                    state.probe_in_flight = False
                self._condition.notify_all()
                return
            state.consecutive_failures += 1
            state.failure_generation += 1
            now = self._clock()
            should_open = (
                error.status_code == 429
                or error.retry_after_seconds is not None
                or state.consecutive_failures >= provider.circuit_failure_threshold
            )
            if should_open:
                if error.retry_after_seconds is not None:
                    cooldown_seconds = float(error.retry_after_seconds)
                elif error.status_code == 429:
                    cooldown_seconds = (
                        float(provider.rate_limit_cooldown_seconds)
                    )
                else:
                    cooldown_seconds = float(provider.failure_cooldown_seconds)
                state.circuit_open_until = max(
                    state.circuit_open_until,
                    now + max(cooldown_seconds, 0.0),
                )
                state.requires_probe = True
            if lease._is_probe:
                state.probe_in_flight = False
            self._condition.notify_all()

    def _release_lease(self, lease: ProviderRunLease) -> None:
        """Release unused reservations and active/probe ownership."""
        with self._condition:
            state = self._states[lease.provider.key]
            state.reserved_requests = max(
                0,
                state.reserved_requests - lease._remaining_reservations,
            )
            lease._remaining_reservations = 0
            state.active_runs = max(0, state.active_runs - 1)
            if lease._is_probe:
                state.probe_in_flight = False
            self._condition.notify_all()

    def snapshot(self, source_key: str) -> ProviderStateSnapshot:
        """Return current rolling-budget and circuit state for one provider."""
        provider = self.provider(source_key)
        with self._condition:
            now = self._clock()
            self._purge_request_window_unlocked(provider, now)
            state = self._states[source_key]
            return ProviderStateSnapshot(
                source_key=source_key,
                requests_in_window=len(state.request_started_at),
                reserved_requests=state.reserved_requests,
                active_runs=state.active_runs,
                consecutive_failures=state.consecutive_failures,
                failure_generation=state.failure_generation,
                recovery_generation=state.recovery_generation,
                circuit_open_seconds=max(state.circuit_open_until - now, 0.0),
                probe_in_flight=state.probe_in_flight,
            )


UPSTREAM_PROVIDER_DISPATCH = ProviderDispatchController(
    WSPR_DATABASE_PROVIDERS,
    acquire_timeout_seconds=WSPR_PROVIDER_ACQUIRE_TIMEOUT_SEC,
    poll_interval_seconds=WSPR_PROVIDER_ACQUIRE_POLL_INTERVAL_SEC,
)
