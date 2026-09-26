"""Render Zander Figure 4 from raw-source production replay and paper evidence.

Frozen expected results are assertions only; they never supply plotted values.
The generated SQL runs offline through the bounded regression SQLite adapter.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "tests/regression")]
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.text import Text
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import numpy as np
import pandas as pd
from PIL import Image
from test_zander_experiment_a_reference import _calculate_run
from core.matplotlib_runtime import matplotlib_operation_lock
from scripts.demo_pdf_footer import DEMO_PDF_FOOTER_TEXT, add_demo_pdf_footer
from config.demo_pdf_headers import DEMO_PDF_HEADERS
from scripts.demo_pdf_header import add_demo_pdf_header, demo_pdf_metadata
from i18n import T
from ui.plots.evidence_figures import render_segment_insight_export_figure
from ui.results_export import _style_figure_for_paper

PAPER = ROOT / "tests/regression/reference_fixtures/zander_fig4_paper_v1"
ARCHIVE = ROOT / "tests/regression/reference_fixtures/zander_experiment_a_v1"
OUTPUT = PAPER / "figure4_histogram_overlay.png"


def build_comparison_inputs(source_rows=None, configuration_document=None):
    """Calculate every plotted reconstruction value through current production.

    This function deliberately never opens expected_* files. Coarse rebinning
    changes only the display of the actual production 1 dB histogram counts.
    """
    annotations = json.loads((PAPER / "paper_features.json").read_text(encoding="utf-8"))
    policy = json.loads((PAPER / "comparison_policy.json").read_text(encoding="utf-8"))
    if source_rows is None:
        source_rows = pd.read_csv(ARCHIVE / "source_rows.csv", float_precision="round_trip")
    run = _calculate_run(source_rows, configuration_document)
    recipe = run.recipe["spot_histogram"]
    differences = run.points["metric"].to_numpy(dtype=float)
    sample_count = int(recipe["value_count"])
    assert recipe["bin_width"] == 1 and sample_count == len(differences)
    fine_counts = np.asarray(recipe["counts"], dtype=int)
    fine_centers = np.asarray(recipe["centers"], dtype=float)
    percentages = 100 * fine_counts / sample_count
    edges = np.asarray(policy["nominal_edges_db"], dtype=float)
    widths = np.diff(edges)
    counts = np.histogram(fine_centers, bins=edges, weights=fine_counts)[0]
    assert counts.sum() == fine_counts.sum() == sample_count, "Do not renormalize clipped evidence"
    density = counts / (sample_count * widths)
    paper_density = np.array([entry["density_per_db"] for entry in annotations["digitization"]["bins"][:9]])
    return SimpleNamespace(
        run=run, annotations=annotations, policy=policy, recipe=recipe,
        differences=differences, sample_count=sample_count,
        percentages=percentages, edges=edges, widths=widths, counts=counts,
        density=density, paper_density=paper_density, residuals=density-paper_density,
        mean=float(recipe["mean"]), median=float(recipe["median"]),
        sample_sd=float(differences.std(ddof=1)),
        identities=len(run.points[["station", "grid"]].drop_duplicates()),
        cycles=int(run.points["plot_time"].nunique()),
    )


def verify_comparison_inputs_against_references(comparison):
    """Let independent expectations reject a render, never generate its values."""
    fine_expected = pd.read_csv(ARCHIVE / "expected_histogram_1db.csv", float_precision="round_trip")
    np.testing.assert_array_equal(comparison.recipe["centers"], fine_expected.delta_snr_db)
    np.testing.assert_array_equal(comparison.recipe["counts"], fine_expected.joint_spots)
    np.testing.assert_allclose(comparison.percentages, fine_expected.percent_of_sample, rtol=0, atol=1e-12)
    paired_expected = pd.read_csv(ARCHIVE / "expected_paired_rows.csv", float_precision="round_trip")
    actual_pairs = comparison.run.points.rename(columns={
        "station": "peer_sign", "grid": "peer_grid", "metric": "delta_snr_db",
    }).copy()
    actual_pairs["time_slot"] = pd.to_datetime(actual_pairs["plot_time"], utc=True).dt.as_unit("s").astype("int64") // 120
    keys = ["time_slot", "peer_sign", "peer_grid"]
    columns = keys + ["delta_snr_db"]
    pd.testing.assert_frame_equal(
        actual_pairs[columns].sort_values(keys).reset_index(drop=True),
        paired_expected[columns].sort_values(keys).reset_index(drop=True),
        check_dtype=False, check_exact=True,
    )
    tolerance = comparison.annotations["digitization"]["density_absolute_readout_tolerance_per_db"]
    assert np.all(np.abs(comparison.residuals) <= tolerance)
    assert np.isclose(comparison.percentages.sum(), 100)
    assert np.isclose(np.dot(comparison.density, comparison.widths), 1)


def render_comparison(comparison, output_path):
    """Render three comparison panels with the unchanged native histogram.

    The page retains its 5:3 aspect ratio, the original publication raster and
    the residual diagnostic. Only displayed numbers are rounded; calculated
    observations, histogram values and provenance retain their full precision.
    """
    annotations, recipe = comparison.annotations, comparison.recipe
    percentages, edges, widths = comparison.percentages, comparison.edges, comparison.widths
    density, paper_density, residuals = comparison.density, comparison.paper_density, comparison.residuals
    mean, sample_sd, median = comparison.mean, comparison.sample_sd, comparison.median
    identities, cycles = comparison.identities, comparison.cycles
    sample_count = comparison.sample_count

    INK, MUTED, TEAL, ORANGE = "#172B3A", "#526572", "#148A91", "#D9792C"
    BACKGROUND, GRID = "white", "#DEE5E7"
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 12, "text.color": INK,
        "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
        "axes.edgecolor": "#91A0A8", "figure.facecolor": BACKGROUND,
        "axes.facecolor": "white", "savefig.facecolor": BACKGROUND,
    })
    # Retain the production figure and its actual right-hand histogram artists.
    # The common paper-export style changes the background, not series colours,
    # binning, statistics, axis limits or transformations.
    native_recipe = dict(comparison.run.recipe)
    native_recipe["paired_evidence_title"] = T["en"]["fig_joint_spot_delta"]
    native_recipe["metric_axis_label"] = T["en"]["tbl_col_delta_snr"]
    figure = render_segment_insight_export_figure(native_recipe)
    _style_figure_for_paper(figure)
    app_axis = next(axis for axis in figure.axes if any(
        patch.get_gid() == "spot-metric-histogram" for patch in axis.patches
    ))
    for axis in list(figure.axes):
        if axis is not app_axis:
            figure.delaxes(axis)
    for page_text in list(figure.texts):
        page_text.remove()
    figure.set_size_inches(24, 14.4)
    figure.set_layout_engine(None)
    lefts, width, bottom, height = [.055, .375, .695], .27, .424, .30
    app_axis.set_box_aspect(None)
    app_axis.set_position([lefts[2], bottom, width, height])
    app_axis.set_title(native_recipe["paired_evidence_title"], fontsize=13, pad=12)
    native_legend = app_axis.get_legend()
    median_handles, median_labels = app_axis.get_legend_handles_labels()
    if native_legend is not None:
        native_legend.remove()
    for native_text in app_axis.findobj(Text):
        native_text.set_fontfamily("DejaVu Sans")
        native_text.set_fontsize(13)
        native_text.set_color(INK)
    app_axis.tick_params(labelsize=12)

    add_demo_pdf_header(figure, DEMO_PDF_HEADERS["zander_figure4"])
    titles = ["Panel A - Original publication", "Panel B - Reconstruction", "Panel C - WSPRadar view"]
    subtitles = ["Original image; orange line: paper’s normal curve.", "Paper-style bins, with digitized paper bars overlaid.", "Native Joint-Spot histogram with 1 dB bins."]
    for left, title, subtitle in zip(lefts, titles, subtitles):
        figure.text(left, .796, title, fontsize=16, weight="bold")
        figure.text(left, .773, subtitle, fontsize=12, color=MUTED)

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
    for axis in [overlay_axis]:
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
    figure.legend(handles=[
        Line2D([], [], color=ORANGE, lw=2.2, label="Paper bars (digitized)"),
        Patch(facecolor=TEAL, alpha=.35, edgecolor=TEAL, label="Reconstruction (B)"),
    ], labels=["Paper bars (B)", "Reconstruction (B)"],
        loc="center", bbox_to_anchor=(lefts[1] + width / 2, .361),
        ncol=2, fontsize=13, frameon=False)
    figure.legend(handles=[
        Patch(facecolor="#36aaf9", alpha=.70, edgecolor="#67c4ff", label="Joint Spots (C)"),
        *median_handles,
    ], labels=["Joint Spots (C)",
               *[f"{label} (C)" for label in median_labels]],
        loc="center", bbox_to_anchor=(lefts[2] + width / 2, .361),
        ncol=2, fontsize=13, frameon=False)
    overlay_axis.annotate("Final flat region combines\ntwo source bars", xy=(1.9, density[-1]), xytext=(-.5, .034),
                          fontsize=12, color=MUTED, arrowprops={"arrowstyle": "-", "color": MUTED, "lw": .8})

    bars = [patch for patch in app_axis.patches if patch.get_gid() == "spot-metric-histogram"]
    np.testing.assert_allclose([bar.get_height() for bar in bars], percentages, rtol=0, atol=1e-12)
    np.testing.assert_array_equal([bar.get_x() + bar.get_width()/2 for bar in bars], recipe["centers"])

    # Retain the former C residual evidence as a smaller unlettered supporting plot.
    figure.text(lefts[1], .324, "Agreement check - Panel B minus paper", fontsize=14, weight="bold")
    figure.text(lefts[1], .299, f"Maximum |residual| {np.abs(residuals).max() * 1e4:.2f} × 10⁻⁴ dB⁻¹", fontsize=12, color=MUTED)
    residual_axis = figure.add_axes([lefts[1], .180, width, .096])
    residual_axis.axhspan(-5, 5, color=ORANGE, alpha=.10)
    residual_axis.axhline(0, color="#71838D", lw=.8)
    residual_axis.stairs(residuals * 1e4, edges, color=TEAL, lw=1.8, baseline=None)
    residual_axis.scatter((edges[:-1] + edges[1:])/2, residuals * 1e4, color=TEAL, s=20)
    residual_axis.set(xlim=x_limits, ylim=(-5.8, 5.8), ylabel="Residual (×10⁻⁴ dB⁻¹)", xlabel="Target − Reference ΔSNR (dB)")
    residual_axis.set_xticks(calibration["x_tick_values_db"])
    residual_axis.set_yticks([-5, 0, 5])
    residual_axis.spines[["top", "right"]].set_visible(False)
    residual_axis.tick_params(labelsize=12)

    figure.text(lefts[0], .324, "Rounded paper statistics", fontsize=14, weight="bold")
    figure.text(lefts[0], .296, "Mean −6.8 dB  ·  Reported σ 3.5 dB", fontsize=14)
    figure.text(lefts[0], .256, "Current WSPRadar reconstruction", fontsize=14, weight="bold")
    figure.text(lefts[0], .228, f"Mean {mean:.1f} dB  ·  Sample σ {sample_sd:.1f} dB", fontsize=14, color=TEAL)
    figure.text(lefts[0], .196, f"{sample_count} receiver-cycle pairs · {identities} receiver identities · {cycles} cycles", fontsize=12, color=MUTED)

    figure.text(lefts[2], .324, "Same observations, finer display", fontsize=14, weight="bold")
    figure.text(lefts[2], .296, "The 1 dB bins reveal uneven counts and empty bins\nthat the paper’s coarser histogram combines.\nThe mean and standard deviation do not change.", fontsize=12, color=MUTED, va="top", linespacing=1.4)
    figure.text(lefts[2], .232, f"Panel B: density = count / ({sample_count} × bin width in dB);\nbar areas sum to 1. Panel C: percent of all {sample_count}\npairs per 1 dB bin; bar heights sum to 100%.", fontsize=12, color=MUTED, va="top", linespacing=1.4)
    figure.text(lefts[2], .177, "Read both histogram axes linearly. Panel C retains\nWSPRadar’s native binning, colours and statistics.", fontsize=12, color=MUTED, va="top", linespacing=1.4)
    figure.text(lefts[2], .131, "No fitted curve, time shift or density rescaling\nis applied to the reconstruction.", fontsize=12, color=MUTED, va="top", linespacing=1.4)

    figure.add_artist(Line2D([.055, .965], [.088, .088], transform=figure.transFigure, color=GRID, lw=1))
    figure.text(.055, .064, "READ  ΔSNR = Target − Reference: negative values favour the Reference vertical. Each Joint Spot pairs both signals at one receiver in one cycle.", fontsize=12)
    add_demo_pdf_footer(figure, right=.965, bottom=.018)

    figure.savefig(output_path, dpi=180, metadata={
        "Title": "Zander Figure 4: publication to reconstruction to WSPRadar",
        "Description": "Panel A original publication, Panel B fixed coarse-bin density overlay, Panel C native WSPRadar histogram; residual check retained underneath Panel B.",
        "Inputs": json.dumps({str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in [
            PAPER/"paper_features.json", PAPER/"comparison_policy.json", PAPER/"paper_figure4.png", ARCHIVE/"source_rows.csv", ARCHIVE/"demo.config"]}),
    })
    # Bars, lines and labels remain vector; only the original paper is raster.
    with matplotlib.rc_context({"pdf.fonttype": 42}):
        figure.savefig(output_path.with_name("WSPRadar_Demo_Zander_Figure4.pdf"), metadata={
            **demo_pdf_metadata(DEMO_PDF_HEADERS["zander_figure4"]),
            "Subject": "Vector histogram reconstruction and comparison with the original publication raster",
            "CreationDate": None, "ModDate": None,
        })
    plt.close(figure)
    print(json.dumps({"output": str(output_path), "sample_count": sample_count, "fine_bin_counts_and_bar_heights_verified": True, "maximum_density_residual": float(np.abs(residuals).max())}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-directory", type=Path, default=PAPER)
    output_directory = parser.parse_args().output_directory
    output_directory.mkdir(parents=True, exist_ok=True)
    comparison = build_comparison_inputs()
    verify_comparison_inputs_against_references(comparison)
    with matplotlib_operation_lock():
        render_comparison(comparison, output_directory / OUTPUT.name)
    provenance = {
        "scientific_values": "Current WSPRadar calculations from frozen raw provider reports; expected_* files are assertions only",
        "pipeline": [
            "validated demo.config -> AnalysisContext -> build_analysis_batches",
            "current generated SQL -> reference_sql.execute_generated_sql over source_rows.csv",
            "apply_post_fetch_filters -> build_map_data_result -> build_compare_inspector_view_model",
            "_build_compare_unit_rows -> _retain_thresholded_compare_outcomes -> _compare_joint_evidence_points",
            "_segment_figure_export_recipe -> spot_histogram",
        ],
        "adapter_limit": "SQLite executes the generated scientific SELECT, predicates, grouping and aggregation through a bounded ClickHouse-function adapter; this is not native ClickHouse verification",
        "presentation": {
            "footer_text": DEMO_PDF_FOOTER_TEXT,
            "A": "Original publication raster",
            "B": "Coarse paper-style rebinning of production 1 dB histogram counts; external digitized paper bars overlaid",
            "C": "Native production Joint-Spot histogram renderer, with unchanged bins, percentage heights, colours, median and mean; white paper-export theme",
            "style_specification": "config/demo_pdf_style.md",
            "page_inches": [24, 14.4],
            "page_aspect_ratio": "5:3 (unchanged)",
            "display_precision": "One decimal place for mean and sample standard deviation; at most two decimal places for other calculated display values; residuals use a coefficient times 10^-4 per dB; original paper and arXiv identifier unchanged",
            "axes": "Linear axes; native Panel C limits and tick policy retained",
            "legend": "Separate legends centered below Panels B and C, with panel-scoped labels; native red dashed median retained",
            "sample_standard_deviation": "Supplemental paper-review statistic: NumPy standard deviation with ddof=1 over actual production paired differences; this is not a statistic supplied by the app histogram recipe",
            "sample_standard_deviation_label": "Sample σ, following the paper's symbol for its estimated sample standard deviation; reconstruction still uses ddof=1",
        },
        "source_input_sha256": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (ARCHIVE / "source_rows.csv", ARCHIVE / "demo.config")
        },
        "assertion_only_input_sha256": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (ARCHIVE / "expected_paired_rows.csv", ARCHIVE / "expected_histogram_1db.csv")
        },
        "generated_sql_sha256": hashlib.sha256(comparison.run.analysis.query.encode("utf-8")).hexdigest(),
        "observed": {
            "raw_report_count": len(comparison.run.source_rows),
            "sql_group_count": len(comparison.run.sql_rows),
            "retained_group_count": len(comparison.run.processed),
            "joint_pairs": comparison.sample_count,
            "paired_receiver_identities": comparison.identities,
            "paired_cycles": comparison.cycles,
            "mean_delta_snr_db": comparison.mean,
            "median_delta_snr_db": comparison.median,
            "sample_std_delta_snr_db": comparison.sample_sd,
            "paper_style_region_counts": comparison.counts.tolist(),
            "maximum_paper_density_residual_per_db": float(np.abs(comparison.residuals).max()),
        },
    }
    (output_directory / "figure4_comparison_provenance.json").write_text(
        json.dumps(provenance, indent=2) + "\n", encoding="utf-8", newline="\n",
    )


if __name__ == "__main__":
    main()
