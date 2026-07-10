"""
Plot Engine.
Fuehrt die geografische Aggregation durch und zeichnet die Cartopy-Map.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use the non-interactive backend required by Streamlit Cloud.
import matplotlib as mpl
from contextlib import nullcontext
from matplotlib.patches import Patch, Wedge
from matplotlib.collections import PatchCollection
import os
from time import perf_counter
import streamlit as st

from config import *
from core.opportunity_engine import (
    aggregate_opportunity_peers,
    aggregate_opportunity_segments,
    SUCCESS_RATE_BOUNDS,
    SUCCESS_RATE_COLORS,
    SUCCESS_RATE_TICK_LABELS,
)
from core.compare_engine import aggregate_compare_map_data, compare_footer_counts
from core.map_base import create_base_map_figure, create_preview_cached_base_map_figure
from core.matplotlib_runtime import ensure_agg_canvas, synchronized_matplotlib
from core.math_utils import locator_to_latlon
from core.snr_utils import round_snr_like_columns
from i18n import T, absolute_terms

MIN_LABEL_CUTOFF_PCT = 0.02
COMPARE_NEUTRAL_COLOR = "#fff2a8"
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
    basemap_qth = str(qth or "").strip().upper()[:4]
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
    theme="dark",
    analysis_kind="comparison",
    timing_collector=None,
):
    """Hauptfunktion zum Berechnen der Aggregate und Plotten der Radar-Karte."""
    theme_cfg = MAP_THEMES.get(theme, MAP_THEMES["dark"])
    is_opportunity = analysis_kind == "opportunity"

    if is_opportunity:
        with _timed_span(timing_collector, "map aggregation: opportunity peers"):
            df = aggregate_opportunity_peers(
                df,
                min_opportunities=st.session_state.get("val_min_opportunities", 5),
            )
        if df.empty:
            return None
    
    with _timed_span(timing_collector, "geometry bucketing"):
        # Entfernungen & Azimut berechnen
        l1, n1, l2, n2 = map(np.radians, [lat_0, lon_0, df['peer_lat'], df['peer_lon']])
        a = np.sin((l2-l1)/2.0)**2 + np.cos(l1)*np.cos(l2)*np.sin((n2-n1)/2.0)**2
        df['calc_dist'] = (2 * EARTH_RADIUS_KM) * np.arcsin(np.sqrt(a))

        y = np.sin(n2-n1) * np.cos(l2)
        x = np.cos(l1) * np.sin(l2) - np.sin(l1) * np.cos(l2) * np.cos(n2-n1)
        df['calc_azimuth'] = (np.degrees(np.arctan2(y, x)) + 360) % 360

        # Segment-Klassifizierung
        df['az_bucket'] = ((df['calc_azimuth'] + (AZIMUTH_STEP / 2.0)) % 360) // AZIMUTH_STEP
        df['dir_name'] = df['az_bucket'].apply(lambda v: COMPASS[int(v)] if pd.notnull(v) else "")

        df['r_min'] = pd.cut(df['calc_dist'], bins=DIST_BINS, labels=DIST_BINS[:-1], right=False).astype(float)
        df['r_max'] = pd.cut(df['calc_dist'], bins=DIST_BINS, labels=DIST_BINS[1:], right=False).astype(float)
        df['dist_label'] = df.apply(lambda r: f"[{int(r['r_min'])}-{int(r['r_max'])}km]" if pd.notnull(r['r_min']) else "", axis=1)
        df['SegmentID'] = df.apply(lambda r: f"{r['dist_label']} {r['dir_name']}" if pd.notnull(r['r_min']) else "Out of Bounds", axis=1)

    if is_opportunity:
        with _timed_span(timing_collector, "map aggregation: opportunity segments"):
            df_plot = df.copy()
            segs = aggregate_opportunity_segments(df_plot)
            if not segs.empty:
                segs = segs[segs["cnt"] >= base_min_stations]
    elif not is_compare:
        with _timed_span(timing_collector, "map aggregation: absolute segments"):
            # Absolute Logik: Median Aggregation
            station_counts = df.groupby(['SegmentID', 'peer_sign']).size().reset_index(name='spot_count')
            valid_stations = station_counts[station_counts['spot_count'] >= st.session_state.val_min_spots]
            df_valid = df.merge(valid_stations[['SegmentID', 'peer_sign']], on=['SegmentID', 'peer_sign'], how='inner')

            reporter_medians = df_valid.groupby(['SegmentID', 'dist_label', 'dir_name', 'r_min', 'r_max', 'az_bucket', 'peer_sign', 'peer_grid']).agg(
                stat_val=('stat_val', 'median'),
                spot_count=('stat_val', 'count'),
                peer_lat=('peer_lat', 'first'),
                peer_lon=('peer_lon', 'first'),
                calc_dist=('calc_dist', 'first'),
                calc_azimuth=('calc_azimuth', 'first')
            ).reset_index()
            reporter_medians = round_snr_like_columns(reporter_medians)

            segs = reporter_medians.groupby(['SegmentID', 'dist_label', 'dir_name', 'r_min', 'r_max', 'az_bucket']).agg(
                val=('stat_val', 'median'),
                cnt=('peer_sign', 'nunique'),
                total_spots=('spot_count', 'sum')
            ).reset_index()
            segs = round_snr_like_columns(segs, columns=['val'])
            segs = segs[segs['cnt'] >= base_min_stations]
            df_plot = reporter_medians
    else:
        with _timed_span(timing_collector, "map aggregation: compare segments"):
            df_plot, segs = aggregate_compare_map_data(
                df,
                is_sequential=is_sequential,
                min_spots=st.session_state.val_min_spots,
                base_min_stations=base_min_stations,
                tx_ab_bin_minutes=st.session_state.get('val_tx_ab_bin_minutes', 8),
            )

    if df_plot.empty or (segs.empty and not is_opportunity): return None

    if theme == "dark" and _preview_base_map_cache_enabled():
        with _timed_span(timing_collector, "base-map cache construction"):
            cache_label, cache_latitude, cache_longitude = _preview_basemap_cache_center(
                st.session_state.get("val_qth", ""),
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

    # UI Texts
    t_lang = T[st.session_state.lang]
    target_call = st.session_state.val_callsign.upper()
    absolute_mode = "TX" if analysis_id.startswith("TX") else "RX"
    abs_terms = absolute_terms(t_lang, absolute_mode)
    # Setup specific labels based on the active test mode
    if st.session_state.val_comp_mode == t_lang["opt_comp_self"]:
        if st.session_state.val_self_test_mode == t_lang["opt_self_rx"]:
            lbl_only_me = t_lang['leg_only_me'].format(callsign=st.session_state.val_callsign.upper())
            lbl_only_ref = t_lang['leg_only_ref'].format(ref_callsign=st.session_state.val_self_call_b.upper())
        else:
            lbl_only_me = t_lang['leg_only_me'].format(callsign="Setup A")
            lbl_only_ref = t_lang['leg_only_ref'].format(ref_callsign="Setup B")
    else:
        lbl_only_me = t_lang['leg_only_me'].format(callsign=target_call)
        if st.session_state.val_comp_mode == t_lang["opt_comp_radius"]:
            lbl_only_ref = t_lang['leg_only_ref_radius']
        else:
            lbl_only_ref = t_lang['leg_only_ref'].format(ref_callsign=st.session_state.val_ref_callsign.upper())

    # Colormaps
    if is_compare:
        clrs = ['#030b2e', '#0a318f', '#2270c1', '#6eb2e4', COMPARE_NEUTRAL_COLOR, '#fca083', '#f03b20', '#a50f15', '#400005']
        bnds = [-27, -21, -15, -9, -3, 3, 9, 15, 21, 27]
        lbls = ['-4S', '-3S', '-2S', '-1S', '±0', '+1S', '+2S', '+3S', '+4S']
        ticks = [-24, -18, -12, -6, 0, 6, 12, 18, 24]
        cbar_title = t_lang["cbar_comp"]
    elif is_opportunity:
        clrs = list(SUCCESS_RATE_COLORS)
        bnds = np.asarray(SUCCESS_RATE_BOUNDS, dtype=float)
        lbls = list(SUCCESS_RATE_TICK_LABELS)
        ticks = bnds
        cbar_title = t_lang["cbar_abs"]
    else:
        clrs = ['#190824', '#4662d7', '#36aaf9', '#1ae4b6', '#72fe5e', '#c9ef34', '#faba39', '#f66b19', '#cb2a04', '#590202']
        bnds = np.arange(-48, 18, 6)
        lbls = [f"{b}dB" for b in bnds]
        ticks = bnds
        cbar_title = t_lang["cbar_abs"]
    
    cmap = mpl.colors.ListedColormap(clrs)
    norm = mpl.colors.BoundaryNorm(bnds, cmap.N, clip=True)
    
    with _timed_span(timing_collector, "wedge creation"):
        # Draw Heatmap Wedges
        patches = []
        visible_segs = segs[segs["r_min"] < max_dist_km].copy()
        for _, r in visible_segs.iterrows():
            center_az = r['az_bucket'] * AZIMUTH_STEP
            az_min = center_az - (AZIMUTH_STEP / 2.0)
            az_max = center_az + (AZIMUTH_STEP / 2.0)
            theta1 = 90 - az_max
            theta2 = 90 - az_min
            patches.append(Wedge((0,0), min(r['r_max'], max_dist_km)*1000, theta1, theta2, width=(min(r['r_max'], max_dist_km)-r['r_min'])*1000))

        heatmap_alpha = 0.75
        if patches:
            p = PatchCollection(patches, cmap=cmap, norm=norm, alpha=heatmap_alpha, edgecolor='none', transform=proj, zorder=3)
            p.set_array(visible_segs['val'].to_numpy())
            ax.add_collection(p)
        else:
            p = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
            p.set_array([])
    
    lbl_both_async = t_lang.get('leg_both_async', 'Both (Async)')

    scatter_start = perf_counter()

    # Draw Scatter Dots
    if is_compare and 'count_only_u' in df_plot.columns:
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
    elif is_opportunity:
        eligible = df_plot[df_plot["eligible"] & df_plot["rate_pct"].notna()]
        hit_stations = eligible[eligible["hits"] > 0]
        miss_stations = eligible[eligible["hits"] == 0]
        hit_tiers = [
            (
                hit_stations[hit_stations["hits"] == 1],
                "#9aff85",
                7,
                t_lang.get("leg_abs_hit_one", "Target (T) = 1"),
            ),
            (
                hit_stations[hit_stations["hits"].between(2, 5, inclusive="both")],
                "#39ff14",
                9,
                t_lang.get("leg_abs_hit_mid", "Target (T) = 2-5"),
            ),
            (
                hit_stations[hit_stations["hits"] > 5],
                "#0b6f24",
                12,
                t_lang.get("leg_abs_hit_high", "Target (T) > 5"),
            ),
        ]
        for tier_df, tier_color, tier_size, tier_label in hit_tiers:
            if tier_df.empty:
                continue
            ax.scatter(
                tier_df["peer_lon"], tier_df["peer_lat"],
                c=tier_color,
                s=tier_size,
                alpha=1.0,
                edgecolors="black",
                linewidth=0.35, transform=pc_proj, zorder=10,
                label=tier_label,
            )
        if not miss_stations.empty:
            ax.scatter(
                miss_stations["peer_lon"], miss_stations["peer_lat"],
                c="#c7c7c7", s=8, alpha=0.9, edgecolors="black",
                linewidth=0.35, transform=pc_proj, zorder=9,
                label=abs_terms["counter_marker"],
            )
        handles, labels = ax.get_legend_handles_labels()
        no_hm_label = abs_terms["no_evidence"]
        handles.append(
            Patch(
                facecolor=theme_cfg.get("no_hm_face", "black"),
                edgecolor=theme_cfg.get("no_hm_edge", "#777777"),
                linewidth=0.9,
                label=no_hm_label,
            )
        )
        labels.append(no_hm_label)
        leg = ax.legend(
            handles,
            labels,
            loc="lower center",
            bbox_to_anchor=(LEG_BBOX[0], LEG_BBOX[1] - 0.05),
            facecolor=theme_cfg["legend_face"],
            edgecolor=theme_cfg["legend_edge"],
            labelcolor=theme_cfg["legend_text"],
            fontsize=FONT_LEGEND,
            markerscale=1.6,
        )
        leg.set_zorder(15)
    else:
        ax.scatter(df_plot['peer_lon'], df_plot['peer_lat'], c=COLOR_ONLY_ME, s=5, alpha=1.0, edgecolors='black', linewidth=0.35, transform=pc_proj, zorder=10, label=lbl_only_me)

    if timing_collector is not None:
        timing_collector.add("scatter rendering", perf_counter() - scatter_start)

    # Colorbar
    cax = fig.add_axes(CBAR_BBOX)

    # The heatmap wedges are semi-transparent over the dark map.
    # The colorbar must use the same dark backing, otherwise alpha blends against
    # the default axes background and the legend colors no longer match the map.
    cax.set_facecolor(theme_cfg["cbar_face"])

    cbar = fig.colorbar(p, cax=cax, ticks=ticks, spacing="uniform")
    cbar.ax.set_facecolor(theme_cfg["cbar_face"])

    if hasattr(cbar, "solids"):
        cbar.solids.set_alpha(heatmap_alpha)
        cbar.solids.set_edgecolor("face")

    cbar.ax.set_yticklabels(lbls, color=theme_cfg["cbar_text"])
    cbar.ax.tick_params(labelsize=FONT_CBAR)
    cbar.ax.tick_params(colors=theme_cfg["cbar_text"])
    cbar.set_label(cbar_title, color=theme_cfg["cbar_text"], fontweight='bold', labelpad=15, fontsize=FONT_LEGEND)

    
    # Meta Footer
    lbl_time = "Zeitraum" if st.session_state.lang == "de" else "Time"
    t_time = f"{start_t.strftime('%d-%b-%Y')} - {end_t.strftime('%d-%b-%Y')}"
    t_band = st.session_state.val_band
    t_solar = st.session_state.val_solar.split(" ")[0]

    meta_parts = [f"{lbl_time}: {t_time}", f"Band: {t_band}", f"Solar: {t_solar}"]
    
    if is_compare:
        if is_sequential:
            meta_parts.append("Sync: Sequential A/B")
            meta_parts.append(f"Joint Bins/Station: >={st.session_state.val_min_spots}")
            meta_parts.append(f"Joint Stations/Seg: >={base_min_stations}")
        else:
            meta_parts.append(f"Joint Spots/Station: ≥{st.session_state.val_min_spots}")
            meta_parts.append(f"Joint Stations/Seg: >={base_min_stations}")
            
        benchmark_offset_db = round(float(st.session_state.get("val_benchmark_offset_db", 0.0)), 1)
        if abs(benchmark_offset_db) >= 0.05:
            offset_label = t_lang.get("txt_benchmark_offset_note", "Ref SNR Corr: {offset:+.1f} dB")
            meta_parts.append(offset_label.format(offset=benchmark_offset_db))

        if st.session_state.val_comp_mode == t_lang["opt_comp_radius"]:
            local_mode = st.session_state.get('val_local_benchmark', t_lang.get('opt_local_median', 'Local Median Neighborhood'))
            ref_radius = st.session_state.get('val_ref_radius_km', 250)
            meta_parts.append(f"Ref: {local_mode} (≤{ref_radius} km)")
        elif st.session_state.val_comp_mode == t_lang["opt_comp_self"]:
            meta_parts.append(f"Ref: Self-Test Config")
        else: meta_parts.append(f"Ref: {st.session_state.val_ref_callsign.upper()}")
    elif is_opportunity:
        meta_parts.append(f"{abs_terms['pair']}/Station: >={st.session_state.get('val_min_opportunities', 5)}")
        meta_parts.append(f"Stations/Seg: >={base_min_stations}")
        meta_parts.append(f"Segment: average station {abs_terms['formula']}")
    else:
        meta_parts.append(f"Spots/Station: ≥{st.session_state.val_min_spots}")
        meta_parts.append(f"Stations/Seg: ≥{base_min_stations}")

    # Neu: Füge Max distance Peer hinzu
    if is_compare and st.session_state.val_comp_mode == t_lang["opt_comp_radius"]:
        if 'best_ref_dist' in df_plot.columns:
            # Filtere leere/NaN Distanzen raus
            valid_dists = df_plot[df_plot['best_ref_dist'] > 0]['best_ref_dist']
            if not valid_dists.empty:
                max_peer_dist = int(valid_dists.max() / 1000)
                meta_parts.append(f"Max reference distance: {max_peer_dist} km")

    line1_str = " | ".join(meta_parts)
    remote_str = t_lang['txt_rx_stations'] if analysis_id.startswith("TX") else t_lang['txt_tx_stations']
    
    # ==========================================
    # RENDER FOOTER METRICS & PARAMETERS
    # ==========================================
    if is_compare and 'count_only_u' in df_plot.columns:
        
        counts = compare_footer_counts(df_plot, max_dist_km=max_dist_km)
        stat_joint = counts["stat_joint"]
        stat_both_async = counts["stat_both_async"]
        stat_only_u = counts["stat_only_u"]
        stat_only_r = counts["stat_only_r"]
        spot_joint = counts["spot_joint"]
        spot_both_async = counts["spot_both_async"]
        spot_only_u = counts["spot_only_u"]
        spot_only_r = counts["spot_only_r"]
        tot_stats = counts["tot_stats"]
        tot_spots = counts["tot_spots"]

        # 2. Native Categorical Axes setup
        ax_bars = fig.add_axes(theme_cfg.get("bar_bbox", [0.12, 0.035, 0.85, 0.045]))
        ax_bars.set_facecolor(theme_cfg["bar_face"])
        for spine in ax_bars.spines.values(): spine.set_visible(False)
        ax_bars.set_xticks([])
        ax_bars.tick_params(axis='y', length=0, pad=10, colors=theme_cfg["bar_tick"], labelsize=FONT_LEGEND)
        
        # Prozentuale Breiten (0-100%) für sauberes Matplotlib-Skalieren
        pct_u_stat = (stat_only_u / tot_stats * 100) if tot_stats > 0 else 0
        pct_j_stat = (stat_joint / tot_stats * 100) if tot_stats > 0 else 0
        pct_a_stat = (stat_both_async / tot_stats * 100) if tot_stats > 0 else 0
        pct_r_stat = (stat_only_r / tot_stats * 100) if tot_stats > 0 else 0

        pct_u_spot = (spot_only_u / tot_spots * 100) if tot_spots > 0 else 0
        pct_j_spot = (spot_joint / tot_spots * 100) if tot_spots > 0 else 0
        pct_a_spot = (spot_both_async / tot_spots * 100) if tot_spots > 0 else 0
        pct_r_spot = (spot_only_r / tot_spots * 100) if tot_spots > 0 else 0
        
        # Radius Modus Check: Spots-Venn ausblenden, wenn wir gegen die Referenz-Wolke vergleichen
        is_radius_mode = (st.session_state.val_comp_mode == t_lang["opt_comp_radius"])
        
        categories = ['STATIONS', ' '] if is_radius_mode else ['STATIONS', 'SPOTS']

        # 3. Rendern der 4 Balken-Segmente übereinandergestapelt
        # Segment 1: Only U (Lila)
        p1 = ax_bars.barh(categories, [pct_u_stat, pct_u_spot if not is_radius_mode else 0], color=COLOR_ONLY_ME, height=0.6)
        # Segment 2: Joint (Grün)
        p2 = ax_bars.barh(categories, [pct_j_stat, pct_j_spot if not is_radius_mode else 0], left=[pct_u_stat, pct_u_spot if not is_radius_mode else 0], color=COLOR_JOINT, height=0.6)
        # Segment 3: Both Async (Orange)
        p3 = ax_bars.barh(categories, [pct_a_stat, pct_a_spot if not is_radius_mode else 0], left=[pct_u_stat+pct_j_stat, pct_u_spot+pct_j_spot if not is_radius_mode else 0], color=COLOR_BOTH_ASYNC, height=0.6)
        # Segment 4: Only R (Weiß)
        p4 = ax_bars.barh(categories, [pct_r_stat, pct_r_spot if not is_radius_mode else 0], left=[pct_u_stat+pct_j_stat+pct_a_stat, pct_u_spot+pct_j_spot+pct_a_spot if not is_radius_mode else 0], color=theme_cfg["only_ref"], height=0.6)
        
        # Dynamisches Zentrieren der echten Zahlenwerte in den Boxen
        def add_labels(rects, real_values, text_color):
            for rect, val in zip(rects, real_values):
                width = rect.get_width()
                if val > 0 and width >= 2.5:  # Keine Labels bei winzigen Slivers
                    x = rect.get_x() + (width / 2)
                    y = rect.get_y() + (rect.get_height() / 2)
                    ax_bars.text(x, y, str(val), color=text_color, ha='center', va='center', fontsize=FONT_LEGEND-2)

        # Die berechneten, absoluten Werte in die Render-Rechtecke injizieren
        if is_radius_mode:
            add_labels(p1, [stat_only_u], 'white')
            add_labels(p2, [stat_joint], 'black')
            add_labels(p3, [stat_both_async], 'black')
            add_labels(p4, [stat_only_r], 'black')
        else:
            add_labels(p1, [stat_only_u, spot_only_u], 'white')
            add_labels(p2, [stat_joint, spot_joint], 'black')
            add_labels(p3, [stat_both_async, spot_both_async], 'black')
            add_labels(p4, [stat_only_r, spot_only_r], 'black')
            
        # 4. Config string zentriert am unteren Rand
        fig.text(0.50, 0.025, line1_str, color=theme_cfg["footer"], ha='center', fontsize=FONT_FOOTER)
        fig.text(0.98, 0.008, f"WSPRadar.org {APP_VERSION}", color=theme_cfg["footer"], ha='right', fontsize=FONT_FOOTER)
        
    else:
        # Fallback für Absolute Maps
        fig.text(0.50, 0.035, line1_str, color=theme_cfg["footer_abs"], ha='center', fontsize=FONT_FOOTER)
        fig.text(0.98, 0.015, f"WSPRadar.org {APP_VERSION}", color=theme_cfg["footer"], ha='right', fontsize=FONT_FOOTER)

    return fig, df_plot, segs, line1_str
