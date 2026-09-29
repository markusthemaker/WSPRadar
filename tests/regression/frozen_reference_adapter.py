"""Explicit test-only projection of immutable, pre-1.0 scientific fixtures.

Frozen input bytes, source reports and numerical expectations remain untouched.
This adapter is not an application configuration import/migration path.
"""

from copy import deepcopy

from ui.config_io import validate_config_document


RETIRED_CONTEXT_FIELDS = {
    "self_test_mode", "tx_ab_method", "tx_ab_repeat_interval_minutes",
    "tx_ab_target_start_minute", "tx_ab_reference_start_minute",
}


def frozen_context_projection(values):
    projected = deepcopy(values)
    assert projected.get("tx_ab_method", "simultaneous") == "simultaneous"
    for key in RETIRED_CONTEXT_FIELDS:
        projected.pop(key, None)
    if projected.get("comparison_mode") == "hardware_ab":
        projected["comparison_mode"] = "reference_station"
        projected["reference_qth"] = projected["qth"][:4]
    return projected


def frozen_document_projection(document):
    projected = deepcopy(document)
    comparison = projected["settings"]["comparison_parameters"]
    assert comparison.get("tx_ab_method", "simultaneous") == "simultaneous"
    for key in RETIRED_CONTEXT_FIELDS:
        comparison.pop(key, None)
    if comparison.get("mode") == "hardware_ab":
        comparison["mode"] = "reference_station"
        comparison["reference_qth"] = projected["settings"]["core_parameters"]["qth"][:4]
    return projected


def validate_frozen_reference_document(document):
    return validate_config_document(frozen_document_projection(document))
