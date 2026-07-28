import ast
import inspect
from types import SimpleNamespace

import pandas as pd
import pytest

from i18n import T
from ui.components import segment_inspector
from ui.inspector import drilldown, view_models
from ui.inspector.session_cache import (
    SessionInspectorCache,
    estimate_cache_value_bytes,
)
from ui.result_hierarchy import transition_prompt_html


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
        total_count=75,
        joint_count=60,
        joint_label="Joint",
    )
    spot_summary = segment_inspector._compare_metric_distribution_summary(
        [-10.0, -7.0, -6.0, 1.0],
        T["en"]["fmt_results_joint_spot_delta_summary"],
        total_count=7139,
        joint_count=5379,
        joint_label="Joint",
    )

    assert segment_inspector._segment_summary_lines(
        station_summary=station_summary,
        spot_summary=spot_summary,
    ) == [
        "Stations (n=75; Joint=60) · Median -4.5 dB · Mean -3.8 dB",
        "Spots (n=7'139; Joint=5'379) · Median -6.5 dB · Mean -5.5 dB",
    ]


def test_compare_segment_summary_uses_localized_scheduled_pair_wording():
    """Keep sequential TX A/B summaries distinct from simultaneous joint spots."""
    summary = segment_inspector._compare_metric_distribution_summary(
        [1.0, 2.0, 6.0],
        T["de"]["fmt_results_scheduled_pair_delta_summary"],
        total_count=12345,
        joint_count=6789,
        joint_label=T["de"]["tbl_col_joint_pairs"],
    )

    assert summary == (
        "Geplante Paare (n=12'345; Joint-Paare=6'789) · "
        "Median +2.0 dB · Mittelwert +3.0 dB"
    )
    assert segment_inspector._compare_metric_distribution_summary(
        [],
        T["en"]["fmt_results_joint_spot_delta_summary"],
        total_count=0,
        joint_count=0,
        joint_label="Joint",
    ) is None


def test_compare_summary_count_uses_apostrophe_thousands_separator():
    """Keep compact evidence counts independent of UI-locale separators."""
    assert segment_inspector._format_summary_count(7139) == "7'139"


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


def test_segment_temporal_controls_have_localized_instruction_prompts():
    """Invite a segment-bin choice without changing selected-station controls."""
    assert T["en"]["lbl_time_aggregation_bin_size"] == (
        "Select time aggregation bin size"
    )
    assert T["de"]["lbl_time_aggregation_bin_size"] == (
        "Zeitliche Aggregationsbreite auswählen"
    )
    assert T["en"]["lbl_include_unpaired_evidence"] == (
        "Include Unpaired Evidence"
    )
    assert T["de"]["lbl_include_unpaired_evidence"] == (
        "Ungepaarte Evidenz einbeziehen"
    )


@pytest.mark.parametrize(
    ("language", "range_summary", "direction_summary", "figure_title"),
    (
        (
            "en",
            "3 ranges",
            "5 directions",
            "Selected Station Evidence: K1AAA (FN31) · 2 joint spots",
        ),
        (
            "de",
            "3 Bereiche",
            "5 Richtungen",
            "Evidenz der ausgewählten Station: K1AAA (FN31) · 2 Joint Spots",
        ),
    ),
)
def test_segment_inspector_labels_use_the_bilingual_catalog(
    language,
    range_summary,
    direction_summary,
    figure_title,
):
    """Resolve scope, figure, and plot labels without renderer language branches."""
    translations = T[language]

    assert segment_inspector._selection_summary(
        ("A", "B", "C"),
        translations["opt_full_range"],
        "range",
        translations,
    ) == range_summary
    assert segment_inspector._selection_summary(
        ("N", "NE", "E", "SE", "S"),
        translations["opt_all_dirs"],
        "direction",
        translations,
    ) == direction_summary
    assert segment_inspector._selected_evidence_figure_title(
        ("K1AAA (FN31)",),
        2,
        analysis_id="RX_COMP",
        is_sequential=False,
        translations=translations,
    ) == figure_title

    labels = segment_inspector._evidence_labels(translations)
    assert labels["dist_title"] == translations[
        "fig_compare_delta_distribution"
    ]
    assert labels["time_title"] == translations[
        "fig_segment_chronological_delta"
    ]
    assert labels["mean_label"] == translations["fig_mean_label"]
    assert {
        "aggregate",
        "pooled_median_label",
        "pooled_mean_label",
    }.isdisjoint(labels)


@pytest.mark.parametrize("language", ("en", "de"))
def test_missing_station_warning_uses_the_active_translation(
    monkeypatch,
    language,
):
    """Render saved-selection warnings from the supplied translation mapping."""
    warnings = []
    monkeypatch.setattr(
        segment_inspector,
        "st",
        SimpleNamespace(
            warning=lambda message, **kwargs: warnings.append(
                (message, kwargs)
            )
        ),
    )

    segment_inspector._warn_missing_station_identities(
        [{"callsign": "K1AAA", "locator": "FN31"}],
        T[language],
    )

    assert warnings == [
        (
            T[language]["warn_saved_station_unavailable"].format(
                stations="K1AAA (FN31)"
            ),
            {"icon": ":material/warning:"},
        )
    ]


def test_targeted_inspector_renderers_have_no_language_wording_branches():
    """Keep localized wording in catalog lookups and plumb it into exports."""
    module_sources = (
        inspect.getsource(segment_inspector),
        inspect.getsource(drilldown),
    )
    for module_source in module_sources:
        module_tree = ast.parse(module_source)
        language_conditions = [
            node
            for node in ast.walk(module_tree)
            if isinstance(node, (ast.If, ast.IfExp))
            and "lang" in ast.dump(node.test).lower()
            and "Constant(value='de')" in ast.dump(node.test)
        ]
        translation_fallbacks = [
            node
            for node in ast.walk(module_tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "get"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id in {"t", "translations"}
        ]
        assert language_conditions == []
        assert translation_fallbacks == []

    segment_tree = ast.parse(module_sources[0])
    export_calls = [
        node
        for node in ast.walk(segment_tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "register_inspector_export"
    ]
    assert len(export_calls) == 3
    assert all(
        any(keyword.arg == "translations" for keyword in call.keywords)
        for call in export_calls
    )


def _render_segment_temporal_for_test(monkeypatch, *, is_compare):
    """Render one temporal bundle while recording compact-recipe dispatches."""
    render_calls = []
    monkeypatch.setattr(
        segment_inspector,
        "st",
        SimpleNamespace(markdown=lambda *_args, **_kwargs: None),
    )
    monkeypatch.setattr(
        segment_inspector,
        "render_result_guidance_popover",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        segment_inspector,
        "_initialize_time_bin_widget_state",
        lambda *_args, **_kwargs: "6h",
    )
    monkeypatch.setattr(
        segment_inspector,
        "_render_prompted_segment_time_bin_control",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        segment_inspector,
        "_sync_time_bin_widget_state",
        lambda *_args, **_kwargs: "6h",
    )

    def record_render(recipe, **kwargs):
        render_calls.append((recipe, kwargs))

    monkeypatch.setattr(
        segment_inspector,
        "_render_cached_recipe",
        record_render,
    )
    result = segment_inspector._render_segment_temporal_evidence(
        {
            "base_recipe": {
                "kind": (
                    "segment_compare_temporal"
                    if is_compare
                    else "opportunity_success_temporal"
                ),
                "time_bin": "3h",
            },
            "time_bin_options": ("3h", "6h"),
            "time_bin_default": "3h",
        },
        analysis_id="RX_COMP" if is_compare else "RX_ABS",
        run_id=7,
        scope_token="all",
        cache_key=("segment",),
        t={
            "hdr_results_temporal_evidence": "Temporal Evidence",
            "sub_results_temporal_evidence": "Compare subtitle",
            "sub_results_success_temporal": "Performance subtitle",
            "lbl_time_aggregation_bin_size": "Select time aggregation bin size",
        },
        is_compare=is_compare,
        is_sequential=False,
        analysis_context=SimpleNamespace(),
        language="en",
    )
    return result, render_calls


def test_success_segment_temporal_renders_snr_before_lower_evidence(monkeypatch):
    """Use separate cache entries and export recipes for the two Success canvases."""
    result, render_calls = _render_segment_temporal_for_test(
        monkeypatch,
        is_compare=False,
    )

    assert len(render_calls) == 2
    snr_recipe, snr_call = render_calls[0]
    evidence_recipe, evidence_call = render_calls[1]
    assert snr_call["render_figure"] is (
        segment_inspector.render_segment_temporal_snr_export_figure
    )
    assert evidence_call["render_figure"] is (
        segment_inspector.render_segment_temporal_evidence_export_figure
    )
    assert snr_call["cache_key"] != evidence_call["cache_key"]
    assert snr_recipe["time_bin"] == "6h"
    assert evidence_recipe["time_bin"] == "6h"
    assert snr_recipe is not evidence_recipe
    assert result == {
        "export_recipe": evidence_recipe,
        "snr_export_recipe": snr_recipe,
        "time_bin": "6h",
    }


def test_compare_segment_temporal_keeps_one_combined_figure(monkeypatch):
    """Do not split or otherwise reroute the established Compare figure."""
    result, render_calls = _render_segment_temporal_for_test(
        monkeypatch,
        is_compare=True,
    )

    assert len(render_calls) == 1
    recipe, render_call = render_calls[0]
    assert render_call["render_figure"] is (
        segment_inspector.render_segment_temporal_evidence_export_figure
    )
    assert recipe["time_bin"] == "6h"
    assert result == {
        "export_recipe": recipe,
        "snr_export_recipe": None,
        "time_bin": "6h",
    }


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
    guidance_calls = []
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
    monkeypatch.setattr(
        segment_inspector,
        "render_result_guidance_popover",
        lambda *args, **kwargs: guidance_calls.append((args, kwargs)),
    )

    result = segment_inspector._render_selected_station_evidence(
        pd.DataFrame({"peer_sign": ["G3AAA"], "peer_grid": ["IO90"]}),
        pd.DataFrame({"peer_sign": ["G3AAA"], "peer_grid": ["IO90"]}),
        False,
        10,
        0,
        2,
        t=T["en"],
        analysis_id="RX_COMP",
        run_id=7,
        scope_token="all",
        cache_key=("selected",),
        analysis_context=SimpleNamespace(),
        language="en",
    )

    rendered_markup = "".join(markdown_calls)
    assert result is None
    assert "04 · SELECTED STATIONS" not in rendered_markup
    assert (
        "aria-label='04 · Selected station: Selected Station Evidence'"
        in rendered_markup
    )
    assert "Selected Station Evidence" in rendered_markup
    assert "G3AAA (IO90) · 0 joint spots" in rendered_markup
    assert T["en"]["txt_results_selected_no_paired_evidence"] in rendered_markup
    assert len(guidance_calls) == 1
    assert (
        guidance_calls[0][0][0]
        == segment_inspector.RESULT_GUIDANCE_SELECTED_STATIONS
    )


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


def test_segment_time_bin_prompt_renders_above_full_width_selector(monkeypatch):
    """Reuse the established transition cue before the adaptive choices."""
    events = []

    def markdown(body, **kwargs):
        events.append(("markdown", body, kwargs))

    def segmented_control(label, options, **kwargs):
        events.append(("segmented_control", label, tuple(options), kwargs))
        return "3h"

    monkeypatch.setattr(
        segment_inspector,
        "st",
        SimpleNamespace(
            markdown=markdown,
            segmented_control=segmented_control,
        ),
    )

    selected = segment_inspector._render_prompted_segment_time_bin_control(
        T["en"]["lbl_time_aggregation_bin_size"],
        ["1h", "2h", "3h", "6h", "12h", "24h"],
        "segment_time_widget",
    )

    assert selected == "3h"
    assert events[0] == (
        "markdown",
        transition_prompt_html("Select time aggregation bin size"),
        {"unsafe_allow_html": True},
    )
    assert events[1][0:3] == (
        "segmented_control",
        "Select time aggregation bin size",
        ("1h", "2h", "3h", "6h", "12h", "24h"),
    )


def test_performance_drilldown_uses_five_row_viewport_without_changing_compare(
    monkeypatch,
):
    """Compact only the Performance audit table and retain its scrolling viewport."""
    assert segment_inspector.COMPACT_DATAFRAME_VISIBLE_BODY_ROWS == 5

    class FakeStreamlit:
        """Record the dataframe options used by the drill-down renderer."""

        def __init__(self):
            self.session_state = {}
            self.dataframe_calls = []

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def markdown(self, *_args, **_kwargs):
            return None

        def columns(self, widths, **_kwargs):
            return tuple(self for _width in widths)

        def popover(self, *_args, **_kwargs):
            return self

        def multiselect(self, *_args, **_kwargs):
            return []

        def dataframe(self, *_args, **kwargs):
            self.dataframe_calls.append(dict(kwargs))
            return None

    fake_streamlit = FakeStreamlit()
    monkeypatch.setattr(segment_inspector, "st", fake_streamlit)
    monkeypatch.setattr(
        segment_inspector,
        "render_result_guidance_popover",
        lambda *_args, **_kwargs: None,
    )
    drilldown_rows = pd.DataFrame(
        {
            "Date/Time (UTC)": ["01-Jul-2026 00:00:00"],
            "Outcome": ["Target"],
            "Target (T)": [1],
            "Elsewhere (E)": [0],
        }
    )
    common_arguments = (
        drilldown_rows,
        ["K1AAA (FN31)"],
        "RX_ABS",
        71,
        "rall_dall",
        T["en"],
    )

    segment_inspector._render_drilldown_dataframe(
        *common_arguments,
        False,
        False,
        SimpleNamespace(),
        "en",
    )
    segment_inspector._render_drilldown_dataframe(
        *common_arguments,
        True,
        False,
        SimpleNamespace(),
        "en",
    )

    performance_call, compare_call = fake_streamlit.dataframe_calls
    assert performance_call["height"] == (
        segment_inspector.COMPACT_DATAFRAME_HEIGHT_PX
    )
    assert performance_call["row_height"] == (
        segment_inspector.COMPACT_DATAFRAME_ROW_HEIGHT_PX
    )
    assert "height" not in compare_call
    assert "row_height" not in compare_call


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


def test_station_selection_defaults_distinguish_unset_from_explicit_empty():
    """Retain the first-row default without replacing an intentional deselection."""
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


def test_station_selection_matches_one_identity_and_reports_missing():
    """Match one normalized identity and never choose a substitute."""
    station_table = pd.DataFrame(
        {
            "Station": ["A1AAA", "B2BBB", "C3CCC"],
            "Locator": ["AA00", "BB11", "cc22aa"],
        }
    )

    selected_rows, missing_identities = (
        segment_inspector._station_selection_default_rows(
            station_table,
            "Station",
            "Locator",
            [{"callsign": "c3ccc", "locator": "cc22aa"}],
        )
    )
    assert selected_rows == [2]
    assert missing_identities == []

    selected_rows, missing_identities = (
        segment_inspector._station_selection_default_rows(
            station_table,
            "Station",
            "Locator",
            [{"callsign": "D4DDD", "locator": "DD33"}],
        )
    )
    assert selected_rows == []
    assert missing_identities == [
        {"callsign": "D4DDD", "locator": "DD33"}
    ]


@pytest.mark.parametrize(
    "configured_identities",
    [
        "all",
        ({"callsign": "A1AAA", "locator": "AA00"},),
        [
            {"callsign": "A1AAA", "locator": "AA00"},
            {"callsign": "B2BBB", "locator": "BB11"},
        ],
        [
            {"callsign": "A1AAA", "locator": "AA00"},
            {"callsign": "a1aaa", "locator": "aa00"},
        ],
        [{"callsign": "MISSING", "locator": "AA00"}],
        [{"callsign": "A1AAA", "locator": "ZZ99"}],
        [{"callsign": "A1AAA", "locator": "AA00", "extra": True}],
    ],
)
def test_station_selection_rejects_noncanonical_or_multiple_state(
    configured_identities,
):
    """Reject legacy, multiple, duplicate, and malformed durable state."""
    station_table = pd.DataFrame(
        {
            "Station": ["A1AAA", "B2BBB"],
            "Locator": ["AA00", "BB11"],
        }
    )

    with pytest.raises(ValueError):
        segment_inspector._station_selection_default_rows(
            station_table,
            "Station",
            "Locator",
            configured_identities,
        )


def test_station_selection_sync_replaces_then_clears_identity(monkeypatch):
    """Persist A, replace it with B, then preserve explicit deselection."""
    persistent_key = segment_inspector.RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY
    session_state = {}
    station_table = pd.DataFrame(
        {
            "Station": ["A1AAA", "B2BBB"],
            "Locator": ["AA00", "BB11"],
        }
    )
    monkeypatch.setattr(
        segment_inspector,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    assert segment_inspector._sync_selected_station_state(
        persistent_key,
        station_table,
        [0],
        "Station",
        "Locator",
    ) == [
        {"callsign": "A1AAA", "locator": "AA00"}
    ]
    assert segment_inspector._sync_selected_station_state(
        persistent_key,
        station_table,
        [1],
        "Station",
        "Locator",
    ) == [
        {"callsign": "B2BBB", "locator": "BB11"},
    ]
    assert segment_inspector._sync_selected_station_state(
        persistent_key,
        station_table,
        [],
        "Station",
        "Locator",
    ) == []
    assert (
        session_state[persistent_key]
        == []
    )


def test_station_selection_writer_rejects_multiple_rows_atomically(monkeypatch):
    """Reject multiple rows without overwriting the prior identity."""
    previous_selection = [{"callsign": "A1AAA", "locator": "AA00"}]
    session_state = {"selected": previous_selection}
    station_table = pd.DataFrame(
        {
            "Station": ["A1AAA", "B2BBB"],
            "Locator": ["AA00", "BB11"],
        }
    )
    monkeypatch.setattr(
        segment_inspector,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    segment_inspector._mark_station_selection_changed(
        "table_selection_changed"
    )
    with pytest.raises(ValueError, match="at most one row"):
        segment_inspector._sync_selected_station_state_if_changed(
            "table_selection_changed",
            "selected",
            station_table,
            [0, 1],
            "Station",
            "Locator",
        )
    assert session_state["selected"] is previous_selection

    malformed_station_table = pd.DataFrame(
        {"Station": ["MISSING"], "Locator": ["AA00"]}
    )
    segment_inspector._mark_station_selection_changed(
        "table_selection_changed"
    )
    with pytest.raises(ValueError, match="callsign"):
        segment_inspector._sync_selected_station_state_if_changed(
            "table_selection_changed",
            "selected",
            malformed_station_table,
            [0],
            "Station",
            "Locator",
        )
    assert session_state["selected"] is previous_selection


def test_station_selection_state_changes_only_after_user_selection(monkeypatch):
    """Keep loaded state until an event replaces or clears the identity."""
    station_table = pd.DataFrame(
        {
            "Station": ["M7AEO", "F4WBN"],
            "Locator": ["IO82", "JN18"],
        }
    )
    configured_identities = [
        {"callsign": "M7AEO", "locator": "IO82"},
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
        [1],
        "Station",
        "Locator",
    ) == [
        {"callsign": "F4WBN", "locator": "JN18"},
    ]
    assert session_state["selected"] == [
        {"callsign": "F4WBN", "locator": "JN18"},
    ]

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
        [{"callsign": "D4DDD", "locator": "DD33"}],
    )


def test_compare_station_insights_uses_single_row_selection():
    """Keep Compare Station Insights on Streamlit's replacement semantics."""
    function_source = inspect.getsource(
        segment_inspector._render_segment_inspector_body
    )

    assert '"selection_mode": "single-row"' in function_source
    assert '"selection_mode": "multi-row"' not in function_source


def test_inspector_fragment_synchronizes_durable_url_state_in_place():
    """Keep result-control URL updates inside the Inspector fragment rerun."""
    function_source = inspect.getsource(
        segment_inspector.render_segment_inspector
    )

    assert "render_current_url_synchronizer(" in function_source
    assert "URL_QUERY_SYNCHRONIZER_FRAGMENT_KEY" in function_source
    assert "@st.fragment" in inspect.getsource(
        segment_inspector.render_segment_inspector
    )


def test_selected_station_evidence_rejects_multiple_identities():
    """Reject accidental multi-station fan-in before cache or figure work."""
    selected_identity_df = pd.DataFrame(
        {
            "peer_sign": ["A1AAA", "B2BBB"],
            "peer_grid": ["AA00", "BB11"],
        }
    )

    with pytest.raises(ValueError, match="exactly one station identity"):
        segment_inspector._render_selected_station_evidence(
            pd.DataFrame(),
            selected_identity_df,
            False,
            10,
            0,
            2,
            t=T["en"],
            analysis_id="RX_COMPARE",
            run_id=7,
            scope_token="all",
            cache_key=("selected",),
            analysis_context=SimpleNamespace(),
            language="en",
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
    assert cache.entry_count == 2


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
    assert cache.entry_count == 1


def test_new_run_replaces_the_session_cache(monkeypatch):
    session_state = {}
    monkeypatch.setattr(segment_inspector, "st", SimpleNamespace(session_state=session_state))

    first = segment_inspector._inspector_cache(1)
    first.put("png", "preview", b"png", size_bytes=3)
    second = segment_inspector._inspector_cache(2)

    assert second is not first
    assert second.run_id == 2
    assert second.entry_count == 0


def test_success_new_station_builds_after_segment_cache_hit_without_provider_request(
    monkeypatch,
):
    """Replace A with B, then clear, without rebuilding or querying the segment."""
    from core import data_engine

    class FakeContainer:
        """Provide the small context/container surface used by the Success inspector."""

        def __init__(self, fake_streamlit):
            self.fake_streamlit = fake_streamlit

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def markdown(self, *_args, **_kwargs):
            return None

        def columns(self, widths, **kwargs):
            self.fake_streamlit.column_calls.append((list(widths), kwargs))
            return tuple(FakeContainer(self.fake_streamlit) for _ in widths)

        def dataframe(self, *_args, **kwargs):
            self.fake_streamlit.dataframe_calls.append(dict(kwargs))
            on_select = kwargs.get("on_select")
            if callable(on_select):
                on_select()
            return SimpleNamespace(
                selection=SimpleNamespace(
                    rows=list(self.fake_streamlit.selected_rows)
                )
            )

    class FakeStreamlit:
        """Retain session cache state while exposing controlled table selections."""

        def __init__(self):
            self.session_state = {}
            self.selected_rows = [0]
            self.markdown_calls = []
            self.column_calls = []
            self.dataframe_calls = []

        def container(self, **_kwargs):
            return FakeContainer(self)

        def markdown(self, body, **kwargs):
            self.markdown_calls.append((body, kwargs))
            return None

        def toggle(self, *_args, **_kwargs):
            return False

        def popover(self, *_args, **_kwargs):
            return FakeContainer(self)

        def multiselect(self, *_args, **_kwargs):
            return []

    fake_streamlit = FakeStreamlit()
    fake_streamlit.session_state[
        segment_inspector.RESULTS_TIME_BIN_ABSOLUTE_STATE_KEY
    ] = "2h"
    monkeypatch.setattr(segment_inspector, "st", fake_streamlit)

    provider_requests = []

    def reject_provider_request(*args, **kwargs):
        provider_requests.append((args, kwargs))
        raise AssertionError("Inspector rerenders must not contact a provider.")

    monkeypatch.setattr(
        data_engine.http_session,
        "get",
        reject_provider_request,
    )
    monkeypatch.setattr(
        segment_inspector,
        "log_performance_event",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        segment_inspector,
        "_supports_dataframe_selection_default",
        lambda: False,
    )
    monkeypatch.setattr(
        segment_inspector,
        "render_result_guidance_popover",
        lambda *_args, **_kwargs: None,
    )
    selected_render_calls = []

    def record_cached_recipe(_recipe, **kwargs):
        if str(kwargs.get("subject", "")).startswith(
            "opportunity selected"
        ):
            selected_render_calls.append(
                {"recipe": _recipe, **kwargs}
            )
        return None

    monkeypatch.setattr(
        segment_inspector,
        "_render_cached_recipe",
        record_cached_recipe,
    )
    monkeypatch.setattr(
        segment_inspector,
        "_render_segment_temporal_evidence",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        segment_inspector,
        "_render_prompted_segment_time_bin_control",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        segment_inspector,
        "_selected_success_context_line",
        lambda *_args, **_kwargs: "Selected station context",
    )
    drilldown_builds = []
    drilldown_renders = []
    export_calls = []

    def record_drilldown_build(
        _parquet_path,
        selected_meta,
        selected_station_column,
        selected_locator_column,
        *_args,
        station_rows_df,
        **_kwargs,
    ):
        selected_identities = tuple(
            selected_meta[
                [selected_station_column, selected_locator_column]
            ].itertuples(index=False, name=None)
        )
        evidence_identities = tuple(
            station_rows_df[
                ["peer_sign", "peer_grid"]
            ].itertuples(index=False, name=None)
        )
        drilldown_builds.append(
            {
                "selected_identities": selected_identities,
                "evidence_identities": evidence_identities,
            }
        )
        return (
            pd.DataFrame(
                {
                    "Selected station": [
                        selected_identities[0][0]
                    ]
                }
            ),
            None,
        )

    def record_drilldown_render(
        drilldown_table,
        selected_station_labels,
        *_args,
        **_kwargs,
    ):
        drilldown_renders.append(
            {
                "labels": tuple(selected_station_labels),
                "stations": tuple(
                    drilldown_table["Selected station"].astype(str)
                ),
            }
        )
        return drilldown_table

    monkeypatch.setattr(
        segment_inspector,
        "_build_drilldown_table",
        record_drilldown_build,
    )
    monkeypatch.setattr(
        segment_inspector,
        "_render_drilldown_dataframe",
        record_drilldown_render,
    )
    monkeypatch.setattr(
        segment_inspector,
        "register_inspector_export",
        lambda **kwargs: export_calls.append(kwargs),
    )

    station_column = "RX Station"
    locator_column = "Locator"
    distance_column = "km"
    azimuth_column = "Azimuth"
    hit_column = "Heard by Target"
    station_table = pd.DataFrame(
        {
            station_column: [
                "A1AAA",
                "B2BBB",
                "C3CCC",
                "D4DDD",
                "E5EEE",
                "F6FFF",
            ],
            locator_column: [
                "AA00",
                "BB11",
                "CC22",
                "DD33",
                "EE44",
                "FF55",
            ],
            distance_column: [100.0, 200.0, 300.0, 400.0, 500.0, 600.0],
            azimuth_column: [10.0, 20.0, 30.0, 40.0, 50.0, 60.0],
            hit_column: [1, 1, 1, 1, 1, 1],
        }
    )
    opportunity_view_model = SimpleNamespace(
        summary_lines=[],
        confirmed_station_count=6,
        confirmed_opportunity_count=6,
        full_station_table=station_table,
        export_station_table=station_table,
        station_column=station_column,
        locator_column=locator_column,
        distance_column=distance_column,
        azimuth_column=azimuth_column,
        hit_column=hit_column,
        export_station_column=station_column,
        export_locator_column=locator_column,
        confirmed_rows=pd.DataFrame(),
        evidence_rows=pd.DataFrame(),
    )
    monkeypatch.setattr(
        segment_inspector,
        "build_opportunity_inspector_view_model",
        lambda *_args, **_kwargs: opportunity_view_model,
    )
    monkeypatch.setattr(
        segment_inspector,
        "_opportunity_segment_recipe",
        lambda *_args, **_kwargs: {"kind": "segment"},
    )
    selected_recipe_builds = []

    def build_temporal_recipe(
        evidence_title,
        _selected_segment,
        peer_rows,
        temporal_evidence_rows,
        *_args,
        snr_title,
        population_mode,
        snr_representation,
        **_kwargs,
    ):
        if (
            population_mode
            == segment_inspector.SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION
        ):
            selected_recipe_builds.append(
                {
                    "peer_identities": tuple(
                        peer_rows[
                            ["peer_sign", "peer_grid"]
                        ].itertuples(index=False, name=None)
                    ),
                    "evidence_identities": tuple(
                        temporal_evidence_rows[
                            ["peer_sign", "peer_grid"]
                        ].itertuples(index=False, name=None)
                    ),
                    "population_mode": population_mode,
                    "snr_representation": snr_representation,
                }
            )
        return {
            "evidence_title": evidence_title,
            "snr_title": snr_title,
            "time_bin_options": ["1h", "2h"],
            "time_bin_default": "1h",
            "population_mode": population_mode,
            "snr_representation": snr_representation,
        }

    monkeypatch.setattr(
        segment_inspector,
        "_opportunity_temporal_recipe",
        build_temporal_recipe,
    )

    evidence_rows = pd.DataFrame(
        {
            "time_slot": [1, 1, 1, 1, 1, 1],
            "peer_sign": [
                "A1AAA",
                "B2BBB",
                "C3CCC",
                "D4DDD",
                "E5EEE",
                "F6FFF",
            ],
            "peer_grid": [
                "AA00",
                "BB11",
                "CC22",
                "DD33",
                "EE44",
                "FF55",
            ],
            "hit": [1, 1, 1, 1, 1, 1],
            "miss": [0, 0, 0, 0, 0, 0],
            "target_snr": [-10.0, -11.0, -12.0, -13.0, -14.0, -15.0],
        }
    )
    segment_read_count = 0

    def read_segment_rows(*_args, **_kwargs):
        nonlocal segment_read_count
        segment_read_count += 1
        return evidence_rows.copy()

    monkeypatch.setattr(
        segment_inspector,
        "read_parquet_artifact",
        read_segment_rows,
    )

    selected_station_loads = []

    def load_selected_station_rows(
        _parquet_path,
        selected_meta,
        selected_station_column,
        selected_locator_column,
        *,
        columns,
    ):
        del columns
        selected_pairs = [
            (str(callsign), str(locator))
            for callsign, locator in selected_meta[
                [selected_station_column, selected_locator_column]
            ].itertuples(index=False, name=None)
        ]
        selected_station_loads.append(
            tuple(callsign for callsign, _locator in selected_pairs)
        )
        return pd.DataFrame(
            {
                "time_slot": list(range(1, len(selected_pairs) + 1)),
                "peer_sign": [
                    callsign for callsign, _locator in selected_pairs
                ],
                "peer_grid": [
                    locator for _callsign, locator in selected_pairs
                ],
                "hit": [1] * len(selected_pairs),
                "miss": [0] * len(selected_pairs),
                "target_only": [0] * len(selected_pairs),
                "target_snr": [
                    -10.0 - row_index
                    for row_index in range(len(selected_pairs))
                ],
                "path_illumination": ["Daylight"] * len(selected_pairs),
            }
        )

    monkeypatch.setattr(
        segment_inspector,
        "_load_station_rows_for_drilldown",
        load_selected_station_rows,
    )

    cache_events = []
    original_cache_get = segment_inspector._inspector_cache_get

    def recording_cache_get(
        run_id,
        namespace,
        key,
        timing_collector=None,
        *,
        item="",
    ):
        cached_value, is_cache_hit = original_cache_get(
            run_id,
            namespace,
            key,
            timing_collector,
            item=item,
        )
        if namespace in {"segment", "selected"}:
            cache_events.append((namespace, is_cache_hit))
        return cached_value, is_cache_hit

    monkeypatch.setattr(
        segment_inspector,
        "_inspector_cache_get",
        recording_cache_get,
    )

    analysis_start = pd.Timestamp("2026-07-01T00:00:00Z")
    analysis_end = pd.Timestamp("2026-07-01T02:00:00Z")
    analysis_context = SimpleNamespace(
        min_confirmed_opportunities_per_peer=1,
        callsign="G3ZIL",
        tx_ab_repeat_interval_minutes=10,
        tx_ab_target_start_minute=0,
        tx_ab_reference_start_minute=2,
    )
    opportunity_terms = {
        "mode": "RX",
        "show_counter": "Heard only by other stations.",
    }
    presentation_context = SimpleNamespace(
        language="en",
        theme="dark",
        absolute_terms=lambda _mode: opportunity_terms,
    )
    scope_rows = pd.DataFrame(
        {
            "peer_sign": [
                "A1AAA",
                "B2BBB",
                "C3CCC",
                "D4DDD",
                "E5EEE",
                "F6FFF",
            ],
            "peer_grid": [
                "AA00",
                "BB11",
                "CC22",
                "DD33",
                "EE44",
                "FF55",
            ],
        }
    )
    level_two_container = FakeContainer(fake_streamlit)
    scope_summary_placeholder = FakeContainer(fake_streamlit)
    render_arguments = {
        "analysis_id": "RX_ABS",
        "title": "RX Performance",
        "df_seg": scope_rows,
        "parquet_path": "unused-session-artifact.parquet",
        "line1_str": "audit",
        "t": T["en"],
        "selected_seg": "Full Range | All Directions",
        "selected_ranges": ("Full Range",),
        "selected_directions": ("All Directions",),
        "distance_scope_intervals": ((0.0, 1000.0),),
        "range_summary": "Full Range",
        "direction_summary": "All Directions",
        "scope_token": "rall_dall",
        "run_id": 101,
        "level_two_container": level_two_container,
        "active_scope_summary": "Full Range | All Directions",
        "scope_summary_placeholder": scope_summary_placeholder,
        "analysis_start_t": analysis_start,
        "analysis_end_t": analysis_end,
        "show_export_button": False,
        "analysis_context": analysis_context,
        "presentation_context": presentation_context,
    }

    persisted_success_selections = []
    for selected_rows in ([0], [1], []):
        fake_streamlit.selected_rows = list(selected_rows)
        segment_inspector._render_opportunity_scope(**render_arguments)
        persisted_success_selections.append(
            [
                dict(identity)
                for identity in fake_streamlit.session_state[
                    segment_inspector.RESULTS_SELECTED_STATIONS_ABSOLUTE_STATE_KEY
                ]
            ]
        )

    assert cache_events == [
        ("segment", False),
        ("selected", False),
        ("segment", True),
        ("selected", False),
        ("segment", True),
    ]
    assert segment_read_count == 1
    assert selected_station_loads == [
        ("A1AAA",),
        ("B2BBB",),
    ]
    assert [
        recipe_build["peer_identities"]
        for recipe_build in selected_recipe_builds
    ] == [
        (("A1AAA", "AA00"),),
        (("B2BBB", "BB11"),),
    ]
    assert [
        recipe_build["evidence_identities"]
        for recipe_build in selected_recipe_builds
    ] == [
        (("A1AAA", "AA00"),),
        (("B2BBB", "BB11"),),
    ]
    assert all(
        recipe_build["population_mode"]
        == segment_inspector.SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION
        for recipe_build in selected_recipe_builds
    )
    assert all(
        recipe_build["snr_representation"]
        == segment_inspector.SUCCESS_SNR_REPRESENTATION_ACTUAL
        for recipe_build in selected_recipe_builds
    )
    assert drilldown_builds == [
        {
            "selected_identities": (("A1AAA", "AA00"),),
            "evidence_identities": (("A1AAA", "AA00"),),
        },
        {
            "selected_identities": (("B2BBB", "BB11"),),
            "evidence_identities": (("B2BBB", "BB11"),),
        },
    ]
    assert drilldown_renders == [
        {
            "labels": ("A1AAA (AA00)",),
            "stations": ("A1AAA",),
        },
        {
            "labels": ("B2BBB (BB11)",),
            "stations": ("B2BBB",),
        },
    ]
    assert persisted_success_selections == [
        [{"callsign": "A1AAA", "locator": "AA00"}],
        [{"callsign": "B2BBB", "locator": "BB11"}],
        [],
    ]
    assert [
        render_call["render_figure"]
        for render_call in selected_render_calls
    ] == [
        segment_inspector.render_segment_temporal_snr_export_figure,
        segment_inspector.render_segment_temporal_evidence_export_figure,
        segment_inspector.render_segment_temporal_snr_export_figure,
        segment_inspector.render_segment_temporal_evidence_export_figure,
    ]
    assert [
        render_call["recipe"]["time_bin"]
        for render_call in selected_render_calls
    ] == ["2h", "2h", "2h", "2h"]
    assert [
        dataframe_call["selection_mode"]
        for dataframe_call in fake_streamlit.dataframe_calls
    ] == ["single-row", "single-row", "single-row"]
    assert all(
        callable(dataframe_call["on_select"])
        for dataframe_call in fake_streamlit.dataframe_calls
    )
    assert all(
        dataframe_call["height"]
        == segment_inspector.COMPACT_DATAFRAME_HEIGHT_PX
        for dataframe_call in fake_streamlit.dataframe_calls
    )
    assert all(
        dataframe_call["row_height"]
        == segment_inspector.COMPACT_DATAFRAME_ROW_HEIGHT_PX
        for dataframe_call in fake_streamlit.dataframe_calls
    )
    assert (
        list(
            segment_inspector.SUCCESS_STATION_INSIGHTS_CONTROL_COLUMN_WIDTHS
        ),
        {"vertical_alignment": "center"},
    ) in fake_streamlit.column_calls
    assert (
        segment_inspector.SUCCESS_STATION_INSIGHTS_CONTROL_COLUMN_WIDTHS
        == (9, 2)
    )
    assert all(
        "Heard by Target | Heard by others only" not in markdown_body
        for markdown_body, _kwargs in fake_streamlit.markdown_calls
    )
    assert (
        [0.64, 0.36],
        {"vertical_alignment": "top"},
    ) not in fake_streamlit.column_calls
    assert [
        tuple(export_call["selected_stations"])
        for export_call in export_calls
    ] == [
        ("A1AAA (AA00)",),
        ("B2BBB (BB11)",),
        (),
    ]
    assert [
        export_call["selected_station_snr_evidence_figure_recipe"] is not None
        for export_call in export_calls
    ] == [True, True, False]
    assert [
        export_call[
            "selected_station_temporal_evidence_figure_recipe"
        ] is not None
        for export_call in export_calls
    ] == [True, True, False]
    assert all(
        export_call["selected_evidence_figure_recipe"] is None
        for export_call in export_calls
    )
    assert [
        tuple(
            export_call["drilldown_selected_df"][
                "Selected station"
            ].astype(str)
        )
        if not export_call["drilldown_selected_df"].empty
        else ()
        for export_call in export_calls
    ] == [
        ("A1AAA",),
        ("B2BBB",),
        (),
    ]
    assert (
        fake_streamlit.session_state[
            segment_inspector.RESULTS_TIME_BIN_ABSOLUTE_STATE_KEY
        ]
        == "2h"
    )
    assert (
        fake_streamlit.session_state[
            segment_inspector.RESULTS_SELECTED_STATIONS_ABSOLUTE_STATE_KEY
        ]
        == []
    )
    assert provider_requests == []
