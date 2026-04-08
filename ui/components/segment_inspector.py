"""
Segment Inspector & Results Components Module.
Contains the interactive drill-down UI (histograms, data tables) and 
the high-resolution map download button. Isolated as Streamlit fragments 
to allow UI updates without triggering full-page reruns.
"""

import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import cartopy.feature as cfeature
import streamlit as st
from config import COMPASS

@st.fragment
def render_segment_inspector(analysis_id, title, is_compare, is_sequential, enriched_df, segs_df, parquet_path, line1_str, t, max_dist_km):
    """
    Renders the interactive Segment Inspector directly below the map.
    Allows drill-down into specific Azimuth/Distance chunks to show histograms and tabular data.
    Runs as an independent Streamlit fragment to prevent full-page reruns on interaction.
    """
    run_id = st.session_state.get("run_id", 0)
    
    # Extract valid distance segments based on user's max_dist setting
    valid_distances = sorted([d for d in segs_df['dist_label'].dropna().unique()], key=lambda x: int(x.strip('[]km').split('-')[0]))
    filtered_distances = [d for d in valid_distances if int(d.strip('[]km').split('-')[0]) < max_dist_km]
    
    lbl_dist = t.get("opt_insp_dist", "---")
    lbl_dir = t.get("opt_insp_dir", "---")
    opt_full = t.get("opt_full_range", "Full Range")
    opt_all_dir = t.get("opt_all_dirs", "All Directions")
    
    # Render Dropdowns
    col_insp1, col_insp2 = st.columns(2)
    with col_insp1: 
        sel_dist = st.selectbox("Distance", [lbl_dist] + filtered_distances + [opt_full], key=f"dist_{analysis_id}_{run_id}", label_visibility="collapsed")
    with col_insp2:
        if sel_dist != lbl_dist:
            if sel_dist == opt_full: 
                valid_dirs = sorted([d for d in segs_df['dir_name'].dropna().unique() if d in COMPASS], key=lambda x: COMPASS.index(x))
            else: 
                valid_dirs = sorted([d for d in segs_df[segs_df['dist_label'] == sel_dist]['dir_name'].dropna().unique() if d in COMPASS], key=lambda x: COMPASS.index(x))
            
            if not valid_dirs: valid_dirs = [t.get("opt_no_station", "No Stations")]
            if valid_dirs != [t.get("opt_no_station", "No Stations")]: 
                sel_dir = st.selectbox("Direction", [lbl_dir] + valid_dirs + [opt_all_dir], key=f"dir_{analysis_id}_{run_id}", label_visibility="collapsed")
            else: 
                sel_dir = st.selectbox("Direction", [lbl_dir] + valid_dirs, key=f"dir_{analysis_id}_{run_id}", disabled=True, label_visibility="collapsed")
        else: 
            sel_dir = st.selectbox("Direction", [lbl_dir], key=f"dir_{analysis_id}_{run_id}", disabled=True, label_visibility="collapsed")

    # If user selected a valid segment, process the inspection data
    if sel_dist != lbl_dist and sel_dir != lbl_dir and sel_dir != t.get("opt_no_station", "No Stations"):
        selected_seg = f"{sel_dist if sel_dist != opt_full else t['opt_full_range']} | {sel_dir if sel_dir != opt_all_dir else t['opt_all_dirs']}"
        df_seg = enriched_df[enriched_df['SegmentID'] != "Out of Bounds"].copy()
        
        # Apply user filters
        if sel_dist != opt_full: df_seg = df_seg[df_seg['dist_label'] == sel_dist]
        if sel_dir != opt_all_dir: df_seg = df_seg[df_seg['dir_name'] == sel_dir]
            
        vals = df_seg['stat_val'].dropna()
        target_call = st.session_state.val_callsign.upper()
        
        # Setup specific labels based on the active test mode (Self vs Compare)
        if st.session_state.val_comp_mode == t["opt_comp_self"]:
            if st.session_state.val_self_test_mode == t["opt_self_rx"]:
                lbl_only_me = t['leg_only_me'].format(callsign=target_call)
                lbl_only_ref = t['leg_only_ref'].format(ref_callsign=st.session_state.val_self_call_b.upper())
                ref_header = st.session_state.val_self_call_b.upper()
                col_u_name = target_call
            else:
                lbl_only_me = t['leg_only_me'].format(callsign="Setup A")
                lbl_only_ref = t['leg_only_ref'].format(ref_callsign="Setup B")
                ref_header = "Setup B"
                col_u_name = "Setup A"
        else:
            lbl_only_me = t['leg_only_me'].format(callsign=target_call)
            col_u_name = target_call
            if st.session_state.val_comp_mode == t["opt_comp_radius"]: 
                lbl_only_ref = t['leg_only_ref_radius']
                ref_header = "Best Ref"
            else: 
                lbl_only_ref = t['leg_only_ref'].format(ref_callsign=st.session_state.val_ref_callsign.upper())
                ref_header = st.session_state.val_ref_callsign.upper()

        remote_str = t['txt_rx_stations'] if analysis_id.startswith("TX") else t['txt_tx_stations']
        
        # Build the sub-footer info string detailing decode counts
        if is_compare and 'count_only_u' in df_seg.columns:
            if is_sequential:
                seg_line2 = f"Both (Async): {len(df_seg[(df_seg['count_only_u']>0) & (df_seg['count_only_r']>0)])}  |  {lbl_only_me}: {int(df_seg['count_only_u'].sum())}  |  {lbl_only_ref}: {int(df_seg['count_only_r'].sum())}  |  {t['txt_remote']} {remote_str}: {len(df_seg)}"
            else:
                seg_joint = df_seg[df_seg['spot_count'] > 0]
                seg_line2 = f"{t['txt_joint_decodes']}: {int(df_seg['spot_count'].sum())}  |  {lbl_only_me}: {int(df_seg['count_only_u'].sum())}  |  {lbl_only_ref}: {int(df_seg['count_only_r'].sum())}  |  {t['txt_joint']} {remote_str}: {len(seg_joint)}  |  {t['txt_remote']} {remote_str}: {len(df_seg)}"
        else:
            seg_line2 = f"{t['txt_total_decodes']}: {int(df_seg['spot_count'].sum())}  |  {t['txt_remote']} {remote_str}: {len(df_seg)}"

        # ----------------------------------------------------
        # Render Histogram & Yield Chart
        # ----------------------------------------------------
        has_plot_data = False
        if not vals.empty: 
            has_plot_data = True
        elif is_compare and 'count_only_u' in df_seg.columns and (df_seg['count_only_u'].sum() > 0 or df_seg['count_only_r'].sum() > 0): 
            has_plot_data = True

        if has_plot_data:
            fig_hist = plt.figure(figsize=(12, 4.5), facecolor='black')
            
            # Setup Layout based on Absolute vs. Compare Mode
            if is_compare and 'count_only_u' in df_seg.columns:
                fig_hist.subplots_adjust(left=0.05, right=0.95, bottom=0.25, top=0.80, wspace=0.3)
                gs = fig_hist.add_gridspec(1, 3)
                ax_yield = fig_hist.add_subplot(gs[0, 0])
                ax_hist = fig_hist.add_subplot(gs[0, 1:])
                
                # 1. Setup Yield Bar Chart (Left)
                ax_yield.set_facecolor('black')
                ax_yield.tick_params(axis='y', colors='white')
                ax_yield.tick_params(axis='x', colors='white', labelrotation=20, labelsize=9)
                for spine in ax_yield.spines.values(): spine.set_color('#444444')
                
                # System Sensitivity (Yield) counts unique STATIONS, not spots
                if is_sequential:
                    cnt_shared = len(df_seg[(df_seg['count_only_u'] > 0) & (df_seg['count_only_r'] > 0)])
                    cnt_u = len(df_seg[(df_seg['count_only_u'] > 0) & (df_seg['count_only_r'] == 0)])
                    cnt_r = len(df_seg[(df_seg['count_only_u'] == 0) & (df_seg['count_only_r'] > 0)])
                    
                    yield_counts = [cnt_u, cnt_shared, cnt_r]
                    yield_labels = [col_u_name, "Async Both", ref_header]
                else:
                    # Simultane Vergleiche: Dynamische Balken
                    cnt_joint = len(df_seg[df_seg['spot_count'] > 0])
                    cnt_async = len(df_seg[(df_seg['spot_count'] == 0) & (df_seg['count_only_u'] > 0) & (df_seg['count_only_r'] > 0)])
                    cnt_u = len(df_seg[(df_seg['spot_count'] == 0) & (df_seg['count_only_u'] > 0) & (df_seg['count_only_r'] == 0)])
                    cnt_r = len(df_seg[(df_seg['spot_count'] == 0) & (df_seg['count_only_u'] == 0) & (df_seg['count_only_r'] > 0)])
                    
                    # Async-Balken nur rendern, wenn es diese physikalische Ausnahme wirklich gab
                    if cnt_async > 0:
                        yield_counts = [cnt_u, cnt_joint, cnt_async, cnt_r]
                        yield_labels = [col_u_name, "Joint", "Async Both", ref_header]
                    else:
                        yield_counts = [cnt_u, cnt_joint, cnt_r]
                        yield_labels = [col_u_name, "Joint", ref_header]
                
                bar_colors = ["#36aaf9"] * len(yield_counts)
                
                bars = ax_yield.bar(yield_labels, yield_counts, color=bar_colors, alpha=0.8, edgecolor='black')
                ax_yield.set_ylabel(t["lbl_hist_count"], color='white')
                ax_yield.set_title("System Sensitivity (Yield)", color='white', fontweight='bold', pad=10)
                
                # Add percentages on top of the bars
                total_yield = sum(yield_counts)
                if total_yield > 0:
                    for bar in bars:
                        height = bar.get_height()
                        ax_yield.text(bar.get_x() + bar.get_width()/2., height + (max(yield_counts)*0.02),
                                f'{(height/total_yield)*100:.1f}%',
                                ha='center', va='bottom', color='white', fontsize=10, fontweight='bold')
                
                # Adjust Titles for Dual Plot
                ax_hist.set_title("Hardware Linearity (Δ SNR)", color='white', fontweight='bold', pad=10)
                fig_hist.suptitle(f"{title} - {selected_seg}", color='white', fontweight='bold', fontsize=14, y=0.98)
                
            else:
                # Fallback for Absolute Mode (Single Plot)
                fig_hist.subplots_adjust(left=0.05, right=0.85, bottom=0.25, top=0.85)
                ax_hist = fig_hist.add_subplot(1,1,1)
                ax_hist.set_title(f"{title} - {selected_seg}", color='white', fontweight='bold', pad=15)

            # 2. Common Histogram Setup (Right / Full)
            ax_hist.set_facecolor('black')
            ax_hist.tick_params(colors='white')
            for spine in ax_hist.spines.values(): spine.set_color('#444444')
            
            if not vals.empty:
                med = vals.median()
                val_counts = vals.value_counts().sort_index()
                ax_hist.bar(val_counts.index, val_counts.values, width=0.4, align='center', color='#36aaf9', alpha=0.8, edgecolor='black')
                
                if (vals.max() - vals.min()) <= 30:
                    ticks = np.arange(np.floor(vals.min()), np.ceil(vals.max()) + 1, 1.0)
                    ax_hist.set_xticks(ticks)
                    
                ax_hist.yaxis.set_major_locator(mpl.ticker.MaxNLocator(integer=True))
                ax_hist.axvline(med, color='red', linestyle='dashed', linewidth=2, label=t["lbl_med_seg"].format(med=med))
                ax_hist.legend(facecolor='#121212', edgecolor='#444444', labelcolor='white')
            else:
                # Handle edge case: We have exclusive yield data, but exactly 0 joint spots
                ax_hist.text(0.5, 0.5, t["lbl_no_joint"], color='white', ha='center', va='center', fontsize=12)
                ax_hist.set_xticks([])
                ax_hist.set_yticks([])
                
            station_type = t['tbl_col_rx'] if analysis_id.startswith("TX") else t['tbl_col_tx']
            if not is_compare: 
                ax_hist.set_xlabel(t["lbl_hist_x_abs"].format(station_type=station_type), color='white')
                ax_hist.set_ylabel(t["lbl_hist_count"], color='white')
            else: 
                ax_hist.set_xlabel(t["lbl_hist_x_comp"].format(station_type=station_type), color='white')
                ax_hist.set_ylabel("Joint Spots", color='white')
            
            # 3. Add Common Footer Text
            # Footer distorts the size of the histogram. We don't need it right now. Keep it off. Commented out. 
            # fig_hist.text(0.05, 0.02, f"{line1_str}\n{seg_line2}", fontsize=11, color='#cccccc', ha='left', va='bottom', linespacing=1.6)
            
            # Richtiges Streamlit-Parameter für volle Breite
            st.pyplot(fig_hist, width='stretch')
            plt.close(fig_hist)
        else:
            st.info(t["lbl_no_joint"], icon="ℹ️")
            st.markdown(f"<div style='font-size:11px; color:#ccc; margin-bottom:1rem; font-family:monospace;'>{line1_str}<br>{seg_line2}</div>", unsafe_allow_html=True)

        # --- 1. Layout-Spalten definieren ---
        # 3 Spalten: 50% für Titel, 30% für Toggle, 20% für Filter-Button
        col_ins1, col_ins2, col_ins3 = st.columns([0.6, 0.3, 0.3], vertical_alignment="center")
        
        with col_ins1:
            # Platzsparende, zweisprachige Kurzform für den Subtitel
            sub_text = " (Norm. @ 1W. Details per Klick)" if st.session_state.lang == "de" else " (Norm. @ 1W. Click for details)"
            st.markdown(f"**{t['lbl_insights']}**<span style='font-size:0.85em; color:gray;'>{sub_text}</span>", unsafe_allow_html=True)
            
        with col_ins2:
            show_non_joint = False
            if is_compare:
                default_state = True if is_sequential else False
                # Gekürzter Text: "Show Non-Joint"
                show_non_joint = st.toggle("Show Non-Joint", value=default_state, key=f"tgl_{analysis_id}_{run_id}_{selected_seg}")

        station_col = t['tbl_col_rx'] if analysis_id.startswith("TX") else t['tbl_col_tx']
        
        # ----------------------------------------------------
        # Render Interactive Master Table
        # ----------------------------------------------------
        if not is_compare:
            disp_df = df_seg[['peer_sign', 'peer_grid', 'calc_dist', 'calc_azimuth', 'spot_count', 'stat_val']].copy()
            disp_df.columns = [station_col, t['tbl_col_loc'], t['tbl_col_km'], t['tbl_col_az'], t['tbl_col_spots'], t['tbl_col_med_snr']]
        else:
            disp_df = df_seg[['peer_sign', 'peer_grid', 'calc_dist', 'calc_azimuth', 'spot_count', 'count_only_u', 'count_only_r', 'stat_val']].copy()
            disp_df.columns = [station_col, t['tbl_col_loc'], t['tbl_col_km'], t['tbl_col_az'], t['tbl_col_joint'], t['tbl_col_only_u'].format(callsign=col_u_name), lbl_only_ref, t['tbl_col_med_delta']]
        
        km_col = t['tbl_col_km']
        az_col = t['tbl_col_az']
        disp_df[km_col] = disp_df[km_col].round(0).astype(int)
        disp_df[az_col] = disp_df[az_col].round(1)
        
        # Verstecke Reihen mit 0 Joint Spots, es sei denn der Raw-Schalter ist an
        col_joint_name = t.get('tbl_col_joint', 'Joint')
        if is_compare and not show_non_joint and col_joint_name in disp_df.columns:
            disp_df = disp_df[disp_df[col_joint_name] > 0]

        sorted_disp_df = disp_df.sort_values(by=disp_df.columns[-1], ascending=False, na_position='last').reset_index(drop=True)

        # --- DYNAMIC EXCEL-STYLE FILTER ---
        # Da wir sorted_disp_df jetzt vorbereitet haben, springen wir zurück in Spalte 3 für den Button
        with col_ins3:
            # Dezenter Button mit nativem Material-Design Trichter-Icon!
            with st.popover("Filter", icon=":material/filter_alt:", use_container_width=True):
                st.markdown("**Filter column(s):**")
                filter_cols = st.multiselect("Select Columns", sorted_disp_df.columns, label_visibility="collapsed")
                
                for col in filter_cols:
                    if pd.api.types.is_numeric_dtype(sorted_disp_df[col]):
                        min_val = float(sorted_disp_df[col].min())
                        max_val = float(sorted_disp_df[col].max())
                        if min_val < max_val:
                            step = 1.0 if pd.api.types.is_integer_dtype(sorted_disp_df[col]) else 0.1
                            sel_range = st.slider(f"{col}", min_val, max_val, (min_val, max_val), step=step)
                            sorted_disp_df = sorted_disp_df[(sorted_disp_df[col] >= sel_range[0]) & (sorted_disp_df[col] <= sel_range[1])]
                    else:
                        unique_vals = sorted_disp_df[col].dropna().unique()
                        sel_vals = st.multiselect(f"{col}", unique_vals, default=[])
                        if sel_vals:
                            sorted_disp_df = sorted_disp_df[sorted_disp_df[col].isin(sel_vals)]

        # --- END FILTER ---

        # Die Tabelle rendert nun den gefilterten Zustand
        tbl_event = st.dataframe(sorted_disp_df, width='stretch', hide_index=True, selection_mode="multi-row", on_select="rerun", key=f"tbl_{analysis_id}_{run_id}_{selected_seg}")

        # ----------------------------------------------------
        # Render Raw Drill-Down Data (if user clicks a row)
        # ----------------------------------------------------
        sel_rows = tbl_event.selection.rows
        if sel_rows:
            sel_stations = sorted_disp_df.iloc[sel_rows][station_col].tolist()
            
            # Titel vorbereiten (wird erst unten im Layout gerendert)
            if len(sel_rows) == 1: 
                drill_title = t['lbl_drill_single'].format(station=sel_stations[0])
            else: 
                drill_title = t['lbl_drill_multi'].format(count=len(sel_rows))
                
            try:
                # Load the raw spots straight from the parquet cache for blazing fast drill-downs
                station_df = pd.read_parquet(parquet_path, filters=[('peer_sign', 'in', sel_stations)])
                
                # Merge logic to append calculated distance and azimuth from the aggregated dataframe to the raw spots
                meta_df = sorted_disp_df[[station_col, t['tbl_col_loc'], t['tbl_col_km'], t['tbl_col_az']]]
                station_df = station_df.merge(meta_df, left_on='peer_sign', right_on=station_col, how='inner')
                
                drill_df = None
                info_msg = None
                
                if not is_compare:
                    station_df['Date/Time (UTC)'] = pd.to_datetime(station_df['time']).dt.strftime('%d-%b-%Y %H:%M:%S')
                    drill_df = station_df[['Date/Time (UTC)', station_col, t['tbl_col_loc'], t['tbl_col_km'], t['tbl_col_az'], 'snr', 'power', 'stat_val']].copy()
                    drill_df.columns = ['Date/Time (UTC)', station_col, t['tbl_col_loc'], t['tbl_col_km'], t['tbl_col_az'], 'SNR (Raw)', 'TX Power (dBm)', 'Norm@1W']
                    
                else:
                    if is_sequential:
                        joint_df = station_df.copy()
                        if not joint_df.empty:
                            joint_df['Date/Time (UTC)'] = pd.to_datetime(joint_df['time']).dt.strftime('%d-%b-%Y %H:%M:%S')
                            col_u = f'{col_u_name} SNR (dB)'
                            col_r = f'{ref_header} SNR (dB)'
                            joint_df[col_u] = np.where(joint_df['is_me'] == 1, joint_df['stat_val'], np.nan)
                            joint_df[col_r] = np.where(joint_df['is_me'] == 0, joint_df['stat_val'], np.nan)
                            
                            # Keine Deltas für asynchrone Einzel-Spots berechnen, da sie in der Zeit nicht matchen
                            col_delta_lbl = "Δ SNR (Async)"
                            joint_df[col_delta_lbl] = np.nan
                            
                            drill_df = joint_df[['Date/Time (UTC)', station_col, t['tbl_col_loc'], t['tbl_col_km'], t['tbl_col_az'], col_u, col_r, col_delta_lbl]].copy()
                        else: 
                            info_msg = "No spots available for the selected station(s)."
                    else:
                        # Für Simultane Vergleiche: Umschaltbar zwischen Joint Spots und Non-Joint (Raw) Spots
                        if show_non_joint:
                            joint_df = station_df.copy()
                        else:
                            joint_df = station_df[(station_df['has_u'] > 0) & (station_df['has_r'] > 0)].copy()

                        if not joint_df.empty:
                            joint_df['Date/Time (UTC)'] = pd.to_datetime(joint_df['time_slot'] * 120, unit='s').dt.strftime('%d-%b-%Y %H:%M:%S')
                            
                            # ClickHouse gibt 0.0 zurück, wenn maxIf() nichts findet. Wir setzen das explizit auf NaN anhand der countIf() Metriken (has_u / has_r)
                            joint_df.loc[joint_df['has_u'] == 0, 'snr_u_norm'] = np.nan
                            joint_df.loc[joint_df['has_r'] == 0, 'snr_r_norm'] = np.nan
                            
                            # Delta nur berechnen, wenn BEIDE Seiten existieren
                            joint_df['Δ SNR (dB)'] = np.where((joint_df['has_u'] > 0) & (joint_df['has_r'] > 0), (joint_df['snr_u_norm'] - joint_df['snr_r_norm']).round(1), np.nan)
                            
                            col_u = f'{col_u_name} SNR (dB)'
                            col_r = f'{ref_header} SNR (dB)'
                            col_delta_lbl = "Δ SNR (dB)"
                            station_type = 'RX Station' if analysis_id.startswith("TX") else 'TX Station'
                            
                            # 1. Werte für fehlenden Empfang auf Text "None" umstellen (damit es nicht wie 0 dB wirkt)
                            joint_df['snr_u_norm'] = joint_df['snr_u_norm'].astype(object).fillna("None")
                            joint_df['snr_r_norm'] = joint_df['snr_r_norm'].astype(object).fillna("None")
                            joint_df['Δ SNR (dB)'] = joint_df['Δ SNR (dB)'].astype(object).fillna("None")
                            
                            if 'best_ref_sign' in joint_df.columns:
                                # 2. Auch leere "Best Ref" Felder mit "None" auffüllen
                                joint_df['best_ref_sign'] = joint_df['best_ref_sign'].fillna("None")
                                # Runden auf ganze Zahlen (round(0)), damit der Int64-Cast bei Kommazahlen nicht crasht
                                joint_df['best_ref_dist_km'] = (joint_df['best_ref_dist'] / 1000).round(0).astype('Int64')
                                
                                # 3. Swap der SNR-Spalten (zuerst snr_r_norm, dann snr_u_norm)
                                drill_df = joint_df[['Date/Time (UTC)', station_col, t['tbl_col_loc'], t['tbl_col_km'], t['tbl_col_az'], 'best_ref_sign', 'best_ref_dist_km', 'snr_r_norm', 'snr_u_norm', 'Δ SNR (dB)']].copy()
                                drill_df.columns = ['Date/Time (UTC)', station_type, t['tbl_col_loc'], t['tbl_col_km'], t['tbl_col_az'], 'Best Ref', 'Ref km', col_r, col_u, col_delta_lbl]
                            else:
                                # Swap der SNR-Spalten (zuerst snr_r_norm, dann snr_u_norm)
                                drill_df = joint_df[['Date/Time (UTC)', station_col, t['tbl_col_loc'], t['tbl_col_km'], t['tbl_col_az'], 'snr_r_norm', 'snr_u_norm', 'Δ SNR (dB)']].copy()
                                drill_df.columns = ['Date/Time (UTC)', station_type, t['tbl_col_loc'], t['tbl_col_km'], t['tbl_col_az'], col_r, col_u, col_delta_lbl]
                        else: 
                            info_msg = "No spots available." if show_non_joint else "No joint spots available for the selected station(s)."
                
                # --- LAYOUT, FILTER & RENDERING FÜR DRILL-DOWN ---
                if info_msg:
                    st.info(info_msg, icon="ℹ️")
                elif drill_df is not None and not drill_df.empty:
                    # Spalten-Layout ähnlich der Master-Tabelle (Titel links, Filter rechts)
                    col_d1, col_d2 = st.columns([0.7, 0.3], vertical_alignment="center")
                    
                    with col_d1:
                        st.markdown(drill_title)
                        
                    with col_d2:
                        with st.popover("Filter", icon=":material/filter_alt:", use_container_width=True):
                            st.markdown("**Filter column(s):**")
                            # Eigene Keys generieren, da diese Checkboxen unabhängig von der Master-Tabelle sind
                            d_filter_cols = st.multiselect("Select Columns", drill_df.columns, label_visibility="collapsed", key=f"d_flt_{analysis_id}_{run_id}_{selected_seg}")
                            
                            for col in d_filter_cols:
                                if pd.api.types.is_numeric_dtype(drill_df[col]):
                                    min_val = float(drill_df[col].min())
                                    max_val = float(drill_df[col].max())
                                    if min_val < max_val:
                                        step = 1.0 if pd.api.types.is_integer_dtype(drill_df[col]) else 0.1
                                        sel_range = st.slider(f"{col}", min_val, max_val, (min_val, max_val), step=step, key=f"d_sld_{col}_{analysis_id}_{run_id}_{selected_seg}")
                                        drill_df = drill_df[(drill_df[col] >= sel_range[0]) & (drill_df[col] <= sel_range[1])]
                                else:
                                    # Alles in String casten, um Typen-Konflikte (z.B. bei Mix aus Floats und dem Wort "None") zu vermeiden
                                    unique_vals = drill_df[col].astype(str).dropna().unique()
                                    sel_vals = st.multiselect(f"{col}", unique_vals, default=[], key=f"d_ms_{col}_{analysis_id}_{run_id}_{selected_seg}")
                                    if sel_vals:
                                        drill_df = drill_df[drill_df[col].astype(str).isin(sel_vals)]

                    st.dataframe(drill_df, width='stretch', hide_index=True)

            except FileNotFoundError: 
                st.warning("Cache file expired. Please Run Analysis again.")

@st.fragment
def render_lazy_download(analysis_id, fig, callsign, t):
    """
    Renders a subtle 'Render High-Res Map' button that dynamically generates
    a 300 DPI PNG map for download upon user request without blocking the main UI layout.
    """
    run_id = st.session_state.get("run_id", 0)
    buf_key = f"img_buf_{analysis_id}_{run_id}"
    
    if buf_key in st.session_state:
        st.download_button("💾 Download", data=st.session_state[buf_key], file_name=f"WSPR_Map_{analysis_id}_{callsign}.png", mime="image/png", type="tertiary", width='stretch', key=f"dl_{analysis_id}_{run_id}")
    else:
        if st.button("Render High-Res Map ⚙️", key=f"prep_{analysis_id}_{run_id}", type="tertiary", width='stretch'):
            with st.spinner("⏳"):
                if fig.axes:
                    ax = fig.axes[0]
                    # Apply country borders explicitly for the high-res export
                    ax.add_feature(cfeature.BORDERS, linewidth=0.6, edgecolor="#414040", zorder=5, alpha=0.5)
                img_buf = io.BytesIO()
                fig.savefig(img_buf, format="png", dpi=300, facecolor='black', edgecolor='none')
                st.session_state[buf_key] = img_buf.getvalue()
            st.rerun(scope="fragment")