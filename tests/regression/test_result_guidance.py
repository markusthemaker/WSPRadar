"""Focused regression contracts for result interpretation popovers."""

import ast
from collections import Counter
from html import escape
from pathlib import Path
import re
from string import Formatter

import pytest
from streamlit.testing.v1 import AppTest

from core.analysis_context import (
    AnalysisContext,
    COMPARISON_LOCAL_NEIGHBORHOOD,
    COMPARISON_NONE,
    COMPARISON_REFERENCE_STATION,
    LOCAL_BENCHMARK_MEDIAN,
)
from i18n import GUIDED_INPUTS, RESULT_GUIDANCE, T
from ui.result_guidance import (
    RESULT_GUIDANCE_COMPARISON_EVIDENCE,
    RESULT_GUIDANCE_CONTEXT,
    RESULT_GUIDANCE_DOWNLOAD,
    RESULT_GUIDANCE_DRILLDOWN,
    RESULT_GUIDANCE_MAP,
    RESULT_GUIDANCE_OUTLIER_FOCUS,
    RESULT_GUIDANCE_OUTLIER_REPORT,
    RESULT_GUIDANCE_SEGMENT,
    RESULT_GUIDANCE_SELECTED_STATIONS,
    RESULT_GUIDANCE_STATION_INSIGHTS,
    RESULT_GUIDANCE_SUCCESS_EVIDENCE,
    RESULT_GUIDANCE_TEMPORAL_EVIDENCE,
    RESULT_GUIDANCE_TEMPORAL_EVIDENCE_COVERAGE,
    build_result_guidance,
)


COMPARE_SECTIONS = (
    RESULT_GUIDANCE_CONTEXT,
    RESULT_GUIDANCE_MAP,
    RESULT_GUIDANCE_SEGMENT,
    RESULT_GUIDANCE_COMPARISON_EVIDENCE,
    RESULT_GUIDANCE_TEMPORAL_EVIDENCE,
    RESULT_GUIDANCE_TEMPORAL_EVIDENCE_COVERAGE,
    RESULT_GUIDANCE_OUTLIER_REPORT,
    RESULT_GUIDANCE_OUTLIER_FOCUS,
    RESULT_GUIDANCE_STATION_INSIGHTS,
    RESULT_GUIDANCE_SELECTED_STATIONS,
    RESULT_GUIDANCE_DRILLDOWN,
    RESULT_GUIDANCE_DOWNLOAD,
)

SUCCESS_SECTIONS = (
    RESULT_GUIDANCE_CONTEXT,
    RESULT_GUIDANCE_MAP,
    RESULT_GUIDANCE_SEGMENT,
    RESULT_GUIDANCE_SUCCESS_EVIDENCE,
    RESULT_GUIDANCE_TEMPORAL_EVIDENCE,
    RESULT_GUIDANCE_STATION_INSIGHTS,
    RESULT_GUIDANCE_SELECTED_STATIONS,
    RESULT_GUIDANCE_DRILLDOWN,
    RESULT_GUIDANCE_DOWNLOAD,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def _context_layout_headings(translations, *, is_compare):
    """Name the actual section headers expected in the top-level reading path."""
    heading_keys = {
        "map_heading": "hdr_results_map_view",
        "segment_heading": "hdr_results_segment_inspector",
        "evidence_heading": (
            "hdr_results_comparison_evidence" if is_compare else "hdr_results_success_evidence"
        ),
        "temporal_heading": "hdr_results_temporal_evidence",
        "stations_heading": "lbl_insights",
        "selected_heading": "hdr_results_selected_station_evidence",
        "drilldown_heading": "hdr_results_drilldown",
    }
    return {field: escape(translations[key]) for field, key in heading_keys.items()}


def _flatten_catalog(catalog, prefix=()):
    """Return every nested catalog leaf keyed by its complete semantic path."""
    leaves = {}
    for key, value in catalog.items():
        path = (*prefix, key)
        if isinstance(value, dict):
            leaves.update(_flatten_catalog(value, path))
        else:
            leaves[path] = value
    return leaves


def _format_fields(template):
    """Return all named replacement fields used by one localized template."""
    return {
        field_name
        for _literal, field_name, _format_spec, _conversion in Formatter().parse(
            template
        )
        if field_name
    }


def _plain_guidance(guidance):
    """Ignore emphasis and paragraph spacing when checking prose meaning."""
    unstyled = re.sub(r"</?strong(?:\s+[^>]*)?>", "", guidance).replace("**", "")
    return " ".join(unstyled.split())


def _build_guidance(
    section_id,
    *,
    language="en",
    analysis_id="RX_COMP",
    is_compare=True,

    analysis_context=None,
    selected_station_count=None,
    allows_multiple_station_selection=False,
):
    """Build guidance with the matching localized general translation catalog."""
    return build_result_guidance(
        section_id,
        language=language,
        translations=T[language],
        analysis_id=analysis_id,
        is_compare=is_compare,

        analysis_context=analysis_context,
        selected_station_count=selected_station_count,
        allows_multiple_station_selection=(
            allows_multiple_station_selection
        ),
    )


@pytest.mark.parametrize("language", ("en", "de"))
@pytest.mark.parametrize("direction", ("rx", "tx"))
def test_performance_guidance_counts_target_only_success_and_names_endpoint_roles(language, direction):
    """Keep detailed opportunity and outcome definitions beside the evidence."""
    map_guidance = _plain_guidance(_build_guidance(
        RESULT_GUIDANCE_MAP, language=language,
        analysis_id=f"{direction.upper()}_SUCCESS", is_compare=False,
    ))
    drilldown = _plain_guidance(_build_guidance(
        RESULT_GUIDANCE_DRILLDOWN, language=language,
        analysis_id=f"{direction.upper()}_SUCCESS", is_compare=False,
    ))
    for label in (
        T[language][f"map_success_{direction}_opportunity_target"],
        T[language][f"map_success_{direction}_opportunity_counter"],
    ):
        assert label in map_guidance
    if language == "en":
        for phrase in ("callsign and reported locator", "in one WSPR cycle",
                       "Target activity is confirmed", "confirms both endpoints",
                       "Target-only", "already included once", "success count and successful SNR",
                       "was listening"):
            assert phrase in drilldown
        expected = (
            ("another eligible receiver to report the same transmitter",
             "Cycles without evidence of Target activity are excluded")
            if direction == "rx" else
            ("same receiver to report another qualifying transmitter",
             "insufficient activity evidence remains unknown and excluded")
        )
        assert "does not enter this rate" not in drilldown
    else:
        for phrase in ("Rufzeichen und gemeldeten Locator", "in einem WSPR-Zyklus",
                       "bestätigter Target-Aktivität", "bestätigt beide Endpunkte",
                       "Target-only", "bereits einmal", "Erfolgsanzahl und im erfolgreichen SNR",
                       "zugehört hat"):
            assert phrase in drilldown
        expected = (
            ("anderer geeigneter Empfänger denselben Sender meldet",
             "Zyklen ohne Nachweis der Target-Aktivität werden ausgeschlossen")
            if direction == "rx" else
            ("derselbe Empfänger einen anderen qualifizierenden Sender meldet",
             "unzureichend belegte Aktivität bleibt unbekannt und ausgeschlossen")
        )
        assert "fließt aber nicht in diese Rate ein" not in drilldown
    for phrase in expected:
        assert phrase in drilldown
    segment = _plain_guidance(_build_guidance(
        RESULT_GUIDANCE_SEGMENT, language=language,
        analysis_id=f"{direction.upper()}_SUCCESS", is_compare=False,
    ))
    assert (
        "successful opportunities divided by all confirmed opportunities" if language == "en"
        else "erfolgreiche Gelegenheiten durch alle bestätigten Gelegenheiten"
    ) in segment


def test_result_guidance_catalog_has_recursive_bilingual_placeholder_parity():
    """Keep every nested English and German guidance leaf interchangeable."""
    assert set(RESULT_GUIDANCE) == {"en", "de"}
    english_leaves = _flatten_catalog(RESULT_GUIDANCE["en"])
    german_leaves = _flatten_catalog(RESULT_GUIDANCE["de"])

    assert english_leaves.keys() == german_leaves.keys()
    for path in sorted(english_leaves):
        english_value = english_leaves[path]
        german_value = german_leaves[path]
        assert isinstance(english_value, str), path
        assert isinstance(german_value, str), path
        assert english_value.strip(), path
        assert german_value.strip(), path
        assert _format_fields(english_value) == _format_fields(
            german_value
        ), path
        assert _format_fields(english_value) <= {
            "counter",
                "formula",
                "peer_type",
                "radius",
                "section",
                "station_counter",
                "station_target",
                "map_heading",
                "segment_heading",
                "evidence_heading",
                "temporal_heading",
                "stations_heading",
                "selected_heading",
                "drilldown_heading",
            }, path

    for language in ("en", "de"):
        assert RESULT_GUIDANCE[language]["sections"]
        for section_key, section_content in RESULT_GUIDANCE[language][
            "sections"
        ].items():
            assert set(section_content) == {"read", "limits"}, (
                language,
                section_key,
            )
            read_text = section_content["read"]
            if section_key.startswith("context_"):
                read_text += "\n\n" + RESULT_GUIDANCE[language]["context_layout"].format(
                    **_context_layout_headings(T[language], is_compare=section_key.endswith("compare"))
                )
            assert len(section_content["limits"]) < len(read_text), (language, section_key)
            for part in section_content.values():
                assert part.count('<strong class="defined-term">') == part.count(
                    "</strong>"
                ), (language, section_key)


@pytest.mark.parametrize(
    ("catalog_name", "catalog"),
    (
        ("translations", T),
        ("result_guidance", RESULT_GUIDANCE),
        ("guided_inputs", GUIDED_INPUTS),
    ),
)
def test_user_visible_catalogs_separate_em_dashes_from_words(
    catalog_name,
    catalog,
):
    """Prevent the global monospace theme from turning prose dashes into joins."""
    for path, catalog_value in _flatten_catalog(catalog).items():
        if not isinstance(catalog_value, str):
            continue
        assert re.search(r"(?<!\s)—|—(?!\s)", catalog_value) is None, (
            catalog_name,
            path,
        )


def test_retired_compare_view_localization_and_guidance_are_absent():
    """Do not retain copy for removed Compare figures or dead aliases."""
    retired_guidance_names = {
        "en": (
            "ΔSNR Change from Station Baseline",
            "Path Agreement and Within-Path Consistency",
        ),
        "de": (
            "ΔSNR-Änderung gegenüber der Stationsbasislinie",
            "Übereinstimmung und Konsistenz der Funkwege",
        ),
    }

    for language in ("en", "de"):
        assert not any(
            key.startswith("fig_compare_delta_change_")
            for key in T[language]
        )
        assert not any(
            key.startswith("fig_compare_path_consistency_")
            for key in T[language]
        )
        assert "fig_compare_coverage_unavailable" not in T[language]
        assert (
            "fig_selected_compare_coverage_utc_hour_subtitle"
            not in T[language]
        )
        complete_guidance = " ".join(
            text
            for section in RESULT_GUIDANCE[language]["sections"].values()
            for text in section.values()
        )
        for retired_name in retired_guidance_names[language]:
            assert retired_name not in complete_guidance


@pytest.mark.parametrize(
    "section_key",
    (
        "temporal_evidence_joint",
        "selected_compare_joint",
    ),
)
def test_compare_temporal_and_selected_guidance_uses_full_readability_budget(
    section_key,
):
    """Keep detailed Compare help substantive and below a generous ceiling."""
    for language in ("en", "de"):
        item = RESULT_GUIDANCE[language]["sections"][section_key]
        copy_count = len(item["read"]) + len(item["limits"])
        assert 1000 <= copy_count <= 2400, (
            language,
            section_key,
            copy_count,
        )


@pytest.mark.parametrize("section_key", ("temporal_evidence_joint", "selected_compare_joint"))
def test_compare_temporal_guidance_explains_full_window_and_blank_intervals(section_key):
    """Explain selected-window geometry without treating missing pairs as zero."""
    english = RESULT_GUIDANCE["en"]["sections"][section_key]["read"]
    german = RESULT_GUIDANCE["de"]["sections"][section_key]["read"]
    for phrase in ("UTC window", "begin", "last may be shorter", "Blank intervals",
                   "no Joint evidence", "not a 0 dB"):
        assert phrase in english
    for phrase in ("UTC-Zeitfenster", "beginnen", "letzte", "kürzer",
                   "Leere Intervalle", "keine Joint-Evidenz", "0 dB"):
        assert phrase in german
    coverage = RESULT_GUIDANCE["en"]["sections"]["temporal_evidence_coverage_joint"]["read"]
    assert "Only Target and Only Reference" in coverage


def test_selected_compare_guidance_names_the_rendered_coverage_units():
    """Keep one-path coverage on retained cycles with date-averaged hourly bars."""
    for language, phrases in {
        "en": ("retained WSPR cycles", "per represented date", "all three outcomes"),
        "de": ("berücksichtigte WSPR-Zyklen", "je berücksichtigtem Tag", "aller drei Outcomes"),
    }.items():
        combined = _plain_guidance(" ".join(
            RESULT_GUIDANCE[language]["sections"]["selected_compare_joint"].values()
        ))
        for phrase in phrases:
            assert phrase in combined


def test_joint_temporal_guidance_explains_the_figures_and_target_favored_gate():
    """Keep paired-metric help separate from coverage weighting and Target gate."""
    phrases = {
        "en": {
            "temporal_evidence_joint": (
                "median of all qualifying Joint Spots", "relative observation concentration",
                "nonlinear dB axis", "at least two dates",
                "time from left to right and ΔSNR vertically",
                "blue cells contain a lower concentration", "orange/red cells a higher concentration",
            ),
            "temporal_evidence_coverage_joint": (
                "each station one vote", "blue line", "amber line",
                "total height counts stations", "one remote station in one WSPR cycle",
                "Joint units divided by all retained units", "daily average",
                "each distinct station one rate vote", "observed Target activity",
                "decoded a qualifying signal in RX", "decoded somewhere in TX",
                "no equivalent gate", "not symmetric wins or losses",
                "Joint Spots already contain both sides", "pairability, not Target success",
            ),
            "selected_compare_joint": (
                "one selected {peer_type} path", "Every Joint Spot has equal weight",
                "Target-offline cycles are excluded", "without an equivalent Reference activity gate",
                "Swapping roles can change coverage", "paired differences reverse sign",
                "Joint Spots already contain both sides",
            ),
        },
        "de": {
            "temporal_evidence_joint": (
                "Median aller qualifizierenden Joint Spots", "relative Beobachtungsdichte",
                "nichtlinearen dB-Achse", "mindestens zwei Tagen",
                "Zeit von links nach rechts und ΔSNR senkrecht",
                "Blaue Felder enthalten eine geringere Dichte", "orange und rote eine höhere",
            ),
            "temporal_evidence_coverage_joint": (
                "jede Station eine Stimme", "blaue Linie", "bernsteinfarbene Linie",
                "Gesamthöhe zählt daher Stationen", "jeweils eine Gegenstation in einem WSPR-Zyklus",
                "Joint-Einheiten geteilt durch alle beibehaltenen Einheiten",
                "durchschnittliche tägliche Beteiligung", "einer Ratenstimme",
                "beobachteter Target-Aktivität", "qualifizierendes Signal decodiert",
                "irgendwo decodiert", "kein entsprechendes Gate",
                "keine symmetrischen Siege oder Niederlagen",
                "Joint Spots enthalten bereits beide Seiten", "Paarbarkeit, nicht den Target-Erfolg",
            ),
            "selected_compare_joint": (
                "einem ausgewählten {peer_type}-Funkweg", "Jeder Joint Spot hat hier dasselbe Gewicht",
                "Zyklen ohne Target-Aktivität werden ausgeschlossen",
                "ohne entsprechende Aktivitätsbedingung für die Referenz",
                "Ein Rollentausch kann die Abdeckung verändern",
                "gepaarte Differenzen wechseln das Vorzeichen",
                "Joint Spots enthalten bereits beide Seiten",
            ),
        },
    }
    for language, items in phrases.items():
        for key, expected in items.items():
            combined = _plain_guidance(" ".join(RESULT_GUIDANCE[language]["sections"][key].values()))
            for phrase in expected:
                assert phrase in combined, (language, key, phrase)




def test_directional_success_temporal_guidance_stays_near_readability_target():
    """Bound readable prose without charging HTML and Markdown styling as text."""
    for language in ("en", "de"):
        for direction in ("rx", "tx"):
            item = RESULT_GUIDANCE[language]["sections"][
                f"success_temporal_evidence_{direction}"
            ]
            assert len(_plain_guidance(" ".join(item.values()))) <= 2700


@pytest.mark.parametrize("language", ("en", "de"))
@pytest.mark.parametrize("section_key", (
    "temporal_evidence_joint", "selected_compare_joint",
    "success_temporal_evidence_rx", "success_temporal_evidence_tx",
    "selected_success_rx", "selected_success_tx",
))
def test_temporal_iqr_guidance_defines_population_support_and_interpretation(language, section_key):
    """Preserve middle-half spread, minimum support, and the actual population."""
    item = RESULT_GUIDANCE[language]["sections"][section_key]
    text = _plain_guidance(" ".join(item.values()))
    for phrase in (("Q1–Q3", "middle 50%", "five", "not a confidence interval")
                   if language == "en"
                   else ("Q1–Q3", "mittleren 50 %", "fünf", "kein Konfidenzintervall")):
        assert phrase in text
    if section_key.startswith("success_temporal"):
        role = "receiver" if section_key.endswith("tx") else "station"
        german_role = "Empfänger" if section_key.endswith("tx") else "Station"
        expected = ((f"one median per {role} in each chronological bin",
                     f"one median per {role}, date, and hour")
                    if language == "en" else
                    (f"einen Median je {german_role} in jedem chronologischen Bin",
                     f"einen Median je {german_role}, Datum und Stunde"))
    elif section_key.startswith("selected_success"):
        expected = (("chronologically", "date-hour medians")
                    if language == "en" else ("im Zeitverlauf", "Datum-Stunden-Mediane"))
    else:
        expected = ("Joint Spots",)
    for phrase in expected:
        assert phrase in text


@pytest.mark.parametrize(
    (
        "language",
        "analysis_id",
        "direction",
        "success_outcome",
        "counter_outcome",
        "snr_figure_name",
        "temporal_figure_name",
        "replacement_wording",
    ),
    (
        (
            "en",
            "RX_ABS",
            "rx",
            "Heard by Target",
            "Heard by others only",
            "Selected Station SNR Evidence",
            "Selected Station Temporal Evidence",
            "replaces it",
        ),
        (
            "en",
            "TX_ABS",
            "tx",
            "Target heard",
            "Other signals heard only",
            "Selected Station SNR Evidence",
            "Selected Station Temporal Evidence",
            "replaces it",
        ),
        (
            "de",
            "RX_ABS",
            "rx",
            "Vom Target gehört",
            "Nur von anderen gehört",
            "SNR-Evidenz der ausgewählten Station",
            "Zeitliche Evidenz der ausgewählten Station",
            "ersetzt ihn",
        ),
        (
            "de",
            "TX_ABS",
            "tx",
            "Target gehört",
            "Nur andere Signale gehört",
            "SNR-Evidenz der ausgewählten Station",
            "Zeitliche Evidenz der ausgewählten Station",
            "ersetzt ihn",
        ),
    ),
)
def test_success_selected_guidance_routes_one_station(
    language,
    analysis_id,
    direction,
    success_outcome,
    counter_outcome,
    snr_figure_name,
    temporal_figure_name,
    replacement_wording,
):
    """Route exact direction-specific singleton guidance from semantic state."""
    guidance = _build_guidance(
        RESULT_GUIDANCE_SELECTED_STATIONS,
        language=language,
        analysis_id=analysis_id,
        is_compare=False,
        analysis_context=AnalysisContext(),
        selected_station_count=1,
    )
    expected_key = f"selected_success_{direction}"
    expected_item = RESULT_GUIDANCE[language]["sections"][expected_key]

    assert expected_item["read"] in guidance
    assert expected_item["limits"] in guidance
    assert success_outcome in guidance
    assert counter_outcome in guidance
    assert snr_figure_name in guidance
    assert temporal_figure_name in guidance
    assert replacement_wording in guidance
    assert "Selected Path Summary" not in guidance
    assert "Zusammenfassung des ausgewählten Funkwegs" not in guidance
    assert "combined observation-weighted selection" not in guidance
    assert "kombinierte beobachtungsgewichtete Auswahl" not in guidance


@pytest.mark.parametrize(
    "selected_station_count",
    (None, 0, -1, False, 1.5, "2", 2, 5),
)
def test_success_selected_guidance_requires_exactly_one_station(
    selected_station_count,
):
    """Reject any cardinality that violates Success singleton selection."""
    with pytest.raises(
        ValueError,
        match="requires exactly one selected station",
    ):
        _build_guidance(
            RESULT_GUIDANCE_SELECTED_STATIONS,
            analysis_id="RX_ABS",
            is_compare=False,
            analysis_context=AnalysisContext(),
            selected_station_count=selected_station_count,
        )


def test_compare_selected_guidance_routes_single_and_combined_station_copy():
    """Describe both one-path and combined Compare selections."""
    guidance = _build_guidance(
        RESULT_GUIDANCE_SELECTED_STATIONS,
        analysis_id="RX_COMP",
        is_compare=True,
        analysis_context=AnalysisContext(
            comparison_mode=COMPARISON_REFERENCE_STATION
        ),
        selected_station_count=1,
    )

    assert "one selected TX path" in guidance
    assert "one selected TX path" in guidance
    assert "chosen TX stations" not in guidance
    assert not _format_fields(guidance)

    for selected_station_count in (None, 0, -1, False, 1.5, "2"):
        with pytest.raises(
            ValueError,
            match="requires exactly one selected station",
        ):
            _build_guidance(
                RESULT_GUIDANCE_SELECTED_STATIONS,
                analysis_id="RX_COMP",
                is_compare=True,
                analysis_context=AnalysisContext(
                    comparison_mode=COMPARISON_REFERENCE_STATION
                ),
                selected_station_count=selected_station_count,
            )

    combined_guidance = _build_guidance(
        RESULT_GUIDANCE_SELECTED_STATIONS,
        analysis_id="RX_COMP",
        is_compare=True,
        analysis_context=AnalysisContext(
            comparison_mode=COMPARISON_REFERENCE_STATION
        ),
        selected_station_count=2,
        allows_multiple_station_selection=True,
    )
    assert "selected TX paths" in combined_guidance
    assert (
        "path with more paired observations has more influence"
        in _plain_guidance(combined_guidance)
    )
    assert "one selected TX path" not in combined_guidance
    assert not _format_fields(combined_guidance)


def test_compare_station_insights_guidance_gates_multi_selection_copy():
    """Route single-row and combined-path instructions only by selection capability."""
    context = AnalysisContext(comparison_mode=COMPARISON_REFERENCE_STATION)
    single = _build_guidance(RESULT_GUIDANCE_STATION_INSIGHTS, analysis_context=context)
    multi = _build_guidance(RESULT_GUIDANCE_STATION_INSIGHTS, analysis_context=context,
                            allows_multiple_station_selection=True)
    assert "select one row to examine that path" in single
    assert "several paths" not in single
    assert "several paths to inspect their combined evidence" in multi
    assert "does not give each path equal weight" in multi


def test_outlier_report_guidance_uses_shared_gates_and_descriptive_classes():
    """Preserve detector qualification, report meanings, and noncausal interpretation."""
    contracts = {
        "en": ("excluding the candidate itself", "observed ΔSNR minus that baseline",
               "All use the same configured requirements", "median departure", "robust z-score",
               "stability between the before/after baselines", "both point-level departure requirements",
               "weaker observations may remain", "does not classify them as normal",
               "not established physical events", "Target, Reference, or both changed"),
        "de": ("der Kandidat selbst bleibt dabei ausgeschlossen", "abzüglich dieser Baseline",
               "Für alle gelten dieselben konfigurierten Anforderungen", "Medianabweichung",
               "robusten z-Wert", "Stabilität der Baselines davor und danach",
               "beide Abweichungsanforderungen auf Einzelpunktebene",
               "schwächere Beobachtungen", "nicht als normal eingestuft",
               "keine nachgewiesenen physischen Ereignisse", "Target, Referenz oder beide"),
    }
    for language, phrases in contracts.items():
        item = RESULT_GUIDANCE[language]["sections"]["outlier_report"]
        text = _plain_guidance(" ".join(item.values()))
        for phrase in phrases:
            assert phrase in text, (language, phrase)
        for title in (
            ("Expected local ΔSNR", "Observed median ΔSNR", "Largest single-cycle departure")
            if language == "en" else
            ("Erwartetes lokales ΔSNR", "Beobachteter ΔSNR-Median", "Größte Einzelzyklusabweichung")
        ):
            assert title in text
        tooltip = T[language]["tt_report_delta_snr_outlier_candidates"]
        assert ("does not remove evidence" if language == "en"
                else "es entfernt keine Evidenz") in tooltip
        guidance = _build_guidance(RESULT_GUIDANCE_OUTLIER_REPORT, language=language,
            analysis_context=AnalysisContext(comparison_mode=COMPARISON_REFERENCE_STATION))
        assert item["read"] in guidance and item["limits"] in guidance
        assert ("robust-z guides" if language == "en" else "Symmetrische Hilfslinien") not in text


def test_drilldown_focus_copy_defines_centered_native_evidence_and_detector_guides():
    """Keep the focused-view controls, evidence units and caveats bilingual."""
    assert T["en"]["btn_outlier_show_path_in_station_insights"] == (
        "↓ Show in Station Insights"
    )
    assert T["en"]["btn_outlier_show_drilldown_details"] == (
        "↓ Show Drill-Down Details"
    )
    assert T["de"]["btn_outlier_show_path_in_station_insights"] == (
        "↓ In Station Insights anzeigen"
    )
    assert T["de"]["btn_outlier_show_drilldown_details"] == (
        "↓ Drill-Down-Details anzeigen"
    )
    assert T["en"]["fig_drilldown_outlier_candidate"] == (
        "Outlier candidate"
    )
    assert T["de"]["fig_drilldown_outlier_candidate"] == (
        "Ausreißerkandidat"
    )
    assert T["en"]["fig_drilldown_outlier_focused_episode"] == (
        "Focused episode"
    )
    assert T["de"]["fig_drilldown_outlier_focused_episode"] == (
        "Fokussierte Episode"
    )

    expected_controls = {
        "en": (
            "Center date (UTC)",
            "Center time (UTC)",
            "← Earlier",
            "Later →",
            "Outlier Focus",
            "Filter table",
        ),
        "de": (
            "Datum der Fenstermitte (UTC)",
            "Uhrzeit der Fenstermitte (UTC)",
            "← Früher",
            "Später →",
            "Ausreißerfokus",
            "Tabelle filtern",
        ),
    }
    control_keys = (
        "lbl_drilldown_center_date_utc",
        "lbl_drilldown_center_time_utc",
        "btn_drilldown_zoom_earlier",
        "btn_drilldown_zoom_later",
        "lbl_drilldown_zoom_outlier_focus",
        "lbl_filter_table",
    )
    for language, expected_values in expected_controls.items():
        assert tuple(T[language][key] for key in control_keys) == expected_values
    assert T["en"]["txt_results_drilldown_filter_note"] == (
        "Filter table changes only the displayed table; Zoom window limits both "
        "the focused plots and table, never the completed analysis."
    )
    assert T["de"]["txt_results_drilldown_filter_note"] == (
        "Mit „Tabelle filtern“ wird nur die angezeigte Tabelle verändert; das "
        "Zoom-Zeitfenster begrenzt fokussierte Abbildungen und Tabelle, niemals "
        "die abgeschlossene Analyse."
    )

    assert T["en"]["fmt_drilldown_zoom_time_window"].format(
        identity="DG2CAD (JN47mv)",
        start="2021-05-10 17:31",
        end="2021-05-11 05:31",
    ) == (
        "DG2CAD (JN47mv) - Time Window: "
        "2021-05-10 17:31 to 2021-05-11 05:31 UTC"
    )
    assert T["de"]["fmt_drilldown_zoom_time_window"].format(
        identity="DG2CAD (JN47mv)",
        start="10.05.2021 17:31",
        end="11.05.2021 05:31",
    ) == (
        "DG2CAD (JN47mv) - Zeitfenster: "
        "10.05.2021 17:31 bis 11.05.2021 05:31 UTC"
    )
    assert T["en"]["fmt_drilldown_zoom_selected_window"].format(
        start="2021-05-10 17:31",
        end="2021-05-11 05:31",
    ) == "Selected window: 2021-05-10 17:31 to 2021-05-11 05:31 UTC"
    assert T["de"]["fmt_drilldown_zoom_selected_window"].format(
        start="10.05.2021 17:31",
        end="11.05.2021 05:31",
    ) == "Ausgewähltes Zeitfenster: 10.05.2021 17:31 bis 11.05.2021 05:31 UTC"

    for language in ("en", "de"):
        for superseded_key in (
            "lbl_drilldown_focus_date_utc",
            "lbl_drilldown_focus_time_utc",
            "lbl_drilldown_zoom_event_focus_12h",
            "lbl_drilldown_zoom_fit_detector_context",
            "txt_drilldown_zoom_cycle_resolution",
            "txt_drilldown_outlier_overlay_note",
            "fig_drilldown_outlier_candidate_interval",
        ):
            assert superseded_key not in T[language]

    contracts = {
        "en": {
            "drilldown_compare_joint": (
                "centered interval", "one actual value per retained Joint Spot",
                "cycle time", "without time-bin medians", "density coloring",
                "an IQR band", "a full-run median", "UTC-hour folding",
                "retain their aggregated views", "narrows only the displayed rows",
            ),
            "drilldown_success_rx": (
                "each successful opportunity", "normalized Target SNR",
                "missed opportunities have no SNR point", "without temporal medians",
                "changes only displayed rows",
            ),
            "drilldown_success_tx": (
                "each successful opportunity", "normalized Target SNR",
                "missed opportunities have no SNR point", "without temporal medians",
                "changes only displayed rows",
            ),
            "outlier_focus": (
                "actual cycle times", "Focused episode", "Expected local ΔSNR",
                "guides at 1, 2, 3", "configured threshold", "difference in dB",
                "individually pass both departure requirements",
                "different baseline and scatter", "strongest individually qualifying observation",
                "Largest single-cycle departure", "not confidence intervals",
                "Crossing one line alone", "display padding", "clipped to the selected window",
                "does not measure a physical event",
            ),
        },
        "de": {
            "drilldown_compare_joint": (
                "zentriertes Intervall", "einen tatsächlichen Wert je berücksichtigtem Joint Spot",
                "Zykluszeit", "ohne Zeit-Bin-Mediane", "Dichtefärbung", "IQR-Band",
                "Median des vollständigen Laufs", "UTC-Stunde",
                "aggregierte Darstellung", "nur die angezeigten Zeilen",
            ),
            "drilldown_success_rx": (
                "jeder erfolgreichen Gelegenheit", "normierte Target-SNR",
                "verpasste Gelegenheiten haben keinen SNR-Punkt", "Einzelwerte ohne Zeitmediane",
                "verändert nur angezeigte Zeilen",
            ),
            "drilldown_success_tx": (
                "jeder erfolgreichen Gelegenheit", "normierte Target-SNR",
                "verpasste Gelegenheiten haben keinen SNR-Punkt", "Einzelwerte ohne Zeitmediane",
                "verändert nur angezeigte Zeilen",
            ),
            "outlier_focus": (
                "tatsächlichen Zykluszeiten", "Fokussierte Episode", "Erwartetes lokales ΔSNR",
                "bei 1, 2, 3", "konfigurierten Schwelle", "Unterschied in dB",
                "einzeln beide Abweichungsanforderungen", "anderen Baseline und Streuung",
                "stärkste einzeln qualifizierende Beobachtung", "Einzelzyklusabweichung",
                "keine Konfidenzintervalle", "Überschreiten einer einzelnen Linie",
                "Anzeigerand", "auf das ausgewählte Fenster begrenzt",
                "nicht die Dauer eines physischen Ereignisses",
            ),
        },
    }
    for language, items in contracts.items():
        for key, phrases in items.items():
            item = RESULT_GUIDANCE[language]["sections"][key]
            text = _plain_guidance(" ".join(item.values()))
            for phrase in phrases:
                assert phrase in text, (language, key, phrase)


def test_success_selected_guidance_stays_near_readability_target():
    """Keep each selected-station popover within the generous copy ceiling."""
    for language in ("en", "de"):
        for direction in ("rx", "tx"):
            item = RESULT_GUIDANCE[language]["sections"][
                f"selected_success_{direction}"
            ]
            assert len(item["read"]) + len(item["limits"]) <= 2700


@pytest.mark.parametrize("language", ("en", "de"))
@pytest.mark.parametrize("direction", ("rx", "tx"))
def test_success_temporal_guidance_explains_two_figures_rates_and_folded_averages(language, direction):
    """Preserve station-balanced versus opportunity-weighted rates and folded support."""
    item = RESULT_GUIDANCE[language]["sections"][f"success_temporal_evidence_{direction}"]
    text = _plain_guidance(" ".join(item.values()))
    for key in (f"map_success_{direction}_opportunity_target",
                f"map_success_{direction}_opportunity_counter"):
        assert T[language][key] in text
    role = "receiver" if direction == "tx" else "station"
    german_presences = "Empfängerpräsenzen" if direction == "tx" else "Stationspräsenzen"
    german_vote = (
        "jedem unterschiedlichen Empfänger weiterhin eine Stimme über alle Tage"
        if direction == "tx"
        else "jeder unterschiedlichen Station weiterhin eine Stimme über alle Tage"
    )
    phrases = (
        ("three successful observations", "station row", "opportunity row",
         "counts every confirmed opportunity", f"daily average {role} presences",
         f"each distinct {role} one vote across dates", "`1h`",
         "corresponding chronological hourly totals", "at least two represented dates")
        if language == "en" else
        ("drei erfolgreiche Beobachtungen", "Stationszeile", "Gelegenheitszeile",
         "zählt jede bestätigte Gelegenheit", f"durchschnittliche tägliche {german_presences}",
         german_vote,
         "`1h`", "chronologischen Stundensummen", "mindestens zwei berücksichtigte Tage")
    )
    for phrase in phrases:
        assert phrase in text, (language, direction, phrase)


@pytest.mark.parametrize("section_key", ("map_compare_rx", "map_compare_tx"))
def test_compare_map_guidance_explains_dynamic_symmetric_db_scale(section_key):
    """Explain comparable dB values without exposing the color-bin implementation."""
    contracts = {
        "en": ("symmetric dB scale", "at least −6 to +6 dB", "can expand between runs",
               "color-bar numbers rather than colors alone", "display interval",
               "only 0 dB means equality", "no qualifying summary"),
        "de": ("symmetrische dB-Skala", "mindestens von −6 bis +6 dB",
               "kann sich zwischen Läufen erweitern", "Zahlen der Farbskala",
               "Darstellungsintervall", "nur 0 dB bedeutet Gleichheit",
               "keine qualifizierende Zusammenfassung"),
    }
    for language, phrases in contracts.items():
        text = RESULT_GUIDANCE[language]["sections"][section_key]["limits"]
        for phrase in phrases:
            assert phrase in text
        assert "13" not in text
        assert "S-unit" not in text
        assert "S-Stufe" not in text


def test_success_map_guidance_uses_status_markers_and_two_level_support():
    """Keep actual marker labels separate from the arithmetic mean sector rate."""
    for language in ("en", "de"):
        for direction in ("rx", "tx"):
            text = _plain_guidance(" ".join(
                RESULT_GUIDANCE[language]["sections"][f"map_success_{direction}"].values()
            ))
            for key in (
                f"map_success_{direction}_station_target",
                f"map_success_{direction}_station_counter",
                "map_success_footer_stations", "map_success_footer_opportunities",
            ):
                assert T[language][key] in text
            expected = (("arithmetic mean", "equal weight", "at least once",
                         "does not mean every opportunity succeeded", "light-gray",
                         "lack enough stations for shading")
                        if language == "en" else
                        ("arithmetische Mittel", "dasselbe Gewicht", "mindestens einmal",
                         "nicht, dass jede Gelegenheit erfolgreich war", "hellgrauer",
                         "für eine Einfärbung nicht ausreicht"))
            for phrase in expected:
                assert phrase in text


def test_success_segment_distance_and_temporal_guidance_matches_editorial_contract():
    """Preserve visible figure names, distance spread, and unequal evidence weights."""
    for language in ("en", "de"):
        for direction in ("rx", "tx"):
            sections = RESULT_GUIDANCE[language]["sections"]
            distance = _plain_guidance(" ".join(sections[f"success_evidence_{direction}"].values()))
            segment = _plain_guidance(" ".join(sections[f"segment_success_{direction}"].values()))
            for key in (
                f"fig_success_reach_title_{direction}", f"fig_success_consistency_title_{direction}",
                f"fig_success_snr_distance_title_{direction}",
            ):
                assert T[language][key] in distance
            role = "receivers" if direction == "tx" else "stations"
            german_role = "Empfängern" if direction == "tx" else "Stationen"
            for phrase in ((f"two contributing {role}", "Min-Max", "three or more",
                            "middle 50%", "30 dBm (1 W)")
                           if language == "en" else
                           (f"zwei beitragenden {german_role}", "Min-Max", "drei oder mehr",
                            "mittleren 50 %", "30 dBm (1 W)")):
                assert phrase in distance
            assert ("equal weight" if language == "en" else "gleichem Gewicht") in segment
            assert ("all confirmed opportunities" if language == "en"
                    else "alle bestätigten Gelegenheiten") in segment
            assert ("do not prove" if language == "en" else "belegen nicht") in segment


def test_success_map_presentation_labels_are_bilingual_and_status_only():
    """Keep the compact legend and footer labels aligned across languages."""
    expected_labels = {
        "en": {
            "cbar_abs_rx": "Station-balanced RX Decode Rate (%)",
            "cbar_abs_tx": "Station-balanced TX Decode Rate (%)",
            "map_success_footer_opportunities": "OPPORTUNITIES",
            "map_success_footer_stations": "STATIONS",
            "map_success_rx_opportunity_target": "Heard by Target",
            "map_success_rx_opportunity_counter": "Heard by others only",
            "map_success_rx_station_target": "Heard by Target",
            "map_success_rx_station_counter": "Heard by others only",
            "map_success_tx_opportunity_target": "Target heard",
            "map_success_tx_opportunity_counter": "Other signals heard only",
            "map_success_tx_station_target": "Target heard",
            "map_success_tx_station_counter": "Other signals heard only",
            "map_success_legend_insufficient": "Insufficient evidence",
        },
        "de": {
            "cbar_abs_rx": "Stationsgleichgewichtete RX-Dekodierrate (%)",
            "cbar_abs_tx": "Stationsgleichgewichtete TX-Dekodierrate (%)",
            "map_success_footer_opportunities": "GELEGENHEITEN",
            "map_success_footer_stations": "STATIONEN",
            "map_success_rx_opportunity_target": "Vom Target gehört",
            "map_success_rx_opportunity_counter": "Nur von anderen gehört",
            "map_success_rx_station_target": "Vom Target gehört",
            "map_success_rx_station_counter": "Nur von anderen gehört",
            "map_success_tx_opportunity_target": "Target gehört",
            "map_success_tx_opportunity_counter": "Nur andere Signale gehört",
            "map_success_tx_station_target": "Target gehört",
            "map_success_tx_station_counter": "Nur andere Signale gehört",
            "map_success_legend_insufficient": "Unzureichende Evidenz",
        },
    }

    for language, labels in expected_labels.items():
        for key, expected_text in labels.items():
            assert T[language][key] == expected_text

    retired_keys = {
        "map_success_sector_legend",
        "map_success_marker_legend",
        "map_success_footer_station_categories",
        "map_success_footer_opportunity_categories",
        "map_footer_stations",
        "map_footer_confirmed_opportunities",
        "map_success_target_observed",
        "map_success_zero_target",
        "map_success_no_qualifying_segment",
        "fmt_results_decimal_separator",
        "leg_abs_hit_one",
        "leg_abs_hit_mid",
        "leg_abs_hit_high",
    }
    for language in ("en", "de"):
        assert retired_keys.isdisjoint(T[language])


@pytest.mark.parametrize(
    (
        "language",
        "analysis_id",
        "map_success",
        "map_counter",
        "mode_key",
    ),
    (
        ("en", "RX_ABS", "Heard by Target", "Heard by others only", "rx"),
        (
            "en",
            "TX_ABS",
            "Target heard",
            "Other signals heard only",
            "tx",
        ),
        ("de", "RX_ABS", "Vom Target gehört", "Nur von anderen gehört", "rx"),
        (
            "de",
            "TX_ABS",
            "Target gehört",
            "Nur andere Signale gehört",
            "tx",
        ),
    ),
)
def test_success_guidance_uses_mode_specific_station_status_labels(
    language,
    analysis_id,
    map_success,
    map_counter,
    mode_key,
):
    """Resolve direction-aware map outcomes and exact distance-panel names."""
    map_guidance = _build_guidance(
        RESULT_GUIDANCE_MAP,
        language=language,
        analysis_id=analysis_id,
        is_compare=False,
        analysis_context=AnalysisContext(),
    )
    distance_guidance = _build_guidance(
        RESULT_GUIDANCE_SUCCESS_EVIDENCE,
        language=language,
        analysis_id=analysis_id,
        is_compare=False,
        analysis_context=AnalysisContext(),
    )

    assert map_success in map_guidance
    assert map_counter in map_guidance
    for key in (
        f"fig_success_reach_title_{mode_key}",
        f"fig_success_consistency_title_{mode_key}",
        f"fig_success_snr_distance_title_{mode_key}",
    ):
        assert T[language][key] in distance_guidance


def test_result_guidance_uses_practical_station_language():
    """Use archive identities without claiming one unique physical station."""
    for language in ("en", "de"):
        complete = " ".join(text for item in RESULT_GUIDANCE[language]["sections"].values()
                            for text in item.values()).lower()
        assert "estimator" not in complete
        assert "schätzer" not in complete
        for key in ("station_insights_compare_joint", "station_insights_success_rx",
                    "station_insights_success_tx"):
            text = _plain_guidance(" ".join(RESULT_GUIDANCE[language]["sections"][key].values()))
            assert ("callsign and locator" if language == "en"
                    else "Rufzeichen und Locator") in text
            assert ("physical" if language == "en" else "physisch") in text


@pytest.mark.parametrize("language", ("en", "de"))
@pytest.mark.parametrize(('analysis_id', 'is_compare', 'analysis_context', 'section_ids'), [('RX_COMP', True, AnalysisContext(comparison_mode=COMPARISON_REFERENCE_STATION), COMPARE_SECTIONS), ('TX_COMP', True, AnalysisContext(comparison_mode=COMPARISON_REFERENCE_STATION), COMPARE_SECTIONS), ('RX_ABS', False, AnalysisContext(comparison_mode=COMPARISON_NONE), SUCCESS_SECTIONS), ('TX_ABS', False, AnalysisContext(comparison_mode=COMPARISON_NONE), SUCCESS_SECTIONS)])
def test_every_valid_result_family_resolves_all_of_its_sections(
    language,
    analysis_id,
    is_compare,

    analysis_context,
    section_ids,
):
    """Render every valid Compare and Success section without raw placeholders."""
    for section_id in section_ids:
        guidance = _build_guidance(
            section_id,
            language=language,
            analysis_id=analysis_id,
            is_compare=is_compare,

            analysis_context=analysis_context,
            selected_station_count=(
                1
                if section_id == RESULT_GUIDANCE_SELECTED_STATIONS
                else None
            ),
        )

        assert RESULT_GUIDANCE[language]["read_label"] in guidance
        assert RESULT_GUIDANCE[language]["limits_label"] in guidance
        assert not _format_fields(guidance)


@pytest.mark.parametrize(
    (
        "comparison_mode",
        "local_benchmark",
        "expected_text",
        "unexpected_text",
    ),
    (
        (
            COMPARISON_REFERENCE_STATION,
            LOCAL_BENCHMARK_MEDIAN,
            "A controlled comparison can investigate antennas, feedlines, radios, or complete setups",
            "independently configured",
        ),
        (
            COMPARISON_REFERENCE_STATION,
            LOCAL_BENCHMARK_MEDIAN,
            "selected Reference callsign within the four-character locator resolved from the archive period",
            "independently configured",
        ),
        (
            COMPARISON_LOCAL_NEIGHBORHOOD,
            LOCAL_BENCHMARK_MEDIAN,
            "qualifying observations from stations within 175 km",
            "strongest qualifying local station",
        ),
    ),
)
def test_compare_drilldown_resolves_the_active_benchmark(
    comparison_mode,
    local_benchmark,
    expected_text,
    unexpected_text,
):
    """Preserve detailed reference construction beside its underlying observations."""
    guidance = _build_guidance(
        RESULT_GUIDANCE_DRILLDOWN,
        analysis_context=AnalysisContext(
            comparison_mode=comparison_mode,
            local_benchmark=local_benchmark,
            neighborhood_radius_km=175,
        ),
    )

    plain_guidance = _plain_guidance(guidance)
    assert expected_text in plain_guidance
    assert unexpected_text not in plain_guidance


def test_mode_specific_terms_and_compare_pairing_are_resolved_semantically():
    """Use direction-specific peer roles, denominators, and pairing language."""
    rx_context = _build_guidance(
        RESULT_GUIDANCE_CONTEXT,
        analysis_id="RX_ABS",
        is_compare=False,
        analysis_context=AnalysisContext(),
    )
    tx_context = _build_guidance(
        RESULT_GUIDANCE_CONTEXT,
        analysis_id="TX_ABS",
        is_compare=False,
        analysis_context=AnalysisContext(),
    )
    rx_success = _build_guidance(
        RESULT_GUIDANCE_MAP,
        analysis_id="RX_ABS",
        is_compare=False,
        analysis_context=AnalysisContext(),
    )
    tx_success = _build_guidance(
        RESULT_GUIDANCE_MAP,
        analysis_id="TX_ABS",
        is_compare=False,
        analysis_context=AnalysisContext(),
    )
    joint_compare = _build_guidance(
        RESULT_GUIDANCE_COMPARISON_EVIDENCE,
        analysis_context=AnalysisContext(
            comparison_mode=COMPARISON_REFERENCE_STATION
        ),
        selected_station_count=1,
    )
    tx_compare = _build_guidance(
        RESULT_GUIDANCE_COMPARISON_EVIDENCE,
        analysis_id="TX_COMP",

        analysis_context=AnalysisContext(
            comparison_mode=COMPARISON_REFERENCE_STATION
        ),
    )
    joint_compare_plain = _plain_guidance(joint_compare)
    tx_compare_plain = _plain_guidance(tx_compare)

    assert "qualifying remote transmitter identity" in rx_success
    assert "Heard by Target" in rx_success
    assert "Heard by others only" in rx_success
    assert "Elsewhere" not in rx_success
    assert "qualifying remote receiver identity" in tx_success
    assert "Target heard" in tx_success
    assert "Other signals heard only" in tx_success
    assert "Other Signals" not in tx_success
    assert "confirmed reception opportunities" in rx_context
    assert "confirmed reception opportunities" in tx_context
    assert "Joint Spot contains Target and Reference evidence for the same remote transmitter in RX, or the same remote receiver in TX, in one WSPR cycle" in joint_compare_plain
    assert all(
        outcome in joint_compare_plain
        for outcome in (
            "Joint",
            "Only Target",
            "Both (Async)",
            "Only Reference",
        )
    )
    assert "hatched bars (Stations) use the total station count" in joint_compare_plain
    assert "solid bars (Spots) use the total spot count" in joint_compare_plain
    assert "Total and Joint counts above the figure" in joint_compare_plain
    assert (
        "Joint Spot contains Target and Reference evidence for the same remote transmitter in RX, or the same remote receiver in TX, in one WSPR cycle"
        in tx_compare_plain
    )
    assert "solid bars (Spots) use the total spot count" in tx_compare_plain
    assert "Scheduled Pair" not in tx_compare_plain


@pytest.mark.parametrize("language", ("en", "de"))
@pytest.mark.parametrize("direction", ("RX", "TX"))
def test_benchmark_distributions_explain_population_weighting_and_delta_axis(language, direction):
    """Retain separate station/observation populations and the signed dB axis."""
    guidance = _plain_guidance(_build_guidance(
        RESULT_GUIDANCE_COMPARISON_EVIDENCE,
        language=language,
        analysis_id=f"{direction}_COMP",
        analysis_context=AnalysisContext(
            comparison_mode=COMPARISON_REFERENCE_STATION,
        ),
    ))
    expected = {
        "en": (
            "each qualifying station one median paired difference",
            "percentage of stations in each ΔSNR range",
            "each Joint Spot one value",
            "frequently observed stations contribute more",
            "percentage of Joint Spots in each range",
            "within their own population",
            "ΔSNR in dB on the horizontal axis",
            "positive favors Target", "negative favors Reference", "0 dB means equality",
        ),
        "de": (
            "jeder qualifizierenden Station einen Median ihrer gepaarten Unterschiede",
            "Prozentanteil der Stationen im jeweiligen ΔSNR-Bereich",
            "jedem Joint Spot einen Wert",
            "häufig beobachtete Stationen tragen daher mehr bei",
            "Prozentanteil der Joint Spots im jeweiligen Bereich",
            "innerhalb ihrer jeweiligen Population",
            "ΔSNR in dB an der horizontalen Achse",
            "Positive Werte sprechen für das Target", "negative für die Referenz",
            "0 dB bedeutet Gleichheit",
        ),
    }[language]
    for phrase in expected:
        assert phrase in guidance, (language, direction, phrase)


@pytest.mark.parametrize("language", ("en", "de"))
def test_success_segment_and_temporal_guidance_route_without_changing_compare(language):
    """Keep the new Success summaries separate from established Compare help."""
    success_segment = _build_guidance(
        RESULT_GUIDANCE_SEGMENT,
        language=language,
        analysis_id="RX_ABS",
        is_compare=False,
        analysis_context=AnalysisContext(),
    )
    compare_segment = _build_guidance(
        RESULT_GUIDANCE_SEGMENT,
        language=language,
        analysis_id="RX_COMP",
        is_compare=True,
        analysis_context=AnalysisContext(
            comparison_mode=COMPARISON_REFERENCE_STATION
        ),
    )
    success_temporal = _build_guidance(
        RESULT_GUIDANCE_TEMPORAL_EVIDENCE,
        language=language,
        analysis_id="RX_ABS",
        is_compare=False,
        analysis_context=AnalysisContext(),
    )
    compare_temporal = _build_guidance(
        RESULT_GUIDANCE_TEMPORAL_EVIDENCE,
        language=language,
        analysis_id="RX_COMP",
        is_compare=True,
        analysis_context=AnalysisContext(
            comparison_mode=COMPARISON_REFERENCE_STATION
        ),
    )

    assert (
        "Decode Rate" in success_segment
        if language == "en"
        else "Dekodierrate" in success_segment
    )
    assert (
        "Heard by Target" in success_segment
        if language == "en"
        else "Vom Target gehört" in success_segment
    )
    assert (
        "Read both rates" in success_segment
        if language == "en"
        else "Lies beide Raten" in success_segment
    )
    assert "Joint Spots" in compare_segment
    assert (
        "Successful RX SNR Deviation" in success_temporal
        if language == "en"
        else "Abweichung des erfolgreichen RX-SNR" in success_temporal
    )
    assert (
        "Heard by others only" in success_temporal
        if language == "en"
        else "Nur von anderen gehört" in success_temporal
    )
    assert "Joint Spots" in compare_temporal


def test_success_guidance_does_not_interpolate_mutable_ui_labels():
    """Keep static editorial guidance independent of presentation label values."""
    translations = {
        **T["en"],
        "abs_rx_counter": "<script>alert(1)</script>",
        "map_success_rx_station_target": "<img src=x onerror=alert(2)>",
        "map_success_rx_station_counter": "<iframe src=bad></iframe>",
    }
    map_guidance = build_result_guidance(
        RESULT_GUIDANCE_MAP,
        language="en",
        translations=translations,
        analysis_id="RX_ABS",
        is_compare=False,
        analysis_context=AnalysisContext(),
    )
    temporal_guidance = build_result_guidance(
        RESULT_GUIDANCE_TEMPORAL_EVIDENCE,
        language="en",
        translations=translations,
        analysis_id="RX_ABS",
        is_compare=False,
        analysis_context=AnalysisContext(),
    )

    assert map_guidance == _build_guidance(
        RESULT_GUIDANCE_MAP,
        analysis_id="RX_ABS",
        is_compare=False,
        analysis_context=AnalysisContext(),
    )
    assert temporal_guidance == _build_guidance(
        RESULT_GUIDANCE_TEMPORAL_EVIDENCE,
        analysis_id="RX_ABS",
        is_compare=False,
        analysis_context=AnalysisContext(),
    )
    for unsafe_fragment in ("<script>", "<img ", "<iframe "):
        assert unsafe_fragment not in map_guidance
        assert unsafe_fragment not in temporal_guidance


@pytest.mark.parametrize("language", ("en", "de"))
@pytest.mark.parametrize("is_compare", (False, True), ids=("performance", "benchmark"))
def test_context_layout_escapes_supplied_section_headers(language, is_compare):
    """Render actual supplied headers as text without allowing HTML injection."""
    heading_keys = (
        "hdr_results_map_view", "hdr_results_segment_inspector",
        "hdr_results_comparison_evidence", "hdr_results_success_evidence",
        "hdr_results_temporal_evidence", "lbl_insights",
        "hdr_results_selected_station_evidence", "hdr_results_drilldown",
    )
    translations = dict(T[language])
    for key in heading_keys:
        translations[key] = f'{key}: <img src=x onerror="alert(1)"> & \'text\''
    guidance = build_result_guidance(
        RESULT_GUIDANCE_CONTEXT,
        language=language,
        translations=translations,
        analysis_id="RX_COMP" if is_compare else "RX_ABS",
        is_compare=is_compare,
        analysis_context=AnalysisContext(
            comparison_mode=COMPARISON_REFERENCE_STATION if is_compare else COMPARISON_NONE,
        ),
    )
    expected_path = " → ".join(
        _context_layout_headings(translations, is_compare=is_compare).values()
    )
    assert f'<strong class="defined-term">{expected_path}</strong>' in guidance
    assert "<img " not in guidance
    assert "&lt;img " in guidance
    assert "&quot;alert(1)&quot;" in guidance
    assert "&amp; &#x27;text&#x27;" in guidance
    inactive_evidence_key = (
        "hdr_results_success_evidence" if is_compare else "hdr_results_comparison_evidence"
    )
    assert inactive_evidence_key not in guidance


def test_success_guidance_generation_does_not_mutate_analysis_context():
    """Keep presentation-only guidance outside canonical scientific state."""
    analysis_context = AnalysisContext(
        comparison_mode=COMPARISON_NONE,
        neighborhood_radius_km=175,
    )
    original_fields = analysis_context.__dict__.copy()

    for section_id in (
        RESULT_GUIDANCE_MAP,
        RESULT_GUIDANCE_SEGMENT,
        RESULT_GUIDANCE_SUCCESS_EVIDENCE,
        RESULT_GUIDANCE_TEMPORAL_EVIDENCE,
    ):
        _build_guidance(
            section_id,
            analysis_id="RX_ABS",
            is_compare=False,
            analysis_context=analysis_context,
        )

    assert analysis_context.__dict__ == original_fields


@pytest.mark.parametrize("language", ("en", "de"))
@pytest.mark.parametrize(
    "section_id",
    (
        RESULT_GUIDANCE_MAP,
        RESULT_GUIDANCE_SEGMENT,
        RESULT_GUIDANCE_SUCCESS_EVIDENCE,
        RESULT_GUIDANCE_TEMPORAL_EVIDENCE,
    ),
)
def test_success_guidance_defined_term_markup_is_balanced(language, section_id):
    """Pass every redesigned semantic term through the established HTML path."""
    guidance = _build_guidance(
        section_id,
        language=language,
        analysis_id="RX_ABS",
        is_compare=False,
        analysis_context=AnalysisContext(),
    )

    assert guidance.count('<strong class="defined-term">') >= 1
    assert guidance.count("<strong") == guidance.count("</strong>")


def test_german_success_guidance_and_toggle_retire_zero_target_wording():
    """Use the evidence outcome in guidance and the matching display toggle."""
    guidance = _build_guidance(
        RESULT_GUIDANCE_STATION_INSIGHTS,
        language="de",
        analysis_id="RX_ABS",
        is_compare=False,
        analysis_context=AnalysisContext(),
    )

    assert "Nur von anderen gehört" in guidance
    assert "Zero-Target" not in guidance
    assert (
        T["de"]["success_rx_show_counter"]
        == "Nur von anderen Stationen gehört."
    )


@pytest.mark.parametrize(
    (
        "language",
        "analysis_id",
        "station_counter",
        "snr_header",
        "retired_counter",
        "retired_snr_header",
        "retired_opportunity_label",
    ),
    (
        (
            "en",
            "TX_ABS",
            "Other signals heard",
            "Median SNR @ 30 dBm",
            "Other signals heard only",
            "Median successful Target SNR",
            "confirmed opportunities",
        ),
        (
            "de",
            "TX_ABS",
            "Andere Signale gehört",
            "Median-SNR @ 30 dBm",
            "Nur andere Signale gehört",
            "Median des erfolgreichen Target-SNR",
            "bestätigte Gelegenheiten",
        ),
    ),
)
def test_performance_table_guidance_names_only_active_display_columns(
    language,
    analysis_id,
    station_counter,
    snr_header,
    retired_counter,
    retired_snr_header,
    retired_opportunity_label,
):
    """Keep Station Insights and Drill-Down guidance aligned with visible tables."""
    station_guidance = _build_guidance(
        RESULT_GUIDANCE_STATION_INSIGHTS,
        language=language,
        analysis_id=analysis_id,
        is_compare=False,
        analysis_context=AnalysisContext(),
    )
    drilldown_guidance = _build_guidance(
        RESULT_GUIDANCE_DRILLDOWN,
        language=language,
        analysis_id=analysis_id,
        is_compare=False,
        analysis_context=AnalysisContext(),
    )

    assert station_counter in station_guidance
    assert station_counter in drilldown_guidance
    assert snr_header in station_guidance
    assert f'<strong class="defined-term">{retired_counter}</strong>' not in station_guidance
    assert f'<strong class="defined-term">{retired_counter}</strong>' not in drilldown_guidance
    assert retired_snr_header not in station_guidance
    assert f'<strong class="defined-term">{retired_opportunity_label}</strong>' not in station_guidance
    assert "Outcomes identify" not in drilldown_guidance
    assert "Outcomes unterscheiden" not in drilldown_guidance


@pytest.mark.parametrize("language", ("en", "de"))
def test_success_guidance_names_the_rendered_figures_exactly(language):
    """Let readers match each explanation to its visible figure title."""
    success_figures = _build_guidance(
        RESULT_GUIDANCE_SUCCESS_EVIDENCE,
        language=language,
        analysis_id="RX_ABS",
        is_compare=False,
        analysis_context=AnalysisContext(),
    )
    temporal_figures = _build_guidance(
        RESULT_GUIDANCE_TEMPORAL_EVIDENCE,
        language=language,
        analysis_id="RX_ABS",
        is_compare=False,
        analysis_context=AnalysisContext(),
    )
    selected_figures = _build_guidance(
        RESULT_GUIDANCE_SELECTED_STATIONS,
        language=language,
        analysis_id="RX_ABS",
        is_compare=False,
        analysis_context=AnalysisContext(),
        selected_station_count=1,
    )

    for key in (
        "fig_success_reach_title_rx",
        "fig_success_consistency_title_rx",
        "fig_success_snr_distance_title_rx",
    ):
        assert T[language][key] in success_figures
    assert (
        "Successful RX SNR Deviation" in temporal_figures
        if language == "en"
        else "Abweichung des erfolgreichen RX-SNR" in temporal_figures
    )
    assert (
        "station presences" in temporal_figures
        if language == "en"
        else "Stationspräsenzen" in temporal_figures
    )
    assert (
        "Heard by Target" in selected_figures
        if language == "en"
        else "Vom Target gehört" in selected_figures
    )
    assert (
        "Heard by others only" in selected_figures
        if language == "en"
        else "Nur von anderen gehört" in selected_figures
    )
    assert "Target" in selected_figures
    for retired_name in (
        "Station Success Rate by Evidence Count",
        "Station Success Distribution",
        "Evidence Depth per Station",
        "Average Station Success Rate",
        "Observation-Level Success Rate",
    ):
        assert retired_name not in success_figures


@pytest.mark.parametrize(
    (
        "language",
        "joint_title",
        "selected_chronological_title",
        "selected_folded_title",
    ),
    (
        (
            "en",
            "Joint-Spot Δ SNR",
            "Δ SNR over Time",
            "Δ SNR by UTC Hour",
        ),
        (
            "de",
            "Joint-Spot Δ SNR",
            "Δ SNR im Zeitverlauf",
            "Δ SNR nach UTC-Stunde",
        ),
    ),
)
def test_compare_guidance_names_the_rendered_figures_exactly(
    language,
    joint_title,
    selected_chronological_title,
    selected_folded_title,
):
    """Use the same spacing and localization as the visible Compare figures."""
    joint_figures = _build_guidance(
        RESULT_GUIDANCE_COMPARISON_EVIDENCE,
        language=language,
        analysis_context=AnalysisContext(
            comparison_mode=COMPARISON_REFERENCE_STATION
        ),
    )
    tx_figures = _build_guidance(
        RESULT_GUIDANCE_COMPARISON_EVIDENCE,
        language=language,
        analysis_id="TX_COMP",

        analysis_context=AnalysisContext(
            comparison_mode=COMPARISON_REFERENCE_STATION
        ),
    )
    selected_figures = _build_guidance(
        RESULT_GUIDANCE_SELECTED_STATIONS,
        language=language,
        analysis_context=AnalysisContext(
            comparison_mode=COMPARISON_REFERENCE_STATION
        ),
        selected_station_count=1,
    )

    for guidance in (joint_figures, tx_figures):
        for title in (T[language]["fig_station_medians_delta"], joint_title):
            assert f'<strong class="defined-term">{title}</strong>' in guidance
    for title in (selected_chronological_title, selected_folded_title):
        assert f'<strong class="defined-term">{title}</strong>' in selected_figures
    retired_selected_title = (
        "Δ SNR Distribution"
        if language == "en"
        else "Δ SNR Verteilung"
    )
    assert retired_selected_title not in selected_figures


@pytest.mark.parametrize(('section_id', 'analysis_id', 'is_compare', 'match'), [(RESULT_GUIDANCE_COMPARISON_EVIDENCE, 'RX_ABS', False, 'unavailable for Performance'), (RESULT_GUIDANCE_SUCCESS_EVIDENCE, 'RX_COMP', True, 'unavailable for Benchmark'), (RESULT_GUIDANCE_MAP, 'not-an-analysis', False, 'requires an RX or TX analysis ID')])
def test_invalid_mode_and_section_combinations_are_rejected(
    section_id,
    analysis_id,
    is_compare,

    match,
):
    """Reject result-help combinations absent from the actual analysis flow."""
    with pytest.raises(ValueError, match=match):
        _build_guidance(
            section_id,
            analysis_id=analysis_id,
            is_compare=is_compare,

            analysis_context=AnalysisContext(
                comparison_mode=COMPARISON_REFERENCE_STATION
            ),
        )


def test_invalid_guidance_identity_language_and_benchmark_are_rejected():
    """Fail clearly instead of silently selecting unrelated localized content."""
    with pytest.raises(ValueError, match="Unknown result-guidance section"):
        _build_guidance(
            "not-a-section",
            analysis_context=AnalysisContext(
                comparison_mode=COMPARISON_REFERENCE_STATION
            ),
        )

    with pytest.raises(ValueError, match="Unsupported result-guidance language"):
        build_result_guidance(
            RESULT_GUIDANCE_DOWNLOAD,
            language="fr",
            translations=T["en"],
        )

    with pytest.raises(ValueError, match="supported comparison mode"):
        _build_guidance(
            RESULT_GUIDANCE_CONTEXT,
            analysis_context=AnalysisContext(
                comparison_mode=COMPARISON_NONE
            ),
        )

    with pytest.raises(ValueError, match="Unsupported local benchmark"):
        _build_guidance(
            RESULT_GUIDANCE_CONTEXT,
            analysis_context=AnalysisContext(
                comparison_mode=COMPARISON_LOCAL_NEIGHBORHOOD,
                local_benchmark="unsupported-local-benchmark",
            ),
        )


def test_local_median_drilldown_appends_dynamic_reference_explanation():
    """Explain expanded contributors only for the Local Median row contract."""
    local_median = _build_guidance(
        RESULT_GUIDANCE_DRILLDOWN,
        analysis_context=AnalysisContext(
            comparison_mode=COMPARISON_LOCAL_NEIGHBORHOOD,
            local_benchmark=LOCAL_BENCHMARK_MEDIAN,
        ),
    )
    fixed_reference = _build_guidance(
        RESULT_GUIDANCE_DRILLDOWN,
        analysis_context=AnalysisContext(
            comparison_mode=COMPARISON_REFERENCE_STATION,
        ),
    )

    median_read = RESULT_GUIDANCE["en"]["sections"][
        "drilldown_local_median"
    ]["read"]
    median_limits = RESULT_GUIDANCE["en"]["sections"][
        "drilldown_local_median"
    ]["limits"]
    assert median_read in local_median
    assert median_limits in local_median
    assert median_read not in fixed_reference
    assert median_limits not in fixed_reference
    assert RESULT_GUIDANCE["en"]["sections"]["drilldown_compare_joint"][
        "read"
    ] in local_median


@pytest.mark.parametrize("language", ("en", "de"))
@pytest.mark.parametrize("direction", ("RX", "TX"))
@pytest.mark.parametrize(
    ("section_id", "catalog_key"),
    (
        (RESULT_GUIDANCE_TEMPORAL_EVIDENCE_COVERAGE, "temporal_evidence_coverage_joint"),
        (RESULT_GUIDANCE_OUTLIER_FOCUS, "outlier_focus"),
    ),
)
def test_new_benchmark_guidance_routes_and_rejects_performance(
    language, direction, section_id, catalog_key
):
    """Route relocated interpretation to its own Benchmark-only help location."""
    context = AnalysisContext(comparison_mode=COMPARISON_REFERENCE_STATION)
    guidance = _build_guidance(
        section_id, language=language, analysis_id=f"{direction}_COMP",
        analysis_context=context,
    )
    item = RESULT_GUIDANCE[language]["sections"][catalog_key]
    assert item["read"] in guidance
    assert item["limits"] in guidance
    assert not _format_fields(guidance)
    assert guidance.count("<strong") == guidance.count("</strong>")
    with pytest.raises(ValueError, match="unavailable for Performance"):
        _build_guidance(
            section_id, language=language, analysis_id=f"{direction}_ABS",
            is_compare=False, analysis_context=AnalysisContext(),
        )


@pytest.mark.parametrize("language", ("en", "de"))
@pytest.mark.parametrize("direction", ("rx", "tx"))
def test_header_and_drilldown_omit_repeated_snr_definitions(language, direction):
    """Keep orientation above the map and practical table/plot guidance in Drill-Down."""
    sections = RESULT_GUIDANCE[language]["sections"]
    compare = _plain_guidance(sections[f"context_{direction}_compare"]["read"])
    performance = _plain_guidance(sections[f"context_{direction}_success"]["read"])
    for text in (compare, performance):
        assert "result header" not in text
        assert "UTC window" not in text
        assert "Ergebniskopf" not in text
        assert "UTC-Zeitfenster" not in text
        assert "offset" not in text.lower()
        assert "30 dBm" not in text
    drilldown = _plain_guidance(_build_guidance(
        RESULT_GUIDANCE_DRILLDOWN,
        language=language,
        analysis_id=f"{direction.upper()}_COMP",
        analysis_context=AnalysisContext(comparison_mode=COMPARISON_REFERENCE_STATION),
    ))
    if language == "en":
        assert "where and when relative signal levels differ" in compare
        assert "paired and one-sided evidence" in compare
        assert "geographic reach, Decode Rate, and successful signal levels" in performance
        expected = (
            "normalized Target and Reference SNR", "paired ΔSNR",
            "one actual value", "at its cycle time", "without time-bin medians",
            "only the displayed rows", "completed analysis unchanged",
        )
        removed = (
            "SNR is the reported signal-to-noise ratio",
            "normalized Target value minus the normalized Reference value",
        )
    else:
        assert "wo und wann sich die relativen Signalpegel unterscheiden" in compare
        assert "gepaarte und einseitige Evidenz" in compare
        assert "geografische Reichweite, Dekodierrate und erfolgreichen Signalpegel" in performance
        expected = (
            "normiertes Target- und Referenz-SNR", "gepaartes ΔSNR",
            "einen tatsächlichen Wert", "zu dessen Zykluszeit", "ohne Zeit-Bin-Mediane",
            "nur die angezeigten Zeilen", "abgeschlossene Analyse unverändert",
        )
        removed = (
            "SNR ist das gemeldete Signal-Rausch-Verhältnis",
            "normierte Target-Wert abzüglich des normierten Referenzwerts",
        )
    for phrase in expected:
        assert phrase in drilldown
    for phrase in removed:
        assert phrase not in drilldown


@pytest.mark.parametrize("language", ("en", "de"))
@pytest.mark.parametrize("direction", ("RX", "TX"))
@pytest.mark.parametrize("is_compare", (False, True), ids=("performance", "benchmark"))
def test_header_guidance_highlights_the_actual_mode_specific_result_headers(
    language, direction, is_compare,
):
    """Use the seven visible section headers in order and only the active evidence mode."""
    headings = _context_layout_headings(T[language], is_compare=is_compare)
    expected_path = " → ".join(headings.values())
    emphasized_path = f'<strong class="defined-term">{expected_path}</strong>'
    catalog_key = f"context_{direction.lower()}_{'compare' if is_compare else 'success'}"
    layout_template = RESULT_GUIDANCE[language]["context_layout"]
    assert _format_fields(layout_template) == set(headings)
    layout = layout_template.format(**headings)
    assert layout.count(emphasized_path) == 1
    assert emphasized_path not in RESULT_GUIDANCE[language]["sections"][catalog_key]["read"]
    guidance = _build_guidance(
        RESULT_GUIDANCE_CONTEXT,
        language=language,
        analysis_id=f"{direction}_{'COMP' if is_compare else 'ABS'}",
        is_compare=is_compare,
        analysis_context=AnalysisContext(
            comparison_mode=COMPARISON_REFERENCE_STATION if is_compare else COMPARISON_NONE,
        ),
    )
    assert guidance.count(emphasized_path) == 1
    assert f"{layout}\n\n**{RESULT_GUIDANCE[language]['limits_label']}**" in guidance
    inactive_evidence_key = (
        "hdr_results_success_evidence" if is_compare else "hdr_results_comparison_evidence"
    )
    assert T[language][inactive_evidence_key] not in guidance
    assert "Performance/Benchmark" not in guidance
    assert "Performance-/Benchmark" not in guidance
    assert not _format_fields(guidance)


@pytest.mark.parametrize("language", ("en", "de"))
@pytest.mark.parametrize("comparison_mode, benchmark_key", (
    (COMPARISON_REFERENCE_STATION, "benchmark_reference"),
    (COMPARISON_LOCAL_NEIGHBORHOOD, "benchmark_local_median"),
))
def test_benchmark_header_omits_reference_subtype_and_keeps_details_in_drilldown(
    language, comparison_mode, benchmark_key,
):
    """Keep the header on purpose/layout and preserve the full Reference explanation below."""
    context = AnalysisContext(comparison_mode=comparison_mode, neighborhood_radius_km=175)
    guidance = _build_guidance(
        RESULT_GUIDANCE_CONTEXT, language=language, analysis_context=context,
    )
    sections = RESULT_GUIDANCE[language]["sections"]
    base = sections["context_rx_compare"]
    assert f"context_{benchmark_key}" not in sections
    reference = sections[benchmark_key]
    format_values = {"radius": 175}
    layout = RESULT_GUIDANCE[language]["context_layout"].format(
        **_context_layout_headings(T[language], is_compare=True)
    )
    assert guidance == (
        f"**{RESULT_GUIDANCE[language]['read_label']}** {base['read']}\n\n{layout}\n\n"
        f"**{RESULT_GUIDANCE[language]['limits_label']}** {base['limits']}"
    )
    assert reference["read"].format(**format_values) not in guidance
    drilldown = _build_guidance(
        RESULT_GUIDANCE_DRILLDOWN, language=language, analysis_context=context,
    )
    detailed_read = reference["read"].format(**format_values)
    assert detailed_read in drilldown
    assert reference["limits"] in drilldown
    assert layout not in drilldown
    if comparison_mode == COMPARISON_LOCAL_NEIGHBORHOOD:
        assert f"{detailed_read}\n\n{sections['drilldown_local_median']['read']}" in drilldown


@pytest.mark.parametrize("language", ("en", "de"))
def test_benchmark_segment_help_omits_the_redundant_evidence_scope_paragraph(language):
    """Keep scope guidance concise while retaining the separate statistics label."""
    read_text = RESULT_GUIDANCE[language]["sections"]["segment"]["read"]
    scope_label = "Evidence in scope" if language == "en" else "Evidenz im aktiven Bereich"
    assert scope_label not in read_text
    assert scope_label in T[language]["txt_results_evidence_scope"]
    assert T[language]["hdr_results_segment_inspector"] in read_text
    assert ("active scope" if language == "en" else "aktiven Bereich") in read_text


@pytest.mark.parametrize("language", ("en", "de"))
@pytest.mark.parametrize("direction", ("rx", "tx"))
def test_benchmark_map_help_respects_evidence_minimums_and_spot_classification(language, direction):
    """Do not mistake map thresholds for evidence absence or station classes for spot counts."""
    item = RESULT_GUIDANCE[language]["sections"][f"map_compare_{direction}"]
    text = _plain_guidance(" ".join(item.values()))
    assert T[language]["leg_joint"] in text
    assert T[language]["leg_both_async"] in text
    assert T[language]["map_compare_footer_spots"] in text
    expected = (("Joint Spot requirement", "no qualifying Joint summary",
                 "unpaired observations from Joint-classified", "does not prove that no pairs existed")
                if language == "en" else
                ("Joint-Spot-Anforderung", "keine qualifizierende Joint-Zusammenfassung",
                 "ungepaarte Beobachtungen von als Joint eingestuften",
                 "beweist nicht, dass keine Paare vorlagen"))
    for phrase in expected:
        assert phrase in text
    assert "PAIRS" not in text
    assert "at least one usable pair" not in text


def _render_popover_snapshot(input_view):
    """Run one minimal result popover and return its visible semantic payload."""
    script = f"""
import streamlit as st
from core.analysis_context import AnalysisContext, COMPARISON_REFERENCE_STATION
from i18n import T
from ui.result_guidance import (
    RESULT_GUIDANCE_MAP,
    render_result_guidance_popover,
)

st.session_state["input_view"] = {input_view!r}
render_result_guidance_popover(
    RESULT_GUIDANCE_MAP,
    "Map View",
    language="en",
    translations=T["en"],
    key="result-guidance-map",
    analysis_id="RX_COMP",
    is_compare=True,
    analysis_context=AnalysisContext(
        comparison_mode=COMPARISON_REFERENCE_STATION
    ),
)
"""
    application = AppTest.from_string(script, default_timeout=10).run()

    assert not application.exception
    assert application.session_state["input_view"] == input_view
    assert len(application.get("popover")) == 1
    assert len(application.markdown) == 1
    popover_proto = application.get("popover")[0].proto
    return {
        "label": popover_proto.popover.label,
        "help": popover_proto.popover.help,
        "icon": popover_proto.popover.icon,
        "type": popover_proto.popover.type,
        "uses_content_width": popover_proto.width_config.use_content,
        "body": application.markdown[0].value,
        "allows_catalog_html": application.markdown[0].proto.allow_html,
    }


def test_result_popover_is_identical_in_guided_and_classic_input_views():
    """Expose the same optional interpretation layer in both input workflows."""
    guided = _render_popover_snapshot("guided")
    classic = _render_popover_snapshot("classic")

    assert guided == classic
    assert guided["label"] == RESULT_GUIDANCE["en"]["trigger"]
    assert guided["help"] == "How to read Map View"
    assert guided["icon"] == ":material/help_outline:"
    assert guided["type"] == "tertiary"
    assert guided["uses_content_width"] is True
    assert guided["allows_catalog_html"] is True
    assert RESULT_GUIDANCE["en"]["read_label"] in guided["body"]
    assert RESULT_GUIDANCE["en"]["limits_label"] in guided["body"]
    assert 'class="defined-term"' in guided["body"]
    assert "result-guidance-body-marker" in guided["body"]


def test_success_selected_popover_renders_singleton_guidance():
    """Render the exact singleton guidance at the Success selection point."""
    script = """
from core.analysis_context import AnalysisContext
from i18n import T
from ui.result_guidance import (
    RESULT_GUIDANCE_SELECTED_STATIONS,
    render_result_guidance_popover,
)

render_result_guidance_popover(
    RESULT_GUIDANCE_SELECTED_STATIONS,
    "Selected Station Evidence",
    language="en",
    translations=T["en"],
    key="result-guidance-selected",
    analysis_id="RX_ABS",
    is_compare=False,
    analysis_context=AnalysisContext(),
    selected_station_count=1,
)
"""
    application = AppTest.from_string(script, default_timeout=10).run()

    assert not application.exception
    assert len(application.markdown) == 1
    guidance_body = application.markdown[0].value
    assert "Selected Station SNR Evidence" in guidance_body
    assert "Selected Station Temporal Evidence" in guidance_body
    assert "successful Target SNR normalized to 30 dBm" in _plain_guidance(guidance_body)
    assert "combined observation-weighted selection" not in guidance_body
    assert "Selected Path Summary" not in guidance_body


def test_result_guidance_popover_css_is_wide_and_responsive():
    """Keep the help body readable without widening its compact trigger."""
    css_source = (REPOSITORY_ROOT / "ui" / "css.py").read_text(
        encoding="utf-8"
    )
    scoped_selector = (
        'div[data-testid="stPopoverBody"]:has(.result-guidance-body-marker)'
    )

    assert scoped_selector in css_source
    assert "width: min(66.667vw, 43rem) !important;" in css_source
    assert "max-width: calc(100vw - 2rem) !important;" in css_source
    assert "min-width: 0 !important;" in css_source
    assert "@media (max-width: 768px)" in css_source
    assert "width: calc(100vw - 2rem) !important;" in css_source
    assert (
        f"{scoped_selector}\n"
        "            .stMarkdown strong.defined-term"
    ) in css_source
    assert (
        f"{scoped_selector}\n"
        "            .stMarkdown p"
    ) in css_source
    assert "font-family: Arial, Helvetica, sans-serif !important;" in css_source


def test_result_guidance_trigger_uses_scoped_information_blue():
    """Color only result-help triggers blue while preserving the body term styling."""
    css_source = (REPOSITORY_ROOT / "ui" / "css.py").read_text(encoding="utf-8")
    selector = '[class*="st-key-results_guidance_"] button[kind="tertiary"]'
    for suffix in ("", ":hover"):
        rule = re.search(re.escape(selector + suffix) + r"\s*\{([^}]+)\}", css_source)
        assert rule is not None
        assert "color: #3d9df3 !important;" in rule.group(1)
    assert ".stMarkdown strong.defined-term" in css_source


def _guidance_call_sections(relative_path):
    """Return the semantic section constants passed at one renderer call site."""
    source_path = REPOSITORY_ROOT / relative_path
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    sections = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Name):
            continue
        if node.func.id != "render_result_guidance_popover":
            continue
        assert node.args and isinstance(node.args[0], ast.Name), relative_path
        sections.append(node.args[0].id)
    return Counter(sections)


def test_every_rendered_result_heading_has_its_expected_guidance_placement():
    """Keep optional help attached to the complete shared result hierarchy."""
    assert _guidance_call_sections("ui/run_controller.py") == Counter(
        {
            "RESULT_GUIDANCE_CONTEXT": 1,
            "RESULT_GUIDANCE_MAP": 1,
        }
    )
    assert _guidance_call_sections("ui/results_export.py") == Counter(
        {"RESULT_GUIDANCE_DOWNLOAD": 1}
    )
    assert sum(
        (_guidance_call_sections(f"ui/components/{module}.py") for module in (
            "segment_inspector", "inspector_scope", "inspector_stations",
            "inspector_outliers", "inspector_selected",
        )), Counter(),
    ) == Counter(
        {
            "RESULT_GUIDANCE_SEGMENT": 1,
            "RESULT_GUIDANCE_COMPARISON_EVIDENCE": 1,
            "RESULT_GUIDANCE_TEMPORAL_EVIDENCE": 1,
            "RESULT_GUIDANCE_TEMPORAL_EVIDENCE_COVERAGE": 1,
            "RESULT_GUIDANCE_OUTLIER_REPORT": 1,
            "RESULT_GUIDANCE_OUTLIER_FOCUS": 1,
            "RESULT_GUIDANCE_SUCCESS_EVIDENCE": 1,
            "RESULT_GUIDANCE_STATION_INSIGHTS": 2,
            "RESULT_GUIDANCE_SELECTED_STATIONS": 2,
            "RESULT_GUIDANCE_DRILLDOWN": 1,
        }
    )

    documentation_source = (
        REPOSITORY_ROOT / "ui" / "documentation.py"
    ).read_text(encoding="utf-8")
    assert "render_result_guidance_popover" not in documentation_source
