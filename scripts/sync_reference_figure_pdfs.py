"""Publish fixture PDFs referenced by demo Markdown into Streamlit static assets.

Run after rebuilding comparison figures; use --check in verification. The demo
links are the publication list, so adding a figure needs no runtime mapping.
"""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
LINK_PREFIX = "app/static/reference_figures/"
PDF_LINK_PATTERN = re.compile(r"\]\((app/static/reference_figures/[^)\s]+)\)")
SAFE_NAME_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*\Z")


def collect_reference_pdf_paths(demo_directory):
    """Return unique, validated fixture-relative PDF paths in demo descriptions."""
    reference_paths = set()
    for config_path in sorted(Path(demo_directory).glob("*.config")):
        document = json.loads(config_path.read_text(encoding="utf-8"))
        for description in document.get("profile", {}).get("description", {}).values():
            links = PDF_LINK_PATTERN.findall(description)
            if description.count(LINK_PREFIX) != len(links):
                raise ValueError(f"Malformed reference PDF link in {config_path.name}")
            for link in links:
                relative_text = link[len(LINK_PREFIX):]
                relative_path = PurePosixPath(relative_text)
                if (
                    len(relative_path.parts) != 2
                    or relative_path.as_posix() != relative_text
                    or any(not SAFE_NAME_PATTERN.fullmatch(part)
                           for part in relative_path.parts)
                    or relative_path.suffix != ".pdf"
                ):
                    raise ValueError(f"Invalid reference PDF path: {relative_text}")
                reference_paths.add(relative_path)
    return sorted(reference_paths)


def _contained_path(root, relative_path):
    root = Path(root).resolve()
    candidate = (root / relative_path).resolve()
    if not candidate.is_relative_to(root):
        raise ValueError(f"Reference PDF escapes its root: {relative_path}")
    return candidate


def sync_reference_figure_pdfs(repository_root=REPOSITORY_ROOT, *, check=False):
    """Copy or check exactly the referenced PDFs after verifying fixture hashes."""
    repository_root = Path(repository_root)
    fixture_root = repository_root / "tests/regression/reference_fixtures"
    static_root = repository_root / "static/reference_figures"
    reference_paths = collect_reference_pdf_paths(repository_root / "config/demos")
    # Validate all source files before changing any deployed copy.
    verified_sources = []
    for relative_path in reference_paths:
        source_path = _contained_path(fixture_root, relative_path)
        source_bytes = source_path.read_bytes()
        if not source_bytes.startswith(b"%PDF-"):
            raise ValueError(f"Not a PDF: {relative_path}")
        manifest = json.loads(
            source_path.with_name("manifest.json").read_text(encoding="utf-8")
        )
        matching_entries = [entry for entry in manifest["files"]
                            if entry["path"] == source_path.name]
        if len(matching_entries) != 1 or (
            matching_entries[0]["bytes"] != len(source_bytes)
            or matching_entries[0]["sha256"] != hashlib.sha256(source_bytes).hexdigest()
        ):
            raise ValueError(f"Reference PDF does not match fixture manifest: {relative_path}")
        destination_path = _contained_path(static_root, relative_path)
        verified_sources.append((relative_path, source_path, destination_path, source_bytes))

    for relative_path, source_path, destination_path, source_bytes in verified_sources:
        if check:
            if not destination_path.is_file() or destination_path.read_bytes() != source_bytes:
                raise ValueError(f"Missing or stale published PDF: {relative_path}")
        else:
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_path, destination_path)
    return reference_paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check without copying files")
    arguments = parser.parse_args()
    reference_paths = sync_reference_figure_pdfs(check=arguments.check)
    print(f"{'Checked' if arguments.check else 'Published'} {len(reference_paths)} reference PDFs.")


if __name__ == "__main__":
    main()
