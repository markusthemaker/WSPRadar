from pathlib import Path

import pandas as pd
import pytest

from config import WSPR_DATABASE_PROVIDERS
from core.analysis_runner import DECODE_FILTER_LEGACY, DECODE_FILTER_STRICT
from core.fetch_models import (
    DatabaseSource,
    FetchError,
    FetchFailureScope,
    FetchResult,
    FetchSource,
)
from core.provider_dispatch import ProviderDispatchController
from core.run_data_preparation import (
    ProviderBundleFetchError,
    ProviderBundlePreparationError,
    prepare_provider_bundle,
)


def _analysis_plans():
    return [
        {
            "id": "RX_COMP",
            "title": "Compare",
            "analysis_kind": "comparison",
            "is_sequential": False,
            "decode_filter_mode": DECODE_FILTER_STRICT,
            "legacy_decode_filter_mode": DECODE_FILTER_LEGACY,
            "query": "COMPARE STRICT",
            "legacy_query": "COMPARE LEGACY",
            "response_format": "csv",
        },
        {
            "id": "RX_ABS",
            "title": "Success",
            "analysis_kind": "opportunity",
            "is_sequential": False,
            "decode_filter_mode": DECODE_FILTER_STRICT,
            "legacy_decode_filter_mode": DECODE_FILTER_LEGACY,
            "query": "SUCCESS STRICT",
            "legacy_query": "SUCCESS LEGACY",
            "response_format": "parquet",
        },
    ]


def _controller():
    return ProviderDispatchController(
        WSPR_DATABASE_PROVIDERS,
        acquire_timeout_seconds=1.0,
        poll_interval_seconds=0.01,
    )


def _direct_source(provider_key):
    return {
        "wspr_live": FetchSource.WSPR_LIVE,
        "wd2": FetchSource.WD2,
        "wd1": FetchSource.WD1,
    }[provider_key]


def _result(provider_key, frame=None, error=None):
    return FetchResult(
        dataframe=frame,
        source=_direct_source(provider_key),
        database_source=DatabaseSource(provider_key),
        error=error,
    )


def _comparison_frame(*, has_u=1):
    """Return one production-shaped simultaneous Compare response row."""
    return pd.DataFrame({
        "time_slot": [1],
        "peer_sign": ["PEER"],
        "peer_grid": ["JN37"],
        "peer_lat": [47.0],
        "peer_lon": [8.0],
        "snr_u_norm": [-10.0],
        "snr_r_norm": [-12.0],
        "has_u": [has_u],
        "has_r": [1],
        "best_ref_sign": ["REF"],
        "best_ref_dist": [1000.0],
    })


def _opportunity_frame(*, target_seen=1, external_seen=1):
    """Return one production-shaped Success query response row."""
    return pd.DataFrame({
        "time_slot": [1],
        "peer_sign": ["PEER"],
        "peer_grid": ["JN37"],
        "target_seen": [target_seen],
        "external_seen": [external_seen],
        "target_snr": [-15.0],
    })


def _post_fetch(frame, *_args, **_kwargs):
    return frame, None


def _artifact_paths(tmp_path):
    return {
        "RX_COMP": tmp_path / "compare.parquet",
        "RX_ABS": tmp_path / "success.parquet",
    }


@pytest.mark.parametrize(
    ("fetch_source", "expected_label"),
    [
        (FetchSource.WSPR_LIVE, "database request"),
        (FetchSource.WD2, "database request"),
        (FetchSource.WD1, "database request"),
        (FetchSource.MEMORY_CACHE, "RAM cache"),
        (FetchSource.DISK_CACHE, "disk cache"),
    ],
)
def test_fetch_source_delivery_label_separates_origin_from_tier(
    fetch_source,
    expected_label,
):
    """Use one generic direct-request label while retaining cache-tier names."""
    assert fetch_source.delivery_label == expected_label


def test_complete_bundle_keeps_strict_legacy_compare_and_success_on_one_source(tmp_path):
    controller = _controller()
    lease = controller.try_acquire_run({"wspr_live": 4, "wd2": 4, "wd1": 4})
    requests = []

    def fake_fetch(query, *, database_provider, request_permit, **_kwargs):
        requests.append((database_provider.key, query))
        request_permit.consume_request()
        if query == "COMPARE STRICT":
            return _result(database_provider.key, _comparison_frame(has_u=0))
        if query == "COMPARE LEGACY":
            return _result(database_provider.key, _comparison_frame(has_u=1))
        return _result(database_provider.key, _opportunity_frame())

    bundle = prepare_provider_bundle(
        _analysis_plans(),
        provider_lease=lease,
        is_demo_run=False,
        analysis_context=object(),
        center_latitude=47.0,
        center_longitude=8.0,
        labels={"warn_no_data": "No data: {title}"},
        artifact_paths=_artifact_paths(tmp_path),
        fetch_data=fake_fetch,
        post_fetch_filter=_post_fetch,
    )
    lease.report_success()
    lease.release()

    assert bundle.database_source == DatabaseSource.WSPR_LIVE
    assert requests == [
        ("wspr_live", "COMPARE STRICT"),
        ("wspr_live", "COMPARE LEGACY"),
        ("wspr_live", "SUCCESS STRICT"),
    ]
    assert bundle.analyses[0].analysis["decode_filter_mode"] == DECODE_FILTER_LEGACY
    assert [
        query_fetch.decode_filter_mode
        for query_fetch in bundle.analyses[0].query_fetches
    ] == [DECODE_FILTER_STRICT, DECODE_FILTER_LEGACY]
    assert [
        query_fetch.decode_filter_mode
        for query_fetch in bundle.analyses[1].query_fetches
    ] == [DECODE_FILTER_STRICT]
    assert all(item.artifact_path.is_file() for item in bundle.analyses)


def test_query_fetch_trace_preserves_strict_and_legacy_tiers_and_timings(tmp_path):
    """Keep each executed query's tier and duration instead of only the last."""
    plans = [_analysis_plans()[0]]
    controller = _controller()
    lease = controller.try_acquire_run({"wspr_live": 2, "wd2": 2, "wd1": 2})
    clock_values = iter([10.0, 10.125, 20.0, 20.75])

    def fake_fetch(query, *, database_provider, **_kwargs):
        if query == "COMPARE STRICT":
            return FetchResult(
                dataframe=_comparison_frame(has_u=0),
                source=FetchSource.MEMORY_CACHE,
                database_source=DatabaseSource(database_provider.key),
            )
        return FetchResult(
            dataframe=_comparison_frame(has_u=1),
            source=FetchSource.DISK_CACHE,
            database_source=DatabaseSource(database_provider.key),
        )

    bundle = prepare_provider_bundle(
        plans,
        provider_lease=lease,
        is_demo_run=True,
        analysis_context=object(),
        center_latitude=47.0,
        center_longitude=8.0,
        labels={"warn_no_data": "No data: {title}"},
        artifact_paths={"RX_COMP": tmp_path / "compare.parquet"},
        fetch_data=fake_fetch,
        post_fetch_filter=_post_fetch,
        clock=lambda: next(clock_values),
    )
    lease.report_success()
    lease.release()

    prepared_analysis = bundle.analyses[0]
    assert [
        (
            query_fetch.decode_filter_mode,
            query_fetch.delivery_source,
            query_fetch.elapsed_seconds,
        )
        for query_fetch in prepared_analysis.query_fetches
    ] == [
        (DECODE_FILTER_STRICT, FetchSource.MEMORY_CACHE, 0.125),
        (DECODE_FILTER_LEGACY, FetchSource.DISK_CACHE, 0.75),
    ]
    assert prepared_analysis.fetch_seconds == pytest.approx(0.875)
    assert prepared_analysis.delivery_source == FetchSource.DISK_CACHE
    assert [
        (row["span"], row["seconds"], row["detail"])
        for row in prepared_analysis.profile_timer.rows()
        if row["span"].startswith("fetch ")
    ] == [
        ("fetch strict", 0.125, "wspr.live via RAM cache"),
        ("fetch legacy compatibility", 0.75, "wspr.live via disk cache"),
    ]


def test_operational_strict_failure_never_triggers_legacy_query(tmp_path):
    controller = _controller()
    lease = controller.try_acquire_run({"wspr_live": 4, "wd2": 4, "wd1": 4})
    requests = []

    def fake_fetch(query, *, database_provider, request_permit, **_kwargs):
        requests.append(query)
        request_permit.consume_request()
        return _result(database_provider.key, error=FetchError(
            code="timeout",
            message="timed out",
            scope=FetchFailureScope.PROVIDER,
        ))

    with pytest.raises(ProviderBundleFetchError) as exc_info:
        prepare_provider_bundle(
            _analysis_plans(),
            provider_lease=lease,
            is_demo_run=False,
            analysis_context=object(),
            center_latitude=47.0,
            center_longitude=8.0,
            labels={"warn_no_data": "No data: {title}"},
            artifact_paths=_artifact_paths(tmp_path),
            fetch_data=fake_fetch,
            post_fetch_filter=_post_fetch,
        )
    lease.release()

    assert exc_info.value.fetch_result.error.scope == FetchFailureScope.PROVIDER
    assert requests == ["COMPARE STRICT"]
    assert list(tmp_path.glob("*.parquet")) == []


def test_later_fetch_failure_removes_earlier_unpublished_stage(tmp_path):
    controller = _controller()
    lease = controller.try_acquire_run({"wspr_live": 4, "wd2": 4, "wd1": 4})

    def fake_fetch(query, *, database_provider, request_permit, **_kwargs):
        request_permit.consume_request()
        if query == "COMPARE STRICT":
            return _result(database_provider.key, _comparison_frame())
        return _result(database_provider.key, error=FetchError(
            code="http_error",
            message="unavailable",
            scope=FetchFailureScope.PROVIDER,
            status_code=503,
        ))

    with pytest.raises(ProviderBundleFetchError):
        prepare_provider_bundle(
            _analysis_plans(),
            provider_lease=lease,
            is_demo_run=False,
            analysis_context=object(),
            center_latitude=47.0,
            center_longitude=8.0,
            labels={"warn_no_data": "No data: {title}"},
            artifact_paths=_artifact_paths(tmp_path),
            fetch_data=fake_fetch,
            post_fetch_filter=_post_fetch,
        )
    lease.release()

    assert list(tmp_path.glob("*.parquet")) == []


def test_valid_empty_strict_and_legacy_responses_do_not_become_provider_errors(tmp_path):
    plans = [_analysis_plans()[0]]
    controller = _controller()
    lease = controller.try_acquire_run({"wspr_live": 2, "wd2": 2, "wd1": 2})
    requests = []

    def fake_fetch(query, *, database_provider, request_permit, **_kwargs):
        requests.append((database_provider.key, query))
        request_permit.consume_request()
        return _result(database_provider.key)

    bundle = prepare_provider_bundle(
        plans,
        provider_lease=lease,
        is_demo_run=False,
        analysis_context=object(),
        center_latitude=47.0,
        center_longitude=8.0,
        labels={"warn_no_data": "No data: {title}"},
        artifact_paths={"RX_COMP": tmp_path / "compare.parquet"},
        fetch_data=fake_fetch,
        post_fetch_filter=_post_fetch,
    )
    lease.report_success()
    lease.release()

    assert requests == [
        ("wspr_live", "COMPARE STRICT"),
        ("wspr_live", "COMPARE LEGACY"),
    ]
    assert bundle.analyses[0].artifact_path is None
    assert bundle.analyses[0].warning_message == "No data: Compare"
    assert [
        query_fetch.decode_filter_mode
        for query_fetch in bundle.analyses[0].query_fetches
    ] == [DECODE_FILTER_STRICT, DECODE_FILTER_LEGACY]


@pytest.mark.parametrize(
    ("plan_index", "delivery_source"),
    [
        (0, FetchSource.MEMORY_CACHE),
        (1, FetchSource.DISK_CACHE),
    ],
)
def test_cached_schema_error_invalidates_query_and_replans_capacity(
    tmp_path,
    plan_index,
    delivery_source,
):
    """Discard incompatible cached rows before replanning provider capacity."""
    plan = _analysis_plans()[plan_index]
    controller = _controller()
    lease = controller.try_acquire_run({"wspr_live": 0, "wd2": 0, "wd1": 0})
    invalidations = []

    def fake_fetch(_query, *, database_provider, **_kwargs):
        return FetchResult(
            dataframe=pd.DataFrame({"unexpected": [1]}),
            source=delivery_source,
            database_source=DatabaseSource(database_provider.key),
        )

    def capture_invalidation(
        query,
        *,
        is_demo,
        response_format,
        database_provider,
    ):
        invalidations.append({
            "query": query,
            "is_demo": is_demo,
            "response_format": response_format,
            "database_provider": database_provider,
        })

    with pytest.raises(ProviderBundleFetchError) as exc_info:
        prepare_provider_bundle(
            [plan],
            provider_lease=lease,
            is_demo_run=True,
            analysis_context=object(),
            center_latitude=47.0,
            center_longitude=8.0,
            labels={"warn_no_data": "No data: {title}"},
            artifact_paths={plan["id"]: tmp_path / "analysis.parquet"},
            fetch_data=fake_fetch,
            post_fetch_filter=_post_fetch,
            query_cache_invalidator=capture_invalidation,
        )
    lease.release()

    assert exc_info.value.fetch_result.error.code == "schema_error"
    assert exc_info.value.fetch_result.error.scope == FetchFailureScope.CAPACITY
    assert invalidations == [{
        "query": plan["query"],
        "is_demo": True,
        "response_format": plan["response_format"],
        "database_provider": WSPR_DATABASE_PROVIDERS[0],
    }]


def test_nonempty_incompatible_schema_is_provider_scoped(tmp_path):
    plans = [_analysis_plans()[1]]
    controller = _controller()
    lease = controller.try_acquire_run({"wspr_live": 1, "wd2": 1, "wd1": 1})

    def fake_fetch(_query, *, database_provider, request_permit, **_kwargs):
        request_permit.consume_request()
        return _result(
            database_provider.key,
            pd.DataFrame({"target_seen": [1], "external_seen": [1]}),
        )

    with pytest.raises(ProviderBundleFetchError) as exc_info:
        prepare_provider_bundle(
            plans,
            provider_lease=lease,
            is_demo_run=False,
            analysis_context=object(),
            center_latitude=47.0,
            center_longitude=8.0,
            labels={"warn_no_data": "No data: {title}"},
            artifact_paths={"RX_ABS": Path(tmp_path / "success.parquet")},
            fetch_data=fake_fetch,
            post_fetch_filter=_post_fetch,
        )
    lease.release()

    assert exc_info.value.fetch_result.error.code == "schema_error"
    assert exc_info.value.fetch_result.error.scope == FetchFailureScope.PROVIDER


def test_header_only_incompatible_csv_schema_is_provider_scoped(tmp_path):
    """Reject one-line maintenance/error text parsed as an empty CSV frame."""
    plans = [_analysis_plans()[0]]
    controller = _controller()
    lease = controller.try_acquire_run({"wspr_live": 1, "wd2": 1, "wd1": 1})

    def fake_fetch(_query, *, database_provider, request_permit, **_kwargs):
        request_permit.consume_request()
        return _result(
            database_provider.key,
            pd.DataFrame(columns=["<html>temporarily unavailable</html>"]),
        )

    with pytest.raises(ProviderBundleFetchError) as exc_info:
        prepare_provider_bundle(
            plans,
            provider_lease=lease,
            is_demo_run=False,
            analysis_context=object(),
            center_latitude=47.0,
            center_longitude=8.0,
            labels={"warn_no_data": "No data: {title}"},
            artifact_paths={"RX_COMP": Path(tmp_path / "compare.parquet")},
            fetch_data=fake_fetch,
            post_fetch_filter=_post_fetch,
        )
    lease.release()

    assert exc_info.value.fetch_result.error.code == "schema_error"
    assert exc_info.value.fetch_result.error.scope == FetchFailureScope.PROVIDER


def test_partial_comparison_schema_is_provider_scoped(tmp_path):
    """Reject marker-only Compare rows before local processing can raise."""
    plans = [_analysis_plans()[0]]
    controller = _controller()
    lease = controller.try_acquire_run({"wspr_live": 1, "wd2": 1, "wd1": 1})

    def fake_fetch(_query, *, database_provider, request_permit, **_kwargs):
        request_permit.consume_request()
        return _result(database_provider.key, pd.DataFrame({"has_u": [1]}))

    with pytest.raises(ProviderBundleFetchError) as exc_info:
        prepare_provider_bundle(
            plans,
            provider_lease=lease,
            is_demo_run=False,
            analysis_context=object(),
            center_latitude=47.0,
            center_longitude=8.0,
            labels={"warn_no_data": "No data: {title}"},
            artifact_paths={"RX_COMP": Path(tmp_path / "compare.parquet")},
            fetch_data=fake_fetch,
            post_fetch_filter=_post_fetch,
        )
    lease.release()

    assert exc_info.value.fetch_result.error.code == "schema_error"
    assert exc_info.value.fetch_result.error.scope == FetchFailureScope.PROVIDER


def test_partial_sequential_comparison_schema_is_provider_scoped(tmp_path):
    """Reject marker-only sequential Compare rows before local processing."""
    plan = {
        **_analysis_plans()[0],
        "id": "TX_COMP",
        "is_sequential": True,
    }
    controller = _controller()
    lease = controller.try_acquire_run({"wspr_live": 1, "wd2": 1, "wd1": 1})

    def fake_fetch(_query, *, database_provider, request_permit, **_kwargs):
        request_permit.consume_request()
        return _result(database_provider.key, pd.DataFrame({"is_me": [1]}))

    with pytest.raises(ProviderBundleFetchError) as exc_info:
        prepare_provider_bundle(
            [plan],
            provider_lease=lease,
            is_demo_run=False,
            analysis_context=object(),
            center_latitude=47.0,
            center_longitude=8.0,
            labels={"warn_no_data": "No data: {title}"},
            artifact_paths={"TX_COMP": Path(tmp_path / "compare.parquet")},
            fetch_data=fake_fetch,
            post_fetch_filter=_post_fetch,
        )
    lease.release()

    assert exc_info.value.fetch_result.error.code == "schema_error"
    assert exc_info.value.fetch_result.error.scope == FetchFailureScope.PROVIDER


def test_local_median_requires_contributor_detail_column(tmp_path):
    """Treat missing Local Median contributor detail as provider incompatibility."""
    plan = {
        **_analysis_plans()[0],
        "is_local_median": True,
    }
    controller = _controller()
    lease = controller.try_acquire_run({"wspr_live": 1, "wd2": 1, "wd1": 1})

    def fake_fetch(_query, *, database_provider, request_permit, **_kwargs):
        request_permit.consume_request()
        return _result(database_provider.key, _comparison_frame())

    with pytest.raises(ProviderBundleFetchError) as exc_info:
        prepare_provider_bundle(
            [plan],
            provider_lease=lease,
            is_demo_run=False,
            analysis_context=object(),
            center_latitude=47.0,
            center_longitude=8.0,
            labels={"warn_no_data": "No data: {title}"},
            artifact_paths={"RX_COMP": Path(tmp_path / "compare.parquet")},
            fetch_data=fake_fetch,
            post_fetch_filter=_post_fetch,
        )
    lease.release()

    assert exc_info.value.fetch_result.error.code == "schema_error"
    assert "ref_detail_rows" in exc_info.value.fetch_result.error.message


def test_post_filter_exception_becomes_controlled_local_preparation_error(tmp_path):
    """Keep deterministic local processing failures out of provider failover."""
    plans = _analysis_plans()
    controller = _controller()
    lease = controller.try_acquire_run({"wspr_live": 2, "wd2": 2, "wd1": 2})

    def fake_fetch(query, *, database_provider, request_permit, **_kwargs):
        request_permit.consume_request()
        frame = (
            _comparison_frame()
            if query == "COMPARE STRICT"
            else _opportunity_frame()
        )
        return _result(database_provider.key, frame)

    def failing_post_fetch(frame, analysis, *_args, **_kwargs):
        if analysis["id"] == "RX_ABS":
            raise ValueError("invalid local transformation")
        return frame, None

    with pytest.raises(ProviderBundlePreparationError) as exc_info:
        prepare_provider_bundle(
            plans,
            provider_lease=lease,
            is_demo_run=False,
            analysis_context=object(),
            center_latitude=47.0,
            center_longitude=8.0,
            labels={"warn_no_data": "No data: {title}"},
            artifact_paths=_artifact_paths(tmp_path),
            fetch_data=fake_fetch,
            post_fetch_filter=failing_post_fetch,
        )
    lease.release()

    assert "invalid local transformation" in str(exc_info.value)
    assert list(tmp_path.glob("*.parquet")) == []
