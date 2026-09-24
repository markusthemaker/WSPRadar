from collections import OrderedDict
from contextlib import nullcontext
from datetime import date, datetime, time, timezone
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from config import DEMO_PROFILES, WSPR_DATABASE_PROVIDERS
from core.analysis_admission import (
    AdmissionSnapshot,
    AnalysisDuplicateRequest,
    AnalysisQueueFull,
    AnalysisQueueTimeout,
)
from core.analysis_runner import (
    DECODE_FILTER_LEGACY,
    DECODE_FILTER_STRICT,
    AnalysisConfigError,
)
from core.artifact_store import (
    SESSION_ARTIFACT_OWNER_KEY,
    SESSION_ARTIFACT_PATHS_KEY,
)
from core.fetch_models import (
    DatabaseSource,
    FetchError,
    FetchFailureScope,
    FetchResult,
    FetchSource,
)
from core.map_models import EmptyMapResult, MapData, MapFigure
from core.opportunity_engine import ABSOLUTE_METHOD_VERSION
from core.provider_dispatch import ProviderDispatchController, ProviderSkipReason
from core.run_data_preparation import (
    PreparedAnalysisData,
    PreparedProviderBundle,
    PreparedQueryFetch,
    ProviderBundleFetchError,
    ProviderBundlePreparationError,
)
from core.result_diagnostics import (
    NO_TARGET_MODE_EVIDENCE,
    PERFORMANCE_NO_ELIGIBLE_STATION,
    ResultDiagnostic,
)
from i18n import T
from ui import callbacks, run_controller
from ui.analysis_context_adapter import build_analysis_context_from_session_state
from ui.analysis_submission_state import (
    begin_analysis_submission,
    cancel_analysis_submission,
    claim_analysis_submission_request,
    handoff_analysis_submission,
    get_analysis_submission,
    update_analysis_submission,
)
from core.completed_run import CompletedAnalysisIdentity, CompletedRun
from ui.result_state import (
    COMPLETED_RUN_SNAPSHOT_KEY,
    COMPLETED_RUN_SNAPSHOT_SCHEMA_VERSION,
    EXPORT_STATE_KEY,
    INSPECTOR_CACHE_STATE_KEY,
    get_active_run_database_source,
    get_completed_run_snapshot,
    publish_completed_run_snapshot,
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

    def spinner(self, *_args, **_kwargs):
        return _Context()

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
    def span(self, *_args, **_kwargs):
        return _Context()

    def add_memory(self, *_args, **_kwargs):
        return None

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
    is_compare = analysis_id.endswith("COMP")
    analysis = {
        "id": analysis_id,
        "title": title,
        "query": f"SELECT {analysis_id}",
        "legacy_query": f"SELECT {analysis_id} LEGACY",
        "legacy_decode_filter_mode": DECODE_FILTER_LEGACY,
        "decode_filter_mode": DECODE_FILTER_STRICT,
        "is_compare": is_compare,
        "is_sequential": False,
        "analysis_kind": "comparison" if is_compare else "opportunity",
        "result_family": "benchmark" if is_compare else "performance",
        "response_format": "csv" if is_compare else "parquet",
    }
    if is_compare:
        analysis.update(
            analysis_start_utc=datetime(2026, 7, 1, tzinfo=timezone.utc),
            analysis_end_utc=datetime(2026, 7, 2, tzinfo=timezone.utc),
        )
    else:
        analysis.update(
            absolute_mode="TX" if analysis_id.startswith("TX") else "RX",
            absolute_method_version="opportunity-v2",
        )
    return analysis


def test_blocked_mode_fallback_message_survives_diagnostic_restore_and_language_change():
    diagnostic = ResultDiagnostic.create(
        NO_TARGET_MODE_EVIDENCE, measured_counts={"source_row_count": 4},
    )
    restored = ResultDiagnostic.from_dict(diagnostic.to_dict())
    analysis = _analysis("RX_COMP", "Compare")
    for language in ("en", "de", "en"):
        message = run_controller._format_result_diagnostic_warning(T[language], analysis, restored)
        assert message == T[language]["warn_no_target_mode_evidence"]
        assert "WSPR-2" in message
        assert "`code = 1`" in message
        assert "2022 (UTC)" in message
    assert T["en"]["warn_no_target_mode_evidence"].startswith(
        "No reports for the Target matched the required **WSPR-2 mode filter**"
    )


def _completed_no_data_snapshot(run_id=77):
    """Use a complete immutable publication marker in lightweight UI tests."""
    return CompletedRun.from_dict({
        "schema_version": COMPLETED_RUN_SNAPSHOT_SCHEMA_VERSION,
        "map_data_schema_version": run_controller.MAP_DATA_ARTIFACT_SCHEMA_VERSION,
        "run_id": run_id,
        "request_fingerprint": "request-key",
        "analysis_plan_fingerprint": "analysis-plan-key",
        "database_source": "wd2",
        "analyses": ({
            "analysis": CompletedAnalysisIdentity.from_analysis(_analysis("RX_COMP", "Completed")).to_dict(),
            "outcome": "prepared_no_data",
            "evidence_path": None,
            "station_rows_path": None,
            "segment_rows_path": None,
            "selected_decode_filter_mode": DECODE_FILTER_STRICT,
            "query_fetches": ({
                "decode_filter_mode": DECODE_FILTER_STRICT,
                "elapsed_seconds": 0.12,
                "delivery_source": FetchSource.DISK_CACHE.value,
            },),
            "diagnostic": None,
        },),
    })


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
        lambda plans, **_kwargs: {
            plan["id"]: run_controller._StagedAnalysisArtifactPaths(
                evidence_path=Path(f"{plan['id']}_evidence.parquet"),
                map_data_paths=run_controller.MapDataArtifactPaths(
                    station_rows_path=Path(
                        f"{plan['id']}_map_stations.parquet"
                    ),
                    segment_rows_path=Path(
                        f"{plan['id']}_map_segments.parquet"
                    ),
                ),
            )
            for plan in plans
        },
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
    return run_controller.render_analysis_run(
        t=translations or {},
        run_status_slot=run_status_slot,
        callsign="G3ZIL",
        qth_locator="IO90",
        band_filter=7,
        start_t=SimpleNamespace(isoformat=lambda: "start"),
        end_t=SimpleNamespace(isoformat=lambda: "end"),
        generate_map_plot=lambda *_args, **_kwargs: None,
    )


def _publish_valid_completed_snapshot(
    fake_st,
    analysis,
    *,
    path_root=None,
    request_fingerprint="request-key",
    analysis_plan_fingerprint="analysis-plan-key",
    selected_decode_filter_mode=DECODE_FILTER_STRICT,
):
    """Publish one registered renderable snapshot for controller tests."""
    cache_root = Path(path_root) if path_root is not None else Path.cwd()
    fake_st.completed_cache_root = cache_root
    artifact_root = (
        cache_root
        / "session-artifacts"
        / "owner-token"
        / f"run_{fake_st.session_state.run_id}_attempt"
    )
    evidence_path = (artifact_root / f"spots_{analysis['id']}.parquet").resolve()
    station_rows_path = (
        artifact_root / f"map_stations_{analysis['id']}.parquet"
    ).resolve()
    segment_rows_path = (
        artifact_root / f"map_segments_{analysis['id']}.parquet"
    ).resolve()
    artifact_root.mkdir(parents=True, exist_ok=True)
    for artifact_path in (
        evidence_path,
        station_rows_path,
        segment_rows_path,
    ):
        artifact_path.write_bytes(b"registered test artifact")
    fake_st.session_state[SESSION_ARTIFACT_OWNER_KEY] = "owner-token"
    fake_st.session_state[SESSION_ARTIFACT_PATHS_KEY] = [
        str(evidence_path),
        str(station_rows_path),
        str(segment_rows_path),
    ]
    set_active_run_database_source(
        fake_st.session_state,
        run_id=fake_st.session_state.run_id,
        source_key="wd2",
    )
    query_fetches = [{
        "decode_filter_mode": DECODE_FILTER_STRICT,
        "elapsed_seconds": 0.12,
        "delivery_source": FetchSource.DISK_CACHE.value,
    }]
    if selected_decode_filter_mode == DECODE_FILTER_LEGACY:
        query_fetches.append({
            "decode_filter_mode": DECODE_FILTER_LEGACY,
            "elapsed_seconds": 0.34,
            "delivery_source": FetchSource.MEMORY_CACHE.value,
        })
    snapshot = {
        "schema_version": COMPLETED_RUN_SNAPSHOT_SCHEMA_VERSION,
        "map_data_schema_version": (
            run_controller.MAP_DATA_ARTIFACT_SCHEMA_VERSION
        ),
        "run_id": fake_st.session_state.run_id,
        "request_fingerprint": request_fingerprint,
        "analysis_plan_fingerprint": analysis_plan_fingerprint,
        "database_source": "wd2",
        "analyses": ({
            "analysis": CompletedAnalysisIdentity.from_analysis(analysis).to_dict(),
            "outcome": run_controller.COMPLETED_RENDERABLE,
            "evidence_path": str(evidence_path),
            "station_rows_path": str(station_rows_path),
            "segment_rows_path": str(segment_rows_path),
            "selected_decode_filter_mode": selected_decode_filter_mode,
            "query_fetches": tuple(query_fetches),
            "diagnostic": None,
        },),
    }
    publish_completed_run_snapshot(fake_st.session_state, snapshot)
    return get_completed_run_snapshot(fake_st.session_state)


def _patch_completed_rerender_environment(
    monkeypatch,
    fake_st,
    gate,
    analysis,
):
    """Install a deterministic shell for implicit completed-result rerenders."""
    analysis_context = SimpleNamespace(
        to_dict=lambda: {"scientific": "current"},
        max_peer_distance_km=22000,
    )
    presentation_context = SimpleNamespace(language="de", theme="dark")
    monkeypatch.setattr(run_controller, "st", fake_st)
    monkeypatch.setattr(
        run_controller,
        "CACHE_DIR",
        fake_st.completed_cache_root,
    )
    monkeypatch.setattr(run_controller, "ANALYSIS_ADMISSION_GATE", gate)
    monkeypatch.setattr(run_controller, "is_valid_callsign", lambda _value: True)
    monkeypatch.setattr(run_controller, "is_valid_locator", lambda _value: True)
    monkeypatch.setattr(
        run_controller,
        "locator_to_latlon",
        lambda _value: (47.0, 8.0),
    )
    monkeypatch.setattr(
        run_controller,
        "build_analysis_context_from_session_state",
        lambda _state: analysis_context,
    )
    monkeypatch.setattr(
        run_controller,
        "build_presentation_context_from_session_state",
        lambda *_args, **_kwargs: presentation_context,
    )
    monkeypatch.setattr(
        run_controller,
        "build_analysis_batches",
        lambda *_args, **_kwargs: [dict(analysis)],
    )
    monkeypatch.setattr(
        run_controller,
        "_refresh_session_artifacts_before_cleanup",
        lambda: {},
    )
    monkeypatch.setattr(
        run_controller,
        "session_artifact_owner",
        lambda _state: "owner-token",
    )
    monkeypatch.setattr(
        run_controller,
        "_analysis_request_fingerprint",
        lambda **_kwargs: "request-key",
    )
    monkeypatch.setattr(
        run_controller,
        "_analysis_plan_fingerprint",
        lambda _analyses: "analysis-plan-key",
    )
    monkeypatch.setattr(run_controller, "process_rss_bytes", lambda: 0)
    monkeypatch.setattr(run_controller, "process_peak_rss_bytes", lambda: 0)
    monkeypatch.setattr(
        run_controller,
        "log_performance_event",
        lambda *_args, **_kwargs: None,
    )
    return analysis_context, presentation_context


def _render_completed_rerender(fake_st, run_status_slot, render_map_figure):
    """Invoke the public implicit-rerender path with fixed valid inputs."""
    return run_controller.render_analysis_run(
        t={
            "warn_analysis_cache_expired": "Completed result expired.",
        },
        run_status_slot=run_status_slot,
        callsign="G3ZIL",
        qth_locator="IO90",
        band_filter=7,
        start_t=SimpleNamespace(isoformat=lambda: "start"),
        end_t=SimpleNamespace(isoformat=lambda: "end"),
        generate_map_plot=lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("Completed rerender must not rebuild map data")
        ),
        render_map_figure=render_map_figure,
        is_existing_run_rerender=True,
    )


@pytest.mark.parametrize(
    ("language", "expected_message"),
    [
        (
            "en",
            "The analysis configuration is invalid. "
            "Check the inputs and try again.",
        ),
        (
            "de",
            "Die Analysekonfiguration ist ungültig. "
            "Prüfe die Eingaben und versuche es erneut.",
        ),
    ],
)
def test_analysis_configuration_errors_are_localized_at_the_ui_boundary(
    monkeypatch,
    language,
    expected_message,
):
    """Keep canonical core diagnostics out of the bilingual presentation."""
    fake_st = _FakeStreamlit()
    run_status_slot = _RunStatusSlot()
    gate = SimpleNamespace(
        acquire=lambda **_kwargs: (_ for _ in ()).throw(
            AssertionError("Invalid configuration must fail before admission")
        ),
        counts=lambda: (0, 0),
    )
    _patch_admission_presentation_environment(monkeypatch, fake_st, gate)
    monkeypatch.setattr(
        run_controller,
        "build_analysis_batches",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AnalysisConfigError(
                "Success opportunity analysis requires canonical internal data."
            )
        ),
    )
    performance_events = []
    monkeypatch.setattr(
        run_controller,
        "log_performance_event",
        lambda event, **values: performance_events.append((event, values)),
    )

    _render_admission_presentation(
        fake_st,
        run_status_slot,
        translations=T[language],
    )

    assert fake_st.errors == [expected_message]
    assert "Success opportunity" not in " ".join(fake_st.errors)
    assert performance_events == [
        (
            "analysis_configuration_failure",
            {
                "failure_type": "AnalysisConfigError",
                "technical_error": (
                    "Success opportunity analysis requires canonical "
                    "internal data."
                ),
            },
        )
    ]


@pytest.mark.parametrize("language", ("en", "de"))
@pytest.mark.parametrize("is_existing_run_rerender", (False, True))
def test_invalid_local_method_rejects_run_and_clears_stale_result_state(
    monkeypatch,
    language,
    is_existing_run_rerender,
):
    """Invalid live input cannot rerender or export an earlier local result."""
    fake_st = _FakeStreamlit()
    fake_st.session_state.update(
        val_comp_mode="local_neighborhood",
        val_local_benchmark="local_best",
        val_callsign="G3ZIL",
        val_qth="IO90",
        result_export_zip_bytes=b"previous result",
    )
    fake_st.session_state[EXPORT_STATE_KEY] = {"RX_COMPARE": "previous export"}
    fake_st.session_state[INSPECTOR_CACHE_STATE_KEY] = {"previous": "evidence"}
    publish_completed_run_snapshot(
        fake_st.session_state,
        _completed_no_data_snapshot(),
    )
    set_active_run_database_source(
        fake_st.session_state,
        run_id=fake_st.session_state.run_id,
        source_key="wd2",
    )
    gate = SimpleNamespace(
        acquire=lambda **_kwargs: pytest.fail(
            "Invalid configuration must fail before admission"
        ),
        counts=lambda: (0, 0),
    )
    _patch_admission_presentation_environment(monkeypatch, fake_st, gate)
    monkeypatch.setattr(
        run_controller,
        "build_analysis_context_from_session_state",
        build_analysis_context_from_session_state,
    )
    monkeypatch.setattr(
        run_controller,
        "build_analysis_batches",
        lambda *_args, **_kwargs: pytest.fail(
            "Unsupported local input must fail before SQL construction"
        ),
    )

    run_controller.render_analysis_run(
        t=T[language],
        run_status_slot=_RunStatusSlot(),
        callsign="G3ZIL",
        qth_locator="IO90",
        band_filter=7,
        start_t=SimpleNamespace(isoformat=lambda: "start"),
        end_t=SimpleNamespace(isoformat=lambda: "end"),
        generate_map_plot=lambda *_args, **_kwargs: pytest.fail(
            "Invalid configuration must never render a map"
        ),
        is_existing_run_rerender=is_existing_run_rerender,
    )

    assert fake_st.errors == [T[language]["err_local_benchmark"]]
    assert fake_st.session_state.val_local_benchmark == "local_best"
    assert fake_st.session_state.run_mode is None
    assert fake_st.session_state[EXPORT_STATE_KEY] == {}
    assert INSPECTOR_CACHE_STATE_KEY not in fake_st.session_state
    assert "result_export_zip_bytes" not in fake_st.session_state
    assert get_completed_run_snapshot(fake_st.session_state) is None
    assert get_active_run_database_source(fake_st.session_state) is None


def test_context_adapter_value_error_is_rejected_before_run_admission(monkeypatch):
    """Context scalar validation uses the same recovery as core validation."""
    fake_st = _FakeStreamlit()
    gate = SimpleNamespace(
        acquire=lambda **_kwargs: pytest.fail(
            "Invalid scalar input must fail before admission"
        ),
        counts=lambda: (0, 0),
    )
    _patch_admission_presentation_environment(monkeypatch, fake_st, gate)

    def reject_invalid_context(_session_state):
        raise ValueError("Invalid numeric configuration")

    monkeypatch.setattr(
        run_controller,
        "build_analysis_context_from_session_state",
        reject_invalid_context,
    )

    _render_admission_presentation(
        fake_st,
        _RunStatusSlot(),
        translations=T["en"],
    )

    assert fake_st.errors == [T["en"]["err_analysis_configuration_invalid"]]
    assert fake_st.session_state.run_mode is None


@pytest.mark.parametrize(
    ("input_view", "language", "direction"),
    (("guided", "en", "rx"), ("classic", "de", "tx")),
)
def test_stale_local_method_recovers_through_application_reset(
    monkeypatch,
    input_view,
    language,
    direction,
):
    """Both editors keep invalid input reviewable and the global Reset usable."""
    from ui import documentation_scroll_trigger, page_navigation, url_synchronizer

    # Browser components have their own payload/JavaScript tests. Their cached
    # declarations are not registered in each AppTest runtime within this suite.
    for component_module, component_attribute in (
        (page_navigation, "_PAGE_NAVIGATION_CONTROLLER"),
        (url_synchronizer, "_URL_QUERY_SYNCHRONIZER"),
        (documentation_scroll_trigger, "_DOCUMENTATION_SCROLL_TRIGGER"),
    ):
        monkeypatch.setattr(
            component_module,
            component_attribute,
            lambda **_kwargs: None,
        )
    monkeypatch.setattr(
        run_controller,
        "build_analysis_batches",
        lambda *_args, **_kwargs: pytest.fail(
            "Stale local input must never create a provider query"
        ),
    )
    application = AppTest.from_file(
        str(Path(__file__).resolve().parents[2] / "app.py"),
        default_timeout=60,
    )
    initial_state = {
        "_initial_config_loaded": True,
        "input_view": input_view,
        "lang": language,
        "run_mode": direction.upper(),
        "run_id": 77,
        "guided_use_case": f"{direction}_benchmark",
        "guided_reference_design": "local_neighborhood",
        "val_analysis_direction": direction,
        "val_callsign": "G3ZIL",
        "val_qth": "IO90",
        "val_comp_mode": "local_neighborhood",
        "val_local_benchmark": "local_best",
        "val_start_d": date(2026, 7, 1),
        "val_start_t": time(0, 0),
        "val_end_d": date(2026, 7, 2),
        "val_end_t": time(0, 0),
        COMPLETED_RUN_SNAPSHOT_KEY: {
            "schema_version": COMPLETED_RUN_SNAPSHOT_SCHEMA_VERSION,
        },
        EXPORT_STATE_KEY: {"RX_COMPARE": "previous export"},
    }
    for state_key, state_value in initial_state.items():
        application.session_state[state_key] = state_value

    application.run()

    assert list(application.exception) == []
    assert T[language]["err_local_benchmark"] in [
        error.value for error in application.error
    ]
    assert application.session_state["val_local_benchmark"] == "local_best"
    assert application.session_state["run_mode"] is None
    assert application.session_state[EXPORT_STATE_KEY] == {}
    assert COMPLETED_RUN_SNAPSHOT_KEY not in application.session_state
    assert all(widget.key != "val_local_benchmark" for widget in application.radio)

    application.button(key="reset_configuration").click().run()

    assert list(application.exception) == []
    assert application.session_state["val_local_benchmark"] == "local_median"
    assert application.session_state["val_comp_mode"] == "none"
    assert application.session_state["run_mode"] is None
    assert T[language]["err_local_benchmark"] not in [
        error.value for error in application.error
    ]

    for state_key, state_value in initial_state.items():
        if state_key not in {
            "run_mode",
            "val_local_benchmark",
            COMPLETED_RUN_SNAPSHOT_KEY,
            EXPORT_STATE_KEY,
        }:
            application.session_state[state_key] = state_value
    application.session_state["guided_reconstruct_requested"] = True
    application.run()
    application.run()

    assert list(application.exception) == []
    assert application.session_state["val_local_benchmark"] == "local_median"
    assert all(widget.key != "val_local_benchmark" for widget in application.radio)
    local_method_headings = [
        markdown for markdown in application.markdown
        if markdown.value == f"**{T[language]['opt_local_median']}**"
    ]
    assert len(local_method_headings) == 1
    explanation = T[language]["txt_local_median_explanation"]
    visible_captions = [caption.value for caption in application.caption]
    if input_view == "classic":
        assert local_method_headings[0].proto.help == explanation
        assert explanation not in visible_captions
    else:
        assert local_method_headings[0].proto.help == ""
        assert explanation in visible_captions


def test_waiting_status_shows_only_the_sessions_own_queue_position(monkeypatch):
    """Keep global active and waiting counts out of the personal queue status."""
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

    assert [status.label for status in fake_st.statuses] == [
        "All analysis capacity is in use; queued at position 8."
    ]
    assert fake_st.placeholders == []


@pytest.mark.parametrize("language", ["en", "de"])
@pytest.mark.parametrize("direction", ["RX", "TX"])
@pytest.mark.parametrize("phase", [None, "submitted", "queued", "running"])
def test_language_change_preserves_completed_evidence_and_retires_submission(
    monkeypatch, tmp_path, language, direction, phase,
):
    """Keep committed evidence eligible for an implicit localized rerender."""
    fake_st = _FakeStreamlit()
    fake_st.session_state.run_mode = direction
    fake_st.session_state.lang = "de" if language == "en" else "en"
    fake_st.session_state.lang_selector_ui = language.upper()
    analysis = _analysis(f"{direction}_COMP", "Completed map")
    _publish_valid_completed_snapshot(fake_st, analysis, path_root=tmp_path)
    expected_state = dict(fake_st.session_state)
    expected_state["lang"] = language
    if phase is not None:
        token = begin_analysis_submission(fake_st.session_state)
        update_analysis_submission(fake_st.session_state, token, phase=phase)
    monkeypatch.setattr(callbacks, "st", fake_st)

    callbacks.update_lang()

    assert fake_st.session_state == expected_state
    assert get_analysis_submission(fake_st.session_state) is None
    assert claim_analysis_submission_request(fake_st.session_state) is None


@pytest.mark.parametrize("phase", [None, "submitted", "queued", "running"])
@pytest.mark.parametrize("snapshot", [None, {"schema_version": -1}])
def test_language_change_without_completed_evidence_cancels_pending_run(
    monkeypatch, phase, snapshot,
):
    """A language change must not automatically restart unfinished analysis."""
    fake_st = _FakeStreamlit()
    fake_st.session_state.lang_selector_ui = "DE"
    if snapshot is not None:
        fake_st.session_state[COMPLETED_RUN_SNAPSHOT_KEY] = snapshot
    if phase is not None:
        token = begin_analysis_submission(fake_st.session_state)
        update_analysis_submission(fake_st.session_state, token, phase=phase)
    monkeypatch.setattr(callbacks, "st", fake_st)

    callbacks.update_lang()

    assert fake_st.session_state.lang == "de"
    assert fake_st.session_state.run_mode is None
    assert fake_st.session_state.run_id == 77
    assert get_analysis_submission(fake_st.session_state) is None
    assert claim_analysis_submission_request(fake_st.session_state) is None


@pytest.mark.parametrize("input_view", ["guided", "classic"])
@pytest.mark.parametrize("direction", ["rx", "tx"])
@pytest.mark.parametrize("comparison_mode", ["none", "reference_station"])
def test_language_selector_rerenders_completed_result_in_both_editors(
    monkeypatch, input_view, direction, comparison_mode,
):
    """Exercise the real language widget and app routing without a new Run."""
    import streamlit as st
    from ui import documentation_scroll_trigger, page_navigation, url_synchronizer

    for component_module, component_attribute in (
        (page_navigation, "_PAGE_NAVIGATION_CONTROLLER"),
        (url_synchronizer, "_URL_QUERY_SYNCHRONIZER"),
        (documentation_scroll_trigger, "_DOCUMENTATION_SCROLL_TRIGGER"),
    ):
        monkeypatch.setattr(
            component_module, component_attribute, lambda **_kwargs: None,
        )
    rendered_languages = []
    scientific_contexts = []

    def render_completed_result(**kwargs):
        assert kwargs["is_existing_run_rerender"] is True
        language = st.session_state.lang
        assert kwargs["t"] == T[language]
        rendered_languages.append(language)
        scientific_contexts.append(
            build_analysis_context_from_session_state(st.session_state)
        )
        st.markdown(f"Completed evidence: {language}")

    monkeypatch.setattr(run_controller, "render_analysis_run", render_completed_result)
    application = AppTest.from_file(
        str(Path(__file__).resolve().parents[2] / "app.py"), default_timeout=60,
    )
    snapshot = _completed_no_data_snapshot()
    result_type = "performance" if comparison_mode == "none" else "benchmark"
    initial_state = {
        "_initial_config_loaded": True,
        "input_view": input_view,
        "lang": "en",
        "run_mode": direction.upper(),
        "run_id": 77,
        "guided_use_case": f"{direction}_{result_type}",
        "guided_reference_design": (
            None if comparison_mode == "none" else comparison_mode
        ),
        "val_analysis_direction": direction,
        "val_callsign": "G3ZIL",
        "val_qth": "IO90",
        "val_comp_mode": comparison_mode,
        "val_ref_callsign": "G4HZW",
        "val_ref_qth": "IO83",
        "val_start_d": date(2026, 7, 1),
        "val_start_t": time(0, 0),
        "val_end_d": date(2026, 7, 2),
        "val_end_t": time(0, 0),
        COMPLETED_RUN_SNAPSHOT_KEY: snapshot,
    }
    for state_key, state_value in initial_state.items():
        application.session_state[state_key] = state_value

    application.run()
    assert list(application.exception) == []
    for language in ("de", "en"):
        application.selectbox(key="lang_selector_ui").select(language.upper()).run()
        assert list(application.exception) == []
        assert f"Completed evidence: {language}" in [
            markdown.value for markdown in application.markdown
        ]
        assert application.session_state["run_mode"] == direction.upper()
        assert application.session_state["run_id"] == 77
        assert application.session_state[COMPLETED_RUN_SNAPSHOT_KEY] == snapshot
        assert not application.session_state["configuration_changed_since_run"]

    assert rendered_languages == ["en", "de", "en"]
    assert scientific_contexts == [scientific_contexts[0]] * 3


def test_valid_completed_rerender_is_admitted_without_provider_capacity(
    monkeypatch,
    tmp_path,
):
    """Rebuild presentation from a completed snapshot without query work."""
    fake_st = _FakeStreamlit()
    analysis = _analysis("RX_COMP", "Current translated title")
    _publish_valid_completed_snapshot(
        fake_st,
        analysis,
        path_root=tmp_path,
    )
    acquire_calls = []
    permit = _Context()

    def acquire(**kwargs):
        acquire_calls.append(kwargs)
        return permit

    gate = SimpleNamespace(acquire=acquire, counts=lambda: (0, 0))
    analysis_context, presentation_context = (
        _patch_completed_rerender_environment(
            monkeypatch,
            fake_st,
            gate,
            analysis,
        )
    )
    monkeypatch.setattr(
        run_controller,
        "_try_reserve_upstream_capacity",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("Completed rerender must not reserve provider capacity")
        ),
    )
    monkeypatch.setattr(
        run_controller,
        "prepare_provider_bundle",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("Completed rerender must not prepare query data")
        ),
    )
    completed_calls = []

    def render_completed(**kwargs):
        completed_calls.append(kwargs)
        return "completed"

    monkeypatch.setattr(
        run_controller,
        "_render_completed_analysis_run",
        render_completed,
    )
    render_map_figure = lambda *_args, **_kwargs: None

    outcome = _render_completed_rerender(
        fake_st,
        _RunStatusSlot(),
        render_map_figure,
    )

    assert outcome is None
    assert len(acquire_calls) == 1
    assert acquire_calls[0]["reserve_capacity"] is None
    assert completed_calls[0]["analysis_context"] is analysis_context
    assert completed_calls[0]["presentation_context"] is presentation_context
    assert completed_calls[0]["render_map_figure"] is render_map_figure
    assert fake_st.session_state.run_mode == "RX"
    assert get_completed_run_snapshot(fake_st.session_state) is not None


def test_invalid_completed_rerender_requires_explicit_run_without_admission(
    monkeypatch,
    tmp_path,
):
    """Invalidate stale identity and stop before either admission or database work."""
    fake_st = _FakeStreamlit()
    analysis = _analysis("RX_COMP", "Current translated title")
    _publish_valid_completed_snapshot(
        fake_st,
        analysis,
        path_root=tmp_path,
        request_fingerprint="stale-request-key",
    )
    gate = SimpleNamespace(
        acquire=lambda **_kwargs: (_ for _ in ()).throw(
            AssertionError("Invalid completed result must fail before admission")
        ),
        counts=lambda: (0, 0),
    )
    _patch_completed_rerender_environment(
        monkeypatch,
        fake_st,
        gate,
        analysis,
    )
    monkeypatch.setattr(
        run_controller,
        "prepare_provider_bundle",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("Invalid completed result must not query a database")
        ),
    )

    outcome = _render_completed_rerender(
        fake_st,
        _RunStatusSlot(),
        lambda *_args, **_kwargs: None,
    )

    assert outcome == run_controller.COMPLETED_RUN_RERENDER_UNAVAILABLE
    assert fake_st.warnings == ["Completed result expired."]
    assert fake_st.session_state.run_mode is None
    assert get_completed_run_snapshot(fake_st.session_state) is None
    assert get_active_run_database_source(fake_st.session_state) is None


@pytest.mark.parametrize(
    "invalid_contract",
    [
        "snapshot_schema",
        "map_schema",
        "run_id",
        "request_fingerprint",
        "analysis_plan",
        "database_source",
        "analysis_contract",
        "diagnostic_contract",
        "artifact_registration",
        "artifact_scope",
    ],
)
def test_completed_snapshot_validation_rejects_every_identity_boundary(
    monkeypatch,
    tmp_path,
    invalid_contract,
):
    """Require all version, identity, provenance, and ownership checks together."""
    fake_st = _FakeStreamlit()
    analysis = _analysis("RX_COMP", "Current title")
    _publish_valid_completed_snapshot(
        fake_st,
        analysis,
        path_root=tmp_path,
    )
    snapshot = fake_st.session_state[COMPLETED_RUN_SNAPSHOT_KEY].to_dict()
    fake_st.session_state[COMPLETED_RUN_SNAPSHOT_KEY] = snapshot
    request_fingerprint = "request-key"
    analysis_plan_fingerprint = "analysis-plan-key"
    committed_source = "wd2"
    if invalid_contract == "snapshot_schema":
        snapshot["schema_version"] = 999
    elif invalid_contract == "map_schema":
        snapshot["map_data_schema_version"] = 999
    elif invalid_contract == "run_id":
        snapshot["run_id"] = 999
    elif invalid_contract == "request_fingerprint":
        request_fingerprint = "different-request"
    elif invalid_contract == "analysis_plan":
        analysis_plan_fingerprint = "different-plan"
    elif invalid_contract == "database_source":
        snapshot["database_source"] = "unsupported-source"
        committed_source = "unsupported-source"
        fake_st.session_state["active_run_database_source"]["source_key"] = (
            "unsupported-source"
        )
    elif invalid_contract == "analysis_contract":
        snapshot["analyses"][0]["analysis"]["analysis_kind"] = "opportunity"
    elif invalid_contract == "diagnostic_contract":
        snapshot["analyses"][0].pop("diagnostic")
    elif invalid_contract == "artifact_registration":
        fake_st.session_state[SESSION_ARTIFACT_PATHS_KEY].pop()
    elif invalid_contract == "artifact_scope":
        outside_path = (tmp_path / "outside" / "spots_RX_COMP.parquet").resolve()
        snapshot["analyses"][0]["evidence_path"] = str(outside_path)
        fake_st.session_state[SESSION_ARTIFACT_PATHS_KEY][0] = str(outside_path)
    monkeypatch.setattr(run_controller, "st", fake_st)
    monkeypatch.setattr(run_controller, "CACHE_DIR", tmp_path)

    assert run_controller._validate_completed_run_snapshot(
        analyses=[analysis],
        request_fingerprint=request_fingerprint,
        analysis_plan_fingerprint=analysis_plan_fingerprint,
        committed_source=committed_source,
        session_owner="owner",
    ) is None


@pytest.mark.parametrize("mode", ["RX", "TX"])
def test_completed_performance_snapshot_rejects_pre_consolidation_method(
    monkeypatch, tmp_path, mode,
):
    """Require a fresh run when canonical peer-cycle classification changes."""
    fake_st = _FakeStreamlit()
    old_analysis = {
        **_analysis(f"{mode}_PERFORMANCE", f"{mode} Performance"),
        "absolute_method_version": "opportunity-v1",
    }
    current_analysis = {
        **old_analysis,
        "absolute_method_version": ABSOLUTE_METHOD_VERSION,
    }
    old_plan_fingerprint = run_controller._analysis_plan_fingerprint([old_analysis])
    current_plan_fingerprint = run_controller._analysis_plan_fingerprint([current_analysis])
    assert old_plan_fingerprint != current_plan_fingerprint
    _publish_valid_completed_snapshot(
        fake_st,
        old_analysis,
        path_root=tmp_path,
        analysis_plan_fingerprint=old_plan_fingerprint,
    )
    monkeypatch.setattr(run_controller, "st", fake_st)
    monkeypatch.setattr(run_controller, "CACHE_DIR", tmp_path)
    validation_arguments = {
        "request_fingerprint": "request-key",
        "committed_source": "wd2",
        "session_owner": "owner-token",
    }
    assert run_controller._validate_completed_run_snapshot(
        analyses=[old_analysis],
        analysis_plan_fingerprint=old_plan_fingerprint,
        **validation_arguments,
    ) is not None
    assert run_controller._validate_completed_run_snapshot(
        analyses=[current_analysis],
        analysis_plan_fingerprint=current_plan_fingerprint,
        **validation_arguments,
    ) is None
    # The stored per-analysis contract also rejects old evidence independently
    # of the outer plan fingerprint.
    assert run_controller._validate_completed_run_snapshot(
        analyses=[current_analysis],
        analysis_plan_fingerprint=old_plan_fingerprint,
        **validation_arguments,
    ) is None


def test_completed_snapshot_rejects_artifact_triples_swapped_between_analyses(
    monkeypatch,
    tmp_path,
):
    """Bind every registered artifact filename to its owning analysis ID."""
    fake_st = _FakeStreamlit()
    first_analysis = _analysis("RX_COMP", "Compare")
    second_analysis = _analysis("RX_ABS", "Performance")
    second_analysis.update({
        "analysis_kind": "opportunity",
        "is_compare": False,
    })

    first_snapshot = _publish_valid_completed_snapshot(
        fake_st,
        first_analysis,
        path_root=tmp_path,
    )
    first_registered_paths = list(
        fake_st.session_state[SESSION_ARTIFACT_PATHS_KEY]
    )
    second_snapshot = _publish_valid_completed_snapshot(
        fake_st,
        second_analysis,
        path_root=tmp_path,
    )
    second_registered_paths = list(
        fake_st.session_state[SESSION_ARTIFACT_PATHS_KEY]
    )
    first_entry = first_snapshot.analyses[0].to_dict()
    second_entry = second_snapshot.analyses[0].to_dict()
    artifact_path_keys = (
        "evidence_path",
        "station_rows_path",
        "segment_rows_path",
    )
    swapped_first_entry = {
        **first_entry,
        **{path_key: second_entry[path_key] for path_key in artifact_path_keys},
    }
    swapped_second_entry = {
        **second_entry,
        **{path_key: first_entry[path_key] for path_key in artifact_path_keys},
    }
    fake_st.session_state[SESSION_ARTIFACT_PATHS_KEY] = (
        first_registered_paths + second_registered_paths
    )
    publish_completed_run_snapshot(
        fake_st.session_state,
        {
            **first_snapshot.to_dict(),
            "analyses": (swapped_first_entry, swapped_second_entry),
        },
    )
    monkeypatch.setattr(run_controller, "st", fake_st)
    monkeypatch.setattr(run_controller, "CACHE_DIR", tmp_path)

    assert run_controller._validate_completed_run_snapshot(
        analyses=[first_analysis, second_analysis],
        request_fingerprint="request-key",
        analysis_plan_fingerprint="analysis-plan-key",
        committed_source="wd2",
        session_owner="owner",
    ) is None


@pytest.mark.parametrize(
    "queue_error",
    [
        AnalysisQueueFull("simulated full queue"),
        AnalysisQueueTimeout("simulated queue timeout"),
    ],
)
def test_completed_rerender_queue_pressure_preserves_snapshot_and_run_mode(
    monkeypatch,
    tmp_path,
    queue_error,
):
    """Allow an implicit render retry after temporary analysis-slot pressure."""
    fake_st = _FakeStreamlit()
    analysis = _analysis("RX_COMP", "Current translated title")
    expected_snapshot = _publish_valid_completed_snapshot(
        fake_st,
        analysis,
        path_root=tmp_path,
    )
    acquire_calls = []

    def reject(**kwargs):
        acquire_calls.append(kwargs)
        raise queue_error

    gate = SimpleNamespace(acquire=reject, counts=lambda: (0, 10))
    _patch_completed_rerender_environment(
        monkeypatch,
        fake_st,
        gate,
        analysis,
    )
    run_status_slot = _RunStatusSlot()

    outcome = _render_completed_rerender(
        fake_st,
        run_status_slot,
        lambda *_args, **_kwargs: None,
    )

    assert outcome is None
    assert acquire_calls[0]["reserve_capacity"] is None
    assert fake_st.session_state.run_mode == "RX"
    assert get_completed_run_snapshot(fake_st.session_state) == expected_snapshot
    assert run_status_slot.notices[0][0] == "warning"


def test_completed_renderer_uses_stored_decode_method_and_current_presentation(
    monkeypatch,
    tmp_path,
):
    """Preserve scientific/export provenance while rebuilding localized figures."""
    fake_st = _MapNavigationStreamlit()
    fake_st.session_state.val_min_stations = 3
    existing_export_registry = {"old": "recipe"}
    fake_st.session_state[EXPORT_STATE_KEY] = existing_export_registry
    inspector_cache = object()
    fake_st.session_state[INSPECTOR_CACHE_STATE_KEY] = inspector_cache
    current_analysis = _analysis("RX_COMP", "Aktueller Kartentitel")
    completed_snapshot = _publish_valid_completed_snapshot(
        fake_st,
        current_analysis,
        path_root=tmp_path,
        selected_decode_filter_mode=DECODE_FILTER_LEGACY,
    )
    monkeypatch.setattr(run_controller, "st", fake_st)
    monkeypatch.setattr(
        run_controller,
        "PerformanceTimer",
        lambda: _ProfileTimer(),
    )
    monkeypatch.setattr(
        run_controller,
        "matplotlib_profile_collector",
        lambda *_args, **_kwargs: _Context(),
    )
    map_data = MapData(
        station_rows=pd.DataFrame({
            "SegmentID": ["[0-2500km] N"],
            "dist_label": ["[0-2500km]"],
            "dir_name": ["N"],
            "r_min": [0.0],
            "r_max": [2500.0],
            "az_bucket": [0.0],
            "peer_sign": ["K1ABC"],
            "peer_grid": ["FN31"],
            "peer_lat": [41.5],
            "peer_lon": [-72.5],
            "calc_dist": [6000.0],
            "calc_azimuth": [300.0],
            "spot_count": [4],
            "stat_val": [1.5],
            "count_only_u": [0],
            "count_only_r": [0],
        }),
        segment_rows=pd.DataFrame({
            "SegmentID": ["[0-2500km] N"],
            "dist_label": ["[0-2500km]"],
            "dir_name": ["N"],
            "r_min": [0.0],
            "r_max": [2500.0],
            "az_bucket": [0.0],
            "val": [1.5],
            "cnt": [1],
        }),
        analysis_id="RX_COMP",
        is_compare=True,
        is_sequential=False,
        analysis_kind="comparison",
    )
    run_controller.write_map_data_artifacts(
        map_data,
        run_controller.MapDataArtifactPaths(
            station_rows_path=Path(
                completed_snapshot.to_dict()["analyses"][0]["station_rows_path"]
            ),
            segment_rows_path=Path(
                completed_snapshot.to_dict()["analyses"][0]["segment_rows_path"]
            ),
        ),
    )
    render_calls = []

    def render_map(restored_map_data, **kwargs):
        assert map_results_slot.containers == []
        render_calls.append((restored_map_data, kwargs))
        return SimpleNamespace(figure=object(), map_data=restored_map_data)

    block_calls = []
    map_results_slot = _MapResultsSlot(fake_st)
    map_results_display = run_controller._MapResultsDisplay(map_results_slot)

    def render_block(**kwargs):
        with kwargs["map_results_display"].container():
            block_calls.append(kwargs)
        return {"deferred": True}

    monkeypatch.setattr(
        run_controller,
        "_render_map_result_block",
        render_block,
    )
    deferred_calls = []
    monkeypatch.setattr(
        run_controller,
        "_render_deferred_inspectors",
        lambda entries, **kwargs: deferred_calls.append((entries, kwargs)),
    )
    presentation_context = SimpleNamespace(language="de", theme="dark")
    analysis_context = SimpleNamespace(max_peer_distance_km=22000)
    permit = SimpleNamespace(touch=lambda: True)

    outcome = run_controller._render_completed_analysis_run(
        t={**T["de"], "msg_loading": "Laden", "warn_no_data": "Keine Daten: {title}"},
        run_status_slot=_RunStatusSlot(),
        start_t="start",
        end_t="end",
        render_map_figure=render_map,
        admission_permit=permit,
        analyses=[current_analysis],
        analysis_context=analysis_context,
        presentation_context=presentation_context,
        center_latitude=47.0,
        center_longitude=8.0,
        completed_run_snapshot=completed_snapshot,
        map_results_display=map_results_display,
    )

    assert outcome == "completed"
    assert len(map_results_slot.containers) == 1
    pd.testing.assert_frame_equal(
        render_calls[0][0].station_rows,
        map_data.station_rows,
    )
    assert render_calls[0][0].analysis_id == "RX_COMP"
    assert render_calls[0][1]["title"] == "Aktueller Kartentitel"
    assert render_calls[0][1]["presentation_context"] is presentation_context
    assert block_calls[0]["analysis"]["decode_filter_mode"] == DECODE_FILTER_LEGACY
    assert block_calls[0]["analysis"]["title"] == "Aktueller Kartentitel"
    assert block_calls[0]["presentation_context"] is presentation_context
    assert block_calls[0]["is_first_map"] is True
    assert block_calls[0]["map_results_display"] is map_results_display
    assert block_calls[0].get("navigation_submission_token") is None
    assert block_calls[0]["parquet_path"] == Path(
        completed_snapshot.to_dict()["analyses"][0]["evidence_path"]
    )
    assert block_calls[0]["map_data_paths"] == run_controller.MapDataArtifactPaths(
        station_rows_path=Path(
            completed_snapshot.to_dict()["analyses"][0]["station_rows_path"]
        ),
        segment_rows_path=Path(
            completed_snapshot.to_dict()["analyses"][0]["segment_rows_path"]
        ),
    )
    assert deferred_calls[0][0] == [{"deferred": True}]
    assert fake_st.session_state[EXPORT_STATE_KEY] is existing_export_registry
    assert (
        fake_st.session_state[INSPECTOR_CACHE_STATE_KEY]
        is inspector_cache
    )
    assert get_completed_run_snapshot(fake_st.session_state) == completed_snapshot
    audit_text = fake_st.placeholders[0].markdowns[-1]
    assert "strict: **disk cache**" in audit_text
    assert "legacy: **RAM cache**" in audit_text


def test_completed_render_failure_retires_snapshot_without_database_fallback(
    monkeypatch,
    tmp_path,
):
    """Convert corrupt aggregate rendering into an explicit-run warning."""
    fake_st = _FakeStreamlit()
    fake_st.session_state.val_min_stations = 3
    analysis = _analysis("RX_COMP", "Current title")
    completed_snapshot = _publish_valid_completed_snapshot(
        fake_st,
        analysis,
        path_root=tmp_path,
    )
    monkeypatch.setattr(run_controller, "st", fake_st)
    monkeypatch.setattr(
        run_controller,
        "PerformanceTimer",
        lambda: _ProfileTimer(),
    )
    monkeypatch.setattr(
        run_controller,
        "matplotlib_profile_collector",
        lambda *_args, **_kwargs: _Context(),
    )
    monkeypatch.setattr(
        run_controller,
        "read_map_data_artifacts",
        lambda *_args, **_kwargs: SimpleNamespace(
            station_rows=pd.DataFrame({"corrupt": [object()]})
        ),
    )
    monkeypatch.setattr(
        run_controller,
        "prepare_provider_bundle",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("A restoration failure must not query a provider")
        ),
    )

    outcome = run_controller._render_completed_analysis_run(
        t={
            "msg_loading": "Loading",
            "warn_no_data": "No data: {title}",
            "warn_analysis_cache_expired": "Completed result expired.",
        },
        run_status_slot=_RunStatusSlot(),
        start_t="start",
        end_t="end",
        render_map_figure=lambda *_args, **_kwargs: (_ for _ in ()).throw(
            TypeError("corrupt aggregate dtype")
        ),
        admission_permit=SimpleNamespace(touch=lambda: True),
        analyses=[analysis],
        analysis_context=SimpleNamespace(max_peer_distance_km=22000),
        presentation_context=SimpleNamespace(language="en"),
        center_latitude=47.0,
        center_longitude=8.0,
        completed_run_snapshot=completed_snapshot,
    )

    assert outcome == run_controller.COMPLETED_RUN_RERENDER_UNAVAILABLE
    assert fake_st.warnings == ["Completed result expired."]
    assert fake_st.session_state.run_mode is None
    assert get_completed_run_snapshot(fake_st.session_state) is None
    assert get_active_run_database_source(fake_st.session_state) is None
    assert SESSION_ARTIFACT_PATHS_KEY not in fake_st.session_state


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


def test_duplicate_rerun_restores_the_existing_personal_queue_position(monkeypatch):
    """Do not replace a live queued request with the generic duplicate notice."""
    fake_st = _FakeStreamlit()
    run_status_slot = _RunStatusSlot()
    queued_snapshot = AdmissionSnapshot(
        position=1,
        active=0,
        queued=7,
        max_active=2,
        max_queued=10,
    )

    def reject_duplicate(**_kwargs):
        raise AnalysisDuplicateRequest("simulated duplicate")

    gate = SimpleNamespace(
        acquire=reject_duplicate,
        counts=lambda: (0, 7),
        request_snapshot=lambda *_args, **_kwargs: queued_snapshot,
    )
    _patch_admission_presentation_environment(monkeypatch, fake_st, gate)

    followed_requests = []

    def follow_existing(owner, request_key, *, on_update):
        followed_requests.append((owner, request_key))
        on_update(queued_snapshot)

    gate.wait_for_request_completion = follow_existing
    follower_outcome = _render_admission_presentation(
        fake_st,
        run_status_slot,
    )

    assert [status.label for status in fake_st.statuses] == [
        "All analysis capacity is in use; queued at position 1."
    ]
    assert run_status_slot.notices == []
    assert fake_st.session_state.run_mode == "RX"
    assert followed_requests == [("owner", "request-key")]
    assert follower_outcome == run_controller.ANALYSIS_RUN_FOLLOWER_COMPLETED


def test_main_submission_of_loaded_demo_reaches_demo_reservation_policy(monkeypatch):
    """Classify an unchanged loaded demo as a demo after the main Run action."""
    fake_st = _FakeStreamlit()
    fake_st.session_state.active_demo_profile = "vanhamel_rx_calibration"
    submission_token = begin_analysis_submission(
        fake_st.session_state,
        request_source="main_button",
    )
    submission_request = claim_analysis_submission_request(fake_st.session_state)
    assert submission_request is not None
    assert submission_request.token == submission_token
    assert submission_request.source == "main_button"

    reservation_modes = []

    def capture_demo_reservation(
        request_counts,
        *,
        is_demo_run,
        allowed_sources,
    ):
        assert request_counts == {"wspr_live": 0, "wd2": 0, "wd1": 0}
        reservation_modes.append((is_demo_run, allowed_sources))
        return SimpleNamespace()

    def reserve_then_stop(**kwargs):
        kwargs["prepare_capacity"]()
        kwargs["reserve_capacity"]()
        raise AnalysisQueueFull("stop after reservation classification")

    gate = SimpleNamespace(
        acquire=reserve_then_stop,
        counts=lambda: (0, 0),
    )
    _patch_admission_presentation_environment(monkeypatch, fake_st, gate)
    monkeypatch.setattr(
        run_controller,
        "_try_reserve_upstream_capacity",
        capture_demo_reservation,
    )
    monkeypatch.setattr(
        run_controller,
        "_provider_request_counts",
        lambda *_args, **_kwargs: {"wspr_live": 0, "wd2": 0, "wd1": 0},
    )

    _render_admission_presentation(fake_st, _RunStatusSlot())

    assert reservation_modes == [(True, None)]


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

    run_controller._render_fetch_error(
        fetch_result,
        T["en"],
        exclude_special_callsigns=False,
    )

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
        generate_map_plot=lambda *_args, **_kwargs: None,
    )

    run_event = next(
        values
        for event, values in performance_events
        if event == "analysis_run"
    )
    admission_event = next(
        values
        for event, values in performance_events
        if event == "analysis_admission"
    )
    assert admission_event["banner_label"] == "ANALYSIS RUN START"
    assert admission_event["leading_blank_line"] is True
    assert admission_event["started_at_utc"].endswith("+00:00")
    assert admission_event["outcome"] == "admitted"
    assert run_event["outcome"] == "failed"


def test_unexpected_first_render_failure_clears_partial_result_state(
    monkeypatch,
    tmp_path,
):
    """Leave no source, snapshot, or registered artifacts after an exception."""
    fake_st = _FakeStreamlit()
    analysis = _analysis("RX_COMP", "Prior result")
    _publish_valid_completed_snapshot(
        fake_st,
        analysis,
        path_root=tmp_path,
    )
    gate = SimpleNamespace(
        acquire=lambda **_kwargs: _Context(),
        counts=lambda: (0, 0),
    )
    _patch_admission_presentation_environment(monkeypatch, fake_st, gate)
    monkeypatch.setattr(
        run_controller,
        "_render_admitted_analysis_run",
        lambda **_kwargs: (_ for _ in ()).throw(
            RuntimeError("simulated first-render failure")
        ),
    )

    with pytest.raises(RuntimeError, match="first-render failure"):
        _render_admission_presentation(fake_st, _RunStatusSlot())

    assert fake_st.session_state.run_mode is None
    assert get_completed_run_snapshot(fake_st.session_state) is None
    assert get_active_run_database_source(fake_st.session_state) is None
    assert SESSION_ARTIFACT_PATHS_KEY not in fake_st.session_state


def test_each_capacity_attempt_reinspects_source_specific_caches(monkeypatch):
    """Do not retain request estimates across a potentially long queue wait."""
    fake_st = _FakeStreamlit()
    estimates = [
        {"wspr_live": 2, "wd2": 2, "wd1": 2},
        {"wspr_live": 0, "wd2": 2, "wd1": 2},
    ]
    reservations = []
    preparing = False

    def estimate_counts(*_args, **_kwargs):
        assert preparing, "Cache inspection belongs to preparation, not reservation."
        return estimates.pop(0)

    def reserve(counts, **kwargs):
        assert not preparing
        reservations.append((dict(counts), kwargs["allowed_sources"], kwargs["prefer_cache_only"]))

    def retry_then_stop(**kwargs):
        nonlocal preparing
        for _attempt in range(2):
            preparing = True
            kwargs["prepare_capacity"]()
            preparing = False
            kwargs["reserve_capacity"]()
        raise AnalysisQueueFull("stop after fresh reservation attempts")

    gate = SimpleNamespace(acquire=retry_then_stop, counts=lambda: (0, 0))
    _patch_admission_presentation_environment(monkeypatch, fake_st, gate)
    monkeypatch.setattr(
        run_controller, "UPSTREAM_PROVIDER_DISPATCH", SimpleNamespace(try_acquire_run=reserve),
    )
    monkeypatch.setattr(
        run_controller,
        "_provider_request_counts",
        estimate_counts,
    )
    _render_admission_presentation(fake_st, _RunStatusSlot())

    assert estimates == []
    assert reservations == [
        ({"wspr_live": 2, "wd2": 2, "wd1": 2}, None, False),
        ({"wspr_live": 0, "wd2": 2, "wd1": 2}, None, False),
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
        lambda *_args, **_kwargs: pytest.fail("Atomic reservation must not inspect caches."),
    )

    demo_lease = run_controller._try_reserve_upstream_capacity(
        request_counts,
        is_demo_run=True,
        allowed_sources=None,
    )
    assert demo_lease.source_key == "wd2"
    assert demo_lease.used_cache_affinity
    demo_lease.release()

    ordinary_lease = run_controller._try_reserve_upstream_capacity(
        request_counts,
        is_demo_run=False,
        allowed_sources=None,
    )
    assert ordinary_lease.source_key == "wspr_live"
    assert not ordinary_lease.used_cache_affinity
    ordinary_lease.release()

    pinned_lease = run_controller._try_reserve_upstream_capacity(
        request_counts,
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
    language="en",
    exclude_special_callsigns=False,
    map_results_display=None,
):
    """Execute the admitted transactional path without map rendering."""
    fake_st.analysis_run_outcome = run_controller._render_admitted_analysis_run(
        t={
            **T[language],
            "warn_no_data": "No data: {title}",
        },
        run_status_slot=_RunStatusSlot(),
        start_t="start",
        end_t="end",
        generate_map_plot=lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("No map should render for no-data staged results")
        ),
        admission_permit=permit,
        analyses=analyses,
        analysis_context=SimpleNamespace(
            max_peer_distance_km=22000,
            exclude_special_callsigns=exclude_special_callsigns,
        ),
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
        request_fingerprint="request-key",
        analysis_plan_fingerprint="analysis-plan-key",
        map_results_display=map_results_display,
    )
    return fake_st


@pytest.mark.parametrize("leading_no_data", [False, True])
def test_completed_snapshot_is_published_after_compact_map_artifacts_and_ui(
    monkeypatch,
    tmp_path,
    leading_no_data,
):
    """Commit a reusable result only after both map tables and consumers succeed."""
    fake_st = _MapNavigationStreamlit()
    fake_st.session_state.val_min_stations = 1
    navigation_token = begin_analysis_submission(
        fake_st.session_state, request_source="main_button",
    )
    controller = ProviderDispatchController(
        WSPR_DATABASE_PROVIDERS,
        acquire_timeout_seconds=1.0,
        poll_interval_seconds=0.01,
    )
    permit = _AnalysisPermit(controller.try_acquire_run(
        {"wspr_live": 1, "wd2": 1, "wd1": 1}
    ))
    analysis = _analysis("RX_ABS", "Performance")
    evidence_path = tmp_path / "evidence.parquet"
    evidence_path.write_bytes(b"prepared evidence")
    map_paths = run_controller.MapDataArtifactPaths(
        station_rows_path=tmp_path / "map_stations.parquet",
        segment_rows_path=tmp_path / "map_segments.parquet",
    )
    station_rows = pd.DataFrame({
        "SegmentID": ["[0-2500km] N"],
        "dist_label": ["[0-2500km]"],
        "dir_name": ["N"],
        "r_min": [0.0],
        "r_max": [2500.0],
        "az_bucket": [0.0],
        "peer_sign": ["K1ABC"],
        "peer_grid": ["FN31"],
        "peer_lat": [41.5],
        "peer_lon": [-72.5],
        "calc_dist": [6000.0],
        "calc_azimuth": [300.0],
        "spot_count": [4],
        "stat_val": [75.0],
        "opportunities": [4],
        "hits": [3],
        "misses": [1],
        "target_only": [2],
        "target_observations": [5],
        "successful_snr_median": [-12.5],
        "eligible": [True],
        "rate_pct": [75.0],
    })
    segment_rows = pd.DataFrame({
        "SegmentID": ["[0-2500km] N"],
        "dist_label": ["[0-2500km]"],
        "dir_name": ["N"],
        "r_min": [0.0],
        "r_max": [2500.0],
        "az_bucket": [0.0],
        "val": [75.0],
        "cnt": [1],
    })
    map_data = MapData(
        station_rows=station_rows,
        segment_rows=segment_rows,
        analysis_id="RX_ABS",
        is_compare=False,
        is_sequential=False,
        analysis_kind="opportunity",
    )
    prepared_bundle = PreparedProviderBundle(
        database_source=DatabaseSource.WSPR_LIVE,
        analyses=[PreparedAnalysisData(
            analysis=dict(analysis),
            artifact_path=evidence_path,
            warning_message=None,
            query_fetches=(PreparedQueryFetch(
                decode_filter_mode=DECODE_FILTER_STRICT,
                elapsed_seconds=0.1,
                delivery_source=FetchSource.WSPR_LIVE,
            ),),
            profile_timer=_ProfileTimer(),
        )],
    )
    if leading_no_data:
        prepared_bundle = PreparedProviderBundle(
            database_source=prepared_bundle.database_source,
            analyses=[
                *_no_data_bundle(
                    "wspr_live", [_analysis("RX_COMP", "Empty first analysis")],
                ).analyses,
                *prepared_bundle.analyses,
            ],
        )
    _patch_run_environment(
        monkeypatch,
        fake_st,
        controller,
        lambda *_args, **_kwargs: prepared_bundle,
    )
    monkeypatch.setattr(
        run_controller,
        "_staged_artifact_paths",
        lambda _plans, **_kwargs: {
            "RX_ABS": run_controller._StagedAnalysisArtifactPaths(
                evidence_path=evidence_path,
                map_data_paths=map_paths,
            )
        },
    )
    map_read_calls = []

    def read_map_projection(path, *, columns):
        map_read_calls.append((path, columns))
        return pd.DataFrame({"prepared": [1]})

    monkeypatch.setattr(run_controller, "read_parquet_artifact", read_map_projection)
    monkeypatch.setattr(
        run_controller,
        "matplotlib_profile_collector",
        lambda *_args, **_kwargs: _Context(),
    )
    lifecycle_events = []
    rendered_map_blocks = []
    map_results_slot = _MapResultsSlot(fake_st)
    map_results_display = run_controller._MapResultsDisplay(map_results_slot)

    def generate_map(*_args, **_kwargs):
        assert len(map_results_slot.containers) == int(leading_no_data)
        lifecycle_events.append("map generated")
        return MapFigure(
            figure=object(),
            map_data=map_data,
            footer_text="footer",
        )

    def render_map_block(**kwargs):
        with kwargs["map_results_display"].container():
            rendered_map_blocks.append(kwargs)
        lifecycle_events.append("map UI rendered")
        return {"deferred": True}

    monkeypatch.setattr(
        run_controller,
        "_render_map_result_block",
        render_map_block,
    )
    monkeypatch.setattr(
        run_controller,
        "_render_deferred_inspectors",
        lambda *_args, **_kwargs: lifecycle_events.append(
            "inspectors rendered"
        ),
    )
    real_publish_snapshot = run_controller.publish_completed_analysis_run

    def publish_snapshot(session_state, snapshot):
        lifecycle_events.append("snapshot published")
        real_publish_snapshot(session_state, snapshot)

    monkeypatch.setattr(
        run_controller,
        "publish_completed_analysis_run",
        publish_snapshot,
    )

    outcome = run_controller._render_admitted_analysis_run(
        t={**T["en"], "warn_no_data": "No data: {title}"},
        run_status_slot=_RunStatusSlot(),
        start_t="start",
        end_t="end",
        generate_map_plot=generate_map,
        admission_permit=permit,
        analyses=[entry.analysis for entry in prepared_bundle.analyses],
        analysis_context=SimpleNamespace(
            max_peer_distance_km=22000,
            exclude_special_callsigns=False,
        ),
        presentation_context=SimpleNamespace(),
        center_latitude=47.0,
        center_longitude=8.0,
        active_demo=None,
        active_demo_key=None,
        is_demo_run=False,
        request_counts_by_provider={"wspr_live": 1, "wd2": 1, "wd1": 1},
        committed_source=None,
        request_fingerprint="request-key",
        analysis_plan_fingerprint="analysis-plan-key",
        navigation_submission_token=navigation_token,
        map_results_display=map_results_display,
    )

    assert outcome == "completed"
    assert len(map_results_slot.containers) == 1
    assert lifecycle_events == [
        "map generated",
        "map UI rendered",
        "inspectors rendered",
        "snapshot published",
    ]
    assert map_read_calls == [(evidence_path, list(run_controller.map_preparation_columns(
        analysis_kind="opportunity", is_compare=False, is_sequential=False,
    )))]
    assert len(rendered_map_blocks) == 1
    assert rendered_map_blocks[0]["map_data_paths"] == map_paths
    assert rendered_map_blocks[0]["is_first_map"] is True
    assert rendered_map_blocks[0]["map_results_display"] is map_results_display
    assert rendered_map_blocks[0]["navigation_submission_token"] == navigation_token
    assert map_paths.station_rows_path.is_file()
    assert map_paths.segment_rows_path.is_file()
    registered_paths = set(fake_st.session_state[SESSION_ARTIFACT_PATHS_KEY])
    assert registered_paths == {
        str(evidence_path.resolve()),
        str(map_paths.station_rows_path.resolve()),
        str(map_paths.segment_rows_path.resolve()),
    }
    snapshot = get_completed_run_snapshot(fake_st.session_state).to_dict()
    assert snapshot["database_source"] == "wspr_live"
    assert snapshot["analyses"][-1]["outcome"] == (
        run_controller.COMPLETED_RENDERABLE
    )
    assert snapshot["analyses"][-1]["station_rows_path"] == str(
        map_paths.station_rows_path.resolve()
    )

    if leading_no_data:
        assert snapshot["analyses"][0]["outcome"] == (
            run_controller.COMPLETED_PREPARED_NO_DATA
        )


def test_diagnosed_nonrenderable_performance_skips_map_and_inspector_content(
    monkeypatch,
    tmp_path,
):
    fake_st = _FakeStreamlit()
    fake_st.session_state.val_min_stations = 2
    controller = ProviderDispatchController(
        WSPR_DATABASE_PROVIDERS,
        acquire_timeout_seconds=1.0,
        poll_interval_seconds=0.01,
    )
    permit = _AnalysisPermit(controller.try_acquire_run(
        {"wspr_live": 1, "wd2": 1, "wd1": 1}
    ))
    analysis = _analysis("RX_ABS", "Performance")
    evidence_path = tmp_path / "evidence.parquet"
    evidence_path.write_bytes(b"prepared evidence")
    diagnostic = ResultDiagnostic.create(
        PERFORMANCE_NO_ELIGIBLE_STATION,
        applied_thresholds={
            "min_confirmed_opportunities_per_peer": 5,
            "min_joint_stations_per_map_segment": 2,
        },
        measured_counts={
            "station_identity_count": 8,
            "eligible_station_count": 0,
            "maximum_confirmed_opportunities_per_station": 3,
        },
    )
    prepared_bundle = PreparedProviderBundle(
        database_source=DatabaseSource.WSPR_LIVE,
        analyses=[PreparedAnalysisData(
            analysis=dict(analysis),
            artifact_path=evidence_path,
            warning_message=None,
            query_fetches=(PreparedQueryFetch(
                decode_filter_mode=DECODE_FILTER_STRICT,
                elapsed_seconds=0.1,
                delivery_source=FetchSource.WSPR_LIVE,
            ),),
            profile_timer=_ProfileTimer(),
        )],
    )
    _patch_run_environment(
        monkeypatch,
        fake_st,
        controller,
        lambda *_args, **_kwargs: prepared_bundle,
    )
    monkeypatch.setattr(
        run_controller,
        "read_parquet_artifact",
        lambda _path, *, columns: pd.DataFrame({"prepared": [1]}),
    )
    monkeypatch.setattr(
        run_controller,
        "matplotlib_profile_collector",
        lambda *_args, **_kwargs: _Context(),
    )
    monkeypatch.setattr(
        run_controller,
        "_render_map_result_block",
        lambda **_kwargs: pytest.fail("non-renderable result reached map UI"),
    )
    deferred_inspector_inputs = []
    monkeypatch.setattr(
        run_controller,
        "_render_deferred_inspectors",
        lambda values, **_kwargs: deferred_inspector_inputs.extend(values),
    )

    outcome = run_controller._render_admitted_analysis_run(
        t={
            **T["en"],
            "warn_no_data": "No data: {title}",
            "warn_performance_no_eligible_station": (
                "{station_identity_count} stations; maximum "
                "{maximum_confirmed_opportunities_per_station}; minimum "
                "{minimum_confirmed_opportunities_per_station}."
            ),
        },
        run_status_slot=_RunStatusSlot(),
        start_t="start",
        end_t="end",
        generate_map_plot=lambda *_args, **_kwargs: EmptyMapResult(diagnostic),
        admission_permit=permit,
        analyses=[analysis],
        analysis_context=SimpleNamespace(
            max_peer_distance_km=22000,
            exclude_special_callsigns=False,
        ),
        presentation_context=SimpleNamespace(),
        center_latitude=47.0,
        center_longitude=8.0,
        active_demo=None,
        active_demo_key=None,
        is_demo_run=False,
        request_counts_by_provider={"wspr_live": 1, "wd2": 1, "wd1": 1},
        committed_source=None,
        request_fingerprint="request-key",
        analysis_plan_fingerprint="analysis-plan-key",
    )

    assert outcome == "completed"
    assert deferred_inspector_inputs == []
    assert fake_st.warnings == ["8 stations; maximum 3; minimum 5."]
    snapshot = get_completed_run_snapshot(fake_st.session_state).to_dict()
    assert snapshot["analyses"][0]["outcome"] == (
        run_controller.COMPLETED_MAP_NO_DATA
    )
    assert snapshot["analyses"][0]["diagnostic"] == diagnostic.to_dict()
    assert fake_st.statuses[0].updates[-1] == {
        "label": "Complete",
        "state": "complete",
        "expanded": True,
    }


@pytest.mark.parametrize("is_demo_run", [False, True])
def test_malformed_numeric_csv_restarts_complete_bundle_on_wd2(
    monkeypatch,
    tmp_path,
    is_demo_run,
):
    """Reject malformed HTTP-200 evidence before cache or result publication."""
    from core import data_engine, run_data_preparation

    fake_st = _FakeStreamlit()
    controller = ProviderDispatchController(
        WSPR_DATABASE_PROVIDERS,
        acquire_timeout_seconds=1.0,
        poll_interval_seconds=0.01,
    )
    request_counts = {provider.key: 2 for provider in WSPR_DATABASE_PROVIDERS}
    permit = _AnalysisPermit(controller.try_acquire_run(request_counts))
    analyses = [
        _analysis("RX_COMP", "RX Compare"),
        _analysis("TX_COMP", "TX Compare"),
    ]
    for analysis in analyses:
        analysis["is_sequential"] = True
        analysis.pop("legacy_query")
        analysis.pop("legacy_decode_filter_mode")

    providers_by_url = {
        provider.url: provider for provider in WSPR_DATABASE_PROVIDERS
    }
    requests_received = []
    filtered_rows = []
    fetch_failures = []
    first_primary_artifact = tmp_path / "staged" / "wspr_live" / "RX_COMP.parquet"

    def receive_csv_request(url, *, params, **_kwargs):
        provider = providers_by_url[url]
        query = params["query"]
        requests_received.append((provider.key, query))
        assert get_active_run_database_source(fake_st.session_state) is None
        assert get_completed_run_snapshot(fake_st.session_state) is None

        if provider.key == "wspr_live":
            peer_sign = "K1AAA"
            if query == analyses[0]["query"]:
                statistic = "-12.3"
            else:
                assert query == analyses[1]["query"]
                assert first_primary_artifact.is_file()
                statistic = "broken"
        else:
            assert provider.key == "wd2"
            assert not first_primary_artifact.exists()
            peer_sign = "K2BBB"
            statistic = "-8.4"

        payload = (
            "time,peer_sign,peer_grid,peer_lat,peer_lon,snr,power,stat_val,is_me\n"
            f"2026-09-01 00:00:00,{peer_sign},FN31,41.5,-72.5,-12,23,{statistic},1\n"
        ).encode("utf-8")
        return nullcontext(SimpleNamespace(
            status_code=200,
            encoding="utf-8",
            headers={},
            iter_content=lambda chunk_size: iter([payload]),
        ))

    def filter_validated_rows(frame, analysis, *_args, **_kwargs):
        peer_sign = frame.loc[0, "peer_sign"]
        if peer_sign == "K1AAA" and analysis["id"] == "TX_COMP":
            pytest.fail("Malformed primary rows reached scientific filtering")
        filtered_rows.append((peer_sign, analysis["id"], frame.loc[0, "stat_val"]))
        if peer_sign == "K1AAA":
            return frame, None
        # Complete the replacement bundle through the real no-data path while
        # keeping map rendering outside this decoding/failover regression.
        return frame.iloc[0:0], None

    def prepare_real_bundle(plans, **kwargs):
        try:
            return run_data_preparation.prepare_provider_bundle(
                plans,
                **kwargs,
                fetch_data=data_engine.fetch_wspr_data,
                post_fetch_filter=filter_validated_rows,
            )
        except ProviderBundleFetchError as exc:
            fetch_failures.append(exc.fetch_result)
            raise

    _patch_run_environment(monkeypatch, fake_st, controller, prepare_real_bundle)
    monkeypatch.setattr(data_engine, "CACHE_DIR", tmp_path / "query-cache")
    monkeypatch.setattr(data_engine, "_dataframe_cache", OrderedDict())
    monkeypatch.setattr(data_engine, "_result_row_limit_cache", OrderedDict())
    monkeypatch.setattr(data_engine.http_session, "get", receive_csv_request)
    monkeypatch.setattr(
        run_controller,
        "_staged_artifact_paths",
        lambda plans, *, provider_key: {
            plan["id"]: run_controller._StagedAnalysisArtifactPaths(
                evidence_path=(
                    tmp_path / "staged" / provider_key / f"{plan['id']}.parquet"
                ),
                map_data_paths=run_controller.MapDataArtifactPaths(
                    station_rows_path=tmp_path / "unused_stations.parquet",
                    segment_rows_path=tmp_path / "unused_segments.parquet",
                ),
            )
            for plan in plans
        },
    )

    _render_fake_run(
        fake_st,
        permit,
        analyses,
        is_demo_run=is_demo_run,
        request_counts_by_provider=request_counts,
    )

    assert requests_received == [
        ("wspr_live", analyses[0]["query"]),
        ("wspr_live", analyses[1]["query"]),
        ("wd2", analyses[0]["query"]),
        ("wd2", analyses[1]["query"]),
    ]
    assert len(fetch_failures) == 1
    assert fetch_failures[0].error.code == "decode_error"
    assert fetch_failures[0].error.scope == FetchFailureScope.PROVIDER
    assert fetch_failures[0].dataframe is None
    assert [(peer_sign, analysis_id) for peer_sign, analysis_id, _ in filtered_rows] == [
        ("K1AAA", "RX_COMP"),
        ("K2BBB", "RX_COMP"),
        ("K2BBB", "TX_COMP"),
    ]
    assert [statistic for _, _, statistic in filtered_rows] == pytest.approx(
        [-12.3, -8.4, -8.4]
    )
    assert not first_primary_artifact.exists()
    primary_provider = WSPR_DATABASE_PROVIDERS[0]
    assert not data_engine._query_cache_path(
        analyses[1]["query"],
        primary_provider,
        is_demo=is_demo_run,
    ).exists()
    assert not data_engine.is_wspr_query_cached(
        analyses[1]["query"],
        is_demo=is_demo_run,
        database_provider=primary_provider,
    )
    assert controller.snapshot("wspr_live").consecutive_failures == 1
    assert controller.snapshot("wd2").consecutive_failures == 0
    assert fake_st.analysis_run_outcome == "completed"
    assert fake_st.errors == []
    assert get_active_run_database_source(fake_st.session_state) == "wd2"
    snapshot = get_completed_run_snapshot(fake_st.session_state).to_dict()
    assert snapshot["database_source"] == "wd2"
    assert len(snapshot["analyses"]) == 2
    assert all(
        query_fetch["delivery_source"] == FetchSource.WD2.value
        for analysis_snapshot in snapshot["analyses"]
        for query_fetch in analysis_snapshot["query_fetches"]
    )


def test_provider_failure_restarts_active_compare_analysis_on_wd2(monkeypatch):
    """Retry one active Compare analysis and retain its strict-to-legacy audit."""
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
    analyses = [_analysis("RX_COMP", "Compare")]
    attempts = []

    def fake_prepare(plans, *, provider_lease, **_kwargs):
        attempts.append((provider_lease.source_key, [plan["id"] for plan in plans]))
        if provider_lease.source_key == "wspr_live":
            raise _provider_failure(provider_lease.source_key, plans[0])
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
        ("wspr_live", ["RX_COMP"]),
        ("wd2", ["RX_COMP"]),
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


def test_two_provider_failures_restart_active_success_analysis_on_wd1(
    monkeypatch,
):
    fake_st = _FakeStreamlit()
    controller = ProviderDispatchController(
        WSPR_DATABASE_PROVIDERS,
        acquire_timeout_seconds=1.0,
        poll_interval_seconds=0.01,
    )
    permit = _AnalysisPermit(controller.try_acquire_run(
        {"wspr_live": 1, "wd2": 1, "wd1": 1}
    ))
    analyses = [_analysis("RX_ABS", "Performance")]
    attempts = []

    def fake_prepare(plans, *, provider_lease, **_kwargs):
        attempts.append((provider_lease.source_key, [plan["id"] for plan in plans]))
        if provider_lease.source_key != "wd1":
            raise _provider_failure(provider_lease.source_key, plans[0])
        return _no_data_bundle(provider_lease.source_key, plans)

    _patch_run_environment(monkeypatch, fake_st, controller, fake_prepare)
    _render_fake_run(fake_st, permit, analyses)

    assert attempts == [
        ("wspr_live", ["RX_ABS"]),
        ("wd2", ["RX_ABS"]),
        ("wd1", ["RX_ABS"]),
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
    analyses = [_analysis("RX_ABS", "Performance")]
    attempts = []

    def fake_prepare(plans, *, provider_lease, **_kwargs):
        attempts.append(provider_lease.source_key)
        if provider_lease.source_key == "wd2":
            raise _provider_failure(provider_lease.source_key, plans[0])
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
    analyses = [_analysis("RX_ABS", "Performance")]
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
    analyses = [_analysis("RX_COMP", "Compare")]
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
    analyses = [_analysis("RX_COMP", "Compare")]
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
    analyses = [_analysis("RX_ABS", "Performance")]
    attempts = []

    def fake_prepare(plans, *, provider_lease, **_kwargs):
        attempts.append(provider_lease.source_key)
        raise _provider_failure(provider_lease.source_key, plans[0])

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
    analyses = [_analysis("RX_ABS", "Performance")]
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


@pytest.mark.parametrize("language", ["en", "de"])
@pytest.mark.parametrize("exclude_special_callsigns", [False, True])
def test_result_row_limit_warning_is_localized_and_does_not_fail_over(
    monkeypatch,
    language,
    exclude_special_callsigns,
):
    """Treat the safety stop as the user's request outcome, not provider health."""
    fake_st = _FakeStreamlit()
    fake_st.session_state.lang = language
    controller = ProviderDispatchController(
        WSPR_DATABASE_PROVIDERS,
        acquire_timeout_seconds=1.0,
        poll_interval_seconds=0.01,
    )
    permit = _AnalysisPermit(controller.try_acquire_run(
        {"wspr_live": 1, "wd2": 1, "wd1": 1}
    ))
    analyses = [_analysis("RX_ABS", "Performance")]
    attempts = []

    def fake_prepare(plans, *, provider_lease, **_kwargs):
        attempts.append(provider_lease.source_key)
        raise ProviderBundleFetchError(
            FetchResult(
                source=FetchSource.WSPR_LIVE,
                database_source=DatabaseSource.WSPR_LIVE,
                error=FetchError(
                    code="result_row_limit_exceeded",
                    message="technical row limit detail",
                    scope=FetchFailureScope.REQUEST,
                    query="SELECT private_query_text",
                    failure_stage="validate_csv_result_rows",
                ),
            ),
            plans[0],
        )

    _patch_run_environment(monkeypatch, fake_st, controller, fake_prepare)
    _render_fake_run(
        fake_st,
        permit,
        analyses,
        language=language,
        exclude_special_callsigns=exclude_special_callsigns,
    )

    special_callsign_advice = (
        ""
        if exclude_special_callsigns
        else T[language][
            "warn_analysis_result_row_limit_special_callsign_advice"
        ].format(
            special_callsign_label=T[language]["lbl_exclude_special"],
        )
    )
    expected_warning = T[language]["warn_analysis_result_row_limit"].format(
        max_rows=("1,000,000" if language == "en" else "1.000.000"),
        special_callsign_advice=special_callsign_advice,
        max_peer_distance_label=T[language]["lbl_max_dist"],
        neighborhood_radius_label=T[language]["lbl_ref_radius_km"],
    )
    assert fake_st.analysis_run_outcome == "failed"
    assert attempts == ["wspr_live"]
    assert controller.snapshot("wspr_live").consecutive_failures == 0
    assert get_active_run_database_source(fake_st.session_state) is None
    assert fake_st.warnings == [expected_warning]
    assert fake_st.errors == []
    assert fake_st.codes == []
    assert fake_st.statuses[0].label == T[language][
        "status_analysis_result_row_limit"
    ]
    assert T[language]["status_analysis_result_row_limit"] in (
        fake_st.placeholders[0].markdowns[-1]
    )
    assert "could not complete the data bundle" not in (
        fake_st.placeholders[0].markdowns[-1]
    )


@pytest.mark.parametrize(
    ("language", "expected_message"),
    [
        (
            "en",
            "Analysis evidence could not be prepared. "
            "Please run the analysis again.",
        ),
        (
            "de",
            "Die Analyse-Evidenz konnte nicht vorbereitet werden. "
            "Bitte führe die Analyse erneut aus.",
        ),
    ],
)
def test_local_preparation_failure_does_not_switch_or_penalize_database(
    monkeypatch,
    language,
    expected_message,
):
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
    analyses = [_analysis("RX_ABS", "Performance")]
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
    _render_fake_run(fake_st, permit, analyses, language=language)

    assert attempts == ["wspr_live"]
    assert controller.snapshot("wspr_live").consecutive_failures == 0
    assert get_active_run_database_source(fake_st.session_state) is None
    assert fake_st.statuses[0].label == expected_message
    assert fake_st.errors == [expected_message]
    visible_status_text = " ".join(
        placeholder_text
        for placeholder in fake_st.placeholders
        for placeholder_text in placeholder.markdowns
    )
    assert "invalid local transformation" not in visible_status_text
    assert fake_st.session_state.run_mode is None
    assert fake_st.analysis_run_outcome == "failed"
    assert performance_events == [(
        "analysis_preparation_failure",
        {
            "source": "wspr_live",
            "failure_scope": "local",
            "failure_type": "ProviderBundlePreparationError",
            "technical_error": "invalid local transformation",
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
    analyses = [_analysis("RX_ABS", "Performance")]
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
    analyses = [_analysis("RX_ABS", "Performance")]
    attempts = []

    def fake_prepare(plans, *, provider_lease, **_kwargs):
        attempts.append(provider_lease.source_key)
        raise _provider_failure(provider_lease.source_key, plans[0])

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
    })
    controller = ProviderDispatchController(
        WSPR_DATABASE_PROVIDERS,
        acquire_timeout_seconds=1.0,
        poll_interval_seconds=0.01,
    )
    permit = _AnalysisPermit(controller.try_acquire_run(
        {"wspr_live": 1, "wd2": 1, "wd1": 1}
    ))
    analyses = [_analysis("RX_ABS", "Performance")]

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
    analyses = [_analysis("RX_COMP", "Compare")]

    def fake_prepare(plans, *, provider_lease, on_legacy_retry, **_kwargs):
        if provider_lease.source_key == "wspr_live":
            on_legacy_retry(0, len(plans), plans[0])
            raise _provider_failure(provider_lease.source_key, plans[0])
        return _no_data_bundle(provider_lease.source_key, plans)

    _patch_run_environment(monkeypatch, fake_st, controller, fake_prepare)
    _render_fake_run(fake_st, permit, analyses)

    final_audit = fake_st.placeholders[0].markdowns[-1]
    assert "strict `code = 1` found no target-side evidence" not in final_audit


class _MapNavigationPlaceholder(_Placeholder):
    def __init__(self):
        super().__init__()
        self.captions = []
        self.empty_calls = 0

    def container(self):
        return _Context()

    def caption(self, text):
        self.captions.append(text)

    def empty(self):
        self.empty_calls += 1


class _MapNavigationContainer(_Context):
    def __init__(self, streamlit):
        self.streamlit = streamlit
        self.parent_containers = streamlit.active_containers
        self._context_stack = []

    def __enter__(self):
        self._context_stack.append(self.streamlit.active_containers)
        self.streamlit.active_containers = (*self.parent_containers, self)
        return self

    def __exit__(self, *_args):
        self.streamlit.active_containers = self._context_stack.pop()
        return False

    def markdown(self, text, **kwargs):
        self.streamlit.markdown(text, **kwargs)

    def empty(self):
        return self.streamlit.empty()


class _MapNavigationStreamlit(_FakeStreamlit):
    def __init__(self):
        super().__init__()
        self.active_containers = ()
        self.notice_contexts = []

    def error(self, message):
        self.notice_contexts.append(self.active_containers)
        super().error(message)

    def warning(self, message):
        self.notice_contexts.append(self.active_containers)
        super().warning(message)

    def container(self, **_kwargs):
        return _MapNavigationContainer(self)

    def empty(self):
        placeholder = _MapNavigationPlaceholder()
        self.placeholders.append(placeholder)
        return placeholder

    def markdown(self, text, **_kwargs):
        super().markdown(text)

    def caption(self, _text):
        pass

    def columns(self, count):
        return [_Context() for _index in range(count)]

    def selectbox(self, *_args, **_kwargs):
        pass


@pytest.fixture
def map_navigation_harness(monkeypatch):
    """Exercise real map/Inspector orchestration while replacing external UI work."""
    fake_st = _MapNavigationStreamlit()
    fake_st.session_state.val_min_stations = 1
    token = begin_analysis_submission(fake_st.session_state, request_source="main_button")
    events = []
    anchors = []
    markers = []
    monkeypatch.setattr(run_controller, "st", fake_st)
    monkeypatch.setattr(
        run_controller, "build_result_context",
        lambda *_args: SimpleNamespace(title="Map context"),
    )
    monkeypatch.setattr(run_controller, "result_context_html", lambda _context: "Map context")
    monkeypatch.setattr(run_controller, "render_result_guidance_popover", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(run_controller, "matplotlib_profile_collector", lambda *_args: _Context())
    monkeypatch.setattr(run_controller, "render_analysis_map_anchor", anchors.append)

    def mark_ready(submission_token, **kwargs):
        events.append("map ready")
        markers.append((submission_token, kwargs["image_container_key"]))

    monkeypatch.setattr(run_controller, "render_analysis_map_ready_marker", mark_ready)
    monkeypatch.setattr(run_controller, "register_map_export_context", lambda _payload: events.append("export registered"))
    monkeypatch.setattr(run_controller, "dispose_matplotlib_figure", lambda _figure: events.append("figure disposed"))
    monkeypatch.setattr(run_controller, "render_matplotlib_figure", lambda *_args, **_kwargs: events.append("map drawn"))
    monkeypatch.setattr(run_controller, "render_segment_inspector", lambda *_args, **_kwargs: events.append("Inspector rendered"))

    def render_block(*, first_map=True, navigation_token=token, map_results_display=None):
        return run_controller._render_map_result_block(
            t=T["en"],
            analysis=_analysis("RX_ABS", "Performance"),
            plot_result=SimpleNamespace(
                figure=object(),
                map_data=SimpleNamespace(station_rows=pd.DataFrame()),
                footer_text="footer",
            ),
            parquet_path=Path("evidence.parquet"),
            map_data_paths=SimpleNamespace(),
            start_t="start",
            end_t="end",
            loading_label="Loading",
            max_peer_distance_km=22000,
            center_latitude=47.0,
            center_longitude=8.0,
            analysis_context=SimpleNamespace(),
            presentation_context=SimpleNamespace(language="en"),
            database_source="wspr_live",
            profile_timer=_ProfileTimer(),
            is_first_map=first_map,
            navigation_submission_token=navigation_token,
            map_results_display=map_results_display,
        )

    def render_inspectors(entries):
        run_controller._render_deferred_inspectors(
            entries,
            t=T["en"],
            admission_permit=SimpleNamespace(touch=lambda: True),
            max_peer_distance_km=22000,
            analysis_context=SimpleNamespace(),
            presentation_context=SimpleNamespace(language="en"),
        )

    return SimpleNamespace(
        streamlit=fake_st, token=token, events=events, anchors=anchors,
        markers=markers, render_block=render_block, render_inspectors=render_inspectors,
    )


@pytest.mark.parametrize("scenario", [
    "current", "later_map", "completed_rerender", "replaced_during_render",
    "cancelled_during_render", "render_failure",
])
def test_map_ready_marker_follows_successful_render_and_current_submission(
    monkeypatch, map_navigation_harness, scenario,
):
    """Signal only the owning first map, after image emission and before Inspector work."""
    harness = map_navigation_harness
    replacement_token = None

    def draw_map(*_args, **_kwargs):
        nonlocal replacement_token
        assert harness.markers == []
        harness.events.append("map drawing started")
        if scenario == "replaced_during_render":
            replacement_token = handoff_analysis_submission(
                harness.streamlit.session_state, request_source="input_view_change",
            )
        elif scenario == "cancelled_during_render":
            cancel_analysis_submission(harness.streamlit.session_state)
        elif scenario == "render_failure":
            raise RuntimeError("map rendering failed")
        harness.events.append("map drawn")

    monkeypatch.setattr(run_controller, "render_matplotlib_figure", draw_map)
    if scenario == "render_failure":
        with pytest.raises(RuntimeError, match="map rendering failed"):
            harness.render_block()
        assert harness.events == ["map drawing started", "figure disposed"]
        assert harness.markers == []
        return

    entry = harness.render_block(
        first_map=scenario != "later_map",
        navigation_token=None if scenario == "completed_rerender" else harness.token,
    )
    harness.render_inspectors([entry])
    if scenario == "current":
        assert harness.markers == [(harness.token, "results_evidence_level_1_RX_ABS_77")]
        assert harness.events.index("map drawn") < harness.events.index("map ready")
        assert harness.events.index("map ready") < harness.events.index("Inspector rendered")
    else:
        assert harness.markers == []
    assert harness.anchors == (
        [] if scenario == "later_map"
        else [None if scenario == "completed_rerender" else harness.token]
    )
    assert "figure disposed" in harness.events
    assert harness.events[-1] == "Inspector rendered"
    if replacement_token is not None:
        assert get_analysis_submission(harness.streamlit.session_state).token == replacement_token


@pytest.mark.parametrize("inspector_fails", [False, True])
def test_deferred_inspector_clears_loading_caption_on_success_and_failure(
    monkeypatch, map_navigation_harness, inspector_fails,
):
    """Retain a visible ready map without leaving an endless Inspector-loading caption."""
    harness = map_navigation_harness
    entry = harness.render_block()

    def render_inspector(*_args, **_kwargs):
        loading = harness.streamlit.placeholders[-1]
        assert loading.captions == [T["en"]["msg_preparing_inspector"]]
        assert loading.empty_calls == 0
        assert entry["skeleton_ph"].empty_calls == 1
        if inspector_fails:
            raise RuntimeError("Inspector preparation failed")

    monkeypatch.setattr(run_controller, "render_segment_inspector", render_inspector)
    if inspector_fails:
        with pytest.raises(RuntimeError, match="Inspector preparation failed"):
            harness.render_inspectors([entry])
    else:
        harness.render_inspectors([entry])
    assert harness.streamlit.placeholders[-1].empty_calls == 1
    assert harness.markers == [(harness.token, "results_evidence_level_1_RX_ABS_77")]


class _MapResultsSlot:
    """Record when the cleared area receives a container, including its ancestry."""

    def __init__(self, streamlit):
        self.streamlit = streamlit
        self.containers = []

    def container(self):
        container = _MapNavigationContainer(self.streamlit)
        self.containers.append(container)
        return container


@pytest.mark.parametrize("use_slot", [False, True])
def test_map_display_opens_lazily_and_keeps_maps_and_inspectors_in_one_region(
    monkeypatch, map_navigation_harness, use_slot,
):
    """Keep the clear delta intact until map output and retain deferred-child ancestry."""
    harness = map_navigation_harness
    slot = _MapResultsSlot(harness.streamlit)
    display = run_controller._MapResultsDisplay(slot if use_slot else None)
    assert slot.containers == []
    map_contexts = []
    inspector_contexts = []
    monkeypatch.setattr(
        run_controller, "render_matplotlib_figure",
        lambda *_args, **_kwargs: map_contexts.append(harness.streamlit.active_containers),
    )
    monkeypatch.setattr(
        run_controller, "render_segment_inspector",
        lambda *_args, **_kwargs: inspector_contexts.append(harness.streamlit.active_containers),
    )

    first_entry = harness.render_block(map_results_display=display)
    assert len(slot.containers) == int(use_slot)
    second_entry = harness.render_block(first_map=False, map_results_display=display)
    assert len(slot.containers) == int(use_slot)
    assert harness.streamlit.active_containers == ()
    harness.render_inspectors([first_entry, second_entry])

    assert len(map_contexts) == len(inspector_contexts) == 2
    for map_context, inspector_context, entry in zip(
        map_contexts, inspector_contexts, [first_entry, second_entry], strict=True,
    ):
        assert inspector_context[-1] is entry["inspector_container"]
        assert inspector_context[-1].parent_containers == map_context[:-1]
        if use_slot:
            assert map_context[0] is slot.containers[0]
            assert inspector_context[0] is slot.containers[0]
        else:
            assert len(map_context) == 3
            assert len(inspector_context) == 3
    assert harness.streamlit.active_containers == ()
    assert len(slot.containers) == int(use_slot)
    assert harness.markers == [(harness.token, "results_evidence_level_1_RX_ABS_77")]


@pytest.mark.parametrize("preparation_fails", [False, True])
def test_no_data_and_preparation_errors_open_the_map_slot_only_for_final_notices(
    monkeypatch, preparation_fails,
):
    """Keep preparation empty, then place terminal notices in the stable map region."""
    fake_st = _MapNavigationStreamlit()
    slot = _MapResultsSlot(fake_st)
    display = run_controller._MapResultsDisplay(slot)
    controller = ProviderDispatchController(
        WSPR_DATABASE_PROVIDERS,
        acquire_timeout_seconds=1.0,
        poll_interval_seconds=0.01,
    )
    permit = _AnalysisPermit(controller.try_acquire_run(
        {"wspr_live": 1, "wd2": 1, "wd1": 1}
    ))
    analyses = [_analysis("RX_ABS", "Performance")]
    prepared = []

    def prepare(plans, *, provider_lease, **_kwargs):
        assert slot.containers == []
        assert fake_st.active_containers == ()
        prepared.append(provider_lease.source_key)
        if preparation_fails:
            raise ProviderBundlePreparationError("invalid prepared evidence")
        return _no_data_bundle(provider_lease.source_key, plans)

    _patch_run_environment(monkeypatch, fake_st, controller, prepare)
    _render_fake_run(fake_st, permit, analyses, map_results_display=display)

    assert prepared == ["wspr_live"]
    assert len(slot.containers) == 1
    assert fake_st.notice_contexts == [(slot.containers[0],)]
    assert fake_st.active_containers == ()
    if preparation_fails:
        assert fake_st.analysis_run_outcome == "failed"
        assert fake_st.errors == [T["en"]["err_analysis_processing_failed"]]
    else:
        assert fake_st.analysis_run_outcome == "completed"
        assert fake_st.warnings == ["No data: Performance"]
        assert fake_st.errors == []


@pytest.mark.parametrize("completed_rerender", [False, True])
def test_public_controller_preserves_empty_map_slot_until_the_executor_uses_it(
    monkeypatch, tmp_path, completed_rerender,
):
    """Keep new output lazy while retaining the existing completed-result container."""
    fake_st = _MapNavigationStreamlit()
    slot = _MapResultsSlot(fake_st)
    existing_container = (
        _MapNavigationContainer(fake_st) if completed_rerender else None
    )
    executor_calls = []

    def acquire(**_kwargs):
        assert slot.containers == []
        return _Context()

    gate = SimpleNamespace(acquire=acquire, counts=lambda: (0, 0))
    if completed_rerender:
        analysis = _analysis("RX_COMP", "Completed map")
        _publish_valid_completed_snapshot(fake_st, analysis, path_root=tmp_path)
        _patch_completed_rerender_environment(monkeypatch, fake_st, gate, analysis)
        executor_name = "_render_completed_analysis_run"
    else:
        _patch_admission_presentation_environment(monkeypatch, fake_st, gate)
        executor_name = "_render_admitted_analysis_run"

    def execute(**kwargs):
        assert slot.containers == []
        executor_calls.append(kwargs)
        with kwargs["map_results_display"].container():
            expected_container = (
                existing_container if completed_rerender else slot.containers[0]
            )
            assert fake_st.active_containers == (expected_container,)
        return "completed"

    monkeypatch.setattr(run_controller, executor_name, execute)
    outcome = run_controller.render_analysis_run(
        t=T["en"],
        run_status_slot=_RunStatusSlot(),
        callsign="G3ZIL",
        qth_locator="IO90",
        band_filter=7,
        start_t=SimpleNamespace(isoformat=lambda: "start"),
        end_t=SimpleNamespace(isoformat=lambda: "end"),
        generate_map_plot=lambda *_args, **_kwargs: None,
        render_map_figure=lambda *_args, **_kwargs: None,
        is_existing_run_rerender=completed_rerender,
        map_results_slot=None if completed_rerender else slot,
        map_results_container=existing_container,
    )

    assert outcome is None
    assert len(executor_calls) == 1
    assert len(slot.containers) == int(not completed_rerender)
    assert fake_st.active_containers == ()


def test_existing_map_container_is_reused_without_clearing_or_nesting(monkeypatch):
    """Retain completed-result geometry while replacing its contents in the same region."""
    fake_st = _MapNavigationStreamlit()
    existing_container = _MapNavigationContainer(fake_st)

    def reject_clear_or_child(*_args, **_kwargs):
        pytest.fail("An existing result region must not be cleared or given another wrapper.")

    monkeypatch.setattr(existing_container, "empty", reject_clear_or_child)
    monkeypatch.setattr(existing_container, "container", reject_clear_or_child, raising=False)
    display = run_controller._MapResultsDisplay(existing_container=existing_container)
    for _map_index in range(2):
        assert display.container() is existing_container
        with display.container():
            assert fake_st.active_containers == (existing_container,)
        assert fake_st.active_containers == ()
