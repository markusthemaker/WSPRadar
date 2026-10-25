"""Rebuild lossless browser previews from the retained Demo #1 RC3 PNG exports.

This is an asset preparation recipe, not a scientific figure generator. The eight
native PNGs and their existing hashes are authoritative and never rewritten.
"""

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

try:
    from .browser_assets import resource_payload
except ImportError:
    from browser_assets import resource_payload


ROOT = Path(__file__).resolve().parents[1]
RESOURCE_ROOT = ROOT / "source/assets/demos/griffiths_squibb_fig3"
OUTPUT = ROOT / "generated/assets/demos/griffiths_squibb_fig3"
MANIFEST = RESOURCE_ROOT / "manifest.json"
KEY_PREFIX = "rc3-demo1-"


def fingerprint(path):
    payload = path.read_bytes()
    return {"bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}


def payload(*, rebuild=False):
    """Materialize the reviewed recipes without rewriting the source manifest."""
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    records = {entry["path"]: entry for entry in manifest["files"]}
    figures = [entry for entry in manifest["figures"] if entry["key"].startswith(KEY_PREFIX)]
    if len(figures) != 8:
        raise ValueError("Expected the eight reviewed Demo #1 RC3 figures")

    selected = set()
    # Verify reviewed sources before preparing any generated previews.
    for figure in figures:
        source = RESOURCE_ROOT / figure["path"]
        declared = records[figure["path"]]
        if fingerprint(source) != {key: declared[key] for key in ("bytes", "sha256")}:
            raise ValueError("Native figure differs from the reviewed export: " + figure["path"])
        with Image.open(source) as original:
            if original.size != (figure["width"], figure["height"]):
                raise ValueError("Native figure dimensions differ from the reviewed export")
        selected.add(figure["path"])
        selected.update(variant["path"] for variant in figure["variants"])
    return resource_payload(RESOURCE_ROOT, {"files": [record for record in manifest["files"] if record["path"] in selected]}, rebuild=rebuild)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check generated previews without changing source files")
    parser.add_argument("--rebuild", action="store_true", help="Re-encode recipes without using the disposable browser asset cache")
    args = parser.parse_args()
    outputs = payload(rebuild=args.rebuild)
    for relative, data in outputs.items():
        destination = OUTPUT / relative
        if args.check:
            if not destination.is_file() or destination.read_bytes() != data:
                raise ValueError("Generated Demo #1 asset is missing or stale: " + relative)
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
    print(f"{'Verified' if args.check else 'Prepared'} {len(outputs)} reviewed Demo #1 assets.")


if __name__ == "__main__":
    main()
