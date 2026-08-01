"""Scientific regression contracts for retained Compare evidence views."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from i18n import T
import ui.plots.compare_evidence_figures as compare_evidence_figures
from ui.inspector.evidence_data import (
    COMPARE_OUTCOME_JOINT,
    COMPARE_OUTCOME_REFERENCE_ONLY,
    COMPARE_OUTCOME_TARGET_ONLY,
    _build_compare_unit_rows,
    _build_evidence_points,
    _compare_joint_evidence_points,
    _retain_thresholded_compare_outcomes,
)
from ui.matplotlib_renderer import dispose_matplotlib_figure
from ui.plots.compare_evidence_figures import (
    COMPARE_SELECTED_PATH_COVERAGE_RECIPE_KIND,
    COMPARE_TEMPORAL_COVERAGE_RECIPE_KIND,
    _aggregate_compare_chronological_coverage,
    _aggregate_compare_folded_coverage,
    _compare_coverage_recipe,
    _prepare_compare_coverage_units,
    render_compare_temporal_coverage_export_figure,
    render_selected_compare_coverage_export_figure,
)
from ui.plots.evidence_figures import (
    METRIC_LEGEND_FONTSIZE,
)
from ui.plots.opportunity_figures import (
    SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION,
)


def _canonical_compare_units(rows):
    """Return canonical retained Compare units from compact test tuples."""
    units = pd.DataFrame(
        rows,
        columns=[
            "peer_sign",
            "peer_grid",
            "evidence_utc",
            "outcome",
            "metric",
            "paired_eligible",
        ],
    )
    units["evidence_utc"] = pd.to_datetime(
        units["evidence_utc"],
        utc=True,
    )
    identity_pairs = units[["peer_sign", "peer_grid"]].drop_duplicates()
    identity_pairs["identity_order"] = np.arange(len(identity_pairs))
    units = units.merge(
        identity_pairs,
        on=["peer_sign", "peer_grid"],
        how="left",
    )
    units["identity"] = (
        units["peer_sign"].astype(str)
        + " ("
        + units["peer_grid"].astype(str)
        + ")"
    )
    return units


def _compare_coverage_labels():
    """Return complete neutral labels for pure recipe and render tests."""
    return {
        "utc_dates_folded": "{count} dates",
        "time_x": "Time",
        "utc_hour_x": "UTC hour",
        "evidence_chronological_title": "Coverage ({time_bin})",
        "evidence_utc_hour_title": "Coverage by UTC hour",
        "station_vote_y": "Station votes",
        "station_folded_y": "Average station presences",
        "unit_y": "Comparison units",
        "unit_folded_y": "Average comparison units",
        "joint_share_y": "Joint Evidence Share (%)",
        "station_joint_share": "Station-balanced Joint Evidence Share",
        "outcome_joint_share": "Outcome-level Joint Evidence Share",
        "target_only": "Only Target",
        "joint": "Joint",
        "reference_only": "Only Reference",
        "gate_note": "Target-Active Gate",
        "selected_chronological_title": "Selected path ({time_bin})",
        "selected_utc_hour_title": "Selected path by UTC hour",
        "selected_title_unit": "Retained WSPR Cycles",
        "selected_unit_y": "WSPR Cycles",
        "selected_unit_folded_y": "Average WSPR Cycles",
        "selected_joint_share": "Joint Evidence Share",
    }


def _coverage_recipe(units, *, start, end, population_mode=None):
    """Build one one-hour Compare temporal recipe for tests."""
    recipe_kwargs = {}
    if population_mode is not None:
        recipe_kwargs["population_mode"] = population_mode
    return _compare_coverage_recipe(
        units,
        coverage_title="Compare Temporal Evidence Coverage",
        selected_segment="0-1000 km",
        analysis_start_t=start,
        analysis_end_t=end,
        time_bin_options=["1h"],
        time_bin_default="1h",
        figure_labels=_compare_coverage_labels(),
        **recipe_kwargs,
    )


def _figure_artist_with_gid(figure, gid):
    """Return the unique figure, legend, or axis-text artist with ``gid``."""
    candidates = [*figure.texts, *figure.legends]
    for axis in figure.axes:
        candidates.extend(axis.texts)
    matches = [
        artist
        for artist in candidates
        if artist.get_gid() == gid
    ]
    assert len(matches) == 1, gid
    return matches[0]


def _assert_artists_do_not_overlap(figure, artists):
    """Assert that every named layout artist has a disjoint rendered box."""
    figure.canvas.draw()
    renderer = figure.canvas.get_renderer()
    rendered_bounds = [
        (artist, artist.get_window_extent(renderer))
        for artist in artists
    ]
    for index, (left_artist, left_bounds) in enumerate(rendered_bounds):
        for right_artist, right_bounds in rendered_bounds[index + 1 :]:
            assert not left_bounds.overlaps(right_bounds), (
                left_artist.get_gid(),
                right_artist.get_gid(),
            )


def _assert_compare_coverage_header_layout(
    figure,
    *,
    header_gids,
    subtitle_gids=(),
):
    """Keep the coverage title, legend, and retained headings disjoint."""
    title = figure._suptitle
    assert title is not None
    title.set_gid("compare-temporal-coverage-title")
    legend = _figure_artist_with_gid(
        figure,
        "compare-temporal-coverage-legend",
    )
    _assert_artists_do_not_overlap(
        figure,
        [
            title,
            legend,
            *(
                _figure_artist_with_gid(figure, gid)
                for gid in (*header_gids, *subtitle_gids)
            ),
        ],
    )
    figure.canvas.draw()
    renderer = figure.canvas.get_renderer()
    for artist in (
        title,
        legend,
        *(
            _figure_artist_with_gid(figure, gid)
            for gid in (*header_gids, *subtitle_gids)
        ),
    ):
        bounds = artist.get_window_extent(renderer)
        assert figure.bbox.x0 <= bounds.x0
        assert bounds.x1 <= figure.bbox.x1
        assert figure.bbox.y0 <= bounds.y0
        assert bounds.y1 <= figure.bbox.y1


def _assert_neighboring_y_labels_do_not_overlap(
    figure,
    *,
    axis_gid_pairs,
):
    """Keep folded average-unit labels clear of chronological share labels."""
    figure.canvas.draw()
    renderer = figure.canvas.get_renderer()
    for left_axis_gid, right_axis_gid in axis_gid_pairs:
        left_axis = next(
            axis
            for axis in figure.axes
            if axis.get_gid() == left_axis_gid
        )
        right_axis = next(
            axis
            for axis in figure.axes
            if axis.get_gid() == right_axis_gid
        )
        left_bounds = left_axis.yaxis.label.get_window_extent(renderer)
        right_bounds = right_axis.yaxis.label.get_window_extent(renderer)
        assert not left_bounds.overlaps(right_bounds), (
            left_axis_gid,
            right_axis_gid,
        )
        assert figure.bbox.x0 <= right_bounds.x0
        assert right_bounds.x1 <= figure.bbox.x1


def _assert_folded_y_labels_fit_figure(
    figure,
    *,
    folded_axis_gids,
    header_gids,
):
    """Keep folded average labels inside and clear of surrounding copy."""
    folded_labels = [
        next(
            axis
            for axis in figure.axes
            if axis.get_gid() == axis_gid
        ).yaxis.label
        for axis_gid in folded_axis_gids
    ]
    surrounding_artists = [
        figure._suptitle,
        _figure_artist_with_gid(
            figure,
            "compare-temporal-coverage-legend",
        ),
        _figure_artist_with_gid(
            figure,
            "compare-temporal-coverage-gate-note",
        ),
        *(
            _figure_artist_with_gid(figure, gid)
            for gid in header_gids
        ),
    ]
    _assert_artists_do_not_overlap(
        figure,
        [*folded_labels, *surrounding_artists],
    )
    figure.canvas.draw()
    renderer = figure.canvas.get_renderer()
    for label in folded_labels:
        bounds = label.get_window_extent(renderer)
        assert figure.bbox.x0 <= bounds.x0
        assert bounds.x1 <= figure.bbox.x1
        assert figure.bbox.y0 <= bounds.y0
        assert bounds.y1 <= figure.bbox.y1


def _assert_compare_coverage_note_is_in_footer(
    figure,
    *,
    primary_axis_gids,
):
    """Keep the gate note below every decorated primary plot axis."""
    note = _figure_artist_with_gid(
        figure,
        "compare-temporal-coverage-gate-note",
    )
    primary_axes = [
        next(axis for axis in figure.axes if axis.get_gid() == gid)
        for gid in primary_axis_gids
    ]
    figure.canvas.draw()
    renderer = figure.canvas.get_renderer()
    note_bounds = note.get_window_extent(renderer)
    axis_bounds = [
        axis.get_tightbbox(renderer)
        for axis in primary_axes
    ]
    assert note_bounds.y1 < min(bounds.y0 for bounds in axis_bounds)
    assert figure.bbox.x0 <= note_bounds.x0
    assert note_bounds.x1 <= figure.bbox.x1
    return note


def _assert_compare_coverage_footer_typography(
    figure,
    expected_note,
):
    """Keep the two-line gate note at the exact shared legend font size."""
    note = _figure_artist_with_gid(
        figure,
        "compare-temporal-coverage-gate-note",
    )
    legend = _figure_artist_with_gid(
        figure,
        "compare-temporal-coverage-legend",
    )
    legend_texts = legend.get_texts()
    assert legend_texts
    assert note.get_text() == expected_note
    assert expected_note.count("\n") == 1
    first_line, second_line = note.get_text().splitlines()
    assert first_line.endswith(".")
    assert second_line
    assert note.get_fontsize() == pytest.approx(METRIC_LEGEND_FONTSIZE)
    assert all(
        text_artist.get_fontsize()
        == pytest.approx(METRIC_LEGEND_FONTSIZE)
        for text_artist in legend_texts
    )
    assert note.get_fontsize() == pytest.approx(
        max(text_artist.get_fontsize() for text_artist in legend_texts)
    )
    assert all(
        note.get_fontfamily() == text_artist.get_fontfamily()
        and note.get_fontweight() == text_artist.get_fontweight()
        for text_artist in legend_texts
    )


def _assert_compare_coverage_outcome_order(
    figure,
    *,
    primary_axis_gids,
    labels,
):
    """Keep Joint at the stack baseline and first in the shared legend."""
    expected_categories = (
        ("joint", labels["joint"]),
        ("target-only", labels["target_only"]),
        ("reference-only", labels["reference_only"]),
    )
    legend = _figure_artist_with_gid(
        figure,
        "compare-temporal-coverage-legend",
    )
    assert tuple(
        text_artist.get_text() for text_artist in legend.get_texts()[:3]
    ) == tuple(label for _, label in expected_categories)

    for axis_gid in primary_axis_gids:
        axis = next(
            axis for axis in figure.axes if axis.get_gid() == axis_gid
        )
        bars_by_category = {
            category: sorted(
                (
                    bar
                    for bar in axis.patches
                    if (bar.get_gid() or "").endswith(f"-{category}")
                ),
                key=lambda bar: bar.get_x(),
            )
            for category, _ in expected_categories
        }
        joint_bars = bars_by_category["joint"]
        target_bars = bars_by_category["target-only"]
        reference_bars = bars_by_category["reference-only"]
        assert joint_bars
        assert len(joint_bars) == len(target_bars) == len(reference_bars)
        for joint_bar, target_bar, reference_bar in zip(
            joint_bars,
            target_bars,
            reference_bars,
        ):
            assert target_bar.get_x() == pytest.approx(joint_bar.get_x())
            assert reference_bar.get_x() == pytest.approx(joint_bar.get_x())
            assert target_bar.get_width() == pytest.approx(
                joint_bar.get_width()
            )
            assert reference_bar.get_width() == pytest.approx(
                joint_bar.get_width()
            )
            assert joint_bar.get_y() == pytest.approx(0.0)
            assert target_bar.get_y() == pytest.approx(
                joint_bar.get_height()
            )
            assert reference_bar.get_y() == pytest.approx(
                joint_bar.get_height() + target_bar.get_height()
            )


def _assert_compare_coverage_share_labels(
    figure,
    *,
    expected_axis_label,
    expected_legend_labels,
):
    """Distinguish compact secondary-axis units from full legend metrics."""
    share_axes = [
        axis
        for axis in figure.axes
        if (axis.get_gid() or "").endswith("-share-axis")
    ]
    assert share_axes
    assert {
        axis.get_ylabel() for axis in share_axes
    } == {expected_axis_label}
    legend = _figure_artist_with_gid(
        figure,
        "compare-temporal-coverage-legend",
    )
    legend_texts = {
        text_artist.get_text()
        for text_artist in legend.get_texts()
    }
    assert set(expected_legend_labels).issubset(legend_texts)
    assert expected_axis_label not in legend_texts


def test_coverage_splits_one_station_vote_and_preserves_raw_unit_counts():
    """Keep station-balanced and outcome-level Joint denominators distinct."""
    rows = []
    rows.extend(
        ("A1AAA", "AA00", f"2026-07-01T00:{minute:02d}Z", "joint", 1.0, True)
        for minute in range(9)
    )
    rows.append(
        ("A1AAA", "AA00", "2026-07-01T00:09Z", "target_only", np.nan, True)
    )
    rows.append(
        ("B2BBB", "BB00", "2026-07-01T00:10Z", "joint", -1.0, True)
    )
    rows.append(
        (
            "B2BBB",
            "BB00",
            "2026-07-01T00:11Z",
            "reference_only",
            np.nan,
            True,
        )
    )
    work, start, end = _prepare_compare_coverage_units(
        _canonical_compare_units(rows),
        analysis_start_t="2026-07-01T00:00Z",
        analysis_end_t="2026-07-01T01:00Z",
    )

    chronological = _aggregate_compare_chronological_coverage(
        work,
        start,
        end,
        "1h",
    )
    folded = _aggregate_compare_folded_coverage(work, start, end)

    assert chronological["station_target_votes"][0] == pytest.approx(0.1)
    assert chronological["station_joint_votes"][0] == pytest.approx(1.4)
    assert chronological["station_reference_votes"][0] == pytest.approx(0.5)
    assert (
        chronological["station_target_votes"][0]
        + chronological["station_joint_votes"][0]
        + chronological["station_reference_votes"][0]
    ) == pytest.approx(2.0)
    assert chronological["station_counts"][0] == 2
    assert chronological["unit_target_counts"][0] == 1
    assert chronological["unit_joint_counts"][0] == 10
    assert chronological["unit_reference_counts"][0] == 1
    assert chronological["station_joint_share_pct"][0] == pytest.approx(70.0)
    assert chronological["outcome_joint_share_pct"][0] == pytest.approx(
        100.0 * 10.0 / 12.0
    )
    assert folded["station_joint_share_pct"][0] == pytest.approx(70.0)
    assert folded["outcome_joint_share_pct"][0] == pytest.approx(
        100.0 * 10.0 / 12.0
    )


def test_folded_coverage_uses_represented_date_denominators_and_zero_support():
    """Average support over all represented dates, including empty date-hours."""
    work, start, end = _prepare_compare_coverage_units(
        _canonical_compare_units(
            [
                (
                    "A1AAA",
                    "AA00",
                    "2026-07-01T00:05Z",
                    "joint",
                    1.0,
                    True,
                ),
                (
                    "B2BBB",
                    "BB00",
                    "2026-07-01T00:10Z",
                    "target_only",
                    np.nan,
                    False,
                ),
                (
                    "A1AAA",
                    "AA00",
                    "2026-07-02T01:05Z",
                    "reference_only",
                    np.nan,
                    True,
                ),
            ]
        ),
        analysis_start_t="2026-07-01T00:00Z",
        analysis_end_t="2026-07-03T00:00Z",
    )

    folded = _aggregate_compare_folded_coverage(work, start, end)

    assert folded["represented_utc_date_counts"][0] == 2
    assert folded["station_date_hour_presence_counts"][0] == 2
    assert folded["station_average_support_per_utc_date"][0] == 1.0
    assert folded["station_target_support_per_utc_date"][0] == 0.5
    assert folded["station_joint_support_per_utc_date"][0] == 0.5
    assert folded["station_reference_support_per_utc_date"][0] == 0.0
    assert folded["unit_target_counts_per_utc_date"][0] == 0.5
    assert folded["unit_joint_counts_per_utc_date"][0] == 0.5
    assert folded["unit_reference_counts_per_utc_date"][0] == 0.0
    assert folded["represented_utc_date_counts"][2] == 2
    assert folded["station_average_support_per_utc_date"][2] == 0.0
    assert np.isnan(folded["station_joint_share_pct"][2])
    assert np.isnan(folded["outcome_joint_share_pct"][2])


def test_simultaneous_units_preserve_target_active_gate_asymmetry():
    """Retain Only Reference at a Target-active slot without a same-path Target."""
    time_slot = int(
        pd.Timestamp("2026-07-01T00:00Z").timestamp() // 120
    )
    station_rows = pd.DataFrame(
        {
            "peer_sign": ["A1AAA", "B2BBB", "C3CCC", "D4DDD"],
            "peer_grid": ["AA00", "BB00", "CC00", "DD00"],
            "time_slot": [time_slot] * 4,
            "has_u": [1, 0, 1, 0],
            "has_r": [0, 1, 1, 0],
            "snr_u_norm": [4.0, np.nan, 5.04, np.nan],
            "snr_r_norm": [np.nan, -3.0, 1.01, np.nan],
        }
    )
    identities = station_rows[["peer_sign", "peer_grid"]]

    units = _build_compare_unit_rows(
        station_rows,
        identities,
        is_sequential=False,
    )

    assert dict(zip(units["peer_sign"], units["outcome"])) == {
        "A1AAA": COMPARE_OUTCOME_TARGET_ONLY,
        "B2BBB": COMPARE_OUTCOME_REFERENCE_ONLY,
        "C3CCC": COMPARE_OUTCOME_JOINT,
    }
    assert units.loc[
        units["peer_sign"].eq("C3CCC"),
        "metric",
    ].item() == pytest.approx(4.03)
    assert units["evidence_utc"].nunique() == 1


def test_coverage_keeps_only_station_categories_retained_by_threshold():
    """Align coverage units with thresholded map and Station Insights counts."""
    units = _canonical_compare_units(
        [
            ("A1AAA", "AA00", "2026-07-01T00:00Z", "joint", 1.0, True),
            (
                "A1AAA",
                "AA00",
                "2026-07-01T01:00Z",
                "target_only",
                np.nan,
                True,
            ),
            (
                "A1AAA",
                "AA00",
                "2026-07-01T02:00Z",
                "reference_only",
                np.nan,
                True,
            ),
        ]
    )
    thresholded_station_rows = pd.DataFrame(
        {
            "peer_sign": ["A1AAA"],
            "peer_grid": ["AA00"],
            "spot_count": [3],
            "count_only_u": [0],
            "count_only_r": [4],
        }
    )

    retained = _retain_thresholded_compare_outcomes(
        units,
        thresholded_station_rows,
    )

    assert retained["outcome"].tolist() == [
        COMPARE_OUTCOME_JOINT,
        COMPARE_OUTCOME_REFERENCE_ONLY,
    ]


def test_scheduled_pairs_use_planned_target_time_and_per_side_micro_medians():
    """Reduce scheduled decodes to Joint and one-sided planned-pair outcomes."""
    station_rows = pd.DataFrame(
        {
            "peer_sign": ["A1AAA"] * 7,
            "peer_grid": ["AA00"] * 7,
            "time": pd.to_datetime(
                [
                    "2026-07-01T00:00Z",
                    "2026-07-01T00:00Z",
                    "2026-07-01T00:02Z",
                    "2026-07-01T00:02Z",
                    "2026-07-01T00:10Z",
                    "2026-07-01T00:22Z",
                    "2026-07-01T00:04Z",
                ],
                utc=True,
            ),
            "is_me": [1, 1, 0, 0, 1, 0, 1],
            "stat_val": [1.0, 5.0, -1.0, 3.0, 7.0, 4.0, 99.0],
        }
    )
    identities = station_rows[["peer_sign", "peer_grid"]].drop_duplicates()

    units = _build_compare_unit_rows(
        station_rows,
        identities,
        is_sequential=True,
        tx_ab_repeat_interval_minutes=10,
        tx_ab_target_start_minute=0,
        tx_ab_reference_start_minute=2,
    )

    assert units["outcome"].tolist() == [
        COMPARE_OUTCOME_JOINT,
        COMPARE_OUTCOME_TARGET_ONLY,
        COMPARE_OUTCOME_REFERENCE_ONLY,
    ]
    assert units["evidence_utc"].tolist() == list(
        pd.to_datetime(
            [
                "2026-07-01T00:00Z",
                "2026-07-01T00:10Z",
                "2026-07-01T00:20Z",
            ],
            utc=True,
        )
    )
    assert units["metric"].iloc[0] == 2.0
    assert units["metric"].iloc[1:].isna().all()


@pytest.mark.parametrize("language", ("en", "de"))
def test_selected_path_coverage_recipe_renders_only_comparison_unit_row(
    language,
):
    """Do not duplicate station support when the selected population is one path."""
    units = _canonical_compare_units(
        [
            ("A1AAA", "AA00", "2026-07-01T00:00Z", "joint", 1.0, True),
            (
                "A1AAA",
                "AA00",
                "2026-07-01T01:00Z",
                "target_only",
                np.nan,
                True,
            ),
            ("A1AAA", "AA00", "2026-07-02T00:00Z", "joint", 2.0, True),
            (
                "A1AAA",
                "AA00",
                "2026-07-02T01:00Z",
                "reference_only",
                np.nan,
                True,
            ),
            ("A1AAA", "AA00", "2026-07-02T02:00Z", "joint", 3.0, True),
        ]
    )
    recipe = _coverage_recipe(
        units,
        start="2026-07-01T00:00Z",
        end="2026-07-03T00:00Z",
        population_mode=SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION,
    )
    recipe["labels"]["gate_note"] = T[language][
        "fig_compare_coverage_gate_simultaneous"
    ]
    recipe["labels"]["joint_share_y"] = T[language][
        "fig_compare_joint_share_y"
    ]
    recipe["labels"]["selected_joint_share"] = T[language][
        "fig_selected_compare_joint_share"
    ]
    recipe["labels"]["selected_chronological_title"] = T[language][
        "fig_selected_compare_coverage_chronological_title"
    ]
    recipe["labels"]["selected_utc_hour_title"] = T[language][
        "fig_selected_compare_coverage_utc_hour_title"
    ]
    recipe["labels"]["selected_title_unit"] = T[language][
        "fig_selected_compare_coverage_unit_simultaneous"
    ]
    recipe["labels"]["selected_unit_y"] = T[language][
        "fig_selected_compare_coverage_unit_y_simultaneous"
    ]
    recipe["labels"]["selected_unit_folded_y"] = T[language][
        "fig_selected_compare_coverage_unit_folded_y_simultaneous"
    ]

    assert recipe["kind"] == COMPARE_SELECTED_PATH_COVERAGE_RECIPE_KIND
    assert recipe["comparison_unit_count"] == 5
    assert recipe["paired_comparison_unit_count"] == 3
    assert {
        "selected_chronological_subtitle",
        "selected_folded_subtitle",
        "selected_summary",
    }.isdisjoint(recipe["labels"])
    assert {
        "fig_selected_compare_coverage_chronological_subtitle",
        "fig_selected_compare_coverage_folded_subtitle",
        "fig_selected_compare_coverage_summary",
    }.isdisjoint(T[language])

    figure = render_selected_compare_coverage_export_figure(recipe)
    try:
        axis_gids = {
            axis.get_gid() for axis in figure.axes if axis.get_gid()
        }
        assert {
            "selected-compare-coverage-chronological-axis",
            "selected-compare-coverage-folded-axis",
            "compare-temporal-selected-outcome-chronological-share-axis",
            "compare-temporal-selected-outcome-folded-share-axis",
        }.issubset(axis_gids)
        assert not any("station" in gid for gid in axis_gids)
        assert not any(
            gid.startswith("compare-temporal-unit-")
            for gid in axis_gids
        )
        assert tuple(figure.get_size_inches()) == pytest.approx((13.0, 5.6))
        _assert_compare_coverage_header_layout(
            figure,
            header_gids=(
                "selected-compare-coverage-chronological-header",
                "selected-compare-coverage-folded-header",
            ),
        )
        assert _figure_artist_with_gid(
            figure,
            "selected-compare-coverage-chronological-header",
        ).get_text() == T[language][
            "fig_selected_compare_coverage_chronological_title"
        ].format(
            unit=T[language][
                "fig_selected_compare_coverage_unit_simultaneous"
            ],
            time_bin="1 h",
        )
        assert _figure_artist_with_gid(
            figure,
            "selected-compare-coverage-folded-header",
        ).get_text() == T[language][
            "fig_selected_compare_coverage_utc_hour_title"
        ].format(
            unit=T[language][
                "fig_selected_compare_coverage_unit_simultaneous"
            ],
        )
        assert next(
            axis
            for axis in figure.axes
            if axis.get_gid()
            == "selected-compare-coverage-chronological-axis"
        ).get_ylabel() == T[language][
            "fig_selected_compare_coverage_unit_y_simultaneous"
        ]
        assert next(
            axis
            for axis in figure.axes
            if axis.get_gid()
            == "selected-compare-coverage-folded-axis"
        ).get_ylabel() == T[language][
            "fig_selected_compare_coverage_unit_folded_y_simultaneous"
        ]
        _assert_neighboring_y_labels_do_not_overlap(
            figure,
            axis_gid_pairs=(
                (
                    "compare-temporal-selected-outcome-chronological-share-axis",
                    "selected-compare-coverage-folded-axis",
                ),
            ),
        )
        _assert_folded_y_labels_fit_figure(
            figure,
            folded_axis_gids=(
                "selected-compare-coverage-folded-axis",
            ),
            header_gids=(
                "selected-compare-coverage-chronological-header",
                "selected-compare-coverage-folded-header",
            ),
        )
        rendered_text_gids = {
            artist.get_gid()
            for artist in (
                *figure.texts,
                *(
                    text_artist
                    for axis in figure.axes
                    for text_artist in axis.texts
                ),
            )
            if artist.get_gid()
        }
        assert {
            "selected-compare-coverage-chronological-subtitle",
            "selected-compare-coverage-folded-subtitle",
            "selected-compare-coverage-summary",
        }.isdisjoint(rendered_text_gids)
        _assert_compare_coverage_note_is_in_footer(
            figure,
            primary_axis_gids=(
                "selected-compare-coverage-chronological-axis",
                "selected-compare-coverage-folded-axis",
            ),
        )
        _assert_compare_coverage_footer_typography(
            figure,
            T[language]["fig_compare_coverage_gate_simultaneous"],
        )
        _assert_compare_coverage_share_labels(
            figure,
            expected_axis_label=T[language][
                "fig_compare_joint_share_y"
            ],
            expected_legend_labels=(
                T[language]["fig_selected_compare_joint_share"],
            ),
        )
        _assert_compare_coverage_outcome_order(
            figure,
            primary_axis_gids=(
                "selected-compare-coverage-chronological-axis",
                "selected-compare-coverage-folded-axis",
            ),
            labels=recipe["labels"],
        )
    finally:
        dispose_matplotlib_figure(figure)


@pytest.mark.parametrize("language", ("en", "de"))
def test_selected_scheduled_coverage_names_pairs_in_titles_and_y_axes(
    language,
):
    """Keep scheduled A/B units distinct from simultaneous WSPR cycles."""
    units = _canonical_compare_units(
        [
            ("A1AAA", "AA00", "2026-07-01T00:00Z", "joint", 1.0, True),
            (
                "A1AAA",
                "AA00",
                "2026-07-01T01:00Z",
                "target_only",
                np.nan,
                True,
            ),
            ("A1AAA", "AA00", "2026-07-02T00:00Z", "joint", 2.0, True),
            (
                "A1AAA",
                "AA00",
                "2026-07-02T01:00Z",
                "reference_only",
                np.nan,
                True,
            ),
        ]
    )
    recipe = _coverage_recipe(
        units,
        start="2026-07-01T00:00Z",
        end="2026-07-03T00:00Z",
        population_mode=SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION,
    )
    translations = T[language]
    recipe["labels"].update(
        {
            "gate_note": translations[
                "fig_compare_coverage_gate_scheduled"
            ],
            "joint_share_y": translations["fig_compare_joint_share_y"],
            "selected_joint_share": translations[
                "fig_selected_compare_joint_share"
            ],
            "selected_chronological_title": translations[
                "fig_selected_compare_coverage_chronological_title"
            ],
            "selected_utc_hour_title": translations[
                "fig_selected_compare_coverage_utc_hour_title"
            ],
            "selected_title_unit": translations[
                "fig_selected_compare_coverage_unit_scheduled"
            ],
            "selected_unit_y": translations[
                "fig_compare_coverage_unit_y_scheduled"
            ],
            "selected_unit_folded_y": translations[
                "fig_compare_coverage_unit_folded_y_scheduled"
            ],
        }
    )

    figure = render_selected_compare_coverage_export_figure(recipe)
    try:
        _assert_compare_coverage_header_layout(
            figure,
            header_gids=(
                "selected-compare-coverage-chronological-header",
                "selected-compare-coverage-folded-header",
            ),
        )
        assert _figure_artist_with_gid(
            figure,
            "selected-compare-coverage-chronological-header",
        ).get_text() == translations[
            "fig_selected_compare_coverage_chronological_title"
        ].format(
            unit=translations[
                "fig_selected_compare_coverage_unit_scheduled"
            ],
            time_bin="1 h",
        )
        assert _figure_artist_with_gid(
            figure,
            "selected-compare-coverage-folded-header",
        ).get_text() == translations[
            "fig_selected_compare_coverage_utc_hour_title"
        ].format(
            unit=translations[
                "fig_selected_compare_coverage_unit_scheduled"
            ],
        )
        assert next(
            axis
            for axis in figure.axes
            if axis.get_gid()
            == "selected-compare-coverage-chronological-axis"
        ).get_ylabel() == translations[
            "fig_compare_coverage_unit_y_scheduled"
        ]
        assert next(
            axis
            for axis in figure.axes
            if axis.get_gid()
            == "selected-compare-coverage-folded-axis"
        ).get_ylabel() == translations[
            "fig_compare_coverage_unit_folded_y_scheduled"
        ]
        _assert_neighboring_y_labels_do_not_overlap(
            figure,
            axis_gid_pairs=(
                (
                    "compare-temporal-selected-outcome-chronological-share-axis",
                    "selected-compare-coverage-folded-axis",
                ),
            ),
        )
        _assert_folded_y_labels_fit_figure(
            figure,
            folded_axis_gids=(
                "selected-compare-coverage-folded-axis",
            ),
            header_gids=(
                "selected-compare-coverage-chronological-header",
                "selected-compare-coverage-folded-header",
            ),
        )
        note = _assert_compare_coverage_note_is_in_footer(
            figure,
            primary_axis_gids=(
                "selected-compare-coverage-chronological-axis",
                "selected-compare-coverage-folded-axis",
            ),
        )
        assert note.get_text() == translations[
            "fig_compare_coverage_gate_scheduled"
        ]
    finally:
        dispose_matplotlib_figure(figure)


@pytest.mark.parametrize("language", ("en", "de"))
def test_segment_coverage_recipe_accepts_minimal_units_and_renders(language):
    """Render coverage without retired paired-metric or baseline inputs."""
    units = _canonical_compare_units(
        [
            ("A1AAA", "AA00", "2026-07-01T00:00Z", "joint", 1.0, True),
            ("A1AAA", "AA00", "2026-07-01T01:00Z", "joint", 2.0, True),
            ("A1AAA", "AA00", "2026-07-02T00:00Z", "joint", 4.0, True),
            (
                "A1AAA",
                "AA00",
                "2026-07-02T01:00Z",
                "target_only",
                np.nan,
                True,
            ),
            (
                "B2BBB",
                "BB00",
                "2026-07-01T00:00Z",
                "reference_only",
                np.nan,
                False,
            ),
        ]
    )
    recipe = _coverage_recipe(
        units[["peer_sign", "peer_grid", "evidence_utc", "outcome"]],
        start="2026-07-01T00:00Z",
        end="2026-07-03T00:00Z",
    )
    recipe["labels"]["gate_note"] = T[language][
        "fig_compare_coverage_gate_simultaneous"
    ]
    recipe["labels"]["joint_share_y"] = T[language][
        "fig_compare_joint_share_y"
    ]
    recipe["labels"]["station_joint_share"] = T[language][
        "fig_compare_joint_share_station"
    ]
    recipe["labels"]["outcome_joint_share"] = T[language][
        "fig_compare_joint_share_outcome"
    ]
    recipe["labels"]["station_vote_y"] = T[language][
        "fig_compare_coverage_station_y_rx"
    ]
    recipe["labels"]["station_folded_y"] = T[language][
        "fig_compare_coverage_station_folded_y_rx"
    ]
    recipe["labels"]["unit_y"] = T[language][
        "fig_compare_coverage_unit_y_rx"
    ]
    recipe["labels"]["unit_folded_y"] = T[language][
        "fig_compare_coverage_unit_folded_y_rx"
    ]

    assert recipe["kind"] == COMPARE_TEMPORAL_COVERAGE_RECIPE_KIND
    assert recipe["schema_version"] == 1
    assert not any(key.startswith("snr_") for key in recipe)
    assert "reference_snr_correction_notice" not in recipe
    assert "absolute_mode" not in recipe
    assert "is_sequential" not in recipe
    assert "selected_station_summary" not in recipe
    assert {
        "temporal_unavailable",
        "coverage_unavailable",
        "selected_utc_hour_subtitle",
    }.isdisjoint(recipe["labels"])

    coverage_figure = render_compare_temporal_coverage_export_figure(recipe)
    try:
        coverage_axis_gids = {
            axis.get_gid()
            for axis in coverage_figure.axes
            if axis.get_gid()
        }
        assert {
            "compare-temporal-station-chronological-axis",
            "compare-temporal-unit-chronological-axis",
            "compare-temporal-station-folded-axis",
            "compare-temporal-unit-folded-axis",
        }.issubset(coverage_axis_gids)
        assert tuple(coverage_figure.get_size_inches()) == pytest.approx(
            (13.0, 5.6)
        )
        _assert_compare_coverage_header_layout(
            coverage_figure,
            header_gids=(
                "compare-temporal-coverage-chronological-column-header",
                "compare-temporal-coverage-folded-column-header",
            ),
        )
        rendered_text_gids = {
            artist.get_gid()
            for artist in (
                *coverage_figure.texts,
                *(
                    text_artist
                    for axis in coverage_figure.axes
                    for text_artist in axis.texts
                ),
            )
            if artist.get_gid()
        }
        assert "reference-snr-correction-notice" not in rendered_text_gids
        assert {
            "compare-temporal-station-folded-subtitle",
            "compare-temporal-unit-folded-subtitle",
        }.isdisjoint(rendered_text_gids)
        expected_y_labels = {
            "compare-temporal-station-chronological-axis": T[language][
                "fig_compare_coverage_station_y_rx"
            ],
            "compare-temporal-unit-chronological-axis": T[language][
                "fig_compare_coverage_unit_y_rx"
            ],
            "compare-temporal-station-folded-axis": T[language][
                "fig_compare_coverage_station_folded_y_rx"
            ],
            "compare-temporal-unit-folded-axis": T[language][
                "fig_compare_coverage_unit_folded_y_rx"
            ],
        }
        for axis_gid, expected_y_label in expected_y_labels.items():
            assert next(
                axis
                for axis in coverage_figure.axes
                if axis.get_gid() == axis_gid
            ).get_ylabel() == expected_y_label
        _assert_neighboring_y_labels_do_not_overlap(
            coverage_figure,
            axis_gid_pairs=(
                (
                    "compare-temporal-station-balanced-chronological-share-axis",
                    "compare-temporal-station-folded-axis",
                ),
                (
                    "compare-temporal-outcome-level-chronological-share-axis",
                    "compare-temporal-unit-folded-axis",
                ),
            ),
        )
        _assert_folded_y_labels_fit_figure(
            coverage_figure,
            folded_axis_gids=(
                "compare-temporal-station-folded-axis",
                "compare-temporal-unit-folded-axis",
            ),
            header_gids=(
                "compare-temporal-coverage-chronological-column-header",
                "compare-temporal-coverage-folded-column-header",
            ),
        )
        _assert_compare_coverage_note_is_in_footer(
            coverage_figure,
            primary_axis_gids=(
                "compare-temporal-station-chronological-axis",
                "compare-temporal-unit-chronological-axis",
                "compare-temporal-station-folded-axis",
                "compare-temporal-unit-folded-axis",
            ),
        )
        _assert_compare_coverage_footer_typography(
            coverage_figure,
            T[language]["fig_compare_coverage_gate_simultaneous"],
        )
        _assert_compare_coverage_share_labels(
            coverage_figure,
            expected_axis_label=T[language][
                "fig_compare_joint_share_y"
            ],
            expected_legend_labels=(
                T[language]["fig_compare_joint_share_station"],
                T[language]["fig_compare_joint_share_outcome"],
            ),
        )
        _assert_compare_coverage_outcome_order(
            coverage_figure,
            primary_axis_gids=(
                "compare-temporal-station-chronological-axis",
                "compare-temporal-unit-chronological-axis",
                "compare-temporal-station-folded-axis",
                "compare-temporal-unit-folded-axis",
            ),
            labels=recipe["labels"],
        )
    finally:
        dispose_matplotlib_figure(coverage_figure)


def test_selected_coverage_shortens_plot_area_without_resizing_canvas():
    """Shorten only the selected-path plot grid while retaining export size."""
    units = _canonical_compare_units(
        [
            ("A1AAA", "AA00", "2026-07-01T00:00Z", "joint", 1.0, True),
            (
                "A1AAA",
                "AA00",
                "2026-07-01T01:00Z",
                "target_only",
                np.nan,
                True,
            ),
            ("A1AAA", "AA00", "2026-07-02T00:00Z", "joint", 2.0, True),
            (
                "A1AAA",
                "AA00",
                "2026-07-02T01:00Z",
                "reference_only",
                np.nan,
                True,
            ),
        ]
    )
    segment_recipe = _coverage_recipe(
        units,
        start="2026-07-01T00:00Z",
        end="2026-07-03T00:00Z",
    )
    selected_recipe = _coverage_recipe(
        units,
        start="2026-07-01T00:00Z",
        end="2026-07-03T00:00Z",
        population_mode=SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION,
    )
    assert "reference_snr_correction_notice" not in segment_recipe
    assert "reference_snr_correction_notice" not in selected_recipe

    segment_figure = render_compare_temporal_coverage_export_figure(
        segment_recipe
    )
    selected_figure = render_selected_compare_coverage_export_figure(
        selected_recipe
    )
    try:
        assert not any(
            artist.get_gid() == "reference-snr-correction-notice"
            for figure in (segment_figure, selected_figure)
            for artist in figure.texts
        )
        assert tuple(segment_figure.get_size_inches()) == pytest.approx(
            (13.0, 5.6)
        )
        assert tuple(selected_figure.get_size_inches()) == pytest.approx(
            tuple(segment_figure.get_size_inches())
        )
        selected_primary_axes = [
            axis
            for axis in selected_figure.axes
            if axis.get_gid()
            in {
                "selected-compare-coverage-chronological-axis",
                "selected-compare-coverage-folded-axis",
            }
        ]
        segment_primary_axes = [
            axis
            for axis in segment_figure.axes
            if axis.get_gid()
            in {
                "compare-temporal-station-chronological-axis",
                "compare-temporal-unit-chronological-axis",
                "compare-temporal-station-folded-axis",
                "compare-temporal-unit-folded-axis",
            }
        ]
        selected_plot_top = max(
            axis.get_position().y1 for axis in selected_primary_axes
        )
        selected_plot_bottom = min(
            axis.get_position().y0 for axis in selected_primary_axes
        )
        segment_plot_top = max(
            axis.get_position().y1 for axis in segment_primary_axes
        )
        segment_plot_bottom = min(
            axis.get_position().y0 for axis in segment_primary_axes
        )
        assert selected_plot_top == pytest.approx(segment_plot_top)
        assert selected_plot_bottom > segment_plot_bottom
        assert (
            selected_plot_top - selected_plot_bottom
            < segment_plot_top - segment_plot_bottom
        )
    finally:
        dispose_matplotlib_figure(segment_figure)
        dispose_matplotlib_figure(selected_figure)


def test_retired_compare_views_have_no_scientific_or_renderer_symbols():
    """Prevent the removed baseline-change and path-consistency views returning."""
    retired_symbols = (
        "COMPARE_DELTA_BASELINE_VERSION",
        "COMPARE_MINIMUM_DELTA_BASELINE_OBSERVATIONS",
        "COMPARE_PATH_CONSISTENCY_MINIMUM_OBSERVATIONS",
        "COMPARE_PATH_SIMILARITY_THRESHOLD_DB",
        "COMPARE_PATH_MARKER_MIN_AREA",
        "COMPARE_PATH_MARKER_MAX_AREA",
        "COMPARE_TEMPORAL_RECIPE_KIND",
        "COMPARE_SELECTED_TEMPORAL_RECIPE_KIND",
        "_compare_temporal_recipe",
        "_prepare_compare_temporal_units",
        "_prepare_compare_delta_changes",
        "_compare_path_consistency_recipe",
        "_compare_path_marker_areas",
        "render_compare_delta_change_export_figure",
        "render_compare_path_consistency_export_figure",
    )

    assert not any(
        hasattr(compare_evidence_figures, symbol)
        for symbol in retired_symbols
    )


def test_joint_projection_preserves_existing_absolute_delta_snr_contract():
    """Keep the established absolute Delta-SNR rows unchanged by canonical units."""
    time_slot = int(
        pd.Timestamp("2026-07-01T00:00Z").timestamp() // 120
    )
    station_rows = pd.DataFrame(
        {
            "peer_sign": ["A1AAA", "A1AAA", "B2BBB"],
            "peer_grid": ["AA00", "AA00", "BB00"],
            "time_slot": [time_slot, time_slot + 1, time_slot],
            "has_u": [1, 1, 1],
            "has_r": [1, 1, 0],
            "snr_u_norm": [5.04, -1.04, 9.0],
            "snr_r_norm": [2.01, -2.08, np.nan],
        }
    )
    identities = station_rows[["peer_sign", "peer_grid"]].drop_duplicates()

    comparison_units = _build_compare_unit_rows(
        station_rows,
        identities,
        is_sequential=False,
    )
    assert comparison_units.loc[
        comparison_units["outcome"].eq(COMPARE_OUTCOME_JOINT),
        "metric",
    ].tolist() == pytest.approx([3.03, 1.04])
    projected = _compare_joint_evidence_points(comparison_units)
    wrapper_result = _build_evidence_points(
        station_rows,
        identities,
        is_sequential=False,
    )

    pd.testing.assert_frame_equal(projected, wrapper_result)
    assert list(projected.columns) == [
        "identity",
        "station",
        "grid",
        "identity_order",
        "plot_time",
        "metric",
    ]
    assert projected["station"].tolist() == ["A1AAA", "A1AAA"]
    assert projected["metric"].tolist() == [3.0, 1.0]
    assert projected["plot_time"].tolist() == list(
        pd.to_datetime(
            ["2026-07-01T00:00Z", "2026-07-01T00:02Z"],
            utc=True,
        )
    )


def test_absolute_projection_keeps_legacy_nonmissing_infinite_metric():
    """Preserve the established absolute projection of nonmissing infinity."""
    units = _canonical_compare_units(
        [
            ("A1AAA", "AA00", "2026-07-01T00:00Z", "joint", np.inf, True),
            ("A1AAA", "AA00", "2026-07-01T00:02Z", "joint", np.nan, True),
        ]
    )

    projected = _compare_joint_evidence_points(units)

    assert len(projected) == 1
    assert np.isposinf(projected["metric"].iloc[0])


def test_contributor_language_distinguishes_visible_and_compatibility_terms():
    """Keep the mandatory contributor-language correction narrow and explicit."""
    repository_root = Path(__file__).resolve().parents[2]
    contributor_text = (
        repository_root / "AGENTS.md"
    ).read_text(encoding="utf-8")

    assert "visible Performance and Compare paths" in contributor_text
    assert "canonical `success` compatibility paths" in contributor_text
    assert "within-path consistency" in contributor_text
    assert "experimental repeatability" in contributor_text
    assert "Joint Evidence Share" in contributor_text
    assert "pairability or coverage metric" in contributor_text
    assert "Decode Rate" in contributor_text
    for stale_phrase in (
        "Compare/Success",
        "Success Rate",
        "Success and Compare results",
        "Success classification",
    ):
        assert stale_phrase not in contributor_text
