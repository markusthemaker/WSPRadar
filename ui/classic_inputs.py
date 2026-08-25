"""Composition of the compact, question-first Classic input editor."""

from dataclasses import dataclass
from typing import Any

import streamlit as st

from i18n import GUIDED_INPUTS
from ui.classic_input_state import (
    classic_result_type,
    initialize_classic_input_state,
    is_classic_input_ready,
)
from ui.components.config_panel import (
    render_advanced_expander,
    render_benchmark_expander,
    render_classic_question_expander,
    render_core_expander,
)
from ui.components.config_review import (
    is_canonical_configuration_ready,
    render_configuration_review,
)


@dataclass(frozen=True)
class ClassicRenderResult:
    """Describe Classic result intent and action/serialization readiness."""

    result_type: str | None
    is_ready: bool
    review_actions_slot: Any


def _is_classic_review_ready(result_type: str | None) -> bool:
    """Require every active canonical field before claiming run readiness."""
    return bool(
        result_type in {"performance", "benchmark"}
        and is_classic_input_ready(st.session_state)
        and is_canonical_configuration_ready(st.session_state)
    )


def render_classic_inputs(t) -> ClassicRenderResult:
    """Render ordered Classic panels over the canonical shared configuration."""
    initialize_classic_input_state(st.session_state)
    st.session_state.config_panels_expanded = True
    st.session_state._collapse_config_panels_once = False
    render_classic_question_expander(t, step_number=1)
    render_core_expander(t, step_number=2)

    result_type = classic_result_type(st.session_state)
    if result_type == "benchmark":
        render_benchmark_expander(t, step_number=3)
        advanced_step_number = 4
    else:
        advanced_step_number = 3
    render_advanced_expander(
        t,
        result_type=result_type or "performance",
        step_number=advanced_step_number,
    )
    review_step_number = advanced_step_number + 1
    is_ready = _is_classic_review_ready(result_type)
    guided_content = GUIDED_INPUTS[st.session_state.get("lang", "en")]
    review_heading = (
        guided_content["summaries"]["review_ready"].format(
            step=review_step_number
        )
        if is_ready
        else f"{review_step_number} · {guided_content['steps']['review_and_run']['title']}"
    )
    with st.expander(
        review_heading,
        expanded=True,
        icon=":material/route:",
    ):
        st.markdown(
            guided_content["steps"]["review_and_run"]["body_md"],
            unsafe_allow_html=True,
        )
        if is_ready:
            review_actions_slot = render_configuration_review(
                st,
                t,
                guided_content,
                st.session_state,
            )
        else:
            st.info(guided_content["validation"]["review_and_run"])
            review_actions_slot = st.empty()
    return ClassicRenderResult(
        result_type=result_type,
        is_ready=is_ready,
        review_actions_slot=review_actions_slot,
    )
