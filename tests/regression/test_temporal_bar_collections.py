"""Geometry and raster parity for collection-based temporal outcome bars."""

from __future__ import annotations

import numpy as np
import pytest
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.collections import PolyCollection
from matplotlib.figure import Figure

from ui.plots.temporal_bars import draw_temporal_bar_collection


def _make_axis(dpi=100):
    """Construct a small isolated Agg figure without pyplot global state."""
    figure = Figure(figsize=(6, 3), dpi=dpi)
    FigureCanvasAgg(figure)
    return figure, figure.subplots()


def _draw_legacy_bars(axis, x, heights, widths, bottoms, color, label):
    """Retain the pre-collection renderer as a geometry and raster oracle."""
    return axis.bar(
        x,
        heights,
        width=widths,
        bottom=bottoms,
        color=color,
        edgecolor="#111111",
        linewidth=0.35,
        label=label,
        zorder=2,
    )


@pytest.mark.parametrize("date_coordinates", [False, True])
def test_temporal_collection_preserves_each_rectangle_geometry(date_coordinates):
    """Retain bin edges, fractional layers, partial widths and zero bins."""
    x = np.array([0.5, 1.5, 2.25, 3.5])
    widths = np.array([0.78, 0.78, 0.39, 0.78])
    if date_coordinates:
        x = 20644.0 + x / 24.0
        widths = widths / 24.0
    first = np.array([0.0, 1.0, 0.25, 4.0])
    second = np.array([0.0, 2.0, 0.75, 0.0])
    legacy_figure, legacy_axis = _make_axis()
    figure, axis = _make_axis()
    try:
        for heights, bottoms, color, label in (
            (first, np.zeros(4), "#39ff14", "Target"),
            (second, first, "#858585", "Counter"),
        ):
            old = _draw_legacy_bars(
                legacy_axis, x, heights, widths, bottoms, color, label,
            )
            collection = draw_temporal_bar_collection(
                axis,
                x,
                heights,
                widths=widths,
                bottoms=bottoms,
                color=color,
                label=label,
                gid=f"outcome-{label}",
            )
            assert isinstance(collection, PolyCollection)
            assert collection.get_gid() == f"outcome-{label}"
            assert collection.get_label() == label
            assert len(collection.get_paths()) == len(old)
            for path, rectangle in zip(collection.get_paths(), old):
                np.testing.assert_array_equal(
                    path.vertices,
                    rectangle.get_path().transformed(
                        rectangle.get_patch_transform(),
                    ).vertices,
                )
            assert collection.get_joinstyle() == old[0].get_joinstyle()
            assert collection.get_capstyle() == old[0].get_capstyle()
            np.testing.assert_array_equal(
                collection.get_linewidths(), [old[0].get_linewidth()],
            )
            np.testing.assert_array_equal(
                collection.get_facecolors(), [old[0].get_facecolor()],
            )
            np.testing.assert_array_equal(
                collection.get_edgecolors(), [old[0].get_edgecolor()],
            )
            assert set(collection.sticky_edges.y) == set(bottoms)
        assert not axis.patches
        assert not axis.containers
        assert len(axis.collections) == 2
        np.testing.assert_array_equal(axis.dataLim.bounds, legacy_axis.dataLim.bounds)
        np.testing.assert_array_equal(axis.get_xlim(), legacy_axis.get_xlim())
        np.testing.assert_array_equal(axis.get_ylim(), legacy_axis.get_ylim())
    finally:
        legacy_figure.clear()
        figure.clear()


@pytest.mark.parametrize("dpi", [100, 220])
@pytest.mark.parametrize(
    "layers",
    [
        ([0.0, 1.0, 0.25, 4.0], [0.0, 2.0, 0.75, 0.0]),
        ([0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]),
        ([np.nan, 1.0, 0.25, 4.0], [0.0, 2.0, 0.75, 0.0]),
        ([], []),
    ],
)
def test_temporal_collection_matches_preview_and_export_raster(dpi, layers):
    """Preserve automatic limits and exact pixels in the full temporal window."""
    images = []
    limits = []
    for use_collection in (False, True):
        figure, axis = _make_axis(dpi)
        try:
            first, second = (np.asarray(values, dtype=float) for values in layers)
            x = np.array([0.5, 1.5, 2.25, 3.5])[:len(first)]
            widths = np.array([0.78, 0.78, 0.39, 0.78])[:len(first)]
            for heights, bottoms, color, label in (
                (first, np.zeros(len(first)), "#39ff14", "Target"),
                (second, first, "#858585", "Counter"),
            ):
                if use_collection:
                    draw_temporal_bar_collection(
                        axis, x, heights, widths=widths, bottoms=bottoms,
                        color=color, label=label, gid=f"outcome-{label}",
                    )
                else:
                    _draw_legacy_bars(
                        axis, x, heights, widths, bottoms, color, label,
                    )
            axis.set_ylim(bottom=0.0)
            limits.append((axis.get_xlim(), axis.get_ylim()))
            # Production temporal figures retain their complete requested
            # time window, including bins with missing or zero evidence.
            axis.set_xlim(0.0, 4.0)
            if len(first):
                axis.legend(loc="upper right")
            figure.canvas.draw()
            images.append(np.asarray(figure.canvas.buffer_rgba()).copy())
        finally:
            figure.clear()
    np.testing.assert_array_equal(limits[0], limits[1])
    np.testing.assert_array_equal(images[0], images[1])


@pytest.mark.parametrize("x_origin", [0.5, 2.5, 20644.020833333333, -180.0])
def test_temporal_collection_retains_unit_difference_and_bbox_arithmetic(x_origin):
    """Match float geometry after Matplotlib's unit and bbox conversions."""
    x = x_origin + np.array([0.0, 1.0, 2.0])
    widths = np.array([0.78, 0.039, 1.0 / 30.0])
    heights = np.array([1.0 / 3.0, 7.0 / 15.0, 37.0 / 60.0])
    bottoms = np.array([1.0 / 29.0, 1.0 / 31.0, 1.0 / 23.0])
    old_figure, old_axis = _make_axis()
    figure, axis = _make_axis()
    try:
        bars = _draw_legacy_bars(
            old_axis, x, heights, widths, bottoms, "#39ff14", "Target",
        )
        collection = draw_temporal_bar_collection(
            axis, x, heights, widths=widths, bottoms=bottoms,
            color="#39ff14", label="Target", gid="fractional-outcome",
        )
        for path, rectangle in zip(collection.get_paths(), bars):
            np.testing.assert_array_equal(
                path.vertices,
                rectangle.get_path().transformed(
                    rectangle.get_patch_transform(),
                ).vertices,
            )
        np.testing.assert_array_equal(axis.dataLim.bounds, old_axis.dataLim.bounds)
    finally:
        old_figure.clear()
        figure.clear()
