"""
Result export helpers for WSPRadar.

The export layer deliberately consumes registered result recipes instead of
rerunning analysis SQL. High-resolution figures and full-segment drill-down
tables are built only after the user requests the prepared results package,
while preserving the current segment, station, non-joint, and time-bin state.
"""

import io
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import streamlit as st
from matplotlib import colors as mcolors
from matplotlib.lines import Line2D
from matplotlib.text import Text

from config import APP_VERSION
from core.matplotlib_runtime import matplotlib_operation_lock
from core.snr_utils import format_snr_like_columns_for_csv
from ui.config_io import CONFIG_APP_NAME, build_config_payload
from ui.matplotlib_renderer import dispose_matplotlib_figure


EXPORT_STATE_KEY = "result_export_blocks"
EXPORT_RUN_ID_KEY = "result_export_run_id"
EXPORT_ZIP_BYTES_KEY = "result_export_zip_bytes"
EXPORT_ZIP_FILENAME_KEY = "result_export_zip_filename"
EXPORT_ZIP_SIGNATURE_KEY = "result_export_zip_signature"


def _current_run_id():
    return st.session_state.get("run_id", 0)


def reset_result_export_state():
    """Clear export artifacts for a fresh analysis run."""
    st.session_state[EXPORT_STATE_KEY] = {}
    st.session_state[EXPORT_RUN_ID_KEY] = _current_run_id()
    st.session_state.pop("segment_stability_cache", None)
    _clear_prepared_results()


def _clear_prepared_results():
    """Drop prepared ZIP bytes when result selections or analysis runs change."""
    for key in [EXPORT_ZIP_BYTES_KEY, EXPORT_ZIP_FILENAME_KEY, EXPORT_ZIP_SIGNATURE_KEY]:
        st.session_state.pop(key, None)


def _ensure_current_export_state():
    run_id = _current_run_id()
    if st.session_state.get(EXPORT_RUN_ID_KEY) != run_id:
        st.session_state[EXPORT_STATE_KEY] = {}
        st.session_state[EXPORT_RUN_ID_KEY] = run_id
        _clear_prepared_results()
    if EXPORT_STATE_KEY not in st.session_state:
        st.session_state[EXPORT_STATE_KEY] = {}
    return st.session_state[EXPORT_STATE_KEY]


def _set_with_restore(snapshots, obj, getter_name, setter_name, value):
    try:
        getter = getattr(obj, getter_name)
        setter = getattr(obj, setter_name)
        old_value = getter()
        setter(value)
        snapshots.append((setter, old_value))
    except Exception:
        return


def _is_near_white(rgba):
    try:
        r, g, b, a = mcolors.to_rgba(rgba)
        return a > 0 and r > 0.94 and g > 0.94 and b > 0.94
    except Exception:
        return False


def _is_near_black(rgba):
    try:
        r, g, b, a = mcolors.to_rgba(rgba)
        return a > 0 and r < 0.16 and g < 0.16 and b < 0.16
    except Exception:
        return False


def _is_light_line_color(rgba):
    """Return True for pale line colors that disappear on white export backgrounds."""
    try:
        r, g, b, a = mcolors.to_rgba(rgba)
        return a > 0 and r > 0.65 and g > 0.65 and b > 0.65
    except Exception:
        return False


def _style_figure_for_paper(fig):
    """Temporarily restyle a dark UI figure for white-paper PNG export."""
    snapshots = []
    _set_with_restore(snapshots, fig.patch, "get_facecolor", "set_facecolor", "white")

    for ax in fig.axes:
        _set_with_restore(snapshots, ax, "get_facecolor", "set_facecolor", "white")
        try:
            ax.tick_params(colors="#222222")
        except Exception:
            pass
        for spine in ax.spines.values():
            _set_with_restore(snapshots, spine, "get_edgecolor", "set_edgecolor", "#777777")
        for patch in ax.patches:
            if _is_near_white(patch.get_facecolor()):
                _set_with_restore(snapshots, patch, "get_facecolor", "set_facecolor", "#d0d0d0")
            elif _is_near_black(patch.get_facecolor()):
                _set_with_restore(snapshots, patch, "get_facecolor", "set_facecolor", "#f3f3f3")
            if _is_near_white(patch.get_edgecolor()):
                _set_with_restore(snapshots, patch, "get_edgecolor", "set_edgecolor", "#777777")
        for collection in ax.collections:
            try:
                facecolors = collection.get_facecolors()
            except Exception:
                continue
            if len(facecolors) and all(_is_near_white(color) for color in facecolors):
                _set_with_restore(snapshots, collection, "get_facecolors", "set_facecolor", "#d0d0d0")
            elif len(facecolors) and all(_is_near_black(color) for color in facecolors):
                _set_with_restore(snapshots, collection, "get_facecolors", "set_facecolor", "#f3f3f3")
            try:
                edgecolors = collection.get_edgecolors()
            except Exception:
                edgecolors = []
            if len(edgecolors) and all(_is_near_white(color) for color in edgecolors):
                _set_with_restore(snapshots, collection, "get_edgecolors", "set_edgecolor", "#777777")

    for text in fig.findobj(Text):
        _set_with_restore(snapshots, text, "get_color", "set_color", "#111111")

    for line in fig.findobj(Line2D):
        if _is_near_white(line.get_color()) or _is_light_line_color(line.get_color()):
            _set_with_restore(snapshots, line, "get_color", "set_color", "#111111")

    for legend in fig.legends:
        frame = legend.get_frame()
        _set_with_restore(snapshots, frame, "get_facecolor", "set_facecolor", "white")
        _set_with_restore(snapshots, frame, "get_edgecolor", "set_edgecolor", "#bbbbbb")
        for text in legend.get_texts():
            _set_with_restore(snapshots, text, "get_color", "set_color", "#111111")

    for ax in fig.axes:
        legend = ax.get_legend()
        if legend is None:
            continue
        frame = legend.get_frame()
        _set_with_restore(snapshots, frame, "get_facecolor", "set_facecolor", "white")
        _set_with_restore(snapshots, frame, "get_edgecolor", "set_edgecolor", "#bbbbbb")
        for text in legend.get_texts():
            _set_with_restore(snapshots, text, "get_color", "set_color", "#111111")

    for ax in fig.axes:
        try:
            ax.grid(axis="y", color="#dddddd", linewidth=0.8, alpha=0.9)
        except Exception:
            pass

    return snapshots


def _restore_figure_style(snapshots):
    for setter, old_value in reversed(snapshots):
        try:
            setter(old_value)
        except Exception:
            continue


def figure_to_png_bytes(fig, dpi=300, paper_theme=True):
    """Render a Matplotlib figure to high-resolution PNG bytes."""
    with matplotlib_operation_lock():
        snapshots = _style_figure_for_paper(fig) if paper_theme else []
        try:
            buf = io.BytesIO()
            fig.savefig(
                buf,
                format="png",
                dpi=dpi,
                facecolor="white" if paper_theme else fig.get_facecolor(),
                edgecolor="none",
                bbox_inches="tight",
                pad_inches=0.15,
            )
            return buf.getvalue()
        finally:
            _restore_figure_style(snapshots)


def register_map_export_context(analysis, parquet_path, start_t, end_t, max_dist_km, base_min_stations, lat_0, lon_0):
    """Register enough context to render the high-resolution light map on demand."""
    blocks = _ensure_current_export_state()
    block = blocks.setdefault(analysis["id"], {})
    block.update({
        "analysis_id": analysis["id"],
        "title": analysis["title"],
        "mode_folder": "compare" if analysis["is_compare"] else "absolute",
        "is_compare": bool(analysis["is_compare"]),
        "is_sequential": bool(analysis["is_sequential"]),
        "analysis_kind": analysis.get("analysis_kind", "comparison"),
        "absolute_method_version": analysis.get("absolute_method_version"),
        "decode_filter_mode": analysis.get("decode_filter_mode"),
        "map_context": {
            "parquet_path": parquet_path,
            "start_t": start_t,
            "end_t": end_t,
            "max_dist_km": max_dist_km,
            "base_min_stations": base_min_stations,
            "lat_0": lat_0,
            "lon_0": lon_0,
        },
    })
    _clear_prepared_results()


def register_inspector_export(
    analysis_id,
    selected_segment,
    selected_distance,
    selected_direction,
    show_non_joint,
    evidence_time_bin,
    selected_stations,
    selected_ranges=None,
    selected_directions=None,
    segment_figure_recipe=None,
    selected_evidence_figure_recipe=None,
    station_insights_df=None,
    drilldown_selected_df=None,
    all_drilldown_context=None,
    reference_snr_header=None,
):
    """Register compact current inspector state for lazy high-resolution export."""
    blocks = _ensure_current_export_state()
    block = blocks.setdefault(analysis_id, {"analysis_id": analysis_id})
    block.update({
        "selected_segment": selected_segment,
        "selected_distance": selected_distance,
        "selected_direction": selected_direction,
        "selected_ranges": list(selected_ranges or []),
        "selected_directions": list(selected_directions or []),
        "show_non_joint": bool(show_non_joint),
        "evidence_time_bin": evidence_time_bin,
        "selected_stations": selected_stations or [],
        "segment_figure_recipe": segment_figure_recipe,
        "selected_evidence_figure_recipe": selected_evidence_figure_recipe,
        "table_station_insights_current_segment.csv": station_insights_df.copy() if isinstance(station_insights_df, pd.DataFrame) else pd.DataFrame(),
        "table_drilldown_selected_stations.csv": drilldown_selected_df.copy() if isinstance(drilldown_selected_df, pd.DataFrame) else pd.DataFrame(),
        "all_drilldown_context": all_drilldown_context,
        "reference_snr_header": reference_snr_header,
    })


def _should_annotate_reference_correction(column_name, reference_snr_header=None):
    text = str(column_name).strip().casefold()
    reference_text = str(reference_snr_header).strip().casefold() if reference_snr_header else ""
    if reference_text and text == reference_text:
        return True
    return (
        "ref snr" in text or
        "reference snr" in text or
        "cycle ref median" in text or
        "micro-med b" in text or
        "bin \u03b4" in text or
        "\u03b4 snr" in text or
        "delta snr" in text or
        "median \u03b4" in text
    )


def _annotate_reference_correction_headers(df, correction_db, reference_snr_header=None):
    if not isinstance(df, pd.DataFrame) or df.empty or abs(float(correction_db or 0.0)) < 0.05:
        return df

    suffix = f" (ref corr {float(correction_db):+.1f} dB)"
    renamed = {}
    for col in df.columns:
        if _should_annotate_reference_correction(col, reference_snr_header):
            renamed[col] = f"{col}{suffix}"
    return df.rename(columns=renamed) if renamed else df


def _dataframe_to_csv_bytes(df, correction_db=0.0, reference_snr_header=None):
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame()
    export_df = _annotate_reference_correction_headers(df, correction_db, reference_snr_header)
    return format_snr_like_columns_for_csv(export_df).to_csv(index=False).encode("utf-8-sig")


def _json_default(value):
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    return str(value)


def _build_run_metadata(blocks, config_payload, analysis_cache_paths=None):
    config = config_payload.get("config", {})
    compare_present = any(block.get("mode_folder") == "compare" for block in blocks.values())
    absolute_present = any(block.get("mode_folder") == "absolute" for block in blocks.values())
    analysis_cache_paths = analysis_cache_paths or {}

    return {
        "app": CONFIG_APP_NAME,
        "version": APP_VERSION,
        "export_signature": _export_signature(blocks),
        "exported_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "language": st.session_state.get("lang"),
        "run_mode": st.session_state.get("run_mode"),
        "blocks_present": {
            "compare": compare_present,
            "absolute": absolute_present,
        },
        "callsign": config.get("callsign"),
        "reference_or_benchmark_mode": config.get("benchmark_mode"),
        "band": config.get("band"),
        "time_window": {
            "time_mode": config.get("time_mode"),
            "hours": config.get("hours"),
            "start_date": config.get("start_date"),
            "start_time": config.get("start_time"),
            "end_date": config.get("end_date"),
            "end_time": config.get("end_time"),
        },
        "benchmark_snr_correction_db": config.get("benchmark_snr_correction_db"),
        "thresholds_and_filters": {
            "solar_state": config.get("solar_state"),
            "map_scope_km": config.get("map_scope_km"),
            "exclude_special_callsigns": config.get("exclude_special_callsigns"),
            "exclude_moving_stations": config.get("exclude_moving_stations"),
            "min_joint_spots_per_station": config.get("min_joint_spots_per_station"),
            "min_confirmed_opportunities_per_peer": config.get("min_confirmed_opportunities_per_peer"),
            "min_joint_stations_per_map_segment": config.get("min_joint_stations_per_map_segment"),
        },
        "result_blocks": [
            {
                "analysis_id": block.get("analysis_id"),
                "title": block.get("title"),
                "folder": block.get("mode_folder"),
                "analysis_cache_file": analysis_cache_paths.get(key),
                "selected_segment": block.get("selected_segment"),
                "selected_distance": block.get("selected_distance"),
                "selected_direction": block.get("selected_direction"),
                "selected_ranges": block.get("selected_ranges", []),
                "selected_directions": block.get("selected_directions", []),
                "selected_stations": block.get("selected_stations", []),
                "show_non_joint": block.get("show_non_joint"),
                "evidence_time_bin": block.get("evidence_time_bin"),
                "is_compare": block.get("is_compare"),
                "is_sequential": block.get("is_sequential"),
                "analysis_kind": block.get("analysis_kind"),
                "absolute_method_version": block.get("absolute_method_version"),
            }
            for key, block in blocks.items()
        ],
    }


def _table_signature_value(df):
    if not isinstance(df, pd.DataFrame):
        return [0, 0]
    return [int(df.shape[0]), int(df.shape[1])]


def _export_signature(blocks):
    """Return a compact fingerprint for the currently registered export state."""
    payload = []
    for key, block in sorted(blocks.items()):
        payload.append({
            "key": key,
            "analysis_id": block.get("analysis_id"),
            "title": block.get("title"),
            "mode_folder": block.get("mode_folder"),
            "selected_segment": block.get("selected_segment"),
            "selected_distance": block.get("selected_distance"),
            "selected_direction": block.get("selected_direction"),
            "selected_ranges": block.get("selected_ranges", []),
            "selected_directions": block.get("selected_directions", []),
            "selected_stations": block.get("selected_stations", []),
            "show_non_joint": block.get("show_non_joint"),
            "evidence_time_bin": block.get("evidence_time_bin"),
            "map_context": block.get("map_context"),
            "station_table_shape": _table_signature_value(block.get("table_station_insights_current_segment.csv")),
            "selected_drilldown_shape": _table_signature_value(block.get("table_drilldown_selected_stations.csv")),
            "all_drilldown_station_count": len((block.get("all_drilldown_context") or {}).get("station_meta_df", [])),
        })
    return json.dumps(payload, sort_keys=True, default=_json_default)


def _safe_analysis_filename(analysis_id):
    safe_id = "".join(ch.lower() if ch.isalnum() else "_" for ch in str(analysis_id or "analysis"))
    safe_id = "_".join(part for part in safe_id.split("_") if part)
    return safe_id or "analysis"


def _analysis_cache_export_paths(blocks):
    """Return ZIP-relative parquet cache paths for exportable result blocks."""
    paths = {}
    used_folders = {}

    for key, block in blocks.items():
        folder = block.get("mode_folder")
        context = block.get("map_context") or {}
        parquet_path = context.get("parquet_path")
        if folder not in {"compare", "absolute"} or not parquet_path:
            continue
        if not Path(parquet_path).exists():
            continue

        folder_count = used_folders.get(folder, 0)
        used_folders[folder] = folder_count + 1
        parquet_name = "analysis_cache.parquet" if folder_count == 0 else f"analysis_cache_{_safe_analysis_filename(block.get('analysis_id'))}.parquet"
        paths[key] = f"{folder}/{parquet_name}"

    return paths


def _render_map_png_for_block(block):
    """Render the registered map context as a high-resolution light-theme PNG."""
    context = block.get("map_context")
    if not context:
        return block.get("figure_map_highres.png")

    try:
        df = pd.read_parquet(context["parquet_path"])
    except Exception:
        return None

    from core.plot_engine import generate_map_plot
    plot_result = generate_map_plot(
        df,
        block.get("title", ""),
        block.get("is_compare", False),
        block.get("is_sequential", False),
        context["start_t"],
        context["end_t"],
        context["max_dist_km"],
        block.get("analysis_id"),
        context["base_min_stations"],
        context["lat_0"],
        context["lon_0"],
        theme="light",
        analysis_kind=block.get("analysis_kind", "comparison"),
    )
    if plot_result is None:
        return None

    fig = plot_result[0]
    try:
        return figure_to_png_bytes(fig, paper_theme=False)
    finally:
        dispose_matplotlib_figure(fig)

def _render_inspector_png_for_block(block, figure_name):
    """Render one inspector figure from compact inputs only during ZIP preparation."""
    from ui.plots.evidence_figures import (
        render_segment_insight_export_figure,
        render_selected_evidence_export_figure,
    )
    if figure_name == "figure_segment_insight.png":
        fig = render_segment_insight_export_figure(block.get("segment_figure_recipe"))
    elif figure_name == "figure_selected_station_evidence.png":
        fig = render_selected_evidence_export_figure(block.get("selected_evidence_figure_recipe"))
    else:
        return None
    if fig is None:
        return None
    try:
        return figure_to_png_bytes(fig, paper_theme=True)
    finally:
        dispose_matplotlib_figure(fig)

def _build_all_drilldown_for_block(block):
    """Load and build the full-segment drill-down table only during ZIP preparation."""
    context = block.get("all_drilldown_context") or {}
    map_context = block.get("map_context") or {}
    station_meta_df = context.get("station_meta_df")
    parquet_path = map_context.get("parquet_path")
    if not isinstance(station_meta_df, pd.DataFrame) or station_meta_df.empty or not parquet_path:
        return pd.DataFrame()

    from i18n import T
    from ui.inspector.drilldown import _build_drilldown_table, _load_station_rows_for_drilldown

    lang = context.get("lang", "en")
    t = T.get(lang, T["en"])
    try:
        station_rows_df = _load_station_rows_for_drilldown(
            parquet_path,
            station_meta_df,
            context["station_col"],
            context["loc_col"],
        )
        drilldown_df, _ = _build_drilldown_table(
            parquet_path,
            station_meta_df,
            context["station_col"],
            context["loc_col"],
            context["km_col"],
            context["az_col"],
            context["analysis_id"],
            context["is_compare"],
            context["is_sequential"],
            context["show_non_joint"],
            context["is_local_median"],
            context["col_u_name"],
            context["ref_header"],
            t,
            station_rows_df=station_rows_df,
        )
        return drilldown_df
    except (FileNotFoundError, KeyError, ValueError):
        return pd.DataFrame()


def build_results_zip():
    """Build the all-results ZIP payload from registered current result blocks."""
    blocks = _ensure_current_export_state()
    exportable_blocks = {
        key: block for key, block in blocks.items()
        if block.get("mode_folder") in {"compare", "absolute"}
    }
    if not exportable_blocks:
        return None, None

    config_bytes, _ = build_config_payload()
    config_payload = json.loads(config_bytes.decode("utf-8"))
    analysis_cache_paths = _analysis_cache_export_paths(exportable_blocks)
    metadata = _build_run_metadata(exportable_blocks, config_payload, analysis_cache_paths)
    timestamp_local = datetime.now().strftime("%Y_%m_%d__%H_%M")
    root = f"WSPRadar_export_{timestamp_local}"

    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{root}/config/wspradar_config.config", config_bytes)
        zf.writestr(
            f"{root}/config/run_metadata.json",
            json.dumps(metadata, indent=2, default=_json_default).encode("utf-8"),
        )

        for block_key, block in exportable_blocks.items():
            folder = block["mode_folder"]
            correction_db = config_payload.get("config", {}).get("benchmark_snr_correction_db", 0.0) if block.get("is_compare") else 0.0
            for figure_name in [
                "figure_map_highres.png",
                "figure_segment_insight.png",
                "figure_selected_station_evidence.png",
            ]:
                png_bytes = (
                    _render_map_png_for_block(block)
                    if figure_name == "figure_map_highres.png"
                    else _render_inspector_png_for_block(block, figure_name)
                )
                if png_bytes:
                    zf.writestr(f"{root}/{folder}/{figure_name}", png_bytes)

            lazy_all_drilldown_df = _build_all_drilldown_for_block(block)
            for table_name in [
                "table_station_insights_current_segment.csv",
                "table_drilldown_selected_stations.csv",
                "table_drilldown_all_stations_current_segment.csv",
            ]:
                table_df = (
                    lazy_all_drilldown_df
                    if table_name == "table_drilldown_all_stations_current_segment.csv"
                    else block.get(table_name)
                )
                zf.writestr(
                    f"{root}/{folder}/{table_name}",
                    _dataframe_to_csv_bytes(
                        table_df,
                        correction_db=correction_db,
                        reference_snr_header=block.get("reference_snr_header"),
                    )
                )

            analysis_cache_path = analysis_cache_paths.get(block_key)
            parquet_path = (block.get("map_context") or {}).get("parquet_path")
            if analysis_cache_path and parquet_path:
                parquet_path = Path(parquet_path)
                if parquet_path.exists():
                    zf.write(parquet_path, f"{root}/{analysis_cache_path}")

    return zip_buf.getvalue(), f"{root}.zip"


def render_download_all_results(t):
    """Render the centered lazy all-results ZIP prepare/download controls."""
    blocks = _ensure_current_export_state()
    exportable_blocks = {
        key: block for key, block in blocks.items()
        if block.get("mode_folder") in {"compare", "absolute"}
    }
    if not exportable_blocks:
        return

    signature = _export_signature(exportable_blocks)
    if st.session_state.get(EXPORT_ZIP_SIGNATURE_KEY) != signature:
        _clear_prepared_results()

    st.markdown("<div style='height:1.0rem;'></div>", unsafe_allow_html=True)
    c_left, c_mid, c_right = st.columns([0.25, 0.5, 0.25])
    with c_mid:
        prepared_bytes = st.session_state.get(EXPORT_ZIP_BYTES_KEY)
        prepared_filename = st.session_state.get(EXPORT_ZIP_FILENAME_KEY)
        if prepared_bytes and prepared_filename:
            st.download_button(
                t.get("btn_download_prepared_results", "Download Prepared Results"),
                data=prepared_bytes,
                file_name=prepared_filename,
                mime="application/zip",
                icon=":material/download:",
                type="primary",
                width="stretch",
            )
            return

        if not st.button(
            t.get("btn_prepare_all_results", "Prepare All Results for Download"),
            icon=":material/archive:",
            type="secondary",
            width="stretch",
        ):
            return

        with st.spinner(t.get("msg_preparing_all_results", "Preparing high-resolution result package...")):
            zip_bytes, filename = build_results_zip()
        if not zip_bytes:
            return
        st.session_state[EXPORT_ZIP_BYTES_KEY] = zip_bytes
        st.session_state[EXPORT_ZIP_FILENAME_KEY] = filename
        st.session_state[EXPORT_ZIP_SIGNATURE_KEY] = signature
        st.download_button(
            t.get("btn_download_prepared_results", "Download Prepared Results"),
            data=zip_bytes,
            file_name=filename,
            mime="application/zip",
            icon=":material/download:",
            type="primary",
            width="stretch",
        )
