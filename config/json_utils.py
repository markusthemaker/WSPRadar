"""Strict, dependency-free JSON decoding shared by configuration readers."""

import json


def decode_strict_json_bytes(raw_bytes, *, document_name):
    """Decode strict UTF-8 JSON and report precise source locations when known."""

    def reject_duplicate_keys(pairs):
        decoded_object = {}
        for key, value in pairs:
            if key in decoded_object:
                raise ValueError(
                    f"The {document_name} contains a duplicate JSON key: {key}."
                )
            decoded_object[key] = value
        return decoded_object

    def reject_non_finite_number(value):
        raise ValueError(
            f"The {document_name} contains a non-finite JSON number: {value}."
        )

    try:
        decoded_text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        line_number = raw_bytes.count(b"\n", 0, exc.start) + 1
        line_start_offset = raw_bytes.rfind(b"\n", 0, exc.start) + 1
        valid_line_prefix = raw_bytes[line_start_offset:exc.start].decode("utf-8")
        column_number = len(valid_line_prefix) + 1
        raise ValueError(
            f"The {document_name} contains invalid UTF-8 at line {line_number}, "
            f"column {column_number} (byte offset {exc.start})."
        ) from exc

    try:
        return json.loads(
            decoded_text,
            object_pairs_hook=reject_duplicate_keys,
            parse_constant=reject_non_finite_number,
        )
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"The {document_name} contains invalid JSON at line {exc.lineno}, "
            f"column {exc.colno}: {exc.msg}."
        ) from exc
