"""Contracts for language-specific walkthrough structure and retained anchors."""

from copy import deepcopy
from html import escape
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from scripts import build_site
from scripts.demo_walkthrough import demo_launch_url, demo_sections, demo_settings_table, render_demo


LAUNCH_URL = (
    "https://wspradar.org/?v=1&run=1&direction=rx&callsign=TARGET&qth=IO90HW"
    "&band=40m&from=2017-04-01T00%3A00Z&to=2017-05-01T00%3A00Z"
    "&mode=benchmark&station_bin=12h#wspradar-results-inspection"
)


class LocalizedWalkthroughTests(unittest.TestCase):
    def setUp(self):
        scratch = Path(__file__).resolve().parents[1] / ".tmp"
        scratch.mkdir(exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix="localized-sections-test-", dir=scratch)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = (
            "<!-- section: hero -->\n# Demo\n\nIntroduction.\n\n"
            "<!-- section: setup -->\n## Setup\n\nSetup explanation.\n\n"
            "<!-- section: step -->\n## Existing step\n\nComplete original explanation.\n\n"
            "<!-- section: child -->\n## Existing child\n\nComplete nested explanation.\n"
        )
        for language in ("en", "de"):
            (self.root / f"{language}.md").write_text(self.source, encoding="utf-8")
        text = {
            "eyebrow": "Demo", "period": "April 2017", "mode": "RX Benchmark",
            "nav_setup": "Setup", "evidence_title": "Evidence", "evidence_intro": "Details.",
        }
        self.config = {
            "markdown_paths": {"en": "en.md", "de": "de.md"},
            "languages": {language: deepcopy(text) for language in ("en", "de")},
            "show_setup_media": False,
            "show_setup_summary": False,
            "sections": [{
                "id": "step", "nav_label": {"en": "Step", "de": "Schritt"},
                "media_keys": ["original-figure"],
                "subsections": [{"id": "child", "layout": "full"}],
            }],
        }
        self.demo = {
            "id": "fixture",
            "launch_url": LAUNCH_URL,
            "settings": {"core_parameters": {
                "callsign": "TARGET", "qth": "IO90HW", "band": "40m",
                "time_selection": {"start_utc": "2017-04-01T00:00Z", "end_utc": "2017-05-01T00:00Z"},
            }},
        }
        self.builder = SimpleNamespace(
            demo_root=self.root,
            copy={language: {"contents": "Contents", "run_demo": "Run", "full_size": "Full size"}
                  for language in ("en", "de")},
            figures=[{
                "key": key, "demo_id": "fixture", "asset_path": key + ".png",
                "title": {"en": key, "de": key}, "alt": {"en": key, "de": key},
                "width": 100, "height": 100,
            } for key in ("original-figure", "english-figure")],
            screenshots=[],
            md=lambda value, language: "<p>" + escape(value) + "</p>",
        )

    def render(self, language):
        return render_demo(self.builder, language, self.demo, self.config,
                           build_site.button, build_site.route, build_site.APP_URL)

    def add_english_override(self):
        sections = deepcopy(self.config["sections"])
        sections[0].update(id="new-step", aliases=["step"], media_keys=["english-figure"])
        sections[0]["subsections"][0].update(id="new-child", aliases=["child"])
        self.config["sections_by_language"] = {"en": sections}
        (self.root / "en.md").write_text(
            self.source.replace("section: step", "section: new-step")
                       .replace("section: child", "section: new-child"), encoding="utf-8")

    def test_language_override_changes_structure_and_media_but_keeps_canonical_launch(self):
        original_config = deepcopy(self.config)
        german_before = self.render("de")
        self.add_english_override()
        german_after = self.render("de")
        english = self.render("en")
        self.assertEqual(german_after, german_before)
        self.assertEqual(self.config["sections"], original_config["sections"])
        self.assertIn('href="#new-step"', english)
        self.assertNotIn('href="#step"', english)
        self.assertIn('id="case-media-english-figure"', english)
        self.assertNotIn('id="case-media-original-figure"', english)
        self.assertIn(escape(LAUNCH_URL, quote=True), english)
        self.assertIn('id="case-media-original-figure"', german_after)
        self.assertNotIn("new-step", german_after)
        self.assertEqual(demo_launch_url(self.demo), LAUNCH_URL)
        self.assertIn(escape(LAUNCH_URL, quote=True), german_after)

    def test_aliases_preserve_old_targets_inside_their_respective_sections(self):
        self.add_english_override()
        page = self.render("en")
        for current, previous in (("new-step", "step"), ("new-child", "child")):
            self.assertIn(f'<section class="case-evidence-group" id="{current}">'
                          f'<span id="{previous}" aria-hidden="true"></span>', page)
            self.assertEqual(page.count(f'id="{previous}"'), 1)
        self.assertIn("Complete original explanation.", page)
        self.assertIn("Complete nested explanation.", page)

    def test_explicit_same_structure_preserves_default_html(self):
        baseline = {language: self.render(language) for language in ("en", "de")}
        self.config["sections_by_language"] = {"en": deepcopy(self.config["sections"])}
        for language in ("en", "de"):
            with self.subTest(language=language):
                self.assertEqual(self.render(language), baseline[language])

    def test_subsection_navigation_is_explicit_localized_and_preserves_content(self):
        baseline = {language: self.render(language) for language in ("en", "de")}
        child = self.config["sections"][0]["subsections"][0]
        child["nav_label"] = {"en": "Paper & Evidence", "de": "Publikationsvergleich"}
        for language in ("en", "de"):
            self.assertEqual(self.render(language), baseline[language])
        english_sections = deepcopy(self.config["sections"])
        english_sections[0]["subsections"][0]["show_in_nav"] = True
        self.config["sections_by_language"] = {"en": english_sections}
        english = self.render("en")
        added_link = '<li><a href="#child">Paper &amp; Evidence</a></li>'
        self.assertIn('<li><a href="#step">Step</a></li>' + added_link, english)
        self.assertEqual(english.count(added_link), 1)
        self.assertEqual(english.replace(added_link, ""), baseline["en"])
        self.assertEqual(self.render("de"), baseline["de"])

    def test_subsection_navigation_rejects_invalid_flags_and_missing_labels(self):
        child = self.config["sections"][0]["subsections"][0]
        for invalid in (None, 1, "true", []):
            with self.subTest(flag=invalid):
                child["show_in_nav"] = invalid
                with self.assertRaisesRegex(ValueError, "show_in_nav must be a boolean"):
                    self.render("en")
        child["show_in_nav"] = True
        for invalid in (None, [], {}, {"de": "Nur Deutsch"}, {"en": " "}, {"en": 1}):
            with self.subTest(label=invalid):
                child["nav_label"] = invalid
                with self.assertRaisesRegex(ValueError, "requires a navigation label for en"):
                    self.render("en")

    def test_unplaced_markdown_and_duplicate_media_use_the_selected_tree(self):
        self.add_english_override()
        with (self.root / "en.md").open("a", encoding="utf-8") as output:
            output.write("\n<!-- section: lost -->\n## Preserve this paragraph\n\nEvidence.\n")
        with self.assertRaisesRegex(ValueError, "Unplaced demo Markdown sections: lost"):
            self.render("en")
        self.render("de")
        child = self.config["sections_by_language"]["en"][0]["subsections"][0]
        child.pop("layout")
        child["media_keys"] = ["english-figure"]
        with self.assertRaisesRegex(ValueError, "Unknown or duplicate case-study media"):
            self.render("en")
        self.render("de")

    def test_invalid_language_maps_and_canonical_launches_are_rejected(self):
        for invalid in (None, [], "en", {"fr": []}):
            with self.subTest(invalid=invalid):
                config = {**self.config, "sections_by_language": invalid}
                with self.assertRaisesRegex(ValueError, "must map configured languages"):
                    demo_sections(config, "en")
        for invalid in (None, False, "https://example.com/", LAUNCH_URL.replace("run=1", "run=0")):
            with self.subTest(url=invalid):
                demo = {**self.demo, "launch_url": invalid}
                with self.assertRaisesRegex(ValueError, "reviewed full-configuration launch_url"):
                    demo_launch_url(demo)

    def test_site_authored_launch_overrides_are_rejected(self):
        for field, value in (("launch_url", LAUNCH_URL), ("launch_urls", {"en": LAUNCH_URL})):
            with self.subTest(field=field):
                self.config[field] = value
                with self.assertRaisesRegex(ValueError, "imported canonical configuration"):
                    self.render("en")
                self.config.pop(field)

    def test_footer_placeholder_tracks_the_same_canonical_launch_as_the_hero(self):
        with (self.root / "en.md").open("a", encoding="utf-8") as output:
            output.write("\n[Run]({{demo_launch_url}})\n")
        changed = LAUNCH_URL.replace("station_bin=12h", "station_bin=1h")
        self.demo["launch_url"] = changed
        page = self.render("en")
        self.assertEqual(page.count(escape(changed, quote=True)), 2)
        self.assertNotIn("{{demo_launch_url}}", page)
        self.assertNotIn(escape(LAUNCH_URL, quote=True), page)

    def configure_settings_table(self):
        self.config["settings_tables"] = {"en": {
            "columns": ["Setting", "Value", "Meaning"],
            "rows": [{"key": "minimum", "meaning": "Required support."}],
        }}
        self.demo["settings_summary"] = [{
            "key": "minimum", "label": {"en": "Minimum pairs", "de": "Mindestpaare"},
            "value": {"en": "2", "de": "2"},
        }]

    def test_generated_setting_values_follow_imported_summary_and_selected_language(self):
        self.configure_settings_table()
        self.assertIn("| Minimum pairs | **2** | Required support. |",
                      demo_settings_table(self.demo, self.config, "en"))
        self.demo["settings_summary"][0]["value"]["en"] = "7"
        updated = demo_settings_table(self.demo, self.config, "en")
        self.assertIn("**7**", updated)
        self.assertNotIn("**2**", updated)
        self.assertIsNone(demo_settings_table(self.demo, self.config, "de"))

    def test_generated_settings_table_requires_one_marker_and_preserves_surrounding_text(self):
        self.configure_settings_table()
        with self.assertRaisesRegex(ValueError, "exactly one matching Markdown marker"):
            self.render("en")
        path = self.root / "en.md"
        path.write_text(self.source.replace("Setup explanation.",
                        "Setup explanation.\n\n{{demo_settings_table}}\n\nKeep this conclusion."), encoding="utf-8")
        page = self.render("en")
        self.assertIn("Minimum pairs", page)
        self.assertIn("Setup explanation.", page)
        self.assertIn("Keep this conclusion.", page)
        self.assertNotIn("{{demo_settings_table}}", page)
        self.assertNotIn("Minimum pairs", self.render("de"))
        with path.open("a", encoding="utf-8") as output:
            output.write("\n{{demo_settings_table}}\n")
        with self.assertRaisesRegex(ValueError, "exactly one matching Markdown marker"):
            self.render("en")

    def test_generated_settings_table_rejects_missing_duplicate_or_unknown_rows(self):
        self.configure_settings_table()
        for summary in (None, {}, [], self.demo["settings_summary"] * 2):
            with self.subTest(summary=summary), self.assertRaises(ValueError):
                demo_settings_table({**self.demo, "settings_summary": summary}, self.config, "en")
        self.config["settings_tables"]["en"]["rows"].append(
            {"key": "minimum", "meaning": "Duplicate."})
        with self.assertRaisesRegex(ValueError, "Unknown, duplicate or invalid"):
            demo_settings_table(self.demo, self.config, "en")

    def test_invalid_or_colliding_section_ids_and_aliases_are_rejected(self):
        invalid_sections = [
            None, {}, [None], [{"id": "step", "aliases": "old"}],
            [{"id": "step", "aliases": ["bad anchor"]}],
            [{"id": "step", "aliases": ["setup"]}],
            [{"id": "objective"}],
            [{"id": "step", "aliases": ["objective"]}],
            [{"id": "step", "aliases": ["step"]}],
            [{"id": "step", "aliases": ["old", "old"]}],
            [{"id": "step"}, {"id": "step"}],
            [{"id": "step", "aliases": ["old"], "subsections": [{"id": "old"}]}],
            [{"id": "step", "subsections": {}}],
        ]
        for sections in invalid_sections:
            with self.subTest(sections=sections):
                config = {**self.config, "sections_by_language": {"en": sections}}
                with self.assertRaises(ValueError):
                    demo_sections(config, "en")


if __name__ == "__main__":
    unittest.main()
