from datetime import date, datetime, time, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from config import DEFAULT_BAND
from config.delta_snr_outlier import (
    DEFAULT_DELTA_SNR_OUTLIER_DETECTION_POLICY,
    DELTA_SNR_OUTLIER_CONFIG_FIELD_TO_POLICY_FIELD,
    DELTA_SNR_OUTLIER_MAXIMUM_THRESHOLD,
    DELTA_SNR_OUTLIER_MINIMUM_THRESHOLD,
)
from core.analysis_context import COMPARISON_NONE
from i18n import GUIDED_INPUTS, T
from ui import callbacks, state_manager
from ui.analysis_context_adapter import build_analysis_context_from_session_state
from ui.classic_input_state import is_classic_input_ready
from ui.components import config_fields, config_panel
from ui.components.config_panel import (
    _benchmark_mode_options,
    _comparison_column_widths,
)
from ui.config_io import MODE_KEYS, _default_config


class _SessionState(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def __setattr__(self, key, value):
        self[key] = value


class _NullContext:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


def test_classic_benchmark_design_excludes_canonical_performance_mode():
    canonical_modes = [
        "none",
        "reference_station",
        "local_neighborhood",
    ]
    assert list(MODE_KEYS) == canonical_modes
    for lang in ["en", "de"]:
        assert _benchmark_mode_options(T[lang]) == canonical_modes[1:]


@pytest.mark.parametrize(
    ("language", "expected_labels"),
    [
        (
            "en",
            (
                "Reference Setup/Station",
                "Reference Neighbourhood",
            ),
        ),
        (
            "de",
            (
                "Referenzaufbau/-station",
                "Referenznachbarschaft",
            ),
        ),
    ],
)
def test_classic_benchmark_selector_formats_canonical_modes_bilingually(
    monkeypatch,
    language,
    expected_labels,
):
    """Offer only the two localized designs after Benchmark is selected."""
    benchmark_selector = Mock()
    session_state = _SessionState(
        {
            "config_panels_expanded": True,
            "val_analysis_direction": "rx",
            "val_comp_mode": "none",
        }
    )
    monkeypatch.setattr(
        config_panel,
        "st",
        SimpleNamespace(
            session_state=session_state,
            expander=Mock(return_value=_NullContext()),
            columns=Mock(return_value=(_NullContext(), _NullContext())),
            radio=benchmark_selector,
        ),
    )

    labels = T[language]
    config_panel.render_benchmark_expander(labels)

    positional_args, keyword_args = benchmark_selector.call_args
    canonical_modes = [
        "reference_station",
        "local_neighborhood",
    ]
    assert positional_args == (labels["lbl_comp_mode"], canonical_modes)
    assert tuple(
        keyword_args["format_func"](benchmark_mode)
        for benchmark_mode in canonical_modes
    ) == expected_labels
    assert keyword_args["label_visibility"] == "collapsed"


@pytest.mark.parametrize(
    ("language", "expected_intro", "expected_labels", "expected_captions"),
    [
        (
            "en",
            "The **Target** is the station or controlled signal path being evaluated - likely your station. Choose whether to assess its RX or TX Performance, or Benchmark it against a Reference:",
            (
                "RX Performance",
                "TX Performance",
                "RX Benchmark",
                "TX Benchmark",
            ),
            (
                "Assess how reliably the Target RX decodes peer TX signals across confirmed opportunities.",
                "Assess how reliably active receivers hear the Target.",
                "Compare what the Target and Reference receivers hear under matched conditions.",
                "Compare how the Target and Reference transmit paths are heard under matched conditions.",
            ),
        ),
        (
            "de",
            "Als **Target** wird eine Station oder ein kontrollierter Signalpfad ausgewertet – wahrscheinlich deine Station. Wähle, ob du die RX- oder TX-Performance des Targets bewerten oder es gegen eine Referenz benchmarken möchtest:",
            (
                "RX Performance",
                "TX Performance",
                "RX-Benchmark",
                "TX-Benchmark",
            ),
            (
                "Bewerte, wie zuverlässig der Target-RX Peer-TX-Signale innerhalb bestätigter Gelegenheiten decodiert.",
                "Bewerte, wie zuverlässig nachweislich aktive Empfänger das Target hören.",
                "Vergleiche, was die Target- und Referenzempfänger unter zugeordneten Bedingungen hören.",
                "Vergleiche, wie die Target- und Referenzsendepfade unter zugeordneten Bedingungen gehört werden.",
            ),
        ),
    ],
)
def test_classic_question_selector_is_four_way_and_bilingual(
    monkeypatch,
    language,
    expected_intro,
    expected_labels,
    expected_captions,
):
    """Explain Target and each atomic Classic question in both languages."""
    question_selector = Mock()
    intro_markdown = Mock()
    monkeypatch.setattr(
        config_panel,
        "st",
        SimpleNamespace(
            session_state=_SessionState(
                {
                    "config_panels_expanded": True,
                    "classic_question": None,
                }
            ),
            expander=Mock(return_value=_NullContext()),
            markdown=intro_markdown,
            radio=question_selector,
        ),
    )

    labels = T[language]
    config_panel.render_classic_question_expander(labels, step_number=1)

    positional_args, keyword_args = question_selector.call_args
    canonical_questions = (
        "rx_performance",
        "tx_performance",
        "rx_benchmark",
        "tx_benchmark",
    )
    assert positional_args == (labels["lbl_question"], canonical_questions)
    assert tuple(
        keyword_args["format_func"](question)
        for question in canonical_questions
    ) == expected_labels
    intro_markdown.assert_called_once_with(expected_intro)
    assert keyword_args["captions"] == expected_captions
    assert keyword_args["index"] is None
    assert keyword_args["label_visibility"] == "collapsed"


@pytest.mark.parametrize(
    (
        "language",
        "expected_question_heading",
        "expected_core_heading",
        "expected_comparison_heading",
        "expected_advanced_heading",
        "expected_rx_callsign",
        "expected_tx_callsign",
        "expected_qth",
    ),
    [
        (
            "en",
            "Question",
            "Target and measurement window",
            "Benchmark design",
            "Optional filters, analysis scope, and evidence requirements",
            "Target callsign (receiver under test)",
            "Target callsign (transmitter under test)",
            "Target QTH (4 or 6 characters)",
        ),
        (
            "de",
            "Frage",
            "Target und Messzeitraum",
            "Benchmark-Design",
            "Optionale Filter, Analyseumfang und Evidenzanforderungen",
            "Target-Rufzeichen (Empfänger im Test)",
            "Target-Rufzeichen (Sender im Test)",
            "Target-QTH (4 oder 6 Zeichen)",
        ),
    ],
)
def test_classic_headings_and_target_labels_are_task_oriented(
    language,
    expected_question_heading,
    expected_core_heading,
    expected_comparison_heading,
    expected_advanced_heading,
    expected_rx_callsign,
    expected_tx_callsign,
    expected_qth,
):
    """Keep the compact Classic hierarchy explicit and bilingual."""
    labels = T[language]

    assert labels["exp_question"] == expected_question_heading
    assert labels["exp_core"] == expected_core_heading
    assert labels["exp_comp"] == expected_comparison_heading
    assert labels["lbl_comp_mode"] == expected_comparison_heading
    assert labels["exp_adv"] == expected_advanced_heading
    assert labels["lbl_callsign_rx"] == expected_rx_callsign
    assert labels["lbl_callsign_tx"] == expected_tx_callsign
    assert labels["lbl_qth"] == expected_qth


@pytest.mark.parametrize(
    ("language", "expected_labels"),
    [
        (
            "en",
            {
                "lbl_time_window": "UTC measurement window",
                "lbl_start_d": "Start Date (UTC)",
                "lbl_start_t": "Start Time (UTC)",
                "lbl_end_d": "End Date (UTC)",
                "lbl_end_t": "End Time (UTC)",
                "lbl_benchmark_offset_db": "Reference-side SNR correction (dB)",
                "lbl_reference_callsign": "Reference callsign",
                "lbl_solar": "Solar state at Target QTH",
                "lbl_max_dist": "Maximum peer distance from Target (km)",
                "lbl_min_spots": "Minimum joint evidence per station",
                "lbl_min_opportunities": "Minimum confirmed opportunities per station",
                "lbl_min_stations": "Minimum qualifying stations per map segment",
            },
        ),
        (
            "de",
            {
                "lbl_time_window": "UTC-Messzeitraum",
                "lbl_start_d": "Startdatum (UTC)",
                "lbl_start_t": "Startzeit (UTC)",
                "lbl_end_d": "Enddatum (UTC)",
                "lbl_end_t": "Endzeit (UTC)",
                "lbl_benchmark_offset_db": "Referenzseitige SNR-Korrektur (dB)",
                "lbl_reference_callsign": "Referenz-Rufzeichen",
                "lbl_solar": "Sonnenstand am Target-QTH",
                "lbl_max_dist": "Maximale Peer-Entfernung vom Target (km)",
                "lbl_min_spots": "Minimale Joint-Evidenz pro Station",
                "lbl_min_opportunities": "Minimale bestätigte Gelegenheiten pro Station",
                "lbl_min_stations": "Minimale qualifizierte Stationen pro Kartensegment",
            },
        ),
    ],
)
def test_classic_compact_control_labels_are_bilingual(language, expected_labels):
    """Keep the agreed compact labels synchronized across both languages."""
    labels = T[language]

    assert {key: labels[key] for key in expected_labels} == expected_labels


@pytest.mark.parametrize("language", ["en", "de"])
def test_classic_advanced_panel_groups_filters_scope_and_evidence(
    monkeypatch,
    language,
):
    """Expose the three scientific control groups without Guided explanations."""
    markdown = Mock()
    station_population_fields = Mock()
    scope_fields = Mock()
    evidence_threshold_fields = Mock()
    session_state = _SessionState({"config_panels_expanded": True})
    monkeypatch.setattr(
        config_panel,
        "st",
        SimpleNamespace(
            session_state=session_state,
            expander=Mock(return_value=_NullContext()),
            columns=Mock(return_value=(_NullContext(), _NullContext())),
            markdown=markdown,
        ),
    )
    monkeypatch.setattr(
        config_panel,
        "render_station_population_fields",
        station_population_fields,
    )
    monkeypatch.setattr(config_panel, "render_scope_fields", scope_fields)
    monkeypatch.setattr(
        config_panel,
        "render_evidence_threshold_fields",
        evidence_threshold_fields,
    )

    labels = T[language]
    config_panel.render_advanced_expander(labels)

    assert [call.args[0] for call in markdown.call_args_list] == [
        f"**{labels['hdr_remote_station_filters']}**",
        f"**{labels['hdr_analysis_scope']}**",
        f"**{labels['hdr_evidence_requirements']}**",
    ]
    station_population_fields.assert_called_once_with(labels)
    scope_fields.assert_called_once_with(labels)
    evidence_threshold_fields.assert_called_once_with(labels, result_type=None)


def test_population_toggles_register_explicit_edits_before_owner_callback(
    monkeypatch,
):
    """Wrap each shared toggle with its field-specific override callback."""
    toggle = Mock()
    owner_callback = Mock()
    session_state = _SessionState({"val_comp_mode": "none"})
    monkeypatch.setattr(
        config_panel,
        "st",
        SimpleNamespace(session_state=session_state, toggle=toggle),
    )

    config_fields.render_station_population_fields(
        T["en"],
        on_change=owner_callback,
        on_change_args=("scope_and_evidence",),
    )

    assert [call.kwargs["on_change"] for call in toggle.call_args_list] == [
        callbacks.handle_population_exclusion_change,
        callbacks.handle_population_exclusion_change,
    ]
    assert [call.kwargs["key"] for call in toggle.call_args_list] == [
        "_val_exclude_special_callsigns",
        "_val_filter_moving",
    ]
    assert [call.kwargs["args"] for call in toggle.call_args_list] == [
        (
            "val_exclude_special_callsigns",
            owner_callback,
            ("scope_and_evidence",),
        ),
        (
            "val_filter_moving",
            owner_callback,
            ("scope_and_evidence",),
        ),
    ]
    assert session_state.val_exclude_special_callsigns is True
    assert session_state.val_filter_moving is True
    assert session_state._val_exclude_special_callsigns is True
    assert session_state._val_filter_moving is True

    monkeypatch.setattr(
        callbacks,
        "st",
        SimpleNamespace(session_state=session_state),
    )
    session_state._val_exclude_special_callsigns = False
    callbacks.handle_population_exclusion_change(
        "val_exclude_special_callsigns",
        owner_callback,
        ("scope_and_evidence",),
    )

    assert session_state.val_exclude_special_callsigns is False
    assert session_state.val_filter_moving is True
    assert session_state._population_exclusion_overrides == {
        "val_exclude_special_callsigns": True,
        "val_filter_moving": False,
    }
    owner_callback.assert_called_once_with("scope_and_evidence")


def test_outlier_reporting_toggle_uses_presentation_only_callback_contract(
    monkeypatch,
):
    """Expose the canonical key and optional non-resetting Guided callback."""
    toggle = Mock()
    owner_callback = Mock()
    labels = {
        "lbl_report_delta_snr_outlier_candidates": "Report outliers",
        "tt_report_delta_snr_outlier_candidates": "Inspect unusual changes.",
    }
    monkeypatch.setattr(
        config_panel,
        "st",
        SimpleNamespace(session_state=_SessionState(), toggle=toggle),
    )

    config_fields.render_delta_snr_outlier_reporting_field(
        labels,
        on_change=owner_callback,
        on_change_args=("scope_and_evidence",),
    )

    toggle.assert_called_once_with(
        "Report outliers",
        key="val_report_delta_snr_outlier_candidates",
        help="Inspect unusual changes.",
        on_change=callbacks.handle_delta_snr_outlier_reporting_change,
        args=(owner_callback, ("scope_and_evidence",)),
    )


def test_enabled_outlier_reporting_renders_three_shared_gates_directly_below_toggle(
    monkeypatch,
):
    """Expose three bounded, explained gates without the retired duration matrix."""
    session_state = _SessionState(
        {
            "val_report_delta_snr_outlier_candidates": True,
            **{
                f"val_{config_field}": getattr(
                    DEFAULT_DELTA_SNR_OUTLIER_DETECTION_POLICY,
                    policy_field,
                )
                for config_field, policy_field in (
                    DELTA_SNR_OUTLIER_CONFIG_FIELD_TO_POLICY_FIELD
                )
            },
        }
    )
    number_input_calls = []
    rendered_button = Mock()
    rendered_error = Mock()
    rendered_caption = Mock()
    rendered_columns = Mock()
    fake_streamlit = SimpleNamespace(
        session_state=session_state,
        toggle=Mock(),
        caption=rendered_caption,
        columns=rendered_columns,
        number_input=lambda label, **kwargs: number_input_calls.append(
            (label, kwargs)
        ),
        error=rendered_error,
        button=rendered_button,
    )
    monkeypatch.setattr(config_panel, "st", fake_streamlit)

    config_fields.render_delta_snr_outlier_reporting_field(T["en"])

    expected_fields = [
        (
            "val_delta_snr_outlier_minimum_departure_db",
            "lbl_delta_snr_outlier_minimum_departure_db",
            "tt_delta_snr_outlier_minimum_departure_db",
            6.0,
        ),
        (
            "val_delta_snr_outlier_minimum_robust_z",
            "lbl_delta_snr_outlier_minimum_robust_z",
            "tt_delta_snr_outlier_minimum_robust_z",
            3.0,
        ),
        (
            "val_delta_snr_outlier_maximum_baseline_difference_db",
            "lbl_delta_snr_outlier_maximum_baseline_difference_db",
            "tt_delta_snr_outlier_maximum_baseline_difference_db",
            3.0,
        ),
    ]
    assert len(number_input_calls) == len(expected_fields) == 3
    for (label, kwargs), (
        state_key,
        label_key,
        help_key,
        expected_default,
    ) in zip(number_input_calls, expected_fields):
        assert label == T["en"][label_key]
        assert kwargs["key"] == state_key
        assert kwargs["help"] == T["en"][help_key]
        assert kwargs["on_change"] is config_panel.reset_audit
        assert kwargs["args"] == ()
        assert session_state[state_key] == expected_default
    assert all(
        call[1]["min_value"] == DELTA_SNR_OUTLIER_MINIMUM_THRESHOLD
        and call[1]["max_value"] == DELTA_SNR_OUTLIER_MAXIMUM_THRESHOLD
        for call in number_input_calls
    )
    rendered_caption.assert_not_called()
    rendered_columns.assert_not_called()
    rendered_error.assert_not_called()
    rendered_button.assert_called_once_with(
        "Reset detector defaults",
        key="reset_delta_snr_outlier_detector_defaults",
        on_click=callbacks.reset_delta_snr_outlier_detector_defaults,
        args=(config_panel.reset_audit, ()),
    )


def test_reset_outlier_detector_defaults_preserves_enabled_state_and_notifies_owner(
    monkeypatch,
):
    """Reset only policy scalars while leaving the opt-in and callback ownership intact."""
    session_state = _SessionState(
        {
            "val_report_delta_snr_outlier_candidates": True,
            **{
                f"val_{config_field}": 9.0
                for config_field, _policy_field in (
                    DELTA_SNR_OUTLIER_CONFIG_FIELD_TO_POLICY_FIELD
                )
            },
        }
    )
    owner_callback = Mock()
    monkeypatch.setattr(
        callbacks,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    callbacks.reset_delta_snr_outlier_detector_defaults(
        owner_callback,
        ("scope_and_evidence",),
    )

    assert session_state.val_report_delta_snr_outlier_candidates is True
    for config_field, policy_field in (
        DELTA_SNR_OUTLIER_CONFIG_FIELD_TO_POLICY_FIELD
    ):
        assert session_state[f"val_{config_field}"] == getattr(
            DEFAULT_DELTA_SNR_OUTLIER_DETECTION_POLICY,
            policy_field,
        )
    owner_callback.assert_called_once_with("scope_and_evidence")


def test_classic_outlier_callbacks_invalidate_results_without_starting_analysis(
    monkeypatch,
):
    """Use the ordinary Classic reset callback for toggle and threshold edits."""
    reset = Mock()
    session_state = _SessionState(
        {"val_report_delta_snr_outlier_candidates": True}
    )
    monkeypatch.setattr(
        callbacks,
        "st",
        SimpleNamespace(session_state=session_state),
    )
    monkeypatch.setattr(callbacks, "reset_audit", reset)

    callbacks.handle_delta_snr_outlier_reporting_change()
    callbacks.reset_delta_snr_outlier_detector_defaults()

    assert reset.call_count == 2
    assert session_state.val_report_delta_snr_outlier_candidates is True
    assert session_state.val_delta_snr_outlier_minimum_departure_db == 6.0
    assert session_state.val_delta_snr_outlier_minimum_robust_z == 3.0
    assert session_state.val_delta_snr_outlier_maximum_baseline_difference_db == 3.0


def test_classic_readiness_validates_detector_policy_only_when_enabled():
    """Disable Run for invalid visible thresholds but ignore retained opt-out tuning."""
    state = {
        "classic_question": "rx_benchmark",
        "val_analysis_direction": "rx",
        "val_comp_mode": "reference_station",
        "val_report_delta_snr_outlier_candidates": False,
        "val_delta_snr_outlier_minimum_departure_db": 0.0,
    }

    assert is_classic_input_ready(state)
    state["val_report_delta_snr_outlier_candidates"] = True
    assert not is_classic_input_ready(state)


def test_outlier_reporting_opt_out_normalizes_selection_before_owner_callback(
    monkeypatch,
):
    """Make same-rerun config and URL serialization singleton-safe."""
    callback_observations = []
    session_state = _SessionState(
        {
            "val_report_delta_snr_outlier_candidates": False,
            "val_results_selected_stations_compare": [
                {"callsign": "A1AAA", "locator": "AA00"},
                {"callsign": "B2BBB", "locator": "BB11"},
            ],
        }
    )
    monkeypatch.setattr(
        callbacks,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    callbacks.handle_delta_snr_outlier_reporting_change(
        lambda marker: callback_observations.append(
            (
                marker,
                list(session_state.val_results_selected_stations_compare),
            )
        ),
        ("after-normalization",),
    )

    assert session_state.val_results_selected_stations_compare == [
        {"callsign": "A1AAA", "locator": "AA00"}
    ]
    assert callback_observations == [
        (
            "after-normalization",
            [{"callsign": "A1AAA", "locator": "AA00"}],
        )
    ]


@pytest.mark.parametrize(
    ("result_type", "expected_calls"),
    (("performance", 0), ("benchmark", 1)),
)
def test_classic_advanced_outlier_reporting_is_benchmark_only(
    monkeypatch,
    result_type,
    expected_calls,
):
    """Hide the optional reporting setting from Classic Performance."""
    outlier_field = Mock()
    monkeypatch.setattr(
        config_panel,
        "st",
        SimpleNamespace(
            session_state=_SessionState({"config_panels_expanded": True}),
            expander=Mock(return_value=_NullContext()),
            columns=Mock(return_value=(_NullContext(), _NullContext())),
            markdown=Mock(),
        ),
    )
    monkeypatch.setattr(config_panel, "render_station_population_fields", Mock())
    monkeypatch.setattr(config_panel, "render_scope_fields", Mock())
    monkeypatch.setattr(config_panel, "render_evidence_threshold_fields", Mock())
    monkeypatch.setattr(
        config_panel,
        "render_delta_snr_outlier_reporting_field",
        outlier_field,
    )

    config_panel.render_advanced_expander(T["en"], result_type=result_type)

    assert outlier_field.call_count == expected_calls
    if result_type == "benchmark":
        outlier_field.assert_called_once_with(T["en"])




@pytest.mark.parametrize(
    ("result_type", "comparison_mode", "expected_label", "inactive_label"),
    [
        ("performance", "none", "lbl_min_opportunities", "lbl_min_spots"),
        ("benchmark", "reference_station", "lbl_min_spots", "lbl_min_opportunities"),
    ],
)
def test_shared_evidence_fields_render_only_the_active_result_threshold(
    monkeypatch,
    result_type,
    comparison_mode,
    expected_label,
    inactive_label,
):
    """Keep Guided and Classic free of the inactive result type's threshold."""
    sliders = Mock()
    session_state = _SessionState(
        {
            "val_comp_mode": comparison_mode,
            "val_analysis_direction": "rx",
            "val_min_spots": 1,
            "val_min_opportunities": 5,
            "val_min_stations": 1,
        }
    )
    monkeypatch.setattr(
        config_panel,
        "st",
        SimpleNamespace(session_state=session_state, slider=sliders),
    )

    config_fields.render_evidence_threshold_fields(
        T["en"],
        result_type=result_type,
    )

    rendered_labels = [call.args[0] for call in sliders.call_args_list]
    assert T["en"][expected_label] in rendered_labels
    assert T["en"][inactive_label] not in rendered_labels
    assert T["en"]["lbl_min_stations"] in rendered_labels


@pytest.mark.parametrize("language", ["en", "de"])
@pytest.mark.parametrize("use_two_column_layout", [False, True])
@pytest.mark.parametrize(
    ("analysis_direction", "comparison_mode", "tx_ab_method"),
    [
        ("rx", "reference_station", "simultaneous"),
        ("tx", "reference_station", "simultaneous"),
        ("tx", "reference_station", "sequential"),
        ("rx", "reference_station", "simultaneous"),
        ("tx", "reference_station", "simultaneous"),
        ("rx", "local_neighborhood", "simultaneous"),
        ("tx", "local_neighborhood", "simultaneous"),
    ],
)
def test_benchmark_segment_threshold_help_uses_reported_peer_identity(
    monkeypatch,
    language,
    use_two_column_layout,
    analysis_direction,
    comparison_mode,
    tx_ab_method,
):
    """Route one bilingual identity contract through every shared Benchmark editor path."""
    sliders = Mock()
    session_state = _SessionState(
        {
            "val_comp_mode": comparison_mode,
            "val_analysis_direction": analysis_direction,
            "val_min_spots": 1,
            "val_min_opportunities": 5,
            "val_min_stations": 2,
        }
    )
    monkeypatch.setattr(
        config_panel,
        "st",
        SimpleNamespace(
            session_state=session_state,
            slider=sliders,
            columns=Mock(return_value=(_NullContext(), _NullContext())),
        ),
    )

    config_fields.render_evidence_threshold_fields(
        T[language],
        result_type="benchmark",
        use_two_column_layout=use_two_column_layout,
    )

    station_threshold_calls = [
        slider_call
        for slider_call in sliders.call_args_list
        if slider_call.kwargs["key"] == "val_min_stations"
    ]
    assert len(station_threshold_calls) == 1
    threshold_help = station_threshold_calls[0].kwargs["help"]
    assert threshold_help == T[language]["hlp_min_stations_compare"]
    assert session_state.val_min_stations == 2
    guided_help = GUIDED_INPUTS[language]["messages"][
        "compare_evidence_requirements_body"
    ]
    expected_fragments = {
        "en": (
            "callsign + full reported locator",
            "same callsign at different locators counts separately",
            "One-sided evidence does not",
            "independent physical stations",
        ),
        "de": (
            "Rufzeichen + vollständig gemeldetem Locator",
            "dasselbe Rufzeichen mit unterschiedlichen Locatorn zählt getrennt",
            "Einseitige Evidenz",
            "physisch",
        ),
    }
    for required_fragment in expected_fragments[language]:
        assert required_fragment in threshold_help
        assert required_fragment in guided_help
    assert (
        "one station median" in guided_help
        if language == "en"
        else "einen Stationsmedian" in guided_help
    )


def test_guided_scope_fields_use_two_equal_columns(monkeypatch):
    """Place solar state and geographic distance beside each other."""
    selectbox = Mock()
    columns = Mock(return_value=(_NullContext(), _NullContext()))
    monkeypatch.setattr(
        config_panel,
        "st",
        SimpleNamespace(session_state=_SessionState(), columns=columns, selectbox=selectbox),
    )

    config_fields.render_scope_fields(
        T["en"],
        use_two_column_layout=True,
    )

    columns.assert_called_once_with(2, gap="large")
    assert [call.args[0] for call in selectbox.call_args_list] == [
        T["en"]["lbl_solar"],
        T["en"]["lbl_max_dist"],
    ]


def test_guided_evidence_fields_use_two_equal_columns(monkeypatch):
    """Place the active per-station and map-segment thresholds side by side."""
    slider = Mock()
    columns = Mock(return_value=(_NullContext(), _NullContext()))
    session_state = _SessionState(
        {
            "val_comp_mode": "reference_station",
            "val_analysis_direction": "rx",
            "val_min_spots": 1,
            "val_min_opportunities": 5,
            "val_min_stations": 1,
        }
    )
    monkeypatch.setattr(
        config_panel,
        "st",
        SimpleNamespace(
            session_state=session_state,
            columns=columns,
            slider=slider,
        ),
    )

    config_fields.render_evidence_threshold_fields(
        T["en"],
        result_type="benchmark",
        use_two_column_layout=True,
    )

    columns.assert_called_once_with(2, gap="large")
    assert [call.args[0] for call in slider.call_args_list] == [
        T["en"]["lbl_min_spots"],
        T["en"]["lbl_min_stations"],
    ]


@pytest.mark.parametrize("language", ["en", "de"])
def test_callsign_entry_guidance_recommends_standard_forms_in_both_languages(
    language,
):
    """Explain letter-only and suffix forms without treating aliases as equivalent."""
    labels = T[language]

    assert "CALL" in labels["hlp_callsign_entry"]
    assert "CALL/P" in labels["hlp_callsign_entry"]
    assert "CALL-1" in labels["hlp_callsign_entry"]
    assert "distinct" in labels["hlp_callsign_entry"].lower() or "eigene" in labels[
        "hlp_callsign_entry"
    ].lower()
    assert "CALL/P" in labels["ph_reference_callsign"]
    guided_messages = GUIDED_INPUTS[language]["messages"]
    assert "CALL" in guided_messages["target_callsign_help"]
    assert "CALL/P" in guided_messages["reference_callsign_help"]
    if language == "en":
        required_letter_text = "at least one letter"
        no_digit_text = "a digit is not required"
    else:
        required_letter_text = "mindestens einen Buchstaben"
        no_digit_text = "eine Ziffer ist nicht erforderlich"
    for error_key in ("err_callsign_format", "err_reference_callsign_format"):
        assert required_letter_text in labels[error_key]
        assert no_digit_text in labels[error_key]


@pytest.mark.parametrize(
    ("language", "expected_rx_label", "expected_tx_label"),
    [
        ("en", "RX Analysis", "TX Analysis"),
        ("de", "RX-Analyse", "TX-Analyse"),
    ],
)
def test_analysis_selector_uses_full_width_segments_without_visible_heading(
    monkeypatch,
    language,
    expected_rx_label,
    expected_tx_label,
):
    """Keep the governing direction choice visually balanced and concise."""
    segmented_control = Mock(return_value=None)
    monkeypatch.setattr(
        config_panel,
        "st",
        SimpleNamespace(
            session_state=SimpleNamespace(),
            segmented_control=segmented_control,
        ),
    )

    labels = T[language]
    config_fields.render_analysis_direction(labels)

    positional_args, keyword_args = segmented_control.call_args
    assert positional_args == (labels["lbl_analysis_selector"], ("rx", "tx"))
    assert keyword_args["selection_mode"] == "single"
    assert keyword_args["required"] is True
    assert keyword_args["key"] == "val_analysis_direction"
    assert keyword_args["label_visibility"] == "collapsed"
    assert keyword_args["width"] == "stretch"
    assert keyword_args["format_func"]("rx") == expected_rx_label
    assert keyword_args["format_func"]("tx") == expected_tx_label






@pytest.mark.parametrize("language", ["en", "de"])
@pytest.mark.parametrize("direction", ["rx", "tx"])
@pytest.mark.parametrize("method", ["local_median", "local_best"])
def test_local_benchmark_shows_fixed_method_without_mutating_state(
    monkeypatch, language, direction, method,
):
    """Keep method help in a tooltip, preserve radius and reject stale input."""
    session_state = _SessionState({
        "val_comp_mode": "local_neighborhood",
        "val_analysis_direction": direction,
        "val_local_benchmark": method,
        "val_ref_radius_km": 150,
    })
    surface = SimpleNamespace(
        session_state=session_state,
        radio=Mock(), slider=Mock(), markdown=Mock(), caption=Mock(), error=Mock(),
    )
    monkeypatch.setattr(config_panel, "st", surface)
    config_fields.render_reference_design_fields(T[language])
    surface.radio.assert_not_called()
    explanation = T[language]["txt_local_median_explanation"]
    surface.markdown.assert_called_once_with(
        f"**{T[language]['opt_local_median']}**",
        help=explanation,
    )
    surface.caption.assert_not_called()
    assert surface.slider.call_args.kwargs["key"] == "val_ref_radius_km"
    assert session_state["val_local_benchmark"] == method
    assert session_state["val_ref_radius_km"] == 150
    if method == "local_median":
        surface.error.assert_not_called()
    else:
        surface.error.assert_called_once_with(T[language]["err_local_benchmark"])


@pytest.mark.parametrize("language", ["en", "de"])
@pytest.mark.parametrize("reference_qth", ["", "JO62"])
def test_reference_identity_has_one_callsign_without_location_caption(monkeypatch, language, reference_qth):
    text_input = Mock()
    state = _SessionState({"val_callsign": "CALL", "val_qth": "JN37AA", "val_ref_callsign": "CALL/P", "val_ref_qth": reference_qth})
    surface = SimpleNamespace(session_state=state, error=Mock(), caption=Mock(), selectbox=Mock(), markdown=Mock())
    monkeypatch.setattr(config_panel, "st", surface)
    monkeypatch.setattr(config_panel, "text_input_no_autocomplete", text_input)
    config_panel._render_reference_identity(T[language])
    assert text_input.call_count == 1
    assert text_input.call_args.kwargs["key"] == "val_ref_callsign"
    assert text_input.call_args.kwargs["placeholder"] == T[language]["ph_reference_callsign"]
    surface.selectbox.assert_not_called()
    surface.caption.assert_not_called()
    assert state.val_ref_qth == reference_qth
    surface.error.assert_not_called()



def test_target_callsign_widget_uses_shared_entry_guidance(monkeypatch):
    """Accept a letter-only archive identity in the shared Target field."""
    text_input = Mock()
    error = Mock()
    session_state = _SessionState(
        {
            "config_panels_expanded": True,
            "val_analysis_direction": "rx",
            "val_callsign": "KFS",
            "val_qth": "JN37",
            "val_start_d": date(2026, 7, 1),
            "val_start_t": time(0, 0),
            "val_end_d": date(2026, 7, 2),
            "val_end_t": time(0, 0),
        }
    )
    monkeypatch.setattr(
        config_panel,
        "st",
        SimpleNamespace(
            session_state=session_state,
            columns=Mock(return_value=(_NullContext(), _NullContext())),
            error=error,
            markdown=Mock(),
            selectbox=Mock(),
            date_input=Mock(),
            time_input=Mock(),
        ),
    )
    monkeypatch.setattr(config_panel, "text_input_no_autocomplete", text_input)

    config_fields.render_target_and_window_fields(T["en"])

    target_callsign_input = next(
        call
        for call in text_input.call_args_list
        if call.kwargs.get("key") == "val_callsign"
    )
    assert target_callsign_input.kwargs["help"] == T["en"]["hlp_callsign_entry"]
    error.assert_not_called()


@pytest.mark.parametrize("language", ["en", "de"])
@pytest.mark.parametrize("input_view", ["guided", "classic"])
def test_shared_date_widgets_suggest_and_constrain_the_end_date(
    monkeypatch, language, input_view,
):
    """Keep date fields at row start with their help, callbacks and date bounds."""
    date_input = Mock()
    markdown = Mock()
    session_state = _SessionState(
        {
            "val_analysis_direction": "rx",
            "val_callsign": "DL1MKS",
            "val_qth": "JN37",
            "val_band": "20m",
            "val_start_d": date(2026, 7, 1),
            "val_start_t": time(0, 0),
            "val_end_d": date(2026, 7, 2),
            "val_end_t": time(0, 0),
        }
    )
    monkeypatch.setattr(
        config_panel,
        "st",
        SimpleNamespace(
            session_state=session_state,
            columns=Mock(return_value=(_NullContext(), _NullContext())),
            error=Mock(),
            markdown=markdown,
            selectbox=Mock(),
            date_input=date_input,
            time_input=Mock(),
        ),
    )
    monkeypatch.setattr(config_panel, "text_input_no_autocomplete", Mock())

    time_help = (
        GUIDED_INPUTS[language]["messages"]["time_help"]
        if input_view == "guided"
        else None
    )
    config_fields.render_target_and_window_fields(
        T[language], help_overrides={"time": time_help},
    )

    start_date_call, end_date_call = date_input.call_args_list
    markdown.assert_not_called()
    assert start_date_call.args == (T[language]["lbl_start_d"],)
    assert end_date_call.args == (T[language]["lbl_end_d"],)
    assert start_date_call.kwargs["help"] == time_help
    assert end_date_call.kwargs["help"] == time_help
    assert start_date_call.kwargs["on_change"] is callbacks.handle_start_date_change
    assert end_date_call.kwargs["on_change"] is callbacks.handle_time_window_change
    assert end_date_call.kwargs["min_value"] == date(2026, 7, 1)
    assert end_date_call.kwargs["max_value"] == date(2026, 8, 1)


@pytest.mark.parametrize("language", ["en", "de"])
def test_shared_time_fields_report_an_excessive_window_during_entry(
    monkeypatch,
    language,
):
    """Show the exact localized 31-day error before Run can be submitted."""
    error = Mock()
    session_state = _SessionState(
        {
            "val_analysis_direction": "rx",
            "val_callsign": "DL1MKS",
            "val_qth": "JN37",
            "val_band": "20m",
            "val_start_d": date(2026, 6, 1),
            "val_start_t": time(0, 0),
            "val_end_d": date(2026, 7, 2),
            "val_end_t": time(0, 15),
        }
    )
    monkeypatch.setattr(
        config_panel,
        "st",
        SimpleNamespace(
            session_state=session_state,
            columns=Mock(return_value=(_NullContext(), _NullContext())),
            error=error,
            markdown=Mock(),
            selectbox=Mock(),
            date_input=Mock(),
            time_input=Mock(),
        ),
    )
    monkeypatch.setattr(config_panel, "text_input_no_autocomplete", Mock())

    config_fields.render_target_and_window_fields(T[language])

    error.assert_called_once_with(T[language]["err_time_duration"])




def test_reference_station_identity_reports_invalid_reference_callsign(monkeypatch):
    state = _SessionState({"val_callsign": "CALL", "val_ref_callsign": "123", "val_ref_qth": ""})
    surface = SimpleNamespace(session_state=state, error=Mock(), caption=Mock(), selectbox=Mock(), markdown=Mock())
    monkeypatch.setattr(config_panel, "st", surface)
    monkeypatch.setattr(config_panel, "text_input_no_autocomplete", Mock())
    config_panel._render_reference_identity(T["en"])
    surface.error.assert_called_once_with(T["en"]["err_reference_callsign_format"])



@pytest.mark.parametrize("identity", ["DL1\u00df", "D\u01311ABC", "J\u212a37"])
def test_identity_normalization_does_not_expand_unicode_into_ascii(
    monkeypatch,
    identity,
):
    """Preserve non-ASCII input so validation can reject it visibly."""
    session_state = _SessionState({"identity": f" {identity} "})
    monkeypatch.setattr(
        config_panel,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    config_panel._normalize_text_state("identity", should_uppercase=True)

    assert session_state.identity == identity


def test_missing_benchmark_design_defaults_to_success_only(monkeypatch):
    session_state = _SessionState()
    monkeypatch.setattr(
        state_manager,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    before_init = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    state_manager.init_session_state()
    after_init = datetime.now(timezone.utc).replace(second=0, microsecond=0)

    assert session_state.input_view == "guided"
    assert session_state.val_analysis_direction is None
    assert session_state.val_comp_mode == "none"
    assert session_state.val_ref_callsign == ""
    assert session_state.val_ref_qth == ""
    assert session_state.val_snr_correction_mode == "no_offset"
    assert session_state.val_benchmark_offset_db == 0.0
    assert session_state.val_exclude_special_callsigns is True
    assert session_state.val_filter_moving is True
    assert session_state.val_results_show_zero_target is False
    assert session_state.val_results_selected_ranges_compare == "all"
    assert session_state.val_results_selected_directions_compare == "all"
    assert session_state.val_results_selected_ranges_absolute == "all"
    assert session_state.val_results_selected_directions_absolute == "all"
    assert session_state.val_results_segment_time_bin_absolute == "auto"
    assert session_state.val_report_delta_snr_outlier_candidates is False
    for config_field, policy_field in (
        DELTA_SNR_OUTLIER_CONFIG_FIELD_TO_POLICY_FIELD
    ):
        assert session_state[f"val_{config_field}"] == getattr(
            DEFAULT_DELTA_SNR_OUTLIER_DETECTION_POLICY,
            policy_field,
        )
    default_start_utc = datetime.combine(
        session_state.val_start_d,
        session_state.val_start_t,
        tzinfo=timezone.utc,
    )
    default_end_utc = datetime.combine(
        session_state.val_end_d,
        session_state.val_end_t,
        tzinfo=timezone.utc,
    )
    assert default_end_utc - default_start_utc == timedelta(hours=24)
    assert before_init <= default_end_utc <= after_init
    assert default_end_utc.second == default_end_utc.microsecond == 0
    assert _default_config()["benchmark_mode"] == COMPARISON_NONE
    assert _default_config()["segment_evidence_time_bin_absolute"] == "auto"
    assert _default_config()["snr_correction_mode"] == "no_offset"
    assert _default_config()["band"] == DEFAULT_BAND
    assert _default_config()["report_delta_snr_outlier_candidates"] is False
    analysis_context = build_analysis_context_from_session_state({})
    assert analysis_context.comparison_mode == COMPARISON_NONE
    assert analysis_context.band == DEFAULT_BAND
    assert analysis_context.reference_qth == ""
    assert analysis_context.max_peer_distance_km == 22000
    assert analysis_context.exclude_special_callsigns is True
    assert analysis_context.exclude_moving_stations is True


@pytest.mark.parametrize(
    "initial_state",
    [
        {
            "val_comp_mode": "reference_station",
            "val_snr_correction_mode": "no_offset",
            "val_benchmark_offset_db": 1.2,
        },
        {
            "val_comp_mode": "local_neighborhood",
            "val_snr_correction_mode": "establish_offset",
            "val_benchmark_offset_db": 0.0,
        },
    ],
)
def test_session_initialization_repairs_invalid_correction_pairs(
    monkeypatch,
    initial_state,
):
    """Keep live state inside the same mode/value contract as saved configs."""
    session_state = _SessionState(initial_state)
    monkeypatch.setattr(
        state_manager,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    state_manager.init_session_state()

    assert session_state.val_snr_correction_mode == "no_offset"
    assert session_state.val_benchmark_offset_db == 0.0


def test_correction_workflow_mode_does_not_change_analysis_context():
    """Keep operator provenance out of the scientific analysis context."""
    base_state = {
        "val_analysis_direction": "rx",
        "val_comp_mode": "reference_station",
        "val_snr_correction_mode": "no_offset",
        "val_benchmark_offset_db": 0.0,
    }
    establishment_state = {
        **base_state,
        "val_snr_correction_mode": "establish_offset",
    }

    assert build_analysis_context_from_session_state(
        base_state
    ) == build_analysis_context_from_session_state(establishment_state)


def test_outlier_reporting_toggle_does_not_change_analysis_context():
    """Keep the optional report outside scientific and provider identities."""
    base_state = {
        "val_analysis_direction": "rx",
        "val_comp_mode": "reference_station",
        "val_report_delta_snr_outlier_candidates": False,
    }
    reporting_state = {
        **base_state,
        "val_report_delta_snr_outlier_candidates": True,
        "val_delta_snr_outlier_minimum_departure_db": 4.0,
        "val_delta_snr_outlier_minimum_robust_z": 5.0,
        "val_delta_snr_outlier_maximum_baseline_difference_db": 4.0,
    }

    assert build_analysis_context_from_session_state(
        base_state
    ) == build_analysis_context_from_session_state(reporting_state)


@pytest.mark.parametrize("old_label", ["Reference Station (Buddy Test)", "Fremdes Rufzeichen (Buddy-Test)", "Local Neighborhood Benchmark"])
def test_old_localized_state_labels_are_not_converted_to_a_scientific_design(monkeypatch, old_label):
    state = _SessionState({"val_comp_mode": old_label})
    monkeypatch.setattr(state_manager, "st", SimpleNamespace(session_state=state))
    state_manager.init_session_state()
    assert state.val_comp_mode == "none"



def test_reset_config_returns_to_success_only(monkeypatch):
    session_state = _SessionState(
        {
            "lang": "en",
            "val_comp_mode": "local_neighborhood",
        }
    )
    monkeypatch.setattr(
        callbacks,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    before_reset = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    callbacks.set_reset_config()
    after_reset = datetime.now(timezone.utc).replace(second=0, microsecond=0)

    assert session_state.val_comp_mode == "none"
    assert session_state.val_band == DEFAULT_BAND
    assert session_state.val_analysis_direction is None
    assert session_state.val_ref_qth == ""
    assert session_state.val_exclude_special_callsigns is True
    assert session_state.val_filter_moving is True
    assert session_state.val_results_show_non_joint is None
    assert session_state.val_results_show_zero_target is False
    assert session_state.val_results_selected_ranges_compare == "all"
    assert session_state.val_results_selected_directions_compare == "all"
    assert session_state.val_results_selected_ranges_absolute == "all"
    assert session_state.val_results_selected_directions_absolute == "all"
    assert session_state.val_results_time_bin_compare is None
    assert session_state.val_results_time_bin_absolute is None
    assert session_state.val_results_segment_time_bin_absolute == "auto"
    assert session_state.val_report_delta_snr_outlier_candidates is False
    reset_start_utc = datetime.combine(
        session_state.val_start_d,
        session_state.val_start_t,
        tzinfo=timezone.utc,
    )
    reset_end_utc = datetime.combine(
        session_state.val_end_d,
        session_state.val_end_t,
        tzinfo=timezone.utc,
    )
    assert reset_end_utc - reset_start_utc == timedelta(hours=24)
    assert before_reset <= reset_end_utc <= after_reset
    assert reset_end_utc.second == reset_end_utc.microsecond == 0


def test_compare_session_starts_with_both_population_exclusions_off(monkeypatch):
    """Apply Compare defaults when that result family owns a new session."""
    session_state = _SessionState({"val_comp_mode": "reference_station"})
    monkeypatch.setattr(
        state_manager,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    state_manager.init_session_state()

    assert session_state.val_exclude_special_callsigns is False
    assert session_state.val_filter_moving is False


def test_mode_defaults_follow_untouched_fields_and_preserve_manual_edits(
    monkeypatch,
):
    """Keep explicit filter choices while untouched fields follow result defaults."""
    session_state = _SessionState()
    monkeypatch.setattr(
        state_manager,
        "st",
        SimpleNamespace(session_state=session_state),
    )
    state_manager.init_session_state()
    monkeypatch.setattr(
        callbacks,
        "st",
        SimpleNamespace(session_state=session_state),
    )
    monkeypatch.setattr(callbacks, "reset_audit", lambda: None)

    session_state._val_exclude_special_callsigns = False
    callbacks.handle_population_exclusion_change(
        "val_exclude_special_callsigns"
    )
    session_state.val_comp_mode = "reference_station"
    callbacks.handle_comp_mode_change()

    assert session_state.val_exclude_special_callsigns is False
    assert session_state.val_filter_moving is False

    session_state.val_comp_mode = "reference_station"
    callbacks.handle_comp_mode_change()
    assert session_state.val_exclude_special_callsigns is False
    assert session_state.val_filter_moving is False

    session_state.val_comp_mode = "none"
    callbacks.handle_comp_mode_change()
    assert session_state.val_exclude_special_callsigns is False
    assert session_state.val_filter_moving is True




@pytest.mark.parametrize("analysis_direction", ["rx", "tx"])
def test_analysis_context_has_one_direction_discriminator(analysis_direction):
    context = build_analysis_context_from_session_state({"val_analysis_direction": analysis_direction, "run_mode": analysis_direction.upper()})
    assert context.run_mode == analysis_direction.upper()
    assert not hasattr(context, "self_test_mode")
    assert not hasattr(context, "tx_ab_method")





def test_analysis_context_preserves_reference_station_grid4():
    """Keep the independently authored Buddy grid in Reference Station mode."""
    analysis_context = build_analysis_context_from_session_state(
        {
            "lang": "en",
            "val_analysis_direction": "tx",
            "val_comp_mode": "reference_station",
            "val_qth": "JN37AA",
            "val_ref_qth": "jo62",
        }
    )

    assert analysis_context.reference_qth == "JO62"


def test_direction_change_clears_reference_resolution_and_correction(monkeypatch):
    state = _SessionState({"val_comp_mode": "reference_station", "val_ref_callsign": "CALL/P", "val_ref_qth": "JN37", "val_benchmark_offset_db": 1.5, "_reference_location_resolution": {"status": "resolved"}})
    monkeypatch.setattr(callbacks, "st", SimpleNamespace(session_state=state))
    monkeypatch.setattr(callbacks, "reset_audit", lambda: None)
    callbacks.handle_analysis_direction_change()
    assert state.val_comp_mode == "reference_station"
    assert state.val_ref_callsign == "CALL/P"
    assert state.val_ref_qth == ""
    assert "_reference_location_resolution" not in state
    assert state.val_benchmark_offset_db == 0.0





@pytest.mark.parametrize("comparison_mode", ["reference_station", "local_neighborhood"])
def test_classic_direction_change_clears_direction_specific_correction(
    monkeypatch,
    comparison_mode,
):
    """Match Guided handling of fixed-station and neighborhood baselines."""
    session_state = _SessionState(
        {
            "val_comp_mode": comparison_mode,
            "guided_last_benchmark_mode": comparison_mode,
            "val_snr_correction_mode": "established_offset",
            "val_benchmark_offset_db": -0.8,
        }
    )
    monkeypatch.setattr(
        callbacks,
        "st",
        SimpleNamespace(session_state=session_state),
    )
    monkeypatch.setattr(callbacks, "reset_audit", lambda: None)

    callbacks.handle_analysis_direction_change()

    assert session_state.val_comp_mode == comparison_mode
    assert session_state.guided_last_benchmark_mode == comparison_mode
    assert session_state.val_benchmark_offset_db == 0.0
    assert session_state.val_snr_correction_mode == "no_offset"




def test_comparison_designs_use_equal_columns():
    for comparison_mode in _benchmark_mode_options(T["en"]):
        for analysis_direction in (None, "rx", "tx"):
            assert _comparison_column_widths(T["en"], comparison_mode, analysis_direction) == [0.5, 0.5]



@pytest.mark.parametrize(
    "benchmark_mode",
    [
        "reference_station",
        "local_neighborhood",
    ],
)
def test_each_benchmark_design_starts_with_zero_snr_correction(monkeypatch, benchmark_mode):
    session_state = _SessionState(
        {
            "val_comp_mode": benchmark_mode,
            "val_benchmark_offset_db": -99.9,
            "val_ref_callsign": "CALL/P",
            "val_ref_qth": "IO90",
            "_reference_location_resolution": {"status": "resolved"},
        }
    )
    monkeypatch.setattr(
        callbacks,
        "st",
        SimpleNamespace(session_state=session_state),
    )
    monkeypatch.setattr(callbacks, "reset_audit", lambda: None)

    callbacks.handle_comp_mode_change()

    assert session_state.val_benchmark_offset_db == 0.0
    assert session_state.val_ref_callsign == "CALL/P"
    assert session_state.val_ref_qth == ""
    assert "_reference_location_resolution" not in session_state


def test_classic_context_edit_clears_established_reference_correction(monkeypatch):
    """Do not carry a pair correction across Classic identity/QTH/band edits."""
    session_state = _SessionState(
        {
            "val_comp_mode": "reference_station",
            "guided_last_benchmark_mode": "reference_station",
            "val_snr_correction_mode": "established_offset",
            "val_benchmark_offset_db": 1.2,
        }
    )
    reset = Mock()
    monkeypatch.setattr(
        callbacks,
        "st",
        SimpleNamespace(session_state=session_state),
    )
    monkeypatch.setattr(callbacks, "reset_experiment_definition", reset)

    callbacks.handle_reference_correction_context_change()

    assert session_state.val_benchmark_offset_db == 0.0
    assert session_state.val_snr_correction_mode == "no_offset"
    reset.assert_called_once_with()


def test_classic_nonzero_correction_edit_sets_established_mode(monkeypatch):
    """Keep Classic numeric edits consistent with the durable correction mode."""
    callback = Mock()
    session_state = _SessionState(
        {
            "val_comp_mode": "reference_station",
            "val_snr_correction_mode": "no_offset",
            "val_benchmark_offset_db": 1.24,
        }
    )
    monkeypatch.setattr(
        config_panel,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    config_panel._normalize_reference_correction_state(callback)

    assert session_state.val_benchmark_offset_db == 1.2
    assert session_state.val_snr_correction_mode == "established_offset"
    callback.assert_called_once_with()


def test_reference_correction_renders_as_blank_text_with_decimal_point_placeholder(
    monkeypatch,
):
    """Render a text-only decimal field without number-input steppers."""
    text_input = Mock()
    number_input = Mock()
    session_state = _SessionState({"val_benchmark_offset_db": 0.0})
    monkeypatch.setattr(
        config_panel,
        "st",
        SimpleNamespace(
            session_state=session_state,
            text_input=text_input,
            number_input=number_input,
            error=Mock(),
        ),
    )

    config_panel.render_reference_correction_field(T["en"])

    number_input.assert_not_called()
    text_input.assert_called_once()
    assert session_state[config_panel._REFERENCE_CORRECTION_TEXT_KEY] == ""
    assert text_input.call_args.kwargs["placeholder"] == "0.0"
    assert text_input.call_args.kwargs["autocomplete"] == "off"


@pytest.mark.parametrize(
    ("correction_text", "expected_correction_db", "expected_text"),
    [
        ("1.24", 1.2, "1.2"),
        ("-1.25", -1.2, "-1.2"),
        ("+0.04", 0.0, ""),
        ("", 0.0, ""),
    ],
)
def test_reference_correction_text_accepts_decimal_points_and_blank_zero(
    monkeypatch,
    correction_text,
    expected_correction_db,
    expected_text,
):
    """Convert accepted point-decimal text into the canonical float state."""
    callback = Mock()
    session_state = _SessionState(
        {
            "val_comp_mode": "reference_station",
            "val_snr_correction_mode": "no_offset",
            "val_benchmark_offset_db": 0.0,
            config_panel._REFERENCE_CORRECTION_TEXT_KEY: correction_text,
        }
    )
    monkeypatch.setattr(
        config_panel,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    config_panel._normalize_reference_correction_state(callback)

    assert session_state.val_benchmark_offset_db == expected_correction_db
    assert (
        session_state[config_panel._REFERENCE_CORRECTION_TEXT_KEY]
        == expected_text
    )
    callback.assert_called_once_with()


@pytest.mark.parametrize("correction_text", ["1,2", "100.0", "nan", "1e1"])
def test_reference_correction_text_rejects_non_point_or_out_of_range_values(
    monkeypatch,
    correction_text,
):
    """Reject ambiguous or unsafe text without changing scientific state."""
    callback = Mock()
    session_state = _SessionState(
        {
            "val_comp_mode": "reference_station",
            "val_snr_correction_mode": "established_offset",
            "val_benchmark_offset_db": 1.2,
            config_panel._REFERENCE_CORRECTION_TEXT_KEY: correction_text,
        }
    )
    monkeypatch.setattr(
        config_panel,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    config_panel._normalize_reference_correction_state(callback)

    assert session_state.val_benchmark_offset_db == 1.2
    assert session_state[config_panel._REFERENCE_CORRECTION_TEXT_KEY] == "1.2"
    assert session_state[config_panel._REFERENCE_CORRECTION_ERROR_KEY] is True
    callback.assert_not_called()


def test_classic_zero_correction_preserves_explicit_established_mode(monkeypatch):
    """Do not infer that an explicitly established 0.0 dB means no offset."""
    session_state = _SessionState(
        {
            "val_comp_mode": "reference_station",
            "val_snr_correction_mode": "established_offset",
            "val_benchmark_offset_db": 0.0,
        }
    )
    monkeypatch.setattr(
        config_panel,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    config_panel._normalize_reference_correction_state()

    assert session_state.val_snr_correction_mode == "established_offset"




def test_removed_all_band_session_state_returns_to_exact_default(monkeypatch):
    session_state = _SessionState({"val_band": "All"})
    monkeypatch.setattr(
        state_manager,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    state_manager.init_session_state()

    assert session_state.val_band == DEFAULT_BAND


def test_json_demo_configuration_applies_complete_deterministic_state(monkeypatch):
    """Load an active demo entirely from its embedded versioned config document."""
    session_state = _SessionState(
        {"lang": "en", "val_max_peer_distance_km": 22000}
    )
    monkeypatch.setattr(
        callbacks,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    callbacks._apply_demo_profile_values("milazzo_tx_buddy")

    assert session_state.val_callsign == "KP4MD"
    assert session_state.val_qth == "CM98"
    assert session_state.val_band == "40m"
    assert session_state.val_ref_callsign == "WB6RQN"
    assert session_state.val_snr_correction_mode == "no_offset"
    assert session_state.val_analysis_direction == "rx"
    assert session_state.val_comp_mode == "reference_station"
    assert session_state.val_max_peer_distance_km == 5000
    assert session_state.val_min_opportunities == 5
    assert session_state.val_report_delta_snr_outlier_candidates is False
    assert session_state.val_results_show_non_joint is False
    assert session_state.val_results_show_zero_target is False
    assert session_state.val_results_selected_ranges_compare == "all"
    assert session_state.val_results_selected_directions_compare == "all"
    assert session_state.val_results_selected_ranges_absolute == "all"
    assert session_state.val_results_selected_directions_absolute == "all"
    assert session_state.val_results_time_bin_compare == "3h"
    assert session_state.val_results_time_bin_absolute == "3h"
    assert session_state.val_results_segment_time_bin_absolute == "auto"
    assert session_state.val_results_selected_stations_compare == [
        {"callsign": "VE6PDQ", "locator": "DO34IR"}
    ]
    assert session_state.val_start_d == date(2010, 12, 19)
    assert session_state.val_start_t == time(12, 0)
    assert session_state.val_end_d == date(2010, 12, 20)
    assert session_state.val_end_t == time(20, 0)
