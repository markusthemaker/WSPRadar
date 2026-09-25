"""Presentation-only Figure 6 comparison; all frozen numerical inputs are read-only."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib import patheffects
import numpy as np
import pandas as pd
from PIL import Image

from core.matplotlib_runtime import matplotlib_operation_lock, dispose_agg_figure
from i18n import T
from ui.plots.evidence_figures import (
    _compare_temporal_profile_values,
    _segment_temporal_evidence_export_recipe,
    render_segment_temporal_evidence_export_figure,
)
from ui.results_export import _style_figure_for_paper

OUTPUT = ROOT / "tests/regression/reference_fixtures/griffiths_fig6_paper_v1"
PAPER = ROOT / "tests/regression/reference_fixtures/griffiths_fig6_paper_v1"
ARCHIVE = ROOT / "tests/regression/reference_fixtures/griffiths_fig6_diurnal_v1"
INK, MUTED, TEAL = "#172B3A", "#526572", "#008F8C"
MAGENTA, ORANGE, BACKGROUND = "#B5366F", "#C86612", "#FCFBF8"


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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-directory", type=Path, default=OUTPUT)
    output_directory = parser.parse_args().output_directory
    output_directory.mkdir(parents=True, exist_ok=True)
    features = read_json(PAPER / "paper_features.json")
    point_annotations = read_json(PAPER / "paper_points.json")
    policy = read_json(PAPER / "comparison_policy.json")
    config = read_json(ARCHIVE / "demo.config")
    pairs = pd.read_parquet(ARCHIVE / "expected_paired_rows.parquet")
    points = pairs.rename(columns={"evidence_utc": "plot_time", "delta_snr_db": "metric"})
    selection = config["settings"]["core_parameters"]["time_selection"]
    labels = T["en"]
    recipe = _segment_temporal_evidence_export_recipe(
        points[["plot_time", "metric"]], "Frozen Figure 6 illustration", "1h", "Joint spots",
        analysis_start_t=selection["start_utc"], analysis_end_t=selection["end_utc"],
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
    lefts, width, bottom, height = [.048, .365, .687], .255, .395, .427
    app_axis.set_position([lefts[2], bottom, .240, height])
    app_colorbar_axis.set_box_aspect(None)
    app_colorbar_axis.set_aspect("auto")
    app_colorbar_axis.set_position([.936, bottom, .007, height])
    app_axis.tick_params(labelsize=11)
    app_axis.xaxis.label.set_fontsize(12)
    app_axis.yaxis.label.set_fontsize(12)
    app_axis.title.set_fontsize(13)
    app_colorbar_axis.tick_params(labelsize=10)
    app_colorbar_axis.yaxis.label.set_fontsize(11)
    for text in app_axis.get_legend().get_texts():
        text.set_fontsize(10)
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
    figure.text(.048, .965, "Griffiths & Squibb Figure 6 · from the paper to WSPRadar", fontsize=26, weight="bold", color=INK)
    figure.text(.048, .929, "G3ZIL − G4HZX  |  5–7 April 2017  |  Panels B and C use the same 6,459 frozen paired observations", fontsize=15, color=MUTED)
    for x, title in zip(lefts, ("A  Published Figure 6", "B  Reconstruction", "C  WSPRadar view")):
        figure.text(x, .883, title, fontsize=17, weight="bold", color=INK)
    for x in (.332, .654):
        figure.text(x, .883, "→", fontsize=24, ha="center", color=TEAL)
    left.set_title("Original scatter and contours · linear dB", fontsize=13, weight="bold", pad=14)
    right.set_title("Fixed smoothing · linear dB", fontsize=13, weight="bold", pad=14)

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
    density_artist = right.pcolormesh(hour_edges, snr_edges, relative_density, cmap="Blues",
                                     vmin=0, vmax=1, shading="flat", rasterized=True)
    right.scatter(utc_hours, deltas, s=3.3, color="#233842", alpha=.23, linewidths=0, zorder=2)
    right.scatter(*np.asarray(modes).T, marker="x", s=17, linewidths=.75, color="#546772", alpha=.65, zorder=3)
    matches = []
    feature_names = ["Early-night negative branch", "Morning positive branch",
                     "Strongest evening island", "Late-night negative branch"]
    for index, feature in enumerate(features["features"]):
        box = feature["pixel_box"]
        xmin, xmax = hour_from_pixel(box["x_min"]), hour_from_pixel(box["x_max"])
        ymin, ymax = snr_from_pixel(box["y_max"]), snr_from_pixel(box["y_min"])
        label = f"R{index + 1}"
        for axis in (*axes, app_axis):
            region_box = Rectangle((xmin, ymin), xmax-xmin, ymax-ymin, fill=False,
                                   edgecolor=TEAL, linewidth=1.8, linestyle=(0, (4, 2)), zorder=5)
            if axis is app_axis:
                region_box.set_path_effects([patheffects.Stroke(linewidth=3.8, foreground="white", alpha=.8),
                                            patheffects.Normal()])
            axis.add_patch(region_box)
            axis.text((xmin+xmax)/2, ymax+.72, label, color=TEAL, fontsize=11, weight="bold",
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
        right.scatter(*np.asarray(matching).T, marker="x", s=65, linewidths=2, color=ORANGE, zorder=8)
        matches.append({"id": feature["id"], "modes": matching})
        text_x = .048 + (index % 2) * .317
        text_y = .216 - (index // 2) * .025
        figure.text(text_x, text_y, label, color=TEAL, fontsize=12, weight="bold")
        figure.text(text_x+.024, text_y, feature_names[index], fontsize=11, weight="bold")

    maximum_rows, maximum_columns = np.where(density == density.max())
    right.scatter(hours[maximum_columns], snr_centers[maximum_rows], marker="*", s=155,
                  facecolor="white", edgecolor=INK, linewidths=1.4, zorder=9)
    witness_matches = []
    tolerance = point_annotations["recommended_comparison_tolerance"]
    for index, point in enumerate(point_annotations["points"]):
        label = f"P{index+1}"
        close = (((utc_hours-point["utc_hour"]+12) % 24 - 12).abs() <= tolerance["utc_hour"]) & (
            (deltas-point["delta_snr_db"]).abs() <= tolerance["delta_snr_db"])
        assert close.any(), point["id"]
        matching_positions = sorted(set(zip(utc_hours[close], deltas[close])))
        for axis, positions in ((left, [(point["utc_hour"], point["delta_snr_db"])]),
                                (right, matching_positions), (app_axis, matching_positions)):
            axis.scatter(*np.asarray(positions).T, s=110, facecolors="none", edgecolors=MAGENTA, linewidths=1.7, zorder=8)
            if axis is app_axis:
                anchor_hour, anchor_snr = matching_positions[0]
                axis.annotate(label, (anchor_hour, anchor_snr), xytext=(0, 11 if anchor_snr < 0 else -11),
                              textcoords="offset points", color=MAGENTA, fontsize=10, weight="bold",
                              ha="center", va="bottom" if anchor_snr < 0 else "top", zorder=9,
                              bbox={"facecolor": "white", "alpha": .95, "edgecolor": "none", "pad": 1.2})
                continue
            label_y = point["delta_snr_db"] + (1.3 if point["delta_snr_db"] < 0 else -1.3)
            axis.text(point["utc_hour"], label_y, label, color=MAGENTA, fontsize=10, weight="bold",
                      ha="center", va="bottom" if point["delta_snr_db"] < 0 else "top", zorder=9,
                      bbox={"facecolor": "white", "alpha": .95, "edgecolor": "none", "pad": 1.2})
        witness_matches.append({"id": point["id"], "matching_pairs": int(close.sum()),
                                "distinct_folded_coordinates": matching_positions})
    for axis in axes:
        axis.set(xlim=(0, 24), ylim=(-15, 25), xticks=np.arange(0, 25, 3),
                 yticks=np.arange(-15, 26, 5), xlabel="Time of day (UTC hour)")
        axis.tick_params(length=4, labelsize=11)
    left.set_ylabel("Δ SNR, G3ZIL − G4HZX (dB)", labelpad=10)
    right.set_ylabel("Δ SNR (dB)", labelpad=10)
    right.axhline(0, color=INK, linewidth=.6, alpha=.45)
    colorbar_axis = figure.add_axes([.49, .321, .13, .011])
    colorbar = figure.colorbar(density_artist, cax=colorbar_axis, orientation="horizontal", ticks=[0, .5, 1])
    colorbar.ax.tick_params(labelsize=9, length=2)
    figure.text(.365, .323, "Smoothed density / maximum", fontsize=10)
    handles = [
        Line2D([], [], color=TEAL, linestyle="--", linewidth=2, label="R1–R4: fixed paper contour regions"),
        Line2D([], [], color=ORANGE, marker="x", linestyle="none", markersize=8, markeredgewidth=2,
               label="Matching density peaks"),
        Line2D([], [], marker="*", linestyle="none", markerfacecolor="white", markeredgecolor=INK,
               markersize=12, label="Reconstructed global maximum"),
        Line2D([], [], color=MAGENTA, marker="o", markerfacecolor="none", linestyle="none", markersize=8,
               label="P1–P3: isolated scatter witnesses"),
    ]
    figure.legend(handles=handles, loc="upper left", bbox_to_anchor=(.045, .286), ncol=2,
                  frameon=False, fontsize=11, columnspacing=2.6, handlelength=2.5)
    figure.text(.687, .337, "Same observations, native WSPRadar presentation", fontsize=12, weight="bold")
    figure.text(.687, .316, "R1–R4 map the same paper bounds onto the app’s axis.", fontsize=10.5, color=TEAL)
    figure.text(.687, .295, "P1–P3 mark matched native spots within hourly cells.", fontsize=10.5, color=MAGENTA)
    figure.text(.687, .270, "Unsmoothed 1-hour × 1-dB cells; pooled median +5 dB.\n"
                "Markers: hourly medians. Band: hourly middle 50% (IQR).", fontsize=10.5, linespacing=1.6, va="top")
    figure.text(.687, .216, "C uses the app’s median-centered nonlinear dB axis.\n"
                "Read the dB labels; vertical pixel positions differ from A/B.\n"
                "These medians and IQRs are calculated from frozen pairs;\n"
                "they are not measurements extracted from the paper.", fontsize=10.5, linespacing=1.6, va="top")
    figure.text(.048, .150, "A/B alignment: printed-axis calibration, with no fitted shift or scale. R1–R4 are contour regions, not confidence intervals.\n"
                "Matching peaks use the fixed ±4-pixel readout + half-cell allowances; boxes show the source regions alone. P1–P3 match folded time/SNR, not identified dates or stations.",
                fontsize=10.5, linespacing=1.6, va="top")
    figure.text(.048, .100, "B reconstruction: frozen same-cycle pairs → production 1-hour × 1-dB count grid → fixed Gaussian comparison smoother (σ = 1 hour, 1 dB; UTC wraps).\n"
                "The full −17 to +40 dB sample range enters smoothing; A/B display −15 to +25 dB. Faint points are native pairs; gray × mark other density peaks. C retains the full app view.",
                fontsize=10.5, linespacing=1.6, va="top")
    figure.text(.048, .049, "Source: Griffiths & Squibb, Practical Wireless, October 2017, p. 25, Fig. 6 (5–7 April). Frozen demo: 5 April 00:00–7 April 23:45 UTC; distance <10,000 km.\n"
                "Illustration from the existing frozen fixture, not a fresh live run. Author smoothing, contour levels and exact population are unknown: agreement concerns selected features, not the complete distribution.",
                fontsize=10, color=MUTED, linespacing=1.6, va="top")
    output_path = output_directory / "figure6_evidence_comparison.png"
    figure.savefig(output_path, dpi=180, facecolor=BACKGROUND)
    # Keep reconstruction, app artists, text and annotations vector in PDF.
    # The original publication image remains an embedded source raster.
    for artist in figure.findobj():
        if artist.get_rasterized():
            artist.set_rasterized(False)
    with matplotlib.rc_context({"pdf.fonttype": 42}):
        figure.savefig(output_path.with_suffix(".pdf"), facecolor=BACKGROUND, metadata={
            "Title": "Griffiths and Squibb Figure 6: publication, reconstruction and WSPRadar",
            "Subject": "Vector reconstruction and WSPRadar artists with the original publication raster",
            "CreationDate": None, "ModDate": None,
        })
    dispose_agg_figure(figure)
    metadata = {
        "output": output_path.name, "pdf_output": output_path.with_suffix(".pdf").name, "source_rows": len(pairs), "count_grid_shape": list(counts.shape),
        "method": "A: calibrated source raster; B: existing fixed Gaussian policy; C: production temporal renderer and paper export theme, with identical R1-R4 paper bounds and matched native P1-P3 coordinates transformed by the native axis",
        "verified": "All 24 hourly counts, medians, Q1, Q3 and all 1392 density cells equal the existing frozen CSVs; C artist medians/IQR verified",
        "source_feature_matches": matches, "scatter_witnesses": witness_matches,
        "sample_range_db": [float(deltas.min()), float(deltas.max())],
        "input_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in (
                              PAPER / "paper_features.json", PAPER / "paper_points.json",
                              PAPER / "comparison_policy.json", PAPER / "paper_figure6.png",
                              ARCHIVE / "demo.config", ARCHIVE / "expected_paired_rows.parquet",
                              ARCHIVE / "expected_utc_hour.csv", ARCHIVE / "expected_density_utc_hour.csv",
                          )},
    }
    (output_directory / "render_checks.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output_path), "pairs": len(pairs), "features": len(matches),
                      "witnesses": len(witness_matches), "verified": metadata["verified"]}, indent=2))


if __name__ == "__main__":
    with matplotlib_operation_lock():
        main()
