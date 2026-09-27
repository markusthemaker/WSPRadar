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

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests/regression"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as matplotlib_dates
from matplotlib.collections import QuadMesh
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd
from PIL import Image

from config.demo_pdf_headers import DEMO_PDF_HEADERS
from core.matplotlib_runtime import dispose_agg_figure, matplotlib_operation_lock
from i18n import T
from scripts.internal.demo_pdf_footer import add_demo_pdf_footer, DEMO_PDF_FOOTER_TEXT
from scripts.internal.demo_pdf_header import add_demo_pdf_header, demo_pdf_metadata
from ui.plots.evidence_figures import (
    _compare_temporal_profile_values,
    _prepare_temporal_metric_rows,
    _relative_density_values,
    _segment_temporal_evidence_export_recipe,
    render_segment_temporal_evidence_export_figure,
)
from ui.results_export import _style_figure_for_paper
from test_griffiths_temporal_reference import (
    _assert_paired_rows_match_reference, _canonical_paired_rows, _prepare_reference_run,
)


FIXTURES = ROOT / "tests/regression/reference_fixtures"
PAPER = FIXTURES / "griffiths_fig3_paper_v1"
ARCHIVE = FIXTURES / "griffiths_fig3_temporal_v1"
START = pd.Timestamp("2017-04-01T00:00Z")
INK, MUTED, TEAL, MAGENTA = "#172B3A", "#526572", "#007C83", "#B5366F"
NATIVE = "#35566A"
NATIVE_MARKER_AREA_POINTS2 = 7.0
NATIVE_MARKER_ALPHA = .30
SPUR_REPORT_URL = "https://valentfx.com/vanilla/uploads/Uploader/a9/f19334bbbcca28d72b85cb1f5be6ce.pdf"


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
    replay = _prepare_reference_run(ARCHIVE, ("12h",))
    pairs = _canonical_paired_rows(replay)
    # The frozen baseline may reject a changed computation; it never supplies
    # the plotted observations or replaces the newly calculated result.
    _assert_paired_rows_match_reference(replay)
    pairs["days"] = (pairs.evidence_utc - START).dt.total_seconds() / 86400
    # Independent duplicate-report diagnostic only: this all-combinations
    # join never feeds the reconstruction or supplies production pair values.
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
    check = selected_keys.merge(independent, on=keys, how="left", validate="one_to_one", suffixes=("_production", "_independent"))
    np.testing.assert_array_equal(check.delta_snr_db_production, check.delta_snr_db_independent)
    assert len(pairs) == 57767 and len(expanded) == 59019
    return pairs, expanded, replay


def temporal_recipe(pairs, *, reference_snr_correction_db):
    """Prepare production density using the replay context's numerical correction."""
    points = pairs.rename(columns={"evidence_utc": "plot_time", "delta_snr_db": "metric"})
    labels = T["en"]
    selection = read_json(ARCHIVE / "demo.config")["settings"]["core_parameters"]["time_selection"]
    return _segment_temporal_evidence_export_recipe(
        points[["plot_time", "metric"]], "Griffiths Figure 3 frozen evidence", "12h", "Joint spots",
        reference_snr_correction_db=reference_snr_correction_db,
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
        bin_iqr_label=labels["fig_temporal_bin_iqr"], time_bin_options=("1h", "12h"),
    )


def prepare_density_reconstruction(pairs, recipe):
    """Project production hourly density and every original paired marker.

    The count grid and its month-wide normalization are production outputs.
    Cell lookup only validates marker placement; it does not recalculate counts,
    pairing or Delta SNR. Production membership owns half-dB boundaries.
    """
    profiles = recipe["prepared_profiles"]
    counts, _, time_edges, _ = _compare_temporal_profile_values(profiles["chronological"]["1h"])
    y_edges = np.asarray(profiles["y_edges"], dtype=float)
    point_rows = _prepare_temporal_metric_rows(pairs.rename(columns={
        "evidence_utc": "plot_time", "delta_snr_db": "metric",
    }), reference_snr_correction_db=recipe["reference_snr_correction_db"])
    assert len(point_rows) == len(pairs) == int(counts.sum())
    point_times = matplotlib_dates.date2num(point_rows.plot_time.to_numpy())
    time_indexes = np.searchsorted(time_edges, point_times, side="right") - 1
    metric_indexes = np.searchsorted(profiles["metric_bin_ids"], point_rows.metric_bin)
    assert ((time_indexes >= 0) & (time_indexes < counts.shape[1])).all()
    assert ((metric_indexes >= 0) & (metric_indexes < counts.shape[0])).all()
    point_cell_counts = counts[metric_indexes, time_indexes]
    assert (point_cell_counts > 0).all()
    start_day = matplotlib_dates.date2num(START)
    return {
        "counts": counts,
        "relative_density": _relative_density_values(counts),
        "time_edges_days": time_edges - start_day,
        "y_edges_db": y_edges,
        "native_days": point_times - start_day,
        "native_delta_snr_db": point_rows.metric.to_numpy(),
        "native_cell_counts": point_cell_counts,
    }


def draw_density_reconstruction(axis, density):
    """Draw every native pair over the unchanged linear monthly density scale."""
    mesh = axis.pcolormesh(
        density["time_edges_days"], density["y_edges_db"], density["relative_density"],
        cmap="gray_r", norm=matplotlib.colors.Normalize(vmin=0, vmax=100),
        shading="flat", zorder=1,
    )
    mesh.set_gid("figure3-production-hourly-density")
    markers = axis.scatter(
        density["native_days"], density["native_delta_snr_db"],
        s=NATIVE_MARKER_AREA_POINTS2, c="black", alpha=NATIVE_MARKER_ALPHA,
        linewidths=0, zorder=2,
    )
    markers.set_gid("figure3-all-native-pairs")
    return mesh, markers


def save_figure(figure, directory, name, header_configuration, *, pdf_name):
    """Render both formats from the same artists, not a PNG embedded in PDF."""
    for axis in figure.axes:
        for artist in (*axis.collections, *axis.lines, *axis.patches):
            artist.set_rasterized(False)
            if isinstance(artist, QuadMesh):
                # Shared cell edges otherwise show white PDF-viewer seams.
                artist.set_edgecolor("face")
                artist.set_linewidth(.04)
    figure.savefig(directory / f"{name}.png", dpi=180, facecolor="white")
    figure.savefig(directory / pdf_name, facecolor="white", metadata={
        **demo_pdf_metadata(header_configuration),
        "Subject": "Scientific reference comparison; publication image with native vector reconstruction and WSPRadar artists",
        "Creator": "WSPRadar build_griffiths_figure3_comparisons.py",
        "CreationDate": None, "ModDate": None,
    })


def render_comparison(pairs, features, image, directory, *, reference_snr_correction_db):
    """Compare the original image with unchanged production observations and summaries."""
    recipe = temporal_recipe(pairs, reference_snr_correction_db=reference_snr_correction_db)
    density = prepare_density_reconstruction(pairs, recipe)
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
    left, width, height = .115, .765, .180
    app_axis.set_position([left, .114, width, height])
    colorbar.set_box_aspect(None)
    colorbar.set_aspect("auto")
    colorbar.set_position([.899, .114, .011, height])
    app_axis.tick_params(labelsize=10)
    app_axis.title.set_fontsize(12)
    app_axis.set_title("")  # The chart title is integrated into the panel heading.
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

    # Hide only the decorative outer raster frame; retain all chart content and
    # the source file unchanged. Calibrated source coordinates still align A/B/C.
    calibration = features["axes"]
    image_height, image_width = image.shape[:2]
    source_plot_width = calibration["x_may1_px"] - calibration["x_april1_px"]
    source_plot_height = calibration["y_negative20_db_px"] - calibration["y_positive30_db_px"]
    crop_left, crop_top = 20.5, 50.5
    crop_right, crop_bottom = image_width - 25.5, image_height - 20.5
    raster_width = width * (crop_right - crop_left) / source_plot_width
    raster_height = height * (crop_bottom - crop_top) / source_plot_height
    source_left = left - width * (calibration["x_april1_px"] - crop_left) / source_plot_width
    source_bottom = .642 - height * (crop_bottom - calibration["y_negative20_db_px"]) / source_plot_height
    paper_axis = figure.add_axes([source_left, source_bottom, raster_width, raster_height])
    paper_axis.imshow(image, interpolation="nearest", aspect="auto")
    paper_axis.set_xlim(crop_left, crop_right)
    paper_axis.set_ylim(crop_bottom, crop_top)
    paper_axis.axis("off")
    native_axis = figure.add_axes([left, .358, width, height], facecolor="white")
    density_mesh, _ = draw_density_reconstruction(native_axis, density)
    density_colorbar_axis = figure.add_axes([.899, .358, .011, height])
    density_colorbar = figure.colorbar(density_mesh, cax=density_colorbar_axis, ticks=[0, 25, 50, 75, 100])
    density_colorbar.set_label("Relative joint-spot density (% of panel maximum)", fontsize=10)
    density_colorbar.ax.tick_params(labelsize=9)
    native_axis.set(xlim=(0, 30), ylim=(-20, 30), yticks=np.arange(-20, 31, 5),
                    ylabel="Delta SNR G3ZIL−G4HZX (dB)", xlabel="Time (UTC)")
    native_axis.set_xticks([0, 7, 14, 21, 28, 30], ["01/04/17", "08/04/17", "15/04/17", "22/04/17", "29/04/17", "01/05/17"])
    native_axis.tick_params(labelsize=10)
    native_axis.grid(axis="y", color="#c7c7c7", linewidth=.7)
    native_axis.set_axisbelow(True)

    # Navigate to the existing expanded diagnostic, without redefining the
    # frozen paper feature or attributing the authors' undocumented join.
    tail_feature = next(feature for feature in features["features"] if feature["kind"] == "negative_tail")
    tail_start, tail_end, _, _ = source_bounds(tail_feature, calibration, allowance=True)
    tail_low_db, tail_high_db = -20, 0
    tail_pdf = "WSPRadar_Demo_Griffiths_Figure3_diagnostic.pdf"
    paper_x0 = calibration["x_april1_px"] + tail_start / 30 * source_plot_width
    paper_x1 = calibration["x_april1_px"] + tail_end / 30 * source_plot_width
    paper_y0 = calibration["y_positive30_db_px"] + (30 - tail_high_db) / 50 * source_plot_height
    paper_y1 = calibration["y_positive30_db_px"] + (30 - tail_low_db) / 50 * source_plot_height
    for axis, rectangle, arrow_target, label_position in (
        (paper_axis, (paper_x0, paper_y0, paper_x1-paper_x0, paper_y1-paper_y0),
         (paper_x1, (paper_y0+paper_y1)/2),
         (calibration["x_april1_px"] + 19/30 * source_plot_width,
          calibration["y_positive30_db_px"] + (30+12.5)/50 * source_plot_height)),
        (native_axis, (tail_start, tail_low_db, tail_end-tail_start, tail_high_db-tail_low_db),
         (tail_end, (tail_low_db+tail_high_db)/2), (19, -12.5)),
    ):
        axis.add_patch(Rectangle(
            rectangle[:2], rectangle[2], rectangle[3], fill=False,
            edgecolor=MAGENTA, linewidth=1.6, linestyle="--", zorder=8, clip_on=False,
        ))
        callout = axis.annotate(
            "Negative-tail discrepancy\nSee separate diagnostic PDF",
            xy=arrow_target, xytext=label_position, fontsize=10, color=MAGENTA,
            ha="left", va="center", linespacing=1.4,
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": .92, "pad": 3},
            arrowprops={"arrowstyle": "-", "color": MAGENTA, "linewidth": 1.2},
            zorder=9,
        )
        callout.set_url(tail_pdf)
    add_demo_pdf_header(figure, DEMO_PDF_HEADERS["griffiths_figure3"])
    figure.text(.045, paper_axis.get_position().y1 + .015, "A  Original image from publication", fontsize=15, weight="bold", color=INK)
    figure.text(.045, .553, "B  Reconstruction from WSPRadar data", fontsize=15, weight="bold", color=INK)
    figure.text(.475, .553, "All 57,767 pairs; 1h × 1dB density", fontsize=11, color=MUTED)
    figure.text(.045, .309, "C  WSPRadar view · Δ SNR over Time · 12h bins", fontsize=15, weight="bold", color=INK)
    figure.text(.045, .052, "A: Blue points show soil moisture, not SNR summaries. Scatter darkness is not calibrated density.", fontsize=10, color=MUTED)
    figure.text(.045, .039, "B: All paired dots over 1h density; the scale describes the background. C: 12h bins, medians, middle 50% (IQR) and nonlinear axis.", fontsize=10, color=MUTED)
    figure.text(.045, .026, "The demo opens with 24h bins; C uses 12h bins. Original figure: p. 24, Figure 3. The April 16 tail is examined in the separate PDF.", fontsize=10, color=MUTED)
    figure.text(
        .045, .013,
        f"Pairing and duplicate reports: {tail_pdf}",
        fontsize=10, color=MAGENTA, url=tail_pdf,
    )
    add_demo_pdf_footer(figure, right=.96, bottom=.013)
    save_figure(figure, directory, "figure3_evidence_comparison", DEMO_PDF_HEADERS["griffiths_figure3"],
                pdf_name="WSPRadar_Demo_Griffiths_Figure3.pdf")
    dispose_agg_figure(figure)
    return {"paired_observations": len(pairs), "time_bin": "12h", "temporal_bins": len(summary),
            "count_grid_sum": int(counts.sum()), "independent_12h_summary_check": "counts, medians, Q1 and Q3 exact",
            "production_artist_check": "all 60 median markers and both IQR curves exact; native nonlinear axis retained",
            "tail_diagnostic_callout": {
                "panels": ["A", "B"],
                "horizontal_days_after_april1": [tail_start, tail_end],
                "diagnostic_range_db_inclusive": [tail_low_db, tail_high_db],
                "publication_rectangle_pixels": [paper_x0, paper_y0, paper_x1, paper_y1],
                "pdf_link": tail_pdf,
                "scope": "Navigation to the existing expanded diagnostic; frozen paper feature and numerical expectations unchanged",
            },
            "reconstruction_density": {
                "time_bin": "1h", "snr_bin_width_db": 1,
                "count_grid_sum": int(density["counts"].sum()),
                "time_bins": int(density["counts"].shape[1]),
                "peak_cell_count": int(density["counts"].max()),
                "scale": "Production relative density, linear 0-100 percent of the full-month maximum; no per-hour normalization",
                "smoothing": "none; exact production count cells",
                "native_markers": len(density["native_days"]),
                "marker_area_points_squared": NATIVE_MARKER_AREA_POINTS2,
                "marker_alpha": NATIVE_MARKER_ALPHA,
                "marker_presentation": "Every production pair at its original coordinates, including coincident observations; fixed size and opacity are display choices",
                "colorbar_scope": "Unchanged density background only; overlaid black markers also contribute visual darkness",
                "display_limits_only_db": [-20, 30],
                "all_pairs_retained_before_display_clipping": True,
            }}


def draw_wrapped_figure_text(figure, x, y, text, width, *, fontsize, color, linespacing=1.25, **kwargs):
    """Wrap figure prose to a measured width without changing its words."""
    from matplotlib.font_manager import FontProperties

    renderer = figure.canvas.get_renderer()
    font = FontProperties(family="DejaVu Sans", size=fontsize)
    max_width = width * figure.bbox.width
    lines = []
    for paragraph in text.split("\n\n"):
        line = ""
        for word in paragraph.split():
            candidate = f"{line} {word}" if line else word
            candidate_width = renderer.get_text_width_height_descent(candidate, font, ismath=False)[0]
            if line and candidate_width > max_width:
                lines.append(line)
                line = word
            else:
                line = candidate
        lines.append(line)
    return figure.text(x, y, "\n".join(lines), fontsize=fontsize, linespacing=linespacing,
                       color=color, va="top", **kwargs)


def render_tail(pairs, expanded, features, image, directory):
    """Explain repeated database reports in the reviewed 0 to -20 dB display range."""
    calibration = features["axes"]
    feature = next(feature for feature in features["features"] if feature["kind"] == "negative_tail")
    x0, x1, old_y0, old_y1 = source_bounds(feature, calibration, allowance=True)
    native = pairs.loc[pairs.days.between(x0, x1) & pairs.delta_snr_db.between(-20, 0)]
    combinations = expanded.loc[expanded.days.between(x0, x1) & expanded.delta_snr_db.between(-20, 0)].copy()
    strongest = combinations.loc[combinations.uses_strongest_reports & combinations.in_demo_population]
    weaker = combinations.loc[~combinations.uses_strongest_reports]
    outside = combinations.loc[combinations.uses_strongest_reports & ~combinations.in_demo_population]
    assert len(outside) == 0, "Display a separate population category if future source inputs change"
    assert len(strongest) == len(native) == 94 and len(weaker) == 554 and len(combinations) == 648
    original_tail = expanded.loc[expanded.days.between(x0, x1) & expanded.delta_snr_db.between(old_y0, old_y1) & expanded.delta_snr_db.lt(-15)]
    assert len(original_tail) == 38
    assert not (pairs.days.between(x0, x1) & pairs.delta_snr_db.between(old_y0, old_y1) & pairs.delta_snr_db.lt(-15)).any()
    combinations["classification"] = np.where(combinations.uses_strongest_reports, "retained_strongest_pair", "weaker_report_combination")
    columns = ["time", "tx_sign", "tx_loc", "id_target", "id_reference", "snr_target", "snr_reference",
               "power_target", "power_reference", "delta_snr_db", "classification"]
    combinations.sort_values(["time", "tx_sign", "id_target", "id_reference"])[columns].to_csv(directory / "figure3_tail_report_combinations.csv", index=False, lineterminator="\n")

    # The example frequencies were independently checked against the public
    # database on 2026-09-26; the original source fixture has no frequency
    # column. Keep its identity in the audit data, but omit it from the PDF.
    # Check each displayed SNR and paired calculation against the fixture.
    example_time = pd.Timestamp("2017-04-16T10:46Z")
    example = expanded.loc[expanded.time.eq(example_time) & expanded.tx_sign.eq("HB9MHB")]
    example_target = example.drop_duplicates("id_target")
    example_reference = example.drop_duplicates("id_reference")
    assert sorted(example_target.snr_target.tolist()) == [-27, -26, -15, -5]
    assert sorted(example_reference.snr_reference.tolist()) == [-18, -8]
    assert example.power_target.eq(43).all() and example.power_reference.eq(43).all()
    assert len(example) == 8
    assert weaker.tx_sign.eq(example.tx_sign.iloc[0]).sum() == 551
    assert example.loc[example.uses_strongest_reports, "delta_snr_db"].tolist() == [3]

    figure = plt.figure(figsize=(17, 17), facecolor="white")
    add_demo_pdf_header(figure, DEMO_PDF_HEADERS["griffiths_figure3_diagnostic"])
    left = figure.add_axes([.075, .575, .395, .23])
    right = figure.add_axes([.570, .575, .395, .23])
    extent = (day_from_pixel(-.5, calibration), day_from_pixel(image.shape[1]-.5, calibration),
              snr_from_pixel(image.shape[0]-.5, calibration), snr_from_pixel(-.5, calibration))
    left.imshow(image, extent=extent, origin="upper", aspect="auto", interpolation="nearest")
    right.scatter(weaker.days, weaker.delta_snr_db, s=34, facecolors="none", edgecolors=MAGENTA, linewidths=1.1, zorder=3, clip_on=False)
    right.scatter(native.days, native.delta_snr_db, s=42, c=NATIVE, edgecolors="white", linewidths=.45, zorder=5, clip_on=False)
    figure.text(.075, .821, "A  Original image from publication", fontsize=13, weight="bold", color=INK)
    figure.text(.075, .839, "Enlarged detail", fontsize=10, color=MUTED)
    figure.text(.570, .821, "B  Database reports", fontsize=13, weight="bold", color=INK)
    figure.text(.570, .839, "Strongest pairs and additional combinations", fontsize=10, color=MUTED)
    for axis in (left, right):
        axis.set(xlim=(x0, x1), ylim=(-20, 0), yticks=[-20, -15, -10, -5, 0],
                 xlabel="16 April 2017 · Time (UTC)", ylabel="ΔSNR, G3ZIL − G4HZX (dB)")
        axis.set_xticks(15 + np.array([9, 12, 15, 18])/24, ["09:00", "12:00", "15:00", "18:00"])
        axis.set_axisbelow(True)
        axis.tick_params(labelsize=12)
        axis.xaxis.label.set_fontsize(12)
        axis.yaxis.label.set_fontsize(12)
    right.grid(c="#DBE2E6", lw=.6)
    handles = [
        Line2D([], [], marker="o", linestyle="none", color=NATIVE, markersize=7, label="94 WSPRadar strongest-report pairs"),
        Line2D([], [], marker="o", linestyle="none", color=MAGENTA, markerfacecolor="none", markersize=7, label="554 additional weaker-report combinations"),
    ]
    figure.legend(handles=handles, loc="upper center", bbox_to_anchor=(.7675, .528), ncol=1,
                  frameon=False, fontsize=12, handlelength=2.5, borderaxespad=0, labelspacing=.45)
    draw_wrapped_figure_text(figure, .075, .488, 'A receiver can report the same transmitter more than once within one WSPR cycle, at different reported frequencies.\nPairing every report from one receiver with every report from the other creates additional SNR differences.\nWSPRadar retains the strongest qualifying report at each receiver and calculates one paired difference.', 0.89,
                             fontsize=12, color=INK)
    figure.text(.075, .438, 'Worked example: one transmitting station → G3ZIL · 16 April 2017, 10:46 UTC', fontsize=13, weight="bold", color=INK)
    table_axis = figure.add_axes([.075, .306, .43, .112])
    table_axis.axis("off")
    table = table_axis.table(
        cellText=[["7.040194", "−27"], ["7.040125", "−15"], ["7.040094", "−5"], ["7.040033", "−26"]],
        colLabels=["Reported frequency (MHz)", "Reported SNR (dB)"],
        cellLoc="center", colWidths=[.57, .43], bbox=[0, 0, 1, 1],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    for (row, column), cell in table.get_celld().items():
        cell.set_edgecolor("#D8E0E5")
        cell.set_linewidth(.65)
        if row == 0:
            cell.set_facecolor("#E9EFF3")
            cell.set_text_props(weight="bold", color=INK)
        elif row == 3:
            cell.set_facecolor("#E2F0ED")
            cell.set_text_props(weight="bold", color=INK)
        else:
            cell.set_facecolor("white")
    draw_wrapped_figure_text(figure, .555, .414, "The table lists four G3ZIL reports of this station.\nFor the same transmitter and cycle, G4HZX supplied\ntwo further reports: −18 and −8 dB (not shown).\nPairing each table row with each G4HZX report\nproduces 4 × 2 = 8 possible SNR differences.\nWSPRadar uses the strongest report at each receiver:\n\n\nG3ZIL − G4HZX = −5 − (−8) = +3 dB.\n\n\nThis retained pair is above the plot's upper limit of 0 dB;\nfive of the other seven combinations fall inside it.\nAll six reports specify 43 dBm TX power, so\npower normalization does not change these differences.", 0.41,
                             fontsize=12, color=INK)
    figure.text(.075, .274, 'What explains the April 16 concentration?', fontsize=13, weight="bold", color=INK)
    draw_wrapped_figure_text(figure, .075, .268, 'One transmitting callsign accounts for 551 of the 554 additional weaker-report combinations in the displayed window.\nThe callsign is available upon request. These combinations do not represent separate transmissions.', 0.89,
                             fontsize=12, color=INK)
    figure.text(.075, .214, 'Evidence from other receivers', fontsize=13, weight="bold", color=INK)
    draw_wrapped_figure_text(figure, .075, .208, "At 10:46 UTC, both comparison receivers and many other stations reported a weaker signal from this transmitter\napproximately 30-31 Hz above their strongest report, typically about 10 dB lower in SNR. The wider database shows\nthe pattern becoming widespread at 03:22 UTC and declining sharply at 15:46 UTC, even as the strongest reports became stronger.\nMatching frequency offsets and relative strengths across receivers favour additional spectral components associated with the transmitted signal.\nPossible causes include unwanted modulation in the transmitter's oscillator, power supply or audio chain [1].\nThe physical cause remains unconfirmed; database reports alone cannot exclude a shared decoding artifact.", 0.89,
                             fontsize=12, color=INK)
    figure.text(.075, .129, 'Effect on the monthly comparison', fontsize=13, weight="bold", color=INK)
    draw_wrapped_figure_text(figure, .075, .123, 'Multiple reports affect 211 of 57,767 selected paired cycles (0.365%) across April. Excluding this one callsign leaves\nthe monthly median ΔSNR unchanged at +7 dB. This supports the stability of the monthly median, but does not establish\nthat every transmission was free of unwanted spectral components.', 0.89,
                             fontsize=12, color=INK)
    draw_wrapped_figure_text(figure, .075, .080, "The 648 combinations cover only the displayed range and time window (approximately 06:01-20:26 UTC).\nThe all-combinations calculation can explain the negative plume; the authors' exact pairing procedure is not known.", 0.89,
                             fontsize=11, color=MUTED)
    draw_wrapped_figure_text(figure, .075, .048, 'Additional analysis of April 2017 WSPR database reports, retrieved 26 September 2026. Frequency and SNR values were checked directly.\nOriginal figure: p. 24, Figure 3. [1] Griffiths, Elmore and Robinett, Some Observations While Using the KiwiSDR to Spot WSPR Stations, sections 4 and 7.', 0.89,
                             fontsize=10.5, color=MUTED, url=SPUR_REPORT_URL)
    figure.text(.075, .014, 'Read the supporting WSPR measurement report', fontsize=10.5, color=TEAL, url=SPUR_REPORT_URL)
    add_demo_pdf_footer(figure, right=.96, bottom=.014)
    save_figure(figure, directory, "figure3_tail_diagnostic", DEMO_PDF_HEADERS["griffiths_figure3_diagnostic"],
                pdf_name="WSPRadar_Demo_Griffiths_Figure3_diagnostic.pdf")
    dispose_agg_figure(figure)
    return {"diagnostic_range_db_inclusive": [-20, 0], "horizontal_days_after_april1": [x0, x1],
            "retained_strongest_pairs": len(native), "weaker_report_combinations": len(weaker),
            "total_report_combinations": len(combinations), "weaker_by_transmitter": weaker.tx_sign.value_counts().to_dict(),
            "original_fixed_tail": {"retained_strongest_pairs": 0, "duplicate_expanded_combinations": len(original_tail)},
            "worked_example": {"transmitter": "HB9MHB", "utc": example_time.isoformat(),
                               "target_reported_frequency_mhz": [7.040194, 7.040125, 7.040094, 7.040033],
                               "target_reported_snr_db": [-27, -15, -5, -26],
                               "reference_reported_snr_db": [-18, -8], "retained_delta_snr_db": 3,
                               "frequency_source": "WSPR Live database reports retrieved 2026-09-26, independently matching the documented WSPR Rocks example; frequencies absent from original source_rows.parquet",
                               "public_identity": "withheld; callsign available upon request",
                               "database_research": {"captured_on": "2026-09-26",
                                   "provider": "https://db1.wspr.live/",
                                   "all_receiver_download_sha256": "d8cc0f74e091ce0080272b187d22a488b944d4240a1d9324bb693d503b5a793d",
                                   "displayed_weaker_combinations_from_one_callsign": 551,
                                   "monthly_selected_pairs_with_multiple_reports": 211,
                                   "monthly_selected_pairs": 57767,
                                   "monthly_median_db_with_and_without_callsign": 7,
                                   "widespread_offset_hz": [30, 31],
                                   "first_widespread_cycle_utc": "2017-04-16T03:22:00Z",
                                   "marked_decline_cycle_utc": "2017-04-16T15:46:00Z",
                                   "evidence_boundary": "New database analysis, not a claim from the publication; physical cause unconfirmed"},
                               "hypothesis_source": SPUR_REPORT_URL,
                               "cause_in_this_example": "unconfirmed"}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-directory", type=Path, default=PAPER)
    args = parser.parse_args()
    args.output_directory.mkdir(parents=True, exist_ok=True)
    paths = [PAPER / "paper_features.json", PAPER / "paper_figure3.png", PAPER / "frozen_inputs.json",
             PAPER / "comparison_policy.json", ARCHIVE / "expected_paired_rows.parquet", ARCHIVE / "source_rows.parquet", ARCHIVE / "demo.config"]
    hashes = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    pairs, expanded, replay = load_pairing_evidence()
    features = read_json(PAPER / "paper_features.json")
    image = np.asarray(Image.open(PAPER / "paper_figure3.png").convert("RGB"))
    with matplotlib_operation_lock(), matplotlib.rc_context({"font.family": "DejaVu Sans", "font.size": 11, "pdf.fonttype": 42}):
        comparison = render_comparison(pairs, features, image, args.output_directory,
                                       reference_snr_correction_db=replay.context.reference_snr_correction_db)
        diagnostic = render_tail(pairs, expanded, features, image, args.output_directory)
    assert hashes == {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    report = {"schema_version": 1, "builder": str(Path(__file__).relative_to(ROOT)),
              "footer_text": DEMO_PDF_FOOTER_TEXT,
              "builder_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "input_sha256": hashes, "comparison": comparison, "tail_diagnostic": diagnostic,
              "reconstruction_origin": {
                  "input": "source_rows.parquet only; expected_paired_rows is checked after calculation",
                  "stages": "generated SQL via SQLite adapter; strict-to-legacy selection; post-fetch; map; Inspector; native pairs; production temporal recipe",
                  "source_rows": replay.source_row_count, "strict_sql_rows": replay.strict_row_count,
                  "selected_sql_rows": replay.input_row_count,
                  "selected_query_sha256": hashlib.sha256(replay.analysis.query.encode("utf-8")).hexdigest(),
                  "limit": "No native ClickHouse engine, HTTP, cache/admission or provider geographic-distance validation",
              },
              "pdf_representation": "Native vector reconstruction, temporal cells and annotations; original publication raster only"}
    (args.output_directory / "figure3_render_checks.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
