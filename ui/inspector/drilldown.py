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

def opportunity_drilldown_display_table(drill_df, translations, analysis_id):
    """Prepare direction-aware Success drill-down columns for visible display.

    The returned frame retains the source index so the caller can map any
    display-only filtering back to the unchanged canonical export rows.
    """
    if drill_df is None or drill_df.empty:
        return pd.DataFrame() if drill_df is None else drill_df.copy()
    terms = absolute_terms(
        translations,
        "TX" if str(analysis_id).upper().startswith("TX") else "RX",
    )
    display_df = drill_df.copy()
    is_tx = str(analysis_id).upper().startswith("TX")
    canonical_success_column = terms["target_column"]
    canonical_counter_column = terms["counter_column"]
    counter_display_column = (
        translations["tbl_col_success_counter_display_tx"]
        if is_tx
        else terms["opportunity_counter"]
    )
    display_df = display_df.drop(columns=["Outcome"], errors="ignore")
    return display_df.rename(
        columns={
            canonical_success_column: terms["opportunity_success"],
            canonical_counter_column: counter_display_column,
        }
    )

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
    show_non_joint,
    is_local_median,
    col_u_name,
    ref_header,
    t,
    station_rows_df=None,
):
    """Build the drill-down dataframe for selected or all current segment identities."""
    if selected_meta_df is None or selected_meta_df.empty:
        return pd.DataFrame(), t["msg_drilldown_no_stations_selected"]

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
        return pd.DataFrame(), t["msg_drilldown_no_spots"]

    is_opportunity = {
        "hit",
        "miss",
        "target_only",
        "target_snr",
        "time_slot",
    }.issubset(station_df.columns)

    if is_opportunity:
        opportunity_terms = absolute_terms(t, "TX" if analysis_id.startswith("TX") else "RX")
        target_snr_col = "Target SNR (dB @ 30 dBm)"
        station_df["Date/Time (UTC)"] = (
            opportunity_utc_from_time_slot(station_df["time_slot"])
            .dt.strftime("%d-%b-%Y %H:%M:%S")
        )
        station_df["Outcome"] = np.select(
            [
                station_df["target_only"] > 0,
                station_df["hit"] > 0,
                station_df["miss"] > 0,
            ],
            [
                "Target-only",
                "T - Target",
                f"{opportunity_terms['counter_short']} - {opportunity_terms['counter']}",
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
    else:
        joint_df = station_df.copy() if show_non_joint else station_df[(station_df['has_u'] > 0) & (station_df['has_r'] > 0)].copy()
        if joint_df.empty:
            return (
                pd.DataFrame(),
                (
                    t["msg_drilldown_no_spots"]
                    if show_non_joint
                    else t["msg_drilldown_no_joint_spots"]
                ),
            )

        joint_df['Date/Time (UTC)'] = pd.to_datetime(joint_df['time_slot'] * 120, unit='s').dt.strftime('%d-%b-%Y %H:%M:%S')
        joint_df.loc[joint_df['has_u'] == 0, 'snr_u_norm'] = np.nan
        joint_df.loc[joint_df['has_r'] == 0, 'snr_r_norm'] = np.nan

        col_u = f'{col_u_name} SNR (dB)'
        col_r = f'{ref_header} SNR (dB)'
        col_delta_lbl = t['tbl_col_delta_snr']
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
                            t['tbl_col_ref_station']: ref["ref_sign"],
                            loc_col + ' (Ref)': ref["ref_grid"],
                            'Ref km': ref_dist_km,
                            t['tbl_col_ref_snr']: ref_snr,
                            t['tbl_col_cycle_ref_median']: round(cycle_ref_median, 1) if pd.notna(cycle_ref_median) else np.nan,
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
                        t['tbl_col_ref_station']: np.nan,
                        loc_col + ' (Ref)': np.nan,
                        'Ref km': np.nan,
                        t['tbl_col_ref_snr']: np.nan,
                        t['tbl_col_cycle_ref_median']: np.nan,
                        col_u: round(own_snr, 1) if pd.notna(own_snr) else np.nan,
                        col_delta_lbl: np.nan
                    })

            if expanded_rows:
                drill_df = pd.DataFrame(expanded_rows).sort_values('Date/Time (UTC)', ascending=False)
            else:
                info_msg = t[
                    "msg_drilldown_no_reference_station_details"
                ]
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
