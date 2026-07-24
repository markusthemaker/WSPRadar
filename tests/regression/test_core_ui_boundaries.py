from collections import OrderedDict
from datetime import datetime, timezone
import inspect
import os
import time
import uuid

import pandas as pd
import pytest

from config import WSPR_DATABASE_PROVIDERS
from core import data_engine, plot_engine
from core.analysis_context import (
    AnalysisContext,
    COMPARISON_HARDWARE_AB,
    COMPARISON_REFERENCE_STATION,
)
from core.analysis_runner import build_analysis_batches
from core.artifact_store import ArtifactNamespace
from core.fetch_models import DatabaseSource, FetchSource
from core.map_data import build_map_data
from core.map_models import MapFigure
from core.presentation_context import PresentationContext
from i18n import T, absolute_terms
from ui.inspector import drilldown, evidence_data, view_models
from ui.plots import opportunity_figures


START_TIME = datetime(2026, 5, 27, tzinfo=timezone.utc)
END_TIME = datetime(2026, 5, 28, tzinfo=timezone.utc)


class _StreamingResponse:
    def __init__(self, content, *, status_code=200, encoding="utf-8"):
        self.content = bytes(content)
        self.status_code = status_code
        self.encoding = encoding

    @property
    def text(self):
        return self.content.decode(self.encoding)

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def iter_content(self, chunk_size):
        for offset in range(0, len(self.content), chunk_size):
            yield self.content[offset:offset + chunk_size]


def _analysis_context(**overrides):
    values = {
        "run_mode": "TX",
        "callsign": "DL1MKS",
        "qth": "JN37",
        "band": "20m",
        "comparison_mode": COMPARISON_REFERENCE_STATION,
        "reference_callsign": "DL2XYZ",
        "reference_qth": "JO62",
    }
    values.update(overrides)
    return AnalysisContext(**values)


def _presentation(language):
    return PresentationContext(
        language=language,
        labels=T[language],
        theme="dark",
        solar_label="All" if language == "en" else "Alle",
    )


def test_analysis_context_contains_only_scientific_configuration():
    values = _analysis_context().to_dict()

    assert "language" not in values
    assert "labels" not in values
    assert "theme" not in values
    assert "is_demo_run" not in values
    assert "active_demo_profile" not in values


def test_presentation_context_preserves_existing_absolute_terminology():
    for language in ["en", "de"]:
        presentation = _presentation(language)
        for mode in ["TX", "RX"]:
            assert presentation.absolute_terms(mode) == absolute_terms(T[language], mode)


def test_no_data_warning_prompts_for_primary_run_definition_inputs():
    assert T["en"]["warn_no_data"].endswith(
        "Are the callsign entries, locator, band, date, and UTC time correct?"
    )
    assert T["de"]["warn_no_data"].endswith(
        "Sind Rufzeichenangaben, Locator, Band, Datum und UTC-Zeit korrekt?"
    )


def test_localized_presentation_changes_titles_but_not_queries():
    context = _analysis_context()

    english = build_analysis_batches(
        context,
        START_TIME,
        END_TIME,
        47.0,
        8.0,
        "AND band = '14'",
        presentation_context=_presentation("en"),
    )
    german = build_analysis_batches(
        context,
        START_TIME,
        END_TIME,
        47.0,
        8.0,
        "AND band = '14'",
        presentation_context=_presentation("de"),
    )

    assert [item["id"] for item in english] == [item["id"] for item in german]
    assert [item["query"] for item in english] == [item["query"] for item in german]
    assert [item["title"] for item in english] != [item["title"] for item in german]


def test_data_engine_returns_structured_http_error_without_ui_calls(monkeypatch):
    monkeypatch.setattr(
        data_engine.http_session,
        "get",
        lambda *_args, **_kwargs: _StreamingResponse(
            b"service unavailable",
            status_code=503,
        ),
    )
    query = f"SELECT '{uuid.uuid4().hex}' FORMAT CSVWithNames"

    result = data_engine.fetch_wspr_data(query)

    assert result.dataframe is None
    assert result.source == FetchSource.WSPR_LIVE
    assert result.database_source == DatabaseSource.WSPR_LIVE
    assert result.error is not None
    assert result.error.code == "http_error"
    assert result.error.status_code == 503
    assert result.error.response_text == "service unavailable"


def test_standard_fetch_cache_is_copy_on_read(monkeypatch):
    query = f"SELECT '{uuid.uuid4().hex}' FORMAT CSVWithNames"
    request_count = 0

    def fake_get(*_args, **_kwargs):
        nonlocal request_count
        request_count += 1
        return _StreamingResponse(b"peer_sign,stat_val\nK1AAA,-12.3\n")

    monkeypatch.setattr(data_engine.http_session, "get", fake_get)
    first = data_engine.fetch_wspr_data(query)
    first.dataframe.loc[0, "stat_val"] = 999.0
    second = data_engine.fetch_wspr_data(query)

    assert request_count == 1
    assert first.source == FetchSource.WSPR_LIVE
    assert second.source == FetchSource.MEMORY_CACHE
    assert second.database_source == DatabaseSource.WSPR_LIVE
    assert float(second.dataframe.loc[0, "stat_val"]) == pytest.approx(-12.3)


def test_demo_and_standard_fetches_use_separate_cache_keys(tmp_path, monkeypatch):
    query = f"SELECT '{uuid.uuid4().hex}' FORMAT CSVWithNames"
    request_count = 0

    def fake_get(*_args, **_kwargs):
        nonlocal request_count
        request_count += 1
        return _StreamingResponse(b"peer_sign,stat_val\nK1AAA,-12.3\n")

    monkeypatch.setattr(data_engine, "CACHE_DIR", str(tmp_path))
    monkeypatch.setattr(data_engine, "_dataframe_cache", OrderedDict())
    monkeypatch.setattr(data_engine.http_session, "get", fake_get)
    standard = data_engine.fetch_wspr_data(query, is_demo=False)
    demo = data_engine.fetch_wspr_data(query, is_demo=True)
    standard_hit = data_engine.fetch_wspr_data(query, is_demo=False)
    demo_hit = data_engine.fetch_wspr_data(query, is_demo=True)

    assert request_count == 2
    assert str(standard.dataframe["stat_val"].dtype) == "float32"
    assert str(demo.dataframe["stat_val"].dtype) == "float64"
    assert standard_hit.source == FetchSource.MEMORY_CACHE
    assert demo_hit.source == FetchSource.MEMORY_CACHE


def test_demo_compare_uses_direct_ram_and_disk_cache_with_copy_on_read(
    tmp_path,
    monkeypatch,
):
    """Persist raw demo CSV rows and isolate callers from both cache tiers."""
    query = "SELECT demo_compare_cache FORMAT CSVWithNames"
    request_count = 0

    def fake_get(*_args, **_kwargs):
        nonlocal request_count
        request_count += 1
        return _StreamingResponse(b"peer_sign,stat_val\nK1AAA,-12.3\n")

    monkeypatch.setattr(data_engine, "CACHE_DIR", str(tmp_path))
    monkeypatch.setattr(data_engine, "_dataframe_cache", OrderedDict())
    monkeypatch.setattr(data_engine.http_session, "get", fake_get)

    direct_result = data_engine.fetch_wspr_data(query, is_demo=True)
    direct_result.dataframe.loc[0, "stat_val"] = 999.0
    ram_result = data_engine.fetch_wspr_data(query, is_demo=True)
    ram_value_before_mutation = float(ram_result.dataframe.loc[0, "stat_val"])
    ram_result.dataframe.loc[0, "stat_val"] = 888.0

    data_engine._dataframe_cache.clear()
    disk_result = data_engine.fetch_wspr_data(query, is_demo=True)
    disk_result.dataframe.loc[0, "stat_val"] = 777.0

    data_engine._dataframe_cache.clear()
    second_disk_result = data_engine.fetch_wspr_data(query, is_demo=True)
    cache_path = data_engine._query_cache_path(query, is_demo=True)

    assert request_count == 1
    assert direct_result.source == FetchSource.WSPR_LIVE
    assert ram_result.source == FetchSource.MEMORY_CACHE
    assert disk_result.source == FetchSource.DISK_CACHE
    assert second_disk_result.source == FetchSource.DISK_CACHE
    assert ram_value_before_mutation == pytest.approx(-12.3)
    assert float(second_disk_result.dataframe.loc[0, "stat_val"]) == pytest.approx(-12.3)
    assert disk_result.artifact_path == cache_path
    assert cache_path.parent.parent.name == ArtifactNamespace.DEMO_QUERY.value


def test_demo_compare_disk_reload_does_not_extend_absolute_expiry(
    tmp_path,
    monkeypatch,
):
    """Anchor RAM and disk freshness to the original demo publication time."""
    query = "SELECT demo_compare_absolute_expiry FORMAT CSVWithNames"
    request_count = 0

    def fake_get(*_args, **_kwargs):
        nonlocal request_count
        request_count += 1
        return _StreamingResponse(b"peer_sign,has_u\nK1AAA,0\n")

    monkeypatch.setattr(data_engine, "CACHE_DIR", str(tmp_path))
    monkeypatch.setattr(data_engine, "_dataframe_cache", OrderedDict())
    monkeypatch.setattr(data_engine.http_session, "get", fake_get)

    data_engine.fetch_wspr_data(query, is_demo=True)
    cache_path = data_engine._query_cache_path(query, is_demo=True)
    late_publication_time = (
        time.time() - data_engine.DEMO_QUERY_CACHE_TTL_SEC + 300.0
    )
    os.utime(cache_path, (late_publication_time, late_publication_time))
    published_mtime = cache_path.stat().st_mtime
    data_engine._dataframe_cache.clear()

    disk_result = data_engine.fetch_wspr_data(query, is_demo=True)
    cache_key = data_engine._memory_cache_key(
        query,
        is_demo=True,
        database_provider=WSPR_DATABASE_PROVIDERS[0],
    )
    initial_ram_expiry = data_engine._dataframe_cache[cache_key][0]
    first_ram_result = data_engine.fetch_wspr_data(query, is_demo=True)
    second_ram_result = data_engine.fetch_wspr_data(query, is_demo=True)
    repeated_ram_expiry = data_engine._dataframe_cache[cache_key][0]

    assert request_count == 1
    assert disk_result.source == FetchSource.DISK_CACHE
    assert first_ram_result.source == FetchSource.MEMORY_CACHE
    assert second_ram_result.source == FetchSource.MEMORY_CACHE
    assert cache_path.stat().st_mtime == pytest.approx(published_mtime, abs=0.01)
    assert initial_ram_expiry == pytest.approx(
        published_mtime + data_engine.DEMO_QUERY_CACHE_TTL_SEC,
        abs=0.01,
    )
    assert repeated_ram_expiry == initial_ram_expiry
    assert data_engine._query_cache_expiry_epoch(
        cache_path,
        data_engine.DEMO_QUERY_CACHE_TTL_SEC,
        now=published_mtime + data_engine.DEMO_QUERY_CACHE_TTL_SEC + 1.0,
    ) is None


def test_identical_csv_query_caches_are_isolated_by_database_source(monkeypatch):
    query = f"SELECT '{uuid.uuid4().hex}' FORMAT CSVWithNames"
    requested_urls = []

    def fake_get(url, *_args, **_kwargs):
        requested_urls.append(url)
        value = -12.3 if "db1.wspr.live" in url else -9.4
        return _StreamingResponse(
            f"peer_sign,stat_val\nK1AAA,{value}\n".encode("utf-8")
        )

    monkeypatch.setattr(data_engine.http_session, "get", fake_get)
    primary, wd2, _wd1 = WSPR_DATABASE_PROVIDERS

    live_result = data_engine.fetch_wspr_data(query, database_provider=primary)
    wd2_result = data_engine.fetch_wspr_data(query, database_provider=wd2)
    live_cached = data_engine.fetch_wspr_data(query, database_provider=primary)
    wd2_cached = data_engine.fetch_wspr_data(query, database_provider=wd2)

    assert requested_urls == [primary.url, wd2.url]
    assert live_result.database_source == DatabaseSource.WSPR_LIVE
    assert wd2_result.source == FetchSource.WD2
    assert wd2_result.database_source == DatabaseSource.WD2
    assert live_cached.source == FetchSource.MEMORY_CACHE
    assert live_cached.database_source == DatabaseSource.WSPR_LIVE
    assert wd2_cached.source == FetchSource.MEMORY_CACHE
    assert wd2_cached.database_source == DatabaseSource.WD2
    assert float(live_cached.dataframe.loc[0, "stat_val"]) == pytest.approx(-12.3)
    assert float(wd2_cached.dataframe.loc[0, "stat_val"]) == pytest.approx(-9.4)


def test_map_data_is_pure_and_preserves_legacy_absolute_aggregates():
    source = pd.DataFrame(
        {
            "peer_sign": ["K1AAA", "K1AAA", "K2BBB"],
            "peer_grid": ["FN31", "FN31", "EM12"],
            "peer_lat": [41.0, 41.0, 32.8],
            "peer_lon": [-72.0, -72.0, -96.8],
            "stat_val": [-10.0, -12.0, -5.0],
        }
    )
    original = source.copy(deep=True)

    map_data = build_map_data(
        source,
        analysis_id="TX_ABS",
        is_compare=False,
        is_sequential=False,
        analysis_kind="comparison",
        center_latitude=47.0,
        center_longitude=8.0,
        min_spots=1,
        min_opportunities=5,
        base_min_stations=1,
        tx_ab_repeat_interval_minutes=10,
        tx_ab_target_start_minute=0,
        tx_ab_reference_start_minute=2,
    )

    pd.testing.assert_frame_equal(source, original)
    assert map_data is not None
    assert set(map_data.station_rows["peer_sign"]) == {"K1AAA", "K2BBB"}
    assert float(
        map_data.station_rows.loc[
            map_data.station_rows["peer_sign"] == "K1AAA",
            "stat_val",
        ].iloc[0]
    ) == -11.0
    assert not map_data.segment_rows.empty


def test_generate_map_plot_returns_explicit_map_figure_contract(monkeypatch):
    source = pd.DataFrame(
        {
            "peer_sign": ["K1AAA"],
            "peer_grid": ["FN31"],
            "peer_lat": [41.0],
            "peer_lon": [-72.0],
            "stat_val": [-10.0],
        }
    )

    def fake_render(map_data, **_kwargs):
        return MapFigure(figure="figure", map_data=map_data, footer_text="footer")

    monkeypatch.setattr(plot_engine, "render_map_figure", fake_render)
    result = plot_engine.generate_map_plot(
        source,
        "Title",
        False,
        False,
        START_TIME,
        END_TIME,
        22000,
        "TX_ABS",
        1,
        47.0,
        8.0,
        analysis_context=_analysis_context(),
        presentation_context=_presentation("en"),
    )

    assert isinstance(result, MapFigure)
    assert result.figure == "figure"
    assert result.footer_text == "footer"
    assert result.map_data.analysis_id == "TX_ABS"


def test_compare_view_model_localization_cannot_change_scope_or_evidence():
    scope_rows = pd.DataFrame(
        {
            "peer_sign": ["K1AAA", "K2BBB"],
            "peer_grid": ["FN31", "EM12"],
            "calc_dist": [100.0, 200.0],
            "calc_azimuth": [45.0, 90.0],
            "spot_count": [4, 0],
            "count_only_u": [0, 3],
            "count_only_r": [0, 0],
            "stat_val": [1.2, None],
        }
    )
    context = _analysis_context()

    english = view_models.build_compare_inspector_view_model(
        scope_rows,
        analysis_id="TX_COMP",
        is_compare=True,
        is_sequential=False,
        show_non_joint=True,
        analysis_context=context,
        presentation_context=_presentation("en"),
    )
    german = view_models.build_compare_inspector_view_model(
        scope_rows,
        analysis_id="TX_COMP",
        is_compare=True,
        is_sequential=False,
        show_non_joint=True,
        analysis_context=context,
        presentation_context=_presentation("de"),
    )

    pd.testing.assert_frame_equal(english.scope_rows, german.scope_rows)
    pd.testing.assert_frame_equal(english.evidence_identities, german.evidence_identities)
    pd.testing.assert_series_equal(english.values, german.values)
    assert list(english.station_table.columns) != list(german.station_table.columns)


def test_hardware_compare_labels_use_fixed_identities_or_scheduled_roles():
    """Expose callsigns for simultaneous paths and roles for one-callsign schedules."""
    simultaneous_context = _analysis_context(
        comparison_mode=COMPARISON_HARDWARE_AB,
        reference_callsign="DL2XYZ/P",
        reference_qth="JN37",
    )
    simultaneous = view_models._compare_labels(
        simultaneous_context,
        T["en"],
        is_sequential=False,
    )
    sequential = view_models._compare_labels(
        simultaneous_context,
        T["en"],
        is_sequential=True,
    )

    assert simultaneous[:2] == ("DL1MKS", "DL2XYZ/P")
    assert sequential[:2] == ("Target", "Reference")


def test_cached_all_rows_view_model_derives_identical_joint_only_table():
    scope_rows = pd.DataFrame(
        {
            "peer_sign": ["K1AAA", "K2BBB", "K3CCC"],
            "peer_grid": ["FN31", "EM12", "IO91"],
            "calc_dist": [100.0, 200.0, 300.0],
            "calc_azimuth": [45.0, 90.0, 135.0],
            "spot_count": [4, 0, 2],
            "count_only_u": [0, 3, 0],
            "count_only_r": [0, 0, 0],
            "stat_val": [1.2, None, -0.4],
        }
    )
    kwargs = {
        "analysis_id": "TX_COMP",
        "is_compare": True,
        "is_sequential": False,
        "analysis_context": _analysis_context(),
        "presentation_context": _presentation("en"),
    }
    all_rows = view_models.build_compare_inspector_view_model(
        scope_rows,
        show_non_joint=True,
        **kwargs,
    )
    joint_only = view_models.build_compare_inspector_view_model(
        scope_rows,
        show_non_joint=False,
        **kwargs,
    )
    derived_joint_only = all_rows.station_table[
        all_rows.station_table[all_rows.joint_column] > 0
    ].reset_index(drop=True)

    pd.testing.assert_frame_equal(derived_joint_only, joint_only.station_table)
    pd.testing.assert_frame_equal(all_rows.evidence_identities, joint_only.evidence_identities)


def test_opportunity_view_model_localization_cannot_change_eligibility_or_evidence():
    scope_rows = pd.DataFrame(
        {
            "peer_sign": ["K1AAA", "K2BBB"],
            "peer_grid": ["FN31", "EM12"],
            "calc_dist": [100.0, 200.0],
            "calc_azimuth": [45.0, 90.0],
            "eligible": [True, False],
            "rate_pct": [50.0, 100.0],
            "hits": [1, 1],
            "misses": [1, 0],
            "successful_snr_median": [-12.0, -5.0],
        }
    )
    evidence_rows = pd.DataFrame(
        {
            "peer_sign": ["K1AAA", "K1AAA", "K2BBB"],
            "peer_grid": ["FN31", "FN31", "EM12"],
            "hit": [1, 0, 1],
            "miss": [0, 1, 0],
        }
    )

    english = view_models.build_opportunity_inspector_view_model(
        scope_rows,
        evidence_rows,
        analysis_id="RX_ABS",
        minimum_confirmed=5,
        presentation_context=_presentation("en"),
    )
    german = view_models.build_opportunity_inspector_view_model(
        scope_rows,
        evidence_rows,
        analysis_id="RX_ABS",
        minimum_confirmed=5,
        presentation_context=_presentation("de"),
    )

    pd.testing.assert_frame_equal(english.confirmed_rows, german.confirmed_rows)
    pd.testing.assert_frame_equal(english.evidence_rows, german.evidence_rows)
    assert english.confirmed_rows["peer_sign"].tolist() == ["K1AAA"]
    assert english.confirmed_station_count == 1
    assert english.confirmed_opportunity_count == 2
    assert german.confirmed_station_count == 1
    assert german.confirmed_opportunity_count == 2
    assert all(
        "Selected Segment" not in summary
        and "Ausgewähltes Segment" not in summary
        for summary in english.summary_lines + german.summary_lines
    )
    assert list(english.full_station_table.columns) != list(german.full_station_table.columns)


def test_core_and_pure_inspector_modules_have_no_streamlit_dependency():
    for module in [
        data_engine,
        plot_engine,
        evidence_data,
        drilldown,
        view_models,
        opportunity_figures,
    ]:
        source = inspect.getsource(module)
        assert "import streamlit" not in source
        assert "st.session_state" not in source
    assert "from config import *" not in inspect.getsource(plot_engine)
