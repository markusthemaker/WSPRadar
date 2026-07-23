"""Load and validate the declarative Guided Input workflow."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

from config.json_utils import decode_strict_json_bytes
from i18n import GUIDED_INPUTS


FLOW_SCHEMA_VERSION = 1
MAX_GUIDED_FLOW_BYTES = 100_000
CONFIG_DIRECTORY = Path(__file__).resolve().parents[2] / "config"
FLOW_PATH = CONFIG_DIRECTORY / "guided_input_flow.json"
FLOW_SCHEMA_PATH = CONFIG_DIRECTORY / "guided_input_flow.schema.json"

CONTROL_RENDERER_NAMES = frozenset(
    {
        "use_case_selector",
        "target_and_window_fields",
        "reference_design_fields",
        "offset_calibration_fields",
        "scope_and_evidence_fields",
        "review_and_run",
    }
)
SUMMARY_RENDERER_NAMES = frozenset(
    {
        "use_case_summary",
        "target_and_window_summary",
        "reference_design_summary",
        "offset_calibration_summary",
        "scope_and_evidence_summary",
        "review_and_run_summary",
    }
)


class GuidedFlowError(ValueError):
    """Report an invalid or unsafe Guided Input workflow definition."""


def _read_bounded_json(path: Path, *, document_name: str) -> Any:
    """Read one bounded strict-JSON document independently of the current CWD."""
    try:
        raw_bytes = path.read_bytes()
    except OSError as exc:
        raise GuidedFlowError(f"Could not read {document_name}: {exc}") from exc
    if len(raw_bytes) > MAX_GUIDED_FLOW_BYTES:
        raise GuidedFlowError(
            f"The {document_name} exceeds {MAX_GUIDED_FLOW_BYTES} bytes."
        )
    try:
        return decode_strict_json_bytes(raw_bytes, document_name=document_name)
    except ValueError as exc:
        raise GuidedFlowError(str(exc)) from exc


def resolve_content_key(content: Mapping[str, Any], content_key: str) -> Any:
    """Resolve one stable dotted Guided Input content key."""
    current: Any = content
    for key_part in str(content_key).split("."):
        if not isinstance(current, Mapping) or key_part not in current:
            raise KeyError(content_key)
        current = current[key_part]
    return current


def _validate_schema(flow: Any, schema: Any) -> None:
    """Validate the flow against its bundled Draft 2020-12 JSON Schema."""
    try:
        from jsonschema import Draft202012Validator
        from jsonschema.exceptions import SchemaError
    except ImportError as exc:  # pragma: no cover - deployment dependency guard
        raise GuidedFlowError(
            "Guided Input requires the declared jsonschema runtime dependency."
        ) from exc

    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        raise GuidedFlowError(f"The Guided Input JSON Schema is invalid: {exc}") from exc

    errors = sorted(
        Draft202012Validator(schema).iter_errors(flow),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if not errors:
        return
    first_error = errors[0]
    location = ".".join(str(part) for part in first_error.absolute_path) or "$"
    raise GuidedFlowError(
        f"Guided Input flow does not match its schema at {location}: "
        f"{first_error.message}"
    )


def _validate_content_keys(nodes: Mapping[str, Any]) -> None:
    """Require every flow content key to resolve to a title/body pair in both languages."""
    for node_id, node in nodes.items():
        content_key = node["content_key"]
        for language in ("en", "de"):
            try:
                content = resolve_content_key(GUIDED_INPUTS[language], content_key)
            except KeyError as exc:
                raise GuidedFlowError(
                    f"Node {node_id!r} references missing {language} content "
                    f"key {content_key!r}."
                ) from exc
            if not isinstance(content, Mapping):
                raise GuidedFlowError(
                    f"Node {node_id!r} content {content_key!r} must be an object."
                )
            for required_key in ("title", "body_md"):
                value = content.get(required_key)
                if not isinstance(value, str) or not value.strip():
                    raise GuidedFlowError(
                        f"Node {node_id!r} has blank {language} "
                        f"{content_key}.{required_key}."
                    )


def _validate_graph(flow: Mapping[str, Any]) -> None:
    """Reject unknown references, unreachable nodes, dead ends, and every cycle."""
    nodes = flow["nodes"]
    node_order = flow["node_order"]
    start_node = flow["start_node"]
    terminal_node = flow["terminal_node"]
    node_ids = set(nodes)

    if node_order != list(nodes):
        raise GuidedFlowError(
            "node_order must list every node exactly once in the same declared order."
        )
    if node_order[0] != start_node:
        raise GuidedFlowError("The Guided Input start node must be first in node_order.")
    if terminal_node not in nodes:
        raise GuidedFlowError(f"Unknown terminal node {terminal_node!r}.")
    if nodes[terminal_node]["transitions"]:
        raise GuidedFlowError("The terminal Guided Input node must not have transitions.")
    if "skip_when" in nodes[terminal_node]:
        raise GuidedFlowError("The terminal Guided Input node cannot be skipped.")

    adjacency: dict[str, tuple[str, ...]] = {}
    for node_id, node in nodes.items():
        if node["renderer"] not in CONTROL_RENDERER_NAMES:
            raise GuidedFlowError(
                f"Node {node_id!r} uses unregistered renderer {node['renderer']!r}."
            )
        if node["summary_renderer"] not in SUMMARY_RENDERER_NAMES:
            raise GuidedFlowError(
                f"Node {node_id!r} uses unregistered summary renderer "
                f"{node['summary_renderer']!r}."
            )
        next_nodes = tuple(
            transition["next"] for transition in node["transitions"]
        )
        unknown_nodes = sorted(set(next_nodes) - node_ids)
        if unknown_nodes:
            raise GuidedFlowError(
                f"Node {node_id!r} references unknown node(s): "
                + ", ".join(unknown_nodes)
                + "."
            )
        if node_id != terminal_node and not next_nodes:
            raise GuidedFlowError(
                f"Non-terminal node {node_id!r} has no allowed transition."
            )
        adjacency[node_id] = next_nodes

    visited: set[str] = set()
    active: set[str] = set()

    def visit(node_id: str) -> None:
        if node_id in active:
            raise GuidedFlowError(
                f"Guided Input flow contains a cycle through {node_id!r}."
            )
        if node_id in visited:
            return
        active.add(node_id)
        for next_node in adjacency[node_id]:
            visit(next_node)
        active.remove(node_id)
        visited.add(node_id)

    for node_id in nodes:
        visit(node_id)

    reachable: set[str] = set()
    pending = [start_node]
    while pending:
        node_id = pending.pop()
        if node_id in reachable:
            continue
        reachable.add(node_id)
        pending.extend(adjacency[node_id])
    unreachable = sorted(node_ids - reachable)
    if unreachable:
        raise GuidedFlowError(
            "Guided Input flow contains unreachable node(s): "
            + ", ".join(unreachable)
            + "."
        )

    can_reach_terminal = {terminal_node}
    changed = True
    while changed:
        changed = False
        for node_id, next_nodes in adjacency.items():
            if node_id not in can_reach_terminal and any(
                next_node in can_reach_terminal for next_node in next_nodes
            ):
                can_reach_terminal.add(node_id)
                changed = True
    dead_ends = sorted(node_ids - can_reach_terminal)
    if dead_ends:
        raise GuidedFlowError(
            "Guided Input node(s) cannot reach the terminal review: "
            + ", ".join(dead_ends)
            + "."
        )


def validate_guided_input_flow(flow: Any, schema: Any) -> Mapping[str, Any]:
    """Return a structurally and semantically validated Guided Input flow."""
    _validate_schema(flow, schema)
    if flow.get("schema_version") != FLOW_SCHEMA_VERSION:
        raise GuidedFlowError(
            f"Unsupported Guided Input schema version {flow.get('schema_version')!r}."
        )
    _validate_graph(flow)
    _validate_content_keys(flow["nodes"])
    return flow


@lru_cache(maxsize=1)
def load_guided_input_flow() -> Mapping[str, Any]:
    """Load and validate the bundled workflow once per application process."""
    schema = _read_bounded_json(
        FLOW_SCHEMA_PATH,
        document_name="Guided Input flow schema",
    )
    flow = _read_bounded_json(FLOW_PATH, document_name="Guided Input flow")
    return validate_guided_input_flow(flow, schema)
