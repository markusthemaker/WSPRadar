"""Shared presentation geometry for chronological and folded UTC figures."""

from __future__ import annotations

import textwrap

import matplotlib as mpl


TEMPORAL_EVIDENCE_LAYOUT_VERSION = 1
TEMPORAL_COLUMN_WIDTH_RATIOS = (1.95, 1.0)
TEMPORAL_COLUMN_SPACE = 0.20
TEMPORAL_EVIDENCE_ROW_SPACE = 0.24
TEMPORAL_COLORBAR_PAD = 0.012
TEMPORAL_COLORBAR_FRACTION = 0.03
TEMPORAL_FOLDED_COLUMN_X_SHIFT = 0.025
TEMPORAL_REFERENCE_FIGURE_WIDTH_PX = 1300.0
TEMPORAL_FOLDED_COLUMN_LEFT_EXPANSION_PX = 28.0
FOLDED_UTC_UNAVAILABLE_WRAP_WIDTH = 34
FOLDED_UTC_UNAVAILABLE_DETAIL_WRAP_WIDTH = 30


def build_temporal_plot_grid(
    figure,
    *,
    row_count,
    row_space,
    column_space=TEMPORAL_COLUMN_SPACE,
):
    """Create the invariant chronological/folded two-column plot grid."""
    return figure.add_gridspec(
        nrows=int(row_count),
        ncols=2,
        hspace=float(row_space),
        width_ratios=TEMPORAL_COLUMN_WIDTH_RATIOS,
        wspace=float(column_space),
    )


def align_folded_evidence_axes_to_colorbar(
    figure,
    *,
    all_axes,
    folded_axes,
):
    """Align lower folded evidence axes with a companion density colorbar.

    The operation atomically reserves the companion figure's colorbar
    footprint, translates the complete folded column into that footprint, and
    widens it 28 pixels toward the left on the 1,300-pixel reference canvas.
    Chronological axes retain their colorbar-reserved bounds, while every
    folded axis keeps the translated right edge.
    """
    resolved_axes = tuple(axis for axis in all_axes if axis is not None)
    resolved_folded_axes = tuple(
        axis for axis in folded_axes if axis is not None
    )
    if not resolved_axes:
        raise ValueError("Temporal layout requires at least one plot axis.")
    if not resolved_folded_axes:
        raise ValueError("Temporal layout requires at least one folded axis.")

    layout_mappable = mpl.cm.ScalarMappable(
        norm=mpl.colors.Normalize(vmin=0.0, vmax=1.0),
        cmap=mpl.colormaps["viridis"],
    )
    reserved_colorbar = figure.colorbar(
        layout_mappable,
        ax=list(resolved_axes),
        pad=TEMPORAL_COLORBAR_PAD,
        fraction=TEMPORAL_COLORBAR_FRACTION,
    )
    reserved_colorbar.ax.remove()

    left_expansion = (
        TEMPORAL_FOLDED_COLUMN_LEFT_EXPANSION_PX
        / TEMPORAL_REFERENCE_FIGURE_WIDTH_PX
    )
    for axis in resolved_folded_axes:
        position = axis.get_position()
        axis.set_position(
            [
                position.x0
                + TEMPORAL_FOLDED_COLUMN_X_SHIFT
                - left_expansion,
                position.y0,
                position.width + left_expansion,
                position.height,
            ],
            which="both",
        )


def draw_temporal_unavailable_annotation(
    axis,
    message,
    *,
    artist_gid="temporal-unavailable-annotation",
):
    """Draw one shared boxed notice inside an unavailable temporal panel."""
    normalized_message = " ".join(str(message).split())
    headline = None
    detail = None
    for separator in (" - ", " \N{EM DASH} ", " \N{EN DASH} "):
        if separator in normalized_message:
            headline, detail = normalized_message.split(separator, maxsplit=1)
            break
    if headline is not None and detail is not None:
        detail = detail[:1].upper() + detail[1:]
        wrapped_lines = [headline]
        wrapped_lines.extend(
            textwrap.wrap(
                detail,
                width=FOLDED_UTC_UNAVAILABLE_DETAIL_WRAP_WIDTH,
                break_long_words=False,
                break_on_hyphens=False,
            )
        )
    else:
        wrapped_lines = textwrap.wrap(
            normalized_message,
            width=FOLDED_UTC_UNAVAILABLE_WRAP_WIDTH,
            break_long_words=False,
            break_on_hyphens=False,
        )
    annotation = axis.text(
        0.5,
        0.5,
        "\n".join(wrapped_lines),
        transform=axis.transAxes,
        color="white",
        ha="center",
        va="center",
        fontsize=9,
        fontfamily="sans-serif",
        fontweight="normal",
        linespacing=1.3,
        bbox={
            "boxstyle": "round,pad=0.55",
            "facecolor": "black",
            "edgecolor": "#555555",
            "linewidth": 0.8,
            "alpha": 1.0,
        },
        zorder=10,
    )
    annotation.set_gid(str(artist_gid))
    return annotation


def draw_folded_utc_unavailable_annotation(axis, message):
    """Draw the shared boxed notice inside an unavailable folded UTC panel."""
    return draw_temporal_unavailable_annotation(
        axis,
        message,
        artist_gid="folded-utc-unavailable-annotation",
    )
