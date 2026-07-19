from pathlib import Path
from types import SimpleNamespace

from config import DEMO_PROFILES, WSPR_DATABASE_PROVIDERS
from core.analysis_admission import (
    AdmissionSnapshot,
    AnalysisQueueFull,
    AnalysisQueueTimeout,
)
from core.analysis_runner import DECODE_FILTER_LEGACY, DECODE_FILTER_STRICT
from core.fetch_models import (
    DatabaseSource,
    FetchError,
    FetchFailureScope,
    FetchResult,
    FetchSource,
)
from core.provider_dispatch import ProviderDispatchController, ProviderSkipReason
from core.run_data_preparation import (
    PreparedAnalysisData,
    PreparedProviderBundle,
    PreparedQueryFetch,
    ProviderBundleFetchError,
    ProviderBundlePreparationError,
)
from ui import run_controller
from ui.result_state import (
    EXPORT_STATE_KEY,
    INSPECTOR_CACHE_STATE_KEY,
    STABILITY_CACHE_STATE_KEY,
    get_active_run_database_source,
    set_active_run_database_source,
)


class _SessionState(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name, value):
        self[name] = value


class _Context:
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


class _Placeholder:
    def __init__(self):
        self.markdowns = []

    def markdown(self, text):
        self.markdowns.append(text)


class _Status(_Context):
    def __init__(self, label):
        self.label = label
        self.updates = []

    def update(self, **kwargs):
        self.updates.append(kwargs)
        if "label" in kwargs:
            self.label = kwargs["label"]


class _RunStatusSlot:
    def __init__(self):
        self.empty_calls = 0
        self.notices = []

    def container(self):
        return _Context()

    def empty(self):
        self.empty_calls += 1

    def info(self, message):
        self.notices.append(("info", str(message)))

    def warning(self, message):
        self.notices.append(("warning", str(message)))


class _FakeStreamlit:
    def __init__(self):
        self.session_state = _SessionState(
            run_id=77,
            run_mode="RX",
            lang="en",
        )
        self.placeholders = []
        self.statuses = []
        self.errors = []
        self.warnings = []
        self.markdowns = []
        self.codes = []

    def status(self, label, **_kwargs):
        status = _Status(label)
        self.statuses.append(status)
        return status

    def empty(self):
        placeholder = _Placeholder()
        self.placeholders.append(placeholder)
        return placeholder

    def error(self, message):
        self.errors.append(str(message))

    def warning(self, message):
        self.warnings.append(str(message))

    def markdown(self, message):
        self.markdowns.append(str(message))

    def code(self, body, *, language=None):
        self.codes.append((str(body), language))


class _ProfileTimer:
    def log_report(self, **_kwargs):
        return None


class _AnalysisPermit:
    def __init__(self, capacity_lease):
        self.capacity_lease = capacity_lease

    def touch(self):
        return True

    def release_capacity_lease(self):
        prior = self.capacity_lease
        self.capacity_lease = None
        return prior.release() if prior is not None else False

    def replace_capacity_lease(self, capacity_lease):
        prior = self.capacity_lease
        self.capacity_lease = capacity_lease
        if prior is not None:
            prior.release()
        return True


def _analysis(analysis_id, title):
    return {
        "id": analysis_id,
        "title": title,
        "query": f"SELECT {analysis_id}",
        "legacy_query": f"SELECT {analysis_id} LEGACY",
        "decode_filter_mode": DECODE_FILTER_STRICT,
        "is_compare": analysis_id.endswith("COMP"),
        "is_sequential": False,
        "analysis_kind": (
            "comparison" if analysis_id.endswith("COMP") else "opportunity"
        ),
    }


def _provider_failure(provider_key, analysis, *, scope=FetchFailureScope.PROVIDER):
    """Return one structured bundle failure for a fake provider attempt."""
    return ProviderBundleFetchError(
        FetchResult(
            source={
                "wspr_live": FetchSource.WSPR_LIVE,
                "wd2": FetchSource.WD2,
                "wd1": FetchSource.WD1,
            }[provider_key],
            database_source=DatabaseSource(provider_key),
            error=FetchError(
                code="http_error",
                message="service unavailable",
                scope=scope,
                status_code=503 if scope == FetchFailureScope.PROVIDER else 400,
            ),
        ),
        analysis,
    )


def _no_data_bundle(provider_key, plans):
    """Return a complete fake bundle whose analyses legitimately contain no rows."""
    return PreparedProviderBundle(
        database_source=DatabaseSource(provider_key),
        analyses=[
            PreparedAnalysisData(
                analysis=dict(plan),
                artifact_path=None,
                warning_message=f"No data: {plan['title']}",
                query_fetches=(PreparedQueryFetch(
                    decode_filter_mode=DECODE_FILTER_STRICT,
                    elapsed_seconds=0.1,
                    delivery_source={
                        "wspr_live": FetchSource.WSPR_LIVE,
                        "wd2": FetchSource.WD2,
                        "wd1": FetchSource.WD1,
                    }[provider_key],
                ),),
                profile_timer=_ProfileTimer(),
            )
            for plan in plans
        ],
    )


def _patch_run_environment(monkeypatch, fake_st, controller, fake_prepare):
    """Install the dependency-light fakes shared by source-selection tests."""
    monkeypatch.setattr(run_controller, "st", fake_st)
    monkeypatch.setattr(run_controller, "UPSTREAM_PROVIDER_DISPATCH", controller)
    monkeypatch.setattr(run_controller, "prepare_provider_bundle", fake_prepare)
    monkeypatch.setattr(run_controller, "touch_registered_session_artifacts", lambda _state: 0)
    monkeypatch.setattr(run_controller, "cleanup_old_parquets", lambda: {})
    monkeypatch.setattr(run_controller, "retire_registered_session_artifacts", lambda _state: 0)
    monkeypatch.setattr(run_controller, "log_performance_event", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        run_controller,
        "_staged_artifact_paths",
        lambda plans, **_kwargs: {plan["id"]: None for plan in plans},
    )


def test_session_artifacts_are_refreshed_before_global_cleanup(monkeypatch):
    """Prevent TTL cleanup from deleting this session's retained results."""
    fake_st = _FakeStreamlit()
    calls = []
    monkeypatch.setattr(run_controller, "st", fake_st)
    monkeypatch.setattr(
        run_controller,
        "touch_registered_session_artifacts",
        lambda state: calls.append(("touch", state)) or 2,
    )
    monkeypatch.setattr(
        run_controller,
        "cleanup_old_parquets",
        lambda: calls.append(("cleanup", None)) or {},
    )

    run_controller._refresh_session_artifacts_before_cleanup()

    assert calls == [("touch", fake_st.session_state), ("cleanup", None)]


def _patch_admission_presentation_environment(monkeypatch, fake_st, gate):
    """Install the dependency-light shell needed to exercise queue notices."""
    analysis_context = SimpleNamespace(to_dict=lambda: {})
    monkeypatch.setattr(run_controller, "st", fake_st)
    monkeypatch.setattr(run_controller, "ANALYSIS_ADMISSION_GATE", gate)
    monkeypatch.setattr(run_controller, "is_valid_callsign", lambda _value: True)
    monkeypatch.setattr(run_controller, "is_valid_locator", lambda _value: True)
    monkeypatch.setattr(run_controller, "locator_to_latlon", lambda _value: (47.0, 8.0))
    monkeypatch.setattr(
        run_controller,
        "build_analysis_context_from_session_state",
        lambda _state: analysis_context,
    )
    monkeypatch.setattr(
        run_controller,
        "build_presentation_context_from_session_state",
        lambda *_args, **_kwargs: SimpleNamespace(),
    )
    monkeypatch.setattr(
        run_controller,
        "build_analysis_batches",
        lambda *_args, **_kwargs: [],
    )
    monkeypatch.setattr(
        run_controller,
        "_refresh_session_artifacts_before_cleanup",
        lambda: {},
    )
    monkeypatch.setattr(
        run_controller,
        "session_artifact_owner",
        lambda _state: "owner",
    )
    monkeypatch.setattr(
        run_controller,
        "_analysis_request_fingerprint",
        lambda **_kwargs: "request-key",
    )
    monkeypatch.setattr(run_controller, "process_rss_bytes", lambda: 0)
    monkeypatch.setattr(run_controller, "process_peak_rss_bytes", lambda: 0)
    monkeypatch.setattr(
        run_controller,
        "log_performance_event",
        lambda *_args, **_kwargs: None,
    )


def _render_admission_presentation(fake_st, run_status_slot, *, translations=None):
    """Invoke the public controller with fixed valid inputs for queue tests."""
    run_controller.render_analysis_run(
        t=translations or {},
        run_status_slot=run_status_slot,
        callsign="G3ZIL",
        qth_locator="IO90",
        band_filter=7,
        start_t=SimpleNamespace(isoformat=lambda: "start"),
        end_t=SimpleNamespace(isoformat=lambda: "end"),
        max_dist_km=22000,
        generate_map_plot=lambda *_args, **_kwargs: None,
    )


def test_waiting_status_shows_queue_count_without_active_fraction(monkeypatch):
    """Keep provider-capacity waits clear when no analysis slot is active."""
    fake_st = _FakeStreamlit()
    run_status_slot = _RunStatusSlot()

    def wait_then_timeout(**kwargs):
        kwargs["on_wait"](AdmissionSnapshot(
            position=8,
            active=0,
            queued=8,
            max_active=2,
            max_queued=10,
        ))
        raise AnalysisQueueTimeout("simulated queue timeout")

    gate = SimpleNamespace(
        acquire=wait_then_timeout,
        counts=lambda: (0, 8),
    )
    _patch_admission_presentation_environment(monkeypatch, fake_st, gate)

    _render_admission_presentation(fake_st, run_status_slot)

    assert fake_st.placeholders[0].markdowns == ["Analyses waiting: 8."]
    assert "0/2" not in fake_st.placeholders[0].markdowns[0]


def test_queue_full_warning_uses_replaceable_run_status_slot(monkeypatch):
    """Ensure a later accepted retry can replace the prior queue-full notice."""
    fake_st = _FakeStreamlit()
    run_status_slot = _RunStatusSlot()

    def reject_full_queue(**_kwargs):
        raise AnalysisQueueFull("simulated full queue")

    gate = SimpleNamespace(
        acquire=reject_full_queue,
        counts=lambda: (0, 10),
    )
    _patch_admission_presentation_environment(monkeypatch, fake_st, gate)

    _render_admission_presentation(fake_st, run_status_slot)

    assert run_status_slot.notices == [(
        "warning",
        "High demand right now. The analysis queue is full. Please try again shortly.",
    )]
    assert fake_st.warnings == []


def test_fetch_failure_telemetry_omits_query_and_error_message(monkeypatch):
    """Log safe structured diagnostics without duplicating sensitive SQL text."""
    fake_st = _FakeStreamlit()
    performance_events = []
    monkeypatch.setattr(run_controller, "st", fake_st)
    monkeypatch.setattr(
        run_controller,
        "log_performance_event",
        lambda event, **values: performance_events.append((event, values)),
    )
    fetch_result = FetchResult(
        artifact_path=Path(".wspr_cache/demo-queries/wd2/query.parquet"),
        source=FetchSource.WD2,
        database_source=DatabaseSource.WD2,
        error=FetchError(
            code="local_io_error",
            message="private filesystem detail",
            scope=FetchFailureScope.LOCAL,
            query="SELECT private_query_text",
            failure_stage="validate_query_cache_temporary",
        ),
    )

    run_controller._render_fetch_error(fetch_result)

    assert performance_events == [(
        "analysis_fetch_failure",
        {
            "source": "wd2",
            "delivery_source": "WD2",
            "failure_code": "local_io_error",
            "failure_scope": "local",
            "failure_stage": "validate_query_cache_temporary",
            "cache_namespace": "demo-queries",
            "cache_policy": "demo_absolute_24h",
        },
    )]
    assert fake_st.codes == [("SELECT private_query_text", "sql")]


def test_database_selection_reason_distinguishes_routing_paths():
    """Keep admission spillover distinct from an in-run provider failure."""
    assert run_controller._database_selection_reason(
        "wspr_live",
        failed_sources=[],
        committed_source=None,
    ) == "primary"
    assert run_controller._database_selection_reason(
        "wd2",
        failed_sources=[],
        committed_source=None,
        used_cache_affinity=True,
    ) == "cache_affinity"
    assert run_controller._database_selection_reason(
        "wd2",
        failed_sources=["wspr_live"],
        committed_source=None,
        used_cache_affinity=True,
    ) == "failure_fallback"
    assert run_controller._database_selection_reason(
        "wd2",
        failed_sources=[],
        committed_source="wd2",
        used_cache_affinity=True,
    ) == "committed_source"
    assert run_controller._database_selection_reason(
        "wd2",
        failed_sources=[],
        committed_source=None,
    ) == "capacity_spillover"
    assert run_controller._database_selection_reason(
        "wd2",
        failed_sources=[],
        committed_source=None,
        skipped_source_reasons=(
            ("wspr_live", ProviderSkipReason.CIRCUIT_OPEN),
        ),
        used_cache_affinity=True,
    ) == "failure_fallback"
    assert run_controller._database_selection_reason(
        "wd2",
        failed_sources=["wspr_live"],
        committed_source=None,
    ) == "failure_fallback"
    assert run_controller._database_selection_reason(
        "wd2",
        failed_sources=[],
        committed_source="wd2",
    ) == "committed_source"
    assert run_controller._database_selection_reason(
        "wspr_live",
        failed_sources=[],
        committed_source="wspr_live",
    ) == "committed_source"


def test_structured_early_failure_marks_complete_run_telemetry_failed(monkeypatch):
    """Propagate an admitted renderer's early failure into the run event."""
    fake_st = _FakeStreamlit()
    performance_events = []
    permit = _Context()
    fake_gate = SimpleNamespace(
        acquire=lambda **_kwargs: permit,
        counts=lambda: (0, 0),
    )
    analysis_context = SimpleNamespace(to_dict=lambda: {})

    monkeypatch.setattr(run_controller, "st", fake_st)
    monkeypatch.setattr(run_controller, "ANALYSIS_ADMISSION_GATE", fake_gate)
    monkeypatch.setattr(run_controller, "is_valid_callsign", lambda _value: True)
    monkeypatch.setattr(run_controller, "is_valid_locator", lambda _value: True)
    monkeypatch.setattr(run_controller, "locator_to_latlon", lambda _value: (47.0, 8.0))
    monkeypatch.setattr(
        run_controller,
        "build_analysis_context_from_session_state",
        lambda _state: analysis_context,
    )
    monkeypatch.setattr(
        run_controller,
        "build_presentation_context_from_session_state",
        lambda *_args, **_kwargs: SimpleNamespace(),
    )
    monkeypatch.setattr(run_controller, "build_analysis_batches", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(
        run_controller,
        "_refresh_session_artifacts_before_cleanup",
        lambda: {},
    )
    monkeypatch.setattr(run_controller, "session_artifact_owner", lambda _state: "owner")
    monkeypatch.setattr(
        run_controller,
        "_analysis_request_fingerprint",
        lambda **_kwargs: "request-key",
    )
    monkeypatch.setattr(
        run_controller,
        "_render_admitted_analysis_run",
        lambda **_kwargs: "failed",
    )
    monkeypatch.setattr(run_controller, "process_rss_bytes", lambda: 0)
    monkeypatch.setattr(run_controller, "process_peak_rss_bytes", lambda: 0)
    monkeypatch.setattr(
        run_controller,
        "log_performance_event",
        lambda event, **values: performance_events.append((event, values)),
    )

    run_controller.render_analysis_run(
        t={},
        run_status_slot=_RunStatusSlot(),
        callsign="G3ZIL",
        qth_locator="IO90",
        band_filter=7,
        start_t=SimpleNamespace(isoformat=lambda: "start"),
        end_t=SimpleNamespace(isoformat=lambda: "end"),
        max_dist_km=22000,
        generate_map_plot=lambda *_args, **_kwargs: None,
    )

    run_event = next(
        values
        for event, values in performance_events
        if event == "analysis_run"
    )
    assert run_event["outcome"] == "failed"


def test_each_capacity_attempt_reinspects_source_specific_caches(monkeypatch):
    """Do not retain request estimates across a potentially long queue wait."""
    estimates = [
        {"wspr_live": 2, "wd2": 2, "wd1": 2},
        {"wspr_live": 0, "wd2": 2, "wd1": 2},
    ]
    reservations = []
    fake_dispatch = SimpleNamespace(
        try_acquire_run=lambda counts, **kwargs: reservations.append(
            (
                dict(counts),
                kwargs["allowed_sources"],
                kwargs["prefer_cache_only"],
            )
        )
    )
    monkeypatch.setattr(run_controller, "UPSTREAM_PROVIDER_DISPATCH", fake_dispatch)
    monkeypatch.setattr(
        run_controller,
        "_provider_request_counts",
        lambda *_args, **_kwargs: estimates.pop(0),
    )

    first = run_controller._try_reserve_upstream_capacity(
        ["analysis"],
        is_demo_run=False,
        allowed_sources=None,
    )
    second = run_controller._try_reserve_upstream_capacity(
        ["analysis"],
        is_demo_run=False,
        allowed_sources={"wspr_live"},
    )

    assert first[1]["wspr_live"] == 2
    assert second[1]["wspr_live"] == 0
    assert reservations == [
        ({"wspr_live": 2, "wd2": 2, "wd1": 2}, None, False),
        ({"wspr_live": 0, "wd2": 2, "wd1": 2}, {"wspr_live"}, False),
    ]


def test_demo_reservation_enables_cross_provider_cache_affinity(monkeypatch):
    """Enable complete cached-provider preference only for guided demos."""
    controller = ProviderDispatchController(
        WSPR_DATABASE_PROVIDERS,
        acquire_timeout_seconds=1.0,
        poll_interval_seconds=0.01,
    )
    request_counts = {"wspr_live": 1, "wd2": 0, "wd1": 1}
    monkeypatch.setattr(run_controller, "UPSTREAM_PROVIDER_DISPATCH", controller)
    monkeypatch.setattr(
        run_controller,
        "_provider_request_counts",
        lambda *_args, **_kwargs: dict(request_counts),
    )

    demo_lease, _counts = run_controller._try_reserve_upstream_capacity(
        ["analysis"],
        is_demo_run=True,
        allowed_sources=None,
    )
    assert demo_lease.source_key == "wd2"
    assert demo_lease.used_cache_affinity
    demo_lease.release()

    ordinary_lease, _counts = run_controller._try_reserve_upstream_capacity(
        ["analysis"],
        is_demo_run=False,
        allowed_sources=None,
    )
    assert ordinary_lease.source_key == "wspr_live"
    assert not ordinary_lease.used_cache_affinity
    ordinary_lease.release()

    pinned_lease, _counts = run_controller._try_reserve_upstream_capacity(
        ["analysis"],
        is_demo_run=True,
        allowed_sources={"wspr_live"},
    )
    assert pinned_lease.source_key == "wspr_live"
    assert not pinned_lease.used_cache_affinity
    pinned_lease.release()


def _render_fake_run(
    fake_st,
    permit,
    analyses,
    *,
    committed_source=None,
    is_demo_run=False,
    active_demo_key=None,
    request_counts_by_provider=None,
):
    """Execute the admitted transactional path without map rendering."""
    fake_st.analysis_run_outcome = run_controller._render_admitted_analysis_run(
        t={"warn_no_data": "No data: {title}"},
        run_status_slot=_RunStatusSlot(),
        start_t="start",
        end_t="end",
        max_dist_km=22000,
        generate_map_plot=lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("No map should render for no-data staged results")
        ),
        admission_permit=permit,
        analyses=analyses,
        analysis_context=SimpleNamespace(),
        presentation_context=SimpleNamespace(),
        center_latitude=47.0,
        center_longitude=8.0,
        active_demo=(
            DEMO_PROFILES.get(active_demo_key) if is_demo_run else None
        ),
        active_demo_key=active_demo_key,
        is_demo_run=is_demo_run,
        request_counts_by_provider=(
            request_counts_by_provider
            or {"wspr_live": 1, "wd2": 1, "wd1": 1}
        ),
        committed_source=committed_source,
    )
    return fake_st


def test_failed_success_preparation_restarts_whole_bundle_on_wd2(monkeypatch):
    fake_st = _FakeStreamlit()
    controller = ProviderDispatchController(
        WSPR_DATABASE_PROVIDERS,
        acquire_timeout_seconds=1.0,
        poll_interval_seconds=0.01,
    )
    initial_lease = controller.try_acquire_run(
        {"wspr_live": 1, "wd2": 1, "wd1": 1}
    )
    permit = _AnalysisPermit(initial_lease)
    analyses = [_analysis("RX_COMP", "Compare"), _analysis("RX_ABS", "Success")]
    attempts = []

    def fake_prepare(plans, *, provider_lease, **_kwargs):
        attempts.append((provider_lease.source_key, [plan["id"] for plan in plans]))
        if provider_lease.source_key == "wspr_live":
            raise _provider_failure(provider_lease.source_key, plans[1])
        bundle = _no_data_bundle(provider_lease.source_key, plans)
        bundle.analyses[0].analysis["decode_filter_mode"] = DECODE_FILTER_LEGACY
        bundle.analyses[0].query_fetches = (
            PreparedQueryFetch(
                decode_filter_mode=DECODE_FILTER_STRICT,
                elapsed_seconds=0.12,
                delivery_source=FetchSource.MEMORY_CACHE,
            ),
            PreparedQueryFetch(
                decode_filter_mode=DECODE_FILTER_LEGACY,
                elapsed_seconds=0.34,
                delivery_source=FetchSource.DISK_CACHE,
            ),
        )
        return bundle

    performance_events = []
    _patch_run_environment(monkeypatch, fake_st, controller, fake_prepare)
    monkeypatch.setattr(
        run_controller,
        "log_performance_event",
        lambda event, **values: performance_events.append((event, values)),
    )
    _render_fake_run(fake_st, permit, analyses)

    assert attempts == [
        ("wspr_live", ["RX_COMP", "RX_ABS"]),
        ("wd2", ["RX_COMP", "RX_ABS"]),
    ]
    assert get_active_run_database_source(fake_st.session_state) == "wd2"
    complete_audit = fake_st.placeholders[0].markdowns[-1]
    assert "Database origin for complete run: **WD2** (failure fallback)" in complete_audit
    assert (
        "Compare — strict: **RAM cache** in 0.12s "
        "(no target-side evidence); legacy: **disk cache** in 0.34s "
        "(completed; no usable result; no code filter)"
    ) in complete_audit
    assert "strict: **WD2**" not in complete_audit
    assert fake_st.errors == []
    assert fake_st.statuses[0].label == "Complete"
    assert fake_st.analysis_run_outcome == "completed"
    selection_event = next(
        values
        for event, values in performance_events
        if event == "database_source_selected"
    )
    assert selection_event["selection_reason"] == "failure_fallback"
    assert selection_event["failed_sources"] == ["wspr_live"]


def test_two_provider_failures_restart_whole_bundle_on_wd1(monkeypatch):
    fake_st = _FakeStreamlit()
    controller = ProviderDispatchController(
        WSPR_DATABASE_PROVIDERS,
        acquire_timeout_seconds=1.0,
        poll_interval_seconds=0.01,
    )
    permit = _AnalysisPermit(controller.try_acquire_run(
        {"wspr_live": 1, "wd2": 1, "wd1": 1}
    ))
    analyses = [_analysis("RX_COMP", "Compare"), _analysis("RX_ABS", "Success")]
    attempts = []

    def fake_prepare(plans, *, provider_lease, **_kwargs):
        attempts.append((provider_lease.source_key, [plan["id"] for plan in plans]))
        if provider_lease.source_key != "wd1":
            raise _provider_failure(provider_lease.source_key, plans[1])
        return _no_data_bundle(provider_lease.source_key, plans)

    _patch_run_environment(monkeypatch, fake_st, controller, fake_prepare)
    _render_fake_run(fake_st, permit, analyses)

    assert attempts == [
        ("wspr_live", ["RX_COMP", "RX_ABS"]),
        ("wd2", ["RX_COMP", "RX_ABS"]),
        ("wd1", ["RX_COMP", "RX_ABS"]),
    ]
    assert get_active_run_database_source(fake_st.session_state) == "wd1"
    complete_audit = fake_st.placeholders[0].markdowns[-1]
    assert "Database origin for complete run: **WD1** (failure fallback)" in complete_audit
    assert (
        "strict: **database request** in 0.10s "
        "(completed; no usable result); legacy: not needed"
    ) in complete_audit
    assert fake_st.statuses[0].label == "Complete"


def test_skipped_primary_is_not_retried_after_wd2_failure(monkeypatch):
    """Keep fallback progression monotonic after primary capacity was unavailable."""
    fake_st = _FakeStreamlit()
    controller = ProviderDispatchController(
        WSPR_DATABASE_PROVIDERS,
        acquire_timeout_seconds=1.0,
        poll_interval_seconds=0.01,
    )
    primary_hold = controller.try_acquire_run({
        provider.key: provider.request_limit
        for provider in WSPR_DATABASE_PROVIDERS
    })
    initial_lease = controller.try_acquire_run(
        {"wspr_live": 1, "wd2": 1, "wd1": 1}
    )
    assert initial_lease.source_key == "wd2"
    permit = _AnalysisPermit(initial_lease)
    analyses = [_analysis("RX_COMP", "Compare"), _analysis("RX_ABS", "Success")]
    attempts = []

    def fake_prepare(plans, *, provider_lease, **_kwargs):
        attempts.append(provider_lease.source_key)
        if provider_lease.source_key == "wd2":
            raise _provider_failure(provider_lease.source_key, plans[1])
        return _no_data_bundle(provider_lease.source_key, plans)

    _patch_run_environment(monkeypatch, fake_st, controller, fake_prepare)
    try:
        _render_fake_run(fake_st, permit, analyses)
    finally:
        primary_hold.release()

    assert attempts == ["wd2", "wd1"]
    assert get_active_run_database_source(fake_st.session_state) == "wd1"


def test_initial_nonprimary_selection_is_reported_as_capacity_spillover(monkeypatch):
    """Do not describe admission-time provider capacity routing as a failure."""
    fake_st = _FakeStreamlit()
    controller = ProviderDispatchController(
        WSPR_DATABASE_PROVIDERS,
        acquire_timeout_seconds=1.0,
        poll_interval_seconds=0.01,
    )
    primary_hold = controller.try_acquire_run({
        provider.key: provider.request_limit
        for provider in WSPR_DATABASE_PROVIDERS
    })
    initial_lease = controller.try_acquire_run(
        {"wspr_live": 1, "wd2": 1, "wd1": 1}
    )
    assert initial_lease.source_key == "wd2"
    permit = _AnalysisPermit(initial_lease)
    analyses = [_analysis("RX_COMP", "Compare"), _analysis("RX_ABS", "Success")]
    performance_events = []

    _patch_run_environment(
        monkeypatch,
        fake_st,
        controller,
        lambda plans, *, provider_lease, **_kwargs: _no_data_bundle(
            provider_lease.source_key,
            plans,
        ),
    )
    monkeypatch.setattr(
        run_controller,
        "log_performance_event",
        lambda event, **values: performance_events.append((event, values)),
    )
    try:
        _render_fake_run(fake_st, permit, analyses)
    finally:
        primary_hold.release()

    complete_audit = fake_st.placeholders[0].markdowns[-1]
    assert "Database origin for complete run: **WD2** (capacity spillover)" in complete_audit
    selection_event = next(
        values
        for event, values in performance_events
        if event == "database_source_selected"
    )
    assert selection_event["selection_reason"] == "capacity_spillover"
    assert selection_event["failed_sources"] == []
    assert selection_event["skipped_source_reasons"] == (
        "wspr_live:rolling_request_capacity_unavailable",
    )


def test_demo_cache_affinity_is_reported_in_audit_and_telemetry(monkeypatch):
    """Separate cached WD2 origin, affinity routing, and disk delivery tier."""
    fake_st = _FakeStreamlit()
    controller = ProviderDispatchController(
        WSPR_DATABASE_PROVIDERS,
        acquire_timeout_seconds=1.0,
        poll_interval_seconds=0.01,
    )
    request_counts = {"wspr_live": 1, "wd2": 0, "wd1": 1}
    initial_lease = controller.try_acquire_run(
        request_counts,
        prefer_cache_only=True,
    )
    permit = _AnalysisPermit(initial_lease)
    analyses = [_analysis("RX_COMP", "Compare"), _analysis("RX_ABS", "Success")]
    performance_events = []

    def cached_bundle(plans, *, provider_lease, **_kwargs):
        bundle = _no_data_bundle(provider_lease.source_key, plans)
        for prepared_analysis in bundle.analyses:
            prepared_analysis.query_fetches = (PreparedQueryFetch(
                decode_filter_mode=DECODE_FILTER_STRICT,
                elapsed_seconds=0.02,
                delivery_source=FetchSource.DISK_CACHE,
            ),)
        return bundle

    _patch_run_environment(monkeypatch, fake_st, controller, cached_bundle)
    monkeypatch.setattr(
        run_controller,
        "log_performance_event",
        lambda event, **values: performance_events.append((event, values)),
    )
    _render_fake_run(
        fake_st,
        permit,
        analyses,
        is_demo_run=True,
        active_demo_key="vanhamel_rx_buddy",
        request_counts_by_provider=request_counts,
    )

    complete_audit = fake_st.placeholders[0].markdowns[-1]
    assert "Database origin for complete run: **WD2** (cache affinity)" in complete_audit
    assert "Compare" in complete_audit
    assert "strict: **disk cache** in 0.02s" in complete_audit
    selection_event = next(
        values
        for event, values in performance_events
        if event == "database_source_selected"
    )
    assert selection_event["source"] == "wd2"
    assert selection_event["selection_reason"] == "cache_affinity"
    assert selection_event["is_nonprimary_source"] is True
    assert selection_event["is_failure_fallback"] is False
    assert selection_event["cache_affinity_applied"] is True
    assert selection_event["cache_affinity_bypassed_sources"] == ("wspr_live",)
    assert selection_event["planned_network_requests"] == 0
    assert selection_event["actual_network_requests"] == 0
    assert selection_event["is_demo_run"] is True
    assert selection_event["demo_profile"] == "vanhamel_rx_buddy"
    assert selection_event["failed_sources"] == []
    assert selection_event["skipped_source_reasons"] == ()


def test_disappearing_demo_cache_replans_without_excluding_primary(monkeypatch):
    """Return to normal priority if an affinity-selected cache becomes unusable."""
    fake_st = _FakeStreamlit()
    controller = ProviderDispatchController(
        WSPR_DATABASE_PROVIDERS,
        acquire_timeout_seconds=1.0,
        poll_interval_seconds=0.01,
    )
    initial_counts = {"wspr_live": 1, "wd2": 0, "wd1": 1}
    initial_lease = controller.try_acquire_run(
        initial_counts,
        prefer_cache_only=True,
    )
    permit = _AnalysisPermit(initial_lease)
    analyses = [_analysis("RX_COMP", "Compare"), _analysis("RX_ABS", "Success")]
    attempts = []

    def fake_prepare(plans, *, provider_lease, **_kwargs):
        attempts.append(provider_lease.source_key)
        if len(attempts) == 1:
            raise _provider_failure(
                provider_lease.source_key,
                plans[0],
                scope=FetchFailureScope.CAPACITY,
            )
        return _no_data_bundle(provider_lease.source_key, plans)

    _patch_run_environment(monkeypatch, fake_st, controller, fake_prepare)
    performance_events = []
    monkeypatch.setattr(
        run_controller,
        "log_performance_event",
        lambda event, **values: performance_events.append((event, values)),
    )
    monkeypatch.setattr(
        run_controller,
        "_provider_request_counts",
        lambda *_args, **_kwargs: {"wspr_live": 1, "wd2": 1, "wd1": 1},
    )
    _render_fake_run(
        fake_st,
        permit,
        analyses,
        is_demo_run=True,
        active_demo_key="vanhamel_rx_buddy",
        request_counts_by_provider=initial_counts,
    )

    assert attempts == ["wd2", "wspr_live"]
    assert controller.snapshot("wd2").consecutive_failures == 0
    assert get_active_run_database_source(fake_st.session_state) == "wspr_live"
    complete_audit = fake_st.placeholders[0].markdowns[-1]
    assert "Database origin for complete run: **wspr.live** (primary)" in complete_audit
    selection_event = next(
        values
        for event, values in performance_events
        if event == "database_source_selected"
    )
    assert selection_event["selection_reason"] == "primary"
    assert selection_event["cache_affinity_applied"] is False
    assert selection_event["cache_affinity_bypassed_sources"] == ()
    assert selection_event["planned_network_requests"] == 1


def test_all_provider_failures_publish_no_source_or_complete_result(monkeypatch):
    fake_st = _FakeStreamlit()
    controller = ProviderDispatchController(
        WSPR_DATABASE_PROVIDERS,
        acquire_timeout_seconds=1.0,
        poll_interval_seconds=0.01,
    )
    permit = _AnalysisPermit(controller.try_acquire_run(
        {"wspr_live": 1, "wd2": 1, "wd1": 1}
    ))
    analyses = [_analysis("RX_COMP", "Compare"), _analysis("RX_ABS", "Success")]
    attempts = []

    def fake_prepare(plans, *, provider_lease, **_kwargs):
        attempts.append(provider_lease.source_key)
        raise _provider_failure(provider_lease.source_key, plans[1])

    _patch_run_environment(monkeypatch, fake_st, controller, fake_prepare)
    _render_fake_run(fake_st, permit, analyses)

    assert attempts == ["wspr_live", "wd2", "wd1"]
    assert get_active_run_database_source(fake_st.session_state) is None
    assert fake_st.statuses[0].label != "Complete"
    assert fake_st.errors


def test_request_scoped_failure_does_not_switch_database(monkeypatch):
    fake_st = _FakeStreamlit()
    controller = ProviderDispatchController(
        WSPR_DATABASE_PROVIDERS,
        acquire_timeout_seconds=1.0,
        poll_interval_seconds=0.01,
    )
    permit = _AnalysisPermit(controller.try_acquire_run(
        {"wspr_live": 1, "wd2": 1, "wd1": 1}
    ))
    analyses = [_analysis("RX_COMP", "Compare"), _analysis("RX_ABS", "Success")]
    attempts = []

    def fake_prepare(plans, *, provider_lease, **_kwargs):
        attempts.append(provider_lease.source_key)
        raise _provider_failure(
            provider_lease.source_key,
            plans[0],
            scope=FetchFailureScope.REQUEST,
        )

    _patch_run_environment(monkeypatch, fake_st, controller, fake_prepare)
    _render_fake_run(fake_st, permit, analyses)

    assert attempts == ["wspr_live"]
    assert get_active_run_database_source(fake_st.session_state) is None
    assert fake_st.errors


def test_local_preparation_failure_does_not_switch_or_penalize_database(monkeypatch):
    """A local transform failure stops the run without provider failover."""
    fake_st = _FakeStreamlit()
    controller = ProviderDispatchController(
        WSPR_DATABASE_PROVIDERS,
        acquire_timeout_seconds=1.0,
        poll_interval_seconds=0.01,
    )
    permit = _AnalysisPermit(controller.try_acquire_run(
        {"wspr_live": 1, "wd2": 1, "wd1": 1}
    ))
    analyses = [_analysis("RX_COMP", "Compare"), _analysis("RX_ABS", "Success")]
    attempts = []

    def fake_prepare(_plans, *, provider_lease, **_kwargs):
        attempts.append(provider_lease.source_key)
        raise ProviderBundlePreparationError("invalid local transformation")

    performance_events = []
    _patch_run_environment(monkeypatch, fake_st, controller, fake_prepare)
    monkeypatch.setattr(
        run_controller,
        "log_performance_event",
        lambda event, **values: performance_events.append((event, values)),
    )
    _render_fake_run(fake_st, permit, analyses)

    assert attempts == ["wspr_live"]
    assert controller.snapshot("wspr_live").consecutive_failures == 0
    assert get_active_run_database_source(fake_st.session_state) is None
    assert fake_st.statuses[0].label == "Analysis preparation failed"
    assert fake_st.session_state.run_mode is None
    assert fake_st.analysis_run_outcome == "failed"
    assert performance_events == [(
        "analysis_preparation_failure",
        {
            "source": "wspr_live",
            "failure_scope": "local",
            "failure_type": "ProviderBundlePreparationError",
        },
    )]


def test_cache_capacity_change_replans_without_poisoning_provider_health(monkeypatch):
    fake_st = _FakeStreamlit()
    controller = ProviderDispatchController(
        WSPR_DATABASE_PROVIDERS,
        acquire_timeout_seconds=1.0,
        poll_interval_seconds=0.01,
    )
    permit = _AnalysisPermit(controller.try_acquire_run(
        {"wspr_live": 1, "wd2": 1, "wd1": 1}
    ))
    analyses = [_analysis("RX_COMP", "Compare"), _analysis("RX_ABS", "Success")]
    attempts = []

    def fake_prepare(plans, *, provider_lease, **_kwargs):
        attempts.append(provider_lease.source_key)
        if len(attempts) == 1:
            raise _provider_failure(
                provider_lease.source_key,
                plans[0],
                scope=FetchFailureScope.CAPACITY,
            )
        return _no_data_bundle(provider_lease.source_key, plans)

    _patch_run_environment(monkeypatch, fake_st, controller, fake_prepare)
    monkeypatch.setattr(
        run_controller,
        "_provider_request_counts",
        lambda *_args, **_kwargs: {"wspr_live": 1, "wd2": 1, "wd1": 1},
    )
    _render_fake_run(fake_st, permit, analyses)

    assert attempts == ["wspr_live", "wspr_live"]
    assert controller.snapshot("wspr_live").consecutive_failures == 0
    assert get_active_run_database_source(fake_st.session_state) == "wspr_live"


def test_committed_rerender_never_changes_its_database_source(monkeypatch):
    fake_st = _FakeStreamlit()
    set_active_run_database_source(
        fake_st.session_state,
        run_id=77,
        source_key="wspr_live",
    )
    controller = ProviderDispatchController(
        WSPR_DATABASE_PROVIDERS,
        acquire_timeout_seconds=1.0,
        poll_interval_seconds=0.01,
    )
    permit = _AnalysisPermit(controller.try_acquire_run(
        {"wspr_live": 1, "wd2": 1, "wd1": 1},
        allowed_sources={"wspr_live"},
    ))
    analyses = [_analysis("RX_COMP", "Compare"), _analysis("RX_ABS", "Success")]
    attempts = []

    def fake_prepare(plans, *, provider_lease, **_kwargs):
        attempts.append(provider_lease.source_key)
        raise _provider_failure(provider_lease.source_key, plans[1])

    _patch_run_environment(monkeypatch, fake_st, controller, fake_prepare)
    _render_fake_run(
        fake_st,
        permit,
        analyses,
        committed_source="wspr_live",
    )

    assert attempts == ["wspr_live"]
    assert get_active_run_database_source(fake_st.session_state) == "wspr_live"
    assert fake_st.statuses[0].label != "Complete"


def test_successful_same_run_refresh_clears_stale_export_and_inspector_state(monkeypatch):
    fake_st = _FakeStreamlit()
    fake_st.session_state.update({
        EXPORT_STATE_KEY: {"RX_ABS": {"old": "recipe"}},
        INSPECTOR_CACHE_STATE_KEY: object(),
        STABILITY_CACHE_STATE_KEY: {"old": "model"},
    })
    controller = ProviderDispatchController(
        WSPR_DATABASE_PROVIDERS,
        acquire_timeout_seconds=1.0,
        poll_interval_seconds=0.01,
    )
    permit = _AnalysisPermit(controller.try_acquire_run(
        {"wspr_live": 1, "wd2": 1, "wd1": 1}
    ))
    analyses = [_analysis("RX_COMP", "Compare"), _analysis("RX_ABS", "Success")]

    _patch_run_environment(
        monkeypatch,
        fake_st,
        controller,
        lambda plans, *, provider_lease, **_kwargs: _no_data_bundle(
            provider_lease.source_key,
            plans,
        ),
    )
    _render_fake_run(fake_st, permit, analyses)

    assert fake_st.session_state[EXPORT_STATE_KEY] == {}
    assert INSPECTOR_CACHE_STATE_KEY not in fake_st.session_state
    assert STABILITY_CACHE_STATE_KEY not in fake_st.session_state


def test_failed_attempt_legacy_status_is_not_reported_as_final_method(monkeypatch):
    fake_st = _FakeStreamlit()
    controller = ProviderDispatchController(
        WSPR_DATABASE_PROVIDERS,
        acquire_timeout_seconds=1.0,
        poll_interval_seconds=0.01,
    )
    permit = _AnalysisPermit(controller.try_acquire_run(
        {"wspr_live": 1, "wd2": 1, "wd1": 1}
    ))
    analyses = [_analysis("RX_COMP", "Compare"), _analysis("RX_ABS", "Success")]

    def fake_prepare(plans, *, provider_lease, on_legacy_retry, **_kwargs):
        if provider_lease.source_key == "wspr_live":
            on_legacy_retry(0, len(plans), plans[0])
            raise _provider_failure(provider_lease.source_key, plans[1])
        return _no_data_bundle(provider_lease.source_key, plans)

    _patch_run_environment(monkeypatch, fake_st, controller, fake_prepare)
    _render_fake_run(fake_st, permit, analyses)

    final_audit = fake_st.placeholders[0].markdowns[-1]
    assert "strict `code = 1` found no target-side evidence" not in final_audit
