"""Focused static-site contracts, independent of the Streamlit application."""

from __future__ import annotations

from collections import Counter
from contextlib import redirect_stdout
from copy import deepcopy
import hashlib
from html import escape, unescape
from html.parser import HTMLParser
from io import BytesIO, StringIO
import json
from pathlib import Path
import re
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, unquote, urljoin, urlsplit

from scripts import build_site, demo_walkthrough


class AnchorInventory(HTMLParser):
    """Read rendered link destinations and accessible text for route contracts."""

    def __init__(self) -> None:
        super().__init__()
        self.anchors = []
        self.current = None

    def handle_starttag(self, tag, attributes) -> None:
        if tag == "a":
            self.current = {"attributes": dict(attributes), "text": ""}

    def handle_data(self, data) -> None:
        if self.current is not None:
            self.current["text"] += data

    def handle_endtag(self, tag) -> None:
        if tag == "a" and self.current is not None:
            self.anchors.append(self.current)
            self.current = None


class TemporarySiteTests(unittest.TestCase):
    """Keep every test mutation in one automatically cleaned scratch directory."""

    def setUp(self) -> None:
        scratch = Path(__file__).resolve().parents[1] / ".tmp"
        scratch.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix="site-contract-test-", dir=scratch)
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def write(self, relative: str, content: str | bytes) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))
        return path


class PublishedDemoSelectionTests(unittest.TestCase):
    """Website publication selects canonical records without changing the app catalog."""

    def test_selection_preserves_imported_order_and_record_identity(self) -> None:
        demos = [{"id": "one", "settings": {"value": 1}}, {"id": "two"}, {"id": "three"}]
        original = deepcopy(demos)
        walkthroughs = {"demos": {"three": {}, "one": {}}}
        selected = build_site.select_published_demos(demos, walkthroughs)
        self.assertEqual([demo["id"] for demo in selected], ["one", "three"])
        self.assertIs(selected[0], demos[0])
        self.assertIs(selected[1], demos[2])
        self.assertEqual(demos, original)
        self.assertEqual(list(walkthroughs["demos"]), ["three", "one"])

    def test_selection_rejects_missing_empty_or_malformed_definitions(self) -> None:
        for walkthroughs in ({}, {"demos": {}}, {"demos": []}, {"demos": None},
                             {"demos": ["one"]}, {"demos": "one"}):
            with self.subTest(walkthroughs=walkthroughs), self.assertRaisesRegex(
                    ValueError, "Published demo definitions"):
                build_site.select_published_demos([{"id": "one"}], walkthroughs)

    def test_selection_rejects_unknown_demo_ids(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown published demo IDs"):
            build_site.select_published_demos([{"id": "one"}], {"demos": {"unknown": {}}})


class ProductNavigationContractTests(unittest.TestCase):
    """The exported presentation catalog owns routes on both product surfaces."""

    def test_imported_navigation_requires_explicit_safe_bilingual_routes(self):
        brand = json.loads((build_site.CONTENT / "brand.json").read_text(encoding="utf-8"))
        catalog = build_site.product_navigation_catalog(brand)
        self.assertEqual([item["id"] for item in catalog["items"]],
                         ["overview", "demos", "analysis", "documentation", "community"])
        self.assertEqual(catalog["origins"]["analysis"], build_site.APP_URL)
        self.assertEqual(catalog["local"], {"website_port": 8787, "analysis_port": 8501})
        for mutation in ("path", "language", "duplicate"):
            invalid = deepcopy(brand)
            candidate = invalid["product_navigation"]["catalog"]
            if mutation == "path":
                candidate["items"][0]["path"] = "../private/"
            elif mutation == "language":
                del candidate["items"][0]["label"]["de"]
            else:
                candidate["items"].append(deepcopy(candidate["items"][0]))
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                build_site.product_navigation_catalog(invalid)

    def test_preview_override_only_changes_runtime_routing_configuration(self):
        builder = build_site.SiteBuilder(local_analysis_port=8521)
        for language in ("en", "de"):
            header = builder.header(language, "home", "")
            self.assertNotIn('<span class="launch">', header)
            self.assertIn(build_site.COPY[language]["start_analysis"], header)
            self.assertIn(builder.landing[language]["try_demo"], header)
            builder.page(language, "", "Preview", "<p>Preview</p>", "home", root_alias=language == "en")
        for page in builder.pages.values():
            script = re.search(r'<script id="wspradar-product-navigation" type="application/json">(.*?)</script>', page)
            self.assertIsNotNone(script)
            configuration = json.loads(script[1])
            self.assertEqual(configuration["local_analysis_port"], 8521)
            self.assertEqual(configuration["catalog"]["origins"]["analysis"], build_site.APP_URL)
            self.assertLess(page.index('/assets/product-navigation.js'), page.find('/assets/entry.js') if '/assets/entry.js' in page else len(page))
        with self.assertRaises(ValueError):
            build_site.SiteBuilder(local_analysis_port=70000)

    def test_analysis_tab_policy_covers_raw_and_markdown_links_without_changing_destinations(self):
        builder = build_site.SiteBuilder()
        launch = builder.demos[0]["launch_url"]
        markdown = builder.md(f'[Markdown demo]({launch})', "en")
        body = (markdown + '<a data-test="raw" href="' + escape(launch, quote=True)
                + '" target="_blank" rel="external noopener noreferrer">Raw demo</a>'
                + '<a href="' + build_site.APP_URL + '" target="other">Analysis</a>')
        builder.page("en", "tab-policy/", "Launch navigation", body, "home")
        inventory = AnchorInventory()
        inventory.feed(builder.pages["en/tab-policy/index.html"])
        links = [anchor for anchor in inventory.anchors if anchor["text"] in {"Markdown demo", "Raw demo", "Analysis"}]
        self.assertTrue(links)
        self.assertEqual([anchor["attributes"]["href"] for anchor in links
                          if anchor["text"] in {"Markdown demo", "Raw demo"}], [launch, launch])
        for anchor in links:
            self.assertNotIn("target", anchor["attributes"])

    def test_all_guided_demo_destinations_keep_the_walkthrough_open(self):
        builder = build_site.SiteBuilder()
        for demo in builder.published_demos:
            destinations = [demo["launch_url"], *demo.get("launch_variants", {}).values()]
            for language in ("en", "de"):
                suffix = "demos/" + demo["id"] + "/"
                body = ''.join(build_site.button("Run demo", destination, external=True)
                               + builder.md(f'[Inline demo]({destination})', language)
                               for destination in destinations)
                builder.page(language, suffix, "Demo launch policy", body, "demos")
                inventory = AnchorInventory()
                inventory.feed(builder.pages[language + "/" + suffix + "index.html"])
                launches = [anchor for anchor in inventory.anchors
                            if anchor["attributes"].get("href") in destinations]
                with self.subTest(demo=demo["id"], language=language):
                    self.assertEqual([anchor["attributes"]["href"] for anchor in launches],
                                     [destination for destination in destinations for _ in range(2)])
                    for anchor in launches:
                        self.assertEqual(anchor["attributes"]["target"], "_blank")
                        self.assertTrue({"noopener", "noreferrer"}.issubset(anchor["attributes"]["rel"].split()))
                        if "button" in anchor["attributes"].get("class", "").split():
                            self.assertEqual(anchor["text"], "Run demo ↗")

    def test_analysis_tab_policy_preserves_unrelated_markup_and_external_targets(self):
        catalog = build_site.product_navigation_catalog(json.loads(
            (build_site.CONTENT / "brand.json").read_text(encoding="utf-8"),
        ))
        preserved = ('<!-- <a href="https://wspradar.streamlit.app/" target="_blank">comment</a> -->'
                     '<script>const text = \'<a href="https://wspradar.streamlit.app/" target="_blank">literal</a>\';</script>'
                     '<a href="/en/documentation/" target="_blank" rel="noopener noreferrer">Docs</a>'
                     '<a href="https://example.org/publication" target="_blank" rel="external">Publication</a>'
                     '<a href="https://wspradar.streamlit.app/~/+/app/static/paper.pdf" target="_blank">PDF</a>')
        source = ('<a href="/?v=1&amp;run=1#wspradar-results-inspection" TARGET="_blank" data-preserve="yes">Demo</a>'
                  + preserved)
        rendered = build_site.apply_product_navigation_link_policy(source, catalog)
        self.assertIn(preserved, rendered)
        self.assertIn('href="/?v=1&amp;run=1#wspradar-results-inspection"', rendered)
        self.assertIn('data-preserve="yes"', rendered)
        self.assertNotIn('TARGET=', rendered)
        self.assertEqual(build_site.apply_product_navigation_link_policy(rendered, catalog), rendered)

    def test_prepared_guided_demo_launches_open_separately_with_exact_destinations(self):
        builder = build_site.SiteBuilder()
        launch = builder.demos[0]["launch_url"]
        suffix = urlsplit(launch)
        relative_launch = "/?" + suffix.query + "#" + suffix.fragment
        direct_launch = build_site.APP_URL + "?" + suffix.query + "#" + suffix.fragment
        body = (builder.md(f'[Markdown demo]({launch})', "en")
                + '<a data-test="raw" href="' + escape(relative_launch, quote=True)
                + '" target="_self" rel="external">Raw demo</a>'
                + build_site.button("Run demo", direct_launch, external=True)
                + '<a href="' + build_site.APP_URL + '">Analysis</a>'
                + '<a href="https://example.org/paper" target="_blank">Paper ↗</a>')
        rendered = build_site.apply_product_navigation_link_policy(
            body, builder.navigation, current_suffix="demos/example/",
        )
        inventory = AnchorInventory()
        inventory.feed(rendered)
        launches = inventory.anchors[:3]
        self.assertEqual([anchor["attributes"]["href"] for anchor in launches],
                         [launch, relative_launch, direct_launch])
        for anchor in launches:
            self.assertEqual(anchor["attributes"]["target"], "_blank")
            self.assertTrue({"noopener", "noreferrer"}.issubset(anchor["attributes"]["rel"].split()))
        self.assertIn("external", launches[1]["attributes"]["rel"].split())
        self.assertEqual(launches[2]["text"], "Run demo ↗")
        self.assertNotIn("target", inventory.anchors[3]["attributes"])
        self.assertIn('<a href="https://example.org/paper" target="_blank">Paper ↗</a>', rendered)
        self.assertEqual(build_site.apply_product_navigation_link_policy(
            rendered, builder.navigation, current_suffix="demos/example/",
        ), rendered)
        demo_index = AnchorInventory()
        demo_index.feed(build_site.apply_product_navigation_link_policy(
            body, builder.navigation, current_suffix="demos/",
        ))
        for anchor in demo_index.anchors[:4]:
            self.assertNotIn("target", anchor["attributes"])

    def test_documentation_entries_open_a_new_tab_but_main_and_reader_navigation_stay_current(self):
        catalog = build_site.product_navigation_catalog(json.loads(
            (build_site.CONTENT / "brand.json").read_text(encoding="utf-8"),
        ))
        for language in ("en", "de"):
            source = f'<a href="/{language}/documentation/full/#sec-1" class="button">Documentation →</a>'
            outside = build_site.apply_product_navigation_link_policy(source, catalog)
            inventory = AnchorInventory()
            inventory.feed(outside)
            self.assertEqual(inventory.anchors[0]["attributes"]["target"], "_blank")
            self.assertEqual(set(inventory.anchors[0]["attributes"]["rel"].split()), {"noopener", "noreferrer"})
            self.assertEqual(build_site.apply_product_navigation_link_policy(
                source, catalog, current_suffix="documentation/full/",
            ), source)
            navigation = (f'<a href="/{language}/documentation/" '
                          'data-product-nav="documentation" target="_blank">Documentation</a>')
            same_tab = build_site.apply_product_navigation_link_policy(navigation, catalog)
            inventory = AnchorInventory()
            inventory.feed(same_tab)
            self.assertNotIn("target", inventory.anchors[0]["attributes"])
            self.assertEqual(build_site.apply_product_navigation_link_policy(same_tab, catalog), same_tab)

    def test_same_tab_actions_use_forward_arrows_and_publication_arrows_remain(self):
        catalog = build_site.product_navigation_catalog(json.loads(
            (build_site.CONTENT / "brand.json").read_text(encoding="utf-8"),
        ))
        publication = '<a href="https://example.org/paper" class="button" target="_blank">Paper ↗</a>'
        action = build_site.button("Start analysis", build_site.APP_URL, external=True)
        rendered = build_site.apply_product_navigation_link_policy(action + publication, catalog)
        self.assertIn("Start analysis →</a>", rendered)
        self.assertIn(publication, rendered)


class ProductDesignContractTests(unittest.TestCase):
    """Import shared tokens without altering reviewed website defaults."""

    def test_shared_stylesheet_is_source_hashed_and_legacy_bundles_remain_supported(self):
        self.assertEqual(build_site.product_design_stylesheet_html({}, {"files": {}}), "")
        brand = {"product_design": {"schema_version": 1, "stylesheet": "assets/brand/product-tokens.css"}}
        manifest = {"files": {"assets/brand/product-tokens.css": {"sha256": "a" * 64}}}
        self.assertEqual(
            build_site.product_design_stylesheet_html(brand, manifest),
            '<link rel="stylesheet" href="/content/assets/brand/product-tokens.css?v=' + "a" * 16 + '">',
        )
        brand["product_design"]["stylesheet"] = "../private.css"
        with self.assertRaisesRegex(ValueError, "Invalid imported product-design"):
            build_site.product_design_stylesheet_html(brand, manifest)

    def test_shared_stylesheet_requires_a_verified_bundle_entry(self):
        brand = {"product_design": {"schema_version": 1, "stylesheet": "assets/brand/product-tokens.css"}}
        with self.assertRaisesRegex(ValueError, "missing from the verified bundle"):
            build_site.product_design_stylesheet_html(brand, {"files": {}})

    def test_buttons_use_the_shared_blue_controls_without_recoloring_content(self):
        brand = json.loads((build_site.CONTENT / "brand.json").read_text(encoding="utf-8"))
        tokens = (build_site.CONTENT / brand["product_design"]["stylesheet"]).read_text(encoding="utf-8")
        for name, color in (("control-accent", "#24d3f2"), ("control-border", "#214b60"),
                            ("control-active-bg", "#0c3542")):
            self.assertIn(f"--product-{name}:{color};", tokens)
        source = (build_site.SOURCE / "theme" / "styles" / "site.css").read_text(encoding="utf-8")
        base = re.search(r"\.button\{([^{}]*)\}", source)[1]
        self.assertIn("background:var(--product-control-active-bg)", base)
        self.assertIn("border:1px solid var(--product-control-accent)", base)
        self.assertIn("color:var(--text)!important", base)
        self.assertIn("min-height:44px", base)
        secondary = re.search(r"\.button\.secondary\{([^{}]*)\}", source)[1]
        self.assertIn("background:transparent", secondary)
        self.assertIn("border-color:var(--product-control-border)", secondary)
        for name in ("site.css", "landing.css", "demo-walkthrough.css"):
            stylesheet = (build_site.SOURCE / "theme" / "styles" / name).read_text(encoding="utf-8")
            for selector, declarations in re.findall(r"([^{}]+)\{([^{}]*)\}", stylesheet):
                if ".button" in selector or ".nav-toggle" in selector or ".case-dialog button" in selector:
                    self.assertNotRegex(declarations, r"#(?:39ff14|39ed26|72ff63|22f45b)|rgba\(57,255,20")
        self.assertIn(".landing-header .nav-links>a[aria-current=page]{font-weight:700}", (build_site.SOURCE / "theme" / "styles" / "landing.css").read_text(encoding="utf-8"))
        self.assertIn("--product-green:#2cfa77;", tokens)

    def test_demo_heading_tokens_preserve_current_desktop_and_compact_defaults(self):
        css = (build_site.SOURCE / "theme" / "styles" / "demo-walkthrough.css").read_text(encoding="utf-8")
        defaults = {
            "number-size": "52px", "number-border": "#2d718b", "number-radius": "8px",
            "number-bg": "#041a29", "number-font-size": "32px", "heading-gap": "18px",
            "section-title-size": "32px", "compact-number-size": "44px",
            "compact-number-height": "46px", "compact-number-font-size": "29px",
            "section-title-size-mobile": "30px", "cyan": "#36d9ff",
        }
        for name, value in defaults.items():
            self.assertIn(f"var(--product-{name},{value})", css)
        self.assertIn("--case-green:var(--product-green)", css)
        self.assertIn("var(--product-heading,Rajdhani,Arial,sans-serif)", css)
        self.assertIn(
            "font-family:var(--product-heading,Rajdhani,Arial,sans-serif)",
            (build_site.SOURCE / "theme" / "styles" / "site.css").read_text(encoding="utf-8"),
        )


class ManualRenderingTests(unittest.TestCase):
    """Keep chapter links and continuous-reader links faithful to their context."""

    def test_partition_preserves_all_source_text_and_compatibility_anchors(self) -> None:
        source = '\n---\n\n<a id="preface"></a>\n### 0. Introduction\n\nOpening  spaces.\n\n<a id="part-one"></a>\n## Part I\n\n<a id="legacy-one"></a>\n<a id="chapter-one"></a>\n### 1. First chapter\n\nComplete final text.\n'
        sections = build_site.split_manual(source)
        self.assertEqual("".join(section.text for section in sections), source)
        self.assertEqual([section.key for section in sections], ["preface", "part-one", "legacy-one"])
        self.assertEqual(sections[-1].anchors, ("legacy-one", "chapter-one"))
        self.assertIn("Opening  spaces.", sections[0].text)

    def test_part_zero_subsections_keep_the_existing_introductory_page(self) -> None:
        source = '\n'.join((
            '<a id="sec-1"></a>', '<a id="part-0"></a>',
            '## Part 0: Why WSPRadar', 'Opening  spaces.',
            '<a id="sec-1-1"></a>', '### 0.1 WSPR in 2 Minutes', 'First text.',
            '<a id="sec-1-0"></a>', '<a id="sec-1-2"></a>',
            '### 0.2 What WSPRadar can show', 'Second text.',
            '<a id="sec-1-3"></a>', '### 0.3 What one run produces', 'Third text.',
            '<a id="sec-1-4"></a>', '### 0.4 Your first useful run', 'Fourth text.',
            '<a id="documentation-toc"></a>', '### Table of Contents', 'Contents.',
            '<a id="part-i"></a>', '## Part I: Operator Guide',
            '<a id="sec-2"></a>', '### 1. Choose and Prepare the Analysis', 'Next text.',
        ))
        sections = build_site.split_manual(source)
        self.assertEqual("".join(section.text for section in sections), source)
        self.assertEqual([section.key for section in sections],
                         ["sec-1", "documentation-toc", "part-i", "sec-2"])
        self.assertEqual([section.level for section in sections], [2, 3, 2, 3])
        self.assertEqual(sections[0].anchors,
                         ("sec-1", "part-0", "sec-1-1", "sec-1-0", "sec-1-2", "sec-1-3", "sec-1-4"))
        self.assertNotIn("documentation-toc", sections[0].anchors)

    def test_chapter_crosslinks_route_to_the_owning_chapter_in_each_language(self) -> None:
        for language in ("en", "de"):
            with self.subTest(language=language):
                target = f"/{language}/documentation/science/"
                rendered = build_site.render_markdown('[Methods](#methods) and <a href="#legacy-methods">legacy link</a>.', language, {"methods": target, "legacy-methods": target})
                inventory = build_site.LinkInventory()
                inventory.feed(rendered)
                self.assertEqual(inventory.links, [target + "#methods", target + "#legacy-methods"])

    def test_continuous_reader_retains_local_fragment_links_and_original_ids(self) -> None:
        rendered = build_site.render_markdown('<a id="methods"></a>\n### Methods\n\n[Read methods](#methods)', "en", {"methods": "/en/documentation/science/"}, continuous=True)
        inventory = build_site.LinkInventory()
        inventory.feed(rendered)
        self.assertIn("methods", inventory.ids)
        self.assertEqual(inventory.links, ["#methods"])

    def test_legacy_reference_pdfs_use_the_website_route_and_preserve_query_and_page(self) -> None:
        prefixes = ("app/static/", "/app/static/", "https://wspradar.streamlit.app/~/+/app/static/",
                    "https://wspradar.streamlit.app/app/static/", "/static/", "https://wspradar.org/static/")
        for prefix in prefixes:
            for suffix in ("example/report.pdf", "example/report.pdf?v=2&view=full#page=3", "example/REPORT.PDF#page=2"):
                with self.subTest(prefix=prefix, suffix=suffix):
                    rendered = build_site.render_markdown(
                        f'[Figure]({prefix}reference_figures/{suffix})', "en", {})
                    inventory = AnchorInventory()
                    inventory.feed(rendered)
                    self.assertEqual(inventory.anchors[0]["attributes"]["href"],
                                     f"/assets/demos/{suffix}")

    def test_legacy_application_media_links_use_the_hosted_static_route(self) -> None:
        for suffix in ("example.pdf", "example.pdf?v=2#page=3"):
            with self.subTest(suffix=suffix):
                rendered = build_site.render_markdown(
                    f'[Asset](app/static/downloads/{suffix})', "en", {})
                self.assertIn(
                    f'href="https://wspradar.streamlit.app/~/+/app/static/downloads/{suffix}"',
                    rendered)
        app_link = '[App](https://wspradar.streamlit.app/?run=1)'
        self.assertIn('href="https://wspradar.streamlit.app/?run=1"',
                      build_site.render_markdown(app_link, "en", {}))

    def test_reference_link_migration_preserves_raw_attributes_and_script_literals(self) -> None:
        preserved = ('<script>const text = \'<a href="app/static/reference_figures/example/report.pdf">literal</a>\';</script>'
                     '<a href="app/static/downloads/report.pdf" target="_blank">Other asset</a>')
        source = ("<a data-source='verified' href='app/static/reference_figures/example/report.pdf?v=2&amp;view=full#page=3' target='_blank'>Figure</a>"
                  + preserved)
        rendered = build_site.website_reference_pdf_links(source)
        self.assertEqual(rendered, source.replace(
            "href='app/static/reference_figures/", "href='/assets/demos/", 1,
        ))
        self.assertIn(preserved, rendered)

    def test_scientific_tables_keep_all_cells_in_an_accessible_scroll_region(self) -> None:
        rendered = build_site.render_markdown('| Station | ΔSNR |\n|---|---|\n| DL1MKS | −2 dB |', "de", {})
        self.assertIn('role="region"', rendered)
        self.assertIn('aria-label="Scrollbare Tabelle"', rendered)
        self.assertIn("DL1MKS", rendered)
        self.assertIn("−2 dB", rendered)
        self.assertEqual(rendered.count("<table>"), 1)
        self.assertEqual(rendered.count("</table></div>"), 1)

    def test_table_headers_follow_the_markdown_column_alignment(self) -> None:
        source = '| Label | Count | Status |\n| :--- | ---: | :---: |\n| Station | 1 | Yes |'
        for language in ("en", "de"):
            with self.subTest(language=language):
                rendered = build_site.render_markdown(source, language, {})
                headers = re.findall(r'<th style="text-align: (left|right|center);">', rendered)
                cells = re.findall(r'<td style="text-align: (left|right|center);">', rendered)
                self.assertEqual(headers, ["left", "right", "center"])
                self.assertEqual(cells, headers)
        # Author-selected alignment must survive the shared website styles.
        for filename in ("site.css", "demo-walkthrough.css", "print.css"):
            css = (build_site.SOURCE / "theme" / "styles" / filename).read_text(encoding="utf-8")
            self.assertNotRegex(css, r'text-align\s*:[^;}]*!important')

    def test_inline_and_display_math_keep_mathjax_delimiters_and_tex(self) -> None:
        source = r"Inline $\Delta SNR = 3\,\mathrm{dB}$ and $x < y$." + "\n\n" + r"$$\frac{a_1}{b_2} = \left(1+\epsilon\right)$$"
        rendered = build_site.render_markdown(source, "en", {})
        self.assertIn(r"\(\Delta SNR = 3\,\mathrm{dB}\)", rendered)
        self.assertIn(r"\(x &lt; y\)", rendered)
        self.assertIn(r"\[\frac{a_1}{b_2} = \left(1+\epsilon\right)\]", rendered)
        self.assertEqual(rendered.count('class="math"'), 3)
        self.assertNotIn("<em>", rendered)


class PdfLinkRenderingTests(unittest.TestCase):
    """PDF navigation changes preserve the destination and unrelated HTML."""

    def inventory(self, rendered: str) -> list[dict]:
        inventory = AnchorInventory()
        inventory.feed(rendered)
        return inventory.anchors

    def test_local_external_and_encoded_pdf_paths_open_in_new_tabs(self) -> None:
        destinations = (
            "/assets/figure.pdf", "../reference/report.PDF", "/report.pdf?download=1#page=3",
            "https://example.org/paper.pdf?key=a&mode=view#page=6",
            "//example.org/paper.PdF#page=2", "/assets/paper%2Epdf",
            "/assets/paper.%50%44%46?name=plot#page=4", "/assets/paper%20copy.pdf",
        )
        for href in destinations:
            with self.subTest(href=href):
                source = f'<a href="{escape(href, quote=True)}">Published figure</a>'
                rendered = build_site.open_pdf_links_in_new_tabs(source)
                anchor = self.inventory(rendered)[0]
                self.assertEqual(anchor["attributes"]["href"], href)
                self.assertEqual(anchor["attributes"]["target"], "_blank")
                self.assertEqual(set(anchor["attributes"]["rel"].split()), {"noopener", "noreferrer"})
                self.assertEqual(anchor["text"], "Published figure")

    def test_existing_target_and_rel_are_updated_without_losing_tokens(self) -> None:
        for target, rel in (("_self", "external nofollow"), ("reader", "NoOpener noreferrer"),
                            ("_blank", "ugc noreferrer"), ("_parent", "")):
            with self.subTest(target=target, rel=rel):
                source = f'<a href="/paper.pdf" target="{target}" rel="{rel}">Paper</a>'
                rendered = build_site.open_pdf_links_in_new_tabs(source)
                attrs = self.inventory(rendered)[0]["attributes"]
                self.assertEqual(attrs["target"], "_blank")
                tokens = attrs["rel"].split()
                self.assertEqual(tokens[:len(rel.split())], rel.split())
                lowered = [token.casefold() for token in tokens]
                self.assertEqual(lowered.count("noopener"), 1)
                self.assertEqual(lowered.count("noreferrer"), 1)
                self.assertEqual(len(re.findall(r'\btarget\s*=', rendered, re.I)), 1)
                self.assertEqual(len(re.findall(r'\brel\s*=', rendered, re.I)), 1)

    def test_pdf_href_other_attributes_and_contents_remain_byte_identical(self) -> None:
        source = ("<section>Before &amp; after "
                  "<A class='paper-link' HREF='/report.%50DF?x=1&amp;y=2#page=6' "
                  "title='Angle > 0 &amp; SNR' data-origin=publication download='original.pdf' "
                  "TARGET='_self' REL='external'><strong>Figure 3</strong> ↗</A></section>")
        rendered = build_site.open_pdf_links_in_new_tabs(source)
        before = self.inventory(source)[0]
        after = self.inventory(rendered)[0]
        self.assertEqual(before["text"], after["text"])
        self.assertEqual({k: v for k, v in before["attributes"].items() if k not in {"target", "rel", "download"}},
                         {k: v for k, v in after["attributes"].items() if k not in {"target", "rel"}})
        self.assertNotIn("download", after["attributes"])
        for preserved in ("<section>Before &amp; after ", "class='paper-link'",
                          "HREF='/report.%50DF?x=1&amp;y=2#page=6'",
                          "title='Angle > 0 &amp; SNR'", "data-origin=publication",
                          "><strong>Figure 3</strong> ↗</A></section>"):
            self.assertIn(preserved, rendered)

    def test_non_pdf_links_and_non_anchor_markup_remain_byte_identical(self) -> None:
        source = ("<a href='/guide/?attachment=paper.pdf' target='_self' rel='help'>Guide</a>"
                  "<a href='/paper.pdf/'>Directory</a><a href='#paper.pdf'>Anchor</a>"
                  "<a href='/figure.png#paper.pdf' download='original.png'>Image</a><a id='paper.pdf'>Target</a>"
                  "<a href='https://[bad/paper.pdf'>Malformed URL</a>"
                  "<img src='/figure.pdf' alt='Not a link'>"
                  "<!-- <a href='/comment.pdf'>Comment</a> -->"
                  "<script>const example = '<a href=\"/script.pdf\">Example</a>';</script>")
        self.assertEqual(build_site.open_pdf_links_in_new_tabs(source), source)

    def test_unquoted_attributes_are_supported_without_changing_href(self) -> None:
        source = '<a href=/paper.pdf target=_self rel=external data-id=7>Paper</a>'
        rendered = build_site.open_pdf_links_in_new_tabs(source)
        attrs = self.inventory(rendered)[0]["attributes"]
        self.assertEqual(attrs["href"], "/paper.pdf")
        self.assertEqual(attrs["target"], "_blank")
        self.assertEqual(set(attrs["rel"].split()), {"external", "noopener", "noreferrer"})
        self.assertIn("href=/paper.pdf", rendered)
        self.assertIn("data-id=7", rendered)

    def test_pdf_policy_is_idempotent(self) -> None:
        source = ('<a href="/paper.pdf">Local</a>'
                  '<a href="https://example.org/paper.PDF?download=1#page=3" '
                  'target="_blank" rel="external noopener noreferrer">External</a>')
        rendered = build_site.open_pdf_links_in_new_tabs(source)
        self.assertEqual(build_site.open_pdf_links_in_new_tabs(rendered), rendered)

    def test_pdf_download_attributes_are_removed_in_each_supported_form(self) -> None:
        for download in ("download", 'download="paper.pdf"', "download='paper.pdf'", "DOWNLOAD=paper.pdf"):
            with self.subTest(download=download):
                source = f'<a href="/paper.pdf" {download} class="paper">Paper</a>'
                attrs = self.inventory(build_site.open_pdf_links_in_new_tabs(source))[0]["attributes"]
                self.assertNotIn("download", attrs)
                self.assertEqual(attrs["target"], "_blank")
                self.assertEqual(attrs["href"], "/paper.pdf")
                self.assertEqual(attrs["class"], "paper")


class ImportedBundleTests(TemporarySiteTests):
    """Reject modified payloads and paths outside the imported content boundary."""

    def setUp(self) -> None:
        super().setUp()
        self.directory = self.root / "bundle"
        self.payload = b"Complete manual bytes\n"
        self.write("bundle/manual.en.md", self.payload)
        self.manifest = {
            "schema_version": 1,
            "app_version": "test",
            "source_revision": "a" * 40,
            "source_dirty": False,
            "files": {"manual.en.md": {"bytes": len(self.payload), "sha256": hashlib.sha256(self.payload).hexdigest()}},
        }
        self.save_manifest()

    def save_manifest(self) -> None:
        self.write("bundle/manifest.json", json.dumps(self.manifest))

    def test_valid_bundle_is_read_without_modification(self) -> None:
        before = {path.name: path.read_bytes() for path in self.directory.iterdir()}
        self.assertEqual(build_site.verify_bundle(self.directory), self.manifest)
        self.assertEqual(before, {path.name: path.read_bytes() for path in self.directory.iterdir()})

    def test_changed_payload_is_rejected_even_when_its_size_is_unchanged(self) -> None:
        self.write("bundle/manual.en.md", b"X" * len(self.payload))
        with self.assertRaisesRegex(ValueError, "stale or modified"):
            build_site.verify_bundle(self.directory)

    def test_changed_hash_or_size_is_rejected(self) -> None:
        for field, value in (("sha256", "0" * 64), ("bytes", len(self.payload) + 1)):
            with self.subTest(field=field):
                entry = self.manifest["files"]["manual.en.md"]
                previous = entry[field]
                entry[field] = value
                self.save_manifest()
                with self.assertRaisesRegex(ValueError, "stale or modified"):
                    build_site.verify_bundle(self.directory)
                entry[field] = previous

    def test_undeclared_file_is_rejected(self) -> None:
        self.write("bundle/unreviewed.txt", "Not part of the public bundle")
        with self.assertRaisesRegex(ValueError, "inventory differs"):
            build_site.verify_bundle(self.directory)

    def test_manifest_cannot_read_outside_its_root(self) -> None:
        outside = self.write("outside.md", self.payload)
        for name in ("../outside.md", str(outside), "nested/../../outside.md", "..\\outside.md"):
            with self.subTest(name=name):
                self.manifest["files"] = {name: {"bytes": len(self.payload), "sha256": hashlib.sha256(self.payload).hexdigest()}}
                self.save_manifest()
                with self.assertRaisesRegex(ValueError, "Unsafe manifest path"):
                    build_site.verify_bundle(self.directory)

    def test_noncanonical_manifest_paths_are_rejected(self) -> None:
        for name in ("./manual.en.md", "nested/../manual.en.md", str(self.directory / "manual.en.md")):
            with self.subTest(name=name):
                self.manifest["files"] = {name: {"bytes": len(self.payload), "sha256": hashlib.sha256(self.payload).hexdigest()}}
                self.save_manifest()
                with self.assertRaises(ValueError):
                    build_site.verify_bundle(self.directory)

    def test_boolean_is_not_a_supported_manifest_schema_version(self) -> None:
        self.manifest["schema_version"] = True
        self.save_manifest()
        with self.assertRaises(ValueError):
            build_site.verify_bundle(self.directory)


class LocalLinkValidationTests(TemporarySiteTests):
    """Validate same-page, cross-page, decoded, and resource destinations."""

    def test_valid_fragment_and_crosspage_links_are_accepted(self) -> None:
        self.write("en/index.html", '<main id="main"><a href="#main">Here</a><a href="/de/#ziel">Deutsch</a></main>')
        self.write("de/index.html", '<main id="ziel"><a href="/en/?mode=test#main">English</a></main>')
        self.assertEqual(build_site.validate_site(self.root), 2)

    def test_missing_anchor_is_rejected(self) -> None:
        self.write("index.html", '<main id="main"><a href="#missing">Missing</a></main>')
        with self.assertRaisesRegex(ValueError, "Missing anchor"):
            build_site.validate_site(self.root)

    def test_missing_local_page_is_rejected(self) -> None:
        self.write("index.html", '<a href="/absent/">Absent page</a>')
        with self.assertRaisesRegex(ValueError, "Missing local target"):
            build_site.validate_site(self.root)

    def test_duplicate_ids_and_missing_image_alternatives_are_rejected(self) -> None:
        self.write("index.html", '<p id="same">A</p><p id="same">B</p><img src="/image.png">')
        self.write("image.png", b"placeholder bytes")
        with self.assertRaises(ValueError) as raised:
            build_site.validate_site(self.root)
        self.assertIn("Duplicate HTML IDs", str(raised.exception))
        self.assertIn("Image missing alt", str(raised.exception))

    def test_explicit_empty_alternative_is_valid_for_a_decorative_image(self) -> None:
        self.write("index.html", '<main><img src="/icon.svg" alt="" aria-hidden="true"><h1>Receiving stations</h1></main>')
        self.write("icon.svg", '<svg xmlns="http://www.w3.org/2000/svg"/>')
        self.assertEqual(build_site.validate_site(self.root), 1)

    def test_empty_alternative_requires_the_image_to_be_explicitly_decorative(self) -> None:
        self.write("index.html", '<main><img src="/result.svg" alt=""></main>')
        self.write("result.svg", '<svg xmlns="http://www.w3.org/2000/svg"/>')
        with self.assertRaisesRegex(ValueError, "Image missing alt"):
            build_site.validate_site(self.root)

    def test_percent_encoded_path_escape_is_rejected(self) -> None:
        self.write("index.html", '<a href="/%2e%2e/private.html">Outside</a>')
        with self.assertRaisesRegex(ValueError, "Escaping link"):
            build_site.validate_site(self.root)

    def test_missing_local_stylesheet_is_rejected(self) -> None:
        self.write("index.html", '<link rel="stylesheet" href="/assets/missing.css"><main id="main">Content</main>')
        with self.assertRaisesRegex(ValueError, "Missing local target"):
            build_site.validate_site(self.root)

    def test_missing_responsive_artwork_is_rejected(self) -> None:
        self.write("index.html", '<picture><source media="(max-width:600px)" srcset="/mobile.png"><img src="/desktop.png" alt="Radar artwork"></picture>')
        self.write("desktop.png", b"desktop placeholder")
        with self.assertRaisesRegex(ValueError, "Missing local target.*mobile.png"):
            build_site.validate_site(self.root)


class LandingStylesheetCacheTests(TemporarySiteTests):
    """Keep updated landing markup paired with its current stylesheet bytes."""

    def setUp(self) -> None:
        super().setUp()
        source_site = build_site.SOURCE
        self.source = self.root / "source"
        for relative in (
            "theme/templates/page.html", "config/landing.json", "config/demo_walkthroughs.json",
            "config/demos_index.json",
            "assets/documentation/manifest.json",
            "assets/documentation/WSPRadar_Doc_EN.pdf",
            "assets/documentation/WSPRadar_Doc_DE.pdf",
            "theme/styles/print.css", "theme/scripts/print.js",
        ):
            self.write("source/" + relative, (source_site / relative).read_bytes())
        for page in (source_site / "pages").glob("*.md"):
            self.write("source/pages/" + page.name, page.read_bytes())
        self.stylesheet = self.write("source/theme/styles/landing.css", ".result-crop {color: #111111;}\n")
        site_patch = patch.object(build_site, "SOURCE", self.source)
        site_patch.start()
        self.addCleanup(site_patch.stop)
        landing_patch = patch.object(build_site, "landing_payload", return_value={
            "manifest.json": (source_site / "assets" / "landing" / "manifest.json").read_bytes(),
        })
        landing_patch.start()
        self.addCleanup(landing_patch.stop)

    def stylesheet_urls(self) -> dict[str, str]:
        builder = build_site.SiteBuilder()
        for language in ("en", "de"):
            builder.page(language, "", "Preview", "<p>Preview</p>", "home")
        builder.page("en", "", "Preview", "<p>Preview</p>", "home", root_alias=True)
        urls = {}
        for path, html in builder.pages.items():
            inventory = build_site.LinkInventory()
            inventory.feed(html)
            matching = [href for href in inventory.links
                        if urlsplit(href).path == "/assets/landing.css"]
            self.assertEqual(len(matching), 1, path)
            self.assertTrue(parse_qs(urlsplit(matching[0]).query).get("v", [""])[0], path)
            urls[path] = matching[0]
        self.assertEqual(set(urls), {"en/index.html", "de/index.html", "index.html"})
        self.assertEqual(len(set(urls.values())), 1)
        return urls

    def test_unchanged_css_has_a_stable_url_for_both_languages_and_root(self) -> None:
        before = self.stylesheet_urls()
        self.stylesheet.write_bytes(self.stylesheet.read_bytes())
        self.assertEqual(self.stylesheet_urls(), before)

    def test_changed_css_changes_the_cache_key_on_every_page(self) -> None:
        before = self.stylesheet_urls()
        self.stylesheet.write_bytes(b".result-crop {color: #222222;}\n")
        after = self.stylesheet_urls()
        for path in before:
            with self.subTest(page=path):
                self.assertNotEqual(after[path], before[path])
                self.assertEqual(urlsplit(after[path]).path, "/assets/landing.css")

    def test_versioned_url_resolves_to_the_ordinary_local_stylesheet(self) -> None:
        href = self.stylesheet_urls()["en/index.html"]
        self.write("preview/assets/landing.css", self.stylesheet.read_bytes())
        self.write("preview/index.html", f'<link rel="stylesheet" href="{escape(href, quote=True)}"><main id="main">Preview</main>')
        self.assertEqual(build_site.validate_site(self.root / "preview"), 1)


class GeneratedBilingualInventoryTests(unittest.TestCase):
    """Exercise the real reviewed content without writing to the live preview."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = build_site.SiteBuilder()
        cls.pages = cls.builder.render()

    def test_legacy_logo_keeps_the_published_and_raw_github_bytes(self) -> None:
        canonical = build_site.SOURCE / "assets" / "brand" / "WSPRadar-2x1.png"
        compatibility = build_site.ROOT / "img" / "WSPRadar-2x1.png"
        self.assertEqual(canonical.read_bytes(), compatibility.read_bytes())
        entrypoint = (build_site.ROOT / "index.html").read_text(encoding="utf-8")
        for attribute in ('property="og:image"', 'name="twitter:image"'):
            self.assertIn(
                '<meta ' + attribute + ' content="https://wspradar.org/img/WSPRadar-2x1.png" />',
                entrypoint,
            )

    def test_full_manual_partition_preserves_both_canonical_inputs(self) -> None:
        for language in ("en", "de"):
            with self.subTest(language=language):
                manual = self.builder.manuals[language]
                self.assertEqual("".join(section.text for section in self.builder.sections[language]), manual)
                original_ids = Counter(re.findall(r'<a\s+id="([^"]+)"', manual))
                partition_ids = Counter(anchor for section in self.builder.sections[language] for anchor in section.anchors)
                self.assertEqual(original_ids, partition_ids)

    def test_manual_index_preserves_chapter_links_and_featured_intro_in_part_groups(self) -> None:
        orientation = {
            "en": (
                "Start here: Why WSPRadar?",
                "Did your station change really help—or did conditions change? Explore what WSPR observations can reveal, which questions WSPRadar can answer, and where the limits lie.",
                "Read Why WSPRadar? →",
            ),
            "de": (
                "Einstieg: Warum WSPRadar?",
                "Hat die Änderung an deiner Station wirklich geholfen – oder haben sich die Bedingungen verändert? Erfahre, was WSPR-Beobachtungen zeigen können, welche Fragen WSPRadar beantworten kann und wo die Grenzen liegen.",
                "Lies „Warum WSPRadar?“ →",
            ),
        }
        for language in ("en", "de"):
            with self.subTest(language=language):
                rendered = self.builder.manual_index(language)
                inventory = build_site.LinkInventory()
                inventory.feed(rendered)
                expected = [build_site.chapter_url(language, section.key) for section in self.builder.sections[language]
                            if "documentation-toc" not in section.anchors]
                self.assertEqual(Counter(inventory.links), Counter(expected))
                self.assertNotIn(self.builder.anchors[language]["documentation-toc"], inventory.links)
                self.assertNotIn(build_site.route(language, "documentation/full/"), inventory.links)
                groups = re.findall(r'<section class="manual-group">(.*?)</section>', rendered, re.DOTALL)
                self.assertEqual(len(groups), 5 if language == "en" else 4)
                for index, group in enumerate(groups):
                    self.assertIn("<h3><a ", group)
                    if language == "en" and index == 4:
                        self.assertIn("Part V: References", group)
                        self.assertNotIn("<ul>", group)
                    else:
                        self.assertIn("<ul>", group)
                self.assertNotIn('class="manual-introduction"', rendered)
                self.assertLess(rendered.index('class="manual-start"'), rendered.index('class="manual-index"'))
                self.assertGreater(rendered.index('class="manual-supplementary"'), rendered.index('class="manual-index"'))
                references = next(section for section in self.builder.sections[language] if "sec-ref" in section.anchors)
                reference_group = 4 if language == "en" else 2
                self.assertIn(build_site.chapter_url(language, references.key), groups[reference_group])
                self.assertEqual(references.key, "sec-ref")
                if language == "en":
                    self.assertEqual(self.builder.anchors[language]["part-v"], self.builder.anchors[language]["sec-ref"])
                    self.assertIn('id="part-v"', self.pages["en/documentation/sec-ref/index.html"])
                self.assertNotIn("sec-disclaimer", "".join(groups))
                self.assertNotIn(self.builder.anchors[language]["sec-1"], "".join(groups))
                documentation = re.search(r'<main id="main">(.*?)</main>', self.pages[f"{language}/documentation/index.html"], re.DOTALL)[1]
                featured = re.findall(r'<section class="manual-start"[^>]*>(.*?)</section>', documentation, re.DOTALL)
                self.assertEqual(len(featured), 1)
                title, description, action = orientation[language]
                self.assertEqual(documentation.count(f'<h2 id="manual-start-title">{title}</h2>'), 1)
                self.assertIn(description, featured[0])
                feature_links = AnchorInventory()
                feature_links.feed(featured[0])
                self.assertEqual([(link["attributes"]["href"], link["text"]) for link in feature_links.anchors],
                                 [(self.builder.anchors[language]["sec-1"], action)])
                self.assertNotIn('class="manual-introduction"', documentation)
                feature_end = documentation.index('</section>', documentation.index('class="manual-start"')) + len('</section>')
                self.assertTrue(documentation[feature_end:].lstrip().startswith('<div class="manual-index">'))
                self.assertEqual(re.findall(r'<section class="manual-group">(.*?)</section>', documentation, re.DOTALL), groups)
                documentation_links = build_site.LinkInventory()
                documentation_links.feed(documentation)
                self.assertEqual(Counter(documentation_links.links), Counter(
                    [link for link in expected if link != self.builder.anchors[language]["sec-disclaimer"]]
                    + [f"/assets/documentation/WSPRadar_Doc_{language.upper()}.pdf?v={self.builder.documentation_pdf_versions[language]}"]))

    def test_documentation_pdf_action_uses_local_language_and_loads_only_on_request(self) -> None:
        for language in ("en", "de"):
            page = self.pages[f"{language}/documentation/index.html"]
            inventory = AnchorInventory()
            inventory.feed(page)
            href = f"/assets/documentation/WSPRadar_Doc_{language.upper()}.pdf?v={self.builder.documentation_pdf_versions[language]}"
            actions = [link for link in inventory.anchors if link["attributes"]["href"] == href]
            self.assertEqual(len(actions), 1)
            attributes = actions[0]["attributes"]
            self.assertIn("button", attributes["class"].split())
            self.assertEqual(attributes["target"], "_blank")
            self.assertEqual(set(attributes["rel"].split()), {"noopener", "noreferrer"})
            self.assertNotIn("download", attributes)
            # The PDF appears only in its anchor, never in a preload, iframe or script.
            self.assertEqual(page.count(href), 1)

    def test_numbered_manual_links_retain_complete_accessible_titles(self) -> None:
        for language in ("en", "de"):
            rendered = self.builder.manual_index(language)
            numbered = [section for section in self.builder.sections[language]
                        if re.match(r'(?:(?:Appendix|Anhang) )?([1-9][0-9]*|[A-Z])[.:] ', section.title)]
            for section in numbered:
                with self.subTest(language=language, chapter=section.key):
                    self.assertIn('aria-label="' + escape(section.title, quote=True) + '" href="' + build_site.chapter_url(language, section.key) + '">', rendered)

    def test_every_generated_pdf_anchor_opens_in_a_new_tab(self) -> None:
        pdf_anchors = []
        for path, content in self.pages.items():
            inventory = AnchorInventory()
            inventory.feed(content)
            for anchor in inventory.anchors:
                attrs = anchor["attributes"]
                href = attrs.get("href", "")
                if not unquote(urlsplit(href).path).casefold().endswith(".pdf"):
                    continue
                pdf_anchors.append((path, href))
                with self.subTest(page=path, href=href):
                    self.assertEqual(attrs.get("target"), "_blank")
                    self.assertNotIn("download", attrs)
                    self.assertTrue({"noopener", "noreferrer"}.issubset(
                        {token.casefold() for token in attrs.get("rel", "").split()}))
        self.assertTrue(any(path.startswith("en/") for path, _ in pdf_anchors))
        self.assertTrue(any(path.startswith("de/") for path, _ in pdf_anchors))
        self.assertTrue(any(urlsplit(href).scheme == "https" for _, href in pdf_anchors))

    def test_reference_pdf_routes_cover_all_canonical_demo_links_without_app_hosting(self) -> None:
        expected = set()
        for demo in self.builder.demos:
            for description in demo["description"].values():
                for href in re.findall(r"\]\(([^)\s]+)\)", description):
                    destination = urlsplit(href)
                    if (destination.path.startswith("/assets/demos/")
                            and unquote(destination.path).casefold().endswith(".pdf")):
                        expected.add(destination.path)
        published = build_site.demo_supplement_files(build_site.DEMO_SUPPLEMENTS)
        published_routes = {"/" + name for name in published}
        retained_legacy_routes = {
            f"/assets/demos/milazzo_publication_overlays_v2/WSPRadar_Demo_Milazzo_Figure{number}.pdf"
            for number in (6, 7)
        }
        self.assertTrue(expected)
        self.assertEqual(published_routes, expected | retained_legacy_routes)
        rendered_references = set()
        for path, content in self.pages.items():
            inventory = AnchorInventory()
            inventory.feed(content)
            for anchor in inventory.anchors:
                href = anchor["attributes"].get("href", "")
                destination = urlsplit(href)
                if destination.netloc in {"", "wspradar.org"}:
                    self.assertFalse(destination.path.startswith("/static/"), (path, href))
                if urlsplit(href).path not in published_routes:
                    continue
                with self.subTest(page=path, href=href):
                    destination = urlsplit(href)
                    self.assertTrue(destination.path.startswith("/assets/demos/"))
                    self.assertIn(destination.netloc, {"", "wspradar.org"})
                    self.assertIn(destination.path, published_routes)
                    self.assertEqual(anchor["attributes"].get("target"), "_blank")
                    rendered_references.add(destination.path)
        self.assertTrue(rendered_references)

    def test_complete_page_applies_pdf_policy_to_markdown_and_direct_html(self) -> None:
        builder = build_site.SiteBuilder()
        markdown_link = builder.md('[Paper](/assets/paper.pdf?view=1#page=6)', "en")
        body = markdown_link + '<a href="https://example.org/figure.PDF">Figure</a>'
        builder.page("en", "pdf-policy/", "PDF links", body, "docs")
        inventory = AnchorInventory()
        inventory.feed(builder.pages["en/pdf-policy/index.html"])
        links = [a for a in inventory.anchors if a["text"] in {"Paper", "Figure"}]
        self.assertEqual(len(links), 2)
        for anchor in links:
            self.assertEqual(anchor["attributes"]["target"], "_blank")
            self.assertTrue({"noopener", "noreferrer"}.issubset(anchor["attributes"]["rel"].split()))

    def test_generated_analysis_launches_keep_guided_demos_open(self) -> None:
        launches = 0
        guided_launches = 0
        for path, content in self.pages.items():
            inventory = AnchorInventory()
            inventory.feed(content)
            for anchor in inventory.anchors:
                attributes = anchor["attributes"]
                destination = urlsplit(attributes.get("href", ""))
                direct_analysis = destination.netloc == "wspradar.streamlit.app" and destination.path in {"", "/"}
                canonical_launch = (destination.netloc == "wspradar.org" and destination.path in {"", "/"}
                                    and (destination.query or destination.fragment == "wspradar-results-inspection"))
                if direct_analysis or canonical_launch:
                    launches += 1
                    with self.subTest(page=path, destination=destination.geturl()):
                        guided_demo = re.fullmatch(r"(?:en|de)/demos/[^/]+/index.html", path)
                        prepared_demo = destination.query or destination.fragment == "wspradar-results-inspection"
                        if guided_demo and prepared_demo:
                            guided_launches += 1
                            self.assertEqual(attributes.get("target"), "_blank")
                            self.assertTrue({"noopener", "noreferrer"}.issubset(attributes.get("rel", "").split()))
                            if {"button", "text-link"} & set(attributes.get("class", "").split()):
                                self.assertTrue(anchor["text"].endswith(" ↗"))
                        else:
                            self.assertNotIn("target", attributes)
        self.assertGreater(launches, len(self.pages))
        self.assertGreaterEqual(guided_launches, 2 * len(self.builder.published_demos))

    def test_documentation_entries_outside_main_navigation_and_reader_open_in_a_new_tab(self) -> None:
        entries = 0
        for path, content in self.pages.items():
            if "/documentation/" in path:
                continue
            inventory = AnchorInventory()
            inventory.feed(content)
            for anchor in inventory.anchors:
                attributes = anchor["attributes"]
                destination = urlsplit(attributes.get("href", ""))
                if destination.netloc not in {"", "wspradar.org"} or not re.match(r"^/(?:en|de)/documentation/", destination.path):
                    continue
                if attributes.get("data-product-nav") == "documentation":
                    self.assertNotIn("target", attributes)
                    continue
                entries += 1
                with self.subTest(page=path, destination=destination.geturl()):
                    self.assertEqual(attributes.get("target"), "_blank")
                    self.assertTrue({"noopener", "noreferrer"}.issubset(attributes.get("rel", "").split()))
        self.assertGreater(entries, 20)

    def test_every_page_has_a_language_counterpart(self) -> None:
        for path in self.pages:
            if path == "index.html":
                continue
            language, suffix = path.split("/", 1)
            other = "de" if language == "en" else "en"
            with self.subTest(path=path):
                self.assertIn(f"{other}/{suffix}", self.pages)
                self.assertIn(f'<html lang="{language}">', self.pages[path])

    def test_every_route_preserves_canonical_alternates_and_keyboard_language_navigation(self) -> None:
        for path, content in self.pages.items():
            language = "en" if path == "index.html" else path.split("/", 1)[0]
            suffix = "" if path == "index.html" else path.split("/", 1)[1].removesuffix("index.html")
            other = "de" if language == "en" else "en"
            with self.subTest(path=path):
                self.assertIn(f'<link rel="canonical" href="{build_site.SITE_URL}/{language}/{suffix}">', content)
                for alternate in ("en", "de"):
                    self.assertIn(f'<link rel="alternate" hreflang="{alternate}" href="{build_site.SITE_URL}/{alternate}/{suffix}">', content)
                inventory = AnchorInventory()
                inventory.feed(content)
                switches = [anchor for anchor in inventory.anchors if anchor["attributes"].get("class") == "language-option"]
                self.assertEqual(len(switches), 1)
                for alternate, switch in zip(("en",), switches):
                    self.assertEqual(switch["attributes"]["href"], f"/{alternate}/{suffix}")
                    self.assertEqual(switch["attributes"]["hreflang"], alternate)
                    self.assertEqual(switch["attributes"]["lang"], alternate)
                    self.assertEqual(switch["text"].strip(), build_site.LANGUAGE_NAMES[alternate])
                    self.assertEqual(switch["attributes"].get("aria-current"), "true" if alternate == language else None)
                    self.assertNotEqual(switch["attributes"].get("tabindex"), "-1")
                selector = re.search(r'<details class="language-selector">(.*?)</details>', content, re.DOTALL)
                self.assertIsNotNone(selector)
                label = build_site.COPY[language]["change_language"]
                self.assertIn(f'<summary aria-label="{label}: {build_site.LANGUAGE_NAMES[language]}" title="{label}">', selector[1])
                self.assertIn(f'<span class="language-current" lang="{language}">{language.upper()}</span>', selector[1])
                self.assertIn('class="language-globe"', selector[1])
                self.assertIn('aria-hidden="true" focusable="false"', selector[1])
                self.assertNotIn('class="language-flag"', selector[1])
                self.assertNotIn('class="language-label"', selector[1])
                self.assertIn('class="skip-link" href="#main"', content)

    def test_open_graph_metadata_matches_each_canonical_page(self) -> None:
        class MetadataInventory(HTMLParser):
            def __init__(self) -> None:
                super().__init__()
                self.metadata = {}
                self.canonical = None

            def handle_starttag(self, tag, attributes) -> None:
                attrs = dict(attributes)
                if tag == "meta":
                    self.metadata[attrs.get("property", attrs.get("name"))] = attrs.get("content")
                elif tag == "link" and attrs.get("rel") == "canonical":
                    self.canonical = attrs.get("href")

        for path, content in self.pages.items():
            with self.subTest(path=path):
                inventory = MetadataInventory()
                inventory.feed(content)
                self.assertEqual(inventory.metadata.get("og:url"), inventory.canonical)
                self.assertEqual(inventory.metadata.get("og:type"), "website")
                self.assertEqual(inventory.metadata.get("og:description"), inventory.metadata.get("description"))
                self.assertEqual(inventory.metadata.get("og:image"), build_site.SITE_URL + "/assets/landing/web/hero-1280.png")
                self.assertTrue(inventory.metadata.get("og:title"))

    def test_all_demo_and_manual_routes_are_generated(self) -> None:
        for language in ("en", "de"):
            expected = {f"{language}/{suffix}index.html" for suffix in ("", "documentation/", "documentation/full/", "demos/", "guides/read-results/", "community/", "report/")}
            expected.update(f"{language}/documentation/{section.key}/index.html" for section in self.builder.sections[language])
            expected.update(f"{language}/demos/{demo['id']}/index.html" for demo in self.builder.published_demos)
            self.assertEqual({path for path in self.pages if path.startswith(language + "/")}, expected)

    def test_every_page_navigation_follows_the_station_workflow(self) -> None:
        labels = {
            "en": ["Introduction", "Guided Demos", "WSPRadar App", "Documentation", "Community"],
            "de": ["Einführung", "Geführte Demo", "WSPRadar App", "Dokumentation", "Community"],
        }
        for path, content in self.pages.items():
            language = "en" if path == "index.html" else path.split("/", 1)[0]
            with self.subTest(path=path):
                navigation = re.search(r'<div class="nav-links" id="nav-links">(.*?)</div>', content, re.DOTALL)
                self.assertIsNotNone(navigation)
                self.assertIn('<button class="nav-toggle" aria-controls="nav-links" aria-expanded="true">', content)
                inventory = AnchorInventory()
                inventory.feed(navigation[1])
                self.assertEqual([anchor["attributes"]["href"] for anchor in inventory.anchors],
                                 [f"/{language}/", f"/{language}/demos/", build_site.APP_URL,
                                  f"/{language}/documentation/", f"/{language}/community/"])
                self.assertEqual([anchor["text"] for anchor in inventory.anchors], labels[language])
                self.assertEqual(navigation[1].count('<span class="nav-separator" aria-hidden="true">·</span>'), 5)
                self.assertEqual([anchor["attributes"]["data-product-nav"] for anchor in inventory.anchors],
                                 ["overview", "demos", "analysis", "documentation", "community"])
                for anchor in inventory.anchors:
                    self.assertNotIn("target", anchor["attributes"])
        for language, page_label in (("en", "Guided Demo"), ("de", "Geführte Demo")):
            with self.subTest(preserved_demo_page_language=language):
                content = self.pages[f"{language}/demos/index.html"]
                eyebrow = "GUIDED DEMOS" if language == "en" else page_label
                self.assertIn(f'<p class="eyebrow">{eyebrow}</p>', content)
                self.assertIn(f'<title>{page_label} · WSPRadar</title>', content)

    def test_every_route_has_responsive_english_artwork_and_live_navigation(self) -> None:
        landing = build_site.load_catalog(build_site.SOURCE / "config" / "landing.json", build_site.SOURCE / "pages")
        assets = json.loads((build_site.SOURCE / "assets/landing/manifest.json").read_text(encoding="utf-8"))
        hero = assets["hero"]["fallback"]
        logo = assets["logo"]["fallback"]
        for path, content in self.pages.items():
            language = "en" if path == "index.html" else path.split("/", 1)[0]
            with self.subTest(path=path):
                header = re.search(r'<header\b[^>]*class="[^"]*\bsite-header\b[^"]*"[^>]*>(.*?)</header>', content, re.DOTALL)
                self.assertIsNotNone(header)
                navigation = re.search(r'<div class="site-navigation-shell landing-header">(.*?)</nav></div>', content, re.DOTALL)
                self.assertIsNotNone(navigation)
                self.assertLess(navigation.end(), header.start() + 1)
                self.assertNotIn('radar-artwork', navigation[1])
                self.assertNotIn('<nav', header[1])
                header_content = navigation[1] + '</nav>' + header[1]
                inventory = build_site.LinkInventory()
                inventory.feed(header_content)
                self.assertIn("/assets/landing/" + hero["path"], inventory.links)
                self.assertNotIn("/assets/landing/" + logo["path"], inventory.links)
                self.assertEqual([image["alt"] for image in inventory.images
                                  if image["src"] == "/assets/landing/" + hero["path"]], [landing[language]["hero_alt"]])
                self.assertIn('<picture class="radar-artwork" lang="en">', header_content)
                self.assertIn('class="nav-brand"', header_content)
                self.assertIn('aria-label="WSPRadar.org — ' + build_site.COPY[language]["home"] + '"', header_content)
                self.assertIn('<span>WSPRadar.org</span>', header_content)
                self.assertNotIn(self.builder.brand["credit_html"][language], header_content)
                self.assertEqual(len(inventory.images), 1)
                self.assertLess(header_content.index('<nav class="navigation"'), header_content.index('<picture class="radar-artwork"'))
                links = AnchorInventory()
                links.feed(header_content)
                is_home = path in ("index.html", "en/index.html", "de/index.html")
                demo_route = re.fullmatch(r"(?:en|de)/demos/([^/]+)/index.html", path)
                if demo_route:
                    expected_url = build_site.demo_launch_url(self.builder.demo_by_id[demo_route[1]])
                    launch_links = [anchor for anchor in links.anchors
                                    if anchor["attributes"]["href"] == expected_url]
                    self.assertEqual(launch_links, [])
                    self.assertNotIn('class="launch"', header_content)
                else:
                    self.assertEqual(sum(anchor["attributes"]["href"] == build_site.APP_URL for anchor in links.anchors), 2 if is_home else 1)

    def test_header_serves_responsive_webp_candidates_and_preserves_english_image_on_mobile(self) -> None:
        class PictureInventory(HTMLParser):
            def __init__(self) -> None:
                super().__init__()
                self.sources = []
                self.images = []

            def handle_starttag(self, tag, attributes) -> None:
                if tag == "source":
                    self.sources.append(dict(attributes))
                elif tag == "img":
                    self.images.append(dict(attributes))

        assets = json.loads((build_site.SOURCE / "assets/landing/manifest.json").read_text(encoding="utf-8"))
        hero = assets["hero"]
        fallback = hero["fallback"]
        rendered_pictures = []
        for language in ("en", "de"):
            with self.subTest(language=language):
                inventory = PictureInventory()
                header = self.builder.header(language, "home", "")
                picture = re.search(r'<picture class="radar-artwork" lang="en">(.*?)</picture>', header, re.DOTALL)[1]
                inventory.feed(picture)
                self.assertEqual([source["type"] for source in inventory.sources], ["image/webp"])
                expected = sorted(hero["images"], key=lambda image: image["width"])
                self.assertEqual(inventory.sources[0]["srcset"].split(", "), [f'/assets/landing/{image["path"]} {image["width"]}w' for image in expected])
                self.assertEqual(inventory.sources[0]["sizes"], build_site.HEADER_IMAGE_SIZES)
                self.assertNotIn("media", inventory.sources[0])
                self.assertEqual(len(inventory.images), 1)
                self.assertEqual(inventory.images[0]["src"], "/assets/landing/" + fallback["path"])
                self.assertEqual((inventory.images[0]["width"], inventory.images[0]["height"]), (str(fallback["width"]), str(fallback["height"])))
                self.assertEqual(inventory.images[0]["fetchpriority"], "high")
                self.assertNotEqual(inventory.images[0].get("loading"), "lazy")
                self.assertEqual(inventory.images[0]["lang"], language)
                rendered_pictures.append((inventory.sources, {key: value for key, value in inventory.images[0].items() if key not in ("alt", "lang")}))
        self.assertEqual(rendered_pictures[0], rendered_pictures[1])

    def test_compact_footer_uses_current_imported_version_once_and_preserves_developer_credit(self) -> None:
        for language in ("en", "de"):
            with self.subTest(language=language), patch.dict(self.builder.brand["credit_html"], {language: "Release v2.3 test | Designed by Dr. Markus Brosch (DL1MKS), coded with OpenAI Codex"}), patch.dict(self.builder.brand, {"app_version": "v2.3 test"}):
                self.builder.page(language, "credit-contract/", "Credit contract", "<h1>Credit contract</h1>", "docs")
                content = self.builder.pages.pop(f"{language}/credit-contract/index.html")
                footer = re.search(r'<footer\b[^>]*>(.*?)</footer>', content, re.DOTALL)[1]
                header = re.search(r'<header\b[^>]*>(.*?)</header>', content, re.DOTALL)[1]
                self.assertIn("Designed by Dr. Markus Brosch (DL1MKS), coded with OpenAI Codex", footer)
                self.assertEqual(footer.count("v2.3 test"), 1)
                self.assertNotIn("Release v2.3 test", header)
                self.assertNotIn("v1.0 RC2", footer)

    def test_compact_footer_preserves_unrecognized_imported_credit_without_guessing(self) -> None:
        custom_credit = "Project contributor credit | Maintainer <a href='https://example.org/author'>Author</a>"
        for language in ("en", "de"):
            with self.subTest(language=language), patch.dict(self.builder.brand["credit_html"], {language: custom_credit}):
                self.builder.page(language, "credit-contract/", "Credit contract", "<h1>Credit contract</h1>", "docs")
                content = self.builder.pages.pop(f"{language}/credit-contract/index.html")
                footer = re.search(r'<footer\b[^>]*>(.*?)</footer>', content, re.DOTALL)[1]
                self.assertIn(custom_credit, footer)

    def test_every_footer_keeps_release_developer_and_disclaimer_without_support_links(self) -> None:
        for path, content in self.pages.items():
            language = "en" if path == "index.html" else path.split("/", 1)[0]
            with self.subTest(path=path):
                footer = re.search(r'<footer\b[^>]*>(.*?)</footer>', content, re.DOTALL)[1]
                inventory = AnchorInventory()
                inventory.feed(footer)
                hrefs = [anchor["attributes"]["href"] for anchor in inventory.anchors]
                developer_credit = self.builder.brand["credit_html"][language].split(" | ", 1)[1]
                self.assertIn(developer_credit.strip(), footer)
                self.assertEqual(footer.count(self.builder.brand["app_version"]), 1)
                self.assertIn(f'/{language}/documentation/full/#sec-disclaimer', hrefs)
                self.assertNotIn(f'/{language}/report/', hrefs)
                self.assertNotIn("https://github.com/markusthemaker/WSPRadar", hrefs)
                self.assertEqual(len(hrefs), 2)
                self.assertIn("https://www.qrz.com/db/DL1MKS", hrefs)
                self.assertIn('class="footer-main"', footer)
                self.assertIn('class="footer-legal"', footer)
                self.assertTrue(any("DL1MKS" in anchor["text"] for anchor in inventory.anchors))

    def test_introductory_manual_chapter_marks_documentation_current(self) -> None:
        for language, label in (("en", "Documentation"), ("de", "Dokumentation")):
            content = self.pages[f"{language}/documentation/sec-1/index.html"]
            if language == "en":
                for anchor in ("part-0", "sec-1", "sec-1-1", "sec-1-0", "sec-1-2", "sec-1-3", "sec-1-4"):
                    self.assertEqual(self.builder.anchors[language][anchor], "/en/documentation/sec-1/")
                    self.assertIn(f'id="{anchor}"', content)
                self.assertIn("<h1>Part 0: Why WSPRadar</h1>", content)
                for title in ("0.1 WSPR in 2 Minutes", "0.2 What WSPRadar can show",
                              "0.3 What one run produces", "0.4 Your first useful run"):
                    self.assertIn(f"<h3>{title}</h3>", content)
            navigation = re.search(r'<div class="nav-links" id="nav-links">(.*?)</div>', content, re.DOTALL)
            inventory = AnchorInventory()
            inventory.feed(navigation[1])
            active = [anchor for anchor in inventory.anchors if anchor["attributes"].get("aria-current") == "page"]
            with self.subTest(language=language):
                self.assertEqual(len(active), 1)
                self.assertEqual(active[0]["text"], label)
                self.assertEqual(active[0]["attributes"]["href"], build_site.route(language, "documentation/"))

    def test_overview_keeps_only_the_footer_disclaimer_without_removing_manual_content(self) -> None:
        for language in ("en", "de"):
            paths = [f"{language}/index.html"] + (["index.html"] if language == "en" else [])
            disclaimer_chapter = self.builder.anchors[language]["sec-disclaimer"]
            documentation = self.pages[f"{language}/documentation/index.html"]
            manual_groups = re.findall(r'<section class="manual-group">(.*?)</section>', documentation, re.DOTALL)
            self.assertEqual(len(manual_groups), 5 if language == "en" else 4)
            self.assertNotIn('class="manual-introduction"', documentation)
            for path in paths:
                content = self.pages[path]
                main = re.search(r'<main id="main">(.*?)</main>', content, re.DOTALL)[1]
                footer = re.search(r'<footer\b[^>]*>(.*?)</footer>', content, re.DOTALL)[1]
                with self.subTest(path=path):
                    self.assertNotIn(disclaimer_chapter, main)
                    self.assertNotIn('class="manual-introduction"', main)
                    self.assertNotIn('class="manual-start"', main)
                    self.assertNotIn('class="manual-supplementary"', main)
                    expected_groups = [build_site.apply_product_navigation_link_policy(
                        group, self.builder.navigation,
                    ) for group in manual_groups]
                    self.assertEqual(re.findall(r'<section class="manual-group">(.*?)</section>', main, re.DOTALL), expected_groups)
                    self.assertIn(f'/{language}/documentation/full/#sec-disclaimer', footer)
                    self.assertEqual(footer.count('#sec-disclaimer'), 1)
            documentation_main = re.search(r'<main id="main">(.*?)</main>', documentation, re.DOTALL)[1]
            documentation_footer = re.search(r'<footer\b[^>]*>(.*?)</footer>', documentation, re.DOTALL)[1]
            self.assertNotIn(disclaimer_chapter, documentation_main)
            self.assertNotIn('class="manual-supplementary"', documentation_main)
            self.assertIn(f'/{language}/documentation/full/#sec-disclaimer', documentation_footer)
            self.assertEqual(documentation_footer.count('#sec-disclaimer'), 1)
            self.assertIn('id="sec-disclaimer"', self.pages[disclaimer_chapter.lstrip('/') + "index.html"])
            self.assertIn('id="sec-disclaimer"', self.pages[f"{language}/documentation/full/index.html"])

    def test_overview_explains_literature_demos_and_omits_redundant_labels(self) -> None:
        former_labels = {
            "en": ("Seven demos · Seven detailed walkthroughs", "From the first run to the scientific methods"),
            "de": ("Sieben Demos · Sieben ausführliche Anleitungen", "Vom ersten Lauf bis zu den wissenschaftlichen Methoden"),
        }
        for language in ("en", "de"):
            content = self.pages[f"{language}/index.html"]
            feature = re.search(r'<section class="feature">(.*?)</section>', content, re.DOTALL)[1]
            with self.subTest(language=language):
                self.assertNotIn('class="eyebrow"', feature)
                for label in former_labels[language]:
                    self.assertNotIn(label, content)
                self.assertIn(build_site.COPY[language]["demo_context"], feature)
                self.assertIn(build_site.COPY[language]["demo_summary"], feature)
                self.assertIn(f'/{language}/demos/', feature)

    def test_landing_retains_previous_overview_copy_and_destinations_in_optional_guidance(self) -> None:
        previous_copy_keys = (
            "eyebrow", "hero", "intro", "start", "open",
            "choose_title", "choose_body", "choose_link",
            "experiment_title", "experiment_body", "experiment_link",
            "run_title", "run_body", "demo_feature", "demo_context", "demo_summary",
            "browse_demos", "all_docs", "connect", "connect_body", "community",
            "improve", "improve_body", "bug",
        )
        for language in ("en", "de"):
            with self.subTest(language=language):
                content = self.pages[f"{language}/index.html"]
                guidance = re.search(r'<details\b[^>]*\bid="more-guidance"[^>]*>(.*?)</details>', content, re.DOTALL)
                self.assertIsNotNone(guidance)
                self.assertIn("<summary", guidance[1])
                for key in previous_copy_keys:
                    self.assertIn(build_site.COPY[language][key], unescape(guidance[1]), key)
                self.assertEqual(guidance[1].count('class="journey-card"'), 3)
                self.assertEqual(guidance[1].count('class="manual-group"'), 5 if language == "en" else 4)
                inventory = build_site.LinkInventory()
                inventory.feed(guidance[1])
                for destination in (
                    f"/{language}/demos/", f"/{language}/community/", f"/{language}/report/",
                    self.builder.anchors[language]["sec-2-2"] + "#sec-2-2",
                    self.builder.anchors[language]["sec-2-1"] + "#sec-2-1", build_site.APP_URL,
                ):
                    self.assertIn(destination, inventory.links)
                self.assertNotIn("<h1", guidance[1])

    def test_landing_presents_demo_first_with_four_analysis_choices_before_explanation(self) -> None:
        for language in ("en", "de"):
            with self.subTest(language=language):
                middle = ("analysis-choices", "why-wspradar") if language == "en" else ("why-wspradar", "analysis-choices")
                section_ids = ("how-it-works", *middle, "real-example", "get-started", "more-guidance")
                content = self.pages[f"{language}/index.html"]
                main = re.search(r'<main id="main">(.*?)</main>', content, re.DOTALL)[1]
                self.assertEqual(len(re.findall(r'<h1\b', content)), 1)
                positions = [main.index(f'id="{section_id}"') for section_id in section_ids]
                self.assertEqual(positions, sorted(positions))
                analysis = re.search(r'<section id="analysis-choices"[^>]*>(.*?)</section>', main, re.DOTALL)[1]
                cards = re.findall(r'<article\b[^>]*class="analysis-card"[^>]*>(.*?)</article>', analysis, re.DOTALL)
                self.assertEqual(len(cards), 4)
                self.assertEqual(
                    [unescape(re.search(r'<h[34]\b[^>]*>(.*?)</h[34]>', card, re.DOTALL)[1]) for card in cards],
                    ["RX Benchmark", "TX Benchmark", "RX Performance", "TX Performance"],
                )
                for card in cards:
                    self.assertIn("<p", card)
                    self.assertNotIn("<a ", card)
                get_started = main[positions[4]:positions[5]]
                route_links = AnchorInventory()
                route_links.feed(get_started)
                hrefs = [anchor["attributes"]["href"] for anchor in route_links.anchors]
                self.assertTrue(any(href.startswith(f"/{language}/demos/") for href in hrefs))
                self.assertIn(build_site.APP_URL, hrefs)

    def test_landing_hero_contains_the_primary_actions_only_on_home_routes(self) -> None:
        for path, content in self.pages.items():
            language = "en" if path == "index.html" else path.split("/", 1)[0]
            is_home = path in ("index.html", "en/index.html", "de/index.html")
            header = re.search(r'<header\b[^>]*>(.*?)</header>', content, re.DOTALL)[1]
            main = re.search(r'<main id="main">(.*?)</main>', content, re.DOTALL)[1]
            with self.subTest(path=path):
                actions = re.search(r'<div class="hero-actions"[^>]*>(.*?)</div>', header, re.DOTALL)
                if not is_home:
                    self.assertIsNone(actions)
                    self.assertNotIn('class="hero-entry"', header)
                    continue
                self.assertIsNotNone(actions)
                artwork_stage = re.search(r'<div class="hero-artwork-stage hero-artwork-with-actions">(.*?)</div></div>', header, re.DOTALL)
                self.assertIsNotNone(artwork_stage)
                self.assertIn('<picture class="radar-artwork"', artwork_stage[1])
                self.assertIn(actions[0], artwork_stage[0])
                self.assertIn('class="hero-entry"', header)
                self.assertIn('id="landing-title"', header)
                self.assertNotIn('class="hero-entry"', main)
                self.assertNotIn('class="landing-actions"', main)
                self.assertIn(escape(self.builder.landing[language]["headline"]), header)
                self.assertIn(escape(self.builder.landing[language]["no_station"]), header)
                if "hero_analysis_intro" in self.builder.landing[language]:
                    self.assertIn(self.builder.landing[language]["hero_analysis_intro"], header)
                    self.assertNotIn(self.builder.landing[language]["hero_analysis_intro"], main)
                    self.assertRegex(self.builder.landing[language]["hero_analysis_intro"],
                                     r"<br\s*/?>\s*<strong>Performance</strong>")
                inventory = AnchorInventory()
                inventory.feed(actions[1])
                self.assertEqual([anchor["attributes"]["href"] for anchor in inventory.anchors],
                                 [f"/{language}/demos/", build_site.APP_URL])
                self.assertEqual([anchor["text"] for anchor in inventory.anchors],
                                 [self.builder.landing[language]["try_demo"] + " →", build_site.COPY[language]["start_analysis"] + " →"])

    def test_get_started_has_three_numbered_steps_and_keeps_two_distinct_routes(self) -> None:
        for language in ("en", "de"):
            with self.subTest(language=language):
                content = self.pages[f"{language}/index.html"]
                panel = re.search(r'<section class="get-started-section" id="get-started">(.*?)</section>', content, re.DOTALL)[1]
                copy = self.builder.landing[language]
                self.assertIn(escape(copy["get_started"]), panel)
                self.assertIn('class="start-heading"', panel)
                self.assertIn('class="curiosity-callout"', panel)
                self.assertIn(escape(copy["curiosity_context"]), panel)
                for line in copy["curiosity_lines"]:
                    self.assertIn(escape(line), panel)
                steps = re.findall(r'<li class="start-step">(.*?)</li>', panel, re.DOTALL)
                self.assertEqual(len(steps), 3)
                self.assertEqual(len(copy["start_steps"]), 3)
                for number, (step, configured) in enumerate(zip(steps, copy["start_steps"]), 1):
                    self.assertRegex(step, r'<span class="start-number"[^>]*>' + str(number) + r'</span>')
                    self.assertIn(escape(configured["title"]), step)
                    self.assertIn(escape(configured["body"]), step)
                routes = re.search(r'<div class="start-grid">(.*?)</div>', panel, re.DOTALL)[1]
                cards = re.findall(r'<article>(.*?)</article>', routes, re.DOTALL)
                self.assertEqual(len(cards), 2)
                for card, prefix, destination in zip(cards, ("demo", "own"), (f"/{language}/demos/", build_site.APP_URL)):
                    self.assertIn(escape(copy[prefix + "_title"]), card)
                    self.assertIn(escape(copy[prefix + "_body"]), card)
                    inventory = AnchorInventory()
                    inventory.feed(card)
                    self.assertEqual([anchor["attributes"]["href"] for anchor in inventory.anchors], [destination])

    def test_how_it_works_includes_receiver_and_distinguishes_radio_from_uploaded_data(self) -> None:
        for language in ("en", "de"):
            with self.subTest(language=language):
                content = self.pages[f"{language}/index.html"]
                start = content.index('id="how-it-works"')
                end = content.index('id="analysis-choices"' if language == "en" else 'id="why-wspradar"')
                flow = content[start:end]
                self.assertIn('class="what-copy"', flow)
                self.assertIn('class="how-visual"', flow)
                self.assertEqual(len(re.findall(r'class="flow-step"', flow)), 4)
                inventory = build_site.LinkInventory()
                inventory.feed(flow)
                filenames = [Path(image["src"]).name for image in inventory.images]
                self.assertEqual(filenames, ["tx-station.svg", "rx-station.svg", "wspr-database.svg", "analysis-laptop.svg"])
                self.assertRegex(flow, r'(?i)radio signals' if language == "en" else r'(?i)funksignale')
                self.assertRegex(flow, r'(?i)uploaded spots' if language == "en" else r'(?i)hochgeladene spots')
                self.assertRegex(flow, r'(?i)data over the internet' if language == "en" else r'(?i)daten über das internet')

    def test_why_section_keeps_localized_comparison_and_benchmark_scope_together(self) -> None:
        english = self.builder.landing["en"]["why"]
        german = self.builder.landing["de"]["why"]
        self.assertEqual(set(english) - {"decode_method"}, set(german))
        for removed in ("network_caption", "method_note", "median_legend", "summary_legend", "illustrative_note", "illustrative", "setup_a", "setup_b"):
            self.assertNotIn(removed, english)
            self.assertNotIn(removed, german)
        self.assertEqual(english["repeated_title"], "WSPRadar: Many observations, clear insights")
        self.assertEqual(english["repeated_subtitle"], "Compare your setups through both signal quality and decoding reach.")
        self.assertEqual(english["quick_subtitle"], "One path. One moment. Repeatable?")
        self.assertEqual(english["benefits"][2]["body"], "Less sensitive to outliers")
        self.assertEqual([(item["title"], item["body"]) for item in english["benefits"][:2]],
                         [("100s of stations", "worldwide"), ("1 000s of measurements", "over days or weeks")])
        for collection in ("factors", "benefits", "steps"):
            self.assertEqual(len(english[collection]), len(german[collection]))
            for left, right in zip(english[collection], german[collection]):
                self.assertEqual(set(left), set(right))
                if "icon" in left:
                    self.assertEqual(left["icon"], right["icon"])
        for language in ("en", "de"):
            with self.subTest(language=language):
                page = self.pages[f"{language}/index.html"]
                start = page.index('id="why-wspradar"')
                self.assertLess(page.index('id="how-it-works"'), start)
                if language == "en":
                    self.assertLess(page.index('id="analysis-choices"'), start)
                else:
                    self.assertLess(start, page.index('id="analysis-choices"'))
                section = re.search(r'<section class="why-section"[^>]*>(.*?)</section>', page, re.DOTALL)[0]
                copy = self.builder.landing[language]["why"]
                for key, value in copy.items():
                    if isinstance(value, str) and key not in {"station_label", "delta_label"}:
                        self.assertIn(escape(value), section, key)
                self.assertIn('aria-labelledby="why-title"', section)
                self.assertIn('id="why-title"', section)
                self.assertEqual(section.count('<article class="why-panel '), 2)
                setups = re.findall(r'<div class="why-setup (target|reference)"><h4>(.*?)</h4>.*?<strong>(.*?)</strong>', section)
                self.assertEqual(setups, [("target", copy["target_label"], "−17 dB"), ("reference", copy["reference_label"], "−21 dB")])
                self.assertNotIn('class="why-illustrative"', section)
                step_count = 6 if "decode_method" in copy else 3
                self.assertEqual(section.count('class="why-step-heading"'), step_count)
                self.assertIn("ΔSNR" if language == "en" else "Benchmark", copy["method_title"])
                right_panel = re.search(r'<article class="why-panel why-repeated">(.*?)</article>', section, re.DOTALL)[1]
                self.assertIn('<div class="why-method">', right_panel)
                self.assertEqual(right_panel.count('class="why-step-heading"'), step_count)
                self.assertEqual(section.count('class="why-method"'), 1)
                self.assertIn('<ol class="why-steps" aria-label="' + escape(copy["method_title"]) + '">', right_panel)
                self.assertEqual(right_panel.count('class="why-takeaway"'), 1)
                self.assertEqual(section.count('class="why-takeaway"'), 1)
                self.assertLess(right_panel.index('class="why-steps"'), right_panel.index('class="why-takeaway"'))
                self.assertIn(escape(copy["conclusion_title"]), right_panel)
                self.assertIn(escape(copy["conclusion_body"]), right_panel)
                self.assertNotIn('class="why-diagram-legend"', right_panel)
                self.assertNotIn('class="why-method-note"', right_panel)
                self.assertNotIn('<figcaption>', right_panel)
                for step in copy["steps"]:
                    self.assertIn('<h4>' + escape(step["title"]) + '</h4>', right_panel)
                    self.assertIn(escape(step["body"]), right_panel)
                for benefit in copy["benefits"]:
                    self.assertIn(escape(benefit["title"]), right_panel)
                    self.assertIn(escape(benefit["body"]), right_panel)
                self.assertNotRegex(section, r"(?i)confidence interval|konfidenzintervall")
                for removed_illustration in ("why-pairs", "why-station-medians", "why-dot-row", "why-summary-dots"):
                    self.assertNotIn(removed_illustration, right_panel)

    def test_why_network_uses_responsive_derivatives_and_existing_svg_icons(self) -> None:
        class PictureInventory(build_site.LinkInventory):
            def __init__(self):
                super().__init__()
                self.sources = []

            def handle_starttag(self, tag, attributes):
                super().handle_starttag(tag, attributes)
                if tag == "source":
                    self.sources.append(dict(attributes))

        network = self.builder.landing_assets["network"]
        for language in ("en", "de"):
            with self.subTest(language=language):
                page = self.pages[f"{language}/index.html"]
                section = re.search(r'<section class="why-section"[^>]*>(.*?)</section>', page, re.DOTALL)[0]
                inventory = PictureInventory()
                inventory.feed(section)
                self.assertEqual(len(inventory.sources), 1)
                self.assertEqual(inventory.sources[0]["type"], "image/webp")
                self.assertEqual(inventory.sources[0]["srcset"].split(", "), [f'/assets/landing/{item["path"]} {item["width"]}w' for item in network["images"]])
                fallback = network["fallback"]
                image = next(image for image in inventory.images if image["src"].endswith(fallback["path"]))
                self.assertEqual((image["width"], image["height"]), (str(fallback["width"]), str(fallback["height"])))
                self.assertEqual(image["loading"], "eager")
                self.assertEqual(image["alt"], "")
                icons = {"/assets/landing/" + path for path in self.builder.landing_assets["icons"].values()}
                for image in inventory.images:
                    self.assertIn(image["src"], icons | {"/assets/landing/" + fallback["path"]})

    def test_analysis_families_group_each_mode_once_before_benchmark_guidance(self) -> None:
        page = self.pages["en/index.html"]
        choices = re.search(r'<section id="analysis-choices"[^>]*>(.*?)</section>', page, re.DOTALL)[1]
        families = self.builder.landing["en"]["analysis_families"]
        selections = self.builder.landing["analysis_family_modes"]
        configured_modes = self.builder.landing["en"]["modes"]
        self.assertEqual(sorted(index for key in families for index in selections[key]), list(range(4)))
        self.assertEqual(choices.count('class="analysis-family"'), 2)
        groups = choices.split('<div class="analysis-family">')[1:]
        for (key, family), group in zip(families.items(), groups):
            self.assertIn('<h3>' + escape(family["title"]) + '</h3>', group)
            cards = re.findall(r'<article class="analysis-card">(.*?)</article>', group, re.DOTALL)
            self.assertEqual(len(cards), len(selections[key]))
            for index, card in zip(selections[key], cards):
                configured = configured_modes[index]
                heading = "h" + str(configured.get("heading_level", 4))
                self.assertIn("<" + heading + ">" + escape(configured["title"]) + "</" + heading + ">", card)
                question = escape(configured["question"])
                if configured.get("emphasize_question", False):
                    question = "<strong>" + question + "</strong>"
                self.assertIn('<p class="operator-question">' + question + '</p>', card)
        self.assertLess(page.index('id="analysis-choices"'), page.index('id="why-wspradar"'))
        self.assertNotIn('class="analysis-families"', self.pages["de/index.html"])
        for invalid in ({"benchmark": [0, 1], "performance": [1, 3]},
                        {"benchmark": [0], "performance": [2, 3]}):
            with self.subTest(invalid=invalid), patch.dict(self.builder.landing, {"analysis_family_modes": invalid}):
                with self.assertRaisesRegex(ValueError, "every mode exactly once"):
                    self.builder.home("en")

    def test_analysis_card_presentation_is_typed_and_independent_of_mode_identity(self) -> None:
        from scripts.landing_page import render_analysis_choices

        content = {"modes_title": "Choices", "modes_help": "Help", "modes": [
            {"icon": "any-icon", "title": "Custom <mode>", "question": "A & B?", "body": "Preserved body."}
        ]}
        for level in (3, 4):
            for emphasis in (False, True):
                with self.subTest(level=level, emphasis=emphasis):
                    configured = deepcopy(content)
                    configured["modes"][0].update(heading_level=level, emphasize_question=emphasis)
                    rendered = render_analysis_choices(configured, {}, lambda _: "", "/guide/")
                    self.assertIn(f"<h{level}>Custom &lt;mode&gt;</h{level}>", rendered)
                    question = "<strong>A &amp; B?</strong>" if emphasis else "A &amp; B?"
                    self.assertIn('<p class="operator-question">' + question + '</p>', rendered)
                    self.assertIn('<p class="muted">Preserved body.</p>', rendered)
        invalid = [{"heading_level": value} for value in (2, 5, "3", True, None)]
        invalid += [{"emphasize_question": value} for value in (1, "true", None)]
        for options in invalid:
            with self.subTest(options=options):
                configured = deepcopy(content)
                configured["modes"][0].update(options)
                with self.assertRaisesRegex(ValueError, "heading_level 3 or 4 and boolean emphasize_question"):
                    render_analysis_choices(configured, {}, lambda _: "", "/guide/")

    def test_operating_requirements_follow_get_started_before_first_experiment(self) -> None:
        copy = self.builder.landing["en"]
        for path in ("index.html", "en/index.html"):
            with self.subTest(path=path):
                page = self.pages[path]
                for removed in ('id="benchmark-views"', 'class="benchmark-view"',
                                'class="reach-intro"', "Two complementary benchmark views"):
                    self.assertNotIn(removed, page)
                self.assertEqual(page.count('class="operating-note"'), 1)
                sequence = re.search(
                    r'<section class="get-started-section"[^>]*>.*?</section>'
                    r'<aside class="operating-note"[^>]*>(.*?)</aside>'
                    r'<section class="setup-intro">', page, re.DOTALL)
                self.assertIsNotNone(sequence)
                note = sequence[1]
                for value in copy["operating_note"].values():
                    self.assertIn(escape(value), note)
                self.assertIn("known to be operating", unescape(note))
        self.assertNotIn('class="operating-note"', self.pages["de/index.html"])
        self.assertNotIn('id="benchmark-views"', self.pages["de/index.html"])

    def test_snr_median_and_pooled_decode_have_distinct_method_sequences(self) -> None:
        page = self.pages["en/index.html"]
        copy = self.builder.landing["en"]["why"]
        methods = re.findall(r'<ol class="why-steps" aria-label="([^"]+)">(.*?)</ol>', page, re.DOTALL)
        self.assertEqual(len(methods), 2)
        self.assertEqual([unescape(label) for label, _ in methods],
                         [copy["method_title"], copy["decode_method"]["title"]])
        for (_, rendered), steps in zip(methods, (copy["steps"], copy["decode_method"]["steps"])):
            self.assertEqual(rendered.count('class="why-step-heading"'), 3)
            for step in steps:
                self.assertIn(escape(step["title"]), rendered)
                self.assertIn(escape(step["body"]), rendered)
        self.assertIn("median", unescape(methods[0][1]).lower())
        self.assertNotIn("mean of station", unescape(methods[0][1]).lower())
        self.assertIn("pool each setup’s paired and one-sided decodes", unescape(methods[1][1]).lower())
        self.assertIn("totals divided by their sum", unescape(methods[1][1]).lower())
        self.assertNotIn("mean of station", unescape(methods[1][1]).lower())
        self.assertNotIn("median", unescape(methods[1][1]).lower())
        self.assertNotIn('class="why-method decode-method"', self.pages["de/index.html"])

    def test_landing_preserves_shared_copy_while_english_additions_remain_a_draft(self) -> None:
        landing = build_site.load_catalog(build_site.SOURCE / "config" / "landing.json", build_site.SOURCE / "pages")
        draft_fields = {"hero_analysis_intro", "analysis_families", "operating_note",
                        "demo_metrics", "demo_metric_context", "demo_added_views", "own_benchmark_note"}
        self.assertEqual(set(landing["en"]) - draft_fields, set(landing["de"]))
        self.assertTrue(draft_fields <= set(landing["en"]))
        self.assertTrue(draft_fields.isdisjoint(landing["de"]))
        for collection in ("flow", "modes"):
            self.assertEqual(len(landing["en"][collection]), len(landing["de"][collection]))
            draft_presentation = {"heading_level", "emphasize_question"} if collection == "modes" else set()
            for english, german in zip(landing["en"][collection], landing["de"][collection]):
                self.assertEqual(set(english) - draft_presentation, set(german))
                self.assertTrue(draft_presentation.isdisjoint(german))
                self.assertEqual(english["icon"], german["icon"])
        self.assertEqual(len(landing["en"]["curiosity_lines"]), 2)
        self.assertEqual(len(landing["de"]["curiosity_lines"]), 2)
        self.assertEqual(len(landing["en"]["start_steps"]), 3)
        self.assertEqual(len(landing["de"]["start_steps"]), 3)
        for english, german in zip(landing["en"]["start_steps"], landing["de"]["start_steps"]):
            self.assertEqual(set(english), {"title", "body"})
            self.assertEqual(set(english), set(german))
        for language in ("en", "de"):
            with self.subTest(language=language):
                content = unescape(self.pages[f"{language}/index.html"])
                copy = landing[language]
                for key in ("example_title", "example_intro", "example_question", "result", "result_label", "example_ready"):
                    self.assertIn(copy[key], content, key)
                self.assertEqual(len(copy["result_detail"]), 2)
                for detail in copy["result_detail"]:
                    self.assertIn(detail, content)
                self.assertEqual(len(copy["image_captions"]), 4)
                for caption in copy["image_captions"]:
                    self.assertEqual(set(caption), {"lead", "body"})
                    self.assertIn(caption["lead"], content)
                    self.assertIn(caption["body"], content)
                for key in ("demo_title", "demo_body", "own_title", "own_body", "setup_title", "setup_body"):
                    self.assertIn(copy[key], content, key)
                for mode in copy["modes"]:
                    self.assertIn(mode["question"], content)
                    self.assertIn(mode["body"], content)

    def test_landing_example_keeps_requested_intro_actions_and_installation_context(self) -> None:
        self.assertEqual(self.builder.landing["en"]["example_title"],
                         "See what WSPR can reveal about your station")
        self.assertEqual(self.builder.landing["en"]["example_intro"],
                         "Explore a real antenna comparison—and learn how to read your own results.")
        self.assertEqual(self.builder.landing["en"]["example_question"],
                         "Low dipole or vertical—which setup heard better?")
        self.assertEqual(self.builder.landing["en"]["result_label"], "SNR advantage for the low-dipole setup")
        self.assertEqual(self.builder.landing["de"]["result_label"], "SNR-Vorteil der Anlage mit niedrigem Dipol")
        self.assertEqual(self.builder.landing["en"]["result_detail"], ["57 767 spot pairs", "792 transmitting-station entries"])
        self.assertEqual(self.builder.landing["en"]["example_tag"], "GUIDED DEMO · 40 m RX BENCHMARK")
        self.assertEqual(self.builder.landing["en"]["example_ready"], "The example is ready to explore. No need to enter your own data.")
        self.assertEqual(self.builder.landing["de"]["example_link"], "Rundgang starten")
        self.assertEqual(self.builder.landing["de"]["try_this"], "Diese Demo starten")
        selected = self.builder.landing["featured_demo"]
        selected_config = self.builder.demo_by_id[selected["id"]]
        for language in ("en", "de"):
            with self.subTest(language=language):
                content = self.pages[f"{language}/index.html"]
                section = re.search(r'<section id="real-example"[^>]*>(.*?)</section>', content, re.DOTALL).group(1)
                copy = self.builder.landing[language]
                introduction, showcase = section.split('<div class="example-showcase">', 1)
                self.assertIn('<h2>' + escape(copy["example_title"]) + '</h2>', introduction)
                self.assertIn('<strong>' + escape(copy["example_intro"]) + '</strong>', introduction)
                rendered_meta = build_site.open_pdf_links_in_new_tabs(self.builder.md(copy["example_meta"], language)).replace('<p>', '<p class="example-meta">', 1)
                self.assertIn(rendered_meta, introduction)
                self.assertLess(introduction.index(escape(copy["example_title"])), introduction.index(escape(copy["example_intro"])))
                self.assertLess(introduction.index(escape(copy["example_intro"])), introduction.index('<p class="example-meta">'))
                if language == "en":
                    self.assertIn('<em>Practical Wireless</em>', rendered_meta)
                    configured_links = re.findall(r'\[\*\*([^\]]+?)\*\*\]\(([^)]+)\)', copy["example_meta"])
                    self.assertEqual(len(configured_links), 1)
                    publication = AnchorInventory()
                    publication.feed(rendered_meta)
                    self.assertEqual(len(publication.anchors), 1)
                    anchor = publication.anchors[0]
                    self.assertEqual((anchor["text"], anchor["attributes"]["href"]), configured_links[0])
                    self.assertTrue(urlsplit(anchor["attributes"]["href"]).path.lower().endswith(".pdf"))
                    self.assertEqual(anchor["attributes"]["target"], "_blank")
                    self.assertEqual(set(anchor["attributes"]["rel"].split()), {"noopener", "noreferrer"})
                    self.assertRegex(rendered_meta, r'<a\b[^>]*><strong>' + re.escape(escape(anchor["text"])) + r'</strong></a>')
                context = showcase.split('<div class="result-gallery">', 1)[0]
                self.assertIn('class="example-context"', context)
                self.assertRegex(context, r'class="[^\"]*\bmeasured-result\b[^\"]*"')
                self.assertIn('class="actions"', context)
                self.assertNotIn("example_station_context", copy)
                self.assertNotIn('class="example-stations"', context)
                self.assertNotIn("example_takeaway", copy)
                self.assertNotIn('class="example-takeaway"', context)
                self.assertIn(escape(copy["example_ready"]), context)
                for detail in copy["result_detail"]:
                    self.assertIn('<span>' + escape(detail) + '</span>', context)
                self.assertNotIn("example_body", copy)
                self.assertNotIn('class="example-body"', context)
                self.assertNotIn("April 2017", copy["example_tag"])
                links = AnchorInventory()
                links.feed(context)
                self.assertEqual([anchor["attributes"]["href"] for anchor in links.anchors],
                                 [f'/{language}/demos/{selected["id"]}/', selected_config["launch_url"]])
                self.assertEqual(links.anchors[0]["text"], copy["example_link"] + " →")
                self.assertEqual(links.anchors[0]["attributes"]["class"], "button")
                self.assertIn(copy["try_this"], links.anchors[1]["text"])
                self.assertEqual(links.anchors[1]["attributes"]["class"], "button secondary")
                self.assertNotIn("target", links.anchors[1]["attributes"])
                self.assertEqual(set(links.anchors[1]["attributes"]["rel"].split()), {"noopener", "noreferrer"})
                self.assertNotIn('class="example-notes"', section)
                self.assertNotRegex(" ".join(copy["result_detail"]), r"10[,. ]?000\s*km")
                self.assertNotIn("example_source", copy)
                self.assertNotIn("example_source_link", copy)
                self.assertNotIn('class="example-source"', section)
                self.assertNotIn('id="demo-source-note"', section)
                self.assertNotIn('aria-describedby="demo-source-note"', section)

    def test_landing_evidence_sources_match_native_files_and_lossless_derivative_metadata(self) -> None:
        from PIL import Image

        selected = self.builder.landing["featured_demo"]
        evidence = self.builder.landing_assets["evidence"]
        demo_payload = build_site.resource_files(
            self.builder.demo_asset_root, self.builder.demo_walkthroughs["demos"],
        )
        keys = [card["media_key"] for card in selected["cards"]]
        self.assertEqual(keys, ["landing-demo1-map", "landing-demo1-delta-decode", "landing-demo1-decoding-reach",
                                "landing-demo1-snr", "landing-demo1-temporal", "landing-demo1-coverage"])
        self.assertEqual(len(set(keys)), 6)
        for key in keys:
            item = evidence[key]
            with self.subTest(media=key):
                self.assertEqual(item["demo_id"], selected["id"])
                self.assertEqual(set(item["alt"]), {"en", "de"})
                self.assertTrue(all(item["alt"].values()))
                native = item["native"]
                self.assertTrue(native["path"].endswith(".png"))
                self.assertEqual([image["width"] for image in item["images"]], [600, 1200])
                for record in [native, *item["images"]]:
                    payload = demo_payload[record["path"].removeprefix("/")]
                    if record is native:
                        source = build_site.ROOT / record["source_path"]
                        self.assertTrue(source.is_file(), source)
                        self.assertEqual(payload, source.read_bytes())
                    self.assertEqual(len(payload), record["bytes"])
                    self.assertEqual(hashlib.sha256(payload).hexdigest(), record["sha256"])
                    with Image.open(BytesIO(payload)) as image:
                        self.assertEqual(image.size, (record["width"], record["height"]))
                    self.assertTrue(record["path"].startswith("/assets/demos/"))
                for image in item["images"]:
                    self.assertTrue(image["path"].endswith(".webp"))
                    self.assertLessEqual(image["width"], native["width"])
                    self.assertLessEqual(abs(image["height"] - round(image["width"] * native["height"] / native["width"])), 1)
                preview = item["preview"]
                self.assertEqual([image["width"] for image in preview["images"]], [360, 540, 720])
                source = build_site.SOURCE / "assets/landing" / preview["source"]["path"]
                self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), preview["source"]["sha256"])
                with Image.open(source) as original:
                    for record in preview["images"]:
                        payload = self.builder.landing_payload[
                            record["path"].removeprefix("/assets/landing/")
                        ]
                        self.assertEqual(len(payload), record["bytes"])
                        self.assertEqual(hashlib.sha256(payload).hexdigest(), record["sha256"])
                        self.assertEqual(record["width"] * 3, record["height"] * 4)
                        self.assertIn(record["path"].removeprefix("/assets/landing/"), self.builder.landing_assets["publish_files"])
                        with Image.open(BytesIO(payload)) as decoded:
                            expected = original.convert("RGB").resize((record["width"], record["height"]), Image.Resampling.LANCZOS)
                            self.assertEqual(decoded.convert("RGB").tobytes(), expected.tobytes())
                            self.assertEqual(decoded.getpixel((0, 0)), (0, 11, 25))
                self.assertNotIn(preview["source"]["path"], self.builder.landing_assets["publish_files"])

    def test_demo_metrics_keep_configured_values_with_results(self) -> None:
        page = self.pages["en/index.html"]
        section = re.search(r'<section id="real-example"[^>]*>(.*?)</section>', page, re.DOTALL)[1]
        context = section.split('<div class="result-gallery">', 1)[0]
        copy = self.builder.landing["en"]
        metrics = re.findall(r'<div class="demo-metric(?: measured-result)?">(.*?)</div>', context, re.DOTALL)
        self.assertEqual(len(metrics), 1 + len(copy["demo_metrics"]))
        self.assertIn(escape(copy["result"]), metrics[0])
        self.assertIn(escape(copy["result_label"]), metrics[0])
        for configured, rendered in zip(copy["demo_metrics"], metrics[1:]):
            for value in configured.values():
                self.assertIn(escape(value), rendered)
            self.assertIn(escape(copy["demo_metric_context"]), rendered)
        for removed in ("demo_scope", "demo_balance"):
            self.assertNotIn(removed, copy)
            self.assertNotIn('class="' + removed.replace("_", "-") + '"', context)
        self.assertEqual(len(re.findall(r'<div class="demo-metric(?: measured-result)?">', self.pages["de/index.html"])), 1)

    def test_landing_evidence_cards_show_responsive_previews_and_original_links_in_locale_order(self) -> None:
        selected = self.builder.landing["featured_demo"]
        for language, count in (("en", 6), ("de", 4)):
            with self.subTest(language=language):
                content = self.pages[f"{language}/index.html"]
                self.assertIn('/assets/demo-walkthrough.css', content)
                self.assertIn('/assets/demo-walkthrough.js', content)
                cards = [card for card in selected["cards"] if language in card["locales"]]
                previews = re.findall(r'<figure class="result-preview" data-media-key="([^"]+)">(.*?)</figure>', content, re.DOTALL)
                self.assertEqual(len(previews), count)
                self.assertEqual([key for key, _ in previews], [card["media_key"] for card in cards])
                copy = self.builder.landing[language]
                for card, (key, preview) in zip(cards, previews):
                    item = self.builder.landing_assets["evidence"][key]
                    native = item["native"]
                    thumbnail = item["preview"]
                    inventory = build_site.LinkInventory()
                    inventory.feed(preview)
                    evidence_images = [image for image in inventory.images if image.get("class") == "result-image"]
                    self.assertEqual(len(evidence_images), 1)
                    image = evidence_images[0]
                    self.assertEqual(image["src"], thumbnail["images"][0]["path"])
                    self.assertEqual(image["srcset"].split(", "),
                                     [f'{derivative["path"]} {derivative["width"]}w' for derivative in thumbnail["images"]])
                    self.assertTrue(image["sizes"])
                    self.assertEqual(image["alt"], thumbnail["alt"][language])
                    self.assertEqual(image["loading"], "eager")
                    self.assertEqual((image["width"], image["height"]), ("360", "270"))
                    self.assertNotIn("result-crop", preview)
                    links = AnchorInventory()
                    links.feed(preview)
                    self.assertEqual(len(links.anchors), 1)
                    attributes = links.anchors[0]["attributes"]
                    self.assertEqual(attributes["href"], native["path"])
                    self.assertEqual(attributes["target"], "_blank")
                    self.assertEqual(set(attributes["rel"].split()), {"noopener", "noreferrer"})
                    self.assertEqual(attributes["title"], card["detail_title"][language])
                    self.assertEqual(attributes["aria-label"], self.builder.copy[language]["full_size"] + ": " + card["detail_title"][language])
                    self.assertIn("data-case-lightbox", attributes)
                    self.assertEqual(attributes["data-original-alt"], item["alt"][language])
                    self.assertEqual(attributes["data-caption-id"], "caption-" + key)
                    if card["copy"]["kind"] == "existing":
                        index = card["copy"]["index"]
                        title, caption = copy["image_titles"][index], copy["image_captions"][index]
                    else:
                        caption = next(view for view in copy["demo_added_views"] if view["id"] == card["copy"]["id"])
                        title = caption["title"]
                    heading = "<h4>" + escape(title) + "</h4>"
                    self.assertIn(heading, preview)
                    self.assertIn(escape(card["subtitle"][language]), preview)
                    self.assertLess(preview.index(heading), preview.index("<a "))
                    self.assertLess(preview.index("</a>"), preview.index("<figcaption "))
                    self.assertIn('<figcaption id="caption-' + key + '"><strong>' + escape(caption["lead"]) + "</strong> " + escape(caption["body"]) + "</figcaption>", preview)
                    note = '<p class="result-preview-note">' + escape(thumbnail["note"][language]) + '</p>'
                    self.assertIn(note, preview)
                    self.assertLess(preview.index("</a>"), preview.index(note))
                    self.assertLess(preview.index(note), preview.index("<figcaption "))
                    icons = [image for image in inventory.images if image.get("class") != "result-image"]
                    self.assertEqual(len(icons), 1)
                    icon = self.builder.landing_assets["icons"][card["icon"]]
                    self.assertEqual(icons[0]["src"], "/assets/landing/" + (icon["path"] if isinstance(icon, dict) else icon))
                    self.assertEqual(icons[0]["alt"], "")
                    self.assertEqual(icons[0]["aria-hidden"], "true")

    def test_landing_rejects_evidence_from_a_different_demo(self) -> None:
        selected = self.builder.landing["featured_demo"]
        item = self.builder.landing_assets["evidence"][selected["cards"][0]["media_key"]]
        with patch.dict(item, {"demo_id": "different-experiment"}):
            with self.assertRaisesRegex(ValueError, "Landing media must belong to the featured demo"):
                self.builder.home("en")

    def test_landing_rejects_unknown_or_duplicate_evidence_selections(self) -> None:
        selected = self.builder.landing["featured_demo"]
        for key in ("unknown-evidence", selected["cards"][1]["media_key"]):
            with self.subTest(key=key):
                cards = deepcopy(selected["cards"])
                cards[0]["media_key"] = key
                with patch.dict(selected, {"cards": cards}):
                    with self.assertRaises(ValueError):
                        self.builder.home("en")

    def test_landing_rejects_missing_upscaled_or_distorted_derivatives(self) -> None:
        selected = self.builder.landing["featured_demo"]
        item = self.builder.landing_assets["evidence"][selected["cards"][0]["media_key"]]["preview"]
        distorted = deepcopy(item["images"])
        distorted[0]["height"] += 20
        upscaled = deepcopy(item["images"])
        upscaled[0]["width"] = item["source"]["width"] + 1
        for images in ([], distorted, upscaled):
            with self.subTest(images=images), patch.dict(item, {"images": images}):
                with self.assertRaisesRegex(ValueError, "Landing evidence"):
                    self.builder.home("en")

    def test_website_copy_has_matching_language_keys(self) -> None:
        self.assertEqual(set(build_site.COPY["en"]), set(build_site.COPY["de"]))

    def test_support_pages_route_each_purpose_to_the_matching_discussion_category(self) -> None:
        expected_categories = [
            "ask-a-question", "discuss-your-experiments",
            "ideas-and-feature-requests", "report-a-bug-or-concern",
        ]
        expected_headings = {
            "en": ["Ask a question", "Discuss your experiments", "Ideas and feature requests", "Report a bug or concern"],
            "de": ["Eine Frage stellen", "Experimente diskutieren", "Ideen und Funktionswünsche", "Fehler oder Bedenken melden"],
        }
        retired_headings = {
            "en": ("Questions and experiments", "Report a Bug", "Feature request", "Scientific or methodological concern"),
            "de": ("Fragen und Experimente", "Fehler melden", "Funktionswunsch", "Wissenschaftliches oder methodisches Problem"),
        }
        for language in ("en", "de"):
            for route_name in ("community", "report"):
                content = self.pages[f"{language}/{route_name}/index.html"]
                cards = re.findall(r"<article>(.*?)</article>", content, re.DOTALL)
                with self.subTest(language=language, route=route_name):
                    self.assertEqual(len(cards), 4)
                    headings = [heading for card in cards for heading in re.findall(r"<h2>(.*?)</h2>", card, re.DOTALL)]
                    self.assertEqual(headings, expected_headings[language])
                    for retired in retired_headings[language]:
                        self.assertNotIn(retired, headings)
                    for card, expected in zip(cards, expected_categories):
                        inventory = AnchorInventory()
                        inventory.feed(card)
                        local_links = [anchor["attributes"]["href"] for anchor in inventory.anchors
                                       if anchor["attributes"]["href"].startswith("/")]
                        self.assertEqual(local_links, [f"/{language}/documentation/full/"] if expected == "ask-a-question" else [])
                        if expected == "ask-a-question":
                            paragraphs = re.findall(r"<p\b[^>]*>(.*?)</p>", card, re.DOTALL)
                            self.assertEqual(len(paragraphs), 1)
                            paragraph_inventory = AnchorInventory()
                            paragraph_inventory.feed(paragraphs[0])
                            self.assertEqual(
                                [(anchor["attributes"]["href"], anchor["text"]) for anchor in paragraph_inventory.anchors],
                                [(f"/{language}/documentation/full/", "manual" if language == "en" else "Handbuch")],
                            )
                        submission_links = [anchor for anchor in inventory.anchors
                                            if urlsplit(anchor["attributes"]["href"]).netloc]
                        self.assertEqual(len(submission_links), 1)
                        for anchor in submission_links:
                            destination = urlsplit(anchor["attributes"]["href"])
                            self.assertEqual(destination.scheme, "https")
                            self.assertEqual(destination.netloc, "github.com")
                            self.assertEqual(destination.path, "/markusthemaker/WSPRadar/discussions/new")
                            self.assertEqual(parse_qs(destination.query).get("category", []), [expected])
                    intro = AnchorInventory()
                    intro.feed(content.split('<div class="report-options">', 1)[0])
                    github_links = [anchor["attributes"]["href"] for anchor in intro.anchors
                                    if urlsplit(anchor["attributes"]["href"]).netloc == "github.com"]
                    expected_urls = (["https://github.com/markusthemaker/WSPRadar/discussions/new?category=report-a-bug-or-concern"]
                                     if route_name == "report" else [])
                    self.assertEqual(github_links, expected_urls)
                    self.assertNotIn("/issues/new", content)

    def test_support_card_summary_preserves_complete_guidance_on_report_page(self) -> None:
        scientific_guidance = {
            "en": "a specific assumption, calculation, interpretation, or claim that needs review.",
            "de": "eine konkrete Annahme, Berechnung, Interpretation oder Aussage, die überprüft werden sollte.",
        }
        for language, expected_science in scientific_guidance.items():
            for route_name in ("community", "report"):
                cards = re.findall(r"<article>(.*?)</article>", self.pages[f"{language}/{route_name}/index.html"], re.DOTALL)
                with self.subTest(language=language, route=route_name):
                    self.assertEqual(len(cards), 4)
                    self.assertEqual(re.findall(r"<p>(.*?)</p>", cards[3], re.DOTALL), [build_site.COPY[language]["report_summary"]])
                    for card in cards:
                        self.assertNotIn(expected_science, card)
                        self.assertNotIn(build_site.COPY[language]["bug_intro"], card)
            report_intro = self.pages[f"{language}/report/index.html"].split('<div class="report-options">', 1)[0]
            with self.subTest(language=language):
                self.assertIn(expected_science, report_intro)
                self.assertIn(build_site.COPY[language]["scientific_body"], report_intro)
                self.assertIn(build_site.COPY[language]["bug_intro"], report_intro)

    def test_support_welcomes_manual_clarifications_without_obsolete_categories(self) -> None:
        guidance = {
            "en": ("Please check the manual first", "If your question is unanswered or something is unclear"),
            "de": ("Sieh bitte zuerst im Handbuch nach", "Wenn deine Frage unbeantwortet bleibt oder etwas unklar ist"),
        }
        for language, phrases in guidance.items():
            for route_name in ("community", "report"):
                content = self.pages[f"{language}/{route_name}/index.html"]
                visible_text = unescape(re.sub(r"<[^>]+>", "", content))
                with self.subTest(language=language, route=route_name):
                    for phrase in phrases:
                        self.assertIn(phrase, visible_text)
                    for obsolete in ("Help and bug reports", "Share experiments and ideas", "help-and-bug-reports", "share-experiments-and-ideas"):
                        self.assertNotIn(obsolete, content)

    def test_support_onboarding_is_bilingual_and_does_not_require_a_complete_diagnosis(self) -> None:
        phrases = {
            "en": ("free GitHub account is required", "No programming knowledge is needed", "Please write all posts and replies in English", "Posts are public", "You do not need a confirmed diagnosis"),
            "de": ("kostenloses GitHub-Konto erforderlich", "Programmierkenntnisse sind nicht nötig", "Bitte verfasse alle Beiträge und Antworten auf Englisch", "Beiträge sind öffentlich", "Du brauchst keine bestätigte Diagnose"),
        }
        for language, expected in phrases.items():
            for route_name in ("community", "report"):
                content = self.pages[f"{language}/{route_name}/index.html"]
                with self.subTest(language=language, route=route_name):
                    for phrase in expected:
                        self.assertIn(phrase, content)
            report = self.pages[f"{language}/report/index.html"]
            with self.subTest(language=language):
                self.assertIn("optional", report)
                self.assertIn("UTC", report)
                self.assertIn("Screenshot" if language == "de" else "screenshot", report)

    def test_issue_chooser_points_community_intake_to_discussions(self) -> None:
        config = (build_site.ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml").read_text(encoding="utf-8")
        self.assertIn("blank_issues_enabled: false", config)
        destinations = re.findall(r"^\s+url: (\S+)$", config, re.MULTILINE)
        discussion_categories = []
        for destination in destinations:
            parsed = urlsplit(destination)
            self.assertNotIn("/issues/new", parsed.path)
            if parsed.netloc == "github.com":
                self.assertEqual(parsed.path, "/markusthemaker/WSPRadar/discussions/new")
                discussion_categories.extend(parse_qs(parsed.query).get("category", []))
        self.assertEqual(discussion_categories, ["ask-a-question", "discuss-your-experiments", "ideas-and-feature-requests", "report-a-bug-or-concern"])

    def test_application_buttons_use_localized_app_or_landing_action_labels(self) -> None:
        labels = {"en": "Open WSPRadar App", "de": "WSPRadar App öffnen"}
        for path, content in self.pages.items():
            language = "en" if path == "index.html" else path.split("/", 1)[0]
            inventory = AnchorInventory()
            inventory.feed(content)
            demo_route = re.fullmatch(r"(?:en|de)/demos/([^/]+)/index.html", path)
            expected_labels = {build_site.APP_URL: {labels[language]}}
            if demo_route:
                demo = self.builder.demo_by_id[demo_route[1]]
                config = self.builder.demo_walkthroughs["demos"][demo["id"]]
                actions = demo_walkthrough.language_override(config, "launch_actions", language, None)
                if actions is None:
                    launch_url = build_site.demo_launch_url(demo)
                    expected_labels[launch_url] = {"Run in WSPRadar App" if language == "en" else "In WSPRadar App starten"}
                else:
                    for action in actions:
                        launch_url = demo_walkthrough.demo_launch_url(demo, action["variant"])
                        expected_labels.setdefault(launch_url, set()).add(action["label"])
                sections = list(demo_walkthrough.demo_sections(config, language))
                while sections:
                    section = sections.pop()
                    sections.extend(section.get("subsections", []))
                    if "launch_action" in section:
                        action = section["launch_action"]
                        launch_url = demo_walkthrough.demo_launch_url(demo, action["variant"])
                        expected_labels.setdefault(launch_url, set()).add(action["label"])
            if path in ("index.html", f"{language}/index.html"):
                expected_labels[build_site.APP_URL].add(build_site.COPY[language]["start_analysis"])
                selected = self.builder.landing["featured_demo"]
                launch_url = self.builder.demo_by_id[selected["id"]]["launch_url"]
                expected_labels[launch_url] = {self.builder.landing[language]["try_this"]}
                expected_labels[build_site.APP_URL].add(self.builder.landing[language]["own_link"])
            buttons = [anchor for anchor in inventory.anchors
                       if anchor["attributes"].get("href") in expected_labels
                       and "button" in anchor["attributes"].get("class", "").split()]
            with self.subTest(path=path):
                if demo_route or path in ("index.html", f"{language}/index.html"):
                    self.assertTrue(buttons)
                else:
                    self.assertEqual(buttons, [], "Generic application actions belong in the shared Analysis navigation")
                if path in ("index.html", f"{language}/index.html"):
                    self.assertEqual(sum(anchor["attributes"]["href"] == launch_url for anchor in buttons), 1)
                for anchor in buttons:
                    self.assertIn(anchor["text"].removesuffix(" ↗").removesuffix(" →"), expected_labels[anchor["attributes"]["href"]])

    def test_overview_has_three_ordered_steps_with_the_matching_destinations(self) -> None:
        titles = {
            "en": ["Choose the Question", "Perform the Experiment", "Run WSPRadar App"],
            "de": ["Wähle die Fragestellung", "Führe das Experiment durch", "Starte die WSPRadar App"],
        }
        for language in ("en", "de"):
            paths = [f"{language}/index.html"] + (["index.html"] if language == "en" else [])
            destinations = [self.builder.anchors[language]["sec-2-2"] + "#sec-2-2",
                            self.builder.anchors[language]["sec-2-1"] + "#sec-2-1", build_site.APP_URL]
            for path in paths:
                cards = re.findall(r'<article class="journey-card">(.*?)</article>', self.pages[path], re.DOTALL)
                with self.subTest(path=path):
                    self.assertEqual(len(cards), 3)
                    for number, (card, title, destination) in enumerate(zip(cards, titles[language], destinations), 1):
                        self.assertIn(f'<span class="journey-number" aria-hidden="true">{number:02d}</span>', card)
                        self.assertIn(f"<h2>{title}</h2>", card)
                        inventory = build_site.LinkInventory()
                        inventory.feed(card)
                        self.assertEqual(inventory.links, [destination])

    def test_removed_practical_setup_route_has_no_internal_links_and_manual_guidance_remains(self) -> None:
        manual_anchors = ("sec-2-1", "sec-2-2", "sec-5", "sec-3-rx-benchmark", "sec-3-tx-benchmark",
                          "sec-3-rx-performance", "sec-3-tx-performance", "sec-a",
                          "sec-simultaneous-tx-setup", "sec-reference-snr-calibration")
        for path, content in self.pages.items():
            inventory = build_site.LinkInventory()
            inventory.feed(content)
            with self.subTest(path=path):
                for href in inventory.links:
                    parsed = urlsplit(href)
                    if parsed.scheme or parsed.netloc:
                        continue
                    target = unquote(urljoin("/" + path, parsed.path))
                    self.assertNotRegex(target, r"^/(?:en|de)/practical-setup(?:/|$)")
        for language in ("en", "de"):
            with self.subTest(language=language):
                self.assertNotIn(f"{language}/practical-setup/index.html", self.pages)
                for anchor in manual_anchors:
                    chapter = self.builder.anchors[language][anchor].lstrip("/") + "index.html"
                    inventory = build_site.LinkInventory()
                    inventory.feed(self.pages[chapter])
                    self.assertIn(anchor, inventory.ids)

                content = self.pages[f"{language}/index.html"]
                inventory = AnchorInventory()
                inventory.feed(content)
                for label, anchor in (("basics", "sec-2-1"), ("modes_help", "sec-2-2")):
                    links = [item for item in inventory.anchors
                             if item["text"] == self.builder.landing[language][label] + " →"]
                    self.assertEqual([item["attributes"]["href"] for item in links],
                                     [self.builder.anchors[language][anchor] + "#" + anchor])
                setup = re.search(r'<section class="setup-intro">(.*?)</section>', content, re.DOTALL)
                self.assertIsNotNone(setup)
                inventory = build_site.LinkInventory()
                inventory.feed(setup[1])
                self.assertEqual(inventory.links, [f"/{language}/documentation/", f"/{language}/community/"])

                guide = self.pages[f"{language}/guides/read-results/index.html"]
                breadcrumb = re.search(r'<p class="breadcrumb">(.*?)</p>', guide, re.DOTALL)
                self.assertIsNotNone(breadcrumb)
                inventory = AnchorInventory()
                inventory.feed(breadcrumb[1])
                self.assertEqual([(item["attributes"]["href"], item["text"]) for item in inventory.anchors],
                                 [(f"/{language}/documentation/", build_site.COPY[language]["docs"])])

    def test_full_reader_contains_every_original_anchor_once(self) -> None:
        for language in ("en", "de"):
            inventory = build_site.LinkInventory()
            inventory.feed(self.pages[f"{language}/documentation/full/index.html"])
            for anchor in self.builder.anchors[language]:
                with self.subTest(language=language, anchor=anchor):
                    self.assertEqual(inventory.ids.count(anchor), 1)

    def test_every_chapter_crosslink_resolves_to_an_existing_bilingual_anchor(self) -> None:
        inventories = {}
        for path, content in self.pages.items():
            inventory = build_site.LinkInventory()
            inventory.feed(content)
            inventories[path] = inventory
        for language in ("en", "de"):
            for anchor, chapter in self.builder.anchors[language].items():
                with self.subTest(language=language, anchor=anchor):
                    self.assertIn(anchor, inventories[chapter.lstrip("/") + "index.html"].ids)

    def test_every_rendered_local_page_link_and_fragment_resolves(self) -> None:
        inventories = {}
        for path, content in self.pages.items():
            inventory = build_site.LinkInventory()
            inventory.feed(content)
            inventories[path] = inventory
        for path, inventory in inventories.items():
            for href in inventory.links:
                parsed = urlsplit(href)
                if parsed.scheme or parsed.netloc:
                    continue
                target = unquote(urljoin("/" + path, parsed.path)).lstrip("/") if parsed.path else path
                if target.endswith("/") or not target:
                    target += "index.html"
                if not target.endswith(".html"):
                    continue
                with self.subTest(path=path, href=href):
                    self.assertIn(target, inventories)
                    if parsed.fragment:
                        self.assertIn(unquote(parsed.fragment), inventories[target].ids)

    def test_every_reviewed_figure_and_capture_appears_once_on_its_demo_in_each_language(self) -> None:
        published_ids = {demo["id"] for demo in self.builder.published_demos}
        for language in ("en", "de"):
            for media in [*self.builder.figures, *self.builder.screenshots]:
                with self.subTest(language=language, media=media["key"]):
                    if media["demo_id"] not in published_ids:
                        self.assertNotIn(f"{language}/demos/{media['demo_id']}/index.html", self.pages)
                        continue
                    html = self.pages[f"{language}/demos/{media['demo_id']}/index.html"]
                    inventory = build_site.LinkInventory()
                    inventory.feed(html)
                    matching = [image for image in inventory.images if image.get("src") == "/content/" + media["asset_path"]]
                    config = self.builder.demo_walkthroughs["demos"][media["demo_id"]]
                    excluded = config.get("excluded_media_keys", [])
                    placed = ({config.get("setup_media_key")} - {None}
                              if config.get("show_setup_media", True) else set())
                    sections = list(demo_walkthrough.demo_sections(config, language))
                    while sections:
                        section = sections.pop()
                        sections.extend(section.get("subsections", []))
                        if section.get("layout") != "full":
                            placed.update(section.get("media_keys", []))
                    if media["key"] in excluded or media["key"] not in placed:
                        self.assertEqual(matching, [])
                        continue
                    self.assertEqual(len(matching), 1)
                    self.assertEqual(matching[0]["alt"], media["alt"][language])
                    self.assertIn(escape(media["title"][language]), html)

    def test_guides_and_documentation_figures_load_shared_viewer_on_demand(self) -> None:
        assets = ("/assets/demo-walkthrough.css", "/assets/demo-walkthrough.js")
        for language in ("en", "de"):
            page = self.pages["en/documentation/sec-2/index.html"] if language == "en" else self.pages[f"{language}/guides/read-results/index.html"]
            for asset in assets:
                self.assertEqual(page.count(asset), 1)

        builder = build_site.SiteBuilder()
        original = "/content/example-original.PNG?view=full#figure"
        preview = "/content/example-preview.webp"
        body = ('<article class="prose"><figure><a href="' + original
                + '" target="_blank" rel="noopener noreferrer"><img src="' + preview
                + '" alt="Scientific evidence" loading="lazy"></a>'
                + '<figcaption>Existing figure context.</figcaption></figure></article>')
        builder.page("en", "documentation/viewer-contract/", "Figure contract", body, "docs")
        rendered = builder.pages["en/documentation/viewer-contract/index.html"]
        for asset in assets:
            self.assertEqual(rendered.count(asset), 1)
        inventory = build_site.LinkInventory()
        inventory.feed(rendered)
        self.assertIn(original, inventory.links)
        self.assertIn(preview, [image.get("src") for image in inventory.images])
        self.assertNotIn(original, [image.get("src") for image in inventory.images])
        self.assertNotIn('href="' + original + '" rel="preload"', rendered)
        self.assertIn("Existing figure context.", rendered)

        builder.page("en", "documentation/text-contract/", "Text contract", "<p>Text only.</p>", "docs")
        text_only = builder.pages["en/documentation/text-contract/index.html"]
        for asset in assets:
            self.assertNotIn(asset, text_only, "header artwork alone must not load the figure viewer")

    def test_manual_figures_only_add_illustrations_and_keep_legacy_guide_destinations(self) -> None:
        builder = self.builder
        source = builder.manuals["en"]
        illustrated = builder.illustrated_manual(source, "en")
        pattern = r'<figure class="figure-block manual-figure">.*?</figure>\n\n'
        figures = re.findall(pattern, illustrated, re.DOTALL)
        self.assertEqual(len(figures), 4)
        self.assertEqual(re.sub(pattern, '', illustrated, flags=re.DOTALL), source)
        self.assertEqual(builder.illustrated_manual(builder.manuals["de"], "de"), builder.manuals["de"])
        for suffix in ("sec-2/", "full/"):
            page = self.pages["en/documentation/" + suffix + "index.html"]
            self.assertEqual(page.count('class="figure-block manual-figure"'), 4)
            for figure in figures:
                inventory = build_site.LinkInventory()
                inventory.feed(figure)
                self.assertEqual(len(inventory.images), 1)
                links = re.findall(r'<a[^>]*href="([^"]+)"', figure)
                self.assertEqual(len(links), 2)
                self.assertIn(links[0], page)
                self.assertIn(links[1], page)
        redirect = self.pages["en/guides/read-results/index.html"]
        self.assertIn('location.replace(', redirect)
        for stage in ("map-view", "segment-inspector", "station-insights", "drill-down"):
            self.assertIn(builder.result_step_url("en", stage), redirect)
        self.assertNotIn('guide-section', redirect)

    def test_all_four_practical_guide_stages_use_the_corresponding_live_capture(self) -> None:
        class GuideInventory(HTMLParser):
            def __init__(self) -> None:
                super().__init__()
                self.sections = []
                self.images = {}

            def handle_starttag(self, tag, attributes) -> None:
                attrs = dict(attributes)
                if tag == "section":
                    self.sections.append(attrs.get("id"))
                if tag == "img" and self.sections:
                    self.images.setdefault(self.sections[-1], []).append(attrs.get("src"))

            def handle_endtag(self, tag) -> None:
                if tag == "section":
                    self.sections.pop()

        expected_stages = {"map-view": "map", "segment-inspector": "segment", "station-insights": "stations", "drill-down": "drilldown"}
        published_ids = {demo["id"] for demo in self.builder.published_demos}
        for language in ("de",):
            inventory = GuideInventory()
            inventory.feed(self.pages[f"{language}/guides/read-results/index.html"])
            for section, stage in expected_stages.items():
                with self.subTest(language=language, section=section):
                    captures = [item for item in self.builder.screenshots
                                if item.get("stage") == stage and item["demo_id"] in published_ids]
                    self.assertTrue(captures, f"No reviewed live capture for {stage}")
                    self.assertEqual(inventory.images.get(section), ["/content/" + captures[0]["asset_path"]])


class DemoSupplementManifestTests(TemporarySiteTests):
    """Reviewed downloads are exact, bounded, and independent of app hosting."""

    def setUp(self) -> None:
        super().setUp()
        self.supplements = self.root / "source" / "assets" / "demos"
        self.name = "example/report.pdf"
        self.payload = b"%PDF-1.7\nreviewed fixture\n%%EOF\n"
        self.write("source/assets/demos/" + self.name, self.payload)
        self.record = {"bytes": len(self.payload), "sha256": hashlib.sha256(self.payload).hexdigest()}
        self.manifest = {"schema_version": 1, "files": {self.name: self.record}}
        self.save_manifest()

    def save_manifest(self) -> None:
        self.write("source/assets/demos/manifest.json", json.dumps(self.manifest))

    def test_only_reviewed_pdf_bytes_are_published(self) -> None:
        self.write("source/assets/demos/unreviewed.pdf", b"%PDF-1.7\nnot published")
        self.write("source/assets/demos/private.txt", "not published")
        self.assertEqual(build_site.demo_supplement_files(self.supplements), {"assets/demos/" + self.name: self.payload})

    def test_modified_pdf_or_hash_is_rejected(self) -> None:
        for field, value in (("bytes", len(self.payload) + 1), ("sha256", "0" * 64)):
            with self.subTest(field=field):
                self.manifest["files"][self.name] = {**self.record, field: value}
                self.save_manifest()
                with self.assertRaisesRegex(ValueError, "Demo supplement PDF hash mismatch"):
                    build_site.demo_supplement_files(self.supplements)

    def test_matching_html_response_is_not_accepted_as_pdf(self) -> None:
        payload = b"<html>Unavailable PDF</html>"
        self.write("source/assets/demos/" + self.name, payload)
        self.manifest["files"][self.name] = {"bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, "Demo supplement PDF signature missing"):
            build_site.demo_supplement_files(self.supplements)

    def test_escaping_noncanonical_and_non_pdf_paths_are_rejected(self) -> None:
        for name in ("../report.pdf", "/report.pdf", "folder\\report.pdf", "./report.pdf", "folder//report.pdf", "report.html"):
            with self.subTest(name=name):
                self.manifest["files"] = {name: self.record}
                self.save_manifest()
                with self.assertRaisesRegex(ValueError, "Unsafe demo supplement PDF path"):
                    build_site.demo_supplement_files(self.supplements)

    def test_unknown_schema_and_invalid_records_are_rejected(self) -> None:
        for manifest in ([], {"schema_version": True, "files": {}}, {"schema_version": 2, "files": {}},
                         {"schema_version": 1, "files": []}, {"schema_version": 1, "files": {}, "copy_all": True}):
            with self.subTest(manifest=manifest):
                self.manifest = manifest
                self.save_manifest()
                with self.assertRaisesRegex(ValueError, "Invalid demo supplement PDF manifest"):
                    build_site.demo_supplement_files(self.supplements)
        for record in (None, {"bytes": True, "sha256": "0" * 64}, {"bytes": 1, "sha256": "invalid"},
                       {**self.record, "publish": True}):
            with self.subTest(record=record):
                self.manifest = {"schema_version": 1, "files": {self.name: record}}
                self.save_manifest()
                with self.assertRaisesRegex(ValueError, "Invalid demo supplement PDF record"):
                    build_site.demo_supplement_files(self.supplements)


class StaleBuildCheckTests(TemporarySiteTests):
    """A successful --check must certify the built assets and page inventory too."""

    def setUp(self) -> None:
        super().setUp()
        self.source = self.root / "source"
        self.content = self.root / "source" / "imported" / "app"
        self.output = self.root / "generated"
        self.supplements = self.root / "source" / "assets" / "demos"
        self.pdf = b"%PDF-1.7\nreviewed fixture\n%%EOF\n"
        self.write("source/assets/demos/reference/report.pdf", self.pdf)
        self.write("source/assets/demos/manifest.json", json.dumps({"schema_version": 1, "files": {
            "reference/report.pdf": {"bytes": len(self.pdf), "sha256": hashlib.sha256(self.pdf).hexdigest()}}}))
        renderer = {
            "source_sha256": {"docs/pdf_generator.py": "a" * 64, "i18n.py": "b" * 64},
            "dependencies": {"python": "test"}, "fonts_sha256": {"DejaVuSans.ttf": "c" * 64},
        }
        logo_hash = "d" * 64
        documentation_files = {}
        for language, manual in (("en", "Original manual\n"), ("de", "Originales Handbuch\n")):
            name = f"WSPRadar_Doc_{language.upper()}.pdf"
            self.write("source/assets/documentation/" + name, self.pdf)
            documentation_files[name] = {
                "bytes": len(self.pdf), "sha256": hashlib.sha256(self.pdf).hexdigest(),
                "language": language, "manual_sha256": hashlib.sha256(manual.encode("utf-8")).hexdigest(),
                "app_version": "test",
            }
            identity = {
                "language": language, "manual_sha256": documentation_files[name]["manual_sha256"],
                "app_version": "test", "logo_sha256": logo_hash, "renderer": renderer,
            }
            identity_bytes = (json.dumps(identity, ensure_ascii=False, indent=2, sort_keys=True,
                                         allow_nan=False) + "\n").encode("utf-8")
            documentation_files[name]["render_key"] = hashlib.sha256(identity_bytes).hexdigest()
        self.write("source/assets/documentation/manifest.json", json.dumps({
            "schema_version": 1, "logo_sha256": logo_hash, "renderer": renderer,
            "files": documentation_files}))
        self.write("source/theme/styles/site.css", "body {color: white;}\n")
        self.write("source/theme/styles/landing.css", ".landing {color: white;}\n")
        self.write("source/theme/styles/print.css", "@media print {body {color: black;}}\n")
        self.write("source/theme/scripts/print.js", "'use strict';\n")
        self.write("source/theme/scripts/site.js", "'use strict';\n")
        self.write("source/theme/scripts/entry.js", "'use strict';\n")
        self.write("source/theme/scripts/product-navigation.js", "'use strict';\n")
        self.write("source/theme/styles/demo-walkthrough.css", ".case-study {color: white;}\n")
        self.write("source/theme/scripts/demo-walkthrough.js", "'use strict';\n")
        self.write("source/theme/styles/demos-index.css", ".demos-landing {color: white;}\n")
        self.write("source/theme/scripts/demos-index.js", "'use strict';\n")
        self.write("source/assets/landing/originals/icons/neon/tx-station.svg", '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2v20"/></svg>')
        self.write("source/assets/brand/WSPRadar-2x1.png", b"Reviewed legacy logo fixture")
        self.write("source/imported/app/manual.en.md", "Original manual\n")
        source_bytes = (self.content / "manual.en.md").read_bytes()
        manifest = {"schema_version": 1, "app_version": "test", "source_revision": "a" * 40,
                    "source_dirty": False, "files": {"manual.en.md": {
                        "bytes": len(source_bytes), "sha256": hashlib.sha256(source_bytes).hexdigest()}}}
        self.write("source/imported/app/manifest.json", json.dumps(manifest))
        self.fake_builder = SimpleNamespace(
            brand={"fonts": [], "app_version": "test"}, manuals={"en": "Original manual\n", "de": "Originales Handbuch\n"},
            demos=[{"id": "example"}], published_demos=[], figures=[], screenshots=[],
            landing_assets={"publish_files": ["web/icons/tx-station.svg"]},
            landing_payload={"web/icons/tx-station.svg": (self.source / "assets/landing/originals/icons/neon/tx-station.svg").read_bytes()},
            manifest=manifest, content=self.content,
            documentation_pdfs={f"assets/documentation/WSPRadar_Doc_{language.upper()}.pdf": self.pdf
                                for language in ("en", "de")},
            demo_root=self.source / "pages" / "demos", demo_asset_root=self.source / "assets" / "demos", demo_walkthroughs={"demos": {}},
            render=lambda: {"en/index.html": '<main id="main">Current page</main>'},
        )
        for name, value in (("SOURCE", self.source), ("CONTENT", self.content), ("OUTPUT", self.output), ("DEMO_SUPPLEMENTS", self.supplements)):
            manager = patch.object(build_site, name, value)
            manager.start()
            self.addCleanup(manager.stop)
        builder_patch = patch.object(build_site, "SiteBuilder", return_value=self.fake_builder)
        builder_patch.start()
        self.addCleanup(builder_patch.stop)
        external_patch = patch.object(build_site, "check_external_links", return_value=[])
        self.external_check = external_patch.start()
        self.addCleanup(external_patch.stop)
        with redirect_stdout(StringIO()):
            build_site.build()
        self.external_check.assert_not_called()

    def check(self) -> None:
        with redirect_stdout(StringIO()):
            build_site.build(check=True)

    def test_current_build_passes_without_touching_files(self) -> None:
        mtimes = {path: path.stat().st_mtime_ns for path in self.output.rglob("*") if path.is_file()}
        self.check()
        self.external_check.assert_called_once()
        self.assertEqual(mtimes, {path: path.stat().st_mtime_ns for path in self.output.rglob("*") if path.is_file()})

    def test_check_passes_rendered_external_destinations_to_live_validation(self) -> None:
        self.fake_builder.render = lambda: {"en/index.html": '<a href="https://example.org/reference#section">Reference</a>'}
        with redirect_stdout(StringIO()):
            build_site.build()
        self.external_check.assert_not_called()
        self.check()
        self.external_check.assert_called_once_with(
            {"https://example.org/reference": {"en/index.html"}}, community_url=build_site.COMMUNITY_URL)

    def test_offline_check_explicitly_reports_skipped_external_validation(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            build_site.build(check=True, offline=True)
        self.external_check.assert_not_called()
        self.assertIn("External URLs not checked (--offline)", output.getvalue())

    def test_broken_or_unverified_external_urls_fail_the_check(self) -> None:
        for status in ("broken", "unverified"):
            with self.subTest(status=status):
                self.external_check.return_value = [SimpleNamespace(
                    url="https://example.org/reference", status=status,
                    detail="HTTP response could not establish availability", locations=("en/index.html",))]
                output = StringIO()
                with redirect_stdout(output), self.assertRaisesRegex(ValueError, "External URL validation incomplete"):
                    build_site.build(check=True)
                self.assertIn(status.upper(), output.getvalue())
                self.assertIn("en/index.html", output.getvalue())

    def test_available_redirects_are_reported_without_failing_the_check(self) -> None:
        self.external_check.return_value = [SimpleNamespace(
            url="https://doi.org/example", status="redirected",
            detail="Available at https://example.org/paper", locations=("en/index.html",))]
        output = StringIO()
        with redirect_stdout(output):
            build_site.build(check=True)
        self.assertIn("1 redirected", output.getvalue())

    def test_stale_stylesheet_is_rejected(self) -> None:
        self.write("source/theme/styles/site.css", "body {color: green;}\n")
        with self.assertRaises(ValueError):
            self.check()
        self.external_check.assert_not_called()

    def test_landing_assets_are_copied_exactly_and_checked_for_staleness(self) -> None:
        relative = "web/icons/tx-station.svg"
        source = self.source / "assets/landing/originals/icons/neon/tx-station.svg"
        published = self.output / "assets/landing" / relative
        self.assertEqual(published.read_bytes(), source.read_bytes())
        source.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding="utf-8")
        self.fake_builder.landing_payload[relative] = source.read_bytes()
        with self.assertRaisesRegex(ValueError, "Missing or stale built file"):
            self.check()
        self.external_check.assert_not_called()

    def test_modified_copied_content_is_rejected(self) -> None:
        self.write("generated/content/manual.en.md", "Tampered published manual\n")
        with self.assertRaises(ValueError):
            self.check()

    def test_demo_supplement_is_copied_exactly_and_checked_for_staleness(self) -> None:
        published = self.output / "assets/demos/reference/report.pdf"
        self.assertEqual(published.read_bytes(), self.pdf)
        self.assertFalse((self.output / "assets/demos/manifest.json").exists())
        published.write_bytes(b"%PDF-1.7\ntampered output")
        with self.assertRaisesRegex(ValueError, "Missing or stale built file: assets/demos/reference/report.pdf"):
            self.check()
        self.external_check.assert_not_called()

    def test_demo_resources_cannot_overwrite_supplement_routes(self) -> None:
        with patch.object(build_site, "resource_files", return_value={
                "assets/demos/reference/report.pdf": b"different resource"}):
            with self.assertRaisesRegex(ValueError, "Duplicate demo supplement output"):
                build_site.output_files(self.fake_builder)

    def test_legacy_logo_keeps_its_public_img_route(self) -> None:
        source = self.source / "assets" / "brand" / "WSPRadar-2x1.png"
        published = self.output / "img" / "WSPRadar-2x1.png"
        self.assertEqual(published.read_bytes(), source.read_bytes())

    def test_obsolete_html_page_is_rejected(self) -> None:
        self.write("generated/en/obsolete/index.html", "<main>Obsolete public page</main>")
        with self.assertRaises(ValueError):
            self.check()


class PrintImageLoadingTests(unittest.TestCase):
    def test_only_actual_image_loading_attributes_change(self):
        source = """<p>Unchanged &amp; text</p>
<img alt="A > B" loading='lazy' decoding="async" src="plot.png">
<IMG LOADING=LAZY src='other.png'/>
<script>const example = '<img loading="lazy">';</script>
<textarea><img loading="lazy"></textarea>
<img loading="eager" src="ready.png"><div loading="lazy">Keep</div>"""
        expected = source.replace("loading='lazy'", 'loading="eager"').replace('LOADING=LAZY', 'loading="eager"')
        self.assertEqual(build_site.load_print_images_with_page(source), expected)
        self.assertEqual(build_site.load_print_images_with_page(expected), expected)

    def test_every_rendered_page_loads_figures_before_native_print(self):
        for route, html in build_site.SiteBuilder().render().items():
            with self.subTest(route=route):
                inventory = build_site.LinkInventory()
                inventory.feed(html)
                self.assertTrue(inventory.images)
                self.assertFalse(any(image.get("loading") == "lazy" for image in inventory.images))


if __name__ == "__main__":
    unittest.main()
