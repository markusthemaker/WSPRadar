"""Contracts for editable Markdown walkthroughs and retained scientific content."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from dataclasses import dataclass, field
from html import escape
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from scripts import build_site, demo_walkthrough
from scripts.demo_walkthrough import read_sections, render_demo, resource_files, safe_path


DEMO_ONE_LAUNCH_URL = (
    "https://wspradar.org/?v=1&run=1&direction=rx&callsign=G3ZIL&qth=IO90HW&band=40m"
    "&from=2017-04-01T00%3A00Z&to=2017-05-01T00%3A00Z&mode=benchmark"
    "&benchmark_design=reference_station&reference=G4HZX&reference_qth=IO91"
    "&snr_correction_mode=no_offset&snr_correction_db=0&max_distance_km=10000"
    "&segment_bin=24h&station_bin=12h&selected_station=DJ0ABR%40JN68NT"
    "#wspradar-results-inspection"
)


@dataclass
class Element:
    tag: str
    attributes: dict[str, str | None]
    children: list["Element | str"] = field(default_factory=list)

    @property
    def text(self) -> str:
        return "".join(child.text if isinstance(child, Element) else child for child in self.children)

    def descendants(self, tag: str | None = None) -> list["Element"]:
        result = []
        for child in self.children:
            if isinstance(child, Element):
                if tag is None or child.tag == tag:
                    result.append(child)
                result.extend(child.descendants(tag))
        return result


class Document(HTMLParser):
    """Small semantic inventory; assertions do not depend on attribute order."""

    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self, source: str) -> None:
        super().__init__()
        self.root = Element("document", {})
        self.stack = [self.root]
        self.feed(source)

    def handle_starttag(self, tag, attributes) -> None:
        element = Element(tag, dict(attributes))
        self.stack[-1].children.append(element)
        if tag not in self.VOID:
            self.stack.append(element)

    def handle_startendtag(self, tag, attributes) -> None:
        self.stack[-1].children.append(Element(tag, dict(attributes)))

    def handle_endtag(self, tag) -> None:
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data) -> None:
        self.stack[-1].children.append(data)

    def find(self, *, tag=None, css_class=None, identity=None) -> list[Element]:
        return [element for element in self.root.descendants(tag)
                if (css_class is None or css_class in (element.attributes.get("class") or "").split())
                and (identity is None or element.attributes.get("id") == identity)]


class DemoWalkthroughTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = build_site.SiteBuilder()
        cls.pages = cls.builder.render()
        cls.demo_id = "griffiths_squibb_fig3"
        cls.demo = next(demo for demo in cls.builder.demos if demo["id"] == cls.demo_id)
        cls.configurations = cls.builder.demo_walkthroughs["demos"]

    def page(self, identity: str, language: str) -> str:
        return self.pages[f"{language}/demos/{identity}/index.html"]

    def cases(self):
        for demo in self.builder.published_demos:
            for language in ("en", "de"):
                yield demo, language, self.page(demo["id"], language)

    def explicitly_placed_media(self, identity, language):
        config = self.configurations[identity]
        return {config.get("setup_media_key"),
                *(key for section in self.configured_sections(demo_walkthrough.demo_sections(config, language))
                  if section.get("layout") != "full" for key in section.get("media_keys", []))} - {None}

    def imported_media(self, identity, language):
        config = self.configurations[identity]
        excluded = set(config.get("excluded_media_keys", []))
        placed = self.explicitly_placed_media(identity, language)
        return [item for item in [*self.builder.figures, *self.builder.screenshots]
                if item["demo_id"] == identity and item["key"] not in excluded
                and item["key"] in placed]

    def resource_media(self, identity, language):
        config = self.configurations[identity]
        if not config.get("resource_manifest"):
            return []
        path = safe_path(self.builder.demo_asset_root, config["resource_manifest"])
        excluded = set(config.get("excluded_media_keys", []))
        placed = self.explicitly_placed_media(identity, language)
        return [item for item in json.loads(path.read_text(encoding="utf-8")).get("figures", [])
                if item["key"] not in excluded
                and item["key"] in placed]

    def configured_sections(self, sections):
        for section in sections:
            yield section
            yield from self.configured_sections(section.get("subsections", []))

    def test_all_published_demos_use_shared_layout_and_bilingual_markdown(self) -> None:
        self.assertEqual(len(self.builder.published_demos), 6)
        self.assertEqual(set(self.configurations), {demo["id"] for demo in self.builder.published_demos})
        for demo, language, page in self.cases():
            with self.subTest(demo=demo["id"], language=language):
                config = self.configurations[demo["id"]]
                self.assertEqual(set(config["markdown_paths"]), {"en", "de"})
                sections = read_sections(safe_path(self.builder.demo_root, config["markdown_paths"][language]))
                self.assertTrue({"hero", "setup", *(item["id"] for item in self.configured_sections(demo_walkthrough.demo_sections(config, language)))}.issubset(sections))
                document = Document(page)
                self.assertEqual(len(document.find(css_class="case-study")), 1)
                self.assertEqual(len(document.find(css_class="case-hero")), 1)
                self.assertIn('class="demo-case-page"', page)
                self.assertIn('/assets/demo-walkthrough.css', page)
                self.assertIn('/assets/demo-walkthrough.js', page)

    def test_demo_index_and_routes_exclude_retired_guided_pages(self) -> None:
        published_ids = ["griffiths_squibb_fig3", "griffiths_squibb_rx_performance", "vanhamel_rx_calibration",
                         "vanhamel_rx_buddy", "zander_tx_buddy", "milazzo_tx_buddy"]
        retired_ids = {"griffiths_squibb_fig6"}
        self.assertEqual([demo["id"] for demo in self.builder.published_demos], published_ids)
        self.assertEqual(len(self.builder.demos), 7)
        self.assertTrue(retired_ids.issubset(self.builder.demo_by_id))
        for language in ("en", "de"):
            with self.subTest(language=language):
                document = Document(self.pages[f"{language}/demos/index.html"])
                cards = document.find(css_class="demo-card")
                card_order = ([card["id"] for card in self.builder.demos_index[language]["cards"]]
                              if language in self.builder.demos_index else published_ids)
                self.assertEqual([anchor.attributes["href"] for card in cards
                                  for anchor in card.descendants("a")
                                  if not anchor.attributes["href"].startswith("/assets/demos/")],
                                 [f"/{language}/demos/{identity}/" for identity in card_order])
                if language in self.builder.demos_index:
                    self.assertEqual([node.text for node in document.find(identity="demo-count")], ["6 guided demos"])
                else:
                    status = [node for node in document.find(tag="p")
                              if "data-filter-status" in node.attributes]
                    self.assertEqual([node.text for node in status], ["6 / 6"])
                for identity in retired_ids:
                    self.assertNotIn(f"{language}/demos/{identity}/index.html", self.pages)

    def test_english_discovery_components_are_scoped_to_index(self) -> None:
        for path, page in self.pages.items():
            with self.subTest(path=path):
                expected = path == "en/demos/index.html"
                self.assertEqual('/assets/demos-index.css?v=' in page, expected)
                self.assertEqual('/assets/demos-index.js?v=' in page, expected)
                self.assertEqual('class="demos-landing"' in page, expected)
        english = Document(self.pages["en/demos/index.html"])
        controls = [node for node in english.find() if "data-demo-controls" in node.attributes]
        self.assertTrue(controls)
        self.assertTrue(all("hidden" in node.attributes for node in controls))
        cards = english.find(css_class="demo-card")
        self.assertEqual(len(cards), 6)
        self.assertTrue(all("hidden" not in card.attributes for card in cards))
        self.assertEqual(len(english.find(css_class="placeholder-label")), 0)
        self.assertEqual(len(english.find(css_class="evidence-thumbnail")), 6)
        self.assertEqual(len(english.find(css_class="card-subtitle")), 6)
        self.assertNotIn("data-filter-input", self.pages["en/demos/index.html"])
        self.assertNotIn("data-demo-search", self.pages["en/demos/index.html"])
        self.assertNotIn("Find a demo by name, station, or topic", self.pages["en/demos/index.html"])
        self.assertIn("data-filter-input", self.pages["de/demos/index.html"])

    def test_rx_performance_route_retains_complete_guide_and_canonical_run(self) -> None:
        identity = "griffiths_squibb_rx_performance"
        demo = self.builder.demo_by_id[identity]
        config = self.configurations[identity]
        expected_blocks = {
            "hero", "summary", "setup", "load-demo", "performance-map",
            "performance-evidence", "snr-deviation", "temporal-evidence", "stations",
            "selected-station-snr", "selected-station-evidence", "drill-down", "takeaways",
        }
        expected_figures = {
            "rx-performance-" + suffix for suffix in (
                "performance-map", "performance-evidence", "snr-deviation",
                "temporal-evidence", "selected-station-snr", "selected-station-evidence",
            )
        }
        benchmark_keys = {
            "reference", "benchmark_design", "reference_snr_correction",
            "min_spot_pairs_per_station", "min_decode_event_share_percent",
            "delta_snr_outlier_reporting",
        }
        expected_launch = demo_walkthrough.demo_launch_url(demo)
        query = parse_qs(urlsplit(expected_launch).query)
        self.assertEqual(query["mode"], ["performance"])
        self.assertEqual(demo["settings"]["advanced_parameters"]["max_peer_distance_km"], 22000)
        self.assertEqual(query["direction"], ["rx"])
        self.assertEqual(query["selected_station"], ["HB0QRP@JN47"])
        self.assertEqual(query["segment_bin"], ["12h"])
        self.assertEqual(query["station_bin"], ["12h"])
        self.assertTrue((benchmark_keys | {"reference_qth", "snr_correction_mode",
                                         "snr_correction_db", "min_spot_pairs"}).isdisjoint(query))
        self.assertEqual(demo["settings"]["comparison_parameters"], {"mode": "none"})
        resources = resource_files(self.builder.demo_asset_root, {identity: config},
                                   source_root=build_site.SOURCE)
        evidence_paths = {
            f"/assets/demos/{identity}/source/original_export.zip",
            f"/assets/demos/{identity}/evidence/verified_claims.md",
        }
        documentation = "/en/documentation/full/#sec-3-rx-performance"
        documentation_target = Document(self.pages["en/documentation/full/index.html"])
        self.assertEqual(len(documentation_target.find(identity="sec-3-rx-performance")), 1)
        summary = {row["key"]: row for row in demo["settings_summary"]}
        self.assertTrue(benchmark_keys.isdisjoint(summary))
        for language in ("en", "de"):
            with self.subTest(language=language):
                source = safe_path(self.builder.demo_root, config["markdown_paths"][language])
                self.assertEqual(set(read_sections(source)), expected_blocks)
                page = self.page(identity, language)
                document = Document(page)
                self.assertIsNone(re.search(r"\{\{\s*[a-z_][a-z_0-9]*\s*\}\}", page))
                self.assertEqual(document.find(css_class="case-placeholder"), [])
                figures = document.find(css_class="case-figure")
                self.assertEqual(Counter(figure.attributes["id"] for figure in figures),
                                 Counter("case-media-" + key for key in expected_figures))
                links = {node.attributes.get("href") for node in document.find(tag="a")}
                self.assertIn(expected_launch, links)
                self.assertEqual((evidence_paths | {documentation}) - links, set())
                for destination in evidence_paths:
                    self.assertIn(destination.lstrip("/"), resources)
                    self.assertTrue(resources[destination.lstrip("/")])
                selections = config["settings_tables"][language]["rows"]
                self.assertTrue(benchmark_keys.isdisjoint(row["key"] for row in selections))
                table = document.find(identity="load-demo")[0].descendants("table")[0]
                rows = table.descendants("tr")[1:]
                self.assertEqual(len(rows), len(selections))
                for actual, selected in zip(rows, selections):
                    canonical = summary[selected["key"]]
                    self.assertEqual([cell.text for cell in actual.descendants("td")][:2],
                                     [canonical["label"][language], canonical["value"][language]])

    def test_demo_one_keeps_figure_six_paper_evidence_after_retirement(self) -> None:
        pdf = "/assets/demos/griffiths_fig6_paper_v1/WSPRadar_Demo_Griffiths_Figure6.pdf"
        self.assertIn(pdf.lstrip("/"), build_site.demo_supplement_files(build_site.DEMO_SUPPLEMENTS))
        document = Document(self.page(self.demo_id, "en"))
        links = [node.attributes for node in document.find(tag="a")
                 if node.attributes.get("href") == pdf]
        self.assertTrue(links)
        for attributes in links:
            self.assertEqual(attributes.get("target"), "_blank")
            self.assertTrue({"noopener", "noreferrer"}.issubset(attributes.get("rel", "").split()))

    def test_demo_one_keeps_the_user_approved_english_hero(self) -> None:
        document = Document(self.page(self.demo_id, "en"))
        hero = document.find(css_class="case-hero")[0]
        self.assertEqual([node.text for node in hero.descendants("h1")],
                         ["Low Dipole vs Radial-Free Vertical"])
        self.assertEqual(document.find(css_class="eyebrow")[0].text, "Guided Demo")
        self.assertEqual(document.find(css_class="case-meta")[0].text,
                         "G3ZIL (IO90HW) / G4HZX (IO91) · 40m · April 2017 · RX Benchmark")
        intro = document.find(css_class="case-intro")[0].text.strip()
        self.assertIn("A low dipole versus a vertical on 40 m — a real-world comparison using WSPR data.", intro)
        self.assertIn("Does a better signal-to-noise ratio also mean more signals decoded?", intro)

    def test_authored_hero_title_is_used_in_page_metadata_and_demo_cards(self) -> None:
        for demo, language, page in self.cases():
            with self.subTest(demo=demo["id"], language=language):
                document = Document(page)
                title = document.find(css_class="case-hero")[0].descendants("h1")[0].text
                self.assertEqual(document.find(tag="title")[0].text, title + " · WSPRadar")
                self.assertIn(title + " · WSPRadar", [node.attributes.get("content") for node in document.find(tag="meta")
                                      if node.attributes.get("property") == "og:title"])
                cards = Document(self.pages[f"{language}/demos/index.html"]).find(css_class="demo-card")
                destination = f'/{language}/demos/{demo["id"]}/'
                card = next(card for card in cards
                            if any(link.attributes.get("href") == destination for link in card.descendants("a")))
                if language in self.builder.demos_index:
                    display = next(item for item in self.builder.demos_index[language]["cards"]
                                   if item["id"] == demo["id"])
                    self.assertEqual([heading.text for heading in card.descendants("h3")], [display["title"]])
                    self.assertNotIn("data-demo-search-text", card.attributes)
                else:
                    self.assertEqual([heading.text for heading in card.descendants("h2")], [title])
                    self.assertIn(title, card.attributes["data-filter-text"])

    def test_english_demo_identity_numbers_are_removed_from_visible_copy(self) -> None:
        for demo in self.builder.published_demos:
            with self.subTest(demo=demo["id"]):
                document = Document(self.page(demo["id"], "en"))
                hero = document.find(css_class="case-hero")[0]
                self.assertNotRegex(hero.descendants("h1")[0].text, r"^#\d+\b")
                self.assertNotRegex(document.find(css_class="eyebrow")[0].text, r"#\d+\b")
                self.assertNotRegex(document.find(css_class="case-study")[0].text, r"(?i)\bdemo\s*#\d+\b")
        landing = Document(self.pages["en/demos/index.html"])
        for card in landing.find(css_class="demo-card"):
            self.assertNotRegex(card.text, r"(?i)\bdemo\s*#\d+\b")

    def test_hero_period_visibility_preserves_other_metadata_and_launch_settings(self) -> None:
        config = deepcopy(self.configurations[self.demo_id])
        for language in ("en", "de"):
            with self.subTest(language=language):
                launch_url = demo_walkthrough.demo_launch_url(self.demo)
                config["show_hero_period"] = False
                hidden = render_demo(self.builder, language, self.demo, config,
                                     build_site.button, build_site.route, build_site.APP_URL)
                document = Document(hidden)
                self.assertEqual(document.find(css_class="case-meta")[0].text,
                                 "G3ZIL (IO90HW) / G4HZX (IO91) · 40m · " + config["languages"][language]["mode"])
                hero = document.find(css_class="case-hero")[0]
                self.assertEqual(sum(link.attributes.get("href") == launch_url
                                     for link in hero.descendants("a")), 1)
                config["show_hero_period"] = True
                shown = render_demo(self.builder, language, self.demo, config,
                                    build_site.button, build_site.route, build_site.APP_URL)
                config.pop("show_hero_period")
                default = render_demo(self.builder, language, self.demo, config,
                                      build_site.button, build_site.route, build_site.APP_URL)
                self.assertEqual(shown, default)
                self.assertIn(config["languages"][language]["period"],
                              Document(shown).find(css_class="case-meta")[0].text)
        for invalid in ("false", 0, 1, None, [], {}):
            with self.subTest(invalid=invalid):
                config["show_hero_period"] = invalid
                with self.assertRaisesRegex(ValueError, "show_hero_period must be a boolean"):
                    render_demo(self.builder, "en", self.demo, config,
                                build_site.button, build_site.route, build_site.APP_URL)

    def test_demo_one_launches_the_canonical_settings_in_both_languages(self) -> None:
        self.assertNotIn("launch_url", self.configurations[self.demo_id])
        self.assertNotIn("launch_urls", self.configurations[self.demo_id])
        for language in ("en", "de"):
            with self.subTest(language=language):
                links = Document(self.page(self.demo_id, language)).find(tag="a")
                expected = demo_walkthrough.demo_launch_url(self.demo)
                self.assertEqual(sum(link.attributes.get("href") == expected for link in links), 2 if language == "en" else 1)
                query = parse_qs(urlsplit(expected).query)
                self.assertNotIn("operation_confirmed", query)
                self.assertEqual(query["v"], ["1"])
                # The canonical launch omits the default minimum of one pair.
                self.assertNotIn("min_spot_pairs", query)
                self.assertNotIn("min_joint", query)
                self.assertNotIn("filter_joint", query)
        advanced = self.demo["settings"]["advanced_parameters"]
        self.assertEqual(advanced["min_spot_pairs_per_station"], 1)
        self.assertEqual(advanced["min_qualifying_stations_per_map_segment"], 5)
        self.assertEqual(advanced["min_decode_event_share_percent"], 1.0)
        self.assertNotIn("min_decode_events_per_station", advanced)
        self.assertNotIn("min_decode_stations_per_map_segment", advanced)

    def test_demo_one_settings_table_uses_canonical_labels_and_values(self) -> None:
        table = Document(self.page(self.demo_id, "en")).find(css_class="case-settings-complete")[0].descendants("table")[0]
        rows = table.descendants("tr")[1:]
        selection = self.configurations[self.demo_id]["settings_tables"]["en"]["rows"]
        summary = {row["key"]: row for row in self.demo["settings_summary"]}
        if "min_joint_spots_per_station" in summary:
            summary.setdefault("min_spot_pairs_per_station", summary["min_joint_spots_per_station"])
        self.assertEqual(len(rows), len(selection))
        for actual, selected in zip(rows, selection):
            row = summary[selected["key"]]
            meaning = Document(self.builder.md(selected["meaning"], "en")).find(tag="p")[0].text
            self.assertEqual([cell.text for cell in actual.descendants("td")],
                             [row["label"]["en"], row["value"]["en"], meaning])
        self.assertTrue({"min_spot_pairs_per_station", "min_qualifying_stations_per_map_segment",
                         "min_decode_event_share_percent",
                         "delta_snr_outlier_reporting"}.issubset({row["key"] for row in selection}))
        self.assertTrue({"min_decode_events_per_station", "min_decode_stations_per_map_segment"}.isdisjoint(
            {row["key"] for row in selection}))

    def test_demo_one_footer_links_the_current_canonical_configuration(self) -> None:
        footer = Document(self.page(self.demo_id, "en")).find(identity="takeaways")[0]
        current = [link for link in footer.descendants("a")
                   if link.text == "Run this comparison in WSPRadar ↗"]
        self.assertEqual(len(current), 1)
        self.assertEqual(current[0].attributes["href"], build_site.demo_launch_url(self.demo))
        self.assertNotIn("button", (current[0].attributes.get("class") or "").split())

    def test_demo_one_setup_uses_its_reviewed_schematic_once_instead_of_a_placeholder(self) -> None:
        key = "demo1-setup-network-schematic"
        config = self.configurations[self.demo_id]
        self.assertEqual(config["setup_media_key"], key)
        resource = next(item for item in self.resource_media(self.demo_id, "en") if item["key"] == key)
        self.assertEqual(sorted(item["width"] for item in resource["variants"]), [520, 1040, 1600])
        self.assertTrue(resource["path"].endswith(".webp"))
        for language in ("en", "de"):
            with self.subTest(language=language):
                document = Document(self.page(self.demo_id, language))
                setup = document.find(identity="setup")[0]
                figures = setup.descendants("figure")
                self.assertEqual([figure.attributes.get("id") for figure in figures], ["case-media-" + key])
                self.assertEqual(len(document.find(identity="case-media-" + key)), 1)
                self.assertNotIn("case-placeholder", figures[0].attributes.get("class", "").split())
                self.assertEqual(figures[0].descendants("img")[0].attributes["alt"], resource["alt"][language])
        manifest_path = safe_path(self.builder.demo_asset_root, config["resource_manifest"])
        declared = {entry["path"] for entry in json.loads(manifest_path.read_text(encoding="utf-8"))["files"]}
        self.assertNotIn("source/setup-network-original.png", declared)

    def test_setup_media_position_is_opt_in_and_invalid_positions_are_rejected(self) -> None:
        self.assertEqual(self.configurations[self.demo_id]["setup_media_position"], "left")
        for demo, language, page in self.cases():
            with self.subTest(demo=demo["id"], language=language):
                document = Document(page)
                setup = document.find(identity="setup")[0]
                positioned = document.find(css_class="case-setup-media-left")
                expected_position = self.configurations[demo["id"]].get("setup_media_position", "right")
                self.assertEqual(positioned, [setup] if expected_position == "left" else [])
        config = deepcopy(self.configurations[self.demo_id])
        config.pop("setup_media_position")
        default = render_demo(self.builder, "en", self.demo, config,
                              build_site.button, build_site.route, build_site.APP_URL)
        self.assertEqual(Document(default).find(css_class="case-setup-media-left"), [])
        config["setup_media_position"] = "right"
        self.assertEqual(render_demo(self.builder, "en", self.demo, config,
                                     build_site.button, build_site.route, build_site.APP_URL), default)
        for invalid in ("center", "LEFT", "", None, True, [], {}):
            with self.subTest(invalid=invalid):
                config["setup_media_position"] = invalid
                with self.assertRaisesRegex(ValueError, "setup_media_position"):
                    render_demo(self.builder, "en", self.demo, config,
                                build_site.button, build_site.route, build_site.APP_URL)

    def test_setup_can_omit_media_without_losing_its_description(self) -> None:
        config = deepcopy(self.configurations[self.demo_id])
        config.pop("setup_media_key")
        default = render_demo(self.builder, "en", self.demo, config,
                              build_site.button, build_site.route, build_site.APP_URL)
        self.assertEqual(len(Document(default).find(identity="setup")[0].descendants("figure")), 1)
        config["show_setup_media"] = False
        hidden = render_demo(self.builder, "en", self.demo, config,
                             build_site.button, build_site.route, build_site.APP_URL)
        setup = Document(hidden).find(identity="setup")[0]
        self.assertEqual(setup.descendants("figure"), [])
        sections = read_sections(safe_path(self.builder.demo_root, config["markdown_paths"]["en"]))
        _, body = demo_walkthrough.heading_and_body(sections["setup"], 2)
        self.assertIn(self.builder.md(body, "en"), hidden)
        for invalid in ("false", 0, 1, None, [], {}):
            with self.subTest(invalid=invalid):
                config["show_setup_media"] = invalid
                with self.assertRaisesRegex(ValueError, "show_setup_media must be a boolean"):
                    render_demo(self.builder, "en", self.demo, config,
                                build_site.button, build_site.route, build_site.APP_URL)
        config["show_setup_media"] = False
        config["setup_media_key"] = self.configurations[self.demo_id]["setup_media_key"]
        with self.assertRaisesRegex(ValueError, "setup_media_key requires show_setup_media"):
            render_demo(self.builder, "en", self.demo, config,
                        build_site.button, build_site.route, build_site.APP_URL)

    def test_walkthrough_places_optional_summary_before_setup_and_omits_legacy_metrics(self) -> None:
        for demo, language, page in self.cases():
            with self.subTest(demo=demo["id"], language=language):
                config = self.configurations[demo["id"]]
                sections = read_sections(safe_path(self.builder.demo_root, config["markdown_paths"][language]))
                document = Document(page)
                case = document.find(css_class="case-study")[0]
                content = [node for node in case.children
                           if isinstance(node, Element) and node.tag != "svg"]
                self.assertIn("case-hero", content[0].attributes.get("class", "").split())
                if "summary" in sections:
                    self.assertEqual(content[1].attributes.get("id"), "summary")
                    self.assertEqual(content[2].attributes.get("id"), "setup")
                else:
                    self.assertEqual(content[1].attributes.get("id"), "setup")
                    self.assertEqual(document.find(css_class="case-summary"), [])
                for removed_class in ("case-introduction", "case-glance", "case-metrics"):
                    self.assertEqual(document.find(css_class=removed_class), [])

    def test_optional_summary_preserves_content_and_local_links_without_changing_steps(self) -> None:
        config = self.configurations[self.demo_id]
        sections = read_sections(safe_path(self.builder.demo_root, config["markdown_paths"]["en"]))
        sections.pop("summary", None)
        with patch.object(demo_walkthrough, "read_sections", return_value=sections):
            without_summary = render_demo(self.builder, "en", self.demo, config,
                                          build_site.button, build_site.route, build_site.APP_URL)
            sections["summary"] = (
                '## Findings <reviewed>\n\n'
                '- [**First result**](#stations)\n\n'
                '    Complete supporting explanation.\n\n'
                '- [**Second result**](#drill-down)\n\n'
                '    Further retained evidence.\n\n'
                'A final qualification.'
            )
            with_summary = render_demo(self.builder, "en", self.demo, config,
                                       build_site.button, build_site.route, build_site.APP_URL)
        document = Document(with_summary)
        summary = document.find(identity="summary")[0]
        self.assertEqual(summary.attributes["aria-label"], "Findings <reviewed>")
        self.assertEqual(summary.descendants("h2")[0].text, "Findings <reviewed>")
        self.assertEqual([link.attributes["href"] for link in summary.descendants("a")],
                         ["#stations", "#drill-down"])
        self.assertEqual(len(summary.descendants("li")), 2)
        self.assertIn("Complete supporting explanation.", summary.text)
        self.assertIn("Further retained evidence.", summary.text)
        self.assertIn("A final qualification.", summary.text)
        transition = '<p>' + escape(config["languages"]["en"]["evidence_intro"]) + '</p>'
        self.assertEqual(with_summary.count(transition), 1)
        self.assertIn(transition, re.search(r'<section class="case-summary".*?</section>',
                                          with_summary, re.DOTALL).group())
        self.assertEqual(re.sub(r'<section class="case-summary".*?</section>', '', with_summary,
                                count=1, flags=re.DOTALL), without_summary.replace(transition, '', 1))

    def test_summary_anchor_cannot_be_reused_by_an_evidence_section(self) -> None:
        config = deepcopy(self.configurations[self.demo_id])
        config["sections_by_language"]["en"][0]["aliases"] = ["summary"]
        with self.assertRaisesRegex(ValueError, "Duplicate or reserved demo section ID or alias: summary"):
            render_demo(self.builder, "en", self.demo, config,
                        build_site.button, build_site.route, build_site.APP_URL)

    def test_configured_setup_summaries_and_hero_paper_links_remain(self) -> None:
        self.assertIs(self.configurations[self.demo_id]["show_setup_summary"], False)
        for demo, language, page in self.cases():
            identity = demo["id"]
            config = self.configurations[identity]
            with self.subTest(demo=identity, language=language):
                document = Document(page)
                setup = document.find(identity="setup")[0]
                expected = int(config.get("show_setup_summary", True))
                for css_class in ("case-identities", "case-window"):
                    summaries = [node for node in setup.descendants()
                                 if css_class in node.attributes.get("class", "").split()]
                    self.assertEqual(len(summaries), expected)
                publication = config.get("publication_url")
                summary_links = [anchor for anchor in setup.descendants("a")
                                 if "text-link" in anchor.attributes.get("class", "").split()
                                 and anchor.attributes.get("href") == publication]
                self.assertEqual(len(summary_links), expected * int(bool(publication)))
                hero = document.find(css_class="case-hero")[0]
                hero_paper_links = [anchor for anchor in hero.descendants("a")
                                    if anchor.attributes.get("href") == publication]
                self.assertEqual(len(hero_paper_links), int(bool(publication)))

    def test_demo_pages_have_no_trailing_supporting_panels_or_navigation(self) -> None:
        for demo, language, page in self.cases():
            with self.subTest(demo=demo["id"], language=language):
                document = Document(page)
                case = document.find(css_class="case-study")[0]
                disclosures = case.descendants("details")
                config = self.configurations[demo["id"]]
                configured = language in config.get("settings_table_disclosure", {})
                source = safe_path(self.builder.demo_root, config["markdown_paths"][language]).read_text(encoding="utf-8")
                retained_evidence = source.count('<details class="case-evidence-details">')
                self.assertEqual(len(disclosures), int(configured) + retained_evidence)
                self.assertTrue(all(item.attributes.get("class") in {"case-settings-details", "case-evidence-details"}
                                    for item in disclosures))
                for anchor in ("experiment", "figures", "screenshots"):
                    self.assertEqual(document.find(identity=anchor), [])
                    self.assertNotIn('href="#' + anchor + '"', page)

    def test_every_active_setup_and_walkthrough_heading_and_complete_body_remains_once(self) -> None:
        for demo, language, page in self.cases():
            config = self.configurations[demo["id"]]
            sections = read_sections(safe_path(self.builder.demo_root, config["markdown_paths"][language]))
            settings_table = demo_walkthrough.demo_settings_table(demo, config, language)
            document = Document(page)
            keys = ["setup", *(item["id"] for item in self.configured_sections(demo_walkthrough.demo_sections(config, language)))]
            for key in keys:
                with self.subTest(demo=demo["id"], language=language, section=key):
                    heading, body = demo_walkthrough.heading_and_body(sections[key], 2)
                    section = document.find(identity=key)[0]
                    headings = [node.text for node in section.descendants()
                                if node.tag in {"h2", "h3"}]
                    self.assertEqual(headings.count(heading), 1)
                    expanded = demo_walkthrough.expand_demo_markdown(body, demo, settings_table)
                    rendered = build_site.open_pdf_links_in_new_tabs(self.builder.md(expanded, language))
                    disclosure = demo_walkthrough.settings_table_disclosure(
                        settings_table, config, language, lambda value: self.builder.md(value, language))
                    if disclosure is not None and "{{demo_settings_table}}" in body:
                        rendered = rendered.replace(self.builder.md(settings_table, language), disclosure, 1)
                    rendered = build_site.apply_product_navigation_link_policy(
                        rendered, self.builder.navigation, current_suffix=f"demos/{demo['id']}/")
                    self.assertEqual(page.count(rendered), 1)

    def test_imported_media_stay_once_and_only_declared_resources_are_added(self) -> None:
        for demo, language, page in self.cases():
            identity = demo["id"]
            with self.subTest(demo=identity, language=language):
                case = Document(page).find(css_class="case-study")[0]
                images = case.descendants("img")
                imported = self.imported_media(identity, language)
                resources = self.resource_media(identity, language)
                self.assertEqual(Counter(image.attributes.get("src") for image in images
                                         if image.attributes.get("src", "").startswith("/content/")),
                                 Counter("/content/" + item["asset_path"] for item in imported))
                self.assertEqual(len(images), len(imported) + len(resources))
                expected = [(item, "/content/" + item["asset_path"], None) for item in imported]
                expected += [(item, "/assets/demos/" + identity + "/" + item["path"],
                              "/assets/demos/" + identity + "/") for item in resources]
                for item, full_source, resource_prefix in expected:
                    with self.subTest(media=item["key"]):
                        figures = [figure for figure in case.descendants("figure")
                                   if figure.attributes.get("id") == "case-media-" + item["key"]]
                        self.assertEqual(len(figures), 1)
                        figure = figures[0]
                        self.assertEqual(len(figure.descendants("img")), 1)
                        image = figure.descendants("img")[0]
                        self.assertEqual(image.attributes.get("alt"), item["alt"][language])
                        self.assertGreater(int(image.attributes["width"]), 0)
                        self.assertGreater(int(image.attributes["height"]), 0)
                        permitted_sources = {full_source}
                        if resource_prefix:
                            permitted_sources.update(resource_prefix + variant["path"] for variant in item.get("variants", []))
                        self.assertIn(image.attributes.get("src"), permitted_sources)
                        if image.attributes.get("srcset"):
                            for candidate in image.attributes["srcset"].split(","):
                                self.assertIn(candidate.strip().split()[0], permitted_sources)
                        captions = figure.descendants("figcaption")
                        self.assertEqual(len(captions), 1)
                        self.assertIn(item["title"][language], captions[0].text)
                        full_size_links = [anchor for anchor in captions[0].descendants("a")
                                           if anchor.attributes.get("href") == full_source]
                        self.assertEqual(full_size_links, [])
                        caption = item.get("caption", {}).get(language, "")
                        if caption:
                            self.assertEqual(page.count(build_site.open_pdf_links_in_new_tabs(self.builder.md(caption, language))), 1)
                        anchors = [anchor for anchor in figure.descendants("a")
                                   if "data-case-lightbox" in anchor.attributes]
                        self.assertEqual(len(anchors), 1)
                        self.assertEqual(anchors[0].attributes.get("href"), full_source)

    def test_missing_figures_have_explicit_accessible_placeholders(self) -> None:
        for demo, language, page in self.cases():
            config = self.configurations[demo["id"]]
            document = Document(page)
            with self.subTest(demo=demo["id"], language=language):
                expected = int(config.get("show_setup_media", True) and not config.get("setup_media_key")) + sum(
                    not section.get("media_keys") and section.get("layout") != "full"
                    for section in self.configured_sections(demo_walkthrough.demo_sections(config, language)))
                placeholders = document.find(css_class="case-placeholder")
                self.assertEqual(len(placeholders), expected)
                for placeholder in placeholders:
                    self.assertEqual(placeholder.tag, "figure")
                    self.assertEqual(placeholder.descendants("img"), [])
                    self.assertEqual(len(placeholder.descendants("figcaption")), 1)
                    accessible = [node for node in placeholder.descendants() if node.attributes.get("role") == "img"]
                    self.assertEqual(len(accessible), 1)
                    self.assertTrue(accessible[0].attributes.get("aria-label"))
                    self.assertIn(accessible[0].attributes["aria-label"], placeholder.text)
                for section in self.configured_sections(demo_walkthrough.demo_sections(config, language)):
                    if not section.get("media_keys") and section.get("layout") != "full":
                        block = document.find(identity=section["id"])[0]
                        self.assertIn("Figure to follow" if language == "en" else "Abbildung folgt", block.text)

    def test_renderer_rejects_missing_foreign_and_duplicate_evidence(self) -> None:
        original = self.configurations[self.demo_id]
        foreign = next(item["key"] for item in [*self.builder.figures, *self.builder.screenshots]
                       if item["demo_id"] != self.demo_id)
        first_key = demo_walkthrough.demo_sections(original, "en")[1]["media_keys"][0]
        for keys in (["unknown-review-asset"], [foreign], [first_key, first_key]):
            with self.subTest(keys=keys):
                config = deepcopy(original)
                config["sections_by_language"]["en"][1]["media_keys"] = keys
                with self.assertRaisesRegex(ValueError, "Unknown or duplicate case-study media"):
                    render_demo(self.builder, "en", self.demo, config,
                                build_site.button, build_site.route, build_site.APP_URL)

    def test_unplaced_markdown_is_rejected_instead_of_silently_dropped(self) -> None:
        config = self.configurations[self.demo_id]
        sections = read_sections(safe_path(self.builder.demo_root, config["markdown_paths"]["en"]))
        sections["not-yet-placed"] = "## Additional scientific qualification\n\nThis must never disappear."
        with patch.object(demo_walkthrough, "read_sections", return_value=sections):
            with self.assertRaisesRegex(ValueError, "Unplaced demo Markdown sections: not-yet-placed"):
                render_demo(self.builder, "en", self.demo, config,
                            build_site.button, build_site.route, build_site.APP_URL)

    def test_figure_three_comparison_is_nested_under_temporal_evidence_without_diagnostic_image(self) -> None:
        config = self.configurations[self.demo_id]
        expected_children = [("published-figure3", "griffiths-figure3-comparison")]
        for language in ("en", "de"):
            with self.subTest(language=language):
                page = self.page(self.demo_id, language)
                document = Document(page)
                temporal = document.find(identity="time")
                self.assertEqual(len(temporal), 1)
                direct_sections = [child for child in temporal[0].children
                                   if isinstance(child, Element) and child.tag == "section"]
                self.assertEqual([child.attributes.get("id") for child in direct_sections],
                                 [key for key, _ in expected_children])
                markdown_sections = read_sections(safe_path(self.builder.demo_root, config["markdown_paths"][language]))
                for (key, media_key), child in zip(expected_children, direct_sections):
                    self.assertEqual(len(document.find(identity=key)), 1)
                    figures = [figure for figure in child.descendants("figure")
                               if figure.attributes.get("id") == "case-media-" + media_key]
                    self.assertEqual(len(figures), 0 if media_key in config.get("excluded_media_keys", []) else 1)
                    heading, body = demo_walkthrough.heading_and_body(markdown_sections[key], 2)
                    self.assertEqual([node.text for node in child.descendants("h3")], [heading])
                    self.assertEqual(page.count(build_site.open_pdf_links_in_new_tabs(self.builder.md(body, language))), 1)
                figure_order = [figure.attributes.get("id") for figure in temporal[0].descendants("figure")]
                self.assertEqual(figure_order, ["case-media-demo1-temporal-delta-snr-typography-en-20261024" if language == "en" else "case-media-fresh-demo1-time",
                                               "case-media-griffiths-figure3-comparison"])

    def test_figure_three_comparison_links_keep_expected_website_pdf_destinations(self) -> None:
        figure_three_pdf = "/assets/demos/griffiths_fig3_paper_v1/WSPRadar_Demo_Griffiths_Figure3.pdf"
        figure_six_pdf = "/assets/demos/griffiths_fig6_paper_v1/WSPRadar_Demo_Griffiths_Figure6.pdf"
        expected_by_language = {"en": [figure_three_pdf, figure_six_pdf], "de": [figure_three_pdf]}
        for language in ("en", "de"):
            with self.subTest(language=language):
                section = Document(self.page(self.demo_id, language)).find(identity="published-figure3")[0]
                links = [node.attributes for node in section.descendants("a")
                         if urlsplit(node.attributes.get("href", "")).path.lower().endswith(".pdf")]
                self.assertEqual([node["href"] for node in links], expected_by_language[language])
                for attributes in links:
                    self.assertEqual(attributes["target"], "_blank")
                    self.assertEqual(set(attributes["rel"].split()), {"noopener", "noreferrer"})

    def test_excluded_diagnostic_never_returns_in_retained_or_supplemental_media(self) -> None:
        key = "griffiths-figure3-pairing-diagnostic"
        self.assertIn(key, self.configurations[self.demo_id]["excluded_media_keys"])
        source = next(item for item in self.builder.figures if item["key"] == key)
        for language in ("en", "de"):
            with self.subTest(language=language):
                document = Document(self.page(self.demo_id, language))
                self.assertEqual(document.find(identity="case-media-" + key), [])
                self.assertFalse(any(node.attributes.get("src") == "/content/" + source["asset_path"]
                                     for node in document.find(tag="img")))
                self.assertFalse(any(node.attributes.get("href") == "/content/" + source["asset_path"]
                                     for node in document.find(tag="a")))

    def test_inverted_media_carry_display_metadata_without_changing_sources(self) -> None:
        self.assertIn("griffiths-figure3-comparison", self.configurations[self.demo_id].get("inverted_media_keys", []))
        for demo, language, page in self.cases():
            identity = demo["id"]
            expected = set(self.configurations[identity].get("inverted_media_keys", []))
            document = Document(page)
            with self.subTest(demo=identity, language=language):
                inverted = document.find(css_class="case-figure-inverted")
                self.assertEqual({figure.attributes["id"] for figure in inverted},
                                 {"case-media-" + key for key in expected})
                for figure in document.find(css_class="case-figure"):
                    key = figure.attributes["id"].removeprefix("case-media-")
                    anchors = [anchor for anchor in figure.descendants("a")
                               if "data-case-lightbox" in anchor.attributes]
                    self.assertEqual(len(anchors), 1)
                    self.assertEqual(anchors[0].attributes.get("data-invert-colors") == "true", key in expected)
                # Source links and img/srcset alternatives are verified against
                # their immutable catalogs in the media-preservation test above.

    def test_unknown_excluded_or_inverted_keys_are_rejected(self) -> None:
        for field in ("excluded_media_keys", "inverted_media_keys"):
            with self.subTest(field=field):
                config = deepcopy(self.configurations[self.demo_id])
                config[field] = ["unknown-review-asset"]
                with self.assertRaises(ValueError):
                    render_demo(self.builder, "en", self.demo, config,
                                build_site.button, build_site.route, build_site.APP_URL)

    def test_partial_inversion_preserves_reviewed_color_regions_from_the_original_image(self) -> None:
        key = "griffiths-figure3-comparison"
        expected = {"image_px": [3060, 3060],
                    "rectangles_px": [[353, 2161, 2339, 549], [2752, 2161, 32, 549]],
                    "label_rectangles_px": [[2372, 2161, 320, 106]]}
        self.assertEqual(self.configurations[self.demo_id]["preserved_color_regions"][key], expected)
        source = next(item for item in self.builder.figures if item["key"] == key)
        self.assertEqual(source.get("provenance", {}).get("image_px", [source.get("width"), source.get("height")]),
                         expected["image_px"])
        original_url = "/content/" + source["asset_path"]
        for language in ("en", "de"):
            with self.subTest(language=language):
                document = Document(self.page(self.demo_id, language))
                figure = document.find(identity="case-media-" + key)[0]
                anchor = next(node for node in figure.descendants("a")
                              if "data-case-lightbox" in node.attributes)
                image = anchor.descendants("img")[0]
                self.assertEqual(anchor.attributes["href"], original_url)
                self.assertEqual(image.attributes["src"], original_url)
                self.assertEqual(anchor.attributes["data-invert-colors"], "true")
                reference = anchor.attributes["data-image-filter"]
                self.assertRegex(reference, r"^url\(#[a-z0-9_-]+\)$")
                self.assertEqual(image.attributes["style"], "filter:" + reference)
                filters = document.find(tag="filter", identity=reference[5:-1])
                self.assertEqual(len(filters), 1)
                image_filter = filters[0]
                for attribute in ("filterunits", "primitiveunits"):
                    self.assertEqual(image_filter.attributes[attribute], "objectBoundingBox")
                self.assertEqual(image_filter.attributes["color-interpolation-filters"], "sRGB")
                transfer = [node for node in image_filter.descendants("fecomponenttransfer")
                            if node.attributes.get("result") == "inverted"]
                self.assertEqual(len(transfer), 1)
                self.assertEqual(transfer[0].attributes, {"in": "SourceGraphic", "result": "inverted"})
                for channel in ("fefuncr", "fefuncg", "fefuncb"):
                    self.assertEqual(transfer[0].descendants(channel)[0].attributes,
                                     {"type": "table", "tablevalues": "1 0"})
                masks = [node for node in image_filter.descendants("feflood")
                         if node.attributes.get("result", "").startswith("mask")]
                backgrounds = [node for node in image_filter.descendants("feflood")
                               if node.attributes.get("result", "").startswith("background")]
                composites = [node for node in image_filter.descendants("fecomposite")
                              if node.attributes.get("result", "").startswith("original")]
                self.assertEqual(len(masks), len(expected["rectangles_px"]))
                self.assertEqual(len(backgrounds), len(masks))
                self.assertEqual(len(composites), len(masks))
                for index, (mask, rectangle) in enumerate(zip(masks, expected["rectangles_px"])):
                    x, y, width, height = rectangle
                    self.assertGreaterEqual(min(x, y), 0)
                    self.assertLessEqual(x + width, expected["image_px"][0])
                    self.assertLessEqual(y + height, expected["image_px"][1])
                    for name, numerator, denominator in zip(
                            ("x", "y", "width", "height"), rectangle,
                            expected["image_px"] * 2):
                        self.assertAlmostEqual(float(mask.attributes[name]), numerator / denominator, places=9)
                    self.assertEqual(mask.attributes["result"], f"mask{index}")
                    self.assertEqual(backgrounds[index].attributes,
                                     {**mask.attributes, "flood-color": "black", "result": f"background{index}"})
                    self.assertEqual(composites[index].attributes,
                                     {"in": "native-colors", "in2": f"mask{index}",
                                      "operator": "in", "result": f"original{index}"})
                native_colors = [node for node in image_filter.descendants("fecomposite")
                                 if node.attributes.get("result") == "native-colors"]
                self.assertEqual(len(native_colors), 1)
                self.assertEqual(native_colors[0].attributes,
                                 {"in": "SourceGraphic", "in2": "white-background",
                                  "operator": "out", "result": "native-colors"})
                label = next(node for node in image_filter.descendants("feflood")
                             if node.attributes.get("result") == "label-base0")
                self.assertEqual(label.attributes["flood-color"], "#b9c8d6")
                for name, value, dimension in zip(("x", "y", "width", "height"),
                                                  expected["label_rectangles_px"][0], expected["image_px"] * 2):
                    self.assertAlmostEqual(float(label.attributes[name]), value / dimension, places=9)
                self.assertEqual([node.attributes["in"] for node in image_filter.descendants("femergenode")],
                                 ["inverted", "background0", "original0", "background1", "original1", "label-ink0"])
                for other in document.find(tag="a"):
                    if "data-case-lightbox" in other.attributes and other is not anchor:
                        self.assertNotIn("data-image-filter", other.attributes)

    def test_plot_white_mask_keeps_bright_markers_and_dark_ink_while_removing_pale_backgrounds(self) -> None:
        document = Document(self.page(self.demo_id, "en"))
        image_filter = document.find(tag="filter")[0]
        primitives = {node.attributes["result"]: node for node in image_filter.descendants()
                      if "result" in node.attributes}
        self.assertEqual(primitives["chroma-rgb"].attributes,
                         {"in": "maximum-rgb", "in2": "minimum-rgb", "mode": "difference", "result": "chroma-rgb"})
        self.assertEqual(primitives["white-background"].attributes,
                         {"in": "bright-pixels", "in2": "low-chroma", "operator": "in", "result": "white-background"})
        weights = [float(value) for value in primitives["lightness"].attributes["values"].split()][15:18]

        def ramp(name, value):
            alpha = primitives[name].descendants("fefunca")[0]
            self.assertEqual(alpha.attributes["type"], "linear")
            return min(1.0, max(0.0, float(alpha.attributes["slope"]) * value + float(alpha.attributes["intercept"])))

        def plot_pixel(rgb):
            luminance = sum(weight * value / 255 for weight, value in zip(weights, rgb))
            chroma = (max(rgb) - min(rgb)) / 255
            removed = ramp("bright-pixels", luminance) * ramp("low-chroma", chroma)
            return tuple(round(value * (1 - removed), 6) for value in rgb)

        for rgb in ((255, 255, 255), (242, 242, 242), (231, 236, 246), (240, 244, 250)):
            with self.subTest(background=rgb):
                self.assertEqual(plot_pixel(rgb), (0, 0, 0))
        for rgb in ((200, 244, 255), (17, 17, 17), (25, 66, 177), (255, 176, 0), (0, 128, 64)):
            with self.subTest(native_ink_or_data=rgb):
                self.assertEqual(plot_pixel(rgb), rgb)
        # A resampled pale edge must darken continuously rather than survive as
        # a white halo; its fully saturated blue and cyan endpoints stay native.
        self.assertLess(max(plot_pixel((210, 220, 235))), 180)
        self.assertEqual(primitives["label-ink-mask"].attributes,
                         {"in": "dark-pixels", "in2": "low-chroma", "operator": "in", "result": "label-ink-mask"})
        self.assertEqual(ramp("dark-pixels", 17 / 255) * ramp("low-chroma", 0), 1)
        self.assertEqual(ramp("low-chroma", (255 - 200) / 255), 0)

    def test_partial_inversion_rejects_wrong_dimensions_and_out_of_bounds_rectangles(self) -> None:
        key = "griffiths-figure3-comparison"
        invalid_regions = [
            {"image_px": [1530, 1530], "rectangles_px": [[1, 1, 100, 100]]},
            *({"image_px": [3060, 3060], "rectangles_px": [rectangle]}
              for rectangle in ([-1, 0, 100, 100], [0, -1, 100, 100],
                                [3000, 0, 100, 100], [0, 3000, 100, 100],
                                [0, 0, 0, 100], [0, 0, 100, 0],
                                [0, 0, 100], ["left", 0, 100, 100],
                                [float("nan"), 0, 100, 100], [0, 0, float("inf"), 100])),
        ]
        for regions in invalid_regions:
            with self.subTest(regions=regions):
                config = deepcopy(self.configurations[self.demo_id])
                config["preserved_color_regions"] = {key: regions}
                with self.assertRaises(ValueError):
                    render_demo(self.builder, "en", self.demo, config,
                                build_site.button, build_site.route, build_site.APP_URL)
        config = deepcopy(self.configurations[self.demo_id])
        config["inverted_media_keys"] = []
        with self.assertRaisesRegex(ValueError, "Preserved color regions require an inverted media key"):
            render_demo(self.builder, "en", self.demo, config,
                        build_site.button, build_site.route, build_site.APP_URL)
        for rectangle in ([0, 0, 100, 100], [3000, 3000, 100, 100], [2372, 2161, float("nan"), 106]):
            with self.subTest(label_rectangle=rectangle):
                config = deepcopy(self.configurations[self.demo_id])
                config["preserved_color_regions"][key]["label_rectangles_px"] = [rectangle]
                with self.assertRaises(ValueError):
                    render_demo(self.builder, "en", self.demo, config,
                                build_site.button, build_site.route, build_site.APP_URL)

    def test_drilldown_is_text_only_without_a_missing_figure_placeholder(self) -> None:
        for language in ("en", "de"):
            with self.subTest(language=language):
                section = Document(self.page(self.demo_id, language)).find(identity="drill-down" if language == "en" else "drilldown")[0]
                self.assertEqual(section.descendants("figure"), [])
                self.assertTrue(section.descendants("p"))

    def test_all_demos_number_setup_first_and_preserve_figure_positions(self) -> None:
        for demo, language, page in self.cases():
            document = Document(page)
            config = self.configurations[demo["id"]]
            setup_badges = [node for node in document.find(identity="setup")[0].descendants()
                            if "case-number" in (node.attributes.get("class") or "").split()]
            self.assertEqual([badge.text for badge in setup_badges], ["01"])
            for index, section in enumerate(demo_walkthrough.demo_sections(config, language), 1):
                with self.subTest(demo=demo["id"], language=language, section=section["id"]):
                    group = document.find(identity=section["id"])[0]
                    row = next(child for child in group.children if isinstance(child, Element)
                               and "case-row" in (child.attributes.get("class") or "").split())
                    badges = [node for node in row.descendants()
                              if "case-number" in (node.attributes.get("class") or "").split()]
                    self.assertEqual([badge.text for badge in badges], [f"{index + 1:02d}"])
                    self.assertEqual("case-row-reverse" in row.attributes["class"].split(), index % 2 == 0)
                    heading = row.descendants("h3")[0].text
                    self.assertIsNone(re.match(r"^\d+\.\d+(?:\.|\s)", heading))
                    for child in section.get("subsections", []):
                        child_group = document.find(identity=child["id"])[0]
                        child_badges = [node for node in child_group.descendants()
                                        if "case-number" in (node.attributes.get("class") or "").split()]
                        self.assertEqual([badge.text for badge in child_badges], ["↳"])

    def test_objective_follows_title_and_is_the_first_navigation_target(self) -> None:
        for demo, language, page in self.cases():
            with self.subTest(demo=demo["id"], language=language):
                document = Document(page)
                objective = document.find(identity="objective")[0]
                hero_copy = document.find(css_class="case-hero-copy")[0]
                children = [child for child in hero_copy.children if isinstance(child, Element)]
                title_index = next(index for index, child in enumerate(children) if child.tag == "h1")
                self.assertIs(children[title_index + 1], objective)
                self.assertIn("case-intro", objective.attributes["class"].split())
                self.assertEqual(objective.attributes["aria-label"], "Objective" if language == "en" else "Ziel")
                source = read_sections(safe_path(self.builder.demo_root,
                                       self.configurations[demo["id"]]["markdown_paths"][language]))
                _, intro = demo_walkthrough.heading_and_body(source["hero"], 1)
                rendered = build_site.open_pdf_links_in_new_tabs(self.builder.md(intro, language))
                self.assertIn(rendered, page)
                links = document.find(css_class="case-nav")[0].descendants("a")
                self.assertEqual([link.attributes["href"] for link in links[:2]], ["#objective", "#setup"])
                self.assertEqual(links[0].text, objective.attributes["aria-label"])
                self.assertEqual(document.find(css_class="case-section-heading"), [])

    def test_paper_evidence_navigation_preserves_other_demo_links_and_numbering(self) -> None:
        paper_sections = {
            self.demo_id: ("time", "published-figure3", ["published-figure3"]),
            "vanhamel_rx_buddy": ("stations", "published-figure6", ["published-figure6", "station-decodes"]),
            "zander_tx_buddy": ("difference", "published-figure4", ["published-figure4"]),
        }
        for demo, language, page in self.cases():
            with self.subTest(demo=demo["id"], language=language):
                config = self.configurations[demo["id"]]
                sections = demo_walkthrough.demo_sections(config, language)
                expected = [
                    ("#objective", "Objective" if language == "en" else "Ziel"),
                    ("#setup", config["languages"][language]["nav_setup"]),
                    *(("#" + item["id"], item["nav_label"][language]) for item in sections),
                ]
                document = Document(page)
                if language == "en" and demo["id"] in paper_sections:
                    parent_id, child_id, child_order = paper_sections[demo["id"]]
                    parent_index = next(index for index, item in enumerate(expected) if item[0] == "#" + parent_id)
                    expected.insert(parent_index + 1, ("#" + child_id, "Paper Evidence"))
                    parent_config = next(item for item in sections if item["id"] == parent_id)
                    self.assertEqual([item["id"] for item in parent_config["subsections"]], child_order)
                    paper_config = parent_config["subsections"][0]
                    self.assertIs(paper_config["show_in_nav"], True)
                    self.assertEqual(paper_config["nav_label"][language], "Paper Evidence")
                    parent = document.find(identity=parent_id)[0]
                    child = document.find(identity=child_id)[0]
                    self.assertIn(child, parent.descendants("section"))
                    direct_children = [node for node in parent.children
                                       if isinstance(node, Element) and node.tag == "section"]
                    self.assertEqual([node.attributes.get("id") for node in direct_children], child_order)
                    if demo["id"] == self.demo_id:
                        self.assertEqual(child.descendants("h3")[0].text,
                                         "Verifying WSPRadar against published research")
                    badges = [node.text for node in child.descendants()
                              if "case-number" in (node.attributes.get("class") or "").split()]
                    self.assertEqual(badges, ["↳"])
                links = document.find(css_class="case-nav")[0].descendants("a")
                self.assertEqual([(link.attributes["href"], link.text) for link in links], expected)

    def test_figures_precede_their_related_prose_inside_the_wrapping_container(self) -> None:
        for demo, language, page in self.cases():
            document = Document(page)
            for section in self.configured_sections(demo_walkthrough.demo_sections(self.configurations[demo["id"]], language)):
                if not section.get("media_keys") or section.get("layout") == "full":
                    continue
                with self.subTest(demo=demo["id"], language=language, section=section["id"]):
                    group = document.find(identity=section["id"])[0]
                    row = next(child for child in group.children if isinstance(child, Element)
                               and "case-row" in (child.attributes.get("class") or "").split())
                    copy = next(child for child in row.children if isinstance(child, Element)
                                and "case-copy" in (child.attributes.get("class") or "").split())
                    children = [child for child in copy.children if isinstance(child, Element)]
                    self.assertIn("case-step-heading", children[0].attributes.get("class", "").split())
                    self.assertEqual(len(children[0].descendants("h3")), 1)
                    self.assertEqual(len([node for node in children[0].descendants()
                                          if "case-number" in node.attributes.get("class", "").split()]), 1)
                    self.assertIn("case-media", (children[1].attributes.get("class") or "").split())
                    self.assertTrue(children[1].descendants("figure"))
                    self.assertGreater(len(children), 2)

    def test_image_links_preserve_full_size_access_without_duplicate_caption_actions(self) -> None:
        for demo, language, page in self.cases():
            with self.subTest(demo=demo["id"], language=language):
                document = Document(page)
                anchors = [node for node in document.find(tag="a") if "data-case-lightbox" in node.attributes]
                self.assertEqual(len(anchors), len(self.imported_media(demo["id"], language)) + len(self.resource_media(demo["id"], language)))
                action_text = self.builder.copy[language]["full_size"] + " ↗"
                self.assertFalse(any(action_text in caption.text for caption in document.find(tag="figcaption")))
                ids = {node.attributes["id"] for node in document.root.descendants() if "id" in node.attributes}
                for anchor in anchors:
                    self.assertTrue(anchor.attributes.get("aria-label"))
                    self.assertTrue(anchor.attributes.get("data-title"))
                    self.assertIn(anchor.attributes.get("data-caption-id"), ids)
                    self.assertEqual(anchor.attributes.get("target"), "_blank")
                    self.assertIn("noopener", anchor.attributes.get("rel", "").split())
                    self.assertTrue(anchor.attributes.get("href", "").startswith(("/content/", "/assets/demos/")))
                    self.assertEqual(len(anchor.descendants("img")), 1)

    def test_bilingual_routes_legacy_fragments_navigation_and_exact_demo_launch_survive(self) -> None:
        for demo, language, page in self.cases():
            identity = demo["id"]
            with self.subTest(demo=identity, language=language):
                document = Document(page)
                ids = [node.attributes["id"] for node in document.root.descendants() if "id" in node.attributes]
                self.assertEqual(len(ids), len(set(ids)))
                required = {"setup", "walkthrough"}
                supporting_ids = {"experiment", "figures", "screenshots"}
                self.assertTrue(supporting_ids.isdisjoint(ids))
                self.assertNotIn('href="#experiment"', page)
                if identity == self.demo_id:
                    required.update({"map", "difference", "time", "coverage", "stations", "drilldown", "takeaways"})
                self.assertTrue(required.issubset(ids))
                nav = document.find(css_class="case-nav")
                self.assertEqual(len(nav), 1)
                for anchor in nav[0].descendants("a"):
                    self.assertTrue(anchor.attributes.get("href", "").startswith("#"))
                    self.assertIn(anchor.attributes["href"][1:], ids)
                other = "de" if language == "en" else "en"
                self.assertIn(f"{other}/demos/{identity}/index.html", self.pages)
                switches = document.find(tag="a", css_class="language-option")
                self.assertEqual(
                    [(link.attributes.get("hreflang"), link.attributes.get("href")) for link in switches],
                    [("en", f"/en/demos/{identity}/")],
                )
                self.assertCountEqual(
                    [(link.attributes.get("hreflang"), link.attributes.get("href"))
                     for link in document.find(tag="link") if link.attributes.get("rel") == "alternate"],
                    [(alternate, f"{build_site.SITE_URL}/{alternate}/demos/{identity}/")
                     for alternate in ("en", "de")],
                )
                self.assertIn(f'<link rel="canonical" href="{build_site.SITE_URL}/{language}/demos/{identity}/">', page)
                case_hero = document.find(css_class="case-hero")[0]
                config_links = [anchor for anchor in case_hero.descendants("a")
                                if anchor.attributes.get("href") == "/content/" + demo["config_path"]]
                self.assertEqual(config_links, [])
                expected_label = "Run in WSPRadar App" if language == "en" else "In WSPRadar App starten"
                expected_url = demo_walkthrough.demo_launch_url(demo)
                config = self.configurations[identity]
                actions = demo_walkthrough.language_override(config, "launch_actions", language, None)
                expected_launches = ([(expected_url, expected_label)] if actions is None else [
                    (demo_walkthrough.demo_launch_url(demo, action["variant"]), action["label"])
                    for action in actions
                ])
                header = document.find(css_class="site-header")[0]
                self.assertFalse(any(anchor.attributes.get("href") == expected_url
                                     for anchor in header.descendants("a")))
                self.assertLess(page.index('id="objective"'), page.index(expected_url.replace("&", "&amp;")))
                core = demo["settings"]["core_parameters"]
                comparison = demo["settings"]["comparison_parameters"]
                query = parse_qs(urlsplit(expected_url).query)
                self.assertEqual(query["v"], ["1"])
                self.assertEqual(query["run"], ["1"])
                self.assertEqual(query["direction"], [core["analysis_direction"]])
                self.assertEqual(query["callsign"], [core["callsign"]])
                self.assertEqual(query["qth"], [core["qth"]])
                self.assertEqual(query["band"], [core["band"]])
                self.assertEqual(query["from"], [core["time_selection"]["start_utc"]])
                self.assertEqual(query["to"], [core["time_selection"]["end_utc"]])
                self.assertEqual(query["mode"], ["performance" if comparison["mode"] == "none" else "benchmark"])
                self.assertNotIn("demo", query)
                self.assertTrue(all(len(values) == 1 for values in query.values()))
                if comparison["mode"] != "none":
                    self.assertEqual(query["benchmark_design"], [comparison["mode"]])
                    self.assertEqual(query["reference"], [comparison["reference_callsign"]])
                    self.assertEqual(query["reference_qth"], [comparison["reference_qth"]])
                buttons = [anchor for anchor in case_hero.descendants("a")
                           if "button" in (anchor.attributes.get("class") or "").split()]
                self.assertEqual([(anchor.attributes["href"], anchor.text) for anchor in buttons],
                                 [(url, label + " ↗") for url, label in expected_launches])
                launches = [anchor for anchor in document.find(css_class="case-study")[0].descendants("a")
                            if anchor.attributes.get("href") in {
                                demo_walkthrough.demo_launch_url(demo),
                                *demo.get("launch_variants", {}).values(),
                            }]
                self.assertGreaterEqual(len(launches), len(buttons))
                for launch in launches:
                    self.assertEqual(launch.attributes.get("target"), "_blank")
                    self.assertTrue({"noopener", "noreferrer"}.issubset(
                        launch.attributes.get("rel", "").split()))
                for launch in buttons:
                    target = urlsplit(launch.attributes["href"])
                    self.assertEqual((target.scheme, target.netloc, target.path, target.fragment),
                                     ("https", "wspradar.org", "/", "wspradar-results-inspection"))
                self.assertEqual(document.find(css_class="case-launch-note"), [])


class DemoSourceValidationTests(unittest.TestCase):
    """Exercise editable source and resource boundaries using isolated files."""

    def setUp(self) -> None:
        scratch = Path(__file__).resolve().parents[1] / ".tmp"
        scratch.mkdir(exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix="demo-source-test-", dir=scratch)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def write(self, name, payload):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload if isinstance(payload, bytes) else payload.encode("utf-8"))
        return path

    def test_demo_launch_requires_an_explicit_stored_url(self) -> None:
        self.assertEqual(demo_walkthrough.demo_launch_url({"launch_url": DEMO_ONE_LAUNCH_URL}),
                         DEMO_ONE_LAUNCH_URL)
        for config in ({}, {"launch_url": ""}, {"launch_url": None}):
            with self.subTest(config=config), self.assertRaises(ValueError):
                demo_walkthrough.demo_launch_url(config)

    def test_markdown_sections_keep_all_paragraphs_and_reject_duplicate_blocks(self) -> None:
        source = "<!-- section: hero -->\n# A title\n\nComplete introduction.\n\n<!-- section: setup -->\n## Experiment\n\nFirst paragraph.\n\nSecond paragraph: ΔSNR = Target − Reference.\n"
        path = self.write("walkthrough.en.md", source)
        sections = read_sections(path)
        self.assertEqual(sections, {"hero": "# A title\n\nComplete introduction.",
                                    "setup": "## Experiment\n\nFirst paragraph.\n\nSecond paragraph: ΔSNR = Target − Reference."})
        self.write("walkthrough.en.md", source + "\n<!-- section: setup -->\n## Accidentally duplicated\n")
        with self.assertRaisesRegex(ValueError, "Duplicate demo Markdown section: setup"):
            read_sections(path)

    def test_unmarked_leading_text_and_missing_required_blocks_are_rejected(self) -> None:
        invalid = ("This paragraph must not disappear.\n<!-- section: hero -->\n# Title\n<!-- section: setup -->\n## Setup",
                   "<!-- section: hero -->\n# Title")
        for source in invalid:
            with self.subTest(source=source):
                path = self.write("walkthrough.md", source)
                with self.assertRaises(ValueError):
                    read_sections(path)

    def test_source_paths_cannot_escape_the_markdown_root(self) -> None:
        self.assertEqual(safe_path(self.root, "demo/walkthrough.en.md"), self.root / "demo/walkthrough.en.md")
        for name in ("../private.md", "demo/../../private.md", "..\\private.md", "/absolute.md", str(self.root.parent / "private.md")):
            with self.subTest(path=name), self.assertRaisesRegex(ValueError, "Unsafe demo source path"):
                safe_path(self.root, name)

    def resource_fixture(self):
        payload = b"Reviewed immutable image bytes"
        self.write("demo/image.png", payload)
        entry = {"path": "image.png", "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}
        self.write("demo/resources.json", json.dumps({"files": [entry]}))
        return payload, entry, {"demo": {"resource_manifest": "demo/resources.json"}}

    def test_resource_export_copies_only_allowlisted_unchanged_bytes(self) -> None:
        payload, _, configurations = self.resource_fixture()
        self.write("demo/private-note.txt", "Not declared for publication")
        self.assertEqual(resource_files(self.root, configurations), {"assets/demos/demo/image.png": payload})

    def test_archived_resource_is_read_from_the_selected_source_tree(self) -> None:
        payload, entry, configurations = self.resource_fixture()
        entry["source_path"] = "archive/reviewed-image.png"
        self.write("source/archive/reviewed-image.png", payload)
        self.write("demo/resources.json", json.dumps({"files": [entry]}))
        self.assertEqual(
            resource_files(self.root, configurations, source_root=self.root / "source"),
            {"assets/demos/demo/image.png": payload},
        )
        self.write("source/archive/reviewed-image.png", b"Different source-tree image")
        with self.assertRaisesRegex(ValueError, "Browser asset hash mismatch"):
            resource_files(self.root, configurations, source_root=self.root / "source")

    def test_resource_hash_and_length_mismatches_are_rejected(self) -> None:
        payload, entry, configurations = self.resource_fixture()
        for field, invalid in (("sha256", "0" * 64), ("bytes", len(payload) + 1)):
            with self.subTest(field=field):
                modified = {**entry, field: invalid}
                self.write("demo/resources.json", json.dumps({"files": [modified]}))
                with self.assertRaisesRegex(ValueError, "Browser asset hash mismatch"):
                    resource_files(self.root, configurations)
        self.write("demo/resources.json", json.dumps({"files": [entry]}))
        self.write("demo/image.png", b"X" * len(payload))
        with self.assertRaisesRegex(ValueError, "Browser asset hash mismatch"):
            resource_files(self.root, configurations)

    def test_resource_manifest_and_asset_paths_cannot_escape(self) -> None:
        _, entry, configurations = self.resource_fixture()
        with self.assertRaisesRegex(ValueError, "Unsafe demo source path"):
            resource_files(self.root, {"demo": {"resource_manifest": "../private.json"}})
        entry["path"] = "../outside.png"
        self.write("demo/resources.json", json.dumps({"files": [entry]}))
        with self.assertRaisesRegex(ValueError, "Unsafe browser asset path"):
            resource_files(self.root, configurations)


if __name__ == "__main__":
    unittest.main()
