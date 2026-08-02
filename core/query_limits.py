"""Portable SQL result-row admission guards for analysis queries."""

from __future__ import annotations

import re

from config import MAX_ANALYSIS_RESULT_ROWS


_TERMINAL_FORMAT_PATTERN = re.compile(
    r"\s+FORMAT\s+(?P<response_format>[A-Za-z][A-Za-z0-9_]*)\s*;?\s*$",
    flags=re.IGNORECASE,
)


def apply_analysis_result_row_limit(
    sql_query: str,
    *,
    max_result_rows: int | None = None,
) -> str:
    """Wrap one complete query with a max-plus-one result-row sentinel.

    The outer wrapper is required for queries containing ``UNION ALL``: the
    sentinel must cover the combined logical result, never an individual source
    branch or rows before scientific aggregation. The terminal ClickHouse
    ``FORMAT`` clause is retained exactly once outside the wrapper.
    """
    maximum_rows = (
        MAX_ANALYSIS_RESULT_ROWS
        if max_result_rows is None
        else max_result_rows
    )
    if isinstance(maximum_rows, bool) or not isinstance(maximum_rows, int):
        raise TypeError("max_result_rows must be an integer")
    if maximum_rows < 1:
        raise ValueError("max_result_rows must be positive")

    query_text = str(sql_query or "").strip()
    format_match = _TERMINAL_FORMAT_PATTERN.search(query_text)
    if format_match is None:
        raise ValueError("Analysis SQL must end with a ClickHouse FORMAT clause")
    query_body = query_text[:format_match.start()].strip()
    if not query_body:
        raise ValueError("Analysis SQL must contain a query before FORMAT")

    response_format = format_match.group("response_format")
    sentinel_rows = maximum_rows + 1
    return (
        "SELECT *\n"
        "FROM (\n"
        f"{query_body}\n"
        ")\n"
        f"LIMIT {sentinel_rows}\n"
        f"FORMAT {response_format}"
    )
