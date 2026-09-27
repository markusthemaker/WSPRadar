"""Build review overlays from paper pixels and freshly executed WSPRadar SQL.

This diagnostic artifact builder does not update scientific fixture expectations.
Figure 7 anchors are extracted from the image without using archive coordinates.
"""

import argparse
from collections import deque
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.collections import QuadMesh
from matplotlib.patches import ConnectionPatch
from matplotlib import patheffects
import numpy as np
import pandas as pd
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from config.demo_pdf_headers import DEMO_PDF_HEADERS
from core.analysis_context import solar_path_state
from core.matplotlib_runtime import synchronized_matplotlib
from scripts.demo_pdf_footer import DEMO_PDF_FOOTER_TEXT, add_demo_pdf_footer
from scripts.demo_pdf_header import add_demo_pdf_header, demo_pdf_metadata
from i18n import T
from ui.plots.evidence_figures import (
    _selected_evidence_export_recipe,
    _compare_temporal_profile_values,
    render_selected_evidence_export_figure,
)
from ui.results_export import _style_figure_for_paper

FIXTURES = ROOT / "tests/regression/reference_fixtures"
START = datetime(2010, 12, 19, 12, tzinfo=timezone.utc)
END = datetime(2010, 12, 20, 20, tzinfo=timezone.utc)
SERIES_COLORS = {"KP4MD": "#008864", "WB6RQN": "#b86500"}
GATE_RING_COLOR = "#30343b"
INK = "#172B3A"
MUTED = "#526572"


def extract_figure7_anchors(image_path):
    """Keep compact color components; reject merged markers and thin lines."""
    pixels = np.asarray(Image.open(image_path).convert("RGB"))
    if pixels.shape != (656, 1317, 3):
        raise ValueError("Figure 7 must be the original 1317 x 656 raster")
    masks = {
        "KP4MD": (pixels[:, :, 2] > 150) & (pixels[:, :, 0] < 100) & (pixels[:, :, 1] < 120),
        "WB6RQN": (pixels[:, :, 0] > 150) & (pixels[:, :, 1] < 120) & (pixels[:, :, 2] < 120),
    }
    anchors = []
    for series, mask in masks.items():
        mask[:105] = False
        mask[554:] = False
        mask[:, :79] = False
        mask[:, 1164:] = False
        eroded = np.logical_and.reduce([
            mask[y:y + 654, x:x + 1315] for y in range(3) for x in range(3)
        ])
        remaining = set(zip(*np.where(eroded)))
        centers = []
        while remaining:
            seed = remaining.pop()
            pending = deque([seed])
            component = [seed]
            while pending:
                y, x = pending.popleft()
                for neighbor in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                    if neighbor in remaining:
                        remaining.remove(neighbor)
                        pending.append(neighbor)
                        component.append(neighbor)
            coordinates = np.asarray(component)
            height, width = coordinates.max(axis=0) - coordinates.min(axis=0) + 1
            # An eroded isolated marker is about 8 x 8 pixels. Wider/taller
            # components can combine adjacent reports, so do not assign them
            # a single timestamp even if a candidate happens to be nearby.
            if not (35 <= len(component) <= 90 and width <= 10 and height <= 10):
                continue
            y, x = coordinates.mean(axis=0) + 1
            centers.append((float(x), float(y), len(component)))
        for index, (x, y, area) in enumerate(sorted(centers), 1):
            timestamp = START + timedelta(minutes=(x - 78) * 1920 / 1086)
            snr = (104 - y) / 15
            anchors.append({
                "marker_id": f"{series}_{index:02d}", "series": series,
                "x_pixel": round(x, 6), "y_pixel": round(y, 6),
                "eroded_area_pixels": area, "paper_utc": timestamp.isoformat(),
                "paper_snr_db": round(snr), "calibrated_snr_db": round(snr, 6),
                "time_tolerance_seconds": 240, "snr_tolerance_db": 0.25,
            })
    return pd.DataFrame(anchors)


def sql_endpoint_reports(run, direction):
    """Project pre-gate SQL endpoints and actual production-retained status.

    Pre-gate points are a deliberate publication diagnostic, not eligible
    Benchmark results. Outer rings come from the real post-fetch output and
    must also map to the corresponding retained Inspector outcome.
    """
    if solar_path_state(run.context.solar_state) is not None or run.context.exclude_moving_stations:
        raise ValueError("Milazzo overlay gating requires the frozen all-solar, moving-stations-included scope")
    active_time_slots = set(run.sql_rows.loc[run.sql_rows.has_u.gt(0), "time_slot"])
    retained_keys = set(run.processed[["time_slot", "peer_sign", "peer_grid"]].itertuples(index=False, name=None))
    unit_outcomes = run.units.set_index(["evidence_utc", "peer_sign", "peer_grid"]).outcome
    if not unit_outcomes.index.is_unique:
        raise ValueError("Retained Inspector identities must be unique")
    reports = []
    for row in run.sql_rows.itertuples():
        timestamp = datetime.fromtimestamp(row.time_slot * 120, tz=timezone.utc)
        if not START <= timestamp < END or row.peer_sign != "VE6PDQ":
            continue
        for series, present, normalized in (
            ("KP4MD", row.has_u, row.snr_u_norm),
            ("WB6RQN", row.has_r, row.snr_r_norm),
        ):
            if present:
                # Membership in production output supplies the plotted state.
                # The SQL witness set is only a fail-closed scope assertion: in
                # this frozen path there must be no further post-fetch removal.
                passes_target_active_gate = (row.time_slot, row.peer_sign, row.peer_grid) in retained_keys
                if passes_target_active_gate != (row.time_slot in active_time_slots):
                    raise ValueError("A plotted endpoint has an additional post-fetch exclusion; gate survival must remain distinct")
                unit_key = (pd.Timestamp(timestamp), row.peer_sign, row.peer_grid)
                if passes_target_active_gate != (unit_key in unit_outcomes.index):
                    raise ValueError("A plotted gate-retained endpoint must reach the production Inspector units")
                if passes_target_active_gate:
                    permitted_outcomes = ("joint", "target_only") if series == "KP4MD" else ("joint", "reference_only")
                    if unit_outcomes.loc[unit_key] not in permitted_outcomes:
                        raise ValueError("A plotted endpoint conflicts with its retained production outcome")
                reports.append({
                    "direction": direction, "series": series, "time_slot": row.time_slot,
                    "utc": timestamp.isoformat(), "peer_grid": row.peer_grid,
                    "sql_snr_at_30_dbm": normalized, "snr_at_37_dbm": normalized + 7,
                    "passes_target_active_gate": passes_target_active_gate,
                })
    return pd.DataFrame(reports)


def paired_evidence_points(run):
    """Use the production eligible Joint Spot projection for the lower panel."""
    points = run.points
    timestamps = pd.to_datetime(points.plot_time, utc=True)
    return points[
        points.station.eq("VE6PDQ") & timestamps.ge(START) & timestamps.lt(END)
    ].copy()


def paper_coordinates(reports, direction):
    """Apply only the declared paper-axis mapping to current report values."""
    minutes = (pd.to_datetime(reports.utc, utc=True) - pd.Timestamp(START)).dt.total_seconds() / 60
    if direction == "RX":
        calibration = json.loads((FIXTURES / "milazzo_fig6_rx_v1/paper_features_original.json").read_text())["calibration"]
        x = (minutes - calibration["minutes_intercept"]) / calibration["minutes_from_axis_start_per_x_pixel"]
        y = (reports.snr_at_37_dbm - calibration["snr_db_intercept"]) / calibration["snr_db_per_y_pixel"]
    else:
        x = 78 + minutes * 1086 / 1920
        y = 104 - reports.snr_at_37_dbm * 15
    return x, y


def diagnostic_endpoint(reports, series, utc):
    """Identify an annotated archive report without supplying its plotted SNR."""
    selected = reports[reports.series.eq(series) & pd.to_datetime(reports.utc, utc=True).eq(pd.Timestamp(utc))]
    if len(selected) != 1:
        raise ValueError(f"Expected one diagnostic endpoint for {series} at {utc}")
    return selected


def match_anchors(anchors, reports):
    matches = []
    times = pd.to_datetime(reports.utc, utc=True)
    for marker in anchors.itertuples():
        time_error = (times - pd.Timestamp(marker.paper_utc)).dt.total_seconds()
        time_candidates = reports[
            reports.series.eq(marker.series) & time_error.abs().le(marker.time_tolerance_seconds)
        ]
        candidates = time_candidates[
            (time_candidates.snr_at_37_dbm - marker.paper_snr_db).abs().le(marker.snr_tolerance_db)
        ]
        if len(candidates) != 1:
            raise ValueError(f"Unresolved paper anchor {marker.marker_id}: {len(candidates)} matches")
        report = candidates.iloc[0]
        matches.append({
            "marker_id": marker.marker_id, "series": marker.series,
            "paper_utc": marker.paper_utc, "sql_utc": report.utc,
            "paper_snr_db": marker.paper_snr_db,
            "sql_snr_at_30_dbm": report.sql_snr_at_30_dbm,
            "sql_snr_at_37_dbm": report.snr_at_37_dbm,
            "time_error_seconds": round(time_error.loc[report.name], 6),
            "snr_error_db": report.snr_at_37_dbm - marker.paper_snr_db,
            "nearby_time_candidates": len(time_candidates),
            "passes_target_active_gate": bool(report.passes_target_active_gate),
        })
    return pd.DataFrame(matches)


def _paper_image_extent(image_size, direction):
    """Invert the existing source calibration without fitting report values."""
    calibration_points = pd.DataFrame({"utc": [START, END], "snr_at_37_dbm": [0.0, 1.0]})
    x_pixels, y_pixels = paper_coordinates(calibration_points, direction)
    utc_start, utc_end = mdates.date2num([START, END])
    days_per_pixel = (utc_end - utc_start) / (x_pixels.iloc[1] - x_pixels.iloc[0])
    db_per_pixel = 1 / (y_pixels.iloc[1] - y_pixels.iloc[0])
    width_pixels, height_pixels = image_size
    return (
        utc_start + (-.5 - x_pixels.iloc[0]) * days_per_pixel,
        utc_start + (width_pixels - .5 - x_pixels.iloc[0]) * days_per_pixel,
        (height_pixels - .5 - y_pixels.iloc[0]) * db_per_pixel,
        (-.5 - y_pixels.iloc[0]) * db_per_pixel,
    )


def _production_temporal_recipe(run):
    """Render only the existing VE6PDQ pairs with the configured station bins."""
    labels = T["en"]
    time_bin = run.configuration["station_evidence_time_bin_compare"]
    return _selected_evidence_export_recipe(
        paired_evidence_points(run), "VE6PDQ paired evidence", time_bin,
        run.analysis.is_sequential,
        analysis_start_t=START, analysis_end_t=END,
        reference_snr_correction_db=run.context.reference_snr_correction_db,
        count_label=labels["fig_joint_spot_count"],
        chronological_title=labels["fig_selected_compare_chronological_title"],
        chronological_x_label=labels["fig_segment_chronological_x"],
        chronological_unavailable_text=labels["fig_compare_chronological_unavailable"],
        metric_axis_label="Paired delta SNR (dB)",
        folded_title=labels["fig_selected_compare_folded_title"],
        folded_x_label=labels["fig_segment_utc_hour_x"],
        folded_date_annotation=labels["fig_segment_dates_folded"].replace("{count}", "{utc_date_count}"),
        density_label=labels["fig_relative_joint_spot_density"],
        folded_unavailable_text=labels["fig_segment_folded_unavailable"],
        median_focus_axis_label=labels["fig_compare_median_focus_axis"],
        median_label=labels["fig_median_label"],
        bin_median_label=labels["fig_temporal_bin_median"],
        bin_iqr_label=labels["fig_temporal_bin_iqr"],
        time_bin_options=(time_bin,),
    )


def _joint_survival_connections(reports, pairs):
    """Bind eligible production pairs to their two exact plotted endpoints.

    These are identity guides only: no pairing is inferred from paper pixels,
    graphical proximity, or Target-active survival without Joint eligibility.
    """
    report_times = pd.to_datetime(reports.utc, utc=True)
    connections = []
    for pair in pairs.sort_values(["plot_time", "grid"]).itertuples():
        timestamp = pd.Timestamp(pair.plot_time)
        endpoints = reports[report_times.eq(timestamp) & reports.peer_grid.eq(pair.grid)]
        if len(endpoints) != 2 or set(endpoints.series) != set(SERIES_COLORS):
            raise ValueError("A Joint survival guide requires both exact full-locator report endpoints")
        if not endpoints.passes_target_active_gate.all():
            raise ValueError("Both Joint survival endpoints must be retained by production filtering")
        snrs = endpoints.set_index("series").snr_at_37_dbm
        if not np.isclose(snrs.loc["KP4MD"] - snrs.loc["WB6RQN"], pair.metric, rtol=0, atol=1e-9):
            raise ValueError("Joint survival endpoints must preserve the production paired Delta SNR")
        connections.append({
            "utc": timestamp.isoformat(), "peer_grid": pair.grid,
            "target_snr_at_37_dbm": float(snrs.loc["KP4MD"]),
            "reference_snr_at_37_dbm": float(snrs.loc["WB6RQN"]),
            "paired_delta_snr_db": float(pair.metric),
        })
    return connections


@synchronized_matplotlib
def draw_overlay(image_path, reports, run, direction, output_path, anchor_count):
    """Compose the source, report reconstruction and unmodified native view."""
    figure_number = 6 if direction == "RX" else 7
    header = DEMO_PDF_HEADERS[f"milazzo_figure{figure_number}"]
    pairs = paired_evidence_points(run)
    recipe = _production_temporal_recipe(run)
    fig = render_selected_evidence_export_figure(recipe)
    if fig is None:
        raise ValueError("The Milazzo paired evidence must produce a native figure")
    delta_axes = next(axis for axis in fig.axes if axis.get_gid() == "compare-temporal-chronological-axis")
    colorbar_axes = next(axis for axis in fig.axes if axis.get_gid() == "compare-temporal-colorbar-axis")
    for axis in list(fig.axes):
        if axis not in (delta_axes, colorbar_axes):
            axis.remove()
    for text in list(fig.texts):
        text.remove()
    _style_figure_for_paper(fig)
    fig.set_size_inches(24, 16.2)
    fig.set_facecolor("white")
    add_demo_pdf_header(fig, header)
    fig.text(.25, .835, "Panel A - Original image from publication", ha="center", fontsize=17, weight="bold", color=INK)
    fig.text(.75, .835, "Panel B - Reconstruction", ha="center", fontsize=17, weight="bold", color=INK)
    source_axes = fig.add_axes([.025, .517, .465, .301])
    with Image.open(image_path) as source_image:
        source_axes.imshow(source_image)
    source_axes.axis("off")
    source_axes.set_gid("milazzo-original-publication")

    source_axes.apply_aspect()
    source_bounds = source_axes.get_position()
    # Measure the actual displayed source image after its aspect-ratio inset.
    # Both source images share these printed graph and legend pixel bounds.
    paper_plot_left = source_bounds.x0 + source_bounds.width * 78.5 / 1317
    paper_plot_width = source_bounds.width * 1086 / 1317
    paper_plot_bottom = source_bounds.y0 + source_bounds.height * (1 - 554.5 / 656)
    paper_plot_height = source_bounds.height * 450 / 656
    paper_legend_left = source_bounds.x0 + source_bounds.width * 1198.5 / 1317
    direction_note = fig.text(
        source_bounds.x0 + source_bounds.width / 2, .499,
        "Original publication image retained in Panel A;\nits printed direction is contradicted by the matched reports.",
        ha="center", va="top", fontsize=13, color=MUTED, linespacing=1.3,
    )
    reconstruction_left = .5 + paper_plot_left
    reconstruction_width = paper_plot_width
    native_bottom = .1435
    axes = fig.add_axes([reconstruction_left, paper_plot_bottom, reconstruction_width, paper_plot_height])
    axes.set_gid("milazzo-report-reconstruction")
    with Image.open(image_path) as source_image:
        underlay = axes.imshow(
            source_image, origin="upper", aspect="auto", interpolation="nearest",
            extent=_paper_image_extent(source_image.size, direction), alpha=1, zorder=0,
        )
    underlay.set_gid("milazzo-original-reconciliation-underlay")
    for series, color in SERIES_COLORS.items():
        subset = reports[reports.series.eq(series)]
        timestamps = pd.to_datetime(subset.utc, utc=True)
        axes.scatter(timestamps, subset.snr_at_37_dbm, s=65, facecolors="none", edgecolors=color, linewidths=1.4, zorder=4)
        retained = subset.passes_target_active_gate
        gate_rings = axes.scatter(timestamps[retained], subset.snr_at_37_dbm[retained], s=155, facecolors="none", edgecolors=GATE_RING_COLOR, linewidths=1.1, zorder=5)
        gate_rings.set_gid(f"target-active-gate-rings-{series}")
        gate_rings.set_path_effects([patheffects.Stroke(linewidth=3.2, foreground="white"), patheffects.Normal()])
    if direction == "TX":
        unmatched = diagnostic_endpoint(reports, "WB6RQN", "2010-12-19T13:38:00Z")
        unmatched_time = pd.to_datetime(unmatched.utc, utc=True).iloc[0]
        unmatched_snr = unmatched.snr_at_37_dbm.iloc[0]
        axes.scatter([unmatched_time], [unmatched_snr], s=105, marker="x", color="#ab1671", linewidths=2, zorder=6)
        axes.annotate(f"Archive report, no visible paper marker\n19 Dec 13:38 | WB6RQN | {unmatched_snr:+g} dB at 37 dBm", (mdates.date2num(unmatched_time), unmatched_snr),
                      xytext=(.22, .86), textcoords="axes fraction", fontsize=12, color="#8a1259", zorder=12,
                      arrowprops={"arrowstyle": "->", "color": "#8a1259"},
                      bbox={"facecolor": "white", "edgecolor": "#dddddd", "alpha": .97})
        overlap_target = diagnostic_endpoint(reports, "KP4MD", "2010-12-20T10:34:00Z")
        overlap_reference = diagnostic_endpoint(reports, "WB6RQN", "2010-12-20T10:36:00Z")
        target_status = "passes gate" if overlap_target.passes_target_active_gate.iloc[0] else "does not pass"
        reference_status = "passes gate" if overlap_reference.passes_target_active_gate.iloc[0] else "does not pass"
        axes.annotate(f"20 Dec 10:34 KP4MD: {target_status}\n20 Dec 10:36 WB6RQN: {reference_status}",
                      (mdates.date2num(pd.to_datetime(overlap_target.utc, utc=True).iloc[0]), overlap_target.snr_at_37_dbm.iloc[0]),
                      xytext=(.52, .74), textcoords="axes fraction", fontsize=12, color=GATE_RING_COLOR, zorder=12,
                      arrowprops={"arrowstyle": "->", "color": GATE_RING_COLOR},
                      bbox={"facecolor": "white", "edgecolor": "#dddddd", "alpha": .97})
    axes.set_xlim(START, END)
    axes.set_ylim((-30, 5) if direction == "RX" else (-30, 0))
    axes.set_ylabel("SNR dB", fontsize=14, color=INK)
    axes.set_xlabel("Time UTC", fontsize=14, color=INK)
    axes.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 6, 12, 18], tz=timezone.utc))
    axes.xaxis.set_major_formatter(mdates.DateFormatter("%d Dec\n%H:%M", tz=timezone.utc))
    axes.tick_params(labelsize=12, colors=MUTED)
    # The opaque source already supplies the printed grid and connecting lines.
    axes.grid(False)
    report_handles = [Line2D([], [], marker="o", linestyle="none", markerfacecolor="none", markeredgecolor=color,
                      markersize=9, label=f"Pre-gate SQL diagnostic: {series} (B)") for series, color in SERIES_COLORS.items()]
    report_handles.append(Line2D([], [], marker="o", linestyle="none", markerfacecolor="none", markeredgecolor=GATE_RING_COLOR,
                          markersize=13, label="Outer ring: retained by production gate and Inspector (B)"))
    native_legend = delta_axes.get_legend()
    native_handles = list(native_legend.legend_handles)
    native_labels = [f"{text.get_text()} (C)" for text in native_legend.texts]
    native_legend.remove()

    explanation = ("44 / 44 paper markers match exactly in SNR. All reports are at 5 W: paper SNR = SQL normalized SNR + 7 dB."
                   if direction == "RX" else f"{anchor_count} / {anchor_count} compact paper anchors match exactly in SNR. All 76 archived TX reports in the plotted window are reconstructed in Panel B.")
    normalization_note = ("Common 37 dBm scale: KP4MD raw SNR unchanged; WB6RQN 2 W reports gain 4 dB." if direction == "TX"
                          else "Hollow circles show exact report times; the original image has finite graphical resolution. No fitted axis shift or SNR offset.")
    retained_reports = reports[reports.passes_target_active_gate]
    retained_counts = retained_reports.series.value_counts()
    gate_note = (f"Outer rings: {len(retained_reports)}/{len(reports)} reports pass the gate "
                 f"({retained_counts.get('KP4MD', 0)} KP4MD + {retained_counts.get('WB6RQN', 0)} WB6RQN). Gate survival does not imply a Joint pair.")
    caption_background = {"facecolor": "white", "edgecolor": "none", "pad": 3}
    native_heading = fig.text(.75, .424, "Panel C - WSPRadar view", ha="center", fontsize=17, weight="bold", color=INK, bbox=caption_background)
    native_caption = fig.text(reconstruction_left, .407, f"WSPRadar paired evidence after gating: {len(pairs)} pairs |\nKP4MD - WB6RQN | full locator identity", fontsize=13, color=INK, va="top", linespacing=1.3, bbox=caption_background)
    delta_axes.set_position([reconstruction_left, native_bottom, reconstruction_width, paper_plot_height])
    colorbar_axes.set_box_aspect(None)
    colorbar_axes.set_aspect("auto")
    colorbar_axes.set_position([.5 + paper_legend_left, native_bottom, .006, paper_plot_height])
    delta_axes.tick_params(labelsize=12)
    delta_axes.xaxis.label.set_fontsize(13)
    delta_axes.yaxis.label.set_fontsize(13)
    delta_axes.set_ylabel(delta_axes.get_ylabel().replace(" · ", "\n"))
    delta_axes.title.set_fontsize(13)
    colorbar_axes.tick_params(labelsize=12)
    colorbar_axes.yaxis.label.set_fontsize(13)
    colorbar_axes.set_ylabel(colorbar_axes.get_ylabel().replace(" (", "\n("))
    joint_connections = _joint_survival_connections(reports, pairs)
    connection_artists = []
    for connection in joint_connections:
        utc_coordinate = mdates.date2num(pd.Timestamp(connection["utc"]))
        endpoint_snrs = [connection["target_snr_at_37_dbm"], connection["reference_snr_at_37_dbm"]]
        axes.plot([utc_coordinate, utc_coordinate], endpoint_snrs,
                  color=MUTED, alpha=.45, linewidth=.8, linestyle=(0, (3, 4)), zorder=3)
        guide = ConnectionPatch(
            xyA=(utc_coordinate, min(endpoint_snrs)), coordsA=axes.transData,
            xyB=(utc_coordinate, connection["paired_delta_snr_db"]), coordsB=delta_axes.transData,
            arrowstyle="-", color=MUTED, alpha=.32, linewidth=.8,
            linestyle=(0, (3, 5)), zorder=1, clip_on=False,
        )
        guide.set_gid(f"milazzo-joint-survival-{connection['utc']}-{connection['peer_grid']}")
        fig.add_artist(guide)
        connection_artists.append(guide)
    for locator, group in pairs.groupby("grid", observed=True):
        pair_markers = delta_axes.scatter(pd.to_datetime(group.plot_time, utc=True), group.metric, s=40, marker="o", facecolors="none", edgecolors=INK, linewidths=1.2, zorder=10)
        pair_markers.set_gid(f"milazzo-exact-pairs-{locator}")
        for row in group.itertuples():
            annotation_offset = (-24, -18) if locator == "DO34" else (9, 11)
            delta_axes.annotate(f"{locator}: {row.metric:+.0f}", (mdates.date2num(pd.Timestamp(row.plot_time)), row.metric),
                                xytext=annotation_offset, textcoords="offset points", ha="center", fontsize=12, color=INK,
                                bbox={"facecolor": "white", "alpha": .85, "edgecolor": "none", "pad": 1}, zorder=11)
    exact_pair_handle = Line2D([], [], marker="o", linestyle="none", markerfacecolor="none", markeredgecolor=INK, markersize=7)
    # Each key sits with its own evidence panel. Give the two report series
    # equal space, with the longer gate meaning on a full-width second row.
    report_series_legend = fig.legend(
        handles=report_handles[:2], loc="upper left", bbox_to_anchor=(reconstruction_left, .488, reconstruction_width, 0), mode="expand",
        ncol=2, frameon=True, facecolor="white", edgecolor="white", framealpha=1, fontsize=12, borderaxespad=0, handletextpad=1,
    )
    gate_legend = fig.legend(handles=report_handles[2:], loc="upper left", bbox_to_anchor=(reconstruction_left, .459),
                            frameon=True, facecolor="white", edgecolor="white", framealpha=1, fontsize=12, borderaxespad=0, handletextpad=1)
    native_summary_legend = fig.legend(
        handles=native_handles, labels=native_labels, loc="upper left",
        bbox_to_anchor=(reconstruction_left, .077, reconstruction_width, 0), mode="expand",
        ncol=2, frameon=False, fontsize=12, borderaxespad=0,
    )
    exact_pair_legend = fig.legend(
        handles=[exact_pair_handle], labels=["Exact Joint Spots, labelled by full locator and delta SNR (C)"],
        loc="upper left", bbox_to_anchor=(reconstruction_left, .050), frameon=False, fontsize=12, borderaxespad=0,
    )
    notes = [
        (explanation, "bold", INK),
        (normalization_note, "normal", INK),
        (gate_note, "bold", INK),
        (f"Panel C retains native {recipe['time_bin']} bins, relative density, median and IQR. Read the dB labels on its median-centered nonlinear axis; positive values favor KP4MD.", "normal", INK),
        ("Panel B: original dots and lines at full opacity beneath colored pre-gate SQL circles. Outer rings and Panel C pairs: current production gate, map and Inspector results.", "normal", MUTED),
        ("Faint dashed guides link each retained Joint Spot to its two same-cycle, full-locator reports in Panel B. Unlinked reports remain visible but do not create a Joint Spot; these guides are not interpolated measurements.", "normal", MUTED),
        ("RX gate scope: supplied VE6PDQ path only. Other transmitters could establish Target activity for an unringed report in the full archive."
         if direction == "RX" else "Gate counts refer only to 19 Dec 12:00-20 Dec 20:00 UTC. Target activity is checked across all captured receivers in the exact WSPR cycle.", "normal", MUTED),
        ("The five RX pairs retain both full locator identities, DO34 and DO34ir; plotted agreement does not establish antenna gain."
         if direction == "RX" else "One Joint Spot gives one populated density cell at -2 dB; it cannot establish a time trend or direction-independent antenna gain.", "normal", MUTED),
        ("Source: qsl.net/kp4md/wspr.htm | Current generated WSPRadar SQL executed offline through the regression SQLite adapter; not native ClickHouse.", "normal", MUTED),
    ]
    note_top = .438
    for note, weight, color in notes:
        lines = textwrap.wrap(note, width=88, break_long_words=False, break_on_hyphens=False)
        fig.text(.055, note_top, "\n".join(lines), fontsize=13, weight=weight, color=color, va="top", linespacing=1.25)
        note_top -= (len(lines) * 16.25 + 8) / (16.2 * 72)
    if note_top < .025:
        raise ValueError("Milazzo explanatory text exceeds its lower-left panel")
    add_demo_pdf_footer(fig, right=.96, bottom=.011)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    figure_coordinates = fig.transFigure.inverted()
    caption_bounds = native_caption.get_bbox_patch().get_window_extent(renderer)
    native_title_bounds = delta_axes.title.get_window_extent(renderer)
    if caption_bounds.y0 <= native_title_bounds.y1:
        raise ValueError("The Panel C caption must remain above its native chart title")
    layout_checks = {
        "panel_a_plot_bounds": [paper_plot_left, paper_plot_bottom, paper_plot_width, paper_plot_height],
        "panel_a_legend_left": paper_legend_left,
        "panel_b_plot_bounds": list(axes.get_position().bounds),
        "panel_b_time_limits": list(axes.get_xlim()),
        "panel_c_time_limits": list(delta_axes.get_xlim()),
        "panel_c_plot_bounds": list(delta_axes.get_position().bounds),
        "panel_c_density_bounds": list(colorbar_axes.get_position().bounds),
        "panel_c_caption_bounds": list(caption_bounds.transformed(figure_coordinates).bounds),
        "panel_c_native_title_bounds": list(native_title_bounds.transformed(figure_coordinates).bounds),
        "panel_c_heading_bounds": list(native_heading.get_bbox_patch().get_window_extent(renderer).transformed(figure_coordinates).bounds),
        "panel_b_series_legend_bounds": list(report_series_legend.get_window_extent(renderer).transformed(figure_coordinates).bounds),
        "panel_b_gate_legend_bounds": list(gate_legend.get_window_extent(renderer).transformed(figure_coordinates).bounds),
        "panel_c_summary_legend_bounds": list(native_summary_legend.get_window_extent(renderer).transformed(figure_coordinates).bounds),
        "panel_c_exact_legend_bounds": list(exact_pair_legend.get_window_extent(renderer).transformed(figure_coordinates).bounds),
        "direction_note_bounds": list(direction_note.get_window_extent(renderer).transformed(figure_coordinates).bounds),
        "panel_a_image_bounds": list(source_bounds.bounds),
        "joint_survival_guide_count": len(connection_artists),
        "joint_survival_guide_endpoints": [
            {"source_figure_xy": figure_coordinates.transform(axes.transData.transform(guide.xy1)).tolist(),
             "native_figure_xy": figure_coordinates.transform(delta_axes.transData.transform(guide.xy2)).tolist()}
            for guide in connection_artists
        ],
    }
    fig.savefig(output_path, dpi=160)
    for artist in fig.findobj():
        if artist.get_rasterized():
            artist.set_rasterized(False)
        if isinstance(artist, QuadMesh):
            artist.set_edgecolor("face")
            artist.set_linewidth(.04)
    with matplotlib.rc_context({"pdf.fonttype": 42}):
        fig.savefig(output_path.with_name(f"WSPRadar_Demo_Milazzo_Figure{figure_number}.pdf"), metadata={
            **demo_pdf_metadata(header),
            "Subject": "Original publication, vector report reconstruction and native WSPRadar temporal evidence",
            "CreationDate": None, "ModDate": None,
        })
    density, summaries, _, _ = _compare_temporal_profile_values(recipe["prepared_profiles"]["chronological"][recipe["time_bin"]])
    if int(density.sum()) != len(pairs):
        raise ValueError("Native temporal density must retain every eligible Milazzo pair")
    plt.close(fig)
    return {"page_inches": [24, 16.2], "png_pixels": [3840, 2592], "paired_observations": len(pairs),
            "full_peer_locators": sorted(pairs.grid.unique().tolist()), "paired_delta_snr_db": pairs.metric.tolist(),
            "native_time_bin": recipe["time_bin"], "native_density_total": int(density.sum()),
            "native_populated_bins": int(summaries["count"].gt(0).sum()),
            "native_renderer": "render_selected_evidence_export_figure", "native_axis": "median-centered nonlinear dB",
            "panel_a": "Unmodified original source image, including the printed direction",
            "panel_b": "Complete pre-gate SQL endpoint reconstruction over the original image at full opacity, with production-retained outer rings",
            "panel_b_underlay": {"opacity": 1.0, "calibration": "Existing source-only paper_coordinates transform; no fitted shift or offset"},
            "layout": "B above C with identical graph widths and chronological UTC limits; A and complete notes on the left; separate B/C legends",
            "joint_survival_connections": joint_connections,
            "layout_checks": layout_checks,
            "panel_c": "Native chronological evidence with exact Joint Spot annotations"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--figure6", required=True, type=Path)
    parser.add_argument("--figure7", required=True, type=Path)
    parser.add_argument("--output-directory", required=True, type=Path)
    args = parser.parse_args()
    args.output_directory.mkdir(parents=True, exist_ok=True)
    # Image-only extraction precedes archive matching and application execution.
    anchors7 = extract_figure7_anchors(args.figure7)
    anchors7.to_csv(args.output_directory / "figure7_paper_anchors.csv", index=False)
    sys.path[:0] = [str(ROOT), str(ROOT / "tests/regression")]
    from test_milazzo_reference import _calculate_run
    rx_directory = FIXTURES / "milazzo_fig6_rx_v1"
    tx_directory = FIXTURES / "milazzo_tx_reference_v1"
    rx_run = _calculate_run(pd.read_csv(rx_directory / "source_rows.csv", float_precision="round_trip"),
        configuration_document=json.loads((rx_directory / "rx_reference.config").read_text(encoding="utf-8")))
    tx_run = _calculate_run(pd.read_csv(tx_directory / "source_rows.csv", float_precision="round_trip"))
    rx_reports = sql_endpoint_reports(rx_run, "RX")
    tx_reports = sql_endpoint_reports(tx_run, "TX")
    anchors6 = pd.read_csv(rx_directory / "paper_markers.csv").rename(columns={
        "utc_readout_approx": "paper_utc", "snr_db_approx": "paper_snr_db",
    })
    anchors6["marker_id"] = anchors6.series + "_" + anchors6.visible_marker_number.astype(str)
    anchors6["time_tolerance_seconds"] = 240
    anchors6["snr_tolerance_db"] = 0.25
    matches6 = match_anchors(anchors6, rx_reports)
    matches7 = match_anchors(anchors7, tx_reports)
    presentation_checks = {}
    for direction, number, raster, reports, matches, run in (
        ("RX", 6, args.figure6, rx_reports, matches6, rx_run),
        ("TX", 7, args.figure7, tx_reports, matches7, tx_run),
    ):
        shutil.copyfile(raster, args.output_directory / f"paper_figure{number}.jpg")
        reports.to_csv(args.output_directory / f"figure{number}_sql_endpoint_reports.csv", index=False)
        matches.to_csv(args.output_directory / f"figure{number}_anchor_matches.csv", index=False)
        presentation_checks[f"figure{number}"] = draw_overlay(raster, reports, run, direction, args.output_directory / f"figure{number}_{direction.lower()}_overlay.png", len(matches))
    summary = {
        "source_article": "https://www.qsl.net/kp4md/wspr.htm",
        "source_figures": {
            "6": {"url": "https://www.qsl.net/kp4md/WSPR%2040m%20at%20VE6PDQ.JPG",
                  "sha256": hashlib.sha256(args.figure6.read_bytes()).hexdigest()},
            "7": {"url": "https://www.qsl.net/kp4md/WSPR%2040m%20from%20VE6PDQ.JPG",
                  "sha256": hashlib.sha256(args.figure7.read_bytes()).hexdigest()},
        },
        "figure6": {"direction": "RX", "sql_reports": len(rx_reports), "matched_anchors": len(matches6),
                    "max_time_error_seconds": float(matches6.time_error_seconds.abs().max())},
        "figure7": {"direction": "TX", "sql_reports": len(tx_reports), "matched_compact_anchors": len(matches7),
                    "anchor_series_counts": anchors7.series.value_counts().to_dict(),
                    "max_time_error_seconds": float(matches7.time_error_seconds.abs().max()),
                    "anchor_scope": "Compact colored components only; overlapping/merged markers are not individually counted",
                    "additional_report": "WB6RQN 2010-12-19 13:38 UTC, raw -6 dB at 33 dBm; -2 dB at 37 dBm; no visible marker",
                    "overlap_note": "WB6RQN 20 Dec 10:36 at -19 dB is near the KP4MD 10:34 marker at -19 dB; not an isolated red anchor"},
        "power_scale": "SQL normalized to 30 dBm plus exactly 7 dB = common 37 dBm. RX all nominal 5 W; TX KP4MD 5 W and WB6RQN 2 W within plot window.",
        "time_shift_fit": False, "snr_offset_fit": False,
        "figure7_axis_calibration": {"x_12_utc_dec19": 78, "x_20_utc_dec20": 1164,
                                     "y_zero_db": 104, "y_minus30_db": 554},
        "figure7_extraction": "Blue B>150,R<100,G<120; red R>150,G<120,B<120; 3x3 erosion; 4-neighbor components; 35..90 pixels and width/height <=10; source-only rule to avoid merged centers. Integer SNR read from calibrated ordinate, checked against visible annotations.",
        "figure7_match_rule": "Require one same-series report within 240 seconds and 0.25 dB of each image-derived anchor at the declared common 37 dBm scale; no archive-based axis fitting",
        "runtime_scope": "Current generated SQL through regression SQLite adapter, followed by production filtering and inspector preparation. No live provider calls or native ClickHouse verification.",
        "plot_input_boundary": {
            "colored_rings": "Deliberate pre-gate diagnostic: current generated SQL endpoint components, including reports ineligible for Benchmark results",
            "outer_rings": "Membership in current apply_post_fetch_filters output, verified against the retained production Inspector outcome for the exact cycle/callsign/full-locator identity",
            "lower_panel": "Current _compare_joint_evidence_points(require_paired_eligible=True) output after map, Inspector and threshold preparation; no offline Delta SNR or pair-eligibility calculation",
            "expected_files": "Not used as plotting inputs; independent frozen values remain regression assertions",
            "presentation_only": "Fixed paper-axis transform and common 30 to 37 dBm shift; paired Delta SNR unchanged",
            "unexercised": "Native ClickHouse, live provider, runtime cache and full interactive session",
        },
        "target_active_gate": {
            "rule": "global_time_slot",
            "description": "At least one captured Target report in the exact 120-second WSPR cycle across all eligible peers; no graphical time tolerance or same-peer requirement",
            "plot_start_utc": START.isoformat(), "plot_end_utc_exclusive": END.isoformat(),
            "scope": {"figure6": "Captured VE6PDQ path only; other transmitters may supply missing Target-activity witnesses in the full archive",
                      "figure7": "All captured receivers contribute Target-activity witnesses; plotted reports are the VE6PDQ path"},
            "sql_reports_retained": {"figure6": int(rx_reports.passes_target_active_gate.sum()),
                                     "figure7": int(tx_reports.passes_target_active_gate.sum())},
            "matched_anchors_retained": {"figure6": int(matches6.passes_target_active_gate.sum()),
                                         "figure7": int(matches7.passes_target_active_gate.sum())},
            "rendering": "Existing colored SQL rings remain; a larger charcoal ring with white separation marks each gate-retained endpoint",
            "joint_pairing": "Gate survival alone does not establish a Joint pair; full locator identity still applies",
        },
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "footer_text": DEMO_PDF_FOOTER_TEXT,
        "presentation_revision": "three-panel-native-temporal-2026-09-27",
        "presentation_checks": presentation_checks,
    }
    (args.output_directory / "overlay_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
