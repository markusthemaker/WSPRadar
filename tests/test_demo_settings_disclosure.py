"""Settings previews preserve canonical rows and use a native disclosure."""

from copy import deepcopy
import unittest

from scripts.build_site import render_markdown
from scripts.demo_walkthrough import demo_settings_table, settings_table_disclosure
from tests.test_demo_walkthrough import Document


class SettingsDisclosureTests(unittest.TestCase):
    def setUp(self):
        self.demo = {"settings_summary": [
            {"key": f"setting-{number}", "label": {"en": f"Setting {number}", "de": f"Wert {number}"},
             "value": {"en": str(number * 10), "de": str(number * 10)}}
            for number in range(1, 8)
        ]}
        self.config = {
            "languages": {"en": {}, "de": {}},
            "settings_tables": {"en": {
                "columns": ["Setting", "Value", "Meaning"],
                "rows": [{"key": f"setting-{number}", "meaning": f"Retained explanation {number}."}
                         for number in range(1, 8)],
            }},
            "settings_table_disclosure": {"en": {"preview_rows": 5, "summary": "Show all settings"}},
        }

    def render(self, lang="en"):
        table = demo_settings_table(self.demo, self.config, lang)
        return settings_table_disclosure(table, self.config, lang,
                                         lambda value: render_markdown(value, lang, {}))

    def test_preview_is_first_configured_rows_and_complete_table_is_preserved(self):
        page = self.render()
        document = Document(page)
        preview = document.find(css_class="case-settings-preview")[0]
        complete = document.find(css_class="case-settings-complete")[0]
        preview_rows, complete_rows = preview.descendants("tr"), complete.descendants("tr")
        self.assertEqual(len(preview_rows), 6)
        self.assertEqual(len(complete_rows), 8)
        self.assertEqual([row.text for row in preview_rows], [row.text for row in complete_rows[:6]])
        original = render_markdown(demo_settings_table(self.demo, self.config, "en"), "en", {})
        self.assertEqual(page.count(original), 1)
        details = document.find(tag="details")[0]
        self.assertNotIn("open", details.attributes)
        self.assertEqual(details.children[0].tag, "summary")
        self.assertEqual(details.children[0].text, "Show all settings")

    def test_configuration_order_and_canonical_updates_reach_both_views(self):
        self.config["settings_tables"]["en"]["rows"].reverse()
        self.demo["settings_summary"][-1]["value"]["en"] = "Updated <value>"
        document = Document(self.render())
        for css_class in ("case-settings-preview", "case-settings-complete"):
            first = document.find(css_class=css_class)[0].descendants("tr")[1]
            self.assertEqual([cell.text for cell in first.descendants("td")],
                             ["Setting 7", "Updated <value>", "Retained explanation 7."])

    def test_absent_locale_is_unchanged_and_summary_is_escaped(self):
        self.assertIsNone(self.render("de"))
        self.config["settings_table_disclosure"]["en"]["summary"] = 'Show <all> & "settings"'
        page = self.render()
        self.assertIn("Show &lt;all&gt; &amp; &quot;settings&quot;", page)
        self.assertEqual(Document(page).find(tag="all"), [])
        self.config.pop("settings_table_disclosure")
        self.assertIsNone(self.render())

    def test_invalid_shape_preview_counts_and_languages_are_rejected(self):
        original = deepcopy(self.config)
        specs = [None, False, [], {}, {"preview_rows": 5}, {"preview_rows": 5, "summary": "",},
                 {"preview_rows": 5, "summary": "  "}, {"preview_rows": 5, "summary": False},
                 {"preview_rows": 5, "summary": "More", "unknown": True}]
        specs += [{"preview_rows": value, "summary": "More"} for value in (True, "5", 1.5, 0, -1, 7, 8)]
        for invalid in specs:
            with self.subTest(spec=invalid):
                self.config = deepcopy(original)
                self.config["settings_table_disclosure"]["en"] = invalid
                with self.assertRaises(ValueError):
                    self.render()
        for invalid in (None, [], {"fr": {"preview_rows": 5, "summary": "More"}}):
            with self.subTest(languages=invalid):
                self.config = deepcopy(original)
                self.config["settings_table_disclosure"] = invalid
                with self.assertRaises(ValueError):
                    self.render()

    def test_disclosure_requires_a_full_canonical_table(self):
        self.config.pop("settings_tables")
        with self.assertRaisesRegex(ValueError, "requires a configured settings table"):
            self.render()

    def test_current_setting_selector_preserves_legacy_imported_labels_and_values(self):
        legacy = deepcopy(self.demo["settings_summary"][0])
        legacy["key"] = "min_joint_spots_per_station"
        self.demo["settings_summary"] = [legacy]
        self.config["settings_tables"]["en"]["rows"] = [
            {"key": "min_spot_pairs_per_station", "meaning": "Retained explanation."},
        ]
        original_demo, original_config = deepcopy(self.demo), deepcopy(self.config)
        table = demo_settings_table(self.demo, self.config, "en")
        self.assertIn("| Setting 1 | **10** | Retained explanation. |", table)
        self.assertEqual(self.demo, original_demo)
        self.assertEqual(self.config, original_config)
        self.config["settings_tables"]["en"]["rows"][0]["key"] = legacy["key"]
        self.assertEqual(demo_settings_table(self.demo, self.config, "en"), table)

    def test_current_imported_setting_takes_precedence_over_the_legacy_alias(self):
        legacy, current = deepcopy(self.demo["settings_summary"][:2])
        legacy["key"] = "min_joint_spots_per_station"
        current["key"] = "min_spot_pairs_per_station"
        self.demo["settings_summary"] = [legacy, current]
        self.config["settings_tables"]["en"]["rows"] = [
            {"key": current["key"], "meaning": "Current canonical row."},
        ]
        table = demo_settings_table(self.demo, self.config, "en")
        self.assertIn("| Setting 2 | **20** | Current canonical row. |", table)
        self.assertNotIn("Setting 1", table)

    def test_legacy_alias_does_not_allow_duplicate_or_unknown_setting_selections(self):
        self.demo["settings_summary"][0]["key"] = "min_joint_spots_per_station"
        for selected_keys in (
                ["min_spot_pairs_per_station", "min_joint_spots_per_station"],
                ["min_spot_pairs_per_station", "min_spot_pairs_per_station"],
                ["unknown_setting"]):
            self.config["settings_tables"]["en"]["rows"] = [
                {"key": key, "meaning": "Retained explanation."} for key in selected_keys
            ]
            with self.subTest(keys=selected_keys), self.assertRaisesRegex(
                    ValueError, "Unknown, duplicate or invalid"):
                demo_settings_table(self.demo, self.config, "en")


if __name__ == "__main__":
    unittest.main()
