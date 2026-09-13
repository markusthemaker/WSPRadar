"""Own export content and fingerprint it without rendering or export construction.

Registration can compare content signatures before retaining a changed payload.
An owned snapshot keeps its mutable implementation details private; callers only
receive independent graphs through ``materialize`` on the export preparation
path. Numeric arrays use immutable byte storage inside the snapshot. DataFrame
copies explicitly detach object cells, labels, categories, and attributes rather
than relying on Pandas' nonrecursive ``deep=True`` behavior for object values.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from decimal import Decimal
import hashlib
import json
from pathlib import PurePath
import struct
from typing import Any

import numpy as np
import pandas as pd


_SIGNATURE_VERSION = b"wspradar-export-content-v1"


def _unsupported(value, path):
    raise TypeError(
        f"Unsupported export content at {path}: {type(value).__name__}."
    )


def _digest(tag, parts=()):
    digest = hashlib.sha256()
    digest.update(tag)
    for part in parts:
        digest.update(len(part).to_bytes(8, "big"))
        digest.update(part)
    return digest.digest()


def _text(value):
    return str(value).encode("utf-8", errors="surrogatepass")


def _integer(value):
    magnitude = abs(value)
    return (b"-" if value < 0 else b"+") + magnitude.to_bytes(
        max(1, (magnitude.bit_length() + 7) // 8), "big"
    )


def _numpy_dtype_parts(dtype):
    """Retain dtype interpretation, including structured field layout."""
    return (
        _text(dtype.str),
        _text(dtype.descr),
        _integer(dtype.itemsize),
        b"1" if dtype.isalignedstruct else b"0",
    )


def _fingerprint(value, memo, active, path):
    if value is None:
        return _digest(b"none")
    if value is pd.NA:
        return _digest(b"pandas-na")
    if value is pd.NaT:
        return _digest(b"pandas-nat")
    if isinstance(value, np.generic):
        if value.dtype.metadata:
            _unsupported(value, path + ".dtype.metadata")
        if value.dtype.hasobject:
            return _fingerprint(value.item(), memo, active, path)
        return _digest(b"numpy-scalar", (*_numpy_dtype_parts(value.dtype), value.tobytes()))
    if isinstance(value, bool):
        return _digest(b"bool", (b"1" if value else b"0",))
    if isinstance(value, int):
        return _digest(b"int", (_integer(value),))
    if isinstance(value, float):
        return _digest(b"float", (struct.pack("!d", value),))
    if isinstance(value, complex):
        return _digest(b"complex", (struct.pack("!dd", value.real, value.imag),))
    if isinstance(value, str):
        return _digest(b"str", (_text(value),))
    if isinstance(value, bytes):
        return _digest(b"bytes", (value,))
    if isinstance(value, bytearray):
        return _digest(b"bytearray", (bytes(value),))
    if isinstance(value, memoryview):
        return _digest(
            b"memoryview", (value.tobytes(), _text(value.format), _text(value.shape)),
        )
    if isinstance(value, pd.Timestamp):
        return _digest(
            b"pandas-timestamp",
            (_text(value.isoformat()), _text(value.tz), _integer(value.fold)),
        )
    if isinstance(value, pd.Timedelta):
        return _digest(b"pandas-timedelta", (_text(value.isoformat()),))
    if isinstance(value, (datetime, time)):
        return _digest(
            _text(type(value).__name__),
            (_text(value.isoformat()), _text(value.tzinfo), _integer(value.fold)),
        )
    if isinstance(value, date):
        return _digest(b"date", (_text(value.isoformat()),))
    if isinstance(value, timedelta):
        return _digest(
            b"timedelta",
            tuple(_integer(part) for part in (value.days, value.seconds, value.microseconds)),
        )
    if isinstance(value, PurePath):
        return _digest(b"path", (_text(type(value).__name__), _text(value)))
    if isinstance(value, Decimal):
        return _digest(b"decimal", (_text(value),))
    if isinstance(value, pd.Period):
        return _digest(b"pandas-period", (_integer(value.ordinal), _text(value.freqstr)))
    if isinstance(value, pd.Interval):
        return _digest(
            b"pandas-interval",
            (
                _fingerprint(value.left, memo, active, path + ".left"),
                _fingerprint(value.right, memo, active, path + ".right"),
                _text(value.closed),
            ),
        )
    identity = id(value)
    if identity in active:
        raise ValueError(f"Cyclic export content at {path}.")
    if identity in memo:
        return memo[identity][1]
    active.add(identity)
    try:
        child = lambda item, suffix: _fingerprint(item, memo, active, path + suffix)
        if isinstance(value, Mapping):
            items = list(value.items())
            if all(type(key) is str and type(item) is str for key, item in items):
                # Localization catalogs are large homogeneous mappings. One
                # ordered JSON encoding avoids a SHA invocation for every key
                # and value. UTF-8 surrogatepass retains even literal surrogate
                # code points distinctly from their corresponding astral text.
                serialized = json.dumps(
                    items, ensure_ascii=False, separators=(",", ":"),
                ).encode("utf-8", errors="surrogatepass")
                result = _digest(b"ordered-string-mapping-json", (serialized,))
            else:
                entries = [
                    (child(key, ".<key>"), child(item, f"[{key!r}]"))
                    for key, item in items
                ]
                result = _digest(b"mapping", (_digest(b"entry", entry) for entry in entries))
        elif isinstance(value, (list, tuple)):
            result = _digest(
                b"list" if isinstance(value, list) else b"tuple",
                (child(item, f"[{position}]") for position, item in enumerate(value)),
            )
        elif isinstance(value, np.ndarray):
            if type(value) is not np.ndarray:
                _unsupported(value, path)
            parts = [*_numpy_dtype_parts(value.dtype), child(value.shape, ".shape")]
            if value.dtype.metadata:
                parts.append(child(dict(value.dtype.metadata), ".dtype.metadata"))
            if value.dtype.names:
                parts.extend(child(value[name], f"[{name!r}]") for name in value.dtype.names)
            elif value.dtype.hasobject:
                parts.extend(child(item, f".flat[{position}]") for position, item in enumerate(value.flat))
            else:
                contiguous = np.ascontiguousarray(value)
                parts.append(memoryview(contiguous).cast("B") if contiguous.size else b"")
            result = _digest(b"ndarray", parts)
        elif isinstance(value, pd.DataFrame):
            parts = [
                child(value.index, ".index"),
                child(value.columns, ".columns"),
                child(value.attrs, ".attrs"),
                child(value.flags.allows_duplicate_labels, ".allows_duplicate_labels"),
            ]
            for position, (_, column) in enumerate(value.items()):
                parts.append(_series_fingerprint(column, memo, active, f"{path}.column[{position}]"))
            result = _digest(b"dataframe", parts)
        elif isinstance(value, pd.Index):
            parts = [_text(type(value).__name__), child(list(value.names), ".names")]
            if isinstance(value, pd.MultiIndex):
                parts.extend(child(level, f".levels[{position}]") for position, level in enumerate(value.levels))
                parts.extend(child(code, f".codes[{position}]") for position, code in enumerate(value.codes))
                parts.append(child(value.sortorder, ".sortorder"))
            elif isinstance(value, pd.CategoricalIndex):
                parts.extend((child(value.categories, ".categories"), child(value.codes, ".codes"), child(value.ordered, ".ordered")))
            elif isinstance(value, pd.RangeIndex):
                parts.extend(_integer(item) for item in (value.start, value.stop, value.step))
            else:
                parts.append(_text(repr(value.dtype)))
                parts.append(child(value.to_numpy(copy=False), ".values"))
                if isinstance(value, (pd.DatetimeIndex, pd.TimedeltaIndex, pd.PeriodIndex)):
                    parts.append(_text(value.freqstr))
            result = _digest(b"index", parts)
        else:
            _unsupported(value, path)
        # Retain the source too: Pandas can return temporary array views, whose
        # Python ids must not be reused by later columns during this traversal.
        memo[identity] = (value, result)
        return result
    finally:
        active.remove(identity)


def _series_fingerprint(series, memo, active, path):
    child = lambda value, suffix: _fingerprint(value, memo, active, path + suffix)
    parts = [_text(repr(series.dtype))]
    if isinstance(series.dtype, pd.CategoricalDtype):
        parts.extend((child(series.cat.categories, ".categories"), child(series.cat.codes.to_numpy(copy=False), ".codes"), child(series.cat.ordered, ".ordered")))
    elif isinstance(series.dtype, np.dtype):
        values = series.to_numpy(copy=False)
        scalar_kind = (
            pd.api.types.infer_dtype(values, skipna=False)
            if series.dtype.hasobject else None
        )
        if scalar_kind in {"string", "bytes"}:
            # Ordinary object-backed text columns need no Python cell traversal.
            # Mixed or missing object cells use the exact recursive path below.
            scalar_hashes = pd.util.hash_array(values, categorize=False)
            parts.extend((_text(scalar_kind), child(scalar_hashes, ".scalar_hashes")))
        else:
            parts.append(child(values, ".values"))
    elif isinstance(series.dtype, pd.DatetimeTZDtype):
        parts.extend((_text(series.dtype.unit), _text(series.dtype.tz), child(series.array.asi8, ".utc_values")))
    else:
        # Nullable/string/Arrow extension arrays retain their explicit dtype and
        # missing mask. Pandas hashes scalar values without widening integers.
        scalar_hashes = pd.util.hash_array(series.array, categorize=False)
        parts.extend((child(scalar_hashes, ".scalar_hashes"), child(series.isna().to_numpy(copy=False), ".missing")))
    return _digest(b"column", parts)


def content_signature(value: Any) -> str:
    """Return a deterministic complete digest without retaining caller objects."""
    return _digest(_SIGNATURE_VERSION, (_fingerprint(value, {}, set(), "$"),)).hex()


def _clone_index(index, clone):
    names = clone(list(index.names), ".names")
    if isinstance(index, pd.MultiIndex):
        return pd.MultiIndex(
            levels=[clone(level, f".levels[{position}]") for position, level in enumerate(index.levels)],
            codes=[code.copy() for code in index.codes],
            sortorder=index.sortorder,
            names=names,
            verify_integrity=False,
        )
    if isinstance(index, pd.CategoricalIndex):
        categories = clone(index.categories, ".categories")
        categorical = pd.Categorical.from_codes(index.codes.copy(), categories=categories, ordered=index.ordered)
        return pd.CategoricalIndex(categorical, name=names[0])
    if pd.api.types.is_object_dtype(index.dtype):
        labels = np.empty(len(index), dtype=object)
        for position, label in enumerate(index):
            labels[position] = clone(label, f"[{position}]")
        return pd.Index(labels, dtype=index.dtype, name=names[0], tupleize_cols=False)
    return index.copy(deep=True).rename(names[0])


def _clone_graph(value, memo, active, path, *, readonly_arrays):
    if value is None or value is pd.NA or value is pd.NaT:
        return value
    if isinstance(value, (bool, int, float, complex, str, bytes, date, time, timedelta, PurePath, Decimal, pd.Timestamp, pd.Timedelta, pd.Period, pd.Interval)):
        return value
    if isinstance(value, np.generic) and not value.dtype.hasobject:
        if value.dtype.metadata:
            _unsupported(value, path + ".dtype.metadata")
        return value.copy()
    identity = id(value)
    if identity in active:
        raise ValueError(f"Cyclic export content at {path}.")
    if identity in memo:
        return memo[identity][1]
    active.add(identity)
    try:
        clone = lambda item, suffix: _clone_graph(item, memo, active, path + suffix, readonly_arrays=readonly_arrays)
        if isinstance(value, Mapping):
            result = {clone(key, ".<key>"): clone(item, f"[{key!r}]") for key, item in value.items()}
        elif isinstance(value, (list, tuple)):
            items = [clone(item, f"[{position}]") for position, item in enumerate(value)]
            result = items if isinstance(value, list) else tuple(items)
        elif isinstance(value, bytearray):
            result = bytearray(value)
        elif isinstance(value, memoryview):
            # Preserve byte content and format while detaching its backing store.
            storage = bytes(value) if readonly_arrays else bytearray(value)
            result = memoryview(storage)
            if value.format != "B" or value.shape != (len(storage),):
                result = result.cast(value.format, shape=value.shape)
        elif isinstance(value, np.ndarray):
            if type(value) is not np.ndarray:
                _unsupported(value, path)
            if value.dtype.metadata:
                _unsupported(value, path + ".dtype.metadata")
            if value.dtype.hasobject:
                result = np.empty(value.shape, dtype=value.dtype)
                if value.dtype.names:
                    for name in value.dtype.names:
                        result[name] = clone(value[name], f"[{name!r}]")
                else:
                    for position, item in enumerate(value.flat):
                        result.flat[position] = clone(item, f".flat[{position}]")
                if readonly_arrays:
                    result.flags.writeable = False
            elif readonly_arrays:
                result = np.frombuffer(value.tobytes(order="C"), dtype=value.dtype).reshape(value.shape)
            else:
                result = value.copy()
        elif isinstance(value, pd.Index):
            result = _clone_index(value, clone)
        elif isinstance(value, pd.DataFrame):
            attributes = clone(value.attrs, ".attrs")
            result = value.copy(deep=True)
            result.index = clone(value.index, ".index")
            result.columns = clone(value.columns, ".columns")
            for position in range(len(value.columns)):
                column = value.iloc[:, position]
                if isinstance(column.dtype, pd.CategoricalDtype):
                    categories = clone(column.cat.categories, f".column[{position}].categories")
                    categorical = pd.Categorical.from_codes(column.cat.codes.to_numpy(copy=True), categories=categories, ordered=column.cat.ordered)
                    result.isetitem(position, categorical)
                elif pd.api.types.is_object_dtype(column.dtype):
                    if pd.api.types.infer_dtype(column.to_numpy(copy=False), skipna=False) in {"string", "bytes"}:
                        # Deep frame copying already owns the object-pointer
                        # buffer, and homogeneous text/bytes cells are immutable.
                        continue
                    objects = np.empty(len(column), dtype=object)
                    for row, item in enumerate(column):
                        objects[row] = clone(item, f".column[{position}][{row}]")
                    # Passing a bare object ndarray lets newer Pandas infer a
                    # string/numeric dtype. The declared Series dtype preserves
                    # the caller's schema as well as its detached cell values.
                    result.isetitem(
                        position, pd.Series(objects, index=result.index, dtype=column.dtype),
                    )
            result.attrs = attributes
        else:
            _unsupported(value, path)
        memo[identity] = (value, result)
        return result
    finally:
        active.remove(identity)


@dataclass(frozen=True, slots=True, init=False)
class OwnedExportContent:
    """An isolated export snapshot with a cached digest and no raw-data accessor."""

    signature: str
    _content: Any = field(repr=False, compare=False)

    @classmethod
    def capture(cls, value: Any) -> "OwnedExportContent":
        """Detach caller-owned content once and fingerprint that owned graph."""
        content = _clone_graph(value, {}, set(), "$", readonly_arrays=True)
        snapshot = object.__new__(cls)
        object.__setattr__(snapshot, "_content", content)
        object.__setattr__(snapshot, "signature", content_signature(content))
        return snapshot

    def materialize(self) -> Any:
        """Return an independent mutable graph for one export preparation."""
        return _clone_graph(self._content, {}, set(), "$", readonly_arrays=False)

    def keys(self) -> tuple:
        """Return immutable top-level keys without copying their payloads."""
        if not isinstance(self._content, Mapping):
            raise TypeError("Export content keys require a top-level mapping.")
        return tuple(self._content)

    def materialize_field(self, key) -> Any:
        """Copy only one requested top-level field for a compatibility reader."""
        if not isinstance(self._content, Mapping):
            raise TypeError("Export content fields require a top-level mapping.")
        return _clone_graph(
            self._content[key], {}, set(), f"$[{key!r}]", readonly_arrays=False,
        )


__all__ = ["OwnedExportContent", "content_signature"]
