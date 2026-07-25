from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from io import BytesIO
import threading
import time

import numpy as np
import pandas as pd
from matplotlib.collections import LineCollection, PatchCollection, QuadMesh
from matplotlib.colors import BoundaryNorm, ListedColormap, to_rgba
from matplotlib.figure import Figure
from matplotlib.legend import Legend
from matplotlib.transforms import IdentityTransform
from PIL import Image
import pytest

from core import map_base, plot_engine
from core.analysis_context import AnalysisContext, COMPARISON_REFERENCE_STATION
from core.map_models import MapData
from core.presentation_context import PresentationContext
from i18n import T, absolute_terms
from ui.matplotlib_renderer import (
    _draw_figure_preview_image,
    _serialize_preview_png,
    dispose_matplotlib_figure,
)
from ui.plots.evidence_figures import render_segment_insight_export_figure
from ui.plots.opportunity_figures import (
    _render_opportunity_segment_figure,
    _render_opportunity_selected_figure,
)
from ui.results_export import figure_to_png_bytes


def _assert_shared_evidence_legend(figure, legend, expected_labels):
    """Verify shared foreground styling and conventional key-first layout."""
    figure.canvas.draw()
    renderer = figure.canvas.get_renderer()

    assert [text.get_text() for text in legend.get_texts()] == expected_labels
    assert {text.get_fontsize() for text in legend.get_texts()} == {8.0}
    assert {
        tuple(text.get_fontfamily()) for text in legend.get_texts()
    } == {("sans-serif",)}
    assert {text.get_fontweight() for text in legend.get_texts()} == {"normal"}
    assert legend.get_zorder() == pytest.approx(10.0)
    assert legend.get_frame().get_alpha() == pytest.approx(0.9)
    assert legend.get_frame().get_facecolor()[:3] == pytest.approx(
        to_rgba("#121212")[:3]
    )
    assert legend.get_frame().get_edgecolor()[:3] == pytest.approx(
        to_rgba("#444444")[:3]
    )
    for legend_handle, legend_text in zip(
        legend.legend_handles,
        legend.get_texts(),
    ):
        assert (
            legend_handle.get_window_extent(renderer).x1
            < legend_text.get_window_extent(renderer).x0
        )


def _assert_shared_axis_label(label_artist, expected_text):
    """Verify one Success axis uses the shared evidence-label typography."""
    assert label_artist.get_text() == expected_text
    assert label_artist.get_fontsize() == pytest.approx(10.0)
    assert tuple(label_artist.get_fontfamily()) == ("sans-serif",)
    assert label_artist.get_fontweight() == "normal"


@pytest.mark.parametrize(
    ("segment_values", "expected_half_span_db", "expected_tick_step_db"),
    [
        ([], 6.0, 1.0),
        ([np.nan, np.inf, -np.inf], 6.0, 1.0),
        ([-3.1, 3.1], 6.0, 1.0),
        ([-6.5, 6.5], 6.0, 1.0),
        ([np.nextafter(6.5, np.inf)], 6.0, 3.0),
        ([np.nextafter(-6.5, -np.inf)], 6.0, 3.0),
        ([7.5], 6.0, 3.0),
        ([np.nextafter(7.5, np.inf)], 9.0, 3.0),
        ([12.0], 12.0, 3.0),
        ([19.5], 18.0, 3.0),
        ([np.nextafter(19.5, np.inf)], 18.0, 6.0),
        ([39.0], 36.0, 6.0),
        ([np.nextafter(39.0, np.inf)], 40.0, 10.0),
        ([65.0], 60.0, 10.0),
        ([np.nextafter(65.0, np.inf)], 60.0, 20.0),
    ],
)
def test_compare_map_scale_fits_data_without_fixed_headroom(
    segment_values,
    expected_half_span_db,
    expected_tick_step_db,
):
    """Use the finest symmetric layout whose outer half-bin contains the data."""
    scale = plot_engine._build_compare_map_color_scale(segment_values)
    expected_outer_boundary_db = (
        expected_half_span_db + (expected_tick_step_db / 2.0)
    )
    finite_segment_values = np.asarray(segment_values, dtype=float)
    finite_segment_values = finite_segment_values[
        np.isfinite(finite_segment_values)
    ]

    assert isinstance(scale.colormap, ListedColormap)
    assert isinstance(scale.normalization, BoundaryNorm)
    assert scale.normalization.vmin == pytest.approx(
        -expected_outer_boundary_db
    )
    assert scale.normalization.vmax == pytest.approx(
        expected_outer_boundary_db
    )
    assert scale.colormap.N == len(scale.boundaries_db) - 1
    assert scale.colormap.N % 2 == 1
    assert scale.boundaries_db == tuple(
        -value for value in reversed(scale.boundaries_db)
    )
    assert int(scale.normalization(scale.boundaries_db[0])) == 0
    assert (
        int(scale.normalization(scale.boundaries_db[-1]))
        == scale.colormap.N - 1
    )
    assert scale.ticks_db[0] == pytest.approx(-expected_half_span_db)
    assert scale.ticks_db[-1] == pytest.approx(expected_half_span_db)
    assert np.diff(scale.ticks_db) == pytest.approx(expected_tick_step_db)
    assert scale.ticks_db == tuple(-value for value in reversed(scale.ticks_db))
    assert scale.tick_labels[len(scale.tick_labels) // 2] == "0"
    assert all("S" not in label for label in scale.tick_labels)
    if finite_segment_values.size:
        assert np.max(np.abs(finite_segment_values)) <= (
            scale.boundaries_db[-1]
        )


@pytest.mark.parametrize(
    (
        "segment_values",
        "expected_tick_step_db",
        "expected_positive_boundaries_db",
    ),
    [
        ([-3.0, 3.0], 1.0, (0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5)),
        ([7.6], 3.0, (1.5, 4.5, 7.5, 10.5)),
        ([19.6], 6.0, (3.0, 9.0, 15.0, 21.0)),
        ([39.1], 10.0, (5.0, 15.0, 25.0, 35.0, 45.0)),
    ],
)
def test_compare_map_scale_uses_equal_width_bins(
    segment_values,
    expected_tick_step_db,
    expected_positive_boundaries_db,
):
    """Give every color, including neutral, the active dB-step width."""
    scale = plot_engine._build_compare_map_color_scale(segment_values)
    center_boundary_index = len(scale.boundaries_db) // 2
    bin_midpoints_db = (
        np.asarray(scale.boundaries_db[:-1])
        + np.asarray(scale.boundaries_db[1:])
    ) / 2.0

    assert scale.boundaries_db[center_boundary_index:] == pytest.approx(
        expected_positive_boundaries_db
    )
    assert np.diff(scale.boundaries_db) == pytest.approx(
        expected_tick_step_db
    )
    assert bin_midpoints_db == pytest.approx(scale.ticks_db)
    neutral_bin_index = scale.colormap.N // 2
    neutral_half_width_db = expected_tick_step_db / 2.0
    assert (
        int(scale.normalization(-neutral_half_width_db))
        == neutral_bin_index
    )
    assert (
        int(scale.normalization(neutral_half_width_db))
        == neutral_bin_index
    )
    for positive_boundary_db in expected_positive_boundaries_db[:-1]:
        positive_outward_db = np.nextafter(positive_boundary_db, np.inf)
        negative_outward_db = np.nextafter(-positive_boundary_db, -np.inf)
        assert (
            int(scale.normalization(-positive_boundary_db))
            + int(scale.normalization(positive_boundary_db))
            == scale.colormap.N - 1
        )
        assert (
            int(scale.normalization(negative_outward_db))
            + int(scale.normalization(positive_outward_db))
            == scale.colormap.N - 1
        )


def test_compare_map_scale_uses_discrete_soft_matte_palette():
    """Use distinct hue landmarks without reversing Target and Reference."""
    scale = plot_engine._build_compare_map_color_scale([-3.0, 3.0])
    middle_color_index = len(plot_engine.COMPARE_MAP_COLORS) // 2
    neutral_bin_index = scale.colormap.N // 2

    assert isinstance(scale.colormap, ListedColormap)
    assert plot_engine.COMPARE_MAP_COLORS == (
        "#6e4c8f",
        "#6576b8",
        "#5c9bc7",
        "#55b9c0",
        "#8bcb9a",
        "#c9e5a3",
        "#f4e58a",
        "#efb56f",
        "#df7f68",
        "#b85d5f",
        "#7c5341",
    )
    assert scale.colormap.N == 13
    assert scale.colormap(0.0) == pytest.approx(
        to_rgba(plot_engine.COMPARE_MAP_COLORS[0])
    )
    assert scale.colormap(0.5) == pytest.approx(
        to_rgba(plot_engine.COMPARE_MAP_COLORS[middle_color_index])
    )
    assert scale.colormap(1.0) == pytest.approx(
        to_rgba(plot_engine.COMPARE_MAP_COLORS[-1])
    )
    neutral_red, neutral_green, neutral_blue, _ = scale.colormap(0.5)
    assert neutral_green > neutral_red > neutral_blue
    assert min(neutral_red, neutral_green, neutral_blue) > 0.60
    neutral_rgb = np.asarray(
        (neutral_red, neutral_green, neutral_blue),
        dtype=float,
    )
    white_export_rgb = np.ones(3, dtype=float)
    composited_neutral_rgb = (
        plot_engine.COMPARE_MAP_HEATMAP_ALPHA * neutral_rgb
        + (1.0 - plot_engine.COMPARE_MAP_HEATMAP_ALPHA) * white_export_rgb
    )
    assert np.linalg.norm(
        white_export_rgb - composited_neutral_rgb
    ) > 0.30
    negative_red, _, negative_blue, _ = scale.colormap(
        scale.normalization(-3.0)
    )
    positive_red, _, positive_blue, _ = scale.colormap(
        scale.normalization(3.0)
    )
    assert negative_blue > negative_red
    assert positive_red > positive_blue
    assert int(scale.normalization(-0.49)) == neutral_bin_index
    assert int(scale.normalization(0.49)) == neutral_bin_index
    assert int(scale.normalization(-0.5)) == neutral_bin_index
    assert int(scale.normalization(0.5)) == neutral_bin_index
    for delta_snr_db in (0.0, 0.49, 0.5, 1.0, 3.0, 5.0, 6.0):
        assert (
            int(scale.normalization(-delta_snr_db))
            + int(scale.normalization(delta_snr_db))
            == scale.colormap.N - 1
        )
    for positive_boundary_db in scale.boundaries_db[
        (len(scale.boundaries_db) // 2):-1
    ]:
        positive_outward_db = np.nextafter(positive_boundary_db, np.inf)
        negative_outward_db = np.nextafter(-positive_boundary_db, -np.inf)
        assert (
            int(scale.normalization(negative_outward_db))
            + int(scale.normalization(positive_outward_db))
            == scale.colormap.N - 1
        )


def test_compare_map_scale_handles_very_large_finite_values():
    """Keep tick selection bounded for an extreme plausible display value."""
    scale = plot_engine._build_compare_map_color_scale([1_000_000.0])

    assert scale.normalization.vmax >= 1_000_000.0
    assert scale.normalization.vmin == -scale.normalization.vmax
    assert (
        len(scale.ticks_db)
        <= plot_engine.COMPARE_MAP_ADAPTIVE_MAXIMUM_TICK_COUNT
    )


def test_compare_map_renderer_scales_only_from_visible_segments(monkeypatch):
    """Exclude off-map extremes from the stepped Compare colorbar contract."""
    def fake_create_base_map_figure(**_kwargs):
        figure = Figure(figsize=(8, 8), facecolor="black")
        map_axis = figure.add_axes([0.05, 0.15, 0.75, 0.75])
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
    station_rows = pd.DataFrame(
        {
            "peer_lon": [1.0],
            "peer_lat": [1.0],
            "spot_count": [2],
            "count_only_u": [0],
            "count_only_r": [0],
            "r_min": [0.0],
        }
    )
    segment_rows = pd.DataFrame(
        {
            "r_min": [0.0, 2500.0, 5000.0],
            "r_max": [2500.0, 5000.0, 10000.0],
            "az_bucket": [0.0, 1.0, 2.0],
            "val": [12.0, np.nan, 100.0],
        }
    )
    map_data = MapData(
        station_rows=station_rows,
        segment_rows=segment_rows,
        analysis_id="RX_COMPARE",
        is_compare=True,
        is_sequential=False,
        analysis_kind="compare",
    )
    analysis_context = AnalysisContext(
        callsign="TARGET",
        qth="JN47",
        band="20m",
        comparison_mode=COMPARISON_REFERENCE_STATION,
        reference_callsign="REFERENCE",
    )
    presentation_context = PresentationContext(
        language="en",
        labels=T["en"],
        theme="dark",
        solar_label="All",
    )

    rendered_map = plot_engine.render_map_figure(
        map_data,
        title="Compare map",
        start_t=datetime(2026, 7, 1, tzinfo=timezone.utc),
        end_t=datetime(2026, 7, 2, tzinfo=timezone.utc),
        max_dist_km=5000,
        base_min_stations=1,
        lat_0=0.0,
        lon_0=0.0,
        analysis_context=analysis_context,
        presentation_context=presentation_context,
    )
    try:
        map_axis = rendered_map.figure.axes[0]
        heatmap = next(
            collection
            for collection in map_axis.collections
            if isinstance(collection, PatchCollection)
        )
        colorbar_axis = next(
            axis
            for axis in rendered_map.figure.axes
            if axis.get_ylabel() == T["en"]["cbar_comp"]
        )
        expected_boundaries_db = (
            -13.5,
            -10.5,
            -7.5,
            -4.5,
            -1.5,
            1.5,
            4.5,
            7.5,
            10.5,
            13.5,
        )

        assert isinstance(heatmap.cmap, ListedColormap)
        assert isinstance(heatmap.norm, BoundaryNorm)
        assert heatmap.get_alpha() == pytest.approx(
            plot_engine.COMPARE_MAP_HEATMAP_ALPHA
        )
        assert heatmap.norm.vmin == pytest.approx(-13.5)
        assert heatmap.norm.vmax == pytest.approx(13.5)
        assert heatmap.norm.boundaries == pytest.approx(
            (
                -13.5,
                -10.5,
                -7.5,
                -4.5,
                -1.5,
                np.nextafter(1.5, np.inf),
                np.nextafter(4.5, np.inf),
                np.nextafter(7.5, np.inf),
                np.nextafter(10.5, np.inf),
                13.5,
            )
        )
        heatmap_values = heatmap.get_array()
        assert np.ma.isMaskedArray(heatmap_values)
        assert heatmap_values.compressed() == pytest.approx([12.0])
        assert np.ma.getmaskarray(heatmap_values).tolist() == [False, True]
        assert colorbar_axis.get_position().bounds == pytest.approx(
            plot_engine.COMPARE_MAP_CBAR_BBOX
        )
        assert colorbar_axis.get_ylim() == pytest.approx((-13.5, 13.5))
        assert [tick.get_text() for tick in colorbar_axis.get_yticklabels()] == [
            "\u221212",
            "\u22129",
            "\u22126",
            "\u22123",
            "0",
            "+3",
            "+6",
            "+9",
            "+12",
        ]
        colorbar_solid = next(
            collection
            for collection in colorbar_axis.collections
            if isinstance(collection, QuadMesh)
        )
        assert colorbar_solid.get_alpha() == pytest.approx(
            plot_engine.COMPARE_MAP_HEATMAP_ALPHA
        )
        assert colorbar_solid.get_array().size == 9
        assert (
            colorbar_solid.get_coordinates()[:, 0, 1].tolist()
            == pytest.approx(expected_boundaries_db)
        )
        rendered_boundary_y = colorbar_axis.transData.transform(
            np.column_stack(
                (
                    np.zeros(len(expected_boundaries_db)),
                    expected_boundaries_db,
                )
            )
        )[:, 1]
        rendered_height_fractions = np.diff(rendered_boundary_y)
        rendered_height_fractions /= rendered_height_fractions.sum()
        expected_height_fractions = np.diff(expected_boundaries_db)
        expected_height_fractions /= expected_height_fractions.sum()
        assert rendered_height_fractions == pytest.approx(
            expected_height_fractions
        )
        assert colorbar_solid.get_linewidths() == pytest.approx(0.0)
        assert len(colorbar_solid.get_edgecolors()) == 0
        bin_dividers = next(
            collection
            for collection in colorbar_axis.collections
            if (
                isinstance(collection, LineCollection)
                and collection.get_gid() == "compare-map-bin-dividers"
            )
        )
        assert bin_dividers.get_alpha() == pytest.approx(
            plot_engine.COMPARE_MAP_COLORBAR_DIVIDER_ALPHA
        )
        assert bin_dividers.get_linewidths() == pytest.approx(
            plot_engine.COMPARE_MAP_COLORBAR_DIVIDER_LINEWIDTH
        )
        assert [
            float(segment[0][1])
            for segment in bin_dividers.get_segments()
        ] == pytest.approx(expected_boundaries_db[1:-1])
    finally:
        dispose_matplotlib_figure(rendered_map.figure)


def test_map_figure_stays_outside_pyplot_registry_and_disposes_artists():
    from matplotlib._pylab_helpers import Gcf

    managers_before = tuple(Gcf.get_all_fig_managers())
    figure = map_base._new_map_figure({"fig_face": "black"})
    axis = figure.add_axes([0.0, 0.0, 1.0, 1.0])
    axis.imshow(np.zeros((8, 8, 3), dtype=np.uint8))
    figure.canvas.draw()

    assert tuple(Gcf.get_all_fig_managers()) == managers_before
    assert len(figure.axes) == 1

    dispose_matplotlib_figure(figure)

    assert tuple(Gcf.get_all_fig_managers()) == managers_before
    assert figure.axes == []


def test_footer_summary_renderer_always_draws_spots_and_stations_rows():
    from matplotlib.figure import Figure

    figure = Figure(figsize=(8, 2), facecolor="black")
    try:
        summary_axis = plot_engine._draw_footer_summary_bars(
            figure,
            station_counts=[3, 7],
            spot_counts=[20, 80],
            colors=["#39ff14", "#d0d0d0"],
            text_colors=["black", "black"],
            theme_config={
                "bar_face": "black",
                "bar_tick": "white",
                "bar_bbox": [0.12, 0.1, 0.8, 0.6],
            },
        )

        assert [tick.get_text() for tick in summary_axis.get_yticklabels()] == [
            "STATIONS",
            "SPOTS",
        ]
        assert len(summary_axis.patches) == 4
        assert {label.get_text() for label in summary_axis.texts} == {
            "3",
            "7",
            "20",
            "80",
        }
    finally:
        dispose_matplotlib_figure(figure)


def test_cached_basemap_pixels_are_compact_uint8_rgb(tmp_path):
    cache_path = tmp_path / "basemap.png"
    source_pixels = np.zeros((12, 10, 4), dtype=np.uint8)
    source_pixels[..., 0] = 17
    source_pixels[..., 1] = 34
    source_pixels[..., 2] = 51
    source_pixels[..., 3] = 255
    Image.fromarray(source_pixels, mode="RGBA").save(cache_path)

    loaded_pixels = map_base._load_cached_basemap_pixels(cache_path)

    assert loaded_pixels.dtype == np.uint8
    assert loaded_pixels.shape == (12, 10, 3)
    assert loaded_pixels.nbytes == 12 * 10 * 3
    assert loaded_pixels[0, 0].tolist() == [17, 34, 51]


def test_cached_preview_draws_map_annotations_above_segment_wedges(tmp_path, monkeypatch):
    """Keep labels dynamic so cached background pixels cannot cover their z-order."""
    cache_path = tmp_path / "basemap.png"
    Image.fromarray(np.zeros((12, 10, 3), dtype=np.uint8), mode="RGB").save(cache_path)
    monkeypatch.setattr(
        map_base,
        "_ensure_static_basemap_cache",
        lambda **_kwargs: (cache_path, "hit"),
    )

    figure, axis, _map_projection, _plate_carree_projection, _cache_detail = (
        map_base.create_preview_cached_base_map_figure(
            title="Foreground annotation test",
            maximum_distance_km=22000,
            center_latitude=0.0,
            center_longitude=0.0,
            theme_name="dark",
            theme_config=plot_engine.MAP_THEMES["dark"],
        )
    )

    try:
        annotation_texts = {
            text_artist.get_text().strip(): text_artist for text_artist in axis.texts
        }
        assert {"10000 km", "15000 km", "20000 km", "N-POL", "S-POL"} <= set(
            annotation_texts
        )
        assert all(
            text_artist.get_zorder() > 3 for text_artist in annotation_texts.values()
        )
        assert len(axis.lines) == 2
        assert all(
            pole_marker.get_zorder() > 3 for pole_marker in axis.lines
        )
    finally:
        dispose_matplotlib_figure(figure)


def test_renderer_upgrades_base_canvas_and_uses_stable_local_agg_canvas():
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure

    figure = Figure(figsize=(4, 3), facecolor="black")
    axis = figure.add_subplot(1, 1, 1)
    axis.plot([0, 1], [0, 1])
    assert not isinstance(figure.canvas, FigureCanvasAgg)

    try:
        image, dimensions = _draw_figure_preview_image(figure, dpi=80)
    finally:
        dispose_matplotlib_figure(figure)

    assert image.mode == "RGBA"
    assert dimensions == (320, 240)
    assert isinstance(figure.canvas, FigureCanvasAgg)


def test_static_basemap_save_uses_atomic_temporary_file_and_cleans_it(tmp_path):
    cache_path = tmp_path / "basemap.png"
    figure = map_base._new_map_figure({"fig_face": "black"})
    axis = figure.add_axes([0.0, 0.0, 1.0, 1.0])
    axis.imshow(np.full((8, 8, 3), 127, dtype=np.uint8))

    try:
        map_base._save_static_basemap_preview(figure, cache_path, preview_dpi=10)
    finally:
        dispose_matplotlib_figure(figure)

    assert cache_path.exists()
    with Image.open(cache_path) as cached_image:
        cached_image.verify()
    assert list(tmp_path.glob("*.tmp")) == []


def test_same_basemap_key_is_created_once_under_concurrency(tmp_path, monkeypatch):
    worker_count = 6
    start_barrier = threading.Barrier(worker_count)
    build_count = 0
    build_count_lock = threading.Lock()

    class FakeFigure:
        def clear(self):
            return None

    def fake_create_base_map_figure(**_kwargs):
        nonlocal build_count
        with build_count_lock:
            build_count += 1
        return FakeFigure(), None, None, None

    def fake_save_static_basemap_preview(_figure, cache_path, _preview_dpi):
        time.sleep(0.05)
        cache_path.write_bytes(b"complete-basemap")

    monkeypatch.setattr(map_base, "CACHE_DIR", str(tmp_path))
    monkeypatch.setattr(map_base, "create_base_map_figure", fake_create_base_map_figure)
    monkeypatch.setattr(map_base, "_save_static_basemap_preview", fake_save_static_basemap_preview)

    def ensure_cache():
        start_barrier.wait()
        return map_base._ensure_static_basemap_cache(
            maximum_distance_km=22000,
            center_latitude=47.5,
            center_longitude=7.0,
            theme_name="dark",
            theme_config={"fig_face": "black"},
            cache_label="JN37",
            preview_dpi=100,
        )

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        results = list(executor.map(lambda _index: ensure_cache(), range(worker_count)))

    cache_paths = [cache_path for cache_path, _status in results]
    cache_statuses = [status for _cache_path, status in results]
    assert build_count == 1
    assert cache_statuses.count("miss") == 1
    assert cache_statuses.count("hit") == worker_count - 1
    assert len(set(cache_paths)) == 1
    assert cache_paths[0].read_bytes() == b"complete-basemap"
    assert map_base.ARTIFACT_STORE.lock_bookkeeping_size == 64
    assert list(tmp_path.glob(".artifact-locks/*.lock")) == []


def test_segment_and_opportunity_figures_render_concurrently_without_pyplot_state():
    from matplotlib._pylab_helpers import Gcf

    worker_count = 6
    start_barrier = threading.Barrier(worker_count)
    managers_before = tuple(Gcf.get_all_fig_managers())
    segment_recipe = {
        "title": "Concurrent Segment Insight",
        "selected_segment": "Full Range | All Directions",
        "is_compare": True,
        "is_sequential": False,
        "compare_layout": True,
        "station_values": np.array([-1.0, 0.0, 1.0]),
        "spot_values": np.array([-2.0, -1.0, 0.0, 1.0, 2.0]),
        "panel_counts": [],
        "panel_station_counts": [1, 3, 1, 1],
        "panel_spot_counts": [2, 10, 3, 1],
        "panel_series_labels": ["Stations", "Spots"],
        "panel_labels": ["Target", "Joint", "Both (Async)", "Reference"],
        "panel_y_label": "Share (%)",
    }
    time_ns = np.array(
        [
            np.datetime64("2026-07-10T00:00:00", "ns").astype(np.int64),
            np.datetime64("2026-07-10T03:00:00", "ns").astype(np.int64),
        ],
        dtype=np.int64,
    )
    opportunity_recipe = {
        "kind": "opportunity",
        "title": "Concurrent Opportunity Insight",
        "absolute_mode": "RX",
        "terminology": absolute_terms(T["en"], "RX"),
        "selected_segment": "Full Range | All Directions",
        "time_bin": "3h",
        "station_trials": np.array([5.0, 10.0, 20.0]),
        "station_hits": np.array([1.0, 5.0, 15.0]),
        "station_rates": np.array([20.0, 50.0, 75.0]),
        "minimum_trials": 5,
        "range_labels": ["0-2500 km"],
        "time_ns": time_ns,
        "station_rate_grid": np.array([[20.0, 60.0]]),
        "overall_rate_grid": np.array([[25.0, 65.0]]),
    }

    def render_figure(task_index):
        start_barrier.wait()
        figure = (
            render_segment_insight_export_figure(segment_recipe)
            if task_index % 2 == 0
            else _render_opportunity_segment_figure(opportunity_recipe)
        )
        try:
            image, dimensions = _draw_figure_preview_image(figure, dpi=60)
            image_buffer = BytesIO()
            _serialize_preview_png(image, image_buffer)
            return image_buffer.getvalue(), dimensions
        finally:
            dispose_matplotlib_figure(figure)

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        results = list(executor.map(render_figure, range(worker_count)))

    assert tuple(Gcf.get_all_fig_managers()) == managers_before
    for image_bytes, dimensions in results:
        assert image_bytes.startswith(b"\x89PNG\r\n\x1a\n")
        assert dimensions[0] > 0
        assert dimensions[1] > 0


def test_high_resolution_export_uses_shared_matplotlib_runtime():
    recipe = {
        "title": "Export Segment Insight",
        "selected_segment": "Full Range | All Directions",
        "is_compare": True,
        "is_sequential": False,
        "compare_layout": True,
        "station_values": np.array([-1.0, 0.0, 1.0]),
        "spot_values": np.array([-2.0, 0.0, 2.0]),
        "panel_counts": [],
        "panel_station_counts": [1, 3, 1, 1],
        "panel_spot_counts": [2, 6, 2, 2],
        "panel_series_labels": ["Stations", "Spots"],
        "panel_labels": ["Target", "Joint", "Both (Async)", "Reference"],
        "panel_y_label": "Share (%)",
    }
    figure = render_segment_insight_export_figure(recipe)
    try:
        image_bytes = figure_to_png_bytes(figure, dpi=80, paper_theme=True)
    finally:
        dispose_matplotlib_figure(figure)

    assert image_bytes.startswith(b"\x89PNG\r\n\x1a\n")


def test_compare_segment_histograms_share_median_legend_and_mean_placement():
    """Standardize Compare median legends and separate Mean annotations."""
    recipe = {
        "title": "RX Compare",
        "selected_segment": "Full Range | All Directions",
        "is_compare": True,
        "is_sequential": False,
        "compare_layout": True,
        "station_values": np.array([6.0, 7.0]),
        "spot_values": np.array([6.0, 8.0]),
        "panel_counts": [],
        "panel_station_counts": [1, 2, 0, 1],
        "panel_spot_counts": [2, 8, 1, 3],
        "panel_series_labels": ["Stations", "Spots"],
        "panel_labels": ["Target", "Joint", "Both (Async)", "Reference"],
        "panel_y_label": "Share (%)",
    }

    figure = render_segment_insight_export_figure(recipe)
    try:
        station_axis = next(
            axis for axis in figure.axes if axis.get_title().startswith("Station Medians")
        )
        spot_axis = next(
            axis for axis in figure.axes if axis.get_title() == "Joint-Spot \u0394 SNR"
        )
        station_labels = [
            text.get_text() for text in station_axis.get_legend().get_texts()
        ]
        spot_labels = [
            text.get_text() for text in spot_axis.get_legend().get_texts()
        ]

        assert station_labels == ["Median +6.5 dB"]
        assert spot_labels == ["Median +7.0 dB"]
        assert not any(
            "Stability" in label
            for label in [*station_labels, *spot_labels]
        )
        assert {
            text.get_text()
            for text in station_axis.texts
            if text.get_gid() == "compare-metric-mean"
        } == {"Mean +6.5 dB"}
        assert {
            text.get_text()
            for text in spot_axis.texts
            if text.get_gid() == "compare-metric-mean"
        } == {"Mean +7.0 dB"}
        for axis in (station_axis, spot_axis):
            mean_annotation = next(
                text
                for text in axis.texts
                if text.get_gid() == "compare-metric-mean"
            )
            assert mean_annotation.get_position() == pytest.approx((0.98, 0.04))
            assert mean_annotation.get_fontsize() == pytest.approx(8.0)
            assert mean_annotation.get_zorder() == pytest.approx(10.0)
            assert {
                text.get_fontsize()
                for text in axis.get_legend().get_texts()
            } == {8.0}
    finally:
        dispose_matplotlib_figure(figure)


def test_compare_outcomes_and_station_histogram_share_station_hatching():
    """Keep split inside legends and dense station hatching across Compare."""
    recipe = {
        "title": "RX Compare",
        "selected_segment": "Full Range | All Directions",
        "is_compare": True,
        "is_sequential": False,
        "compare_layout": True,
        "station_values": np.array([-2.0, 0.0, 2.0]),
        "spot_values": np.array([-3.0, -1.0, 1.0, 3.0]),
        "panel_counts": [],
        "panel_station_counts": [1, 2, 0, 1],
        "panel_spot_counts": [1, 198, 1, 0],
        "panel_series_labels": ["Stations", "Spots"],
        "panel_labels": ["Target only", "Joint", "Both (Async)", "Reference only"],
        "panel_y_label": "Share (%)",
    }

    figure = render_segment_insight_export_figure(recipe)
    try:
        outcome_axis = next(
            axis for axis in figure.axes if axis.get_title() == "Decode Outcomes"
        )
        station_bars = [
            patch
            for patch in outcome_axis.patches
            if patch.get_gid() == "decode-outcome-stations"
        ]
        spot_bars = [
            patch
            for patch in outcome_axis.patches
            if patch.get_gid() == "decode-outcome-spots"
        ]

        assert len(station_bars) == len(spot_bars) == 4
        for station_bar, spot_bar in zip(station_bars, spot_bars):
            station_center = station_bar.get_x() + station_bar.get_width() / 2.0
            spot_center = spot_bar.get_x() + spot_bar.get_width() / 2.0
            assert station_center < spot_center
            assert station_bar.get_hatch() == "//////"
            assert station_bar.get_facecolor()[3] == pytest.approx(0.0)
            assert spot_bar.get_hatch() is None
            assert spot_bar.get_facecolor()[:3] == pytest.approx(
                to_rgba("#36aaf9")[:3]
            )

        assert [
            text.get_text()
            for text in outcome_axis.texts
            if text.get_gid() == "decode-outcome-percentage"
        ] == [
            "25%",
            "50%",
            "0%",
            "25%",
            "<1%",
            "99%",
            "<1%",
            "0%",
        ]
        assert outcome_axis.get_ylabel() == "Share (%)"
        assert outcome_axis.get_ylim() == pytest.approx((0.0, 120.0))
        assert max(outcome_axis.get_yticks()) == pytest.approx(100.0)
        outcome_legends = {
            artist.get_gid(): artist
            for artist in outcome_axis.get_children()
            if isinstance(artist, Legend)
        }
        assert [
            text.get_text()
            for text in outcome_legends[
                "decode-outcome-station-legend"
            ].get_texts()
        ] == ["Stations"]
        assert [
            text.get_text()
            for text in outcome_legends[
                "decode-outcome-spot-legend"
            ].get_texts()
        ] == ["Spots"]
        figure.canvas.draw()
        renderer = figure.canvas.get_renderer()
        axis_center_x = outcome_axis.get_window_extent(renderer).x0 + (
            outcome_axis.get_window_extent(renderer).width / 2.0
        )
        assert (
            outcome_legends["decode-outcome-station-legend"]
            .get_window_extent(renderer)
            .x1
            < axis_center_x
        )
        assert (
            outcome_legends["decode-outcome-spot-legend"]
            .get_window_extent(renderer)
            .x0
            > axis_center_x
        )

        station_axis = next(
            axis for axis in figure.axes if axis.get_title().startswith("Station Medians")
        )
        spot_axis = next(
            axis for axis in figure.axes if axis.get_title() == "Joint-Spot \u0394 SNR"
        )
        station_histogram_bars = [
            patch
            for patch in station_axis.patches
            if patch.get_gid() == "station-median-histogram"
        ]
        spot_histogram_bars = [
            patch
            for patch in spot_axis.patches
            if patch.get_gid() == "spot-metric-histogram"
        ]
        assert station_histogram_bars
        assert spot_histogram_bars
        assert {
            patch.get_hatch() for patch in station_histogram_bars
        } == {"//////"}
        assert {
            patch.get_facecolor()[3] for patch in station_histogram_bars
        } == {0.0}
        assert {
            patch.get_hatch() for patch in spot_histogram_bars
        } == {None}
        for patch in spot_histogram_bars:
            assert patch.get_facecolor()[:3] == pytest.approx(
                to_rgba("#36aaf9")[:3]
            )
    finally:
        dispose_matplotlib_figure(figure)


def test_success_segment_histograms_do_not_adopt_compare_mean_summary():
    """Keep the reusable summary artists opt-in for Compare during this change."""
    recipe = {
        "title": "RX Success",
        "selected_segment": "Full Range | All Directions",
        "is_compare": False,
        "is_sequential": False,
        "compare_layout": False,
        "station_values": np.array([-12.0, -10.0, -8.0]),
        "spot_values": np.array([-15.0, -12.0, -9.0]),
        "panel_counts": [2, 6],
        "panel_labels": ["Stations", "Spots"],
        "panel_y_label": "Count",
    }

    figure = render_segment_insight_export_figure(recipe)
    try:
        station_axis = next(
            axis for axis in figure.axes if axis.get_title().startswith("Station Medians")
        )
        spot_axis = next(
            axis for axis in figure.axes if axis.get_title().startswith("Spot SNR")
        )
        for axis in (station_axis, spot_axis):
            assert not any(
                text.get_gid() == "compare-metric-mean"
                for text in axis.texts
            )
            legend_labels = [
                text.get_text() for text in axis.get_legend().get_texts()
            ]
            assert len(legend_labels) == 1
            assert legend_labels[0].startswith("Median ")
            assert not any("Stability" in label for label in legend_labels)
    finally:
        dispose_matplotlib_figure(figure)


def test_success_segment_figure_uses_shared_legend_and_axis_label_style():
    """Apply the reusable visual language without adding summary statistics."""
    terms = absolute_terms(T["en"], "RX")
    time_ns = np.array(
        [
            np.datetime64("2026-07-10T00:00:00", "ns").astype(np.int64),
            np.datetime64("2026-07-10T03:00:00", "ns").astype(np.int64),
        ],
        dtype=np.int64,
    )
    recipe = {
        "kind": "opportunity",
        "title": "RX Success",
        "absolute_mode": "RX",
        "terminology": terms,
        "selected_segment": "Full Range | All Directions",
        "time_bin": "3h",
        "station_trials": np.array([5.0, 10.0, 20.0]),
        "station_hits": np.array([1.0, 5.0, 15.0]),
        "station_rates": np.array([20.0, 50.0, 75.0]),
        "minimum_trials": 5,
        "range_labels": ["0-2500 km"],
        "time_ns": time_ns,
        "station_rate_grid": np.array([[20.0, 60.0]]),
        "overall_rate_grid": np.array([[25.0, 65.0]]),
    }

    figure = _render_opportunity_segment_figure(recipe)
    try:
        rates_axis = next(
            axis
            for axis in figure.axes
            if axis.get_title() == "Station Success Rate by Evidence Count"
        )
        station_time_axis = next(
            axis
            for axis in figure.axes
            if axis.get_title().startswith("Average Station Success Rate")
        )
        observation_time_axis = next(
            axis
            for axis in figure.axes
            if axis.get_title().startswith("Observation-Level Success Rate")
        )
        colorbar_axis = next(
            axis
            for axis in figure.axes
            if axis.get_ylabel().startswith("Success Rate:")
        )

        _assert_shared_evidence_legend(
            figure,
            rates_axis.get_legend(),
            [
                "Station with Target evidence",
                f"{terms['pair']} threshold 5",
            ],
        )
        _assert_shared_axis_label(
            rates_axis.xaxis.label,
            f"Evidence Count (Target + {terms['counter']})",
        )
        _assert_shared_axis_label(rates_axis.yaxis.label, "Success Rate (%)")
        _assert_shared_axis_label(
            station_time_axis.xaxis.label,
            "Date/Time (UTC)",
        )
        _assert_shared_axis_label(
            station_time_axis.yaxis.label,
            "Distance range",
        )
        _assert_shared_axis_label(
            observation_time_axis.xaxis.label,
            "Date/Time (UTC)",
        )
        assert observation_time_axis.get_ylabel() == ""
        _assert_shared_axis_label(
            colorbar_axis.yaxis.label,
            f"Success Rate: {terms['formula_spaced']}",
        )
        visible_legend_labels = [
            text.get_text() for text in rates_axis.get_legend().get_texts()
        ]
        assert not any(
            summary_term in label
            for label in visible_legend_labels
            for summary_term in ("Median", "Mean", "Stability")
        )
    finally:
        dispose_matplotlib_figure(figure)


def test_selected_success_figure_uses_shared_legend_and_axis_label_style():
    """Keep selected Success evidence compact and visually consistent."""
    time_ns = np.array(
        [
            np.datetime64("2026-07-10T00:00:00", "ns").astype(np.int64),
            np.datetime64("2026-07-10T03:00:00", "ns").astype(np.int64),
        ],
        dtype=np.int64,
    )
    terms = absolute_terms(T["en"], "RX")
    recipe = {
        "kind": "opportunity",
        "title": "Selected Station Evidence: OK1FCX (JN79)",
        "absolute_mode": "RX",
        "terminology": terms,
        "time_bin": "3h",
        "time_ns": time_ns,
        "rate_pct": np.array([50.0, 66.7]),
        "hits": np.array([1.0, 2.0]),
        "misses": np.array([1.0, 1.0]),
        "successful_snr": np.array([-18.0, -12.0, -9.0]),
    }

    figure = _render_opportunity_selected_figure(recipe)
    try:
        figure.canvas.draw()

        assert figure.subplotpars.left == 0.05
        assert figure.subplotpars.right == 0.98
        assert figure.subplotpars.wspace == 0.24
        assert len(figure.legends) == 1
        illumination_labels = [
            "Target night",
            "Target greyline/mixed",
            "Target daylight",
            f"{terms['counter']} night",
            f"{terms['counter']} greyline/mixed",
            f"{terms['counter']} daylight",
        ]
        _assert_shared_evidence_legend(
            figure,
            figure.legends[0],
            illumination_labels,
        )
        assert figure.legends[0]._ncols == 6

        time_axis = next(
            axis
            for axis in figure.axes
            if axis.get_title().startswith("Station Success Rate + Evidence")
        )
        snr_axis = next(
            axis for axis in figure.axes if axis.get_title() == "Target SNR"
        )
        evidence_axis = next(
            axis
            for axis in figure.axes
            if axis.get_ylabel() == terms["count_axis_label"]
        )
        _assert_shared_evidence_legend(
            figure,
            time_axis.get_legend(),
            ["Success Rate"],
        )
        _assert_shared_axis_label(time_axis.xaxis.label, "Date/Time (UTC)")
        _assert_shared_axis_label(time_axis.yaxis.label, "Success Rate (%)")
        _assert_shared_axis_label(
            evidence_axis.yaxis.label,
            terms["count_axis_label"],
        )
        _assert_shared_axis_label(
            snr_axis.xaxis.label,
            "Target normalized SNR (dB @ 30 dBm)",
        )
        _assert_shared_axis_label(snr_axis.yaxis.label, "Share (%)")
        all_legend_labels = [
            *illumination_labels,
            *[text.get_text() for text in time_axis.get_legend().get_texts()],
        ]
        assert not any(
            summary_term in label
            for label in all_legend_labels
            for summary_term in ("Median", "Mean", "Stability")
        )
    finally:
        dispose_matplotlib_figure(figure)


def test_sequential_segment_recipe_preserves_scheduled_pair_title():
    """Render the scheduled-pair evidence title stored with the recipe."""
    base_recipe = {
        "title": "TX A/B Segment Insight",
        "selected_segment": "Full Range | All Directions",
        "is_compare": True,
        "is_sequential": True,
        "compare_layout": True,
        "station_values": np.array([-1.0, 0.0, 1.0]),
        "spot_values": np.array([-2.0, 0.0, 2.0]),
        "panel_counts": [],
        "panel_station_counts": [1, 3, 1, 1],
        "panel_spot_counts": [2, 6, 2, 1],
        "panel_series_labels": ["Stations", "Scheduled pairs"],
        "panel_labels": ["Target", "Joint", "Both (Async)", "Reference"],
        "panel_y_label": "Share (%)",
    }

    evidence_title = "Scheduled-Pair \u0394 SNR"
    figure = render_segment_insight_export_figure(
        {**base_recipe, "paired_evidence_title": evidence_title}
    )
    try:
        assert evidence_title in {axis.get_title() for axis in figure.axes}
    finally:
        dispose_matplotlib_figure(figure)


def test_preview_renderer_returns_the_displayed_png_bytes(monkeypatch):
    from matplotlib.figure import Figure

    from ui import matplotlib_renderer

    displayed = []
    monkeypatch.setattr(matplotlib_renderer.st, "image", lambda image, **kwargs: displayed.append(image))
    figure = Figure(figsize=(2, 1), facecolor="black")
    figure.add_subplot(111).plot([0, 1], [0, 1])
    try:
        image_bytes = matplotlib_renderer.render_matplotlib_figure(figure, dpi=40)
    finally:
        dispose_matplotlib_figure(figure)

    assert image_bytes.startswith(b"\x89PNG\r\n\x1a\n")
    assert displayed == [image_bytes]
