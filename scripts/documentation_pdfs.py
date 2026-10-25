"""Verify pre-generated documentation downloads without importing the app renderer."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import stat


PDF_NAMES = {"WSPRadar_Doc_EN.pdf": "en", "WSPRadar_Doc_DE.pdf": "de"}
_RECORD_FIELDS = {
    "bytes", "sha256", "language", "manual_sha256", "app_version", "render_key",
}


# These exact inventories cover published legacy PDFs and the relocated manual
# renderer. Keep the current catalog aligned with WSPRadarApp/localization/sources.py
# without importing private application code into the static website build.
_CATALOG_SOURCE_FILES = frozenset({
    "i18n.py",
    "localization/__init__.py",
    "localization/sources.py",
    "localization/catalogs.py",
    "localization/key_order.py",
    "localization/common_en.py",
    "localization/common_de.py",
    "localization/inputs_en.py",
    "localization/inputs_de.py",
    "localization/results_en.py",
    "localization/results_de.py",
    "localization/figures_en.py",
    "localization/figures_de.py",
    "localization/inspector_en.py",
    "localization/inspector_de.py",
    "localization/exports_en.py",
    "localization/exports_de.py",
    "localization/guided_inputs_en.py",
    "localization/guided_inputs_de.py",
    "localization/result_guidance_en.py",
    "localization/result_guidance_de.py",
})
_SUPPORTED_RENDERER_SOURCES = (
    frozenset({"docs/pdf_generator.py", "i18n.py"}),
    frozenset({"docs/manual/pdf_generator.py", "i18n.py"}),
    frozenset({"docs/manual/pdf_generator.py", *_CATALOG_SOURCE_FILES}),
)


def _sha256(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _source_type(path: Path, *, directory: bool = False) -> None:
    """Reject links and Windows reparse points before opening any source file."""
    try:
        metadata = path.lstat()
    except OSError as error:
        raise ValueError("Missing documentation PDF source: " + str(path)) from error
    if (stat.S_ISLNK(metadata.st_mode)
            or getattr(metadata, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT):
        raise ValueError("Documentation PDF links and junctions are forbidden: " + str(path))
    expected = stat.S_ISDIR if directory else stat.S_ISREG
    if not expected(metadata.st_mode):
        raise ValueError("Invalid documentation PDF source type: " + str(path))


def _renderer_identity(identity: object) -> dict:
    if (not isinstance(identity, dict)
            or set(identity) != {"logo_sha256", "renderer"}):
        raise ValueError("Invalid documentation PDF renderer identity")
    renderer = identity["renderer"]
    if (not _sha256(identity["logo_sha256"])
            or not isinstance(renderer, dict)
            or set(renderer) != {"source_sha256", "dependencies", "fonts_sha256"}):
        raise ValueError("Invalid documentation PDF renderer identity")
    for key in ("source_sha256", "fonts_sha256"):
        hashes = renderer[key]
        if (not isinstance(hashes, dict) or not hashes
                or any(not isinstance(name, str) or not name or not _sha256(value)
                       for name, value in hashes.items())):
            raise ValueError("Invalid documentation PDF renderer hashes")
    if frozenset(renderer["source_sha256"]) not in _SUPPORTED_RENDERER_SOURCES:
        raise ValueError("Invalid documentation PDF renderer sources")
    versions = renderer["dependencies"]
    if (not isinstance(versions, dict) or "python" not in versions
            or any(not isinstance(name, str) or not name
                   or not isinstance(version, str) or not version
                   for name, version in versions.items())):
        raise ValueError("Invalid documentation PDF renderer dependencies")
    return renderer


def documentation_pdf_files(
    directory: Path, manuals: dict[str, str], app_version: str,
) -> dict[str, bytes]:
    """Publish only complete PDFs matching the exact imported manuals and version.

    Renderer/font metadata is checked for internal consistency. Canonical renderer
    freshness belongs to the app exporter; a static website build needs no private
    application sources or PDF rendering dependencies. Schema 2 binds each
    language to its own renderer identity so a reviewed translation can retain
    its original PDF bytes while another language is regenerated.
    """
    if (set(manuals) != {"en", "de"}
            or any(not isinstance(value, str) for value in manuals.values())
            or not isinstance(app_version, str) or not app_version):
        raise ValueError("Invalid imported documentation PDF identity")
    directory = directory.absolute()
    for ancestor in reversed((directory, *directory.parents)):
        _source_type(ancestor, directory=True)
    expected = {"manifest.json", *PDF_NAMES}
    if {path.name for path in directory.iterdir()} != expected:
        raise ValueError("Unexpected or missing documentation PDF source inventory")
    for name in expected:
        _source_type(directory / name)
    try:
        manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError("Invalid documentation PDF manifest") from error
    if (not isinstance(manifest, dict)
            or type(manifest.get("schema_version")) is not int
            or manifest["schema_version"] not in (1, 2)
            or not isinstance(manifest.get("files"), dict)
            or set(manifest["files"]) != set(PDF_NAMES)):
        raise ValueError("Invalid documentation PDF manifest")
    if manifest["schema_version"] == 1:
        if set(manifest) != {"schema_version", "logo_sha256", "renderer", "files"}:
            raise ValueError("Invalid documentation PDF manifest")
        identity = {key: manifest[key] for key in ("logo_sha256", "renderer")}
        renderers = {language: identity for language in PDF_NAMES.values()}
    else:
        if (set(manifest) != {"schema_version", "renderers", "files"}
                or not isinstance(manifest["renderers"], dict)
                or set(manifest["renderers"]) != set(PDF_NAMES.values())):
            raise ValueError("Invalid documentation PDF manifest renderer inventory")
        renderers = manifest["renderers"]
    for identity in renderers.values():
        _renderer_identity(identity)
    output = {}
    for name, language in PDF_NAMES.items():
        record = manifest["files"][name]
        if (not isinstance(record, dict) or set(record) != _RECORD_FIELDS
                or type(record["bytes"]) is not int or record["bytes"] < 1
                or not all(_sha256(record[key]) for key in ("sha256", "manual_sha256", "render_key"))
                or record["language"] != language):
            raise ValueError("Invalid documentation PDF record: " + name)
        manual_hash = hashlib.sha256(manuals[language].encode("utf-8")).hexdigest()
        if record["manual_sha256"] != manual_hash or record["app_version"] != app_version:
            raise ValueError("Stale documentation PDF manual or app version: " + name)
        identity = {
            "language": language, "manual_sha256": manual_hash, "app_version": app_version,
            "logo_sha256": renderers[language]["logo_sha256"],
            "renderer": renderers[language]["renderer"],
        }
        identity_bytes = (json.dumps(identity, ensure_ascii=False, indent=2, sort_keys=True,
                                     allow_nan=False) + "\n").encode("utf-8")
        if record["render_key"] != hashlib.sha256(identity_bytes).hexdigest():
            raise ValueError("Documentation PDF render identity mismatch: " + name)
        payload = (directory / name).read_bytes()
        if (len(payload) != record["bytes"]
                or hashlib.sha256(payload).hexdigest() != record["sha256"]):
            raise ValueError("Documentation PDF hash mismatch: " + name)
        if not payload.startswith(b"%PDF-"):
            raise ValueError("Documentation PDF signature missing: " + name)
        output["assets/documentation/" + name] = payload
    return output
