"""Collection-based rectangular bars for temporal evidence figures."""

from __future__ import annotations

import numpy as np
from matplotlib.collections import PolyCollection


def draw_temporal_bar_collection(
    axis,
    x_values,
    heights,
    *,
    widths,
    bottoms=0.0,
    color,
    label,
    gid,
):
    """Draw one outcome layer with the geometry and styling of centered bars.

    Temporal recipes supply numerical date coordinates or UTC-hour centers.
    Retain one polygon per bin, including zero-height bins, while avoiding
    individual Rectangle artists and their per-artist setup and limit updates.
    """
    x, height, width, bottom = np.broadcast_arrays(
        np.asarray(x_values, dtype=float),
        np.asarray(heights, dtype=float),
        np.asarray(widths, dtype=float),
        np.asarray(bottoms, dtype=float),
    )
    if x.size:
        # Axes.bar converts even unitless widths and heights through a
        # difference from the first finite coordinate. Keep that arithmetic
        # so fractional stacked layers and date-coordinate widths retain the
        # exact legacy Rectangle geometry rather than shifting by one ULP.
        finite_x = x[np.isfinite(x)]
        finite_bottom = bottom[np.isfinite(bottom)]
        x_origin = finite_x[0] if finite_x.size else x[0]
        bottom_origin = finite_bottom[0] if finite_bottom.size else bottom[0]
        width = (x_origin + width) - x_origin
        height = (bottom_origin + height) - bottom_origin
    left = x - width / 2.0
    right = left + width
    top = bottom + height
    # Rectangle transforms its unit path using the span of its bounding box.
    # Preserve that final subtract/add step as well as the stored endpoints.
    right = left + (right - left)
    top = bottom + (top - bottom)
    vertices = np.empty((len(x), 4, 2), dtype=float)
    vertices[:, 0, 0] = left
    vertices[:, 0, 1] = bottom
    vertices[:, 1, 0] = right
    vertices[:, 1, 1] = bottom
    vertices[:, 2, 0] = right
    vertices[:, 2, 1] = top
    vertices[:, 3, 0] = left
    vertices[:, 3, 1] = top
    # A Rectangle with a non-finite coordinate has no finite transformed
    # polygon. Do not let the remaining baseline of such a bin expand limits.
    invalid = ~(
        np.isfinite(left)
        & np.isfinite(right)
        & np.isfinite(bottom)
        & np.isfinite(top)
    )
    vertices[invalid | ((width == 0.0) & (height == 0.0))] = np.nan
    collection = PolyCollection(
        vertices,
        closed=True,
        facecolors=color,
        edgecolors="#111111",
        linewidths=0.35,
        capstyle="butt",
        joinstyle="miter",
        label=label,
        gid=gid,
        zorder=2,
    )
    # Axes.bar marks each bar's baseline as sticky. Preserve that complete
    # set for stacked layers so automatic margins cannot extend through it.
    collection.sticky_edges.y[:] = np.unique(bottom).tolist()
    axis.add_collection(collection)
    # Older supported Matplotlib releases update collection data limits but
    # need this explicit call to update the displayed limits as Axes.bar does.
    axis.autoscale_view()
    return collection
