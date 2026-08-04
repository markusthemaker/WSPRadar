"""Shared transient analysis-question transitions for both input editors."""

from collections.abc import Mapping, MutableMapping

from ui.population_exclusion_state import (
    BENCHMARK_RESULT_TYPE,
    PERFORMANCE_RESULT_TYPE,
    transition_population_exclusion_result_type,
)


ANALYSIS_QUESTION_CHOICES = (
    "rx_performance",
    "tx_performance",
    "rx_benchmark",
    "tx_benchmark",
)
BENCHMARK_MODES = frozenset(
    {"hardware_ab", "reference_station", "local_neighborhood"}
)
_LEGACY_ANALYSIS_QUESTION_ALIASES = {
    "rx_success": "rx_performance",
    "tx_success": "tx_performance",
    "rx_compare": "rx_benchmark",
    "tx_compare": "tx_benchmark",
}


def canonicalize_analysis_question(question: object) -> object:
    """Normalize one bounded legacy question token without guessing intent."""
    return _LEGACY_ANALYSIS_QUESTION_ALIASES.get(question, question)


def analysis_question_result_type(question: object) -> str:
    """Return the visible result family encoded by one valid question token."""
    canonical_question = canonicalize_analysis_question(question)
    if canonical_question not in ANALYSIS_QUESTION_CHOICES:
        raise ValueError(f"Unsupported analysis question {question!r}.")
    return str(canonical_question).split("_", 1)[1]


def derive_analysis_question(state: Mapping) -> str | None:
    """Derive a complete question from canonical direction and design state."""
    analysis_direction = state.get("val_analysis_direction")
    if analysis_direction not in {"rx", "tx"}:
        return None
    comparison_mode = state.get("val_comp_mode", "none")
    if comparison_mode == "none":
        result_type = PERFORMANCE_RESULT_TYPE
    elif comparison_mode in BENCHMARK_MODES:
        result_type = BENCHMARK_RESULT_TYPE
    else:
        return None
    return f"{analysis_direction}_{result_type}"


def apply_analysis_question_choice(
    state: MutableMapping,
    question: object,
) -> str:
    """Apply RX/TX and Performance/Benchmark intent as one atomic UI change.

    The question is transient presentation state. This function updates the
    existing canonical configuration fields and shared retained Benchmark-design
    transients without creating a second scientific configuration. A first
    Benchmark choice may intentionally
    leave ``val_comp_mode`` as ``none`` until the operator chooses a design;
    callers must therefore use the returned question when determining UI
    readiness instead of interpreting that temporary value as Performance.
    """
    canonical_question = canonicalize_analysis_question(question)
    if canonical_question not in ANALYSIS_QUESTION_CHOICES:
        raise ValueError(f"Unsupported analysis question {question!r}.")

    analysis_direction, result_type = str(canonical_question).split("_", 1)
    previous_direction = state.get("val_analysis_direction")
    did_change_direction = (
        previous_direction in {"rx", "tx"}
        and previous_direction != analysis_direction
    )

    active_or_retained_design = state.get("val_comp_mode")
    if active_or_retained_design not in BENCHMARK_MODES:
        active_or_retained_design = state.get("guided_reference_design")
    if active_or_retained_design not in BENCHMARK_MODES:
        active_or_retained_design = state.get("guided_last_benchmark_mode")

    if did_change_direction and active_or_retained_design == "hardware_ab":
        # RX Hardware A/B identities and TX schedule semantics are not
        # interchangeable. Keep Benchmark intent but require a fresh design.
        state["val_comp_mode"] = "none"
        state["guided_reference_design"] = None
        state["guided_last_benchmark_mode"] = None
        state["val_benchmark_offset_db"] = 0.0
        state["val_snr_correction_mode"] = "no_offset"
        state["val_tx_ab_method"] = "simultaneous"
        state["val_tx_ab_repeat_interval_minutes"] = 10
        state["val_tx_ab_target_start_minute"] = 0
        state["val_tx_ab_reference_start_minute"] = 2
    elif did_change_direction and active_or_retained_design in {
        "reference_station",
        "local_neighborhood",
    }:
        # These designs remain structurally valid in either direction, but a
        # correction established for one direction is not valid for the other.
        state["val_benchmark_offset_db"] = 0.0
        state["val_snr_correction_mode"] = "no_offset"

    state["val_analysis_direction"] = analysis_direction
    if result_type == PERFORMANCE_RESULT_TYPE:
        active_design = state.get("val_comp_mode")
        if active_design in BENCHMARK_MODES:
            state["guided_last_benchmark_mode"] = active_design
        state["val_comp_mode"] = "none"
        state["guided_reference_design"] = None
    else:
        retained_design = state.get("val_comp_mode")
        if retained_design not in BENCHMARK_MODES:
            retained_design = state.get("guided_reference_design")
        if retained_design not in BENCHMARK_MODES:
            retained_design = state.get("guided_last_benchmark_mode")
        if retained_design in BENCHMARK_MODES:
            state["val_comp_mode"] = retained_design
            state["guided_reference_design"] = retained_design
        else:
            state["val_comp_mode"] = "none"
            state["guided_reference_design"] = None

    transition_population_exclusion_result_type(state, result_type)
    return str(canonical_question)
