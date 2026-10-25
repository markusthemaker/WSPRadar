"""Shared demo layout with editable Markdown and explicitly reviewed resources."""

try:
    from .browser_assets import resource_payload
except ImportError:
    from browser_assets import resource_payload

from html import escape
from pathlib import Path, PurePosixPath
import hashlib
import json
import math
import re
from urllib.parse import parse_qs, urlsplit


def language_override(config, field, lang, fallback):
    """Resolve an explicit language override without changing the shared default."""
    localized = config.get(field, {})
    languages = config.get("languages", {"en": {}, "de": {}})
    if not isinstance(localized, dict) or set(localized) - set(languages):
        raise ValueError(field + " must map configured languages to overrides")
    return localized.get(lang, fallback)


def demo_sections(config, lang):
    """Select and validate the section tree and compatibility anchors for a page."""
    sections = language_override(config, "sections_by_language", lang, config["sections"])
    anchors = {"hero", "objective", "summary", "setup", "walkthrough"}

    def validate(items):
        if not isinstance(items, list):
            raise ValueError("Demo sections and subsections must be arrays")
        for item in items:
            if not isinstance(item, dict):
                raise ValueError("Demo sections must be objects")
            show_in_nav = item.get("show_in_nav", False)
            if not isinstance(show_in_nav, bool):
                raise ValueError("Demo section show_in_nav must be a boolean")
            if show_in_nav:
                labels = item.get("nav_label", {})
                if not isinstance(labels, dict) or not isinstance(labels.get(lang), str) or not labels[lang].strip():
                    raise ValueError("Visible demo subsection requires a navigation label for " + lang)
            aliases = item.get("aliases", [])
            if not isinstance(aliases, list):
                raise ValueError("Demo section aliases must be an array")
            for anchor in [item.get("id"), *aliases]:
                if not isinstance(anchor, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", anchor):
                    raise ValueError("Invalid demo section ID or alias")
                if anchor in anchors:
                    raise ValueError("Duplicate or reserved demo section ID or alias: " + anchor)
                anchors.add(anchor)
            validate(item.get("subsections", []))

    validate(sections)
    return sections


def demo_launch_url(demo, variant="default"):
    """Use the full-configuration URL exported from the canonical demo config."""
    if not isinstance(variant, str) or not re.fullmatch(r"[a-z][a-z0-9_-]{0,31}", variant):
        raise ValueError("Invalid demo launch variant")
    if variant == "default":
        value = demo.get("launch_url", "")
    else:
        variants = demo.get("launch_variants", {})
        if not isinstance(variants, dict) or variant not in variants:
            raise ValueError("Unknown canonical demo launch variant: " + variant)
        value = variants[variant]
    if not isinstance(value, str):
        raise ValueError("Demo requires a reviewed full-configuration launch_url")
    url = urlsplit(value)
    query = parse_qs(url.query)
    if (url.scheme != "https" or url.netloc != "wspradar.org" or url.path != "/"
            or query.get("v") != ["1"] or query.get("run") != ["1"]
            or not {"direction", "callsign", "qth", "band", "from", "to", "mode"}.issubset(query)
            or "demo" in query or url.fragment != "wspradar-results-inspection"):
        raise ValueError("Demo requires a reviewed full-configuration launch_url")
    return value


def demo_launch_action(demo, spec, button):
    """Website placement and labels select an app-owned canonical launch URL."""
    if (not isinstance(spec, dict) or set(spec) != {"variant", "label"}
            or not isinstance(spec["label"], str) or not spec["label"].strip()):
        raise ValueError("Demo launch action requires a variant and nonempty label")
    return button(spec["label"], demo_launch_url(demo, spec["variant"]), external=True)


def demo_settings_table(demo, config, lang):
    """Render selected canonical settings with website-owned reading guidance."""
    spec = language_override(config, "settings_tables", lang, None)
    if spec is None:
        return None
    if not isinstance(spec, dict) or set(spec) != {"columns", "rows"}:
        raise ValueError("Demo settings table requires columns and rows")
    columns, selected = spec["columns"], spec["rows"]
    if (not isinstance(columns, list) or len(columns) != 3
            or any(not isinstance(value, str) or not value.strip() for value in columns)
            or not isinstance(selected, list) or not selected):
        raise ValueError("Demo settings table requires three column labels and selected rows")
    summary = demo.get("settings_summary")
    if not isinstance(summary, list):
        raise ValueError("Demo requires an imported canonical settings_summary")
    available = {}
    for row in summary:
        if (not isinstance(row, dict) or set(row) != {"key", "label", "value"}
                or not isinstance(row["key"], str) or row["key"] in available):
            raise ValueError("Invalid or duplicate canonical settings-summary row")
        for field in ("label", "value"):
            if not isinstance(row[field], dict) or not isinstance(row[field].get(lang), str):
                raise ValueError("Canonical settings-summary row requires localized text")
        available[row["key"]] = row

    # Preserve reviewed bundles exported before the spot-pair setting-key rename.
    if "min_spot_pairs_per_station" not in available and "min_joint_spots_per_station" in available:
        available["min_spot_pairs_per_station"] = available["min_joint_spots_per_station"]

    def cell(value):
        return escape(value).replace("|", "&#124;").replace("\n", "<br>")

    lines = ["| " + " | ".join(cell(value) for value in columns) + " |", "| :--- | :--- | :--- |"]
    used = set()
    for selection in selected:
        if (not isinstance(selection, dict) or set(selection) != {"key", "meaning"}
                or not isinstance(selection["key"], str)
                or selection["key"] not in available
                or not isinstance(selection["meaning"], str)):
            raise ValueError("Unknown, duplicate or invalid demo settings-table row")
        row = available[selection["key"]]
        key = row["key"]
        if key in used:
            raise ValueError("Unknown, duplicate or invalid demo settings-table row")
        used.add(key)
        meaning = selection["meaning"].replace("|", "&#124;").replace("\n", "<br>")
        lines.append("| " + cell(row["label"][lang]) + " | **" + cell(row["value"][lang])
                     + "** | " + meaning + " |")
    return "\n".join(lines)


def expand_demo_markdown(value, demo, settings_table=None):
    """Expand canonical configuration markers while retaining all authored text."""
    value = value.replace("{{demo_launch_url}}", demo_launch_url(demo))
    if settings_table is not None:
        value = value.replace("{{demo_settings_table}}", settings_table)
    return value


def settings_table_disclosure(settings_table, config, lang, render_table):
    """Show configured preview rows while retaining the complete canonical table."""
    absent = object()
    spec = language_override(config, "settings_table_disclosure", lang, absent)
    if spec is absent:
        return None
    if (not isinstance(spec, dict) or set(spec) != {"preview_rows", "summary"}
            or type(spec["preview_rows"]) is not int
            or not isinstance(spec["summary"], str) or not spec["summary"].strip()):
        raise ValueError("Settings table disclosure requires preview_rows and a nonempty summary")
    if settings_table is None:
        raise ValueError("Settings table disclosure requires a configured settings table")
    lines = settings_table.splitlines()
    if not 1 <= spec["preview_rows"] < len(lines) - 2:
        raise ValueError("Settings table preview_rows must retain at least one collapsed row")
    preview = "\n".join(lines[:2 + spec["preview_rows"]])
    return ('<div class="case-settings-disclosure"><div class="case-settings-preview">'
            + render_table(preview) + '</div><details class="case-settings-details"><summary>'
            + escape(spec["summary"]) + '</summary><div class="case-settings-complete">'
            + render_table(settings_table) + '</div></details></div>')


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


def resource_files(root, configurations, *, source_root=None):
    """Only hash-checked, allowlisted public resources enter the static output."""
    output = {}
    for identity, config in configurations.items():
        manifest_name = config.get("resource_manifest")
        if not manifest_name:
            continue
        manifest_path = safe_path(root, manifest_name)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        prepared = resource_payload(manifest_path.parent, manifest, source_root=source_root)
        for entry in manifest["files"]:
            payload = prepared[entry["path"]]
            if len(payload) != entry["bytes"] or hashlib.sha256(payload).hexdigest() != entry["sha256"]:
                raise ValueError("Demo resource hash mismatch: " + entry["path"])
            name = "assets/demos/" + identity + "/" + entry["path"]
            if name in output:
                raise ValueError("Duplicate demo resource: " + name)
            output[name] = payload
    return output


def render_demo(builder, lang, demo, config, button, route, app_url):
    if "launch_url" in config or "launch_urls" in config:
        raise ValueError("Demo launch URLs belong to the imported canonical configuration")
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
    settings_table = demo_settings_table(demo, config, lang)
    table_marker_count = sum(value.count("{{demo_settings_table}}") for value in sections.values())
    if table_marker_count != (1 if settings_table is not None else 0):
        raise ValueError("Configured demo settings table requires exactly one matching Markdown marker")
    settings_disclosure = settings_table_disclosure(
        settings_table, config, lang, lambda value: builder.md(value, lang))
    configured_sections = demo_sections(config, lang)
    used = {"hero", "setup"}
    title, intro = heading_and_body(sections["hero"], 1)
    catalog = {
        item["key"]: (item, screenshot, False)
        for items, screenshot in ((builder.figures, False), (builder.screenshots, True))
        for item in items if item["demo_id"] == identity
    }
    if config.get("resource_manifest"):
        manifest_path = safe_path(builder.demo_asset_root, config["resource_manifest"])
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

    def md(value, **kwargs):
        rendered = builder.md(expand_demo_markdown(value, demo, settings_table), lang, **kwargs)
        if settings_disclosure is not None and "{{demo_settings_table}}" in value:
            full_table = builder.md(settings_table, lang)
            if rendered.count(full_table) != 1:
                raise ValueError("Settings disclosure requires one standalone rendered table")
            rendered = rendered.replace(full_table, settings_disclosure, 1)
        return rendered

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
    objective_label = "Objective" if lang == "en" else "Ziel"
    nav_items = [("objective", objective_label), ("setup", text["nav_setup"])]

    def add_navigation_items(items, nested=False):
        for item in items:
            if not nested or item.get("show_in_nav", False):
                nav_items.append((item["id"], item["nav_label"][lang]))
            add_navigation_items(item.get("subsections", []), nested=True)

    add_navigation_items(configured_sections)
    nav = '<nav class="case-nav" aria-label="' + escape(copy["contents"], quote=True) + '"><h2>' + escape(copy["contents"]) + '</h2><ol>'
    nav += "".join('<li><a href="#' + escape(key, quote=True) + '">' + escape(label) + '</a></li>' for key, label in nav_items) + '</ol></nav>'
    definitions = '<svg class="case-filter-definitions" aria-hidden="true" width="0" height="0"><defs>' + ''.join(filter_markup) + '</defs></svg>' if filter_markup else ''
    launch_actions = language_override(config, "launch_actions", lang, None)
    if launch_actions is None:
        launch_buttons = button(copy["run_demo"], demo_launch_url(demo), external=True)
    else:
        if not isinstance(launch_actions, list) or not launch_actions:
            raise ValueError("Demo launch_actions requires a nonempty array")
        launch_buttons = '<div class="case-launch-actions">' + ''.join(
            demo_launch_action(demo, action, button) for action in launch_actions) + '</div>'
    parts = ['<article class="case-study">' + definitions + '<header class="case-hero"><div class="case-hero-copy"><p class="eyebrow">' + escape(text["eyebrow"]) + '</p><h1>' + escape(title) + '</h1><div class="case-intro" id="objective" aria-label="' + escape(objective_label, quote=True) + '">' + md(intro) + '</div><p class="case-meta">' + escape(metadata) + '</p><div class="actions">' + launch_buttons + publication + '</div></div>' + nav + '</header>']
    evidence_intro = '<p>' + escape(text["evidence_intro"]) + '</p>' if text.get("evidence_intro") else ""
    if "summary" in sections:
        summary_title, summary_body = heading_and_body(sections["summary"], 2)
        used.add("summary")
        parts.append('<section class="case-summary" id="summary" aria-label="' + escape(summary_title, quote=True) + '"><h2>' + escape(summary_title) + '</h2>' + md(summary_body, continuous=True) + evidence_intro + '</section>')
    setup_title, setup_body = heading_and_body(sections["setup"], 2)
    setup_media_position = config.get("setup_media_position", "right")
    if setup_media_position not in ("left", "right"):
        raise ValueError("setup_media_position must be left or right")
    setup_class = "case-setup case-setup-media-left" if setup_media_position == "left" else "case-setup"
    parts.append('<section class="' + setup_class + '" id="setup"><div class="case-copy"><div class="case-step-heading"><span class="case-number" aria-hidden="true">01</span><h2>' + escape(setup_title) + '</h2></div>')
    if show_setup_media:
        parts.append('<div class="case-media">' + (media(config["setup_media_key"]) if config.get("setup_media_key") else placeholder(True)) + '</div>')
    parts.append(md(setup_body))
    show_setup_summary = config.get("show_setup_summary", True)
    if not isinstance(show_setup_summary, bool):
        raise ValueError("show_setup_summary must be a boolean")
    if show_setup_summary:
        parts.append('<p class="case-identities technical-value">' + escape(" / ".join(identities)) + '</p><p class="case-window technical-value">UTC ' + escape(times["start_utc"]) + ' — ' + escape(times["end_utc"]) + '</p>' + publication)
    parts.append('</div></section>')
    parts.append('<section class="case-evidence" id="walkthrough">' + (evidence_intro if "summary" not in sections else ""))
    def evidence_row(item, number, nested=False):
        key = item["id"]
        used.add(key)
        heading, body = heading_and_body(sections[key], 2)
        full = item.get("layout") == "full"
        aliases = "".join('<span id="' + escape(alias, quote=True) + '" aria-hidden="true"></span>'
                          for alias in item.get("aliases", []))
        heading_action = (demo_launch_action(demo, item["launch_action"], button)
                          if "launch_action" in item else "")
        heading_class = "case-step-heading" + (" case-step-heading-with-action" if heading_action else "")
        parts.append('<section class="case-evidence-group" id="' + escape(key, quote=True) + '">' + aliases + '<div class="case-row' + (' case-row-full' if full else '') + (' case-row-reverse' if number % 2 == 0 else '') + '"><div class="case-copy"><div class="' + heading_class + '"><span class="case-number" aria-hidden="true">' + ('↳' if nested else f'{number + 1:02d}') + '</span><h3>' + escape(heading) + '</h3>' + heading_action + '</div>')
        if not full:
            parts.append('<div class="case-media">' + ("".join(media(asset) for asset in item.get("media_keys", [])) or placeholder()) + '</div>')
        parts.append(md(body) + '</div></div>')
        for child in item.get("subsections", []):
            evidence_row(child, number, nested=True)
        parts.append('</section>')
    for index, item in enumerate(configured_sections, 1):
        evidence_row(item, index)
    parts.append('</section>')
    parts.append('</article>')
    if used != set(sections):
        raise ValueError("Unplaced demo Markdown sections: " + ", ".join(sorted(set(sections) - used)))
    return "".join(parts)
