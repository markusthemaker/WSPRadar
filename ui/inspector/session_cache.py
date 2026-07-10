"""Bounded per-session cache primitives for Segment Inspector results."""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import fields, is_dataclass
from sys import getsizeof

import numpy as np
import pandas as pd


INSPECTOR_CACHE_STATE_KEY = "segment_inspector_cache"


def estimate_cache_value_bytes(value, _seen=None) -> int:
    """Estimate retained bytes for supported compact inspector cache values."""
    if _seen is None:
        _seen = set()
    value_id = id(value)
    if value_id in _seen:
        return 0
    _seen.add(value_id)

    if isinstance(value, pd.DataFrame):
        return int(value.memory_usage(index=True, deep=True).sum())
    if isinstance(value, pd.Series):
        return int(value.memory_usage(index=True, deep=True))
    if isinstance(value, pd.Index):
        return int(value.memory_usage(deep=True))
    if isinstance(value, np.ndarray):
        return int(value.nbytes)
    if isinstance(value, (bytes, bytearray, memoryview)):
        return int(len(value))
    if isinstance(value, str):
        return int(getsizeof(value))
    if isinstance(value, dict):
        return int(getsizeof(value)) + sum(
            estimate_cache_value_bytes(key, _seen) + estimate_cache_value_bytes(item, _seen)
            for key, item in value.items()
        )
    if isinstance(value, (list, tuple, set, frozenset, OrderedDict)):
        return int(getsizeof(value)) + sum(
            estimate_cache_value_bytes(item, _seen) for item in value
        )
    if is_dataclass(value) and not isinstance(value, type):
        return int(getsizeof(value)) + sum(
            estimate_cache_value_bytes(getattr(value, field.name), _seen)
            for field in fields(value)
        )
    return int(getsizeof(value))


class SessionInspectorCache:
    """Run-scoped, byte-bounded LRU cache stored in one Streamlit session."""

    def __init__(self, run_id, *, max_bytes: int, namespace_limits: dict[str, int]):
        self.run_id = run_id
        self.max_bytes = max(0, int(max_bytes))
        self.namespace_limits = {
            str(namespace): max(0, int(limit))
            for namespace, limit in namespace_limits.items()
        }
        self._entries = {
            namespace: OrderedDict()
            for namespace in self.namespace_limits
        }
        self.total_bytes = 0
        self._access_sequence = 0

    @property
    def entry_count(self) -> int:
        return sum(len(entries) for entries in self._entries.values())

    def namespace_entry_count(self, namespace: str) -> int:
        return len(self._entries.get(namespace, ()))

    def get(self, namespace: str, key):
        entries = self._entries.get(namespace)
        if entries is None or key not in entries:
            return None, False
        value, size_bytes, _ = entries.pop(key)
        self._access_sequence += 1
        entries[key] = (value, size_bytes, self._access_sequence)
        return value, True

    def put(self, namespace: str, key, value, *, size_bytes: int | None = None) -> bool:
        entries = self._entries.get(namespace)
        limit = self.namespace_limits.get(namespace, 0)
        if entries is None or limit <= 0 or self.max_bytes <= 0:
            return False

        retained_bytes = (
            estimate_cache_value_bytes(value)
            if size_bytes is None
            else max(0, int(size_bytes))
        )
        if retained_bytes > self.max_bytes:
            return False

        previous = entries.pop(key, None)
        if previous is not None:
            self.total_bytes -= previous[1]
        self._access_sequence += 1
        entries[key] = (value, retained_bytes, self._access_sequence)
        self.total_bytes += retained_bytes

        while len(entries) > limit:
            _, (_, removed_bytes, _) = entries.popitem(last=False)
            self.total_bytes -= removed_bytes
        self._evict_to_byte_limit()
        return key in entries

    def clear(self) -> None:
        for entries in self._entries.values():
            entries.clear()
        self.total_bytes = 0

    def _evict_to_byte_limit(self) -> None:
        while self.total_bytes > self.max_bytes:
            oldest_namespace = None
            oldest_key = None
            oldest_order = None
            for namespace, entries in self._entries.items():
                if not entries:
                    continue
                key = next(iter(entries))
                order = entries[key][2]
                if oldest_namespace is None or order < oldest_order:
                    oldest_namespace = namespace
                    oldest_key = key
                    oldest_order = order
            if oldest_namespace is None:
                break
            _, removed_bytes, _ = self._entries[oldest_namespace].pop(oldest_key)
            self.total_bytes -= removed_bytes
