"""Owned export snapshots and their cheap, read-only registration index.

Borrowed payloads are validated by the export adapter before reaching this
module. Registered content is detached from callers; projecting a field or a
complete block always returns independent mutable content for legacy renderers.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from ui.export_content import OwnedExportContent, content_signature


MAP_EXPORT_FIELDS = frozenset({
    "analysis_id", "title", "mode_folder", "is_compare", "is_sequential",
    "analysis_kind", "performance_method_version", "decode_filter_mode",
    "database_source", "map_context",
})


def split_export_block(block: Mapping) -> tuple[dict, dict]:
    """Separate the independently registered map and Inspector projections."""
    return (
        {key: value for key, value in block.items() if key in MAP_EXPORT_FIELDS},
        {key: value for key, value in block.items() if key not in MAP_EXPORT_FIELDS},
    )


@dataclass(frozen=True, slots=True)
class RegisteredExportBlock(Mapping):
    """One result family with immutable, independently replaceable content."""

    map_content: OwnedExportContent
    inspector_content: OwnedExportContent

    @classmethod
    def capture(cls, block: Mapping) -> RegisteredExportBlock:
        map_fields, inspector_fields = split_export_block(block)
        return cls(
            OwnedExportContent.capture(map_fields),
            OwnedExportContent.capture(inspector_fields),
        )

    @property
    def signature(self) -> str:
        return content_signature((
            self.map_content.signature, self.inspector_content.signature,
        ))

    def replace(self, fields: dict, *, is_map: bool) -> RegisteredExportBlock:
        """Rehash borrowed inputs, avoiding allocation when contents agree."""
        previous = self.map_content if is_map else self.inspector_content
        if content_signature(fields) == previous.signature:
            return self
        replacement = OwnedExportContent.capture(fields)
        return RegisteredExportBlock(
            replacement if is_map else self.map_content,
            self.inspector_content if is_map else replacement,
        )

    def __getitem__(self, key):
        owner = self.map_content if key in MAP_EXPORT_FIELDS else self.inspector_content
        return owner.materialize_field(key)

    def __iter__(self):
        return iter((*self.map_content.keys(), *self.inspector_content.keys()))

    def __len__(self):
        return len(self.map_content.keys()) + len(self.inspector_content.keys())

    def materialize(self) -> dict:
        return {
            **self.map_content.materialize(),
            **self.inspector_content.materialize(),
        }

    def __deepcopy__(self, memo):
        # The content owners never expose mutable internal storage.
        return self


class ExportRegistry(Mapping):
    """Session-owned index; only the export adapter commits replacements."""

    def __init__(self, blocks: Mapping = ()):
        self._blocks = {
            key: block if isinstance(block, RegisteredExportBlock)
            else RegisteredExportBlock.capture(block)
            for key, block in dict(blocks).items()
        }

    def __getitem__(self, key):
        return self._blocks[key]

    def __iter__(self):
        return iter(self._blocks)

    def __len__(self):
        return len(self._blocks)

    def commit(self, analysis_id: str, block: RegisteredExportBlock) -> None:
        self._blocks[analysis_id] = block


@dataclass(frozen=True, slots=True)
class ExportPackagePayload:
    """Exact owned request carried through admission, rendering and publication."""

    blocks: tuple[tuple[str, RegisteredExportBlock], ...]
    config_bytes: bytes
    translations: OwnedExportContent
    language: str
    run_id: int
    signature: str
    exported_utc: str
    root_folder: str

    def materialize_blocks(self) -> dict:
        return {key: block.materialize() for key, block in self.blocks}
