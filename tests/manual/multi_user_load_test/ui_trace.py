"""Bounded structural browser-protocol diagnostics without rendered content.

This records messages observed on the wire, not a reconstruction of Streamlit's
frontend tree or its stale-node cleanup rules. No protobuf messages are retained.
"""

from collections import OrderedDict, deque
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
from itertools import islice
import time


_MAX_TRANSIENT_ELEMENTS = 32
_MAX_IDENTIFIER_LENGTH = 512
_MAX_WIDGET_DIGESTS = 2048
_MAX_RECORDED_WIDGET_CHANGES = 128


def _identifiers(message):
    """Read only explicit structural IDs, never labels or widget values."""
    identifiers = {}
    for field_name in ("id", "key", "form_id"):
        if field_name in message.DESCRIPTOR.fields_by_name:
            identifier = getattr(message, field_name)
            if isinstance(identifier, str) and identifier:
                identifiers[field_name] = identifier[:_MAX_IDENTIFIER_LENGTH]
                if len(identifier) > _MAX_IDENTIFIER_LENGTH:
                    identifiers[f"{field_name}_truncated"] = True
    return identifiers


def _element_summary(element):
    element_type = element.WhichOneof("type")
    summary = {"type": element_type}
    if element_type is not None:
        summary.update(_identifiers(getattr(element, element_type)))
    return summary


def _message_summary(message, message_type):
    summary = {"type": message_type}
    if message_type == "delta":
        delta = message.delta
        delta_type = delta.WhichOneof("type")
        structural_delta = {"type": delta_type, "fragment_id": delta.fragment_id}
        if delta_type == "add_block":
            block = delta.add_block
            block_type = block.WhichOneof("type")
            block_summary = {"type": block_type, **_identifiers(block)}
            if block_type is not None:
                nested_ids = _identifiers(getattr(block, block_type))
                if nested_ids:
                    block_summary["type_ids"] = nested_ids
            structural_delta["block"] = block_summary
        elif delta_type == "new_element":
            structural_delta["element"] = _element_summary(delta.new_element)
        elif delta_type == "new_transient":
            elements = delta.new_transient.elements
            structural_delta["transient"] = {
                "element_count": len(elements),
                "elements": [_element_summary(element)
                             for element in islice(elements, _MAX_TRANSIENT_ELEMENTS)],
                "elements_truncated": len(elements) > _MAX_TRANSIENT_ELEMENTS,
            }
        summary["delta"] = structural_delta
    elif message_type == "new_session":
        summary["new_session"] = {
            "script_run_id": message.new_session.script_run_id,
            "fragment_ids": list(message.new_session.fragment_ids_this_run),
        }
    elif message_type == "script_finished":
        status = message.script_finished
        enum = message.DESCRIPTOR.fields_by_name["script_finished"].enum_type
        descriptor = enum.values_by_number.get(status)
        summary["script_finished"] = descriptor.name if descriptor is not None else status
    elif message_type == "session_status_changed":
        summary["script_is_running"] = message.session_status_changed.script_is_running
    return summary


class UITrace:
    """Keep recent structural messages and a separate LRU of compact cache entries."""

    def __init__(self, limit=2000, cache_limit=2048):
        for name, capacity in (("limit", limit), ("cache_limit", cache_limit)):
            if isinstance(capacity, bool) or not isinstance(capacity, int) or capacity <= 0:
                raise ValueError(f"{name} must be a positive integer")
        self.limit = limit
        self.cache_limit = cache_limit
        self._records = deque(maxlen=limit)
        self._cache = OrderedDict()
        self._sequence = 0
        self._cache_evictions = 0
        self._unresolved_references = 0
        self._widget_digest_limit = min(cache_limit, _MAX_WIDGET_DIGESTS)
        self._widget_digests = OrderedDict()
        self._has_widget_baseline = False

    def observe(self, message, *, script_run_id, fragment_ids, action_phase):
        """Summarize one decoded ForwardMsg using its own placement metadata."""
        self._sequence += 1
        message_type = message.WhichOneof("type")
        reference_hash = message.ref_hash if message_type == "ref_hash" else None
        unresolved_reference = False
        if reference_hash is not None:
            summary = self._cache.get(reference_hash)
            if summary is None:
                unresolved_reference = True
                self._unresolved_references += 1
                summary = {"type": None}
            else:
                self._cache.move_to_end(reference_hash)
        else:
            summary = _message_summary(message, message_type)
            if message.hash:
                self._cache[message.hash] = summary
                self._cache.move_to_end(message.hash)
                if len(self._cache) > self.cache_limit:
                    self._cache.popitem(last=False)
                    self._cache_evictions += 1

        record = {
            "sequence": self._sequence,
            "direction": "in",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "monotonic_seconds": time.monotonic(),
            "script_run_id": script_run_id,
            "fragment_ids": list(fragment_ids or ()),
            "action_phase": action_phase,
            "message_type": message_type,
            "debug_last_backmsg_id": message.debug_last_backmsg_id,
            "message_hash": message.hash or None,
            "reference_hash": reference_hash,
            "unresolved_reference": unresolved_reference,
            "metadata": {
                # Metadata is excluded from cached payloads by Streamlit. A ref
                # frame can deliberately place the same element at a new path.
                "delta_path": list(message.metadata.delta_path),
                "cacheable": message.metadata.cacheable,
                "active_script_hash": message.metadata.active_script_hash,
            },
            "structure": deepcopy(summary),
        }
        self._records.append(record)

    def observe_back_message(self, message, *, script_run_id, fragment_ids, action_phase):
        """Record outgoing rerun routing and changed widget fingerprints, never values."""
        self._sequence += 1
        message_type = message.WhichOneof("type")
        summary = {"type": message_type}
        if message_type == "rerun_script":
            request = message.rerun_script
            initial_baseline = not self._has_widget_baseline
            changed_widgets = []
            changed_count = 0
            widgets = request.widget_states.widgets
            for widget in widgets:
                # Hash the complete state for equality comparison, but retain
                # neither that serialization nor potentially unbounded raw IDs.
                identifier_digest = hashlib.sha256(widget.id.encode("utf-8")).hexdigest()
                state_digest = hashlib.sha256(widget.SerializeToString(deterministic=True)).hexdigest()
                value_type = widget.WhichOneof("value")
                previous = self._widget_digests.get(identifier_digest)
                if previous != state_digest:
                    changed_count += 1
                    if len(changed_widgets) < _MAX_RECORDED_WIDGET_CHANGES:
                        changed_widgets.append({
                            "id": widget.id[:_MAX_IDENTIFIER_LENGTH],
                            "id_truncated": len(widget.id) > _MAX_IDENTIFIER_LENGTH,
                            "value_type": value_type,
                            "digest": state_digest,
                            "change": "baseline" if initial_baseline else (
                                "unseen" if previous is None else "changed"
                            ),
                        })
                self._widget_digests[identifier_digest] = state_digest
                self._widget_digests.move_to_end(identifier_digest)
                if len(self._widget_digests) > self._widget_digest_limit:
                    self._widget_digests.popitem(last=False)
            self._has_widget_baseline = True
            summary["rerun_script"] = {
                "fragment_id": request.fragment_id[:_MAX_IDENTIFIER_LENGTH],
                "is_auto_rerun": request.is_auto_rerun,
                "initial_widget_baseline": initial_baseline,
                "widget_count": len(widgets),
                "changed_widget_count": changed_count,
                "changed_widgets": changed_widgets,
                "changed_widgets_truncated": changed_count > len(changed_widgets),
            }
        self._records.append({
            "sequence": self._sequence,
            "direction": "out",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "monotonic_seconds": time.monotonic(),
            "script_run_id": script_run_id,
            "fragment_ids": list(fragment_ids or ()),
            "action_phase": action_phase,
            "message_type": message_type,
            "debug_last_backmsg_id": message.debug_last_backmsg_id,
            "structure": summary,
        })

    def snapshot(self):
        """Return an independent JSON-compatible snapshot, excluding cache payloads."""
        return {
            "schema_version": 1,
            "record_limit": self.limit,
            "cache_limit": self.cache_limit,
            "observed_message_count": self._sequence,
            "dropped_record_count": max(0, self._sequence - len(self._records)),
            "cache_entry_count": len(self._cache),
            "cache_eviction_count": self._cache_evictions,
            "unresolved_reference_count": self._unresolved_references,
            "widget_digest_limit": self._widget_digest_limit,
            "widget_digest_count": len(self._widget_digests),
            "interpretation": (
                "Observed wire structure only; this does not reconstruct the frontend tree. "
                "Reference resolution uses this bounded diagnostic cache, whose misses do not "
                "establish a browser cache miss. Rendered text, widget values, table data and "
                "image content are omitted. Outgoing widget changes are fingerprint differences, "
                "not proof of which widget caused a rerun; unseen IDs may have been evicted."
            ),
            "records": deepcopy(list(self._records)),
        }
