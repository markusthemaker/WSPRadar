"""Integration contracts for Guided callbacks and terminal action gating."""

import ast
from copy import deepcopy
from datetime import date, time
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from streamlit.testing.v1 import AppTest

from i18n import GUIDED_INPUTS, RESULT_GUIDANCE, T
from ui import callbacks, classic_inputs, config_io, page_navigation
from ui.analysis_context_adapter import build_analysis_context_from_session_state
from ui.analysis_submission_state import (
    begin_main_analysis_submission,
    claim_analysis_submission_request,
    get_analysis_submission,
)
from ui.classic_input_state import (
    CLASSIC_BENCHMARK_DESIGN_WIDGET_KEY,
    CLASSIC_QUESTION_KEY,
    is_classic_input_ready,
)
from ui.guided_inputs import renderer
from ui.guided_inputs.state import reconstruct_guided_transients
from ui.population_exclusion_state import initialize_population_exclusion_state


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
APPLICATION_RESULT_PREFIX = "WSPRADAR_GUIDED_APPLICATION_RESULT="
APPLICATION_PROBE = r'''
from datetime import date, time
import json
from pathlib import Path
import sys

from streamlit.testing.v1 import AppTest

from i18n import T


project_root = Path(sys.argv[1]).resolve()
initial_state = json.loads(sys.argv[2])
click_run = initial_state.pop("_probe_click_run", False)
time_edits = initial_state.pop("_probe_time_edits", [])
application = AppTest.from_file(
    str(project_root / "app.py"),
    default_timeout=60,
)
application.session_state["_initial_config_loaded"] = True
for key, value in initial_state.items():
    if key in {"val_start_d", "val_end_d"}:
        value = date.fromisoformat(value)
    elif key in {"val_start_t", "val_end_t"}:
        value = time.fromisoformat(value)
    application.session_state[key] = value
application.run()
for key, value in time_edits:
    application.time_input(key).set_value(time.fromisoformat(value)).run()
if time_edits:
    application.run()
if click_run:
    application.button(key="run_analysis_button").click().run()
result = {
    "field_errors": dict(application.session_state["_input_field_errors"]) if "_input_field_errors" in application.session_state else {},
    "field_error_styles": [item.value for item in application.markdown if item.value.startswith("<style>.st-key-")],
    "run_mode": application.session_state["run_mode"],
    "time_values": {
        key: application.session_state[key].isoformat()
        for key in ("val_start_t", "val_end_t")
    },
    "exceptions": [str(exception.value) for exception in application.exception],
    "run_actions": [
        {
            "label": button.label,
            "disabled": button.disabled,
            "type": button.proto.type,
        }
        for button in application.button
        if button.key == "run_analysis_button"
    ],
    "save_actions": [
        {
            "label": popover.proto.popover.label,
            "disabled": popover.proto.popover.disabled,
        }
        for popover in application.get("popover")
        if popover.proto.popover.label == T[application.session_state["lang"]]["btn_save_config"]
    ],
    "warnings": [warning.value for warning in application.warning],
    "errors": [error.value for error in application.error],
}
print("WSPRADAR_GUIDED_APPLICATION_RESULT=" + json.dumps(result, sort_keys=True))
'''


class _SessionState(dict):
    """Provide Streamlit-like attribute access over an ordinary test mapping."""

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def __setattr__(self, key, value):
        self[key] = value


class _NullContext:
    """Stand in for Streamlit containers and expanders."""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


def _canonical_state(**overrides):
    """Return one complete RX configuration suitable for callback contracts."""
    state = _SessionState(
        {
            "lang": "en",
            "input_view": "guided",
            "run_mode": None,
            "run_id": 17,
            "active_demo_profile": None,
            "guided_use_case": "rx_performance",
            "guided_reference_design": None,
            "guided_last_benchmark_mode": None,
            "val_snr_correction_mode": "no_offset",
            "guided_scope_mode": "general",
            "guided_active_node": "use_case",
            "guided_collapse_all": False,
            "configuration_changed_since_run": False,
            "val_analysis_direction": "rx",
            "val_callsign": "DL1ABC",
            "val_qth": "JO62QM",
            "val_band": "40m",
            "val_start_d": date(2026, 7, 1),
            "val_start_t": time(0, 0),
            "val_end_d": date(2026, 7, 2),
            "val_end_t": time(0, 0),
            "val_comp_mode": "none",
            "val_local_benchmark": "local_median",
            "val_ref_callsign": "",
            "val_ref_qth": "",
            "val_ref_radius_km": 100,
            "val_benchmark_offset_db": 0.0,
            "val_solar": "all",
            "val_max_peer_distance_km": 22000,
            "val_exclude_special_callsigns": False,
            "val_filter_moving": False,
            "val_min_spots": 1,
            "val_min_opportunities": 5,
            "val_min_stations": 1,
            "val_report_delta_snr_outlier_candidates": False,
        }
    )
    state.update(overrides)
    return state


def _install_shared_streamlit_state(monkeypatch, session_state):
    """Make renderer and callback modules operate on one canonical mapping."""
    fake_streamlit = SimpleNamespace(session_state=session_state)
    monkeypatch.setattr(renderer, "st", fake_streamlit)
    monkeypatch.setattr(callbacks, "st", fake_streamlit)


def test_guided_scope_render_never_reapplies_hidden_demo_or_default_presets(
    monkeypatch,
):
    """Display current canonical values without a hidden preset mutation path."""
    session_state = _canonical_state(
        guided_loaded_demo_profile="benchmark-demo",
        guided_scope_mode="demo",
        val_max_peer_distance_km=5000,
    )
    monkeypatch.setattr(
        renderer,
        "st",
        SimpleNamespace(
            session_state=session_state,
            markdown=Mock(),
            caption=Mock(),
        ),
    )
    monkeypatch.setattr(renderer, "render_station_population_fields", Mock())
    monkeypatch.setattr(renderer, "render_scope_fields", Mock())
    monkeypatch.setattr(renderer, "render_evidence_threshold_fields", Mock())

    renderer._render_scope_and_evidence_fields(T["en"], GUIDED_INPUTS["en"])

    assert session_state.val_max_peer_distance_km == 5000
    assert not hasattr(renderer, "_handle_scope_mode_change")
    assert not hasattr(renderer, "_apply_loaded_demo_scope")


def test_input_view_selector_uses_concise_wizard_and_panel_labels():
    """Keep both localized selector options concise and visually distinct."""
    expected_labels = {
        "en": {"guided": "Guided", "classic": "Classic"},
        "de": {"guided": "Geführt", "classic": "Klassisch"},
    }

    for language, labels in expected_labels.items():
        assert {
            input_view: GUIDED_INPUTS[language]["mode"][input_view]
            for input_view in ("guided", "classic")
        } == labels


def test_classic_keeps_every_input_panel_open_and_mounts_actions_in_review(
    monkeypatch,
):
    """Ignore stale collapse state and reuse the ready shared Review panel."""
    session_state = _canonical_state(
        input_view="classic",
        config_panels_expanded=False,
        _collapse_config_panels_once=True,
    )
    panel_state_observations = []
    review_expanders = []

    def record_input_panel(*_args, **_kwargs):
        panel_state_observations.append(
            (
                session_state.config_panels_expanded,
                session_state._collapse_config_panels_once,
            )
        )

    def record_review_expander(label, *, expanded, icon):
        review_expanders.append((label, expanded, icon))
        return _NullContext()

    review_slot = Mock()
    monkeypatch.setattr(
        classic_inputs,
        "st",
        SimpleNamespace(
            session_state=session_state,
            expander=record_review_expander,
            markdown=Mock(),
            info=Mock(),
            empty=Mock(),
        ),
    )
    monkeypatch.setattr(
        classic_inputs,
        "render_classic_question_expander",
        record_input_panel,
    )
    monkeypatch.setattr(classic_inputs, "render_core_expander", record_input_panel)
    monkeypatch.setattr(
        classic_inputs,
        "render_benchmark_expander",
        record_input_panel,
    )
    monkeypatch.setattr(
        classic_inputs,
        "render_advanced_expander",
        record_input_panel,
    )
    monkeypatch.setattr(
        classic_inputs,
        "is_canonical_configuration_ready",
        lambda _state: True,
    )
    shared_review = Mock(return_value=review_slot)
    monkeypatch.setattr(
        classic_inputs,
        "render_configuration_review",
        shared_review,
    )

    render_result = classic_inputs.render_classic_inputs(T["en"])

    assert panel_state_observations == [(True, False)] * 3
    assert review_expanders == [
        (
            "4 · Review — ready to run ✓",
            True,
            ":material/route:",
        )
    ]
    assert render_result.is_ready is True
    assert render_result.review_actions_slot is review_slot
    shared_review.assert_called_once_with(
        classic_inputs.st,
        T["en"],
        GUIDED_INPUTS["en"],
        session_state,
    )


def test_classic_review_does_not_claim_readiness_for_invalid_configuration(
    monkeypatch,
):
    """Use the neutral Review-and-run title until canonical values validate."""
    session_state = _canonical_state(
        input_view="classic",
        val_callsign="",
    )
    review_expanders = []
    info = Mock()
    empty_slot = Mock()
    monkeypatch.setattr(
        classic_inputs,
        "st",
        SimpleNamespace(
            session_state=session_state,
            expander=lambda label, **kwargs: (
                review_expanders.append((label, kwargs)) or _NullContext()
            ),
            markdown=Mock(),
            info=info,
            empty=Mock(return_value=empty_slot),
        ),
    )
    for renderer_name in (
        "render_classic_question_expander",
        "render_core_expander",
        "render_benchmark_expander",
        "render_advanced_expander",
    ):
        monkeypatch.setattr(classic_inputs, renderer_name, Mock())

    render_result = classic_inputs.render_classic_inputs(T["en"])

    assert review_expanders == [
        (
            "4 · Review and run",
            {"expanded": True, "icon": ":material/route:"},
        )
    ]
    assert render_result.is_ready is False
    assert render_result.review_actions_slot is empty_slot
    info.assert_called_once_with(
        GUIDED_INPUTS["en"]["validation"]["review_and_run"]
    )


def test_guided_definitions_reuse_documentation_defined_term_markup():
    """Highlight introduced domain terms without recoloring ordinary emphasis."""
    expected_terms = {
        "en": ("Target", "Performance", "Benchmark"),
        "de": ("Target", "Performance", "Benchmark"),
    }

    for language, terms in expected_terms.items():
        guided_step_text = " ".join(
            step["body_md"]
            for step in GUIDED_INPUTS[language]["steps"].values()
        )
        for term in terms:
            assert (
                f'<strong class="defined-term">{term}</strong>'
                in guided_step_text
            )

    renderer_source = (
        REPOSITORY_ROOT / "ui" / "guided_inputs" / "renderer.py"
    ).read_text(encoding="utf-8")
    body_markdown_calls = [
        node
        for node in ast.walk(ast.parse(renderer_source))
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "st"
        and node.func.attr == "markdown"
        and node.args
        and any(
            isinstance(argument, ast.Subscript)
            and isinstance(argument.value, ast.Name)
            and argument.value.id == "content"
            and isinstance(argument.slice, ast.Constant)
            and argument.slice.value == "body_md"
            for argument in ast.walk(node.args[0])
        )
    ]
    assert len(body_markdown_calls) == 1
    assert any(
        keyword.arg == "unsafe_allow_html"
        and isinstance(keyword.value, ast.Constant)
        and keyword.value.value is True
        for keyword in body_markdown_calls[0].keywords
    )


def test_reference_design_options_route_localized_descriptions_into_shared_choices(monkeypatch):
    """Place each complete explanation directly under its Reference choice."""
    for language in ("en", "de"):
        markdown = Mock()
        selector = Mock()
        monkeypatch.setattr(renderer, "render_reference_design_selector", selector)
        monkeypatch.setattr(
            renderer,
            "st",
            SimpleNamespace(
                session_state=_canonical_state(lang=language),
                markdown=markdown,
                columns=Mock(return_value=(_NullContext(), _NullContext())),
            ),
        )

        renderer._render_reference_design_fields(
            T[language],
            GUIDED_INPUTS[language],
        )

        markdown.assert_not_called()
        options = GUIDED_INPUTS[language]["options"]["reference_design"]
        positional_args, keyword_args = selector.call_args
        assert positional_args == (T[language],)
        assert keyword_args["descriptions"] == {
            mode: option["description"] for mode, option in options.items()
        }
        assert all(set(option) == {"label", "description"} for option in options.values())
        assert keyword_args["widget_key"] == "guided_reference_design"
        assert keyword_args["on_change"] is renderer._handle_reference_design_change
        assert [T[language][f"opt_benchmark_{mode}"] for mode in options] == [
            option["label"] for option in options.values()
        ]


def test_guided_reference_uses_shared_fields_without_duplicate_explanations(
    monkeypatch,
):
    """Use the shared field tooltips instead of repeating the Reference intro."""
    cases = (
        ("reference_station", "tx"),
        ("local_neighborhood", "rx"),
    )

    for benchmark_mode, analysis_direction in cases:
        markdown = Mock()
        caption = Mock()
        shared_reference_fields = Mock()
        correction_field = Mock()
        monkeypatch.setattr(
            renderer,
            "st",
            SimpleNamespace(
                session_state=_canonical_state(
                    guided_reference_design=benchmark_mode,
                    val_comp_mode=benchmark_mode,
                    val_analysis_direction=analysis_direction,
                ),
                markdown=markdown,
                caption=caption,
                radio=Mock(),
                info=Mock(),
                warning=Mock(),
                columns=Mock(return_value=(_NullContext(), _NullContext())),
            ),
        )
        monkeypatch.setattr(
            renderer,
            "render_reference_design_fields",
            shared_reference_fields,
        )
        monkeypatch.setattr(renderer, "render_reference_correction_field", correction_field)
        monkeypatch.setattr(renderer, "render_reference_design_selector", Mock())

        renderer._render_reference_design_fields(T["en"], GUIDED_INPUTS["en"])

        markdown.assert_not_called()
        caption.assert_not_called()
        correction_field.assert_not_called()
        keyword_args = shared_reference_fields.call_args.kwargs
        assert "local_benchmark_content" not in keyword_args
        assert "should_show_local_benchmark_explanation" not in keyword_args
        assert "tx_ab_method_content" not in keyword_args
        assert "help_overrides" not in keyword_args


@pytest.mark.parametrize("input_view", ["guided", "classic"])
@pytest.mark.parametrize("language", ["en", "de"])
def test_reference_layout_keeps_correction_in_its_editor_specific_section(input_view, language):
    """Keep one correction input in Guided offset or Classic Reference fields."""
    script = '''
import streamlit as st
from i18n import GUIDED_INPUTS, T
from ui.components.config_panel import render_benchmark_expander
from ui.guided_inputs import renderer

language = st.session_state.lang
if st.session_state.input_view == "classic":
    render_benchmark_expander(T[language])
else:
    renderer._render_reference_design_fields(T[language], GUIDED_INPUTS[language])
    renderer._render_offset_calibration_fields(T[language], GUIDED_INPUTS[language])
    st.button("Continue to calibration", key="layout_continue_calibration",
              on_click=renderer._continue_to, args=("offset_calibration",))
'''
    application = AppTest.from_string(script, default_timeout=10)
    initial_state = _canonical_state(
        input_view=input_view,
        lang=language,
        guided_use_case="rx_benchmark",
        classic_question="rx_benchmark",
        guided_reference_design="reference_station",
        val_comp_mode="reference_station",
        val_ref_callsign="CALL/P",
        val_ref_qth="JO63",
    )
    for key, value in initial_state.items():
        application.session_state[key] = value
    application.run()
    assert application.exception.values == []
    columns = application.get("column")
    selector_key = "guided_reference_design" if input_view == "guided" else CLASSIC_BENCHMARK_DESIGN_WIDGET_KEY
    if input_view == "guided":
        assert [widget.key for widget in columns[0].button] == [
            f"{selector_key}_reference_station", f"{selector_key}_local_neighborhood"
        ]
        assert len(columns[0].get("popover")) == 2
    else:
        assert [widget.key for widget in columns[0].radio] == [selector_key]
        assert len(columns[0].button) == 0
        assert len(columns[0].get("popover")) == 0
        selector = application.radio(selector_key)
        assert selector.value == "reference_station"
        assert T[language]["hlp_benchmark_reference_station"] in selector.proto.help
        assert T[language]["hlp_benchmark_local_neighborhood"] in selector.proto.help
        assert T[language]["hlp_reference_callsign"] not in selector.proto.help
        assert T[language]["hlp_reference_radius"] not in selector.proto.help
        assert application.text_input("val_ref_callsign").proto.help == T[language]["hlp_reference_callsign"]
    expected_captions = (
        tuple(
            option["description"]
            for option in GUIDED_INPUTS[language]["options"]["reference_design"].values()
        )
        if input_view == "guided"
        else ()
    )
    assert tuple(caption.value for caption in columns[0].caption) == expected_captions
    assert len(columns[0].text_input) == 0
    reference_field_keys = ["val_ref_callsign"]
    if input_view == "classic":
        reference_field_keys.append("_val_benchmark_offset_db_text")
    reference_column = next(
        column for column in columns
        if any(widget.key == "val_ref_callsign" for widget in column.text_input)
    )
    assert [widget.key for widget in reference_column.text_input] == reference_field_keys
    assert len(application.text_input) == len(reference_field_keys)
    assert len(application.caption) == len(expected_captions)
    assert len(application.info) == 0
    assert application.session_state["val_ref_qth"] == "JO63"
    if input_view == "guided":
        application.radio("val_snr_correction_mode").set_value("established_offset").run()
        assert application.exception.values == []
        assert application.text_input("val_ref_callsign").proto.help == T[language]["hlp_reference_callsign"]
        assert [widget.key for widget in application.text_input] == [
            "val_ref_callsign", "_val_benchmark_offset_db_text",
        ]
        assert application.session_state["val_snr_correction_mode"] == "established_offset"
    assert application.text_input("_val_benchmark_offset_db_text").value == ""

    if input_view == "guided":
        application.text_input("_val_benchmark_offset_db_text").set_value("0.0").run()
        assert application.exception.values == []
        assert application.session_state["val_benchmark_offset_db"] == 0.0
        assert application.session_state["val_snr_correction_mode"] == "established_offset"

    application.text_input("_val_benchmark_offset_db_text").set_value("-1.7").run()
    assert application.exception.values == []
    assert application.session_state["val_benchmark_offset_db"] == -1.7
    assert application.session_state["val_snr_correction_mode"] == "established_offset"
    assert application.session_state["val_ref_qth"] == "JO63"
    if input_view == "guided":
        assert application.session_state["guided_active_node"] == "offset_calibration"
        application.button("layout_continue_calibration").click().run()
        assert application.session_state["guided_active_node"] == "offset_calibration"
        assert application.session_state["val_benchmark_offset_db"] == -1.7
        assert len(application.text_input) == 2
        assert application.radio("val_snr_correction_mode").value == "established_offset"
        application.radio("val_snr_correction_mode").set_value("no_offset").run()
        assert application.exception.values == []
        assert application.session_state["val_benchmark_offset_db"] == 0.0
        assert [widget.key for widget in application.text_input] == ["val_ref_callsign"]
        application.radio("val_snr_correction_mode").set_value("establish_offset").run()
        assert application.exception.values == []
        assert application.session_state["val_benchmark_offset_db"] == 0.0
        assert [widget.key for widget in application.text_input] == ["val_ref_callsign"]
    else:
        application.radio(selector_key).set_value("local_neighborhood").run()
        assert application.exception.values == []
        assert application.session_state["val_comp_mode"] == "local_neighborhood"
        assert application.slider("val_ref_radius_km").proto.help == T[language]["hlp_reference_radius"]
        selector_help = application.radio(selector_key).proto.help
        assert selector_help == selector.proto.help
        assert T[language]["hlp_benchmark_reference_station"] in selector_help
        assert T[language]["hlp_benchmark_local_neighborhood"] in selector_help
        assert T[language]["hlp_reference_radius"] not in selector_help
        assert T[language]["hlp_reference_callsign"] not in selector_help
        assert application.text_input("_val_benchmark_offset_db_text").proto.help == (
            T[language]["hlp_benchmark_offset_db"]
        )
        application.radio(selector_key).set_value("reference_station").run()
        assert application.exception.values == []
        assert application.session_state["val_comp_mode"] == "reference_station"
        assert application.text_input("val_ref_callsign").value == "CALL/P"
        assert application.text_input("val_ref_callsign").proto.help == T[language]["hlp_reference_callsign"]


@pytest.mark.parametrize("intent", ["no_offset", "established_offset", "establish_offset"])
def test_offset_intent_options_use_localized_captioned_radio_rows(monkeypatch, intent):
    """Make each complete offset explanation part of its selection."""
    for language in ("en", "de"):
        markdown = Mock()
        radio = Mock()
        info = Mock()
        warning = Mock()
        correction_field = Mock()
        monkeypatch.setattr(renderer, "render_reference_correction_field", correction_field)
        monkeypatch.setattr(
            renderer,
            "st",
            SimpleNamespace(
                session_state=_canonical_state(
                    lang=language,
                    guided_use_case="rx_benchmark",
                    guided_reference_design="reference_station",
                    val_comp_mode="reference_station",
                    val_snr_correction_mode=intent,
                ),
                markdown=markdown,
                radio=radio,
                info=info,
                warning=warning,
            ),
        )

        renderer._render_offset_calibration_fields(
            T[language],
            GUIDED_INPUTS[language],
        )

        options = GUIDED_INPUTS[language]["options"]["offset_intent"]
        messages = GUIDED_INPUTS[language]["messages"]
        if intent == "established_offset":
            correction_field.assert_called_once_with(
                T[language],
                on_change=renderer._guided_experiment_definition_change,
                on_change_args=("offset_calibration",),
            )
        else:
            correction_field.assert_not_called()
        expected_markdown = [messages["correction_formula"]]
        if intent == "establish_offset":
            warning.assert_called_once_with(messages["calibration_run_notice"])
            expected_markdown.append(messages["establish_reference_guidance"])
        else:
            warning.assert_not_called()
        assert [call.args[0] for call in markdown.call_args_list] == expected_markdown
        info.assert_not_called()
        positional_args, keyword_args = radio.call_args
        assert positional_args == (
            GUIDED_INPUTS[language]["steps"]["offset_calibration"]["title"],
            tuple(options),
        )
        assert keyword_args["captions"] == tuple(
            option["description"] for option in options.values()
        )
        assert keyword_args["width"] == "stretch"
        assert keyword_args["key"] == "val_snr_correction_mode"
        assert keyword_args["on_change"] is renderer._handle_offset_intent_change
        assert [
            keyword_args["format_func"](option_key)
            for option_key in options
        ] == [option["label"] for option in options.values()]


@pytest.mark.parametrize("language", ["en", "de"])
def test_reference_intro_avoids_repeated_metric_definitions_preserved_in_results(language):
    """Keep Reference selection concise and define metrics beside the results."""
    reference_body = GUIDED_INPUTS[language]["steps"]["reference_design"]["body_md"]
    options = GUIDED_INPUTS[language]["options"]["reference_design"]
    assert all(option["label"] not in reference_body for option in options.values())
    assert all(option["description"] not in reference_body for option in options.values())
    assert not any(line.startswith("- ") for line in reference_body.splitlines())
    assert '<strong class="defined-term">SNR</strong>' not in reference_body
    assert '<strong class="defined-term">ΔSNR</strong>' not in reference_body
    for section in ("context_rx_compare", "context_tx_compare"):
        guidance = RESULT_GUIDANCE[language]["sections"][section]["read"]
        assert '<strong class="defined-term">SNR</strong>' in guidance
        assert '<strong class="defined-term">Delta SNR (ΔSNR)</strong>' in guidance


@pytest.mark.parametrize("is_ready,is_busy", [(True, False), (False, False), (True, True)])
def test_guided_demo_metadata_is_localized_and_initially_expanded(
    monkeypatch, is_ready, is_busy,
):
    """Render demo context before steps using the selected profile language."""
    session_state = _canonical_state(
        lang="de",
        guided_loaded_demo_profile="example",
        guided_demo_metadata_open=True,
        loaded_config_profile={
            "title": {"en": "English title", "de": "Deutscher Titel"},
            "description": {
                "en": "English description",
                "de": "Deutsche Beschreibung mit [Quelle](https://example.test).",
            },
        },
    )
    if is_busy:
        begin_main_analysis_submission(session_state)
    expander = Mock(return_value=_NullContext())
    markdown = Mock()
    caption = Mock()
    container = Mock(return_value=_NullContext())
    info = Mock()
    button = Mock()
    monkeypatch.setattr(
        renderer,
        "st",
        SimpleNamespace(
            session_state=session_state,
            expander=expander,
            markdown=markdown,
            caption=caption,
            container=container,
            info=info,
            button=button,
            empty=Mock(return_value=SimpleNamespace(button=button)),
        ),
    )

    renderer._render_demo_metadata(
        GUIDED_INPUTS["de"],
        walkthrough_node="synthetic-start",
        is_ready=is_ready,
    )

    expander.assert_called_once_with(
        GUIDED_INPUTS["de"]["messages"]["demo_title"],
        expanded=True,
        icon=":material/route:",
    )
    container.assert_called_once_with(key="guided_demo_context")
    assert "Deutscher Titel" in markdown.call_args.args[0]
    captions = [call.args[0] for call in caption.call_args_list]
    assert any("Deutsche Beschreibung" in text for text in captions)
    assert any("https://example.test" in text for text in captions)
    messages = GUIDED_INPUTS["de"]["messages"]
    info.assert_called_once_with(messages["demo_preset"])
    assert messages["demo_walkthrough_help"] in captions
    assert messages["demo_skip_to_review_help"] in captions
    assert len(button.call_args_list) == 2
    walkthrough_call, review_call = button.call_args_list
    assert walkthrough_call.args == (messages["demo_walkthrough"],)
    assert walkthrough_call.kwargs == {
        "key": "guided_demo_walkthrough",
        "type": "primary",
        "on_click": renderer._open_demo_node,
        "args": ("synthetic-start",),
        "width": "stretch",
    }
    assert review_call.args == (messages["demo_skip_to_review"],)
    assert review_call.kwargs == {
        "key": "guided_demo_skip_to_review_busy" if is_busy else "guided_demo_skip_to_review",
        "type": "primary",
        "disabled": not is_ready or is_busy,
        "on_click": renderer._skip_to_review_and_run,
        "width": "stretch",
    }


@pytest.mark.parametrize("benchmark_mode", ["reference_station", "local_neighborhood"])
@pytest.mark.parametrize("correction", [0.0, 1.2])
def test_reference_panel_keeps_only_actionable_correction_warning(monkeypatch, benchmark_mode, correction):
    """The intro owns explanation; only a retained local correction needs a warning."""
    session_state = _canonical_state(
        guided_reference_design=benchmark_mode,
        val_comp_mode=benchmark_mode,
        val_benchmark_offset_db=correction,
    )
    info = Mock()
    warning = Mock()
    monkeypatch.setattr(
        renderer,
        "st",
        SimpleNamespace(
            session_state=session_state,
            markdown=Mock(),
            radio=Mock(),
            info=info,
            warning=warning,
            columns=Mock(return_value=(_NullContext(), _NullContext())),
        ),
    )
    monkeypatch.setattr(renderer, "render_reference_design_fields", Mock())
    monkeypatch.setattr(renderer, "render_reference_design_selector", Mock())
    monkeypatch.setattr(renderer, "render_reference_correction_field", Mock())

    renderer._render_reference_design_fields(T["en"], GUIDED_INPUTS["en"])

    info.assert_not_called()
    if benchmark_mode == "local_neighborhood" and correction != 0.0:
        warning.assert_called_once_with(
            GUIDED_INPUTS["en"]["messages"]["local_existing_correction_warning"].format(offset=correction)
        )
    else:
        warning.assert_not_called()


def test_guided_demo_walkthrough_only_opens_the_requested_flow_node(monkeypatch):
    """Navigate from demo context without changing preset or run identity."""
    flow = renderer.load_guided_input_flow()
    for destination in (flow["start_node"],):
        session_state = _canonical_state(
            active_demo_profile="example",
            guided_loaded_demo_profile="example",
            guided_demo_metadata_open=True,
            guided_active_node="target_and_window",
            guided_collapse_all=True,
            run_mode="guided_demo",
        )
        expected_state = deepcopy(session_state)
        expected_state.update(
            {
                "guided_demo_metadata_open": False,
                "guided_active_node": destination,
                "guided_collapse_all": False,
            }
        )
        monkeypatch.setattr(
            renderer,
            "st",
            SimpleNamespace(session_state=session_state),
        )
        navigation_request = Mock()
        monkeypatch.setattr(
            renderer,
            "request_page_navigation",
            navigation_request,
        )

        renderer._open_demo_node(destination)

        assert session_state == expected_state
        navigation_request.assert_called_once_with(
            session_state,
            page_navigation.PARAMETER_SETTINGS_ANCHOR_ID,
            should_scroll=True,
        )


@pytest.mark.parametrize("direction", ["rx", "tx"])
def test_guided_demo_shortcut_opens_review_and_submits_once(monkeypatch, direction):
    """Reuse normal Run validation without changing settings or demo identity."""
    session_state = _canonical_state(
        guided_use_case=f"{direction}_performance",
        val_analysis_direction=direction,
        active_demo_profile="example",
        guided_loaded_demo_profile="example",
        guided_demo_metadata_open=True,
        configuration_changed_since_run=True,
    )
    original_state = deepcopy(session_state)
    _install_shared_streamlit_state(monkeypatch, session_state)

    renderer._skip_to_review_and_run()
    token = get_analysis_submission(session_state).token
    renderer._skip_to_review_and_run()
    request = claim_analysis_submission_request(session_state)

    assert request.token == token
    assert request.source == "main_button"
    assert session_state.guided_active_node == "review_and_run"
    assert session_state.guided_demo_metadata_open is False
    assert session_state.guided_collapse_all is False
    assert session_state.configuration_changed_since_run is False
    for key, value in original_state.items():
        if key not in {
            "guided_active_node", "guided_demo_metadata_open", "configuration_changed_since_run",
        }:
            assert session_state[key] == value
    renderer._skip_to_review_and_run()
    assert claim_analysis_submission_request(session_state) is None
    assert get_analysis_submission(session_state).token == token


@pytest.mark.parametrize("invalid_values", [
    {"val_callsign": "!"},
    {"val_end_d": date(2026, 6, 30)},
    {"guided_use_case": "rx_benchmark", "val_comp_mode": "reference_station"},
    {"val_min_opportunities": 0},
])
def test_guided_demo_shortcut_rechecks_readiness_before_submission(
    monkeypatch, invalid_values,
):
    """Retained demo metadata cannot bypass invalid current configuration."""
    session_state = _canonical_state(
        guided_loaded_demo_profile="example",
        guided_demo_metadata_open=True,
        **invalid_values,
    )
    original_state = deepcopy(session_state)
    _install_shared_streamlit_state(monkeypatch, session_state)

    renderer._skip_to_review_and_run()

    assert session_state == original_state
    assert claim_analysis_submission_request(session_state) is None


@pytest.mark.parametrize("next_node", ["target_and_window", "reference_design", "offset_calibration", "scope_and_evidence", "review_and_run"])
def test_guided_continue_requests_the_next_panel_heading(monkeypatch, next_node):
    """Every Continue opens and targets the next panel, preserving science values."""
    session_state = _canonical_state(
        guided_active_node="use_case",
        guided_collapse_all=True,
    )
    monkeypatch.setattr(
        renderer,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    renderer._continue_to(next_node)
    navigation_request = page_navigation.consume_page_navigation_request(
        session_state
    )

    assert session_state.guided_active_node == next_node
    assert session_state.guided_collapse_all is False
    assert navigation_request is not None
    assert navigation_request["anchor_id"] == (
        page_navigation.PARAMETER_SETTINGS_ANCHOR_ID
    )
    assert navigation_request["should_scroll"] is True
    assert navigation_request["panel_key"] == f"guided_step_{next_node}"


def test_demo_metadata_precedes_steps_but_ready_review_remains_open(monkeypatch):
    """Keep metadata first while retaining the terminal review on demo load."""
    session_state = _canonical_state(
        guided_scope_mode="demo",
        guided_loaded_demo_profile="example",
        guided_demo_metadata_open=True,
        guided_active_node="review_and_run",
    )
    events = []

    def fake_expander(label, *, expanded, icon):
        events.append(("step", label, expanded, icon))
        return _NullContext()

    monkeypatch.setattr(
        renderer,
        "st",
        SimpleNamespace(
            session_state=session_state,
            expander=fake_expander,
            markdown=Mock(),
            button=Mock(),
            info=Mock(),
        ),
    )
    monkeypatch.setattr(
        renderer,
        "_render_demo_metadata",
        lambda guided_content, **navigation: events.append(
            ("metadata", navigation)
        ),
    )
    for renderer_name in tuple(renderer.CONTROL_RENDERERS):
        monkeypatch.setitem(
            renderer.CONTROL_RENDERERS,
            renderer_name,
            lambda t, guided_content: "review-slot",
        )

    render_result = renderer.render_guided_inputs(T["en"])

    assert events[0] == (
        "metadata",
        {
            "walkthrough_node": "use_case",
            "is_ready": True,
        },
    )
    step_events = [event for event in events if event[0] == "step"]
    assert step_events
    assert [event[2] for event in step_events] == [False, False, False, True]
    assert render_result.available_nodes == (
        "use_case",
        "target_and_window",
        "scope_and_evidence",
        "review_and_run",
    )
    assert render_result.is_ready is True
    assert render_result.review_actions_slot == "review-slot"


def test_completed_active_step_stays_open_until_continue_then_opens_next(
    monkeypatch,
):
    """Let Continue, rather than field validity, govern accordion progression."""
    session_state = _canonical_state(
        guided_active_node="use_case",
        guided_demo_metadata_open=False,
        guided_collapse_all=False,
    )
    events = []

    def fake_expander(label, *, expanded, icon):
        events.append(("step", label, expanded))
        return _NullContext()

    def fake_button(label, **kwargs):
        events.append(
            ("button", label, kwargs.get("key"), kwargs.get("type"))
        )

    monkeypatch.setattr(
        renderer,
        "st",
        SimpleNamespace(
            session_state=session_state,
            expander=fake_expander,
            markdown=Mock(),
            button=fake_button,
            info=Mock(),
        ),
    )
    monkeypatch.setattr(
        renderer,
        "_render_demo_metadata",
        lambda content, **navigation: None,
    )
    for renderer_name in tuple(renderer.CONTROL_RENDERERS):
        monkeypatch.setitem(
            renderer.CONTROL_RENDERERS,
            renderer_name,
            lambda t, guided_content: "review-slot",
        )

    renderer.render_guided_inputs(T["en"])

    step_events = [event for event in events if event[0] == "step"]
    button_events = [event for event in events if event[0] == "button"]
    assert step_events[0][2] is True
    assert step_events[1][2] is False
    assert button_events[0] == (
        "button",
        GUIDED_INPUTS["en"]["messages"]["continue"],
        "guided_continue_use_case",
        "primary",
    )

    renderer._continue_to("target_and_window")
    events.clear()
    renderer.render_guided_inputs(T["en"])

    step_events = [event for event in events if event[0] == "step"]
    button_events = [event for event in events if event[0] == "button"]
    assert step_events[0][2] is False
    assert step_events[1][2] is True
    assert button_events[0] == (
        "button",
        GUIDED_INPUTS["en"]["messages"]["continue"],
        "guided_continue_target_and_window",
        "primary",
    )


def test_stale_ready_configuration_also_opens_review_and_rerun_actions(
    monkeypatch,
):
    """Expose rerun actions without closing the complete panel being edited."""
    session_state = _canonical_state(
        guided_active_node="target_and_window",
        guided_demo_metadata_open=False,
        guided_collapse_all=False,
        configuration_changed_since_run=True,
    )
    step_events = []

    def fake_expander(label, *, expanded, icon):
        step_events.append((label, expanded))
        return _NullContext()

    monkeypatch.setattr(
        renderer,
        "st",
        SimpleNamespace(
            session_state=session_state,
            expander=fake_expander,
            markdown=Mock(),
            button=Mock(),
            info=Mock(),
        ),
    )
    monkeypatch.setattr(
        renderer,
        "_render_demo_metadata",
        lambda content, **navigation: None,
    )
    for renderer_name in tuple(renderer.CONTROL_RENDERERS):
        monkeypatch.setitem(
            renderer.CONTROL_RENDERERS,
            renderer_name,
            lambda t, guided_content: "review-slot",
        )

    render_result = renderer.render_guided_inputs(T["en"])

    assert [expanded for _, expanded in step_events] == [
        False,
        True,
        False,
        True,
    ]
    assert render_result.is_ready is True
    assert render_result.review_actions_slot == "review-slot"


def test_stale_incomplete_configuration_does_not_expose_unready_review(
    monkeypatch,
):
    """Keep guiding through required fields when a changed request is incomplete."""
    session_state = _canonical_state(
        val_callsign="",
        guided_active_node="target_and_window",
        configuration_changed_since_run=True,
    )
    step_events = []

    def fake_expander(label, *, expanded, icon):
        step_events.append((label, expanded))
        return _NullContext()

    monkeypatch.setattr(
        renderer,
        "st",
        SimpleNamespace(
            session_state=session_state,
            expander=fake_expander,
            markdown=Mock(),
            button=Mock(),
            warning=Mock(),
        ),
    )
    monkeypatch.setattr(
        renderer,
        "_render_demo_metadata",
        lambda content, **navigation: None,
    )
    for renderer_name in tuple(renderer.CONTROL_RENDERERS):
        monkeypatch.setitem(
            renderer.CONTROL_RENDERERS,
            renderer_name,
            lambda t, guided_content: "review-slot",
        )

    render_result = renderer.render_guided_inputs(T["en"])

    assert [expanded for _, expanded in step_events] == [False, True]
    assert render_result.is_ready is False
    assert render_result.review_actions_slot is None


def test_editing_a_demo_step_closes_metadata_and_keeps_that_step_active(
    monkeypatch,
):
    """Keep an explicitly edited preset panel open after its widget rerun."""
    session_state = _canonical_state(
        guided_demo_metadata_open=True,
        guided_collapse_all=True,
        guided_active_node="review_and_run",
    )
    monkeypatch.setattr(
        renderer,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    renderer._activate_step("target_and_window")

    assert session_state.guided_demo_metadata_open is False
    assert session_state.guided_collapse_all is False
    assert session_state.guided_active_node == "target_and_window"


def test_localized_use_case_descriptions_are_part_of_the_radio_choices(
    monkeypatch,
):
    """Render localized choice descriptions followed by their shared limits."""
    radio = Mock()
    markdown = Mock()
    rendered = Mock()
    rendered.attach_mock(radio, "radio")
    rendered.attach_mock(markdown, "markdown")
    monkeypatch.setattr(
        renderer,
        "st",
        SimpleNamespace(
            session_state=_canonical_state(guided_use_case=None),
            radio=radio,
            markdown=markdown,
        ),
    )

    for language in ("en", "de"):
        rendered.reset_mock()
        options = GUIDED_INPUTS[language]["options"]["use_cases"]
        renderer._render_use_case_selector(
            T[language],
            GUIDED_INPUTS[language],
        )

        assert radio.call_args.args[1] == tuple(options)
        assert radio.call_args.kwargs["captions"] == tuple(
            option["description"] for option in options.values()
        )
        format_choice = radio.call_args.kwargs["format_func"]
        assert tuple(format_choice(option) for option in options) == tuple(
            option["label"] for option in options.values()
        )
        assert radio.call_args.kwargs["on_change"] is (
            renderer._handle_use_case_change
        )
        assert radio.call_args.kwargs["width"] == "stretch"
        markdown.assert_called_once_with(
            GUIDED_INPUTS[language]["messages"]["use_case_limits"]
        )
        assert [call[0] for call in rendered.mock_calls] == ["radio", "markdown"]


def test_scope_panel_always_shows_active_controls_without_preset_choice(monkeypatch):
    """Expose actual scope values directly for defaults, demos, and edits."""
    station_population_fields = Mock()
    scope_fields = Mock()
    evidence_threshold_fields = Mock()
    caption = Mock()
    monkeypatch.setattr(
        renderer,
        "st",
        SimpleNamespace(
            session_state=_canonical_state(guided_scope_mode="general"),
            markdown=Mock(),
            caption=caption,
        ),
    )
    monkeypatch.setattr(
        renderer,
        "render_station_population_fields",
        station_population_fields,
    )
    monkeypatch.setattr(renderer, "render_scope_fields", scope_fields)
    monkeypatch.setattr(
        renderer,
        "render_evidence_threshold_fields",
        evidence_threshold_fields,
    )

    renderer._render_scope_and_evidence_fields(T["en"], GUIDED_INPUTS["en"])

    station_population_fields.assert_called_once()
    scope_fields.assert_called_once()
    evidence_threshold_fields.assert_called_once()
    assert len(caption.call_args_list) == 3


@pytest.mark.parametrize("language", ["en", "de"])
@pytest.mark.parametrize("direction", ["rx", "tx"])
def test_custom_scope_panel_shows_only_relevant_evidence_guidance(
    monkeypatch,
    language,
    direction,
):
    """Explain Performance or Benchmark thresholds for the active result."""
    messages = GUIDED_INPUTS[language]["messages"]
    cases = (
        (
            "none",
            "success_evidence_requirements_body",
            "compare_evidence_requirements_body",
            "performance",
        ),
        (
            "reference_station",
            "compare_evidence_requirements_body",
            "success_evidence_requirements_body",
            "benchmark",
        ),
        (
            "local_neighborhood",
            "compare_evidence_requirements_body",
            "success_evidence_requirements_body",
            "benchmark",
        ),
    )

    for comparison_mode, expected_key, excluded_key, expected_result_type in cases:
        caption = Mock()
        render_evidence_fields = Mock()
        render_outlier_reporting = Mock()
        monkeypatch.setattr(
            renderer,
            "st",
            SimpleNamespace(
                session_state=_canonical_state(
                    guided_scope_mode="custom",
                    val_comp_mode=comparison_mode,
                    val_analysis_direction=direction,
                ),
                radio=Mock(),
                markdown=Mock(),
                caption=caption,
            ),
        )
        monkeypatch.setattr(renderer, "render_station_population_fields", Mock())
        render_scope = Mock()
        monkeypatch.setattr(renderer, "render_scope_fields", render_scope)
        monkeypatch.setattr(
            renderer,
            "render_evidence_threshold_fields",
            render_evidence_fields,
        )
        monkeypatch.setattr(
            renderer,
            "render_delta_snr_outlier_reporting_field",
            render_outlier_reporting,
        )

        renderer._render_scope_and_evidence_fields(
            T[language], GUIDED_INPUTS[language]
        )

        captions = [call.args[0] for call in caption.call_args_list]
        assert messages["station_population_body"] in captions
        assert messages["analysis_scope_body"] in captions
        assert messages[expected_key] in captions
        assert messages[excluded_key] not in captions
        assert render_evidence_fields.call_args.kwargs["result_type"] == (
            expected_result_type
        )
        assert render_scope.call_args.kwargs["use_two_column_layout"] is True
        assert (
            render_evidence_fields.call_args.kwargs["use_two_column_layout"]
            is True
        )
        assert render_outlier_reporting.call_count == (
            0 if comparison_mode == "none" else 1
        )
        if comparison_mode != "none":
            assert render_outlier_reporting.call_args.kwargs == {
                "on_change": renderer._guided_scientific_change,
                "on_change_args": ("scope_and_evidence",),
            }


def test_guided_outlier_setting_invalidates_results_and_requires_manual_run(
    monkeypatch,
):
    """Retire stale evidence while keeping the edited Guided node open."""
    session_state = _canonical_state(
        guided_use_case="rx_benchmark",
        val_comp_mode="reference_station",
        guided_scope_mode="custom",
        run_mode="RX",
        active_demo_profile="hardware-demo",
        completed_run_snapshot={
            "schema_version": 1,
            "analysis_id": "retained",
        },
    )
    captured_callback = {}

    def capture_outlier_field(_labels, **kwargs):
        captured_callback.update(kwargs)

    _install_shared_streamlit_state(monkeypatch, session_state)
    renderer.st.radio = Mock()
    renderer.st.markdown = Mock()
    renderer.st.caption = Mock()
    monkeypatch.setattr(renderer, "render_station_population_fields", Mock())
    monkeypatch.setattr(renderer, "render_scope_fields", Mock())
    monkeypatch.setattr(renderer, "render_evidence_threshold_fields", Mock())
    monkeypatch.setattr(
        renderer,
        "render_delta_snr_outlier_reporting_field",
        capture_outlier_field,
    )

    renderer._render_scope_and_evidence_fields(T["en"], GUIDED_INPUTS["en"])
    captured_callback["on_change"](*captured_callback["on_change_args"])

    assert session_state.guided_active_node == "scope_and_evidence"
    assert session_state.run_mode is None
    assert session_state.active_demo_profile is None
    assert session_state.configuration_changed_since_run is True
    assert "completed_run_snapshot" not in session_state


def test_guided_demo_scope_label_requires_values_to_still_match_profile(
    monkeypatch,
):
    """Do not call edited Classic scope values a demo preset on reconstruction."""
    profile_key = next(iter(renderer.DEMO_PROFILES))
    expected_values = renderer._loaded_demo_scope_values(profile_key)
    assert expected_values
    session_state = _canonical_state(
        guided_loaded_demo_profile=profile_key,
        **expected_values,
    )
    monkeypatch.setattr(
        renderer,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    assert renderer._loaded_demo_scope_matches_current_state() is True
    session_state.val_max_peer_distance_km = (
        5000
        if session_state.val_max_peer_distance_km != 5000
        else 10000
    )
    assert renderer._loaded_demo_scope_matches_current_state() is False


def test_guided_demo_launcher_is_load_only_while_classic_keeps_direct_run():
    """Protect the view-dependent demo action contract without importing app.py."""
    application_tree = ast.parse(
        (REPOSITORY_ROOT / "app.py").read_text(encoding="utf-8")
    )
    launcher = next(
        node
        for node in application_tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "render_demo_launcher"
    )
    view_branch = next(
        node
        for node in ast.walk(launcher)
        if isinstance(node, ast.If)
        and "input_view" in ast.unparse(node.test)
        and "guided" in ast.unparse(node.test)
    )

    guided_calls = {
        node.func.id
        for statement in view_branch.body
        for node in ast.walk(statement)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    classic_calls = {
        node.func.id
        for statement in view_branch.orelse
        for node in ast.walk(statement)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "load_demo_profile_config" in guided_calls
    assert "run_demo_profile" not in guided_calls
    assert {"load_demo_profile_config", "run_demo_profile"} <= classic_calls

    for branch_statements in (view_branch.body, view_branch.orelse):
        load_button_calls = [
            node
            for statement in branch_statements
            for node in ast.walk(statement)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "st"
            and node.func.attr == "button"
            and "btn_load_demo_selected" in ast.unparse(node)
        ]
        assert len(load_button_calls) == 1
        action_keywords = {
            keyword.arg: ast.literal_eval(keyword.value)
            for keyword in load_button_calls[0].keywords
            if keyword.arg in {"key", "type"}
        }
        assert action_keywords == {
            "key": "load_selected_demo_configuration",
            "type": "primary",
        }


@pytest.mark.parametrize("input_view", ["guided", "classic"])
@pytest.mark.parametrize("direction", ["rx", "tx"])
def test_empty_benchmark_selection_defaults_to_fixed_reference(monkeypatch, input_view, direction):
    """A first Benchmark question selects the fixed Reference in both editors."""
    session_state = _canonical_state(
        input_view=input_view,
        guided_use_case=None,
        classic_question=None,
        val_analysis_direction=None,
        val_callsign="",
        val_qth="",
    )
    _install_shared_streamlit_state(monkeypatch, session_state)
    question = f"{direction}_benchmark"
    if input_view == "guided":
        session_state.guided_use_case = question
        renderer._handle_use_case_change()
    else:
        session_state[CLASSIC_QUESTION_KEY] = question
        callbacks.handle_classic_question_change()
    assert session_state.val_analysis_direction == direction
    assert session_state.val_comp_mode == "reference_station"
    assert session_state.guided_reference_design == "reference_station"
    assert session_state.guided_last_benchmark_mode == "reference_station"
    assert session_state.val_ref_callsign == ""
    assert session_state.val_ref_qth == ""


@pytest.mark.parametrize("input_view", ["guided", "classic"])
@pytest.mark.parametrize("direction", ["rx", "tx"])
@pytest.mark.parametrize("current_mode", ["none", "local_neighborhood"])
def test_benchmark_selection_preserves_existing_neighborhood(monkeypatch, input_view, direction, current_mode):
    """The fixed Reference default cannot replace a current or retained neighborhood."""
    session_state = _canonical_state(
        input_view=input_view,
        val_comp_mode=current_mode,
        guided_reference_design="local_neighborhood" if current_mode != "none" else None,
        guided_last_benchmark_mode="local_neighborhood",
        val_ref_radius_km=150,
    )
    _install_shared_streamlit_state(monkeypatch, session_state)
    question = f"{direction}_benchmark"
    if input_view == "guided":
        session_state.guided_use_case = question
        renderer._handle_use_case_change()
    else:
        session_state[CLASSIC_QUESTION_KEY] = question
        callbacks.handle_classic_question_change()
    assert session_state.val_comp_mode == "local_neighborhood"
    assert session_state.guided_reference_design == "local_neighborhood"
    assert session_state.guided_last_benchmark_mode == "local_neighborhood"
    assert session_state.val_ref_radius_km == 150
    session_state.input_view = "classic" if input_view == "guided" else "guided"
    callbacks.handle_input_view_change()
    assert session_state.val_comp_mode == "local_neighborhood"
    assert session_state.guided_reference_design == "local_neighborhood"


def test_guided_use_case_maps_to_canonical_state_and_invalidates_active_results(
    monkeypatch,
):
    """Map Guided intent without a second scientific state or stale results."""
    session_state = _canonical_state(
        run_mode="RX",
        guided_use_case="tx_benchmark",
        guided_reference_design="reference_station",
        val_comp_mode="reference_station",
        val_ref_callsign="DL2XYZ",
        val_ref_qth="JO63",
        result_export_blocks={"old": "result"},
    )
    _install_shared_streamlit_state(monkeypatch, session_state)

    renderer._handle_use_case_change()

    assert session_state.val_analysis_direction == "tx"
    assert session_state.val_comp_mode == "reference_station"
    assert session_state.guided_reference_design == "reference_station"
    assert session_state.guided_active_node == "use_case"
    assert session_state.run_mode is None
    assert session_state.result_export_blocks == {}
    assert session_state.configuration_changed_since_run is True

    session_state.guided_use_case = "rx_performance"
    renderer._handle_use_case_change()

    assert session_state.val_analysis_direction == "rx"
    assert session_state.val_comp_mode == "none"
    assert session_state.guided_reference_design is None
    assert session_state.guided_last_benchmark_mode == "reference_station"
    assert session_state.val_ref_callsign == "DL2XYZ"
    assert session_state.val_ref_qth == ""


def test_guided_result_family_defaults_preserve_only_explicit_filter_edits(
    monkeypatch,
):
    """Apply Benchmark-off and Performance-on while retaining a manual choice."""
    session_state = _canonical_state(
        guided_use_case="rx_performance",
        guided_reference_design=None,
        guided_last_benchmark_mode=None,
        val_comp_mode="none",
    )
    session_state.pop("val_exclude_special_callsigns")
    session_state.pop("val_filter_moving")
    initialize_population_exclusion_state(session_state)
    _install_shared_streamlit_state(monkeypatch, session_state)

    assert session_state.val_exclude_special_callsigns is True
    assert session_state.val_filter_moving is True

    session_state.guided_use_case = "rx_benchmark"
    renderer._handle_use_case_change()
    assert session_state.val_exclude_special_callsigns is False
    assert session_state.val_filter_moving is False

    session_state._val_exclude_special_callsigns = True
    callbacks.handle_population_exclusion_change(
        "val_exclude_special_callsigns"
    )
    session_state.guided_use_case = "rx_performance"
    renderer._handle_use_case_change()
    assert session_state.val_exclude_special_callsigns is True
    assert session_state.val_filter_moving is True

    session_state.guided_use_case = "rx_benchmark"
    renderer._handle_use_case_change()
    assert session_state.val_exclude_special_callsigns is True
    assert session_state.val_filter_moving is False


def test_classic_question_applies_defaults_and_preserves_manual_filter_edits(
    monkeypatch,
):
    """Give Classic the Guided result-family defaults without enforcing them."""
    session_state = _canonical_state(
        input_view="classic",
        classic_question="rx_performance",
        guided_use_case="rx_performance",
        guided_reference_design=None,
        guided_last_benchmark_mode=None,
        val_comp_mode="none",
    )
    session_state.pop("val_exclude_special_callsigns")
    session_state.pop("val_filter_moving")
    initialize_population_exclusion_state(session_state)
    _install_shared_streamlit_state(monkeypatch, session_state)

    assert session_state.val_exclude_special_callsigns is True
    assert session_state.val_filter_moving is True

    session_state[CLASSIC_QUESTION_KEY] = "rx_benchmark"
    callbacks.handle_classic_question_change()

    assert session_state.val_comp_mode == "reference_station"
    assert session_state.guided_reference_design == "reference_station"
    assert session_state.val_exclude_special_callsigns is False
    assert session_state.val_filter_moving is False
    assert is_classic_input_ready(session_state) is True

    session_state._val_exclude_special_callsigns = True
    callbacks.handle_population_exclusion_change(
        "val_exclude_special_callsigns"
    )
    session_state[CLASSIC_QUESTION_KEY] = "rx_performance"
    callbacks.handle_classic_question_change()
    assert session_state.val_exclude_special_callsigns is True
    assert session_state.val_filter_moving is True

    session_state[CLASSIC_QUESTION_KEY] = "rx_benchmark"
    callbacks.handle_classic_question_change()
    assert session_state.val_exclude_special_callsigns is True
    assert session_state.val_filter_moving is False


def test_population_exclusion_widgets_restore_canonical_values_after_cleanup():
    """Keep explicit filters when Streamlit removes conditionally hidden widgets."""
    script = r'''
import streamlit as st

from ui.population_exclusion_state import (
    initialize_population_exclusion_state,
    load_population_exclusion_widget_values,
    population_exclusion_widget_key,
    store_population_exclusion_widget_value,
)


def store_special_callsign_filter():
    store_population_exclusion_widget_value(
        st.session_state,
        "val_exclude_special_callsigns",
    )


def store_moving_station_filter():
    store_population_exclusion_widget_value(
        st.session_state,
        "val_filter_moving",
    )


initialize_population_exclusion_state(st.session_state)
show_filters = st.toggle("Show filters", key="show_population_filters")
if show_filters:
    load_population_exclusion_widget_values(st.session_state)
    st.toggle(
        "Exclude special callsigns",
        key=population_exclusion_widget_key("val_exclude_special_callsigns"),
        on_change=store_special_callsign_filter,
    )
    st.toggle(
        "Exclude moving stations",
        key=population_exclusion_widget_key("val_filter_moving"),
        on_change=store_moving_station_filter,
    )
'''
    application = AppTest.from_string(script, default_timeout=10)
    application.session_state["val_comp_mode"] = "none"
    application.session_state["show_population_filters"] = True

    application.run()
    assert application.exception.values == []
    assert application.toggle("_val_exclude_special_callsigns").value is True
    assert application.toggle("_val_filter_moving").value is True

    application.toggle("_val_exclude_special_callsigns").set_value(False).run()
    assert application.session_state["val_exclude_special_callsigns"] is False
    assert application.session_state["val_filter_moving"] is True

    application.toggle("show_population_filters").set_value(False).run()
    assert "_val_exclude_special_callsigns" not in application.session_state
    assert "_val_filter_moving" not in application.session_state
    assert application.session_state["val_exclude_special_callsigns"] is False
    assert application.session_state["val_filter_moving"] is True

    application.toggle("show_population_filters").set_value(True).run()
    assert application.exception.values == []
    assert application.toggle("_val_exclude_special_callsigns").value is False
    assert application.toggle("_val_filter_moving").value is True


def test_default_guided_reference_design_survives_opening_classic(
    monkeypatch,
):
    """Keep the default fixed Reference and its defaults across editor views."""
    for switch_path in ("selector", "guided_action"):
        session_state = _canonical_state(
            input_view="guided",
            guided_use_case="rx_performance",
            guided_reference_design=None,
            guided_last_benchmark_mode=None,
            val_comp_mode="none",
        )
        session_state.pop("val_exclude_special_callsigns")
        session_state.pop("val_filter_moving")
        initialize_population_exclusion_state(session_state)
        _install_shared_streamlit_state(monkeypatch, session_state)

        session_state.guided_use_case = "rx_benchmark"
        renderer._handle_use_case_change()
        assert session_state.val_comp_mode == "reference_station"
        assert session_state.val_exclude_special_callsigns is False
        assert session_state.val_filter_moving is False

        if switch_path == "selector":
            session_state.input_view = "classic"
            callbacks.handle_input_view_change()
        else:
            renderer._open_classic_view()

        assert session_state.input_view == "classic"
        assert session_state[CLASSIC_QUESTION_KEY] == "rx_benchmark"
        assert session_state.val_comp_mode == "reference_station"
        assert session_state.val_exclude_special_callsigns is False
        assert session_state.val_filter_moving is False
        assert is_classic_input_ready(session_state) is True


def test_guided_direction_change_retains_design_but_clears_resolved_location(monkeypatch):
    session_state = _canonical_state(guided_use_case="tx_benchmark", guided_reference_design="reference_station", guided_last_benchmark_mode="reference_station", val_analysis_direction="rx", val_comp_mode="reference_station", val_ref_callsign="CALL/P", val_ref_qth="JO62", val_benchmark_offset_db=1.4, val_snr_correction_mode="established_offset", _reference_location_resolution={"status":"resolved"})
    _install_shared_streamlit_state(monkeypatch, session_state)
    renderer._handle_use_case_change()
    assert session_state.val_analysis_direction == "tx"
    assert session_state.val_comp_mode == "reference_station"
    assert session_state.val_ref_callsign == "CALL/P"
    assert session_state.val_ref_qth == ""
    assert "_reference_location_resolution" not in session_state
    assert session_state.val_benchmark_offset_db == 0.0
    assert session_state.val_snr_correction_mode == "no_offset"





def test_direction_change_resets_reference_station_pair_correction(monkeypatch):
    """Treat RX and TX Reference baselines as different operating designs."""
    session_state = _canonical_state(
        guided_use_case="tx_benchmark",
        guided_reference_design="reference_station",
        guided_last_benchmark_mode="reference_station",
        val_snr_correction_mode="established_offset",
        val_analysis_direction="rx",
        val_comp_mode="reference_station",
        val_ref_callsign="DL2XYZ",
        val_ref_qth="JO63",
        val_benchmark_offset_db=1.2,
    )
    _install_shared_streamlit_state(monkeypatch, session_state)

    renderer._handle_use_case_change()

    assert session_state.val_analysis_direction == "tx"
    assert session_state.val_comp_mode == "reference_station"
    assert session_state.val_ref_callsign == "DL2XYZ"
    assert session_state.val_ref_qth == ""
    assert session_state.val_benchmark_offset_db == 0.0
    assert session_state.val_snr_correction_mode == "no_offset"


def test_reference_branch_change_clears_only_pair_specific_canonical_values(
    monkeypatch,
):
    """Retain the Reference callsign but invalidate location and correction."""
    session_state = _canonical_state(
        guided_use_case="rx_benchmark",
        guided_reference_design="local_neighborhood",
        val_snr_correction_mode="established_offset",
        val_comp_mode="reference_station",
        val_ref_callsign="DL2XYZ",
        val_ref_qth="JO63",
        val_benchmark_offset_db=1.2,
        val_max_peer_distance_km=5000,
        val_min_spots=3,
        val_min_stations=2,
    )
    _install_shared_streamlit_state(monkeypatch, session_state)

    renderer._handle_reference_design_change()

    assert session_state.val_comp_mode == "local_neighborhood"
    assert session_state.guided_last_benchmark_mode == "local_neighborhood"
    assert session_state.val_ref_callsign == "DL2XYZ"
    assert session_state.val_ref_qth == ""
    assert session_state.val_benchmark_offset_db == 0.0
    assert session_state.val_snr_correction_mode == "no_offset"
    assert session_state.val_callsign == "DL1ABC"
    assert session_state.val_band == "40m"
    assert session_state.val_max_peer_distance_km == 5000
    assert session_state.val_min_spots == 3
    assert session_state.val_min_stations == 2


@pytest.mark.parametrize("language", ["en", "de"])
def test_loaded_demo_reference_design_round_trip_retains_station_and_later_steps(language):
    """A temporary neighbourhood choice must not erase the demo's station input."""
    script = '''
import streamlit as st
from config import DEMO_PROFILES
from i18n import T
from ui.callbacks import load_demo_profile_config, set_reset_config
from ui.guided_inputs.renderer import render_guided_inputs
from ui.state_manager import init_session_state

init_session_state()
st.button("Load first demo", key="test_load_demo", on_click=load_demo_profile_config,
          args=(next(iter(DEMO_PROFILES)),))
st.button("Reset test settings", key="test_reset", on_click=set_reset_config)
result = render_guided_inputs(T[st.session_state.lang])
st.session_state["test_available_nodes"] = result.available_nodes
'''
    application = AppTest.from_string(script, default_timeout=20)
    application.session_state["lang"] = language
    application.run()
    application.button("test_load_demo").click().run()
    assert not application.exception
    reference = application.session_state["val_ref_callsign"]
    assert reference
    application.button("guided_demo_walkthrough").click().run()
    application.button("guided_continue_use_case").click().run()
    application.button("guided_continue_target_and_window").click().run()
    expected_nodes = tuple(application.session_state["test_available_nodes"])
    assert expected_nodes[-3:] == (
        "offset_calibration", "scope_and_evidence", "review_and_run",
    )

    for expected_reference in (reference, "CALL/P"):
        application.button("guided_reference_design_local_neighborhood").click().run()
        assert not application.exception
        assert "scope_and_evidence" in application.session_state["test_available_nodes"]
        assert "review_and_run" in application.session_state["test_available_nodes"]
        assert "offset_calibration" not in application.session_state["test_available_nodes"]
        # A rerun while the callsign widget is hidden must retain its canonical value.
        application.run()
        application.button("guided_reference_design_reference_station").click().run()
        assert not application.exception
        assert application.text_input("val_ref_callsign").value == expected_reference
        assert tuple(application.session_state["test_available_nodes"]) == expected_nodes
        assert application.session_state["val_ref_qth"] == ""
        assert application.session_state["val_benchmark_offset_db"] == 0.0
        assert application.session_state["val_snr_correction_mode"] == "no_offset"
        assert application.session_state["run_mode"] is None
        application.text_input("val_ref_callsign").set_value("CALL/P").run()

    application.button("test_reset").click().run()
    assert application.session_state["val_ref_callsign"] == ""
    application.button("test_load_demo").click().run()
    assert application.session_state["val_ref_callsign"] == reference


def test_offset_intents_share_the_one_canonical_correction_field(monkeypatch):
    """Preserve an entered offset, but pin no-offset/calibration runs to zero."""
    session_state = _canonical_state(
        guided_use_case="rx_benchmark",
        guided_reference_design="reference_station",
        val_snr_correction_mode="established_offset",
        val_comp_mode="reference_station",
        val_ref_callsign="DL1ABC-1",
        val_benchmark_offset_db=-1.3,
    )
    _install_shared_streamlit_state(monkeypatch, session_state)

    renderer._handle_offset_intent_change()
    assert session_state.val_benchmark_offset_db == -1.3

    session_state.val_snr_correction_mode = "establish_offset"
    renderer._handle_offset_intent_change()
    assert session_state.val_benchmark_offset_db == 0.0
    assert session_state.guided_active_node == "offset_calibration"


def test_guided_identity_edit_clears_established_pair_correction(monkeypatch):
    """Require a new offset after changing the pair, QTH, or operating band."""
    session_state = _canonical_state(
        guided_use_case="rx_benchmark",
        guided_reference_design="reference_station",
        guided_last_benchmark_mode="reference_station",
        val_snr_correction_mode="established_offset",
        val_comp_mode="reference_station",
        val_ref_callsign="DL2XYZ",
        val_ref_qth="JO63",
        _reference_location_resolution={"status": "resolved"},
        val_benchmark_offset_db=1.2,
    )
    _install_shared_streamlit_state(monkeypatch, session_state)

    renderer._guided_correction_context_change("target_and_window")

    assert session_state.val_ref_qth == ""
    assert "_reference_location_resolution" not in session_state
    assert session_state.val_benchmark_offset_db == 0.0
    assert session_state.val_snr_correction_mode == "no_offset"
    assert session_state.guided_active_node == "target_and_window"


def test_german_review_uses_resolved_reference_location(monkeypatch):
    session_state = _canonical_state(lang="de", guided_use_case="tx_benchmark", guided_reference_design="reference_station", guided_last_benchmark_mode="reference_station", val_analysis_direction="tx", val_comp_mode="reference_station", val_ref_callsign="CALL/P", val_ref_qth="JO62")
    monkeypatch.setattr(renderer, "st", SimpleNamespace(session_state=session_state))
    review = renderer._reference_review_value(GUIDED_INPUTS["de"])
    assert "CALL/P" in review
    assert "JO62" in review
    assert "Referenzaufbau/-station" in review



def test_switching_to_classic_preserves_configuration_context_and_results(
    monkeypatch,
):
    """Treat editor selection as presentation state only."""
    session_state = _canonical_state(
        run_mode="RX",
        result_export_blocks={"performance": ["retained"]},
    )
    monkeypatch.setattr(
        renderer,
        "st",
        SimpleNamespace(session_state=session_state),
    )
    initialize_population_exclusion_state(session_state)
    before_state = deepcopy(session_state)
    guided_context = build_analysis_context_from_session_state(session_state)

    renderer._open_classic_view()

    assert session_state.input_view == "classic"
    assert session_state.run_mode == "RX"
    assert session_state.result_export_blocks == {"performance": ["retained"]}
    assert {
        key: value
        for key, value in session_state.items()
        if key not in {"input_view", CLASSIC_QUESTION_KEY}
    } == {
        key: value for key, value in before_state.items() if key != "input_view"
    }
    assert session_state[CLASSIC_QUESTION_KEY] == "rx_performance"
    assert build_analysis_context_from_session_state(session_state) == guided_context


def test_returning_from_classic_reconstructs_guided_state_without_resetting_results(
    monkeypatch,
):
    """Reconcile stale Guided choices after Classic changes direction and design."""
    session_state = _canonical_state(
        input_view="guided",
        run_mode="TX",
        guided_use_case="rx_benchmark",
        guided_reference_design="reference_station",
        guided_last_benchmark_mode="reference_station",
        val_snr_correction_mode="established_offset",
        guided_scope_mode="custom",
        guided_reconstruct_requested=False,
        guided_collapse_all=True,
        val_analysis_direction="tx",
        val_comp_mode="local_neighborhood",
        val_local_benchmark="local_median",
        val_ref_radius_km=250,
        val_benchmark_offset_db=0.0,
        result_export_blocks={"benchmark": ["retained"]},
    )
    monkeypatch.setattr(
        callbacks,
        "st",
        SimpleNamespace(session_state=session_state),
    )
    canonical_context = build_analysis_context_from_session_state(session_state)

    callbacks.handle_input_view_change()

    assert session_state.guided_reconstruct_requested is True
    assert session_state.guided_collapse_all is False
    assert session_state.run_mode == "TX"
    assert session_state.result_export_blocks == {"benchmark": ["retained"]}

    reconstruct_guided_transients(session_state, has_loaded_demo=False)

    assert session_state.guided_use_case == "tx_benchmark"
    assert session_state.guided_reference_design == "local_neighborhood"
    assert session_state.guided_last_benchmark_mode == "local_neighborhood"
    assert session_state.val_snr_correction_mode == "established_offset"
    assert session_state.guided_scope_mode == "general"
    assert session_state.run_mode == "TX"
    assert session_state.result_export_blocks == {"benchmark": ["retained"]}
    assert build_analysis_context_from_session_state(session_state) == canonical_context


def test_selector_change_hands_an_active_analysis_to_the_new_script(monkeypatch):
    """Keep a presentation-only rerun following the already admitted analysis."""
    session_state = _canonical_state(
        input_view="guided",
        run_mode="RX",
        guided_reconstruct_requested=False,
        guided_collapse_all=True,
        result_export_blocks={"performance": ["retained"]},
    )
    older_token = begin_main_analysis_submission(session_state)
    assert claim_analysis_submission_request(session_state) is not None
    monkeypatch.setattr(
        callbacks,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    callbacks.handle_input_view_change()

    request = claim_analysis_submission_request(session_state)
    assert request is not None
    assert request.token != older_token
    assert request.source == "input_view_change"
    assert session_state.guided_reconstruct_requested is True
    assert session_state.guided_collapse_all is False
    assert session_state.run_mode == "RX"
    assert session_state.result_export_blocks == {"performance": ["retained"]}


def test_guided_classic_action_hands_an_active_analysis_to_the_new_script(
    monkeypatch,
):
    """Cover the programmatic Guided-to-Classic transition during an active run."""
    session_state = _canonical_state(
        run_mode="TX",
        result_export_blocks={"benchmark": ["retained"]},
    )
    older_token = begin_main_analysis_submission(session_state)
    assert claim_analysis_submission_request(session_state) is not None
    monkeypatch.setattr(
        renderer,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    renderer._open_classic_view()

    request = claim_analysis_submission_request(session_state)
    assert request is not None
    assert request.token != older_token
    assert request.source == "input_view_change"
    assert get_analysis_submission(session_state).token == request.token
    assert session_state.input_view == "classic"
    assert session_state.run_mode == "TX"
    assert session_state.result_export_blocks == {"benchmark": ["retained"]}


def test_view_round_trip_preserves_retained_inactive_benchmark_design(monkeypatch):
    """Keep view switching from erasing a prior Guided Benchmark design."""
    session_state = _canonical_state(
        input_view="guided",
        guided_use_case="rx_performance",
        guided_reference_design=None,
        guided_last_benchmark_mode="reference_station",
        val_snr_correction_mode="established_offset",
        val_comp_mode="none",
        val_ref_callsign="DL2XYZ",
        val_ref_qth="JO63",
        val_benchmark_offset_db=1.2,
    )
    monkeypatch.setattr(
        callbacks,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    callbacks.handle_input_view_change()
    reconstruct_guided_transients(session_state, has_loaded_demo=False)

    assert session_state.guided_use_case == "rx_performance"
    assert session_state.guided_reference_design is None
    assert session_state.guided_last_benchmark_mode == "reference_station"
    assert session_state.val_ref_callsign == "DL2XYZ"
    assert session_state.val_ref_qth == "JO63"
    assert session_state.val_benchmark_offset_db == 1.2


def test_loading_performance_config_clears_previous_transient_benchmark_design(
    monkeypatch,
):
    """Do not let config history choose a later Benchmark branch."""
    session_state = _canonical_state(
        classic_question="rx_benchmark",
        guided_last_benchmark_mode="reference_station",
        guided_reference_design="reference_station",
        val_comp_mode="reference_station",
    )
    monkeypatch.setattr(
        config_io,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    performance_config = config_io._default_config()
    performance_config["analysis_direction"] = "rx"
    config_io.apply_config_values(performance_config)

    assert session_state.val_comp_mode == "none"
    assert session_state[CLASSIC_QUESTION_KEY] == "rx_performance"
    assert is_classic_input_ready(session_state) is True
    assert session_state.guided_last_benchmark_mode is None
    assert session_state.guided_reconstruct_requested is True
    assert session_state.val_exclude_special_callsigns is False
    assert session_state.val_filter_moving is False

    monkeypatch.setattr(
        callbacks,
        "st",
        SimpleNamespace(session_state=session_state),
    )
    monkeypatch.setattr(callbacks, "reset_audit", lambda: None)
    session_state.val_comp_mode = "reference_station"
    callbacks.handle_comp_mode_change()
    session_state.val_comp_mode = "none"
    callbacks.handle_comp_mode_change()

    assert session_state.val_exclude_special_callsigns is False
    assert session_state.val_filter_moving is False


def _run_application_with_state(initial_state):
    """Execute one isolated application session with explicit initial state."""
    serializable_initial_state = dict(initial_state)
    for time_state_key in (
        "val_start_d",
        "val_start_t",
        "val_end_d",
        "val_end_t",
    ):
        time_state_value = serializable_initial_state.get(time_state_key)
        if isinstance(time_state_value, (date, time)):
            serializable_initial_state[time_state_key] = (
                time_state_value.isoformat()
            )
    environment = os.environ.copy()
    existing_python_path = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = os.pathsep.join(
        part
        for part in (str(REPOSITORY_ROOT), existing_python_path)
        if part
    )
    completed_process = subprocess.run(
        [
            sys.executable,
            "-c",
            APPLICATION_PROBE,
            str(REPOSITORY_ROOT),
            json.dumps(serializable_initial_state),
        ],
        cwd=REPOSITORY_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert completed_process.returncode == 0, (
        f"exit code: {completed_process.returncode}\n"
        f"stdout:\n{completed_process.stdout}\n"
        f"stderr:\n{completed_process.stderr}"
    )
    result_lines = [
        line
        for line in completed_process.stdout.splitlines()
        if line.startswith(APPLICATION_RESULT_PREFIX)
    ]
    assert result_lines, completed_process.stdout
    result = json.loads(result_lines[-1][len(APPLICATION_RESULT_PREFIX):])
    assert result["exceptions"] == []
    return result


def test_guided_run_validates_incomplete_inputs_and_save_requires_readiness():
    """Keep Run available to reveal required fields without submitting invalid data."""
    incomplete_application = _run_application_with_state(
        {
            "lang": "en",
            "input_view": "guided",
            "_probe_click_run": True,
        }
    )

    assert len(incomplete_application["run_actions"]) == 1
    assert incomplete_application["run_actions"][0]["disabled"] is False
    assert "guided_use_case" in incomplete_application["field_errors"]
    assert incomplete_application["run_mode"] is None
    assert incomplete_application["save_actions"] == []
    assert GUIDED_INPUTS["en"]["validation"]["use_case"] in incomplete_application["warnings"]

    for direction, use_case, expected_label in (
        ("rx", "rx_performance", "Run RX Analysis"),
        ("tx", "tx_performance", "Run TX Analysis"),
    ):
        ready_application = _run_application_with_state(
            _canonical_state(
                guided_use_case=use_case,
                val_analysis_direction=direction,
            )
        )

        assert ready_application["run_actions"] == [
            {
                "label": expected_label,
                "disabled": False,
                "type": "primary",
            }
        ]
        assert ready_application["save_actions"] == [
            {"label": "Save Config", "disabled": False}
        ]


def test_classic_run_reports_missing_design_and_save_waits_for_readiness():
    """Exercise pending and complete Classic Benchmark states through AppTest."""
    pending_application = _run_application_with_state(
        _canonical_state(
            input_view="classic",
            classic_question="rx_benchmark",
            guided_use_case="rx_benchmark",
            val_comp_mode="none",
            _probe_click_run=True,
        )
    )

    assert "val_comp_mode" in pending_application["field_errors"]
    assert pending_application["run_mode"] is None
    assert pending_application["run_actions"] == [
        {
            "label": "Run RX Analysis",
            "disabled": False,
            "type": "primary",
        }
    ]
    assert pending_application["save_actions"] == [
        {"label": "Save Config", "disabled": True}
    ]

    ready_application = _run_application_with_state(
        _canonical_state(
            input_view="classic",
            classic_question="rx_benchmark",
            guided_use_case="rx_benchmark",
            guided_reference_design="local_neighborhood",
            guided_last_benchmark_mode="local_neighborhood",
            val_comp_mode="local_neighborhood",
        )
    )

    assert ready_application["errors"] == []
    assert ready_application["run_actions"] == [
        {
            "label": "Run RX Analysis",
            "disabled": False,
            "type": "primary",
        }
    ]
    assert ready_application["save_actions"] == [
        {"label": "Save Config", "disabled": False}
    ]


@pytest.mark.parametrize("input_view", ("guided", "classic"))
def test_time_widget_edits_preserve_entered_minutes_across_rerun(input_view):
    application = _run_application_with_state(
        _canonical_state(
            input_view=input_view,
            val_start_d=date(2026, 7, 10),
            val_start_t=time(9, 0),
            val_end_d=date(2026, 7, 10),
            val_end_t=time(11, 0),
            _absolute_time_window_initialized=True,
            _probe_time_edits=[("val_start_t", "09:50:00"), ("val_end_t", "10:20:00")],
        )
    )
    assert application["time_values"] == {"val_start_t": "09:50:00", "val_end_t": "10:20:00"}
    assert application["errors"] == []
    assert application["save_actions"] == [{"label": "Save Config", "disabled": False}]
    assert application["run_mode"] is None


@pytest.mark.parametrize("input_view", ("guided", "classic"))
def test_invalid_windows_are_reported_and_blocked_before_submission(input_view):
    """Render exact and retained-invalid windows without a widget exception."""
    invalid_windows = (
        (
            date(2026, 6, 1),
            time(0, 0),
            date(2026, 7, 2),
            time(0, 15),
            "err_time_duration",
        ),
        (
            date(2026, 6, 1),
            time(0, 0),
            date(2026, 7, 3),
            time(0, 0),
            "err_time_duration",
        ),
        (
            date(2026, 7, 10),
            time(0, 0),
            date(2026, 7, 9),
            time(0, 0),
            "err_time_order",
        ),
        (
            date(2026, 7, 10),
            time(12, 0),
            date(2026, 7, 10),
            time(11, 0),
            "err_time_order",
        ),
        (
            date(2026, 7, 10),
            time(9, 50),
            date(2026, 7, 10),
            time(9, 50),
            "err_time_order",
        ),
    )

    for start_date, start_time, end_date, end_time, error_key in invalid_windows:
        invalid_application = _run_application_with_state(
            _canonical_state(
                input_view=input_view,
                val_start_d=start_date,
                val_start_t=start_time,
                val_end_d=end_date,
                val_end_t=end_time,
                _absolute_time_window_initialized=True,
                _probe_click_run=True,
            )
        )

        assert invalid_application["exceptions"] == []
        assert T["en"][error_key] in invalid_application["errors"]
        for field in ("val_start_d", "val_start_t", "val_end_d", "val_end_t"):
            assert field in invalid_application["field_errors"]
            assert any(f".st-key-{field}" in style for style in invalid_application["field_error_styles"])
        assert invalid_application["run_mode"] is None
        assert invalid_application["run_actions"] == [
            {
                "label": "Run RX Analysis",
                "disabled": False,
                "type": "primary",
            }
        ]


def test_letter_only_archive_identity_is_valid_in_guided_and_classic_inputs():
    """Render KFS without an identity error and keep both editors runnable."""
    for input_view in ("guided", "classic"):
        application = _run_application_with_state(
            _canonical_state(input_view=input_view, val_callsign="KFS")
        )

        assert application["errors"] == []
        assert application["run_actions"] == [
            {
                "label": "Run RX Analysis",
                "disabled": False,
                "type": "primary",
            }
        ]


def test_stale_warning_preserves_the_ready_rerun_action():
    """Keep the injected Run action available for a valid changed request."""
    stale_application = _run_application_with_state(
        _canonical_state(
            guided_active_node="target_and_window",
            configuration_changed_since_run=True,
        )
    )

    assert stale_application["warnings"] == [
        GUIDED_INPUTS["en"]["messages"]["configuration_changed"]
    ]
    assert stale_application["run_actions"] == [
        {
            "label": "Run RX Analysis",
            "disabled": False,
            "type": "primary",
        }
    ]


def _application_tree_nodes_with_paths(application):
    """Expose AppTest's actual delta paths, including unnamed placeholders."""
    from streamlit.testing.v1.element_tree import Block

    def visit(node, path):
        yield path, node
        if isinstance(node, Block):
            for index, child in node.children.items():
                yield from visit(child, (*path, index))

    return list(visit(application._tree, ()))


def _application_page_region_paths(application):
    """Locate each page region by its emitted Streamlit container identity."""
    region_keys = (
        "application_configuration",
        "application_results",
        "application_documentation",
    )
    paths = {}
    for region_key in region_keys:
        matches = [
            path
            for path, node in _application_tree_nodes_with_paths(application)
            if str(getattr(getattr(node, "proto", None), "id", "")).endswith(
                f"-{region_key}"
            )
        ]
        assert len(matches) == 1, (region_key, matches)
        paths[region_key] = matches[0]
    assert all(path[:-1] == (0,) for path in paths.values())
    assert list(paths.values()) == sorted(paths.values())
    return paths


@pytest.fixture
def page_region_application(monkeypatch):
    """Run the real shell with tiny slot-owned maps and no scientific work."""
    import streamlit as st
    from ui import documentation_scroll_trigger, run_controller, url_synchronizer

    # Component JavaScript has independent behavioral coverage. Its cached
    # declarations are not registered in every AppTest runtime in this suite.
    for component_module, component_attribute in (
        (page_navigation, "_PAGE_NAVIGATION_CONTROLLER"),
        (url_synchronizer, "_URL_QUERY_SYNCHRONIZER"),
        (documentation_scroll_trigger, "_DOCUMENTATION_SCROLL_TRIGGER"),
    ):
        monkeypatch.setattr(
            component_module, component_attribute, lambda **_kwargs: None,
        )

    rendered_slot_paths = []

    def render_tiny_results(
        *, map_results_slot, map_results_container, is_existing_run_rerender, **_kwargs,
    ):
        assert (map_results_container is not None) is is_existing_run_rerender
        assert (map_results_slot is None) is is_existing_run_rerender
        result_target = (
            map_results_container if is_existing_run_rerender else map_results_slot
        )
        target_path = tuple(result_target._cursor.delta_path)
        # Container cursors point at their next child; empty placeholders have
        # a locked cursor pointing at the replaceable element itself.
        rendered_slot_paths.append(
            target_path[:-1] if is_existing_run_rerender else target_path
        )
        count = st.session_state["_test_layout_result_count"]
        if count:
            result_context = (
                map_results_container if is_existing_run_rerender
                else map_results_slot.container()
            )
            with result_context:
                for index in range(count):
                    with st.container(key=f"test_layout_result_{index}"):
                        st.markdown(f"WSPRADAR_LAYOUT_RESULT_{index}")

    monkeypatch.setattr(run_controller, "render_analysis_run", render_tiny_results)

    def create(input_view, **overrides):
        application = AppTest.from_file(
            str(REPOSITORY_ROOT / "app.py"), default_timeout=60,
        )
        initial_state = _canonical_state(
            _initial_config_loaded=True,
            input_view=input_view,
            run_mode="RX",
            _test_layout_result_count=2,
        )
        initial_state.update(overrides)
        for key, value in initial_state.items():
            application.session_state[key] = value
        application.run()
        assert list(application.exception) == []
        if initial_state["run_mode"]:
            assert rendered_slot_paths
        return application, rendered_slot_paths

    return create


@pytest.mark.parametrize("language", ["en", "de"])
@pytest.mark.parametrize("direction", ["rx", "tx"])
@pytest.mark.parametrize("result_family", ["performance", "benchmark"])
def test_guided_demo_shortcut_starts_analysis_with_one_click(
    page_region_application, language, direction, result_family,
):
    """The real Guided button opens Review and enters the controller once."""
    application, rendered_slot_paths = page_region_application(
        "guided",
        lang=language,
        run_mode=None,
        guided_use_case=f"{direction}_{result_family}",
        val_analysis_direction=direction,
        val_comp_mode="reference_station" if result_family == "benchmark" else "none",
        guided_reference_design="reference_station" if result_family == "benchmark" else None,
        val_ref_callsign="G1XYZ",
        val_ref_qth="JO01",
        active_demo_profile="example",
        guided_loaded_demo_profile="example",
        guided_demo_metadata_open=True,
        configuration_changed_since_run=True,
        loaded_config_profile={
            "title": {"en": "Demo", "de": "Demo"},
            "description": {"en": "Demo settings", "de": "Demo-Einstellungen"},
        },
    )
    assert rendered_slot_paths == []
    shortcut = application.button(key="guided_demo_skip_to_review")
    assert shortcut.label == GUIDED_INPUTS[language]["messages"]["demo_skip_to_review"]
    assert shortcut.disabled is False

    shortcut.click().run()

    assert list(application.exception) == []
    assert len(rendered_slot_paths) == 1
    assert application.session_state["run_mode"] == direction.upper()
    assert application.session_state["run_id"] != 17
    assert application.session_state["active_demo_profile"] == "example"
    assert application.session_state["guided_active_node"] == "review_and_run"
    assert application.session_state["guided_demo_metadata_open"] is False
    # AppTest exposes expanders with custom icons through its status collection.
    reviews = [
        expander for expander in (*application.expander, *application.status)
        if GUIDED_INPUTS[language]["summaries"]["review_ready"].format(step=6) == expander.label
    ]
    assert len(reviews) == 1
    assert reviews[0].proto.expanded is True
    assert application.button(key="guided_demo_skip_to_review").disabled is False
    assert "_analysis_submission_requested_token" not in application.session_state
    assert GUIDED_INPUTS[language]["messages"]["configuration_changed"] not in [
        warning.value for warning in application.warning
    ]
    run_id = application.session_state["run_id"]
    application.run()
    assert list(application.exception) == []
    assert application.session_state["run_id"] == run_id
    assert application.button(key="guided_demo_skip_to_review").disabled is False


def _assert_application_region_contents(
    application, expected_region_paths, map_slot_path, expected_result_count,
    *, require_empty_element=False,
):
    """Keep all rendered maps in one stable slot and verify empty replacement."""
    assert list(application.exception) == []
    assert _application_page_region_paths(application) == expected_region_paths
    results_path = expected_region_paths["application_results"]
    assert map_slot_path[:-1] == results_path
    nodes = _application_tree_nodes_with_paths(application)
    result_nodes = [
        (path, node)
        for path, node in nodes
        if node.type == "markdown"
        and node.value.startswith("WSPRADAR_LAYOUT_RESULT_")
    ]
    assert [node.value for _path, node in result_nodes] == [
        f"WSPRADAR_LAYOUT_RESULT_{index}"
        for index in range(expected_result_count)
    ]
    assert all(
        path[:len(map_slot_path)] == map_slot_path
        for path, _node in result_nodes
    )
    if expected_result_count == 0:
        slot_nodes = [node for path, node in nodes if path == map_slot_path]
        assert len(slot_nodes) == 1
        if require_empty_element:
            assert slot_nodes[0].type == "empty"
        else:
            assert slot_nodes[0].type == "empty" or not slot_nodes[0].children


@pytest.mark.parametrize("initial_view", ["guided", "classic"])
def test_application_regions_remain_stable_across_editor_and_loader_changes(
    page_region_application, initial_view,
):
    """Variable input panels and launchers never occupy previous result paths."""
    application, rendered_slot_paths = page_region_application(initial_view)
    expected_paths = _application_page_region_paths(application)
    map_slot_path = rendered_slot_paths[0]

    def assert_layout(result_count):
        _assert_application_region_contents(
            application, expected_paths, map_slot_path, result_count,
            require_empty_element=result_count == 0,
        )
        assert set(rendered_slot_paths) == {map_slot_path}

    assert_layout(2)
    next_view = "classic" if initial_view == "guided" else "guided"
    application.selectbox(key="input_view").select(next_view).run()
    assert_layout(2)

    application.button(key="load_demo_launcher").click().run()
    assert application.session_state["show_demo_launcher"] is True
    assert_layout(0)
    # AppTest formats radio values outside ScriptRunContext. Reuse the exact
    # labels the real launcher rendered; its formatter normally reads session
    # language inside the app thread, which bare test serialization cannot do.
    from streamlit.runtime.state.common import TESTING_KEY

    demo_radio = application.radio(key="selected_demo_profile")
    rendered_demo_labels = dict(zip(renderer.DEMO_PROFILES, demo_radio.options, strict=True))
    application.session_state[TESTING_KEY][demo_radio.id] = rendered_demo_labels.__getitem__
    application.button(key="load_demo_launcher").click().run()
    assert application.session_state["show_demo_launcher"] is False
    assert_layout(0)
    application.button(key="run_analysis_button").click().run()
    assert_layout(2)

    next(
        button for button in application.button
        if button.label == T["en"]["btn_load_config"]
    ).click().run()
    assert application.session_state["show_config_loader"] is True
    assert len(application.get("file_uploader")) == 1
    assert_layout(0)
    next(
        button for button in application.button
        if button.label == T["en"]["btn_load_config"]
    ).click().run()
    assert application.session_state["show_config_loader"] is False
    assert len(application.get("file_uploader")) == 0
    assert_layout(0)
    application.button(key="run_analysis_button").click().run()
    assert_layout(2)


@pytest.mark.parametrize("input_view", ["guided", "classic"])
def test_application_result_slot_replaces_shorter_empty_and_invalid_results(
    page_region_application, input_view,
):
    """Two, one, zero, and validation-blocked runs reuse and clear one map slot."""
    application, rendered_slot_paths = page_region_application(input_view)
    expected_paths = _application_page_region_paths(application)
    map_slot_path = rendered_slot_paths[0]
    _assert_application_region_contents(application, expected_paths, map_slot_path, 2)

    for result_count in (1, 0, 1):
        application.session_state["_test_layout_result_count"] = result_count
        application.run()
        _assert_application_region_contents(
            application, expected_paths, map_slot_path, result_count,
        )
    assert set(rendered_slot_paths) == {map_slot_path}

    calls_before_validation = len(rendered_slot_paths)
    application.text_input(key="val_callsign").input("!").run()
    _assert_application_region_contents(
        application, expected_paths, map_slot_path, 0, require_empty_element=True,
    )
    assert len(rendered_slot_paths) == calls_before_validation
    assert application.session_state["run_mode"] is None
    assert T["en"]["err_callsign_format"] in [
        message.value for message in (*application.error, *application.warning)
    ]
