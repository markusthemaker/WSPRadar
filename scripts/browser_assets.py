"""Materialize reviewed browser assets from bounded source files and recipes.

Recipe outputs are cached by source bytes, encoding settings, and tool versions.
The cache is disposable; a clean build recreates every declared derivative.
Assets without a complete reviewed recipe retain an explicit encoded master.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "source"
CACHE_ROOT = ROOT / ".tmp" / "browser-assets"


def bounded_path(root: Path, relative: str) -> Path:
    """Resolve a portable relative path without allowing a source escape."""
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise ValueError("Invalid browser asset path: " + repr(relative))
    candidate = PurePosixPath(relative)
    result = (root / relative).resolve()
    if candidate.is_absolute() or ".." in candidate.parts or ":" in relative or not result.is_relative_to(root.resolve()):
        raise ValueError("Unsafe browser asset path: " + relative)
    return result


def signature(payload: bytes) -> dict[str, object]:
    return {"bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}


def verify(payload: bytes, record: dict, label: str) -> None:
    if signature(payload) != {key: record[key] for key in ("bytes", "sha256")}:
        raise ValueError("Browser asset hash mismatch: " + label)


def tool_versions(kind: str) -> dict[str, str | None]:
    if kind == "image":
        from PIL import __version__, features

        return {"Pillow": __version__, "WebP": features.version("webp")}
    if kind == "font_subset":
        from fontTools import __version__

        return {"FontTools": __version__}
    raise ValueError("Unsupported browser asset recipe: " + kind)


def encode_recipe(source: bytes, recipe: dict) -> bytes:
    """Execute explicit presentation transformations without scientific changes."""
    kind = recipe["kind"]
    buffer = io.BytesIO()
    if kind == "image":
        from PIL import Image

        allowed = {"kind", "source_path", "source_sha256", "source_bytes", "width", "height", "format", "mode", "quality", "lossless", "method", "exact", "optimize"}
        if set(recipe) - allowed:
            raise ValueError("Unknown image recipe field")
        width, height = recipe["width"], recipe["height"]
        if any(type(value) is not int or value < 1 for value in (width, height)):
            raise ValueError("Browser image dimensions must be positive integers")
        if recipe["format"] not in {"WEBP", "PNG"}:
            raise ValueError("Unsupported browser image format")
        with Image.open(io.BytesIO(source)) as original:
            original.load()
            if width > original.width or height != round(original.height * width / original.width):
                raise ValueError("Browser image recipe must retain aspect ratio without upscaling")
            if "mode" in recipe:
                if recipe["mode"] not in {"RGB", "RGBA"}:
                    raise ValueError("Unsupported browser image conversion")
                original = original.convert(recipe["mode"])
            image = original.resize((width, height), Image.Resampling.LANCZOS)
            options = {key: recipe[key] for key in ("quality", "lossless", "method", "exact", "optimize") if key in recipe}
            image.save(buffer, recipe["format"], **options)
            if recipe.get("lossless"):
                with Image.open(io.BytesIO(buffer.getvalue())) as decoded:
                    if decoded.convert("RGBA").tobytes() != image.convert("RGBA").tobytes():
                        raise ValueError("Lossless browser encoding changed resized pixels")
    elif kind == "font_subset":
        from fontTools import subset
        from fontTools.ttLib import TTFont
        from fontTools.varLib.instancer import instantiateVariableFont

        allowed = {"kind", "source_path", "source_sha256", "source_bytes", "axes", "unicode_ranges"}
        if set(recipe) - allowed:
            raise ValueError("Unknown font recipe field")
        font = TTFont(io.BytesIO(source), recalcTimestamp=False)
        try:
            instantiateVariableFont(font, recipe["axes"], inplace=True)
            options = subset.Options()
            options.recalc_timestamp = False
            subsetter = subset.Subsetter(options=options)
            characters = set()
            for start, end in recipe["unicode_ranges"]:
                if type(start) is not int or type(end) is not int or not 0 <= start < end <= 0x110000:
                    raise ValueError("Invalid font Unicode range")
                characters.update(range(start, end))
            subsetter.populate(unicodes=characters)
            subsetter.subset(font)
            font.save(buffer)
        finally:
            font.close()
    else:
        raise ValueError("Unsupported browser asset recipe: " + kind)
    return buffer.getvalue()


def resource_payload(resource_root: Path, manifest: dict, *, source_root: Path | None = None, rebuild: bool = False, cache_root: Path | None = None) -> dict[str, bytes]:
    """Return the allowlisted public payload; never write inside source/."""
    source_root = SOURCE_ROOT if source_root is None else Path(source_root)
    cache_root = CACHE_ROOT if cache_root is None else Path(cache_root)
    output = {}
    for record in manifest["files"]:
        name = record["path"]
        bounded_path(resource_root, name)
        if name in output:
            raise ValueError("Duplicate browser asset: " + name)
        recipe = record.get("recipe")
        if recipe is None:
            source = bounded_path(source_root, record["source_path"]) if "source_path" in record else bounded_path(resource_root, name)
            payload = source.read_bytes()
        else:
            source = bounded_path(source_root, recipe["source_path"]).read_bytes()
            verify(source, {"bytes": recipe["source_bytes"], "sha256": recipe["source_sha256"]}, recipe["source_path"])
            descriptor = {"recipe": recipe, "tools": tool_versions(recipe["kind"]), "cache_schema": 1}
            key = hashlib.sha256(json.dumps(descriptor, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
            cached = cache_root / key
            payload = cached.read_bytes() if not rebuild and cached.is_file() else None
            if payload is None or signature(payload) != {key: record[key] for key in ("bytes", "sha256")}:
                payload = encode_recipe(source, recipe)
                verify(payload, record, name)
                cache_root.mkdir(parents=True, exist_ok=True)
                with tempfile.NamedTemporaryFile(dir=cache_root, prefix=key + ".", delete=False) as temporary:
                    temporary.write(payload)
                    temporary_path = Path(temporary.name)
                try:
                    os.replace(temporary_path, cached)
                finally:
                    temporary_path.unlink(missing_ok=True)
        verify(payload, record, name)
        output[name] = payload
    return output
