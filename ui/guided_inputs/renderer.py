"""Streamlit composition for the bilingual Guided Input accordion."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import streamlit as st

from config import DEMO_PROFILES
from config.delta_snr_outlier import (
    DELTA_SNR_OUTLIER_CONFIG_FIELD_TO_POLICY_FIELD,
)
from config.demo_profiles import prepare_demo_description_markdown
from i18n import GUIDED_INPUTS
from ui.analysis_submission_state import handoff_analysis_submission
from ui.analysis_question_state import apply_analysis_question_choice
from ui.callbacks import reset_audit, reset_experiment_definition
from ui.classic_input_state import (
    classic_result_type,
    synchronize_classic_input_state,
)
from ui.components.config_fields import (
    render_delta_snr_outlier_reporting_field,
    render_evidence_threshold_fields,
    render_reference_correction_field,
    render_reference_design_fields,
    render_scope_fields,
    render_station_population_fields,
    render_target_and_window_fields,
)
from ui.components.config_panel import (
    _prepare_loaded_profile_title_markdown,
    _resolve_loaded_profile_text,
)
from ui.components.config_review import (
    reference_review_value,
    render_configuration_review,
)
from ui.config_io import validate_config_document
from ui.page_navigation import (
    PARAMETER_SETTINGS_ANCHOR_ID,
    request_page_navigation,
)
from ui.population_exclusion_state import (
    BENCHMARK_RESULT_TYPE,
    PERFORMANCE_RESULT_TYPE,
    transition_population_exclusion_result_type,
)

from .flow_engine import available_flow_nodes, matching_next_node
from .flow_loader import (
    CONTROL_RENDERER_NAMES,
    GuidedFlowError,
    load_guided_input_flow,
    resolve_content_key,
)
from .state import (
    COMPARISON_MODES,
    GUIDED_OFFSET_INTENTS,
    GUIDED_USE_CASES,
    canonicalize_guided_use_case,
    guided_facts,
    is_guided_node_complete,
    reconstruct_guided_transients,
)
from .summaries import SUMMARY_RENDERERS


@dataclass(frozen=True)
class GuidedRenderResult:
    """Describe the current Guided branch and its terminal action placement."""

    available_nodes: tuple[str, ...]
    is_ready: bool
    review_actions_slot: Any | None


def _activate_step(node_id: str) -> None:
    """Keep an edited Guided step open across the scientific-state rerun."""
    st.session_state.guided_active_node = node_id
    st.session_state.guided_collapse_all = False
    st.session_state.guided_demo_metadata_open = False


def _guided_scientific_change(node_id: str) -> None:
    """Invalidate a population/scope/evidence edit and retain demo context."""
    _activate_step(node_id)
    reset_audit()


def _guided_experiment_definition_change(node_id: str) -> None:
    """Invalidate an experiment edit and retire its loaded profile context."""
    _activate_step(node_id)
    reset_experiment_definition()


def _guided_correction_context_change(node_id: str) -> None:
    """Invalidate any established offset whose scientific context was edited."""
    active_mode = st.session_state.get("val_comp_mode")
    retained_mode = st.session_state.get("guided_last_benchmark_mode")
    if active_mode in COMPARISON_MODES or retained_mode in COMPARISON_MODES:
        st.session_state.val_benchmark_offset_db = 0.0
        st.session_state.val_snr_correction_mode = "no_offset"
    _guided_experiment_definition_change(node_id)


def _handle_use_case_change() -> None:
    """Map one transient question token atomically into canonical direction/design."""
    use_case = canonicalize_guided_use_case(
        st.session_state.get("guided_use_case")
    )
    if use_case not in GUIDED_USE_CASES:
        return
    st.session_state.guided_use_case = use_case
    apply_analysis_question_choice(st.session_state, use_case)
    _guided_experiment_definition_change("use_case")


def _handle_reference_design_change() -> None:
    """Apply the selected design and clear only values invalid in the new branch."""
    new_mode = st.session_state.get("guided_reference_design")
    if new_mode not in COMPARISON_MODES:
        return
    previous_mode = st.session_state.get("val_comp_mode")
    st.session_state.val_comp_mode = new_mode
    st.session_state.guided_last_benchmark_mode = new_mode
    transition_population_exclusion_result_type(
        st.session_state,
        BENCHMARK_RESULT_TYPE,
    )
    if new_mode != previous_mode:
        # Fixed-Reference identities and corrections have design-specific
        # meanings. Reinterpreting a remote station as a co-located path (or a
        # local path alias as a remote station) would silently create a complete
        # but invalid experiment, so require explicit identity confirmation.
        st.session_state.val_ref_callsign = ""
        st.session_state.val_ref_qth = ""
        st.session_state.val_benchmark_offset_db = 0.0
        st.session_state.val_snr_correction_mode = "no_offset"
    if new_mode == "local_neighborhood":
        st.session_state.val_ref_callsign = ""
        st.session_state.val_ref_qth = ""
        st.session_state.val_benchmark_offset_db = 0.0
        st.session_state.val_snr_correction_mode = "no_offset"
    _guided_experiment_definition_change("reference_design")


def _handle_offset_intent_change() -> None:
    """Keep no-offset and calibration runs pinned to the canonical 0.0 dB value."""
    intent = st.session_state.get("val_snr_correction_mode")
    if intent not in GUIDED_OFFSET_INTENTS:
        return
    if intent in {"no_offset", "establish_offset"}:
        st.session_state.val_benchmark_offset_db = 0.0
    _guided_experiment_definition_change("offset_calibration")


def _loaded_demo_scope_values(profile_key: str | None) -> dict[str, Any] | None:
    """Return the validated population/scope values owned by one demo profile."""
    profile = DEMO_PROFILES.get(profile_key)
    if not profile:
        return None
    configuration = profile.get("configuration", profile)
    normalized = validate_config_document(configuration)
    return {
        "val_solar": normalized["solar_state"],
        "val_max_peer_distance_km": normalized["max_peer_distance_km"],
        "val_exclude_special_callsigns": normalized["exclude_special_callsigns"],
        "val_filter_moving": normalized["exclude_moving_stations"],
        "val_min_spots": normalized.get("min_joint_spots_per_station", 1),
        "val_min_opportunities": normalized[
            "min_confirmed_opportunities_per_peer"
        ],
        "val_min_stations": normalized["min_joint_stations_per_map_segment"],
        **(
            {
                "val_report_delta_snr_outlier_candidates": normalized[
                    "report_delta_snr_outlier_candidates"
                ],
                **(
                    {
                        f"val_{config_field}": normalized[config_field]
                        for config_field, _policy_field in (
                            DELTA_SNR_OUTLIER_CONFIG_FIELD_TO_POLICY_FIELD
                        )
                    }
                    if normalized["report_delta_snr_outlier_candidates"]
                    else {}
                ),
            }
            if normalized["benchmark_mode"] != "none"
            else {}
        ),
    }


def _loaded_demo_scope_matches_current_state() -> bool:
    """Return whether current canonical scope still equals the loaded demo preset."""
    expected_values = _loaded_demo_scope_values(
        st.session_state.get("guided_loaded_demo_profile")
    )
    return bool(
        expected_values
        and all(
            st.session_state.get(state_key) == expected_value
            for state_key, expected_value in expected_values.items()
        )
    )


def _continue_to(next_node: str) -> None:
    """Advance the accordion without changing scientific state."""
    st.session_state.guided_active_node = next_node
    st.session_state.guided_collapse_all = False
    request_page_navigation(
        st.session_state,
        PARAMETER_SETTINGS_ANCHOR_ID,
        should_scroll=False,
    )


def _open_demo_node(node_id: str) -> None:
    """Collapse demo context and open one declaratively selected Guided node."""
    st.session_state.guided_demo_metadata_open = False
    st.session_state.guided_active_node = node_id
    st.session_state.guided_collapse_all = False
    request_page_navigation(
        st.session_state,
        PARAMETER_SETTINGS_ANCHOR_ID,
        should_scroll=True,
    )


def _open_classic_view() -> None:
    """Open Classic while preserving any incomplete Guided Benchmark intent."""
    st.session_state.input_view = "classic"
    synchronize_classic_input_state(
        st.session_state,
        preferred_question=st.session_state.get("guided_use_case"),
    )
    transition_population_exclusion_result_type(
        st.session_state,
        classic_result_type(st.session_state)
        or PERFORMANCE_RESULT_TYPE,
    )
    if st.session_state.get("run_mode"):
        handoff_analysis_submission(
            st.session_state,
            request_source="input_view_change",
        )


def _render_use_case_selector(t, guided_content):
    """Render each operating question and its implication as one radio choice."""
    options = guided_content["options"]["use_cases"]
    st.radio(
        guided_content["steps"]["use_case"]["title"],
        tuple(options),
        key="guided_use_case",
        index=None,
        label_visibility="collapsed",
        format_func=lambda value: options[value]["label"],
        captions=tuple(option["description"] for option in options.values()),
        on_change=_handle_use_case_change,
        width="stretch",
    )


def _render_target_and_window_fields(t, guided_content):
    """Render the existing Target/time widgets with richer Guided field help."""
    messages = guided_content["messages"]
    render_target_and_window_fields(
        t,
        on_change=_guided_experiment_definition_change,
        on_change_args=("target_and_window",),
        correction_context_on_change=_guided_correction_context_change,
        correction_context_on_change_args=("target_and_window",),
        help_overrides={
            "callsign": messages["target_callsign_help"],
            "qth": messages["target_qth_help"],
            "band": messages["band_help"],
            "time": messages["time_help"],
        },
    )


def _render_reference_design_fields(t, guided_content):
    """Render captioned Reference choices and existing branch-specific fields."""
    options = guided_content["options"]["reference_design"]
    messages = guided_content["messages"]
    st.markdown(f"**{messages['reference_designs_title']}**")
    st.radio(
        guided_content["steps"]["reference_design"]["title"],
        tuple(options),
        key="guided_reference_design",
        index=None,
        label_visibility="collapsed",
        format_func=lambda value: options[value]["label"],
        captions=tuple(option["description"] for option in options.values()),
        on_change=_handle_reference_design_change,
        width="stretch",
    )
    benchmark_mode = st.session_state.get("val_comp_mode")
    if benchmark_mode == "hardware_ab":
        st.info(messages["controlled_path_note"])
    elif benchmark_mode == "reference_station":
        st.info(messages["known_reference_note"])
    elif benchmark_mode == "local_neighborhood":
        st.info(messages["local_neighborhood_note"])
        correction_db = float(
            st.session_state.get("val_benchmark_offset_db", 0.0)
        )
        if correction_db != 0.0:
            st.warning(
                messages["local_existing_correction_warning"].format(
                    offset=correction_db
                )
            )
    if benchmark_mode in COMPARISON_MODES:
        render_reference_design_fields(
            t,
            on_change=_guided_correction_context_change,
            on_change_args=("reference_design",),
            local_benchmark_content=guided_content["options"]["local_benchmark"],
            tx_ab_method_content=guided_content["options"]["tx_ab_method"],
            help_overrides={
                "reference_callsign": messages["reference_callsign_help"],
                "reference_qth": messages["reference_grid4_help"],
                "local_benchmark": messages["local_benchmark_help"],
                "local_radius": messages["local_radius_help"],
                "tx_ab_method": messages["tx_ab_method_help"],
            },
        )


def _render_offset_calibration_fields(t, guided_content):
    """Render correction intent, formula, live sign consequence, and guidance."""
    options = guided_content["options"]["offset_intent"]
    messages = guided_content["messages"]
    benchmark_mode = st.session_state.get("val_comp_mode")
    if benchmark_mode == "hardware_ab":
        st.info(messages["hardware_calibration"])
    else:
        st.info(messages["reference_calibration"])
    st.markdown(messages["correction_formula"])
    st.radio(
        guided_content["steps"]["offset_calibration"]["title"],
        tuple(options),
        key="val_snr_correction_mode",
        label_visibility="collapsed",
        format_func=lambda value: options[value]["label"],
        captions=tuple(option["description"] for option in options.values()),
        on_change=_handle_offset_intent_change,
        width="stretch",
    )
    intent = st.session_state.get("val_snr_correction_mode")
    if intent == "established_offset":
        render_reference_correction_field(
            t,
            on_change=_guided_experiment_definition_change,
            on_change_args=("offset_calibration",),
        )
    correction_db = float(st.session_state.get("val_benchmark_offset_db", 0.0))
    if correction_db != 0.0:
        st.success(messages["correction_consequence"].format(offset=correction_db))
    if intent == "establish_offset":
        guidance_key = (
            "establish_hardware_guidance"
            if benchmark_mode == "hardware_ab"
            else "establish_reference_guidance"
        )
        st.warning(messages["calibration_run_notice"])
        st.markdown(messages[guidance_key])


def _render_scope_and_evidence_fields(t, guided_content):
    """Always render the grouped population, scope, and evidence controls."""
    messages = guided_content["messages"]
    st.markdown(f"**{messages['station_population_title']}**")
    st.caption(messages["station_population_body"])
    render_station_population_fields(
        t,
        on_change=_guided_scientific_change,
        on_change_args=("scope_and_evidence",),
    )
    st.markdown(f"**{messages['analysis_scope_title']}**")
    st.caption(messages["analysis_scope_body"])
    render_scope_fields(
        t,
        on_change=_guided_scientific_change,
        on_change_args=("scope_and_evidence",),
        use_two_column_layout=True,
    )
    st.markdown(f"**{messages['evidence_requirements_title']}**")
    evidence_requirements_key = (
        "success_evidence_requirements_body"
        if st.session_state.get("val_comp_mode") == "none"
        else "compare_evidence_requirements_body"
    )
    st.caption(messages[evidence_requirements_key])
    render_evidence_threshold_fields(
        t,
        result_type=(
            "performance"
            if st.session_state.get("val_comp_mode") == "none"
            else "benchmark"
        ),
        on_change=_guided_scientific_change,
        on_change_args=("scope_and_evidence",),
        use_two_column_layout=True,
    )
    if st.session_state.get("val_comp_mode") != "none":
        render_delta_snr_outlier_reporting_field(
            t,
            on_change=_guided_scientific_change,
            on_change_args=("scope_and_evidence",),
        )


def _reference_review_value(guided_content) -> str:
    """Retain the Guided adapter over the shared Reference summary."""
    return reference_review_value(st.session_state, guided_content)


def _render_review_and_run(t, guided_content):
    """Render the Guided terminal review through the shared review component."""
    return render_configuration_review(
        st,
        t,
        guided_content,
        st.session_state,
        on_open_classic=_open_classic_view,
    )


CONTROL_RENDERERS = {
    "use_case_selector": _render_use_case_selector,
    "target_and_window_fields": _render_target_and_window_fields,
    "reference_design_fields": _render_reference_design_fields,
    "offset_calibration_fields": _render_offset_calibration_fields,
    "scope_and_evidence_fields": _render_scope_and_evidence_fields,
    "review_and_run": _render_review_and_run,
}


def _render_demo_metadata(
    guided_content,
    *,
    walkthrough_node: str,
    review_node: str,
) -> None:
    """Render one first-position demo context panel without duplicating metadata."""
    profile_key = st.session_state.get("guided_loaded_demo_profile")
    profile = st.session_state.get("loaded_config_profile")
    if not profile_key or not isinstance(profile, dict):
        return
    language = st.session_state.get("lang", "en")
    messages = guided_content["messages"]
    expanded = bool(st.session_state.get("guided_demo_metadata_open", False))
    with st.expander(messages["demo_title"], expanded=expanded, icon=":material/route:"):
        with st.container(key="guided_demo_context"):
            title = _resolve_loaded_profile_text(profile, "title", language)
            description = _resolve_loaded_profile_text(profile, "description", language)
            if title:
                st.markdown(_prepare_loaded_profile_title_markdown(title))
            if description:
                st.caption(prepare_demo_description_markdown(description))
            st.info(messages["demo_preset"])
            st.caption(messages["demo_walkthrough_help"])
            st.button(
                messages["demo_walkthrough"],
                key="guided_demo_walkthrough",
                type="primary",
                on_click=_open_demo_node,
                args=(walkthrough_node,),
                width="stretch",
            )
            st.caption(messages["demo_skip_to_review_help"])
            st.button(
                messages["demo_skip_to_review"],
                key="guided_demo_skip_to_review",
                type="primary",
                on_click=_open_demo_node,
                args=(review_node,),
                width="stretch",
            )


def render_guided_inputs(t) -> GuidedRenderResult:
    """Render the validated question-led accordion over canonical session state."""
    language = st.session_state.get("lang", "en")
    guided_content = GUIDED_INPUTS[language]
    try:
        flow = load_guided_input_flow()
    except GuidedFlowError as exc:
        st.error(
            guided_content["validation"]["flow_invalid"].format(error=exc)
        )
        return GuidedRenderResult((), False, None)

    if set(CONTROL_RENDERERS) != set(CONTROL_RENDERER_NAMES):
        raise GuidedFlowError("Guided Input control registry does not match the flow whitelist.")

    if st.session_state.get("guided_reconstruct_requested", False):
        reconstruct_guided_transients(
            st.session_state,
            has_loaded_demo=_loaded_demo_scope_matches_current_state(),
        )
        st.session_state.guided_reconstruct_requested = False
        st.session_state.guided_active_node = flow["terminal_node"]

    facts = guided_facts(st.session_state)
    available_nodes = available_flow_nodes(
        flow,
        facts,
        lambda node_id: is_guided_node_complete(node_id, st.session_state),
    )
    _render_demo_metadata(
        guided_content,
        walkthrough_node=available_nodes[0],
        review_node=flow["terminal_node"],
    )
    first_incomplete = next(
        (
            node_id
            for node_id in available_nodes
            if not is_guided_node_complete(node_id, st.session_state)
        ),
        None,
    )
    active_node = st.session_state.get("guided_active_node")
    if active_node not in available_nodes:
        active_node = first_incomplete or available_nodes[-1]
        st.session_state.guided_active_node = active_node

    force_collapsed = bool(
        st.session_state.get("guided_collapse_all", False)
        or st.session_state.get("guided_demo_metadata_open", False)
    )
    is_ready = bool(
        available_nodes
        and available_nodes[-1] == flow["terminal_node"]
        and all(
            is_guided_node_complete(node_id, st.session_state)
            for node_id in available_nodes[:-1]
        )
    )
    should_expand_stale_review = bool(
        is_ready
        and st.session_state.get("configuration_changed_since_run", False)
    )
    review_actions_slot = None
    for node_id in available_nodes:
        node = flow["nodes"][node_id]
        step_number = flow["node_order"].index(node_id) + 1
        is_complete = is_guided_node_complete(node_id, st.session_state)
        content = resolve_content_key(guided_content, node["content_key"])
        if is_complete:
            summary_renderer = SUMMARY_RENDERERS[node["summary_renderer"]]
            expander_label = summary_renderer(
                st.session_state,
                guided_content,
                step_number,
                language,
            )
        else:
            expander_label = f"{step_number} · {content['title']}"
        with st.expander(
            expander_label,
            expanded=(
                (
                    node_id == flow["terminal_node"]
                    and is_ready
                )
                or (
                    not force_collapsed
                    and (
                        active_node == node_id
                        or (
                            node_id == flow["terminal_node"]
                            and should_expand_stale_review
                        )
                    )
                )
            ),
            icon=":material/route:",
        ):
            st.markdown(content["body_md"], unsafe_allow_html=True)
            renderer_result = CONTROL_RENDERERS[node["renderer"]](
                t,
                guided_content,
            )
            if node_id == flow["terminal_node"]:
                review_actions_slot = renderer_result
            elif active_node == node_id and not is_complete:
                st.warning(guided_content["validation"][node_id])

        if (
            node_id != flow["terminal_node"]
            and is_complete
            and active_node == node_id
            and not force_collapsed
        ):
            next_node = matching_next_node(node, guided_facts(st.session_state))
            if next_node is not None:
                st.button(
                    guided_content["messages"]["continue"],
                    key=f"guided_continue_{node_id}",
                    type="primary",
                    on_click=_continue_to,
                    args=(next_node,),
                    width="stretch",
                )

    return GuidedRenderResult(available_nodes, is_ready, review_actions_slot)
