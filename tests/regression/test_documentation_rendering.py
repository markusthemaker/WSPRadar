import inspect
import re
from contextlib import nullcontext

import pytest

from docs.doc_de import DOC_DE
from docs.doc_en import DOC_EN
from docs.pdf_generator import get_docs
from i18n import T
from ui import documentation
from ui import css as ui_css


class _FakeStreamlit:
    def __init__(self, session_state=None):
        self.session_state = session_state if session_state is not None else {}
        self.markdowns = []
        self.container_keys = []
        self.buttons = []

    def columns(self, _widths, **_kwargs):
        return nullcontext(), nullcontext(), nullcontext()

    def container(self, *, key):
        self.container_keys.append(key)
        return nullcontext()

    def markdown(self, body, **kwargs):
        self.markdowns.append((body, kwargs))

    def button(self, label, *, icon, key, on_click, width):
        self.buttons.append(
            {
                "label": label,
                "icon": icon,
                "key": key,
                "on_click": on_click,
                "width": width,
            }
        )
        return False


def _labels(lang="en"):
    if lang == "de":
        return {
            "btn_load_full_documentation": "Vollst\u00e4ndige Dokumentation laden",
            "btn_hide_full_documentation": "Vollst\u00e4ndige Dokumentation ausblenden",
            "sub_documentation": T["de"]["sub_documentation"],
            "dev_credit": "credit",
        }
    return {
        "btn_load_full_documentation": "Load full documentation",
        "btn_hide_full_documentation": "Hide full documentation",
        "sub_documentation": T["en"]["sub_documentation"],
        "dev_credit": "credit",
    }


def _render_with_fake_streamlit(monkeypatch, fake_st, lang="en"):
    pdf_calls = []
    scroll_trigger_calls = []
    monkeypatch.setattr(documentation, "st", fake_st)
    monkeypatch.setattr(
        documentation,
        "render_documentation_pdf_control",
        lambda *args: pdf_calls.append(args),
    )
    monkeypatch.setattr(
        documentation,
        "render_documentation_scroll_trigger",
        lambda **kwargs: scroll_trigger_calls.append(kwargs),
    )
    labels = _labels(lang)
    documentation._render_documentation_section(labels, lang, "logo", "v1")
    return labels, pdf_calls, scroll_trigger_calls


def _assert_documentation_trigger_call(
    trigger_call,
    documentation_text,
    *,
    is_auto_expand_enabled,
    is_documentation_expanded,
    allow_initial_hash_expansion,
):
    """Assert the stable browser-controller inputs without duplicating anchors."""
    assert trigger_call == {
        "key": documentation.DOCUMENTATION_SCROLL_TRIGGER_KEY,
        "anchor_ids": documentation._documentation_anchor_ids(documentation_text),
        "is_auto_expand_enabled": is_auto_expand_enabled,
        "is_documentation_expanded": is_documentation_expanded,
        "allow_initial_hash_expansion": allow_initial_hash_expansion,
        "on_navigation": documentation._expand_documentation_from_navigation,
        "on_trigger": documentation._expand_documentation_from_scroll,
    }


@pytest.mark.parametrize(
    ("lang", "title"),
    (("en", "Documentation"), ("de", "Dokumentation")),
)
def test_documentation_uses_green_semantic_heading_and_subtitle(
    monkeypatch,
    lang,
    title,
):
    """Keep the manual distinct while aligning it with the result hierarchy."""
    fake_st = _FakeStreamlit(session_state={"lang": lang})
    _render_with_fake_streamlit(monkeypatch, fake_st, lang=lang)

    heading_bodies = [
        body
        for body, _kwargs in fake_st.markdowns
        if "documentation-section-title" in body
    ]

    assert len(heading_bodies) == 1
    assert f">{title}</h2>" in heading_bodies[0]
    assert "color: #39ff14" in heading_bodies[0]
    assert T[lang]["sub_documentation"] in heading_bodies[0]


def test_documentation_text_is_process_cached_without_modification():
    get_docs.cache_clear()

    assert get_docs("en") is DOC_EN
    assert get_docs("de") is DOC_DE
    assert get_docs("en") is DOC_EN
    assert get_docs.cache_info().hits == 1


@pytest.mark.parametrize("documentation_text", (DOC_EN, DOC_DE), ids=("en", "de"))
def test_documentation_anchor_extraction_is_ordered_and_complete(documentation_text):
    """Pass every explicit manual anchor to the browser navigation controller."""
    anchor_ids = documentation._documentation_anchor_ids(documentation_text)

    assert anchor_ids[0] == "sec-1"
    assert "documentation-toc" in anchor_ids
    assert "sec-2" in anchor_ids
    assert "ref-1" in anchor_ids
    assert len(anchor_ids) == len(set(anchor_ids))


def test_manual_names_primary_and_fallback_sources_concisely():
    english_sentence_pattern = re.compile(
        r"WSPRadar uses wspr\.live as its primary WSPR data source "
        r'<a href="#ref-(?P<primary>\d+)">\[Ref-(?P=primary)\]</a>, with '
        r"WSPRDaemon WD2 and WD1 as fallback sources "
        r'<a href="#ref-(?P<fallback>\d+)">\[Ref-(?P=fallback)\]</a>\.'
    )
    german_sentence_pattern = re.compile(
        r"WSPRadar nutzt wspr\.live als primäre WSPR-Datenquelle "
        r'<a href="#ref-(?P<primary>\d+)">\[Ref-(?P=primary)\]</a>; '
        r"WSPRDaemon WD2 und WD1 dienen als Ausweichquellen "
        r'<a href="#ref-(?P<fallback>\d+)">\[Ref-(?P=fallback)\]</a>\.'
    )

    for manual, source_sentence_pattern in (
        (DOC_EN, english_sentence_pattern),
        (DOC_DE, german_sentence_pattern),
    ):
        source_sentence_matches = list(source_sentence_pattern.finditer(manual))
        assert len(source_sentence_matches) == 1
        source_sentence = source_sentence_matches[0].group(0)
        containing_paragraph = next(
            paragraph
            for paragraph in manual.split("\n\n")
            if source_sentence in paragraph
        )
        assert len(re.findall(r"\S+", containing_paragraph)) < 100


def test_load_and_hide_controls_have_english_and_german_labels():
    assert T["en"]["btn_load_full_documentation"] == "Load full documentation"
    assert T["en"]["btn_hide_full_documentation"] == "Hide full documentation"
    assert (
        T["de"]["btn_load_full_documentation"]
        == "Vollst\u00e4ndige Dokumentation laden"
    )
    assert (
        T["de"]["btn_hide_full_documentation"]
        == "Vollst\u00e4ndige Dokumentation ausblenden"
    )


@pytest.mark.parametrize(
    ("documentation_text", "section_one_heading", "toc_heading"),
    [
        (DOC_EN, "### 0. Why WSPRadar?", "### Table of Contents"),
        (DOC_DE, "### 0. Warum WSPRadar?", "### Inhaltsverzeichnis"),
    ],
    ids=("en", "de"),
)
def test_manual_split_is_three_way_lossless_and_language_independent(
    documentation_text,
    section_one_heading,
    toc_heading,
):
    section_one, table_of_contents, remaining_sections = (
        documentation._split_documentation_sections(documentation_text)
    )

    assert section_one_heading in section_one
    assert '<a id="sec-1-3"></a>' in section_one
    assert '<a id="sec-1-4"></a>' in section_one
    assert documentation.DOCUMENTATION_TOC_MARKER not in section_one
    assert documentation.DOCUMENTATION_SECTION_TWO_MARKER not in section_one
    assert table_of_contents.startswith(documentation.DOCUMENTATION_TOC_MARKER)
    assert toc_heading in table_of_contents
    assert documentation.DOCUMENTATION_SECTION_TWO_MARKER not in table_of_contents
    assert remaining_sections.startswith(
        documentation.DOCUMENTATION_SECTION_TWO_MARKER
    )
    assert section_one + table_of_contents + remaining_sections == documentation_text

    section_one_lead, section_one_completion = (
        documentation._split_section_one_at_scroll_boundary(section_one)
    )
    assert documentation.DOCUMENTATION_SECTION_ONE_TRIGGER_MARKER not in section_one_lead
    assert section_one_completion.startswith(
        documentation.DOCUMENTATION_SECTION_ONE_TRIGGER_MARKER
    )
    assert section_one_lead + section_one_completion == section_one


@pytest.mark.parametrize("documentation_text", (DOC_EN, DOC_DE), ids=("en", "de"))
def test_manual_contains_one_stable_toc_marker_before_section_two(documentation_text):
    assert documentation_text.count(documentation.DOCUMENTATION_TOC_MARKER) == 1
    assert documentation_text.count(documentation.DOCUMENTATION_SECTION_TWO_MARKER) == 1
    assert documentation_text.index(
        documentation.DOCUMENTATION_TOC_MARKER
    ) < documentation_text.index(documentation.DOCUMENTATION_SECTION_TWO_MARKER)


def test_english_preface_numbering_and_key_defined_terms_are_explicit():
    """The English preface must remain distinct from numbered operator chapters."""
    assert "## Part 0: Preface" not in DOC_EN
    assert DOC_EN.count("**Part 0: Preface**") == 1
    assert "### 0. Why WSPRadar?" in DOC_EN
    assert "#### 0.3 What one run produces" in DOC_EN
    assert "#### 0.4 Your first useful run: start with a guided demo" in DOC_EN
    assert "`Run Selected Demo`" in DOC_EN
    assert "`Load Selected Demo Configuration`" in DOC_EN
    assert "A demo is a worked example of WSPRadar's method" in DOC_EN
    assert "### 1. Experiment Playbooks" in DOC_EN
    assert '<strong class="defined-term">Target</strong>' in DOC_EN
    assert '<strong class="defined-term">Reference</strong>' in DOC_EN
    assert '<strong class="defined-term">Performance</strong>' in DOC_EN


def test_english_playbooks_define_performance_evidence_and_tx_ab_timing():
    """Operator playbooks must retain the clarified Performance and TX A/B guidance."""
    assert '<strong class="defined-term">qualifying evidence</strong>' in DOC_EN
    assert (
        "independently confirmed WSPR opportunities represented in the selected evidence"
        in DOC_EN
    )
    assert "actual recurrence and UTC phase" in DOC_EN
    assert "WSPRadar forms scheduled pairs automatically." in DOC_EN
    assert "[Sections 7.1](#sec-7-1) and [7.7](#sec-7-7)" in DOC_EN
    assert "#### B.3 Ultimate3S schedule example" in DOC_EN
    assert "`Repeat Interval = 20`, `Target Start = 00`, `Reference Start = 10`" in DOC_EN
    assert "an invented power difference into an artificial comparison offset" in DOC_EN
    assert '<a id="sec-b-5"></a>' in DOC_EN


def test_bilingual_tx_hardware_playbooks_cover_both_methods_and_fixed_identity():
    """Keep the operator method choice, matching rules, and gate boundary aligned."""
    expected_anchors = (
        '<a id="sec-2-4-simultaneous"></a>',
        '<a id="sec-2-4-sequential"></a>',
        '<a id="sec-a-4"></a>',
    )
    for manual in (DOC_EN, DOC_DE):
        for anchor in expected_anchors:
            assert anchor in manual
        assert "1450 Hz" in manual
        assert "1550 Hz" in manual
        assert "Setup A" not in manual
        assert "Setup B" not in manual

    assert "TX Hardware A/B offers two methods" in DOC_EN
    assert "TX Hardware A/B bietet zwei Methoden" in DOC_DE
    assert "`Simultaneous TX` is the default" in DOC_EN
    assert "`Simultanes TX` ist die Voreinstellung" in DOC_DE
    assert "Target callsign` and `Reference callsign" in DOC_EN
    assert "Target-Rufzeichen` und `Referenz-Rufzeichen" in DOC_DE
    assert "exact callsign plus its own grid-4" in DOC_EN
    assert "jeweiligen exakten Rufzeichens plus des eigenen Grid-4" in DOC_DE
    assert "Target was decoded nowhere is excluded" in DOC_EN
    assert "Target jedoch nirgends, wird ausgeschlossen" in DOC_DE
    assert "Earlier unpublished v1 prototypes are not migrated" in DOC_EN
    assert "nicht veröffentlichte v1-Prototypen werden nicht migriert" in DOC_DE


def test_bilingual_manuals_define_hyphen_suffix_as_one_exact_identity():
    """Recommend standard forms while documenting the accepted archive token."""
    assert "Prefer standard callsign forms" in DOC_EN
    assert "Bevorzuge standardmäßige Rufzeichenformen" in DOC_DE
    assert "`DL1MKS-1`" in DOC_EN
    assert "`DL1MKS-1`" in DOC_DE
    assert "neither treats `/` and `-` as aliases" in DOC_EN
    assert "behandelt `/` und `-` weder als gleichbedeutend" in DOC_DE


def test_bilingual_manuals_document_explicit_snr_correction_modes():
    """Keep the durable correction meaning distinct from its numeric dB value."""
    assert "`no_offset` and `establish_offset` require `0.0 dB`" in DOC_EN
    assert "`no_offset` und `establish_offset` verlangen `0,0 dB`" in DOC_DE
    assert "`Set up an offset-establishment run`" in DOC_EN
    assert "`Offset-Ermittlungslauf einrichten`" in DOC_DE
    for manual in (DOC_EN, DOC_DE):
        assert "`benchmark_snr_correction_mode`" in manual
        assert "`benchmark_snr_correction_db`" in manual


def test_results_chapter_uses_concise_evidence_path_and_consecutive_sections():
    """Chapter 2 must use the same concise path while retaining its evidence sections."""
    assert "#### 2.1 Confirm the run identity" not in DOC_EN
    assert (
        "**Performance:** Map → Segment Inspector → Station Insights → Drill-Down."
    ) in DOC_EN
    assert (
        "**Compare:** Map → Segment Inspector → Station Insights → Drill-Down."
    ) in DOC_EN
    assert (
        "**Performance:** Karte → Segment-Inspektor → Station Insights → Drill-Down."
    ) in DOC_DE
    assert (
        "**Compare:** Karte → Segment-Inspektor → Station Insights → Drill-Down."
    ) in DOC_DE
    assert "#### 2.1 Read a Performance result" in DOC_EN
    assert "#### 2.2 Read a Compare result" in DOC_EN
    assert "#### 2.8 Worked Compare example" in DOC_EN

    rx_explanation = DOC_EN.index("* In simultaneous RX Compare")
    tx_explanation = DOC_EN.index("* In same-cycle TX Compare")
    sequential_explanation = DOC_EN.index(
        "* Sequential TX Hardware A/B uses deterministic scheduled pairs"
    )
    assert rx_explanation < tx_explanation < sequential_explanation


def test_bilingual_manuals_explain_the_performance_evidence_redesign():
    """Keep exact-distance, temporal-SNR and weighting contracts auditable."""
    english_contract = (
        "OPPORTUNITIES",
        "Station-balanced Decode Rate",
        "Opportunity-level Decode Rate",
        "The station-group counts describe at-least-once reach",
        "Its displayed counts do form that rate's numerator and denominator",
        "TX Stations Heard by Target at Least Once by Distance",
        "RX Stations Hearing the Target at Least Once by Distance",
        "RX Decode Rate by TX-Station Distance",
        "TX Decode Rate by RX-Station Distance",
        "Successful Target SNR by TX-Station Distance",
        "Successful Target SNR by RX-Station Distance",
        "exact, unrounded calculated distance",
        "full qualifying station population",
        "`Show Heard by others only stations`",
        "`Show Other signals heard only stations`",
        "Heard by Target without independent confirmation",
        "Target heard without independent RX-activity confirmation",
        "retained support data",
        "does not render a support-count strip",
        "at least three successful Target SNR observations",
        "station-date-hour median",
        "two vertically aligned figures",
        "RX Performance Temporal SNR Evidence: Target {callsign}",
        "RX Performance Temporal Evidence: Target {callsign}",
        "Evidence over Time ({time_bin} bins)",
        "Evidence by UTC Hour (1 h bins)",
        "Average contributing station presences per represented UTC date",
        "Average confirmed opportunities per represented UTC date",
        "short **TX Stations** or **RX Stations** y-axis title",
        "short **Opportunities** y-axis title",
        "every contributing qualifying station gives one total vote",
        "right-axis line is the Station-balanced Decode Rate",
        "counts every confirmed opportunity once",
        "right-axis line is the unchanged Opportunity-level Decode Rate",
        "One shared legend below the lower figure title",
        "All four right axes use one zero-based Decode Rate scale",
        "average number of distinct station-date-hour presences over represented dates",
        "represented date-hour with no evidence remains in the denominator with zero support",
        "unchanged folded Station-balanced Decode Rate",
        "unchanged Opportunity-level Decode Rate",
        "A **represented UTC date** is a date with at least one confirmed opportunity",
        "compact ham-style notation",
        "Successful-SNR censoring remains possible",
        "station-vote segments can be fractional",
        "`figure_segment_temporal_snr_deviation.png` contains the chronological/UTC-hour",
        "`figure_segment_temporal_evidence.png` contains the aligned lower **RX/TX Performance Temporal Evidence** figure",
        "`1 h`, `2 h`, `3 h`, `6 h`, `12 h` or `24 h`",
        "at least two UTC dates",
        "Empty or sparse rate bins are missing or thin evidence, not failures",
        "Grid-4 is not survey-grade positioning",
    )
    german_contract = (
        "GELEGENHEITEN",
        "stationsgleichgewichtete Dekodierrate",
        "Dekodierrate auf Gelegenheitsebene",
        "Die Anzahlen der Stationsgruppen beschreiben eine Mindestens-einmal-Reichweite",
        "Ihre angezeigten Anzahlen bilden den Zähler und Nenner dieser Rate",
        "Vom Target mindestens einmal gehörte TX-Stationen nach Entfernung",
        "RX-Stationen, die das Target mindestens einmal hörten, nach Entfernung",
        "RX Dekodierrate nach Entfernung der TX-Station",
        "TX Dekodierrate nach Entfernung der RX-Station",
        "Erfolgreiches Target-SNR nach Entfernung der TX-Station",
        "Erfolgreiches Target-SNR nach Entfernung der RX-Station",
        "exakten, ungerundeten berechneten Entfernung",
        "vollständigen qualifizierenden Stationspopulation",
        "`Stationen „Nur von anderen gehört“ anzeigen`",
        "`Stationen „Nur andere Signale gehört“ anzeigen`",
        "Vom Target gehört, aber nicht unabhängig bestätigt",
        "Target gehört, RX-Aktivität nicht unabhängig bestätigt",
        "beibehaltenen Stützdaten",
        "keinen Streifen mit Stützzahlen",
        "mindestens drei erfolgreichen Target-SNR-Beobachtungen",
        "Stations-Datum-Stunden-Median",
        "zwei vertikal ausgerichtete Abbildungen",
        "RX Performance — Zeitliche SNR-Evidenz: Target {callsign}",
        "RX Performance — Zeitliche Evidenz: Target {callsign}",
        "Evidenz im Zeitverlauf ({time_bin}-Bins)",
        "Evidenz nach UTC-Stunde (1-h-Bins)",
        "Durchschnittliche Stationspräsenzen pro berücksichtigtem UTC-Tag",
        "Durchschnittliche bestätigte Gelegenheiten pro berücksichtigtem UTC-Tag",
        "kurzen y-Achsentitel **TX-Stationen** beziehungsweise **RX-Stationen**",
        "kurzen y-Achsentitel **Gelegenheiten**",
        "eine Gesamtstimme ab",
        "Linie an der rechten Achse zeigt die stationsgleichgewichtete Dekodierrate",
        "zählt jede bestätigte Gelegenheit chronologisch einmal",
        "Linie an der rechten Achse zeigt die unveränderte Dekodierrate auf Gelegenheitsebene",
        "Eine gemeinsame Legende unter dem Titel der unteren Abbildung",
        "Alle vier rechten Achsen verwenden eine gemeinsame",
        "durchschnittliche Zahl verschiedener Stations-Datum-Stunden-Präsenzen über die berücksichtigten Tage",
        "eine berücksichtigte Datum-Stunde ohne Evidenz bleibt mit null Stützung im Nenner",
        "unveränderten gefalteten stationsgleichgewichteten Dekodierrate",
        "unveränderte Dekodierrate auf Gelegenheitsebene",
        "Ein **berücksichtigter UTC-Tag** ist ein Tag, an dem",
        "kompakte Amateurfunk-Schreibweisen",
        "Zensierung des erfolgreichen SNR bleibt möglich",
        "Segmente der Stationsstimmen können Bruchteile enthalten",
        "`figure_segment_temporal_snr_deviation.png` enthält die chronologische",
        "`figure_segment_temporal_evidence.png` enthält die daran ausgerichtete untere Abbildung **RX/TX Performance — Zeitliche Evidenz**",
        "`1 h`, `2 h`, `3 h`, `6 h`, `12 h` oder `24 h`",
        "mindestens zwei UTC-Tage",
        "Leere oder schwach belegte Raten-Bins sind fehlende oder dünne Evidenz",
        "Grid-4 ist keine vermessungsgenaue Positionierung",
    )

    for required_text in english_contract:
        assert required_text in DOC_EN
    for required_text in german_contract:
        assert required_text in DOC_DE

    performance_section_en = DOC_EN.split(
        "#### 2.5a Inspect a Geographic Segment (Performance Mode)", 1
    )[1].split("#### 2.5b Inspect a Geographic Segment (Compare Mode)", 1)[0]
    performance_section_de = DOC_DE.split(
        "#### 2.5a Ein geografisches Segment untersuchen (Performance-Modus)", 1
    )[1].split(
        "#### 2.5b Ein geografisches Segment untersuchen (Compare-Modus)", 1
    )[0]
    for retired_text in (
        "Station Success Rate by Evidence Count",
        "Station Success Distribution",
        "Evidence Depth per Station",
        "Success by Distance uses the same radial ranges as the map",
        "Success over time",
        "**Success Rate over Time/by UTC Hour**",
        "**Evidence Support over Time/by UTC Hour**",
        "Station-Balanced Evidence over Time/by UTC Hour",
        "Confirmed Opportunities over Time/by UTC Hour",
        "The folded opportunity subtitle therefore reads",
        "**Average per represented UTC date**",
        "rather than being repeated as temporal lines",
        "implicitly rather than as percentage lines",
        "stacks the raw Target and counter-evidence counts",
    ):
        assert retired_text not in performance_section_en
    for retired_text in (
        "Station Success Rate by Evidence Count",
        "Verteilung der Stations-Success-Rate",
        "Evidenztiefe pro Station",
        "Success nach Entfernung verwendet dieselben radialen Bereiche wie die Karte",
        "Success im Zeitverlauf",
        "Gewichtungsabstand",
        "**Success Rate im Zeitverlauf/nach UTC-Stunde**",
        "**Evidenzumfang im Zeitverlauf/nach UTC-Stunde**",
        "Stationsgleichgewichtete Evidenz im Zeitverlauf/nach UTC-Stunde",
        "Bestätigte Gelegenheiten im Zeitverlauf/nach UTC-Stunde",
        "Der Untertitel des gefalteten Gelegenheits-Panels lautet",
        "**Durchschnitt pro berücksichtigtem UTC-Tag**",
        "statt als Zeitlinien wiederholt zu werden",
        "implizit statt als Prozentlinien",
        "stapelt stattdessen die rohen Anzahlen",
    ):
        assert retired_text not in performance_section_de


def test_bilingual_manuals_define_performance_selected_singleton_and_exports():
    """Keep singleton selection, shared temporal science, and artifacts explicit."""
    english_contract = (
        "Select exactly one station row to open `Selected Station Evidence`",
        "Selecting another row replaces the current station",
        "clearing the row hides the section",
        "Performance saves zero or one exact `callsign + locator` identity",
        "restoration retains the first valid identity in stored order",
        "never substitutes a different station",
        "restores no selection if none remain valid",
        "actual normalized successful Target SNR",
        "chronological density receives every retained successful observation",
        "one median for every represented UTC date and UTC hour",
        "prevents a date with unusually many successful reports from dominating",
        "separates station presence from opportunity depth",
        "total station height is one",
        "opportunity row stacks every confirmed successful and counter opportunity",
        "Station-balanced Decode Rate and the Opportunity-level Decode Rate are numerically identical",
        "conditional on successful Target decodes or reports",
        "Counter outcomes have no recorded Target SNR",
        "successful-decode censoring",
        "UTC-hour folding requires at least two represented UTC dates",
        "do not rerun the provider query",
    )
    german_contract = (
        "Wähle genau eine Stationszeile aus, um die `Evidenz der ausgewählten Station` zu öffnen",
        "Die Auswahl einer anderen Zeile ersetzt die bisherige Station",
        "das Aufheben der Auswahl blendet den Abschnitt aus",
        "Performance speichert keine oder genau eine exakte Identität",
        "erste gültige Identität in gespeicherter Reihenfolge",
        "ersetzt sie nie durch eine andere Station",
        "stellt keine Auswahl wieder her, wenn keine Identität gültig bleibt",
        "tatsächlichen normierten erfolgreichen Target-SNR",
        "jede beibehaltene erfolgreiche Beobachtung dieses Funkwegs",
        "einen Median für jedes berücksichtigte UTC-Datum und jede UTC-Stunde",
        "verhindert, dass ein Tag mit ungewöhnlich vielen erfolgreichen Reports",
        "trennt Stationspräsenz von Evidenztiefe",
        "gesamte Stationshöhe ist damit eins",
        "stapelt jede bestätigte Gelegenheit mit erfolgreichem beziehungsweise Gegen-Outcome",
        "stationsgleichgewichtete Dekodierrate und die Dekodierrate auf Gelegenheitsebene",
        "durch erfolgreiche Target-Decodes beziehungsweise Target-Reports bedingt",
        "Gegen-Outcomes besitzen kein aufgezeichnetes Target-SNR",
        "Zensierung auf erfolgreiche Decodes",
        "mindestens zwei berücksichtigte UTC-Tage",
        "starten keine Provider-Abfrage erneut",
    )

    for required_text in english_contract:
        assert required_text in DOC_EN
    for required_text in german_contract:
        assert required_text in DOC_DE

    selected_performance_filenames = (
        "figure_selected_station_snr_evidence.png",
        "figure_selected_station_temporal_evidence.png",
    )
    obsolete_performance_filenames = (
        "figure_selected_station_chronological.png",
        "figure_selected_station_utc_hour_profile.png",
        "figure_selected_station_snr_distribution.png",
        "figure_selected_station_similar_stations.png",
    )
    metadata_fields = (
        "`selected_station_label`",
        "`selected_station_context`",
        "`selected_station_count`",
        "`selected_station_role`",
        "`selected_evidence_weighting`",
        "`selected_evidence_figures`",
    )
    for manual in (DOC_EN, DOC_DE):
        compare_export_listing = manual.split("compare/", 1)[1].split(
            "success/",
            1,
        )[0]
        performance_export_listing = manual.split("success/", 1)[1].split(
            "```",
            1,
        )[0]
        for filename in selected_performance_filenames:
            assert filename in performance_export_listing
            assert filename in manual
        for filename in obsolete_performance_filenames:
            assert filename not in performance_export_listing
            assert filename not in manual
        assert "figure_selected_station_evidence.png" in compare_export_listing
        assert (
            "figure_selected_station_evidence.png"
            not in performance_export_listing
        )
        for metadata_field in metadata_fields:
            assert metadata_field in manual

    performance_section_en = DOC_EN.split(
        "#### 2.6a Inspect the Contributing Stations (Performance Mode)", 1
    )[1].split("#### 2.6b Inspect the Contributing Stations (Compare Mode)", 1)[0]
    performance_section_de = DOC_DE.split(
        "#### 2.6a Die beitragenden Stationen untersuchen (Performance-Modus)", 1
    )[1].split(
        "#### 2.6b Die beitragenden Stationen untersuchen (Compare-Modus)", 1
    )[0]
    for retired_text in (
        "Selected Path Summary",
        "Selected Stations Summary",
        "SNR Distribution",
        "Selected Path vs. Similar Stations",
        "Selected Stations vs. Similar Stations",
    ):
        assert retired_text not in performance_section_en
    for retired_text in (
        "Zusammenfassung des ausgewählten Funkwegs",
        "Zusammenfassung ausgewählter Stationen",
        "SNR-Verteilung",
        "Ausgewählter Funkweg im Vergleich zu ähnlichen Stationen",
        "Ausgewählte Stationen im Vergleich zu ähnlichen Stationen",
    ):
        assert retired_text not in performance_section_de

    assert "Select one or multiple stations" in DOC_EN
    assert "Wähle eine oder mehrere Stationen aus" in DOC_DE


def test_bilingual_manuals_explain_simplified_performance_map_semantics():
    """Document the sole quantitative layer, status markers, and missing state."""
    english_contract = (
        "sector fill is the only quantitative color layer",
        "a small solid dark-green marker means `Heard by Target`",
        "a small solid light-grey marker means `Heard by others only`",
        "`Target heard` and `Other signals heard only`",
        "encode neither individual Decode Rate nor evidence depth",
        "dark-green markers are drawn above light-grey markers",
        "remains unfilled so the neutral base map shows through",
        "A valid Performance sector at `0%` remains on the Decode Rate scale",
        "`Insufficient evidence` is a different state",
        "upper <strong class=\"defined-term\">OPPORTUNITIES</strong> row",
        "lower <strong class=\"defined-term\">STATIONS</strong> row",
        "Exact counts appear inside segments when they fit",
    )
    german_contract = (
        "Die Sektorfüllung ist die einzige quantitative Farbebene",
        "ein kleiner dunkelgrüner Vollmarker `Vom Target gehört`",
        "ein kleiner hellgrauer Vollmarker `Nur von anderen gehört`",
        "`Target gehört` und `Nur andere Signale gehört`",
        "codieren weder die individuelle Dekodierrate noch die Evidenztiefe",
        "werden dunkelgrüne Marker über hellgrauen Markern gezeichnet",
        "bleibt ungefüllt, sodass die neutrale Basiskarte",
        "Ein gültiges Performance-Segment bei `0%` bleibt Teil der Dekodierratenskala",
        "`Unzureichende Evidenz` ist ein anderer Zustand",
        "obere Zeile <strong class=\"defined-term\">GELEGENHEITEN</strong>",
        "untere Zeile <strong class=\"defined-term\">STATIONEN</strong>",
        "Exakte Anzahlen erscheinen in ausreichend breiten Segmenten",
    )

    for required_text in english_contract:
        assert required_text in DOC_EN
    for required_text in german_contract:
        assert required_text in DOC_DE

    assert (
        "uses the same scale for that station's individual Decode Rate"
        not in DOC_EN
    )
    assert (
        "dieselbe Skala für die individuelle Dekodierrate dieser Station"
        not in DOC_DE
    )


def test_bilingual_manuals_explain_dual_level_decode_outcome_bars():
    """Keep the operator interpretation aligned with the rendered Compare figure."""
    assert "The left, hatched bar in each category" in DOC_EN
    assert "the right, solid-blue bar" in DOC_EN
    assert "Each level is normalized against its own total" in DOC_EN
    assert "The total and Joint counts for each level appear" in DOC_EN
    assert "Der linke, schraffierte Balken jeder Kategorie" in DOC_DE
    assert "der rechte, vollblaue Balken" in DOC_DE
    assert "Jede Ebene wird gegen ihre eigene Gesamtsumme normiert" in DOC_DE
    assert "Die Gesamt- und Joint-Anzahlen jeder Ebene stehen" in DOC_DE


def test_bilingual_manuals_follow_reference_first_use_and_introductory_term_policy():
    """Meaningful documentation contracts must remain aligned across languages."""
    for manual in (DOC_EN, DOC_DE):
        before_references = manual.split('<a id="sec-ref"></a>', 1)[0]
        first_use_order = list(
            dict.fromkeys(
                int(number)
                for number in re.findall(r'href="#ref-(\d+)"', before_references)
            )
        )

        assert first_use_order == list(range(1, 19))
        assert '<strong class="defined-term">Stability</strong>' not in manual
        assert "90% stability" not in manual.lower()
        assert "90-%-stability" not in manual.lower()
        assert "bootstrap" not in manual.lower()

        gate_diagnostic = manual.split('<a id="sec-6-5"></a>', 1)[1].split(
            '<a id="sec-6-6"></a>', 1
        )[0]
        assert "(#sec-7-3)" in gate_diagnostic

    assert '<strong class="defined-term">qualifying evidence</strong>' in DOC_EN
    assert '<strong class="defined-term">qualifizierende Evidenz</strong>' in DOC_DE
    assert "`Include Unpaired Evidence`" in DOC_EN
    assert "`Ungepaarte Evidenz einbeziehen`" in DOC_DE
    assert "where applicable" in DOC_EN
    assert "bei Compare gegebenenfalls" in DOC_DE
    assert "automatically records the application name and version" in DOC_EN
    assert "erfasst automatisch Anwendungsname und -version" in DOC_DE


def test_end_user_manuals_omit_internal_interval_boundary_convention():
    """Keep deterministic interval-boundary mechanics out of operator guidance."""
    assert "half-open" not in DOC_EN
    assert "start <= time < end" not in DOC_EN
    assert "halboffen" not in DOC_DE
    assert "start <= geplanter Start < end" not in DOC_DE


def test_bilingual_manuals_define_segment_temporal_density_and_scope():
    """Keep the new Compare temporal view scientifically and operationally explicit."""
    assert "exactly the same observation-level evidence rows" in DOC_EN
    assert "at least two distinct UTC dates" in DOC_EN
    assert "D_{relative} = 100" in DOC_EN
    assert "The selected view is stored in `.config`" in DOC_EN
    assert (
        "For Compare, the prompt `↓ Select time aggregation bin size` appears under `Temporal Evidence`"
        in DOC_EN
    )

    assert "genau dieselben Evidenzzeilen auf Beobachtungsebene" in DOC_DE
    assert "mindestens zwei verschiedenen UTC-Tagen" in DOC_DE
    assert "D_{relative} = 100" in DOC_DE
    assert "Die gewählte Ansicht wird in `.config` gespeichert" in DOC_DE
    assert (
        "Bei Compare steht die Aufforderung `↓ Zeitliche Aggregationsbreite auswählen` unter `Zeitliche Evidenz`"
        in DOC_DE
    )

    assert "percentage of that panel's maximum cell count" in DOC_EN
    assert "Prozentsatz der maximalen Zellbelegung dieses Panels" in DOC_DE
    assert "Tick labels show the resulting **absolute Delta SNR**" in DOC_EN
    assert "Die Skalenbeschriftungen zeigen das resultierende **absolute Delta SNR**" in DOC_DE
    assert "The two segment temporal panels share the observation-level median" in DOC_EN
    assert "Die beiden Zeitpanels des Segments teilen sich den Median" in DOC_DE
    assert "not the segment median above" in DOC_EN
    assert "nicht den darüber angezeigten Segmentmedian" in DOC_DE
    assert "M +/- 1`, `M +/- 3`, `M +/- 6` and `M +/- 10 dB" in DOC_EN
    assert "M +/- 3`, `M +/- 6`, `M +/- 10`, `M +/- 20` and `M +/- 30 dB" in DOC_EN
    assert "M +/- 1`, `M +/- 3`, `M +/- 6` und `M +/- 10 dB" in DOC_DE
    assert "M +/- 3`, `M +/- 6`, `M +/- 10`, `M +/- 20` und `M +/- 30 dB" in DOC_DE
    assert "Histogram counts and bin edges remain in raw dB" in DOC_EN
    assert "Anzahlen und Klassengrenzen der Histogramme bleiben in untransformierten dB-Werten" in DOC_DE
    assert "white connected markers remain a separate statistic" in DOC_EN
    assert "chronological density receives every retained successful observation" in DOC_EN
    assert "Die weißen verbundenen Marker bleiben eine eigene Statistik" in DOC_DE
    assert "jede beibehaltene erfolgreiche Beobachtung dieses Funkwegs" in DOC_DE
    for documentation_text in (DOC_EN, DOC_DE):
        assert (
            "figure_segment_temporal_snr_deviation.png"
            in documentation_text
        )
        assert "figure_segment_temporal_evidence.png" in documentation_text


def test_compare_map_uses_stepped_station_balanced_db_scale_bilingually():
    """Keep the map label and manual aligned with the signed stepped dB scale."""
    assert T["en"]["cbar_comp"] == "Station-balanced median \u0394SNR (dB)"
    assert (
        T["de"]["cbar_comp"]
        == "Stationsgleichgewichteter Median des \u0394SNR (dB)"
    )
    assert "symmetric stepped dB color scale" in DOC_EN
    assert "plum-to-mint sectors have negative Delta SNR" in DOC_EN
    assert "yellow-to-chestnut sectors have positive Delta SNR" in DOC_EN
    assert "Light yellow-green marks the display-neutral interval" in DOC_EN
    assert "display-neutral interval centered on `0 dB`" in DOC_EN
    assert "a `3 dB` scale uses `-1.5 dB` through `+1.5 dB`" in DOC_EN
    assert "Only exactly `0 dB` means equality" in DOC_EN
    assert "No fixed headroom is added" in DOC_EN
    assert "outer half-bin provides the natural margin" in DOC_EN
    assert "never narrows below `-6 dB` to `+6 dB`" in DOC_EN
    assert "symmetrische, abgestufte dB-Farbskala" in DOC_DE
    assert "Pflaumen- bis Minttöne kennzeichnen ein negatives Delta SNR" in DOC_DE
    assert "Gelb- bis Kastanientöne kennzeichnen ein positives Delta SNR" in DOC_DE
    assert "Helles Gelbgrün markiert das um `0 dB` zentrierte" in DOC_DE
    assert "um `0 dB` zentrierte darstellungsneutrale Intervall" in DOC_DE
    assert "eine `3-dB`-Skala verwendet beispielsweise `-1,5 dB` bis einschließlich `+1,5 dB`" in DOC_DE
    assert "Nur genau `0 dB` bedeutet Gleichheit" in DOC_DE
    assert "keine feste Reserve hinzugefügt" in DOC_DE
    assert "äußere halbe Intervall bildet den natürlichen Rand" in DOC_DE
    assert "nie enger als `-6 dB` bis `+6 dB`" in DOC_DE
    for obsolete_text in ("S-unit", "1S=6dB", "S-Stufe"):
        assert obsolete_text not in DOC_EN
        assert obsolete_text not in DOC_DE
        assert obsolete_text not in T["en"]["cbar_comp"]
        assert obsolete_text not in T["de"]["cbar_comp"]


def test_bilingual_manuals_define_saved_inspector_selection_contracts():
    """Saved result-view guidance must distinguish Performance singleton and Compare all."""
    assert "Compare and Performance selections are saved independently" in DOC_EN
    assert "Its setting is saved for Performance" in DOC_EN
    assert (
        "Performance saves zero or one exact `callsign + locator` identity"
        in DOC_EN
    )
    assert "restoration retains the first valid identity in stored order" in DOC_EN
    assert "never substitutes a different station" in DOC_EN
    assert "Compare selection remains independent and may contain one or more exact identities" in DOC_EN
    assert "Selecting every Compare station stores an all-stations intent" in DOC_EN
    assert "with a moving `Last X Hours` window" in DOC_EN

    assert "für Compare und Performance getrennt gespeichert" in DOC_DE
    assert "Die Einstellung wird für Performance gespeichert" in DOC_DE
    assert (
        "Performance speichert keine oder genau eine exakte Identität"
        in DOC_DE
    )
    assert "erste gültige Identität in gespeicherter Reihenfolge" in DOC_DE
    assert "ersetzt sie nie durch eine andere Station" in DOC_DE
    assert "Die Compare-Auswahl bleibt unabhängig und kann eine oder mehrere exakte Identitäten enthalten" in DOC_DE
    assert "Werden alle Compare-Stationen ausgewählt, speichert die Konfiguration diese Absicht" in DOC_DE
    assert "bei einem gleitenden Fenster `Letzte X Stunden`" in DOC_DE


def test_documentation_css_highlights_subsections_and_defined_terms(monkeypatch):
    """Share explicit defined-term emphasis without recoloring ordinary bold text."""
    rendered_styles = []
    monkeypatch.setattr(
        ui_css.st,
        "markdown",
        lambda body, **_kwargs: rendered_styles.append(body),
    )

    ui_css.apply_custom_css()

    assert len(rendered_styles) == 1
    stylesheet = rendered_styles[0]
    assert ".st-key-documentation_body .stMarkdown h4" in stylesheet
    assert ".st-key-documentation_body .stMarkdown h5" in stylesheet
    assert (
        ".st-key-documentation_body table.documentation-weighted-columns"
        in stylesheet
    )
    assert "table-layout: fixed !important" in stylesheet
    assert ".st-key-documentation_body .stMarkdown strong.defined-term" in stylesheet
    assert ".st-key-guided_input_flow .stMarkdown strong.defined-term" in stylesheet
    assert ".st-key-documentation_body a[id]:not(.header-anchor)" in stylesheet
    assert "scroll-margin-top: 5rem" in stylesheet
    assert "strong:first-child:not(.defined-term)" in stylesheet
    assert "color: #39ff14 !important" in stylesheet
    assert 'div[data-testid="stPopover"] button[kind="primary"]' in stylesheet


@pytest.mark.parametrize("documentation_text", (DOC_EN, DOC_DE), ids=("en", "de"))
def test_manual_internal_links_resolve_to_unique_anchors(documentation_text):
    """Every web/PDF internal link must target exactly one stable source anchor."""
    anchors = re.findall(r'<a id="([^"]+)"></a>', documentation_text)
    internal_links = re.findall(r'(?:href="|\]\()#([^"\)]+)', documentation_text)

    assert len(anchors) == len(set(anchors))
    assert set(internal_links) <= set(anchors)
    for chapter_one_anchor in (
        "sec-1",
        "sec-1-0",
        "sec-1-1",
        "sec-1-2",
        "sec-1-3",
        "sec-1-4",
    ):
        assert anchors.count(chapter_one_anchor) == 1


def test_localized_manuals_preserve_shared_lazy_loading_and_chapter_anchors():
    """Localized manuals must retain the same ordered runtime and chapter anchors."""
    english_anchors = re.findall(r'<a id="([^"]+)"></a>', DOC_EN)
    german_anchors = re.findall(r'<a id="([^"]+)"></a>', DOC_DE)

    assert german_anchors == english_anchors

    shared_runtime_anchors = {
        "sec-1",
        "sec-1-0",
        "sec-1-1",
        "sec-1-2",
        "sec-1-3",
        "sec-1-4",
        "documentation-toc",
        "sec-2",
        "sec-3",
        "sec-4",
        "sec-5",
        "sec-6",
        "sec-7",
        "sec-8",
        "sec-a",
        "sec-b",
        "sec-c",
        "sec-d",
        "sec-ref",
    }
    assert shared_runtime_anchors <= set(english_anchors)
    assert shared_runtime_anchors <= set(german_anchors)


@pytest.mark.parametrize(
    ("malformed_section_one", "expected_count"),
    [
        ("Section 1 without its final subsection marker", 0),
        (
            documentation.DOCUMENTATION_SECTION_ONE_TRIGGER_MARKER
            + documentation.DOCUMENTATION_SECTION_ONE_TRIGGER_MARKER,
            2,
        ),
    ],
)
def test_section_one_scroll_split_rejects_missing_or_duplicate_marker(
    malformed_section_one,
    expected_count,
):
    with pytest.raises(ValueError, match=rf"found {expected_count}"):
        documentation._split_section_one_at_scroll_boundary(
            malformed_section_one
        )


@pytest.mark.parametrize(
    ("malformed_documentation", "expected_message"),
    [
        (
            documentation.DOCUMENTATION_SECTION_TWO_MARKER,
            "table-of-contents marker.*found 0",
        ),
        (
            documentation.DOCUMENTATION_TOC_MARKER
            + documentation.DOCUMENTATION_TOC_MARKER
            + documentation.DOCUMENTATION_SECTION_TWO_MARKER,
            "table-of-contents marker.*found 2",
        ),
        (
            documentation.DOCUMENTATION_TOC_MARKER,
            "Section 2 marker.*found 0",
        ),
        (
            documentation.DOCUMENTATION_TOC_MARKER
            + documentation.DOCUMENTATION_SECTION_TWO_MARKER
            + documentation.DOCUMENTATION_SECTION_TWO_MARKER,
            "Section 2 marker.*found 2",
        ),
        (
            documentation.DOCUMENTATION_SECTION_TWO_MARKER
            + documentation.DOCUMENTATION_TOC_MARKER,
            "table of contents must precede the Section 2 marker",
        ),
    ],
    ids=(
        "missing-toc",
        "duplicate-toc",
        "missing-section-two",
        "duplicate-section-two",
        "reversed-order",
    ),
)
def test_manual_split_rejects_malformed_or_reversed_markers(
    malformed_documentation,
    expected_message,
):
    with pytest.raises(ValueError, match=expected_message):
        documentation._split_documentation_sections(malformed_documentation)


def test_initial_render_shows_only_section_one_and_prominent_load_fallback(
    monkeypatch,
):
    fake_st = _FakeStreamlit(session_state={"lang": "en"})
    labels, pdf_calls, scroll_trigger_calls = _render_with_fake_streamlit(
        monkeypatch,
        fake_st,
    )
    section_one, table_of_contents, remaining_sections = (
        documentation._split_documentation_sections(DOC_EN)
    )
    section_one_lead, section_one_completion = (
        documentation._split_section_one_at_scroll_boundary(section_one)
    )
    rendered_bodies = [body for body, _kwargs in fake_st.markdowns]

    assert fake_st.container_keys == [documentation.DOCUMENTATION_CONTAINER_KEY]
    assert section_one_lead in rendered_bodies
    assert section_one_completion in rendered_bodies
    assert section_one_lead + section_one_completion == section_one
    assert table_of_contents not in rendered_bodies
    assert remaining_sections not in rendered_bodies
    assert not any(labels["dev_credit"] in body for body in rendered_bodies)
    assert fake_st.buttons == [
        {
            "label": labels["btn_load_full_documentation"],
            "icon": ":material/menu_book:",
            "key": documentation.DOCUMENTATION_TOGGLE_KEY,
            "on_click": documentation._load_full_documentation,
            "width": "stretch",
        }
    ]
    assert len(scroll_trigger_calls) == 1
    _assert_documentation_trigger_call(
        scroll_trigger_calls[0],
        DOC_EN,
        is_auto_expand_enabled=True,
        is_documentation_expanded=False,
        allow_initial_hash_expansion=True,
    )
    assert pdf_calls == [(labels, "en", "logo", "v1")]


@pytest.mark.parametrize(
    "session_state",
    [
        {documentation.DOCUMENTATION_SCROLL_TRIGGER_CONSUMED_KEY: True},
        {"run_mode": "tx"},
        {"run_mode": "rx"},
    ],
    ids=("already-consumed", "tx-run-active", "rx-run-active"),
)
def test_navigation_controller_remains_mounted_when_scroll_trigger_is_suppressed(
    monkeypatch,
    session_state,
):
    fake_st = _FakeStreamlit(session_state=session_state)
    _labels_result, _pdf_calls, scroll_trigger_calls = _render_with_fake_streamlit(
        monkeypatch,
        fake_st,
    )

    assert len(scroll_trigger_calls) == 1
    _assert_documentation_trigger_call(
        scroll_trigger_calls[0],
        DOC_EN,
        is_auto_expand_enabled=False,
        is_documentation_expanded=False,
        allow_initial_hash_expansion=not session_state.get(
            documentation.DOCUMENTATION_SCROLL_TRIGGER_CONSUMED_KEY,
            False,
        ),
    )
    assert fake_st.buttons[0]["label"] == "Load full documentation"


def test_scroll_callback_expands_once_and_renders_toc_and_remainder(monkeypatch):
    fake_st = _FakeStreamlit(session_state={"lang": "en"})
    labels, _pdf_calls, scroll_trigger_calls = _render_with_fake_streamlit(
        monkeypatch,
        fake_st,
    )

    scroll_trigger_calls[0]["on_trigger"]()
    assert fake_st.session_state[documentation.DOCUMENTATION_EXPANDED_KEY] is True
    assert (
        fake_st.session_state[
            documentation.DOCUMENTATION_SCROLL_TRIGGER_CONSUMED_KEY
        ]
        is True
    )

    fake_st.markdowns.clear()
    fake_st.buttons.clear()
    scroll_trigger_calls.clear()
    documentation._render_documentation_section(labels, "en", "logo", "v1")
    section_one, table_of_contents, remaining_sections = (
        documentation._split_documentation_sections(DOC_EN)
    )
    section_one_lead, section_one_completion = (
        documentation._split_section_one_at_scroll_boundary(section_one)
    )
    rendered_bodies = [body for body, _kwargs in fake_st.markdowns]

    assert len(scroll_trigger_calls) == 1
    _assert_documentation_trigger_call(
        scroll_trigger_calls[0],
        DOC_EN,
        is_auto_expand_enabled=False,
        is_documentation_expanded=True,
        allow_initial_hash_expansion=False,
    )
    assert section_one_lead in rendered_bodies
    assert section_one_completion in rendered_bodies
    assert table_of_contents in rendered_bodies
    assert remaining_sections in rendered_bodies
    assert section_one + table_of_contents + remaining_sections == DOC_EN


def test_scroll_callback_does_not_expand_or_consume_while_run_is_active(
    monkeypatch,
):
    session_state = {"run_mode": "tx"}
    fake_st = _FakeStreamlit(session_state=session_state)
    monkeypatch.setattr(documentation, "st", fake_st)

    documentation._expand_documentation_from_scroll()

    assert fake_st.session_state == {"run_mode": "tx"}
    assert documentation.DOCUMENTATION_EXPANDED_KEY not in fake_st.session_state
    assert (
        documentation.DOCUMENTATION_SCROLL_TRIGGER_CONSUMED_KEY
        not in fake_st.session_state
    )


def test_explicit_anchor_navigation_expands_during_an_active_run(monkeypatch):
    """Treat a documentation-link click like the explicit load control."""
    fake_st = _FakeStreamlit(session_state={"run_mode": "tx"})
    monkeypatch.setattr(documentation, "st", fake_st)

    documentation._expand_documentation_from_navigation()

    assert fake_st.session_state[documentation.DOCUMENTATION_EXPANDED_KEY] is True
    assert (
        fake_st.session_state[
            documentation.DOCUMENTATION_SCROLL_TRIGGER_CONSUMED_KEY
        ]
        is True
    )


def test_expanded_render_restores_toc_exact_remainder_and_hide_control(monkeypatch):
    fake_st = _FakeStreamlit(
        session_state={
            "lang": "de",
            documentation.DOCUMENTATION_EXPANDED_KEY: True,
        }
    )
    labels, pdf_calls, scroll_trigger_calls = _render_with_fake_streamlit(
        monkeypatch,
        fake_st,
        lang="de",
    )
    section_one, table_of_contents, remaining_sections = (
        documentation._split_documentation_sections(DOC_DE)
    )
    section_one_lead, section_one_completion = (
        documentation._split_section_one_at_scroll_boundary(section_one)
    )
    rendered_bodies = [body for body, _kwargs in fake_st.markdowns]

    assert section_one_lead in rendered_bodies
    assert section_one_completion in rendered_bodies
    assert table_of_contents in rendered_bodies
    assert remaining_sections in rendered_bodies
    assert section_one + table_of_contents + remaining_sections == DOC_DE
    assert "(#sec-2)" in table_of_contents
    assert any(labels["dev_credit"] in body for body in rendered_bodies)
    assert fake_st.buttons[0]["label"] == labels["btn_hide_full_documentation"]
    assert fake_st.buttons[0]["icon"] == ":material/expand_less:"
    assert fake_st.buttons[0]["width"] == "stretch"
    assert len(scroll_trigger_calls) == 1
    _assert_documentation_trigger_call(
        scroll_trigger_calls[0],
        DOC_DE,
        is_auto_expand_enabled=False,
        is_documentation_expanded=True,
        allow_initial_hash_expansion=True,
    )
    assert pdf_calls == [(labels, "de", "logo", "v1")]


def test_manual_load_hide_and_reload_preserve_consumed_autoload(monkeypatch):
    fake_st = _FakeStreamlit(session_state={"lang": "en"})
    labels, _pdf_calls, scroll_trigger_calls = _render_with_fake_streamlit(
        monkeypatch,
        fake_st,
    )

    fake_st.buttons[0]["on_click"]()
    assert fake_st.session_state[documentation.DOCUMENTATION_EXPANDED_KEY] is True
    assert (
        fake_st.session_state[
            documentation.DOCUMENTATION_SCROLL_TRIGGER_CONSUMED_KEY
        ]
        is True
    )

    fake_st.markdowns.clear()
    fake_st.buttons.clear()
    scroll_trigger_calls.clear()
    documentation._render_documentation_section(labels, "en", "logo", "v1")
    assert fake_st.buttons[0]["label"] == labels["btn_hide_full_documentation"]
    assert fake_st.buttons[0]["on_click"] is documentation._hide_full_documentation
    assert len(scroll_trigger_calls) == 1
    _assert_documentation_trigger_call(
        scroll_trigger_calls[0],
        DOC_EN,
        is_auto_expand_enabled=False,
        is_documentation_expanded=True,
        allow_initial_hash_expansion=False,
    )

    fake_st.buttons[0]["on_click"]()
    assert fake_st.session_state[documentation.DOCUMENTATION_EXPANDED_KEY] is False
    assert (
        fake_st.session_state[
            documentation.DOCUMENTATION_SCROLL_TRIGGER_CONSUMED_KEY
        ]
        is True
    )

    fake_st.markdowns.clear()
    fake_st.buttons.clear()
    scroll_trigger_calls.clear()
    documentation._render_documentation_section(labels, "en", "logo", "v1")
    assert fake_st.buttons[0]["label"] == labels["btn_load_full_documentation"]
    assert fake_st.buttons[0]["on_click"] is documentation._load_full_documentation
    assert len(scroll_trigger_calls) == 1
    _assert_documentation_trigger_call(
        scroll_trigger_calls[0],
        DOC_EN,
        is_auto_expand_enabled=False,
        is_documentation_expanded=False,
        allow_initial_hash_expansion=False,
    )

    fake_st.buttons[0]["on_click"]()
    assert fake_st.session_state[documentation.DOCUMENTATION_EXPANDED_KEY] is True
    assert (
        fake_st.session_state[
            documentation.DOCUMENTATION_SCROLL_TRIGGER_CONSUMED_KEY
        ]
        is True
    )


def test_stale_load_callback_cannot_hide_scroll_expanded_documentation(monkeypatch):
    """A queued fallback click must remain an idempotent load action."""
    fake_st = _FakeStreamlit(session_state={"lang": "en"})
    _labels_result, _pdf_calls, scroll_trigger_calls = _render_with_fake_streamlit(
        monkeypatch,
        fake_st,
    )
    stale_load_callback = fake_st.buttons[0]["on_click"]

    scroll_trigger_calls[0]["on_trigger"]()
    stale_load_callback()

    assert fake_st.session_state[documentation.DOCUMENTATION_EXPANDED_KEY] is True
    assert (
        fake_st.session_state[
            documentation.DOCUMENTATION_SCROLL_TRIGGER_CONSUMED_KEY
        ]
        is True
    )


def test_documentation_fragment_has_no_sleep_or_parallel_execution():
    module_source = inspect.getsource(documentation)

    assert "time.sleep" not in module_source
    assert "DOCUMENTATION_INITIAL_LOAD_DELAY_SEC" not in module_source
    assert "_disable_unavailable_toc_links" not in module_source
    assert "@st.fragment" in module_source
    assert "@st.fragment(parallel=True)" not in module_source
