"""Regression coverage for the presentation-only Success map status redesign."""

from __future__ import annotations

from datetime import datetime, timezone

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.collections import PatchCollection, PathCollection
from matplotlib.colors import to_rgba
from matplotlib.figure import Figure
from matplotlib.legend import Legend
from matplotlib.transforms import IdentityTransform
import numpy as np
import pandas as pd
import pytest

from core.analysis_context import AnalysisContext, COMPARISON_REFERENCE_STATION
from core.map_models import MapData
from core.presentation_context import PresentationContext
from core import plot_engine
from i18n import T
from ui.matplotlib_renderer import dispose_matplotlib_figure


SUCCESS_TARGET_MARKERS_GID = "success-target-observed-markers"
SUCCESS_COUNTER_MARKERS_GID = "success-counter-only-markers"
SUCCESS_SECTORS_GID = "success-sector-fills"
SUCCESS_LEGEND_GID = "success-map-legend"
SUCCESS_FOOTER_GID = "success-map-footer"


@pytest.fixture
def map_canvas_without_cartopy(monkeypatch):
    """Replace Cartopy construction with a deterministic Matplotlib canvas."""

    def fake_create_base_map_figure(**kwargs):
        figure = Figure(
            figsize=(12, 12.5),
            facecolor=kwargs["theme_config"]["fig_face"],
        )
        map_axis = figure.add_axes([0.04, 0.13, 0.76, 0.76])
        identity_transform = IdentityTransform()
        return figure, map_axis, identity_transform, identity_transform

    monkeypatch.setattr(
        plot_engine,
        "_preview_base_map_cache_enabled",
        lambda: False,
    )
    monkeypatch.setattr(
        plot_engine,
        "create_base_map_figure",
        fake_create_base_map_figure,
    )


def _presentation_context(*, language="en", theme="dark"):
    return PresentationContext(
        language=language,
        labels=T[language],
        theme=theme,
        solar_label=T[language]["opt_solar_all"].split()[0],
    )


def _analysis_context(*, minimum_opportunities=1):
    return AnalysisContext(
        callsign="TARGET",
        qth="JJ00",
        band="20m",
        min_confirmed_opportunities_per_peer=minimum_opportunities,
    )


def _success_map_data(*, analysis_id="RX_ABS"):
    station_rows = pd.DataFrame(
        {
            "peer_sign": ["TARGET_EVIDENCE", "ZERO_TARGET", "INELIGIBLE"],
            "peer_grid": ["AA00", "BB00", "CC00"],
            "peer_lon": [1.0, 2.0, 3.0],
            "peer_lat": [1.0, 2.0, 3.0],
            "eligible": [True, True, False],
            "rate_pct": [75.0, 0.0, 100.0],
            "hits": [3, 0, 10],
            "misses": [1, 4, 0],
            "opportunities": [4, 4, 10],
            "target_only": [2, 1, 0],
            "r_min": [0.0, 0.0, 0.0],
        }
    )
    segment_rows = pd.DataFrame(
        {
            "r_min": [0.0, 2500.0],
            "r_max": [2500.0, 5000.0],
            "az_bucket": [0.0, 1.0],
            "val": [0.0, 75.0],
            "cnt": [1, 1],
            "total_opportunities": [4, 4],
            "total_hits": [0, 3],
            "total_misses": [4, 1],
        }
    )
    return MapData(
        station_rows=station_rows,
        segment_rows=segment_rows,
        analysis_id=analysis_id,
        is_compare=False,
        is_sequential=False,
        analysis_kind="opportunity",
    )


def _render_map(
    map_data,
    *,
    language="en",
    theme="dark",
    maximum_distance_km=5000,
    minimum_opportunities=1,
    minimum_stations=1,
):
    return plot_engine.render_map_figure(
        map_data,
        title="Performance map",
        start_t=datetime(2026, 7, 1, tzinfo=timezone.utc),
        end_t=datetime(2026, 7, 2, tzinfo=timezone.utc),
        max_dist_km=maximum_distance_km,
        base_min_stations=minimum_stations,
        lat_0=0.0,
        lon_0=0.0,
        analysis_context=_analysis_context(
            minimum_opportunities=minimum_opportunities
        ),
        presentation_context=_presentation_context(
            language=language,
            theme=theme,
        ),
    )


def _artist_with_gid(figure, gid, artist_type):
    matching_artists = [
        artist
        for artist in figure.findobj(match=artist_type)
        if artist.get_gid() == gid
    ]
    assert len(matching_artists) == 1
    return matching_artists[0]


def _raw_opportunity_rows_for_invariance():
    records = []
    time_slot = 1_500_000
    for peer_sign, peer_grid, latitude, longitude, hits, misses in (
        ("A", "AA00", 1.0, 1.0, 5, 5),
        ("B", "BB00", 2.0, 2.0, 0, 2),
        ("LOW", "CC00", 3.0, 3.0, 1, 0),
    ):
        for is_hit in [True] * hits + [False] * misses:
            records.append(
                {
                    "time_slot": time_slot,
                    "peer_sign": peer_sign,
                    "peer_grid": peer_grid,
                    "peer_lat": latitude,
                    "peer_lon": longitude,
                    "target_seen": int(is_hit),
                    "target_snr": -10.0 if is_hit else np.nan,
                    "opportunity": 1,
                    "hit": int(is_hit),
                    "miss": int(not is_hit),
                    "target_only": 0,
                }
            )
            time_slot += 1
    return pd.DataFrame.from_records(records)


def test_preview_and_export_theme_paths_preserve_success_science_and_categories(
    map_canvas_without_cartopy,
):
    """Keep renderer theme changes outside every Success scientific aggregate."""
    analysis_context = _analysis_context(minimum_opportunities=2)
    dark_result = plot_engine.generate_map_plot(
        _raw_opportunity_rows_for_invariance(),
        "RX Performance",
        False,
        False,
        datetime(2026, 7, 1, tzinfo=timezone.utc),
        datetime(2026, 7, 2, tzinfo=timezone.utc),
        5000,
        "RX_ABS",
        1,
        0.0,
        0.0,
        analysis_context=analysis_context,
        presentation_context=_presentation_context(theme="dark"),
        theme="dark",
        analysis_kind="opportunity",
    )
    light_result = plot_engine.generate_map_plot(
        _raw_opportunity_rows_for_invariance(),
        "RX Performance",
        False,
        False,
        datetime(2026, 7, 1, tzinfo=timezone.utc),
        datetime(2026, 7, 2, tzinfo=timezone.utc),
        5000,
        "RX_ABS",
        1,
        0.0,
        0.0,
        analysis_context=analysis_context,
        presentation_context=_presentation_context(theme="dark"),
        theme="light",
        analysis_kind="opportunity",
    )
    assert dark_result is not None
    assert light_result is not None
    try:
        station_sort = ["peer_sign", "peer_grid"]
        segment_sort = ["r_min", "az_bucket"]
        pd.testing.assert_frame_equal(
            dark_result.map_data.station_rows.sort_values(station_sort).reset_index(
                drop=True
            ),
            light_result.map_data.station_rows.sort_values(station_sort).reset_index(
                drop=True
            ),
        )
        pd.testing.assert_frame_equal(
            dark_result.map_data.segment_rows.sort_values(segment_sort).reset_index(
                drop=True
            ),
            light_result.map_data.segment_rows.sort_values(segment_sort).reset_index(
                drop=True
            ),
        )

        peers = dark_result.map_data.station_rows.set_index("peer_sign")
        assert peers.loc["A", ["opportunities", "hits", "misses"]].tolist() == [
            10,
            5,
            5,
        ]
        assert peers.loc["B", ["opportunities", "hits", "misses"]].tolist() == [
            2,
            0,
            2,
        ]
        assert bool(peers.loc["A", "eligible"])
        assert bool(peers.loc["B", "eligible"])
        assert not bool(peers.loc["LOW", "eligible"])
        assert float(peers.loc["A", "rate_pct"]) == pytest.approx(50.0)
        assert float(peers.loc["B", "rate_pct"]) == pytest.approx(0.0)

        segment = dark_result.map_data.segment_rows.iloc[0]
        assert int(segment["cnt"]) == 2
        assert int(segment["total_opportunities"]) == 12
        assert int(segment["total_hits"]) == 5
        assert int(segment["total_misses"]) == 7
        assert float(segment["val"]) == pytest.approx(25.0)
        assert float(segment["pooled_rate_pct"]) == pytest.approx(41.7)

        for rendered_result in (dark_result, light_result):
            target_markers = _artist_with_gid(
                rendered_result.figure,
                SUCCESS_TARGET_MARKERS_GID,
                PathCollection,
            )
            counter_only_markers = _artist_with_gid(
                rendered_result.figure,
                SUCCESS_COUNTER_MARKERS_GID,
                PathCollection,
            )
            assert target_markers.get_array() is None
            assert counter_only_markers.get_array() is None
            np.testing.assert_allclose(
                np.asarray(target_markers.get_offsets()),
                [[1.0, 1.0]],
            )
            np.testing.assert_allclose(
                np.asarray(counter_only_markers.get_offsets()),
                [[2.0, 2.0]],
            )

        dark_target_markers = _artist_with_gid(
            dark_result.figure,
            SUCCESS_TARGET_MARKERS_GID,
            PathCollection,
        )
        light_target_markers = _artist_with_gid(
            light_result.figure,
            SUCCESS_TARGET_MARKERS_GID,
            PathCollection,
        )
        dark_counter_markers = _artist_with_gid(
            dark_result.figure,
            SUCCESS_COUNTER_MARKERS_GID,
            PathCollection,
        )
        light_counter_markers = _artist_with_gid(
            light_result.figure,
            SUCCESS_COUNTER_MARKERS_GID,
            PathCollection,
        )
        assert dark_target_markers.get_sizes().tolist() == (
            light_target_markers.get_sizes().tolist()
        )
        assert dark_counter_markers.get_sizes().tolist() == (
            light_counter_markers.get_sizes().tolist()
        )

        dark_legend = _artist_with_gid(
            dark_result.figure,
            SUCCESS_LEGEND_GID,
            Legend,
        )
        light_legend = _artist_with_gid(
            light_result.figure,
            SUCCESS_LEGEND_GID,
            Legend,
        )
        assert [text.get_text() for text in dark_legend.get_texts()] == [
            text.get_text() for text in light_legend.get_texts()
        ]

        dark_footer = _artist_with_gid(
            dark_result.figure,
            SUCCESS_FOOTER_GID,
            type(dark_result.figure.axes[0]),
        )
        light_footer = _artist_with_gid(
            light_result.figure,
            SUCCESS_FOOTER_GID,
            type(light_result.figure.axes[0]),
        )
        assert [tick.get_text() for tick in dark_footer.get_yticklabels()] == [
            tick.get_text() for tick in light_footer.get_yticklabels()
        ]
        assert [text.get_text() for text in dark_footer.texts] == [
            text.get_text() for text in light_footer.texts
        ]

        for rendered_result in (dark_result, light_result):
            assert not any(
                collection.get_gid() == "success-no-qualifying-segments"
                for collection in rendered_result.figure.axes[0].collections
            )
    finally:
        dispose_matplotlib_figure(dark_result.figure)
        dispose_matplotlib_figure(light_result.figure)


def test_success_renderer_does_not_mutate_precomputed_map_science(
    map_canvas_without_cartopy,
):
    """Treat map aggregation as an immutable scientific input to presentation."""
    map_data = _success_map_data()
    station_rows_before = map_data.station_rows.copy(deep=True)
    segment_rows_before = map_data.segment_rows.copy(deep=True)

    rendered = _render_map(map_data)
    try:
        assert rendered.map_data is map_data
        pd.testing.assert_frame_equal(map_data.station_rows, station_rows_before)
        pd.testing.assert_frame_equal(map_data.segment_rows, segment_rows_before)
    finally:
        dispose_matplotlib_figure(rendered.figure)


def test_success_status_uses_target_count_not_rounded_station_rate(
    map_canvas_without_cartopy,
):
    """Classify a rounded 0.0% station with one Target outcome as Target observed."""
    map_data = _success_map_data()
    map_data.station_rows = pd.DataFrame(
        {
            "peer_sign": ["ROUNDED_ZERO", "TRUE_ZERO"],
            "peer_grid": ["AA00", "BB00"],
            "peer_lon": [1.0, 2.0],
            "peer_lat": [1.0, 2.0],
            "eligible": [True, True],
            "rate_pct": [0.0, 0.0],
            "hits": [1, 0],
            "misses": [9_999, 10_000],
            "opportunities": [10_000, 10_000],
            "target_only": [0, 0],
            "r_min": [0.0, 0.0],
        }
    )

    rendered = _render_map(map_data)
    try:
        target_markers = _artist_with_gid(
            rendered.figure,
            SUCCESS_TARGET_MARKERS_GID,
            PathCollection,
        )
        counter_only_markers = _artist_with_gid(
            rendered.figure,
            SUCCESS_COUNTER_MARKERS_GID,
            PathCollection,
        )
        np.testing.assert_allclose(
            np.asarray(target_markers.get_offsets()),
            [[1.0, 1.0]],
        )
        np.testing.assert_allclose(
            np.asarray(counter_only_markers.get_offsets()),
            [[2.0, 2.0]],
        )
    finally:
        dispose_matplotlib_figure(rendered.figure)


def test_coincident_target_and_counter_markers_keep_target_visibly_on_top(
    map_canvas_without_cartopy,
):
    """Preserve both co-located station rows while restoring Target precedence."""
    map_data = _success_map_data()
    map_data.station_rows = pd.DataFrame(
        {
            "peer_sign": ["TARGET_EVIDENCE", "COUNTER_ONLY"],
            "peer_grid": ["AA00", "AA00"],
            "peer_lon": [1.0, 1.0],
            "peer_lat": [1.0, 1.0],
            "eligible": [True, True],
            "rate_pct": [50.0, 0.0],
            "hits": [1, 0],
            "misses": [1, 2],
            "opportunities": [2, 2],
            "target_only": [0, 0],
            "r_min": [0.0, 0.0],
        }
    )
    station_rows_before = map_data.station_rows.copy(deep=True)

    rendered = _render_map(map_data)
    try:
        target_markers = _artist_with_gid(
            rendered.figure,
            SUCCESS_TARGET_MARKERS_GID,
            PathCollection,
        )
        counter_only_markers = _artist_with_gid(
            rendered.figure,
            SUCCESS_COUNTER_MARKERS_GID,
            PathCollection,
        )

        pd.testing.assert_frame_equal(map_data.station_rows, station_rows_before)
        np.testing.assert_allclose(target_markers.get_offsets(), [[1.0, 1.0]])
        np.testing.assert_allclose(
            counter_only_markers.get_offsets(),
            [[1.0, 1.0]],
        )
        assert len(target_markers.get_offsets()) == 1
        assert len(counter_only_markers.get_offsets()) == 1
        assert target_markers.get_zorder() == pytest.approx(10.0)
        assert counter_only_markers.get_zorder() == pytest.approx(9.0)
        assert target_markers.get_zorder() > counter_only_markers.get_zorder()
    finally:
        dispose_matplotlib_figure(rendered.figure)


def test_dense_success_map_uses_two_vectorized_legacy_size_status_groups(
    map_canvas_without_cartopy,
):
    """Render thousands of stations without per-station artists or value encodings."""
    station_count = 6000
    station_indices = np.arange(station_count)
    has_target = station_indices % 2 == 0
    station_rows = pd.DataFrame(
        {
            "peer_sign": [f"S{index:05d}" for index in station_indices],
            "peer_grid": ["AA00"] * station_count,
            "peer_lon": np.linspace(-175.0, 175.0, station_count),
            "peer_lat": np.linspace(-70.0, 70.0, station_count),
            "eligible": [True] * station_count,
            "rate_pct": np.where(has_target, (station_indices % 99) + 1.0, 0.0),
            "hits": np.where(has_target, (station_indices % 23) + 1, 0),
            "misses": (station_indices % 31) + 1,
            "opportunities": np.where(
                has_target,
                (station_indices % 23) + 1,
                0,
            )
            + (station_indices % 31)
            + 1,
            "target_only": [0] * station_count,
            "r_min": [0.0] * station_count,
        }
    )
    segment_rows = pd.DataFrame(
        {
            "r_min": [0.0],
            "r_max": [2500.0],
            "az_bucket": [0.0],
            "val": [50.0],
            "cnt": [station_count],
        }
    )
    map_data = MapData(
        station_rows=station_rows,
        segment_rows=segment_rows,
        analysis_id="RX_ABS",
        is_compare=False,
        is_sequential=False,
        analysis_kind="opportunity",
    )

    rendered = _render_map(map_data)
    try:
        target_markers = _artist_with_gid(
            rendered.figure,
            SUCCESS_TARGET_MARKERS_GID,
            PathCollection,
        )
        counter_only_markers = _artist_with_gid(
            rendered.figure,
            SUCCESS_COUNTER_MARKERS_GID,
            PathCollection,
        )
        success_marker_collections = [
            collection
            for collection in rendered.figure.findobj(match=PathCollection)
            if str(collection.get_gid() or "").startswith("success-")
        ]
        assert len(rendered.figure.findobj(match=PathCollection)) == 2
        assert {
            collection.get_gid() for collection in success_marker_collections
        } == {
            SUCCESS_TARGET_MARKERS_GID,
            SUCCESS_COUNTER_MARKERS_GID,
        }
        assert len(target_markers.get_offsets()) == station_count // 2
        assert len(counter_only_markers.get_offsets()) == station_count // 2
        assert target_markers.get_array() is None
        assert counter_only_markers.get_array() is None
        expected_marker_size = (
            plot_engine.SUCCESS_MAP_MARKER_SIZE_POINTS_SQUARED
        )
        assert target_markers.get_sizes().tolist() == [
            expected_marker_size
        ]
        assert counter_only_markers.get_sizes().tolist() == [
            expected_marker_size
        ]
        assert len(np.unique(target_markers.get_facecolors(), axis=0)) <= 1
        assert len(np.unique(counter_only_markers.get_facecolors(), axis=0)) <= 1
        assert target_markers.get_facecolors()[0] == pytest.approx(
            to_rgba(plot_engine.SUCCESS_MAP_TARGET_COLOR)
        )
        assert counter_only_markers.get_facecolors()[0] == pytest.approx(
            to_rgba(
                plot_engine.SUCCESS_MAP_COUNTER_COLOR,
                alpha=plot_engine.SUCCESS_MAP_COUNTER_ALPHA,
            )
        )
        assert target_markers.get_zorder() == pytest.approx(10.0)
        assert counter_only_markers.get_zorder() == pytest.approx(9.0)
        np.testing.assert_allclose(
            np.asarray(target_markers.get_offsets()),
            station_rows.loc[has_target, ["peer_lon", "peer_lat"]].to_numpy(),
        )
        np.testing.assert_allclose(
            np.asarray(counter_only_markers.get_offsets()),
            station_rows.loc[~has_target, ["peer_lon", "peer_lat"]].to_numpy(),
        )
    finally:
        dispose_matplotlib_figure(rendered.figure)


def test_success_marker_size_is_fixed_and_carries_no_scientific_value():
    """Keep both simplified status groups at the legacy fixed marker area."""
    assert plot_engine.SUCCESS_MAP_MARKER_SIZE_POINTS_SQUARED == pytest.approx(
        8.0
    )


@pytest.mark.parametrize("theme", ["dark", "light"])
def test_zero_success_and_insufficient_evidence_have_legacy_distinct_rendering(
    map_canvas_without_cartopy,
    theme,
):
    """Keep measured 0% on-scale while insufficient sectors expose the base map."""
    map_data = _success_map_data()
    map_data.segment_rows = map_data.segment_rows.iloc[[0]].copy()
    rendered = _render_map(map_data, theme=theme)
    try:
        FigureCanvasAgg(rendered.figure).draw()
        valid_sectors = _artist_with_gid(
            rendered.figure,
            SUCCESS_SECTORS_GID,
            PatchCollection,
        )
        assert valid_sectors.get_array().tolist() == [0.0]
        assert valid_sectors.norm(0.0) == 0
        assert not any(
            collection.get_gid() == "success-no-qualifying-segments"
            for collection in rendered.figure.axes[0].collections
        )
        legend = _artist_with_gid(rendered.figure, SUCCESS_LEGEND_GID, Legend)
        insufficient_handle = legend.legend_handles[2]
        assert insufficient_handle.get_facecolor() == pytest.approx(
            to_rgba(plot_engine.MAP_THEMES[theme]["no_hm_face"])
        )
        assert insufficient_handle.get_edgecolor() == pytest.approx(
            to_rgba(plot_engine.MAP_THEMES[theme]["no_hm_edge"])
        )
        assert insufficient_handle.get_linewidth() == pytest.approx(0.9)
    finally:
        dispose_matplotlib_figure(rendered.figure)


@pytest.mark.parametrize("theme", ["dark", "light"])
def test_success_footer_restores_compare_aligned_status_colors(
    map_canvas_without_cartopy,
    theme,
):
    """Keep compact Success bars in the legacy Compare-aligned green/light style."""
    rendered = _render_map(_success_map_data(), theme=theme)
    try:
        footer_axis = _artist_with_gid(
            rendered.figure,
            SUCCESS_FOOTER_GID,
            type(rendered.figure.axes[0]),
        )
        assert len(footer_axis.patches) == 4
        expected_target_color = to_rgba(plot_engine.COLOR_JOINT)
        expected_counter_color = to_rgba(
            plot_engine.MAP_THEMES[theme]["only_ref"]
        )
        assert footer_axis.patches[0].get_facecolor() == pytest.approx(
            expected_target_color
        )
        assert footer_axis.patches[1].get_facecolor() == pytest.approx(
            expected_target_color
        )
        assert footer_axis.patches[2].get_facecolor() == pytest.approx(
            expected_counter_color
        )
        assert footer_axis.patches[3].get_facecolor() == pytest.approx(
            expected_counter_color
        )
        assert {text.get_color() for text in footer_axis.texts} == {"black"}
        assert not any("%" in text.get_text() for text in footer_axis.texts)
    finally:
        dispose_matplotlib_figure(rendered.figure)


def test_compact_footer_omits_counts_that_cannot_fit_narrow_segments():
    """Follow Compare footer behavior instead of forcing overlapping labels."""
    figure = Figure(figsize=(12, 2), facecolor="black")
    try:
        footer_axis = plot_engine._draw_footer_summary_bars(
            figure,
            station_counts=[1, 999],
            spot_counts=[1, 999],
            colors=[plot_engine.COLOR_JOINT, "#ffffff"],
            text_colors=["black", "black"],
            theme_config={
                "bar_face": "black",
                "bar_tick": "white",
                "bar_bbox": [0.12, 0.1, 0.85, 0.45],
            },
            stations_plural="STATIONS",
            evidence_plural="OPPORTUNITIES",
        )

        assert [text.get_text() for text in footer_axis.texts] == ["999", "999"]
        assert all("%" not in text.get_text() for text in footer_axis.texts)
    finally:
        dispose_matplotlib_figure(figure)


@pytest.mark.parametrize(
    ("analysis_id", "absolute_mode"),
    [
        ("RX_ABS", "RX"),
        ("TX_ABS", "TX"),
    ],
)
@pytest.mark.parametrize(
    ("language", "expected_footer"),
    [
        (
            "en",
            "Time: 01-Jul-2026 - 02-Jul-2026 | Band: 20m | "
            "Solar: All | Confirmed opportunities/station: ≥7 | "
            "Stations/segment: ≥3 | Segment: Station-balanced Decode Rate",
        ),
        (
            "de",
            "Zeitraum: 01-Jul-2026 - 02-Jul-2026 | Band: 20m | "
            "Sonnenstand: Ganze | Bestätigte Gelegenheiten/Station: ≥7 | "
            "Stationen/Segment: ≥3 | "
            "Segment: Stationsgleichgewichtete Dekodierrate",
        ),
    ],
)
def test_success_legend_colorbar_and_footer_are_mode_aware_and_localized(
    map_canvas_without_cartopy,
    analysis_id,
    absolute_mode,
    language,
    expected_footer,
):
    """Expose exact map-only terms and reconcile compact count-only footer rows."""
    labels = T[language]
    map_data = _success_map_data(analysis_id=analysis_id)
    map_data.station_rows = pd.DataFrame(
        {
            "peer_sign": ["TARGET_EVIDENCE", "ZERO_TARGET"],
            "peer_grid": ["AA00", "BB00"],
            "peer_lon": [1.0, 2.0],
            "peer_lat": [1.0, 2.0],
            "eligible": [True, True],
            "rate_pct": [100.0, 0.0],
            "hits": [113_492, 0],
            "misses": [0, 522_793],
            "opportunities": [113_492, 522_793],
            "target_only": [0, 0],
            "r_min": [0.0, 0.0],
        }
    )

    rendered = _render_map(
        map_data,
        language=language,
        minimum_opportunities=7,
        minimum_stations=3,
    )
    try:
        FigureCanvasAgg(rendered.figure).draw()
        assert rendered.footer_text == expected_footer
        assert "Elsewhere" not in rendered.footer_text
        assert "Other Signals" not in rendered.footer_text
        assert "Target+" not in rendered.footer_text
        assert "Target/(" not in rendered.footer_text
        assert ">=" not in rendered.footer_text
        mode_key = absolute_mode.lower()
        legend = _artist_with_gid(rendered.figure, SUCCESS_LEGEND_GID, Legend)
        assert [text.get_text() for text in legend.get_texts()] == [
            labels[f"map_success_{mode_key}_station_target"],
            labels[f"map_success_{mode_key}_station_counter"],
            labels["map_success_legend_insufficient"],
        ]
        legend_text = " ".join(text.get_text() for text in legend.get_texts())
        for retired_text in (
            "Target observed",
            "Zero-Target",
            "No qualifying segment",
            "Marker color: individual station Success Rate",
            "Sector color: station-balanced Success Rate",
        ):
            assert retired_text not in legend_text
        renderer = rendered.figure.canvas.get_renderer()
        map_bounds = rendered.figure.axes[0].get_window_extent(renderer)
        legend_bounds = legend.get_window_extent(renderer)
        map_center_x = (map_bounds.x0 + map_bounds.x1) / 2.0
        map_center_y = (map_bounds.y0 + map_bounds.y1) / 2.0
        map_radius = min(map_bounds.width, map_bounds.height) / 2.0
        closest_legend_x = np.clip(
            map_center_x,
            legend_bounds.x0,
            legend_bounds.x1,
        )
        closest_legend_y = np.clip(
            map_center_y,
            legend_bounds.y0,
            legend_bounds.y1,
        )
        assert np.hypot(
            closest_legend_x - map_center_x,
            closest_legend_y - map_center_y,
        ) >= map_radius

        colorbar_axis = next(
            axis
            for axis in rendered.figure.axes
            if axis.get_ylabel() == labels[f"cbar_abs_{absolute_mode.lower()}"]
        )
        assert colorbar_axis.get_ylabel() == labels[
            f"cbar_abs_{absolute_mode.lower()}"
        ]

        footer_axis = _artist_with_gid(
            rendered.figure,
            SUCCESS_FOOTER_GID,
            type(rendered.figure.axes[0]),
        )
        assert [tick.get_text() for tick in footer_axis.get_yticklabels()] == [
            labels["map_success_footer_stations"],
            labels["map_success_footer_opportunities"],
        ]
        station_tick, opportunity_tick = footer_axis.get_yticklabels()
        assert (
            opportunity_tick.get_window_extent(renderer).y0
            > station_tick.get_window_extent(renderer).y0
        )
        assert "SPOTS" not in {
            tick.get_text() for tick in footer_axis.get_yticklabels()
        }
        assert sorted(text.get_text() for text in footer_axis.texts) == sorted(
            ["1", "1", "113492", "522793"]
        )
        assert not any("%" in text.get_text() for text in footer_axis.texts)
        footer_patch_labels = {
            patch.get_gid(): patch.get_label() for patch in footer_axis.patches
        }
        assert footer_patch_labels == {
            "success-footer-stations-target": labels[
                f"map_success_{mode_key}_station_target"
            ],
            "success-footer-opportunities-target": labels[
                f"map_success_{mode_key}_opportunity_target"
            ],
            "success-footer-stations-counter": labels[
                f"map_success_{mode_key}_station_counter"
            ],
            "success-footer-opportunities-counter": labels[
                f"map_success_{mode_key}_opportunity_counter"
            ],
        }
    finally:
        dispose_matplotlib_figure(rendered.figure)


def test_compare_map_retains_existing_markers_legend_footer_and_scale(
    map_canvas_without_cartopy,
):
    """Fence the Success-only redesign away from the Compare presentation path."""
    labels = T["en"]
    station_rows = pd.DataFrame(
        {
            "peer_lon": [1.0, 2.0, 3.0, 4.0],
            "peer_lat": [1.0, 2.0, 3.0, 4.0],
            "r_min": [0.0, 0.0, 0.0, 0.0],
            "spot_count": [2, 0, 0, 0],
            "count_only_u": [0, 1, 3, 0],
            "count_only_r": [0, 2, 0, 4],
        }
    )
    segment_rows = pd.DataFrame(
        {
            "r_min": [0.0],
            "r_max": [2500.0],
            "az_bucket": [0.0],
            "val": [3.0],
        }
    )
    map_data = MapData(
        station_rows=station_rows,
        segment_rows=segment_rows,
        analysis_id="RX_COMP",
        is_compare=True,
        is_sequential=False,
        analysis_kind="comparison",
    )
    analysis_context = AnalysisContext(
        callsign="TARGET",
        qth="JJ00",
        band="20m",
        comparison_mode=COMPARISON_REFERENCE_STATION,
        reference_callsign="REFERENCE",
    )
    rendered = plot_engine.render_map_figure(
        map_data,
        title="Compare map",
        start_t=datetime(2026, 7, 1, tzinfo=timezone.utc),
        end_t=datetime(2026, 7, 2, tzinfo=timezone.utc),
        max_dist_km=5000,
        base_min_stations=1,
        lat_0=0.0,
        lon_0=0.0,
        analysis_context=analysis_context,
        presentation_context=_presentation_context(),
    )
    try:
        FigureCanvasAgg(rendered.figure).draw()
        assert not any(
            artist.get_gid()
            in {
                SUCCESS_TARGET_MARKERS_GID,
                SUCCESS_COUNTER_MARKERS_GID,
                SUCCESS_LEGEND_GID,
                SUCCESS_FOOTER_GID,
            }
            for artist in rendered.figure.findobj()
        )
        legend = rendered.figure.axes[0].get_legend()
        assert [text.get_text() for text in legend.get_texts()] == [
            labels["leg_joint"],
            labels["leg_both_async"],
            labels["leg_only_me"].format(callsign="TARGET"),
            labels["leg_only_ref"].format(ref_callsign="REFERENCE"),
        ]
        footer_axis = next(
            axis
            for axis in rendered.figure.axes
            if [tick.get_text() for tick in axis.get_yticklabels()]
            == ["STATIONS", "SPOTS"]
        )
        assert {text.get_text() for text in footer_axis.texts} == {
            "1",
            "2",
            "3",
            "4",
        }
        colorbar_axis = next(
            axis
            for axis in rendered.figure.axes
            if axis.get_ylabel() == labels["cbar_comp"]
        )
        assert colorbar_axis.get_ylabel() == labels["cbar_comp"]
    finally:
        dispose_matplotlib_figure(rendered.figure)
