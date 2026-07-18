from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
import threading
import time

import numpy as np
from matplotlib.colors import to_rgba
from PIL import Image
import pytest

from core import map_base, plot_engine
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
        "station_interval": (0.0, -0.5, 0.5),
        "spot_interval": (0.0, -1.0, 1.0),
        "panel_counts": [1, 3, 1, 1],
        "panel_labels": ["Target", "Joint", "Both (Async)", "Reference"],
        "panel_y_label": "Count (Stations)",
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
        "station_interval": (0.0, -0.5, 0.5),
        "spot_interval": (0.0, -1.0, 1.0),
        "panel_counts": [1, 3, 1, 1],
        "panel_labels": ["Target", "Joint", "Both (Async)", "Reference"],
        "panel_y_label": "Count (Stations)",
    }
    figure = render_segment_insight_export_figure(recipe)
    try:
        image_bytes = figure_to_png_bytes(figure, dpi=80, paper_theme=True)
    finally:
        dispose_matplotlib_figure(figure)

    assert image_bytes.startswith(b"\x89PNG\r\n\x1a\n")


def test_compare_segment_histograms_share_summary_legend_and_mean_placement():
    """Standardize Compare summaries without mixing Mean into median Stability."""
    recipe = {
        "title": "RX Compare",
        "selected_segment": "Full Range | All Directions",
        "is_compare": True,
        "is_sequential": False,
        "compare_layout": True,
        "station_values": np.array([6.0, 7.0]),
        "spot_values": np.array([6.0, 8.0]),
        "station_interval": (6.5, 6.0, 7.0),
        "spot_interval": (7.0, 6.0, 8.0),
        "panel_counts": [1, 2, 0, 1],
        "panel_labels": ["Target", "Joint", "Both (Async)", "Reference"],
        "panel_y_label": "Count (Stations)",
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

        assert station_labels == ["Median +6.5 dB", "90% Stability"]
        assert spot_labels == ["Median +7.0 dB", "90% Stability"]
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
        "station_interval": (-10.0, -12.0, -8.0),
        "spot_interval": (-12.0, -15.0, -9.0),
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
            assert legend_labels[0] == "90% Stability"
            assert legend_labels[1].startswith("Median ")
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
            "Target normalized SNR (dB @ 1 W)",
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
        "station_interval": (0.0, -0.5, 0.5),
        "spot_interval": (0.0, -1.0, 1.0),
        "panel_counts": [1, 3, 1, 1],
        "panel_labels": ["Target", "Joint", "Both (Async)", "Reference"],
        "panel_y_label": "Count (Stations)",
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
