"""Composition of the compact, question-first Classic input editor."""

from dataclasses import dataclass

import streamlit as st

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


@dataclass(frozen=True)
class ClassicRenderResult:
    """Describe Classic result intent and action/serialization readiness."""

    result_type: str | None
    is_ready: bool


def render_classic_inputs(t) -> ClassicRenderResult:
    """Render ordered Classic panels over the canonical shared configuration."""
    initialize_classic_input_state(st.session_state)
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
    return ClassicRenderResult(
        result_type=result_type,
        is_ready=is_classic_input_ready(st.session_state),
    )
