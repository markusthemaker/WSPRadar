"""Integration contracts for Guided callbacks and terminal action gating."""

import ast
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import Mock

from i18n import GUIDED_INPUTS, T
from ui import callbacks, config_io, page_navigation
from ui.analysis_context_adapter import build_analysis_context_from_session_state
from ui.guided_inputs import renderer
from ui.guided_inputs.state import reconstruct_guided_transients


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
APPLICATION_RESULT_PREFIX = "WSPRADAR_GUIDED_APPLICATION_RESULT="
APPLICATION_PROBE = r'''
import json
from pathlib import Path
import sys

from streamlit.testing.v1 import AppTest


project_root = Path(sys.argv[1]).resolve()
initial_state = json.loads(sys.argv[2])
application = AppTest.from_file(
    str(project_root / "app.py"),
    default_timeout=60,
)
application.session_state["_initial_config_loaded"] = True
for key, value in initial_state.items():
    application.session_state[key] = value
application.run()
result = {
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
    ],
    "warnings": [warning.value for warning in application.warning],
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
            "guided_use_case": "rx_success",
            "guided_reference_design": None,
            "guided_last_compare_mode": None,
            "val_snr_correction_mode": "no_offset",
            "guided_scope_mode": "general",
            "guided_active_node": "use_case",
            "guided_collapse_all": False,
            "configuration_changed_since_run": False,
            "val_analysis_direction": "rx",
            "val_callsign": "DL1ABC",
            "val_qth": "JO62QM",
            "val_band": "40m",
            "val_time_mode": "last_x",
            "val_hours": 24,
            "val_comp_mode": "none",
            "val_local_benchmark": "local_median",
            "val_ref_callsign": "",
            "val_ref_qth": "",
            "val_ref_radius_km": 100,
            "val_benchmark_offset_db": 0.0,
            "val_tx_ab_method": "simultaneous",
            "val_tx_ab_repeat_interval_minutes": 10,
            "val_tx_ab_target_start_minute": 0,
            "val_tx_ab_reference_start_minute": 2,
            "val_solar": "all",
            "val_max_peer_distance_km": 22000,
            "val_exclude_special_callsigns": False,
            "val_filter_moving": False,
            "val_min_spots": 1,
            "val_min_opportunities": 5,
            "val_min_stations": 1,
        }
    )
    state.update(overrides)
    return state


def _install_shared_streamlit_state(monkeypatch, session_state):
    """Make renderer and callback modules operate on one canonical mapping."""
    fake_streamlit = SimpleNamespace(session_state=session_state)
    monkeypatch.setattr(renderer, "st", fake_streamlit)
    monkeypatch.setattr(callbacks, "st", fake_streamlit)


def test_input_view_selector_uses_concise_wizard_and_panel_labels():
    """Keep both localized selector options concise and visually distinct."""
    expected_labels = {
        "en": {"guided": "🪄 Guided", "classic": "▤ Classic"},
        "de": {"guided": "🪄 Geführt", "classic": "▤ Klassisch"},
    }

    for language, labels in expected_labels.items():
        assert {
            input_view: GUIDED_INPUTS[language]["mode"][input_view]
            for input_view in ("guided", "classic")
        } == labels


def test_guided_definitions_reuse_documentation_defined_term_markup():
    """Highlight introduced domain terms without recoloring ordinary emphasis."""
    expected_terms = {
        "en": ("Target", "Success", "Compare", "SNR", "ΔSNR"),
        "de": ("Target", "Success", "Compare", "Referenz", "ΔSNR"),
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
    assert 'st.markdown(content["body_md"], unsafe_allow_html=True)' in (
        renderer_source
    )


def test_reference_design_options_use_localized_captioned_radio_rows(monkeypatch):
    """Separate Reference designs and make each explanation selectable."""
    expected_titles = {
        "en": "Reference designs",
        "de": "Referenzdesigns",
    }

    for language, expected_title in expected_titles.items():
        markdown = Mock()
        radio = Mock()
        monkeypatch.setattr(
            renderer,
            "st",
            SimpleNamespace(
                session_state=_canonical_state(lang=language),
                markdown=markdown,
                radio=radio,
            ),
        )

        renderer._render_reference_design_fields(
            T[language],
            GUIDED_INPUTS[language],
        )

        markdown.assert_called_once_with(f"**{expected_title}**")
        options = GUIDED_INPUTS[language]["options"]["reference_design"]
        positional_args, keyword_args = radio.call_args
        assert positional_args == (
            GUIDED_INPUTS[language]["steps"]["reference_design"]["title"],
            tuple(options),
        )
        assert keyword_args["captions"] == tuple(
            option["description"] for option in options.values()
        )
        assert keyword_args["width"] == "stretch"
        assert keyword_args["on_change"] is renderer._handle_reference_design_change
        assert [
            keyword_args["format_func"](option_key)
            for option_key in options
        ] == [option["label"] for option in options.values()]


def test_guided_reference_subchoices_move_into_shared_caption_controls(
    monkeypatch,
):
    """Remove duplicated guides while retaining the complete localized choices."""
    cases = (
        ("hardware_ab", "tx"),
        ("local_neighborhood", "rx"),
    )

    for benchmark_mode, analysis_direction in cases:
        markdown = Mock()
        caption = Mock()
        shared_reference_fields = Mock()
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
            ),
        )
        monkeypatch.setattr(
            renderer,
            "render_reference_design_fields",
            shared_reference_fields,
        )

        renderer._render_reference_design_fields(T["en"], GUIDED_INPUTS["en"])

        markdown.assert_called_once_with("**Reference designs**")
        caption.assert_not_called()
        keyword_args = shared_reference_fields.call_args.kwargs
        assert keyword_args["local_benchmark_content"] is (
            GUIDED_INPUTS["en"]["options"]["local_benchmark"]
        )
        assert keyword_args["tx_ab_method_content"] is (
            GUIDED_INPUTS["en"]["options"]["tx_ab_method"]
        )
        assert keyword_args["help_overrides"]["tx_ab_method"] == (
            GUIDED_INPUTS["en"]["messages"]["tx_ab_method_help"]
        )


def test_offset_intent_options_use_localized_captioned_radio_rows(monkeypatch):
    """Make each complete offset explanation part of its selection."""
    for language in ("en", "de"):
        markdown = Mock()
        radio = Mock()
        info = Mock()
        monkeypatch.setattr(
            renderer,
            "st",
            SimpleNamespace(
                session_state=_canonical_state(
                    lang=language,
                    guided_use_case="rx_compare",
                    guided_reference_design="reference_station",
                    val_comp_mode="reference_station",
                ),
                markdown=markdown,
                radio=radio,
                info=info,
            ),
        )

        renderer._render_offset_calibration_fields(
            T[language],
            GUIDED_INPUTS[language],
        )

        options = GUIDED_INPUTS[language]["options"]["offset_intent"]
        messages = GUIDED_INPUTS[language]["messages"]
        markdown.assert_called_once_with(messages["correction_formula"])
        info.assert_called_once_with(messages["reference_calibration"])
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


def test_compare_terminology_uses_three_bulleted_definitions():
    """Indent each Compare term as a distinct bilingual list item."""
    expected_term_labels = {
        "en": ("SNR", "ΔSNR", "Joint evidence"),
        "de": ("SNR", "ΔSNR", "Joint-Evidenz"),
    }

    for language, term_labels in expected_term_labels.items():
        reference_body = GUIDED_INPUTS[language]["steps"][
            "reference_design"
        ]["body_md"]
        bullet_lines = [
            line
            for line in reference_body.splitlines()
            if line.startswith("- **")
        ]

        assert len(bullet_lines) == 3
        assert all(
            bullet_line.startswith(f"- **{term_label}**")
            for bullet_line, term_label in zip(
                bullet_lines,
                term_labels,
                strict=True,
            )
        )
        assert not any(
            line.startswith(">")
            for line in reference_body.splitlines()
        )


def test_guided_demo_metadata_is_localized_and_initially_expanded(monkeypatch):
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
        ),
    )

    renderer._render_demo_metadata(
        GUIDED_INPUTS["de"],
        walkthrough_node="synthetic-start",
        review_node="synthetic-review",
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
        "key": "guided_demo_skip_to_review",
        "type": "primary",
        "on_click": renderer._open_demo_node,
        "args": ("synthetic-review",),
        "width": "stretch",
    }


def test_known_reference_guidance_uses_informational_callout(monkeypatch):
    """Reserve warning styling for actionable or invalid Guided Input states."""
    session_state = _canonical_state(
        guided_reference_design="reference_station",
        val_comp_mode="reference_station",
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
        ),
    )
    monkeypatch.setattr(renderer, "render_reference_design_fields", Mock())

    renderer._render_reference_design_fields(T["en"], GUIDED_INPUTS["en"])

    info.assert_called_once_with(
        GUIDED_INPUTS["en"]["messages"]["known_reference_note"]
    )
    warning.assert_not_called()


def test_guided_demo_actions_only_open_the_requested_flow_node(monkeypatch):
    """Navigate from demo context without changing preset or run identity."""
    flow = renderer.load_guided_input_flow()
    for destination in (flow["start_node"], flow["terminal_node"]):
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


def test_guided_continue_advances_without_requesting_a_browser_scroll(monkeypatch):
    """Open the next panel while replacing only the stale coarse URL fragment."""
    session_state = _canonical_state(
        guided_active_node="use_case",
        guided_collapse_all=True,
    )
    monkeypatch.setattr(
        renderer,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    renderer._continue_to("target_and_window")
    navigation_request = page_navigation.consume_page_navigation_request(
        session_state
    )

    assert session_state.guided_active_node == "target_and_window"
    assert session_state.guided_collapse_all is False
    assert navigation_request is not None
    assert navigation_request["anchor_id"] == (
        page_navigation.PARAMETER_SETTINGS_ANCHOR_ID
    )
    assert navigation_request["should_scroll"] is False


def test_demo_metadata_precedes_forced_collapsed_scientific_steps(monkeypatch):
    """Keep metadata first and every preset step collapsed on initial demo load."""
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
            "review_node": "review_and_run",
        },
    )
    step_events = [event for event in events if event[0] == "step"]
    assert step_events
    assert all(event[2] is False for event in step_events)
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
    """Attach every localized implication to its selector without duplication."""
    radio = Mock()
    markdown = Mock()
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

    markdown.assert_not_called()


def test_general_scope_panel_omits_redundant_guidance_and_value_summary(monkeypatch):
    """Show the preset choice and caveat without repeating panel-six values."""
    radio = Mock()
    info = Mock()
    markdown = Mock()
    caption = Mock()
    monkeypatch.setattr(
        renderer,
        "st",
        SimpleNamespace(
            session_state=_canonical_state(guided_scope_mode="general"),
            radio=radio,
            info=info,
            markdown=markdown,
            caption=caption,
        ),
    )

    renderer._render_scope_and_evidence_fields(T["en"], GUIDED_INPUTS["en"])

    info.assert_called_once_with(GUIDED_INPUTS["en"]["messages"]["general_active"])
    markdown.assert_not_called()
    caption.assert_not_called()
    assert radio.call_args.args[1] == ("general", "custom")


def test_custom_scope_panel_shows_only_relevant_evidence_guidance(monkeypatch):
    """Explain Success or Compare thresholds according to the active result."""
    messages = GUIDED_INPUTS["en"]["messages"]
    cases = (
        (
            "none",
            "success_evidence_requirements_body",
            "compare_evidence_requirements_body",
            "success",
        ),
        (
            "hardware_ab",
            "compare_evidence_requirements_body",
            "success_evidence_requirements_body",
            "compare",
        ),
    )

    for comparison_mode, expected_key, excluded_key, expected_result_type in cases:
        caption = Mock()
        render_evidence_fields = Mock()
        monkeypatch.setattr(
            renderer,
            "st",
            SimpleNamespace(
                session_state=_canonical_state(
                    guided_scope_mode="custom",
                    val_comp_mode=comparison_mode,
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

        renderer._render_scope_and_evidence_fields(T["en"], GUIDED_INPUTS["en"])

        captions = [call.args[0] for call in caption.call_args_list]
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


def test_guided_use_case_maps_to_canonical_state_and_invalidates_active_results(
    monkeypatch,
):
    """Map Guided intent without a second scientific state or stale results."""
    session_state = _canonical_state(
        run_mode="RX",
        guided_use_case="tx_compare",
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

    session_state.guided_use_case = "rx_success"
    renderer._handle_use_case_change()

    assert session_state.val_analysis_direction == "rx"
    assert session_state.val_comp_mode == "none"
    assert session_state.guided_reference_design is None
    assert session_state.guided_last_compare_mode == "reference_station"
    assert session_state.val_ref_callsign == "DL2XYZ"
    assert session_state.val_ref_qth == "JO63"


def test_guided_direction_change_requires_hardware_design_confirmation(
    monkeypatch,
):
    """Do not reinterpret RX Hardware identity as a TX Hardware schedule."""
    session_state = _canonical_state(
        run_mode="RX",
        guided_use_case="tx_compare",
        guided_reference_design="hardware_ab",
        guided_last_compare_mode="hardware_ab",
        val_snr_correction_mode="established_offset",
        val_analysis_direction="rx",
        val_comp_mode="hardware_ab",
        val_ref_callsign="DL1ABC-1",
        val_benchmark_offset_db=1.4,
        val_tx_ab_method="sequential",
        val_tx_ab_repeat_interval_minutes=20,
        val_tx_ab_target_start_minute=4,
        val_tx_ab_reference_start_minute=6,
    )
    _install_shared_streamlit_state(monkeypatch, session_state)

    renderer._handle_use_case_change()

    assert session_state.val_analysis_direction == "tx"
    assert session_state.val_comp_mode == "none"
    assert session_state.guided_reference_design is None
    assert session_state.guided_last_compare_mode is None
    assert session_state.val_benchmark_offset_db == 0.0
    assert session_state.val_snr_correction_mode == "no_offset"
    assert session_state.val_tx_ab_method == "simultaneous"
    assert session_state.val_tx_ab_repeat_interval_minutes == 10
    assert session_state.val_tx_ab_target_start_minute == 0
    assert session_state.val_tx_ab_reference_start_minute == 2
    assert session_state.val_ref_callsign == "DL1ABC-1"
    assert session_state.run_mode is None
    assert session_state.configuration_changed_since_run is True


def test_direction_change_clears_hardware_retained_behind_success(monkeypatch):
    """Do not reactivate RX Hardware semantics after crossing TX Success."""
    session_state = _canonical_state(
        guided_use_case="rx_success",
        guided_last_compare_mode="hardware_ab",
        val_analysis_direction="rx",
        val_comp_mode="none",
        val_ref_callsign="DL1ABC-1",
    )
    _install_shared_streamlit_state(monkeypatch, session_state)

    session_state.guided_use_case = "tx_success"
    renderer._handle_use_case_change()
    session_state.guided_use_case = "tx_compare"
    renderer._handle_use_case_change()

    assert session_state.val_analysis_direction == "tx"
    assert session_state.val_comp_mode == "none"
    assert session_state.guided_reference_design is None
    assert session_state.guided_last_compare_mode is None


def test_direction_change_resets_reference_station_pair_correction(monkeypatch):
    """Treat RX and TX Reference baselines as different operating designs."""
    session_state = _canonical_state(
        guided_use_case="tx_compare",
        guided_reference_design="reference_station",
        guided_last_compare_mode="reference_station",
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
    assert session_state.val_ref_qth == "JO63"
    assert session_state.val_benchmark_offset_db == 0.0
    assert session_state.val_snr_correction_mode == "no_offset"


def test_reference_branch_change_clears_only_pair_specific_canonical_values(
    monkeypatch,
):
    """Deactivate fixed-Reference identity/correction while retaining scope."""
    session_state = _canonical_state(
        guided_use_case="rx_compare",
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
    assert session_state.guided_last_compare_mode == "local_neighborhood"
    assert session_state.val_ref_callsign == ""
    assert session_state.val_ref_qth == ""
    assert session_state.val_benchmark_offset_db == 0.0
    assert session_state.val_snr_correction_mode == "no_offset"
    assert session_state.val_callsign == "DL1ABC"
    assert session_state.val_band == "40m"
    assert session_state.val_max_peer_distance_km == 5000
    assert session_state.val_min_spots == 3
    assert session_state.val_min_stations == 2


def test_known_station_to_hardware_requires_reference_identity_confirmation(
    monkeypatch,
):
    """Do not reinterpret a remote station identity as a co-located path."""
    session_state = _canonical_state(
        guided_use_case="rx_compare",
        guided_reference_design="hardware_ab",
        val_snr_correction_mode="established_offset",
        val_comp_mode="reference_station",
        val_ref_callsign="DL2XYZ",
        val_ref_qth="JO63",
        val_benchmark_offset_db=1.2,
    )
    _install_shared_streamlit_state(monkeypatch, session_state)

    renderer._handle_reference_design_change()

    assert session_state.val_comp_mode == "hardware_ab"
    assert session_state.val_ref_callsign == ""
    assert session_state.val_ref_qth == ""
    assert session_state.val_benchmark_offset_db == 0.0
    assert session_state.val_snr_correction_mode == "no_offset"


def test_hardware_to_known_station_requires_reference_identity_confirmation(
    monkeypatch,
):
    """Do not reinterpret a local path alias and stale grid as a remote station."""
    session_state = _canonical_state(
        guided_use_case="rx_compare",
        guided_reference_design="reference_station",
        val_snr_correction_mode="established_offset",
        val_comp_mode="hardware_ab",
        val_ref_callsign="DL1ABC-1",
        val_ref_qth="JO63",
        val_benchmark_offset_db=-0.8,
    )
    _install_shared_streamlit_state(monkeypatch, session_state)

    renderer._handle_reference_design_change()

    assert session_state.val_comp_mode == "reference_station"
    assert session_state.val_ref_callsign == ""
    assert session_state.val_ref_qth == ""
    assert session_state.val_benchmark_offset_db == 0.0
    assert session_state.val_snr_correction_mode == "no_offset"


def test_offset_intents_share_the_one_canonical_correction_field(monkeypatch):
    """Preserve an entered offset, but pin no-offset/calibration runs to zero."""
    session_state = _canonical_state(
        guided_use_case="rx_compare",
        guided_reference_design="hardware_ab",
        val_snr_correction_mode="established_offset",
        val_comp_mode="hardware_ab",
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
        guided_use_case="rx_compare",
        guided_reference_design="reference_station",
        guided_last_compare_mode="reference_station",
        val_snr_correction_mode="established_offset",
        val_comp_mode="reference_station",
        val_ref_callsign="DL2XYZ",
        val_ref_qth="JO63",
        val_benchmark_offset_db=1.2,
    )
    _install_shared_streamlit_state(monkeypatch, session_state)

    renderer._guided_correction_context_change("target_and_window")

    assert session_state.val_benchmark_offset_db == 0.0
    assert session_state.val_snr_correction_mode == "no_offset"
    assert session_state.guided_active_node == "target_and_window"


def test_german_review_uses_localized_target_and_complete_tx_schedule(monkeypatch):
    """Keep review prose localized and expose every scheduled pairing control."""
    session_state = _canonical_state(
        lang="de",
        guided_use_case="tx_compare",
        guided_reference_design="hardware_ab",
        guided_last_compare_mode="hardware_ab",
        val_analysis_direction="tx",
        val_comp_mode="hardware_ab",
        val_tx_ab_method="sequential",
        val_tx_ab_repeat_interval_minutes=20,
        val_tx_ab_target_start_minute=4,
        val_tx_ab_reference_start_minute=6,
    )
    markdown = Mock()
    monkeypatch.setattr(
        renderer,
        "st",
        SimpleNamespace(
            session_state=session_state,
            markdown=markdown,
            warning=Mock(),
            button=Mock(),
            empty=Mock(return_value="review-slot"),
        ),
    )

    assert renderer._reference_review_value(GUIDED_INPUTS["de"]) == (
        "Nacheinander nach festem Zeitplan · Intervall 20 min · "
        "Target 04 UTC · Referenz 06 UTC"
    )
    assert (
        renderer._render_review_and_run(T["de"], GUIDED_INPUTS["de"])
        == "review-slot"
    )
    review_markdown = markdown.call_args.args[0]
    assert "DL1ABC bei JO62QM" in review_markdown
    assert " at " not in review_markdown
    assert "Stationspopulation" in review_markdown


def test_switching_to_classic_preserves_configuration_context_and_results(
    monkeypatch,
):
    """Treat editor selection as presentation state only."""
    session_state = _canonical_state(
        run_mode="RX",
        result_export_blocks={"success": ["retained"]},
    )
    monkeypatch.setattr(
        renderer,
        "st",
        SimpleNamespace(session_state=session_state),
    )
    before_state = deepcopy(session_state)
    guided_context = build_analysis_context_from_session_state(session_state)

    renderer._open_classic_view()

    assert session_state.input_view == "classic"
    assert session_state.run_mode == "RX"
    assert session_state.result_export_blocks == {"success": ["retained"]}
    assert {
        key: value for key, value in session_state.items() if key != "input_view"
    } == {
        key: value for key, value in before_state.items() if key != "input_view"
    }
    assert build_analysis_context_from_session_state(session_state) == guided_context


def test_returning_from_classic_reconstructs_guided_state_without_resetting_results(
    monkeypatch,
):
    """Reconcile stale Guided choices after Classic changes direction and design."""
    session_state = _canonical_state(
        input_view="guided",
        run_mode="TX",
        guided_use_case="rx_compare",
        guided_reference_design="hardware_ab",
        guided_last_compare_mode="hardware_ab",
        val_snr_correction_mode="established_offset",
        guided_scope_mode="custom",
        guided_reconstruct_requested=False,
        guided_collapse_all=True,
        val_analysis_direction="tx",
        val_comp_mode="local_neighborhood",
        val_local_benchmark="local_best",
        val_ref_radius_km=250,
        val_benchmark_offset_db=0.0,
        result_export_blocks={"compare": ["retained"]},
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
    assert session_state.result_export_blocks == {"compare": ["retained"]}

    reconstruct_guided_transients(session_state, has_loaded_demo=False)

    assert session_state.guided_use_case == "tx_compare"
    assert session_state.guided_reference_design == "local_neighborhood"
    assert session_state.guided_last_compare_mode == "local_neighborhood"
    assert session_state.val_snr_correction_mode == "established_offset"
    assert session_state.guided_scope_mode == "general"
    assert session_state.run_mode == "TX"
    assert session_state.result_export_blocks == {"compare": ["retained"]}
    assert build_analysis_context_from_session_state(session_state) == canonical_context


def test_view_round_trip_preserves_retained_inactive_compare_design(monkeypatch):
    """Keep view-only switching from erasing a Guided Success user's prior design."""
    session_state = _canonical_state(
        input_view="guided",
        guided_use_case="rx_success",
        guided_reference_design=None,
        guided_last_compare_mode="reference_station",
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

    assert session_state.guided_use_case == "rx_success"
    assert session_state.guided_reference_design is None
    assert session_state.guided_last_compare_mode == "reference_station"
    assert session_state.val_ref_callsign == "DL2XYZ"
    assert session_state.val_ref_qth == "JO63"
    assert session_state.val_benchmark_offset_db == 1.2


def test_loading_success_config_clears_previous_transient_compare_design(
    monkeypatch,
):
    """Do not let history from another config choose a later Compare branch."""
    session_state = _canonical_state(
        guided_last_compare_mode="hardware_ab",
        guided_reference_design="hardware_ab",
        val_comp_mode="hardware_ab",
    )
    monkeypatch.setattr(
        config_io,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    config_io.apply_config_values(config_io._default_config())

    assert session_state.val_comp_mode == "none"
    assert session_state.guided_last_compare_mode is None
    assert session_state.guided_reconstruct_requested is True


def _run_application_with_state(initial_state):
    """Execute one isolated application session with explicit initial state."""
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
            json.dumps(initial_state),
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


def test_guided_run_and_save_actions_are_gated_by_terminal_readiness():
    """Expose primary RX/TX Run actions only when Guided inputs are ready."""
    incomplete_application = _run_application_with_state(
        {
            "lang": "en",
            "input_view": "guided",
        }
    )

    assert incomplete_application["run_actions"] == []
    assert incomplete_application["save_actions"] == []
    assert incomplete_application["warnings"] == [
        GUIDED_INPUTS["en"]["validation"]["use_case"]
    ]

    for direction, use_case, expected_label in (
        ("rx", "rx_success", "Run RX Analysis"),
        ("tx", "tx_success", "Run TX Analysis"),
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
