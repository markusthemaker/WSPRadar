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


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "site" / "assets" / "landing"
SOURCE = ASSETS / "source"
HEADER = SOURCE / "hero" / "WSPR-Insights-Across-Earth.png"
NETWORK = SOURCE / "hero" / "Europe-signal-paths-art-transparent.png"
LOGO = SOURCE / "brand" / "WSPRadar-radar-emblem-concept.png"
HANDWRITING_FONT = SOURCE / "fonts" / "Caveat-variable.ttf"
HANDWRITING_LICENSE = SOURCE / "fonts" / "Caveat-OFL.txt"
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


def payload() -> dict[str, bytes]:
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
        "path_base": "site/assets/landing",
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
    outputs["manifest.json"] = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check reproducible output without writing files")
    args = parser.parse_args()
    if not features.check("webp"):
        raise SystemExit("Pillow must include WebP support")
    outputs = payload()
    for relative, data in outputs.items():
        path = ASSETS / relative
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
