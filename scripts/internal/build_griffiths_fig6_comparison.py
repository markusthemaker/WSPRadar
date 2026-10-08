"""Presentation-only Figure 6 comparison; all frozen numerical inputs are read-only."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
from textwrap import fill

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests/regression"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import QuadMesh
from matplotlib.lines import Line2D
from matplotlib.colors import PowerNorm
import numpy as np
import pandas as pd
from PIL import Image

from config.demo_pdf_headers import DEMO_PDF_HEADERS
from core.matplotlib_runtime import matplotlib_operation_lock, dispose_agg_figure
from core.opportunity_engine import OPPORTUNITY_SLOT_SECONDS
from i18n import T
from scripts.internal.demo_pdf_footer import add_demo_pdf_footer, DEMO_PDF_FOOTER_TEXT
from scripts.internal.demo_pdf_header import add_demo_pdf_header, demo_pdf_metadata
from ui.plots.evidence_figures import (
    _compare_temporal_profile_values,
    _segment_temporal_evidence_export_recipe,
    render_segment_temporal_evidence_export_figure,
)
from ui.results_export import _style_figure_for_paper
from test_griffiths_temporal_reference import (
    _assert_paired_rows_match_reference, _canonical_paired_rows, _prepare_reference_run,
)

OUTPUT = ROOT / "tests/regression/reference_fixtures/griffiths_fig6_paper_v1"
PAPER = ROOT / "tests/regression/reference_fixtures/griffiths_fig6_paper_v1"
ARCHIVE = ROOT / "tests/regression/reference_fixtures/griffiths_fig6_diurnal_v1"
INK, MUTED, TEAL = "#172B3A", "#526572", "#008F8C"
MAGENTA, BACKGROUND = "#B5366F", "white"
DENSITY_COLOR_GAMMA = 0.7
OBSERVATION_ALPHA = 0.45
OBSERVATION_MARKER_AREA = 3.3
OBSERVATION_LEGEND_MARKER_DIAMETER = 6
DUPLICATE_COLOR = "#C43C39"
DIAGNOSTIC_PDF_URL = "../griffiths_fig3_paper_v1/WSPRadar_Demo_Griffiths_Figure3_diagnostic.pdf"
PAPER_URL = "https://www.wsprnet.org/drupal/sites/wsprnet.org/files/G3ZIL%20G4HZX%20WSPR%20Improving%20HF%20SNR-print.pdf"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def smooth_density(counts, sigma_time, sigma_snr):
    """Existing fixed comparison policy; no fitting to the source raster."""
    def kernel(sigma):
        offsets = np.arange(-int(np.ceil(3 * sigma)), int(np.ceil(3 * sigma)) + 1)
        weights = np.exp(-0.5 * (offsets / sigma) ** 2)
        return offsets, weights / weights.sum()
    offsets, weights = kernel(sigma_time)
    time_smoothed = sum(weight * np.roll(counts, int(offset), axis=1)
                        for offset, weight in zip(offsets, weights))
    offsets, weights = kernel(sigma_snr)
    padding = int(offsets[-1])
    padded = np.pad(time_smoothed, ((padding, padding), (0, 0)))
    return sum(weight * padded[padding + offset:padding + offset + len(counts)]
               for offset, weight in zip(offsets, weights))


def vertical_modes(density, hours, snr_centers):
    modes = []
    for column_index, hour in enumerate(hours):
        column = density[:, column_index]
        row = 1
        while row < len(column) - 1:
            last = row
            while last + 1 < len(column) and column[last + 1] == column[row]:
                last += 1
            if (last < len(column) - 1 and last - row <= 1
                    and column[row] > column[row - 1]
                    and column[last] > column[last + 1]):
                modes.append((float(hour), float((snr_centers[row] + snr_centers[last]) / 2)))
            row = last + 1
    return modes


def additional_report_combinations(reports, pairs, target_callsign, reference_callsign):
    """Build a diagnostic overlay without adding observations to production.

    Retain only identities selected by the production replay. A combination is
    additional when it uses a weaker report at either receiver, even when its
    difference equals the retained difference. Report IDs preserve provenance.
    The frozen archive already scopes the band, interval and local endpoints;
    this diagnostic helper does not replace production eligibility filtering.
    """
    reports = reports.copy()
    reports["time_slot"] = (
        pd.to_datetime(reports["time"], utc=True).dt.as_unit("s").astype("int64")
        // OPPORTUNITY_SLOT_SECONDS
    )
    reports["normalized_snr"] = reports["snr"].astype(int) - reports["power"].astype(int) + 30
    keys = ["time_slot", "tx_sign", "tx_loc"]
    target = reports.loc[reports["rx_sign"].eq(target_callsign)]
    reference = reports.loc[reports["rx_sign"].eq(reference_callsign)]
    expanded = target.merge(reference, on=keys, suffixes=("_target", "_reference"))
    selected = pairs.rename(columns={"peer_sign": "tx_sign", "peer_grid": "tx_loc"})
    expanded = expanded.merge(
        selected[keys + ["evidence_utc", "target_snr_db", "reference_snr_db"]],
        on=keys, how="inner", validate="many_to_one",
    )
    maxima = expanded.groupby(keys, observed=True)[
        ["normalized_snr_target", "normalized_snr_reference"]
    ].max().reset_index()
    checked = selected.merge(maxima, on=keys, how="left", validate="one_to_one")
    np.testing.assert_array_equal(checked["target_snr_db"], checked["normalized_snr_target"])
    np.testing.assert_array_equal(checked["reference_snr_db"], checked["normalized_snr_reference"])
    weaker = (
        expanded["normalized_snr_target"].lt(expanded["target_snr_db"])
        | expanded["normalized_snr_reference"].lt(expanded["reference_snr_db"])
    )
    additional = expanded.loc[weaker].copy()
    additional["delta_snr_db"] = additional["normalized_snr_target"] - additional["normalized_snr_reference"]
    times = pd.to_datetime(additional["evidence_utc"], utc=True)
    additional["utc_hour"] = times.dt.hour + times.dt.minute / 60 + times.dt.second / 3600
    return additional.sort_values(keys + ["id_target", "id_reference"]).reset_index(drop=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-directory", type=Path, default=OUTPUT)
    output_directory = parser.parse_args().output_directory
    output_directory.mkdir(parents=True, exist_ok=True)
    features = read_json(PAPER / "paper_features.json")
    point_annotations = read_json(PAPER / "paper_points.json")
    policy = read_json(PAPER / "comparison_policy.json")
    config = read_json(ARCHIVE / "demo.config")
    replay = _prepare_reference_run(ARCHIVE, ("1h", "3h", "6h", "24h"))
    pairs = _canonical_paired_rows(replay)
    _assert_paired_rows_match_reference(replay)
    points = pairs.rename(columns={"evidence_utc": "plot_time", "delta_snr_db": "metric"})
    selection = config["settings"]["core_parameters"]["time_selection"]
    labels = T["en"]
    recipe = _segment_temporal_evidence_export_recipe(
        points[["plot_time", "metric"]], "Figure 6 comparison", "1h", "Joint spots",
        analysis_start_t=selection["start_utc"], analysis_end_t=selection["end_utc"],
        reference_snr_correction_db=replay.context.reference_snr_correction_db,
        chronological_title=labels["fig_segment_chronological_delta"],
        chronological_x_label=labels["fig_segment_chronological_x"],
        chronological_unavailable_text=labels["fig_compare_chronological_unavailable"],
        metric_axis_label="Δ SNR (dB)", folded_title=labels["fig_segment_utc_hour_title"],
        folded_x_label=labels["fig_segment_utc_hour_x"], folded_date_annotation="{utc_date_count} dates",
        density_label=labels["fig_relative_joint_spot_density"],
        folded_unavailable_text=labels["fig_segment_folded_unavailable"],
        median_focus_axis_label=labels["fig_compare_median_focus_axis"],
        median_label=labels["fig_median_label"], bin_median_label=labels["fig_temporal_bin_median"],
        bin_iqr_label=labels["fig_temporal_bin_iqr"], time_bin_options=("1h", "3h", "6h", "24h"),
    )
    profiles = recipe["prepared_profiles"]
    counts, summary, hour_edges, hours = _compare_temporal_profile_values(profiles["folded"])
    snr_edges = np.asarray(profiles["y_edges"])
    snr_centers = (snr_edges[:-1] + snr_edges[1:]) / 2
    np.testing.assert_array_equal(hour_edges, np.arange(25))
    np.testing.assert_array_equal(np.diff(snr_edges), np.ones(len(snr_edges) - 1))
    assert counts.sum() == len(pairs) == 6459
    expected_summary = pd.read_csv(ARCHIVE / "expected_utc_hour.csv")
    for actual, expected in (("count", "joint_spots"), ("median", "median_delta_snr_db"),
                             ("q1", "q1_delta_snr_db"), ("q3", "q3_delta_snr_db")):
        np.testing.assert_array_equal(summary[actual], expected_summary[expected])
    expected_density = pd.read_csv(ARCHIVE / "expected_density_utc_hour.csv").pivot(
        index="delta_snr_bin_db", columns="bin_index", values="joint_spots")
    np.testing.assert_array_equal(counts, expected_density.to_numpy())
    density = smooth_density(counts, policy["smoothing"]["nominal_sigma_time_hours"],
                             policy["smoothing"]["nominal_sigma_snr_db"])
    modes = vertical_modes(density, hours, snr_centers)
    relative_density = density / density.max()
    utc_times = pd.to_datetime(pairs["evidence_utc"], utc=True)
    utc_hours = utc_times.dt.hour + utc_times.dt.minute / 60 + utc_times.dt.second / 3600
    deltas = pairs["delta_snr_db"]
    assert float(deltas.median()) == 5.0
    additional = additional_report_combinations(
        pd.read_parquet(ARCHIVE / "source_rows.parquet"), pairs,
        config["settings"]["core_parameters"]["callsign"],
        config["settings"]["comparison_parameters"]["reference_callsign"],
    )
    displayed_additional = additional.loc[additional["delta_snr_db"].between(-15, 25)]

    # C retains the actual production artists and nonlinear transform. Only
    # layout, export theme and font sizes change to accommodate the triptych.
    figure = render_segment_temporal_evidence_export_figure(recipe)
    assert figure is not None
    app_axis = next(axis for axis in figure.axes if axis.get_gid() == "compare-temporal-folded-axis")
    app_colorbar_axis = next(axis for axis in figure.axes if axis.get_gid() == "compare-temporal-colorbar-axis")
    chronological_axis = next(axis for axis in figure.axes if axis.get_gid() == "compare-temporal-chronological-axis")
    chronological_axis.remove()
    for text in list(figure.texts):
        text.remove()
    _style_figure_for_paper(figure)
    figure.set_size_inches(23, 12.5)
    figure.set_dpi(180)
    figure.set_facecolor(BACKGROUND)
    lefts, width, bottom, height = [.048, .365, .687], .255, .400, .350
    app_axis.set_position([lefts[2], bottom, .240, height])
    app_colorbar_axis.set_box_aspect(None)
    app_colorbar_axis.set_aspect("auto")
    app_colorbar_axis.set_position([.936, bottom, .007, height])
    app_axis.tick_params(labelsize=13)
    app_axis.xaxis.label.set_fontsize(14)
    app_axis.yaxis.label.set_fontsize(13)
    app_axis.title.set_fontsize(14)
    app_axis.title.set_y(1.025)
    app_colorbar_axis.tick_params(labelsize=12)
    app_colorbar_axis.yaxis.label.set_fontsize(12)
    app_legend = app_axis.get_legend()
    app_legend_handles = list(app_legend.legend_handles)
    assert len(app_legend_handles) == 3
    app_legend.remove()
    assert app_axis.get_yscale() == "function"
    median_artist = next(line for line in app_axis.lines if line.get_gid() == "compare-median-focus-center")
    np.testing.assert_array_equal(median_artist.get_ydata(), [5, 5])
    median_markers = next(artist for artist in app_axis.collections
                          if artist.get_gid() == "temporal-bin-median-markers")
    np.testing.assert_array_equal(median_markers.get_offsets()[:, 1], summary["median"])
    for quartile in ("q1", "q3"):
        line = next(line for line in app_axis.lines if line.get_gid() == f"temporal-bin-iqr-{quartile}")
        np.testing.assert_array_equal(line.get_ydata(), summary[quartile])

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "text.color": INK,
                         "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                         "axes.edgecolor": "#91A0A8"})
    left = figure.add_axes([lefts[0], bottom, width, height], facecolor="white")
    right = figure.add_axes([lefts[1], bottom, width, height], facecolor="white")
    axes = (left, right)
    add_demo_pdf_header(figure, DEMO_PDF_HEADERS["griffiths_figure6"])
    for x, title in zip(lefts, ("A  Original image from publication", "B  Reconstruction", "C  WSPRadar view")):
        figure.text(x + width/2, .791, title, ha="center", fontsize=17, weight="bold", color=INK)
    left.set_title("Original scatter and contours · linear dB", fontsize=14, weight="bold", pad=12)
    right.set_title("Smoothed observation density · linear dB", fontsize=14, weight="bold", pad=12)

    calibration = features["axes"]
    scale_hour = 24 / (calibration["x_one_day_px"] - calibration["x_zero_day_px"])
    scale_snr = 40 / (calibration["y_negative_15_db_px"] - calibration["y_positive_25_db_px"])
    def hour_from_pixel(pixel):
        return (pixel - calibration["x_zero_day_px"]) * scale_hour
    def snr_from_pixel(pixel):
        return 25 - (pixel - calibration["y_positive_25_db_px"]) * scale_snr
    source_image = np.asarray(Image.open(PAPER / "paper_figure6.png").convert("RGB"))
    image_height, image_width = source_image.shape[:2]
    left.imshow(source_image, origin="upper", interpolation="nearest", aspect="auto", extent=(
        hour_from_pixel(-.5), hour_from_pixel(image_width - .5),
        snr_from_pixel(image_height - .5), snr_from_pixel(-.5)))
    density_artist = right.pcolormesh(
        hour_edges, snr_edges, relative_density, cmap="Blues",
        norm=PowerNorm(gamma=DENSITY_COLOR_GAMMA, vmin=0, vmax=1),
        shading="flat", rasterized=True,
    )
    right.scatter(utc_hours, deltas, s=OBSERVATION_MARKER_AREA, color="#233842", alpha=OBSERVATION_ALPHA,
                  linewidths=0, zorder=2)
    right.scatter(
        displayed_additional["utc_hour"], displayed_additional["delta_snr_db"],
        s=OBSERVATION_MARKER_AREA, color=DUPLICATE_COLOR, alpha=OBSERVATION_ALPHA,
        linewidths=0, zorder=2.1,
    )
    matches = []
    for index, feature in enumerate(features["features"]):
        box = feature["pixel_box"]
        xmin, xmax = hour_from_pixel(box["x_min"]), hour_from_pixel(box["x_max"])
        ymin, ymax = snr_from_pixel(box["y_max"]), snr_from_pixel(box["y_min"])
        label = f"R{index + 1}"
        for axis in (*axes, app_axis):
            axis.text((xmin+xmax)/2, ymax+.72, label, color=TEAL, fontsize=13, weight="bold",
                      ha="center", va="bottom", zorder=7,
                      bbox={"facecolor": "white", "alpha": .95, "edgecolor": "none", "pad": 1.4})
        readout = policy["branch_match"]["digitization_bound_px"]
        margin_hour, margin_snr = readout * scale_hour + .5, readout * scale_snr + .5
        window = feature["paper_time_window_utc_hours"]
        matching = [(hour, snr) for hour, snr in modes
                    if window[0] <= hour < window[1]
                    and xmin-margin_hour <= hour <= xmax+margin_hour
                    and ymin-margin_snr <= snr <= ymax+margin_snr]
        assert matching, feature["id"]
        matches.append({"id": feature["id"], "modes": matching})

    maximum_rows, maximum_columns = np.where(density == density.max())
    right.scatter(hours[maximum_columns], snr_centers[maximum_rows], marker="*", s=155,
                  facecolor="white", edgecolor=INK, linewidths=1.4, zorder=9)
    witness_matches = []
    tolerance = point_annotations["recommended_comparison_tolerance"]
    for point in point_annotations["points"]:
        label = point["comparison_label"]
        close = (((utc_hours-point["utc_hour"]+12) % 24 - 12).abs() <= tolerance["utc_hour"]) & (
            (deltas-point["delta_snr_db"]).abs() <= tolerance["delta_snr_db"])
        assert close.any(), point["id"]
        matching_positions = sorted(set(zip(utc_hours[close], deltas[close])))
        witness_matches.append({"id": point["id"], "comparison_label": label,
                                "matching_pairs": int(close.sum()),
                                "distinct_folded_coordinates": matching_positions})
        if label is None:
            continue
        for axis, positions in ((left, [(point["utc_hour"], point["delta_snr_db"])]),
                                (right, matching_positions), (app_axis, matching_positions)):
            axis.scatter(*np.asarray(positions).T, s=110, facecolors="none", edgecolors=MAGENTA,
                         linewidths=1.7, zorder=8, clip_on=False)
            if axis is app_axis:
                anchor_hour, anchor_snr = matching_positions[0]
                axis.annotate(label, (anchor_hour, anchor_snr), xytext=(0, 11 if anchor_snr < 0 else -11),
                              textcoords="offset points", color=MAGENTA, fontsize=12, weight="bold",
                              ha="center", va="bottom" if anchor_snr < 0 else "top", zorder=9,
                              bbox={"facecolor": "white", "alpha": .95, "edgecolor": "none", "pad": 1.2})
                continue
            label_y = point["delta_snr_db"] + (1.3 if point["delta_snr_db"] < 0 else -1.3)
            axis.text(point["utc_hour"], label_y, label, color=MAGENTA, fontsize=12, weight="bold",
                      ha="center", va="bottom" if point["delta_snr_db"] < 0 else "top", zorder=9,
                      bbox={"facecolor": "white", "alpha": .95, "edgecolor": "none", "pad": 1.2})
    for axis in axes:
        axis.set(xlim=(0, 24), ylim=(-15, 25), xticks=np.arange(0, 25, 3),
                 yticks=np.arange(-15, 26, 5), xlabel="Time of day (UTC hour)")
        axis.tick_params(length=4, labelsize=13)
        axis.xaxis.label.set_fontsize(14)
        axis.yaxis.label.set_fontsize(13)
    left.set_ylabel("Δ SNR, G3ZIL − G4HZX (dB)", labelpad=10)
    right.set_ylabel("Δ SNR (dB)", labelpad=10)
    right.axhline(0, color=INK, linewidth=.6, alpha=.45)
    colorbar_axis = figure.add_axes([.480, .340, .140, .010])
    colorbar = figure.colorbar(density_artist, cax=colorbar_axis, orientation="horizontal",
                              ticks=[0, .1, .25, .5, 1])
    colorbar.ax.tick_params(labelsize=11, length=2)
    figure.text(.365, .340, "Density / maximum (B)", fontsize=12)

    # Group shared annotations, reconstruction diagnostics and native summaries
    # under A, B and C respectively, without changing the native C artists.
    shared_handles = [
        Line2D([], [], color=TEAL, marker="$R$", linestyle="none", markersize=10,
               label="R1–R4: paper regions (A–C)"),
        Line2D([], [], color=MAGENTA, marker="o", markerfacecolor="none", linestyle="none", markersize=9,
               label="P1–P4: verification examples only (A–C)"),
    ]
    reconstruction_handles = [
        Line2D([], [], color="#233842", marker="o", linestyle="none",
               markersize=OBSERVATION_LEGEND_MARKER_DIAMETER, markeredgewidth=0,
               label="Individual paired observations (B)"),
        Line2D([], [], color=DUPLICATE_COLOR, marker="o", linestyle="none",
               markersize=OBSERVATION_LEGEND_MARKER_DIAMETER, markeredgewidth=0,
               label="Additional weaker-report combinations (B)"),
        Line2D([], [], marker="*", linestyle="none", markerfacecolor="white", markeredgecolor=INK,
               markersize=13, label="Highest reconstructed density (B)"),
    ]
    legend_groups = [
        (lefts[0], shared_handles, [handle.get_label() for handle in shared_handles]),
        (lefts[1], reconstruction_handles, [handle.get_label() for handle in reconstruction_handles]),
        (lefts[2], app_legend_handles[1:],
         ["Median for each UTC hour (C)", "Middle 50% for each UTC hour (C)"]),
    ]
    for x, handles, legend_labels in legend_groups:
        figure.legend(handles=handles, labels=legend_labels, loc="upper left",
                      bbox_to_anchor=(x-.005, .324), ncol=1,
                      frameon=False, fontsize=14, handlelength=2.4,
                      labelspacing=.55, borderaxespad=0)

    panel_notes = (
        "Panel A: Original publication image, calibrated using its printed axes. R1–R4 locate the paper’s regions.",
        "Panel B: Paired observations recalculated through WSPRadar. Dark dots show retained pairs; red dots show additional* weaker-report combinations, excluded from density. WSPRadar retains the strongest report from each receiver per cycle/path. Shading shows the retained pairs’ density with fixed smoothing.",
        "Panel C: The same retained pairs in unsmoothed 1-hour × 1-dB cells, with hourly medians and the middle 50% (IQR). Read the native nonlinear dB axis carefully.",
    )
    for x, note in zip(lefts, panel_notes):
        figure.text(x, .228, fill(note, width=58, break_long_words=False, break_on_hyphens=False),
                    fontsize=13, color=INK, va="top", linespacing=1.35)
    figure.text(lefts[0], .143, fill(
        "P1–P4: Verification examples only, checking selected time-of-day and ΔSNR matches.",
        width=58, break_long_words=False, break_on_hyphens=False,
    ), fontsize=13, color=MUTED, va="top", linespacing=1.35)
    diagnostic_prefix = figure.text(lefts[1], .068, "*see Figure 3 ",
                                    fontsize=13, color=TEAL, url=DIAGNOSTIC_PDF_URL)
    figure.canvas.draw()
    diagnostic_title_x = diagnostic_prefix.get_window_extent(figure.canvas.get_renderer()).x1 / figure.bbox.width
    figure.text(diagnostic_title_x, .068, "Pairing and duplicate reports",
                fontsize=13, weight="bold", color=TEAL, url=DIAGNOSTIC_PDF_URL)
    figure.text(.048, .023, "Original figure: p. 25, Figure 6. Selection: 5 April 00:00-7 April 23:45 UTC; distance <10,000 km.",
                fontsize=13, color=MUTED, url=PAPER_URL)
    add_demo_pdf_footer(figure, right=.96, bottom=.023)
    output_path = output_directory / "figure6_evidence_comparison.png"
    pdf_path = output_directory / "WSPRadar_Demo_Griffiths_Figure6.pdf"
    figure.savefig(output_path, dpi=180, facecolor=BACKGROUND)
    # Keep reconstruction, app artists, text and annotations vector in PDF.
    # The original publication image remains an embedded source raster.
    for artist in figure.findobj():
        if artist.get_rasterized():
            artist.set_rasterized(False)
        if isinstance(artist, QuadMesh):
            artist.set_edgecolor("face")
            artist.set_linewidth(.04)
    with matplotlib.rc_context({"pdf.fonttype": 42}):
        figure.savefig(pdf_path, facecolor=BACKGROUND, metadata={
            **demo_pdf_metadata(DEMO_PDF_HEADERS["griffiths_figure6"]),
            "Subject": "Vector reconstruction and WSPRadar artists with the original publication raster",
            "CreationDate": None, "ModDate": None,
        })
    dispose_agg_figure(figure)
    metadata = {
        "footer_text": DEMO_PDF_FOOTER_TEXT,
        "output": output_path.name, "pdf_output": pdf_path.name, "source_rows": len(pairs), "count_grid_shape": list(counts.shape),
        "method": "A: calibrated source raster; B: existing fixed Gaussian policy with a global power color scale; C: production temporal renderer and paper export theme, with R1-R4 region labels and matched native P1-P4 coordinates transformed by the native axis",
        "presentation": {"density_color_gamma": DENSITY_COLOR_GAMMA,
                         "observation_alpha": OBSERVATION_ALPHA,
                         "observation_marker_area_points2": OBSERVATION_MARKER_AREA,
                         "additional_report_marker_area_points2": OBSERVATION_MARKER_AREA,
                         "additional_report_alpha": OBSERVATION_ALPHA,
                         "additional_report_color": DUPLICATE_COLOR,
                         "observation_legend_marker_diameter_points": OBSERVATION_LEGEND_MARKER_DIAMETER,
                         "observation_legend_alpha": 1.0,
                         "overall_median_in_legend": False,
                         "duplicate_report_explanation": "Panel B note and legend",
                         "region_description_row": False,
                         "panel_notes_order": ["A", "B", "C"],
                         "region_boxes": False, "local_mode_markers": False},
        "additional_report_combinations": {
            "total": len(additional), "displayed": len(displayed_additional),
            "display_range_db": [-15, 25], "included_in_density": False,
            "scope": "Raw weaker-report combinations for production-selected cycle/callsign/full-locator identities only",
            "records": json.loads(additional[[
                "evidence_utc", "tx_sign", "tx_loc", "id_target", "id_reference",
                "normalized_snr_target", "normalized_snr_reference", "delta_snr_db",
                "target_snr_db", "reference_snr_db",
            ]].to_json(orient="records", date_format="iso")),
        },
        "verified": "All 24 hourly counts, medians, Q1, Q3 and all 1392 density cells equal the existing frozen CSVs; C artist medians/IQR verified",
        "source_feature_matches": matches, "scatter_witnesses": witness_matches,
        "sample_range_db": [float(deltas.min()), float(deltas.max())],
        "reconstruction_origin": {
            "input": "source_rows.parquet only; expected files are assertions after calculation",
            "stages": "generated SQL via SQLite adapter; strict-to-legacy selection; post-fetch; map; Inspector; paired evidence; temporal recipe",
            "source_reports": replay.source_row_count, "strict_sql_rows": replay.strict_row_count,
            "selected_sql_rows": replay.input_row_count,
            "selected_query_sha256": hashlib.sha256(replay.analysis.query.encode("utf-8")).hexdigest(),
            "limit": "No native ClickHouse engine, HTTP, cache/admission or provider geographic-distance validation",
        },
        "builder_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "input_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in (
                              PAPER / "paper_features.json", PAPER / "paper_points.json",
                              PAPER / "comparison_policy.json", PAPER / "paper_figure6.png",
                              ARCHIVE / "demo.config", ARCHIVE / "source_rows.parquet", ARCHIVE / "expected_paired_rows.parquet",
                              ARCHIVE / "expected_utc_hour.csv", ARCHIVE / "expected_density_utc_hour.csv",
                          )},
    }
    (output_directory / "render_checks.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"output": str(output_path), "pairs": len(pairs), "features": len(matches),
                      "witnesses": len(witness_matches), "verified": metadata["verified"]}, indent=2))


if __name__ == "__main__":
    with matplotlib_operation_lock():
        main()
