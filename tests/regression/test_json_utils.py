"""Regression coverage for strict JSON decoder diagnostics."""

import json

import pytest

from config.json_utils import decode_strict_json_bytes


def test_invalid_json_reports_exact_line_and_column():
    """Preserve the parser's source location in the user-facing error."""
    raw_document = b'{\n  "valid": true,\n  "broken": /\n}\n'

    with pytest.raises(ValueError) as raised_error:
        decode_strict_json_bytes(
            raw_document,
            document_name="demo config example.config",
        )

    assert str(raised_error.value) == (
        "The demo config example.config contains invalid JSON at line 3, "
        "column 13: Expecting value."
    )
    assert isinstance(raised_error.value.__cause__, json.JSONDecodeError)


def test_invalid_utf8_reports_exact_line_column_and_byte_offset():
    """Locate the first invalid byte without mislabeling it as JSON syntax."""
    raw_document = b'{\n  "label": "\xc2\xb5\xff"\n}\n'

    with pytest.raises(ValueError) as raised_error:
        decode_strict_json_bytes(
            raw_document,
            document_name="uploaded config",
        )

    assert str(raised_error.value) == (
        "The uploaded config contains invalid UTF-8 at line 2, column 14 "
        "(byte offset 16)."
    )
    assert isinstance(raised_error.value.__cause__, UnicodeDecodeError)
