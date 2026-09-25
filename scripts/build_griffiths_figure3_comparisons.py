"""Render Figure 3 review graphics without changing scientific fixture oracles.

Panel C retains the production temporal artists and white export theme. PDF
output preserves vector text, scatter, curves and density cells; the original
publication image remains a raster. Run from any directory with the repo venv.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import QuadMesh
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd
from PIL import Image

from core.matplotlib_runtime import dispose_agg_figure, matplotlib_operation_lock
from i18n import T
from ui.plots.evidence_figures import (
    _compare_temporal_profile_values,
    _segment_temporal_evidence_export_recipe,
    render_segment_temporal_evidence_export_figure,
)
from ui.results_export import _style_figure_for_paper


FIXTURES = ROOT / "tests/regression/reference_fixtures"
PAPER = FIXTURES / "griffiths_fig3_paper_v1"
ARCHIVE = FIXTURES / "griffiths_fig3_temporal_v1"
START = pd.Timestamp("2017-04-01T00:00Z")
INK, MUTED, TEAL, MAGENTA = "#172B3A", "#526572", "#007C83", "#B5366F"
NATIVE = "#35566A"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def source_bounds(feature, calibration, *, allowance=False):
    """Return the unchanged source rectangle in days since April 1 and dB."""
    box = feature["pixel_box"]
    dx = dy = 0
    if allowance:
        dx = feature["manual_box_edge_uncertainty_px"]["x"] + calibration["axis_readout_uncertainty_px"]["x"]
        dy = feature["manual_box_edge_uncertainty_px"]["y"] + calibration["axis_readout_uncertainty_px"]["y"]
    return (
        day_from_pixel(box["x_min"] - dx, calibration),
        day_from_pixel(box["x_max"] + dx, calibration),
        snr_from_pixel(box["y_max"] + dy, calibration),
        snr_from_pixel(box["y_min"] - dy, calibration),
    )


def day_from_pixel(pixel, calibration):
    return 30 * (pixel - calibration["x_april1_px"]) / (calibration["x_may1_px"] - calibration["x_april1_px"])


def snr_from_pixel(pixel, calibration):
    return 30 - 50 * (pixel - calibration["y_positive30_db_px"]) / (calibration["y_negative20_db_px"] - calibration["y_positive30_db_px"])


def load_pairing_evidence():
    pairs = pd.read_parquet(ARCHIVE / "expected_paired_rows.parquet")
    pairs["days"] = (pairs.evidence_utc - START).dt.total_seconds() / 86400
    reports = pd.read_parquet(ARCHIVE / "source_rows.parquet")
    reports["normalized_snr"] = reports.snr.astype(int) - reports.power.astype(int) + 30
    keys = ["time", "tx_sign", "tx_loc"]
    reports["best_normalized_snr"] = reports.groupby(keys + ["rx_sign"], observed=True).normalized_snr.transform("max")
    target = reports.loc[reports.rx_sign.eq("G3ZIL")]
    reference = reports.loc[reports.rx_sign.eq("G4HZX")]
    expanded = target.merge(reference, on=keys, suffixes=("_target", "_reference"))
    assert expanded.power_target.eq(expanded.power_reference).all()
    expanded["delta_snr_db"] = expanded.normalized_snr_target - expanded.normalized_snr_reference
    expanded["days"] = (expanded.time - START).dt.total_seconds() / 86400
    expanded["uses_strongest_reports"] = (
        expanded.normalized_snr_target.eq(expanded.best_normalized_snr_target)
        & expanded.normalized_snr_reference.eq(expanded.best_normalized_snr_reference)
    )
    selected_keys = pairs.rename(columns={"evidence_utc": "time", "peer_sign": "tx_sign", "peer_grid": "tx_loc"})
    expanded = expanded.merge(selected_keys[keys].assign(in_demo_population=True), on=keys, how="left", validate="many_to_one")
    expanded["in_demo_population"] = expanded.in_demo_population.eq(True)
    independent = expanded.loc[expanded.uses_strongest_reports, keys + ["delta_snr_db"]].drop_duplicates()
    check = selected_keys.merge(independent, on=keys, how="left", validate="one_to_one", suffixes=("_frozen", "_independent"))
    np.testing.assert_array_equal(check.delta_snr_db_frozen, check.delta_snr_db_independent)
    assert len(pairs) == 57767 and len(expanded) == 59019
    return pairs, expanded


def temporal_recipe(pairs):
    points = pairs.rename(columns={"evidence_utc": "plot_time", "delta_snr_db": "metric"})
    labels = T["en"]
    selection = read_json(ARCHIVE / "demo.config")["settings"]["core_parameters"]["time_selection"]
    return _segment_temporal_evidence_export_recipe(
        points[["plot_time", "metric"]], "Griffiths Figure 3 frozen evidence", "12h", "Joint spots",
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
        bin_iqr_label=labels["fig_temporal_bin_iqr"], time_bin_options=("12h",),
    )


def save_figure(figure, directory, name, title):
    """Render both formats from the same artists, not a PNG embedded in PDF."""
    for axis in figure.axes:
        for artist in (*axis.collections, *axis.lines, *axis.patches):
            artist.set_rasterized(False)
            if isinstance(artist, QuadMesh):
                # Shared cell edges otherwise show white PDF-viewer seams.
                artist.set_edgecolor("face")
                artist.set_linewidth(.04)
    figure.savefig(directory / f"{name}.png", dpi=180, facecolor="white")
    figure.savefig(directory / f"{name}.pdf", facecolor="white", metadata={
        "Title": title,
        "Subject": "Frozen scientific reference comparison; publication raster with native vector reconstruction and WSPRadar artists",
        "Creator": "WSPRadar build_griffiths_figure3_comparisons.py",
        "CreationDate": None, "ModDate": None,
    })


def render_comparison(pairs, features, image, directory):
    recipe = temporal_recipe(pairs)
    counts, summary, time_edges, _ = _compare_temporal_profile_values(recipe["prepared_profiles"]["chronological"]["12h"])
    independent = pairs.groupby(pairs.evidence_utc.dt.floor("12h")).delta_snr_db
    np.testing.assert_array_equal(summary["count"], independent.size())
    for actual, quantile in (("median", .5), ("q1", .25), ("q3", .75)):
        np.testing.assert_array_equal(summary[actual], independent.quantile(quantile))
    assert int(counts.sum()) == len(pairs) and len(summary) == 60
    np.testing.assert_array_equal(np.diff(time_edges), np.full(60, .5))
    figure = render_segment_temporal_evidence_export_figure(recipe)
    _style_figure_for_paper(figure)
    axes_by_id = {axis.get_gid(): axis for axis in figure.axes}
    app_axis = axes_by_id["compare-temporal-chronological-axis"]
    colorbar = axes_by_id["compare-temporal-colorbar-axis"]
    axes_by_id["compare-temporal-folded-axis"].remove()
    for annotation in list(figure.texts):
        annotation.remove()
    figure.set_size_inches(17, 17)
    figure.set_facecolor("white")
    left, width, height = .115, .765, .208
    app_axis.set_position([left, .105, width, height])
    colorbar.set_box_aspect(None)
    colorbar.set_aspect("auto")
    colorbar.set_position([.899, .105, .011, height])
    app_axis.tick_params(labelsize=10)
    app_axis.title.set_fontsize(12)
    app_axis.xaxis.label.set_fontsize(11)
    app_axis.yaxis.label.set_fontsize(11)
    colorbar.tick_params(labelsize=9)
    colorbar.yaxis.label.set_fontsize(10)
    for legend_text in app_axis.get_legend().get_texts():
        legend_text.set_fontsize(9)
    median_markers = next(artist for artist in app_axis.collections if artist.get_gid() == "temporal-bin-median-markers")
    np.testing.assert_array_equal(median_markers.get_offsets()[:, 1], summary["median"])
    for quantile in ("q1", "q3"):
        artist = next(line for line in app_axis.lines if line.get_gid() == f"temporal-bin-iqr-{quantile}")
        np.testing.assert_array_equal(artist.get_ydata(), summary[quantile])
    assert app_axis.get_yscale() == "function"

    # Preserve the entire publication image, including its blue moisture scale.
    # Align its internal plot rectangle with B and C without modifying pixels.
    calibration = features["axes"]
    image_height, image_width = image.shape[:2]
    source_plot_width = calibration["x_may1_px"] - calibration["x_april1_px"]
    source_plot_height = calibration["y_negative20_db_px"] - calibration["y_positive30_db_px"]
    raster_width = width * image_width / source_plot_width
    raster_height = height * image_height / source_plot_height
    source_left = left - raster_width * calibration["x_april1_px"] / image_width
    source_bottom = .695 - raster_height * (image_height - calibration["y_negative20_db_px"]) / image_height
    paper_axis = figure.add_axes([source_left, source_bottom, raster_width, raster_height])
    paper_axis.imshow(image, interpolation="nearest", aspect="auto")
    paper_axis.axis("off")
    native_axis = figure.add_axes([left, .405, width, height], facecolor="white")
    native_axis.scatter(pairs.days, pairs.delta_snr_db, s=2.5, c="black", alpha=.14, linewidths=0)
    native_axis.set(xlim=(0, 30), ylim=(-20, 30), yticks=np.arange(-20, 31, 5),
                    ylabel="Delta SNR G3ZIL−G4HZX (dB)", xlabel="Time (UTC)")
    native_axis.set_xticks([0, 7, 14, 21, 28, 30], ["01/04/17", "08/04/17", "15/04/17", "22/04/17", "29/04/17", "01/05/17"])
    native_axis.tick_params(labelsize=10)
    native_axis.grid(axis="y", color="#c7c7c7", linewidth=.7)
    native_axis.set_axisbelow(True)
    figure.text(.045, .977, "Griffiths & Squibb · Figure 3 evidence comparison", fontsize=22, weight="bold", color=INK)
    figure.text(.045, .952, "April 2017  |  G3ZIL − G4HZX  |  57,767 frozen same-cycle paired observations", fontsize=12, color=MUTED)
    figure.text(.045, .925, "A  Publication", fontsize=15, weight="bold", color=INK)
    figure.text(.045, .620, "B  Reconstruction from WSPRadar data", fontsize=15, weight="bold", color=INK)
    figure.text(.405, .620, "Every native pair; linear dB; no time binning or fitted offset", fontsize=11, color=MUTED)
    figure.text(.045, .347, "C  WSPRadar view · white export · 12h bins", fontsize=15, weight="bold", color=INK)
    figure.text(.045, .061, "A: Original publication raster. Blue points are soil moisture, not SNR summaries. Scatter darkness is not calibrated density.", fontsize=10, color=MUTED)
    figure.text(.045, .043, "B/C: Same frozen pairs. C retains the production 12-hour × 1-dB density, medians, IQR and median-centered nonlinear axis.", fontsize=10, color=MUTED)
    figure.text(.045, .025, "The duplicate-sensitive April 16 tail is examined separately. Source: Practical Wireless, October 2017, p. 24, Figure 3.", fontsize=10, color=MUTED)
    save_figure(figure, directory, "figure3_evidence_comparison", "Griffiths Figure 3: publication, reconstruction and WSPRadar")
    dispose_agg_figure(figure)
    return {"paired_observations": len(pairs), "time_bin": "12h", "temporal_bins": len(summary),
            "count_grid_sum": int(counts.sum()), "independent_12h_summary_check": "counts, medians, Q1 and Q3 exact",
            "production_artist_check": "all 60 median markers and both IQR curves exact; native nonlinear axis retained"}


def render_tail(pairs, expanded, features, image, directory):
    calibration = features["axes"]
    feature = next(feature for feature in features["features"] if feature["kind"] == "negative_tail")
    x0, x1, old_y0, old_y1 = source_bounds(feature, calibration, allowance=True)
    native = pairs.loc[pairs.days.between(x0, x1) & pairs.delta_snr_db.between(-20, -5)]
    combinations = expanded.loc[expanded.days.between(x0, x1) & expanded.delta_snr_db.between(-20, -5)].copy()
    strongest = combinations.loc[combinations.uses_strongest_reports & combinations.in_demo_population]
    weaker = combinations.loc[~combinations.uses_strongest_reports]
    outside = combinations.loc[combinations.uses_strongest_reports & ~combinations.in_demo_population]
    assert len(outside) == 0, "Display a separate population category if future source inputs change"
    assert len(strongest) == len(native) == 17 and len(weaker) == 343 and len(combinations) == 360
    original_tail = expanded.loc[expanded.days.between(x0, x1) & expanded.delta_snr_db.between(old_y0, old_y1) & expanded.delta_snr_db.lt(-15)]
    assert len(original_tail) == 38
    assert not (pairs.days.between(x0, x1) & pairs.delta_snr_db.between(old_y0, old_y1) & pairs.delta_snr_db.lt(-15)).any()
    combinations["classification"] = np.where(combinations.uses_strongest_reports, "retained_strongest_pair", "weaker_report_combination")
    columns = ["time", "tx_sign", "tx_loc", "id_target", "id_reference", "snr_target", "snr_reference",
               "power_target", "power_reference", "delta_snr_db", "classification"]
    combinations.sort_values(["time", "tx_sign", "id_target", "id_reference"])[columns].to_csv(directory / "figure3_tail_report_combinations.csv", index=False, lineterminator="\n")

    figure = plt.figure(figsize=(17, 10), facecolor="white")
    left = figure.add_axes([.075, .40, .405, .40])
    right = figure.add_axes([.57, .40, .405, .40])
    extent = (day_from_pixel(-.5, calibration), day_from_pixel(image.shape[1]-.5, calibration),
              snr_from_pixel(image.shape[0]-.5, calibration), snr_from_pixel(-.5, calibration))
    left.imshow(image, extent=extent, origin="upper", aspect="auto", interpolation="nearest")
    right.scatter(weaker.days, weaker.delta_snr_db, s=34, facecolors="none", edgecolors=MAGENTA, linewidths=1.1, zorder=3)
    right.scatter(native.days, native.delta_snr_db, s=42, c=NATIVE, edgecolors="white", linewidths=.45, zorder=5)
    left.set_title("A  Publication · enlarged Figure 3 region", loc="left", fontsize=12, weight="bold", pad=16)
    right.set_title("B  Frozen archive · strongest pairs and weaker combinations", loc="left", fontsize=12, weight="bold", pad=16)
    for axis in (left, right):
        axis.set(xlim=(15.15, 15.9), ylim=(-20, -5), yticks=[-20, -15, -10, -5],
                 xlabel="16 April 2017 · UTC interpretation", ylabel="Delta SNR, G3ZIL − G4HZX (dB)")
        axis.set_xticks(15 + np.array([6, 9, 12, 15, 18, 21])/24, ["06:00", "09:00", "12:00", "15:00", "18:00", "21:00"])
        axis.axvspan(15.15, x0, facecolor="white", alpha=.68, zorder=2)
        axis.axvspan(x1, 15.9, facecolor="white", alpha=.68, zorder=2)
        axis.axvline(x0, c=TEAL, ls="--", lw=1)
        axis.axvline(x1, c=TEAL, ls="--", lw=1)
        axis.set_axisbelow(True)
        axis.axhline(-15, c="#6C7F8B", lw=.9, ls=":")
        for allowance in (False, True):
            bx0, bx1, by0, by1 = source_bounds(feature, calibration, allowance=allowance)
            by1 = min(by1, -15)
            axis.add_patch(Rectangle((bx0, by0), bx1-bx0, by1-by0, fill=False, edgecolor=MAGENTA,
                                     linewidth=1.4, linestyle="--" if allowance else "-", zorder=6))
        axis.text((x0+x1)/2, -14.85, "T: original frozen tail window", color=MAGENTA, fontsize=9,
                  ha="center", va="bottom", bbox={"facecolor":"white", "edgecolor":"none", "alpha":.9})
    right.grid(c="#DBE2E6", lw=.6)
    figure.text(.075, .949, "Figure 3 · pairing and duplicate diagnostic", fontsize=23, weight="bold", color=INK)
    figure.text(.075, .908, "Expanded inspection: −20 to −5 dB  |  17 retained strongest pairs + 343 weaker-report combinations", fontsize=13, color=INK)
    figure.text(.075, .871, "Same source-defined horizontal readout allowance: 16 April 06:00:36–20:26:03 UTC. All 360 combinations are classified.", fontsize=11, color=MUTED)
    handles = [
        Line2D([], [], marker="o", linestyle="none", color=NATIVE, markersize=6, label="17 WSPRadar strongest-report pairs"),
        Line2D([], [], marker="o", linestyle="none", color=MAGENTA, markerfacecolor="none", markersize=7, label="343 additional weaker-report combinations"),
        Line2D([], [], color=TEAL, linestyle="--", label="Unchanged source horizontal readout allowance"),
        Line2D([], [], color=MAGENTA, label="T: original narrow region and pixel allowance (0 strongest / 38 combinations)"),
    ]
    figure.legend(handles=handles, loc="upper left", bbox_to_anchor=(.07,.326), ncol=2, frameon=False,
                  fontsize=10, columnspacing=2.4, handlelength=2.5)
    figure.text(.075, .220, "The added combinations use at least one weaker endpoint report from a repeated same-cycle transmission: 342 involve HB9MHB and one DL9GCW.\n"
                "The strongest-report policy retains one difference per transmitter identity and cycle. All 17 strongest combinations here match retained demo pairs.",
                fontsize=10.5, linespacing=1.6, color=INK)
    figure.text(.075, .148, "This wider diagnostic range is not a new paper-derived assertion. The original source box, strict ΔSNR < −15 dB test and expected mismatch remain unchanged.\n"
                "Counts are archive calculations; overlapping paper pixels cannot establish 360 separately visible points or statistically independent events.",
                fontsize=10.5, linespacing=1.6, color=MUTED)
    figure.text(.075, .073, "Alternative join: every same-time, same-transmitter/locator G3ZIL report × every G4HZX report. Equal reported TX powers cancel in each difference.\n"
                "This can explain the negative plume without proving the authors' query. Source: Practical Wireless, October 2017, p. 24, Figure 3; no fitted shift or offset.",
                fontsize=10, linespacing=1.6, color=MUTED)
    save_figure(figure, directory, "figure3_tail_diagnostic", "Griffiths Figure 3: expanded negative-tail pairing diagnostic")
    dispose_agg_figure(figure)
    return {"diagnostic_range_db_inclusive": [-20, -5], "horizontal_days_after_april1": [x0, x1],
            "retained_strongest_pairs": len(native), "weaker_report_combinations": len(weaker),
            "total_report_combinations": len(combinations), "weaker_by_transmitter": weaker.tx_sign.value_counts().to_dict(),
            "original_fixed_tail": {"retained_strongest_pairs": 0, "duplicate_expanded_combinations": len(original_tail)}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-directory", type=Path, default=PAPER)
    args = parser.parse_args()
    args.output_directory.mkdir(parents=True, exist_ok=True)
    paths = [PAPER / "paper_features.json", PAPER / "paper_figure3.png", PAPER / "frozen_inputs.json",
             PAPER / "comparison_policy.json", ARCHIVE / "expected_paired_rows.parquet", ARCHIVE / "source_rows.parquet", ARCHIVE / "demo.config"]
    hashes = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    pairs, expanded = load_pairing_evidence()
    features = read_json(PAPER / "paper_features.json")
    image = np.asarray(Image.open(PAPER / "paper_figure3.png").convert("RGB"))
    with matplotlib_operation_lock(), matplotlib.rc_context({"font.family": "DejaVu Sans", "font.size": 11, "pdf.fonttype": 42}):
        comparison = render_comparison(pairs, features, image, args.output_directory)
        diagnostic = render_tail(pairs, expanded, features, image, args.output_directory)
    assert hashes == {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    report = {"schema_version": 1, "builder": str(Path(__file__).relative_to(ROOT)),
              "builder_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "input_sha256": hashes, "comparison": comparison, "tail_diagnostic": diagnostic,
              "pdf_representation": "Native vector reconstruction, temporal cells and annotations; original publication raster only"}
    (args.output_directory / "figure3_render_checks.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
