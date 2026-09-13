"""Export content owns caller aliases and fingerprints complete retained values."""

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ui.export_content import OwnedExportContent, content_signature


def _mixed_frame():
    frame = pd.DataFrame(
        {
            "count": pd.Series([2**60 + 1, pd.NA], dtype="Int64"),
            "measurement": pd.Series([-12.5, pd.NA], dtype="Float64"),
            "outcome": pd.Categorical(
                ["joint", "target"], categories=["target", "joint", "reference"],
                ordered=True,
            ),
            "utc": pd.to_datetime(["2026-09-01T12:00:00Z", "2026-09-01T12:02:00Z"]),
            "station": pd.Series(["A1AAA", "B2BBB"], dtype="string"),
        }
    )
    frame.index = pd.Index([11, 29], name="row")
    frame.columns.name = "measurements"
    frame.attrs = {"units": {"measurement": "dB"}}
    return frame


def test_capture_and_materialize_isolate_nested_tables_recipes_and_arrays():
    shared_context = {"labels": ["original"], "values": np.array([3, 4])}
    table = pd.DataFrame({"snr": [-12.25], "context": [shared_context]})
    table.attrs = {"notes": ["retained"]}
    array = np.array([1.25, -2.5], dtype=np.float64)
    object_array = np.empty(2, dtype=object)
    object_array[:] = [shared_context, ["second"]]
    source = {
        "table": table,
        "recipe": {"array": array, "profile": [shared_context]},
        "object_array": object_array,
        "compressed": {"dtype": "<i8", "shape": (2,), "payload": b"compressed"},
    }
    original_signature = content_signature(source)
    owned = OwnedExportContent.capture(source)
    assert owned.signature == original_signature

    array[0] = 99
    shared_context["labels"].append("caller edit")
    shared_context["values"][0] = 99
    table.loc[0, "snr"] = 99
    table.attrs["notes"].append("caller edit")
    object_array[1].append("caller edit")

    first = owned.materialize()
    assert first["table"].loc[0, "snr"] == -12.25
    assert first["table"].loc[0, "context"]["labels"] == ["original"]
    assert first["table"].attrs == {"notes": ["retained"]}
    np.testing.assert_array_equal(first["recipe"]["array"], [1.25, -2.5])
    np.testing.assert_array_equal(first["object_array"][0]["values"], [3, 4])
    assert first["object_array"][1] == ["second"]
    assert first["recipe"]["profile"][0] is first["table"].loc[0, "context"]
    assert content_signature(first) == original_signature

    first["recipe"]["array"][0] = 500
    first["table"].loc[0, "context"]["labels"].append("reader edit")
    first["object_array"][1].append("reader edit")
    first["table"].attrs["notes"].append("reader edit")
    second = owned.materialize()
    assert content_signature(second) == original_signature
    assert second["table"] is not first["table"]
    assert second["recipe"]["array"].flags.writeable
    assert owned.signature == original_signature
    with pytest.raises(FrozenInstanceError):
        owned.signature = "changed"


def test_mixed_dataframe_roundtrip_preserves_dtypes_categories_timezones_and_labels():
    original = _mixed_frame()
    owned = OwnedExportContent.capture(original)
    restored = owned.materialize()
    pd.testing.assert_frame_equal(restored, original)
    assert restored.attrs == original.attrs
    assert content_signature(restored) == owned.signature == content_signature(original)

    original.index = pd.Index([100, 200], name="changed")
    original.columns = ["a", "b", "c", "d", "e"]
    pd.testing.assert_frame_equal(owned.materialize(), _mixed_frame())


def test_multiindex_and_object_tuple_labels_roundtrip():
    frame = pd.DataFrame(
        [[1.25, 2.5], [3.75, 5.0]],
        index=pd.MultiIndex.from_tuples(
            [("A1AAA", "AA00"), ("B2BBB", "BB11")], names=["call", "locator"],
        ),
        columns=pd.Index([("snr", "target"), ("snr", "reference")], tupleize_cols=False),
    )
    owned = OwnedExportContent.capture(frame)
    restored = owned.materialize()
    pd.testing.assert_frame_equal(restored, frame)
    assert content_signature(restored) == content_signature(frame) == owned.signature


def test_duplicate_column_labels_retain_every_typed_column_and_value():
    frame = pd.concat(
        [
            pd.Series([1.25, 2.5], dtype="float64"),
            pd.Series(["A1AAA", "B2BBB"], dtype=object),
            pd.Series([2**60 + 1, pd.NA], dtype="Int64"),
        ],
        axis=1,
    )
    frame.columns = ["sample", "sample", "sample"]
    signature = content_signature(frame)
    owned = OwnedExportContent.capture(frame)
    pd.testing.assert_frame_equal(owned.materialize(), frame)
    assert owned.signature == signature
    for position, changed_value in enumerate([1.5, "C3CCC", 2**60 + 2]):
        changed = frame.copy(deep=True)
        changed.iat[0, position] = changed_value
        assert content_signature(changed) != signature
    empty = frame.iloc[:0]
    assert OwnedExportContent.capture(empty).signature == content_signature(empty)


@pytest.mark.parametrize("values", [["A1AAA", "B2BBB"], [1, 2], [1.25, 2.5]])
def test_homogeneous_object_columns_keep_their_explicit_dtype(values):
    frame = pd.DataFrame({"value": pd.Series(values, dtype=object)})
    owned = OwnedExportContent.capture(frame)
    restored = owned.materialize()
    pd.testing.assert_frame_equal(restored, frame)
    assert content_signature(frame) == owned.signature == content_signature(restored)


@pytest.mark.parametrize(
    "alter",
    [
        lambda frame: frame.assign(count=pd.Series([2**60 + 2, pd.NA], index=frame.index, dtype="Int64")),
        lambda frame: frame.rename(columns={"count": "new count"}),
        lambda frame: frame.iloc[::-1],
        lambda frame: frame[["station", "utc", "outcome", "measurement", "count"]],
        lambda frame: frame.astype({"count": "Float64"}),
        lambda frame: frame.rename_axis("different row name"),
    ],
    ids=["integer-precision", "column-label", "row-order", "column-order", "dtype", "index-name"],
)
def test_dataframe_signatures_cover_values_dtype_schema_and_order(alter):
    original = _mixed_frame()
    assert content_signature(alter(original)) != content_signature(original)


@pytest.mark.parametrize(
    ("first", "second"),
    [
        (np.array([1, 2], dtype=np.int32), np.array([1, 2], dtype=np.int64)),
        (np.array([[1, 2]], dtype=np.int64), np.array([1, 2], dtype=np.int64)),
        (np.array([1.0, 2.0]), np.array([1.0, np.nextafter(2.0, 3.0)])),
        (np.array([0.0, np.nan]), np.array([-0.0, np.nan])),
        ({"counts": [1, 2]}, {"counts": [2, 1]}),
        ({"a": 1, "b": 2}, {"b": 2, "a": 1}),
        ((1, 2), [1, 2]),
    ],
    ids=["array-dtype", "array-shape", "precision", "signed-zero", "sequence-order", "mapping-order", "sequence-type"],
)
def test_signatures_cover_nested_wire_content(first, second):
    assert content_signature(first) != content_signature(second)


def test_equal_content_has_equal_signature_without_reusing_mutable_source_identity():
    original = {"frame": _mixed_frame(), "array": np.arange(12).reshape(3, 4)}
    independent = {"frame": _mixed_frame(), "array": np.arange(12).reshape(3, 4)}
    assert content_signature(original) == content_signature(independent)
    before = content_signature(original)
    original["array"][2, 3] += 1
    assert content_signature(original) != before


def test_text_mapping_fingerprint_preserves_order_unicode_and_snapshot_equality():
    source = {
        "Überschrift": "Funkweg Δ SNR",
        "escaped": 'quote " and slash \\ and newline\n',
        "astral": "\U0001f4e1",
        "literal_surrogate": "\ud800",
    }
    signature = content_signature(source)
    owned = OwnedExportContent.capture(source)
    assert owned.signature == signature == content_signature(dict(source))
    assert owned.materialize() == source
    assert owned.keys() == tuple(source)
    assert content_signature(dict(reversed(list(source.items())))) != signature
    assert content_signature(list(source.items())) != signature
    assert content_signature({"text": "\U0001f4e1"}) != content_signature(
        {"text": "\ud83d\udce1"}
    )


def test_noncontiguous_arrays_and_nan_payloads_keep_exact_values():
    values = np.arange(30, dtype=np.float64).reshape(5, 6)[:, ::2]
    special = np.array([0x7FF8000000000001, 0x7FF8000000000002], dtype=np.uint64).view(np.float64)
    source = {"values": values, "special": special}
    owned = OwnedExportContent.capture(source)
    restored = owned.materialize()
    np.testing.assert_array_equal(restored["values"], values)
    np.testing.assert_array_equal(restored["special"].view(np.uint64), special.view(np.uint64))
    assert owned.signature == content_signature(source)
    assert content_signature(special[:1]) != content_signature(special[1:])


def test_datetime_paths_and_compressed_bytes_roundtrip():
    source = {
        "created": datetime(2026, 9, 1, tzinfo=timezone.utc),
        "sample": pd.Timestamp("2026-09-01T12:00:00.123456789", tz="Europe/Berlin"),
        "path": Path("cache") / "analysis.parquet",
        "compressed": {"encoding": "zlib", "dtype": "<f8", "shape": (2, 2), "payload": b"\x00\x01\xff"},
    }
    owned = OwnedExportContent.capture(source)
    assert owned.materialize() == source
    assert owned.signature == content_signature(source)


def test_field_projection_and_cached_signature_do_not_copy_unrequested_tables(monkeypatch):
    owned = OwnedExportContent.capture({"table": _mixed_frame(), "recipe": {"labels": ["SNR"]}})

    def reject_table_copy(*_args, **_kwargs):
        raise AssertionError("Small field reads must not materialize the table.")

    monkeypatch.setattr(pd.DataFrame, "copy", reject_table_copy)
    assert owned.keys() == ("table", "recipe")
    assert len(owned.signature) == 64
    first = owned.materialize_field("recipe")
    first["labels"].append("edited")
    assert owned.materialize_field("recipe") == {"labels": ["SNR"]}
    with pytest.raises(KeyError):
        owned.materialize_field("missing")


def test_unsupported_and_cyclic_values_fail_at_their_field_boundary():
    unsupported = {"recipe": {"bad": object()}}
    with pytest.raises(TypeError, match=r"\['recipe'\]\['bad'\]"):
        OwnedExportContent.capture(unsupported)
    with pytest.raises(TypeError, match=r"\['recipe'\]\['bad'\]"):
        content_signature(unsupported)
    cyclic = []
    cyclic.append(cyclic)
    with pytest.raises(ValueError, match="Cyclic export content"):
        OwnedExportContent.capture({"recipe": cyclic})
    with pytest.raises(ValueError, match="Cyclic export content"):
        content_signature({"recipe": cyclic})
