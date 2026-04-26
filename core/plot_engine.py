"""
Plot Engine.
Führt die geografische Aggregation durch, rechnet Statistik (Wilcoxon) und zeichnet die Cartopy-Map.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Zwingt Matplotlib in den Headless-Modus (verhindert RAM-Leaks auf Streamlit Cloud)
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.path as mpath
from matplotlib.patches import Wedge
from matplotlib.collections import PatchCollection
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import warnings
from scipy.stats import wilcoxon
import streamlit as st

from config import *
from i18n import T

MIN_LABEL_CUTOFF_PCT = 0.02

def generate_map_plot(df, title, is_compare, is_sequential, start_t, end_t, max_dist_km, analysis_id, wilcox_level, base_min_stations, lat_0, lon_0):
    """Hauptfunktion zum Berechnen der Aggregate und Plotten der Radar-Karte."""
    
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

    if not is_compare:
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
        
        segs = reporter_medians.groupby(['SegmentID', 'dist_label', 'dir_name', 'r_min', 'r_max', 'az_bucket']).agg(
            val=('stat_val', 'median'),
            cnt=('peer_sign', 'nunique'),
            total_spots=('spot_count', 'sum')
        ).reset_index()
        segs = segs[segs['cnt'] >= base_min_stations]
        df_plot = reporter_medians 
    else:
        # Compare Logik: Joint Spots / Sequential vs Simultaneous (High-Performance Vectorized)
        df_plot = df.copy()
        min_s = st.session_state.val_min_spots
        
        # Gruppierungsschlüssel und Aggregations-Regeln für die Geometrie-Metadaten
        group_keys = ['SegmentID', 'dist_label', 'dir_name', 'r_min', 'r_max', 'az_bucket', 'peer_sign']
        spatial_agg = {
            'peer_lat': 'first',
            'peer_lon': 'first',
            'peer_grid': 'first',
            'calc_dist': 'first',
            'calc_azimuth': 'first'
        }
        
        # --- NEU: Rette die Radius-Metriken vor dem Pandas Grouping-Löschvorgang ---
        if 'best_ref_sign' in df_plot.columns:
            spatial_agg['best_ref_sign'] = 'first'
            
        if is_sequential:
            # --- NEU: Time-Binning für gepaarte Micro-Mediane im Sequential TX Modus ---
            bin_minutes = st.session_state.get('val_tx_ab_bin_minutes', 8)
            df_plot['dt_time'] = pd.to_datetime(df_plot['time'])
            df_plot['time_bin'] = df_plot['dt_time'].dt.floor(f'{bin_minutes}min')

            df_t = df_plot[df_plot['is_me'] == 1].copy()
            df_r = df_plot[df_plot['is_me'] == 0].copy()

            # FIX: Konvertiere spatial_agg in strikte Named Aggregation Tuples für Pandas!
            spatial_agg_named = {k: (k, v) for k, v in spatial_agg.items()}

            # Micro-Medians per Bin berechnen (inklusive der spatial_agg Metadaten)
            bin_t = df_t.groupby(['time_bin'] + group_keys, dropna=False).agg(
                t_count=('stat_val', 'size'),
                t_med=('stat_val', 'median'),
                **spatial_agg_named
            ).reset_index()

            bin_r = df_r.groupby(['time_bin'] + group_keys, dropna=False).agg(
                r_count=('stat_val', 'size'),
                r_med=('stat_val', 'median')
            ).reset_index()

            # Merge der beiden Setups über Zeitfenster und Station
            df_bins = pd.merge(bin_t, bin_r, on=['time_bin'] + group_keys, how='outer')
            df_bins['t_count'] = df_bins['t_count'].fillna(0)
            df_bins['r_count'] = df_bins['r_count'].fillna(0)

            # Echte "Joint Bins" identifizieren
            df_bins['is_joint'] = (df_bins['t_count'] > 0) & (df_bins['r_count'] > 0)
            df_bins['bin_delta'] = df_bins['t_med'] - df_bins['r_med']

            df_joint = df_bins[df_bins['is_joint']]
            df_excl = df_bins[~df_bins['is_joint']]

            # FIX: Auch hier zwingend Tuples für die 'first' Aggregation verwenden
            spatial_agg_first = {k: (k, 'first') for k in spatial_agg.keys()}

            # 1. Aggregation der Joint Bins
            agg_joint = df_joint.groupby(group_keys, dropna=False).agg(
                joint_bins_count=('time_bin', 'size'),
                spot_count_u=('t_count', 'sum'),
                spot_count_r=('r_count', 'sum'),
                stat_val=('bin_delta', 'median'),
                w_target=('t_med', list), # Arrays für Wilcoxon
                w_ref=('r_med', list),
                **spatial_agg_first
            ).reset_index()
            agg_joint['spot_count'] = agg_joint['spot_count_u'] + agg_joint['spot_count_r']

            # 2. Aggregation der exklusiven Bins
            agg_excl = df_excl.groupby(group_keys, dropna=False).agg(
                count_only_u=('t_count', 'sum'),
                count_only_r=('r_count', 'sum'),
                **spatial_agg_first
            ).reset_index()

            # Merge zu finalem aggregierten DataFrame für die Stationen
            df_agg = pd.merge(agg_joint, agg_excl, on=group_keys, how='outer', suffixes=('', '_excl'))
            
            # Bereinigung der duplizierten Metadaten-Spalten
            for k in spatial_agg.keys():
                if f"{k}_excl" in df_agg.columns:
                    df_agg[k] = df_agg[k].fillna(df_agg[f"{k}_excl"])
                    df_agg = df_agg.drop(columns=[f"{k}_excl"])

            df_agg = df_agg.fillna({
                'joint_bins_count': 0, 'spot_count': 0, 'count_only_u': 0, 'count_only_r': 0
            })

            # Filter-Logik: Min. Joint Bins (nicht Raw Spots!) anwenden
            is_joint = df_agg['joint_bins_count'] >= min_s
            is_u = df_agg['count_only_u'] >= min_s
            is_r = df_agg['count_only_r'] >= min_s
            
            df_agg['stat_val'] = np.where(is_joint, df_agg['stat_val'], np.nan)
            df_agg['spot_count'] = np.where(is_joint, df_agg['spot_count'], 0)
            df_agg['count_only_u'] = np.where(is_u, df_agg['count_only_u'], 0)
            df_agg['count_only_r'] = np.where(is_r, df_agg['count_only_r'], 0)
            
        else:
            # 1. Datenvorbereitung: Vektorisiertes Markieren der Zugehörigkeit und Spot-Differenz
            df_plot['is_joint_spot'] = ((df_plot['has_u'] > 0) & (df_plot['has_r'] > 0)).astype(int)
            df_plot['is_u_spot'] = ((df_plot['has_u'] > 0) & (df_plot['has_r'] == 0)).astype(int)
            df_plot['is_r_spot'] = ((df_plot['has_u'] == 0) & (df_plot['has_r'] > 0)).astype(int)
            df_plot['spot_diff'] = np.where(df_plot['is_joint_spot'] == 1, df_plot['snr_u_norm'] - df_plot['snr_r_norm'], np.nan)
            
            # 2. C-optimierte Aggregation
            agg_ops = {
                'is_joint_spot': 'sum',
                'is_u_spot': 'sum',
                'is_r_spot': 'sum',
                'spot_diff': 'median',
                **spatial_agg
            }
            df_agg = df_plot.groupby(group_keys, dropna=False).agg(agg_ops).reset_index()
            
            # 3. Symmetrische Filter-Logik anwenden
            cnt_j = df_agg['is_joint_spot']
            cnt_u = df_agg['is_u_spot']
            cnt_r = df_agg['is_r_spot']
            
            is_joint = cnt_j >= min_s
            is_u = cnt_u >= min_s
            is_r = cnt_r >= min_s
            
            df_agg['spot_count'] = np.where(is_joint, cnt_j, 0)
            df_agg['count_only_u'] = np.where(is_u, cnt_u, 0)
            df_agg['count_only_r'] = np.where(is_r, cnt_r, 0)
            df_agg['stat_val'] = np.where(is_joint, df_agg['spot_diff'], np.nan)
            
            # 4. Temporäre Rechenspalten bereinigen
            df_agg = df_agg.drop(columns=['is_joint_spot', 'is_u_spot', 'is_r_spot', 'spot_diff'])

        # Radikale Bereinigung: Wirf jede Station weg, deren Zähler in ALLEN drei Kategorien auf 0 gefallen sind
        df_plot = df_agg[(df_agg['spot_count'] > 0) | (df_agg['count_only_u'] > 0) | (df_agg['count_only_r'] > 0)].copy()
        df_plot['stat_val'] = df_plot['stat_val'].round(1)
        
        def segment_agg(x):
            vals = x['stat_val'].dropna()
            cnt = x['peer_sign'].nunique()
            p_val = np.nan
            
            if len(vals) >= 5 and wilcox_level != "OFF":
                # Wilcoxon für gepaarte Micro-Mediane im sequenziellen Modus
                if is_sequential and 'w_target' in x.columns and 'w_ref' in x.columns:
                    from core.math_utils import calc_wilcoxon_from_paired_arrays
                    seg_w_t = [val for sublist in x['w_target'].dropna() for val in sublist]
                    seg_w_r = [val for sublist in x['w_ref'].dropna() for val in sublist]
                    p_val = calc_wilcoxon_from_paired_arrays(seg_w_t, seg_w_r)
                else:
                    # Wilcoxon für 1-Sample (bereits abgezogene Simultandaten)
                    try:
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore")
                            _, p_val = wilcoxon(vals - 0)
                    except ValueError: p_val = 1.0
                    
            return pd.Series({
                'val': vals.median() if len(vals) > 0 else np.nan,
                'cnt': cnt,
                'total_spots': x['spot_count'].sum(),
                'p_value': p_val
            })
            
        segs = df_plot.groupby(['SegmentID', 'dist_label', 'dir_name', 'r_min', 'r_max', 'az_bucket']).apply(segment_agg).reset_index()
        
        req_stations = base_min_stations
        if wilcox_level != "OFF":
            if wilcox_level == "80%": req_stations = max(req_stations, 5)
            elif wilcox_level == "90%": req_stations = max(req_stations, 5)
            elif wilcox_level == "95%": req_stations = max(req_stations, 6)
            elif wilcox_level == "99%": req_stations = max(req_stations, 8)
            
            target_p = 1.0
            if wilcox_level == "80%": target_p = 0.20
            elif wilcox_level == "90%": target_p = 0.10
            elif wilcox_level == "95%": target_p = 0.05
            elif wilcox_level == "99%": target_p = 0.01
            
            segs['conf_passed'] = segs['p_value'] <= target_p
            segs = segs[segs['conf_passed'] == True]
            
        segs = segs[segs['cnt'] >= req_stations]

    if df_plot.empty or segs.empty: return None

    # Plot Setup
    fig = plt.figure(figsize=FIG_SIZE, facecolor='black', dpi=PLOT_DPI)
    fig.text(TITLE_POS[0], TITLE_POS[1], title, fontsize=18, fontweight='bold', color='white', ha='center', va='top')
    
    perfect_globe = ccrs.Globe(semimajor_axis=EARTH_RADIUS_M, semiminor_axis=EARTH_RADIUS_M)
    proj = ccrs.AzimuthalEquidistant(central_longitude=lon_0, central_latitude=lat_0, globe=perfect_globe)
    pc_proj = ccrs.PlateCarree(globe=perfect_globe)
    
    ax = fig.add_axes(MAP_BBOX, projection=proj)
    ax.set_facecolor('black'); ax.set_global()
    
    lim = max_dist_km * 1000 
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
    
    theta = np.linspace(0, 2*np.pi, 100)
    center, radius = [0.5, 0.5], 0.5
    verts = np.vstack([np.sin(theta), np.cos(theta)]).T
    circle = mpath.Path(verts * radius + center)
    ax.set_boundary(circle, transform=ax.transAxes)
    
    ax.add_feature(cfeature.OCEAN, facecolor='#0d0d0d')
    ax.add_feature(cfeature.LAND, facecolor='#202020')
    ax.add_feature(cfeature.COASTLINE, linewidth=0.9, edgecolor='#999999', zorder=5, alpha=0.9)
    #slows down plotting - keep borders off for now
    ax.add_feature(cfeature.BORDERS, linewidth=0.6, edgecolor='#666666', zorder=5, alpha=0.7)
    
    # Draw Rings
    for r_km in THICK_RINGS:
        if r_km <= max_dist_km:
            lw = 1.8 if r_km == max_dist_km else 0.9
            ax.add_patch(plt.Circle((0,0), r_km*1000, fill=False, color='white', linewidth=lw, alpha=0.8, transform=proj, zorder=2))
            if r_km != 5000: ax.text(0, r_km*1000, f" {r_km} km ", color='#00ff00', fontsize=FONT_RINGS, fontweight='bold', ha='center', va='center', transform=proj, zorder=6, bbox=dict(facecolor='black', alpha=1.0, lw=0, pad=0.5))

    for r_km in THIN_RINGS:
        if r_km <= max_dist_km: ax.add_patch(plt.Circle((0,0), r_km*1000, fill=False, color='white', linewidth=0.5, alpha=0.3, linestyle='--', transform=proj, zorder=2))

    max_r_m = max_dist_km * 1000
    for az in np.arange(AZIMUTH_STEP / 2.0, 360, AZIMUTH_STEP): ax.plot([0, max_r_m * np.cos(np.radians(90 - az))], [0, max_r_m * np.sin(np.radians(90 - az))], color='#ffffff', linewidth=0.3, alpha=0.4, transform=proj, zorder=2)
    
    for i, d in enumerate(COMPASS):
        angle = i * AZIMUTH_STEP
        x = (max_r_m * COMPASS_LABEL_OFFSET) * np.cos(np.radians(90 - angle))
        y = (max_r_m * COMPASS_LABEL_OFFSET) * np.sin(np.radians(90 - angle))
        ax.text(x, y, d, color='#cccccc', ha='center', va='center', transform=proj, fontsize=FONT_COMPASS, fontweight='bold', alpha=0.9, clip_on=False)
    
    # Pole Markers
    dist_n_m = (90.0 - lat_0) * (np.pi / 180.0) * EARTH_RADIUS_M
    dist_s_m = (90.0 + lat_0) * (np.pi / 180.0) * EARTH_RADIUS_M
    
    if dist_n_m <= max_r_m:
        ax.plot(0, dist_n_m, marker='*', color='#00ff00', markersize=8, mew=1.2, transform=proj, zorder=20)
        ax.text(0, dist_n_m - 350000, 'N-POL', color='#00ff00', fontsize=FONT_POLES, fontweight='bold', ha='center', va='top', transform=proj, zorder=20)
        
    if dist_s_m <= max_r_m:
        ax.plot(0, -dist_s_m, marker='*', color='#00ff00', markersize=8, mew=1.2, transform=proj, zorder=20)
        ax.text(0, -dist_s_m - 350000, 'S-POL', color='#00ff00', fontsize=FONT_POLES, fontweight='bold', ha='center', va='top', transform=proj, zorder=20)

    # UI Texts
    t_lang = T[st.session_state.lang]
    target_call = st.session_state.val_callsign.upper()
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
        clrs = ['#030b2e', '#0a318f', '#2270c1', '#6eb2e4', '#ffffff', '#fca083', '#f03b20', '#a50f15', '#400005']
        bnds = [-27, -21, -15, -9, -3, 3, 9, 15, 21, 27]
        lbls = ['-4S', '-3S', '-2S', '-1S', '±0', '+1S', '+2S', '+3S', '+4S']
        ticks = [-24, -18, -12, -6, 0, 6, 12, 18, 24]
        cbar_title = t_lang["cbar_comp"]
    else:
        clrs = ['#190824', '#4662d7', '#36aaf9', '#1ae4b6', '#72fe5e', '#c9ef34', '#faba39', '#f66b19', '#cb2a04', '#590202']
        bnds = np.arange(-48, 18, 6)
        lbls = [f"{b}dB" for b in bnds]
        ticks = bnds
        cbar_title = t_lang["cbar_abs"]
    
    cmap = mpl.colors.ListedColormap(clrs); norm = mpl.colors.BoundaryNorm(bnds, cmap.N)
    
    # Draw Heatmap Wedges
    patches = []
    for _, r in segs.iterrows():
        if r['r_min'] < max_dist_km:
            center_az = r['az_bucket'] * AZIMUTH_STEP
            az_min = center_az - (AZIMUTH_STEP / 2.0)
            az_max = center_az + (AZIMUTH_STEP / 2.0)
            theta1 = 90 - az_max
            theta2 = 90 - az_min
            patches.append(Wedge((0,0), min(r['r_max'], max_dist_km)*1000, theta1, theta2, width=(min(r['r_max'], max_dist_km)-r['r_min'])*1000))
            
    p = PatchCollection(patches, cmap=cmap, norm=norm, alpha=0.75, edgecolor='none', transform=proj, zorder=3)
    p.set_array(segs['val']); ax.add_collection(p)
    
    lbl_both_async = t_lang.get('leg_both_async', 'Both (Async)')

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
        if not df_only_r.empty: ax.scatter(df_only_r['peer_lon'], df_only_r['peer_lat'], c=COLOR_ONLY_REF, s=8, alpha=1.0, edgecolors='black', linewidth=0.35, transform=pc_proj, zorder=8, label=lbl_only_ref)
        leg = ax.legend(loc='lower center', bbox_to_anchor=LEG_BBOX, facecolor='#121212', edgecolor='#444444', labelcolor='white', fontsize=FONT_LEGEND, markerscale=2.0)        
        leg.set_zorder(15)
    else:
        ax.scatter(df_plot['peer_lon'], df_plot['peer_lat'], c=COLOR_ONLY_ME, s=5, alpha=1.0, edgecolors='black', linewidth=0.35, transform=pc_proj, zorder=10, label=lbl_only_me)

    # Colorbar
    cax = fig.add_axes(CBAR_BBOX)
    cbar = plt.colorbar(p, cax=cax, ticks=ticks)
    cbar.ax.set_yticklabels(lbls, color='white')
    cbar.ax.tick_params(labelsize=FONT_CBAR) 
    cbar.set_label(cbar_title, color='white', fontweight='bold', labelpad=15, fontsize=FONT_LEGEND)
    
    # Meta Footer
    lbl_time = "Zeitraum" if st.session_state.lang == "de" else "Time"
    t_time = f"{start_t.strftime('%d-%b-%Y')} - {end_t.strftime('%d-%b-%Y')}"
    t_band = st.session_state.val_band
    t_solar = st.session_state.val_solar.split(" ")[0]

    meta_parts = [f"{lbl_time}: {t_time}", f"Band: {t_band}", f"Solar: {t_solar}"]
    
    if is_compare:
        if is_sequential: meta_parts.append("Sync: Sequential A/B")
        elif wilcox_level != "OFF": meta_parts.append(f"Stations/Seg: Wilcoxon ({wilcox_level})")
        else:
            meta_parts.append(f"Spots/Station: ≥{st.session_state.val_min_spots}")
            meta_parts.append(f"Stations/Seg: ≥{base_min_stations}")
            
        if st.session_state.val_comp_mode == t_lang["opt_comp_radius"]:
            local_mode = st.session_state.get('val_local_benchmark', t_lang.get('opt_local_best', 'Local Best Station'))
            ref_radius = st.session_state.get('val_ref_radius_km', 250)
            meta_parts.append(f"Ref: {local_mode} (≤{ref_radius} km)")
        elif st.session_state.val_comp_mode == t_lang["opt_comp_self"]:
            meta_parts.append(f"Ref: Self-Test Config")
        else: meta_parts.append(f"Ref: {st.session_state.val_ref_callsign.upper()}")
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
        
        # Filter dataframe strictly to the rendered map bounds to match the Segment Inspector
        df_footer = df_plot[df_plot['r_min'] < max_dist_km]
        
        # 1. Metriken extrahieren (Spots & Stations) für 4 Segmente
        # Da die Pandas-Aggregation nun in allen Modi "spot_count" (Joint) und "count_only_*" (Exklusiv) sauber trennt, 
        # nutzen wir eine universelle Logik für Simultan und Sequenziell:
        stat_joint = len(df_footer[df_footer['spot_count'] > 0])
        stat_both_async = len(df_footer[(df_footer['spot_count'] == 0) & (df_footer['count_only_u'] > 0) & (df_footer['count_only_r'] > 0)])
        stat_only_u = len(df_footer[(df_footer['spot_count'] == 0) & (df_footer['count_only_u'] > 0) & (df_footer['count_only_r'] == 0)])
        stat_only_r = len(df_footer[(df_footer['spot_count'] == 0) & (df_footer['count_only_u'] == 0) & (df_footer['count_only_r'] > 0)])
        
        spot_joint = int(df_footer['spot_count'].sum())
        spot_both_async = int(df_footer[(df_footer['spot_count'] == 0) & (df_footer['count_only_u'] > 0) & (df_footer['count_only_r'] > 0)][['count_only_u', 'count_only_r']].sum().sum())
        # Auch die Rest-Spots (Async) der Joint-Stationen zum "Both-Async" Topf hinzufügen
        spot_both_async += int(df_footer[df_footer['spot_count'] > 0][['count_only_u', 'count_only_r']].sum().sum())
        spot_only_u = int(df_footer[(df_footer['spot_count'] == 0) & (df_footer['count_only_u'] > 0) & (df_footer['count_only_r'] == 0)]['count_only_u'].sum())
        spot_only_r = int(df_footer[(df_footer['spot_count'] == 0) & (df_footer['count_only_u'] == 0) & (df_footer['count_only_r'] > 0)]['count_only_r'].sum())

        tot_stats = stat_only_u + stat_joint + stat_both_async + stat_only_r
        tot_spots = spot_only_u + spot_joint + spot_both_async + spot_only_r

        # 2. Native Categorical Axes setup
        ax_bars = fig.add_axes([0.12, 0.035, 0.85, 0.045])
        ax_bars.set_facecolor('black')
        for spine in ax_bars.spines.values(): spine.set_visible(False)
        ax_bars.set_xticks([])
        ax_bars.tick_params(axis='y', length=0, pad=10, colors='#cccccc', labelsize=FONT_LEGEND)
        
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
        p4 = ax_bars.barh(categories, [pct_r_stat, pct_r_spot if not is_radius_mode else 0], left=[pct_u_stat+pct_j_stat+pct_a_stat, pct_u_spot+pct_j_spot+pct_a_spot if not is_radius_mode else 0], color=COLOR_ONLY_REF, height=0.6)
        
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
        fig.text(0.50, 0.01, line1_str, color='#888888', ha='center', fontsize=FONT_FOOTER)
        
    else:
        # Fallback für Absolute Maps
        fig.text(0.50, 0.02, line1_str, color='#cccccc', ha='center', fontsize=FONT_FOOTER)

    return fig, df_plot, segs, line1_str
