"""Focused static-site contracts, independent of the Streamlit application."""

from __future__ import annotations

from collections import Counter
from contextlib import redirect_stdout
from copy import deepcopy
import hashlib
from html import escape, unescape
from html.parser import HTMLParser
from io import StringIO
import json
from pathlib import Path
import re
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, unquote, urljoin, urlsplit

from scripts import build_site


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


class ManualRenderingTests(unittest.TestCase):
    """Keep chapter links and continuous-reader links faithful to their context."""

    def test_partition_preserves_all_source_text_and_compatibility_anchors(self) -> None:
        source = '\n---\n\n<a id="preface"></a>\n### 0. Introduction\n\nOpening  spaces.\n\n<a id="part-one"></a>\n## Part I\n\n<a id="legacy-one"></a>\n<a id="chapter-one"></a>\n### 1. First chapter\n\nComplete final text.\n'
        sections = build_site.split_manual(source)
        self.assertEqual("".join(section.text for section in sections), source)
        self.assertEqual([section.key for section in sections], ["preface", "part-one", "legacy-one"])
        self.assertEqual(sections[-1].anchors, ("legacy-one", "chapter-one"))
        self.assertIn("Opening  spaces.", sections[0].text)

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

    def test_legacy_application_media_links_use_the_hosted_static_route(self) -> None:
        for suffix in ("example.pdf", "example.pdf?v=2#page=3"):
            with self.subTest(suffix=suffix):
                rendered = build_site.render_markdown(
                    f'[Figure](app/static/reference_figures/{suffix})', "en", {})
                self.assertIn(
                    f'href="https://wspradar.streamlit.app/~/+/app/static/reference_figures/{suffix}"',
                    rendered)
        app_link = '[App](https://wspradar.streamlit.app/?run=1)'
        self.assertIn('href="https://wspradar.streamlit.app/?run=1"',
                      build_site.render_markdown(app_link, "en", {}))

    def test_scientific_tables_keep_all_cells_in_an_accessible_scroll_region(self) -> None:
        rendered = build_site.render_markdown('| Station | ΔSNR |\n|---|---|\n| DL1MKS | −2 dB |', "de", {})
        self.assertIn('role="region"', rendered)
        self.assertIn('aria-label="Scrollbare Tabelle"', rendered)
        self.assertIn("DL1MKS", rendered)
        self.assertIn("−2 dB", rendered)
        self.assertEqual(rendered.count("<table>"), 1)
        self.assertEqual(rendered.count("</table></div>"), 1)

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
        source_site = build_site.SITE
        self.site = self.root / "site"
        for relative in (
            "page.html", "landing.json", "demo_walkthroughs.json", "print.css", "print.js",
            "assets/landing/manifest.json",
        ):
            self.write("site/" + relative, (source_site / relative).read_bytes())
        self.stylesheet = self.write("site/landing.css", ".result-crop {color: #111111;}\n")
        site_patch = patch.object(build_site, "SITE", self.site)
        site_patch.start()
        self.addCleanup(site_patch.stop)

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

    def test_full_manual_partition_preserves_both_canonical_inputs(self) -> None:
        for language in ("en", "de"):
            with self.subTest(language=language):
                manual = self.builder.manuals[language]
                self.assertEqual("".join(section.text for section in self.builder.sections[language]), manual)
                original_ids = Counter(re.findall(r'<a\s+id="([^"]+)"', manual))
                partition_ids = Counter(anchor for section in self.builder.sections[language] for anchor in section.anchors)
                self.assertEqual(original_ids, partition_ids)

    def test_manual_index_preserves_chapter_links_and_featured_intro_in_four_part_groups(self) -> None:
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
                self.assertEqual(len(groups), 4)
                for group in groups:
                    self.assertIn("<h3><a ", group)
                    self.assertIn("<ul>", group)
                self.assertNotIn('class="manual-introduction"', rendered)
                self.assertLess(rendered.index('class="manual-start"'), rendered.index('class="manual-index"'))
                self.assertGreater(rendered.index('class="manual-supplementary"'), rendered.index('class="manual-index"'))
                references = next(section for section in self.builder.sections[language] if "sec-ref" in section.anchors)
                self.assertIn(build_site.chapter_url(language, references.key), groups[2])
                self.assertNotIn("sec-disclaimer", "".join(groups))
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
                    link for link in expected if link != self.builder.anchors[language]["sec-disclaimer"]))

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
                self.assertEqual(len(switches), 2)
                for alternate, switch in zip(("en", "de"), switches):
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
            expected.update(f"{language}/demos/{demo['id']}/index.html" for demo in self.builder.demos)
            self.assertEqual({path for path in self.pages if path.startswith(language + "/")}, expected)

    def test_every_page_navigation_follows_the_station_workflow(self) -> None:
        suffixes = ("", "demos/", "documentation/", "community/")
        labels = {
            "en": ["Overview", "Demo Walkthrough", "Documentation", "Community"],
            "de": ["Überblick", "Demo-Anleitung", "Dokumentation", "Community"],
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
                                 [f"/{language}/{suffix}" for suffix in suffixes])
                self.assertEqual([anchor["text"] for anchor in inventory.anchors], labels[language])
        for language, page_label in (("en", "Demo walkthrough"), ("de", "Demo-Anleitung")):
            with self.subTest(preserved_demo_page_language=language):
                content = self.pages[f"{language}/demos/index.html"]
                self.assertIn(f'<p class="eyebrow">{page_label}</p>', content)
                self.assertIn(f'<title>{page_label} · WSPRadar</title>', content)

    def test_every_route_has_responsive_english_artwork_and_live_navigation(self) -> None:
        landing = json.loads((build_site.SITE / "landing.json").read_text(encoding="utf-8"))
        assets = json.loads((build_site.SITE / "assets/landing/manifest.json").read_text(encoding="utf-8"))
        hero = assets["hero"]["fallback"]
        logo = assets["logo"]["fallback"]
        for path, content in self.pages.items():
            language = "en" if path == "index.html" else path.split("/", 1)[0]
            with self.subTest(path=path):
                header = re.search(r'<header\b[^>]*class="[^"]*\bsite-header\b[^"]*"[^>]*>(.*?)</header>', content, re.DOTALL)
                self.assertIsNotNone(header)
                inventory = build_site.LinkInventory()
                inventory.feed(header[1])
                self.assertIn("/assets/landing/" + hero["path"], inventory.links)
                self.assertNotIn("/assets/landing/" + logo["path"], inventory.links)
                self.assertEqual([image["alt"] for image in inventory.images
                                  if image["src"] == "/assets/landing/" + hero["path"]], [landing[language]["hero_alt"]])
                self.assertIn('<picture class="radar-artwork" lang="en">', header[1])
                self.assertIn('class="nav-brand"', header[1])
                self.assertIn('aria-label="WSPRadar.org — ' + build_site.COPY[language]["home"] + '"', header[1])
                self.assertIn('<span>WSPRadar.org</span>', header[1])
                self.assertNotIn(self.builder.brand["credit_html"][language], header[1])
                self.assertEqual(len(inventory.images), 1)
                self.assertLess(header[1].index('<nav class="navigation"'), header[1].index('<picture class="radar-artwork"'))
                links = AnchorInventory()
                links.feed(header[1])
                is_home = path in ("index.html", "en/index.html", "de/index.html")
                demo_route = re.fullmatch(r"(?:en|de)/demos/([^/]+)/index.html", path)
                if demo_route:
                    expected_url = self.builder.demo_walkthroughs["demos"][demo_route[1]]["launch_url"]
                    launch_links = [anchor for anchor in links.anchors
                                    if anchor["attributes"]["href"] == expected_url]
                    self.assertEqual(len(launch_links), 1)
                    parameters = parse_qs(urlsplit(launch_links[0]["attributes"]["href"]).query)
                    self.assertEqual(parameters["v"], ["1"])
                    self.assertEqual(parameters["run"], ["1"])
                    self.assertNotIn("demo", parameters)
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

        assets = json.loads((build_site.SITE / "assets/landing/manifest.json").read_text(encoding="utf-8"))
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
            with self.subTest(language=language), patch.dict(self.builder.brand["credit_html"], {language: "Release v2.3 test | Developed by Dr. Markus Brosch"}), patch.dict(self.builder.brand, {"app_version": "v2.3 test"}):
                self.builder.page(language, "credit-contract/", "Credit contract", "<h1>Credit contract</h1>", "docs")
                content = self.builder.pages.pop(f"{language}/credit-contract/index.html")
                footer = re.search(r'<footer\b[^>]*>(.*?)</footer>', content, re.DOTALL)[1]
                header = re.search(r'<header\b[^>]*>(.*?)</header>', content, re.DOTALL)[1]
                self.assertIn("Developed by Dr. Markus Brosch", footer)
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

    def test_every_footer_keeps_release_developer_disclaimer_and_support_destinations(self) -> None:
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
                self.assertIn(f'/{language}/report/', hrefs)
                self.assertIn("https://github.com/markusthemaker/WSPRadar", hrefs)
                self.assertIn('class="footer-main"', footer)
                self.assertIn('class="footer-legal"', footer)
                self.assertTrue(any("DL1MKS" in anchor["text"] for anchor in inventory.anchors))

    def test_introductory_manual_chapter_marks_documentation_current(self) -> None:
        for language, label in (("en", "Documentation"), ("de", "Dokumentation")):
            content = self.pages[f"{language}/documentation/sec-1/index.html"]
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
            self.assertEqual(len(manual_groups), 4)
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
                    self.assertEqual(re.findall(r'<section class="manual-group">(.*?)</section>', main, re.DOTALL), manual_groups)
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
                self.assertEqual(guidance[1].count('class="manual-group"'), 4)
                inventory = build_site.LinkInventory()
                inventory.feed(guidance[1])
                for destination in (
                    f"/{language}/demos/", f"/{language}/community/", f"/{language}/report/",
                    self.builder.anchors[language]["sec-2-2"] + "#sec-2-2",
                    self.builder.anchors[language]["sec-2-1"] + "#sec-2-1", build_site.APP_URL,
                ):
                    self.assertIn(destination, inventory.links)
                self.assertNotIn("<h1", guidance[1])

    def test_landing_presents_demo_first_with_four_equal_analysis_choices(self) -> None:
        section_ids = ("how-it-works", "analysis-choices", "real-example", "get-started", "more-guidance")
        for language in ("en", "de"):
            with self.subTest(language=language):
                content = self.pages[f"{language}/index.html"]
                main = re.search(r'<main id="main">(.*?)</main>', content, re.DOTALL)[1]
                self.assertEqual(len(re.findall(r'<h1\b', content)), 1)
                positions = [main.index(f'id="{section_id}"') for section_id in section_ids]
                self.assertEqual(positions, sorted(positions))
                analysis = main[positions[1]:positions[2]]
                cards = re.findall(r'<article\b[^>]*class="analysis-card"[^>]*>(.*?)</article>', analysis, re.DOTALL)
                self.assertEqual(len(cards), 4)
                self.assertEqual(
                    [unescape(re.search(r'<h3\b[^>]*>(.*?)</h3>', card, re.DOTALL)[1]) for card in cards],
                    ["RX Benchmark", "TX Benchmark", "RX Performance", "TX Performance"],
                )
                for card in cards:
                    self.assertIn("<p", card)
                    self.assertNotIn("<a ", card)
                get_started = main[positions[3]:positions[4]]
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
                inventory = AnchorInventory()
                inventory.feed(actions[1])
                self.assertEqual([anchor["attributes"]["href"] for anchor in inventory.anchors],
                                 [f"/{language}/#real-example", build_site.APP_URL])
                self.assertEqual([anchor["text"] for anchor in inventory.anchors],
                                 [self.builder.landing[language]["try_demo"] + " →", build_site.COPY[language]["open"] + " ↗"])

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
                end = content.index('id="why-wspradar"')
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
        self.assertEqual(set(english), set(german))
        for removed in ("network_caption", "method_note", "median_legend", "summary_legend", "illustrative_note", "illustrative", "setup_a", "setup_b"):
            self.assertNotIn(removed, english)
            self.assertNotIn(removed, german)
        self.assertEqual(english["repeated_title"], "WSPRadar: Many observations, clear insights")
        self.assertEqual(english["repeated_subtitle"], "Consistently compare your setups using matched observations.")
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
                start, end = page.index('id="why-wspradar"'), page.index('id="analysis-choices"')
                self.assertLess(page.index('id="how-it-works"'), start)
                self.assertLess(start, end)
                section = page[start:end]
                copy = self.builder.landing[language]["why"]
                for key, value in copy.items():
                    if isinstance(value, str):
                        self.assertIn(escape(value), section, key)
                self.assertIn('aria-labelledby="why-title"', section)
                self.assertIn('id="why-title"', section)
                self.assertEqual(section.count('<article class="why-panel '), 2)
                setups = re.findall(r'<div class="why-setup (target|reference)"><h4>(.*?)</h4>.*?<strong>(.*?)</strong>', section)
                self.assertEqual(setups, [("target", copy["target_label"], "−17 dB"), ("reference", copy["reference_label"], "−21 dB")])
                self.assertNotIn('class="why-illustrative"', section)
                self.assertEqual(section.count('class="why-step-heading"'), 3)
                self.assertIn("Benchmark", copy["method_title"])
                right_panel = re.search(r'<article class="why-panel why-repeated">(.*?)</article>', section, re.DOTALL)[1]
                self.assertIn('<div class="why-method">', right_panel)
                self.assertEqual(right_panel.count('class="why-step-heading"'), 3)
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
                table_stations = re.findall(r'<th scope="row">(#\d)</th>', section)
                median_stations = re.findall(r'<div><span>(#\d)</span><span class="why-dot-row">', section)
                self.assertEqual(table_stations, ["#1", "#2", "#3"])
                self.assertEqual(table_stations, median_stations)
                rows = re.findall(r'<tr><th scope="row">#\d</th><td>(−\d+) dB</td><td>(−\d+) dB</td><td>(\+\d+) dB</td></tr>', section)
                self.assertEqual(len(rows), 3)
                for reference, target, delta in rows:
                    self.assertEqual(int(target.replace("−", "-")) - int(reference.replace("−", "-")), int(delta))

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
                section = page[page.index('id="why-wspradar"'):page.index('id="analysis-choices"')]
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

    def test_landing_copy_and_scientific_qualifications_have_bilingual_parity(self) -> None:
        landing = json.loads((build_site.SITE / "landing.json").read_text(encoding="utf-8"))
        self.assertEqual(set(landing["en"]), set(landing["de"]))
        for collection in ("flow", "modes"):
            self.assertEqual(len(landing["en"][collection]), len(landing["de"][collection]))
            for english, german in zip(landing["en"][collection], landing["de"][collection]):
                self.assertEqual(set(english), set(german))
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
                for key in ("example_title", "example_intro", "example_meta", "example_question", "result", "result_label", "example_ready"):
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
        self.assertEqual(self.builder.landing["en"]["example_meta"],
                         "Follow two receiving setups on 40 m, comparing the same transmissions. Discover where one setup led, how the advantage changed, and what the observations actually support.")
        self.assertEqual(self.builder.landing["en"]["example_question"],
                         "Low dipole or vertical—which setup heard better?")
        self.assertEqual(self.builder.landing["en"]["result_label"], "SNR advantage for the low-dipole setup")
        self.assertEqual(self.builder.landing["de"]["result_label"], "SNR-Vorteil der Anlage mit niedrigem Dipol")
        self.assertEqual(self.builder.landing["en"]["result_detail"], ["57 767 paired observations", "792 transmitting-station entries"])
        self.assertEqual(self.builder.landing["en"]["example_tag"], "GUIDED WALKTHROUGH · 40 m RX BENCHMARK")
        self.assertEqual(self.builder.landing["en"]["example_ready"], "The example is ready to explore. No need to enter your own data.")
        self.assertEqual(self.builder.landing["en"]["example_link"], "Start walkthrough")
        self.assertEqual(self.builder.landing["en"]["try_this"], "Run this demo")
        self.assertEqual(self.builder.landing["de"]["example_link"], "Rundgang starten")
        self.assertEqual(self.builder.landing["de"]["try_this"], "Diese Demo starten")
        selected = self.builder.landing["featured_demo"]
        selected_config = self.builder.demo_walkthroughs["demos"][selected["id"]]
        for language in ("en", "de"):
            with self.subTest(language=language):
                content = self.pages[f"{language}/index.html"]
                section = re.search(r'<section id="real-example"[^>]*>(.*?)</section>', content, re.DOTALL).group(1)
                copy = self.builder.landing[language]
                introduction, showcase = section.split('<div class="example-showcase">', 1)
                self.assertIn('<h2>' + escape(copy["example_title"]) + '</h2>', introduction)
                self.assertIn('<strong>' + escape(copy["example_intro"]) + '</strong>', introduction)
                self.assertIn('<p class="example-meta">' + escape(copy["example_meta"]) + '</p>', introduction)
                self.assertLess(introduction.index(escape(copy["example_title"])), introduction.index(escape(copy["example_intro"])))
                self.assertLess(introduction.index(escape(copy["example_intro"])), introduction.index(escape(copy["example_meta"])))
                context = showcase.split('<div class="result-gallery">', 1)[0]
                self.assertIn('class="example-context"', context)
                self.assertIn('class="measured-result"', context)
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
                self.assertEqual(links.anchors[1]["attributes"]["target"], "_blank")
                self.assertEqual(set(links.anchors[1]["attributes"]["rel"].split()), {"noopener", "noreferrer"})
                self.assertNotIn('class="example-notes"', section)
                self.assertNotRegex(" ".join(copy["result_detail"]), r"10[,. ]?000\s*km")
                self.assertNotIn("example_source", copy)
                self.assertNotIn("example_source_link", copy)
                self.assertNotIn('class="example-source"', section)
                self.assertNotIn('id="demo-source-note"', section)
                self.assertNotIn('aria-describedby="demo-source-note"', section)

    def test_landing_example_crops_declared_real_capture_media_with_full_size_links(self) -> None:
        selected = self.builder.landing["featured_demo"]
        self.assertEqual(self.builder.landing["en"]["image_titles"], ["Where?", "How much?", "When?", "Who?"])
        self.assertEqual(self.builder.landing["de"]["image_titles"], ["Wo?", "Wie viel?", "Wann?", "Wer?"])
        self.assertEqual(self.builder.landing["en"]["image_captions"][1]["body"],
                         "See how typical SNR differences vary across transmitting stations.")
        self.assertEqual(self.builder.landing["de"]["image_captions"][1]["body"],
                         "Sieh, wie typische SNR-Differenzen zwischen Sendestationen variieren.")
        self.assertEqual(self.builder.landing["en"]["image_captions"][3]["body"],
                         "Check how many stations and observations support the trend.")
        self.assertEqual(self.builder.landing["de"]["image_captions"][3]["body"],
                         "Prüfe, wie viele Stationen und Beobachtungen den Trend stützen.")
        media = {item["key"]: item for item in self.builder.figures + self.builder.screenshots}
        captures = {item["key"]: item for item in self.builder.screenshots}
        self.assertEqual(len(selected["media_keys"]), 4)
        self.assertEqual(len(set(selected["media_keys"])), 4)
        for key in selected["media_keys"]:
            item = media[key]
            with self.subTest(media=key):
                self.assertEqual(item["demo_id"], selected["id"])
                provenance = item["provenance"]
                self.assertEqual(provenance["kind"], "actual-app-screenshot-figure-crop")
                capture = captures[provenance["source_capture_key"]]
                self.assertEqual(capture["demo_id"], selected["id"])
                actual_source_hash = hashlib.sha256((self.builder.content / capture["asset_path"]).read_bytes()).hexdigest()
                self.assertEqual(provenance["source_capture_sha256"], actual_source_hash)
                self.assertEqual(provenance["source_capture_provenance"], capture["provenance"])
                crop = selected["media_crops"][key]
                self.assertEqual(crop["source_size"], [item["width"], item["height"]])
                source_hash = hashlib.sha256((self.builder.content / item["asset_path"]).read_bytes()).hexdigest()
                self.assertEqual(crop["source_sha256"], source_hash)
                self.assertIn(crop["layout"], ("rows", "columns"))
                self.assertTrue(crop["regions"])
                for region in crop["regions"]:
                    x, y, width, height = region["rect"]
                    self.assertTrue(all(type(value) is int for value in region["rect"]))
                    self.assertGreaterEqual(x, 0)
                    self.assertGreaterEqual(y, 0)
                    self.assertGreater(width, 0)
                    self.assertGreater(height, 0)
                    self.assertLessEqual(x + width, item["width"])
                    self.assertLessEqual(y + height, item["height"])
                    self.assertEqual(set(region["alt"]), {"en", "de"})
        for language in ("en", "de"):
            with self.subTest(language=language):
                content = self.pages[f"{language}/index.html"]
                previews = re.findall(r'<figure class="result-preview">(.*?)</figure>', content, re.DOTALL)
                self.assertEqual(len(previews), 4)
                for index, (key, preview) in enumerate(zip(selected["media_keys"], previews)):
                    item = media[key]
                    crop = selected["media_crops"][key]
                    inventory = build_site.LinkInventory()
                    inventory.feed(preview)
                    evidence_images = [image for image in inventory.images if image["src"].startswith("/content/")]
                    self.assertEqual(len(evidence_images), len(crop["regions"]))
                    self.assertIn('class="result-crops result-crops-' + crop["layout"] + '"', preview)
                    self.assertEqual(preview.count('class="result-crop"'), len(crop["regions"]))
                    for image, region in zip(evidence_images, crop["regions"]):
                        self.assertEqual(image["src"], "/content/" + item["asset_path"])
                        self.assertEqual(image["alt"], region["alt"][language])
                        self.assertTrue(image["alt"])
                        self.assertEqual(image["loading"], "eager")
                        self.assertEqual((image["width"], image["height"]), (str(item["width"]), str(item["height"])))
                    links = AnchorInventory()
                    links.feed(preview)
                    self.assertEqual(len(links.anchors), 1)
                    self.assertEqual(links.anchors[0]["attributes"]["href"], "/content/" + item["asset_path"])
                    self.assertTrue(links.anchors[0]["attributes"].get("aria-label"))
                    heading = '<h4>' + escape(self.builder.landing[language]["image_titles"][index]) + '</h4>'
                    self.assertIn(heading, preview)
                    self.assertLess(preview.index(heading), preview.index('<a '))
                    self.assertLess(preview.index('</a>'), preview.index('<figcaption>'))
                    caption = self.builder.landing[language]["image_captions"][index]
                    self.assertIn('<figcaption><strong>' + escape(caption["lead"]) + '</strong> ' + escape(caption["body"]) + '</figcaption>', preview)
                    icons = [image for image in inventory.images if not image["src"].startswith("/content/")]
                    self.assertEqual(len(icons), 1)
                    declared_icons = self.builder.landing_assets["icons"].values()
                    self.assertIn(icons[0]["src"], {"/assets/landing/" + (icon["path"] if isinstance(icon, dict) else icon) for icon in declared_icons})
                    self.assertEqual(icons[0]["alt"], "")
                    self.assertEqual(icons[0]["aria-hidden"], "true")
                self.assertIn(f'/{language}/demos/{selected["id"]}/', content)

    def test_landing_rejects_evidence_from_a_different_demo(self) -> None:
        selected = self.builder.landing["featured_demo"]
        item = next(item for item in self.builder.figures if item["key"] == selected["media_keys"][0])
        with patch.dict(item, {"demo_id": "different-experiment"}):
            with self.assertRaisesRegex(ValueError, "Landing media must belong to the featured demo"):
                self.builder.home("en")

    def test_landing_rejects_crop_config_for_a_changed_source(self) -> None:
        selected = self.builder.landing["featured_demo"]
        key = selected["media_keys"][0]
        crop = selected["media_crops"][key]
        changes = (
            {"source_size": [crop["source_size"][0] + 1, crop["source_size"][1]]},
            {"source_sha256": "0" * 64},
        )
        for change in changes:
            with self.subTest(change=change):
                configured = deepcopy(selected["media_crops"])
                configured[key].update(change)
                with patch.dict(selected, {"media_crops": configured}):
                    with self.assertRaisesRegex(ValueError, "Landing crop"):
                        self.builder.home("en")

    def test_landing_rejects_invalid_crop_layout_and_rectangles(self) -> None:
        selected = self.builder.landing["featured_demo"]
        key = selected["media_keys"][0]
        width, height = selected["media_crops"][key]["source_size"]
        invalid_rectangles = (
            [-1, 0, 10, 10], [0, -1, 10, 10],
            [0, 0, 0, 10], [0, 0, 10, 0],
            [width - 5, 0, 10, 10], [0, height - 5, 10, 10],
            [0.5, 0, 10, 10], [False, 0, 10, 10],
            ["0", 0, 10, 10], [0, 0, 10],
        )
        for rectangle in invalid_rectangles:
            with self.subTest(rectangle=rectangle):
                configured = deepcopy(selected["media_crops"])
                configured[key]["regions"][0]["rect"] = rectangle
                with patch.dict(selected, {"media_crops": configured}):
                    with self.assertRaisesRegex(ValueError, "Landing crop"):
                        self.builder.home("en")
        configured = deepcopy(selected["media_crops"])
        configured[key]["layout"] = "diagonal"
        with patch.dict(selected, {"media_crops": configured}):
            with self.assertRaisesRegex(ValueError, "Landing crop"):
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
                launch_url = self.builder.demo_walkthroughs["demos"][demo_route[1]]["launch_url"]
                expected_labels[launch_url] = {"Run in WSPRadar App" if language == "en" else "In WSPRadar App starten"}
            if path in ("index.html", f"{language}/index.html"):
                selected = self.builder.landing["featured_demo"]
                launch_url = self.builder.demo_walkthroughs["demos"][selected["id"]]["launch_url"]
                expected_labels[launch_url] = {self.builder.landing[language]["try_this"]}
                expected_labels[build_site.APP_URL].add(self.builder.landing[language]["own_link"])
            buttons = [anchor for anchor in inventory.anchors
                       if anchor["attributes"].get("href") in expected_labels
                       and "button" in anchor["attributes"].get("class", "").split()]
            with self.subTest(path=path):
                self.assertTrue(buttons)
                if path in ("index.html", f"{language}/index.html"):
                    self.assertEqual(sum(anchor["attributes"]["href"] == launch_url for anchor in buttons), 1)
                for anchor in buttons:
                    self.assertIn(anchor["text"].removesuffix(" ↗"), expected_labels[anchor["attributes"]["href"]])

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
        for language in ("en", "de"):
            for media in [*self.builder.figures, *self.builder.screenshots]:
                with self.subTest(language=language, media=media["key"]):
                    html = self.pages[f"{language}/demos/{media['demo_id']}/index.html"]
                    inventory = build_site.LinkInventory()
                    inventory.feed(html)
                    matching = [image for image in inventory.images if image.get("src") == "/content/" + media["asset_path"]]
                    config = self.builder.demo_walkthroughs["demos"][media["demo_id"]]
                    excluded = config.get("excluded_media_keys", [])
                    placed = {config.get("setup_media_key")} - {None}
                    sections = list(config["sections"])
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
        for language in ("en", "de"):
            inventory = GuideInventory()
            inventory.feed(self.pages[f"{language}/guides/read-results/index.html"])
            for section, stage in expected_stages.items():
                with self.subTest(language=language, section=section):
                    captures = [item for item in self.builder.screenshots if item.get("stage") == stage]
                    self.assertTrue(captures, f"No reviewed live capture for {stage}")
                    self.assertEqual(inventory.images.get(section), ["/content/" + captures[0]["asset_path"]])


class StaleBuildCheckTests(TemporarySiteTests):
    """A successful --check must certify the built assets and page inventory too."""

    def setUp(self) -> None:
        super().setUp()
        self.site = self.root / "site"
        self.content = self.root / "content"
        self.output = self.root / "dist"
        self.write("site/site.css", "body {color: white;}\n")
        self.write("site/landing.css", ".landing {color: white;}\n")
        self.write("site/print.css", "@media print {body {color: black;}}\n")
        self.write("site/print.js", "'use strict';\n")
        self.write("site/site.js", "'use strict';\n")
        self.write("site/entry.js", "'use strict';\n")
        self.write("site/demo-walkthrough.css", ".case-study {color: white;}\n")
        self.write("site/demo-walkthrough.js", "'use strict';\n")
        self.write("site/assets/landing/web/icons/tx-station.svg", '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2v20"/></svg>')
        self.write("content/manual.en.md", "Original manual\n")
        source_bytes = (self.content / "manual.en.md").read_bytes()
        manifest = {"schema_version": 1, "app_version": "test", "source_revision": "a" * 40,
                    "source_dirty": False, "files": {"manual.en.md": {
                        "bytes": len(source_bytes), "sha256": hashlib.sha256(source_bytes).hexdigest()}}}
        self.write("content/manifest.json", json.dumps(manifest))
        self.fake_builder = SimpleNamespace(
            brand={"fonts": []}, demos=[{"id": "example"}], figures=[], screenshots=[],
            landing_assets={"publish_files": ["web/icons/tx-station.svg"]},
            manifest=manifest, content=self.content,
            demo_root=self.site / "demos", demo_walkthroughs={"demos": {}},
            render=lambda: {"en/index.html": '<main id="main">Current page</main>'},
        )
        for name, value in (("SITE", self.site), ("CONTENT", self.content), ("OUTPUT", self.output)):
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
        self.write("site/site.css", "body {color: green;}\n")
        with self.assertRaises(ValueError):
            self.check()
        self.external_check.assert_not_called()

    def test_landing_assets_are_copied_exactly_and_checked_for_staleness(self) -> None:
        relative = "web/icons/tx-station.svg"
        source = self.site / "assets/landing" / relative
        published = self.output / "assets/landing" / relative
        self.assertEqual(published.read_bytes(), source.read_bytes())
        source.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Missing or stale built file"):
            self.check()
        self.external_check.assert_not_called()

    def test_modified_copied_content_is_rejected(self) -> None:
        self.write("dist/content/manual.en.md", "Tampered published manual\n")
        with self.assertRaises(ValueError):
            self.check()

    def test_obsolete_html_page_is_rejected(self) -> None:
        self.write("dist/en/obsolete/index.html", "<main>Obsolete public page</main>")
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
