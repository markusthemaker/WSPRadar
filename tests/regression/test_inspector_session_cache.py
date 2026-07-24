from types import SimpleNamespace

import pandas as pd

from i18n import T
from ui.components import segment_inspector
from ui.inspector import view_models
from ui.inspector.session_cache import (
    SessionInspectorCache,
    estimate_cache_value_bytes,
)


def _cache(*, max_bytes=64, limits=None, run_id=7):
    return SessionInspectorCache(
        run_id,
        max_bytes=max_bytes,
        namespace_limits=limits or {"segment": 2, "selected": 2, "png": 2},
    )


def test_compare_segment_summary_reports_distribution_median_and_mean():
    """Show the exact plotted station and joint-spot distribution summaries."""
    station_summary = segment_inspector._compare_metric_distribution_summary(
        [-8.0, -5.0, -4.0, 2.0],
        T["en"]["fmt_results_station_delta_summary"],
    )
    spot_summary = segment_inspector._compare_metric_distribution_summary(
        [-10.0, -7.0, -6.0, 1.0],
        T["en"]["fmt_results_joint_spot_delta_summary"],
    )

    assert segment_inspector._segment_summary_lines(
        station_summary=station_summary,
        spot_summary=spot_summary,
    ) == [
        "Station-level - Median -4.5 dB - Mean -3.8 dB",
        "Joint-Spot level - Median -6.5 dB - Mean -5.5 dB",
    ]


def test_compare_segment_summary_uses_localized_scheduled_pair_wording():
    """Keep sequential TX A/B summaries distinct from simultaneous joint spots."""
    summary = segment_inspector._compare_metric_distribution_summary(
        [1.0, 2.0, 6.0],
        T["de"]["fmt_results_scheduled_pair_delta_summary"],
    )

    assert summary == (
        "Ebene geplanter Paare - Median +2.0 dB - Mittelwert +3.0 dB"
    )
    assert segment_inspector._compare_metric_distribution_summary(
        [],
        T["en"]["fmt_results_joint_spot_delta_summary"],
    ) is None


def test_metric_summary_retains_median_without_stability_interval():
    """Keep Success median context after removing inferential intervals."""
    station_summary = segment_inspector._metric_median_summary(
        [-12.0, -8.0, -6.0],
        False,
        "Station-median",
    )
    compare_summary = segment_inspector._metric_median_summary(
        [-2.0, 1.0],
        True,
        "Joint-spot",
    )

    assert station_summary == "Station-median | median SNR -8.0 dB"
    assert compare_summary == "Joint-spot | median Δ SNR -0.5 dB"
    assert "stability" not in station_summary.lower()
    assert segment_inspector._metric_median_summary([], False, "Spot") is None
    assert not hasattr(segment_inspector, "STABILITY_CACHE_STATE_KEY")
    assert not hasattr(segment_inspector, "_cached_segment_stability")


def test_folded_utc_hour_panel_title_is_completely_localized():
    """Keep the fixed-bin suffix consistent with each language's manual."""
    assert segment_inspector._folded_utc_hour_panel_title(T["en"]) == (
        "\u0394 SNR by UTC Hour (1 h bins)"
    )
    assert segment_inspector._folded_utc_hour_panel_title(T["de"]) == (
        "\u0394 SNR nach UTC-Stunde (1-h-Bins)"
    )


def test_selected_temporal_controls_fit_one_horizontal_row():
    """Keep short mode labels beside a bin group with twice the available width."""
    assert T["en"]["opt_temporal_utc_hour"] == "UTC-Hour"
    assert T["en"]["opt_temporal_chronological"] == "Chronological"
    assert T["de"]["opt_temporal_utc_hour"] == "UTC-Stunde"
    assert segment_inspector.SELECTED_TEMPORAL_CONTROL_COLUMN_WIDTHS == (1, 2)


def test_segment_temporal_controls_have_localized_inline_labels():
    """Name the adaptive segment bins without changing selected-station controls."""
    assert T["en"]["lbl_time_aggregation_bin_size"] == (
        "Time aggregation bin size:"
    )
    assert T["de"]["lbl_time_aggregation_bin_size"] == (
        "Zeitliche Aggregationsbreite:"
    )
    assert T["en"]["lbl_include_unpaired_evidence"] == (
        "Include Unpaired Evidence"
    )
    assert T["de"]["lbl_include_unpaired_evidence"] == (
        "Ungepaarte Evidenz einbeziehen"
    )
    assert segment_inspector.SEGMENT_TEMPORAL_CONTROL_COLUMN_WIDTHS == (1.6, 4)


def test_station_insights_toggle_has_room_for_single_line_label():
    """Keep the unpaired-evidence toggle left of a full-width filter control."""
    title_width, toggle_width, filter_width = (
        segment_inspector.STATION_INSIGHTS_CONTROL_COLUMN_WIDTHS
    )

    assert (title_width, toggle_width, filter_width) == (5, 4, 3)
    assert toggle_width > filter_width


def test_unpaired_compare_selection_keeps_selected_evidence_level(monkeypatch):
    """Keep level 04 visible when only retained non-joint rows can be audited."""
    markdown_calls = []
    monkeypatch.setattr(
        segment_inspector,
        "st",
        SimpleNamespace(
            session_state={"lang": "en"},
            markdown=lambda body, **_kwargs: markdown_calls.append(body),
        ),
    )
    monkeypatch.setattr(
        segment_inspector,
        "_inspector_cache_get",
        lambda *_args, **_kwargs: (None, False),
    )
    monkeypatch.setattr(
        segment_inspector,
        "_build_evidence_points",
        lambda *_args, **_kwargs: pd.DataFrame(),
    )

    result = segment_inspector._render_selected_station_evidence(
        pd.DataFrame({"peer_sign": ["G3AAA"], "peer_grid": ["IO90"]}),
        pd.DataFrame({"peer_sign": ["G3AAA"], "peer_grid": ["IO90"]}),
        True,
        False,
        10,
        0,
        2,
        t=T["en"],
        analysis_id="RX_COMP",
        run_id=7,
        scope_token="all",
        cache_key=("selected",),
    )

    rendered_markup = "".join(markdown_calls)
    assert result is None
    assert "04 · SELECTED STATIONS" not in rendered_markup
    assert (
        "aria-label='04 · Selected stations: Selected Station Evidence'"
        in rendered_markup
    )
    assert "Selected Station Evidence" in rendered_markup
    assert "G3AAA (IO90) · 0 joint spots" in rendered_markup
    assert T["en"]["txt_results_selected_no_paired_evidence"] in rendered_markup


def test_segment_temporal_title_distinguishes_rx_and_tx_compare_figures():
    """Keep the compact temporal title scoped without repeating an outer heading."""
    labels = {
        "fig_rx_comp_temporal_prefix": "RX Compare Temporal",
        "fig_tx_comp_temporal_prefix": "TX Compare Temporal",
    }

    assert segment_inspector._segment_temporal_figure_title(
        "RX Compare: G3ZIL (Target) vs. G4HZX (Reference)",
        "RX_COMP",
        "[5000-10000km] | WNW",
        labels,
    ) == (
        "RX Compare Temporal: G3ZIL (Target) vs. G4HZX (Reference) - "
        "[5000-10000km] | WNW"
    )
    assert segment_inspector._segment_temporal_figure_title(
        "TX Compare: G3ZIL (Target) vs. G4HZX (Reference)",
        "TX_COMP",
        "Full Range | All Directions",
        labels,
    ).startswith("TX Compare Temporal:")


def test_long_range_evidence_bins_include_one_and_two_hour_choices():
    """Expose one shared hourly selector beyond 24 h through the 31-day limit."""
    expected_options = ["1h", "2h", "3h", "6h", "12h", "24h"]
    start = pd.Timestamp("2017-04-01T00:00:00Z")

    seven_day_options, seven_day_default = (
        segment_inspector._time_agg_options_for_span(
            pd.DataFrame(
                {"plot_time": [start, start + pd.Timedelta(days=7)]}
            )
        )
    )
    maximum_options, maximum_default = segment_inspector._time_agg_options_for_span(
        pd.DataFrame(
            {"plot_time": [start, start + pd.Timedelta(days=31)]}
        )
    )

    assert seven_day_options == expected_options
    assert seven_day_default == "3h"
    assert maximum_options == expected_options
    assert maximum_default == "6h"


def test_evidence_bins_keep_minute_scale_choices_through_24_hours():
    """Do not replace the existing fine-grained policy for short analyses."""
    start = pd.Timestamp("2017-04-01T00:00:00Z")

    six_hour_options, six_hour_default = segment_inspector._time_agg_options_for_span(
        pd.DataFrame(
            {"plot_time": [start, start + pd.Timedelta(hours=6)]}
        )
    )
    day_options, day_default = segment_inspector._time_agg_options_for_span(
        pd.DataFrame(
            {"plot_time": [start, start + pd.Timedelta(hours=24)]}
        )
    )

    assert six_hour_options == ["5m", "15m", "30m", "1h", "3h"]
    assert six_hour_default == "15m"
    assert day_options == ["15m", "30m", "1h", "3h", "6h"]
    assert day_default == "30m"


def test_time_bin_control_stretches_segmented_options_across_container(monkeypatch):
    """Keep Segment Compare and Success time selectors compact and full-width."""
    captured = {}

    def segmented_control(label, options, **kwargs):
        captured.update(label=label, options=list(options), kwargs=kwargs)
        return "3h"

    monkeypatch.setattr(
        segment_inspector,
        "st",
        SimpleNamespace(segmented_control=segmented_control),
    )

    def callback():
        return None

    assert segment_inspector._render_stretched_time_bin_control(
        "Time aggregation",
        ["1h", "2h", "3h", "6h", "12h", "24h"],
        "time_widget",
        on_change=callback,
        on_change_args=("canonical",),
    ) == "3h"
    assert captured == {
        "label": "Time aggregation",
        "options": ["1h", "2h", "3h", "6h", "12h", "24h"],
        "kwargs": {
            "key": "time_widget",
            "label_visibility": "collapsed",
            "width": "stretch",
            "on_change": callback,
            "args": ("canonical",),
        },
    }


def test_segment_time_bin_label_renders_immediately_before_selector(monkeypatch):
    """Keep the localized explanation and adaptive choices on one desktop row."""
    events = []

    class _Column:
        def __init__(self, name):
            self.name = name

        def __enter__(self):
            events.append(("enter", self.name))
            return self

        def __exit__(self, *_args):
            events.append(("exit", self.name))

    def columns(widths, **kwargs):
        events.append(("columns", tuple(widths), kwargs))
        return _Column("label"), _Column("selector")

    def markdown(body):
        events.append(("markdown", body))

    def segmented_control(label, options, **kwargs):
        events.append(("segmented_control", label, tuple(options), kwargs))
        return "3h"

    monkeypatch.setattr(
        segment_inspector,
        "st",
        SimpleNamespace(
            columns=columns,
            markdown=markdown,
            segmented_control=segmented_control,
        ),
    )

    selected = segment_inspector._render_labeled_segment_time_bin_control(
        T["en"]["lbl_time_aggregation_bin_size"],
        ["1h", "2h", "3h", "6h", "12h", "24h"],
        "segment_time_widget",
    )

    assert selected == "3h"
    assert events[0] == (
        "columns",
        segment_inspector.SEGMENT_TEMPORAL_CONTROL_COLUMN_WIDTHS,
        {"vertical_alignment": "center"},
    )
    assert events[1:4] == [
        ("enter", "label"),
        ("markdown", "**Time aggregation bin size:**"),
        ("exit", "label"),
    ]
    assert events[4] == ("enter", "selector")
    assert events[5][0:3] == (
        "segmented_control",
        "Time aggregation bin size:",
        ("1h", "2h", "3h", "6h", "12h", "24h"),
    )


def test_time_bin_widget_uses_valid_canonical_value_and_syncs_interaction(monkeypatch):
    session_state = {
        segment_inspector.RESULTS_TIME_BIN_COMPARE_STATE_KEY: "6h",
        "time_widget": "3h",
    }
    monkeypatch.setattr(segment_inspector, "st", SimpleNamespace(session_state=session_state))

    selected = segment_inspector._initialize_time_bin_widget_state(
        "time_widget",
        segment_inspector.RESULTS_TIME_BIN_COMPARE_STATE_KEY,
        ["3h", "6h"],
        "3h",
    )

    assert selected == "6h"
    assert session_state["time_widget"] == "6h"

    session_state["time_widget"] = "3h"
    assert segment_inspector._sync_time_bin_widget_state(
        "time_widget",
        segment_inspector.RESULTS_TIME_BIN_COMPARE_STATE_KEY,
        ["3h", "6h"],
        "3h",
    ) == "3h"
    assert session_state[segment_inspector.RESULTS_TIME_BIN_COMPARE_STATE_KEY] == "3h"


def test_time_bin_widget_falls_back_deterministically_when_option_is_unavailable(
    monkeypatch,
):
    session_state = {
        segment_inspector.RESULTS_TIME_BIN_ABSOLUTE_STATE_KEY: "5m",
    }
    monkeypatch.setattr(segment_inspector, "st", SimpleNamespace(session_state=session_state))

    assert segment_inspector._initialize_time_bin_widget_state(
        "time_widget",
        segment_inspector.RESULTS_TIME_BIN_ABSOLUTE_STATE_KEY,
        ["30m", "1h"],
        "1h",
    ) == "1h"
    assert session_state[segment_inspector.RESULTS_TIME_BIN_ABSOLUTE_STATE_KEY] == "1h"

    session_state["time_widget"] = "unsupported"
    assert segment_inspector._sync_time_bin_widget_state(
        "time_widget",
        segment_inspector.RESULTS_TIME_BIN_ABSOLUTE_STATE_KEY,
        ["30m", "1h"],
        "unsupported-default",
    ) == "30m"
    assert session_state[segment_inspector.RESULTS_TIME_BIN_ABSOLUTE_STATE_KEY] == "30m"


def test_segment_time_bin_resolves_auto_and_does_not_change_station_bin(
    monkeypatch,
):
    """Resolve adaptive segment state once without overwriting the station bin."""
    session_state = {
        segment_inspector.RESULTS_TIME_BIN_COMPARE_STATE_KEY: "6h",
        segment_inspector.RESULTS_SEGMENT_TIME_BIN_COMPARE_STATE_KEY: "auto",
        "segment_time_widget": "12h",
    }
    monkeypatch.setattr(
        segment_inspector,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    selected = segment_inspector._initialize_time_bin_widget_state(
        "segment_time_widget",
        segment_inspector.RESULTS_SEGMENT_TIME_BIN_COMPARE_STATE_KEY,
        ["3h", "6h", "12h", "24h"],
        "6h",
    )

    assert selected == "6h"
    assert session_state["segment_time_widget"] == "6h"
    assert (
        session_state[
            segment_inspector.RESULTS_SEGMENT_TIME_BIN_COMPARE_STATE_KEY
        ]
        == "6h"
    )
    assert session_state[segment_inspector.RESULTS_TIME_BIN_COMPARE_STATE_KEY] == "6h"

    session_state["segment_time_widget"] = "12h"
    assert segment_inspector._sync_time_bin_widget_state(
        "segment_time_widget",
        segment_inspector.RESULTS_SEGMENT_TIME_BIN_COMPARE_STATE_KEY,
        ["3h", "6h", "12h", "24h"],
        "6h",
    ) == "12h"
    assert session_state[segment_inspector.RESULTS_TIME_BIN_COMPARE_STATE_KEY] == "6h"


def test_selected_temporal_view_round_trips_and_preserves_chronological_bin(
    monkeypatch,
):
    """Persist the view independently from the saved chronological bin size."""
    session_state = {
        segment_inspector.RESULTS_TIME_BIN_COMPARE_STATE_KEY: "6h",
        segment_inspector.RESULTS_STATION_TEMPORAL_VIEW_COMPARE_STATE_KEY: (
            "utc_hour"
        ),
        "temporal_view_widget": "chronological",
    }
    monkeypatch.setattr(
        segment_inspector,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    selected = segment_inspector._initialize_choice_widget_state(
        "temporal_view_widget",
        segment_inspector.RESULTS_STATION_TEMPORAL_VIEW_COMPARE_STATE_KEY,
        ("chronological", "utc_hour"),
        "chronological",
    )

    assert selected == "utc_hour"
    assert session_state["temporal_view_widget"] == "utc_hour"
    assert session_state[segment_inspector.RESULTS_TIME_BIN_COMPARE_STATE_KEY] == "6h"

    session_state["temporal_view_widget"] = "chronological"
    assert segment_inspector._sync_choice_widget_state(
        "temporal_view_widget",
        segment_inspector.RESULTS_STATION_TEMPORAL_VIEW_COMPARE_STATE_KEY,
        ("chronological", "utc_hour"),
        "chronological",
    ) == "chronological"
    assert (
        session_state[
            segment_inspector.RESULTS_STATION_TEMPORAL_VIEW_COMPARE_STATE_KEY
        ]
        == "chronological"
    )
    assert session_state[segment_inspector.RESULTS_TIME_BIN_COMPARE_STATE_KEY] == "6h"


def test_segment_scope_initializes_from_saved_state_and_syncs_user_changes(
    monkeypatch,
):
    """Keep Compare and Success scope intent outside transient run widget keys."""
    persistent_key = segment_inspector.RESULTS_SELECTED_RANGES_COMPARE_STATE_KEY
    session_state = {
        persistent_key: ["[2500-5000km]", "[5000-10000km]"],
    }
    monkeypatch.setattr(
        segment_inspector,
        "st",
        SimpleNamespace(session_state=session_state),
    )
    specific_options = [
        "[0-2500km]",
        "[2500-5000km]",
        "[5000-10000km]",
    ]

    segment_inspector._initialize_explicit_all_multiselect(
        "range_widget",
        "range_widget_previous",
        "Full Range",
        specific_options,
        persistent_key,
    )

    assert session_state["range_widget"] == [
        "[2500-5000km]",
        "[5000-10000km]",
    ]
    session_state["range_widget"] = ["Full Range"]
    segment_inspector._update_explicit_all_multiselect(
        "range_widget",
        "range_widget_previous",
        "Full Range",
        specific_options,
        persistent_key,
    )
    assert session_state[persistent_key] == "all"

    session_state["range_widget"] = ["[0-2500km]", "[5000-10000km]"]
    segment_inspector._update_explicit_all_multiselect(
        "range_widget",
        "range_widget_previous",
        "Full Range",
        specific_options,
        persistent_key,
    )
    assert session_state[persistent_key] == [
        "[0-2500km]",
        "[5000-10000km]",
    ]


def test_inspector_distance_options_stop_at_ten_thousand_kilometres():
    """Keep Inspector choices inside the run's geographic analysis scope."""
    station_rows = pd.DataFrame(
        {
            "SegmentID": ["a", "b", "c", "d", "Out of Bounds"],
            "r_min": [0, 2500, 5000, 10000, 0],
            "dist_label": [
                "[0-2500km]",
                "[2500-5000km]",
                "[5000-10000km]",
                "[10000-15000km]",
                "[0-2500km]",
            ],
            "dir_name": ["N", "NE", "E", "SE", "S"],
        }
    )

    options = view_models.build_inspector_options(
        station_rows,
        max_peer_distance_km=10000,
    )

    assert options.valid_distances == [
        "[0-2500km]",
        "[2500-5000km]",
        "[5000-10000km]",
    ]
    assert options.valid_directions == ["N", "NE", "E"]
    assert set(options.source_rows["r_min"]) == {0, 2500, 5000}


def test_saved_inspector_range_beyond_ten_thousand_km_falls_back_to_all(
    monkeypatch,
):
    """Do not let stale saved Inspector state widen the active analysis scope."""
    persistent_key = segment_inspector.RESULTS_SELECTED_RANGES_COMPARE_STATE_KEY
    session_state = {persistent_key: ["[10000-15000km]"]}
    monkeypatch.setattr(
        segment_inspector,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    segment_inspector._initialize_explicit_all_multiselect(
        "range_widget",
        "range_widget_previous",
        "Full Range",
        ["[0-2500km]", "[2500-5000km]", "[5000-10000km]"],
        persistent_key,
    )

    assert session_state["range_widget"] == ["Full Range"]
    assert session_state[persistent_key] == "all"


def test_station_selection_defaults_distinguish_legacy_none_from_explicit_empty():
    """Retain first-row compatibility without replacing an intentional deselection."""
    station_table = pd.DataFrame(
        {
            "Station": ["A1AAA", "B2BBB"],
            "Locator": ["AA00", "BB11"],
        }
    )

    assert segment_inspector._station_selection_default_rows(
        station_table,
        "Station",
        "Locator",
        None,
    ) == ([0], [])
    assert segment_inspector._station_selection_default_rows(
        station_table,
        "Station",
        "Locator",
        [],
    ) == ([], [])
    assert segment_inspector._station_selection_default_rows(
        station_table,
        "Station",
        "Locator",
        "all",
    ) == ([0, 1], [])


def test_station_selection_matches_ordered_identities_and_reports_missing():
    """Match stable identity pairs, deduplicate them, and never choose substitutes."""
    station_table = pd.DataFrame(
        {
            "Station": ["A1AAA", "B2BBB", "C3CCC"],
            "Locator": ["AA00", "BB11", "cc22aa"],
        }
    )
    configured_identities = [
        {"callsign": "c3ccc", "locator": "CC22AA"},
        {"callsign": "A1AAA", "locator": "AA00"},
        {"callsign": "C3CCC", "locator": "CC22AA"},
        {"callsign": "MISSING", "locator": "ZZ99"},
    ]

    selected_rows, missing_identities = (
        segment_inspector._station_selection_default_rows(
            station_table,
            "Station",
            "Locator",
            configured_identities,
        )
    )

    assert selected_rows == [2, 0]
    assert missing_identities == [
        {"callsign": "MISSING", "locator": "ZZ99"}
    ]


def test_station_selection_syncs_ordered_identities_including_empty(monkeypatch):
    """Persist exact row identities rather than labels or transient indices."""
    session_state = {}
    station_table = pd.DataFrame(
        {
            "Station": ["A1AAA", "B2BBB", "A1AAA"],
            "Locator": ["AA00", "BB11", "AA00"],
        }
    )
    monkeypatch.setattr(
        segment_inspector,
        "st",
        SimpleNamespace(session_state=session_state),
    )
    selection_universe_table = pd.DataFrame(
        {
            "Station": ["A1AAA", "B2BBB", "C3CCC"],
            "Locator": ["AA00", "BB11", "CC22"],
        }
    )

    assert segment_inspector._sync_selected_station_state(
        segment_inspector.RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY,
        station_table,
        [1, 2, 0, 99],
        "Station",
        "Locator",
        selection_universe_table,
    ) == [
        {"callsign": "B2BBB", "locator": "BB11"},
        {"callsign": "A1AAA", "locator": "AA00"},
    ]
    assert segment_inspector._sync_selected_station_state(
        segment_inspector.RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY,
        station_table,
        [],
        "Station",
        "Locator",
    ) == []
    assert (
        session_state[
            segment_inspector.RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY
        ]
        == []
    )


def test_station_selection_state_changes_only_after_user_selection(monkeypatch):
    """Keep loaded identities through default or missing-row table renders."""
    station_table = pd.DataFrame(
        {
            "Station": ["M7AEO", "F4WBN"],
            "Locator": ["IO82", "JN18"],
        }
    )
    configured_identities = [
        {"callsign": "M7AEO", "locator": "IO82"},
        {"callsign": "MISSING", "locator": "JO00"},
    ]
    session_state = {"selected": configured_identities}
    monkeypatch.setattr(
        segment_inspector,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    assert segment_inspector._sync_selected_station_state_if_changed(
        "table_selection_changed",
        "selected",
        station_table,
        [0],
        "Station",
        "Locator",
    ) == configured_identities
    assert session_state["selected"] == configured_identities

    segment_inspector._mark_station_selection_changed("table_selection_changed")
    assert segment_inspector._sync_selected_station_state_if_changed(
        "table_selection_changed",
        "selected",
        station_table,
        [],
        "Station",
        "Locator",
    ) == []
    assert session_state["selected"] == []


def test_complete_station_selection_compacts_only_against_unfiltered_universe(
    monkeypatch,
):
    """Use ``all`` only when every pre-filter station identity is selected."""
    session_state = {}
    full_station_table = pd.DataFrame(
        {
            "Station": ["A1AAA", "B2BBB", "C3CCC"],
            "Locator": ["AA00", "BB11", "CC22"],
        }
    )
    filtered_station_table = full_station_table.iloc[:2].reset_index(drop=True)
    monkeypatch.setattr(
        segment_inspector,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    assert segment_inspector._sync_selected_station_state(
        "selected",
        full_station_table,
        [0, 1, 2],
        "Station",
        "Locator",
        full_station_table,
    ) == "all"
    assert segment_inspector._sync_selected_station_state(
        "selected",
        filtered_station_table,
        [0, 1],
        "Station",
        "Locator",
        full_station_table,
    ) == [
        {"callsign": "A1AAA", "locator": "AA00"},
        {"callsign": "B2BBB", "locator": "BB11"},
    ]


def test_success_selection_detects_when_zero_hit_rows_must_be_shown():
    """Make a saved zero-hit Success station visible before resolving defaults."""
    station_table = pd.DataFrame(
        {
            "Station": ["A1AAA", "B2BBB"],
            "Locator": ["AA00", "BB11"],
            "Target Hits": [4, 0],
        }
    )

    assert segment_inspector._selection_requires_zero_hit_rows(
        station_table,
        "Station",
        "Locator",
        "Target Hits",
        [{"callsign": "B2BBB", "locator": "BB11"}],
    )
    assert not segment_inspector._selection_requires_zero_hit_rows(
        station_table,
        "Station",
        "Locator",
        "Target Hits",
        [{"callsign": "A1AAA", "locator": "AA00"}],
    )
    assert not segment_inspector._selection_requires_zero_hit_rows(
        station_table,
        "Station",
        "Locator",
        "Target Hits",
        [{"callsign": "MISSING", "locator": "ZZ99"}],
    )
    assert not segment_inspector._selection_requires_zero_hit_rows(
        station_table,
        "Station",
        "Locator",
        "Target Hits",
        "all",
    )


def test_show_non_joint_toggle_round_trips_through_canonical_state(monkeypatch):
    session_state = {
        segment_inspector.RESULTS_SHOW_NON_JOINT_STATE_KEY: True,
        "toggle_widget": False,
    }
    monkeypatch.setattr(segment_inspector, "st", SimpleNamespace(session_state=session_state))

    assert segment_inspector._initialize_boolean_widget_state(
        "toggle_widget",
        segment_inspector.RESULTS_SHOW_NON_JOINT_STATE_KEY,
        False,
    ) is True
    assert session_state["toggle_widget"] is True

    session_state["toggle_widget"] = False
    assert segment_inspector._sync_boolean_widget_state(
        "toggle_widget",
        segment_inspector.RESULTS_SHOW_NON_JOINT_STATE_KEY,
    ) is False
    assert session_state[segment_inspector.RESULTS_SHOW_NON_JOINT_STATE_KEY] is False


def test_unset_view_state_preserves_data_dependent_inspector_defaults(monkeypatch):
    """Use adaptive defaults until a config, demo, or user action selects a view."""
    session_state = {
        segment_inspector.RESULTS_SHOW_NON_JOINT_STATE_KEY: None,
        segment_inspector.RESULTS_TIME_BIN_ABSOLUTE_STATE_KEY: None,
    }
    monkeypatch.setattr(
        segment_inspector,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    assert segment_inspector._initialize_boolean_widget_state(
        "toggle_widget",
        segment_inspector.RESULTS_SHOW_NON_JOINT_STATE_KEY,
        True,
    ) is True
    assert segment_inspector._initialize_time_bin_widget_state(
        "time_widget",
        segment_inspector.RESULTS_TIME_BIN_ABSOLUTE_STATE_KEY,
        ["15m", "30m", "1h", "3h"],
        "30m",
    ) == "30m"


def test_session_cache_enforces_namespace_lru_limit():
    cache = _cache(max_bytes=100, limits={"segment": 2})
    assert cache.put("segment", "first", b"1", size_bytes=1)
    assert cache.put("segment", "second", b"2", size_bytes=1)
    assert cache.get("segment", "first") == (b"1", True)
    assert cache.put("segment", "third", b"3", size_bytes=1)

    assert cache.get("segment", "second") == (None, False)
    assert cache.get("segment", "first") == (b"1", True)
    assert cache.get("segment", "third") == (b"3", True)
    assert cache.namespace_entry_count("segment") == 2


def test_session_cache_enforces_global_byte_limit_by_access_order():
    cache = _cache(max_bytes=6, limits={"segment": 3, "png": 3})
    assert cache.put("segment", "segment-a", b"aaa", size_bytes=3)
    assert cache.put("png", "png-b", b"bbb", size_bytes=3)
    assert cache.get("segment", "segment-a") == (b"aaa", True)
    assert cache.put("png", "png-c", b"ccc", size_bytes=3)

    assert cache.get("png", "png-b") == (None, False)
    assert cache.get("segment", "segment-a") == (b"aaa", True)
    assert cache.get("png", "png-c") == (b"ccc", True)
    assert cache.total_bytes == 6


def test_cache_rejects_single_value_larger_than_session_budget():
    cache = _cache(max_bytes=4, limits={"selected": 2})
    assert not cache.put("selected", "large", b"12345", size_bytes=5)
    assert cache.entry_count == 0
    assert cache.total_bytes == 0


def test_cache_size_estimator_counts_dataframe_and_png_payloads():
    frame = pd.DataFrame({"station": ["K1AAA", "K2BBB"], "value": [1.0, 2.0]})
    value = {"view_model": frame, "png": b"preview"}
    assert estimate_cache_value_bytes(value) >= int(frame.memory_usage(index=True, deep=True).sum()) + len(b"preview")


def test_cached_recipe_builds_and_disposes_figure_only_once(monkeypatch):
    session_state = {}
    monkeypatch.setattr(segment_inspector, "st", SimpleNamespace(session_state=session_state))
    monkeypatch.setattr(segment_inspector, "get_matplotlib_render_mode", lambda: "image")
    monkeypatch.setattr(segment_inspector, "log_performance_event", lambda *args, **kwargs: None)

    calls = {"build": 0, "render": 0, "display": 0, "dispose": 0}
    image_bytes = b"\x89PNG\r\n\x1a\n" + (b"\x00" * 24)

    def build_figure(recipe):
        calls["build"] += 1
        return {"recipe": recipe}

    def render_figure(figure, **kwargs):
        calls["render"] += 1
        return image_bytes

    monkeypatch.setattr(segment_inspector, "render_matplotlib_figure", render_figure)
    monkeypatch.setattr(
        segment_inspector,
        "render_matplotlib_image_bytes",
        lambda *args, **kwargs: calls.__setitem__("display", calls["display"] + 1),
    )
    monkeypatch.setattr(
        segment_inspector,
        "dispose_matplotlib_figure",
        lambda figure: calls.__setitem__("dispose", calls["dispose"] + 1),
    )

    kwargs = {
        "run_id": 42,
        "cache_key": ("RX_COMP", "all"),
        "subject": "segment insight",
        "build_label": "segment insight figure build",
        "render_figure": build_figure,
    }
    assert segment_inspector._render_cached_recipe({"values": [1]}, **kwargs) == image_bytes
    assert segment_inspector._render_cached_recipe({"values": [1]}, **kwargs) == image_bytes

    assert calls == {"build": 1, "render": 1, "display": 1, "dispose": 1}
    cache = session_state[segment_inspector.INSPECTOR_CACHE_STATE_KEY]
    assert cache.run_id == 42
    assert cache.namespace_entry_count("png") == 1


def test_new_run_replaces_the_session_cache(monkeypatch):
    session_state = {}
    monkeypatch.setattr(segment_inspector, "st", SimpleNamespace(session_state=session_state))

    first = segment_inspector._inspector_cache(1)
    first.put("png", "preview", b"png", size_bytes=3)
    second = segment_inspector._inspector_cache(2)

    assert second is not first
    assert second.run_id == 2
    assert second.entry_count == 0
