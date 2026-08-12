"""Regression coverage for optional chronological Delta-SNR candidate markers."""

import matplotlib as mpl
from matplotlib.markers import MarkerStyle
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import pytest

from ui.matplotlib_renderer import dispose_matplotlib_figure
from ui.plots.evidence_figures import (
    DELTA_SNR_OUTLIER_MARKER_FACE_COLOR,
    DELTA_SNR_OUTLIER_MARKER_INNER_EDGE_COLOR,
    DELTA_SNR_OUTLIER_MARKER_INNER_EDGE_WIDTH,
    DELTA_SNR_OUTLIER_MARKER_OUTER_EDGE_COLOR,
    DELTA_SNR_OUTLIER_MARKER_OUTER_EDGE_WIDTH,
    DELTA_SNR_OUTLIER_MARKER_SIZE,
    DELTA_SNR_OUTLIER_MARKER_ZORDER,
    _segment_temporal_evidence_export_recipe,
    render_segment_temporal_evidence_export_figure,
    render_selected_evidence_export_figure,
)


def _benchmark_temporal_recipe(*, kind="segment_benchmark_temporal"):
    """Build one deterministic dual-panel recipe covering two UTC dates."""
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
            "metric": [7.5, 0.0, 0.0, -6.25],
        }
    )
    return _segment_temporal_evidence_export_recipe(
        plot_df,
        "Benchmark temporal evidence",
        "3h",
        "Joint spot count",
        analysis_start_t=pd.Timestamp("2026-07-01T00:00:00Z"),
        analysis_end_t=pd.Timestamp("2026-07-03T00:00:00Z"),
        chronological_title="Delta SNR over time ({time_bin})",
        chronological_x_label="Date/time (UTC)",
        chronological_unavailable_text="No paired evidence.",
        metric_axis_label="Delta SNR (dB)",
        folded_title="Delta SNR by UTC hour",
        folded_x_label="UTC hour",
        folded_date_annotation="{utc_date_count} dates",
        density_label="Relative density",
        folded_unavailable_text="Two dates required.",
        median_focus_axis_label="Delta SNR relative to median (dB)",
        median_label="Median",
        bin_median_label="Bin median",
        bin_iqr_label="Bin IQR",
        kind=kind,
    )


def _collections_with_gid(axis, gid):
    """Return collections tagged as one temporal overlay class."""
    return [
        collection
        for collection in axis.collections
        if collection.get_gid() == gid
    ]


def _legend_texts(axis):
    """Return the visible legend entries for one axis."""
    legend = axis.get_legend()
    assert legend is not None
    return [text.get_text() for text in legend.get_texts()]


def _assert_high_contrast_candidate_style(marker_collection):
    """Verify the magenta fill, white edge, and black outer halo contract."""
    np.testing.assert_allclose(
        marker_collection.get_facecolors(),
        [mpl.colors.to_rgba(DELTA_SNR_OUTLIER_MARKER_FACE_COLOR)],
    )
    np.testing.assert_allclose(
        marker_collection.get_edgecolors(),
        [mpl.colors.to_rgba(DELTA_SNR_OUTLIER_MARKER_INNER_EDGE_COLOR)],
    )
    assert marker_collection.get_linewidths() == pytest.approx(
        [DELTA_SNR_OUTLIER_MARKER_INNER_EDGE_WIDTH]
    )
    marker_path_effects = marker_collection.get_path_effects()
    assert [type(effect).__name__ for effect in marker_path_effects] == [
        "Stroke",
        "Normal",
    ]
    assert marker_path_effects[0]._gc["linewidth"] == pytest.approx(
        DELTA_SNR_OUTLIER_MARKER_OUTER_EDGE_WIDTH
    )
    assert mpl.colors.to_rgba(
        marker_path_effects[0]._gc["foreground"]
    ) == pytest.approx(
        mpl.colors.to_rgba(DELTA_SNR_OUTLIER_MARKER_OUTER_EDGE_COLOR)
    )


def test_absent_outlier_marker_recipe_preserves_existing_figure_contract():
    """Keep disabled recipes, artists, legends, and layout unchanged."""
    recipe = _benchmark_temporal_recipe()

    assert "delta_snr_outlier_markers" not in recipe
    figure = render_segment_temporal_evidence_export_figure(recipe)
    try:
        chronological_axis, folded_axis, colorbar_axis = figure.axes
        assert not _collections_with_gid(
            chronological_axis,
            "delta-snr-outlier-candidate-markers",
        )
        assert not _collections_with_gid(
            folded_axis,
            "delta-snr-outlier-candidate-markers",
        )
        assert _legend_texts(chronological_axis) == [
            "Median +0.0 dB",
            "Bin median",
        ]
        assert _legend_texts(folded_axis) == [
            "Median +0.0 dB",
            "Bin median",
        ]
        assert tuple(figure.get_size_inches()) == pytest.approx((13.0, 5.6))
        assert figure.subplotpars.left == pytest.approx(0.07)
        assert figure.subplotpars.right == pytest.approx(0.95)
        assert figure.subplotpars.bottom == pytest.approx(0.15)
        assert figure.subplotpars.top == pytest.approx(0.82)
        assert figure.subplotpars.wspace == pytest.approx(0.20)
        assert colorbar_axis.get_gid() == "compare-temporal-colorbar-axis"
    finally:
        dispose_matplotlib_figure(figure)


@pytest.mark.parametrize(
    ("kind", "renderer"),
    (
        (
            "segment_benchmark_temporal",
            render_segment_temporal_evidence_export_figure,
        ),
        (
            "selected_benchmark_temporal",
            render_selected_evidence_export_figure,
        ),
    ),
)
def test_outlier_candidates_are_exact_chronological_stars_with_one_localized_legend(
    kind,
    renderer,
):
    """Render every supplied coordinate once, only on the chronological panel."""
    recipe = _benchmark_temporal_recipe(kind=kind)
    centers_utc = pd.to_datetime(
        ["2026-07-01T01:30:00Z", "2026-07-01T01:30:00Z"],
        utc=True,
    )
    marker_delta_snr_db = np.asarray([7.5, -6.25], dtype=float)
    localized_label = "Delta-SNR-Ausreißerkandidat"
    recipe["delta_snr_outlier_markers"] = {
        "schema_version": 3,
        "detector_version": "native-residual-episode-v1",
        "detection_resolution": "native-paired-unit",
        "candidate_count": 2,
        "candidate_signature": "deterministic-test-signature",
        "legend_label": localized_label,
        "markers": [
            {
                "callsign": "A1AAA",
                "locator": "AA00aa",
                "marker_utc_ns": int(centers_utc[0].value),
                "marker_delta_snr_db": marker_delta_snr_db[0],
                "episode_start_utc_ns": int(centers_utc[0].value),
                "episode_end_utc_ns": int(centers_utc[0].value) + 1,
                "event_kind": "spot_impulse",
            },
            {
                "callsign": "B2BBB",
                "locator": "BB11bb",
                "marker_utc_ns": int(centers_utc[1].value),
                "marker_delta_snr_db": marker_delta_snr_db[1],
                "episode_start_utc_ns": int(
                    (centers_utc[1] - pd.Timedelta(minutes=6)).value
                ),
                "episode_end_utc_ns": int(
                    (centers_utc[1] + pd.Timedelta(minutes=8)).value
                ),
                "event_kind": "short_burst",
            },
        ],
    }

    figure = renderer(recipe)
    try:
        chronological_axis, folded_axis = figure.axes[:2]
        chronological_markers = _collections_with_gid(
            chronological_axis,
            "delta-snr-outlier-candidate-markers",
        )
        assert len(chronological_markers) == 1
        marker_collection = chronological_markers[0]
        np.testing.assert_allclose(
            np.asarray(marker_collection.get_offsets(), dtype=float),
            np.column_stack(
                (
                    mdates.date2num(centers_utc.to_pydatetime()),
                    marker_delta_snr_db,
                )
            ),
            rtol=0.0,
            atol=1e-10,
        )
        assert marker_collection.get_sizes() == pytest.approx(
            [DELTA_SNR_OUTLIER_MARKER_SIZE]
        )
        assert marker_collection.get_zorder() == pytest.approx(
            DELTA_SNR_OUTLIER_MARKER_ZORDER
        )
        _assert_high_contrast_candidate_style(marker_collection)
        expected_star = MarkerStyle("*").get_path().transformed(
            MarkerStyle("*").get_transform()
        )
        np.testing.assert_allclose(
            marker_collection.get_paths()[0].vertices,
            expected_star.vertices,
        )

        assert not _collections_with_gid(
            folded_axis,
            "delta-snr-outlier-candidate-markers",
        )
        assert _legend_texts(chronological_axis).count(localized_label) == 1
        assert localized_label not in _legend_texts(folded_axis)
        chronological_legend = chronological_axis.get_legend()
        assert chronological_legend.get_zorder() > marker_collection.get_zorder()
        legend_markers = [
            legend_handle
            for legend_handle in chronological_legend.legend_handles
            if legend_handle.get_gid()
            == "delta-snr-outlier-candidate-markers-legend"
        ]
        assert len(legend_markers) == 1
        assert legend_markers[0].get_sizes() == pytest.approx(
            [DELTA_SNR_OUTLIER_MARKER_SIZE]
        )
        _assert_high_contrast_candidate_style(legend_markers[0])
    finally:
        dispose_matplotlib_figure(figure)


def test_outlier_markers_require_a_localized_legend_label():
    """Reject active markers instead of silently introducing English fallback."""
    recipe = _benchmark_temporal_recipe()
    recipe["delta_snr_outlier_markers"] = {
        "schema_version": 3,
        "detector_version": "native-residual-episode-v1",
        "detection_resolution": "native-paired-unit",
        "candidate_count": 1,
        "candidate_signature": "test-signature",
        "markers": [
            {
                "callsign": "A1AAA",
                "locator": "AA00",
                "marker_utc_ns": int(
                    pd.Timestamp("2026-07-01T01:30:00Z").value
                ),
                "marker_delta_snr_db": 7.5,
                "episode_start_utc_ns": int(
                    pd.Timestamp("2026-07-01T01:28:00Z").value
                ),
                "episode_end_utc_ns": int(
                    pd.Timestamp("2026-07-01T01:32:00Z").value
                ),
                "event_kind": "spot_impulse",
            }
        ],
    }

    with pytest.raises(
        ValueError,
        match="localized legend label",
    ):
        render_segment_temporal_evidence_export_figure(recipe)


@pytest.mark.parametrize(
    ("marker_updates", "recipe_updates", "expected_error"),
    (
        ({}, {"schema_version": 99}, "Unsupported.*schema"),
        ({}, {"candidate_count": 2}, "count must match"),
        (
            {"marker_utc_ns": int(pd.NaT.value)},
            {},
            "UTC values must be valid",
        ),
        (
            {"marker_delta_snr_db": np.inf},
            {},
            "marker values must be finite",
        ),
        (
            {"episode_end_utc_ns": int(
                pd.Timestamp("2026-07-01T01:28:00Z").value
            )},
            {},
            "bounds must define positive intervals",
        ),
        (
            {"marker_utc_ns": int(
                pd.Timestamp("2026-07-01T01:40:00Z").value
            )},
            {},
            "representative UTC values must fall inside",
        ),
        (
            {"event_kind": "hourly_outlier"},
            {},
            "supported event kind",
        ),
        (
            {},
            {"detection_resolution": "1h"},
            "native-paired-unit detection resolution",
        ),
    ),
)
def test_outlier_marker_recipe_rejects_stale_or_nonfinite_payloads(
    marker_updates,
    recipe_updates,
    expected_error,
):
    """Fail closed on incompatible counts, schemas, times, and coordinates."""
    recipe = _benchmark_temporal_recipe()
    marker = {
        "callsign": "A1AAA",
        "locator": "AA00",
        "marker_utc_ns": int(
            pd.Timestamp("2026-07-01T01:30:00Z").value
        ),
        "marker_delta_snr_db": 7.5,
        "episode_start_utc_ns": int(
            pd.Timestamp("2026-07-01T01:28:00Z").value
        ),
        "episode_end_utc_ns": int(
            pd.Timestamp("2026-07-01T01:32:00Z").value
        ),
        "event_kind": "spot_impulse",
    }
    marker.update(marker_updates)
    outlier_recipe = {
        "schema_version": 3,
        "detector_version": "native-residual-episode-v1",
        "detection_resolution": "native-paired-unit",
        "candidate_count": 1,
        "candidate_signature": "test-signature",
        "legend_label": "candidate",
        "markers": [marker],
    }
    outlier_recipe.update(recipe_updates)
    recipe["delta_snr_outlier_markers"] = outlier_recipe

    with pytest.raises(ValueError, match=expected_error):
        render_segment_temporal_evidence_export_figure(recipe)
