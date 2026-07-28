from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from io import BytesIO
import threading
import time

import numpy as np
import pandas as pd
from matplotlib.collections import (
    LineCollection,
    PatchCollection,
    PathCollection,
    QuadMesh,
)
from matplotlib.colors import BoundaryNorm, ListedColormap, to_rgba
from matplotlib.figure import Figure
from matplotlib.legend import Legend
from matplotlib.transforms import IdentityTransform
from PIL import Image
import pytest

from core import map_base, plot_engine
from core.analysis_context import AnalysisContext, COMPARISON_REFERENCE_STATION
from core.map_models import MapData
from core.presentation_context import PresentationContext
from i18n import T, absolute_terms
from ui.components.segment_inspector import _success_figure_labels
from ui.matplotlib_renderer import (
    _draw_figure_preview_image,
    _serialize_preview_png,
    dispose_matplotlib_figure,
)
from ui.plots.evidence_figures import render_segment_insight_export_figure
from ui.plots.opportunity_figures import (
    _opportunity_segment_recipe,
    _render_opportunity_segment_figure,
)
from ui.results_export import figure_to_png_bytes


def _assert_shared_evidence_legend(figure, legend, expected_labels):
    """Verify shared foreground styling and conventional key-first layout."""
    figure.canvas.draw()
    renderer = figure.canvas.get_renderer()

    assert [text.get_text() for text in legend.get_texts()] == expected_labels
    assert {text.get_fontsize() for text in legend.get_texts()} == {8.0}
    assert {
        tuple(text.get_fontfamily()) for text in legend.get_texts()
    } == {("sans-serif",)}
    assert {text.get_fontweight() for text in legend.get_texts()} == {"normal"}
    assert legend.get_zorder() == pytest.approx(10.0)
    assert legend.get_frame().get_alpha() == pytest.approx(0.9)
    assert legend.get_frame().get_facecolor()[:3] == pytest.approx(
        to_rgba("#121212")[:3]
    )
    assert legend.get_frame().get_edgecolor()[:3] == pytest.approx(
        to_rgba("#444444")[:3]
    )
    for legend_handle, legend_text in zip(
        legend.legend_handles,
        legend.get_texts(),
    ):
        assert (
            legend_handle.get_window_extent(renderer).x1
            < legend_text.get_window_extent(renderer).x0
        )


def _assert_shared_axis_label(label_artist, expected_text):
    """Verify one Success axis uses the shared evidence-label typography."""
    assert label_artist.get_text() == expected_text
    assert label_artist.get_fontsize() == pytest.approx(10.0)
    assert tuple(label_artist.get_fontfamily()) == ("sans-serif",)
    assert label_artist.get_fontweight() == "normal"


_SUCCESS_OUTCOME_LABELS = {
    ("en", "RX"): ("Heard by Target", "Heard by others only"),
    ("en", "TX"): ("Target heard", "Other signals heard only"),
    ("de", "RX"): ("Vom Target gehört", "Nur von anderen gehört"),
    ("de", "TX"): ("Target gehört", "Nur andere Signale gehört"),
}


def _localized_compare_segment_recipe(recipe, language="en"):
    """Attach complete localized presentation state to a Compare recipe."""
    translations = T[language]
    is_sequential = bool(recipe.get("is_sequential"))
    return {
        **recipe,
        "panel_y_label": translations["fig_share_percent_axis"],
        "decode_outcomes_title": translations["fig_decode_outcomes"],
        "station_medians_title": translations[
            "fig_station_medians_delta"
        ],
        "paired_evidence_title": translations[
            (
                "fig_scheduled_pair_delta"
                if is_sequential
                else "fig_joint_spot_delta"
            )
        ],
        "metric_axis_label": translations["tbl_col_delta_snr"],
        "median_label": translations["fig_median_label"],
        "mean_label": translations["fig_mean_label"],
        "no_data_label": translations["fig_no_data"],
    }


@pytest.mark.parametrize("language", ["en", "de"])
def test_compare_segment_renderer_uses_localized_recipe_labels(language):
    """Render every Compare panel label from explicit EN/DE recipe state."""
    translations = T[language]
    recipe = _localized_compare_segment_recipe(
        {
            "title": "Localized Compare",
            "selected_segment": "Full Range | All Directions",
            "is_sequential": False,
            "station_values": np.array([], dtype=float),
            "spot_values": np.array([], dtype=float),
            "panel_station_counts": [1, 2, 0, 1],
            "panel_spot_counts": [1, 4, 0, 1],
            "panel_series_labels": [
                translations["lbl_results_stations"],
                translations["lbl_results_spots"],
            ],
            "panel_labels": ["Target", "Joint", "Both (Async)", "Reference"],
        },
        language,
    )

    figure = render_segment_insight_export_figure(recipe)
    try:
        outcome_axis, station_axis, spot_axis = figure.axes
        assert outcome_axis.get_title() == translations[
            "fig_decode_outcomes"
        ]
        assert outcome_axis.get_ylabel() == translations[
            "fig_share_percent_axis"
        ]
        assert station_axis.get_title() == translations[
            "fig_station_medians_delta"
        ]
        assert spot_axis.get_title() == translations[
            "fig_joint_spot_delta"
        ]
        assert station_axis.get_xlabel() == translations[
            "tbl_col_delta_snr"
        ]
        assert spot_axis.get_xlabel() == translations[
            "tbl_col_delta_snr"
        ]
        for axis in (station_axis, spot_axis):
            assert {text.get_text() for text in axis.texts} == {
                translations["fig_no_data"]
            }
    finally:
        dispose_matplotlib_figure(figure)


def _success_segment_figure_recipe_for_test(title):
    """Build one complete localized Success evidence recipe for renderer tests."""
    peer_rows = pd.DataFrame(
        {
            "peer_sign": ["K1AAA", "K2BBB", "K3CCC", "K4DDD"],
            "peer_grid": ["FN31", "EM12", "JN79", "IO90"],
            "dist_label": [
                "[0-2500km]",
                "[0-2500km]",
                "[2500-5000km]",
                "[2500-5000km]",
            ],
            "r_min": [0.0, 0.0, 2500.0, 2500.0],
            "r_max": [2500.0, 2500.0, 5000.0, 5000.0],
            "calc_dist": [500.0, 1500.0, 3000.0, 4000.0],
            "eligible": [True, True, True, True],
            "rate_pct": [20.0, 50.0, 75.0, 0.0],
            "hits": [1, 5, 15, 0],
            "misses": [4, 5, 5, 5],
            "opportunities": [5, 10, 20, 5],
            "successful_snr_median": [-18.0, -12.0, -8.0, np.nan],
        }
    )
    return _opportunity_segment_recipe(
        title,
        "Full Range | All Directions",
        peer_rows,
        pd.DataFrame(),
        pd.Timestamp("2026-07-10T00:00:00Z"),
        pd.Timestamp("2026-07-11T00:00:00Z"),
        absolute_terms(T["en"], "RX"),
        minimum_trials=5,
        figure_labels=_success_figure_labels(T["en"], "RX_ABS"),
    )


@pytest.mark.parametrize(
    ("segment_values", "expected_half_span_db", "expected_tick_step_db"),
    [
        ([], 6.0, 1.0),
        ([np.nan, np.inf, -np.inf], 6.0, 1.0),
        ([-3.1, 3.1], 6.0, 1.0),
        ([-6.5, 6.5], 6.0, 1.0),
        ([np.nextafter(6.5, np.inf)], 6.0, 3.0),
        ([np.nextafter(-6.5, -np.inf)], 6.0, 3.0),
        ([7.5], 6.0, 3.0),
        ([np.nextafter(7.5, np.inf)], 9.0, 3.0),
        ([12.0], 12.0, 3.0),
        ([19.5], 18.0, 3.0),
        ([np.nextafter(19.5, np.inf)], 18.0, 6.0),
        ([39.0], 36.0, 6.0),
        ([np.nextafter(39.0, np.inf)], 40.0, 10.0),
        ([65.0], 60.0, 10.0),
        ([np.nextafter(65.0, np.inf)], 60.0, 20.0),
    ],
)
def test_compare_map_scale_fits_data_without_fixed_headroom(
    segment_values,
    expected_half_span_db,
    expected_tick_step_db,
):
    """Use the finest symmetric layout whose outer half-bin contains the data."""
    scale = plot_engine._build_compare_map_color_scale(segment_values)
    expected_outer_boundary_db = (
        expected_half_span_db + (expected_tick_step_db / 2.0)
    )
    finite_segment_values = np.asarray(segment_values, dtype=float)
    finite_segment_values = finite_segment_values[
        np.isfinite(finite_segment_values)
    ]

    assert isinstance(scale.colormap, ListedColormap)
    assert isinstance(scale.normalization, BoundaryNorm)
    assert scale.normalization.vmin == pytest.approx(
        -expected_outer_boundary_db
    )
    assert scale.normalization.vmax == pytest.approx(
        expected_outer_boundary_db
    )
    assert scale.colormap.N == len(scale.boundaries_db) - 1
    assert scale.colormap.N % 2 == 1
    assert scale.boundaries_db == tuple(
        -value for value in reversed(scale.boundaries_db)
    )
    assert int(scale.normalization(scale.boundaries_db[0])) == 0
    assert (
        int(scale.normalization(scale.boundaries_db[-1]))
        == scale.colormap.N - 1
    )
    assert scale.ticks_db[0] == pytest.approx(-expected_half_span_db)
    assert scale.ticks_db[-1] == pytest.approx(expected_half_span_db)
    assert np.diff(scale.ticks_db) == pytest.approx(expected_tick_step_db)
    assert scale.ticks_db == tuple(-value for value in reversed(scale.ticks_db))
    assert scale.tick_labels[len(scale.tick_labels) // 2] == "0"
    assert all("S" not in label for label in scale.tick_labels)
    if finite_segment_values.size:
        assert np.max(np.abs(finite_segment_values)) <= (
            scale.boundaries_db[-1]
        )


@pytest.mark.parametrize(
    (
        "segment_values",
        "expected_tick_step_db",
        "expected_positive_boundaries_db",
    ),
    [
        ([-3.0, 3.0], 1.0, (0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5)),
        ([7.6], 3.0, (1.5, 4.5, 7.5, 10.5)),
        ([19.6], 6.0, (3.0, 9.0, 15.0, 21.0)),
        ([39.1], 10.0, (5.0, 15.0, 25.0, 35.0, 45.0)),
    ],
)
def test_compare_map_scale_uses_equal_width_bins(
    segment_values,
    expected_tick_step_db,
    expected_positive_boundaries_db,
):
    """Give every color, including neutral, the active dB-step width."""
    scale = plot_engine._build_compare_map_color_scale(segment_values)
    center_boundary_index = len(scale.boundaries_db) // 2
    bin_midpoints_db = (
        np.asarray(scale.boundaries_db[:-1])
        + np.asarray(scale.boundaries_db[1:])
    ) / 2.0

    assert scale.boundaries_db[center_boundary_index:] == pytest.approx(
        expected_positive_boundaries_db
    )
    assert np.diff(scale.boundaries_db) == pytest.approx(
        expected_tick_step_db
    )
    assert bin_midpoints_db == pytest.approx(scale.ticks_db)
    neutral_bin_index = scale.colormap.N // 2
    neutral_half_width_db = expected_tick_step_db / 2.0
    assert (
        int(scale.normalization(-neutral_half_width_db))
        == neutral_bin_index
    )
    assert (
        int(scale.normalization(neutral_half_width_db))
        == neutral_bin_index
    )
    for positive_boundary_db in expected_positive_boundaries_db[:-1]:
        positive_outward_db = np.nextafter(positive_boundary_db, np.inf)
        negative_outward_db = np.nextafter(-positive_boundary_db, -np.inf)
        assert (
            int(scale.normalization(-positive_boundary_db))
            + int(scale.normalization(positive_boundary_db))
            == scale.colormap.N - 1
        )
        assert (
            int(scale.normalization(negative_outward_db))
            + int(scale.normalization(positive_outward_db))
            == scale.colormap.N - 1
        )


def test_compare_map_scale_uses_discrete_soft_matte_palette():
    """Use distinct hue landmarks without reversing Target and Reference."""
    scale = plot_engine._build_compare_map_color_scale([-3.0, 3.0])
    middle_color_index = len(plot_engine.COMPARE_MAP_COLORS) // 2
    neutral_bin_index = scale.colormap.N // 2

    assert isinstance(scale.colormap, ListedColormap)
    assert plot_engine.COMPARE_MAP_COLORS == (
        "#6e4c8f",
        "#6576b8",
        "#5c9bc7",
        "#55b9c0",
        "#8bcb9a",
        "#c9e5a3",
        "#f4e58a",
        "#efb56f",
        "#df7f68",
        "#b85d5f",
        "#7c5341",
    )
    assert scale.colormap.N == 13
    assert scale.colormap(0.0) == pytest.approx(
        to_rgba(plot_engine.COMPARE_MAP_COLORS[0])
    )
    assert scale.colormap(0.5) == pytest.approx(
        to_rgba(plot_engine.COMPARE_MAP_COLORS[middle_color_index])
    )
    assert scale.colormap(1.0) == pytest.approx(
        to_rgba(plot_engine.COMPARE_MAP_COLORS[-1])
    )
    neutral_red, neutral_green, neutral_blue, _ = scale.colormap(0.5)
    assert neutral_green > neutral_red > neutral_blue
    assert min(neutral_red, neutral_green, neutral_blue) > 0.60
    neutral_rgb = np.asarray(
        (neutral_red, neutral_green, neutral_blue),
        dtype=float,
    )
    white_export_rgb = np.ones(3, dtype=float)
    composited_neutral_rgb = (
        plot_engine.COMPARE_MAP_HEATMAP_ALPHA * neutral_rgb
        + (1.0 - plot_engine.COMPARE_MAP_HEATMAP_ALPHA) * white_export_rgb
    )
    assert np.linalg.norm(
        white_export_rgb - composited_neutral_rgb
    ) > 0.30
    negative_red, _, negative_blue, _ = scale.colormap(
        scale.normalization(-3.0)
    )
    positive_red, _, positive_blue, _ = scale.colormap(
        scale.normalization(3.0)
    )
    assert negative_blue > negative_red
    assert positive_red > positive_blue
    assert int(scale.normalization(-0.49)) == neutral_bin_index
    assert int(scale.normalization(0.49)) == neutral_bin_index
    assert int(scale.normalization(-0.5)) == neutral_bin_index
    assert int(scale.normalization(0.5)) == neutral_bin_index
    for delta_snr_db in (0.0, 0.49, 0.5, 1.0, 3.0, 5.0, 6.0):
        assert (
            int(scale.normalization(-delta_snr_db))
            + int(scale.normalization(delta_snr_db))
            == scale.colormap.N - 1
        )
    for positive_boundary_db in scale.boundaries_db[
        (len(scale.boundaries_db) // 2):-1
    ]:
        positive_outward_db = np.nextafter(positive_boundary_db, np.inf)
        negative_outward_db = np.nextafter(-positive_boundary_db, -np.inf)
        assert (
            int(scale.normalization(negative_outward_db))
            + int(scale.normalization(positive_outward_db))
            == scale.colormap.N - 1
        )


def test_compare_map_scale_handles_very_large_finite_values():
    """Keep tick selection bounded for an extreme plausible display value."""
    scale = plot_engine._build_compare_map_color_scale([1_000_000.0])

    assert scale.normalization.vmax >= 1_000_000.0
    assert scale.normalization.vmin == -scale.normalization.vmax
    assert (
        len(scale.ticks_db)
        <= plot_engine.COMPARE_MAP_ADAPTIVE_MAXIMUM_TICK_COUNT
    )


def test_map_renderer_rejects_removed_legacy_absolute_mode():
    """Reject map data outside the canonical Success and Compare modes."""
    map_data = MapData(
        station_rows=pd.DataFrame(),
        segment_rows=pd.DataFrame(),
        analysis_id="RX_ABS",
        is_compare=False,
        is_sequential=False,
        analysis_kind="comparison",
    )
    analysis_context = AnalysisContext(
        callsign="TARGET",
        qth="JN47",
        band="20m",
    )
    presentation_context = PresentationContext(
        language="en",
        labels=T["en"],
        theme="dark",
        solar_label=T["en"]["opt_solar_all"].split()[0],
    )

    with pytest.raises(ValueError, match="Map analysis mode must be Success"):
        plot_engine.render_map_figure(
            map_data,
            title="Removed legacy map",
            start_t=datetime(2026, 7, 1, tzinfo=timezone.utc),
            end_t=datetime(2026, 7, 2, tzinfo=timezone.utc),
            max_dist_km=5000,
            base_min_stations=1,
            lat_0=0.0,
            lon_0=0.0,
            analysis_context=analysis_context,
            presentation_context=presentation_context,
        )


def test_compare_map_renderer_scales_only_from_visible_segments(monkeypatch):
    """Exclude off-map extremes from the stepped Compare colorbar contract."""
    def fake_create_base_map_figure(**_kwargs):
        figure = Figure(figsize=(8, 8), facecolor="black")
        map_axis = figure.add_axes([0.05, 0.15, 0.75, 0.75])
        identity_transform = IdentityTransform()
        return figure, map_axis, identity_transform, identity_transform

    monkeypatch.setattr(
        plot_engine,
        "_preview_base_map_cache_enabled",
        lambda: False,
    )
    monkeypatch.setattr(
        plot_engine,
        "create_base_map_figure",
        fake_create_base_map_figure,
    )
    station_rows = pd.DataFrame(
        {
            "peer_lon": [1.0],
            "peer_lat": [1.0],
            "spot_count": [2],
            "count_only_u": [0],
            "count_only_r": [0],
            "r_min": [0.0],
        }
    )
    segment_rows = pd.DataFrame(
        {
            "r_min": [0.0, 2500.0, 5000.0],
            "r_max": [2500.0, 5000.0, 10000.0],
            "az_bucket": [0.0, 1.0, 2.0],
            "val": [12.0, np.nan, 100.0],
        }
    )
    map_data = MapData(
        station_rows=station_rows,
        segment_rows=segment_rows,
        analysis_id="RX_COMPARE",
        is_compare=True,
        is_sequential=False,
        analysis_kind="comparison",
    )
    analysis_context = AnalysisContext(
        callsign="TARGET",
        qth="JN47",
        band="20m",
        comparison_mode=COMPARISON_REFERENCE_STATION,
        reference_callsign="REFERENCE",
    )
    presentation_context = PresentationContext(
        language="en",
        labels=T["en"],
        theme="dark",
        solar_label=T["en"]["opt_solar_all"].split()[0],
    )

    rendered_map = plot_engine.render_map_figure(
        map_data,
        title="Compare map",
        start_t=datetime(2026, 7, 1, tzinfo=timezone.utc),
        end_t=datetime(2026, 7, 2, tzinfo=timezone.utc),
        max_dist_km=5000,
        base_min_stations=1,
        lat_0=0.0,
        lon_0=0.0,
        analysis_context=analysis_context,
        presentation_context=presentation_context,
    )
    try:
        map_axis = rendered_map.figure.axes[0]
        heatmap = next(
            collection
            for collection in map_axis.collections
            if isinstance(collection, PatchCollection)
        )
        colorbar_axis = next(
            axis
            for axis in rendered_map.figure.axes
            if axis.get_ylabel() == T["en"]["cbar_comp"]
        )
        expected_boundaries_db = (
            -13.5,
            -10.5,
            -7.5,
            -4.5,
            -1.5,
            1.5,
            4.5,
            7.5,
            10.5,
            13.5,
        )

        assert isinstance(heatmap.cmap, ListedColormap)
        assert isinstance(heatmap.norm, BoundaryNorm)
        assert heatmap.get_alpha() == pytest.approx(
            plot_engine.COMPARE_MAP_HEATMAP_ALPHA
        )
        assert heatmap.norm.vmin == pytest.approx(-13.5)
        assert heatmap.norm.vmax == pytest.approx(13.5)
        assert heatmap.norm.boundaries == pytest.approx(
            (
                -13.5,
                -10.5,
                -7.5,
                -4.5,
                -1.5,
                np.nextafter(1.5, np.inf),
                np.nextafter(4.5, np.inf),
                np.nextafter(7.5, np.inf),
                np.nextafter(10.5, np.inf),
                13.5,
            )
        )
        heatmap_values = heatmap.get_array()
        assert np.ma.isMaskedArray(heatmap_values)
        assert heatmap_values.compressed() == pytest.approx([12.0])
        assert np.ma.getmaskarray(heatmap_values).tolist() == [False, True]
        assert colorbar_axis.get_position().bounds == pytest.approx(
            plot_engine.COMPARE_MAP_CBAR_BBOX
        )
        assert colorbar_axis.get_ylim() == pytest.approx((-13.5, 13.5))
        assert [tick.get_text() for tick in colorbar_axis.get_yticklabels()] == [
            "\u221212",
            "\u22129",
            "\u22126",
            "\u22123",
            "0",
            "+3",
            "+6",
            "+9",
            "+12",
        ]
        colorbar_solid = next(
            collection
            for collection in colorbar_axis.collections
            if isinstance(collection, QuadMesh)
        )
        assert colorbar_solid.get_alpha() == pytest.approx(
            plot_engine.COMPARE_MAP_HEATMAP_ALPHA
        )
        assert colorbar_solid.get_array().size == 9
        assert (
            colorbar_solid.get_coordinates()[:, 0, 1].tolist()
            == pytest.approx(expected_boundaries_db)
        )
        rendered_boundary_y = colorbar_axis.transData.transform(
            np.column_stack(
                (
                    np.zeros(len(expected_boundaries_db)),
                    expected_boundaries_db,
                )
            )
        )[:, 1]
        rendered_height_fractions = np.diff(rendered_boundary_y)
        rendered_height_fractions /= rendered_height_fractions.sum()
        expected_height_fractions = np.diff(expected_boundaries_db)
        expected_height_fractions /= expected_height_fractions.sum()
        assert rendered_height_fractions == pytest.approx(
            expected_height_fractions
        )
        assert colorbar_solid.get_linewidths() == pytest.approx(0.0)
        assert len(colorbar_solid.get_edgecolors()) == 0
        bin_dividers = next(
            collection
            for collection in colorbar_axis.collections
            if (
                isinstance(collection, LineCollection)
                and collection.get_gid() == "compare-map-bin-dividers"
            )
        )
        assert bin_dividers.get_alpha() == pytest.approx(
            plot_engine.COMPARE_MAP_COLORBAR_DIVIDER_ALPHA
        )
        assert bin_dividers.get_linewidths() == pytest.approx(
            plot_engine.COMPARE_MAP_COLORBAR_DIVIDER_LINEWIDTH
        )
        assert [
            float(segment[0][1])
            for segment in bin_dividers.get_segments()
        ] == pytest.approx(expected_boundaries_db[1:-1])
    finally:
        dispose_matplotlib_figure(rendered_map.figure)


@pytest.mark.parametrize(
    ("analysis_id", "absolute_mode"),
    [
        ("RX_ABS", "RX"),
        ("TX_ABS", "TX"),
    ],
)
@pytest.mark.parametrize("language", ["en", "de"])
@pytest.mark.parametrize(
    (
        "theme",
        "expected_target_edge",
        "expected_counter_edge",
        "expected_insufficient_face",
    ),
    [
        ("dark", "#000000", "#000000", "black"),
        ("light", "#000000", "#000000", "white"),
    ],
)
def test_success_map_renderer_uses_sector_rate_and_status_only_markers(
    monkeypatch,
    analysis_id,
    absolute_mode,
    language,
    theme,
    expected_target_edge,
    expected_counter_edge,
    expected_insufficient_face,
):
    """Keep the quantitative scale in sectors and marker evidence status only."""
    def fake_create_base_map_figure(**kwargs):
        figure = Figure(
            figsize=(8, 8),
            facecolor=kwargs["theme_config"]["fig_face"],
        )
        map_axis = figure.add_axes([0.05, 0.15, 0.75, 0.75])
        identity_transform = IdentityTransform()
        return figure, map_axis, identity_transform, identity_transform

    monkeypatch.setattr(
        plot_engine,
        "_preview_base_map_cache_enabled",
        lambda: False,
    )
    monkeypatch.setattr(
        plot_engine,
        "create_base_map_figure",
        fake_create_base_map_figure,
    )
    station_rows = pd.DataFrame(
        {
            "peer_lon": [1.0, 2.0, 3.0, 4.0],
            "peer_lat": [1.0, 2.0, 3.0, 4.0],
            "eligible": [True, True, True, False],
            "rate_pct": [0.0, 40.0, 100.0, 75.0],
            "hits": [0, 2, 5, 3],
            "misses": [5, 3, 0, 1],
            "r_min": [0.0, 0.0, 0.0, 0.0],
        }
    )
    segment_rows = pd.DataFrame(
        {
            "r_min": [0.0],
            "r_max": [2500.0],
            "az_bucket": [0.0],
            "val": [0.0],
        }
    )
    map_data = MapData(
        station_rows=station_rows,
        segment_rows=segment_rows,
        analysis_id=analysis_id,
        is_compare=False,
        is_sequential=False,
        analysis_kind="opportunity",
    )
    labels = T[language]
    analysis_context = AnalysisContext(
        callsign="TARGET",
        qth="JN47",
        band="20m",
    )
    presentation_context = PresentationContext(
        language=language,
        labels=labels,
        theme=theme,
        solar_label=T[language]["opt_solar_all"].split()[0],
    )

    rendered_map = plot_engine.render_map_figure(
        map_data,
        title="Performance map",
        start_t=datetime(2026, 7, 1, tzinfo=timezone.utc),
        end_t=datetime(2026, 7, 2, tzinfo=timezone.utc),
        max_dist_km=5000,
        base_min_stations=1,
        lat_0=0.0,
        lon_0=0.0,
        analysis_context=analysis_context,
        presentation_context=presentation_context,
    )
    try:
        _draw_figure_preview_image(rendered_map.figure, dpi=60)
        map_axis = rendered_map.figure.axes[0]
        sector_fills = next(
            collection
            for collection in map_axis.collections
            if collection.get_gid() == "success-sector-fills"
        )
        target_observed_markers = next(
            collection
            for collection in map_axis.collections
            if collection.get_gid() == "success-target-observed-markers"
        )
        counter_only_markers = next(
            collection
            for collection in map_axis.collections
            if collection.get_gid() == "success-counter-only-markers"
        )

        assert isinstance(sector_fills, PatchCollection)
        assert isinstance(target_observed_markers, PathCollection)
        assert isinstance(counter_only_markers, PathCollection)
        assert sector_fills.get_array().tolist() == [0.0]
        assert not any(
            collection.get_gid() == "success-no-qualifying-segments"
            for collection in map_axis.collections
        )
        assert target_observed_markers.get_array() is None
        assert counter_only_markers.get_array() is None
        np.testing.assert_allclose(
            target_observed_markers.get_offsets(),
            np.array([[2.0, 2.0], [3.0, 3.0]]),
        )
        np.testing.assert_allclose(
            counter_only_markers.get_offsets(),
            np.array([[1.0, 1.0]]),
        )
        assert target_observed_markers.get_sizes().tolist() == [
            plot_engine.SUCCESS_MAP_MARKER_SIZE_POINTS_SQUARED
        ]
        assert counter_only_markers.get_sizes().tolist() == [
            plot_engine.SUCCESS_MAP_MARKER_SIZE_POINTS_SQUARED
        ]
        assert tuple(sector_fills.cmap.colors) == tuple(
            plot_engine.SUCCESS_RATE_COLORS
        )
        for rate_pct, expected_color in (
            (0.0, "#081A3A"),
            (0.1, "#0D2B5B"),
            (0.9, "#0D2B5B"),
            (1.0, "#16457E"),
            (1.9, "#16457E"),
            (2.0, "#2A6AA3"),
            (4.9, "#2A6AA3"),
            (5.0, "#49A9C5"),
            (9.9, "#49A9C5"),
            (10.0, "#c9e5a3"),
        ):
            color_index = sector_fills.norm(rate_pct)
            assert sector_fills.cmap(color_index) == pytest.approx(
                to_rgba(expected_color)
            )
        assert sector_fills.get_alpha() == pytest.approx(
            plot_engine.SUCCESS_MAP_HEATMAP_ALPHA
        )
        assert sector_fills.norm.boundaries == pytest.approx(
            plot_engine.SUCCESS_RATE_BOUNDS
        )
        assert target_observed_markers.get_facecolors()[0] == pytest.approx(
            to_rgba(plot_engine.SUCCESS_MAP_TARGET_COLOR)
        )
        assert counter_only_markers.get_facecolors()[0] == pytest.approx(
            to_rgba(
                plot_engine.SUCCESS_MAP_COUNTER_COLOR,
                alpha=plot_engine.SUCCESS_MAP_COUNTER_ALPHA,
            )
        )
        assert target_observed_markers.get_edgecolors()[0] == pytest.approx(
            to_rgba(expected_target_edge)
        )
        assert counter_only_markers.get_edgecolors()[0] == pytest.approx(
            to_rgba(
                expected_counter_edge,
                alpha=plot_engine.SUCCESS_MAP_COUNTER_ALPHA,
            )
        )
        assert target_observed_markers.get_linewidths().tolist() == pytest.approx(
            [plot_engine.SUCCESS_MAP_MARKER_EDGE_LINEWIDTH_POINTS]
        )
        assert counter_only_markers.get_linewidths().tolist() == pytest.approx(
            [plot_engine.SUCCESS_MAP_MARKER_EDGE_LINEWIDTH_POINTS]
        )
        assert target_observed_markers.get_zorder() == pytest.approx(10.0)
        assert counter_only_markers.get_zorder() == pytest.approx(9.0)
        assert target_observed_markers.get_alpha() == pytest.approx(1.0)
        assert counter_only_markers.get_alpha() == pytest.approx(
            plot_engine.SUCCESS_MAP_COUNTER_ALPHA
        )
        assert not any(
            collection.get_gid() == "success-station-marker-halo"
            for collection in map_axis.collections
        )

        colorbar_axis = next(
            axis
            for axis in rendered_map.figure.axes
            if axis.get_ylabel()
            == labels[f"cbar_abs_{absolute_mode.lower()}"]
        )
        expected_colorbar_label = (
            f"Station-balanced {absolute_mode} Decode Rate (%)"
            if language == "en"
            else f"Stationsgleichgewichtete {absolute_mode}-Dekodierrate (%)"
        )
        assert colorbar_axis.get_ylabel() == expected_colorbar_label
        colorbar_solid = next(
            collection
            for collection in colorbar_axis.collections
            if isinstance(collection, QuadMesh)
        )
        assert colorbar_solid.get_alpha() == pytest.approx(
            plot_engine.SUCCESS_MAP_HEATMAP_ALPHA
        )
        summary_axis = next(
            axis
            for axis in rendered_map.figure.axes
            if [tick.get_text() for tick in axis.get_yticklabels()]
            == [
                labels["map_success_footer_stations"],
                labels["map_success_footer_opportunities"],
            ]
        )
        assert len(summary_axis.patches) == 4
        assert summary_axis.get_gid() == "success-map-footer"
        assert summary_axis.get_position().bounds == pytest.approx(
            plot_engine.SUCCESS_MAP_FOOTER_BBOX
        )
        assert {
            tick.get_fontsize() for tick in summary_axis.get_yticklabels()
        } == {plot_engine.FONT_LEGEND}
        station_tick, opportunity_tick = summary_axis.get_yticklabels()
        assert (
            opportunity_tick.get_window_extent().y0
            > station_tick.get_window_extent().y0
        )
        assert {text.get_text() for text in summary_axis.texts} == {
            "1",
            "2",
            "7",
            "8",
        }
        assert not any("%" in text.get_text() for text in summary_axis.texts)
        expected_success, expected_counter = _SUCCESS_OUTCOME_LABELS[
            (language, absolute_mode)
        ]
        footer_patch_labels = {
            patch.get_gid(): patch.get_label() for patch in summary_axis.patches
        }
        assert footer_patch_labels == {
            "success-footer-stations-target": expected_success,
            "success-footer-opportunities-target": expected_success,
            "success-footer-stations-counter": expected_counter,
            "success-footer-opportunities-counter": expected_counter,
        }

        legend = map_axis.get_legend()
        assert legend.get_gid() == "success-map-legend"
        assert [text.get_text() for text in legend.get_texts()] == [
            expected_success,
            expected_counter,
            labels["map_success_legend_insufficient"],
        ]
        assert not {
            "Target",
            "Elsewhere",
            "Other Signals",
        }.intersection(footer_patch_labels.values())
        assert {
            text.get_fontsize() for text in legend.get_texts()
        } == {plot_engine.FONT_LEGEND}
        insufficient_handle = legend.legend_handles[2]
        assert insufficient_handle.get_facecolor() == pytest.approx(
            to_rgba(expected_insufficient_face)
        )
        assert insufficient_handle.get_edgecolor() == pytest.approx(
            to_rgba("#777777")
        )
        assert insufficient_handle.get_linewidth() == pytest.approx(0.9)
        renderer = rendered_map.figure.canvas.get_renderer()
        legend_bounds = legend.get_window_extent(renderer)
        assert legend_bounds.x0 >= rendered_map.figure.bbox.x0
        assert legend_bounds.x1 <= rendered_map.figure.bbox.x1
        assert legend_bounds.y0 >= colorbar_axis.get_window_extent(renderer).y1
    finally:
        dispose_matplotlib_figure(rendered_map.figure)


def test_map_figure_stays_outside_pyplot_registry_and_disposes_artists():
    from matplotlib._pylab_helpers import Gcf

    managers_before = tuple(Gcf.get_all_fig_managers())
    figure = map_base._new_map_figure({"fig_face": "black"})
    axis = figure.add_axes([0.0, 0.0, 1.0, 1.0])
    axis.imshow(np.zeros((8, 8, 3), dtype=np.uint8))
    figure.canvas.draw()

    assert tuple(Gcf.get_all_fig_managers()) == managers_before
    assert len(figure.axes) == 1

    dispose_matplotlib_figure(figure)

    assert tuple(Gcf.get_all_fig_managers()) == managers_before
    assert figure.axes == []


def test_footer_summary_renderer_always_draws_spots_and_stations_rows():
    from matplotlib.figure import Figure

    figure = Figure(figsize=(8, 2), facecolor="black")
    try:
        summary_axis = plot_engine._draw_footer_summary_bars(
            figure,
            station_counts=[3, 7],
            spot_counts=[20, 80],
            colors=["#39ff14", "#d0d0d0"],
            text_colors=["black", "black"],
            theme_config={
                "bar_face": "black",
                "bar_tick": "white",
                "bar_bbox": [0.12, 0.1, 0.8, 0.6],
            },
        )

        assert [tick.get_text() for tick in summary_axis.get_yticklabels()] == [
            "STATIONS",
            "SPOTS",
        ]
        assert len(summary_axis.patches) == 4
        assert {label.get_text() for label in summary_axis.texts} == {
            "3",
            "7",
            "20",
            "80",
        }
    finally:
        dispose_matplotlib_figure(figure)


def test_success_footer_rows_accept_localized_labels_and_count_grouping():
    """Reuse compact footer counts with localized Success row labels and order."""
    figure = Figure(figsize=(12, 2), facecolor="black")
    try:
        summary_axis = plot_engine._draw_footer_summary_bars(
            figure,
            station_counts=[3000, 7000],
            spot_counts=[20000, 80000],
            colors=[plot_engine.SUCCESS_MAP_TARGET_COLOR, "#ffffff"],
            text_colors=["black", "black"],
            theme_config={
                "bar_face": "black",
                "bar_tick": "white",
                "bar_bbox": [0.12, 0.1, 0.85, 0.45],
            },
            stations_plural="STATIONEN",
            evidence_plural="GELEGENHEITEN",
            thousands_separator=".",
            row_label_fontsize=plot_engine.FONT_LEGEND - 2,
        )

        assert [tick.get_text() for tick in summary_axis.get_yticklabels()] == [
            "STATIONEN",
            "GELEGENHEITEN",
        ]
        assert len(summary_axis.patches) == 4
        assert {label.get_text() for label in summary_axis.texts} == {
            "3.000",
            "7.000",
            "20.000",
            "80.000",
        }
        assert not any("%" in label.get_text() for label in summary_axis.texts)
        _draw_figure_preview_image(figure, dpi=100)
        renderer = figure.canvas.get_renderer()
        station_tick, opportunity_tick = summary_axis.get_yticklabels()
        assert (
            opportunity_tick.get_window_extent(renderer).y0
            > station_tick.get_window_extent(renderer).y0
        )
        assert all(
            label.get_window_extent(renderer).x0 >= 0
            for label in summary_axis.get_yticklabels()
        )
    finally:
        dispose_matplotlib_figure(figure)


def test_cached_basemap_pixels_are_compact_uint8_rgb(tmp_path):
    cache_path = tmp_path / "basemap.png"
    source_pixels = np.zeros((12, 10, 4), dtype=np.uint8)
    source_pixels[..., 0] = 17
    source_pixels[..., 1] = 34
    source_pixels[..., 2] = 51
    source_pixels[..., 3] = 255
    Image.fromarray(source_pixels, mode="RGBA").save(cache_path)

    loaded_pixels = map_base._load_cached_basemap_pixels(cache_path)

    assert loaded_pixels.dtype == np.uint8
    assert loaded_pixels.shape == (12, 10, 3)
    assert loaded_pixels.nbytes == 12 * 10 * 3
    assert loaded_pixels[0, 0].tolist() == [17, 34, 51]


def test_cached_preview_draws_map_annotations_above_segment_wedges(tmp_path, monkeypatch):
    """Keep labels dynamic so cached background pixels cannot cover their z-order."""
    cache_path = tmp_path / "basemap.png"
    Image.fromarray(np.zeros((12, 10, 3), dtype=np.uint8), mode="RGB").save(cache_path)
    monkeypatch.setattr(
        map_base,
        "_ensure_static_basemap_cache",
        lambda **_kwargs: (cache_path, "hit"),
    )

    figure, axis, _map_projection, _plate_carree_projection, _cache_detail = (
        map_base.create_preview_cached_base_map_figure(
            title="Foreground annotation test",
            maximum_distance_km=22000,
            center_latitude=0.0,
            center_longitude=0.0,
            theme_name="dark",
            theme_config=plot_engine.MAP_THEMES["dark"],
        )
    )

    try:
        annotation_texts = {
            text_artist.get_text().strip(): text_artist for text_artist in axis.texts
        }
        assert {"10000 km", "15000 km", "20000 km", "N-POL", "S-POL"} <= set(
            annotation_texts
        )
        assert all(
            text_artist.get_zorder() > 3 for text_artist in annotation_texts.values()
        )
        assert len(axis.lines) == 2
        assert all(
            pole_marker.get_zorder() > 3 for pole_marker in axis.lines
        )
    finally:
        dispose_matplotlib_figure(figure)


def test_renderer_upgrades_base_canvas_and_uses_stable_local_agg_canvas():
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure

    figure = Figure(figsize=(4, 3), facecolor="black")
    axis = figure.add_subplot(1, 1, 1)
    axis.plot([0, 1], [0, 1])
    assert not isinstance(figure.canvas, FigureCanvasAgg)

    try:
        image, dimensions = _draw_figure_preview_image(figure, dpi=80)
    finally:
        dispose_matplotlib_figure(figure)

    assert image.mode == "RGBA"
    assert dimensions == (320, 240)
    assert isinstance(figure.canvas, FigureCanvasAgg)


def test_static_basemap_save_uses_atomic_temporary_file_and_cleans_it(tmp_path):
    cache_path = tmp_path / "basemap.png"
    figure = map_base._new_map_figure({"fig_face": "black"})
    axis = figure.add_axes([0.0, 0.0, 1.0, 1.0])
    axis.imshow(np.full((8, 8, 3), 127, dtype=np.uint8))

    try:
        map_base._save_static_basemap_preview(figure, cache_path, preview_dpi=10)
    finally:
        dispose_matplotlib_figure(figure)

    assert cache_path.exists()
    with Image.open(cache_path) as cached_image:
        cached_image.verify()
    assert list(tmp_path.glob("*.tmp")) == []


def test_same_basemap_key_is_created_once_under_concurrency(tmp_path, monkeypatch):
    worker_count = 6
    start_barrier = threading.Barrier(worker_count)
    build_count = 0
    build_count_lock = threading.Lock()

    class FakeFigure:
        def clear(self):
            return None

    def fake_create_base_map_figure(**_kwargs):
        nonlocal build_count
        with build_count_lock:
            build_count += 1
        return FakeFigure(), None, None, None

    def fake_save_static_basemap_preview(_figure, cache_path, _preview_dpi):
        time.sleep(0.05)
        cache_path.write_bytes(b"complete-basemap")

    monkeypatch.setattr(map_base, "CACHE_DIR", str(tmp_path))
    monkeypatch.setattr(map_base, "create_base_map_figure", fake_create_base_map_figure)
    monkeypatch.setattr(map_base, "_save_static_basemap_preview", fake_save_static_basemap_preview)

    def ensure_cache():
        start_barrier.wait()
        return map_base._ensure_static_basemap_cache(
            maximum_distance_km=22000,
            center_latitude=47.5,
            center_longitude=7.0,
            theme_name="dark",
            theme_config={"fig_face": "black"},
            cache_label="JN37",
            preview_dpi=100,
        )

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        results = list(executor.map(lambda _index: ensure_cache(), range(worker_count)))

    cache_paths = [cache_path for cache_path, _status in results]
    cache_statuses = [status for _cache_path, status in results]
    assert build_count == 1
    assert cache_statuses.count("miss") == 1
    assert cache_statuses.count("hit") == worker_count - 1
    assert len(set(cache_paths)) == 1
    assert cache_paths[0].read_bytes() == b"complete-basemap"
    assert map_base.ARTIFACT_STORE.lock_bookkeeping_size == 64
    assert list(tmp_path.glob(".artifact-locks/*.lock")) == []


def test_segment_and_opportunity_figures_render_concurrently_without_pyplot_state():
    from matplotlib._pylab_helpers import Gcf

    worker_count = 6
    start_barrier = threading.Barrier(worker_count)
    managers_before = tuple(Gcf.get_all_fig_managers())
    segment_recipe = {
        "title": "Concurrent Segment Insight",
        "selected_segment": "Full Range | All Directions",
        "is_sequential": False,
        "station_values": np.array([-1.0, 0.0, 1.0]),
        "spot_values": np.array([-2.0, -1.0, 0.0, 1.0, 2.0]),
        "panel_station_counts": [1, 3, 1, 1],
        "panel_spot_counts": [2, 10, 3, 1],
        "panel_series_labels": ["Stations", "Spots"],
        "panel_labels": ["Target", "Joint", "Both (Async)", "Reference"],
        "panel_y_label": "Share (%)",
    }
    segment_recipe = _localized_compare_segment_recipe(segment_recipe)
    opportunity_recipe = _success_segment_figure_recipe_for_test(
        "Concurrent Opportunity Insight"
    )

    def render_figure(task_index):
        start_barrier.wait()
        figure = (
            render_segment_insight_export_figure(segment_recipe)
            if task_index % 2 == 0
            else _render_opportunity_segment_figure(opportunity_recipe)
        )
        try:
            image, dimensions = _draw_figure_preview_image(figure, dpi=60)
            image_buffer = BytesIO()
            _serialize_preview_png(image, image_buffer)
            return image_buffer.getvalue(), dimensions
        finally:
            dispose_matplotlib_figure(figure)

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        results = list(executor.map(render_figure, range(worker_count)))

    assert tuple(Gcf.get_all_fig_managers()) == managers_before
    for image_bytes, dimensions in results:
        assert image_bytes.startswith(b"\x89PNG\r\n\x1a\n")
        assert dimensions[0] > 0
        assert dimensions[1] > 0


def test_high_resolution_export_uses_shared_matplotlib_runtime():
    recipe = {
        "title": "Export Segment Insight",
        "selected_segment": "Full Range | All Directions",
        "is_sequential": False,
        "station_values": np.array([-1.0, 0.0, 1.0]),
        "spot_values": np.array([-2.0, 0.0, 2.0]),
        "panel_station_counts": [1, 3, 1, 1],
        "panel_spot_counts": [2, 6, 2, 2],
        "panel_series_labels": ["Stations", "Spots"],
        "panel_labels": ["Target", "Joint", "Both (Async)", "Reference"],
        "panel_y_label": "Share (%)",
    }
    recipe = _localized_compare_segment_recipe(recipe)
    figure = render_segment_insight_export_figure(recipe)
    try:
        image_bytes = figure_to_png_bytes(figure, dpi=80, paper_theme=True)
    finally:
        dispose_matplotlib_figure(figure)

    assert image_bytes.startswith(b"\x89PNG\r\n\x1a\n")


def test_compare_segment_histograms_share_median_legend_and_mean_placement():
    """Standardize Compare median legends and separate Mean annotations."""
    recipe = {
        "title": "RX Compare",
        "selected_segment": "Full Range | All Directions",
        "is_sequential": False,
        "station_values": np.array([6.0, 7.0]),
        "spot_values": np.array([6.0, 8.0]),
        "panel_station_counts": [1, 2, 0, 1],
        "panel_spot_counts": [2, 8, 1, 3],
        "panel_series_labels": ["Stations", "Spots"],
        "panel_labels": ["Target", "Joint", "Both (Async)", "Reference"],
        "panel_y_label": "Share (%)",
    }
    recipe = _localized_compare_segment_recipe(recipe)

    figure = render_segment_insight_export_figure(recipe)
    try:
        station_axis = next(
            axis for axis in figure.axes if axis.get_title().startswith("Station Medians")
        )
        spot_axis = next(
            axis for axis in figure.axes if axis.get_title() == "Joint-Spot \u0394 SNR"
        )
        station_labels = [
            text.get_text() for text in station_axis.get_legend().get_texts()
        ]
        spot_labels = [
            text.get_text() for text in spot_axis.get_legend().get_texts()
        ]

        assert station_labels == ["Median +6.5 dB"]
        assert spot_labels == ["Median +7.0 dB"]
        assert not any(
            "Stability" in label
            for label in [*station_labels, *spot_labels]
        )
        assert {
            text.get_text()
            for text in station_axis.texts
            if text.get_gid() == "compare-metric-mean"
        } == {"Mean +6.5 dB"}
        assert {
            text.get_text()
            for text in spot_axis.texts
            if text.get_gid() == "compare-metric-mean"
        } == {"Mean +7.0 dB"}
        for axis in (station_axis, spot_axis):
            mean_annotation = next(
                text
                for text in axis.texts
                if text.get_gid() == "compare-metric-mean"
            )
            assert mean_annotation.get_position() == pytest.approx((0.98, 0.04))
            assert mean_annotation.get_fontsize() == pytest.approx(8.0)
            assert mean_annotation.get_zorder() == pytest.approx(10.0)
            assert {
                text.get_fontsize()
                for text in axis.get_legend().get_texts()
            } == {8.0}
    finally:
        dispose_matplotlib_figure(figure)


def test_compare_outcomes_and_station_histogram_share_station_hatching():
    """Keep split inside legends and dense station hatching across Compare."""
    recipe = {
        "title": "RX Compare",
        "selected_segment": "Full Range | All Directions",
        "is_sequential": False,
        "station_values": np.array([-2.0, 0.0, 2.0]),
        "spot_values": np.array([-3.0, -1.0, 1.0, 3.0]),
        "panel_station_counts": [1, 2, 0, 1],
        "panel_spot_counts": [1, 198, 1, 0],
        "panel_series_labels": ["Stations", "Spots"],
        "panel_labels": ["Target only", "Joint", "Both (Async)", "Reference only"],
        "panel_y_label": "Share (%)",
    }
    recipe = _localized_compare_segment_recipe(recipe)

    figure = render_segment_insight_export_figure(recipe)
    try:
        outcome_axis = next(
            axis for axis in figure.axes if axis.get_title() == "Decode Outcomes"
        )
        station_bars = [
            patch
            for patch in outcome_axis.patches
            if patch.get_gid() == "decode-outcome-stations"
        ]
        spot_bars = [
            patch
            for patch in outcome_axis.patches
            if patch.get_gid() == "decode-outcome-spots"
        ]

        assert len(station_bars) == len(spot_bars) == 4
        for station_bar, spot_bar in zip(station_bars, spot_bars):
            station_center = station_bar.get_x() + station_bar.get_width() / 2.0
            spot_center = spot_bar.get_x() + spot_bar.get_width() / 2.0
            assert station_center < spot_center
            assert station_bar.get_hatch() == "//////"
            assert station_bar.get_facecolor()[3] == pytest.approx(0.0)
            assert spot_bar.get_hatch() is None
            assert spot_bar.get_facecolor()[:3] == pytest.approx(
                to_rgba("#36aaf9")[:3]
            )

        assert [
            text.get_text()
            for text in outcome_axis.texts
            if text.get_gid() == "decode-outcome-percentage"
        ] == [
            "25%",
            "50%",
            "0%",
            "25%",
            "<1%",
            "99%",
            "<1%",
            "0%",
        ]
        assert outcome_axis.get_ylabel() == "Share (%)"
        assert outcome_axis.get_ylim() == pytest.approx((0.0, 120.0))
        assert max(outcome_axis.get_yticks()) == pytest.approx(100.0)
        outcome_legends = {
            artist.get_gid(): artist
            for artist in outcome_axis.get_children()
            if isinstance(artist, Legend)
        }
        assert [
            text.get_text()
            for text in outcome_legends[
                "decode-outcome-station-legend"
            ].get_texts()
        ] == ["Stations"]
        assert [
            text.get_text()
            for text in outcome_legends[
                "decode-outcome-spot-legend"
            ].get_texts()
        ] == ["Spots"]
        figure.canvas.draw()
        renderer = figure.canvas.get_renderer()
        axis_center_x = outcome_axis.get_window_extent(renderer).x0 + (
            outcome_axis.get_window_extent(renderer).width / 2.0
        )
        assert (
            outcome_legends["decode-outcome-station-legend"]
            .get_window_extent(renderer)
            .x1
            < axis_center_x
        )
        assert (
            outcome_legends["decode-outcome-spot-legend"]
            .get_window_extent(renderer)
            .x0
            > axis_center_x
        )

        station_axis = next(
            axis for axis in figure.axes if axis.get_title().startswith("Station Medians")
        )
        spot_axis = next(
            axis for axis in figure.axes if axis.get_title() == "Joint-Spot \u0394 SNR"
        )
        station_histogram_bars = [
            patch
            for patch in station_axis.patches
            if patch.get_gid() == "station-median-histogram"
        ]
        spot_histogram_bars = [
            patch
            for patch in spot_axis.patches
            if patch.get_gid() == "spot-metric-histogram"
        ]
        assert station_histogram_bars
        assert spot_histogram_bars
        assert {
            patch.get_hatch() for patch in station_histogram_bars
        } == {"//////"}
        assert {
            patch.get_facecolor()[3] for patch in station_histogram_bars
        } == {0.0}
        assert {
            patch.get_hatch() for patch in spot_histogram_bars
        } == {None}
        for patch in spot_histogram_bars:
            assert patch.get_facecolor()[:3] == pytest.approx(
                to_rgba("#36aaf9")[:3]
            )
    finally:
        dispose_matplotlib_figure(figure)


def test_success_segment_figure_uses_shared_legend_and_axis_label_style():
    """Apply shared styling to the exact-distance Success evidence panels."""
    recipe = _success_segment_figure_recipe_for_test("RX Performance")
    labels = _success_figure_labels(T["en"], "RX_ABS")

    figure = render_segment_insight_export_figure(recipe)
    try:
        figure.canvas.draw()
        reach_axis = next(
            axis
            for axis in figure.axes
            if axis.get_gid() == "success-distance-reach-axis"
        )
        consistency_axis = next(
            axis
            for axis in figure.axes
            if axis.get_gid() == "success-distance-consistency-axis"
        )
        snr_axis = next(
            axis
            for axis in figure.axes
            if axis.get_gid() == "success-distance-snr-axis"
        )

        assert figure.get_size_inches() == pytest.approx((13.0, 6.5))
        assert len(figure.axes) == 3
        assert figure._suptitle.get_fontsize() == pytest.approx(14.0)
        assert figure._suptitle.get_fontweight() == "bold"
        assert tuple(figure._suptitle.get_fontfamily()) == ("sans-serif",)
        for axis in (reach_axis, consistency_axis, snr_axis):
            assert axis.title.get_fontsize() == pytest.approx(12.0)
            assert axis.title.get_fontweight() == "bold"
            assert tuple(axis.title.get_fontfamily()) == ("sans-serif",)
            assert all(
                tick.get_fontsize() == pytest.approx(9.0)
                and tuple(tick.get_fontfamily()) == ("sans-serif",)
                for tick in axis.get_xticklabels()
            )

        reach_bar = next(
            patch
            for patch in reach_axis.patches
            if patch.get_gid() == "success-distance-peer-reach"
        )
        assert reach_bar.get_facecolor()[:3] == pytest.approx(
            to_rgba("#36aaf9")[:3]
        )
        assert reach_bar.get_edgecolor()[:3] == pytest.approx(
            to_rgba("#67c4ff")[:3]
        )
        assert reach_bar.get_alpha() == pytest.approx(0.70)

        _assert_shared_evidence_legend(
            figure,
            consistency_axis.get_legend(),
            [
                labels["station_balanced"],
                labels["observation_level"],
            ],
        )
        _assert_shared_axis_label(
            reach_axis.xaxis.label,
            labels["distance_x"],
        )
        _assert_shared_axis_label(
            reach_axis.yaxis.label,
            labels["reach_y"],
        )
        _assert_shared_axis_label(
            consistency_axis.xaxis.label,
            labels["distance_x"],
        )
        _assert_shared_axis_label(
            consistency_axis.yaxis.label,
            labels["rate_y"],
        )
        _assert_shared_axis_label(
            snr_axis.xaxis.label,
            labels["distance_x"],
        )
        _assert_shared_axis_label(
            snr_axis.yaxis.label,
            labels["snr_y"],
        )
    finally:
        dispose_matplotlib_figure(figure)


def test_segment_insight_rejects_obsolete_opportunity_recipe_alias():
    """Require the explicit current Success evidence recipe kind."""
    assert render_segment_insight_export_figure({"kind": "opportunity"}) is None


def test_success_segment_layout_matches_compare_panel_size_and_title_clearance():
    """Match Compare panel width and measure clearance between both title tiers."""
    compare_recipe = {
        "title": "RX Compare",
        "selected_segment": "Full Range | All Directions",
        "is_sequential": False,
        "station_values": np.array([-2.0, 0.0, 2.0]),
        "spot_values": np.array([-3.0, -1.0, 1.0, 3.0]),
        "panel_station_counts": [1, 2, 0, 1],
        "panel_spot_counts": [1, 8, 1, 0],
        "panel_series_labels": ["Stations", "Spots"],
        "panel_labels": [
            "Target only",
            "Joint",
            "Both (Async)",
            "Reference only",
        ],
        "panel_y_label": "Share (%)",
    }
    compare_recipe = _localized_compare_segment_recipe(compare_recipe)
    success_recipe = _success_segment_figure_recipe_for_test("RX Performance")
    compare_figure = render_segment_insight_export_figure(compare_recipe)
    success_figure = _render_opportunity_segment_figure(success_recipe)
    try:
        compare_figure.canvas.draw()
        success_figure.canvas.draw()
        compare_renderer = compare_figure.canvas.get_renderer()
        success_renderer = success_figure.canvas.get_renderer()
        compare_axes = compare_figure.axes[:3]
        success_axes = success_figure.axes[:3]

        compare_panel_width_inches = (
            compare_axes[0].get_window_extent(compare_renderer).width
            / compare_figure.dpi
        )
        compare_title_clearance_inches = (
            compare_figure._suptitle.get_window_extent(compare_renderer).y0
            - compare_axes[0].title.get_window_extent(compare_renderer).y1
        ) / compare_figure.dpi

        for success_axis in success_axes:
            success_extent = success_axis.get_window_extent(success_renderer)
            success_title_clearance_inches = (
                success_figure._suptitle.get_window_extent(
                    success_renderer
                ).y0
                - success_axis.title.get_window_extent(success_renderer).y1
            ) / success_figure.dpi
            assert (
                success_extent.width / success_figure.dpi
                == pytest.approx(compare_panel_width_inches, abs=0.01)
            )
            assert (
                success_extent.height / success_figure.dpi
                == pytest.approx(compare_panel_width_inches, abs=0.01)
            )
            assert success_title_clearance_inches == pytest.approx(
                compare_title_clearance_inches,
                abs=0.02,
            )

        assert success_recipe["labels"]["locator_precision_note"] not in {
            text.get_text() for text in success_figure.texts
        }
    finally:
        dispose_matplotlib_figure(compare_figure)
        dispose_matplotlib_figure(success_figure)


def test_sequential_segment_recipe_preserves_scheduled_pair_title():
    """Render the scheduled-pair evidence title stored with the recipe."""
    base_recipe = {
        "title": "TX A/B Segment Insight",
        "selected_segment": "Full Range | All Directions",
        "is_sequential": True,
        "station_values": np.array([-1.0, 0.0, 1.0]),
        "spot_values": np.array([-2.0, 0.0, 2.0]),
        "panel_station_counts": [1, 3, 1, 1],
        "panel_spot_counts": [2, 6, 2, 1],
        "panel_series_labels": ["Stations", "Scheduled pairs"],
        "panel_labels": ["Target", "Joint", "Both (Async)", "Reference"],
        "panel_y_label": "Share (%)",
    }
    base_recipe = _localized_compare_segment_recipe(base_recipe)

    evidence_title = "Scheduled-Pair \u0394 SNR"
    figure = render_segment_insight_export_figure(
        {**base_recipe, "paired_evidence_title": evidence_title}
    )
    try:
        assert evidence_title in {axis.get_title() for axis in figure.axes}
    finally:
        dispose_matplotlib_figure(figure)


def test_preview_renderer_returns_the_displayed_png_bytes(monkeypatch):
    from matplotlib.figure import Figure

    from ui import matplotlib_renderer

    displayed = []
    monkeypatch.setattr(matplotlib_renderer.st, "image", lambda image, **kwargs: displayed.append(image))
    figure = Figure(figsize=(2, 1), facecolor="black")
    figure.add_subplot(111).plot([0, 1], [0, 1])
    try:
        image_bytes = matplotlib_renderer.render_matplotlib_figure(figure, dpi=40)
    finally:
        dispose_matplotlib_figure(figure)

    assert image_bytes.startswith(b"\x89PNG\r\n\x1a\n")
    assert displayed == [image_bytes]
