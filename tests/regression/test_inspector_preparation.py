"""Coordinator contracts for cache reuse, lazy reads, and compact evidence."""

from dataclasses import replace
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from core.analysis_context import AnalysisContext, COMPARISON_REFERENCE_STATION
from core.presentation_context import PresentationContext
from i18n import T
from ui.inspector import preparation
from ui.inspector.contracts import InspectorContext, InspectorScope, StationInsightsView
from ui.result_state import INSPECTOR_CACHE_STATE_KEY


def _context(*, is_compare=False, language="en"):
    return InspectorContext(
        analysis_id="TX_COMP" if is_compare else "TX_ABS",
        title="Evidence", is_compare=is_compare, is_sequential=False,
        parquet_path="unused.parquet", line1_str="", translations=T[language],
        max_peer_distance_km=2000,
        analysis_context=AnalysisContext(
            run_mode="TX", callsign="DL1MKS", qth="JN37", band="20m",
            comparison_mode=COMPARISON_REFERENCE_STATION,
            reference_callsign="DL2XYZ", reference_qth="JO62",
            min_confirmed_opportunities_per_peer=1,
        ),
        presentation_context=PresentationContext(
            language=language, labels=T[language], theme="dark", solar_label="All",
        ),
        analysis_kind="comparison" if is_compare else "opportunity", run_id=7,
        analysis_start_t=pd.Timestamp("2026-05-27T00:00:00Z"),
        analysis_end_t=pd.Timestamp("2026-05-27T02:00:00Z"),
    )


def _scope():
    return InspectorScope(
        selected_ranges=(), selected_directions=(), range_summary="Full Range",
        direction_summary="All Directions", selected_segment="Full Range | All Directions",
        active_scope_summary="Full Range | All Directions", scope_token="scope",
        distance_scope_intervals=((0.0, 2000.0),),
    )


def test_coordinator_creation_is_lazy_and_cache_remains_run_scoped(monkeypatch):
    reads = []
    monkeypatch.setattr(preparation, "read_parquet_artifact", lambda *a, **k: reads.append(a))
    state = {}
    coordinator = preparation.InspectorPreparation(state, 7)
    assert state == {}
    assert reads == []
    assert coordinator.cache_put("selected", ("key",), b"recipe")
    first_cache = state[INSPECTOR_CACHE_STATE_KEY]
    assert coordinator.cache_get("selected", ("key",)) == (b"recipe", True)
    next_run = preparation.InspectorPreparation(state, 8)
    assert next_run.cache_get("selected", ("key",)) == (None, False)
    assert state[INSPECTOR_CACHE_STATE_KEY] is not first_cache
    assert state[INSPECTOR_CACHE_STATE_KEY].max_bytes == preparation.INSPECTOR_CACHE_MAX_BYTES
    assert state[INSPECTOR_CACHE_STATE_KEY].namespace_limits == preparation.INSPECTOR_CACHE_NAMESPACE_LIMITS
    assert reads == []


def test_options_cache_does_not_retain_source_or_repeat_preparation(monkeypatch):
    source = pd.DataFrame({"source": [1, 2]})
    calls = []
    options = SimpleNamespace(valid_distances=["[0-1000] km"], valid_directions=["N"])
    def build(rows, **kwargs):
        calls.append((rows, kwargs))
        return options
    monkeypatch.setattr(preparation, "build_inspector_options", build)
    coordinator = preparation.InspectorPreparation({}, 7)
    assert coordinator.prepare_options(source, analysis_id="TX_COMP", max_peer_distance_km=2000) is options
    assert coordinator.prepare_options(source, analysis_id="TX_COMP", max_peer_distance_km=2000) is options
    assert len(calls) == 1
    assert calls[0][0] is source
    coordinator.prepare_options(source, analysis_id="TX_COMP", max_peer_distance_km=3000)
    assert len(calls) == 2


@pytest.mark.parametrize("is_compare", [False, True])
def test_scope_cache_hit_uses_original_key_and_reuses_scope_rows(monkeypatch, is_compare):
    context, scope = _context(is_compare=is_compare), _scope()
    scope_rows = pd.DataFrame({"untouched": [1]})
    coordinator = preparation.InspectorPreparation({}, 7)
    _, _, bin_token = preparation.compare_temporal_time_bin_policy(
        context.analysis_start_t, context.analysis_end_t, "auto",
    )
    if is_compare:
        key = (
            48, "comparison", "TX_COMP", (), (), False,
            int(context.analysis_context.tx_ab_repeat_interval_minutes),
            int(context.analysis_context.tx_ab_target_start_minute),
            int(context.analysis_context.tx_ab_reference_start_minute),
            str(context.analysis_start_t), str(context.analysis_end_t), bin_token,
            "en", "dark", "Evidence", scope.selected_segment,
        )
        method = coordinator.prepare_benchmark_segment
    else:
        key = (
            48, "opportunity", preparation.SUCCESS_DISTANCE_BINNING_VERSION,
            preparation.SUCCESS_SNR_BASELINE_VERSION, "TX_ABS",
            (T["en"]["opt_full_range"],), (T["en"]["opt_all_dirs"],),
            ((0.0, 2000.0),), 1, str(context.analysis_start_t),
            str(context.analysis_end_t), "en", "dark", "Evidence",
            scope.selected_segment, bin_token,
        )
        method = coordinator.prepare_performance_segment
    bundle = {"cached": "existing compact recipe"}
    coordinator.cache_put("segment", key, bundle)
    prepared = method(context, scope, scope_rows, retained_time_bin="auto")
    assert prepared.cache_key == key
    assert prepared.bundle is bundle
    assert prepared.scope_rows is scope_rows
    pd.testing.assert_frame_equal(scope_rows, pd.DataFrame({"untouched": [1]}))


@pytest.mark.parametrize("failure", [FileNotFoundError("expired"), KeyError("schema"), ValueError("projection")])
def test_performance_read_failure_preserves_narrow_boundary(monkeypatch, failure):
    context, scope = _context(), _scope()
    rows = pd.DataFrame({"peer_sign": ["K1AAA"], "peer_grid": ["FN31"]})
    def fail(*args, **kwargs):
        raise failure
    monkeypatch.setattr(preparation, "read_parquet_artifact", fail)
    coordinator = preparation.InspectorPreparation({}, 7)
    with pytest.raises(preparation.InspectorArtifactReadError) as caught:
        coordinator.prepare_performance_segment(context, scope, rows, retained_time_bin="auto")
    assert caught.value.original_exception is failure
    assert caught.value.is_missing == isinstance(failure, FileNotFoundError)
    # Missing source identity is not misreported as an expired/invalid artifact.
    with pytest.raises(KeyError):
        coordinator.prepare_performance_segment(context, scope, pd.DataFrame({"other": [1]}), retained_time_bin="auto")


def test_selected_benchmark_cold_warm_preserves_native_evidence_and_input(monkeypatch):
    context = _context(is_compare=True)
    identities = pd.DataFrame({"peer_sign": ["K1AAA"], "peer_grid": ["FN31"]})
    first_slot = int(context.analysis_start_t.timestamp()) // 120
    rows = pd.DataFrame({
        "peer_sign": ["K1AAA"] * 3, "peer_grid": ["FN31"] * 3,
        "time_slot": [first_slot, first_slot + 1, first_slot + 2],
        "has_u": [1, 1, 1], "has_r": [1, 1, 0],
        "snr_u_norm": [-8.25, -4.75, -9.0], "snr_r_norm": [-10.0, -8.0, np.nan],
    })
    source_copy = rows.copy(deep=True)
    builds = []
    native_metrics = []
    original = preparation._build_compare_unit_rows
    def record(*args, **kwargs):
        builds.append(1)
        comparison_units = original(*args, **kwargs)
        native_metrics.extend(comparison_units["metric"].dropna().tolist())
        return comparison_units
    monkeypatch.setattr(preparation, "_build_compare_unit_rows", record)
    coordinator = preparation.InspectorPreparation({}, 7)
    kwargs = dict(
        t=context.translations, analysis_id=context.analysis_id,
        cache_key=(48, "comparison", "selected-path"), analysis_context=context.analysis_context,
        preferred_time_bin="2m", analysis_start_t=context.analysis_start_t,
        analysis_end_t=context.analysis_end_t,
        target_only_label=context.translations["leg_only_me"].format(
            callsign=context.translations["txt_target"],
        ),
        reference_only_label=context.translations["leg_only_ref"].format(
            ref_callsign=context.translations["txt_reference"],
        ),
    )
    cold = coordinator.prepare_selected_benchmark_evidence(rows, identities, False, 10, 0, 2, **kwargs)
    warm = coordinator.prepare_selected_benchmark_evidence(rows, identities, False, 10, 0, 2, **kwargs)
    assert builds == [1]
    assert warm.bundle is cold.bundle
    assert warm.cache_key == cold.cache_key
    assert cold.bundle["evidence_count"] == 2
    assert cold.bundle["comparison_unit_count"] == 3
    assert cold.bundle["identity_labels"] == ("K1AAA (FN31)",)
    np.testing.assert_allclose(native_metrics, [1.75, 3.25])
    compact_recipe = cold.bundle["base_recipe"]
    profile = compact_recipe["prepared_profiles"]["chronological"]["2m"]
    # The existing Joint display projection rounds to 0.1 dB; native units do not.
    np.testing.assert_allclose(profile["median"][:2], [1.8, 3.2])
    np.testing.assert_allclose(profile["count"][:2], [1.0, 1.0])
    assert np.isnan(profile["count"][2:]).all()
    assert compact_recipe["median_focus"]["median_db"] == 2.5
    assert "metric" not in compact_recipe
    assert cold.bundle["coverage_recipe"] is not None
    pd.testing.assert_frame_equal(rows, source_copy)
    assert "station_df" not in cold.bundle
    assert "comparison_units" not in cold.bundle


def test_benchmark_metadata_survives_lazy_artifact_read_failure(monkeypatch):
    context, scope = _context(is_compare=True), _scope()
    table = pd.DataFrame({"Station": ["K1AAA"], "Locator": ["FN31"], "km": [100.0], "Az": [45.0]})
    station_view = StationInsightsView(
        displayed_table=table, export_station_table=table, full_station_table=table,
        selected_station_table=table, selected_rows=(0,), station_column="Station",
        locator_column="Locator", distance_column="km", azimuth_column="Az",
        show_non_joint=False, level_three_container=None,
    )
    # The normal renderer uses localized table columns; supply those explicit labels.
    translations = dict(T["en"], tbl_col_loc="Locator", tbl_col_km="km", tbl_col_az="Az")
    context = replace(context, translations=translations)
    source = pd.DataFrame({"peer_sign": ["K1AAA"], "peer_grid": ["FN31"]})
    prepared = preparation.PreparedScope((), {}, source)
    def fail(*args, **kwargs):
        raise FileNotFoundError("expired")
    monkeypatch.setattr(preparation, "_load_station_rows_for_drilldown", fail)
    coordinator = preparation.InspectorPreparation({}, 7)
    selected = coordinator.prepare_selected_benchmark(context, scope, station_view, prepared)
    assert selected["selected_station_labels"] == ["K1AAA (FN31)"]
    assert "station_df" not in selected
    with pytest.raises(FileNotFoundError):
        coordinator.load_selected_benchmark_rows(context, station_view, selected["selected_meta_df"])
    assert selected["selected_station_labels"] == ["K1AAA (FN31)"]

def test_performance_cold_warm_and_language_preserve_science_without_extra_reads(monkeypatch):
    context, scope = _context(), _scope()
    scope_rows = pd.DataFrame({
        "peer_sign": ["K1AAA"], "peer_grid": ["FN31"],
        "calc_dist": [100.0], "calc_azimuth": [45.0], "dir_name": ["NE"],
        "eligible": [True], "rate_pct": [50.0], "hits": [1], "misses": [1],
        "successful_snr_median": [-8.0],
    })
    original_scope = scope_rows.copy(deep=True)
    first_slot = int(context.analysis_start_t.timestamp()) // 120
    calls = []
    def read(_path, **kwargs):
        calls.append(kwargs)
        return pd.DataFrame({
            "peer_sign": ["K1AAA", "K1AAA", "K1AAA"],
            "peer_grid": ["FN31", "FN31", "FN31AA"],
            "time_slot": [first_slot, first_slot + 1, first_slot],
            "hit": [1, 0, 1], "miss": [0, 1, 0],
            "target_snr": [-8.0, np.nan, -2.0],
        })
    monkeypatch.setattr(preparation, "read_parquet_artifact", read)
    coordinator = preparation.InspectorPreparation({}, 7)
    cold = coordinator.prepare_performance_segment(context, scope, scope_rows, retained_time_bin="auto")
    warm = coordinator.prepare_performance_segment(context, scope, scope_rows, retained_time_bin="auto")
    assert warm.bundle is cold.bundle
    assert warm.scope_rows is scope_rows
    assert len(calls) == 1
    assert calls[0]["columns"] == list(preparation.OPPORTUNITY_SEGMENT_VIEW_COLUMNS)
    assert calls[0]["filters"] == [("peer_sign", "in", ["K1AAA"])]
    assert cold.bundle["display_model"]["confirmed_station_count"] == 1
    assert cold.bundle["display_model"]["confirmed_opportunity_count"] == 2
    assert set(cold.bundle) == {"display_model", "figure_recipe", "temporal_bundle", "analysis_start_t", "analysis_end_t"}
    german = coordinator.prepare_performance_segment(_context(language="de"), scope, scope_rows, retained_time_bin="auto")
    assert len(calls) == 2  # Existing localized cache-key policy remains unchanged.
    assert german.cache_key != cold.cache_key
    english_recipe = cold.bundle["temporal_bundle"]["base_recipe"]
    german_recipe = german.bundle["temporal_bundle"]["base_recipe"]
    np.testing.assert_equal(english_recipe["chronological_profiles"], german_recipe["chronological_profiles"])
    np.testing.assert_equal(english_recipe["folded_profile"], german_recipe["folded_profile"])
    pd.testing.assert_frame_equal(scope_rows, original_scope)
