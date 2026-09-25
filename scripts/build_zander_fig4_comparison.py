"""Presentation-only A-to-B-to-C layout; all frozen numerical inputs are read-only."""
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
from matplotlib.patches import Patch
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import numpy as np
import pandas as pd
from PIL import Image
from ui.plots.evidence_figures import _vertical_metric_histogram_recipe
from core.matplotlib_runtime import matplotlib_operation_lock

PAPER = ROOT / "tests/regression/reference_fixtures/zander_fig4_paper_v1"
ARCHIVE = ROOT / "tests/regression/reference_fixtures/zander_experiment_a_v1"
OUTPUT = PAPER / "figure4_histogram_overlay.png"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-directory", type=Path, default=PAPER)
    output_directory = parser.parse_args().output_directory
    output_directory.mkdir(parents=True, exist_ok=True)
    output_path = output_directory / OUTPUT.name
    annotations = json.loads((PAPER / "paper_features.json").read_text())
    policy = json.loads((PAPER / "comparison_policy.json").read_text())
    paired = pd.read_csv(ARCHIVE / "expected_paired_rows.csv", float_precision="round_trip")
    fine_expected = pd.read_csv(ARCHIVE / "expected_histogram_1db.csv", float_precision="round_trip")
    differences = paired.delta_snr_db.to_numpy()
    recipe = _vertical_metric_histogram_recipe(differences)
    assert recipe["value_count"] == 166 and recipe["bin_width"] == 1
    np.testing.assert_array_equal(recipe["centers"], fine_expected.delta_snr_db)
    np.testing.assert_array_equal(recipe["counts"], fine_expected.joint_spots)
    percentages = 100 * recipe["counts"] / recipe["value_count"]
    np.testing.assert_allclose(percentages, fine_expected.percent_of_sample, rtol=0, atol=1e-12)
    edges = np.asarray(policy["nominal_edges_db"])
    widths = np.diff(edges)
    counts = np.histogram(differences, bins=edges)[0]
    assert counts.sum() == recipe["counts"].sum() == 166
    density = counts / (166 * widths)
    paper_density = np.array([entry["density_per_db"] for entry in annotations["digitization"]["bins"][:9]])
    residuals = density - paper_density
    tolerance = annotations["digitization"]["density_absolute_readout_tolerance_per_db"]
    assert np.all(np.abs(residuals) <= tolerance)
    assert np.isclose(percentages.sum(), 100) and np.isclose(np.dot(density, widths), 1)
    mean = float(differences.mean())
    sample_sd = float(differences.std(ddof=1))
    median = float(np.median(differences))
    assert median == -7
    identities = len(paired[["peer_sign", "peer_grid"]].drop_duplicates())
    cycles = paired.time_slot.nunique()

    INK, MUTED, TEAL, ORANGE = "#172B3A", "#526572", "#148A91", "#D9792C"
    BACKGROUND, GRID = "#FCFBF8", "#DEE5E7"
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 12, "text.color": INK,
        "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
        "axes.edgecolor": "#91A0A8", "figure.facecolor": BACKGROUND,
        "axes.facecolor": "white", "savefig.facecolor": BACKGROUND,
    })
    figure = plt.figure(figsize=(20, 12), dpi=180)
    lefts, width, bottom, height = [.055, .375, .695], .27, .45, .34
    figure.text(.055, .962, "Zander Figure 4 · from the paper to WSPRadar", fontsize=26, weight="bold")
    figure.text(.055, .924, "Experiment A, 14 MHz  |  The same 166 reconstructed pairs, shown with coarse and fine bins", fontsize=14, color=MUTED)
    titles = ["A  Published Figure 4", "B  Reconstruction in the paper’s bins", "C  WSPRadar · 1 dB bins"]
    subtitles = ["Original raster; orange line: paper’s normal curve.", "Digitized paper bars over the reconstruction.", "Same pairs, percent-of-sample bar heights."]
    for left, title, subtitle in zip(lefts, titles, subtitles):
        figure.text(left, .878, title, fontsize=15, weight="bold")
        figure.text(left, .848, subtitle, fontsize=11, color=MUTED)
    for arrow_x in [.348, .668]:
        figure.text(arrow_x, .88, "→", fontsize=23, color=TEAL, ha="center")

    # Align the original raster's plot frame with B and C while retaining the full
    # source image, including its title, axes, tick labels and original Gaussian.
    image = np.asarray(Image.open(PAPER / "paper_figure4.png").convert("RGB"))
    calibration = annotations["digitization"]
    x_limits = calibration["axis_limits_readout"]["x_db"]
    y_limits = calibration["axis_limits_readout"]["y_density"]
    sx, ix = calibration["x_calibration_db_per_pixel_and_intercept"]
    sy, iy = calibration["y_calibration_density_per_pixel_and_intercept"]
    px0, px1 = [(value - ix) / sx for value in x_limits]
    py_bottom, py_top = [(value - iy) / sy for value in y_limits]
    x_scale, y_scale = width / (px1 - px0), height / (py_bottom - py_top)
    source_axis = figure.add_axes([
        lefts[0] - (px0 + .5) * x_scale,
        bottom - (image.shape[0] - .5 - py_bottom) * y_scale,
        image.shape[1] * x_scale, image.shape[0] * y_scale,
    ])
    source_axis.imshow(image, interpolation="nearest", aspect="auto")
    source_axis.set_axis_off()

    overlay_axis = figure.add_axes([lefts[1], bottom, width, height])
    app_axis = figure.add_axes([lefts[2], bottom, width, height])
    for axis in [overlay_axis, app_axis]:
        axis.set_xlim(x_limits)
        axis.set_xticks(calibration["x_tick_values_db"])
        axis.set_xlabel("Target − Reference ΔSNR (dB)", labelpad=9)
        axis.grid(axis="y", color=GRID, lw=.7, zorder=0)
        axis.spines[["top", "right"]].set_visible(False)

    overlay_axis.bar(edges[:-1], density, width=widths, align="edge", color=TEAL, alpha=.27, edgecolor="none", zorder=2)
    overlay_axis.stairs(density, edges, color=TEAL, linewidth=1.6, zorder=3)
    overlay_axis.stairs(paper_density, edges, color=ORANGE, linewidth=2.2, zorder=4)
    overlay_axis.set_ylim(y_limits)
    overlay_axis.set_ylabel("Probability density (dB⁻¹)", labelpad=9)
    overlay_axis.yaxis.set_major_locator(MultipleLocator(.02))
    overlay_axis.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
    overlay_axis.legend(handles=[
        Line2D([], [], color=ORANGE, lw=2.2, label="Paper bars (digitized)"),
        Patch(facecolor=TEAL, alpha=.35, edgecolor=TEAL, label="WSPRadar reconstruction"),
    ], loc="upper right", fontsize=9.5, framealpha=.97, edgecolor=GRID)
    overlay_axis.annotate("Final flat region combines\ntwo source bars", xy=(1.9, density[-1]), xytext=(1.5, .034),
                          fontsize=10, color=MUTED, arrowprops={"arrowstyle": "-", "color": MUTED, "lw": .8})

    bars = app_axis.bar(recipe["centers"], percentages, width=.82, align="center", color=TEAL, alpha=.55,
                        edgecolor=TEAL, linewidth=.7, zorder=2)
    np.testing.assert_allclose([bar.get_height() for bar in bars], fine_expected.percent_of_sample, rtol=0, atol=1e-12)
    np.testing.assert_array_equal([bar.get_x() + bar.get_width()/2 for bar in bars], recipe["centers"])
    app_axis.set_ylim(0, 15)
    app_axis.set_yticks([0, 3, 6, 9, 12, 15])
    app_axis.set_ylabel("Joint pairs (% of sample)", labelpad=9)
    app_axis.axvline(median, color=INK, ls="--", lw=1.2, alpha=.7)
    app_axis.text(.975, .965, f"n = 166\nMedian {median:.1f} dB\nMean {mean:.3f} dB", transform=app_axis.transAxes,
                  ha="right", va="top", fontsize=10.5, color=MUTED)

    # Retain the former C residual evidence as a smaller unlettered supporting plot.
    figure.text(lefts[1], .351, "Agreement check · reconstruction minus digitized density", fontsize=11.5, weight="bold")
    figure.text(lefts[1], .326, f"Maximum |residual| {np.abs(residuals).max():.7f} dB⁻¹", fontsize=10.5, color=MUTED)
    residual_axis = figure.add_axes([lefts[1], .18, width, .119])
    residual_axis.axhspan(-5, 5, color=ORANGE, alpha=.10)
    residual_axis.axhline(0, color="#71838D", lw=.8)
    residual_axis.stairs(residuals * 1e4, edges, color=TEAL, lw=1.8, baseline=None)
    residual_axis.scatter((edges[:-1] + edges[1:])/2, residuals * 1e4, color=TEAL, s=20)
    residual_axis.set(xlim=x_limits, ylim=(-5.8, 5.8), ylabel="Residual (×10⁻⁴ dB⁻¹)", xlabel="Target − Reference ΔSNR (dB)")
    residual_axis.set_xticks(calibration["x_tick_values_db"])
    residual_axis.set_yticks([-5, 0, 5])
    residual_axis.spines[["top", "right"]].set_visible(False)
    residual_axis.tick_params(labelsize=10)
    figure.text(lefts[1], .132, "Shaded allowance: ±0.0005 dB⁻¹; not a confidence interval.", fontsize=10.2, color=MUTED)

    figure.text(lefts[0], .351, "Rounded paper statistics", fontsize=12, weight="bold")
    figure.text(lefts[0], .321, "Mean −6.8 dB  ·  Reported σ 3.5 dB", fontsize=14)
    figure.text(lefts[0], .272, "Independent archive reconstruction", fontsize=12, weight="bold")
    figure.text(lefts[0], .242, f"Mean {mean:.3f} dB  ·  Sample s {sample_sd:.3f} dB", fontsize=14, color=TEAL)
    figure.text(lefts[0], .206, f"166 receiver-cycle pairs  ·  {identities} receiver identities  ·  {cycles} cycles", fontsize=10.5, color=MUTED)
    figure.text(lefts[0], .165, "All 9 visible regions fall within the\noriginal readout allowance.", fontsize=12, weight="bold", color=TEAL, va="top", linespacing=1.4)

    figure.text(lefts[2], .351, "Same observations, finer display", fontsize=12, weight="bold")
    figure.text(lefts[2], .316, "The 1 dB bins reveal uneven counts and empty bins\nthat are combined in the paper’s coarser histogram.\nThe mean and standard deviation do not change.", fontsize=11.5, color=MUTED, va="top", linespacing=1.6)
    figure.text(lefts[2], .229, "B shows density per dB.\nC shows percent of all 166 pairs per 1 dB bin;\nits percentages sum to 100%.", fontsize=11.5, color=MUTED, va="top", linespacing=1.6)
    figure.text(lefts[2], .132, "No fitted curve, time shift or density rescaling.", fontsize=10.5, color=MUTED)

    figure.add_artist(Line2D([.055, .965], [.104, .104], transform=figure.transFigure, color=GRID, lw=1))
    figure.text(.055, .078, "METHOD  Coarse density = count ÷ (166 × region width). Eight 2.1 dB regions plus one 4.2 dB region; no clipping or subset renormalization.", fontsize=10.5)
    figure.text(.055, .050, "LIMIT  Agreement supports the pooled-pair reconstruction; the paper leaves exact selectors and histogram sample weighting unresolved.", fontsize=10.5)
    figure.text(.055, .023, "SOURCE  Jens Zander (2022), arXiv:2209.08989v1, Figure 4. Graphical allowances are not statistical confidence intervals. Frozen fixture data and tests are unchanged.", fontsize=10, color=MUTED)

    figure.savefig(output_path, dpi=180, metadata={
        "Title": "Zander Figure 4: publication to reconstruction to WSPRadar",
        "Description": "A original publication, B fixed coarse-bin density overlay, C production1dB histogram percentages in the same light style; residual check retained underneath B.",
        "Inputs": json.dumps({str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in [
            PAPER/"paper_features.json", PAPER/"comparison_policy.json", PAPER/"paper_figure4.png", ARCHIVE/"expected_paired_rows.csv", ARCHIVE/"expected_histogram_1db.csv"]}),
    })
    # Bars, lines and labels remain vector; only the original paper is raster.
    with matplotlib.rc_context({"pdf.fonttype": 42}):
        figure.savefig(output_path.with_suffix(".pdf"), metadata={
            "Title": "Zander Figure 4: publication, reconstruction and WSPRadar",
            "Subject": "Vector histogram reconstruction and comparison with the original publication raster",
            "CreationDate": None, "ModDate": None,
        })
    plt.close(figure)
    print(json.dumps({"output": str(output_path), "sample_count": 166, "fine_bin_counts_and_bar_heights_verified": True, "maximum_density_residual": float(np.abs(residuals).max())}))


if __name__ == "__main__":
    with matplotlib_operation_lock():
        main()
