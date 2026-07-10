"""Drill-down table builders for Segment Inspector and export packaging."""

import ast

import numpy as np
import pandas as pd
from core.artifact_store import read_parquet_artifact
from core.opportunity_engine import opportunity_utc_from_time_slot
from i18n import absolute_terms

def _unique_station_order(stations):
    """Return station labels once, preserving the table selection order."""
    return list(dict.fromkeys([str(s) for s in stations if pd.notna(s)]))

def _parse_ref_detail_rows(value):
    """Parse ClickHouse Array(Tuple(...)) CSV output for Local Median drill-down display."""
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        raw_rows = value
    else:
        text = str(value).strip()
        if not text or text.lower() in {"nan", "none", "null"}:
            return []
        try:
            raw_rows = ast.literal_eval(text)
        except (SyntaxError, ValueError):
            return []

    parsed_rows = []
    for row in raw_rows:
        if isinstance(row, (list, tuple)) and len(row) >= 4:
            parsed_rows.append({
                "ref_sign": row[0],
                "ref_grid": row[1],
                "ref_dist": row[2],
                "ref_snr": row[3]
            })
    return parsed_rows

def _sort_drilldown_default(drill_df):
    """Sort drill-down rows by UTC timestamp, then station label when available."""
    if drill_df is None or drill_df.empty or "Date/Time (UTC)" not in drill_df.columns:
        return drill_df

    sort_df = drill_df.copy()
    sort_df["_sort_time"] = pd.to_datetime(sort_df["Date/Time (UTC)"], format="%d-%b-%Y %H:%M:%S", errors="coerce")

    sort_cols = ["_sort_time"]
    for candidate in ["TX Station", "RX Station"]:
        if candidate in sort_df.columns:
            sort_cols.append(candidate)
            break

    sort_df = sort_df.sort_values(sort_cols, ascending=[True] * len(sort_cols), na_position="last")
    return sort_df.drop(columns=["_sort_time"]).reset_index(drop=True)

def _sequential_tx_drilldown_labels(col_u_name, ref_header, *, target_callsign=""):
    """Use actual callsign plus role/setup for TX A/B drill-down traceability."""
    if col_u_name == "Setup A" and ref_header == "Setup B":
        base_call = str(target_callsign or "").strip().upper()
        if base_call:
            return f"{base_call} (Target / Setup A)", f"{base_call} (Reference / Setup B)"
    return col_u_name, ref_header

def _load_station_rows_for_drilldown(parquet_path, selected_meta_df, station_col, loc_col, columns=None):
    """Load raw parquet rows for selected callsign+locator identities."""
    if selected_meta_df is None or selected_meta_df.empty:
        return pd.DataFrame()

    selected_meta_df = selected_meta_df.copy()
    selected_meta_df[station_col] = selected_meta_df[station_col].astype(str)
    selected_meta_df[loc_col] = selected_meta_df[loc_col].astype(str)
    selected_meta_df = selected_meta_df.drop_duplicates(subset=[station_col, loc_col])
    sel_stations = _unique_station_order(selected_meta_df[station_col].tolist())
    if not sel_stations:
        return pd.DataFrame()

    read_columns = None
    if columns is not None:
        read_columns = list(dict.fromkeys(["peer_sign", "peer_grid", *columns]))

    station_df = read_parquet_artifact(
        parquet_path,
        columns=read_columns,
        filters=[('peer_sign', 'in', sel_stations)],
    )
    station_df['peer_sign'] = station_df['peer_sign'].astype(str)
    station_df['peer_grid'] = station_df['peer_grid'].astype(str)

    return station_df.merge(
        selected_meta_df,
        left_on=['peer_sign', 'peer_grid'],
        right_on=[station_col, loc_col],
        how='inner'
    )

def _build_drilldown_table(
    parquet_path,
    selected_meta_df,
    station_col,
    loc_col,
    km_col,
    az_col,
    analysis_id,
    is_compare,
    is_sequential,
    show_non_joint,
    is_local_median,
    col_u_name,
    ref_header,
    t,
    station_rows_df=None,
    tx_ab_bin_minutes=8,
    target_callsign="",
):
    """Build the drill-down dataframe for selected or all current segment identities."""
    if selected_meta_df is None or selected_meta_df.empty:
        return pd.DataFrame(), "No stations selected."

    selected_meta_df = selected_meta_df[[station_col, loc_col, km_col, az_col]].copy()
    selected_meta_df[station_col] = selected_meta_df[station_col].astype(str)
    selected_meta_df[loc_col] = selected_meta_df[loc_col].astype(str)
    selected_meta_df = selected_meta_df.drop_duplicates(subset=[station_col, loc_col])
    if station_rows_df is None:
        station_df = _load_station_rows_for_drilldown(parquet_path, selected_meta_df, station_col, loc_col)
    else:
        station_df = station_rows_df.copy()

    drill_df = None
    info_msg = None

    if station_df.empty:
        return pd.DataFrame(), "No spots available."

    is_opportunity = {
        "hit",
        "miss",
        "target_only",
        "target_snr",
        "time_slot",
    }.issubset(station_df.columns)

    if is_opportunity:
        opportunity_terms = absolute_terms(t, "TX" if analysis_id.startswith("TX") else "RX")
        target_snr_col = "Target SNR (dB @ 1W)"
        station_df["Date/Time (UTC)"] = (
            opportunity_utc_from_time_slot(station_df["time_slot"])
            .dt.strftime("%d-%b-%Y %H:%M:%S")
        )
        station_df["Outcome"] = np.select(
            [
                station_df["hit"] > 0,
                station_df["miss"] > 0,
                station_df["target_only"] > 0,
            ],
            [
                "T - Target",
                f"{opportunity_terms['counter_short']} - {opportunity_terms['counter']}",
                "Target-only",
            ],
            default="",
        )
        drill_df = station_df[
            [
                "Date/Time (UTC)",
                station_col,
                loc_col,
                km_col,
                az_col,
                "Outcome",
                "hit",
                "miss",
                "target_snr",
            ]
        ].copy()
        drill_df.columns = [
            "Date/Time (UTC)",
            station_col,
            loc_col,
            km_col,
            az_col,
            "Outcome",
            opportunity_terms["target_column"],
            opportunity_terms["counter_column"],
            target_snr_col,
        ]
        drill_df[target_snr_col] = pd.to_numeric(
            drill_df[target_snr_col],
            errors="coerce",
        ).round(1)
    elif not is_compare:
        station_df['Date/Time (UTC)'] = pd.to_datetime(station_df['time']).dt.strftime('%d-%b-%Y %H:%M:%S')
        drill_df = station_df[['Date/Time (UTC)', station_col, loc_col, km_col, az_col, 'snr', 'power', 'stat_val']].copy()
        drill_df.columns = ['Date/Time (UTC)', station_col, loc_col, km_col, az_col, 'SNR (Raw)', 'TX Power (dBm)', 'Norm@1W']
        for col in ['SNR (Raw)', 'Norm@1W']:
            drill_df[col] = pd.to_numeric(drill_df[col], errors='coerce').round(1)
    else:
        if is_sequential:
            bin_minutes = int(tx_ab_bin_minutes)
            station_df['dt_time'] = pd.to_datetime(station_df['time'])
            station_df['time_bin'] = station_df['dt_time'].dt.floor(f'{bin_minutes}min')

            df_t = station_df[station_df['is_me'] == 1]
            df_r = station_df[station_df['is_me'] == 0]

            bin_t = df_t.groupby('time_bin')['stat_val'].median().reset_index().rename(columns={'stat_val': 'micro_med_a'})
            bin_r = df_r.groupby('time_bin')['stat_val'].median().reset_index().rename(columns={'stat_val': 'micro_med_b'})

            station_df = pd.merge(station_df, bin_t, on='time_bin', how='left')
            station_df = pd.merge(station_df, bin_r, on='time_bin', how='left')
            station_df['bin_delta'] = np.where(
                station_df['micro_med_a'].notna() & station_df['micro_med_b'].notna(),
                station_df['micro_med_a'] - station_df['micro_med_b'],
                np.nan
            )

            if not show_non_joint:
                station_df = station_df[station_df['micro_med_a'].notna() & station_df['micro_med_b'].notna()]
                if station_df.empty:
                    return pd.DataFrame(), "No joint spots available for the selected station(s)."

            station_df['micro_med_b'] = np.where(station_df['is_me'] == 1, np.nan, station_df['micro_med_b'])
            station_df['micro_med_a'] = np.where(station_df['is_me'] == 0, np.nan, station_df['micro_med_a'])

            station_df = station_df.sort_values('dt_time', ascending=False)
            station_df['time_bin_str'] = station_df['time_bin'].dt.strftime('%H:%M') + ' - ' + (station_df['time_bin'] + pd.Timedelta(minutes=bin_minutes)).dt.strftime('%H:%M')
            station_df['Date/Time (UTC)'] = station_df['dt_time'].dt.strftime('%d-%b-%Y %H:%M:%S')
            target_tx_label, ref_tx_label = _sequential_tx_drilldown_labels(
                col_u_name,
                ref_header,
                target_callsign=target_callsign,
            )
            station_df['tx_callsign'] = np.where(station_df['is_me'] == 1, target_tx_label, ref_tx_label)

            drill_df = station_df[['Date/Time (UTC)', 'time_bin_str', 'tx_callsign', 'power', 'snr', 'stat_val', 'micro_med_a', 'micro_med_b', 'bin_delta']].copy()
            drill_df.columns = [
                'Date/Time (UTC)', t.get('tbl_col_bin', 'Time-Bin'), 'TX Station',
                'TX Power (dBm)', 'SNR (Raw)', 'Norm@1W',
                t.get('tbl_col_micro_a', 'Micro-Med A'), t.get('tbl_col_micro_b', 'Micro-Med B'), t.get('tbl_col_bin_delta', 'Bin \u0394')
            ]

            for col in ['Norm@1W', t.get('tbl_col_micro_a', 'Micro-Med A'), t.get('tbl_col_micro_b', 'Micro-Med B'), t.get('tbl_col_bin_delta', 'Bin \u0394')]:
                drill_df[col] = drill_df[col].map(lambda x: f"{x:+.1f}" if pd.notna(x) else "")
        else:
            joint_df = station_df.copy() if show_non_joint else station_df[(station_df['has_u'] > 0) & (station_df['has_r'] > 0)].copy()
            if joint_df.empty:
                return pd.DataFrame(), "No spots available." if show_non_joint else "No joint spots available for the selected station(s)."

            joint_df['Date/Time (UTC)'] = pd.to_datetime(joint_df['time_slot'] * 120, unit='s').dt.strftime('%d-%b-%Y %H:%M:%S')
            joint_df.loc[joint_df['has_u'] == 0, 'snr_u_norm'] = np.nan
            joint_df.loc[joint_df['has_r'] == 0, 'snr_r_norm'] = np.nan

            col_u = f'{col_u_name} SNR (dB)'
            col_r = f'{ref_header} SNR (dB)'
            col_delta_lbl = t.get('tbl_col_delta_snr', '\u0394 SNR (dB)')
            station_type = 'RX Station' if analysis_id.startswith("TX") else 'TX Station'

            if is_local_median and 'ref_detail_rows' in joint_df.columns:
                expanded_rows = []
                for _, row in joint_df.iterrows():
                    refs = _parse_ref_detail_rows(row.get('ref_detail_rows'))
                    has_u = row.get('has_u', 0) > 0
                    has_r = row.get('has_r', 0) > 0
                    own_snr = row.get('snr_u_norm', np.nan) if has_u else np.nan
                    cycle_ref_median = row.get('snr_r_norm', np.nan) if has_r else np.nan
                    delta_snr = round(own_snr - cycle_ref_median, 1) if pd.notna(own_snr) and pd.notna(cycle_ref_median) else np.nan

                    if refs:
                        for ref in refs:
                            try:
                                ref_dist_km = round(float(ref["ref_dist"]) / 1000)
                            except (TypeError, ValueError):
                                ref_dist_km = np.nan
                            try:
                                ref_snr = round(float(ref["ref_snr"]), 1)
                            except (TypeError, ValueError):
                                ref_snr = np.nan
                            expanded_rows.append({
                                'Date/Time (UTC)': row['Date/Time (UTC)'],
                                station_type: row[station_col],
                                loc_col: row[loc_col],
                                km_col: row[km_col],
                                az_col: row[az_col],
                                t.get('tbl_col_ref_station', 'Ref Station'): ref["ref_sign"],
                                loc_col + ' (Ref)': ref["ref_grid"],
                                'Ref km': ref_dist_km,
                                t.get('tbl_col_ref_snr', 'Ref SNR (dB)'): ref_snr,
                                t.get('tbl_col_cycle_ref_median', 'Cycle Ref Median SNR (dB)'): round(cycle_ref_median, 1) if pd.notna(cycle_ref_median) else np.nan,
                                col_u: round(own_snr, 1) if pd.notna(own_snr) else np.nan,
                                col_delta_lbl: delta_snr
                            })
                    elif has_u:
                        expanded_rows.append({
                            'Date/Time (UTC)': row['Date/Time (UTC)'],
                            station_type: row[station_col],
                            loc_col: row[loc_col],
                            km_col: row[km_col],
                            az_col: row[az_col],
                            t.get('tbl_col_ref_station', 'Ref Station'): np.nan,
                            loc_col + ' (Ref)': np.nan,
                            'Ref km': np.nan,
                            t.get('tbl_col_ref_snr', 'Ref SNR (dB)'): np.nan,
                            t.get('tbl_col_cycle_ref_median', 'Cycle Ref Median SNR (dB)'): np.nan,
                            col_u: round(own_snr, 1) if pd.notna(own_snr) else np.nan,
                            col_delta_lbl: np.nan
                        })

                if expanded_rows:
                    drill_df = pd.DataFrame(expanded_rows).sort_values('Date/Time (UTC)', ascending=False)
                else:
                    info_msg = "No reference station details available for the selected station(s)."
            elif 'best_ref_sign' in joint_df.columns:
                joint_df[col_delta_lbl] = np.where((joint_df['has_u'] > 0) & (joint_df['has_r'] > 0), (joint_df['snr_u_norm'] - joint_df['snr_r_norm']).round(1), np.nan)
                joint_df['snr_u_norm'] = pd.to_numeric(joint_df['snr_u_norm'], errors='coerce').round(1)
                joint_df['snr_r_norm'] = pd.to_numeric(joint_df['snr_r_norm'], errors='coerce').round(1)
                joint_df['snr_u_norm'] = joint_df['snr_u_norm'].astype(object).fillna("None")
                joint_df['snr_r_norm'] = joint_df['snr_r_norm'].astype(object).fillna("None")
                joint_df[col_delta_lbl] = joint_df[col_delta_lbl].astype(object).fillna("None")
                joint_df['best_ref_sign'] = joint_df['best_ref_sign'].fillna("None")
                joint_df['best_ref_dist_km'] = (joint_df['best_ref_dist'] / 1000).round(0).astype('Int64')

                drill_df = joint_df[['Date/Time (UTC)', station_col, loc_col, km_col, az_col, 'best_ref_sign', 'best_ref_dist_km', 'snr_r_norm', 'snr_u_norm', col_delta_lbl]].copy()
                drill_df.columns = ['Date/Time (UTC)', station_type, loc_col, km_col, az_col, 'Best Ref', 'Ref km', col_r, col_u, col_delta_lbl]
            else:
                joint_df[col_delta_lbl] = np.where((joint_df['has_u'] > 0) & (joint_df['has_r'] > 0), (joint_df['snr_u_norm'] - joint_df['snr_r_norm']).round(1), np.nan)
                joint_df['snr_u_norm'] = pd.to_numeric(joint_df['snr_u_norm'], errors='coerce').round(1)
                joint_df['snr_r_norm'] = pd.to_numeric(joint_df['snr_r_norm'], errors='coerce').round(1)
                joint_df['snr_u_norm'] = joint_df['snr_u_norm'].astype(object).fillna("None")
                joint_df['snr_r_norm'] = joint_df['snr_r_norm'].astype(object).fillna("None")
                joint_df[col_delta_lbl] = joint_df[col_delta_lbl].astype(object).fillna("None")
                drill_df = joint_df[['Date/Time (UTC)', station_col, loc_col, km_col, az_col, 'snr_r_norm', 'snr_u_norm', col_delta_lbl]].copy()
                drill_df.columns = ['Date/Time (UTC)', station_type, loc_col, km_col, az_col, col_r, col_u, col_delta_lbl]

    if drill_df is not None and not drill_df.empty:
        drill_df = _sort_drilldown_default(drill_df)
    return drill_df if drill_df is not None else pd.DataFrame(), info_msg
