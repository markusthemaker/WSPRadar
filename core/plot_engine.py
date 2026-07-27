"""
Plot Engine.
Fuehrt die geografische Aggregation durch und zeichnet die Cartopy-Map.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use the non-interactive backend required by Streamlit Cloud.
import matplotlib as mpl
from contextlib import nullcontext
from dataclasses import dataclass, replace
from matplotlib.patches import Patch, Wedge
from matplotlib.collections import PatchCollection
from matplotlib.lines import Line2D
import os
from time import perf_counter

from config import (
    APP_VERSION,
    AZIMUTH_STEP,
    CBAR_BBOX,
    COLOR_BOTH_ASYNC,
    COLOR_JOINT,
    COLOR_ONLY_ME,
    COLOR_ONLY_REF,
    COMPARE_MAP_ADAPTIVE_MAXIMUM_TICK_COUNT,
    COMPARE_MAP_CBAR_BBOX,
    COMPARE_MAP_COLORBAR_DIVIDER_ALPHA,
    COMPARE_MAP_COLORBAR_DIVIDER_LINEWIDTH,
    COMPARE_MAP_COLORS,
    COMPARE_MAP_HEATMAP_ALPHA,
    COMPARE_MAP_MINIMUM_HALF_SPAN_DB,
    COMPARE_MAP_TICK_STEPS_DB,
    FONT_CBAR,
    FONT_FOOTER,
    FONT_LEGEND,
    LEG_BBOX,
)
from config.plot_constants import (
    SUCCESS_MAP_COUNTER_ALPHA,
    SUCCESS_MAP_COUNTER_COLOR,
    SUCCESS_MAP_FOOTER_BBOX,
    SUCCESS_MAP_HEATMAP_ALPHA,
    SUCCESS_MAP_MARKER_EDGE_COLOR,
    SUCCESS_MAP_MARKER_EDGE_LINEWIDTH_POINTS,
    SUCCESS_MAP_LEGEND_BBOX,
    SUCCESS_MAP_MARKER_SIZE_POINTS_SQUARED,
    SUCCESS_MAP_TARGET_COLOR,
)
from core.analysis_context import (
    COMPARISON_HARDWARE_AB,
    COMPARISON_LOCAL_NEIGHBORHOOD,
    LOCAL_BENCHMARK_MEDIAN,
)
from core.opportunity_engine import (
    SUCCESS_RATE_BOUNDS,
    SUCCESS_RATE_COLORS,
    SUCCESS_RATE_TICK_LABELS,
    opportunity_footer_counts,
)
from core.compare_engine import compare_footer_counts
from core.map_data import build_map_data, validate_map_analysis_mode
from core.map_base import create_base_map_figure, create_preview_cached_base_map_figure
from core.map_models import MapFigure
from core.matplotlib_runtime import ensure_agg_canvas, synchronized_matplotlib
from core.input_validation import normalize_ascii_upper
from core.math_utils import locator_to_latlon

BASEMAP_DRAW_PROFILE_ENV = "WSPRADAR_PROFILE_BASEMAP_DRAW"
BASEMAP_CACHE_ENV = "WSPRADAR_PREVIEW_BASEMAP_CACHE"
MAP_PROFILE_PREVIEW_DPI = 100

MAP_THEMES = {
    "dark": {
        "fig_face": "black",
        "title": "white",
        "ax_face": "black",
        "ocean": "#0d0d0d",
        "land": "#202020",
        "coast": "#999999",
        "border": "#666666",
        "ring": "white",
        "ring_alpha": 0.8,
        "thin_ring_alpha": 0.3,
        "azimuth": "#ffffff",
        "compass": "#cccccc",
        "ring_label": "#00ff00",
        "ring_label_box": dict(facecolor="black", alpha=1.0, lw=0, pad=0.5),
        "pole": "#00ff00",
        "legend_face": "#121212",
        "legend_edge": "#444444",
        "legend_text": "white",
        "no_hm_face": "black",
        "no_hm_edge": "#777777",
        "cbar_face": "#0d0d0d",
        "cbar_text": "white",
        "bar_face": "black",
        "bar_tick": "#cccccc",
        "bar_bbox": [0.12, 0.047, 0.85, 0.045],
        "only_ref": COLOR_ONLY_REF,
        "only_ref_edge": "black",
        "footer": "#888888",
        "footer_abs": "#cccccc",
    },
    "light": {
        "fig_face": "white",
        "title": "#111111",
        "ax_face": "white",
        "ocean": "#f7f7f7",
        "land": "#efefef",
        "coast": "#8a8a8a",
        "border": "#b0b0b0",
        "ring": "#888888",
        "ring_alpha": 0.85,
        "thin_ring_alpha": 0.35,
        "azimuth": "#c8c8c8",
        "compass": "#222222",
        "ring_label": "#111111",
        "ring_label_box": None,
        "pole": "#00b000",
        "legend_face": "white",
        "legend_edge": "#cccccc",
        "legend_text": "#111111",
        "no_hm_face": "white",
        "no_hm_edge": "#777777",
        "cbar_face": "white",
        "cbar_text": "#111111",
        "bar_face": "white",
        "bar_tick": "#222222",
        "bar_bbox": [0.12, 0.047, 0.85, 0.045],
        "only_ref": "#d0d0d0",
        "only_ref_edge": "#555555",
        "footer": "#222222",
        "footer_abs": "#222222",
    },
}


@dataclass(frozen=True)
class _CompareMapColorScale:
    """Describe one stepped, symmetric Compare-map display scale in dB."""

    colormap: mpl.colors.ListedColormap
    normalization: mpl.colors.BoundaryNorm
    boundaries_db: tuple[float, ...]
    ticks_db: tuple[float, ...]
    tick_labels: tuple[str, ...]


def _format_compare_map_tick(value_db):
    """Format one signed whole-dB Compare-map colorbar tick."""
    rounded_value = int(round(float(value_db)))
    if rounded_value > 0:
        return f"+{rounded_value}"
    if rounded_value < 0:
        return f"\u2212{abs(rounded_value)}"
    return "0"


def _compare_map_positive_tick_count(maximum_absolute_db, tick_step_db):
    """
    Return the fewest positive ticks that contain the visible Compare values.

    The nominal ticks never narrow below +/-6 dB. Containment includes the
    natural half-step beyond the outer tick, so exact boundary values do not
    force an otherwise empty color tier.
    """
    minimum_scale_tick_count = int(
        np.ceil(COMPARE_MAP_MINIMUM_HALF_SPAN_DB / tick_step_db)
    )
    data_tick_count = max(
        0,
        int(np.ceil((maximum_absolute_db / tick_step_db) - 0.5)),
    )
    positive_tick_count = max(
        1,
        minimum_scale_tick_count,
        data_tick_count,
    )
    outer_boundary_db = (positive_tick_count + 0.5) * tick_step_db
    if outer_boundary_db < maximum_absolute_db:
        positive_tick_count += 1
    return positive_tick_count


def _compare_map_tick_layout(maximum_absolute_db):
    """Return the finest readable tick layout containing every finite value."""
    maximum_absolute_db = max(0.0, float(maximum_absolute_db))
    for tick_step_db in COMPARE_MAP_TICK_STEPS_DB:
        positive_tick_count = _compare_map_positive_tick_count(
            maximum_absolute_db,
            tick_step_db,
        )
        if (
            (2 * positive_tick_count) + 1
            <= COMPARE_MAP_ADAPTIVE_MAXIMUM_TICK_COUNT
        ):
            return (
                float(positive_tick_count * tick_step_db),
                float(tick_step_db),
            )

    tick_step_db = COMPARE_MAP_TICK_STEPS_DB[-1]
    while True:
        positive_tick_count = _compare_map_positive_tick_count(
            maximum_absolute_db,
            tick_step_db,
        )
        if (
            (2 * positive_tick_count) + 1
            <= COMPARE_MAP_ADAPTIVE_MAXIMUM_TICK_COUNT
        ):
            return (
                float(positive_tick_count * tick_step_db),
                float(tick_step_db),
            )
        tick_step_db *= 2.0


def _compare_map_bin_boundaries(half_span_db, tick_step_db):
    """
    Return exact equal-width display-bin boundaries centered on neutral.

    Every interval has the active tick-step width, including the neutral color
    centered on 0 dB. Boundaries sit halfway between nominal tick values, and
    the outer boundaries extend half a step beyond the last ticks.
    """
    if tick_step_db < 1.0:
        raise ValueError("Compare-map tick spacing must be at least 1 dB.")

    positive_tick_count = int(round(half_span_db / tick_step_db))
    positive_boundaries_db = tuple(
        float((boundary_index + 0.5) * tick_step_db)
        for boundary_index in range(positive_tick_count + 1)
    )
    return (
        *tuple(
            -boundary_db
            for boundary_db in reversed(positive_boundaries_db)
        ),
        *positive_boundaries_db,
    )


def _build_compare_map_color_scale(segment_values):
    """
    Build the presentation-only Compare scale from rendered sector medians.

    The outer half-bin contains every finite sector value without fixed
    headroom. Nominal ticks remain symmetric around equality and never narrow
    below -6 to +6 dB. Discrete soft-matte colors run from plum, periwinkle,
    blue, turquoise and mint through a light yellow-green neutral band to
    yellow, apricot, coral, brick red and chestnut. Negative Delta SNR favors
    Reference and positive Delta SNR favors Target.
    """
    numeric_values = np.asarray(segment_values, dtype=float).reshape(-1)
    finite_values = numeric_values[np.isfinite(numeric_values)]
    maximum_absolute_db = (
        float(np.max(np.abs(finite_values)))
        if finite_values.size
        else 0.0
    )
    half_span_db, tick_step_db = _compare_map_tick_layout(
        maximum_absolute_db
    )
    positive_tick_count = int(round(half_span_db / tick_step_db))
    ticks_db = tuple(
        float(tick_index * tick_step_db)
        for tick_index in range(-positive_tick_count, positive_tick_count + 1)
    )
    boundaries_db = _compare_map_bin_boundaries(
        half_span_db,
        tick_step_db,
    )
    # BoundaryNorm assigns exact internal boundaries to the higher-index bin.
    # Shift only positive internal cut points one ULP outward so exact +x and
    # -x values receive mirrored colors and both signed half-step cuts remain
    # in the central display-neutral bin.
    outer_boundary_db = boundaries_db[-1]
    normalization_boundaries_db = tuple(
        (
            float(np.nextafter(boundary_db, np.inf))
            if 0.0 < boundary_db < outer_boundary_db
            else boundary_db
        )
        for boundary_db in boundaries_db
    )
    source_colormap = mpl.colors.LinearSegmentedColormap.from_list(
        "wspr_compare_map_source",
        COMPARE_MAP_COLORS,
        N=257,
    )
    bin_count = len(boundaries_db) - 1
    colormap = mpl.colors.ListedColormap(
        source_colormap(np.linspace(0.0, 1.0, bin_count)),
        name="wspr_compare_map",
    )
    normalization = mpl.colors.BoundaryNorm(
        normalization_boundaries_db,
        colormap.N,
        clip=True,
    )
    return _CompareMapColorScale(
        colormap=colormap,
        normalization=normalization,
        boundaries_db=boundaries_db,
        ticks_db=ticks_db,
        tick_labels=tuple(
            _format_compare_map_tick(tick_db) for tick_db in ticks_db
        ),
    )


def _timed_span(timing_collector, label, detail=""):
    """Return a timing context when profiling is active."""
    if timing_collector is None:
        return nullcontext()
    return timing_collector.span(label, detail=detail)


def _base_map_draw_profile_enabled():
    """Return whether the expensive base-only map draw diagnostic is enabled."""
    value = os.getenv(BASEMAP_DRAW_PROFILE_ENV, "")
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _preview_base_map_cache_enabled():
    """Return whether live preview maps should use the static basemap raster cache."""
    value = os.getenv(BASEMAP_CACHE_ENV, "1")
    return str(value).strip().lower() not in {"0", "false", "no", "off"}


def _preview_basemap_cache_center(qth, fallback_latitude, fallback_longitude):
    """Return the 4-character QTH cache label and static preview basemap center."""
    basemap_qth = normalize_ascii_upper(qth)[:4]
    if len(basemap_qth) != 4:
        return "", fallback_latitude, fallback_longitude

    try:
        cache_latitude, cache_longitude = locator_to_latlon(basemap_qth)
    except (TypeError, ValueError):
        return "", fallback_latitude, fallback_longitude
    return basemap_qth, cache_latitude, cache_longitude


def _draw_preview_canvas_for_profile(fig, dpi=MAP_PROFILE_PREVIEW_DPI):
    """Draw a figure canvas at preview DPI and return a profiler detail string."""
    canvas = ensure_agg_canvas(fig)

    original_dpi = fig.dpi
    try:
        fig.set_dpi(dpi)
        canvas.draw()
        width_px, height_px = canvas.get_width_height()
    finally:
        fig.set_dpi(original_dpi)
    return f"{width_px}x{height_px} px | {dpi:g} dpi | extra diagnostic draw"


def _draw_footer_summary_bars(
    fig,
    *,
    station_counts,
    spot_counts,
    colors,
    text_colors,
    theme_config,
    stations_plural="STATIONS",
    evidence_plural="SPOTS",
    thousands_separator=None,
    bar_bbox=None,
    row_label_fontsize=FONT_LEGEND,
):
    """Draw visible-scope station and evidence composition as two stacked bars."""
    if not (
        len(station_counts)
        == len(spot_counts)
        == len(colors)
        == len(text_colors)
    ):
        raise ValueError("Footer summary series must have matching lengths")

    station_total = sum(station_counts)
    spot_total = sum(spot_counts)
    station_percentages = [
        count / station_total * 100 if station_total > 0 else 0
        for count in station_counts
    ]
    spot_percentages = [
        count / spot_total * 100 if spot_total > 0 else 0
        for count in spot_counts
    ]

    summary_axis = fig.add_axes(
        (
            bar_bbox
            if bar_bbox is not None
            else theme_config.get("bar_bbox", [0.12, 0.035, 0.85, 0.045])
        )
    )
    summary_axis.set_facecolor(theme_config["bar_face"])
    for spine in summary_axis.spines.values():
        spine.set_visible(False)
    summary_axis.set_xticks([])
    summary_axis.tick_params(
        axis="y",
        length=0,
        pad=10,
        colors=theme_config["bar_tick"],
        labelsize=row_label_fontsize,
    )

    left_positions = [0.0, 0.0]
    for station_count, spot_count, station_pct, spot_pct, color, text_color in zip(
        station_counts,
        spot_counts,
        station_percentages,
        spot_percentages,
        colors,
        text_colors,
    ):
        rectangles = summary_axis.barh(
            [stations_plural, evidence_plural],
            [station_pct, spot_pct],
            left=left_positions,
            color=color,
            height=0.6,
        )
        for rectangle, count in zip(rectangles, [station_count, spot_count]):
            if count <= 0 or rectangle.get_width() < 2.5:
                continue
            summary_axis.text(
                rectangle.get_x() + rectangle.get_width() / 2,
                rectangle.get_y() + rectangle.get_height() / 2,
                (
                    str(int(count))
                    if thousands_separator is None
                    else f"{int(count):,}".replace(
                        ",",
                        str(thousands_separator),
                    )
                ),
                color=text_color,
                ha="center",
                va="center",
                fontsize=FONT_LEGEND - 2,
            )
        left_positions[0] += station_pct
        left_positions[1] += spot_pct

    return summary_axis


def _success_map_presentation_labels(
    translations,
    absolute_mode,
    success_terms,
):
    """Return localized map-only footer and legend terms for RX or TX Performance."""
    mode_key = "tx" if str(absolute_mode).upper().startswith("TX") else "rx"
    key_prefix = f"map_success_{mode_key}"
    return {
        "footer_opportunities": translations[
            "map_success_footer_opportunities"
        ],
        "footer_stations": translations["map_success_footer_stations"],
        "opportunity_target": success_terms.get(
            "opportunity_success",
            translations[f"{key_prefix}_opportunity_target"],
        ),
        "opportunity_counter": success_terms.get(
            "opportunity_counter",
            translations[f"{key_prefix}_opportunity_counter"],
        ),
        "station_target": success_terms.get(
            "station_success",
            translations[f"{key_prefix}_station_target"],
        ),
        "station_counter": success_terms.get(
            "station_counter",
            translations[f"{key_prefix}_station_counter"],
        ),
        "insufficient": translations["map_success_legend_insufficient"],
    }


def _draw_success_map_legend(
    ax,
    *,
    presentation_labels,
    theme_config,
    marker_size_points_squared,
):
    """Draw the three-entry Success station-status legend outside the map disk."""
    legend_marker_size = float(np.sqrt(marker_size_points_squared))
    target_observed_handle = Line2D(
        [],
        [],
        linestyle="none",
        marker="o",
        markersize=legend_marker_size,
        markerfacecolor=SUCCESS_MAP_TARGET_COLOR,
        markeredgecolor=SUCCESS_MAP_MARKER_EDGE_COLOR,
        markeredgewidth=SUCCESS_MAP_MARKER_EDGE_LINEWIDTH_POINTS,
        label=presentation_labels["station_target"],
    )
    counter_only_handle = Line2D(
        [],
        [],
        linestyle="none",
        marker="o",
        markersize=legend_marker_size,
        markerfacecolor=SUCCESS_MAP_COUNTER_COLOR,
        markeredgecolor=SUCCESS_MAP_MARKER_EDGE_COLOR,
        markeredgewidth=SUCCESS_MAP_MARKER_EDGE_LINEWIDTH_POINTS,
        alpha=SUCCESS_MAP_COUNTER_ALPHA,
        label=presentation_labels["station_counter"],
    )
    no_segment_handle = Patch(
        facecolor=theme_config["no_hm_face"],
        edgecolor=theme_config["no_hm_edge"],
        linewidth=0.9,
        label=presentation_labels["insufficient"],
    )
    legend = ax.legend(
        handles=[
            target_observed_handle,
            counter_only_handle,
            no_segment_handle,
        ],
        loc="upper right",
        bbox_to_anchor=SUCCESS_MAP_LEGEND_BBOX,
        bbox_transform=ax.figure.transFigure,
        facecolor=theme_config["legend_face"],
        edgecolor=theme_config["legend_edge"],
        labelcolor=theme_config["legend_text"],
        fontsize=FONT_LEGEND,
        markerscale=1.6,
    )
    legend.set_gid("success-map-legend")
    legend.set_zorder(15)
    return legend


def _profile_base_only_map_draw(
    *,
    title,
    maximum_distance_km,
    center_latitude,
    center_longitude,
    theme_name,
    theme_config,
    timing_collector,
):
    """Measure the static base-map draw path without changing the rendered map."""
    if timing_collector is None or not _base_map_draw_profile_enabled():
        return

    with _timed_span(timing_collector, "diagnostic base-only construction"):
        base_fig, _, _, _ = create_base_map_figure(
            title=title,
            maximum_distance_km=maximum_distance_km,
            center_latitude=center_latitude,
            center_longitude=center_longitude,
            theme_name=theme_name,
            theme_config=theme_config,
        )

    try:
        draw_start = perf_counter()
        detail = _draw_preview_canvas_for_profile(base_fig)
        timing_collector.add("diagnostic base-only canvas draw", perf_counter() - draw_start, detail=detail)
    finally:
        base_fig.clear()


@synchronized_matplotlib
def render_map_figure(
    map_data,
    *,
    title,
    start_t,
    end_t,
    max_dist_km,
    base_min_stations,
    lat_0,
    lon_0,
    analysis_context,
    presentation_context,
    timing_collector=None,
):
    """Render presentation-only map output from precomputed pure aggregates."""
    theme = presentation_context.theme
    theme_cfg = MAP_THEMES.get(theme, MAP_THEMES["dark"])
    analysis_id = map_data.analysis_id
    is_compare = map_data.is_compare
    is_sequential = map_data.is_sequential
    is_opportunity = validate_map_analysis_mode(
        analysis_kind=map_data.analysis_kind,
        is_compare=is_compare,
    )
    df_plot = map_data.station_rows
    segs = map_data.segment_rows

    if theme == "dark" and _preview_base_map_cache_enabled():
        with _timed_span(timing_collector, "base-map cache construction"):
            cache_label, cache_latitude, cache_longitude = _preview_basemap_cache_center(
                analysis_context.qth,
                lat_0,
                lon_0,
            )
            fig, ax, proj, pc_proj, cache_detail = create_preview_cached_base_map_figure(
                title=title,
                maximum_distance_km=max_dist_km,
                center_latitude=lat_0,
                center_longitude=lon_0,
                theme_name=theme,
                theme_config=theme_cfg,
                cache_label=cache_label,
                cache_center_latitude=cache_latitude,
                cache_center_longitude=cache_longitude,
                preview_dpi=MAP_PROFILE_PREVIEW_DPI,
            )
        if timing_collector is not None:
            timing_collector.add("base-map cache", 0.0, detail=cache_detail)
    else:
        with _timed_span(timing_collector, "base-map construction"):
            fig, ax, proj, pc_proj = create_base_map_figure(
                title=title,
                maximum_distance_km=max_dist_km,
                center_latitude=lat_0,
                center_longitude=lon_0,
                theme_name=theme,
                theme_config=theme_cfg,
            )

        _profile_base_only_map_draw(
            title=title,
            maximum_distance_km=max_dist_km,
            center_latitude=lat_0,
            center_longitude=lon_0,
            theme_name=theme,
            theme_config=theme_cfg,
            timing_collector=timing_collector,
        )

    # Presentation text is supplied explicitly and never controls scientific branches.
    t_lang = presentation_context.labels
    target_call = analysis_context.callsign.upper()
    absolute_mode = "TX" if analysis_id.startswith("TX") else "RX"
    abs_terms = presentation_context.absolute_terms(absolute_mode)
    success_map_labels = (
        _success_map_presentation_labels(t_lang, absolute_mode, abs_terms)
        if is_opportunity
        else None
    )
    # Fixed identities use their callsigns. Sequential TX uses path roles
    # because Target and Reference share one transmitter callsign.
    if (
        analysis_context.comparison_mode == COMPARISON_HARDWARE_AB
        and is_sequential
    ):
        lbl_only_me = t_lang['leg_only_me'].format(
            callsign=t_lang['txt_target']
        )
        lbl_only_ref = t_lang['leg_only_ref'].format(
            ref_callsign=t_lang['txt_reference']
        )
    else:
        lbl_only_me = t_lang['leg_only_me'].format(callsign=target_call)
        if analysis_context.comparison_mode == COMPARISON_LOCAL_NEIGHBORHOOD:
            lbl_only_ref = t_lang['leg_only_ref_radius']
        else:
            lbl_only_ref = t_lang['leg_only_ref'].format(
                ref_callsign=analysis_context.reference_callsign.upper()
            )

    visible_segs = segs[segs["r_min"] < max_dist_km].copy()

    # Colormaps
    if is_compare:
        compare_scale = _build_compare_map_color_scale(
            visible_segs["val"].to_numpy()
        )
        cmap = compare_scale.colormap
        norm = compare_scale.normalization
        ticks = compare_scale.ticks_db
        lbls = compare_scale.tick_labels
        cbar_title = t_lang["cbar_comp"]
    else:
        clrs = list(SUCCESS_RATE_COLORS)
        bnds = np.asarray(SUCCESS_RATE_BOUNDS, dtype=float)
        lbls = list(SUCCESS_RATE_TICK_LABELS)
        ticks = bnds
        cbar_title = t_lang[f"cbar_abs_{abs_terms['mode'].lower()}"]
        cmap = mpl.colors.ListedColormap(clrs)
        norm = mpl.colors.BoundaryNorm(bnds, cmap.N, clip=True)
    
    with _timed_span(timing_collector, "wedge creation"):
        # Draw Heatmap Wedges
        patches = []
        for _, r in visible_segs.iterrows():
            center_az = r['az_bucket'] * AZIMUTH_STEP
            az_min = center_az - (AZIMUTH_STEP / 2.0)
            az_max = center_az + (AZIMUTH_STEP / 2.0)
            theta1 = 90 - az_max
            theta2 = 90 - az_min
            patches.append(Wedge((0,0), min(r['r_max'], max_dist_km)*1000, theta1, theta2, width=(min(r['r_max'], max_dist_km)-r['r_min'])*1000))

        if is_compare:
            heatmap_alpha = COMPARE_MAP_HEATMAP_ALPHA
        else:
            heatmap_alpha = SUCCESS_MAP_HEATMAP_ALPHA
        if patches:
            p = PatchCollection(patches, cmap=cmap, norm=norm, alpha=heatmap_alpha, edgecolor='none', transform=proj, zorder=3)
            p.set_array(visible_segs['val'].to_numpy())
            ax.add_collection(p)
        else:
            p = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
            p.set_array([])
        if is_opportunity:
            p.set_gid("success-sector-fills")
    
    lbl_both_async = t_lang['leg_both_async']

    scatter_start = perf_counter()

    # Draw Scatter Dots
    if is_compare:
        df_joint = df_plot[df_plot['spot_count'] > 0]
        df_both = df_plot[(df_plot['spot_count'] == 0) & (df_plot['count_only_u'] > 0) & (df_plot['count_only_r'] > 0)]
        df_only_u = df_plot[(df_plot['spot_count'] == 0) & (df_plot['count_only_u'] > 0) & (df_plot['count_only_r'] == 0)]
        df_only_r = df_plot[(df_plot['spot_count'] == 0) & (df_plot['count_only_u'] == 0) & (df_plot['count_only_r'] > 0)]
        
        # Draw Scatter Dots Legend
        if not df_joint.empty: ax.scatter(df_joint['peer_lon'], df_joint['peer_lat'], c=COLOR_JOINT, s=8, alpha=1.0, edgecolors='black', linewidth=0.35, transform=pc_proj, zorder=10, label=t_lang['leg_joint'])
        if not df_both.empty: ax.scatter(df_both['peer_lon'], df_both['peer_lat'], c=COLOR_BOTH_ASYNC, s=8, alpha=1.0, edgecolors='black', linewidth=0.35, transform=pc_proj, zorder=9, label=lbl_both_async)
        if not df_only_u.empty: ax.scatter(df_only_u['peer_lon'], df_only_u['peer_lat'], c=COLOR_ONLY_ME, s=8, alpha=1.0, edgecolors='black', linewidth=0.35, transform=pc_proj, zorder=8, label=lbl_only_me)
        if not df_only_r.empty: ax.scatter(df_only_r['peer_lon'], df_only_r['peer_lat'], c=theme_cfg["only_ref"], s=8, alpha=1.0, edgecolors=theme_cfg["only_ref_edge"], linewidth=0.35, transform=pc_proj, zorder=8, label=lbl_only_ref)
        leg = ax.legend(loc='lower center', bbox_to_anchor=LEG_BBOX, facecolor=theme_cfg["legend_face"], edgecolor=theme_cfg["legend_edge"], labelcolor=theme_cfg["legend_text"], fontsize=FONT_LEGEND, markerscale=2.0)
        leg.set_zorder(15)
    else:
        eligible = df_plot[
            (df_plot["r_min"] < float(max_dist_km))
            & df_plot["eligible"]
            & df_plot["rate_pct"].notna()
        ]
        target_observed_stations = eligible[eligible["hits"] > 0]
        counter_only_stations = eligible[eligible["hits"] == 0]
        common_marker_size = SUCCESS_MAP_MARKER_SIZE_POINTS_SQUARED
        if not counter_only_stations.empty:
            counter_only_markers = ax.scatter(
                counter_only_stations["peer_lon"],
                counter_only_stations["peer_lat"],
                s=common_marker_size,
                facecolors=SUCCESS_MAP_COUNTER_COLOR,
                edgecolors=SUCCESS_MAP_MARKER_EDGE_COLOR,
                linewidth=SUCCESS_MAP_MARKER_EDGE_LINEWIDTH_POINTS,
                alpha=SUCCESS_MAP_COUNTER_ALPHA,
                transform=pc_proj,
                zorder=9,
            )
            counter_only_markers.set_gid("success-counter-only-markers")
        if not target_observed_stations.empty:
            target_observed_markers = ax.scatter(
                target_observed_stations["peer_lon"],
                target_observed_stations["peer_lat"],
                s=common_marker_size,
                facecolors=SUCCESS_MAP_TARGET_COLOR,
                edgecolors=SUCCESS_MAP_MARKER_EDGE_COLOR,
                linewidth=SUCCESS_MAP_MARKER_EDGE_LINEWIDTH_POINTS,
                alpha=1.0,
                transform=pc_proj,
                zorder=10,
            )
            target_observed_markers.set_gid(
                "success-target-observed-markers"
            )
        _draw_success_map_legend(
            ax,
            presentation_labels=success_map_labels,
            theme_config=theme_cfg,
            marker_size_points_squared=common_marker_size,
        )

    if timing_collector is not None:
        timing_collector.add("scatter rendering", perf_counter() - scatter_start)

    # Colorbar
    colorbar_bbox = COMPARE_MAP_CBAR_BBOX if is_compare else CBAR_BBOX
    cax = fig.add_axes(colorbar_bbox)

    # The heatmap wedges are semi-transparent over the dark map.
    # The colorbar must use the same dark backing, otherwise alpha blends against
    # the default axes background and the legend colors no longer match the map.
    cax.set_facecolor(theme_cfg["cbar_face"])

    if is_compare:
        cbar = fig.colorbar(
            p,
            cax=cax,
            ticks=ticks,
            boundaries=compare_scale.boundaries_db,
            spacing="proportional",
            drawedges=True,
        )
    else:
        cbar = fig.colorbar(p, cax=cax, ticks=ticks, spacing="uniform")
    cbar.ax.set_facecolor(theme_cfg["cbar_face"])

    if hasattr(cbar, "solids"):
        cbar.solids.set_alpha(heatmap_alpha)
        if is_compare:
            cbar.solids.set_edgecolor("none")
            cbar.solids.set_linewidth(0.0)
        else:
            cbar.solids.set_edgecolor("face")

    if is_compare and hasattr(cbar, "dividers"):
        cbar.dividers.set_color(theme_cfg["cbar_text"])
        cbar.dividers.set_alpha(COMPARE_MAP_COLORBAR_DIVIDER_ALPHA)
        cbar.dividers.set_linewidth(COMPARE_MAP_COLORBAR_DIVIDER_LINEWIDTH)
        cbar.dividers.set_gid("compare-map-bin-dividers")

    cbar.ax.set_yticklabels(lbls, color=theme_cfg["cbar_text"])
    cbar.ax.tick_params(labelsize=FONT_CBAR)
    cbar.ax.tick_params(colors=theme_cfg["cbar_text"])
    cbar.set_label(cbar_title, color=theme_cfg["cbar_text"], fontweight='bold', labelpad=15, fontsize=FONT_LEGEND)

    
    # Meta Footer
    t_time = f"{start_t.strftime('%d-%b-%Y')} - {end_t.strftime('%d-%b-%Y')}"
    t_band = analysis_context.band
    t_solar = presentation_context.solar_label

    meta_parts = [
        t_lang["map_footer_time"].format(value=t_time),
        t_lang["map_footer_band"].format(value=t_band),
        t_lang["map_footer_solar"].format(value=t_solar),
    ]
    
    if is_compare:
        if is_sequential:
            meta_parts.append(t_lang["map_footer_sync_sequential_ab"])
            meta_parts.append(
                t_lang["map_footer_joint_pairs_per_station"].format(
                    threshold=analysis_context.min_joint_spots_per_station
                )
            )
            meta_parts.append(
                t_lang["map_footer_schedule"].format(
                    interval=analysis_context.tx_ab_repeat_interval_minutes,
                    target_start=analysis_context.tx_ab_target_start_minute,
                    reference_start=analysis_context.tx_ab_reference_start_minute,
                )
            )
            meta_parts.append(
                t_lang["map_footer_joint_stations_per_segment"].format(
                    threshold=base_min_stations
                )
            )
        else:
            meta_parts.append(
                t_lang["map_footer_joint_spots_per_station"].format(
                    threshold=analysis_context.min_joint_spots_per_station
                )
            )
            meta_parts.append(
                t_lang["map_footer_joint_stations_per_segment"].format(
                    threshold=base_min_stations
                )
            )
            
        benchmark_offset_db = round(float(analysis_context.reference_snr_correction_db), 1)
        if abs(benchmark_offset_db) >= 0.05:
            offset_label = t_lang["txt_benchmark_offset_note"]
            meta_parts.append(offset_label.format(offset=benchmark_offset_db))

        if analysis_context.comparison_mode == COMPARISON_LOCAL_NEIGHBORHOOD:
            local_mode = (
                t_lang['opt_local_median']
                if analysis_context.local_benchmark == LOCAL_BENCHMARK_MEDIAN
                else t_lang['opt_local_best']
            )
            ref_radius = analysis_context.neighborhood_radius_km
            reference_value = f"{local_mode} (≤{ref_radius} km)"
        elif analysis_context.comparison_mode == COMPARISON_HARDWARE_AB:
            if is_sequential:
                reference_value = t_lang['txt_reference']
            else:
                reference_value = analysis_context.reference_callsign.upper()
        else:
            reference_value = analysis_context.reference_callsign.upper()
        meta_parts.append(
            t_lang["map_footer_reference"].format(reference=reference_value)
        )
    else:
        meta_parts.append(
            t_lang[
                "map_performance_footer_confirmed_opportunities_per_station"
            ].format(
                threshold=analysis_context.min_confirmed_opportunities_per_peer
            )
        )
        meta_parts.append(
            t_lang["map_performance_footer_stations_per_segment"].format(
                threshold=base_min_stations
            )
        )
        meta_parts.append(t_lang["map_performance_footer_segment_metric"])

    # Neu: Füge Max distance Peer hinzu
    if is_compare and analysis_context.comparison_mode == COMPARISON_LOCAL_NEIGHBORHOOD:
        if 'best_ref_dist' in df_plot.columns:
            # Filtere leere/NaN Distanzen raus
            valid_dists = df_plot[df_plot['best_ref_dist'] > 0]['best_ref_dist']
            if not valid_dists.empty:
                max_peer_dist = int(valid_dists.max() / 1000)
                meta_parts.append(
                    t_lang["map_footer_max_reference_distance"].format(
                        distance_km=max_peer_dist
                    )
                )

    line1_str = " | ".join(meta_parts)
    # ==========================================
    # RENDER FOOTER METRICS & PARAMETERS
    # ==========================================
    if is_compare:
        counts = compare_footer_counts(df_plot, max_dist_km=max_dist_km)
        _draw_footer_summary_bars(
            fig,
            station_counts=[
                counts["stat_only_u"],
                counts["stat_joint"],
                counts["stat_both_async"],
                counts["stat_only_r"],
            ],
            spot_counts=[
                counts["spot_only_u"],
                counts["spot_joint"],
                counts["spot_both_async"],
                counts["spot_only_r"],
            ],
            colors=[
                COLOR_ONLY_ME,
                COLOR_JOINT,
                COLOR_BOTH_ASYNC,
                theme_cfg["only_ref"],
            ],
            text_colors=["white", "black", "black", "black"],
            theme_config=theme_cfg,
            stations_plural=t_lang["map_success_footer_stations"],
            evidence_plural=(
                t_lang["map_compare_footer_pairs"]
                if is_sequential
                else t_lang["map_compare_footer_spots"]
            ),
        )
        fig.text(0.50, 0.025, line1_str, color=theme_cfg["footer"], ha='center', fontsize=FONT_FOOTER)
        fig.text(0.98, 0.008, f"WSPRadar.org {APP_VERSION}", color=theme_cfg["footer"], ha='right', fontsize=FONT_FOOTER)
        
    else:
        counts = opportunity_footer_counts(df_plot, max_dist_km=max_dist_km)
        success_footer_axis = _draw_footer_summary_bars(
            fig,
            station_counts=[counts["stat_target"], counts["stat_counter_only"]],
            spot_counts=[counts["spot_target"], counts["spot_counter"]],
            colors=[COLOR_JOINT, theme_cfg["only_ref"]],
            text_colors=["black", "black"],
            theme_config=theme_cfg,
            stations_plural=success_map_labels["footer_stations"],
            evidence_plural=success_map_labels["footer_opportunities"],
            bar_bbox=SUCCESS_MAP_FOOTER_BBOX,
            row_label_fontsize=FONT_LEGEND,
        )
        success_footer_axis.set_gid("success-map-footer")
        success_footer_patch_specs = (
            (
                0,
                "success-footer-stations-target",
                success_map_labels["station_target"],
            ),
            (
                1,
                "success-footer-opportunities-target",
                success_map_labels["opportunity_target"],
            ),
            (
                2,
                "success-footer-stations-counter",
                success_map_labels["station_counter"],
            ),
            (
                3,
                "success-footer-opportunities-counter",
                success_map_labels["opportunity_counter"],
            ),
        )
        for patch_index, patch_gid, patch_label in success_footer_patch_specs:
            success_footer_patch = success_footer_axis.patches[patch_index]
            success_footer_patch.set_gid(patch_gid)
            success_footer_patch.set_label(patch_label)
        fig.text(0.50, 0.025, line1_str, color=theme_cfg["footer_abs"], ha='center', fontsize=FONT_FOOTER)
        fig.text(0.98, 0.008, f"WSPRadar.org {APP_VERSION}", color=theme_cfg["footer"], ha='right', fontsize=FONT_FOOTER)

    return MapFigure(
        figure=fig,
        map_data=map_data,
        footer_text=line1_str,
    )


def generate_map_plot(
    df,
    title,
    is_compare,
    is_sequential,
    start_t,
    end_t,
    max_dist_km,
    analysis_id,
    base_min_stations,
    lat_0,
    lon_0,
    *,
    analysis_context,
    presentation_context,
    theme=None,
    analysis_kind,
    timing_collector=None,
):
    """Build pure map aggregates, then render them through presentation context."""
    with _timed_span(timing_collector, "map data aggregation"):
        map_data = build_map_data(
            df,
            analysis_id=analysis_id,
            is_compare=is_compare,
            is_sequential=is_sequential,
            analysis_kind=analysis_kind,
            center_latitude=lat_0,
            center_longitude=lon_0,
            min_spots=analysis_context.min_joint_spots_per_station,
            min_opportunities=analysis_context.min_confirmed_opportunities_per_peer,
            base_min_stations=base_min_stations,
            tx_ab_repeat_interval_minutes=(
                analysis_context.tx_ab_repeat_interval_minutes
            ),
            tx_ab_target_start_minute=analysis_context.tx_ab_target_start_minute,
            tx_ab_reference_start_minute=(
                analysis_context.tx_ab_reference_start_minute
            ),
            owns_input=True,
        )
    if map_data is None:
        return None

    render_context = (
        replace(presentation_context, theme=theme)
        if theme is not None and theme != presentation_context.theme
        else presentation_context
    )
    return render_map_figure(
        map_data,
        title=title,
        start_t=start_t,
        end_t=end_t,
        max_dist_km=max_dist_km,
        base_min_stations=base_min_stations,
        lat_0=lat_0,
        lon_0=lon_0,
        analysis_context=analysis_context,
        presentation_context=render_context,
        timing_collector=timing_collector,
    )
