"""
Neutral Cartopy map scaffolding for WSPRadar map figures.

This module draws only the shared geographic frame: projection, circular map
boundary, land/ocean/coastlines, distance rings, azimuth spokes, compass labels,
and pole markers. Data overlays, legends, colorbars, and footer metrics remain
in plot_engine because their meaning differs between Compare and Absolute modes.
"""

from __future__ import annotations

import numpy as np
import matplotlib.path as mpath
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from config import (
    AZIMUTH_STEP,
    COMPASS,
    COMPASS_LABEL_OFFSET,
    EARTH_RADIUS_M,
    FIG_SIZE,
    FONT_COMPASS,
    FONT_POLES,
    FONT_RINGS,
    MAP_BBOX,
    PLOT_DPI,
    THICK_RINGS,
    THIN_RINGS,
    TITLE_POS,
    ZOOMED_MAP_SCALE,
)


def create_base_map_figure(
    *,
    title: str,
    maximum_distance_km: float,
    center_latitude: float,
    center_longitude: float,
    theme_name: str,
    theme_config: dict,
):
    """Create the shared WSPRadar map frame and return figure, axis, and projections."""
    figure = plt.figure(figsize=FIG_SIZE, facecolor=theme_config["fig_face"], dpi=PLOT_DPI)
    figure.text(
        TITLE_POS[0],
        TITLE_POS[1],
        title,
        fontsize=18,
        fontweight="bold",
        color=theme_config["title"],
        ha="center",
        va="top",
    )

    earth_globe = ccrs.Globe(semimajor_axis=EARTH_RADIUS_M, semiminor_axis=EARTH_RADIUS_M)
    map_projection = ccrs.AzimuthalEquidistant(
        central_longitude=center_longitude,
        central_latitude=center_latitude,
        globe=earth_globe,
    )
    plate_carree_projection = ccrs.PlateCarree(globe=earth_globe)

    axis = figure.add_axes(MAP_BBOX, projection=map_projection)
    axis.set_facecolor(theme_config["ax_face"])
    axis.set_global()

    map_scale = 1.0 if maximum_distance_km == 22000 else ZOOMED_MAP_SCALE
    maximum_radius_m = maximum_distance_km * 1000
    map_limit_m = maximum_radius_m / map_scale
    axis.set_xlim(-map_limit_m, map_limit_m)
    axis.set_ylim(-map_limit_m, map_limit_m)

    theta = np.linspace(0, 2 * np.pi, 100)
    boundary_center = [0.5, 0.5]
    boundary_radius = 0.5 * map_scale
    boundary_vertices = np.vstack([np.sin(theta), np.cos(theta)]).T
    circle = mpath.Path(boundary_vertices * boundary_radius + boundary_center)
    axis.set_boundary(circle, transform=axis.transAxes)
    if theme_name == "light":
        for spine in axis.spines.values():
            spine.set_visible(False)

    axis.add_feature(cfeature.OCEAN, facecolor=theme_config["ocean"])
    axis.add_feature(cfeature.LAND, facecolor=theme_config["land"])
    axis.add_feature(
        cfeature.COASTLINE,
        linewidth=0.9,
        edgecolor=theme_config["coast"],
        zorder=5,
        alpha=0.9,
    )
    # Slows down plotting; keep borders off only if performance becomes an issue again.
    axis.add_feature(
        cfeature.BORDERS,
        linewidth=0.6,
        edgecolor=theme_config["border"],
        zorder=5,
        alpha=0.7,
    )

    for ring_km in THICK_RINGS:
        if ring_km > maximum_distance_km:
            continue
        linewidth = 1.8 if ring_km == maximum_distance_km else 0.9
        axis.add_patch(
            plt.Circle(
                (0, 0),
                ring_km * 1000,
                fill=False,
                color=theme_config["ring"],
                linewidth=linewidth,
                alpha=theme_config["ring_alpha"],
                transform=map_projection,
                zorder=2,
            )
        )
        if ring_km != 5000:
            axis.text(
                0,
                ring_km * 1000,
                f" {ring_km} km ",
                color=theme_config["ring_label"],
                fontsize=FONT_RINGS,
                fontweight="bold",
                ha="center",
                va="center",
                transform=map_projection,
                zorder=6,
                bbox=theme_config["ring_label_box"],
            )

    for ring_km in THIN_RINGS:
        if ring_km <= maximum_distance_km:
            axis.add_patch(
                plt.Circle(
                    (0, 0),
                    ring_km * 1000,
                    fill=False,
                    color=theme_config["ring"],
                    linewidth=0.5,
                    alpha=theme_config["thin_ring_alpha"],
                    linestyle="--",
                    transform=map_projection,
                    zorder=2,
                )
            )

    for azimuth_degrees in np.arange(AZIMUTH_STEP / 2.0, 360, AZIMUTH_STEP):
        axis.plot(
            [0, maximum_radius_m * np.cos(np.radians(90 - azimuth_degrees))],
            [0, maximum_radius_m * np.sin(np.radians(90 - azimuth_degrees))],
            color=theme_config["azimuth"],
            linewidth=0.3,
            alpha=0.4,
            transform=map_projection,
            zorder=2,
        )

    label_radius_m = map_limit_m * COMPASS_LABEL_OFFSET
    for compass_index, direction_label in enumerate(COMPASS):
        angle = compass_index * AZIMUTH_STEP
        label_x = label_radius_m * np.cos(np.radians(90 - angle))
        label_y = label_radius_m * np.sin(np.radians(90 - angle))
        axis.text(
            label_x,
            label_y,
            direction_label,
            color=theme_config["compass"],
            ha="center",
            va="center",
            transform=map_projection,
            fontsize=FONT_COMPASS,
            fontweight="bold",
            alpha=0.9,
            clip_on=False,
        )

    north_pole_distance_m = (90.0 - center_latitude) * (np.pi / 180.0) * EARTH_RADIUS_M
    south_pole_distance_m = (90.0 + center_latitude) * (np.pi / 180.0) * EARTH_RADIUS_M

    if north_pole_distance_m <= maximum_radius_m:
        axis.plot(
            0,
            north_pole_distance_m,
            marker="*",
            color=theme_config["pole"],
            markersize=8,
            mew=1.2,
            transform=map_projection,
            zorder=20,
        )
        axis.text(
            0,
            north_pole_distance_m - 350000,
            "N-POL",
            color=theme_config["pole"],
            fontsize=FONT_POLES,
            fontweight="bold",
            ha="center",
            va="top",
            transform=map_projection,
            zorder=20,
        )

    if south_pole_distance_m <= maximum_radius_m:
        axis.plot(
            0,
            -south_pole_distance_m,
            marker="*",
            color=theme_config["pole"],
            markersize=8,
            mew=1.2,
            transform=map_projection,
            zorder=20,
        )
        axis.text(
            0,
            -south_pole_distance_m - 350000,
            "S-POL",
            color=theme_config["pole"],
            fontsize=FONT_POLES,
            fontweight="bold",
            ha="center",
            va="top",
            transform=map_projection,
            zorder=20,
        )

    return figure, axis, map_projection, plate_carree_projection
