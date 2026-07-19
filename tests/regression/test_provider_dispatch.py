from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import threading

import pytest

from config import WSPR_DATABASE_PROVIDERS
from core.fetch_models import FetchError, FetchFailureScope
from core.provider_dispatch import (
    NoProviderAvailable,
    ProviderDispatchController,
    ProviderRateLimitExceeded,
    ProviderSkipReason,
)


class _Clock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += float(seconds)


def _controller(clock, *, request_limit=4, failure_threshold=1):
    providers = tuple(
        replace(
            provider,
            request_limit=request_limit,
            request_window_seconds=60.0,
            circuit_failure_threshold=failure_threshold,
            rate_limit_cooldown_seconds=30.0,
            failure_cooldown_seconds=10.0,
        )
        for provider in WSPR_DATABASE_PROVIDERS
    )
    return ProviderDispatchController(
        providers,
        acquire_timeout_seconds=1.0,
        poll_interval_seconds=0.01,
        clock=clock,
    )


def test_provider_skip_reason_values_are_stable_for_telemetry():
    """Keep provider-selection diagnostics machine-readable across releases."""
    assert tuple(reason.value for reason in ProviderSkipReason) == (
        "request_plan_exceeds_provider_limit",
        "circuit_open",
        "recovery_probe_in_flight",
        "rolling_request_capacity_unavailable",
    )


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "expected_exception"),
    (
        ("enabled", 1, TypeError),
        ("key", "unknown", ValueError),
        ("request_limit", "20", ValueError),
        ("request_limit", True, ValueError),
        ("request_window_seconds", float("nan"), ValueError),
        ("circuit_failure_threshold", 1.0, ValueError),
        ("rate_limit_cooldown_seconds", float("inf"), ValueError),
    ),
)
def test_invalid_provider_policy_types_fail_during_controller_construction(
    field_name,
    invalid_value,
    expected_exception,
):
    """Reject malformed app policy before the first live reservation attempt."""
    provider = replace(
        WSPR_DATABASE_PROVIDERS[0],
        **{field_name: invalid_value},
    )

    with pytest.raises(expected_exception):
        ProviderDispatchController(
            (provider,),
            acquire_timeout_seconds=1.0,
            poll_interval_seconds=0.01,
        )


def test_dispatch_uses_configured_priority_and_releases_unused_reservations():
    clock = _Clock()
    controller = _controller(clock)

    lease = controller.try_acquire_run({"wspr_live": 3, "wd2": 3, "wd1": 3})

    assert lease.source_key == "wspr_live"
    assert controller.snapshot("wspr_live").reserved_requests == 3
    lease.consume_request()
    lease.report_success()
    lease.release()

    snapshot = controller.snapshot("wspr_live")
    assert snapshot.requests_in_window == 1
    assert snapshot.reserved_requests == 0
    assert snapshot.active_runs == 0


def test_rolling_budget_skips_primary_then_returns_after_window_expiry():
    clock = _Clock()
    controller = _controller(clock, request_limit=2)
    first = controller.try_acquire_run({"wspr_live": 2, "wd2": 2, "wd1": 2})
    first.consume_request()
    first.consume_request()
    first.report_success()
    first.release()

    fallback = controller.try_acquire_run(
        {"wspr_live": 1, "wd2": 1, "wd1": 1}
    )
    assert fallback.source_key == "wd2"
    assert fallback.skipped_sources == ("wspr_live",)
    assert fallback.skipped_source_reasons == (
        (
            "wspr_live",
            ProviderSkipReason.ROLLING_REQUEST_CAPACITY_UNAVAILABLE,
        ),
    )
    fallback.release()

    clock.advance(60.0)
    primary_again = controller.try_acquire_run(
        {"wspr_live": 1, "wd2": 1, "wd1": 1}
    )
    assert primary_again.source_key == "wspr_live"
    primary_again.release()


def test_waiting_acquisition_rechecks_dynamic_cache_request_plan():
    """Allow a waiting provider to become eligible after its cache is filled."""
    clock = _Clock()
    provider = replace(WSPR_DATABASE_PROVIDERS[0], request_limit=1)
    controller = ProviderDispatchController(
        (provider,),
        acquire_timeout_seconds=1.0,
        poll_interval_seconds=0.01,
        clock=clock,
    )
    prior = controller.try_acquire_run({provider.key: 1})
    prior.consume_request()
    prior.report_success()
    prior.release()
    cache_is_ready = False
    supplier_calls = 0

    def request_plan():
        nonlocal supplier_calls
        supplier_calls += 1
        return {provider.key: 0 if cache_is_ready else 1}

    def mark_cache_ready(_snapshot):
        nonlocal cache_is_ready
        cache_is_ready = True

    cached_lease = controller.acquire_run(
        request_plan,
        allowed_sources={provider.key},
        on_wait=mark_cache_ready,
    )

    assert cached_lease.source_key == provider.key
    assert cached_lease.actual_requests == 0
    assert supplier_calls >= 2
    cached_lease.release()


def test_429_opens_primary_circuit_and_half_open_allows_one_probe():
    clock = _Clock()
    controller = _controller(clock, request_limit=4)
    primary = controller.try_acquire_run(
        {"wspr_live": 1, "wd2": 1, "wd1": 1}
    )
    primary.consume_request()
    primary.report_failure(FetchError(
        code="http_error",
        message="rate limited",
        scope=FetchFailureScope.PROVIDER,
        status_code=429,
        retry_after_seconds=12.0,
    ))
    primary.release()

    fallback = controller.try_acquire_run(
        {"wspr_live": 1, "wd2": 1, "wd1": 1}
    )
    assert fallback.source_key == "wd2"
    assert fallback.skipped_sources == ("wspr_live",)
    assert fallback.skipped_source_reasons == (
        ("wspr_live", ProviderSkipReason.CIRCUIT_OPEN),
    )
    fallback.release()

    clock.advance(12.0)
    probe = controller.try_acquire_run(
        {"wspr_live": 1, "wd2": 1, "wd1": 1}
    )
    assert probe.source_key == "wspr_live"
    concurrent = controller.try_acquire_run(
        {"wspr_live": 1, "wd2": 1, "wd1": 1}
    )
    assert concurrent.source_key == "wd2"
    assert concurrent.skipped_source_reasons == (
        ("wspr_live", ProviderSkipReason.RECOVERY_PROBE_IN_FLIGHT),
    )
    concurrent.release()

    probe.consume_request()
    probe.report_success()
    probe.release()
    normal = controller.try_acquire_run(
        {"wspr_live": 1, "wd2": 1, "wd1": 1}
    )
    assert normal.source_key == "wspr_live"
    normal.release()


def test_cache_only_run_can_use_pinned_source_while_network_circuit_is_open():
    clock = _Clock()
    controller = _controller(clock)
    primary = controller.try_acquire_run(
        {"wspr_live": 1, "wd2": 1, "wd1": 1}
    )
    primary.consume_request()
    primary.report_failure(FetchError(
        code="timeout",
        message="timeout",
        scope=FetchFailureScope.PROVIDER,
    ))
    primary.release()

    cached = controller.try_acquire_run(
        {"wspr_live": 0},
        allowed_sources={"wspr_live"},
    )
    assert cached.source_key == "wspr_live"
    assert cached.actual_requests == 0
    with pytest.raises(ProviderRateLimitExceeded):
        cached.consume_request()
    cached.report_success()
    cached.release()
    assert controller.snapshot("wspr_live").consecutive_failures == 1


def test_older_success_cannot_cancel_a_newer_rate_limit_failure():
    """Preserve Retry-After when an already-running lease finishes later."""
    clock = _Clock()
    controller = _controller(clock, request_limit=4)
    older = controller.try_acquire_run(
        {"wspr_live": 2, "wd2": 2, "wd1": 2}
    )
    older.consume_request()
    newer = controller.try_acquire_run(
        {"wspr_live": 1, "wd2": 1, "wd1": 1}
    )
    assert newer.source_key == "wspr_live"
    newer.consume_request()
    newer.report_failure(FetchError(
        code="http_error",
        message="rate limited",
        scope=FetchFailureScope.PROVIDER,
        status_code=429,
        retry_after_seconds=20.0,
    ))

    with pytest.raises(ProviderRateLimitExceeded):
        older.consume_request()
    older.report_success()
    snapshot = controller.snapshot("wspr_live")

    assert snapshot.consecutive_failures == 1
    assert snapshot.circuit_open_seconds == pytest.approx(20.0)
    older.release()
    newer.release()


def test_late_old_failure_cannot_reopen_after_successful_recovery_probe():
    """Ignore an old in-flight failure after a newer probe restored health."""
    clock = _Clock()
    controller = _controller(clock, request_limit=4)
    first_old = controller.try_acquire_run(
        {"wspr_live": 1, "wd2": 1, "wd1": 1}
    )
    second_old = controller.try_acquire_run(
        {"wspr_live": 1, "wd2": 1, "wd1": 1}
    )
    first_old.consume_request()
    second_old.consume_request()
    first_old.report_failure(FetchError(
        code="timeout",
        message="timeout",
        scope=FetchFailureScope.PROVIDER,
    ))

    clock.advance(10.0)
    probe = controller.try_acquire_run(
        {"wspr_live": 1, "wd2": 1, "wd1": 1}
    )
    assert probe.source_key == "wspr_live"
    probe.consume_request()
    probe.report_success()
    probe.release()

    second_old.report_failure(FetchError(
        code="timeout",
        message="late timeout",
        scope=FetchFailureScope.PROVIDER,
    ))
    snapshot = controller.snapshot("wspr_live")

    assert snapshot.consecutive_failures == 0
    assert snapshot.circuit_open_seconds == 0.0
    assert snapshot.recovery_generation == 1
    first_old.release()
    second_old.release()


def test_old_lease_cannot_start_more_requests_after_provider_recovery():
    """Force a fresh reservation epoch after a newer probe restored health."""
    clock = _Clock()
    controller = _controller(clock, request_limit=5)
    failing = controller.try_acquire_run(
        {"wspr_live": 1, "wd2": 1, "wd1": 1}
    )
    old_remaining = controller.try_acquire_run(
        {"wspr_live": 2, "wd2": 2, "wd1": 2}
    )
    failing.consume_request()
    old_remaining.consume_request()
    failing.report_failure(FetchError(
        code="timeout",
        message="timeout",
        scope=FetchFailureScope.PROVIDER,
    ))

    clock.advance(10.0)
    probe = controller.try_acquire_run(
        {"wspr_live": 1, "wd2": 1, "wd1": 1}
    )
    probe.consume_request()
    probe.report_success()
    probe.release()

    with pytest.raises(ProviderRateLimitExceeded):
        old_remaining.consume_request()

    failing.release()
    old_remaining.release()


def test_retry_after_is_honored_for_provider_503_responses():
    clock = _Clock()
    controller = _controller(clock, failure_threshold=2)
    lease = controller.try_acquire_run(
        {"wspr_live": 1, "wd2": 1, "wd1": 1}
    )
    lease.consume_request()
    lease.report_failure(FetchError(
        code="http_error",
        message="maintenance",
        scope=FetchFailureScope.PROVIDER,
        status_code=503,
        retry_after_seconds=17.0,
    ))
    lease.release()

    assert controller.snapshot("wspr_live").circuit_open_seconds == pytest.approx(17.0)


def test_concurrent_reservations_are_atomic_within_one_provider_budget():
    """Never reserve more request slots than one rolling-window limit."""
    clock = _Clock()
    provider = replace(
        WSPR_DATABASE_PROVIDERS[0],
        request_limit=2,
        request_window_seconds=60.0,
    )
    controller = ProviderDispatchController(
        (provider,),
        acquire_timeout_seconds=1.0,
        poll_interval_seconds=0.01,
        clock=clock,
    )
    start = threading.Barrier(3)

    def reserve_complete_budget():
        start.wait(timeout=1.0)
        return controller.try_acquire_run({provider.key: 2})

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(reserve_complete_budget) for _ in range(2)]
        start.wait(timeout=1.0)
        leases = [future.result(timeout=1.0) for future in futures]

    acquired = [lease for lease in leases if lease is not None]
    assert len(acquired) == 1
    assert controller.snapshot(provider.key).reserved_requests == 2
    acquired[0].release()


def test_excluding_every_provider_fails_without_retrying_prior_source():
    controller = _controller(_Clock())

    with pytest.raises(NoProviderAvailable):
        controller.try_acquire_run(
            {"wspr_live": 1, "wd2": 1, "wd1": 1},
            excluded_sources={"wspr_live", "wd2", "wd1"},
        )


def test_oversized_request_plan_records_stable_skip_reason():
    """Expose permanent plan incompatibility separately from transient capacity."""
    clock = _Clock()
    controller = _controller(clock, request_limit=2)

    fallback = controller.try_acquire_run(
        {"wspr_live": 3, "wd2": 1, "wd1": 1}
    )

    assert fallback.source_key == "wd2"
    assert fallback.skipped_sources == ("wspr_live",)
    assert fallback.skipped_source_reasons == (
        (
            "wspr_live",
            ProviderSkipReason.REQUEST_PLAN_EXCEEDS_PROVIDER_LIMIT,
        ),
    )
    fallback.release()
