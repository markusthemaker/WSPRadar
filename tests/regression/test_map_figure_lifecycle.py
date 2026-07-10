from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
import threading
import time

import numpy as np
from PIL import Image

from core import map_base
from i18n import T, absolute_terms
from ui.matplotlib_renderer import (
    _draw_figure_preview_image,
    _serialize_preview_png,
    dispose_matplotlib_figure,
)
from ui.plots.evidence_figures import render_segment_insight_export_figure
from ui.plots.opportunity_figures import _render_opportunity_segment_figure
from ui.results_export import figure_to_png_bytes


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
