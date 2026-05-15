"""
Result export helpers for WSPRadar.

The export layer deliberately consumes already-rendered result state instead of
rerunning analysis SQL. This keeps the downloaded package traceable to the
current UI selections: segment, selected station rows, non-joint toggle, and
evidence time-bin setting.
"""

import io
import json
import zipfile
from datetime import datetime, timezone

import pandas as pd
import streamlit as st
from matplotlib import colors as mcolors
from matplotlib.lines import Line2D
from matplotlib.text import Text

from config import APP_VERSION
from ui.config_io import CONFIG_APP_NAME, build_config_payload


EXPORT_STATE_KEY = "result_export_blocks"
EXPORT_RUN_ID_KEY = "result_export_run_id"


def _current_run_id():
    return st.session_state.get("run_id", 0)


def reset_result_export_state():
    """Clear export artifacts for a fresh analysis run."""
    st.session_state[EXPORT_STATE_KEY] = {}
    st.session_state[EXPORT_RUN_ID_KEY] = _current_run_id()


def _ensure_current_export_state():
    run_id = _current_run_id()
    if st.session_state.get(EXPORT_RUN_ID_KEY) != run_id:
        st.session_state[EXPORT_STATE_KEY] = {}
        st.session_state[EXPORT_RUN_ID_KEY] = run_id
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
        try:
            ax.grid(axis="y", color="#dddddd", linewidth=0.8, alpha=0.9)
        except Exception:
            pass
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

    return snapshots


def _restore_figure_style(snapshots):
    for setter, old_value in reversed(snapshots):
        try:
            setter(old_value)
        except Exception:
            continue


def figure_to_png_bytes(fig, dpi=300, paper_theme=True):
    """Render a Matplotlib figure to high-resolution PNG bytes."""
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


def register_map_export(analysis, fig, line1_str, paper_theme=True):
    """Register the current map figure for the all-results export ZIP."""
    blocks = _ensure_current_export_state()
    block = blocks.setdefault(analysis["id"], {})
    block.update({
        "analysis_id": analysis["id"],
        "title": analysis["title"],
        "mode_folder": "compare" if analysis["is_compare"] else "absolute",
        "is_compare": bool(analysis["is_compare"]),
        "is_sequential": bool(analysis["is_sequential"]),
        "line1_str": line1_str,
        "figure_map_highres.png": figure_to_png_bytes(fig, paper_theme=paper_theme),
    })


def register_inspector_export(
    analysis_id,
    selected_segment,
    selected_distance,
    selected_direction,
    show_non_joint,
    evidence_time_bin,
    selected_stations,
    segment_figure_png=None,
    selected_evidence_figure_png=None,
    station_insights_df=None,
    drilldown_selected_df=None,
    drilldown_all_df=None,
):
    """Register current segment-inspector state and tables for one result block."""
    blocks = _ensure_current_export_state()
    block = blocks.setdefault(analysis_id, {"analysis_id": analysis_id})
    block.update({
        "selected_segment": selected_segment,
        "selected_distance": selected_distance,
        "selected_direction": selected_direction,
        "show_non_joint": bool(show_non_joint),
        "evidence_time_bin": evidence_time_bin,
        "selected_stations": selected_stations or [],
        "figure_segment_insight.png": segment_figure_png,
        "figure_selected_station_evidence.png": selected_evidence_figure_png,
        "table_station_insights_current_segment.csv": station_insights_df.copy() if isinstance(station_insights_df, pd.DataFrame) else pd.DataFrame(),
        "table_drilldown_selected_stations.csv": drilldown_selected_df.copy() if isinstance(drilldown_selected_df, pd.DataFrame) else pd.DataFrame(),
        "table_drilldown_all_stations_current_segment.csv": drilldown_all_df.copy() if isinstance(drilldown_all_df, pd.DataFrame) else pd.DataFrame(),
    })


def _dataframe_to_csv_bytes(df):
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame()
    return df.to_csv(index=False).encode("utf-8-sig")


def _json_default(value):
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    return str(value)


def _build_run_metadata(blocks, config_payload):
    config = config_payload.get("config", {})
    compare_present = any(block.get("mode_folder") == "compare" for block in blocks.values())
    absolute_present = any(block.get("mode_folder") == "absolute" for block in blocks.values())

    return {
        "app": CONFIG_APP_NAME,
        "version": APP_VERSION,
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
            "min_joint_stations_per_map_segment": config.get("min_joint_stations_per_map_segment"),
        },
        "result_blocks": [
            {
                "analysis_id": block.get("analysis_id"),
                "title": block.get("title"),
                "folder": block.get("mode_folder"),
                "selected_segment": block.get("selected_segment"),
                "selected_distance": block.get("selected_distance"),
                "selected_direction": block.get("selected_direction"),
                "selected_stations": block.get("selected_stations", []),
                "show_non_joint": block.get("show_non_joint"),
                "evidence_time_bin": block.get("evidence_time_bin"),
                "is_compare": block.get("is_compare"),
                "is_sequential": block.get("is_sequential"),
            }
            for block in blocks.values()
        ],
    }


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
    metadata = _build_run_metadata(exportable_blocks, config_payload)
    timestamp_local = datetime.now().strftime("%Y_%m_%d__%H_%M")
    root = f"WSPRadar_export_{timestamp_local}"

    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{root}/config/wspradar_config.config", config_bytes)
        zf.writestr(
            f"{root}/config/run_metadata.json",
            json.dumps(metadata, indent=2, default=_json_default).encode("utf-8"),
        )

        for block in exportable_blocks.values():
            folder = block["mode_folder"]
            for figure_name in [
                "figure_map_highres.png",
                "figure_segment_insight.png",
                "figure_selected_station_evidence.png",
            ]:
                png_bytes = block.get(figure_name)
                if png_bytes:
                    zf.writestr(f"{root}/{folder}/{figure_name}", png_bytes)

            for table_name in [
                "table_station_insights_current_segment.csv",
                "table_drilldown_selected_stations.csv",
                "table_drilldown_all_stations_current_segment.csv",
            ]:
                zf.writestr(f"{root}/{folder}/{table_name}", _dataframe_to_csv_bytes(block.get(table_name)))

    return zip_buf.getvalue(), f"{root}.zip"


def render_download_all_results(t):
    """Render the centered all-results ZIP download button."""
    zip_bytes, filename = build_results_zip()
    if not zip_bytes:
        return

    st.markdown("<div style='height:1.0rem;'></div>", unsafe_allow_html=True)
    c_left, c_mid, c_right = st.columns([0.25, 0.5, 0.25])
    with c_mid:
        st.download_button(
            t.get("btn_download_all_results", "Download All Results"),
            data=zip_bytes,
            file_name=filename,
            mime="application/zip",
            icon=":material/archive:",
            type="primary",
            width="stretch",
        )
