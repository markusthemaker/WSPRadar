"""Regression coverage for Compare selected and segment temporal evidence."""

from matplotlib.collections import QuadMesh
from matplotlib.colors import to_rgba
import numpy as np
import pandas as pd
import pytest

from i18n import T
from ui.matplotlib_renderer import dispose_matplotlib_figure
from ui.plots.evidence_figures import (
    _build_compare_median_focus_spec,
    _compare_median_focus_forward,
    _compare_median_focus_inverse,
    _compare_median_focus_spec_from_recipe,
    _format_temporal_time_bin_label,
    _segment_temporal_evidence_export_recipe,
    _selected_evidence_export_recipe,
    render_segment_temporal_evidence_export_figure,
    render_selected_evidence_export_figure,
)


def _localized_selected_evidence_recipe(
    plot_df,
    evidence_title,
    time_agg,
    *,
    language="en",
    is_sequential=False,
    **overrides,
):
    """Build one localized dual-panel selected-Compare recipe."""
    translations = T[language]
    presentation = {
        "count_label": translations[
            (
                "fig_scheduled_pair_count"
                if is_sequential
                else "fig_joint_spot_count"
            )
        ],
        "chronological_title": translations[
            "fig_selected_compare_chronological_title"
        ],
        "chronological_subtitle": translations[
            "fig_selected_compare_chronological_subtitle"
        ],
        "chronological_x_label": translations[
            "fig_segment_chronological_x"
        ],
        "metric_axis_label": translations["tbl_col_delta_snr"],
        "folded_title": translations[
            "fig_selected_compare_folded_title"
        ],
        "folded_subtitle": translations[
            "fig_selected_compare_folded_subtitle"
        ],
        "folded_x_label": translations["fig_segment_utc_hour_x"],
        "folded_date_annotation": translations[
            "fig_segment_dates_folded"
        ].replace("{count}", "{utc_date_count}"),
        "density_label": translations[
            (
                "fig_relative_scheduled_pair_density"
                if is_sequential
                else "fig_relative_joint_spot_density"
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
    }
    presentation.update(overrides)
    return _selected_evidence_export_recipe(
        plot_df,
        evidence_title,
        time_agg,
        is_sequential,
        **presentation,
    )


def _localized_segment_temporal_recipe(
    plot_df,
    title,
    time_bin,
    count_label=None,
    *,
    language="en",
    is_sequential=False,
    **overrides,
):
    """Build a segment-temporal recipe with explicit localized labels."""
    translations = T[language]
    resolved_count_label = count_label or translations[
        (
            "fig_scheduled_pair_count"
            if is_sequential
            else "fig_joint_spot_count"
        )
    ]
    chronological_title = translations["fig_segment_chronological_delta"]
    presentation = {
        "chronological_title": translations[
            "fmt_temporal_title_with_bins"
        ].format(
            title=chronological_title,
            time_bin="{time_bin}",
        ),
        "chronological_x_label": translations[
            "fig_segment_chronological_x"
        ],
        "metric_axis_label": translations["tbl_col_delta_snr"],
        "folded_title": translations["fig_segment_utc_hour_title"],
        "folded_x_label": translations["fig_segment_utc_hour_x"],
        "folded_date_annotation": translations[
            "fig_segment_dates_folded"
        ].replace("{count}", "{utc_date_count}"),
        "density_label": translations[
            (
                "fig_relative_scheduled_pair_density"
                if is_sequential
                else "fig_relative_joint_spot_density"
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
    }
    presentation.update(overrides)
    return _segment_temporal_evidence_export_recipe(
        plot_df,
        title,
        time_bin,
        resolved_count_label,
        **presentation,
    )


def _render_compare_evidence_figure(metric_values, identity_labels):
    """Render one Compare selected-station recipe from exact evidence rows."""
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
        is_sequential=False,
    )
    assert recipe["kind"] == "selected_compare_temporal"
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
        chronological_axis, colorbar_axis = figure.axes
        assert chronological_axis.get_gid() == (
            "compare-temporal-chronological-axis"
        )
        assert chronological_axis.get_title() == translations[
            "fig_selected_compare_chronological_title"
        ]
        assert [
            text.get_text()
            for text in _texts_with_gid(
                chronological_axis,
                "compare-temporal-chronological-subtitle",
            )
        ] == [
            translations[
                "fig_selected_compare_chronological_subtitle"
            ].format(time_bin=_format_temporal_time_bin_label("3h"))
        ]
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
        assert translations["fig_segment_folded_unavailable"] in {
            text.get_text() for text in chronological_axis.texts
        }
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


def _formatted_y_ticks(axis):
    """Return the active major y-tick labels without requiring a GUI canvas."""
    formatter = axis.yaxis.get_major_formatter()
    return [formatter(tick_value, index) for index, tick_value in enumerate(axis.get_yticks())]


def _texts_with_gid(axis, gid):
    """Return axis text artists tagged as one visual-summary class."""
    return [text_artist for text_artist in axis.texts if text_artist.get_gid() == gid]


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
        is_sequential=False,
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

    assert recipe["kind"] == "selected_compare_temporal"
    assert recipe["time_bin"] == "6h"
    assert recipe["chronological_title"] == "\u0394 SNR over Time"
    assert recipe["chronological_subtitle"] == (
        "Selected station \u00b7 6 h bins"
    )
    assert recipe["folded_title"] == "\u0394 SNR by UTC Hour"
    assert recipe["folded_subtitle"] == "Selected station \u00b7 1 h bins"
    assert recipe["omit_folded_when_unavailable"] is True
    assert recipe["show_folded_date_annotation"] is True
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
    ):
        assert retired_field not in recipe


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
        is_sequential=False,
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
            "+6 M",
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
            assert len(
                _lines_with_gid(axis, "compare-temporal-zero-line")
            ) == 1
            assert _legend_texts(axis) == ["Median +6.0 dB", "Bin median"]
            _assert_legend_keys_precede_text(figure, axis)
            assert not _texts_with_gid(axis, "compare-median-focus-note")
            assert not axis.patches
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


def test_selected_compare_marks_absolute_zero_between_noninteger_focus_ticks():
    """Keep Target/Reference equality visible when zero is not a focus anchor."""
    figure = _render_compare_evidence_figure(
        [4.5, 5.5, 5.5, 6.5],
        ["A (AA00)"] * 4,
    )

    try:
        chronological_axis, folded_axis = figure.axes[:2]
        for axis in (chronological_axis, folded_axis):
            assert "+5.5 M" in _formatted_y_ticks(axis)
            assert "0" not in _formatted_y_ticks(axis)
            assert len(
                _lines_with_gid(axis, "compare-temporal-zero-line")
            ) == 1
            zero_labels = [
                text
                for text in axis.texts
                if text.get_gid() == "compare-temporal-zero-label"
            ]
            assert [text.get_text() for text in zero_labels] == ["0 dB"]
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
        is_sequential=False,
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
        is_sequential=False,
        folded_title="UTC profile",
        folded_subtitle="Selected station \u00b7 1 h bins",
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
        assert "2 UTC dates folded" in {
            text.get_text() for text in folded_axis.texts
        }
        assert colorbar_axis.get_ylabel() == "Relative selected density"
        assert colorbar_axis.get_gid() == "compare-temporal-colorbar-axis"
        assert chronological_axis.get_gid() == (
            "compare-temporal-chronological-axis"
        )
        assert folded_axis.get_gid() == "compare-temporal-folded-axis"
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
        assert [
            text.get_text()
            for text in _texts_with_gid(
                one_hour_chronological,
                "compare-temporal-chronological-subtitle",
            )
        ] == ["Selected station \u00b7 1 h bins"]
        assert [
            text.get_text()
            for text in _texts_with_gid(
                six_hour_chronological,
                "compare-temporal-chronological-subtitle",
            )
        ] == ["Selected station \u00b7 6 h bins"]
        for folded_axis in (one_hour_folded, six_hour_folded):
            assert [
                text.get_text()
                for text in _texts_with_gid(
                    folded_axis,
                    "compare-temporal-folded-subtitle",
                )
            ] == ["Selected station \u00b7 1 h bins"]
    finally:
        dispose_matplotlib_figure(one_hour_figure)
        dispose_matplotlib_figure(six_hour_figure)


def test_selected_folded_view_uses_localized_placeholder_below_two_dates():
    """Expand chronology and omit the folded panel below two UTC dates."""
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
        is_sequential=False,
        folded_title="UTC-Profil",
        folded_subtitle="Ausgew\u00e4hlte Station \u00b7 1-h-Bins",
        folded_x_label="UTC-Stunde",
        folded_unavailable_text=placeholder,
    )

    figure = render_selected_evidence_export_figure(recipe)
    try:
        assert len(figure.axes) == 2
        chronological_axis, colorbar_axis = figure.axes

        assert any(
            isinstance(collection, QuadMesh)
            for collection in chronological_axis.collections
        )
        assert chronological_axis.get_gid() == (
            "compare-temporal-chronological-axis"
        )
        assert all(
            axis.get_gid() != "compare-temporal-folded-axis"
            for axis in figure.axes
        )
        assert chronological_axis.get_position().width > 0.75
        assert placeholder in {
            text.get_text() for text in chronological_axis.texts
        }
        assert chronological_axis.get_title() == (
            T["en"]["fig_selected_compare_chronological_title"]
        )
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
def test_selected_compare_dual_panels_share_reference_line_hierarchy(
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
        is_sequential=False,
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
        assert len(zero_understrokes) == 1
        assert len(zero_lines) == 1
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
            "0 M",
            "+3",
            "+6",
            "+10",
            "+20",
        ]
        assert zero_lines[0].get_linestyle() == "--"
        assert zero_lines[0].get_linewidth() == pytest.approx(0.85)
        assert zero_understrokes[0].get_linewidth() == pytest.approx(1.7)
        assert zero_lines[0].get_color() == "#f4f1e8"
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
                *zero_understrokes,
                *zero_lines,
                *median_lines,
            ]
        ) < 4.0
        assert not any(gridline.get_visible() for gridline in temporal_axis.get_ygridlines())
    finally:
        dispose_matplotlib_figure(figure)


def test_segment_compare_temporal_recipe_and_dual_density_figure():
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
        "RX Compare Temporal: G3ZIL (Target) vs. G4HZX (Reference)",
        "3h",
        "Joint spot count",
    )

    assert recipe["kind"] == "segment_compare_temporal"
    assert recipe["schema_version"] == 1
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
            "0 M",
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
            "RX Compare Temporal: G3ZIL (Target) vs. G4HZX (Reference)"
        )
        assert colorbar_axis.get_ylabel() == (
            "Relative joint-spot density (% of panel maximum)"
        )
    finally:
        dispose_matplotlib_figure(figure)


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
        "Fractional Compare Temporal Evidence",
        "3h",
        "Joint spot count",
    )

    assert recipe["median_focus"]["median_db"] == pytest.approx(2.8)
    figure = render_segment_temporal_evidence_export_figure(recipe)
    try:
        chronological_axis = figure.axes[0]
        assert "+2.8 M" in _formatted_y_ticks(chronological_axis)

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


def test_sequential_time_heatmap_uses_relative_scheduled_pair_density_label():
    """Keep periodic TX A/B relative density distinct from old spot-bin wording."""
    plot_df = pd.DataFrame(
        {
            "identity": ["A (AA00)", "A (AA00)"],
            "plot_time": pd.to_datetime(
                ["2026-07-01T00:00:00Z", "2026-07-01T00:10:00Z"],
                utc=True,
            ),
            "metric": [1.0, 2.0],
        }
    )
    recipe = _localized_selected_evidence_recipe(
        plot_df,
        "Scheduled Evidence",
        "1h",
        is_sequential=True,
    )

    figure = render_selected_evidence_export_figure(recipe)
    try:
        assert "Relative scheduled-pair density (% of panel maximum)" in {
            axis.get_ylabel() for axis in figure.axes
        }
        chronological_axis = figure.axes[0]
        assert T["en"]["fig_segment_folded_unavailable"] in {
            text.get_text() for text in chronological_axis.texts
        }
        assert "requires paired evidence" in T["en"][
            "fig_segment_folded_unavailable"
        ]
        assert all(
            axis.get_gid() != "compare-temporal-folded-axis"
            for axis in figure.axes
        )
    finally:
        dispose_matplotlib_figure(figure)
