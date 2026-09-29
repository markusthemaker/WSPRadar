"""Regression coverage for Benchmark selected and temporal evidence."""

from matplotlib.collections import QuadMesh
from matplotlib.colors import to_rgba
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import pytest

from config import TEMPORAL_IQR_BAND_ALPHA
from i18n import T
from ui.matplotlib_renderer import dispose_matplotlib_figure
from ui.results_export import figure_to_png_bytes
from ui.plots import evidence_figures
from ui.plots.evidence_figures import (
    METRIC_FONT_FAMILY,
    METRIC_LEGEND_FONTSIZE,
    SEGMENT_FIGURE_BASE_HEIGHT_INCHES,
    SEGMENT_FIGURE_BOTTOM,
    SEGMENT_FIGURE_FOOTER_Y,
    SEGMENT_INSIGHT_CORRECTION_FOOTER_ADDED_HEIGHT_INCHES,
    SEGMENT_TEMPORAL_CORRECTION_FOOTER_ADDED_HEIGHT_INCHES,
    SEGMENT_TEMPORAL_FIGURE_TOP,
    TEMPORAL_IQR_COLOR,
    TEMPORAL_IQR_MIN_COUNT,
    TEMPORAL_IQR_UNDERSTROKE_COLOR,
    _build_compare_median_focus_spec,
    _compare_median_focus_forward,
    _compare_median_focus_inverse,
    _compare_median_focus_spec_from_recipe,
    _segment_figure_export_recipe,
    _segment_temporal_evidence_export_recipe,
    _selected_evidence_export_recipe,
    render_segment_insight_export_figure,
    render_segment_temporal_evidence_export_figure,
    render_selected_evidence_export_figure,
)


def _localized_selected_evidence_recipe(
    plot_df,
    evidence_title,
    time_agg,
    *,
    language="en",

    **overrides,
):
    """Build one localized dual-panel selected-Benchmark recipe."""
    translations = T[language]
    analysis_start_t, analysis_end_t = _default_temporal_bounds(
        plot_df,
        time_agg,
    )
    presentation = {
        "reference_snr_correction_db": 0.0,
        "analysis_start_t": analysis_start_t,
        "analysis_end_t": analysis_end_t,
        "count_label": translations[
            (
                "fig_joint_spot_count"
            )
        ],
        "chronological_title": translations[
            "fig_selected_compare_chronological_title"
        ],
        "chronological_x_label": translations[
            "fig_segment_chronological_x"
        ],
        "chronological_unavailable_text": translations[
            "fig_compare_chronological_unavailable"
        ],
        "metric_axis_label": translations["tbl_col_delta_snr"],
        "folded_title": translations[
            "fig_selected_compare_folded_title"
        ],
        "folded_x_label": translations["fig_segment_utc_hour_x"],
        "folded_date_annotation": translations[
            "fig_segment_dates_folded"
        ].replace("{count}", "{utc_date_count}"),
        "density_label": translations[
            (
                "fig_relative_joint_spot_density"
            )
        ],
        "folded_unavailable_text": translations[
            "fig_segment_folded_unavailable"
        ],
        "median_focus_axis_label": translations[
            "fig_compare_median_focus_axis"
        ],
        "median_label": translations["fig_median_label"],
        "bin_median_label": translations["fig_temporal_bin_median"],
        "bin_iqr_label": translations["fig_temporal_bin_iqr"],
    }
    presentation.update(overrides)
    return _selected_evidence_export_recipe(
        plot_df,
        evidence_title,
        time_agg,

        **presentation,
    )


def _localized_segment_temporal_recipe(
    plot_df,
    title,
    time_bin,
    count_label=None,
    *,
    language="en",

    **overrides,
):
    """Build a segment-temporal recipe with explicit localized labels."""
    translations = T[language]
    analysis_start_t, analysis_end_t = _default_temporal_bounds(
        plot_df,
        time_bin,
    )
    resolved_count_label = count_label or translations[
        (
            "fig_joint_spot_count"
        )
    ]
    chronological_title = translations["fig_segment_chronological_delta"]
    presentation = {
        "reference_snr_correction_db": 0.0,
        "analysis_start_t": analysis_start_t,
        "analysis_end_t": analysis_end_t,
        "chronological_title": translations[
            "fmt_temporal_title_with_bins"
        ].format(
            title=chronological_title,
            time_bin="{time_bin}",
        ),
        "chronological_x_label": translations[
            "fig_segment_chronological_x"
        ],
        "chronological_unavailable_text": translations[
            "fig_compare_chronological_unavailable"
        ],
        "metric_axis_label": translations["tbl_col_delta_snr"],
        "folded_title": translations["fig_segment_utc_hour_title"],
        "folded_x_label": translations["fig_segment_utc_hour_x"],
        "folded_date_annotation": translations[
            "fig_segment_dates_folded"
        ].replace("{count}", "{utc_date_count}"),
        "density_label": translations[
            (
                "fig_relative_joint_spot_density"
            )
        ],
        "folded_unavailable_text": translations[
            "fig_segment_folded_unavailable"
        ],
        "median_focus_axis_label": translations[
            "fig_compare_median_focus_axis"
        ],
        "median_label": translations["fig_median_label"],
        "bin_median_label": translations["fig_temporal_bin_median"],
        "bin_iqr_label": translations["fig_temporal_bin_iqr"],
    }
    presentation.update(overrides)
    return _segment_temporal_evidence_export_recipe(
        plot_df,
        title,
        time_bin,
        resolved_count_label,
        **presentation,
    )


def _default_temporal_bounds(plot_df, time_bin):
    """Return old-compatible test bounds unless a case supplies explicit bounds."""
    bin_minutes = evidence_figures._time_agg_minutes(time_bin)
    bin_delta = pd.Timedelta(minutes=bin_minutes)
    if plot_df is None or plot_df.empty or "plot_time" not in plot_df.columns:
        start = pd.Timestamp("2026-07-01T00:00:00Z")
        return start, start + bin_delta
    plot_times = pd.to_datetime(
        plot_df["plot_time"],
        errors="coerce",
        utc=True,
    ).dropna()
    if plot_times.empty:
        start = pd.Timestamp("2026-07-01T00:00:00Z")
        return start, start + bin_delta
    start = plot_times.min().floor(f"{bin_minutes}min")
    end = plot_times.max().floor(f"{bin_minutes}min") + bin_delta
    return start, end


def _correction_footer_test_rows():
    """Return compact two-date Joint evidence for correction-footer tests."""
    return pd.DataFrame(
        {
            "identity": ["A (AA00)", "A (AA00)", "A (AA00)"],
            "plot_time": pd.to_datetime(
                [
                    "2026-07-01T00:05:00Z",
                    "2026-07-01T06:05:00Z",
                    "2026-07-02T00:05:00Z",
                ],
                utc=True,
            ),
            "metric": [-1.0, 0.5, 2.0],
        }
    )


def _correction_footer_segment_recipe(notice=""):
    """Build one complete Benchmark segment recipe for footer assertions."""
    return _segment_figure_export_recipe(
        title="RX Benchmark",
        selected_segment="Full Range | All Directions",

        station_values=[-1.0, 1.0],
        spot_values=[-2.0, 0.0, 2.0],
        panel_labels=["Only Target", "Joint", "Both (Async)", "Only Reference"],
        panel_y_label="Share (%)",
        decode_outcomes_title="Decode Outcomes",
        station_medians_title="Station Medians Delta SNR",
        paired_evidence_title="Joint-Spot Delta SNR",
        metric_axis_label="Delta SNR (dB)",
        median_label="Median",
        mean_label="Mean",
        no_data_label="No data",
        panel_station_counts=[1, 2, 0, 1],
        panel_spot_counts=[2, 6, 0, 2],
        panel_series_labels=["Stations", "Spots"],
        reference_snr_correction_notice=notice,
    )


def _render_correction_footer_figure(figure_kind, notice):
    """Render one Benchmark Delta-SNR figure through the requested recipe path."""
    if figure_kind == "segment":
        recipe = _correction_footer_segment_recipe(notice)
        return render_segment_insight_export_figure(recipe), recipe
    if figure_kind == "segment_temporal":
        recipe = _localized_segment_temporal_recipe(
            _correction_footer_test_rows(),
            "RX Benchmark Temporal Evidence",
            "3h",
            reference_snr_correction_notice=notice,
        )
        return render_segment_temporal_evidence_export_figure(recipe), recipe
    if figure_kind == "selected":
        recipe = _localized_selected_evidence_recipe(
            _correction_footer_test_rows(),
            "Selected Station Evidence",
            "3h",
            reference_snr_correction_notice=notice,
        )
        return render_selected_evidence_export_figure(recipe), recipe
    raise AssertionError(f"Unsupported figure kind: {figure_kind}")


def test_compare_segment_recipe_retains_histograms_without_observation_vectors():
    """Keep exact Segment Insight statistics independent of evidence row count."""
    recipe = _correction_footer_segment_recipe()

    assert recipe["schema_version"] == 3
    assert "station_values" not in recipe
    assert "spot_values" not in recipe
    assert recipe["station_histogram"]["counts"].sum() == 2
    assert recipe["spot_histogram"]["counts"].sum() == 3
    assert recipe["station_histogram"]["median"] == pytest.approx(0.0)
    assert recipe["spot_histogram"]["mean"] == pytest.approx(0.0)


@pytest.mark.parametrize(
    "figure_kind",
    ["segment", "segment_temporal", "selected"],
)
def test_compare_delta_snr_recipes_propagate_and_render_correction_footer(
    figure_kind,
):
    """Keep a configured correction in each Delta-SNR recipe and footer."""
    notice = "Configured SNR correction: +1.2 dB applied to Reference (ON4AWM1)"
    figure, recipe = _render_correction_footer_figure(figure_kind, notice)
    try:
        assert recipe["reference_snr_correction_notice"] == notice
        correction_notices = [
            artist
            for artist in figure.texts
            if artist.get_gid() == "reference-snr-correction-notice"
        ]
        assert len(correction_notices) == 1
        correction_notice = correction_notices[0]
        assert correction_notice.get_text() == notice
        assert correction_notice.get_position() == pytest.approx(
            (
                0.02,
                SEGMENT_FIGURE_FOOTER_Y
                * SEGMENT_FIGURE_BASE_HEIGHT_INCHES
                / figure.get_figheight(),
            )
        )
        assert correction_notice.get_ha() == "left"
        assert correction_notice.get_va() == "bottom"
        assert correction_notice.get_fontsize() == pytest.approx(
            METRIC_LEGEND_FONTSIZE
        )
        assert tuple(correction_notice.get_fontfamily()) == (
            METRIC_FONT_FAMILY,
        )
        assert correction_notice.get_fontweight() == "normal"
        figure.canvas.draw()
        renderer = figure.canvas.get_renderer()
        correction_bounds = correction_notice.get_window_extent(renderer)
        version_notices = [
            artist
            for artist in figure.texts
            if artist.get_text().startswith("WSPRadar.org ")
        ]
        assert len(version_notices) == 1
        version_bounds = version_notices[0].get_window_extent(renderer)
        assert figure.bbox.contains(correction_bounds.x0, correction_bounds.y0)
        assert figure.bbox.contains(correction_bounds.x1, correction_bounds.y1)
        assert correction_bounds.x1 < version_bounds.x0
    finally:
        dispose_matplotlib_figure(figure)


@pytest.mark.parametrize(
    "figure_kind",
    ["segment", "segment_temporal", "selected"],
)
def test_compare_delta_snr_footer_adds_canvas_without_shrinking_plot(
    figure_kind,
):
    """Reserve a separate footer strip while preserving the original plot area."""
    notice = "Configured SNR correction: +1.2 dB applied to Reference (ON4AWM1)"
    corrected_figure, _recipe = _render_correction_footer_figure(
        figure_kind,
        notice,
    )
    baseline_figure, _baseline_recipe = _render_correction_footer_figure(
        figure_kind,
        "",
    )
    try:
        expected_added_height_inches = (
            SEGMENT_INSIGHT_CORRECTION_FOOTER_ADDED_HEIGHT_INCHES
            if figure_kind == "segment"
            else SEGMENT_TEMPORAL_CORRECTION_FOOTER_ADDED_HEIGHT_INCHES
        )
        assert baseline_figure.get_figheight() == pytest.approx(
            SEGMENT_FIGURE_BASE_HEIGHT_INCHES
        )
        assert corrected_figure.get_figheight() == pytest.approx(
            SEGMENT_FIGURE_BASE_HEIGHT_INCHES
            + expected_added_height_inches
        )
        assert corrected_figure.get_figwidth() == pytest.approx(
            baseline_figure.get_figwidth()
        )

        baseline_figure.canvas.draw()
        corrected_figure.canvas.draw()
        assert len(corrected_figure.axes) == len(baseline_figure.axes)
        added_height_pixels = (
            expected_added_height_inches * corrected_figure.dpi
        )
        for corrected_axis, baseline_axis in zip(
            corrected_figure.axes,
            baseline_figure.axes,
        ):
            corrected_bounds = corrected_axis.get_window_extent()
            baseline_bounds = baseline_axis.get_window_extent()
            assert corrected_bounds.x0 == pytest.approx(baseline_bounds.x0)
            assert corrected_bounds.width == pytest.approx(
                baseline_bounds.width
            )
            assert corrected_bounds.height == pytest.approx(
                baseline_bounds.height
            )
            assert corrected_bounds.y0 == pytest.approx(
                baseline_bounds.y0 + added_height_pixels
            )

        corrected_renderer = corrected_figure.canvas.get_renderer()
        correction_notice = next(
            artist
            for artist in corrected_figure.texts
            if artist.get_gid() == "reference-snr-correction-notice"
        )
        correction_bounds = correction_notice.get_window_extent(
            corrected_renderer
        )
        version_notice = next(
            artist
            for artist in corrected_figure.texts
            if artist.get_text().startswith("WSPRadar.org ")
        )
        version_bounds = version_notice.get_window_extent(corrected_renderer)
        assert correction_bounds.y0 >= 0.0
        assert correction_bounds.y1 <= corrected_figure.bbox.y1
        assert version_bounds.y0 >= 0.0
        assert version_bounds.y1 <= corrected_figure.bbox.y1
        assert correction_bounds.x1 < version_bounds.x0
        plot_content_bottom = min(
            axis.get_tightbbox(corrected_renderer).y0
            for axis in corrected_figure.axes
        )
        assert max(correction_bounds.y1, version_bounds.y1) + 4.0 <= (
            plot_content_bottom
        )
    finally:
        dispose_matplotlib_figure(corrected_figure)
        dispose_matplotlib_figure(baseline_figure)


@pytest.mark.parametrize(
    "figure_kind",
    ["segment", "segment_temporal", "selected"],
)
def test_compare_delta_snr_figures_omit_empty_correction_footer(figure_kind):
    """Do not reserve a correction artist when the completed run has no notice."""
    figure, recipe = _render_correction_footer_figure(figure_kind, "")
    try:
        assert recipe["reference_snr_correction_notice"] == ""
        assert figure.get_figheight() == pytest.approx(
            SEGMENT_FIGURE_BASE_HEIGHT_INCHES
        )
        assert figure.subplotpars.bottom == pytest.approx(
            SEGMENT_FIGURE_BOTTOM
        )
        expected_top = (
            0.80
            if figure_kind == "segment"
            else SEGMENT_TEMPORAL_FIGURE_TOP
        )
        expected_title_y = 0.98 if figure_kind == "segment" else 0.96
        assert figure.subplotpars.top == pytest.approx(expected_top)
        assert figure._suptitle.get_position()[1] == pytest.approx(
            expected_title_y
        )
        version_notices = [
            artist
            for artist in figure.texts
            if artist.get_text().startswith("WSPRadar.org ")
        ]
        assert len(version_notices) == 1
        assert version_notices[0].get_position()[1] == pytest.approx(
            SEGMENT_FIGURE_FOOTER_Y
        )
        assert not [
            artist
            for artist in figure.texts
            if artist.get_gid() == "reference-snr-correction-notice"
        ]
    finally:
        dispose_matplotlib_figure(figure)


def _render_compare_evidence_figure(metric_values, identity_labels):
    """Render one Benchmark selected-station recipe from exact evidence rows."""
    plot_df = pd.DataFrame(
        {
            "identity": identity_labels,
            "plot_time": pd.date_range(
                "2026-07-01T00:00:00Z",
                periods=len(metric_values),
                freq="12h",
            ),
            "metric": metric_values,
        }
    )
    recipe = _localized_selected_evidence_recipe(
        plot_df,
        "Selected Station Evidence",
        "3h",

    )
    assert recipe["kind"] == "selected_benchmark_temporal"
    assert "temporal_view" not in recipe
    return render_selected_evidence_export_figure(recipe)


@pytest.mark.parametrize("language", ["en", "de"])
def test_selected_single_evidence_uses_localized_recipe_labels(language):
    """Render sparse selected evidence through the localized temporal layout."""
    translations = T[language]
    plot_df = pd.DataFrame(
        {
            "identity": ["A (AA00)"],
            "plot_time": pd.to_datetime(
                ["2026-07-01T00:05:00Z"],
                utc=True,
            ),
            "metric": [1.5],
        }
    )
    recipe = _localized_selected_evidence_recipe(
        plot_df,
        "Localized Selected Evidence",
        "3h",
        language=language,
    )

    figure = render_selected_evidence_export_figure(recipe)
    try:
        chronological_axis, folded_axis, colorbar_axis = figure.axes
        assert chronological_axis.get_gid() == (
            "compare-temporal-chronological-axis"
        )
        assert chronological_axis.get_title() == translations[
            "fig_selected_compare_chronological_title"
        ]
        _assert_no_selected_compare_subtitles(figure)
        assert chronological_axis.get_xlabel() == translations[
            "fig_segment_chronological_x"
        ]
        assert chronological_axis.get_ylabel() == translations[
            "fig_compare_median_focus_axis"
        ]
        assert colorbar_axis.get_gid() == "compare-temporal-colorbar-axis"
        assert colorbar_axis.get_ylabel() == translations[
            "fig_relative_joint_spot_density"
        ]
        assert folded_axis.get_gid() == "compare-temporal-folded-axis"
        assert folded_axis.get_title() == translations[
            "fig_selected_compare_folded_title"
        ]
        _assert_folded_unavailable_annotation(
            figure,
            folded_axis,
            translations["fig_segment_folded_unavailable"],
        )
        assert not any(
            isinstance(collection, QuadMesh)
            for collection in folded_axis.collections
        )
        assert not any(
            "Distribution" in axis.get_title()
            or "Verteilung" in axis.get_title()
            for axis in figure.axes
        )
    finally:
        dispose_matplotlib_figure(figure)


def _legend_texts(axis):
    """Return the text visible in an axis legend."""
    legend = axis.get_legend()
    assert legend is not None
    return [text_artist.get_text() for text_artist in legend.get_texts()]


def _lines_with_gid(axis, gid):
    """Return lines tagged as one temporal reference-guide class."""
    return [line_artist for line_artist in axis.lines if line_artist.get_gid() == gid]


def _collections_with_gid(axis, gid):
    """Return collections tagged as one temporal evidence-overlay class."""
    return [
        collection
        for collection in axis.collections
        if collection.get_gid() == gid
    ]


def _legend_handles_with_gid(axis, gid):
    """Return legend proxy artists tagged as one visual-summary class."""
    legend = axis.get_legend()
    assert legend is not None
    return [
        legend_handle
        for legend_handle in legend.legend_handles
        if legend_handle.get_gid() == gid
    ]


def _formatted_y_ticks(axis):
    """Return the active major y-tick labels without requiring a GUI canvas."""
    formatter = axis.yaxis.get_major_formatter()
    return [formatter(tick_value, index) for index, tick_value in enumerate(axis.get_yticks())]


def _texts_with_gid(axis, gid):
    """Return axis text artists tagged as one visual-summary class."""
    return [text_artist for text_artist in axis.texts if text_artist.get_gid() == gid]


def _assert_no_selected_compare_subtitles(figure):
    """Keep selected Benchmark panels free of redundant subtitle artists."""
    subtitle_gids = {
        "compare-temporal-chronological-subtitle",
        "compare-temporal-folded-subtitle",
    }
    assert not [
        text_artist
        for axis in figure.axes
        for text_artist in axis.texts
        if text_artist.get_gid() in subtitle_gids
    ]


def _assert_folded_unavailable_annotation(figure, axis, source_text):
    """Verify the shared three-line foreground notice remains inside its panel."""
    annotations = _texts_with_gid(
        axis,
        "folded-utc-unavailable-annotation",
    )
    assert len(annotations) == 1
    annotation = annotations[0]
    rendered_lines = annotation.get_text().splitlines()
    assert len(rendered_lines) == 3
    rendered_message = " ".join(rendered_lines).casefold()
    source_message = " ".join(source_text.replace(" - ", " ").split()).casefold()
    assert rendered_message == source_message
    assert annotation.get_color() == "white"
    assert annotation.get_fontsize() == pytest.approx(9.0)
    assert annotation.get_fontweight() == "normal"
    assert annotation.get_zorder() == pytest.approx(10.0)

    background = annotation.get_bbox_patch()
    assert background is not None
    assert background.get_facecolor() == pytest.approx(to_rgba("black"))
    assert background.get_alpha() == pytest.approx(1.0)

    figure.canvas.draw()
    renderer = figure.canvas.get_renderer()
    axis_bounds = axis.get_window_extent(renderer)
    background_bounds = background.get_window_extent(renderer)
    assert background_bounds.x0 >= axis_bounds.x0
    assert background_bounds.x1 <= axis_bounds.x1
    assert background_bounds.y0 >= axis_bounds.y0
    assert background_bounds.y1 <= axis_bounds.y1


def _assert_legend_keys_precede_text(figure, axis):
    """Verify conventional key-first layout after Matplotlib resolves geometry."""
    figure.canvas.draw()
    renderer = figure.canvas.get_renderer()
    legend = axis.get_legend()
    assert legend is not None
    assert len(legend.legend_handles) == len(legend.get_texts())
    for legend_handle, legend_text in zip(
        legend.legend_handles,
        legend.get_texts(),
    ):
        assert (
            legend_handle.get_window_extent(renderer).x1
            < legend_text.get_window_extent(renderer).x0
        )


def test_compare_median_focus_scale_uses_absolute_ham_radio_ticks_and_round_trips():
    """Center on the exact median while labelling equal focus anchors in raw dB."""
    metric_values = [-24, -14, -4, 0, 3, 6, 9, 12, 16, 26, 36]
    focus_spec = _build_compare_median_focus_spec(metric_values)

    assert focus_spec.median_db == pytest.approx(6.0)
    assert focus_spec.anchor_offsets_db[:7] == pytest.approx(
        [0.0, 3.0, 6.0, 10.0, 20.0, 30.0, 60.0]
    )
    assert focus_spec.tick_values_db == pytest.approx(metric_values)

    transformed_ticks = _compare_median_focus_forward(
        focus_spec.tick_values_db,
        focus_spec,
    )
    assert transformed_ticks == pytest.approx(np.arange(-5.0, 6.0))
    restored_values = _compare_median_focus_inverse(
        transformed_ticks,
        focus_spec,
    )
    assert restored_values == pytest.approx(metric_values)


def test_compare_median_focus_scale_uses_tight_profile_within_ten_db():
    """Reveal 1 dB structure only when the full required range is genuinely tight."""
    focus_spec = _build_compare_median_focus_spec([4.0, 5.0, 6.0, 7.0, 8.0])

    assert focus_spec.median_db == pytest.approx(6.0)
    assert focus_spec.anchor_offsets_db[:6] == pytest.approx(
        [0.0, 1.0, 3.0, 6.0, 10.0, 20.0]
    )
    assert focus_spec.tick_values_db == pytest.approx(
        [0.0, 3.0, 5.0, 6.0, 7.0, 9.0, 12.0]
    )


def test_compare_median_focus_rejects_unordered_retained_tick_offsets():
    """Derive a safe scale when retained presentation metadata is malformed."""
    focus_spec = _compare_median_focus_spec_from_recipe(
        {
            "median_db": 99.0,
            "anchor_offsets_db": [0.0, 3.0, 6.0, 10.0],
            "labelled_offsets_db": [0.0, 6.0, 3.0],
            "half_span_db": 10.0,
        },
        [1.0, 2.0, 3.0],
    )

    assert focus_spec.median_db == pytest.approx(2.0)
    assert focus_spec.labelled_offsets_db == pytest.approx(
        [0.0, 1.0, 3.0, 6.0, 10.0]
    )


def test_segment_and_selected_recipes_keep_their_own_evidence_medians():
    """Center each two-panel evidence scope without borrowing the other median."""
    segment_plot_df = pd.DataFrame(
        {
            "plot_time": pd.date_range(
                "2026-07-01T00:00:00Z",
                periods=5,
                freq="3h",
            ),
            "metric": [0.0, 3.0, 6.0, 9.0, 12.0],
        }
    )
    selected_plot_df = pd.DataFrame(
        {
            "identity": ["A (AA00)"] * 3,
            "plot_time": pd.date_range(
                "2026-07-01T00:00:00Z",
                periods=3,
                freq="3h",
            ),
            "metric": [1.0, 2.0, 3.0],
        }
    )

    segment_recipe = _localized_segment_temporal_recipe(
        segment_plot_df,
        "Segment Evidence",
        "3h",
        "Joint spot count",
    )
    selected_recipe = _localized_selected_evidence_recipe(
        selected_plot_df,
        "Selected Evidence",
        "3h",

    )

    assert segment_recipe["median_focus"]["median_db"] == pytest.approx(6.0)
    assert selected_recipe["median_focus"]["median_db"] == pytest.approx(2.0)
    assert "stability_interval" not in selected_recipe


def test_selected_compare_recipe_retires_histogram_and_temporal_view_state():
    """Store one dual-panel temporal recipe without retired distribution state."""
    plot_df = pd.DataFrame(
        {
            "identity": ["A (AA00)"] * 4,
            "plot_time": pd.to_datetime(
                [
                    "2026-07-01T00:05:00Z",
                    "2026-07-01T03:05:00Z",
                    "2026-07-02T00:05:00Z",
                    "2026-07-02T03:05:00Z",
                ],
                utc=True,
            ),
            "metric": [-2.0, 1.0, 2.0, 3.0],
        }
    )

    recipe = _localized_selected_evidence_recipe(
        plot_df,
        "Selected Station Evidence",
        "6h",
    )

    assert recipe["kind"] == "selected_benchmark_temporal"
    assert recipe["time_bin"] == "6h"
    assert recipe["chronological_title"] == "\u0394 SNR over Time"
    assert recipe["chronological_subtitle"] is None
    assert recipe["folded_title"] == "\u0394 SNR by UTC Hour"
    assert recipe["folded_subtitle"] is None
    assert recipe["show_folded_date_annotation"] is False
    assert recipe["selected_identity_count"] == 1
    assert len(recipe["plot_time_ns"]) == len(plot_df)
    np.testing.assert_allclose(recipe["metric"], plot_df["metric"])
    for retired_field in (
        "temporal_view",
        "labels",
        "distribution",
        "histogram",
        "mean_label",
        "share_axis_label",
        "omit_folded_when_unavailable",
    ):
        assert retired_field not in recipe


def test_selected_compare_recipe_prepares_every_interactive_time_bin():
    """Keep selected-station bin changes independent of retained evidence rows."""
    plot_df = pd.DataFrame(
        {
            "identity": ["A (AA00)"] * 4,
            "plot_time": pd.to_datetime(
                [
                    "2026-07-01T00:05:00Z",
                    "2026-07-01T03:05:00Z",
                    "2026-07-02T00:05:00Z",
                    "2026-07-02T03:05:00Z",
                ],
                utc=True,
            ),
            "metric": [-2.0, 1.0, 2.0, 3.0],
        }
    )
    recipe = _localized_selected_evidence_recipe(
        plot_df,
        "Selected Station Evidence",
        "1h",
        time_bin_options=("1h", "3h"),
    )

    assert set(recipe["prepared_profiles"]["chronological"]) == {"1h", "3h"}
    assert "plot_time_ns" not in recipe
    assert "metric" not in recipe

    render_recipe = dict(recipe)
    render_recipe["time_bin"] = "3h"
    figure = render_selected_evidence_export_figure(render_recipe)
    try:
        assert figure is not None
        assert len(figure.axes) == 3
    finally:
        dispose_matplotlib_figure(figure)


def test_selected_compare_panels_center_on_selected_median_with_absolute_ticks():
    """Use the pooled selected evidence median for both selected-station panels."""
    metric_values = [-24, -14, -4, 0, 3, 6, 9, 12, 16, 26, 36]
    plot_df = pd.DataFrame(
        {
            "identity": ["A (AA00)"] * len(metric_values),
            "plot_time": pd.date_range(
                "2026-07-01T00:00:00Z",
                periods=len(metric_values),
                freq="12h",
            ),
            "metric": metric_values,
        }
    )
    recipe = _localized_selected_evidence_recipe(
        plot_df,
        "Selected Evidence",
        "3h",

    )

    assert recipe["median_focus"]["median_db"] == pytest.approx(6.0)
    figure = render_selected_evidence_export_figure(recipe)
    try:
        chronological_axis, folded_axis, colorbar_axis = figure.axes
        expected_tick_labels = [
            "−24",
            "−14",
            "−4",
            "0",
            "+3",
            "+6",
            "+9",
            "+12",
            "+16",
            "+26",
            "+36",
        ]

        for axis in (chronological_axis, folded_axis):
            assert axis.get_yscale() == "function"
            assert _formatted_y_ticks(axis) == expected_tick_labels
            assert axis.get_ylabel() == (
                "\u0394 SNR (dB \u00b7 median-centered nonlinear)"
            )
            assert not _lines_with_gid(axis, "compare-temporal-zero-line")
            assert not _lines_with_gid(
                axis,
                "compare-temporal-zero-understroke",
            )
            assert not _texts_with_gid(axis, "compare-temporal-zero-label")
            _assert_legend_keys_precede_text(figure, axis)
            assert not _texts_with_gid(axis, "compare-median-focus-note")
            assert not axis.patches
        assert _legend_texts(chronological_axis) == [
            "Median +6.0 dB",
            "Bin median",
        ]
        assert _legend_texts(folded_axis) == [
            "Median +6.0 dB",
            "Bin median",
        ]
        assert not _lines_with_gid(folded_axis, "temporal-bin-iqr-q1")
        assert not _lines_with_gid(folded_axis, "temporal-bin-iqr-q3")
        assert chronological_axis.get_ylim() == pytest.approx(
            folded_axis.get_ylim()
        )
        assert colorbar_axis.get_gid() == "compare-temporal-colorbar-axis"
        assert all(
            "Distribution" not in axis.get_title()
            for axis in (chronological_axis, folded_axis)
        )
    finally:
        dispose_matplotlib_figure(figure)


def test_selected_compare_omits_separate_zero_reference_and_median_tick_suffix():
    """Use plain absolute ticks without a separate boxed zero reference."""
    figure = _render_compare_evidence_figure(
        [4.5, 5.5, 5.5, 6.5],
        ["A (AA00)"] * 4,
    )

    try:
        chronological_axis, folded_axis = figure.axes[:2]
        for axis in (chronological_axis, folded_axis):
            assert "+5.5" in _formatted_y_ticks(axis)
            assert "0" not in _formatted_y_ticks(axis)
            assert not _lines_with_gid(axis, "compare-temporal-zero-line")
            assert not _lines_with_gid(
                axis,
                "compare-temporal-zero-understroke",
            )
            assert not _texts_with_gid(axis, "compare-temporal-zero-label")
    finally:
        dispose_matplotlib_figure(figure)


def test_selected_time_heatmap_uses_panel_max_relative_density():
    """Scale raw cell counts to the densest cell while keeping a fixed color norm."""
    plot_df = pd.DataFrame(
        {
            "identity": ["A (AA00)"] * 3,
            "plot_time": pd.to_datetime(
                [
                    "2026-07-01T00:05:00Z",
                    "2026-07-01T00:10:00Z",
                    "2026-07-01T01:05:00Z",
                ],
                utc=True,
            ),
            "metric": [1.0, 1.0, 2.0],
        }
    )
    recipe = _localized_selected_evidence_recipe(
        plot_df,
        "Selected Evidence",
        "1h",

    )

    figure = render_selected_evidence_export_figure(recipe)
    try:
        chronological_axis = figure.axes[0]
        density_mesh = next(
            collection
            for collection in chronological_axis.collections
            if isinstance(collection, QuadMesh)
        )
        density_values = np.ma.asarray(density_mesh.get_array()).compressed()

        assert sorted(np.unique(density_values)) == pytest.approx([50.0, 100.0])
        assert density_mesh.norm.vmin == pytest.approx(0.0)
        assert density_mesh.norm.vmax == pytest.approx(100.0)
        assert figure.axes[-1].get_ylabel() == (
            "Relative joint-spot density (% of panel maximum)"
        )
        assert chronological_axis.get_gid() == (
            "compare-temporal-chronological-axis"
        )
        assert all(
            "Distribution" not in axis.get_title()
            for axis in figure.axes
        )
    finally:
        dispose_matplotlib_figure(figure)


def test_selected_compare_can_render_folded_utc_hour_density():
    """Render chronology and raw-row UTC-hour density in one shared layout."""
    plot_df = pd.DataFrame(
        {
            "identity": ["A (AA00)"] * 4,
            "plot_time": pd.to_datetime(
                [
                    "2026-07-01T00:05:00Z",
                    "2026-07-01T00:05:00Z",
                    "2026-07-01T03:05:00Z",
                    "2026-07-02T00:05:00Z",
                ],
                utc=True,
            ),
            "metric": [0.0, 0.0, 1.0, 0.0],
        }
    )
    recipe = _localized_selected_evidence_recipe(
        plot_df,
        "Selected Folded Evidence",
        "3h",

        folded_title="UTC profile",
        folded_x_label="UTC clock hour",
        density_label="Relative selected density",
    )

    assert recipe["utc_date_count"] == 2
    assert recipe["folded_title"] == "UTC profile"
    assert isinstance(recipe["plot_time_ns"], np.ndarray)
    assert isinstance(recipe["metric"], np.ndarray)

    figure = render_selected_evidence_export_figure(recipe)
    try:
        assert tuple(figure.get_size_inches()) == pytest.approx((13.0, 5.6))
        assert figure.subplotpars.left == pytest.approx(0.07)
        assert figure.subplotpars.right == pytest.approx(0.95)
        assert figure.subplotpars.bottom == pytest.approx(0.15)
        assert figure.subplotpars.top == pytest.approx(0.82)
        assert figure.subplotpars.wspace == pytest.approx(0.20)
        assert len(figure.axes) == 3
        chronological_axis, folded_axis, colorbar_axis = figure.axes
        chronological_mesh = next(
            collection
            for collection in chronological_axis.collections
            if isinstance(collection, QuadMesh)
        )
        folded_mesh = next(
            collection
            for collection in folded_axis.collections
            if isinstance(collection, QuadMesh)
        )
        chronological_density = np.ma.asarray(
            chronological_mesh.get_array()
        ).compressed()
        folded_density = np.ma.asarray(folded_mesh.get_array()).compressed()

        assert not chronological_axis.patches
        assert not folded_axis.patches
        assert sorted(np.unique(chronological_density)) == pytest.approx(
            [50.0, 100.0]
        )
        # Every selected Joint Spot remains one folded observation. The two
        # duplicate rows in the first UTC-hour cell are not reduced to one
        # date-hour median as they are in Performance selected-SNR evidence.
        assert sorted(np.unique(folded_density)) == pytest.approx(
            [100.0 / 3.0, 100.0]
        )
        assert folded_mesh.norm.vmin == pytest.approx(0.0)
        assert folded_mesh.norm.vmax == pytest.approx(100.0)
        assert folded_mesh.get_coordinates().shape[1] == 25
        assert folded_axis.get_xlim() == pytest.approx((0.0, 24.0))
        assert folded_axis.get_title() == "UTC profile"
        assert folded_axis.get_xlabel() == "UTC clock hour"
        assert "2 UTC dates folded" not in {
            text.get_text() for text in folded_axis.texts
        }
        assert colorbar_axis.get_ylabel() == "Relative selected density"
        assert colorbar_axis.get_gid() == "compare-temporal-colorbar-axis"
        assert chronological_axis.get_gid() == (
            "compare-temporal-chronological-axis"
        )
        assert folded_axis.get_gid() == "compare-temporal-folded-axis"
        _assert_no_selected_compare_subtitles(figure)
        assert (
            chronological_axis.get_position().width
            / folded_axis.get_position().width
        ) == pytest.approx(1.95)
        assert chronological_axis.get_ylim() == pytest.approx(
            folded_axis.get_ylim()
        )
    finally:
        dispose_matplotlib_figure(figure)


def test_selected_compare_bin_changes_chronology_but_not_fixed_utc_hour_fold():
    """Apply the selected bin only on the left while keeping 24 one-hour slots."""
    plot_df = pd.DataFrame(
        {
            "identity": ["A (AA00)"] * 8,
            "plot_time": pd.to_datetime(
                [
                    "2026-07-01T00:05:00Z",
                    "2026-07-01T01:05:00Z",
                    "2026-07-01T06:05:00Z",
                    "2026-07-01T07:05:00Z",
                    "2026-07-02T00:05:00Z",
                    "2026-07-02T01:05:00Z",
                    "2026-07-02T06:05:00Z",
                    "2026-07-02T07:05:00Z",
                ],
                utc=True,
            ),
            "metric": [-2.0, -1.0, 1.0, 2.0, -1.0, 0.0, 2.0, 3.0],
        }
    )
    one_hour_recipe = _localized_selected_evidence_recipe(
        plot_df,
        "Selected Evidence",
        "1h",
    )
    six_hour_recipe = _localized_selected_evidence_recipe(
        plot_df,
        "Selected Evidence",
        "6h",
    )
    one_hour_figure = render_selected_evidence_export_figure(
        one_hour_recipe
    )
    six_hour_figure = render_selected_evidence_export_figure(
        six_hour_recipe
    )
    try:
        one_hour_chronological, one_hour_folded = one_hour_figure.axes[:2]
        six_hour_chronological, six_hour_folded = six_hour_figure.axes[:2]
        one_hour_chronological_mesh = next(
            collection
            for collection in one_hour_chronological.collections
            if isinstance(collection, QuadMesh)
        )
        six_hour_chronological_mesh = next(
            collection
            for collection in six_hour_chronological.collections
            if isinstance(collection, QuadMesh)
        )
        one_hour_folded_mesh = next(
            collection
            for collection in one_hour_folded.collections
            if isinstance(collection, QuadMesh)
        )
        six_hour_folded_mesh = next(
            collection
            for collection in six_hour_folded.collections
            if isinstance(collection, QuadMesh)
        )

        assert (
            one_hour_chronological_mesh.get_coordinates().shape[1]
            > six_hour_chronological_mesh.get_coordinates().shape[1]
        )
        np.testing.assert_allclose(
            np.ma.filled(one_hour_folded_mesh.get_array(), np.nan),
            np.ma.filled(six_hour_folded_mesh.get_array(), np.nan),
            equal_nan=True,
        )
        assert one_hour_folded_mesh.get_coordinates().shape[1] == 25
        assert six_hour_folded_mesh.get_coordinates().shape[1] == 25
        assert one_hour_folded.get_xlim() == pytest.approx((0.0, 24.0))
        assert six_hour_folded.get_xlim() == pytest.approx((0.0, 24.0))
        _assert_no_selected_compare_subtitles(one_hour_figure)
        _assert_no_selected_compare_subtitles(six_hour_figure)
    finally:
        dispose_matplotlib_figure(one_hour_figure)
        dispose_matplotlib_figure(six_hour_figure)


def test_selected_folded_view_uses_localized_placeholder_below_two_dates():
    """Keep the folded panel and show its notice below two UTC dates."""
    plot_df = pd.DataFrame(
        {
            "identity": ["A (AA00)"] * 3,
            "plot_time": pd.to_datetime(
                [
                    "2026-07-01T00:05:00Z",
                    "2026-07-01T03:05:00Z",
                    "2026-07-01T06:05:00Z",
                ],
                utc=True,
            ),
            "metric": [0.0, 1.0, 2.0],
        }
    )
    placeholder = T["de"]["fig_segment_folded_unavailable"]
    recipe = _localized_selected_evidence_recipe(
        plot_df,
        "Selected Folded Evidence",
        "3h",

        folded_title="UTC-Profil",
        folded_x_label="UTC-Stunde",
        folded_unavailable_text=placeholder,
    )

    figure = render_selected_evidence_export_figure(recipe)
    try:
        assert len(figure.axes) == 3
        chronological_axis, folded_axis, colorbar_axis = figure.axes

        assert any(
            isinstance(collection, QuadMesh)
            for collection in chronological_axis.collections
        )
        assert chronological_axis.get_gid() == (
            "compare-temporal-chronological-axis"
        )
        assert folded_axis.get_gid() == "compare-temporal-folded-axis"
        assert not any(
            isinstance(collection, QuadMesh)
            for collection in folded_axis.collections
        )
        assert (
            chronological_axis.get_position().width
            / folded_axis.get_position().width
        ) == pytest.approx(1.95)
        assert not _texts_with_gid(
            chronological_axis,
            "folded-utc-unavailable-annotation",
        )
        _assert_folded_unavailable_annotation(
            figure,
            folded_axis,
            placeholder,
        )
        assert chronological_axis.get_title() == (
            T["en"]["fig_selected_compare_chronological_title"]
        )
        assert folded_axis.get_title() == "UTC-Profil"
        _assert_no_selected_compare_subtitles(figure)
        assert colorbar_axis.get_gid() == "compare-temporal-colorbar-axis"
        assert colorbar_axis.get_ylabel() == (
            "Relative joint-spot density (% of panel maximum)"
        )
    finally:
        dispose_matplotlib_figure(figure)


@pytest.mark.parametrize(
    ("axis_index", "axis_gid"),
    (
        (0, "compare-temporal-chronological-axis"),
        (1, "compare-temporal-folded-axis"),
    ),
)
def test_selected_compare_dual_panels_share_guide_and_median_hierarchy(
    axis_index,
    axis_gid,
):
    """Keep both simultaneous panels' guides beneath temporal median markers."""
    plot_df = pd.DataFrame(
        {
            "identity": ["A (AA00)"] * 4,
            "plot_time": pd.to_datetime(
                [
                    "2026-07-01T00:05:00Z",
                    "2026-07-01T03:05:00Z",
                    "2026-07-02T00:05:00Z",
                    "2026-07-02T03:05:00Z",
                ],
                utc=True,
            ),
            "metric": [-12.0, -6.0, 6.0, 12.0],
        }
    )
    recipe = _localized_selected_evidence_recipe(
        plot_df,
        "Selected Evidence",
        "3h",

    )

    figure = render_selected_evidence_export_figure(recipe)
    try:
        temporal_axis = figure.axes[axis_index]
        assert temporal_axis.get_gid() == axis_gid
        focus_guides = _lines_with_gid(
            temporal_axis,
            "compare-median-focus-guide",
        )
        zero_understrokes = _lines_with_gid(
            temporal_axis,
            "compare-temporal-zero-understroke",
        )
        zero_lines = _lines_with_gid(
            temporal_axis,
            "compare-temporal-zero-line",
        )
        median_lines = _lines_with_gid(
            temporal_axis,
            "compare-median-focus-center",
        )

        assert sorted(float(line.get_ydata()[0]) for line in focus_guides) == [
            -20.0,
            -10.0,
            -6.0,
            -3.0,
            3.0,
            6.0,
            10.0,
            20.0,
        ]
        assert not zero_understrokes
        assert not zero_lines
        assert len(median_lines) == 1
        for guide_line in focus_guides:
            assert guide_line.get_color() == "#d0d0d0"
            assert guide_line.get_linewidth() == pytest.approx(0.9)
            assert guide_line.get_alpha() == pytest.approx(0.42)
            assert guide_line.get_zorder() == pytest.approx(2.6)
        assert temporal_axis.get_yscale() == "function"
        assert _formatted_y_ticks(temporal_axis) == [
            "−20",
            "−10",
            "−6",
            "−3",
            "0",
            "+3",
            "+6",
            "+10",
            "+20",
        ]
        assert median_lines[0].get_color() == "red"
        assert median_lines[0].get_linestyle() == "--"
        assert median_lines[0].get_linewidth() == pytest.approx(1.0)
        assert median_lines[0].get_alpha() == pytest.approx(1.0)
        assert median_lines[0].get_zorder() == pytest.approx(3.2)
        assert _legend_texts(temporal_axis) == ["Median +0.0 dB", "Bin median"]
        temporal_legend = temporal_axis.get_legend()
        assert temporal_legend.get_zorder() == pytest.approx(10.0)
        assert temporal_legend.legend_handles[1].get_facecolors()[0] == pytest.approx(
            to_rgba("#c8f4ff")
        )
        assert temporal_legend.legend_handles[1].get_edgecolors()[0] == pytest.approx(
            to_rgba("#00384d")
        )
        assert {
            text.get_fontsize() for text in temporal_legend.get_texts()
        } == {8.0}
        _assert_legend_keys_precede_text(figure, temporal_axis)
        assert max(
            line.get_zorder()
            for line in [
                *focus_guides,
                *median_lines,
            ]
        ) < 4.0
        assert not any(gridline.get_visible() for gridline in temporal_axis.get_ygridlines())
    finally:
        dispose_matplotlib_figure(figure)


def _compare_temporal_iqr_gap_rows():
    """Return fractional raw evidence with supported rail runs around a gap."""
    first_bin_values = [0.11, 0.21, 0.31, 0.41, 2.51]
    second_bin_values = [1.11, 1.21, 1.31, 1.41, 3.51]
    gap_bin_values = [8.11, 8.21, 8.31, 8.41]
    fourth_bin_values = [4.05, 4.15, 4.25, 4.35, 7.45]
    fifth_bin_values = [5.05, 5.15, 5.25, 5.35, 8.45]
    timestamps = (
        ["2026-07-01T00:05:00Z"] * len(first_bin_values)
        + ["2026-07-01T03:05:00Z"] * len(second_bin_values)
        + ["2026-07-01T06:05:00Z"] * len(gap_bin_values)
        + ["2026-07-01T09:05:00Z"] * len(fourth_bin_values)
        + ["2026-07-01T12:05:00Z"] * len(fifth_bin_values)
        + ["2026-07-02T12:05:00Z"]
    )
    metric_values = (
        first_bin_values
        + second_bin_values
        + gap_bin_values
        + fourth_bin_values
        + fifth_bin_values
        + [1.25]
    )
    return pd.DataFrame(
        {
            "identity": ["A (AA00)"] * len(metric_values),
            "plot_time": pd.to_datetime(timestamps, utc=True),
            "metric": metric_values,
        }
    )


@pytest.mark.parametrize("scope", ["segment", "selected"])
def test_compare_temporal_iqr_uses_raw_quartiles_and_breaks_at_unsupported_bins(
    scope,
    monkeypatch,
):
    """Share one supported IQR band without bridging a four-value bin."""
    plot_df = _compare_temporal_iqr_gap_rows()
    if scope == "segment":
        recipe = _localized_segment_temporal_recipe(
            plot_df,
            "Segment temporal IQR",
            "3h",
        )
        figure = render_segment_temporal_evidence_export_figure(recipe)
    else:
        recipe = _localized_selected_evidence_recipe(
            plot_df,
            "Selected temporal IQR",
            "3h",
        )
        figure = render_selected_evidence_export_figure(recipe)

    try:
        chronological_axis = figure.axes[0]
        q1_lines = _lines_with_gid(chronological_axis, "temporal-bin-iqr-q1")
        q3_lines = _lines_with_gid(chronological_axis, "temporal-bin-iqr-q3")
        iqr_bands = _collections_with_gid(
            chronological_axis,
            "temporal-bin-iqr-band",
        )
        assert len(q1_lines) == len(q3_lines) == len(iqr_bands) == 1
        iqr_band = iqr_bands[0]
        q1_values = np.asarray(q1_lines[0].get_ydata(), dtype=float)
        q3_values = np.asarray(q3_lines[0].get_ydata(), dtype=float)
        assert np.flatnonzero(np.isfinite(q1_values)).tolist() == [0, 1, 3, 4]
        assert np.flatnonzero(np.isfinite(q3_values)).tolist() == [0, 1, 3, 4]
        assert q1_values[[0, 1, 3, 4]] == pytest.approx(
            [0.21, 1.21, 4.15, 5.15]
        )
        assert q3_values[[0, 1, 3, 4]] == pytest.approx(
            [0.41, 1.41, 4.35, 5.35]
        )
        assert np.isnan(q1_values[2])
        assert np.isnan(q3_values[2])
        assert q1_lines[0].get_marker() == "None"
        assert q3_lines[0].get_marker() == "None"
        assert q1_lines[0].get_color() == TEMPORAL_IQR_COLOR
        assert q3_lines[0].get_linewidth() == pytest.approx(0.68)
        assert q3_lines[0].get_zorder() < 4.0
        assert len(iqr_band.get_paths()) == 2
        assert iqr_band.get_label() == "Bin IQR (middle 50%)"
        assert iqr_band.get_alpha() == pytest.approx(
            TEMPORAL_IQR_BAND_ALPHA
        )
        assert iqr_band.get_facecolors()[0] == pytest.approx(
            to_rgba(TEMPORAL_IQR_COLOR, TEMPORAL_IQR_BAND_ALPHA)
        )
        assert iqr_band.get_zorder() < q1_lines[0].get_zorder()

        q1_understrokes = _lines_with_gid(
            chronological_axis,
            "temporal-bin-iqr-q1-understroke",
        )
        q3_understrokes = _lines_with_gid(
            chronological_axis,
            "temporal-bin-iqr-q3-understroke",
        )
        assert len(q1_understrokes) == len(q3_understrokes) == 1
        assert q1_understrokes[0].get_color() == TEMPORAL_IQR_UNDERSTROKE_COLOR
        assert q1_understrokes[0].get_linewidth() > q1_lines[0].get_linewidth()
        assert q1_understrokes[0].get_marker() == "None"
        assert q3_understrokes[0].get_marker() == "None"

        legend_texts = _legend_texts(chronological_axis)
        assert legend_texts.count(recipe["bin_iqr_label"]) == 1
        assert legend_texts[-1] == recipe["bin_iqr_label"]
        iqr_legend_handles = _legend_handles_with_gid(
            chronological_axis,
            "temporal-bin-iqr-band-legend",
        )
        assert len(iqr_legend_handles) == 1
        iqr_legend_handle = iqr_legend_handles[0]
        assert iqr_legend_handle.get_facecolor() == pytest.approx(
            to_rgba(TEMPORAL_IQR_COLOR, TEMPORAL_IQR_BAND_ALPHA)
        )
        assert iqr_legend_handle.get_edgecolor() == pytest.approx(
            to_rgba(TEMPORAL_IQR_COLOR)
        )
        assert iqr_legend_handle.get_linewidth() == pytest.approx(0.68)
        median_markers = next(
            collection
            for collection in chronological_axis.collections
            if collection.get_gid() == "temporal-bin-median-markers"
        )
        assert median_markers.get_zorder() > q3_lines[0].get_zorder()

        median_reference = _lines_with_gid(
            chronological_axis,
            "compare-median-focus-center",
        )[0]

        def inspect_paper_style(image_buffer, **_save_options):
            """Assert paper styling uses a fine black band and boundary."""
            assert not q1_understrokes[0].get_visible()
            assert not q3_understrokes[0].get_visible()
            assert iqr_band.get_alpha() == pytest.approx(
                TEMPORAL_IQR_BAND_ALPHA
            )
            assert iqr_band.get_facecolors()[0] == pytest.approx(
                to_rgba("#111111", TEMPORAL_IQR_BAND_ALPHA)
            )
            assert iqr_legend_handle.get_facecolor() == pytest.approx(
                to_rgba("#111111", TEMPORAL_IQR_BAND_ALPHA)
            )
            assert iqr_legend_handle.get_edgecolor() == pytest.approx(
                to_rgba("#111111")
            )
            assert iqr_legend_handle.get_linewidth() == pytest.approx(0.4)
            for quartile_line in (q1_lines[0], q3_lines[0]):
                assert quartile_line.get_visible()
                assert quartile_line.get_color() == "#111111"
                assert quartile_line.get_linewidth() == pytest.approx(0.4)
                assert quartile_line.get_marker() == "None"
                assert (
                    quartile_line.get_linewidth()
                    < median_reference.get_linewidth()
                )
            image_buffer.write(b"paper-style")

        monkeypatch.setattr(figure, "savefig", inspect_paper_style)
        assert figure_to_png_bytes(figure, dpi=80) == b"paper-style"
        assert q1_understrokes[0].get_visible()
        assert q3_understrokes[0].get_visible()
        assert q1_lines[0].get_color() == TEMPORAL_IQR_COLOR
        assert q3_lines[0].get_color() == TEMPORAL_IQR_COLOR
        assert q1_lines[0].get_linewidth() == pytest.approx(0.68)
        assert q3_lines[0].get_linewidth() == pytest.approx(0.68)
        assert iqr_band.get_facecolors()[0] == pytest.approx(
            to_rgba(TEMPORAL_IQR_COLOR, TEMPORAL_IQR_BAND_ALPHA)
        )
        assert iqr_legend_handle.get_facecolor() == pytest.approx(
            to_rgba(TEMPORAL_IQR_COLOR, TEMPORAL_IQR_BAND_ALPHA)
        )
        assert iqr_legend_handle.get_edgecolor() == pytest.approx(
            to_rgba(TEMPORAL_IQR_COLOR)
        )
        assert iqr_legend_handle.get_linewidth() == pytest.approx(0.68)
    finally:
        dispose_matplotlib_figure(figure)


def test_compare_folded_iqr_pools_raw_rows_and_requires_a_rail_run():
    """Pool UTC-hour quartiles and omit an isolated chronological band."""
    plot_df = pd.DataFrame(
        {
            "identity": ["A (AA00)"] * 14,
            "plot_time": pd.to_datetime(
                [
                    "2026-07-01T00:05:00Z",
                    "2026-07-01T00:10:00Z",
                    "2026-07-01T00:15:00Z",
                    "2026-07-02T00:05:00Z",
                    "2026-07-02T00:10:00Z",
                    "2026-07-01T01:05:00Z",
                    "2026-07-01T01:10:00Z",
                    "2026-07-01T01:15:00Z",
                    "2026-07-02T01:05:00Z",
                    "2026-07-02T01:10:00Z",
                    "2026-07-01T03:05:00Z",
                    "2026-07-01T03:10:00Z",
                    "2026-07-02T03:05:00Z",
                    "2026-07-02T03:10:00Z",
                ],
                utc=True,
            ),
            "metric": [
                0.11,
                0.21,
                0.31,
                0.41,
                2.51,
                1.11,
                1.21,
                1.31,
                1.41,
                3.51,
                8.11,
                8.21,
                8.31,
                8.41,
            ],
        }
    )
    recipe = _localized_selected_evidence_recipe(
        plot_df,
        "Selected folded IQR",
        "3h",
    )
    figure = render_selected_evidence_export_figure(recipe)
    try:
        chronological_axis, folded_axis = figure.axes[:2]
        assert not _lines_with_gid(chronological_axis, "temporal-bin-iqr-q1")
        assert not _collections_with_gid(
            chronological_axis,
            "temporal-bin-iqr-band",
        )
        assert recipe["bin_iqr_label"] not in _legend_texts(chronological_axis)

        folded_q1 = _lines_with_gid(folded_axis, "temporal-bin-iqr-q1")
        folded_q3 = _lines_with_gid(folded_axis, "temporal-bin-iqr-q3")
        assert len(folded_q1) == len(folded_q3) == 1
        q1_values = np.asarray(folded_q1[0].get_ydata(), dtype=float)
        q3_values = np.asarray(folded_q3[0].get_ydata(), dtype=float)
        assert np.flatnonzero(np.isfinite(q1_values)).tolist() == [0, 1]
        assert np.flatnonzero(np.isfinite(q3_values)).tolist() == [0, 1]
        assert q1_values[[0, 1]] == pytest.approx([0.21, 1.21])
        assert q3_values[[0, 1]] == pytest.approx([0.41, 1.41])
        assert np.isnan(q1_values[3])
        assert np.isnan(q3_values[3])
        assert folded_q1[0].get_marker() == "None"
        assert folded_q3[0].get_marker() == "None"
        folded_bands = _collections_with_gid(
            folded_axis,
            "temporal-bin-iqr-band",
        )
        assert len(folded_bands) == 1
        assert len(folded_bands[0].get_paths()) == 1
        assert _legend_texts(folded_axis).count(recipe["bin_iqr_label"]) == 1
    finally:
        dispose_matplotlib_figure(figure)


def test_compare_temporal_iqr_fails_closed_for_tampered_recipe_threshold():
    """Do not render quartile rails when recipe metadata relaxes the contract."""
    recipe = _localized_segment_temporal_recipe(
        _compare_temporal_iqr_gap_rows(),
        "Tampered temporal IQR",
        "3h",
    )
    recipe["iqr_min_count"] = TEMPORAL_IQR_MIN_COUNT - 1

    figure = render_segment_temporal_evidence_export_figure(recipe)
    try:
        for temporal_axis in figure.axes[:2]:
            assert not _lines_with_gid(temporal_axis, "temporal-bin-iqr-q1")
            assert not _collections_with_gid(
                temporal_axis,
                "temporal-bin-iqr-band",
            )
            assert recipe["bin_iqr_label"] not in _legend_texts(temporal_axis)
    finally:
        dispose_matplotlib_figure(figure)


def test_segment_benchmark_temporal_recipe_and_dual_density_figure():
    """Keep recipes compact and normalize chronological/folded panels separately."""
    plot_df = pd.DataFrame(
        {
            "plot_time": pd.to_datetime(
                [
                    "2026-07-01T00:05:00Z",
                    "2026-07-01T00:05:00Z",
                    "2026-07-01T03:05:00Z",
                    "2026-07-02T00:05:00Z",
                ],
                utc=True,
            ),
            "metric": [0.0, 0.0, 1.0, 0.0],
        }
    )
    recipe = _localized_segment_temporal_recipe(
        plot_df,
        "RX Benchmark Temporal: G3ZIL (Target) vs. G4HZX (Reference)",
        "3h",
        "Joint spot count",
    )

    assert recipe["kind"] == "segment_benchmark_temporal"
    assert recipe["schema_version"] == 7
    assert recipe["iqr_min_count"] == TEMPORAL_IQR_MIN_COUNT
    assert recipe["time_bin"] == "3h"
    assert recipe["utc_date_count"] == 2
    assert recipe["folded_title"] == "\u0394 SNR by UTC Hour (1 h bins)"
    assert recipe["folded_date_annotation"] == "2 UTC dates folded"
    assert isinstance(recipe["plot_time_ns"], np.ndarray)
    assert recipe["plot_time_ns"].dtype == np.dtype("int64")
    assert isinstance(recipe["metric"], np.ndarray)
    assert recipe["metric"].dtype == np.dtype("float64")
    assert len(recipe["plot_time_ns"]) == 4
    assert len(recipe["metric"]) == 4
    assert recipe["median_focus"]["median_db"] == pytest.approx(0.0)
    assert recipe["median_focus"]["anchor_offsets_db"][:6] == pytest.approx(
        [0.0, 1.0, 3.0, 6.0, 10.0, 20.0]
    )

    figure = render_segment_temporal_evidence_export_figure(recipe)
    try:
        assert tuple(figure.get_size_inches()) == pytest.approx((13.0, 5.6))
        assert figure.subplotpars.left == pytest.approx(0.07)
        assert figure.subplotpars.right == pytest.approx(0.95)
        assert figure.subplotpars.bottom == pytest.approx(0.15)
        assert figure.subplotpars.top == pytest.approx(0.82)
        assert figure.subplotpars.wspace == pytest.approx(0.20)
        assert len(figure.axes) == 3
        chronological_axis, folded_axis, colorbar_axis = figure.axes
        chronological_mesh = next(
            collection
            for collection in chronological_axis.collections
            if isinstance(collection, QuadMesh)
        )
        folded_mesh = next(
            collection
            for collection in folded_axis.collections
            if isinstance(collection, QuadMesh)
        )
        chronological_density = np.ma.asarray(
            chronological_mesh.get_array()
        ).compressed()
        folded_density = np.ma.asarray(folded_mesh.get_array()).compressed()

        assert sorted(np.unique(chronological_density)) == pytest.approx([50.0, 100.0])
        assert sorted(np.unique(folded_density)) == pytest.approx(
            [100.0 / 3.0, 100.0]
        )
        assert chronological_mesh.norm.vmin == pytest.approx(0.0)
        assert chronological_mesh.norm.vmax == pytest.approx(100.0)
        assert folded_mesh.norm.vmin == pytest.approx(0.0)
        assert folded_mesh.norm.vmax == pytest.approx(100.0)
        assert folded_mesh.get_coordinates().shape[1] == 25
        assert folded_axis.get_xlim() == pytest.approx((0.0, 24.0))
        assert chronological_axis.get_ylim() == pytest.approx(folded_axis.get_ylim())
        assert chronological_axis.get_yscale() == "function"
        assert folded_axis.get_yscale() == "function"
        assert _formatted_y_ticks(chronological_axis) == [
            "−3",
            "−1",
            "0",
            "+1",
            "+3",
        ]
        assert _formatted_y_ticks(folded_axis) == _formatted_y_ticks(
            chronological_axis
        )
        for axis in (chronological_axis, folded_axis):
            assert _legend_texts(axis) == ["Median +0.0 dB", "Bin median"]
            median_lines = _lines_with_gid(
                axis,
                "compare-median-focus-center",
            )
            assert len(median_lines) == 1
            assert median_lines[0].get_color() == "red"
            assert median_lines[0].get_linestyle() == "--"
        panel_width_ratio = (
            chronological_axis.get_position().width
            / folded_axis.get_position().width
        )
        assert panel_width_ratio == pytest.approx(1.95)
        inter_panel_gap = (
            folded_axis.get_position().x0
            - chronological_axis.get_position().x1
        )
        folded_colorbar_gap = (
            colorbar_axis.get_position().x0
            - folded_axis.get_position().x1
        )
        assert folded_colorbar_gap < inter_panel_gap
        figure.canvas.draw()
        renderer = figure.canvas.get_renderer()
        chronological_bbox = chronological_axis.get_window_extent(renderer)
        folded_y_label_bbox = folded_axis.yaxis.label.get_window_extent(renderer)
        assert chronological_bbox.x1 < folded_y_label_bbox.x0
        assert folded_axis.get_title() == "\u0394 SNR by UTC Hour (1 h bins)"
        assert not _texts_with_gid(folded_axis, "folded-utc-date-annotation")
        assert "2 UTC dates folded" not in {
            text.get_text() for text in folded_axis.texts
        }
        assert figure._suptitle.get_text() == (
            "RX Benchmark Temporal: G3ZIL (Target) vs. G4HZX (Reference)"
        )
        assert colorbar_axis.get_ylabel() == (
            "Relative joint-spot density (% of panel maximum)"
        )
    finally:
        dispose_matplotlib_figure(figure)


def test_prepared_compare_profiles_render_time_bin_changes_without_row_work(
    monkeypatch,
):
    """Render every retained bin without decoding or regrouping evidence rows."""
    plot_df = pd.DataFrame(
        {
            "plot_time": pd.to_datetime(
                [
                    "2026-07-01T00:05:00Z",
                    "2026-07-01T01:05:00Z",
                    "2026-07-02T00:05:00Z",
                    "2026-07-02T03:05:00Z",
                ],
                utc=True,
            ),
            "metric": [-2.0, 0.0, 1.0, 3.0],
        }
    )
    recipe = _localized_segment_temporal_recipe(
        plot_df,
        "Prepared Benchmark Temporal Evidence",
        "1h",
        time_bin_options=("1h", "3h"),
    )

    assert "prepared_profiles" in recipe
    assert "plot_time_ns" not in recipe
    assert "metric" not in recipe
    assert set(recipe["prepared_profiles"]["chronological"]) == {"1h", "3h"}

    def fail_row_work(*_args, **_kwargs):
        raise AssertionError("prepared rendering must not revisit evidence rows")

    monkeypatch.setattr(
        evidence_figures,
        "_prepare_temporal_metric_rows",
        fail_row_work,
    )
    monkeypatch.setattr(
        evidence_figures,
        "_chronological_density_components",
        fail_row_work,
    )
    monkeypatch.setattr(
        evidence_figures,
        "_folded_utc_hour_density_components",
        fail_row_work,
    )

    for time_bin in ("1h", "3h"):
        render_recipe = dict(recipe)
        render_recipe["time_bin"] = time_bin
        figure = render_segment_temporal_evidence_export_figure(render_recipe)
        try:
            assert figure is not None
            assert len(figure.axes) == 3
        finally:
            dispose_matplotlib_figure(figure)


@pytest.mark.parametrize("time_bin", ("1h", "3h"))
def test_prepared_compare_profile_matches_exact_row_aggregation(time_bin):
    """Retain the exact density, median and quartile inputs for every bin."""
    plot_df = pd.DataFrame(
        {
            "plot_time": pd.to_datetime(
                [
                    "2026-07-01T00:05:00Z",
                    "2026-07-01T01:05:00Z",
                    "2026-07-02T00:05:00Z",
                    "2026-07-02T03:05:00Z",
                    "2026-07-02T03:25:00Z",
                ],
                utc=True,
            ),
            "metric": [-2.0, 0.0, 1.0, 3.0, 3.5],
        }
    )
    recipe = _localized_segment_temporal_recipe(
        plot_df,
        "Prepared Benchmark Temporal Evidence",
        "1h",
        time_bin_options=("1h", "3h"),
    )
    work_df = evidence_figures._prepare_temporal_metric_rows(
        plot_df, reference_snr_correction_db=0.0,
    )
    metric_bins = np.arange(
        int(work_df["metric_bin"].min()),
        int(work_df["metric_bin"].max()) + 1,
    )
    expected = evidence_figures._chronological_density_components(
        work_df,
        evidence_figures._time_agg_minutes(time_bin),
        metric_bins,
        pd.Timestamp(recipe["analysis_start_utc_ns"], unit="ns"),
        pd.Timestamp(recipe["analysis_end_utc_ns"], unit="ns"),
    )
    actual = evidence_figures._compare_temporal_profile_values(
        recipe["prepared_profiles"]["chronological"][time_bin]
    )

    np.testing.assert_array_equal(actual[0], expected[0].to_numpy())
    for column in ("median", "count", "q1", "q3"):
        np.testing.assert_allclose(
            actual[1][column],
            expected[1][column],
            equal_nan=True,
        )
    np.testing.assert_allclose(actual[2], expected[2])
    np.testing.assert_allclose(actual[3], expected[3])

    expected_folded = evidence_figures._folded_utc_hour_density_components(
        work_df,
        metric_bins,
    )
    actual_folded = evidence_figures._compare_temporal_profile_values(
        recipe["prepared_profiles"]["folded"]
    )
    np.testing.assert_array_equal(
        actual_folded[0],
        expected_folded[0].to_numpy(),
    )
    for column in ("median", "count", "q1", "q3"):
        np.testing.assert_allclose(
            actual_folded[1][column],
            expected_folded[1][column],
            equal_nan=True,
        )
    np.testing.assert_allclose(actual_folded[2], expected_folded[2])
    np.testing.assert_allclose(actual_folded[3], expected_folded[3])


def test_large_compare_recipe_arrays_round_trip_without_precision_loss():
    """Compact large numeric payloads while retaining exact dtype and values."""
    arrays = (
        np.linspace(-40.0, 40.0, 40_000, dtype=np.float64),
        np.tile(np.arange(400, dtype=np.int64), (400, 1)),
    )

    for values in arrays:
        compact_values = evidence_figures._compact_compare_recipe_array(
            values,
            dtype=values.dtype,
        )
        restored_values = evidence_figures._compare_recipe_array_values(
            compact_values,
            dtype=values.dtype,
        )

        assert isinstance(compact_values, dict)
        assert compact_values["encoding"] == "numpy-zlib-v1"
        assert restored_values.dtype == values.dtype
        np.testing.assert_array_equal(restored_values, values)


def test_compact_compare_recipe_arrays_reject_corrupt_metadata_and_payloads():
    """Fail closed on truncated, trailing or structurally mismatched arrays."""
    encoded = evidence_figures._encode_compare_recipe_array(
        np.arange(1_000, dtype=np.float64),
        dtype=np.float64,
    )
    invalid_payloads = []
    for replacement in (
        {"payload": encoded["payload"][:-1]},
        {"payload": encoded["payload"] + b"trailing"},
        {"dtype": np.dtype(np.int64).str},
        {"shape": (999,)},
    ):
        invalid_payload = dict(encoded)
        invalid_payload.update(replacement)
        invalid_payloads.append(invalid_payload)

    for invalid_payload in invalid_payloads:
        with pytest.raises(ValueError):
            evidence_figures._compare_recipe_array_values(
                invalid_payload,
                dtype=np.float64,
            )


def test_segment_temporal_fractional_ticks_remain_inside_the_canvas():
    """Reserve enough left margin for signed decimal absolute-dB tick labels."""
    plot_df = pd.DataFrame(
        {
            "plot_time": pd.to_datetime(
                [
                    "2026-07-01T00:05:00Z",
                    "2026-07-01T03:05:00Z",
                    "2026-07-02T00:05:00Z",
                    "2026-07-02T03:05:00Z",
                ],
                utc=True,
            ),
            "metric": [-0.2, 2.8, 2.8, 5.8],
        }
    )
    recipe = _localized_segment_temporal_recipe(
        plot_df,
        "Fractional Benchmark Temporal Evidence",
        "3h",
        "Joint spot count",
    )

    assert recipe["median_focus"]["median_db"] == pytest.approx(2.8)
    figure = render_segment_temporal_evidence_export_figure(recipe)
    try:
        chronological_axis = figure.axes[0]
        assert "+2.8" in _formatted_y_ticks(chronological_axis)

        figure.canvas.draw()
        renderer = figure.canvas.get_renderer()
        chronological_bounds = chronological_axis.get_tightbbox(renderer)
        assert chronological_bounds.x0 >= figure.bbox.x0
    finally:
        dispose_matplotlib_figure(figure)


def test_segment_temporal_recipe_accepts_localized_labels():
    """Carry localized plot text without retaining a dataframe or figure."""
    plot_df = pd.DataFrame(
        {
            "plot_time": pd.to_datetime(
                ["2026-07-01T00:00:00Z", "2026-07-02T00:00:00Z"],
                utc=True,
            ),
            "metric": [1.0, 2.0],
        }
    )
    recipe = _localized_segment_temporal_recipe(
        plot_df,
        "Zeitliche Segment-Evidenz",
        "3h",
        "Anzahl gemeinsamer Spots",
        chronological_title="Zeitverlauf ({time_bin})",
        chronological_x_label="Datum/Zeit (UTC)",
        metric_axis_label=T["de"]["tbl_col_delta_snr"],
        folded_title="UTC-Stunde ({utc_date_count} UTC-Tage; 1h-Bins)",
        folded_x_label="UTC-Stunde",
        folded_date_annotation="{utc_date_count} UTC-Tage gefaltet",
        density_label="Relative Dichte (% des Panelmaximums)",
        folded_unavailable_text="Mindestens zwei UTC-Tage sind erforderlich.",
        median_focus_axis_label=(
            "\u0394 SNR (dB \u00b7 nichtlinear um Median zentriert)"
        ),
        median_label="Median",
        bin_median_label=T["de"]["fig_temporal_bin_median"],
        bin_iqr_label=T["de"]["fig_temporal_bin_iqr"],
    )

    assert recipe["chronological_title"] == "Zeitverlauf (3h)"
    assert recipe["chronological_x_label"] == "Datum/Zeit (UTC)"
    assert recipe["folded_title"] == "UTC-Stunde (2 UTC-Tage; 1h-Bins)"
    assert recipe["folded_x_label"] == "UTC-Stunde"
    assert recipe["folded_date_annotation"] == "2 UTC-Tage gefaltet"
    assert recipe["density_label"] == "Relative Dichte (% des Panelmaximums)"
    assert recipe["folded_unavailable_text"] == (
        "Mindestens zwei UTC-Tage sind erforderlich."
    )
    assert recipe["median_focus_axis_label"] == (
        "\u0394 SNR (dB \u00b7 nichtlinear um Median zentriert)"
    )
    assert recipe["median_label"] == "Median"
    assert recipe["bin_median_label"] == "Lokaler Median"
    assert recipe["bin_iqr_label"] == "IQR je Bin (mittlere 50 %)"


def test_segment_temporal_figure_keeps_folded_placeholder_for_one_utc_date():
    """Render chronology but avoid implying a daily pattern from one UTC date."""
    plot_df = pd.DataFrame(
        {
            "plot_time": pd.to_datetime(
                [
                    "2026-07-01T00:05:00Z",
                    "2026-07-01T03:05:00Z",
                    "2026-07-01T06:05:00Z",
                ],
                utc=True,
            ),
            "metric": [0.0, 1.0, 2.0],
        }
    )
    placeholder = T["en"]["fig_segment_folded_unavailable"]
    recipe = _localized_segment_temporal_recipe(
        plot_df,
        "Short Segment Evidence",
        "3h",
        "Joint spot count",
        folded_unavailable_text=placeholder,
        time_bin_options=("1h", "3h"),
    )

    figure = render_segment_temporal_evidence_export_figure(recipe)
    try:
        chronological_axis, folded_axis, colorbar_axis = figure.axes

        assert any(
            isinstance(collection, QuadMesh)
            for collection in chronological_axis.collections
        )
        assert not any(
            isinstance(collection, QuadMesh)
            for collection in folded_axis.collections
        )
        _assert_folded_unavailable_annotation(
            figure,
            folded_axis,
            placeholder,
        )
        assert folded_axis.get_title() == "\u0394 SNR by UTC Hour (1 h bins)"
        assert not _texts_with_gid(folded_axis, "folded-utc-date-annotation")
        assert "1 UTC date available; folding unavailable" not in {
            text.get_text() for text in folded_axis.texts
        }
        assert colorbar_axis.get_ylabel() == (
            "Relative joint-spot density (% of panel maximum)"
        )
    finally:
        dispose_matplotlib_figure(figure)




def test_compare_chronological_bins_anchor_to_selected_start_and_keep_gaps():
    """Use the complete window grid without filling unsupported intervals."""
    analysis_start = pd.Timestamp("2026-07-01T00:17:00Z")
    analysis_end = pd.Timestamp("2026-07-01T04:05:00Z")
    plot_df = pd.DataFrame(
        {
            "plot_time": pd.to_datetime(
                [
                    "2026-07-01T00:17:00Z",
                    "2026-07-01T02:17:00Z",
                    "2026-07-01T04:05:00Z",
                ],
                utc=True,
            ),
            "metric": [0.0, 0.0, 0.0],
        }
    )
    work_df = evidence_figures._prepare_temporal_metric_rows(
        plot_df, reference_snr_correction_db=0.0,
    )

    count_grid, summaries, x_edges, x_centers = (
        evidence_figures._chronological_density_components(
            work_df,
            60,
            np.array([0], dtype=np.int64),
            analysis_start,
            analysis_end,
        )
    )

    expected_edges = pd.to_datetime(
        [
            "2026-07-01T00:17:00Z",
            "2026-07-01T01:17:00Z",
            "2026-07-01T02:17:00Z",
            "2026-07-01T03:17:00Z",
            "2026-07-01T04:05:00Z",
        ],
        utc=True,
    ).tz_convert(None)
    expected_centers = pd.to_datetime(
        [
            "2026-07-01T00:47:00Z",
            "2026-07-01T01:47:00Z",
            "2026-07-01T02:47:00Z",
            "2026-07-01T03:41:00Z",
        ],
        utc=True,
    ).tz_convert(None)
    np.testing.assert_allclose(
        x_edges,
        mdates.date2num(expected_edges.to_pydatetime()),
    )
    np.testing.assert_allclose(
        x_centers,
        mdates.date2num(expected_centers.to_pydatetime()),
    )
    np.testing.assert_array_equal(
        count_grid.to_numpy(),
        np.array([[1, 0, 1, 0]], dtype=np.int64),
    )
    assert summaries["count"].fillna(0).tolist() == [1, 0, 1, 0]
    assert np.isnan(summaries.loc[1, "median"])
    assert np.isnan(summaries.loc[3, "median"])


@pytest.mark.parametrize("recipe_kind", ("segment", "selected"))
def test_compare_temporal_views_use_exact_selected_window(recipe_kind):
    """Keep segment and selected-path chronological limits on the run window."""
    analysis_start = pd.Timestamp("2026-07-01T02:17:00+02:00")
    analysis_end = pd.Timestamp("2026-07-01T06:05:00+02:00")
    plot_df = pd.DataFrame(
        {
            "plot_time": pd.to_datetime(
                [
                    "2026-07-01T01:20:00Z",
                    "2026-07-01T03:20:00Z",
                ],
                utc=True,
            ),
            "metric": [-1.0, 2.0],
        }
    )
    common_overrides = {
        "analysis_start_t": analysis_start,
        "analysis_end_t": analysis_end,
        "time_bin_options": ("1h",),
    }
    if recipe_kind == "segment":
        recipe = _localized_segment_temporal_recipe(
            plot_df,
            "Selected-window segment",
            "1h",
            **common_overrides,
        )
    else:
        recipe = _localized_selected_evidence_recipe(
            plot_df,
            "Selected-window path",
            "1h",
            **common_overrides,
        )

    figure = render_segment_temporal_evidence_export_figure(recipe)
    try:
        chronological_axis, folded_axis, _colorbar_axis = figure.axes
        expected_limits = mdates.date2num(
            pd.to_datetime(
                [
                    "2026-07-01T00:17:00Z",
                    "2026-07-01T04:05:00Z",
                ],
                utc=True,
            ).tz_convert(None).to_pydatetime()
        )
        assert chronological_axis.get_xlim() == pytest.approx(expected_limits)
        assert folded_axis.get_xlim() == pytest.approx((0.0, 24.0))
    finally:
        dispose_matplotlib_figure(figure)


def test_empty_compare_temporal_recipe_keeps_full_frame_and_precise_notice():
    """Distinguish no paired evidence from a zero-dB observation or short range."""
    analysis_start = pd.Timestamp("2026-07-01T00:17:00Z")
    analysis_end = pd.Timestamp("2026-07-03T02:05:00Z")
    empty_rows = pd.DataFrame(
        {
            "plot_time": pd.Series(dtype="datetime64[ns, UTC]"),
            "metric": pd.Series(dtype="float64"),
        }
    )
    recipe = _localized_segment_temporal_recipe(
        empty_rows,
        "Empty selected window",
        "3h",
        analysis_start_t=analysis_start,
        analysis_end_t=analysis_end,
        time_bin_options=("3h",),
    )

    figure = render_segment_temporal_evidence_export_figure(recipe)
    try:
        chronological_axis, folded_axis, _colorbar_axis = figure.axes
        expected_limits = mdates.date2num(
            pd.DatetimeIndex(
                [analysis_start.tz_localize(None), analysis_end.tz_localize(None)]
            ).to_pydatetime()
        )
        assert chronological_axis.get_xlim() == pytest.approx(expected_limits)
        assert folded_axis.get_xlim() == pytest.approx((0.0, 24.0))
        for axis, annotation_gid in (
            (
                chronological_axis,
                "compare-temporal-chronological-no-paired-evidence-annotation",
            ),
            (
                folded_axis,
                "compare-temporal-folded-no-paired-evidence-annotation",
            ),
        ):
            annotations = _texts_with_gid(axis, annotation_gid)
            assert len(annotations) == 1
            assert " ".join(annotations[0].get_text().split()) == T["en"][
                "fig_compare_chronological_unavailable"
            ]
            assert axis.get_yticks().size == 0
            assert not _collections_with_gid(
                axis,
                "temporal-bin-median-markers",
            )
            assert not _collections_with_gid(axis, "temporal-bin-iqr-band")
        density_mesh = next(
            collection
            for collection in chronological_axis.collections
            if isinstance(collection, QuadMesh)
        )
        assert np.ma.asarray(density_mesh.get_array()).count() == 0
    finally:
        dispose_matplotlib_figure(figure)


@pytest.mark.parametrize(
    ("language", "expected_text"),
    (
        (
            "en",
            "No paired Δ SNR evidence is available in the selected UTC window.",
        ),
        (
            "de",
            "Im ausgewählten UTC-Zeitfenster liegt keine gepaarte Evidenz "
            "für Δ SNR vor.",
        ),
    ),
)
def test_compare_chronological_empty_notice_is_exact_and_bilingual(
    language,
    expected_text,
):
    """Keep the empty frame distinct from zero dB in both UI languages."""
    assert T[language]["fig_compare_chronological_unavailable"] == expected_text


@pytest.mark.parametrize("obsolete_schema", (4, 5))
def test_compare_temporal_renderer_rejects_stale_data_tight_recipe_schema(obsolete_schema):
    """Reject obsolete window geometry and pre-correction temporal density grids."""
    recipe = _localized_segment_temporal_recipe(
        _correction_footer_test_rows(),
        "Stale selected window",
        "3h",
    )
    recipe["schema_version"] = obsolete_schema

    with pytest.raises(
        ValueError,
        match="Unsupported Benchmark temporal recipe schema",
    ):
        render_segment_temporal_evidence_export_figure(recipe)


_TEMPORAL_TEST_CORRECTIONS_DB = (0.0, 0.5, -0.5, 1.2, -1.2, 1.6, -1.6)


def _correction_grid_population():
    """Provide fractional raw comparisons and hand-calculated half-open IDs."""
    comparison_values = np.array([
        -4.0, -3.56, -3.5, -3.44, -2.5, -2.25,
        -1.75, -1.56, -1.5, -1.44, -1.0, -0.5,
        -0.25, 0.0, 0.44, 0.5, 0.56, 0.75,
        1.25, 1.5, 2.0, 2.5, 3.5, 5.0,
    ])
    expected_bin_ids = np.array([
        -4, -4, -3, -3, -2, -2, -2, -2, -1, -1, -1, 0,
        0, 0, 0, 1, 1, 1, 1, 2, 2, 3, 4, 5,
    ])
    group_times = pd.to_datetime([
        "2026-07-01T00:17:00Z", "2026-07-01T02:17:00Z",
        "2026-07-02T00:17:00Z", "2026-07-02T02:59:00Z",
    ], utc=True)
    plot_times = group_times.repeat(6)
    return comparison_values, expected_bin_ids, plot_times


@pytest.mark.parametrize("correction_db", _TEMPORAL_TEST_CORRECTIONS_DB)
def test_temporal_grid_membership_and_edges_use_independent_half_open_expectations(
    correction_db,
):
    """Translate physical 1 dB cells without re-correcting scientific values."""
    comparisons, expected_ids, plot_times = _correction_grid_population()
    corrected_values = comparisons - correction_db
    source = pd.DataFrame({"plot_time": plot_times, "metric": corrected_values})
    source_before = source.copy(deep=True)
    prepared = evidence_figures._prepare_temporal_metric_rows(
        source, reference_snr_correction_db=correction_db,
    )
    np.testing.assert_array_equal(prepared["metric"], corrected_values)
    np.testing.assert_array_equal(prepared["metric_bin"], expected_ids)
    pd.testing.assert_frame_equal(source, source_before)

    actual_ids, actual_edges = evidence_figures._temporal_metric_bin_axis(
        prepared["metric_bin"], reference_snr_correction_db=correction_db,
    )
    np.testing.assert_array_equal(actual_ids, [-4, -3, -2, -1, 0, 1, 2, 3, 4, 5])
    zero_correction_edges = np.array([
        -4.5, -3.5, -2.5, -1.5, -0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5,
    ])
    np.testing.assert_array_equal(actual_edges, zero_correction_edges - correction_db)
    np.testing.assert_allclose(np.diff(actual_edges), 1.0, rtol=0, atol=1e-15)


@pytest.mark.parametrize("correction_db", _TEMPORAL_TEST_CORRECTIONS_DB)
def test_temporal_grid_uses_authorized_tenth_db_membership_resolution(
    correction_db,
):
    """Suppress sub-tenth noise while preserving distinct 0.1 dB-scale inputs."""
    for raw_boundary, lower_id, upper_id in (
        (-3.5, -4, -3), (-1.5, -2, -1), (-0.5, -1, 0),
        (0.5, 0, 1), (2.5, 2, 3),
    ):
        corrected_boundary = np.float64(raw_boundary) - correction_db
        corrected_values = np.array([
            corrected_boundary - 0.06,
            np.nextafter(corrected_boundary, -np.inf),
            corrected_boundary,
            np.nextafter(corrected_boundary, np.inf),
            corrected_boundary + 0.06,
        ])
        actual_ids = evidence_figures._temporal_metric_bin_ids(
            corrected_values, reference_snr_correction_db=correction_db,
        )
        np.testing.assert_array_equal(actual_ids, [lower_id, upper_id, upper_id, upper_id, upper_id])


@pytest.mark.parametrize("recipe_kind", ("segment", "selected"))
@pytest.mark.parametrize("correction_db", _TEMPORAL_TEST_CORRECTIONS_DB)
def test_temporal_profiles_translate_with_fixed_membership_statistics_and_time_grid(
    recipe_kind, correction_db,
):
    """Use independently tabulated cells for both routes, gaps and final partial bin."""
    comparisons, expected_ids, plot_times = _correction_grid_population()
    corrected_values = comparisons - correction_db
    recipe_builder = (
        _localized_segment_temporal_recipe if recipe_kind == "segment"
        else _localized_selected_evidence_recipe
    )
    common = {
        "reference_snr_correction_db": correction_db,
        "analysis_start_t": pd.Timestamp("2026-07-01T00:17:00Z"),
        "analysis_end_t": pd.Timestamp("2026-07-02T03:05:00Z"),
    }
    source = pd.DataFrame({"plot_time": plot_times, "metric": corrected_values})
    compact_recipe = recipe_builder(source, "Correction grid", "1h", **common)
    prepared_recipe = recipe_builder(
        source, "Correction grid", "1h", time_bin_options=("1h",), **common,
    )
    assert compact_recipe["reference_snr_correction_db"] == correction_db
    assert prepared_recipe["reference_snr_correction_db"] == correction_db
    np.testing.assert_array_equal(
        evidence_figures._compare_recipe_array_values(compact_recipe["metric"], dtype=np.float64),
        corrected_values,
    )
    profiles = prepared_recipe["prepared_profiles"]
    np.testing.assert_array_equal(profiles["metric_bin_ids"], np.arange(-4, 6))
    expected_edges = np.arange(-4.5, 6.0, 1.0) - correction_db
    np.testing.assert_array_equal(profiles["y_edges"], expected_edges)
    for profile_name, expected_column_count, observation_columns in (
        ("chronological", 27, np.repeat([0, 2, 24, 26], 6)),
        ("folded", 24, np.repeat([0, 2, 0, 2], 6)),
    ):
        profile = (
            profiles["chronological"]["1h"] if profile_name == "chronological"
            else profiles["folded"]
        )
        counts, statistics, x_edges, _ = evidence_figures._compare_temporal_profile_values(profile)
        expected_counts = np.zeros((10, expected_column_count), dtype=np.int64)
        for bin_id, column in zip(expected_ids, observation_columns):
            expected_counts[bin_id + 4, column] += 1
        np.testing.assert_array_equal(counts, expected_counts)
        density = evidence_figures._relative_density_values(counts)
        np.testing.assert_array_equal(np.ma.getmaskarray(density), expected_counts == 0)
        np.testing.assert_array_equal(
            density.compressed(),
            (100.0 * expected_counts / expected_counts.max())[expected_counts > 0],
        )
        for column in range(expected_column_count):
            group_values = comparisons[observation_columns == column]
            if not len(group_values):
                assert np.isnan(statistics.loc[column, "median"])
                assert np.isnan(statistics.loc[column, "q1"])
                assert np.isnan(statistics.loc[column, "q3"])
                assert np.isnan(statistics.loc[column, "count"])
                continue
            assert statistics.loc[column, "count"] == len(group_values)
            np.testing.assert_allclose(
                statistics.loc[column, ["q1", "median", "q3"]].to_numpy(dtype=float),
                np.quantile(group_values, [0.25, 0.5, 0.75]) - correction_db,
                rtol=0, atol=1e-14,
            )
        if profile_name == "chronological":
            expected_times = pd.date_range(common["analysis_start_t"], periods=27, freq="1h")
            expected_times = expected_times.append(pd.DatetimeIndex([common["analysis_end_t"]]))
            np.testing.assert_array_equal(x_edges, mdates.date2num(expected_times.to_pydatetime()))
        else:
            np.testing.assert_array_equal(x_edges, np.arange(25))


@pytest.mark.parametrize("recipe_kind", ("segment", "selected"))
@pytest.mark.parametrize("correction_db", (-1.6, 1.6))
def test_corrected_compact_and_prepared_renderers_match_both_density_panels(
    recipe_kind, correction_db,
):
    """Screen/export renderer paths receive identical shifted physical geometry."""
    comparisons, _, plot_times = _correction_grid_population()
    recipe_builder = (
        _localized_segment_temporal_recipe if recipe_kind == "segment"
        else _localized_selected_evidence_recipe
    )
    renderer = (
        render_segment_temporal_evidence_export_figure if recipe_kind == "segment"
        else render_selected_evidence_export_figure
    )
    source = pd.DataFrame({"plot_time": plot_times, "metric": comparisons - correction_db})
    common = {
        "reference_snr_correction_db": correction_db,
        "analysis_start_t": pd.Timestamp("2026-07-01T00:17:00Z"),
        "analysis_end_t": pd.Timestamp("2026-07-02T03:05:00Z"),
    }
    # A deliberately misleading localized footer must never select geometry.
    common["reference_snr_correction_notice"] = "Configured correction: -99 dB"
    recipes = [
        recipe_builder(source, "Correction grid", "1h", **common),
        recipe_builder(source, "Correction grid", "1h", time_bin_options=("1h",), **common),
    ]
    figures = []
    try:
        figures = [renderer(recipe) for recipe in recipes]
        for panel in (0, 1):
            meshes = [next(collection for collection in figure.axes[panel].collections
                           if isinstance(collection, QuadMesh)) for figure in figures]
            np.testing.assert_array_equal(meshes[0].get_coordinates(), meshes[1].get_coordinates())
            np.testing.assert_array_equal(meshes[0].get_array(), meshes[1].get_array())
            np.testing.assert_array_equal(
                np.ma.getmaskarray(meshes[0].get_array()), np.ma.getmaskarray(meshes[1].get_array()),
            )
            np.testing.assert_array_equal(
                meshes[0].get_coordinates()[:, 0, 1], np.arange(-4.5, 6.0, 1.0) - correction_db,
            )
            for figure in figures:
                axis = figure.axes[panel]
                lower, upper = axis.get_ylim()
                assert lower <= min(float(source["metric"].min()), -4.5 - correction_db, 0.0)
                assert upper >= max(float(source["metric"].max()), 5.5 - correction_db, 0.0)
                median_markers = _collections_with_gid(axis, "temporal-bin-median-markers")
                assert len(median_markers) == 1
            np.testing.assert_array_equal(
                _collections_with_gid(figures[0].axes[panel], "temporal-bin-median-markers")[0].get_offsets(),
                _collections_with_gid(figures[1].axes[panel], "temporal-bin-median-markers")[0].get_offsets(),
            )
    finally:
        for figure in figures:
            dispose_matplotlib_figure(figure)


@pytest.mark.parametrize("correction_db", _TEMPORAL_TEST_CORRECTIONS_DB)
def test_empty_temporal_grid_retains_shifted_cell_without_fabricated_evidence(correction_db):
    recipe = _localized_segment_temporal_recipe(
        pd.DataFrame(columns=["plot_time", "metric"]), "Empty", "1h",
        reference_snr_correction_db=correction_db, time_bin_options=("1h",),
    )
    profiles = recipe["prepared_profiles"]
    np.testing.assert_array_equal(profiles["metric_bin_ids"], [0])
    np.testing.assert_array_equal(profiles["y_edges"], np.array([-0.5, 0.5]) - correction_db)
    counts, statistics, _, _ = evidence_figures._compare_temporal_profile_values(profiles["chronological"]["1h"])
    assert not counts.any()
    assert statistics["median"].isna().all()
    assert profiles["folded"] is None


@pytest.mark.parametrize("correction_db", (np.nan, np.inf, -np.inf, "invalid", None))
def test_temporal_recipe_rejects_invalid_numerical_correction_even_with_valid_footer(correction_db):
    with pytest.raises((TypeError, ValueError)):
        _localized_segment_temporal_recipe(
            _correction_footer_test_rows(), "Invalid correction", "1h",
            reference_snr_correction_db=correction_db,
            reference_snr_correction_notice="Configured correction: +1.6 dB",
        )


@pytest.mark.parametrize("correction_db", _TEMPORAL_TEST_CORRECTIONS_DB)
@pytest.mark.parametrize("uses_display_projection", (False, True))
def test_temporal_membership_preserves_half_db_ids_after_production_correction_order(
    correction_db, uses_display_projection,
):
    """Cover T-(R+c) cancellation and the existing one-decimal Joint projection."""
    target_snr = np.array([-39.5, -10.5, -0.5, 0.5, 1.5])
    reference_snr = np.array([-40.0, -10.0, 0.0, 0.0, 0.0])
    corrected_metrics = target_snr - (reference_snr + correction_db)
    if uses_display_projection:
        corrected_metrics = corrected_metrics.round(1)
    source = pd.DataFrame({
        "plot_time": pd.date_range("2026-07-01T00:00Z", periods=5, freq="2min"),
        "metric": corrected_metrics,
    })
    prepared = evidence_figures._prepare_temporal_metric_rows(
        source, reference_snr_correction_db=correction_db,
    )
    np.testing.assert_array_equal(prepared["metric_bin"], [1, 0, 0, 1, 2])
    np.testing.assert_array_equal(prepared["metric"], corrected_metrics)


@pytest.mark.parametrize("correction_db", _TEMPORAL_TEST_CORRECTIONS_DB)
def test_temporal_coordinate_quantization_documents_exact_half_tenth_ties(correction_db):
    """Only comparison-coordinate tenths use ties-to-even, never half-dB IDs."""
    coordinates = [-0.56, -0.55, -0.54, -0.46, -0.45, -0.44, 0.44, 0.45, 0.46]
    expected_ids = [-1, -1, 0, 0, 0, 0, 0, 0, 1]
    np.testing.assert_array_equal(
        evidence_figures._temporal_metric_bin_ids(
            np.array(coordinates) - correction_db, reference_snr_correction_db=correction_db,
        ),
        expected_ids,
    )


@pytest.mark.parametrize("correction_db", _TEMPORAL_TEST_CORRECTIONS_DB)
def test_temporal_coordinate_quantization_preserves_values_beyond_midpoint_roundoff_guard(correction_db):
    """Do not turn a float64 arithmetic guard into a broad midpoint tolerance."""
    comparison_coordinates = np.array([
        -0.550000001, -0.55, -0.549999999,
        0.449999999, 0.45, 0.450000001,
    ])
    np.testing.assert_array_equal(
        evidence_figures._temporal_metric_bin_ids(
            comparison_coordinates - correction_db, reference_snr_correction_db=correction_db,
        ),
        [-1, -1, 0, 0, 0, 1],
    )


@pytest.mark.parametrize("correction_db", _TEMPORAL_TEST_CORRECTIONS_DB)
def test_temporal_median_focus_covers_shifted_cells_extreme_tails_and_absolute_zero(correction_db):
    comparisons = np.array([-37.25, -36.5, 2.5, 40.5])
    corrected_metrics = comparisons - correction_db
    expected_edges = np.arange(-37.5, 42.0, 1.0) - correction_db
    focus = _build_compare_median_focus_spec(corrected_metrics, temporal_y_edges=expected_edges)
    assert focus.median_db == np.median(corrected_metrics)
    assert focus.median_db - focus.half_span_db <= min(expected_edges[0], corrected_metrics.min(), 0.0)
    assert focus.median_db + focus.half_span_db >= max(expected_edges[-1], corrected_metrics.max(), 0.0)
