"""Rebuild the landing-page browser assets from the retained supplied originals.

Requires Pillow with WebP support and FontTools. This tool resizes and encodes
images and prepares a local font subset; it does not regenerate artwork or
change the English wording in the header.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path

from PIL import Image, features
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

try:
    from .browser_assets import resource_payload
except ImportError:
    from browser_assets import resource_payload


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "source" / "assets" / "landing"
SOURCE = ASSETS / "originals"
OUTPUT = ROOT / "generated" / "assets" / "landing"
HEADER = SOURCE / "hero" / "WSPR-Insights-Across-Earth.png"
NETWORK = SOURCE / "hero" / "Europe-signal-paths-art-transparent.png"
LOGO = SOURCE / "brand" / "WSPRadar-radar-emblem-concept.png"
HANDWRITING_FONT = SOURCE / "fonts" / "Caveat-variable.ttf"
HANDWRITING_LICENSE = SOURCE / "fonts" / "Caveat-OFL.txt"
FRONTPAGE_EXTENSION = SOURCE / "frontpage-update-20261018" / "integration.json"
THUMBNAIL_INTEGRATION = SOURCE / "demo1-thumbnails" / "integration.json"
HEADER_WIDTHS = (480, 768, 1280, 1600, 2172)
NETWORK_WIDTHS = (400, 700, 1000)
LOGO_WIDTHS = (64, 128)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encoded(image: Image.Image, image_format: str, **options: object) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, image_format, **options)
    return buffer.getvalue()


def resized(image: Image.Image, width: int) -> Image.Image:
    if width > image.width:
        raise ValueError(f"Refusing to upscale {image.width}px source to {width}px")
    height = round(width * image.height / image.width)
    if (width, height) == image.size:
        return image.copy()
    return image.resize((width, height), Image.Resampling.LANCZOS)


def file_record(path: str, data: bytes) -> dict[str, object]:
    return {"path": path, "bytes": len(data), "sha256": digest(data)}


def image_record(path: str, data: bytes, image: Image.Image, mime: str) -> dict[str, object]:
    return {
        **file_record(path, data),
        "width": image.width,
        "height": image.height,
        "mime_type": mime,
    }


def handwriting_font() -> bytes:
    """Keep 400-weight Latin text and punctuation, with contextual glyphs intact."""
    font = TTFont(HANDWRITING_FONT, recalcTimestamp=False)
    instantiateVariableFont(font, {"wght": 400}, inplace=True)
    options = subset.Options()
    options.recalc_timestamp = False
    subsetter = subset.Subsetter(options=options)
    subsetter.populate(unicodes=set(range(0x0250)) | set(range(0x2000, 0x2070)))
    subsetter.subset(font)
    buffer = io.BytesIO()
    font.save(buffer)
    font.close()
    return buffer.getvalue()


def reviewed_resource_path(base: Path, relative: str) -> Path:
    """Resolve a manifest-owned relative path within its declared directory."""
    candidate = Path(relative)
    path = (base / candidate).resolve()
    if candidate.is_absolute() or ".." in candidate.parts or not path.is_relative_to(base.resolve()):
        raise ValueError("Unsafe reviewed resource path: " + relative)
    return path


def evidence_records() -> dict[str, dict[str, object]]:
    """Reuse reviewed native figures and lossless previews without altering them."""
    integration = json.loads(FRONTPAGE_EXTENSION.read_text(encoding="utf-8"))
    records = {}
    for selected in integration["evidence"]:
        manifest_path = reviewed_resource_path(ROOT, selected["resource_manifest"])
        if not manifest_path.is_relative_to((ROOT / "source" / "assets" / "demos").resolve()):
            raise ValueError("Landing evidence must use website-owned demo resources")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        resources = resource_payload(manifest_path.parent, manifest)
        figure = next(item for item in manifest["figures"] if item["key"] == selected["resource_key"])
        files = {item["path"]: item for item in manifest["files"]}
        prefix = "/assets/demos/" + selected["demo_id"] + "/"

        def record(relative: str, width: int, height: int) -> dict[str, object]:
            source = reviewed_resource_path(manifest_path.parent, relative)
            data = resources[relative]
            declared = files[relative]
            if digest(data) != declared["sha256"] or len(data) != declared["bytes"]:
                raise ValueError("Reviewed landing evidence changed: " + relative)
            with Image.open(io.BytesIO(data)) as image:
                if image.size != (width, height):
                    raise ValueError("Reviewed landing evidence dimensions changed: " + relative)
            return {
                **file_record(prefix + relative, data),
                "source_path": source.relative_to(ROOT).as_posix() if source.is_file() else "generated" + prefix + relative,
                "width": width,
                "height": height,
            }

        native = record(figure["path"], figure["width"], figure["height"])
        if native["sha256"] != selected["source_sha256"]:
            raise ValueError("Landing evidence differs from its reviewed integration source")
        variants = [record(item["path"], item["width"], item["height"]) for item in figure["variants"]]
        with Image.open(io.BytesIO(resources[figure["path"]])) as original:
            original.load()
            for variant in variants:
                if variant["width"] > original.width:
                    raise ValueError("Landing previews must not upscale native evidence")
                expected = resized(original, variant["width"])
                with Image.open(io.BytesIO(resources[variant["path"].removeprefix(prefix)])) as decoded:
                    if decoded.convert("RGBA").tobytes() != expected.convert("RGBA").tobytes():
                        raise ValueError("Landing preview differs from the lossless source resize")
        records[selected["key"]] = {
            "demo_id": selected["demo_id"],
            "resource_manifest": selected["resource_manifest"],
            "resource_key": selected["resource_key"],
            "native": native,
            "images": variants,
            "alt": selected["alt"],
            "provenance": {
                **selected["provenance"],
                "source_package": integration["source_package"],
                "source_package_sha256": integration["source_package_sha256"],
                "resource_manifest_sha256": digest(manifest_path.read_bytes()),
                "resource_provenance": figure["provenance"],
            },
        }
    return records


def add_data_derived_previews(evidence, outputs):
    """Encode approved previews separately from their full scientific originals."""
    if not THUMBNAIL_INTEGRATION.is_file():
        return
    specification = json.loads(THUMBNAIL_INTEGRATION.read_text(encoding="utf-8"))
    if specification["schema_version"] != 1:
        raise ValueError("Unsupported landing thumbnail schema")
    base = THUMBNAIL_INTEGRATION.parent
    provenance_path = reviewed_resource_path(base, specification["provenance"])
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    sources = {item["path"]: item for item in provenance["figures"]}
    widths = specification["widths"]
    if not widths or any(type(width) is not int or width < 1 for width in widths) or widths != sorted(set(widths)):
        raise ValueError("Landing thumbnail widths must be ordered positive integers")
    seen = set()
    for selected in specification["previews"]:
        key = selected["media_key"]
        if key not in evidence or key in seen:
            raise ValueError("Unknown or duplicate landing thumbnail media key")
        seen.add(key)
        item = evidence[key]
        source = reviewed_resource_path(base, selected["source"])
        approved = sources[selected["source"]]
        payload = source.read_bytes()
        if digest(payload) != approved["sha256"] or len(payload) != approved["bytes"]:
            raise ValueError("Approved landing thumbnail changed: " + selected["source"])
        if approved["original_fingerprint"]["sha256"] != item["native"]["sha256"]:
            raise ValueError("Landing thumbnail no longer matches its original figure")
        for field in (selected["alt"], specification["note"]):
            if set(field) != {"en", "de"} or not all(isinstance(value, str) and value.strip() for value in field.values()):
                raise ValueError("Landing previews require English and German descriptions")
        variants = []
        with Image.open(source) as original:
            original.load()
            if original.size != (approved["width"], approved["height"]) or original.width * 3 != original.height * 4:
                raise ValueError("Approved landing thumbnails must preserve their 4:3 dimensions")
            for width in widths:
                image = resized(original.convert("RGB"), width)
                path = f"web/thumbnails/{key}-{width}.webp"
                data = encoded(image, "WEBP", lossless=True, quality=100, method=6, exact=True)
                with Image.open(io.BytesIO(data)) as decoded:
                    if decoded.convert("RGB").tobytes() != image.tobytes():
                        raise ValueError("Landing thumbnail encoding changed resized pixels")
                outputs[path] = data
                variants.append({
                    **image_record("/assets/landing/" + path, data, image, "image/webp"),
                    "source_path": (OUTPUT / path).relative_to(ROOT).as_posix(),
                })
        item["preview"] = {
            "source": {
                **file_record(source.relative_to(ASSETS).as_posix(), payload),
                "width": approved["width"], "height": approved["height"],
            },
            "images": variants,
            "alt": selected["alt"],
            "note": specification["note"],
            "provenance": {
                "scientific_recipe": provenance["recipe"],
                "approved_provenance_sha256": digest(provenance_path.read_bytes()),
                "evidence_sha256": provenance["evidence"]["sha256"],
                "canvas": provenance["canvas"],
                "encoding": "Lossless WebP; direct LANCZOS resize from the approved PNG; no upscaling",
            },
        }


def extend_manifest(manifest: dict[str, object], outputs: dict[str, bytes]) -> None:
    """Add retained frontpage evidence and icons to either build mode."""
    if not FRONTPAGE_EXTENSION.is_file():
        return
    manifest["purpose"] = "Supplied illustrative artwork, reviewed native scientific evidence, and separate browser derivatives; each asset retains its source provenance."
    manifest["evidence"] = evidence_records()
    add_data_derived_previews(manifest["evidence"], outputs)
    for source in sorted((SOURCE / "icons" / "neon").glob("*.svg")):
        path = f"web/icons/{source.name}"
        outputs[path] = source.read_bytes()
        manifest["icons"][source.stem] = path
    manifest["sources"] = [
        file_record(path.relative_to(ASSETS).as_posix(), path.read_bytes())
        for path in sorted(SOURCE.rglob("*"))
        if path.is_file()
    ]
    manifest["publish_files"] = sorted(set(manifest["publish_files"]) | set(outputs))


def extension_payload(*, rebuild: bool = False) -> dict[str, bytes]:
    """Prepare added icons and evidence previews in the generated destination."""
    return {name: data for name, data in payload(rebuild=rebuild).items() if name == "manifest.json" or name.startswith(("web/icons/", "web/thumbnails/"))}


def audit_artwork_payload() -> dict[str, bytes]:
    """Recreate the retained encoding comparison audit on explicit request."""
    outputs: dict[str, bytes] = {}
    sources = [
        file_record(path.relative_to(ASSETS).as_posix(), path.read_bytes())
        for path in sorted(SOURCE.rglob("*"))
        if path.is_file()
    ]
    comparisons: list[dict[str, object]] = []
    hero_images: list[dict[str, object]] = []
    with Image.open(HEADER) as original:
        original.load()
        for width in HEADER_WIDTHS:
            image = resized(original, width)
            path = f"web/hero-{width}.webp"
            data = encoded(image, "WEBP", quality=94, method=6)
            outputs[path] = data
            hero_images.append(image_record(path, data, image, "image/webp"))
            comparisons.append({
                "width": image.width,
                "height": image.height,
                "webp_quality_94_bytes": len(data),
                "webp_quality_90_bytes": len(encoded(image, "WEBP", quality=90, method=6)),
                "webp_lossless_bytes": len(encoded(image, "WEBP", lossless=True, method=6)),
            })
        fallback_image = resized(original, 1280)
        fallback_path = "web/hero-1280.png"
        fallback_data = encoded(fallback_image, "PNG", optimize=True)
        outputs[fallback_path] = fallback_data
        hero_fallback = image_record(fallback_path, fallback_data, fallback_image, "image/png")
    network_images: list[dict[str, object]] = []
    network_comparisons: list[dict[str, object]] = []
    with Image.open(NETWORK) as original:
        original.load()
        for width in NETWORK_WIDTHS:
            image = resized(original, width)
            path = f"web/network-{width}.webp"
            data = encoded(image, "WEBP", quality=94, method=6, exact=True)
            outputs[path] = data
            network_images.append(image_record(path, data, image, "image/webp"))
            network_comparisons.append({
                "width": image.width,
                "height": image.height,
                "webp_quality_94_bytes": len(data),
                "webp_quality_90_bytes": len(encoded(image, "WEBP", quality=90, method=6, exact=True)),
                "webp_lossless_bytes": len(encoded(image, "WEBP", lossless=True, method=6, exact=True)),
            })
        fallback_image = resized(original, 700)
        fallback_path = "web/network-700.png"
        fallback_data = encoded(fallback_image, "PNG", optimize=True)
        outputs[fallback_path] = fallback_data
        network_fallback = image_record(fallback_path, fallback_data, fallback_image, "image/png")
    logo_images: list[dict[str, object]] = []
    with Image.open(LOGO) as original:
        original.load()
        for width in LOGO_WIDTHS:
            image = resized(original, width)
            path = f"web/logo-{width}.webp"
            data = encoded(image, "WEBP", lossless=True, method=6, exact=True)
            outputs[path] = data
            logo_images.append(image_record(path, data, image, "image/webp"))
        fallback_image = resized(original, 128)
        fallback_path = "web/logo-128.png"
        fallback_data = encoded(fallback_image, "PNG", optimize=True)
        outputs[fallback_path] = fallback_data
        logo_fallback = image_record(fallback_path, fallback_data, fallback_image, "image/png")
    icons: dict[str, str] = {}
    for source in sorted((SOURCE / "icons" / "neon").glob("*.svg")):
        path = f"web/icons/{source.name}"
        outputs[path] = source.read_bytes()
        icons[source.stem] = path
    font_path = "web/fonts/caveat-hand-latin.ttf"
    font_data = handwriting_font()
    outputs[font_path] = font_data
    license_path = "web/fonts/Caveat-OFL.txt"
    outputs[license_path] = HANDWRITING_LICENSE.read_bytes()
    manifest = {
        "schema_version": 1,
        "purpose": "Supplied concept assets and separate browser derivatives; artwork is illustrative, not measured evidence.",
        "path_base": "source/assets/landing",
        "hero": {
            "source": HEADER.relative_to(ASSETS).as_posix(),
            "language": "en",
            "language_policy": "Keep the supplied English text inside the image in both website languages.",
            "encoding": {"format": "webp", "quality": 94, "method": 6, "resampling": "LANCZOS"},
            "images": hero_images,
            "fallback": hero_fallback,
            "encoding_comparison": comparisons,
        },
        "logo": {
            "source": LOGO.relative_to(ASSETS).as_posix(),
            "encoding": {"format": "webp", "lossless": True, "method": 6, "exact": True, "resampling": "LANCZOS"},
            "images": logo_images,
            "fallback": logo_fallback,
        },
        "network": {
            "source": NETWORK.relative_to(ASSETS).as_posix(),
            "purpose": "Illustrative worldwide signal paths; not measured coverage or a scientific result.",
            "encoding": {"format": "webp", "quality": 94, "method": 6, "exact": True, "resampling": "LANCZOS"},
            "images": network_images,
            "fallback": network_fallback,
            "encoding_comparison": network_comparisons,
        },
        "icons": icons,
        "fonts": {
            "handwriting": {
                **file_record(font_path, font_data),
                "family": "Caveat",
                "weight": 400,
                "style": "normal",
                "mime_type": "font/ttf",
                "source": HANDWRITING_FONT.relative_to(ASSETS).as_posix(),
                "license_path": license_path,
                "license": "OFL-1.1",
                "unicode_ranges": ["U+0000-024F", "U+2000-206F"],
                "derivation": "Static 400-weight instance with Latin, Latin Extended, and general punctuation; contextual glyph closure retained; original source timestamp preserved.",
            }
        },
        "publish_files": sorted(outputs),
        "sources": sources,
    }
    extend_manifest(manifest, outputs)
    outputs["manifest.json"] = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    return outputs


def payload(*, rebuild: bool = False, asset_root: Path | None = None, source_root: Path | None = None, cache_root: Path | None = None) -> dict[str, bytes]:
    """Build approved outputs from source recipes, using a disposable cache."""
    asset_root = ASSETS if asset_root is None else Path(asset_root)
    manifest_bytes = (asset_root / "manifest.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    outputs = resource_payload(asset_root, manifest, source_root=source_root, rebuild=rebuild, cache_root=cache_root)
    if set(outputs) != set(manifest["publish_files"]) or len(manifest["publish_files"]) != len(outputs):
        raise ValueError("Landing publication list differs from reviewed asset records")
    outputs["manifest.json"] = manifest_bytes
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check reproducible output without writing files")
    parser.add_argument("--extension-only", action="store_true", help="Prepare only added icons and evidence previews")
    parser.add_argument("--rebuild", action="store_true", help="Re-encode declared recipes without using the disposable asset cache")
    args = parser.parse_args()
    if not features.check("webp"):
        raise SystemExit("Pillow must include WebP support")
    outputs = extension_payload(rebuild=args.rebuild) if args.extension_only else payload(rebuild=args.rebuild)
    outputs.pop("manifest.json")
    for relative, data in outputs.items():
        path = OUTPUT / relative
        if args.check:
            if not path.is_file() or path.read_bytes() != data:
                raise SystemExit(f"Landing asset is missing or stale: {relative}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(f"{'Verified' if args.check else 'Prepared'} {len(outputs)} landing asset files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
