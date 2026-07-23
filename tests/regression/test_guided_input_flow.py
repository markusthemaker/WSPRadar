"""Contracts for the declarative, bilingual Guided Input workflow."""

from __future__ import annotations

from datetime import date, time, timedelta
import json
from pathlib import Path
from string import Formatter

import pytest
from jsonschema import Draft202012Validator, ValidationError

from i18n import GUIDED_INPUTS
from ui.guided_inputs.flow_engine import (
    available_flow_nodes,
    evaluate_condition,
    matching_next_node,
    resolve_flow_path,
)
from ui.guided_inputs.flow_loader import (
    CONTROL_RENDERER_NAMES,
    FLOW_PATH,
    FLOW_SCHEMA_PATH,
    SUMMARY_RENDERER_NAMES,
    GuidedFlowError,
    load_guided_input_flow,
    resolve_content_key,
    validate_guided_input_flow,
)
from ui.guided_inputs.renderer import CONTROL_RENDERERS
from ui.guided_inputs.state import (
    apply_general_scope_defaults,
    derive_guided_use_case,
    guided_facts,
    is_guided_node_complete,
    reconstruct_guided_transients,
    scope_matches_general_defaults,
)
from ui.guided_inputs.summaries import SUMMARY_RENDERERS, _window_summary


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_NODE_ORDER = [
    "use_case",
    "target_and_window",
    "reference_design",
    "offset_calibration",
    "scope_and_evidence",
    "review_and_run",
]


def _read_json(path: Path):
    """Return one repository JSON document as decoded UTF-8."""
    return json.loads(path.read_text(encoding="utf-8"))


def _flow_and_schema():
    """Return independent copies of the bundled flow and its formal schema."""
    return _read_json(FLOW_PATH), _read_json(FLOW_SCHEMA_PATH)


def _flatten_strings(value, path=()):
    """Yield dotted leaf paths and strings from one nested localization tree."""
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _flatten_strings(child, (*path, key))
        return
    yield ".".join(path), value


def _placeholder_names(value: str) -> set[str]:
    """Return the named ``str.format`` fields used by one localized string."""
    return {
        field_name
        for _, field_name, _, _ in Formatter().parse(value)
        if field_name is not None
    }


def _complete_state(**overrides):
    """Return one valid RX Hardware A/B Guided Input state."""
    state = {
        "guided_use_case": "rx_compare",
        "val_analysis_direction": "rx",
        "val_callsign": "DL1MKS",
        "val_qth": "JN37AA",
        "val_band": "20m",
        "val_time_mode": "last_x",
        "val_hours": 24,
        "val_start_d": date(2026, 7, 1),
        "val_end_d": date(2026, 7, 2),
        "val_start_t": time(0, 0),
        "val_end_t": time(0, 0),
        "val_comp_mode": "hardware_ab",
        "guided_reference_design": "hardware_ab",
        "val_ref_callsign": "DL1MKS/P",
        "val_ref_qth": "JO62",
        "val_local_benchmark": "local_median",
        "val_ref_radius_km": 100,
        "val_tx_ab_method": "simultaneous",
        "val_tx_ab_repeat_interval_minutes": 10,
        "val_tx_ab_target_start_minute": 0,
        "val_tx_ab_reference_start_minute": 2,
        "guided_offset_intent": "no_offset",
        "val_benchmark_offset_db": 0.0,
        "guided_scope_mode": "general",
        "val_solar": "all",
        "val_max_peer_distance_km": 22000,
        "val_exclude_special_callsigns": False,
        "val_filter_moving": False,
        "val_min_spots": 1,
        "val_min_opportunities": 5,
        "val_min_stations": 1,
    }
    state.update(overrides)
    return state


def test_bundled_flow_and_schema_validate_formally_and_through_loader(
    monkeypatch,
    tmp_path,
):
    """Keep the checked schema, flow document, and CWD-independent loader aligned."""
    flow, schema = _flow_and_schema()

    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(flow)
    assert validate_guided_input_flow(flow, schema) is flow
    assert flow["node_order"] == EXPECTED_NODE_ORDER
    assert flow["start_node"] == "use_case"
    assert flow["terminal_node"] == "review_and_run"

    load_guided_input_flow.cache_clear()
    monkeypatch.chdir(tmp_path)
    try:
        loaded_flow = load_guided_input_flow()
    finally:
        load_guided_input_flow.cache_clear()
    assert loaded_flow["node_order"] == EXPECTED_NODE_ORDER
    assert FLOW_PATH == REPOSITORY_ROOT / "config" / "guided_input_flow.json"
    assert FLOW_SCHEMA_PATH == (
        REPOSITORY_ROOT / "config" / "guided_input_flow.schema.json"
    )


@pytest.mark.parametrize(
    ("mutation", "error_pattern"),
    [
        (
            lambda flow: flow["nodes"]["use_case"].update(
                {"renderer": "dynamic.module.renderer"}
            ),
            "does not match its schema",
        ),
        (
            lambda flow: flow["nodes"]["use_case"].update(
                {"renderer": "unregistered_renderer"}
            ),
            "unregistered renderer",
        ),
        (
            lambda flow: flow["nodes"]["use_case"].update(
                {"summary_renderer": "unregistered_summary"}
            ),
            "unregistered summary renderer",
        ),
        (
            lambda flow: flow["nodes"]["use_case"].update(
                {"content_key": "steps.missing"}
            ),
            "missing en content key",
        ),
        (
            lambda flow: flow["nodes"]["use_case"]["transitions"][0].update(
                {"next": "missing_node"}
            ),
            "unknown node",
        ),
        (
            lambda flow: flow["nodes"]["scope_and_evidence"]["transitions"][
                0
            ].update({"next": "target_and_window"}),
            "contains a cycle",
        ),
        (
            lambda flow: flow.update(
                {"node_order": list(reversed(flow["node_order"]))}
            ),
            "same declared order|start node must be first",
        ),
    ],
    ids=[
        "non-token-renderer",
        "unregistered-renderer",
        "unregistered-summary",
        "missing-content",
        "unknown-node",
        "cycle",
        "wrong-order",
    ],
)
def test_loader_rejects_invalid_or_unsafe_flow_mutations(mutation, error_pattern):
    """Reject invalid schema shapes and unsafe semantic graph references."""
    flow, schema = _flow_and_schema()
    mutation(flow)

    with pytest.raises(GuidedFlowError, match=error_pattern):
        validate_guided_input_flow(flow, schema)


def test_guided_english_and_german_have_recursive_parity_and_placeholders():
    """Require every Guided content leaf and format field in both languages."""
    english_leaves = dict(_flatten_strings(GUIDED_INPUTS["en"]))
    german_leaves = dict(_flatten_strings(GUIDED_INPUTS["de"]))

    assert english_leaves.keys() == german_leaves.keys()
    assert english_leaves
    for path in english_leaves:
        english_value = english_leaves[path]
        german_value = german_leaves[path]
        assert isinstance(english_value, str), path
        assert isinstance(german_value, str), path
        assert english_value.strip(), path
        assert german_value.strip(), path
        assert _placeholder_names(english_value) == _placeholder_names(
            german_value
        ), path


def test_offset_establishment_guidance_explains_estimator_choice_and_sign():
    """Keep calibration weighting, robustness, sign, and validation explicit."""
    expected_phrases = {
        "en": (
            "median or arithmetic mean",
            "Station Medians",
            "Joint Spots / Scheduled Pairs",
            "with the same sign",
            "not the preferred answer",
            "centered near `0 dB`",
        ),
        "de": (
            "Median oder arithmetisches Mittel",
            "Stationsmediane",
            "Joint-Spots / geplante Paare",
            "mit demselben Vorzeichen",
            "nicht nach dem bevorzugten Ergebnis",
            "um `0 dB` zentriert",
        ),
    }

    for language, phrases in expected_phrases.items():
        messages = GUIDED_INPUTS[language]["messages"]
        assert "0.0 dB" in messages["calibration_run_notice"] or (
            "0,0 dB" in messages["calibration_run_notice"]
        )
        for guidance_key in (
            "establish_hardware_guidance",
            "establish_reference_guidance",
        ):
            guidance = messages[guidance_key]
            assert "\n\n" in guidance
            for phrase in phrases:
                assert phrase in guidance


def test_every_flow_content_key_resolves_to_bilingual_title_and_body():
    """Keep declarative content references stable and complete in both languages."""
    flow = load_guided_input_flow()

    for node_id, node in flow["nodes"].items():
        for language in ("en", "de"):
            content = resolve_content_key(
                GUIDED_INPUTS[language],
                node["content_key"],
            )
            assert set(content) == {"title", "body_md"}, (node_id, language)
            assert all(value.strip() for value in content.values())


def test_guided_window_summaries_are_bilingual_and_locale_independent():
    """Keep every relative/custom window phrase inside Guided localization."""
    relative_state = {"val_time_mode": "last_x", "val_hours": 24}
    custom_state = {
        "val_time_mode": "custom",
        "val_start_d": date(2026, 5, 1),
        "val_start_t": time(17, 24),
        "val_end_d": date(2026, 5, 15),
        "val_end_t": time(7, 12),
    }

    assert _window_summary(relative_state, GUIDED_INPUTS["en"]) == "last 24 h"
    assert _window_summary(relative_state, GUIDED_INPUTS["de"]) == "letzte 24 h"
    expected_custom = "2026-05-01 17:24–2026-05-15 07:12 UTC"
    assert _window_summary(custom_state, GUIDED_INPUTS["en"]) == expected_custom
    assert _window_summary(custom_state, GUIDED_INPUTS["de"]) == expected_custom


@pytest.mark.parametrize(
    ("condition", "facts", "expected"),
    [
        ({"field": "mode", "equals": "rx"}, {"mode": "rx"}, True),
        ({"field": "mode", "equals": "rx"}, {"mode": "tx"}, False),
        ({"field": "mode", "in": ["rx", "tx"]}, {"mode": "tx"}, True),
        ({"field": "mode", "in": ["rx", "tx"]}, {}, False),
        (
            {
                "all": [
                    {"field": "mode", "equals": "tx"},
                    {"field": "method", "equals": "sequential"},
                ]
            },
            {"mode": "tx", "method": "sequential"},
            True,
        ),
        (
            {
                "any": [
                    {"field": "mode", "equals": "rx"},
                    {"field": "method", "equals": "sequential"},
                ]
            },
            {"mode": "tx", "method": "sequential"},
            True,
        ),
        (
            {"not": {"field": "mode", "equals": "rx"}},
            {"mode": "tx"},
            True,
        ),
    ],
    ids=["equals", "equals-false", "in", "in-missing", "all", "any", "not"],
)
def test_condition_vocabulary(condition, facts, expected):
    """Evaluate only the finite equals/in/all/any/not condition vocabulary."""
    assert evaluate_condition(condition, facts) is expected


@pytest.mark.parametrize(
    "invalid_condition",
    [
        {"field": "mode", "greater_than": 1},
        {"field": "mode", "equals": "rx", "in": ["rx"]},
        {"all": []},
        {"any": []},
        {"not": {"field": "mode", "contains": "r"}},
    ],
)
def test_schema_rejects_conditions_outside_the_whitelisted_vocabulary(
    invalid_condition,
):
    """Prevent executable or ambiguous condition syntax entering the flow."""
    _, schema = _flow_and_schema()
    condition_schema = {"$ref": "#/$defs/condition", "$defs": schema["$defs"]}

    with pytest.raises(ValidationError):
        Draft202012Validator(condition_schema).validate(invalid_condition)


def test_condition_engine_rejects_an_unsupported_condition():
    """Fail clearly even if an unvalidated condition reaches pure evaluation."""
    with pytest.raises(GuidedFlowError, match="Unsupported Guided Input condition"):
        evaluate_condition({"python": "dangerous()"}, {})


@pytest.mark.parametrize(
    (
        "use_case",
        "benchmark_mode",
        "local_benchmark",
        "tx_ab_method",
        "offset_intent",
        "expected_path",
    ),
    [
        (
            "rx_success",
            "none",
            "local_median",
            "simultaneous",
            "no_offset",
            ("use_case", "target_and_window", "scope_and_evidence", "review_and_run"),
        ),
        (
            "tx_success",
            "none",
            "local_median",
            "simultaneous",
            "no_offset",
            ("use_case", "target_and_window", "scope_and_evidence", "review_and_run"),
        ),
        (
            "rx_compare",
            "hardware_ab",
            "local_median",
            "simultaneous",
            "no_offset",
            (
                "use_case",
                "target_and_window",
                "reference_design",
                "offset_calibration",
                "scope_and_evidence",
                "review_and_run",
            ),
        ),
        (
            "rx_compare",
            "reference_station",
            "local_median",
            "simultaneous",
            "established_offset",
            (
                "use_case",
                "target_and_window",
                "reference_design",
                "offset_calibration",
                "scope_and_evidence",
                "review_and_run",
            ),
        ),
        (
            "rx_compare",
            "local_neighborhood",
            "local_median",
            "simultaneous",
            "no_offset",
            (
                "use_case",
                "target_and_window",
                "reference_design",
                "scope_and_evidence",
                "review_and_run",
            ),
        ),
        (
            "rx_compare",
            "local_neighborhood",
            "local_best",
            "simultaneous",
            "no_offset",
            (
                "use_case",
                "target_and_window",
                "reference_design",
                "scope_and_evidence",
                "review_and_run",
            ),
        ),
        (
            "tx_compare",
            "hardware_ab",
            "local_median",
            "simultaneous",
            "establish_offset",
            (
                "use_case",
                "target_and_window",
                "reference_design",
                "offset_calibration",
                "scope_and_evidence",
                "review_and_run",
            ),
        ),
        (
            "tx_compare",
            "hardware_ab",
            "local_median",
            "sequential",
            "no_offset",
            (
                "use_case",
                "target_and_window",
                "reference_design",
                "offset_calibration",
                "scope_and_evidence",
                "review_and_run",
            ),
        ),
        (
            "tx_compare",
            "reference_station",
            "local_median",
            "simultaneous",
            "established_offset",
            (
                "use_case",
                "target_and_window",
                "reference_design",
                "offset_calibration",
                "scope_and_evidence",
                "review_and_run",
            ),
        ),
        (
            "tx_compare",
            "local_neighborhood",
            "local_median",
            "simultaneous",
            "no_offset",
            (
                "use_case",
                "target_and_window",
                "reference_design",
                "scope_and_evidence",
                "review_and_run",
            ),
        ),
    ],
    ids=[
        "rx-success",
        "tx-success",
        "rx-hardware-no-offset",
        "rx-reference-established-offset",
        "rx-local-median",
        "rx-local-best",
        "tx-hardware-simultaneous-establish-offset",
        "tx-hardware-sequential",
        "tx-reference",
        "tx-local-neighborhood",
    ],
)
def test_every_specified_branch_reaches_review(
    use_case,
    benchmark_mode,
    local_benchmark,
    tx_ab_method,
    offset_intent,
    expected_path,
):
    """Resolve every required Success/Compare design to the terminal review."""
    flow = load_guided_input_flow()
    facts = {
        "guided_use_case": use_case,
        "benchmark_mode": benchmark_mode,
        "local_benchmark": local_benchmark,
        "tx_ab_method": tx_ab_method,
        "guided_offset_intent": offset_intent,
        "guided_scope_mode": "general",
    }

    path = resolve_flow_path(flow, facts)

    assert path == expected_path
    assert path[-1] == flow["terminal_node"]


def test_matching_next_node_rejects_overlapping_transitions():
    """Require deterministic transition selection for every resolved branch."""
    node = {
        "transitions": [
            {
                "when": {"field": "mode", "in": ["rx", "tx"]},
                "next": "first",
            },
            {
                "when": {"field": "mode", "equals": "rx"},
                "next": "second",
            },
        ]
    }

    with pytest.raises(GuidedFlowError, match="overlapping transitions"):
        matching_next_node(node, {"mode": "rx"})


def test_optional_skip_condition_omits_node_and_follows_its_transition():
    """Execute accepted ``skip_when`` syntax instead of treating it as metadata."""
    flow, _ = _flow_and_schema()
    flow["nodes"]["reference_design"]["skip_when"] = {
        "field": "guided_use_case",
        "in": ["rx_success", "tx_success"],
    }
    flow["nodes"]["target_and_window"]["transitions"][0]["next"] = (
        "reference_design"
    )
    flow["nodes"]["reference_design"]["transitions"].insert(
        0,
        {
            "when": {
                "field": "guided_use_case",
                "in": ["rx_success", "tx_success"],
            },
            "next": "scope_and_evidence",
        },
    )

    path = resolve_flow_path(
        flow,
        {
            "guided_use_case": "rx_success",
            "guided_scope_mode": "general",
        },
    )

    assert path == (
        "use_case",
        "target_and_window",
        "scope_and_evidence",
        "review_and_run",
    )


def test_skipped_node_without_matching_transition_fails_clearly():
    """Reject a skip rule that cannot advance through the declared graph."""
    flow, _ = _flow_and_schema()
    flow["nodes"]["reference_design"]["skip_when"] = {
        "field": "guided_use_case",
        "equals": "rx_success",
    }
    flow["nodes"]["target_and_window"]["transitions"][0]["next"] = (
        "reference_design"
    )

    with pytest.raises(GuidedFlowError, match="has no matching transition"):
        resolve_flow_path(flow, {"guided_use_case": "rx_success"})


def test_complete_hardware_state_satisfies_every_node_rule():
    """Accept one complete canonical configuration across all applicable steps."""
    state = _complete_state()

    assert all(
        is_guided_node_complete(node_id, state)
        for node_id in EXPECTED_NODE_ORDER
    )


@pytest.mark.parametrize(
    ("node_id", "updates"),
    [
        ("use_case", {"guided_use_case": None}),
        ("target_and_window", {"val_callsign": "NOT-A-CALL"}),
        ("target_and_window", {"val_qth": "ZZ99"}),
        ("target_and_window", {"val_hours": True}),
        ("reference_design", {"val_ref_callsign": "DL1MKS"}),
        ("offset_calibration", {"guided_offset_intent": "no_offset", "val_benchmark_offset_db": 1.0}),
        ("offset_calibration", {"guided_offset_intent": "established_offset", "val_benchmark_offset_db": float("nan")}),
        ("scope_and_evidence", {"val_solar": "local_noon"}),
        ("scope_and_evidence", {"val_min_stations": True}),
    ],
    ids=[
        "missing-use-case",
        "bad-callsign",
        "bad-qth",
        "boolean-hours",
        "same-reference",
        "nonzero-no-offset",
        "nonfinite-offset",
        "bad-solar",
        "boolean-threshold",
    ],
)
def test_completion_rules_reject_incomplete_or_semantically_invalid_state(
    node_id,
    updates,
):
    """Reject invalid values at the step that owns their completion contract."""
    state = _complete_state(**updates)

    assert not is_guided_node_complete(node_id, state)


def test_completion_rules_cover_reference_and_time_subbranches():
    """Validate custom time, fixed Reference, local, and scheduled TX branches."""
    custom_state = _complete_state(
        val_time_mode="custom",
        val_start_d=date(2026, 7, 1),
        val_start_t=time(12, 0),
        val_end_d=date(2026, 7, 2),
        val_end_t=time(12, 0),
    )
    assert is_guided_node_complete("target_and_window", custom_state)
    custom_state["val_end_d"] = custom_state["val_start_d"] + timedelta(days=32)
    assert not is_guided_node_complete("target_and_window", custom_state)

    reference_state = _complete_state(
        val_comp_mode="reference_station",
        guided_reference_design="reference_station",
        val_ref_callsign="DL2XYZ",
        val_ref_qth="JO62",
    )
    assert is_guided_node_complete("reference_design", reference_state)
    reference_state["val_ref_qth"] = "JO62QM"
    assert not is_guided_node_complete("reference_design", reference_state)

    local_state = _complete_state(
        val_comp_mode="local_neighborhood",
        guided_reference_design="local_neighborhood",
        val_local_benchmark="local_best",
        val_ref_radius_km=250,
    )
    assert is_guided_node_complete("reference_design", local_state)
    local_state["val_ref_radius_km"] = 255
    assert not is_guided_node_complete("reference_design", local_state)

    scheduled_state = _complete_state(
        guided_use_case="tx_compare",
        val_analysis_direction="tx",
        val_tx_ab_method="sequential",
        val_tx_ab_repeat_interval_minutes=10,
        val_tx_ab_target_start_minute=0,
        val_tx_ab_reference_start_minute=2,
    )
    assert is_guided_node_complete("reference_design", scheduled_state)
    scheduled_state["val_tx_ab_reference_start_minute"] = 0
    assert not is_guided_node_complete("reference_design", scheduled_state)


def test_available_nodes_stop_at_the_first_incomplete_prerequisite():
    """Expose only the completed branch prefix and its next incomplete step."""
    flow = load_guided_input_flow()
    state = _complete_state(val_callsign="")

    available = available_flow_nodes(
        flow,
        guided_facts(state),
        lambda node_id: is_guided_node_complete(node_id, state),
    )

    assert available == ("use_case", "target_and_window")

    complete_available = available_flow_nodes(
        flow,
        guided_facts(_complete_state()),
        lambda node_id: is_guided_node_complete(node_id, _complete_state()),
    )
    assert complete_available == tuple(EXPECTED_NODE_ORDER)


def test_reconstruct_guided_transients_from_canonical_loaded_config():
    """Reconstruct the Guided path without persisting a second scientific state."""
    state = _complete_state(
        guided_use_case=None,
        val_analysis_direction="tx",
        val_comp_mode="reference_station",
        guided_reference_design=None,
        val_benchmark_offset_db=1.2,
        guided_offset_intent=None,
        guided_scope_mode=None,
        val_max_peer_distance_km=5000,
    )

    reconstruct_guided_transients(state, has_loaded_demo=False)

    assert state["guided_use_case"] == "tx_compare"
    assert state["guided_reference_design"] == "reference_station"
    assert state["guided_last_compare_mode"] == "reference_station"
    assert state["guided_offset_intent"] == "established_offset"
    assert state["guided_scope_mode"] == "custom"

    reconstruct_guided_transients(state, has_loaded_demo=True)
    assert state["guided_scope_mode"] == "demo"


def test_reconstruct_guided_transients_selects_calibration_demo_intent():
    """Present the unchanged Vanhamel calibration demo as an establishment run."""
    state = _complete_state(
        active_demo_profile="vanhamel_rx_calibration",
        guided_offset_intent=None,
        val_benchmark_offset_db=0.0,
    )

    reconstruct_guided_transients(state, has_loaded_demo=True)

    assert state["guided_offset_intent"] == "establish_offset"
    assert state["val_benchmark_offset_db"] == 0.0


def test_reconstruct_success_and_general_defaults_from_canonical_state():
    """Derive Success and general-purpose transient choices from ordinary values."""
    state = _complete_state(
        guided_use_case=None,
        val_analysis_direction="rx",
        val_comp_mode="none",
        guided_reference_design="hardware_ab",
        val_benchmark_offset_db=0.0,
        guided_offset_intent=None,
        guided_scope_mode=None,
        val_solar="night",
        val_max_peer_distance_km=5000,
        val_exclude_special_callsigns=True,
        val_filter_moving=True,
        val_min_spots=12,
        val_min_opportunities=25,
        val_min_stations=3,
    )
    assert derive_guided_use_case(state) == "rx_success"
    assert not scope_matches_general_defaults(state)

    apply_general_scope_defaults(state)
    assert scope_matches_general_defaults(state)
    reconstruct_guided_transients(state, has_loaded_demo=False)

    assert state["guided_use_case"] == "rx_success"
    assert state["guided_reference_design"] is None
    assert state["guided_offset_intent"] == "no_offset"
    assert state["guided_scope_mode"] == "general"


def test_flow_fields_and_renderers_are_closed_whitelists():
    """Keep declarative names bound to literal registered callables and facts."""
    flow = load_guided_input_flow()
    flow_renderer_names = {node["renderer"] for node in flow["nodes"].values()}
    flow_summary_names = {
        node["summary_renderer"] for node in flow["nodes"].values()
    }
    required_fields = {
        field
        for node in flow["nodes"].values()
        for field in node["required_fields"]
    }

    assert flow_renderer_names == CONTROL_RENDERER_NAMES == set(CONTROL_RENDERERS)
    assert flow_summary_names == SUMMARY_RENDERER_NAMES == set(SUMMARY_RENDERERS)
    assert all(callable(renderer) for renderer in CONTROL_RENDERERS.values())
    assert all(callable(renderer) for renderer in SUMMARY_RENDERERS.values())
    assert required_fields <= set(guided_facts(_complete_state()))
