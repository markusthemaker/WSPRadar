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

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib import patheffects
import numpy as np
import pandas as pd
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.analysis_context import solar_path_state
from core.matplotlib_runtime import synchronized_matplotlib

FIXTURES = ROOT / "tests/regression/reference_fixtures"
START = datetime(2010, 12, 19, 12, tzinfo=timezone.utc)
END = datetime(2010, 12, 20, 20, tzinfo=timezone.utc)
SERIES_COLORS = {"KP4MD": "#008864", "WB6RQN": "#b86500"}
GATE_RING_COLOR = "#30343b"


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
    """Keep every plotted endpoint and label exact captured-source gate status."""
    if solar_path_state(run.context.solar_state) is not None or run.context.exclude_moving_stations:
        raise ValueError("Milazzo overlay gating requires the frozen all-solar, moving-stations-included scope")
    active_time_slots = set(run.sql_rows.loc[run.sql_rows.has_u.gt(0), "time_slot"])
    retained_keys = set(run.processed[["time_slot", "peer_sign", "peer_grid"]].itertuples(index=False, name=None))
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
                passes_target_active_gate = row.time_slot in active_time_slots
                is_retained = (row.time_slot, row.peer_sign, row.peer_grid) in retained_keys
                if passes_target_active_gate != is_retained:
                    raise ValueError("A plotted endpoint has an additional post-fetch exclusion; gate survival must remain distinct")
                reports.append({
                    "direction": direction, "series": series, "time_slot": row.time_slot,
                    "utc": timestamp.isoformat(), "peer_grid": row.peer_grid,
                    "sql_snr_at_30_dbm": normalized, "snr_at_37_dbm": normalized + 7,
                    "passes_target_active_gate": passes_target_active_gate,
                })
    return pd.DataFrame(reports)


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


@synchronized_matplotlib
def draw_overlay(image_path, reports, run, direction, output_path, anchor_count):
    figure_number = 6 if direction == "RX" else 7
    direction_text = (
        "VE6PDQ transmitting to KP4MD / WB6RQN" if direction == "RX"
        else "KP4MD / WB6RQN transmitting to VE6PDQ"
    )
    fig = plt.figure(figsize=(16, 10.8), facecolor="white")
    fig.text(0.04, 0.966, f"Milazzo Figure {figure_number} | Reconciled {direction} direction", fontsize=21, weight="bold")
    fig.text(0.04, 0.932, direction_text, fontsize=14)
    fig.text(0.04, 0.906, "Original publication image retained below; its printed direction is contradicted by the matched reports.", fontsize=10, color="#555555")
    axes = fig.add_axes([0.025, 0.31, 0.95, 0.57])
    axes.imshow(Image.open(image_path))
    # Suppress only the embedded publication title in this review rendering;
    # preserve source JPEGs, plot coordinates, and every evidence annotation.
    axes.add_patch(Rectangle((535, 18), 250, 34, facecolor="white", edgecolor="none", zorder=2))
    for series, color in SERIES_COLORS.items():
        subset = reports[reports.series.eq(series)]
        minutes = (pd.to_datetime(subset.utc, utc=True) - pd.Timestamp(START)).dt.total_seconds() / 60
        if direction == "RX":
            calibration = json.loads((FIXTURES / "milazzo_fig6_rx_v1/paper_features_original.json").read_text())["calibration"]
            x = (minutes - calibration["minutes_intercept"]) / calibration["minutes_from_axis_start_per_x_pixel"]
            y = (subset.snr_at_37_dbm - calibration["snr_db_intercept"]) / calibration["snr_db_per_y_pixel"]
        else:
            x = 78 + minutes * 1086 / 1920
            y = 104 - subset.snr_at_37_dbm * 15
        axes.scatter(x, y, s=115, facecolors="none", edgecolors=color, linewidths=1.3, zorder=4)
        retained = subset.passes_target_active_gate
        gate_rings = axes.scatter(x[retained], y[retained], s=250, facecolors="none",
                                  edgecolors=GATE_RING_COLOR, linewidths=1.15, zorder=5)
        gate_rings.set_gid(f"target-active-gate-rings-{series}")
        gate_rings.set_path_effects([
            patheffects.Stroke(linewidth=3.2, foreground="white"), patheffects.Normal(),
        ])
    if direction == "TX":
        x = 78 + 98 * 1086 / 1920
        axes.scatter([x], [134], s=150, marker="x", color="#ab1671", linewidths=2, zorder=5)
        axes.annotate("Archive report, no visible paper marker\n19 Dec 13:38 | WB6RQN | -2 dB at 37 dBm", (x, 134),
                      xytext=(365, 122), fontsize=8.7, color="#8a1259",
                      arrowprops={"arrowstyle": "->", "color": "#8a1259"},
                      bbox={"facecolor": "white", "edgecolor": "#dddddd", "alpha": 0.95})
        overlap_x = 78 + (24 * 60 - 86) * 1086 / 1920
        axes.annotate("20 Dec 10:34 KP4MD: passes gate\n20 Dec 10:36 WB6RQN: does not pass", (overlap_x, 389),
                      xytext=(690, 205), fontsize=8.5, color=GATE_RING_COLOR,
                      arrowprops={"arrowstyle": "->", "color": GATE_RING_COLOR},
                      bbox={"facecolor": "white", "edgecolor": "#dddddd", "alpha": 0.95})
    axes.set_xlim(-0.5, 1316.5)
    axes.set_ylim(655.5, -0.5)
    axes.axis("off")
    handles = [Line2D([], [], marker="o", linestyle="none", markerfacecolor="none",
                      markeredgecolor=color, markersize=9, label=f"WSPRadar SQL: {series}")
               for series, color in SERIES_COLORS.items()]
    handles.append(Line2D([], [], marker="o", linestyle="none", markerfacecolor="none",
                          markeredgecolor=GATE_RING_COLOR, markersize=13,
                          label="Outer ring: passes Target-Active Gate in captured source"))
    fig.legend(handles=handles, loc="upper right", bbox_to_anchor=(0.96, 0.900), frameon=False, fontsize=9)
    if direction == "RX":
        explanation = "44 / 44 paper markers match exactly in SNR. All reports are at 5 W: paper SNR = SQL normalized SNR + 7 dB."
    else:
        explanation = f"{anchor_count} / {anchor_count} compact paper anchors match exactly in SNR. All 76 archived TX reports in the plotted window are overlaid."
    fig.text(0.055, 0.305, explanation, fontsize=10.5, weight="bold")
    fig.text(0.055, 0.280, "Common 37 dBm scale: KP4MD raw SNR unchanged; WB6RQN 2 W reports gain 4 dB." if direction == "TX"
             else "Hollow circles show exact report times; the original image has finite graphical resolution. No fitted axis shift or SNR offset.", fontsize=10)
    retained_reports = reports[reports.passes_target_active_gate]
    retained_counts = retained_reports.series.value_counts()
    fig.text(0.055, 0.255,
             f"Outer rings: {len(retained_reports)}/{len(reports)} reports pass the gate "
             f"({retained_counts.get('KP4MD', 0)} KP4MD + {retained_counts.get('WB6RQN', 0)} WB6RQN). "
             "Gate survival does not imply a Joint pair.", fontsize=9.5, weight="bold")
    pairs = run.units[run.units.outcome.eq("joint") & run.units.peer_sign.eq("VE6PDQ")].copy()
    pairs = pairs[(pd.to_datetime(pairs.evidence_utc, utc=True) >= START) & (pd.to_datetime(pairs.evidence_utc, utc=True) < END)]
    delta_axes = fig.add_axes([0.093, 0.103, 0.78, 0.125])
    for locator, group in pairs.groupby("peer_grid", observed=True):
        delta_axes.scatter(pd.to_datetime(group.evidence_utc, utc=True), group.metric, s=55, label=locator)
        for row in group.itertuples():
            annotation_offset = (-10, 9) if locator == "DO34" else (9, 18)
            delta_axes.annotate(f"{row.metric:+.0f}", (mdates.date2num(pd.Timestamp(row.evidence_utc)), row.metric),
                                xytext=annotation_offset, textcoords="offset points", ha="center", fontsize=9)
    delta_axes.set_xlim(START, END)
    delta_axes.set_ylim((-4, 32) if direction == "RX" else (-5, 1))
    delta_axes.axhline(0, color="#777777", linewidth=0.6)
    delta_axes.grid(alpha=0.2)
    delta_axes.set_ylabel("Paired delta SNR (dB)", fontsize=9)
    delta_axes.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 6, 12, 18], tz=timezone.utc))
    delta_axes.xaxis.set_major_formatter(mdates.DateFormatter("%d Dec\n%H:%M UTC", tz=timezone.utc))
    delta_axes.tick_params(labelsize=9)
    delta_axes.set_title(f"WSPRadar paired evidence after gating: {len(pairs)} pairs | KP4MD - WB6RQN | full locator identity", loc="left", fontsize=10)
    delta_axes.legend(loc="upper right", fontsize=8, frameon=False)
    fig.text(0.055, 0.043, "Main overlay includes non-joint reports before the Target-Active Gate. Lower panel uses eligible same-cycle pairs; no gap interpolation.", fontsize=9)
    if direction == "RX":
        fig.text(0.055, 0.025, "RX gate scope: supplied VE6PDQ path only. Other transmitters could establish Target activity for an unringed report in the full archive.",
                 fontsize=8.2, color="#555555")
    else:
        fig.text(0.055, 0.025, "Gate counts refer only to 19 Dec 12:00–20 Dec 20:00 UTC. Target activity is checked across all captured receivers in the exact WSPR cycle.",
                 fontsize=8.2, color="#555555")
    fig.text(0.055, 0.009, "Source: qsl.net/kp4md/wspr.htm | Current generated WSPRadar SQL executed offline through the regression SQLite adapter; not native ClickHouse.", fontsize=8, color="#555555")
    fig.savefig(output_path, dpi=160)
    # Preserve real vector rings, annotations and paired-evidence artists.
    # Only the original publication image is an embedded raster in the PDF.
    with matplotlib.rc_context({"pdf.fonttype": 42}):
        fig.savefig(output_path.with_suffix(".pdf"), metadata={
            "Title": f"Milazzo Figure {figure_number}: reconciled {direction} direction",
            "Subject": "Publication raster with vector SQL reconciliation and Target-Active Gate rings",
            "CreationDate": None, "ModDate": None,
        })
    plt.close(fig)


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
    for direction, number, raster, reports, matches, run in (
        ("RX", 6, args.figure6, rx_reports, matches6, rx_run),
        ("TX", 7, args.figure7, tx_reports, matches7, tx_run),
    ):
        shutil.copyfile(raster, args.output_directory / f"paper_figure{number}.jpg")
        reports.to_csv(args.output_directory / f"figure{number}_sql_endpoint_reports.csv", index=False)
        matches.to_csv(args.output_directory / f"figure{number}_anchor_matches.csv", index=False)
        draw_overlay(raster, reports, run, direction, args.output_directory / f"figure{number}_{direction.lower()}_overlay.png", len(matches))
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
    }
    (args.output_directory / "overlay_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
