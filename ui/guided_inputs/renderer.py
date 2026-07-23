"""Streamlit composition for the bilingual Guided Input accordion."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import streamlit as st

from config import DEMO_PROFILES
from config.demo_profiles import prepare_demo_description_markdown
from i18n import GUIDED_INPUTS, T
from ui.callbacks import reset_audit
from ui.components.config_fields import (
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
from ui.config_io import SOLAR_KEYS, validate_config_document
from ui.page_navigation import (
    PARAMETER_SETTINGS_ANCHOR_ID,
    request_page_navigation,
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
    GUIDED_SCOPE_MODES,
    GUIDED_USE_CASES,
    apply_general_scope_defaults,
    guided_facts,
    is_guided_node_complete,
    reconstruct_guided_transients,
)
from .summaries import SUMMARY_RENDERERS, _window_summary


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
    """Invalidate stale results while retaining the edited accordion panel."""
    _activate_step(node_id)
    reset_audit()


def _guided_correction_context_change(node_id: str) -> None:
    """Invalidate any established offset whose scientific context was edited."""
    active_mode = st.session_state.get("val_comp_mode")
    retained_mode = st.session_state.get("guided_last_compare_mode")
    if active_mode in COMPARISON_MODES or retained_mode in COMPARISON_MODES:
        st.session_state.val_benchmark_offset_db = 0.0
        st.session_state.guided_offset_intent = "no_offset"
    _guided_scientific_change(node_id)


def _handle_use_case_change() -> None:
    """Map one transient question token atomically into canonical direction/design."""
    use_case = st.session_state.get("guided_use_case")
    if use_case not in GUIDED_USE_CASES:
        return
    analysis_direction, result_type = use_case.split("_", 1)
    previous_direction = st.session_state.get("val_analysis_direction")
    did_change_direction = (
        previous_direction in {"rx", "tx"}
        and previous_direction != analysis_direction
    )
    active_or_retained_design = st.session_state.get("val_comp_mode")
    if active_or_retained_design not in COMPARISON_MODES:
        active_or_retained_design = st.session_state.get(
            "guided_reference_design"
        )
    if active_or_retained_design not in COMPARISON_MODES:
        active_or_retained_design = st.session_state.get(
            "guided_last_compare_mode"
        )
    if (
        did_change_direction
        and active_or_retained_design == "hardware_ab"
    ):
        # RX and TX Hardware A/B have different identity/schedule semantics.
        # Match the Classic editor by requiring the operator to choose that
        # design again after changing direction, while retaining harmless
        # downstream values for possible reuse.
        st.session_state.val_comp_mode = "none"
        st.session_state.guided_reference_design = None
        st.session_state.guided_last_compare_mode = None
        st.session_state.val_benchmark_offset_db = 0.0
        st.session_state.guided_offset_intent = "no_offset"
        st.session_state.val_tx_ab_method = "simultaneous"
        st.session_state.val_tx_ab_repeat_interval_minutes = 10
        st.session_state.val_tx_ab_target_start_minute = 0
        st.session_state.val_tx_ab_reference_start_minute = 2
    elif did_change_direction and active_or_retained_design in {
        "reference_station",
        "local_neighborhood",
    }:
        # RX and TX compare different sides of a station pair or neighborhood.
        # A correction established for one direction is not an established
        # baseline for the other, even when the identities/scope remain useful.
        st.session_state.val_benchmark_offset_db = 0.0
        st.session_state.guided_offset_intent = "no_offset"
    st.session_state.val_analysis_direction = analysis_direction
    if result_type == "success":
        current_mode = st.session_state.get("val_comp_mode")
        if current_mode in COMPARISON_MODES:
            st.session_state.guided_last_compare_mode = current_mode
        st.session_state.val_comp_mode = "none"
        st.session_state.guided_reference_design = None
    else:
        retained_mode = st.session_state.get("guided_reference_design")
        if retained_mode not in COMPARISON_MODES:
            retained_mode = st.session_state.get("guided_last_compare_mode")
        if retained_mode in COMPARISON_MODES:
            st.session_state.val_comp_mode = retained_mode
            st.session_state.guided_reference_design = retained_mode
        else:
            # Compare intent is intentionally incomplete until Step 3; do not
            # silently choose a scientific Reference design for the operator.
            st.session_state.val_comp_mode = "none"
            st.session_state.guided_reference_design = None
    _guided_scientific_change("use_case")


def _handle_reference_design_change() -> None:
    """Apply the selected design and clear only values invalid in the new branch."""
    new_mode = st.session_state.get("guided_reference_design")
    if new_mode not in COMPARISON_MODES:
        return
    previous_mode = st.session_state.get("val_comp_mode")
    st.session_state.val_comp_mode = new_mode
    st.session_state.guided_last_compare_mode = new_mode
    if new_mode != previous_mode:
        # Fixed-Reference identities and corrections have design-specific
        # meanings. Reinterpreting a remote station as a co-located path (or a
        # local path alias as a remote station) would silently create a complete
        # but invalid experiment, so require explicit identity confirmation.
        st.session_state.val_ref_callsign = ""
        st.session_state.val_ref_qth = ""
        st.session_state.val_benchmark_offset_db = 0.0
        st.session_state.guided_offset_intent = "no_offset"
    if new_mode == "local_neighborhood":
        st.session_state.val_ref_callsign = ""
        st.session_state.val_ref_qth = ""
        st.session_state.val_benchmark_offset_db = 0.0
        st.session_state.guided_offset_intent = "no_offset"
    _guided_scientific_change("reference_design")


def _handle_offset_intent_change() -> None:
    """Keep no-offset and calibration runs pinned to the canonical 0.0 dB value."""
    intent = st.session_state.get("guided_offset_intent")
    if intent not in GUIDED_OFFSET_INTENTS:
        return
    if intent in {"no_offset", "establish_offset"}:
        st.session_state.val_benchmark_offset_db = 0.0
    _guided_scientific_change("offset_calibration")


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


def _apply_loaded_demo_scope() -> None:
    """Restore only advanced values from the loaded built-in demo profile."""
    scope_values = _loaded_demo_scope_values(
        st.session_state.get("guided_loaded_demo_profile")
    )
    if scope_values:
        st.session_state.update(scope_values)


def _handle_scope_mode_change() -> None:
    """Apply an explicit preset once; Custom leaves every current value intact."""
    scope_mode = st.session_state.get("guided_scope_mode")
    if scope_mode not in GUIDED_SCOPE_MODES:
        return
    if scope_mode == "general":
        apply_general_scope_defaults(st.session_state)
    elif scope_mode == "demo":
        _apply_loaded_demo_scope()
    _guided_scientific_change("scope_and_evidence")


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
    """Switch editors without touching the shared scientific configuration."""
    st.session_state.input_view = "classic"


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
        on_change=_guided_scientific_change,
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
        key="guided_offset_intent",
        label_visibility="collapsed",
        format_func=lambda value: options[value]["label"],
        captions=tuple(option["description"] for option in options.values()),
        on_change=_handle_offset_intent_change,
        width="stretch",
    )
    intent = st.session_state.get("guided_offset_intent")
    if intent == "established_offset":
        render_reference_correction_field(
            t,
            on_change=_guided_scientific_change,
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


def _evidence_value_summary(guided_content) -> str:
    """Return the localized thresholds active for the selected result type."""
    messages = guided_content["messages"]
    is_compare = st.session_state.get("val_comp_mode") != "none"
    return messages[
        "compare_evidence" if is_compare else "success_evidence"
    ].format(
        value=(
            st.session_state.get("val_min_spots", 1)
            if is_compare
            else st.session_state.get("val_min_opportunities", 5)
        ),
        stations=st.session_state.get("val_min_stations", 1),
    )


def _render_scope_and_evidence_fields(t, guided_content):
    """Render the scope preset choice or the relevant grouped shared controls."""
    options = dict(guided_content["options"]["scope_mode"])
    messages = guided_content["messages"]
    if not st.session_state.get("guided_loaded_demo_profile"):
        options.pop("demo", None)
        if st.session_state.get("guided_scope_mode") == "demo":
            st.session_state.guided_scope_mode = "custom"
    st.radio(
        guided_content["steps"]["scope_and_evidence"]["title"],
        tuple(options),
        key="guided_scope_mode",
        label_visibility="collapsed",
        format_func=lambda value: options[value]["label"],
        on_change=_handle_scope_mode_change,
    )
    scope_mode = st.session_state.get("guided_scope_mode")
    if scope_mode in {"general", "demo"}:
        st.info(messages["general_active" if scope_mode == "general" else "demo_active"])
        return

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
            "success" if st.session_state.get("val_comp_mode") == "none" else "compare"
        ),
        on_change=_guided_scientific_change,
        on_change_args=("scope_and_evidence",),
        use_two_column_layout=True,
    )


def _reference_review_value(guided_content) -> str:
    """Return one human-readable active Reference value for terminal review."""
    options = guided_content["options"]
    benchmark_mode = st.session_state.get("val_comp_mode")
    if benchmark_mode == "reference_station":
        return (
            f"{st.session_state.get('val_ref_callsign', '').upper()} · "
            f"{st.session_state.get('val_ref_qth', '').upper()} · "
            f"{options['reference_design'][benchmark_mode]['label']}"
        )
    if benchmark_mode == "local_neighborhood":
        local_method = st.session_state.get("val_local_benchmark", "local_median")
        return (
            f"{options['local_benchmark'][local_method]['label']} · "
            f"{st.session_state.get('val_ref_radius_km', 100)} km"
        )
    if (
        st.session_state.get("val_analysis_direction") == "tx"
        and st.session_state.get("val_tx_ab_method") == "sequential"
    ):
        return guided_content["messages"]["review_tx_sequential_value"].format(
            method=options["tx_ab_method"]["sequential"]["label"],
            repeat=st.session_state.get("val_tx_ab_repeat_interval_minutes", 10),
            target=int(st.session_state.get("val_tx_ab_target_start_minute", 0)),
            reference=int(
                st.session_state.get("val_tx_ab_reference_start_minute", 2)
            ),
        )
    if st.session_state.get("val_analysis_direction") == "tx":
        return guided_content["messages"]["review_tx_simultaneous_value"].format(
            callsign=st.session_state.get("val_ref_callsign", "").upper(),
            method=options["tx_ab_method"]["simultaneous"]["label"],
        )
    return (
        f"{st.session_state.get('val_ref_callsign', '').upper()} · "
        f"{options['reference_design']['hardware_ab']['label']}"
    )


def _render_review_and_run(t, guided_content):
    """Render the complete active-only configuration summary and action placeholder."""
    messages = guided_content["messages"]
    use_case = st.session_state.get("guided_use_case")
    is_compare = use_case in {"rx_compare", "tx_compare"}
    lines = [
        f"- **{messages['review_question']}:** {guided_content['options']['use_cases'][use_case]['label']}",
        f"- **{messages['review_target']}:** "
        + messages["review_target_value"].format(
            callsign=st.session_state.get("val_callsign", "").upper(),
            qth=st.session_state.get("val_qth", "").upper(),
        ),
    ]
    if is_compare:
        lines.append(
            f"- **{messages['review_reference']}:** {_reference_review_value(guided_content)}"
        )
    lines.append(
        f"- **{messages['review_band_window']}:** {st.session_state.get('val_band')} · {_window_summary(st.session_state, guided_content)}"
    )
    if is_compare and (
        st.session_state.get("val_comp_mode") != "local_neighborhood"
        or float(st.session_state.get("val_benchmark_offset_db", 0.0)) != 0.0
    ):
        lines.append(
            f"- **{messages['review_correction']}:** {float(st.session_state.get('val_benchmark_offset_db', 0.0)):+.1f} dB"
        )
    lines.extend(
        [
            f"- **{messages['review_population']}:** "
            + messages["review_population_value"].format(
                special=(
                    messages["included"]
                    if st.session_state.get("val_exclude_special_callsigns")
                    else messages["not_included"]
                ),
                moving=(
                    messages["included"]
                    if st.session_state.get("val_filter_moving")
                    else messages["not_included"]
                ),
            ),
            f"- **{messages['review_scope']}:** {st.session_state.get('val_max_peer_distance_km', 22000)} km · {t[SOLAR_KEYS.get(st.session_state.get('val_solar'), 'opt_solar_all')]}",
            f"- **{messages['review_evidence']}:** {_evidence_value_summary(guided_content)}",
            f"- **{messages['review_result']}:** {messages['result_compare' if is_compare else 'result_success']}",
        ]
    )
    st.markdown("\n".join(lines))
    if st.session_state.get("guided_offset_intent") == "establish_offset":
        st.warning(messages["calibration_run_notice"])
    st.button(
        messages["open_classic"],
        icon=":material/settings:",
        key="guided_open_classic",
        on_click=_open_classic_view,
        width="stretch",
    )
    return st.empty()


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
                not force_collapsed
                and (
                    active_node == node_id
                    or (
                        node_id == flow["terminal_node"]
                        and should_expand_stale_review
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
