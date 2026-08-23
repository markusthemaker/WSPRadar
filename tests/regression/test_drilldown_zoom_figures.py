from copy import deepcopy
from types import SimpleNamespace

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.collections import QuadMesh
from matplotlib.colors import to_rgba
import matplotlib.dates as mdates
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
import pytest

from ui.inspector.evidence_data import (
    _build_compare_unit_rows,
    _compare_joint_evidence_points,
)
from ui.inspector.drilldown_focus import (
    DrilldownFocusWindow,
    DrilldownOutlierCandidateContext,
)
from ui.components import segment_inspector
from ui.plots.evidence_figures import (
    DELTA_SNR_OUTLIER_MARKER_FACE_COLOR,
    DELTA_SNR_OUTLIER_MARKER_INNER_EDGE_COLOR,
    DELTA_SNR_OUTLIER_MARKER_SIZE,
)
from ui.plots.drilldown_zoom_figures import (
    DRILLDOWN_ZOOM_BENCHMARK_NATIVE_KIND,
    DRILLDOWN_ZOOM_FIGURE_LAYOUT_VERSION,
    DRILLDOWN_ZOOM_NATIVE_RECIPE_SCHEMA_VERSION,
    _expand_chronological_column,
    build_drilldown_zoom_benchmark_delta_snr_recipe,
    build_drilldown_zoom_outlier_overlay_recipe,
    build_drilldown_zoom_performance_snr_recipe,
    render_drilldown_zoom_benchmark_delta_snr_figure,
    render_drilldown_zoom_performance_snr_figure,
)


START_UTC = pd.Timestamp("2026-07-10T00:00:00Z")
END_UTC = pd.Timestamp("2026-07-10T12:00:00Z")


def _overlay_labels():
    return {
        "marker": "Outlier candidate",
        "focused_episode": "Focused episode",
        "local_baseline": "Expected local Delta SNR",
        "flank_baseline": "Pre/post flank baseline",
        "robust_z": "Robust-z guide |z| = {value:g}",
        "qualifying_robust_z": (
            "Robust-z qualifying threshold |z| = {value:g}"
        ),
        "absolute_departure": "Absolute-departure gate (+/-{value:g} dB)",
    }


def _outlier_overlay(*, minimum_robust_z=4.0):
    return build_drilldown_zoom_outlier_overlay_recipe(
        representative_utc="2026-07-10T06:00:00Z",
        representative_delta_snr_db=10.0,
        qualifying_marker_times_utc=[
            "2026-07-10T05:58:00Z",
            "2026-07-10T06:00:00Z",
            "2026-07-10T06:02:00Z",
        ],
        qualifying_marker_delta_snr_db=[7.0, 10.0, 8.0],
        candidate_start_utc="2026-07-10T05:58:00Z",
        candidate_end_utc="2026-07-10T06:02:00.000000001Z",
        native_evidence_unit_minutes=2.0,
        local_baseline_db=1.0,
        pre_baseline_db=0.5,
        post_baseline_db=1.5,
        pre_flank_start_utc="2026-07-10T00:00:00Z",
        pre_flank_end_utc="2026-07-10T05:48:00Z",
        post_flank_start_utc="2026-07-10T06:14:00Z",
        post_flank_end_utc="2026-07-10T12:00:00Z",
        robust_spread_db=2.0,
        robust_spread_method="mad",
        minimum_robust_z=minimum_robust_z,
        minimum_departure_db=6.0,
        labels=_overlay_labels(),
    )


def _benchmark_recipe(*, overlay=None):
    evidence = pd.DataFrame(
        {
            "plot_time": pd.to_datetime(
                [
                    "2026-07-10T05:56:00Z",
                    "2026-07-10T05:58:00Z",
                    "2026-07-10T06:00:00Z",
                    "2026-07-10T06:02:00Z",
                ],
                utc=True,
            ),
            "metric": [1.0, 7.0, 10.0, 8.0],
        }
    )
    return build_drilldown_zoom_benchmark_delta_snr_recipe(
        evidence,
        start_utc=START_UTC,
        end_utc=END_UTC,
        title="DG2CAD (JN47mv) - Time Window: 00:00 to 12:00 UTC",
        panel_title="Delta SNR over Time",
        x_label="Date/Time (UTC)",
        y_label="Delta SNR (dB)",
        empty_text="No paired evidence in this time window.",
        evidence_unit_label="Individual Joint Spot",
        is_sequential=False,
        outlier_overlay=overlay,
    )


def test_performance_native_recipe_keeps_each_successful_cycle_value():
    time_slots = [
        int((START_UTC + pd.Timedelta(minutes=minute)).timestamp() // 120)
        for minute in (0, 2, 4, 6, 8)
    ]
    rows = pd.DataFrame(
        {
            "time_slot": [*time_slots, time_slots[1], time_slots[-1] + 500],
            "hit": [1, 0, 1, 1, 1, 1, 1],
            "target_snr": [-10.25, np.nan, -8.75, np.inf, -7.5, -9.0, -3.0],
        }
    )

    recipe = build_drilldown_zoom_performance_snr_recipe(
        rows,
        start_utc=START_UTC,
        end_utc=START_UTC + pd.Timedelta(minutes=20),
        title="SEL (SE00) - Time Window: 00:00 to 00:20 UTC",
        panel_title="Normalized Target SNR over Time",
        x_label="Date/Time (UTC)",
        y_label="Normalized Target SNR (dB)",
        empty_text="No successful evidence in this time window.",
        evidence_unit_label="Individual successful opportunity",
    )

    assert recipe["schema_version"] == DRILLDOWN_ZOOM_NATIVE_RECIPE_SCHEMA_VERSION
    assert recipe["resolution"] == "native-evidence-unit"
    assert recipe["aggregation"] == "none"
    assert recipe["time_bin"] == "native"
    assert recipe["point_count"] == 4
    assert recipe["metric_db"].tolist() == [-10.25, -9.0, -8.75, -7.5]
    assert recipe["point_utc_ns"].tolist() == [
        int(START_UTC.value),
        int((START_UTC + pd.Timedelta(minutes=2)).value),
        int((START_UTC + pd.Timedelta(minutes=4)).value),
        int((START_UTC + pd.Timedelta(minutes=8)).value),
    ]
    assert "median" not in recipe
    assert "density" not in recipe
    assert "iqr" not in recipe


def test_sequential_recipe_has_one_point_per_complete_scheduled_pair():
    first_pair_id = int(START_UTC.timestamp() // 60)
    second_pair_id = first_pair_id + 10
    station_rows = pd.DataFrame(
        {
            "peer_sign": ["SEL"] * 7,
            "peer_grid": ["SE00"] * 7,
            "tx_ab_pair_id": [
                first_pair_id,
                first_pair_id,
                first_pair_id,
                first_pair_id,
                second_pair_id,
                second_pair_id,
                second_pair_id,
            ],
            "is_me": [1, 1, 0, 0, 1, 0, 0],
            "stat_val": [-10.0, -8.0, -13.0, -11.0, -7.0, -10.0, -8.0],
        }
    )
    identities = station_rows[["peer_sign", "peer_grid"]].drop_duplicates()
    comparison_units = _build_compare_unit_rows(
        station_rows,
        identities,
        is_sequential=True,
        paired_identity_df=identities,
    )
    evidence = _compare_joint_evidence_points(comparison_units)
    overlay = build_drilldown_zoom_outlier_overlay_recipe(
        representative_utc=START_UTC,
        representative_delta_snr_db=3.0,
        qualifying_marker_times_utc=[
            START_UTC,
            START_UTC + pd.Timedelta(minutes=10),
        ],
        qualifying_marker_delta_snr_db=[3.0, 2.0],
        candidate_start_utc=START_UTC,
        candidate_end_utc=(
            START_UTC
            + pd.Timedelta(minutes=10)
            + pd.Timedelta(nanoseconds=1)
        ),
        native_evidence_unit_minutes=10.0,
        local_baseline_db=-4.0,
        pre_baseline_db=-4.0,
        post_baseline_db=-4.0,
        pre_flank_start_utc=None,
        pre_flank_end_utc=None,
        post_flank_start_utc=None,
        post_flank_end_utc=None,
        robust_spread_db=1.0,
        robust_spread_method="mad",
        minimum_robust_z=3.0,
        minimum_departure_db=6.0,
        labels=_overlay_labels(),
    )

    recipe = build_drilldown_zoom_benchmark_delta_snr_recipe(
        evidence,
        start_utc=START_UTC,
        end_utc=END_UTC,
        title="SEL (SE00) - Time Window: 00:00 to 12:00 UTC",
        panel_title="Delta SNR over Time",
        x_label="Planned Target start (UTC)",
        y_label="Delta SNR (dB)",
        empty_text="No complete Scheduled Pairs.",
        evidence_unit_label="Individual complete Scheduled Pair",
        is_sequential=True,
        outlier_overlay=overlay,
    )

    assert len(station_rows) == 7
    assert len(comparison_units) == 2
    assert recipe["point_count"] == 2
    assert recipe["evidence_unit_kind"] == "complete_scheduled_pair"
    assert recipe["metric_db"].tolist() == pytest.approx([3.0, 2.0])
    assert recipe["point_utc_ns"].tolist() == [
        int(START_UTC.value),
        int((START_UTC + pd.Timedelta(minutes=10)).value),
    ]
    assert recipe["outlier_overlay"][
        "native_evidence_unit_width_ns"
    ] == int(pd.Timedelta(minutes=10).value)
    assert recipe["outlier_overlay"][
        "focused_episode_visual_start_utc_ns"
    ] == int((START_UTC - pd.Timedelta(minutes=5)).value)
    assert recipe["outlier_overlay"][
        "focused_episode_visual_end_utc_ns"
    ] == int((START_UTC + pd.Timedelta(minutes=15)).value)
    rendered_figure = render_drilldown_zoom_benchmark_delta_snr_figure(recipe)
    try:
        rendered_figure.canvas.draw()
    finally:
        rendered_figure.clear()


def test_outlier_overlay_uses_exact_modified_robust_z_boundaries():
    overlay = _outlier_overlay(minimum_robust_z=4.0)

    assert overlay["candidate_start_utc_ns"] == int(
        pd.Timestamp("2026-07-10T05:58:00Z").value
    )
    assert overlay["candidate_end_utc_ns"] == int(
        pd.Timestamp("2026-07-10T06:02:00.000000001Z").value
    )
    assert overlay["qualifying_marker_count"] == 3
    assert overlay["qualifying_marker_utc_ns"].tolist() == [
        int(pd.Timestamp("2026-07-10T05:58:00Z").value),
        int(pd.Timestamp("2026-07-10T06:00:00Z").value),
        int(pd.Timestamp("2026-07-10T06:02:00Z").value),
    ]
    assert overlay["qualifying_marker_delta_snr_db"].tolist() == [
        7.0,
        10.0,
        8.0,
    ]
    assert overlay["native_evidence_unit_width_ns"] == int(
        pd.Timedelta(minutes=2).value
    )
    assert overlay["focused_episode_visual_start_utc_ns"] == int(
        pd.Timestamp("2026-07-10T05:57:00Z").value
    )
    assert overlay["focused_episode_visual_end_utc_ns"] == int(
        pd.Timestamp("2026-07-10T06:03:00Z").value
    )
    guides = overlay["robust_z_guides"]
    assert [guide["robust_z"] for guide in guides] == [1.0, 2.0, 3.0, 4.0]
    for guide in guides:
        expected_offset = 2.0 * guide["robust_z"] / 0.6745
        assert guide["offset_db"] == pytest.approx(expected_offset)
        assert guide["lower_db"] == pytest.approx(1.0 - expected_offset)
        assert guide["upper_db"] == pytest.approx(1.0 + expected_offset)
    assert [
        guide["robust_z"]
        for guide in guides
        if guide["is_qualification_threshold"]
    ] == [4.0]
    assert overlay["absolute_departure_lower_db"] == -5.0
    assert overlay["absolute_departure_upper_db"] == 7.0


def test_outlier_overlay_deduplicates_standard_qualifying_z_threshold():
    overlay = _outlier_overlay(minimum_robust_z=3.0)

    guides = overlay["robust_z_guides"]
    assert [guide["robust_z"] for guide in guides] == [1.0, 2.0, 3.0]
    assert sum(
        bool(guide["is_qualification_threshold"]) for guide in guides
    ) == 1
    assert "qualifying threshold" in guides[-1]["label"]


def test_impulse_focus_band_has_one_native_unit_and_clips_to_zoom_window():
    impulse_utc = pd.Timestamp("2026-07-10T06:00:00Z")
    overlay = build_drilldown_zoom_outlier_overlay_recipe(
        representative_utc=impulse_utc,
        representative_delta_snr_db=10.0,
        qualifying_marker_times_utc=[impulse_utc],
        qualifying_marker_delta_snr_db=[10.0],
        candidate_start_utc=impulse_utc,
        candidate_end_utc=impulse_utc + pd.Timedelta(nanoseconds=1),
        native_evidence_unit_minutes=2.0,
        local_baseline_db=1.0,
        pre_baseline_db=0.5,
        post_baseline_db=1.5,
        pre_flank_start_utc=None,
        pre_flank_end_utc=None,
        post_flank_start_utc=None,
        post_flank_end_utc=None,
        robust_spread_db=2.0,
        robust_spread_method="mad",
        minimum_robust_z=3.0,
        minimum_departure_db=6.0,
        labels=_overlay_labels(),
    )
    assert (
        overlay["focused_episode_visual_end_utc_ns"]
        - overlay["focused_episode_visual_start_utc_ns"]
    ) == pd.Timedelta(minutes=2).value

    clipped_start = impulse_utc - pd.Timedelta(seconds=30)
    clipped_end = impulse_utc + pd.Timedelta(seconds=30)
    recipe = build_drilldown_zoom_benchmark_delta_snr_recipe(
        pd.DataFrame({"plot_time": [impulse_utc], "metric": [10.0]}),
        start_utc=clipped_start,
        end_utc=clipped_end,
        title="Impulse focus",
        panel_title="Delta SNR over Time",
        x_label="Date/Time (UTC)",
        y_label="Delta SNR (dB)",
        empty_text="No paired evidence.",
        evidence_unit_label="Individual Joint Spot",
        is_sequential=False,
        outlier_overlay=overlay,
    )
    figure = render_drilldown_zoom_benchmark_delta_snr_figure(recipe)
    try:
        axis = figure.axes[0]
        focused_episode_band = next(
            patch
            for patch in axis.patches
            if patch.get_gid() == "drilldown-outlier-focused-episode"
        )
        expected_start = mdates.date2num(
            clipped_start.tz_localize(None).to_pydatetime()
        )
        expected_end = mdates.date2num(
            clipped_end.tz_localize(None).to_pydatetime()
        )
        assert focused_episode_band.get_x() == pytest.approx(expected_start)
        assert focused_episode_band.get_width() == pytest.approx(
            expected_end - expected_start
        )
        figure.canvas.draw()
    finally:
        figure.clear()


def test_renderer_requires_visible_representative_among_qualifying_markers():
    recipe = _benchmark_recipe(overlay=_outlier_overlay())
    modified = deepcopy(recipe)
    marker_times_ns = modified["outlier_overlay"][
        "qualifying_marker_utc_ns"
    ]
    representative_position = int(
        np.flatnonzero(
            marker_times_ns
            == modified["outlier_overlay"]["representative_utc_ns"]
        )[0]
    )
    modified["outlier_overlay"]["qualifying_marker_utc_ns"] = np.delete(
        marker_times_ns,
        representative_position,
    )
    modified["outlier_overlay"][
        "qualifying_marker_delta_snr_db"
    ] = np.delete(
        modified["outlier_overlay"]["qualifying_marker_delta_snr_db"],
        representative_position,
    )
    modified["outlier_overlay"]["qualifying_marker_count"] -= 1

    with pytest.raises(
        ValueError,
        match="visible focused representative",
    ):
        render_drilldown_zoom_benchmark_delta_snr_figure(modified)


def test_native_benchmark_renderer_draws_points_and_detector_guides_without_density():
    recipe = _benchmark_recipe(overlay=_outlier_overlay())

    assert DRILLDOWN_ZOOM_FIGURE_LAYOUT_VERSION == 4
    figure = render_drilldown_zoom_benchmark_delta_snr_figure(recipe)
    try:
        assert len(figure.axes) == 1
        axis = figure.axes[0]
        assert axis.get_gid() == "drilldown-native-chronological-axis"
        assert (
            figure._wspradar_drilldown_zoom_layout_version
            == DRILLDOWN_ZOOM_FIGURE_LAYOUT_VERSION
        )
        assert figure._wspradar_drilldown_zoom_native_point_count == 4
        gids = {
            str(artist.get_gid() or "")
            for artist in figure.findobj()
            if hasattr(artist, "get_gid")
        }
        assert "drilldown-native-evidence-points" in gids
        assert "delta-snr-outlier-candidate-markers" in gids
        assert "drilldown-outlier-focused-episode" in gids
        assert "drilldown-outlier-candidate-interval" not in gids
        assert "drilldown-outlier-local-baseline" in gids
        assert "drilldown-outlier-pre-flank-baseline" in gids
        assert "drilldown-outlier-post-flank-baseline" in gids
        assert "drilldown-outlier-absolute-departure-upper" in gids
        assert not any("temporal-bin-median" in gid for gid in gids)
        assert not any("colorbar" in gid for gid in gids)
        assert not any(isinstance(artist, QuadMesh) for artist in figure.findobj())
        point_collection = next(
            collection
            for collection in axis.collections
            if collection.get_gid() == "drilldown-native-evidence-points"
        )
        assert len(point_collection.get_offsets()) == 4
        marker_collection = next(
            collection
            for collection in axis.collections
            if collection.get_gid() == "delta-snr-outlier-candidate-markers"
        )
        assert len(marker_collection.get_offsets()) == 3
        assert marker_collection.get_sizes().tolist() == [
            DELTA_SNR_OUTLIER_MARKER_SIZE
        ]
        assert marker_collection.get_facecolors()[0].tolist() == pytest.approx(
            to_rgba(DELTA_SNR_OUTLIER_MARKER_FACE_COLOR)
        )
        assert marker_collection.get_edgecolors()[0].tolist() == pytest.approx(
            to_rgba(DELTA_SNR_OUTLIER_MARKER_INNER_EDGE_COLOR)
        )
        assert marker_collection.get_path_effects()
        focused_episode_band = next(
            patch
            for patch in axis.patches
            if patch.get_gid() == "drilldown-outlier-focused-episode"
        )
        expected_band_start = mdates.date2num(
            pd.Timestamp("2026-07-10T05:57:00Z")
            .tz_localize(None)
            .to_pydatetime()
        )
        expected_band_end = mdates.date2num(
            pd.Timestamp("2026-07-10T06:03:00Z")
            .tz_localize(None)
            .to_pydatetime()
        )
        assert focused_episode_band.get_x() == pytest.approx(
            expected_band_start
        )
        assert focused_episode_band.get_width() == pytest.approx(
            expected_band_end - expected_band_start
        )
        assert focused_episode_band.get_alpha() == pytest.approx(0.16)
        assert focused_episode_band.get_facecolor()[:3] == pytest.approx(
            to_rgba("#78909c")[:3]
        )
        assert focused_episode_band.get_edgecolor()[3] == pytest.approx(0.0)
        assert focused_episode_band.get_zorder() < point_collection.get_zorder()
        assert focused_episode_band.get_zorder() < marker_collection.get_zorder()
        assert figure._suptitle.get_text() == recipe["title"]

        robust_z_lines = [
            line
            for line in axis.lines
            if str(line.get_gid() or "").startswith(
                "drilldown-outlier-robust-z-"
            )
        ]
        assert len(robust_z_lines) == 8
        assert {
            (
                line.get_color(),
                line.get_linestyle(),
                line.get_linewidth(),
                line.get_alpha(),
            )
            for line in robust_z_lines
        } == {("#ef5350", "--", 0.85, 0.66)}

        local_baseline = next(
            line
            for line in axis.lines
            if line.get_gid() == "drilldown-outlier-local-baseline"
        )
        assert local_baseline.get_linestyle() == "-"
        assert local_baseline.get_linewidth() > robust_z_lines[0].get_linewidth()

        robust_z_labels = [
            text_artist
            for text_artist in axis.texts
            if str(text_artist.get_gid() or "").startswith(
                "drilldown-outlier-robust-z-"
            )
            and str(text_artist.get_gid() or "").endswith("-label")
        ]
        assert len(robust_z_labels) == 4
        assert all(label.get_position()[0] == 0.005 for label in robust_z_labels)
        assert all(label.get_ha() == "left" for label in robust_z_labels)
        assert all(label.get_fontsize() >= 9.0 for label in robust_z_labels)

        departure_label = next(
            text_artist
            for text_artist in axis.texts
            if text_artist.get_gid()
            == "drilldown-outlier-absolute-departure-label"
        )
        assert departure_label.get_position()[0] == 0.005
        assert departure_label.get_position()[1] == recipe["outlier_overlay"][
            "absolute_departure_upper_db"
        ]
        assert departure_label.get_ha() == "left"
        assert departure_label.get_va() == "bottom"
        assert departure_label.get_fontsize() >= 9.0

        legend_labels = [
            text_artist.get_text()
            for text_artist in axis.get_legend().get_texts()
        ]
        assert "Candidate interval" not in legend_labels
        assert "Outlier candidate" in legend_labels
        assert "Focused episode" in legend_labels
        figure.canvas.draw()
    finally:
        figure.clear()


def test_renderer_rejects_modified_robust_z_boundary():
    recipe = _benchmark_recipe(overlay=_outlier_overlay())
    modified = deepcopy(recipe)
    modified["outlier_overlay"]["robust_z_guides"][0]["upper_db"] += 0.1

    with pytest.raises(
        ValueError,
        match="robust-z guide boundaries are inconsistent",
    ):
        render_drilldown_zoom_benchmark_delta_snr_figure(modified)


def test_renderer_still_validates_candidate_provenance_without_drawing_span():
    recipe = _benchmark_recipe(overlay=_outlier_overlay())
    modified = deepcopy(recipe)
    modified["outlier_overlay"]["candidate_end_utc_ns"] = modified[
        "outlier_overlay"
    ]["representative_utc_ns"]

    with pytest.raises(
        ValueError,
        match="representative must lie in its interval",
    ):
        render_drilldown_zoom_benchmark_delta_snr_figure(modified)


def test_performance_native_renderer_has_one_panel_and_no_colorbar():
    rows = pd.DataFrame(
        {
            "time_slot": [
                int(START_UTC.timestamp() // 120),
                int((START_UTC + pd.Timedelta(minutes=2)).timestamp() // 120),
            ],
            "hit": [1, 1],
            "target_snr": [-10.0, -8.0],
        }
    )
    recipe = build_drilldown_zoom_performance_snr_recipe(
        rows,
        start_utc=START_UTC,
        end_utc=START_UTC + pd.Timedelta(hours=1),
        title="SEL (SE00) - Time Window: 00:00 to 01:00 UTC",
        panel_title="Normalized Target SNR over Time",
        x_label="Date/Time (UTC)",
        y_label="Normalized Target SNR (dB)",
        empty_text="No successful evidence.",
        evidence_unit_label="Individual successful opportunity",
    )

    figure = render_drilldown_zoom_performance_snr_figure(recipe)
    try:
        assert len(figure.axes) == 1
        assert not any(
            "colorbar" in str(axis.get_gid() or "") for axis in figure.axes
        )
        assert not any(isinstance(artist, QuadMesh) for artist in figure.findobj())
    finally:
        figure.clear()


def test_native_recipe_owns_input_arrays_and_overlay_payload():
    evidence = pd.DataFrame(
        {
            "plot_time": pd.to_datetime(["2026-07-10T06:00:00Z"], utc=True),
            "metric": [10.0],
        }
    )
    overlay = _outlier_overlay()
    overlay["qualifying_marker_utc_ns"] = np.asarray(
        [pd.Timestamp("2026-07-10T06:00:00Z").value],
        dtype=np.int64,
    )
    overlay["qualifying_marker_delta_snr_db"] = np.asarray(
        [10.0],
        dtype=np.float64,
    )
    overlay["qualifying_marker_count"] = 1
    recipe = build_drilldown_zoom_benchmark_delta_snr_recipe(
        evidence,
        start_utc=START_UTC,
        end_utc=END_UTC,
        title="Title",
        panel_title="Panel",
        x_label="UTC",
        y_label="Delta SNR",
        empty_text="Empty",
        evidence_unit_label="Joint Spot",
        is_sequential=False,
        outlier_overlay=overlay,
    )

    evidence.loc[0, "metric"] = -99.0
    overlay["robust_z_guides"][0]["upper_db"] = -99.0
    overlay["qualifying_marker_delta_snr_db"][0] = -99.0
    assert recipe["metric_db"].tolist() == [10.0]
    assert recipe["outlier_overlay"]["robust_z_guides"][0]["upper_db"] != -99.0
    assert recipe["outlier_overlay"][
        "qualifying_marker_delta_snr_db"
    ][0] != -99.0


def test_chronological_companion_adapter_removes_folded_axis_and_expands_width():
    figure = Figure(figsize=(12, 4))
    FigureCanvasAgg(figure)
    chronological_axis = figure.add_axes([0.08, 0.15, 0.38, 0.70])
    chronological_axis.set_gid("selected-chronological-axis")
    folded_axis = figure.add_axes([0.54, 0.15, 0.38, 0.70])
    folded_axis.set_gid("selected-folded-axis")
    folded_note = folded_axis.text(0.5, 0.5, "folded")
    folded_note.set_gid("selected-folded-note")

    expanded = _expand_chronological_column(figure)

    assert expanded is figure
    assert folded_axis not in figure.axes
    assert chronological_axis.get_position().x0 == 0.08
    assert chronological_axis.get_position().x1 == pytest.approx(0.92)
    assert (
        figure._wspradar_drilldown_zoom_layout_version
        == DRILLDOWN_ZOOM_FIGURE_LAYOUT_VERSION
    )


def test_benchmark_recipe_declares_native_kind_and_does_not_store_bin_statistics():
    recipe = _benchmark_recipe()

    assert recipe["kind"] == DRILLDOWN_ZOOM_BENCHMARK_NATIVE_KIND
    assert recipe["evidence_unit_kind"] == "joint_spot"
    assert recipe["aggregation"] == "none"
    assert not {
        "prepared_profiles",
        "count_grid",
        "median",
        "q1",
        "q3",
        "density_label",
        "bin_median_label",
    }.intersection(recipe)


def _integration_translations():
    return {
        "fmt_drilldown_zoom_time_window": (
            "{identity} - Time Window: {start} to {end} UTC"
        ),
        "fig_drilldown_native_performance_panel_title": (
            "Normalized Target SNR over Time"
        ),
        "fig_drilldown_native_time_x": "Date/Time (UTC)",
        "fig_drilldown_native_performance_y": (
            "Normalized Target SNR (dB)"
        ),
        "fig_drilldown_native_performance_unavailable": "No evidence.",
        "fig_drilldown_native_successful_opportunity": (
            "Individual successful opportunity"
        ),
        "fig_drilldown_native_benchmark_panel_title": "Delta SNR over Time",
        "fig_drilldown_native_benchmark_y": "Delta SNR (dB)",
        "fig_drilldown_native_benchmark_unavailable": "No paired evidence.",
        "fig_drilldown_native_joint_spot": "Individual Joint Spot",
        "fig_drilldown_native_scheduled_pair": (
            "Individual complete Scheduled Pair"
        ),
        "fig_drilldown_outlier_candidate": "Outlier candidate",
        "fig_drilldown_outlier_focused_episode": "Focused episode",
        "fig_drilldown_outlier_expected_local_delta_snr": (
            "Expected local Delta SNR"
        ),
        "fig_drilldown_outlier_flank_baseline": "Pre/post flank baseline",
        "fmt_drilldown_outlier_robust_z_guide": (
            "Robust-z guide |z| = {value:g}"
        ),
        "fmt_drilldown_outlier_qualifying_robust_z_guide": (
            "Robust-z qualifying threshold |z| = {value:g}"
        ),
        "fmt_drilldown_outlier_absolute_departure_gate": (
            "Absolute-departure gate (+/-{value:g} dB)"
        ),
    }


def test_performance_zoom_integration_uses_native_points_and_compact_title(
    monkeypatch,
):
    focus_window = DrilldownFocusWindow(
        START_UTC,
        START_UTC + pd.Timedelta(hours=1),
        "1h",
        "manual",
    )
    rows = pd.DataFrame(
        {
            "time_slot": [
                int(START_UTC.timestamp() // 120),
                int((START_UTC + pd.Timedelta(minutes=2)).timestamp() // 120),
            ],
            "hit": [1, 1],
            "target_snr": [-10.0, -8.0],
        }
    )
    companion_calls = []

    def _fake_companion(*args, **kwargs):
        companion_calls.append((args, kwargs))
        return {"kind": "focused-outcomes"}

    monkeypatch.setattr(
        segment_inspector,
        "_opportunity_temporal_recipe",
        _fake_companion,
    )

    metric_recipe, companion_recipe = (
        segment_inspector._build_performance_drilldown_zoom_recipes(
            {
                "selected_segment": {"label": "segment"},
                "terminology": {},
                "labels": {},
            },
            pd.DataFrame(),
            rows,
            "DG2CAD (JN47mv)",
            focus_window,
            "2m",
            _integration_translations(),
        )
    )

    assert metric_recipe["aggregation"] == "none"
    assert metric_recipe["point_count"] == 2
    assert metric_recipe["title"] == (
        "DG2CAD (JN47mv) - Time Window: 2026-07-10 00:00 "
        "to 2026-07-10 01:00 UTC"
    )
    assert companion_recipe["time_bin"] == "2m"
    assert companion_calls[0][1]["time_bin_options"] == ("2m",)


def test_benchmark_zoom_integration_adds_matching_detector_overlay(
    monkeypatch,
):
    focus_window = DrilldownFocusWindow(
        START_UTC,
        END_UTC,
        "12h",
        "manual",
    )
    time_slots = [
        int((START_UTC + pd.Timedelta(hours=6, minutes=minute)).timestamp() // 120)
        for minute in (0, 2)
    ]
    station_rows = pd.DataFrame(
        {
            "peer_sign": ["DG2CAD", "DG2CAD"],
            "peer_grid": ["JN47mv", "JN47mv"],
            "time_slot": time_slots,
            "has_u": [1, 1],
            "has_r": [1, 1],
            "snr_u_norm": [3.03, 10.04],
            "snr_r_norm": [2.0, 1.0],
        }
    )
    qualifying_marker_delta_snr_db = (3.03 - 2.0, 10.04 - 1.0)
    candidate = DrilldownOutlierCandidateContext(
        analysis_id="benchmark",
        run_id="run-1",
        scope_token="scope-1",
        callsign="DG2CAD",
        locator="JN47mv",
        request_token="request-1",
        representative_utc=START_UTC + pd.Timedelta(hours=6, minutes=2),
        representative_delta_snr_db=qualifying_marker_delta_snr_db[1],
        event_start_utc=START_UTC + pd.Timedelta(hours=6),
        event_end_utc=(
            START_UTC
            + pd.Timedelta(hours=6, minutes=2)
            + pd.Timedelta(nanoseconds=1)
        ),
        baseline_anchor_start_utc=START_UTC + pd.Timedelta(hours=6),
        baseline_anchor_end_utc=(
            START_UTC + pd.Timedelta(hours=6, minutes=4) - pd.Timedelta(nanoseconds=1)
        ),
        episode_guard_minutes=10.0,
        pre_flank_start_utc=START_UTC,
        pre_flank_end_utc=START_UTC + pd.Timedelta(hours=5, minutes=50),
        post_flank_start_utc=START_UTC + pd.Timedelta(hours=6, minutes=14),
        post_flank_end_utc=END_UTC,
        local_baseline_db=1.0,
        pre_baseline_db=0.5,
        post_baseline_db=1.5,
        robust_spread_db=2.0,
        robust_spread_method="mad",
        robust_z=4.5,
        minimum_robust_z=4.0,
        minimum_departure_db=6.0,
        detector_version=(
            segment_inspector.DELTA_SNR_OUTLIER_DETECTOR_VERSION
        ),
        candidate_signature="candidate-1",
    )
    monkeypatch.setattr(
        segment_inspector,
        "_compare_coverage_recipe",
        lambda *args, **kwargs: {"kind": "focused-coverage"},
    )
    qualifying_marker_times = [
        START_UTC + pd.Timedelta(hours=6),
        START_UTC + pd.Timedelta(hours=6, minutes=2),
    ]
    outlier_model = SimpleNamespace(
        detector_version=(
            segment_inspector.DELTA_SNR_OUTLIER_DETECTOR_VERSION
        ),
        candidate_signature="candidate-1",
        qualifying_unit_marker_recipe=lambda *args, **kwargs: {
            "candidate_signature": "candidate-1",
            "markers": [
                {
                    "marker_utc_ns": int(marker_time.value),
                    "marker_delta_snr_db": marker_delta_snr,
                }
                for marker_time, marker_delta_snr in zip(
                    qualifying_marker_times,
                    qualifying_marker_delta_snr_db,
                )
            ],
        },
    )

    metric_recipe, coverage_recipe = (
        segment_inspector._build_benchmark_drilldown_zoom_recipes(
            station_rows,
            pd.DataFrame(
                {"peer_sign": ["DG2CAD"], "peer_grid": ["JN47mv"]}
            ),
            None,
            False,
            SimpleNamespace(
                tx_ab_repeat_interval_minutes=10,
                tx_ab_target_start_minute=0,
                tx_ab_reference_start_minute=2,
            ),
            focus_window,
            "2m",
            {"reference_snr_correction_notice": ""},
            {"selected_segment": {"label": "segment"}, "labels": {}},
            _integration_translations(),
            outlier_context=candidate,
            outlier_model=outlier_model,
        )
    )

    assert metric_recipe["aggregation"] == "none"
    assert metric_recipe["metric_db"].tolist() == pytest.approx([1.03, 9.04])
    assert metric_recipe["outlier_overlay"][
        "representative_delta_snr_db"
    ] == pytest.approx(9.04)
    assert metric_recipe["outlier_overlay"][
        "qualifying_marker_utc_ns"
    ].tolist() == [int(marker_time.value) for marker_time in qualifying_marker_times]
    assert metric_recipe["outlier_overlay"][
        "qualifying_marker_delta_snr_db"
    ].tolist() == pytest.approx([1.03, 9.04])
    assert metric_recipe["outlier_overlay"]["qualifying_marker_count"] == 2
    assert metric_recipe["title"].startswith(
        "DG2CAD (JN47mv) - Time Window:"
    )
    assert coverage_recipe == {"kind": "focused-coverage"}
    rendered_metric_figure = (
        render_drilldown_zoom_benchmark_delta_snr_figure(metric_recipe)
    )
    try:
        rendered_metric_figure.canvas.draw()
    finally:
        rendered_metric_figure.clear()

    stale_model = SimpleNamespace(
        detector_version=(
            segment_inspector.DELTA_SNR_OUTLIER_DETECTOR_VERSION
        ),
        candidate_signature="changed-candidate-signature",
        qualifying_unit_marker_recipe=lambda *args, **kwargs: pytest.fail(
            "stale candidate provenance must not request marker coordinates"
        ),
    )
    stale_metric_recipe, _stale_coverage_recipe = (
        segment_inspector._build_benchmark_drilldown_zoom_recipes(
            station_rows,
            pd.DataFrame(
                {"peer_sign": ["DG2CAD"], "peer_grid": ["JN47mv"]}
            ),
            None,
            False,
            SimpleNamespace(
                tx_ab_repeat_interval_minutes=10,
                tx_ab_target_start_minute=0,
                tx_ab_reference_start_minute=2,
            ),
            focus_window,
            "2m",
            {"reference_snr_correction_notice": ""},
            {"selected_segment": {"label": "segment"}, "labels": {}},
            _integration_translations(),
            outlier_context=candidate,
            outlier_model=stale_model,
        )
    )
    assert stale_metric_recipe["outlier_overlay"] is None
