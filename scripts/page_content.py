"""Resolve website prose from named Markdown blocks without rewriting its text.

Templates keep their existing HTML rendering contracts. A catalog reference such
as {"$text": "home.en.md#landing.intro"} inserts the exact corresponding block;
inline Markdown and HTML are interpreted by the same renderers as before.
"""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
import re


BLOCK = re.compile(
    r"<!-- text: ([a-zA-Z0-9_.-]+) -->\n(.*?)\n<!-- /text -->",
    re.DOTALL,
)


def read_text_blocks(path: Path) -> dict[str, str]:
    """Reject duplicate markers and unplaced prose instead of silently losing it."""
    source = path.read_text(encoding="utf-8")
    blocks = {}
    end = 0
    for match in BLOCK.finditer(source):
        if source[end:match.start()].strip():
            raise ValueError("Unplaced page text: " + str(path))
        key, value = match.groups()
        if key in blocks:
            raise ValueError("Duplicate page text block: " + key)
        blocks[key] = value
        end = match.end()
    if not blocks or source[end:].strip():
        raise ValueError("Missing blocks or unplaced page text: " + str(path))
    return blocks


def load_catalog(path: Path, pages_root: Path):
    """Resolve explicit text references within a bounded website pages directory."""
    pages_root = pages_root.resolve()
    documents = {}

    def resolve(value):
        if isinstance(value, list):
            return [resolve(item) for item in value]
        if not isinstance(value, dict):
            return value
        if "$text" not in value:
            return {key: resolve(item) for key, item in value.items()}
        reference = value.get("$text")
        if set(value) != {"$text"} or not isinstance(reference, str):
            raise ValueError("Invalid page text reference")
        name, separator, key = reference.partition("#")
        relative = PurePosixPath(name)
        target = (pages_root / name).resolve()
        if (not separator or not key or relative.is_absolute()
                or ".." in relative.parts or "\\" in name
                or ":" in name or relative.suffix != ".md"
                or not target.is_relative_to(pages_root)):
            raise ValueError("Unsafe page text reference: " + reference)
        if name not in documents:
            documents[name] = read_text_blocks(target)
        if key not in documents[name]:
            raise ValueError("Unknown page text block: " + reference)
        return documents[name][key]

    return resolve(json.loads(path.read_text(encoding="utf-8")))
