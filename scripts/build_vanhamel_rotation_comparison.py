"""Render the Vanhamel Figure 6 comparison without refreshing scientific oracles.

The offline regression harness executes production SQL against frozen source
reports. Its output feeds the reconstructed traces and the actual WSPRadar
selected-station temporal renderer. Only presentation artifacts are written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
from matplotlib.collections import QuadMesh
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests/regression"))

from core.matplotlib_runtime import dispose_agg_figure, synchronized_matplotlib
from i18n import T
from test_vanhamel_rotation_reference import _calculate_run, _assert_exact_trace
from ui.plots.evidence_figures import (
    _selected_evidence_export_recipe,
    render_selected_evidence_export_figure,
)
from ui.results_export import _style_figure_for_paper


FIXTURE = ROOT / "tests/regression/reference_fixtures/vanhamel_fig6_rotation_v1"
OUTPUT_NAME = "figure6_overlay_1p6"
LANDMARK_COLOR = "#9d4b00"
ROTATION_COLOR = "#77438a"


def _production_recipe(run):
    labels = T["en"]
    return _selected_evidence_export_recipe(
        run.points, "Selected Station Evidence: M7AEO (IO82)", "12h", False,
        analysis_start_t=run.configuration["start_utc"],
        analysis_end_t=run.configuration["end_utc"],
        count_label=labels["fig_joint_spot_count"],
        chronological_title=labels["fig_selected_compare_chronological_title"],
        chronological_x_label=labels["fig_segment_chronological_x"],
        chronological_unavailable_text=labels["fig_compare_chronological_unavailable"],
        metric_axis_label=labels["tbl_col_delta_snr"],
        folded_title=labels["fig_selected_compare_folded_title"],
        folded_x_label=labels["fig_segment_utc_hour_x"],
        folded_date_annotation=labels["fig_segment_dates_folded"].replace("{count}", "{utc_date_count}"),
        density_label=labels["fig_relative_joint_spot_density"],
        folded_unavailable_text=labels["fig_segment_folded_unavailable"],
        median_focus_axis_label=labels["fig_compare_median_focus_axis"],
        median_label=labels["fig_median_label"],
        bin_median_label=labels["fig_temporal_bin_median"],
        bin_iqr_label=labels["fig_temporal_bin_iqr"],
        time_bin_options=("12h",),
    )


def _trace_axes_style(axis, reception_count):
    axis.set_xlim(0, reception_count)
    axis.set_ylim(-40, 11)
    axis.set_xticks([0, 250, 500, 750, 1000, 1250, reception_count])
    axis.set_yticks([-40, -30, -20, -10, 0, 10])
    axis.set_xlabel("Reception number in chronological order", fontsize=10)
    axis.set_ylabel("SNR / ΔSNR (dB)", fontsize=10)
    axis.tick_params(labelsize=9)
    axis.axvline(750, color=ROTATION_COLOR, linestyle="--", linewidth=1.0)
    axis.text(761, -37.8, "Paper rotation boundary: reception 750", color=ROTATION_COLOR, fontsize=8.5)
    axis.spines[["top", "right"]].set_visible(False)


@synchronized_matplotlib
def render_comparison(run, output_directory):
    paper = json.loads((FIXTURE / "paper_features.json").read_text(encoding="utf-8"))
    points = run.points.sort_values("plot_time").reset_index(drop=True)
    paired_units = run.units[run.units.metric.notna()].sort_values("evidence_utc").reset_index(drop=True)
    np.testing.assert_allclose(points.metric, paired_units.metric, rtol=0, atol=1e-12)
    reception_indexes = np.arange(1, len(points) + 1)

    # Both reported transmitter powers are 23 dBm. Undo the common +7 dB
    # normalization for the endpoint traces to reproduce the paper's SNR scale.
    # The Reference's established +1.6 dB correction remains applied.
    raw_pairs = pd.read_csv(FIXTURE / "expected_paired_rows.csv")
    assert set(raw_pairs.target_report_power_dbm) == {23}
    assert set(raw_pairs.reference_report_power_dbm) == {23}
    target_trace = paired_units.target_snr_db.to_numpy() - 7
    reference_trace = paired_units.reference_snr_db.to_numpy() - 7
    np.testing.assert_allclose(target_trace, raw_pairs.target_report_snr_db, rtol=0, atol=1e-12)
    np.testing.assert_allclose(reference_trace, raw_pairs.reference_report_snr_db + 1.6, rtol=0, atol=1e-12)

    # Start with the actual production figure, preserving the chronological
    # artists, nonlinear y transform, complete density mesh, medians and IQR.
    figure = render_selected_evidence_export_figure(_production_recipe(run))
    _style_figure_for_paper(figure)
    figure.set_size_inches(16, 14.7)
    figure.set_layout_engine(None)
    axes_by_gid = {axis.get_gid(): axis for axis in figure.axes}
    chronological = axes_by_gid["compare-temporal-chronological-axis"]
    folded = axes_by_gid["compare-temporal-folded-axis"]
    colorbar = axes_by_gid["compare-temporal-colorbar-axis"]
    figure.delaxes(folded)
    chronological.set_position([.075, .120, .80, .212])
    colorbar.set_position([.89, .120, .016, .212])
    colorbar.set_aspect("auto")
    colorbar.set_box_aspect(None)
    chronological.set_title("", loc="center")
    chronological.set_title("Δ SNR over Time (12h bins)", loc="center", fontsize=12, pad=10)
    for text in list(figure.texts):
        text.remove()

    figure.text(.075, .98, "Vanhamel Figure 6 | Publication, reconstruction and WSPRadar", fontsize=19, weight="bold", va="top")
    figure.text(.075, .956, "M7AEO (IO82) received by ON4AWM0 and ON4AWM1 | 1,441 same-cycle pairs | Reference correction +1.6 dB", fontsize=11, va="top")

    publication_axis = figure.add_axes([.075, .703, .80, .213])
    reconstruction_axis = figure.add_axes([.075, .430, .80, .205])
    figure.text(.075, .931, "A  Publication | Original Figure 6 image", fontsize=13, weight="bold")
    figure.text(.075, .650, "B  Reconstruction | WSPRadar paired results at every reception", fontsize=13, weight="bold")
    figure.text(.075, .365, "C  WSPRadar | Selected Station Evidence, white export, 12h bins", fontsize=13, weight="bold")

    calibration = paper["pixel_calibration"]
    original = np.asarray(Image.open(FIXTURE / "paper_figure6.png"))
    height, width = original.shape[:2]
    image_extent = (
        calibration["index_intercept"] - .5 * calibration["index_per_x_pixel"],
        calibration["index_intercept"] + (width - .5) * calibration["index_per_x_pixel"],
        calibration["db_intercept"] + (height - .5) * calibration["db_per_y_pixel"],
        calibration["db_intercept"] - .5 * calibration["db_per_y_pixel"],
    )
    publication_axis.imshow(original, extent=image_extent, aspect="auto", interpolation="none", zorder=0)
    for axis in (publication_axis, reconstruction_axis):
        _trace_axes_style(axis, len(points))
    publication_axis.set_xlabel("")
    reconstruction_axis.grid(color="#c8d6d4", linewidth=.7)
    reconstruction_axis.axhline(0, color="#555555", linewidth=.8)
    reconstruction_axis.plot(reception_indexes, target_trace, color="#219af5", linewidth=1.15)
    reconstruction_axis.plot(reception_indexes, reference_trace, color="#fa004d", linestyle=":", linewidth=1.4)
    reconstruction_axis.plot(reception_indexes, points.metric, color="#101c20", linewidth=1.2)

    landmark_records = []
    for landmark in paper["black_trace_landmarks"]:
        center = landmark["reception_index_approx"]
        tolerance = paper["landmark_readout_policy"]["index_tolerance_receptions"]
        nearby = points.iloc[max(0, center - tolerance - 1):center + tolerance]
        index = nearby.metric.idxmin() if landmark["delta_snr_db_approx"] < 0 else nearby.metric.idxmax()
        observed = float(points.metric.iloc[index])
        assert abs(observed - landmark["delta_snr_db_approx"]) <= .4 + 1e-12
        publication_axis.scatter([center], [landmark["delta_snr_db_approx"]], s=55, facecolors="none", edgecolors=LANDMARK_COLOR, linewidths=1.1, zorder=5)
        reconstruction_axis.scatter([index + 1], [observed], s=55, facecolors="none", edgecolors=LANDMARK_COLOR, linewidths=1.1, zorder=5)
        landmark_records.append({"name": landmark["name"], "observed_reception_index": int(index + 1), "observed_delta_snr_db": observed, "observed_utc": points.plot_time.iloc[index].isoformat()})

    legend_handles = [
        Line2D([], [], color="#219af5", label="ITA LWA II (Target)"),
        Line2D([], [], color="#fa004d", linestyle=":", label="Shorted dipole (corrected Reference)"),
        Line2D([], [], color="#101c20", label="Difference: Target - Reference"),
        Line2D([], [], color=LANDMARK_COLOR, marker="o", markerfacecolor="none", linestyle="none", label="Seven independently read landmarks"),
    ]
    figure.legend(handles=legend_handles, loc="upper left", bbox_to_anchor=(.071, .683), ncol=4, frameon=False, fontsize=8.8)
    figure.text(.075, .390, "A/B: identical linear axes; reported-SNR scale for antenna traces. No fitted shift, amplitude scaling or time warp.", fontsize=9, color="#444444")
    figure.text(.075, .061, "C uses elapsed UTC time and WSPRadar's nonlinear median-centered axis; 12h bins retain counts, medians, IQR and tail cells.", fontsize=9, color="#444444")
    figure.text(.075, .043, "The bin grid begins at 01 May 2021 17:15 UTC. Empty bins remain empty. Reception 750 is not an exact published UTC timestamp.", fontsize=9, color="#444444")
    figure.text(.075, .025, "Source: Vanhamel, Machiels & Lamy (2022), Figure 6, doi:10.1155/2022/4809313, CC BY 4.0. Paper image raster; B/C vector graphics.", fontsize=8.5, color="#555555")

    output_directory.mkdir(parents=True, exist_ok=True)
    # Matplotlib otherwise rasterizes its colorbar at the default threshold.
    # Keep every generated artist vector-native; only the paper image is raster.
    for axis in figure.axes:
        for collection in axis.collections:
            collection.set_rasterized(False)
            if axis is colorbar and isinstance(collection, QuadMesh):
                # Avoid white seams between vector colorbar cells in PDF viewers.
                collection.set_edgecolor("face")
    try:
        figure.savefig(output_directory / f"{OUTPUT_NAME}.png", dpi=180, facecolor="white")
        with matplotlib.rc_context({"pdf.fonttype": 42}):
            figure.savefig(output_directory / f"{OUTPUT_NAME}.pdf", facecolor="white", metadata={"Title": "Vanhamel Figure 6: publication, WSPRadar reconstruction and 12h evidence", "Author": "WSPRadar", "Subject": "Paper raster and vector-native reconstruction; Reference correction +1.6 dB"})
    finally:
        dispose_agg_figure(figure)
    return {
        "builder": str(Path(__file__).relative_to(ROOT)).replace("\\", "/"),
        "builder_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "figure": 6,
        "source": "Frozen raw reports, actual generated SQL, production post-fetch and selected-station preparation",
        "paired_observations": len(points),
        "reference_correction_db": 1.6,
        "panel_a": "Original full embedded publication raster, with fixed tick calibration and external landmark rings",
        "panel_b": "Every WSPRadar paired reception; endpoint SNR subtracts common 7 dB normalization only to match paper display; paired difference unchanged",
        "panel_c": "Actual selected_benchmark_temporal chronological artists and production white export styling; 12h bins, UTC axis, median-centered nonlinear delta SNR",
        "scientific_expectations_updated": False,
        "pdf_raster_boundary": "Only the original published Figure 6 image is raster; reconstruction, production density cells, lines, markers, text and axes remain vector",
        "observed_landmarks": landmark_records,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-directory", required=True, type=Path)
    arguments = parser.parse_args()
    source = pd.read_csv(FIXTURE / "source_rows.csv", float_precision="round_trip")
    run = _calculate_run(source)
    _assert_exact_trace(run.points)
    metadata = render_comparison(run, arguments.output_directory)
    (arguments.output_directory / "comparison_presentation.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"output_directory": str(arguments.output_directory), "paired_observations": metadata["paired_observations"]}))


if __name__ == "__main__":
    main()
