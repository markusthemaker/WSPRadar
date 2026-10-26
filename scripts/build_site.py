"""Build the public WSPRadar website from its reviewed content bundle.

No application checkout, runtime import, database query, or credentials are
required. Imported content is verified before any build output is written.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import re
from string import Template
from urllib.parse import unquote, urlsplit

import markdown

if __package__:
    from .documentation_pdfs import documentation_pdf_files
    from .page_content import load_catalog
    from .prepare_landing_assets import payload as landing_payload
    from .external_links import check_external_links, collect_external_links
    from .demos_index import render_demos_index
    from .landing_page import render_landing
    from .demo_walkthrough import demo_launch_url, heading_and_body, read_sections, render_demo, resource_files, safe_path
else:
    from documentation_pdfs import documentation_pdf_files
    from page_content import load_catalog
    from prepare_landing_assets import payload as landing_payload
    from external_links import check_external_links, collect_external_links
    from demos_index import render_demos_index
    from landing_page import render_landing
    from demo_walkthrough import demo_launch_url, heading_and_body, read_sections, render_demo, resource_files, safe_path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
CONTENT = SOURCE / "imported" / "app"
DEMO_SUPPLEMENTS = SOURCE / "assets" / "demos"
OUTPUT = ROOT / "generated"
APP_URL = "https://wspradar.streamlit.app/"
# Legacy Community Cloud asset links remain recognized after launch migration.
# Active application launches come from the exported navigation catalog.
APP_STATIC_URL = APP_URL + "~/+/app/static/"
SITE_URL = "https://www.wspradar.org"
COMMUNITY_URL = "https://github.com/markusthemaker/WSPRadar/discussions"
HELP_URL = COMMUNITY_URL + "/new?category=ask-a-question"
EXPERIMENTS_URL = COMMUNITY_URL + "/new?category=discuss-your-experiments"
IDEAS_URL = COMMUNITY_URL + "/new?category=ideas-and-feature-requests"
REPORT_URL = COMMUNITY_URL + "/new?category=report-a-bug-or-concern"
# Match the border-box site shell and its horizontal padding in source/theme/styles/site.css.
HEADER_IMAGE_SIZES = "(max-width:580px) calc(100vw - 34px), (max-width:1280px) calc(100vw - 48px), 1232px"
LANGUAGE_NAMES = {"en": "English", "de": "Deutsch"}
# German remains supported; offer it again after the translation is ready.
HEADER_LANGUAGES = ("en",)

COPY = load_catalog(SOURCE / "config" / "interface.json", SOURCE / "pages")


@dataclass(frozen=True)
class Section:
    key: str
    title: str
    level: int
    text: str
    anchors: tuple[str, ...]


def json_read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def verify_bundle(directory: Path) -> dict:
    manifest = json_read(directory / "manifest.json")
    if type(manifest.get("schema_version")) is not int or manifest["schema_version"] != 1:
        raise ValueError("Unsupported public-content manifest version")
    declared = manifest.get("files")
    if not isinstance(declared, dict) or not declared:
        raise ValueError("Manifest contains no file inventory")
    for name, expected in declared.items():
        relative = PurePosixPath(name)
        if not isinstance(name, str) or relative.is_absolute() or relative.as_posix() != name or any(part in (".", "..") for part in relative.parts) or ":" in name:
            raise ValueError(f"Unsafe manifest path: {name}")
        candidate = (directory / name).resolve()
        if not candidate.is_relative_to(directory.resolve()) or "\\" in name:
            raise ValueError(f"Unsafe manifest path: {name}")
        data = candidate.read_bytes()
        if len(data) != expected["bytes"] or hashlib.sha256(data).hexdigest() != expected["sha256"]:
            raise ValueError(f"Imported content is stale or modified: {name}")
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
    if actual != set(declared) | {"manifest.json"}:
        raise ValueError("Imported content inventory differs from manifest")
    return manifest


def split_manual(text: str) -> list[Section]:
    """Partition the entire source; no sentence or compatibility anchor is dropped."""
    lines = text.splitlines(keepends=True)
    starts = []
    heading_data = []
    in_part_zero = False
    for index, line in enumerate(lines):
        match = re.match(r"^(#{2,3})\s+(.+?)\s*$", line)
        if not match:
            continue
        start = index
        while start and (not lines[start - 1].strip() or re.fullmatch(r'<a id="[^"]+"></a>\s*', lines[start - 1])):
            start -= 1
        if len(match[1]) == 2:
            leading = "".join(lines[start:index])
            in_part_zero = '<a id="part-0"></a>' in leading
        elif in_part_zero and re.match(r"^0\.\d+\s", match[2]):
            # Keep the introductory subsections at their existing sec-1 URLs.
            continue
        starts.append(start)
        heading_data.append((len(match[1]), match[2], index))
    if not starts:
        raise ValueError("Manual has no recognized section headings")
    starts[0] = 0
    sections = []
    used_keys = set()
    for number, start in enumerate(starts):
        end = starts[number + 1] if number + 1 < len(starts) else len(lines)
        source = "".join(lines[start:end])
        anchors = tuple(re.findall(r'<a\s+id="([^"]+)"', source))
        level, title, heading_index = heading_data[number]
        leading = "".join(lines[start:heading_index])
        leading_ids = re.findall(r'<a\s+id="([^"]+)"', leading)
        key = leading_ids[0] if leading_ids else f"section-{number}"
        if key in used_keys:
            raise ValueError(f"Duplicate manual section key: {key}")
        used_keys.add(key)
        sections.append(Section(key, title, level, source, anchors))
    if "".join(section.text for section in sections) != text:
        raise ValueError("Manual partition changed the source text")
    return sections


def route(lang: str, suffix: str = "") -> str:
    return f"/{lang}/" + suffix


def chapter_url(lang: str, key: str) -> str:
    return route(lang, f"documentation/{key}/")


def render_markdown(text: str, lang: str, anchor_map: dict[str, str], *, continuous=False) -> str:
    expressions = {}
    def math_replace(match):
        expression = match[2]
        delimiter = r"\[" if match[1] == "$$" else r"\("
        ending = r"\]" if match[1] == "$$" else r"\)"
        token = 'WSPRADARMATH' + hashlib.sha256(match[0].encode()).hexdigest() + 'END'
        expressions[token] = '<span class="math">' + delimiter + escape(expression) + ending + '</span>'
        return token

    text = re.sub(r"(\${1,2})(.+?)\1", math_replace, text, flags=re.DOTALL)
    rendered = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])
    for token, expression in expressions.items():
        rendered = rendered.replace(token, expression)
    rendered = website_reference_pdf_links(rendered)
    rendered = re.sub(r'<a([^>]*?)href="app/static/([^"<>]+)"', lambda m: f'<a{m[1]}href="{APP_STATIC_URL}{m[2]}"', rendered)
    if not continuous:
        rendered = re.sub(r'href="#([^"]+)"', lambda m: f'href="{anchor_map.get(m[1], route(lang, "documentation/full/"))}#{m[1]}"', rendered)
    rendered = rendered.replace("<table>", '<div class="table-scroll" role="region" aria-label="' + ("Scrollable table" if lang == "en" else "Scrollbare Tabelle") + '" tabindex="0"><table>')
    return rendered.replace("</table>", "</table></div>")


class _PDFLinkPolicyParser(HTMLParser):
    """Locate real anchors while leaving their surrounding source untouched."""

    CDATA_CONTENT_ELEMENTS = (
        "script", "style", "textarea", "title", "xmp", "iframe", "noembed",
        "noframes", "plaintext",
    )
    _attribute = re.compile(
        r"""(?P<name>[^\s=/>]+)(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+))?"""
    )

    def __init__(self, source: str):
        super().__init__(convert_charrefs=False)
        self.line_offsets = [0] + [match.end() for match in re.finditer("\n", source)]
        self.replacements: list[tuple[int, int, str]] = []

    def handle_starttag(self, tag, attrs):
        self._handle_anchor(tag, attrs, self_closing=False)

    def handle_startendtag(self, tag, attrs):
        self._handle_anchor(tag, attrs, self_closing=True)

    def _handle_anchor(self, tag, attrs, *, self_closing):
        if tag != "a":
            return
        # The first href is the effective attribute when malformed HTML repeats it.
        href = next((value for name, value in attrs if name == "href"), None)
        if not href:
            return
        try:
            is_pdf = unquote(urlsplit(href).path).casefold().endswith(".pdf")
        except ValueError:
            return
        if not is_pdf:
            return

        tokens = [token for name, value in attrs if name == "rel"
                  for token in (value or "").split()]
        for required in ("noopener", "noreferrer"):
            if required not in {token.casefold() for token in tokens}:
                tokens.append(required)
        values = {"target": "_blank", "rel": " ".join(tokens)}
        raw = self.get_starttag_text()
        tag_end = re.match(r"<a\b", raw, re.IGNORECASE).end()
        edits = []
        found = set()
        for match in self._attribute.finditer(raw, tag_end):
            name = match["name"]
            key = name.casefold()
            if key == "download":
                # A download hint can override opening a local PDF in a new tab.
                edits.append((match.start(), match.end(), ""))
            elif key in values:
                found.add(key)
                edits.append((match.start(), match.end(),
                              name + '="' + escape(values[key], quote=True) + '"'))
        missing = ''.join(' ' + key + '="' + escape(value, quote=True) + '"'
                          for key, value in values.items() if key not in found)
        if missing:
            close_at = len(raw) - (2 if self_closing else 1)
            edits.append((close_at, close_at, missing))
        updated = raw
        for start, end, replacement in sorted(edits, reverse=True):
            updated = updated[:start] + replacement + updated[end:]
        if updated != raw:
            line, column = self.getpos()
            start = self.line_offsets[line - 1] + column
            self.replacements.append((start, start + len(raw), updated))


def open_pdf_links_in_new_tabs(html: str) -> str:
    """Apply the shared PDF policy without reserializing unrelated markup."""
    parser = _PDFLinkPolicyParser(html)
    parser.feed(html)
    parser.close()
    for start, end, replacement in reversed(parser.replacements):
        html = html[:start] + replacement + html[end:]
    return html


class _WebsiteReferencePDFLinkParser(_PDFLinkPolicyParser):
    """Route legacy comparison PDFs locally, preserving unrelated app media."""

    def _handle_anchor(self, tag, attrs, *, self_closing):
        if tag != "a":
            return
        href = next((value for name, value in attrs if name == "href"), None)
        if not href:
            return
        prefixes = ("app/static/reference_figures/", "/app/static/reference_figures/",
                    APP_STATIC_URL + "reference_figures/", APP_URL + "app/static/reference_figures/",
                    "/static/reference_figures/", SITE_URL + "/static/reference_figures/",
                    "https://wspradar.org/static/reference_figures/")
        prefix = next((value for value in prefixes if href.startswith(value)), None)
        if prefix is None or not unquote(urlsplit(href).path).casefold().endswith(".pdf"):
            return
        raw = self.get_starttag_text()
        tag_end = re.match(r"<a\b", raw, re.IGNORECASE).end()
        updated = raw
        for match in reversed(list(self._attribute.finditer(raw, tag_end))):
            if match["name"].casefold() == "href":
                attribute = match[0].replace(prefix, "/assets/demos/", 1)
                updated = updated[:match.start()] + attribute + updated[match.end():]
        if updated != raw:
            line, column = self.getpos()
            start = self.line_offsets[line - 1] + column
            self.replacements.append((start, start + len(raw), updated))


def website_reference_pdf_links(html):
    """Retain exact comparison paths, queries, fragments and nonreference links."""
    parser = _WebsiteReferencePDFLinkParser(html)
    parser.feed(html)
    parser.close()
    for start, end, replacement in reversed(parser.replacements):
        html = html[:start] + replacement + html[end:]
    return html


class _ProductNavigationLinkPolicyParser(_PDFLinkPolicyParser):
    """Keep product pages and all analysis launches in the current tab."""

    def __init__(self, source, catalog, *, current_suffix=""):
        super().__init__(source)
        self.website_origins = {
            (urlsplit(value).scheme, urlsplit(value).netloc)
            for value in (catalog["origins"]["website"], "https://wspradar.org/")
        }
        self.analysis_origins = {
            (urlsplit(value).scheme, urlsplit(value).netloc)
            for value in [catalog["origins"]["analysis"], *catalog.get("analysis_aliases", [])]
        }
        self.new_tab = next(item["new_tab"] for item in catalog["items"]
                            if item["destination"] == "analysis" and not item["path"])
        self.same_tab_action = False

    def _handle_anchor(self, tag, attrs, *, self_closing):
        if tag != "a":
            return
        self.same_tab_action = False
        href = next((value for name, value in attrs if name == "href"), None)
        if not href:
            return
        try:
            url = urlsplit(href)
            origin = (url.scheme, url.netloc)
            analysis_root = origin in self.analysis_origins
            website_root = origin in self.website_origins
            website_link = website_root or (not url.scheme and not url.netloc)
            relative_root = not url.scheme and not url.netloc and url.path == "/"
            launch = (url.path in {"", "/"} and (analysis_root or (
                (website_root or relative_root)
                and (url.query or url.fragment == "wspradar-results-inspection")
            )))
            website_page = website_link and (
                url.path in {"", "/"}
                or re.fullmatch(r"/(?:en|de)/(?:[a-zA-Z0-9_-]+/)*", url.path)
            )
        except ValueError:
            return
        if not launch and not website_page:
            return
        new_tab = self.new_tab if launch else False
        classes = {token for name, value in attrs if name == "class" for token in (value or "").split()}
        self.same_tab_action = (launch or website_page) and not new_tab and not self_closing and bool(classes & {"button", "text-link"})
        raw = self.get_starttag_text()
        tag_end = re.match(r"<a\b", raw, re.IGNORECASE).end()
        edits = []
        values = {}
        if new_tab:
            tokens = [token for name, value in attrs if name == "rel" for token in (value or "").split()]
            for required in ("noopener", "noreferrer"):
                if required not in {token.casefold() for token in tokens}:
                    tokens.append(required)
            values = {"target": "_blank", "rel": " ".join(tokens)}
        found = set()
        for match in self._attribute.finditer(raw, tag_end):
            key = match["name"].casefold()
            if key == "target" and not new_tab:
                edits.append((match.start(), match.end(), ""))
            elif key in values:
                found.add(key)
                replacement = match["name"] + '="' + escape(values[key], quote=True) + '"'
                edits.append((match.start(), match.end(), replacement))
        missing = ''.join(' ' + key + '="' + escape(value, quote=True) + '"'
                          for key, value in values.items() if key not in found)
        if missing:
            close_at = len(raw) - (2 if self_closing else 1)
            edits.append((close_at, close_at, missing))
        updated = raw
        for start, end, replacement in sorted(edits, reverse=True):
            updated = updated[:start] + replacement + updated[end:]
        if updated != raw:
            line, column = self.getpos()
            start = self.line_offsets[line - 1] + column
            self.replacements.append((start, start + len(raw), updated))

    def handle_data(self, data):
        if self.same_tab_action and data.endswith(" ↗"):
            line, column = self.getpos()
            end = self.line_offsets[line - 1] + column + len(data)
            self.replacements.append((end - 1, end, "→"))

    def handle_endtag(self, tag):
        if tag == "a":
            self.same_tab_action = False


def apply_product_navigation_link_policy(html, catalog, *, current_suffix=""):
    """Keep complete analysis launch URLs and unrelated markup byte-exact."""
    parser = _ProductNavigationLinkPolicyParser(html, catalog, current_suffix=current_suffix)
    parser.feed(html)
    parser.close()
    for start, end, replacement in reversed(parser.replacements):
        html = html[:start] + replacement + html[end:]
    return html


class _PrintImageParser(HTMLParser):
    """Promote real image loading hints without rewriting content or sources."""

    CDATA_CONTENT_ELEMENTS = _PDFLinkPolicyParser.CDATA_CONTENT_ELEMENTS

    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.line_offsets = [0] + [match.end() for match in re.finditer("\n", source)]
        self.replacements = []

    def handle_starttag(self, tag, attrs):
        if tag != "img" or not any(name == "loading" and (value or "").lower() == "lazy" for name, value in attrs):
            return
        raw = self.get_starttag_text()
        tag_end = re.match(r"<img\b", raw, re.IGNORECASE).end()
        updated = raw
        for match in reversed(list(_PDFLinkPolicyParser._attribute.finditer(raw, tag_end))):
            if match["name"].lower() == "loading":
                updated = updated[:match.start()] + 'loading="eager"' + updated[match.end():]
        line, column = self.getpos()
        start = self.line_offsets[line - 1] + column
        self.replacements.append((start, start + len(raw), updated))

    handle_startendtag = handle_starttag


def load_print_images_with_page(html: str) -> str:
    """Native print can snapshot before lazy-image requests from beforeprint finish."""
    parser = _PrintImageParser(html)
    parser.feed(html)
    parser.close()
    for start, end, replacement in reversed(parser.replacements):
        html = html[:start] + replacement + html[end:]
    return html


def button(label: str, href: str, *, secondary=False, external=False, download=False) -> str:
    attributes = ' target="_blank" rel="noopener noreferrer"' if external else ""
    if download:
        attributes += " download"
    return f'<a class="button{" secondary" if secondary else ""}" href="{escape(href, quote=True)}"{attributes}>{escape(label)}{" ↗" if external else ""}</a>'


def product_design_stylesheet_html(brand, manifest):
    """Use the imported, source-hashed design tokens without private imports."""
    if "product_design" not in brand:
        # Older reviewed bundles keep the exact CSS fallback values until their
        # next explicit public-content export.
        return ""
    design = brand["product_design"]
    if (not isinstance(design, dict) or type(design.get("schema_version")) is not int
            or design["schema_version"] != 1
            or design.get("stylesheet") != "assets/brand/product-tokens.css"):
        raise ValueError("Invalid imported product-design metadata")
    name = design["stylesheet"]
    record = manifest["files"].get(name)
    if (not isinstance(record, dict) or not isinstance(record.get("sha256"), str)
            or not re.fullmatch(r"[0-9a-f]{64}", record["sha256"])):
        raise ValueError("Product-design stylesheet is missing from the verified bundle")
    return '<link rel="stylesheet" href="/content/' + name + '?v=' + record["sha256"][:16] + '">'


def product_navigation_catalog(brand):
    """Read manifest-verified shared routes without importing private app code."""
    metadata = brand.get("product_navigation")
    if not isinstance(metadata, dict) or metadata.get("schema_version") != 1:
        raise ValueError("Shared product navigation is missing; refresh the public navigation export")
    catalog = metadata.get("catalog")
    if (not isinstance(catalog, dict) or set(catalog) not in ({"schema_version", "origins", "local", "items"},
                    {"schema_version", "origins", "local", "items", "analysis_aliases"})
            or type(catalog["schema_version"]) is not int or catalog["schema_version"] != 1
            or not isinstance(catalog["origins"], dict)
            or set(catalog["origins"]) != {"website", "analysis"}
            or not isinstance(catalog["local"], dict) or set(catalog["local"]) != {"website_port", "analysis_port"}
            or not isinstance(catalog["items"], list) or not catalog["items"]):
        raise ValueError("Invalid imported product-navigation catalog")
    aliases = catalog.get("analysis_aliases", [])
    if not isinstance(aliases, list):
        raise ValueError("Analysis aliases must be an explicit list of HTTPS origins")
    normalized_origins = []
    for value in [*catalog["origins"].values(), *aliases]:
        if not isinstance(value, str):
            raise ValueError("Invalid imported navigation origin")
        try:
            origin = urlsplit(value)
            valid_port = origin.port is None or 1 <= origin.port <= 65535
        except ValueError as exc:
            raise ValueError("Invalid imported navigation origin") from exc
        if (origin.scheme != "https" or not origin.hostname or origin.username is not None
                or origin.password is not None or origin.path not in {"", "/"} or origin.query or origin.fragment
                or not valid_port or any(character.isspace() for character in value)):
            raise ValueError("Invalid imported navigation origin")
        normalized_origins.append(f"{origin.scheme}://{origin.netloc}/")
    known_origins = set(normalized_origins[:len(catalog["origins"])])
    for alias in normalized_origins[len(catalog["origins"]):]:
        if alias in known_origins:
            raise ValueError("Analysis aliases must be unique and distinct from primary origins")
        known_origins.add(alias)
    if any(type(port) is not int or not 1 <= port <= 65535 for port in catalog["local"].values()):
        raise ValueError("Invalid imported navigation local ports")
    identities = set()
    for item in catalog["items"]:
        if (not isinstance(item, dict) or set(item) != {"id", "destination", "path", "label", "new_tab"}
                or not isinstance(item["id"], str) or not re.fullmatch(r"[a-z][a-z0-9_-]*", item["id"])
                or item["id"] in identities or item["destination"] not in {"website", "analysis"}
                or not isinstance(item["path"], str) or not re.fullmatch(r"(?:[a-z0-9-]+/)*", item["path"])
                or not isinstance(item["label"], dict) or set(item["label"]) != {"en", "de"}
                or any(not isinstance(label, str) or not label.strip() for label in item["label"].values())
                or type(item["new_tab"]) is not bool):
            raise ValueError("Invalid imported product-navigation item")
        identities.add(item["id"])
    return catalog


def select_published_demos(demos, walkthroughs):
    """Select website walkthroughs while retaining the imported application catalog."""
    definitions = walkthroughs.get("demos") if isinstance(walkthroughs, dict) else None
    if not isinstance(definitions, dict) or not definitions:
        raise ValueError("Published demo definitions must be a nonempty object")
    unknown = set(definitions) - {demo["id"] for demo in demos}
    if unknown:
        raise ValueError("Unknown published demo IDs: " + ", ".join(sorted(unknown)))
    return [demo for demo in demos if demo["id"] in definitions]


class SiteBuilder:
    def __init__(self, content=CONTENT, *, local_analysis_port=None):
        self.content = Path(content)
        self.manifest = verify_bundle(self.content)
        self.brand = json_read(self.content / "brand.json")
        self.navigation = product_navigation_catalog(self.brand)
        if local_analysis_port is not None and (type(local_analysis_port) is not int or not 1 <= local_analysis_port <= 65535):
            raise ValueError("Local analysis preview port must be an integer between 1 and 65535")
        self.local_analysis_port = local_analysis_port
        self.demos = json_read(self.content / "demos.json")
        self.demo_by_id = {demo["id"]: demo for demo in self.demos}
        self.website = json_read(self.content / "website.json")
        self.figures = json_read(self.content / "figures.json")
        self.screenshots = json_read(self.content / "screenshots.json")
        self.manuals = {lang: (self.content / f"manual.{lang}.md").read_bytes().decode("utf-8") for lang in COPY}
        self.documentation_pdfs = documentation_pdf_files(
            SOURCE / 'assets' / 'documentation', self.manuals, self.brand['app_version'])
        self.documentation_pdf_versions = {
            lang: hashlib.sha256(self.documentation_pdfs[
                'assets/documentation/WSPRadar_Doc_' + lang.upper() + '.pdf']).hexdigest()[:12]
            for lang in COPY
        }
        self.sections = {lang: split_manual(value) for lang, value in self.manuals.items()}
        self.anchors = {lang: {anchor: chapter_url(lang, s.key) for s in sections for anchor in s.anchors} for lang, sections in self.sections.items()}
        for lang in COPY:
            all_anchors = [anchor for s in self.sections[lang] for anchor in s.anchors]
            if len(all_anchors) != len(set(all_anchors)):
                raise ValueError(f"Duplicate manual anchors in {lang}")
        self.template = Template((SOURCE / "theme" / "templates" / "page.html").read_text(encoding="utf-8"))
        self.landing_css_version = hashlib.sha256((SOURCE / "theme" / "styles" / "landing.css").read_bytes()).hexdigest()[:16]
        self.print_assets_version = hashlib.sha256((SOURCE / "theme" / "styles" / "print.css").read_bytes() + (SOURCE / "theme" / "scripts" / "print.js").read_bytes()).hexdigest()[:16]
        self.copy = COPY
        self.landing = load_catalog(SOURCE / "config" / "landing.json", SOURCE / "pages")
        self.landing_payload = landing_payload(
            asset_root=SOURCE / "assets" / "landing", source_root=SOURCE)
        self.landing_assets = json.loads(self.landing_payload["manifest.json"])
        self.demo_walkthroughs = json_read(SOURCE / "config" / "demo_walkthroughs.json")
        self.published_demos = select_published_demos(self.demos, self.demo_walkthroughs)
        self.demos_index = load_catalog(SOURCE / "config" / "demos_index.json", SOURCE / "pages")
        self.demo_root = SOURCE / "pages" / "demos"
        self.demo_asset_root = SOURCE / "assets" / "demos"
        figure_catalog = SOURCE / "config" / "manual_figures.json"
        self.manual_figures = json_read(figure_catalog) if figure_catalog.is_file() else {}
        for lang, placements in self.manual_figures.items():
            for placement in placements:
                if placement["before_anchor"] not in self.anchors[lang]:
                    raise ValueError("Unknown manual figure anchor: " + placement["before_anchor"])
        self.pages: dict[str, str] = {}

    def md(self, text, lang, **kwargs):
        return render_markdown(text, lang, self.anchors[lang], **kwargs)

    def language_selector(self, lang: str, suffix: str) -> str:
        """Show the current language and preserve the route for offered choices."""
        label = COPY[lang]["change_language"]
        options = []
        for language in HEADER_LANGUAGES:
            name = LANGUAGE_NAMES[language]
            current = ' aria-current="true"' if language == lang else ""
            options.append(
                f'<a class="language-option" href="{route(language, suffix)}" lang="{language}" hreflang="{language}"{current}>'
                f'<span>{name}</span></a>'
            )
        return (
            '<details class="language-selector">'
            f'<summary aria-label="{label}: {LANGUAGE_NAMES[lang]}" title="{label}">'
            '<svg class="language-globe" width="18" height="18" viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.6">'
            '<circle cx="12" cy="12" r="9"></circle><ellipse cx="12" cy="12" rx="4" ry="9"></ellipse><path d="M3 12h18"></path></svg>'
            f'<span class="language-current" lang="{lang}">{lang.upper()}</span>'
            '<span class="language-chevron" aria-hidden="true">⌄</span></summary>'
            f'<div class="language-options" role="group" aria-label="{label}">' + ''.join(options) + '</div></details>'
        )

    def header(self, lang: str, active: str, suffix: str) -> str:
        t = COPY[lang]
        links = []
        current_section = {"home": "overview", "docs": "documentation"}.get(active, active)
        for item in self.navigation["items"]:
            destination = (route(lang, item["path"]) if item["destination"] == "website"
                           else self.navigation["origins"]["analysis"] + item["path"])
            current = ' aria-current="page"' if item["id"] == current_section else ""
            tab = ' target="_blank" rel="noopener noreferrer"' if item["new_tab"] and item["id"] != "documentation" else ""
            links.append(f'<a href="{escape(destination, quote=True)}" data-product-nav="{item["id"]}"{current}{tab}>{escape(item["label"][lang])}</a>')
        hero = self.landing_assets["hero"]
        fallback = hero["fallback"]
        candidates = sorted(hero["images"], key=lambda image: image["width"])
        srcset = ", ".join(f'/assets/landing/{image["path"]} {image["width"]}w' for image in candidates)
        print_artwork = candidates[-1]
        print_header_style = escape('--print-header-image:url("/assets/landing/' + print_artwork["path"] + '")', quote=True)
        hero_entry = ''
        hero_actions = ''
        if active == 'home':
            landing = self.landing[lang]
            hero_actions = '<div class="hero-actions">' + button(landing['try_demo'] + ' →', route(lang, 'demos/')) + button(t['start_analysis'], self.navigation['origins']['analysis'], secondary=True, external=True) + '<span class="hero-reassurance">' + escape(landing['no_station']) + '</span></div>'
            hero_entry = ('<section class="hero-entry" aria-labelledby="landing-title">'
                          '<div class="mobile-intro"><h1 id="landing-title">' + escape(landing['headline']) + '</h1><p>' + escape(landing['intro']) + '</p></div>'
                          '</section>')
            if landing.get('hero_analysis_intro'):
                hero_entry += '<p class="hero-analysis-intro">' + landing['hero_analysis_intro'] + '</p>'
        artwork_class = 'hero-artwork-stage hero-artwork-with-actions' if hero_actions else 'hero-artwork-stage'
        return (
            '<div class="site-navigation-shell landing-header"><nav class="navigation" aria-label="' + t["menu"] + '">'
            '<a class="nav-brand" href="' + route(lang) + '" aria-label="WSPRadar.org — ' + t['home'] + '"><span>WSPRadar.org</span></a>'
            '<button class="nav-toggle" aria-controls="nav-links" aria-expanded="true">' + t["menu"] + '</button><div class="nav-links" id="nav-links">' + '<span class="nav-separator" aria-hidden="true">·</span>'.join(["", *links]) + '</div>'
            + self.language_selector(lang, suffix) + '</nav></div>'
            '<header class="site-header landing-header" style="' + print_header_style + '">'
            '<div class="radar-visual"><div class="' + artwork_class + '"><picture class="radar-artwork" lang="en">'
            '<source type="image/webp" srcset="' + srcset + '" sizes="' + HEADER_IMAGE_SIZES + '" width="' + str(fallback['width']) + '" height="' + str(fallback['height']) + '">'
            '<img lang="' + lang + '" src="/assets/landing/' + fallback['path'] + '" width="' + str(fallback['width']) + '" height="' + str(fallback['height']) + '" alt="' + escape(self.landing[lang]['hero_alt'], quote=True) + '" fetchpriority="high" loading="eager">'
            '</picture>' + hero_actions + '</div>' + hero_entry + '</div></header>'
        )

    def page(self, lang, suffix, title, body, active, *, math=False, root_alias=False, case_study=False):
        t = COPY[lang]
        credit = self.brand['credit_html'][lang]
        release_prefix = 'Release ' + self.brand['app_version'] + ' | '
        developer_credit = credit.removeprefix(release_prefix)
        footer = ('<footer class="site-footer"><div class="footer-main"><span class="footer-wordmark">WSPRadar ' + escape(self.brand['app_version']) + '</span> <span class="footer-tagline">' + self.landing[lang]['footer_tagline'] + '</span> <span class="footer-credit">' + developer_credit + '</span></div><div class="footer-actions"><div class="footer-legal"><a href="' + route(lang,'documentation/full/#sec-disclaimer') + '">' + t['disclaimer'] + '</a></div></div></footer>')
        scripts = ''
        if math:
            scripts = '<script>window.MathJax={tex:{inlineMath:[["\\\\(","\\\\)"]],displayMath:[["\\\\[","\\\\]"]]},options:{ignoreHtmlClass:".*",processHtmlClass:"math"}};</script><script defer src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-mml-chtml.js"></script>'
        entry_script='<script src="/assets/entry.js"></script>' if root_alias else ''
        component_assets = '<link rel="stylesheet" href="/assets/demo-walkthrough.css"><script src="/assets/demo-walkthrough.js" defer></script>' if case_study or active == 'home' or re.search(r'<img\b', body, re.IGNORECASE) else ''
        if suffix == 'demos/' and lang in self.demos_index:
            for name, kind in (('demos-index.css', 'styles'), ('demos-index.js', 'scripts')):
                version = hashlib.sha256((SOURCE / 'theme' / kind / name).read_bytes()).hexdigest()[:16]
                asset = '/assets/' + name + '?v=' + version
                component_assets += ('<link rel="stylesheet" href="' + asset + '">' if kind == 'styles'
                                     else '<script src="' + asset + '" defer></script>')
        navigation_config = {"catalog": self.navigation, "local_analysis_port": self.local_analysis_port}
        navigation_script = '<script id="wspradar-product-navigation" type="application/json">' + json.dumps(navigation_config, ensure_ascii=False).replace("<", "\\u003c") + '</script><script src="/assets/product-navigation.js"></script>'
        html = self.template.substitute(lang=lang,title=escape(title),description=escape(t["intro"],quote=True),canonical=SITE_URL+route(lang,suffix),alternate_en=SITE_URL+route("en",suffix),alternate_de=SITE_URL+route("de",suffix),skip_label=t["skip"],header=self.header(lang,active,suffix),body=body,footer=footer,math_scripts=scripts,entry_script=entry_script,component_assets=component_assets,landing_css_version=self.landing_css_version,print_assets_version=self.print_assets_version,product_design_stylesheet=product_design_stylesheet_html(self.brand,self.manifest),product_navigation_script=navigation_script,body_attrs=(' class="demo-case-page"' if case_study else ' class="demos-index-page"' if suffix == 'demos/' and lang in self.demos_index else ' class="community-page"' if suffix == 'community/' else ' class="documentation-index-page"' if suffix == 'documentation/' else ' class="documentation-reader-page"' if suffix.startswith('documentation/') and suffix != 'documentation/full/' else ''))
        destination = "index.html" if root_alias else f"{lang}/{suffix}index.html"
        self.pages[destination] = load_print_images_with_page(open_pdf_links_in_new_tabs(
            apply_product_navigation_link_policy(html, self.navigation, current_suffix=suffix),
        ))

    def manual_index(self, lang, *, include_disclaimer=True, include_introduction=True):
        """Present the manual parts with optional orientation and disclaimer links."""
        t = COPY[lang]
        groups = []
        current = []
        for section in self.sections[lang]:
            if section.level == 2 and current:
                groups.append(current)
                current = []
            current.append(section)
        if current:
            groups.append(current)
        supplementary_links = []
        chunks = []
        for group in groups:
            first = group[0]
            if first.level != 2 or "part-0" in first.anchors:
                # The introductory chapter has its own featured card; the contents
                # section remains available in the manual and chapter navigation.
                continue
            if len(group) == 1 and not any(anchor.startswith("part-") for anchor in first.anchors):
                if not include_disclaimer and 'sec-disclaimer' in first.anchors:
                    continue
                supplementary_links.append('<a href="' + chapter_url(lang, first.key) + '">' + escape(first.title) + '</a>')
                continue
            entries = []
            for section in group[1:]:
                if "documentation-toc" in section.anchors:
                    continue
                numbered = re.match(r'(?:(?:Appendix|Anhang) )?([0-9]+|[A-Z])[.:] (.+)', section.title)
                if numbered:
                    label = '<span class="chapter-number" aria-hidden="true">' + escape(numbered[1]) + '</span><span>' + escape(numbered[2]) + '</span>'
                    attributes = ' class="numbered-chapter" aria-label="' + escape(section.title, quote=True) + '"'
                else:
                    label = escape(section.title)
                    attributes = ' class="unnumbered-chapter"'
                entries.append('<li><a' + attributes + ' href="' + chapter_url(lang, section.key) + '">' + label + '</a></li>')
            heading_link = '<a href="' + chapter_url(lang, first.key) + '">' + escape(first.title) + '</a>'
            chapter_list = '<ul>' + ''.join(entries) + '</ul>' if entries else ''
            chunks.append('<section class="manual-group"><h3>' + heading_link + '</h3>' + chapter_list + '</section>')
        introduction = ''
        if include_introduction:
            introduction = ('<section class="manual-start" aria-labelledby="manual-start-title">'
                            + '<h2 id="manual-start-title">' + t['manual_start_title'] + '</h2>'
                            + '<p>' + t['manual_start_body'] + '</p>'
                            + '<a class="text-link" href="' + self.anchors[lang]['sec-1'] + '">'
                            + t['manual_start_link'] + ' →</a></section>')
        return (introduction
                + '<div class="manual-index">' + ''.join(chunks) + '</div>'
                + ('<div class="manual-supplementary">' + ''.join(supplementary_links) + '</div>' if supplementary_links else ''))

    def evidence_items(self, lang):
        return self.website["evidence"][lang]

    def evidence_path(self, lang):
        evidence = ''.join('<a class="evidence-step" href="'+self.result_step_url(lang, item['id'])+'"><span class="step-number">'+f'{number:02d}'+'</span><span><strong>'+escape(item["title"])+'</strong><small>'+escape(item["question"])+'</small></span></a>' for number,item in enumerate(self.evidence_items(lang),1))
        return '<div class="evidence-path"><p class="eyebrow">'+COPY[lang]["follow"]+'</p>'+evidence+'</div>'

    def home(self, lang):
        t = COPY[lang]
        analysis_url = self.navigation["origins"]["analysis"]
        body = '<section class="hero overview-hero"><p class="eyebrow">'+t["eyebrow"]+'</p><h2>'+t["hero"]+'</h2><p class="intro">'+t["intro"]+'</p><div class="actions">'+button(t["start"]+' →',route(lang,'demos/'))+button(t["open"],analysis_url,secondary=True,external=True)+'</div></section>'
        steps = (
            ('choose', self.anchors[lang]['sec-2-2']+'#sec-2-2', t['choose_link']),
            ('experiment', self.anchors[lang]['sec-2-1']+'#sec-2-1', t['experiment_link']),
            ('run', analysis_url, t['open']),
        )
        cards = []
        for number, (key, href, label) in enumerate(steps, 1):
            external = href == analysis_url
            attributes = ' target="_blank" rel="noopener noreferrer"' if external else ''
            cards.append('<article class="journey-card"><span class="journey-number" aria-hidden="true">'+f'{number:02d}'+'</span><h2>'+t[key+'_title']+'</h2><p>'+t[key+'_body']+'</p><a class="text-link" href="'+href+'"'+attributes+'>'+label+(' ↗' if external else ' →')+'</a></article>')
        body += '<section class="journey">'+''.join(cards)+'</section>'
        body += '<section class="feature"><h2>'+t["demo_feature"]+'</h2><p>'+t["demo_context"]+'</p><p class="muted">'+t["demo_summary"]+'</p>'+button(t["browse_demos"]+' →',route(lang,'demos/'))+'</section>'
        body += '<section><div class="section-heading"><h2>'+t["all_docs"]+'</h2></div>'+self.manual_index(lang, include_disclaimer=False, include_introduction=False)+'</section>'
        body += '<section class="support-strip"><div><h2>'+t["connect"]+'</h2><p>'+t["connect_body"]+'</p><a class="text-link" href="'+route(lang,'community/')+'">'+t["community"]+' →</a></div><div><h2>'+t["improve"]+'</h2><p>'+t["improve_body"]+'</p><a class="text-link" href="'+route(lang,'report/')+'">'+t["bug"]+' →</a></div></section>'
        body = render_landing(self, lang, button, route, analysis_url) + '<details class="more-guidance" id="more-guidance"><summary>' + escape(self.landing[lang]['more_guidance']) + '</summary>' + body + '</details>'
        self.page(lang,'',t["home"],body,'home')
        if lang == 'en':
            self.page(lang,'',t["home"],body,'home',root_alias=True)

    def result_step_url(self, lang, step):
        if lang != 'en':
            return route(lang, 'guides/read-results/#' + step)
        anchors = {'map-view':'sec-3-4', 'segment-inspector':'sec-3-6',
                   'station-insights':'sec-3-7', 'drill-down':'sec-3-8'}
        anchor = anchors[step]
        return self.anchors[lang][anchor] + '#' + anchor

    def illustrated_manual(self, text, lang):
        """Add website-owned demo figures without changing canonical manual prose."""
        for placement in self.manual_figures.get(lang, []):
            anchor = placement["before_anchor"]
            marker = '<a id="' + anchor + '"></a>'
            if marker not in text:
                continue  # This chapter does not contain the placement.
            demo_id = placement["demo_id"]
            config = self.demo_walkthroughs["demos"][demo_id]
            resources = json_read(safe_path(self.demo_asset_root, config["resource_manifest"]))
            media = {item["key"]: (item, '/assets/demos/' + demo_id + '/')
                     for item in resources["figures"]}
            media.update({item["key"]: (item, '/content/')
                          for item in (*self.figures, *self.screenshots)
                          if item["demo_id"] == demo_id})
            item, prefix = media[placement["media_key"]]
            original = prefix + item.get("path", item.get("asset_path", ""))
            variants = sorted(item.get("variants", []), key=lambda value: value["width"])
            preview = prefix + variants[0]["path"] if variants else original
            responsive = (' srcset="' + escape(', '.join(prefix + variant["path"] + ' ' + str(variant["width"]) + 'w' for variant in variants), quote=True)
                          + '" sizes="(max-width: 620px) calc(100vw - 64px), 520px"') if variants else ''
            width, height = item.get("provenance", {}).get("image_px", [item.get("width"), item.get("height")])
            demo_url = route(lang, 'demos/' + demo_id + '/#' + placement["demo_anchor"])
            figure = ('<figure class="figure-block manual-figure">'
                      '<a href="' + escape(original, quote=True) + '" data-case-lightbox data-title="' + escape(item["title"][lang], quote=True) + '" aria-label="' + escape(COPY[lang]["full_size"] + ': ' + item["title"][lang], quote=True) + '">'
                      '<img loading="lazy" decoding="async" width="' + str(width) + '" height="' + str(height) + '" src="' + escape(preview, quote=True) + '"' + responsive + ' alt="' + escape(item["alt"][lang], quote=True) + '"></a>'
                      '<figcaption>' + escape(placement["caption"]) + ' <a href="' + escape(demo_url, quote=True) + '">Explore this guided demo →</a></figcaption></figure>')
            text = text.replace(marker, figure + '\n\n' + marker, 1)
        return text

    def documentation(self, lang):
        t = COPY[lang]
        illustrated = self.illustrated_manual(self.manuals[lang], lang)
        pdf_url = '/assets/documentation/WSPRadar_Doc_' + lang.upper() + '.pdf?v=' + self.documentation_pdf_versions[lang]
        pdf_action = '<div class="actions">' + button(t["download_documentation_pdf"] + ' ↗', pdf_url, secondary=True) + '</div>'
        index = '<p class="eyebrow">'+t["docs"]+'</p><h1>'+t["all_docs"]+'</h1><p class="intro">'+t["manual_intro"]+'</p>'+pdf_action+self.manual_index(lang, include_disclaimer=False)
        self.page(lang,'documentation/',t["docs"],index,'docs')
        sidebar = '<details class="reader-index" open><summary>'+t["docs"]+'</summary>' + ''.join('<a class="'+('part-link' if s.level==2 else 'chapter-link')+'" href="'+chapter_url(lang,s.key)+'">'+escape(s.title)+'</a>' for s in self.sections[lang]) + '</details>'
        for number,section in enumerate(split_manual(illustrated)):
            selected = sidebar.replace('href="'+chapter_url(lang,section.key)+'"','aria-current="page" href="'+chapter_url(lang,section.key)+'"')
            article = self.md(section.text,lang)
            article = re.sub(r'<h([23])>(.*?)</h\1>', r'<h1>\2</h1>', article, count=1, flags=re.DOTALL)
            adjacent=[]
            for delta,key in ((-1,"previous"),(1,"next")):
                if 0 <= number+delta < len(self.sections[lang]):
                    neighbor=self.sections[lang][number+delta]
                    adjacent.append('<a href="'+chapter_url(lang,neighbor.key)+'">'+t[key]+': '+escape(neighbor.title)+'</a>')
            body='<p class="breadcrumb"><a href="'+route(lang,'documentation/')+'">'+t["docs"]+'</a> / '+escape(section.title)+'</p><div class="reader-layout">'+selected+'<article class="prose">'+article+'<nav class="doc-actions" aria-label="'+t["docs"]+'">'+''.join(adjacent)+'</nav></article></div>'
            active = 'docs'
            self.page(lang,'documentation/'+section.key+'/',section.title,body,active,math=True)
        body='<h1>'+t["all_docs"]+'</h1><p class="print-note">'+t["print"]+'</p><div class="prose">'+self.md(illustrated,lang,continuous=True)+'</div>'
        self.page(lang,'documentation/full/',t["full_manual"],body,'docs',math=True)

    def media(self, item, lang, *, screenshot=False):
        t=COPY[lang]
        url='/content/'+item['asset_path']
        caption=self.md(item.get('caption',{}).get(lang,''),lang)
        provenance=item.get('provenance',{})
        detail=''
        if screenshot:
            captured_utc = str(provenance.get('captured_at_utc', provenance.get('captured_utc', '')))
            detail = escape(t['english_capture']) + ' <span class="technical-value">' + escape(captured_utc) + '</span>'
        size=provenance.get('image_px', [item.get('width'),item.get('height')])
        dimensions=f' width="{int(size[0])}" height="{int(size[1])}"' if all(size) else ''
        label=escape(t['full_size']+': '+item['title'][lang],quote=True)
        return '<figure class="figure-block"><a href="'+escape(url,quote=True)+'" target="_blank" rel="noopener noreferrer" data-case-lightbox data-title="'+escape(item['title'][lang],quote=True)+'" aria-label="'+label+'"><img loading="lazy"'+dimensions+' src="'+escape(url,quote=True)+'" alt="'+escape(item['alt'][lang],quote=True)+'"></a><figcaption><strong>'+escape(item['title'][lang])+'</strong>'+caption+'<a href="'+escape(url,quote=True)+'" target="_blank" rel="noopener noreferrer">'+t['full_size']+' ↗</a>'+('<span class="source-note">'+detail+'</span>' if detail else '')+'</figcaption></figure>'

    def demo_pages(self,lang):
        t=COPY[lang]
        cards=[]
        authored={d['id']:d for d in self.website['demos']}
        for demo in self.published_demos:
            identity=demo['id']
            presentation = self.demo_walkthroughs.get('demos', {}).get(identity)
            if not presentation:
                raise ValueError('Missing default Markdown walkthrough for demo: ' + identity)
            hero = read_sections(safe_path(self.demo_root, presentation['markdown_paths'][lang]))['hero']
            title, _ = heading_and_body(hero, 1)
            figures=[f for f in self.figures if f['demo_id']==identity]
            screenshots=[s for s in self.screenshots if s['demo_id']==identity]
            steps=authored.get(identity,{}).get('walkthrough',{}).get(lang,[])
            settings=demo['settings']['core_parameters']
            meta=presentation['languages'][lang]['mode']+' · '+settings['band']+' · '+settings['callsign']
            summary=steps[0]['body'] if steps else ''
            preview=('<img src="/content/'+figures[0]['asset_path']+'" alt="'+escape(figures[0]['alt'][lang],quote=True)+'" loading="lazy">') if figures else ''
            cards.append('<article class="demo-card" data-filter-text="'+escape(title+' '+meta+' '+summary,quote=True)+'">'+preview+'<p class="meta">'+escape(meta)+'</p><h2>'+escape(title)+'</h2><a class="text-link" href="'+route(lang,'demos/'+identity+'/')+'">'+t['walkthrough']+' →</a></article>')
            body = render_demo(self, lang, demo, presentation, button, route, self.navigation["origins"]["analysis"])
            self.page(lang,'demos/'+identity+'/',title,body,'demos',math=True,case_study=True)
        total = str(len(cards))
        body='<p class="eyebrow">'+t['demos']+'</p><h1>'+t['demo_title']+'</h1><p class="intro">'+t['demo_intro']+'</p><label class="search-label">'+t['filter']+'<input type="search" data-filter-input autocomplete="off"></label><p class="small muted" data-filter-status aria-live="polite">'+total+' / '+total+'</p><div class="demo-grid">'+''.join(cards)+'</div>'
        if lang in self.demos_index:
            body = render_demos_index(self.demos_index[lang], self.published_demos, self.landing_assets,
                                      SOURCE / 'theme' / 'templates' / 'demos-index.html',
                                      lang, route)
        self.page(lang,'demos/',t['demos'],body,'demos')

    def guides(self,lang):
        t=COPY[lang]
        anchor_names={'map-view':'sec-3-4','segment-inspector':'sec-3-6','station-insights':'sec-3-7','drill-down':'sec-3-8'}
        if lang == 'en':
            target = self.anchors[lang]['sec-2-3-overview'] + '#sec-2-3-overview'
            destinations = {key:self.anchors[lang][anchor] + '#' + anchor for key,anchor in anchor_names.items()}
            body = ('<p class="breadcrumb"><a href="' + route(lang,'documentation/') + '">' + t['docs'] + '</a></p>'
                    '<h1>Read the results in the manual</h1><p><a href="' + target + '">Open Section 1.3: Navigate the results →</a></p>'
                    '<script>location.replace((' + json.dumps(destinations) + ')[location.hash.slice(1)] || ' + json.dumps(target) + ');</script>')
            self.page(lang,'guides/read-results/',t['guides_title'],body,'docs')
            return
        capture_stages={'map-view':'map','segment-inspector':'segment','station-insights':'stations','drill-down':'drilldown'}
        body='<p class="breadcrumb"><a href="'+route(lang,'documentation/')+'">'+t['docs']+'</a></p><p class="eyebrow">'+t['follow']+'</p><h1>'+t['guides_title']+'</h1><p class="intro">'+t['guides_intro']+'</p><nav class="guide-links" aria-label="'+t['follow']+'">'+''.join('<a href="#'+i['id']+'">'+escape(i['title'])+'</a>' for i in self.evidence_items(lang))+'</nav>'
        for n,item in enumerate(self.evidence_items(lang),1):
            shots=[s for s in self.screenshots if s.get('stage')==capture_stages[item['id']]
                   and s['demo_id'] in self.demo_walkthroughs['demos']]
            shot=shots[0] if shots else None
            body+='<section class="guide-section" id="'+item['id']+'"><p class="eyebrow">'+f'{n:02d}'+' · '+escape(item['title'])+'</p><h2>'+escape(item['question'])+'</h2><div class="prose">'+self.md(item['body'],lang)+'</div>'
            if shot:body+=self.media(shot,lang,screenshot=True)
            anchor=anchor_names[item['id']]
            example=shot['demo_id'] if shot else self.published_demos[0]['id']
            body+='<div class="guide-links"><a href="'+self.anchors[lang][anchor]+'#'+anchor+'">'+t['read_manual']+' →</a><a href="'+route(lang,'demos/'+example+'/')+'">'+t['related_demo']+' →</a></div></section>'
        self.page(lang,'guides/read-results/',t['guides_title'],body,'guides',math=True)

    def support(self,lang):
        t=COPY[lang]
        options=[
            ('questions',('questions_body',),HELP_URL,'ask'),
            ('experiments',('experiments_body',),EXPERIMENTS_URL,'share_experiment'),
            ('feature',('feature_body',),IDEAS_URL,'continue'),
            ('report_category',('report_summary',),REPORT_URL,'continue'),
        ]
        cards='<div class="report-options">'
        for key,paragraphs,url,action in options:
            cards+='<article><h2>'+t[key]+'</h2>'+''.join('<p>'+t[body].format(manual_url=route(lang,'documentation/full/'))+'</p>' for body in paragraphs)
            cards+='<div class="actions">'+button(t[action],url,external=True)
            cards+='</div></article>'
        cards+='</div>'
        participation='<p>'+t['participation']+'</p>'
        self.page(lang,'community/',t['community'],'<p class="eyebrow">'+t['community']+'</p><h1>'+t['community_title']+'</h1><p class="intro">'+t['community_intro']+'</p>'+participation+cards,'community')
        self.page(lang,'report/',t['bug'],'<p class="eyebrow">'+t['improve']+'</p><h1>'+t['bug']+'</h1><p class="intro">'+t['bug_intro']+'</p>'+participation+'<div class="actions">'+button(t['continue'],REPORT_URL,external=True)+'</div><p>'+t['scientific_body']+'</p><p>'+t['report_body']+'</p><p>'+t['report_followup']+'</p>'+cards,'bug')

    def render(self):
        for lang in COPY:
            self.home(lang)
            self.documentation(lang)
            self.demo_pages(lang)
            self.guides(lang)
            self.support(lang)
        return self.pages


class LinkInventory(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=[]
        self.links=[]
        self.images=[]
    def handle_starttag(self,tag,attributes):
        attrs=dict(attributes)
        if 'id' in attrs:self.ids.append(attrs['id'])
        if tag in ('a','link') and 'href' in attrs:self.links.append(attrs['href'])
        if tag in ('img','script') and attrs.get('src','').startswith('/'):self.links.append(attrs['src'])
        if tag in ('source','img') and attrs.get('srcset'):
            self.links.extend(candidate.strip().split()[0] for candidate in attrs['srcset'].split(',') if candidate.strip().startswith('/'))
        if tag=='img':self.images.append(attrs)


def validate_site(directory: Path):
    inventories={}
    errors=[]
    for page in directory.rglob('*.html'):
        inventory=LinkInventory()
        inventory.feed(page.read_text(encoding='utf-8'))
        inventories[page.resolve()]=inventory
        if len(inventory.ids)!=len(set(inventory.ids)):errors.append(f'Duplicate HTML IDs: {page.relative_to(directory)}')
        if any('alt' not in image or (not image['alt'] and image.get('aria-hidden') != 'true') for image in inventory.images):errors.append(f'Image missing alt: {page.relative_to(directory)}')
    for page,inventory in inventories.items():
        for href in inventory.links:
            url=urlsplit(href)
            if url.scheme or url.netloc:continue
            target=((directory / unquote(url.path).lstrip('/')) if url.path.startswith('/') else (page.parent / unquote(url.path))).resolve() if url.path else page
            if not target.is_relative_to(directory.resolve()):errors.append(f'Escaping link: {href}');continue
            if target.is_dir():target=target/'index.html'
            if not target.is_file():errors.append(f'Missing local target: {page.relative_to(directory)} -> {href}');continue
            if url.fragment and target in inventories and unquote(url.fragment) not in inventories[target].ids:
                errors.append(f'Missing anchor: {page.relative_to(directory)} -> {href}')
    if errors:raise ValueError('\n'.join(sorted(set(errors))))
    return len(inventories)


def demo_supplement_files(root: Path) -> dict[str, bytes]:
    """Publish only explicitly reviewed PDFs with verified source bytes."""
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    if (not isinstance(manifest, dict) or set(manifest) != {"schema_version", "files"}
            or type(manifest["schema_version"]) is not int
            or manifest["schema_version"] != 1
            or not isinstance(manifest["files"], dict)):
        raise ValueError("Invalid demo supplement PDF manifest")
    output = {}
    for name, record in manifest["files"].items():
        relative = PurePosixPath(name)
        source = (root / name).resolve()
        if (relative.is_absolute() or ".." in relative.parts or "\\" in name
                or relative.as_posix() != name or relative.suffix.lower() != ".pdf"
                or not source.is_relative_to(root.resolve())):
            raise ValueError("Unsafe demo supplement PDF path: " + name)
        if (not isinstance(record, dict) or set(record) != {"bytes", "sha256"}
                or type(record["bytes"]) is not int or record["bytes"] < 1
                or not isinstance(record["sha256"], str)
                or not re.fullmatch(r"[0-9a-f]{64}", record["sha256"])):
            raise ValueError("Invalid demo supplement PDF record: " + name)
        payload = source.read_bytes()
        if len(payload) != record["bytes"] or hashlib.sha256(payload).hexdigest() != record["sha256"]:
            raise ValueError("Demo supplement PDF hash mismatch: " + name)
        if not payload.startswith(b"%PDF-"):
            raise ValueError("Demo supplement PDF signature missing: " + name)
        output["assets/demos/" + name] = payload
    return output


def output_files(builder: SiteBuilder) -> dict[str, bytes]:
    """Construct the complete static payload before writing or checking it."""
    pages=builder.render()
    files={name:value.encode('utf-8') for name,value in pages.items()}
    for name in ('site.css','landing.css','print.css','print.js','site.js','entry.js','product-navigation.js','demo-walkthrough.css','demo-walkthrough.js','demos-index.css','demos-index.js'):
        category = 'styles' if name.endswith('.css') else 'scripts'
        files['assets/'+name]=(SOURCE/'theme'/category/name).read_bytes()
    for name in builder.landing_assets['publish_files']:
        relative = PurePosixPath(name)
        if relative.is_absolute() or '..' in relative.parts or '\\' in name:
            raise ValueError('Unsafe landing asset path: ' + name)
        files['assets/landing/' + name] = builder.landing_payload[name]
    files.update(resource_files(builder.demo_asset_root, builder.demo_walkthroughs["demos"],
                                source_root=SOURCE))
    supplements = demo_supplement_files(DEMO_SUPPLEMENTS)
    duplicate_supplements = files.keys() & supplements.keys()
    if duplicate_supplements:
        raise ValueError("Duplicate demo supplement output: " + ", ".join(sorted(duplicate_supplements)))
    files.update(supplements)
    files.update(builder.documentation_pdfs)
    legacy_logo = SOURCE / 'assets' / 'brand' / 'WSPRadar-2x1.png'
    files['img/WSPRadar-2x1.png'] = legacy_logo.read_bytes()
    colors=builder.brand.get('colors',{})
    theme={variable:colors[key] for variable,key in (('--bg','background'),('--green','primary'),('--text','text')) if key in colors}
    if any(not re.fullmatch(r'#[0-9a-fA-F]{6}',value) for value in theme.values()):
        raise ValueError('Invalid imported brand color')
    if '--green' in theme:
        theme['--green']='var(--product-green,'+theme['--green']+')'
    if theme:
        files['assets/site.css']+=('\n:root{'+''.join(key+':'+value+';' for key,value in theme.items())+'}\n').encode('utf-8')
    fonts=[]
    for font in builder.brand['fonts']:
        fonts.append('@font-face{font-family:"'+font['family']+'";font-style:'+font['style']+';font-weight:'+str(font['weight'])+';font-display:swap;src:url("/content/'+font['path']+'") format("woff2");'+('unicode-range:'+font['unicode_range']+';' if font.get('unicode_range') else '')+'}')
    files['assets/fonts.css']=('\n'.join(fonts)+'\n').encode('utf-8')
    for name in (*builder.manifest['files'],'manifest.json'):
        files['content/'+name]=(builder.content/name).read_bytes()
    files['CNAME']=b'www.wspradar.org\n'
    files['.nojekyll']=b''
    sitemap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+SITE_URL+'/'+name.removesuffix('index.html')+'</loc></url>' for name in sorted(pages) if name!='index.html')+'</urlset>\n'
    files['sitemap.xml']=sitemap.encode('utf-8')
    files['robots.txt']=('User-agent: *\nAllow: /\nSitemap: '+SITE_URL+'/sitemap.xml\n').encode('utf-8')
    return files


def build(*, check=False, offline=False, local_analysis_port=None):
    if offline and not check:
        raise ValueError('--offline is only valid with --check')
    builder=SiteBuilder(local_analysis_port=local_analysis_port)
    files=output_files(builder)
    actual={p.relative_to(OUTPUT).as_posix() for p in OUTPUT.rglob('*') if p.is_file()}
    extra=actual-set(files)
    if extra:
        raise ValueError('Unexpected build files; review before removal: '+', '.join(sorted(extra)))
    for name,data in files.items():
        path=OUTPUT/name
        if not path.resolve().is_relative_to(OUTPUT.resolve()):
            raise ValueError(f'Unsafe build output path: {name}')
        if check:
            if not path.is_file() or path.read_bytes()!=data:
                raise ValueError(f'Missing or stale built file: {name}')
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(data)
    count=validate_site(OUTPUT)
    if check:
        print(f'Checked {count} pages, {len(files)} files, local links, anchors, and image alternatives.')
        if offline:
            print('External URLs not checked (--offline); only local build validation completed.')
            return
        links=collect_external_links(files,SITE_URL)
        print(f'Checking {len(links)} distinct external HTTP(S) URLs without authentication...',flush=True)
        results=check_external_links(links,community_url=COMMUNITY_URL)
        counts={status:sum(result.status==status for result in results)
                for status in ('available','redirected','broken','unverified')}
        for result in results:
            if result.status=='available':
                continue
            locations=', '.join(result.locations[:3])
            if len(result.locations)>3:
                locations+=f' (+{len(result.locations)-3} more files)'
            print(f'{result.status.upper()}: {result.url}\n  {result.detail}\n  Referenced in: {locations}')
        print('External URLs: '+', '.join(f'{count} {status}' for status,count in counts.items())+'.')
        if counts['broken'] or counts['unverified']:
            raise ValueError('External URL validation incomplete: broken or unverified URLs remain; see details above.')
        return
    print(f'Built {count} pages with complete bilingual manuals and {len(builder.published_demos)} demos.')
    print(f'Imported {len(builder.figures)} figures and {len(builder.screenshots)} live screenshots.')


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true',help='Verify generated files, local links, and live external HTTP(S) URLs without writing')
    parser.add_argument('--offline',action='store_true',help='With --check, explicitly skip live external URL validation')
    parser.add_argument('--local-analysis-port', type=int, help='Override the local-only analysis port (default from shared navigation); production URLs remain unchanged')
    args=parser.parse_args(argv)
    if args.offline and not args.check:
        parser.error('--offline requires --check')
    try:
        build(check=args.check,offline=args.offline,local_analysis_port=args.local_analysis_port)
    except ValueError as error:
        parser.exit(1,f'Validation failed: {error}\n')


if __name__=='__main__':
    main()


