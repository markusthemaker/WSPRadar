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
from types import SimpleNamespace

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
from matplotlib.collections import QuadMesh
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests/regression"))

from config.demo_pdf_headers import DEMO_PDF_HEADERS
from core.matplotlib_runtime import dispose_agg_figure, synchronized_matplotlib
from i18n import T
from scripts.internal.demo_pdf_footer import DEMO_PDF_FOOTER_TEXT, add_demo_pdf_footer
from scripts.internal.demo_pdf_header import add_demo_pdf_header, demo_pdf_metadata
from test_vanhamel_rotation_reference import _calculate_run, _assert_exact_trace
from ui.plots.evidence_figures import (
    _selected_evidence_export_recipe,
    _compare_temporal_profile_values,
    render_selected_evidence_export_figure,
)
from ui.results_export import _style_figure_for_paper


FIXTURE = ROOT / "tests/regression/reference_fixtures/vanhamel_fig6_rotation_v1"
OUTPUT_NAME = "figure6_overlay_1p6"
LANDMARK_COLOR = "#9d4b00"
ROTATION_COLOR = "#77438a"
NAVY = "#142c45"
BIN_HIGHLIGHT_COLORS = {1: "#aa610c", 8: "#7953a2", 15: "#087d70"}


def _production_recipe(run):
    labels = T["en"]
    return _selected_evidence_export_recipe(
        run.points, "Selected Station Evidence: M7AEO (IO82)", "12h", False,
        reference_snr_correction_db=run.context.reference_snr_correction_db,
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


def prepare_reconstruction(run):
    """Project current production evidence; no expected-results file is read.

    Reception order and the common endpoint display shift are presentation
    transformations. Pair selection, correction and Delta SNR come from the
    production post-fetch/map/Inspector pipeline executed by ``_calculate_run``.
    """
    points = run.points.sort_values("plot_time").reset_index(drop=True)
    endpoints = points[["plot_time", "station", "grid"]].merge(
        run.units[["evidence_utc", "peer_sign", "peer_grid", "target_snr_db", "reference_snr_db"]],
        left_on=["plot_time", "station", "grid"],
        right_on=["evidence_utc", "peer_sign", "peer_grid"],
        how="left", validate="one_to_one",
    )
    assert endpoints[["target_snr_db", "reference_snr_db"]].notna().all().all()
    selected_source = run.source_rows[
        run.source_rows.tx_sign.eq("M7AEO")
        & run.source_rows.tx_loc.str.upper().eq("IO82")
        & run.source_rows.rx_sign.isin(["ON4AWM0", "ON4AWM1"])
    ]
    assert not selected_source.empty and selected_source.power.eq(23).all()
    # The raw metadata establishes this declared common display shift. It does
    # not recalculate any pair, correction, difference, median or density cell.
    return SimpleNamespace(
        points=points,
        reception_indexes=np.arange(1, len(points) + 1),
        target_trace=endpoints.target_snr_db.to_numpy() - 7,
        reference_trace=endpoints.reference_snr_db.to_numpy() - 7,
        temporal_recipe=_production_recipe(run),
    )


def assert_reference_reconstruction(reconstruction):
    """Use the frozen independent oracle only as an assertion boundary."""
    _assert_exact_trace(reconstruction.points)
    expected = pd.read_csv(FIXTURE / "expected_paired_rows.csv")
    np.testing.assert_allclose(reconstruction.target_trace, expected.target_report_snr_db, rtol=0, atol=1e-12)
    np.testing.assert_allclose(reconstruction.reference_trace, expected.reference_report_snr_db + 1.6, rtol=0, atol=1e-12)


def prepare_reception_bin_mapping(reconstruction):
    """Map existing production UTC bins to chronological reception support."""
    recipe = reconstruction.temporal_recipe
    profile = recipe["prepared_profiles"]["chronological"][recipe["time_bin"]]
    counts, summary, utc_edges, _centers = _compare_temporal_profile_values(profile)
    edge_times = pd.DatetimeIndex(pd.to_datetime(mdates.num2date(utc_edges), utc=True))
    edge_ns = edge_times.to_numpy(dtype="datetime64[ns]").astype(np.int64)
    times = pd.to_datetime(reconstruction.points.plot_time, utc=True)
    point_ns = times.to_numpy(dtype="datetime64[ns]").astype(np.int64)
    if np.any(np.diff(point_ns) < 0):
        raise ValueError("Reception mapping requires chronological production points")
    if np.any(np.diff(edge_ns) <= 0):
        raise ValueError("UTC bin edges must increase strictly")
    if np.any(point_ns < edge_ns[0]) or np.any(point_ns >= edge_ns[-1]):
        raise ValueError("Reception mapping requires points inside the half-open UTC window")

    # Exact membership from timestamps; no interpolation between receptions.
    point_bin_indexes = np.searchsorted(edge_ns, point_ns, side="right") - 1
    pair_counts = np.bincount(point_bin_indexes, minlength=len(edge_ns) - 1)
    np.testing.assert_array_equal(pair_counts, counts.sum(axis=0))
    np.testing.assert_array_equal(pair_counts, summary["count"].fillna(0))
    np.testing.assert_array_equal(
        reconstruction.reception_indexes, np.arange(1, len(point_ns) + 1)
    )

    cumulative = np.concatenate(([0], np.cumsum(pair_counts)))
    # Retain repeated edges: an empty UTC column has zero reception width.
    reception_edges = cumulative.astype(float) + 0.5
    records = [
        {
            "bin_id": k + 1,
            "start_utc": edge_times[k],
            "end_utc": edge_times[k + 1],
            "pair_count": int(n),
            "first_reception": int(cumulative[k] + 1) if n else None,
            "last_reception": int(cumulative[k + 1]) if n else None,
        }
        for k, n in enumerate(pair_counts)
    ]
    return SimpleNamespace(
        reception_edges=reception_edges,
        utc_edges=utc_edges,
        edge_times=edge_times,
        pair_counts=pair_counts,
        point_bin_indexes=point_bin_indexes,
        count_grid=counts,
        y_edges=np.asarray(recipe["prepared_profiles"]["y_edges"], dtype=float),
        records=records,
    )


def draw_reception_density_bridge(axis, native_mesh, mapping):
    """Reuse native production cells/colour mapping and change only x geometry."""
    native_coordinates = native_mesh.get_coordinates()
    np.testing.assert_array_equal(native_coordinates[:, 0, 1], mapping.y_edges)
    np.testing.assert_array_equal(native_coordinates[0, :, 0], mapping.utc_edges)
    bridge = axis.pcolormesh(
        mapping.reception_edges,
        mapping.y_edges,
        native_mesh.get_array().copy(),
        cmap=native_mesh.get_cmap(),
        norm=native_mesh.norm,
        alpha=native_mesh.get_alpha(),
        shading="flat",
        zorder=1,
    )
    bridge.set_gid("vanhamel-reception-density-bridge")
    return bridge




@synchronized_matplotlib
def render_comparison(run, output_directory):
    """Render four linked panels without changing the production observations."""
    paper = json.loads((FIXTURE / "paper_features.json").read_text(encoding="utf-8"))
    reconstruction = prepare_reconstruction(run)
    assert_reference_reconstruction(reconstruction)
    mapping = prepare_reception_bin_mapping(reconstruction)
    points = reconstruction.points
    reception_indexes = reconstruction.reception_indexes

    figure = render_selected_evidence_export_figure(reconstruction.temporal_recipe)
    _style_figure_for_paper(figure)
    # Enlarge the page while retaining the reviewed 16:14.7 landscape ratio.
    figure.set_size_inches(22, 20.2125)
    figure.set_layout_engine(None)
    page_width, page_height = figure.get_size_inches() * 72
    # Expand the aligned panels to balance the outer content margins, including
    # the left y-axis labels and the shared colour-bar label on the right.
    plot_width_points = 1343
    colorbar_left_points = 1476

    def bounds(left, bottom, width, height):
        return [left / page_width, bottom / page_height, width / page_width, height / page_height]

    def text_at(left, bottom, text, size=12, **kwargs):
        return figure.text(left / page_width, bottom / page_height, text,
                           fontsize=size, color=NAVY, fontfamily="DejaVu Sans", **kwargs)

    axes_by_gid = {axis.get_gid(): axis for axis in figure.axes}
    chronological = axes_by_gid["compare-temporal-chronological-axis"]
    colorbar = axes_by_gid["compare-temporal-colorbar-axis"]
    figure.delaxes(axes_by_gid["compare-temporal-folded-axis"])
    chronological.set_position(bounds(104, 116, plot_width_points, 164))
    colorbar.set_position(bounds(colorbar_left_points, 116, 18, 432))
    colorbar.set_aspect("auto")
    colorbar.set_box_aspect(None)
    chronological.set_title("")
    native_mesh = next(item for item in chronological.collections if isinstance(item, QuadMesh))
    for item in list(figure.texts):
        item.remove()

    publication_axis = figure.add_axes(bounds(104, 1010, plot_width_points, 210))
    reconstruction_axis = figure.add_axes(bounds(104, 678, plot_width_points, 210))
    bridge_axis = figure.add_axes(bounds(104, 404, plot_width_points, 144))
    publication_axis.set_gid("vanhamel-publication-axis")
    reconstruction_axis.set_gid("vanhamel-reconstruction-axis")
    bridge_axis.set_gid("vanhamel-reception-density-axis")

    add_demo_pdf_header(figure, DEMO_PDF_HEADERS["vanhamel_figure6"])
    text_at(104, 1238, "Panel A - Original image from publication", 16, weight="bold")
    text_at(104, 906, "Panel B - Reconstruction: every paired reception", 16, weight="bold")
    text_at(104, 600, "Panel C - Linking the black ΔSNR curve to the 12-hour density bins", 16, weight="bold")
    text_at(104, 318, "Panel D - WSPRadar view: Δ SNR over Time (12h bins)", 16, weight="bold")

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
    reconstruction_axis.plot(reception_indexes, reconstruction.target_trace, color="#219af5", linewidth=1.15)
    reconstruction_axis.plot(reception_indexes, reconstruction.reference_trace, color="#fa004d", linestyle=":", linewidth=1.4)
    reconstruction_axis.plot(reception_indexes, points.metric, color="#101c20", linewidth=1.2)

    landmark_records = []
    for landmark in paper["black_trace_landmarks"]:
        center = landmark["reception_index_approx"]
        tolerance = paper["landmark_readout_policy"]["index_tolerance_receptions"]
        nearby = points.iloc[max(0, center - tolerance - 1):center + tolerance]
        index = nearby.metric.idxmin() if landmark["delta_snr_db_approx"] < 0 else nearby.metric.idxmax()
        observed = float(points.metric.iloc[index])
        assert abs(observed - landmark["delta_snr_db_approx"]) <= .4 + 1e-12
        publication_axis.scatter([center], [landmark["delta_snr_db_approx"]], s=65, facecolors="none", edgecolors=LANDMARK_COLOR, linewidths=1.1, zorder=5)
        reconstruction_axis.scatter([index + 1], [observed], s=65, facecolors="none", edgecolors=LANDMARK_COLOR, linewidths=1.1, zorder=5)
        landmark_records.append({"name": landmark["name"], "observed_reception_index": int(index + 1), "observed_delta_snr_db": observed, "observed_utc": points.plot_time.iloc[index].isoformat()})

    draw_reception_density_bridge(bridge_axis, native_mesh, mapping)
    bridge_axis.plot(reception_indexes, points.metric, color="#101c20", linewidth=1.0, zorder=4)
    bridge_axis.set(xlim=(0, len(points) + .5), ylim=(-8, 10.5),
                    xlabel="Reception number in chronological order", ylabel="ΔSNR (dB; linear)")
    bridge_axis.set_xticks([0, 250, 500, 750, 1000, 1250, len(points)])
    bridge_axis.xaxis.tick_top()
    bridge_axis.xaxis.set_label_position("top")
    bridge_axis.set_yticks([-5, 0, 5, 10])
    bridge_axis.spines[["top", "right"]].set_visible(False)

    # Every nonempty bin retains its ordinal support; UTC gaps have no ordinal width.
    for index, record in enumerate(mapping.records):
        color = BIN_HIGHLIGHT_COLORS.get(record["bin_id"], "#6e7b88")
        for axis, edges in ((bridge_axis, mapping.reception_edges), (chronological, mapping.utc_edges)):
            if axis is bridge_axis and not record["pair_count"]:
                continue
            left, right = edges[index:index + 2]
            is_bridge = axis is bridge_axis
            strip_bottom, strip_top = (-.045, -.013) if is_bridge else (1.012, 1.044)
            label_y = -.070 if is_bridge else 1.066
            axis.axvspan(left, right, ymin=strip_bottom, ymax=strip_top,
                         facecolor=color if record["pair_count"] else "white",
                         edgecolor="white" if record["pair_count"] else color,
                         linewidth=.6, hatch=None if record["pair_count"] else "///", clip_on=False)
            axis.text((left + right) / 2, label_y, str(record["bin_id"]),
                      transform=axis.get_xaxis_transform(), ha="center",
                      va="top" if is_bridge else "bottom",
                      fontsize=12, color=color, weight="bold", clip_on=False)
    bridge_axis.text(.5, -.195, "UTC bin number (matching Panel D)",
                     transform=bridge_axis.transAxes, ha="center", va="top",
                     fontsize=13, color=NAVY)

    legend_handles = [
        Line2D([], [], color="#219af5", label="ITA LWA II: Target (A, B)"),
        Line2D([], [], color="#fa004d", linestyle=":", label="Shorted dipole: corrected Reference (A, B)"),
        Line2D([], [], color="#101c20", label="ΔSNR: Target - Reference (A, B, C)"),
        Line2D([], [], color=LANDMARK_COLOR, marker="o", markerfacecolor="none", linestyle="none", label="Seven independently read landmarks (A, B)"),
    ]
    figure.legend(handles=legend_handles, loc="upper left",
                  bbox_to_anchor=(104 / page_width, 971 / page_height, plot_width_points / page_width, 0),
                  ncol=4, mode="expand", borderaxespad=0, frameon=False,
                  fontsize=12.5, columnspacing=1.5, handlelength=2.2)
    text_at(104, 630, "Panels A and B use identical linear axes and reported SNR for the antenna traces. No fitted shift, amplitude scaling or time warp.", 12)
    text_at(104, 342, "Each column is one UTC bin: Panel C counts receptions; Panel D shows elapsed time. Cells are 1 dB high; their centres and edges shift by the negative Reference correction.", 12)
    text_at(104, 50, "Matching bin numbers link Panels C and D. Empty bins (hatched in Panel D) have no width in Panel C. Final bin: 1 h 45 min.", 12)
    text_at(104, 31, "Bins start at 17:15 / 05:15 UTC. Panel D retains its nonlinear dB axis, medians, IQR and tail cells. Reception 750 does not date the rotation.", 12)
    add_demo_pdf_footer(figure, right=(page_width - 43.14) / page_width, bottom=12 / page_height)

    colorbar.set_ylabel("Relative joint-spot density (% of panel maximum) - shared by Panels C and D", fontsize=12)
    reconstruction_axis.xaxis.labelpad = 0
    bridge_axis.xaxis.labelpad = 7
    chronological.xaxis.labelpad = -3
    for axis in figure.axes:
        axis.tick_params(labelsize=12, colors=NAVY)
        axis.xaxis.label.set(fontsize=13, color=NAVY, fontfamily="DejaVu Sans")
        axis.yaxis.label.set(fontsize=13, color=NAVY, fontfamily="DejaVu Sans")
        for label in axis.texts:
            label.set_fontfamily("DejaVu Sans")
            label.set_fontsize(max(label.get_fontsize(), 12))
        legend = axis.get_legend()
        if legend is not None:
            for label in legend.get_texts():
                label.set_fontsize(12)
                label.set_fontfamily("DejaVu Sans")
        for collection in axis.collections:
            collection.set_rasterized(False)
            if axis is colorbar and isinstance(collection, QuadMesh):
                collection.set_edgecolor("face")

    output_directory.mkdir(parents=True, exist_ok=True)
    try:
        figure.savefig(output_directory / f"{OUTPUT_NAME}.png", dpi=150, facecolor="white")
        with matplotlib.rc_context({"pdf.fonttype": 42}):
            figure.savefig(output_directory / "WSPRadar_Demo_Vanhamel_Figure6.pdf", facecolor="white",
                           metadata={**demo_pdf_metadata(DEMO_PDF_HEADERS["vanhamel_figure6"]),
                                     "Subject": "Four panels; production density bins mapped to reception spans; Reference correction +1.6 dB"})
    finally:
        dispose_agg_figure(figure)
    return {
        "builder": str(Path(__file__).relative_to(ROOT)).replace("\\", "/"),
        "builder_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "footer_text": DEMO_PDF_FOOTER_TEXT,
        "figure": 6,
        "source": "Frozen raw reports, actual generated SQL, production post-fetch and selected-station preparation",
        "paired_observations": len(points),
        "reference_correction_db": run.context.reference_snr_correction_db,
        "temporal_density_contract": "correction-aware-1db-v1: membership-only d+c rounded to 0.1 dB, then k=floor(coordinate+0.5); physical interval [k-0.5-c, k+0.5-c)",
        "density_expectations": "expected_density_12h_correction_aware_v1.csv; legacy expected_density_12h.csv retained unchanged",
        "page_size_inches": [22, 20.2125],
        "horizontal_layout_points": {"plot_left": 104, "plot_width": plot_width_points, "colorbar_left": colorbar_left_points, "colorbar_width": 18},
        "panel_a": "Original full embedded publication raster, with fixed tick calibration and external landmark rings",
        "panel_b": "Every WSPRadar paired reception; endpoint SNR subtracts common 7 dB normalization only to match paper display; paired difference unchanged",
        "panel_c": "Unchanged black paired Delta SNR trace; native density values, masks, colours and global normalization projected onto exact reception-number membership spans; linear dB axis",
        "panel_d": "Actual selected_benchmark_temporal chronological artists and production white export styling; 12h bins, UTC axis, median-centered nonlinear delta SNR",
        "scientific_expectations_updated": False,
        "expectation_input_boundary": "Frozen expected files are read only by assert_reference_reconstruction; plotted data are prepared exclusively from current production points, endpoint units and source power metadata",
        "scientific_pipeline": ["build_analysis_batches / generated SQL", "offline SQLite compatibility execution", "apply_post_fetch_filters", "build_map_data_result", "build_compare_inspector_view_model", "_build_compare_unit_rows", "_retain_thresholded_compare_outcomes", "_compare_joint_evidence_points(require_paired_eligible=True)", "_selected_evidence_export_recipe", "render_selected_evidence_export_figure", "_style_figure_for_paper"],
        "presentation_adaptations": ["Full publication raster in calibrated reception-number/dB coordinates", "One-based chronological reception index", "Common -7 dB endpoint display shift to reported SNR; paired Delta SNR unchanged", "Production chronological subplot repositioned to Panel D; UTC-hour companion omitted", "Native density cells projected onto reception support edges in Panel C; repeated edges give empty UTC bins zero width", "Matching one-based bin labels in Panels C and D", "Panel C reception scale above and bin-number scale below", "Independently read paper landmarks shown as review annotations only"],
        "unexercised_boundaries": ["Native ClickHouse", "Live provider HTTP/availability", "Runtime cache and full interactive application session"],
        "pdf_raster_boundary": "Only the original published Figure 6 image is raster; reconstruction, production density cells, lines, markers, text and axes remain vector",
        "observed_landmarks": landmark_records,
        "bin_mapping": [{**record, "start_utc": record["start_utc"].isoformat(), "end_utc": record["end_utc"].isoformat()} for record in mapping.records],
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
