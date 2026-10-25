"""Canonical alternate demo launches and their requested placements."""

from copy import deepcopy
from urllib.parse import parse_qs, urlsplit
import unittest

from scripts import build_site, demo_walkthrough
from tests.test_demo_walkthrough import Document


class DemoLaunchActionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = build_site.SiteBuilder()
        cls.demo = next(demo for demo in cls.builder.demos if demo["id"] == "milazzo_tx_buddy")

    def render(self, language="en", config=None):
        body = demo_walkthrough.render_demo(
            self.builder, language, self.demo,
            config or self.builder.demo_walkthroughs["demos"][self.demo["id"]],
            build_site.button, build_site.route, build_site.APP_URL)
        suffix = "demos/" + self.demo["id"] + "/"
        self.builder.page(language, suffix, "Demo launch actions", body, "demos")
        return Document(self.builder.pages[language + "/" + suffix + "index.html"])

    def test_milazzo_has_adjacent_canonical_rx_tx_actions_and_repeated_tx_heading_action(self):
        document = self.render()
        group = document.find(css_class="case-launch-actions")
        self.assertEqual(len(group), 1)
        links = group[0].descendants("a")
        self.assertEqual([link.text for link in links],
                         ["Run in WSPRadar App · RX ↗", "Run in WSPRadar App · TX ↗"])
        expected = [demo_walkthrough.demo_launch_url(self.demo),
                    demo_walkthrough.demo_launch_url(self.demo, "tx")]
        self.assertEqual([link.attributes["href"] for link in links], expected)
        queries = [parse_qs(urlsplit(url).query) for url in expected]
        self.assertEqual([query.pop("direction") for query in queries], [["rx"], ["tx"]])
        self.assertEqual(queries[0], queries[1])
        self.assertEqual(queries[0]["selected_station"], ["VE6PDQ@DO34IR"])
        heading = document.find(css_class="case-step-heading-with-action")
        self.assertEqual(len(heading), 1)
        self.assertEqual(heading[0].descendants("h3")[0].text, "Reverse the direction: Figure 7")
        self.assertEqual(heading[0].descendants("a")[0].attributes["href"], expected[1])
        launches = [anchor for anchor in document.find(css_class="case-study")[0].descendants("a")
                    if anchor.attributes.get("href") in expected]
        self.assertGreater(len(launches), len(links))
        for anchor in launches:
            self.assertEqual(anchor.attributes.get("target"), "_blank")
            self.assertTrue({"noopener", "noreferrer"}.issubset(anchor.attributes.get("rel", "").split()))

    def test_unconfigured_language_keeps_the_single_default_action(self):
        document = self.render("de")
        self.assertFalse(document.find(css_class="case-launch-actions"))
        self.assertFalse(document.find(css_class="case-step-heading-with-action"))
        buttons = document.find(css_class="button")
        self.assertEqual([button.attributes["href"] for button in buttons], [self.demo["launch_url"]])

    def test_unknown_or_invalid_imported_variants_fail_closed(self):
        for variant in (None, [], "", "../tx", "missing"):
            with self.subTest(variant=variant), self.assertRaises(ValueError):
                demo_walkthrough.demo_launch_url(self.demo, variant)
        for variants in ([], {"tx": "javascript:alert(1)"}, {"tx": 12},
                         {"tx": self.demo["launch_url"].replace("run=1", "run=0")}):
            with self.subTest(variants=variants), self.assertRaises(ValueError):
                demo_walkthrough.demo_launch_url({**self.demo, "launch_variants": variants}, "tx")

    def test_website_actions_cannot_override_canonical_urls(self):
        for action in ({}, {"variant": "tx", "label": ""},
                       {"variant": "tx", "label": "Run", "url": self.demo["launch_url"]},
                       {"variant": "missing", "label": "Run"}):
            with self.subTest(action=action), self.assertRaises(ValueError):
                demo_walkthrough.demo_launch_action(self.demo, action, build_site.button)
        for value in ([], {}, "tx"):
            config = deepcopy(self.builder.demo_walkthroughs["demos"][self.demo["id"]])
            config["launch_actions"]["en"] = value
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "launch_actions"):
                self.render(config=config)


if __name__ == "__main__":
    unittest.main()
