"""
Neutral Cartopy map scaffolding for WSPRadar map figures.

This module draws only the shared geographic frame: projection, circular map
boundary, land/ocean/coastlines, distance rings, azimuth spokes, compass labels,
and pole markers. Data overlays, legends, colorbars, and footer metrics remain
in plot_engine because their meaning differs between Compare and Absolute modes.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

import numpy as np
import matplotlib.path as mpath
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from config import (
    AZIMUTH_STEP,
    CACHE_DIR,
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

BASEMAP_CACHE_VERSION = "v1"
BASEMAP_PREVIEW_DPI = 100
BASEMAP_PNG_COMPRESSION_LEVEL = 1


def create_base_map_figure(
    *,
    title: str,
    maximum_distance_km: float,
    center_latitude: float,
    center_longitude: float,
    theme_name: str,
    theme_config: dict,
    include_title: bool = True,
):
    """Create the shared WSPRadar map frame and return figure, axis, and projections."""
    figure = plt.figure(figsize=FIG_SIZE, facecolor=theme_config["fig_face"], dpi=PLOT_DPI)
    if include_title:
        _add_map_title(figure, title, theme_config)

    earth_globe, map_projection, plate_carree_projection = _map_projections(center_latitude, center_longitude)

    axis = figure.add_axes(MAP_BBOX, projection=map_projection)
    axis.set_facecolor(theme_config["ax_face"])
    axis.set_global()

    map_scale, maximum_radius_m, map_limit_m = _map_scale_and_limits(maximum_distance_km)
    axis.set_xlim(-map_limit_m, map_limit_m)
    axis.set_ylim(-map_limit_m, map_limit_m)

    axis.set_boundary(_map_boundary_path(map_scale), transform=axis.transAxes)
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


def create_preview_cached_base_map_figure(
    *,
    title: str,
    maximum_distance_km: float,
    center_latitude: float,
    center_longitude: float,
    theme_name: str,
    theme_config: dict,
    cache_label: str = "",
    cache_center_latitude: float | None = None,
    cache_center_longitude: float | None = None,
    preview_dpi: int = BASEMAP_PREVIEW_DPI,
):
    """Create a map figure using a cached static basemap raster for live preview."""
    static_center_latitude = center_latitude if cache_center_latitude is None else cache_center_latitude
    static_center_longitude = center_longitude if cache_center_longitude is None else cache_center_longitude
    cache_path, cache_status = _ensure_static_basemap_cache(
        maximum_distance_km=maximum_distance_km,
        center_latitude=static_center_latitude,
        center_longitude=static_center_longitude,
        theme_name=theme_name,
        theme_config=theme_config,
        cache_label=cache_label,
        preview_dpi=preview_dpi,
    )

    figure = plt.figure(figsize=FIG_SIZE, facecolor=theme_config["fig_face"], dpi=PLOT_DPI)
    background_axis = figure.add_axes([0.0, 0.0, 1.0, 1.0], zorder=-100)
    background_axis.imshow(plt.imread(cache_path), aspect="auto")
    background_axis.set_axis_off()
    _add_map_title(figure, title, theme_config)

    earth_globe, map_projection, plate_carree_projection = _map_projections(center_latitude, center_longitude)
    axis = figure.add_axes(MAP_BBOX, projection=map_projection)
    axis.patch.set_alpha(0.0)
    axis.set_global()

    map_scale, _, map_limit_m = _map_scale_and_limits(maximum_distance_km)
    axis.set_xlim(-map_limit_m, map_limit_m)
    axis.set_ylim(-map_limit_m, map_limit_m)
    axis.set_boundary(_map_boundary_path(map_scale), transform=axis.transAxes)
    axis.set_xticks([])
    axis.set_yticks([])
    for spine in axis.spines.values():
        spine.set_visible(False)

    cache_detail = f"{cache_status}: {cache_path.name}"
    return figure, axis, map_projection, plate_carree_projection, cache_detail


def _add_map_title(figure, title, theme_config):
    """Add the dynamic analysis title to a WSPRadar map figure."""
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


def _map_projections(center_latitude, center_longitude):
    """Return the WSPRadar map and geographic source projections."""
    earth_globe = ccrs.Globe(semimajor_axis=EARTH_RADIUS_M, semiminor_axis=EARTH_RADIUS_M)
    map_projection = ccrs.AzimuthalEquidistant(
        central_longitude=center_longitude,
        central_latitude=center_latitude,
        globe=earth_globe,
    )
    plate_carree_projection = ccrs.PlateCarree(globe=earth_globe)
    return earth_globe, map_projection, plate_carree_projection


def _map_scale_and_limits(maximum_distance_km):
    """Return map scale, requested radius, and visible projected limit in meters."""
    map_scale = 1.0 if maximum_distance_km == 22000 else ZOOMED_MAP_SCALE
    maximum_radius_m = maximum_distance_km * 1000
    map_limit_m = maximum_radius_m / map_scale
    return map_scale, maximum_radius_m, map_limit_m


def _map_boundary_path(map_scale):
    """Return the circular map boundary path in axes coordinates."""
    theta = np.linspace(0, 2 * np.pi, 100)
    boundary_center = [0.5, 0.5]
    boundary_radius = 0.5 * map_scale
    boundary_vertices = np.vstack([np.sin(theta), np.cos(theta)]).T
    return mpath.Path(boundary_vertices * boundary_radius + boundary_center)


def _ensure_static_basemap_cache(
    *,
    maximum_distance_km,
    center_latitude,
    center_longitude,
    theme_name,
    theme_config,
    cache_label,
    preview_dpi,
):
    """Return a static basemap PNG path, rendering it once when absent."""
    cache_dir = Path(CACHE_DIR) / "basemaps"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / _static_basemap_cache_filename(
        maximum_distance_km=maximum_distance_km,
        center_latitude=center_latitude,
        center_longitude=center_longitude,
        theme_name=theme_name,
        theme_config=theme_config,
        cache_label=cache_label,
        preview_dpi=preview_dpi,
    )
    if cache_path.exists():
        return cache_path, "hit"

    base_figure, _, _, _ = create_base_map_figure(
        title="",
        maximum_distance_km=maximum_distance_km,
        center_latitude=center_latitude,
        center_longitude=center_longitude,
        theme_name=theme_name,
        theme_config=theme_config,
        include_title=False,
    )
    try:
        _save_static_basemap_preview(base_figure, cache_path, preview_dpi)
    finally:
        plt.close(base_figure)
    return cache_path, "miss"


def _static_basemap_cache_filename(
    *,
    maximum_distance_km,
    center_latitude,
    center_longitude,
    theme_name,
    theme_config,
    cache_label,
    preview_dpi,
):
    """Return a human-readable, style-versioned static basemap cache filename."""
    pixel_width = int(round(FIG_SIZE[0] * preview_dpi))
    pixel_height = int(round(FIG_SIZE[1] * preview_dpi))
    style_payload = {
        "version": BASEMAP_CACHE_VERSION,
        "theme": theme_name,
        "theme_config": theme_config,
        "center_latitude": round(float(center_latitude), 5),
        "center_longitude": round(float(center_longitude), 5),
        "maximum_distance_km": float(maximum_distance_km),
        "fig_size": FIG_SIZE,
        "map_bbox": MAP_BBOX,
        "preview_dpi": preview_dpi,
        "azimuth_step": AZIMUTH_STEP,
        "compass": COMPASS,
        "rings": {"thick": THICK_RINGS, "thin": THIN_RINGS},
        "zoomed_map_scale": ZOOMED_MAP_SCALE,
    }
    digest = hashlib.sha256(json.dumps(style_payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:12]
    label_token = _cache_token(cache_label) if cache_label else _lat_lon_token(center_latitude, center_longitude)
    radius_token = f"{int(round(float(maximum_distance_km)))}km"
    return (
        f"basemap_{BASEMAP_CACHE_VERSION}_{theme_name}_{label_token}_{radius_token}_"
        f"{pixel_width}x{pixel_height}_{digest}.png"
    )


def _cache_token(value):
    """Return a filesystem-safe compact token."""
    token = re.sub(r"[^A-Za-z0-9_-]+", "-", str(value).strip())
    token = token.strip("-_")
    return token or "map"


def _lat_lon_token(latitude, longitude):
    """Return a compact latitude/longitude cache token."""
    lat_token = f"{float(latitude):+07.3f}".replace("+", "N").replace("-", "S").replace(".", "p")
    lon_token = f"{float(longitude):+08.3f}".replace("+", "E").replace("-", "W").replace(".", "p")
    return f"{lat_token}_{lon_token}"


def _save_static_basemap_preview(figure, cache_path, preview_dpi):
    """Render and save a static basemap preview PNG."""
    from PIL import Image

    if not hasattr(figure.canvas, "buffer_rgba"):
        FigureCanvasAgg(figure)

    original_dpi = figure.dpi
    try:
        figure.set_dpi(preview_dpi)
        figure.canvas.draw()
        width, height = figure.canvas.get_width_height()
        image = Image.frombuffer("RGBA", (width, height), figure.canvas.buffer_rgba(), "raw", "RGBA", 0, 1).copy()
    finally:
        figure.set_dpi(original_dpi)

    temp_path = cache_path.with_suffix(f".{BASEMAP_CACHE_VERSION}.tmp")
    image.save(
        temp_path,
        format="PNG",
        compress_level=BASEMAP_PNG_COMPRESSION_LEVEL,
        optimize=False,
    )
    temp_path.replace(cache_path)
