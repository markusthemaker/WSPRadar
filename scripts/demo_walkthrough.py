"""Shared demo layout with editable Markdown and explicitly reviewed resources."""

from html import escape
from pathlib import Path, PurePosixPath
import hashlib
import json
import math
import re
from urllib.parse import parse_qs, urlsplit


def demo_launch_url(config):
    """Require a reviewed full-configuration link supported by the deployed app."""
    value = config.get("launch_url", "")
    url = urlsplit(value)
    query = parse_qs(url.query)
    if (url.scheme != "https" or url.netloc != "wspradar.org" or url.path != "/"
            or query.get("v") != ["1"] or query.get("run") != ["1"]
            or not {"direction", "callsign", "qth", "band", "from", "to", "mode"}.issubset(query)
            or "demo" in query or url.fragment != "wspradar-results-inspection"):
        raise ValueError("Demo requires a reviewed full-configuration launch_url")
    return value


def safe_path(root, name):
    relative = PurePosixPath(name)
    path = (root / name).resolve()
    if relative.is_absolute() or ".." in relative.parts or "\\" in name or not path.is_relative_to(root.resolve()):
        raise ValueError("Unsafe demo source path: " + name)
    return path


def read_sections(path):
    """Markers name layout slots; their Markdown remains ordinary editable text."""
    source = path.read_text(encoding="utf-8")
    matches = list(re.finditer(r"^<!-- section: ([a-z][a-z0-9-]*) -->\s*$", source, re.MULTILINE))
    if not matches or source[:matches[0].start()].strip():
        raise ValueError("Demo Markdown must begin with a section marker: " + str(path))
    sections = {}
    for index, match in enumerate(matches):
        key = match[1]
        if key in sections:
            raise ValueError("Duplicate demo Markdown section: " + key)
        end = matches[index + 1].start() if index + 1 < len(matches) else len(source)
        sections[key] = source[match.end():end].strip()
    if not {"hero", "setup"}.issubset(sections):
        raise ValueError("Demo Markdown requires hero and setup sections")
    return sections


def heading_and_body(markdown, level):
    first, _, body = markdown.partition("\n")
    prefix = "#" * level + " "
    if not first.startswith(prefix):
        raise ValueError("Demo section must start with " + prefix + "heading")
    return first[len(prefix):], body.strip()


def resource_files(root, configurations):
    """Only hash-checked, allowlisted public resources enter the static output."""
    output = {}
    for identity, config in configurations.items():
        manifest_name = config.get("resource_manifest")
        if not manifest_name:
            continue
        manifest_path = safe_path(root, manifest_name)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for entry in manifest["files"]:
            payload = safe_path(manifest_path.parent, entry["path"]).read_bytes()
            if len(payload) != entry["bytes"] or hashlib.sha256(payload).hexdigest() != entry["sha256"]:
                raise ValueError("Demo resource hash mismatch: " + entry["path"])
            name = "assets/demos/" + identity + "/" + entry["path"]
            if name in output:
                raise ValueError("Duplicate demo resource: " + name)
            output[name] = payload
    return output


def render_demo(builder, lang, demo, config, button, route, app_url):
    copy = builder.copy[lang]
    text = config["languages"][lang]
    identity = demo["id"]
    show_hero_period = config.get("show_hero_period", True)
    if not isinstance(show_hero_period, bool):
        raise ValueError("show_hero_period must be a boolean")
    show_setup_media = config.get("show_setup_media", True)
    if not isinstance(show_setup_media, bool):
        raise ValueError("show_setup_media must be a boolean")
    if not show_setup_media and config.get("setup_media_key"):
        raise ValueError("A setup_media_key requires show_setup_media")
    sections = read_sections(safe_path(builder.demo_root, config["markdown_paths"][lang]))
    used = {"hero", "setup"}
    title, intro = heading_and_body(sections["hero"], 1)
    catalog = {
        item["key"]: (item, screenshot, False)
        for items, screenshot in ((builder.figures, False), (builder.screenshots, True))
        for item in items if item["demo_id"] == identity
    }
    if config.get("resource_manifest"):
        manifest_path = safe_path(builder.demo_root, config["resource_manifest"])
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        allowed = {item["path"] for item in manifest["files"]}
        for item in manifest.get("figures", []):
            paths = [item["path"], *(variant["path"] for variant in item.get("variants", []))]
            if item["key"] in catalog or any(path not in allowed for path in paths):
                raise ValueError("Unreviewed or duplicate demo resource figure: " + item["key"])
            catalog[item["key"]] = (item, False, True)
    excluded = set(config.get("excluded_media_keys", []))
    inverted = set(config.get("inverted_media_keys", []))
    if (excluded | inverted) - catalog.keys():
        raise ValueError("Unknown excluded or inverted demo media")
    if excluded & inverted:
        raise ValueError("Excluded demo media cannot also be inverted")
    preserved = config.get("preserved_color_regions", {})
    if set(preserved) - inverted:
        raise ValueError("Preserved color regions require an inverted media key")
    filters = {}
    filter_markup = []
    for key, regions in preserved.items():
        item = catalog[key][0]
        size = item.get("provenance", {}).get("image_px", [item.get("width"), item.get("height")])
        if regions.get("image_px") != size or not all(size):
            raise ValueError("Preserved color region image dimensions do not match")
        width, height = size
        filter_id = "case-filter-" + identity + "-" + key
        filters[key] = "url(#" + filter_id + ")"
        # The browser resamples the source before filtering. Soft brightness and
        # chroma ramps remove white backgrounds and pale blended edge pixels,
        # while keeping bright saturated data markers and the native dark ink.
        primitives = ['<feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.2126 0.7152 0.0722 0 0" result="lightness"/><feComponentTransfer in="lightness" result="bright-pixels"><feFuncA type="linear" slope="8" intercept="-6"/></feComponentTransfer>']
        for channel, name in enumerate(("red", "green", "blue")):
            matrix = [0] * 20
            for row in range(3):
                matrix[row * 5 + channel] = 1
            matrix[18] = 1
            primitives.append('<feColorMatrix in="SourceGraphic" type="matrix" values="' + " ".join(map(str, matrix)) + '" result="' + name + '-channel"/>')
        primitives.append('<feBlend in="red-channel" in2="green-channel" mode="lighten" result="maximum-rg"/><feBlend in="maximum-rg" in2="blue-channel" mode="lighten" result="maximum-rgb"/><feBlend in="red-channel" in2="green-channel" mode="darken" result="minimum-rg"/><feBlend in="minimum-rg" in2="blue-channel" mode="darken" result="minimum-rgb"/><feBlend in="maximum-rgb" in2="minimum-rgb" mode="difference" result="chroma-rgb"/><feColorMatrix in="chroma-rgb" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0" result="chroma"/><feComponentTransfer in="chroma" result="low-chroma"><feFuncA type="linear" slope="-16" intercept="2"/></feComponentTransfer><feComposite in="bright-pixels" in2="low-chroma" operator="in" result="white-background"/><feComposite in="SourceGraphic" in2="white-background" operator="out" result="native-colors"/>')
        merged = ['<feMergeNode in="inverted"/>']

        def checked_rectangle(rect):
            if len(rect) != 4 or any(not isinstance(value, (int, float)) or not math.isfinite(value) for value in rect):
                raise ValueError("Invalid preserved color rectangle")
            x, y, w, h = rect
            if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > width or y + h > height:
                raise ValueError("Preserved color rectangle outside image")
            return x, y, w, h

        preserved_rectangles = [checked_rectangle(rect) for rect in regions["rectangles_px"]]
        for index, (x, y, w, h) in enumerate(preserved_rectangles):
            bounds = f'x="{x/width:.10f}" y="{y/height:.10f}" width="{w/width:.10f}" height="{h/height:.10f}"'
            primitives.append(f'<feFlood {bounds} flood-color="white" result="mask{index}"/><feFlood {bounds} flood-color="black" result="background{index}"/><feComposite in="native-colors" in2="mask{index}" operator="in" result="original{index}"/>')
            merged.extend((f'<feMergeNode in="background{index}"/>', f'<feMergeNode in="original{index}"/>'))
        if regions.get("label_rectangles_px"):
            # Only the bounded legend needs light lettering on its dark panel;
            # scientific contours elsewhere retain their original dark colour.
            primitives.append('<feComponentTransfer in="lightness" result="dark-pixels"><feFuncA type="linear" slope="-4" intercept="2"/></feComponentTransfer><feComposite in="dark-pixels" in2="low-chroma" operator="in" result="label-ink-mask"/>')
        for index, rect in enumerate(regions.get("label_rectangles_px", [])):
            x, y, w, h = checked_rectangle(rect)
            if not any(x >= px and y >= py and x + w <= px + pw and y + h <= py + ph
                       for px, py, pw, ph in preserved_rectangles):
                raise ValueError("Legend label rectangle must be inside a preserved color rectangle")
            bounds = f'x="{x/width:.10f}" y="{y/height:.10f}" width="{w/width:.10f}" height="{h/height:.10f}"'
            primitives.append(f'<feFlood {bounds} flood-color="#b9c8d6" result="label-base{index}"/><feComposite in="label-base{index}" in2="label-ink-mask" operator="in" result="label-ink{index}"/>')
            merged.append(f'<feMergeNode in="label-ink{index}"/>')
        filter_markup.append('<filter id="' + escape(filter_id, quote=True) + '" x="0" y="0" width="1" height="1" filterUnits="objectBoundingBox" primitiveUnits="objectBoundingBox" color-interpolation-filters="sRGB"><feComponentTransfer in="SourceGraphic" result="inverted"><feFuncR type="table" tableValues="1 0"/><feFuncG type="table" tableValues="1 0"/><feFuncB type="table" tableValues="1 0"/></feComponentTransfer>' + ''.join(primitives) + '<feMerge>' + ''.join(merged) + '</feMerge></filter>')
    placed = set(excluded)

    def md(value):
        return builder.md(value, lang)

    def placeholder(setup=False):
        label = text["placeholder_title"] if setup else ("Figure to follow" if lang == "en" else "Abbildung folgt")
        detail = text["placeholder_detail"] if setup else ("A reviewed figure for this step will appear here." if lang == "en" else "Hier folgt eine geprüfte Abbildung zu diesem Schritt.")
        return '<figure class="case-placeholder"><div class="case-placeholder-art" role="img" aria-label="' + escape(label, quote=True) + '"><strong>' + escape(label) + '</strong></div><figcaption>' + escape(detail) + '</figcaption></figure>'

    def media(key):
        if key not in catalog or key in placed:
            raise ValueError(f"Unknown or duplicate case-study media: {identity}/{lang}/{key}")
        placed.add(key)
        item, screenshot, resource = catalog[key]
        prefix = "/assets/demos/" + identity + "/" if resource else "/content/"
        url = prefix + (item["path"] if resource else item["asset_path"])
        provenance = item.get("provenance", {})
        size = provenance.get("image_px", [item.get("width"), item.get("height")])
        dimensions = f' width="{int(size[0])}" height="{int(size[1])}"' if all(size) else ""
        src = url
        responsive = ""
        if item.get("variants"):
            variants = sorted(item["variants"], key=lambda value: value["width"])
            src = prefix + variants[0]["path"]
            responsive = ' srcset="' + escape(", ".join(prefix + value["path"] + " " + str(value["width"]) + "w" for value in variants), quote=True) + '" sizes="(max-width: 759px) calc(100vw - 52px), (max-width: 980px) 42vw, 520px"'
        title = item["title"][lang]
        figure_class = " case-figure-inverted" if key in inverted else ""
        display_attributes = ' data-invert-colors="true"' if key in inverted else ""
        image_style = ""
        if key in filters:
            display_attributes += ' data-image-filter="' + escape(filters[key], quote=True) + '"'
            image_style = ' style="filter:' + escape(filters[key], quote=True) + '"'
        caption_id = "case-caption-" + key
        note = ""
        if screenshot:
            stamp = str(provenance.get("captured_at_utc", provenance.get("captured_utc", "")))
            note = '<span class="source-note">' + escape(copy["english_capture"]) + ' <span class="technical-value">' + escape(stamp) + '</span></span>'
        return (
            '<figure class="case-figure figure-block' + figure_class + '" id="case-media-' + escape(key, quote=True) + '"><a class="case-image-link" href="' + escape(url, quote=True) + '" target="_blank" rel="noopener noreferrer" data-case-lightbox' + display_attributes + ' data-title="' + escape(title, quote=True) + '" data-caption-id="' + escape(caption_id, quote=True) + '" aria-label="' + escape(copy["full_size"] + ": " + title, quote=True) + '">'
            '<img loading="lazy" decoding="async"' + dimensions + image_style + ' src="' + escape(src, quote=True) + '"' + responsive + ' alt="' + escape(item["alt"][lang], quote=True) + '"></a>'
            '<figcaption id="' + escape(caption_id, quote=True) + '"><strong>' + escape(title) + '</strong>' + md(item.get("caption", {}).get(lang, "")) + note + '</figcaption></figure>'
        )

    settings = demo["settings"]["core_parameters"]
    comparison = demo["settings"].get("comparison_parameters", {})
    times = settings["time_selection"]
    identities = [settings["callsign"] + " (" + settings["qth"] + ")"]
    if comparison.get("reference_callsign"):
        identities.append(comparison["reference_callsign"] + " (" + comparison["reference_qth"] + ")")
    metadata_parts = [" / ".join(identities), settings["band"]]
    if show_hero_period:
        metadata_parts.append(text["period"])
    metadata_parts.append(text["mode"])
    metadata = " · ".join(metadata_parts)
    publication = '<a class="text-link" href="' + escape(config["publication_url"], quote=True) + '" target="_blank" rel="noopener noreferrer">' + escape(text["publication"]) + ' ↗</a>' if config.get("publication_url") else ""
    nav_items = [("setup", text["nav_setup"])]
    nav_items.extend((item["id"], item["nav_label"][lang]) for item in config["sections"])
    nav = '<nav class="case-nav" aria-label="' + escape(copy["contents"], quote=True) + '"><h2>' + escape(copy["contents"]) + '</h2><ol>'
    nav += "".join('<li><a href="#' + escape(key, quote=True) + '">' + escape(label) + '</a></li>' for key, label in nav_items) + '</ol></nav>'
    definitions = '<svg class="case-filter-definitions" aria-hidden="true" width="0" height="0"><defs>' + ''.join(filter_markup) + '</defs></svg>' if filter_markup else ''
    parts = ['<article class="case-study">' + definitions + '<header class="case-hero"><div class="case-hero-copy"><p class="eyebrow">' + escape(text["eyebrow"]) + '</p><h1>' + escape(title) + '</h1><p class="case-meta">' + escape(metadata) + '</p><div class="case-intro">' + md(intro) + '</div><div class="actions">' + button(copy["run_demo"], demo_launch_url(config), external=True) + publication + '</div></div>' + nav + '</header>']
    setup_title, setup_body = heading_and_body(sections["setup"], 2)
    setup_media_position = config.get("setup_media_position", "right")
    if setup_media_position not in ("left", "right"):
        raise ValueError("setup_media_position must be left or right")
    setup_class = "case-setup case-setup-media-left" if setup_media_position == "left" else "case-setup"
    parts.append('<section class="' + setup_class + '" id="setup"><div class="case-copy"><h2>' + escape(setup_title) + '</h2>')
    if show_setup_media:
        parts.append('<div class="case-media">' + (media(config["setup_media_key"]) if config.get("setup_media_key") else placeholder(True)) + '</div>')
    parts.append(md(setup_body))
    show_setup_summary = config.get("show_setup_summary", True)
    if not isinstance(show_setup_summary, bool):
        raise ValueError("show_setup_summary must be a boolean")
    if show_setup_summary:
        parts.append('<p class="case-identities technical-value">' + escape(" / ".join(identities)) + '</p><p class="case-window technical-value">UTC ' + escape(times["start_utc"]) + ' — ' + escape(times["end_utc"]) + '</p>' + publication)
    parts.append('</div></section>')
    parts.append('<section class="case-evidence" id="walkthrough"><div class="case-section-heading"><h2>' + escape(text["evidence_title"]) + '</h2><p>' + escape(text["evidence_intro"]) + '</p></div>')
    def evidence_row(item, number, nested=False):
        key = item["id"]
        used.add(key)
        heading, body = heading_and_body(sections[key], 2)
        full = item.get("layout") == "full"
        parts.append('<section class="case-evidence-group" id="' + escape(key, quote=True) + '"><div class="case-row' + (' case-row-full' if full else '') + (' case-row-reverse' if number % 2 == 0 else '') + '"><span class="case-number" aria-hidden="true">' + ('↳' if nested else f'{number:02d}') + '</span><div class="case-copy"><h3>' + escape(heading) + '</h3>')
        if not full:
            parts.append('<div class="case-media">' + ("".join(media(asset) for asset in item.get("media_keys", [])) or placeholder()) + '</div>')
        parts.append(md(body) + '</div></div>')
        for child in item.get("subsections", []):
            evidence_row(child, number, nested=True)
        parts.append('</section>')
    for index, item in enumerate(config["sections"], 1):
        evidence_row(item, index)
    parts.append('</section>')
    parts.append('</article>')
    if used != set(sections):
        raise ValueError("Unplaced demo Markdown sections: " + ", ".join(sorted(set(sections) - used)))
    return "".join(parts)
