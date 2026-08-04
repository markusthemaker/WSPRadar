"""Transient question and readiness state for the Classic input editor."""

from collections.abc import Mapping, MutableMapping

from ui.analysis_question_state import (
    ANALYSIS_QUESTION_CHOICES,
    BENCHMARK_MODES,
    analysis_question_result_type,
    canonicalize_analysis_question,
    derive_analysis_question,
)


CLASSIC_QUESTION_KEY = "classic_question"
CLASSIC_BENCHMARK_DESIGN_WIDGET_KEY = "_classic_benchmark_design"


def _question_matches_canonical_direction(
    question: object,
    state: Mapping,
) -> bool:
    """Return whether one valid question agrees with canonical direction."""
    if question not in ANALYSIS_QUESTION_CHOICES:
        return False
    return str(question).split("_", 1)[0] == state.get(
        "val_analysis_direction"
    )


def synchronize_classic_input_state(
    state: MutableMapping,
    *,
    preferred_question: object = None,
) -> str | None:
    """Replace Classic transients from explicit editor intent or canonical state.

    ``preferred_question`` is used when moving from Guided Input because a
    Benchmark question can be valid before a canonical design exists. Loaded
    configurations omit that argument so their complete canonical branch always
    replaces any stale transient Classic question.
    """
    canonical_preference = canonicalize_analysis_question(preferred_question)
    comparison_mode = state.get("val_comp_mode", "none")
    if (
        _question_matches_canonical_direction(canonical_preference, state)
        and (
            comparison_mode == "none"
            or analysis_question_result_type(canonical_preference) == "benchmark"
        )
    ):
        question = str(canonical_preference)
    else:
        question = derive_analysis_question(state)

    state[CLASSIC_QUESTION_KEY] = question
    if comparison_mode in BENCHMARK_MODES:
        state["guided_reference_design"] = comparison_mode
        state["guided_last_benchmark_mode"] = comparison_mode
    else:
        state["guided_reference_design"] = None
    state.pop(CLASSIC_BENCHMARK_DESIGN_WIDGET_KEY, None)
    return question


def initialize_classic_input_state(state: MutableMapping) -> None:
    """Initialize Classic intent while preserving a valid incomplete question."""
    question = canonicalize_analysis_question(state.get(CLASSIC_QUESTION_KEY))
    comparison_mode = state.get("val_comp_mode", "none")
    is_compatible = (
        _question_matches_canonical_direction(question, state)
        and not (
            analysis_question_result_type(question) == "performance"
            and comparison_mode != "none"
        )
    )
    if is_compatible:
        state[CLASSIC_QUESTION_KEY] = question
        return
    synchronize_classic_input_state(
        state,
        preferred_question=state.get("guided_use_case"),
    )


def classic_result_type(state: Mapping) -> str | None:
    """Return the result family selected in Classic, including pending Benchmark."""
    question = canonicalize_analysis_question(state.get(CLASSIC_QUESTION_KEY))
    if question not in ANALYSIS_QUESTION_CHOICES:
        return None
    return analysis_question_result_type(question)


def is_classic_input_ready(state: Mapping) -> bool:
    """Return whether Classic represents one complete serializable analysis."""
    question = canonicalize_analysis_question(state.get(CLASSIC_QUESTION_KEY))
    if not _question_matches_canonical_direction(question, state):
        return False
    result_type = analysis_question_result_type(question)
    comparison_mode = state.get("val_comp_mode")
    if result_type == "performance":
        return comparison_mode == "none"
    return comparison_mode in BENCHMARK_MODES
