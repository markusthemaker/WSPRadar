"""Pure condition and path evaluation for Guided Input."""

from __future__ import annotations

from typing import Any, Callable, Mapping

from .flow_loader import GuidedFlowError


def evaluate_condition(condition: Mapping[str, Any], facts: Mapping[str, Any]) -> bool:
    """Evaluate the flow's small declarative condition vocabulary."""
    if "equals" in condition:
        return facts.get(condition["field"]) == condition["equals"]
    if "in" in condition:
        return facts.get(condition["field"]) in condition["in"]
    if "all" in condition:
        return all(evaluate_condition(child, facts) for child in condition["all"])
    if "any" in condition:
        return any(evaluate_condition(child, facts) for child in condition["any"])
    if "not" in condition:
        return not evaluate_condition(condition["not"], facts)
    raise GuidedFlowError(f"Unsupported Guided Input condition: {condition!r}")


def matching_next_node(node: Mapping[str, Any], facts: Mapping[str, Any]) -> str | None:
    """Return the sole matching transition target, or None while input is incomplete."""
    matching_nodes = [
        transition["next"]
        for transition in node["transitions"]
        if evaluate_condition(transition["when"], facts)
    ]
    if len(matching_nodes) > 1:
        raise GuidedFlowError(
            "Guided Input flow has overlapping transitions for the current state: "
            + ", ".join(matching_nodes)
            + "."
        )
    return matching_nodes[0] if matching_nodes else None


def resolve_flow_path(
    flow: Mapping[str, Any],
    facts: Mapping[str, Any],
) -> tuple[str, ...]:
    """Resolve the visible deterministic branch until input is incomplete.

    Nodes whose optional ``skip_when`` condition matches are traversed but omitted
    from the returned path. A skipped node must still select exactly one declared
    transition so malformed flow state cannot silently truncate the workflow.
    """
    path: list[str] = []
    visited: set[str] = set()
    current_node = flow["start_node"]
    while current_node is not None:
        if current_node in visited:
            raise GuidedFlowError(
                f"Guided Input flow revisited node {current_node!r}."
            )
        visited.add(current_node)
        node = flow["nodes"][current_node]
        should_skip = "skip_when" in node and evaluate_condition(
            node["skip_when"], facts
        )
        if should_skip:
            if current_node == flow["terminal_node"]:
                raise GuidedFlowError(
                    "The terminal Guided Input node cannot be skipped."
                )
            next_node = matching_next_node(node, facts)
            if next_node is None:
                raise GuidedFlowError(
                    f"Skipped Guided Input node {current_node!r} has no matching "
                    "transition."
                )
            current_node = next_node
            continue
        path.append(current_node)
        if current_node == flow["terminal_node"]:
            break
        current_node = matching_next_node(node, facts)
    return tuple(path)


def available_flow_nodes(
    flow: Mapping[str, Any],
    facts: Mapping[str, Any],
    is_complete: Callable[[str], bool],
) -> tuple[str, ...]:
    """Return the branch prefix whose prerequisites have actually been completed."""
    resolved_path = resolve_flow_path(flow, facts)
    available: list[str] = []
    for node_id in resolved_path:
        available.append(node_id)
        if node_id != flow["terminal_node"] and not is_complete(node_id):
            break
    return tuple(available)
