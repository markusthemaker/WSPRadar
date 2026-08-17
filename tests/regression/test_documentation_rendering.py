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
        "documentation_language": "en" if documentation_text is DOC_EN else "de",
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


def test_english_scientific_methods_use_streamlit_math_delimiters():
    """Keep Chapter 7 formulas parseable without changing their mathematics."""
    scientific_methods = DOC_EN.split('<a id="sec-7"></a>', 1)[1].split(
        '<a id="sec-8"></a>', 1
    )[0]

    assert r"\(" not in scientific_methods
    assert r"\)" not in scientific_methods
    assert (
        r"$$v_{T,i,b}=\frac{T_{i,b}}{N_{i,b}},\qquad "
        r"v_{J,i,b}=\frac{J_{i,b}}{N_{i,b}},\qquad "
        r"v_{R,i,b}=\frac{R_{i,b}}{N_{i,b}}$$"
        in scientific_methods
    )


def test_scientific_methods_keep_bilingual_section_and_formula_parity():
    """Keep Chapter 7 structure and mathematical contracts language-neutral."""
    english_methods = DOC_EN.split('<a id="sec-7"></a>', 1)[1].split(
        '<a id="sec-8"></a>', 1
    )[0]
    german_methods = DOC_DE.split('<a id="sec-7"></a>', 1)[1].split(
        '<a id="sec-8"></a>', 1
    )[0]

    english_anchors = re.findall(r'<a id="(sec-7(?:-[^"]+)?)"></a>', english_methods)
    german_anchors = re.findall(r'<a id="(sec-7(?:-[^"]+)?)"></a>', german_methods)
    english_formulas = re.findall(r"\$\$(.*?)\$\$", english_methods, flags=re.DOTALL)
    german_formulas = re.findall(r"\$\$(.*?)\$\$", german_methods, flags=re.DOTALL)
    english_formal = english_methods.split('<a id="sec-7-11"></a>', 1)[1]
    german_formal = german_methods.split('<a id="sec-7-11"></a>', 1)[1]
    english_outlier_formulas = re.findall(
        r"\$\$(.*?)\$\$", english_formal, flags=re.DOTALL
    )
    german_outlier_formulas = re.findall(
        r"\$\$(.*?)\$\$", german_formal, flags=re.DOTALL
    )

    assert english_anchors == german_anchors
    assert english_formulas == german_formulas
    assert len(english_formulas) == 29
    assert len(english_outlier_formulas) == 13
    assert english_outlier_formulas == german_outlier_formulas
    assert len(english_formulas) - len(english_outlier_formulas) == 16


def test_outlier_method_keeps_mnemonic_notation_inside_section_7_11():
    """Keep the approved symbols local to the formal detector method."""
    english_before, english_remainder = DOC_EN.split(
        '<a id="sec-7-11"></a>', 1
    )
    english_formal, english_after = english_remainder.split(
        '<a id="sec-8"></a>', 1
    )
    german_before, german_remainder = DOC_DE.split(
        '<a id="sec-7-11"></a>', 1
    )
    german_formal, german_after = german_remainder.split(
        '<a id="sec-8"></a>', 1
    )

    mnemonic_symbols = (
        r"\widetilde D_{i,k}",
        r"\mathcal{B}_{\mathrm{pre}}",
        r"B^P_{i,k}",
        r"r^P_{i,u}",
        r"\mathcal{V}",
        r"W_i^P",
        r"W_i^B",
        r"z_E",
        r"\operatorname{agree}(E)",
    )
    for symbol in mnemonic_symbols:
        assert symbol in english_formal
        assert symbol in german_formal
        assert symbol not in english_before + english_after
        assert symbol not in german_before + german_after

    for obsolete_symbol in (
        r"Q_{i,k}",
        r"\mathcal{Q}_{\mathrm{pre}}",
        r"\mathcal{U}",
        r"L=\min",
        r"W_i=\max",
    ):
        assert obsolete_symbol not in english_formal
        assert obsolete_symbol not in german_formal

    for formula_fragment in (
        r"B=\frac{B_{\mathrm{pre}}+B_{\mathrm{post}}}{2}",
        r"F=\min(1\ \mathrm{dB},D_{\min})",
        r"r^P_{i,u}=D_{i,u}-B^P_{i,k(u)}",
        r"W_i^B=\max(10,C_i)\ \mathrm{minutes}",
        r"z_E=0.6745\frac{m_E}{S_{\mathrm{robust}}}",
        r"\operatorname{agree}(E)\geq\frac{2}{3}",
    ):
        assert formula_fragment in english_formal
        assert formula_fragment in german_formal


def test_bilingual_preface_introduces_target_peer_and_decode_rate():
    """Keep the first-use operator vocabulary explicit in both languages."""
    english_preface = DOC_EN.split('<a id="sec-1-0"></a>', 1)[1].split(
        '<a id="sec-1-3"></a>', 1
    )[0]
    german_preface = DOC_DE.split('<a id="sec-1-0"></a>', 1)[1].split(
        '<a id="sec-1-3"></a>', 1
    )[0]

    assert "the station under test, normally your station" in english_preface
    assert '<strong class="defined-term">peer</strong>' in english_preface
    assert "percentage of independently confirmed opportunities" in english_preface
    assert "the Target decoded the peer in RX" in english_preface
    assert "the peer decoded the Target in TX" in english_preface

    assert "die zu untersuchende Station, normalerweise deine Station" in german_preface
    assert '<strong class="defined-term">Peer</strong>' in german_preface
    assert "Prozentsatz unabhängig bestätigter Gelegenheiten" in german_preface
    assert "Bei RX decodiert das Target den Peer" in german_preface
    assert "bei TX decodiert der Peer das Target" in german_preface


def test_bilingual_controls_keep_exact_run_labels_and_callsign_syntax():
    """Match the rendered Run actions and authoritative callsign validator."""
    for run_label in (
        T["en"]["btn_run_analysis_rx"],
        T["en"]["btn_run_analysis_tx"],
    ):
        assert f"`{run_label}`" in DOC_EN
    for run_label in (
        T["de"]["btn_run_analysis_rx"],
        T["de"]["btn_run_analysis_tx"],
    ):
        assert f"`{run_label}`" in DOC_DE

    assert "one optional terminal alphanumeric hyphen suffix" in DOC_EN
    assert "ein optionales abschließendes alphanumerisches Bindestrich-Suffix" in DOC_DE
    assert "**Start Date/Time (UTC)** and **End Date/Time (UTC)**" in DOC_EN
    assert "**Startdatum/-zeit (UTC)** und **Enddatum/-zeit (UTC)**" in DOC_DE


def test_bilingual_manuals_document_the_outlier_detector_contract():
    """Keep controls, paired units, gates, boundaries, and limits aligned."""
    english_controls = DOC_EN.split('<a id="sec-5-6"></a>', 1)[1].split(
        '<a id="sec-6"></a>', 1
    )[0]
    german_controls = DOC_DE.split('<a id="sec-5-6"></a>', 1)[1].split(
        '<a id="sec-6"></a>', 1
    )[0]
    english_outlier = DOC_EN.split('<a id="sec-outlier"></a>', 1)[1].split(
        '<a id="sec-3-9"></a>', 1
    )[0]
    german_outlier = DOC_DE.split('<a id="sec-outlier"></a>', 1)[1].split(
        '<a id="sec-3-9"></a>', 1
    )[0]
    english_formal = DOC_EN.split('<a id="sec-7-11"></a>', 1)[1].split(
        '<a id="sec-8"></a>', 1
    )[0]
    german_formal = DOC_DE.split('<a id="sec-7-11"></a>', 1)[1].split(
        '<a id="sec-8"></a>', 1
    )[0]

    control_keys = (
        "lbl_report_delta_snr_outlier_candidates",
        "lbl_delta_snr_outlier_minimum_departure_db",
        "lbl_delta_snr_outlier_minimum_robust_z",
        "lbl_delta_snr_outlier_maximum_baseline_difference_db",
    )
    for control_key in control_keys:
        assert f"`{T['en'][control_key]}`" in english_controls
        assert f"`{T['de'][control_key]}`" in german_controls
    for run_key in ("btn_run_analysis_rx", "btn_run_analysis_tx"):
        assert f"`{T['en'][run_key]}`" in english_controls
        assert f"`{T['de'][run_key]}`" in german_controls

    assert "| off |" in english_controls
    assert "| aus |" in german_controls
    assert "`6.0`; `0.1`–`100.0 dB` inclusive" in english_controls
    assert "`3.0`; `0.1`–`100.0` inclusive" in english_controls
    assert "`6.0`; einschließlich `0.1`–`100.0 dB`" in german_controls
    assert "`3.0`; einschließlich `0.1`–`100.0`" in german_controls
    assert "prioritizes large absolute movements" in english_controls
    assert "priorisiert große absolute Auslenkungen" in german_controls
    assert "does not automatically start an analysis" in english_controls
    assert "startet aber nicht automatisch eine Analyse" in german_controls
    assert "All three thresholds apply unchanged" in english_controls
    assert "Alle drei Schwellen gelten unverändert" in german_controls

    for section in (english_controls, english_outlier, english_formal):
        assert "Joint Spot" in section
        assert "complete Scheduled Pair" in section
    for section in (german_controls, german_outlier, german_formal):
        assert "Joint Spot" in section
        assert "vollständige" in section
        assert "Paar" in section
    assert "optional expert diagnostic tool" in english_outlier
    assert "not a routine step intended for every operator" in english_outlier
    assert "[Section 7.11](#sec-7-11)" in english_outlier
    assert "optionales Diagnosewerkzeug für erfahrene Anwender" in german_outlier
    assert "nicht für den routinemäßigen Einsatz" in german_outlier
    assert "[Abschnitt 7.11](#sec-7-11)" in german_outlier
    assert "cannot create, merge, split or remove an event" in english_outlier
    assert (
        "kann daher kein Ereignis erzeugen, zusammenführen, teilen oder entfernen"
        in german_outlier
    )
    assert "at least four populated cells" in english_formal
    assert "missing cells are never imputed" in english_formal
    assert "mindestens vier belegte Zellen" in german_formal
    assert "fehlende Zellen werden niemals ergänzt" in german_formal
    assert "trimmed to the first and last strong anchor" in english_formal
    assert "Units already grouped between them remain internal evidence" in english_formal
    assert "auf den ersten und letzten starken Anker gekürzt" in german_formal
    assert "dazwischen gruppierte Einheiten" in german_formal
    assert "does not calculate a p-value" in english_outlier
    assert "berechnet keinen p-Wert" in german_outlier
    assert "$$" not in english_outlier
    assert "$$" not in german_outlier
    assert "gyroelectric" not in DOC_EN.casefold()
    assert "gyroelectric" not in DOC_DE.casefold()
    assert "### 5. Troubleshooting and Data Quality" in DOC_EN
    assert "### 5. Fehlersuche und Datenqualität" in DOC_DE


def test_bilingual_methods_keep_the_approved_plain_language_explanations():
    """Protect the approved symbol, evidence-unit, and interpretation details."""
    assert "An indicator is `1` when its condition is met and `0` otherwise" in DOC_EN
    assert "Ein Indikator ist `1`, wenn seine Bedingung erfüllt ist, und sonst `0`" in DOC_DE
    assert "These units are constructed from reported spots; they are not additional radio measurements" in DOC_EN
    assert "Diese Einheiten werden aus gemeldeten Spots gebildet; sie sind keine zusätzlichen Funkmessungen" in DOC_DE
    assert "an SNR reported as `-15 dB` at `20 dBm` is normalized to `-5 dB` at `30 dBm`" in DOC_EN
    assert "Ein mit `-15 dB` gemeldetes SNR bei `20 dBm` wird beispielsweise auf `-5 dB` bei `30 dBm` normiert" in DOC_DE
    assert "The value $D_{i,c}$ is an observed paired difference for exactly one retained comparison unit" in DOC_EN
    assert "Der Wert $D_{i,c}$ ist eine beobachtete gepaarte Differenz für genau eine beibehaltene Vergleichseinheit" in DOC_DE
    assert "$c'$ indexes all successful observations for peer $i$" in DOC_EN
    assert "$c'$ durchläuft alle erfolgreichen Beobachtungen des Peers $i$" in DOC_DE
    assert "Here $n_{cell}$ is the evidence count in one density cell" in DOC_EN
    assert "Dabei ist $n_{cell}$ die Evidenzanzahl in einer Dichtezelle" in DOC_DE
    assert "1,000 spots are not the same as 1,000 unrelated experiments" in DOC_EN
    assert "1.000 Spots nicht dasselbe wie 1.000 voneinander unabhängige Experimente" in DOC_DE
    assert "The selected design therefore defines the analysis target" not in DOC_EN
    assert "formal statistical language, the estimand" not in DOC_EN
    assert "Das gewählte Design definiert damit das **Analyseziel**" not in DOC_DE
    assert "*Estimand*" not in DOC_DE
    assert "This chapter uses **summary** or **descriptive statistic**" in DOC_EN
    assert "Dieses Kapitel verwendet **Zusammenfassung** oder **deskriptive Kennzahl**" in DOC_DE


def test_bilingual_contract_summary_is_public_concise_and_non_exhaustive():
    """Keep Chapter 8 useful without presenting it as an exhaustive schema."""
    for manual in (DOC_EN, DOC_DE):
        assert "`config/wspradar-config.schema.json`" in manual
        assert "`results_view.performance`" in manual
        assert "`results_view.benchmark`" in manual
        assert "`benchmark_snr_correction_mode`" in manual
        assert "`benchmark_snr_correction_db`" in manual

    assert "not an exhaustive saved-configuration field, URL-parameter or export-metadata catalog" in DOC_EN
    assert "kein vollständiger Katalog der Felder gespeicherter Konfigurationen, URL-Parameter oder Exportmetadaten" in DOC_DE
    assert "as defined in [Section 4.4](#sec-5-4)" in DOC_EN
    assert "gemäß [Abschnitt 4.4](#sec-5-4)" in DOC_DE


@pytest.mark.parametrize("documentation_text", (DOC_EN, DOC_DE), ids=("en", "de"))
def test_simultaneous_benchmark_formulas_stay_nested_in_numbered_steps(
    documentation_text,
):
    """Align peer and segment estimators with their numbered instructions."""
    before_peer_formula, after_peer_formula = documentation_text.split(
        "$$m_i=\\operatorname{median}_{c}(D_{i,c})$$",
        1,
    )

    assert before_peer_formula.endswith("\n    ")
    assert (
        "\n    $$M_g=\\operatorname{median}_{i\\in I_g}(m_i)$$"
        in after_peer_formula
    )


@pytest.mark.parametrize("documentation_text", (DOC_EN, DOC_DE), ids=("en", "de"))
def test_manual_em_dashes_are_separated_from_surrounding_words(
    documentation_text,
):
    """Keep long-form em dashes legible in web and PDF typography."""
    assert re.search(r"(?<!\s)—|—(?!\s)", documentation_text) is None


@pytest.mark.parametrize("documentation_text", (DOC_EN, DOC_DE), ids=("en", "de"))
def test_documentation_anchor_extraction_is_ordered_and_complete(documentation_text):
    """Pass every explicit manual anchor to the browser navigation controller."""
    anchor_ids = documentation._documentation_anchor_ids(documentation_text)

    assert anchor_ids[0] == "sec-1"
    assert "documentation-toc" in anchor_ids
    assert "sec-2" in anchor_ids
    assert "ref-1" in anchor_ids
    assert len(anchor_ids) == len(set(anchor_ids))


def test_bilingual_manuals_define_one_selected_archive_per_completed_run():
    """Describe source provenance without freezing provider failover narration."""
    english_data_source = DOC_EN.split('<a id="sec-7-1"></a>', 1)[1].split(
        '<a id="sec-7-2"></a>', 1
    )[0]
    german_data_source = DOC_DE.split('<a id="sec-7-1"></a>', 1)[1].split(
        '<a id="sec-7-2"></a>', 1
    )[0]

    assert "one selected read-only archive for each completed run" in english_data_source
    assert "does not combine data sources" in english_data_source
    assert "einem ausgewählten, schreibgeschützten Archiv" in german_data_source
    assert "mischt keine Datenquellen" in german_data_source
    for manual in (DOC_EN, DOC_DE):
        assert "wspr.live" in manual
        assert "WSPRDaemon" in manual
        assert '<a href="#ref-10">[Ref-10]</a>' in manual
        assert '<a href="#ref-11">[Ref-11]</a>' in manual


def test_bilingual_introductions_highlight_archives_and_explain_data_source_routing():
    """Introduce upstream stewardship, priority, and whole-run routing early."""
    english_intro = DOC_EN.split('<a id="sec-1-1"></a>', 1)[1].split(
        '<a id="sec-1-0"></a>', 1
    )[0]
    german_intro = DOC_DE.split('<a id="sec-1-1"></a>', 1)[1].split(
        '<a id="sec-1-0"></a>', 1
    )[0]

    english_archive_term = '<strong class="defined-term">archives</strong>'
    german_archive_term = '<strong class="defined-term">Archive</strong>'
    assert english_archive_term in english_intro
    assert german_archive_term in german_intro
    assert "archive" not in DOC_EN.split(english_archive_term, 1)[0].lower()
    assert "archiv" not in DOC_DE.split(german_archive_term, 1)[0].lower()

    for required_text in (
        "**Data sources.** WSPRadar uses **wspr.live** as its primary data source",
        "is grateful to the people behind wspr.live and WSPRDaemon",
        "route a complete new run to **WSPRDaemon WD2** and then **WD1**",
        "ordered capacity spillover is distinct from provider failover",
        "Every completed run remains pinned to one archive",
        "records from different sources are never combined",
    ):
        assert required_text in english_intro

    for required_text in (
        "**Datenquellen.** WSPRadar verwendet **wspr.live** als primäre Datenquelle",
        "dankt den Menschen hinter wspr.live und WSPRDaemon",
        "an **WSPRDaemon WD2** und danach **WD1** weiterleiten",
        "geordnete Kapazitätsausgleich unterscheidet sich von einem Quellenwechsel nach einem Ausfall",
        "Jeder abgeschlossene Lauf bleibt an genau ein Archiv gebunden",
        "Datensätze aus verschiedenen Quellen werden niemals zusammengeführt",
    ):
        assert required_text in german_intro


def test_bilingual_reference_entries_use_current_project_landing_pages():
    """Keep the two early archive references on their approved public pages."""
    for manual in (DOC_EN, DOC_DE):
        assert (
            '<a id="ref-10"></a><a href="https://wspr.live/">[Ref-10]</a>'
            in manual
        )
        assert (
            '<a id="ref-11"></a><a href="https://www.wsprdaemon.org/">'
            "[Ref-11]</a>"
            in manual
        )
        assert "wspr.live/wspr_downloader.php" not in manual
        assert "wsprdaemon.readthedocs.io" not in manual


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
    for heading in (
        "#### 0.0 WSPR in 2 Minutes",
        "#### 0.1 What WSPRadar can show",
        "#### 0.2 What one run produces",
        "#### 0.3 Your first useful run",
    ):
        assert heading in DOC_EN
    for toc_entry in (
        "* [0.0 WSPR in 2 Minutes](#sec-1-1)",
        "* [0.1 What WSPRadar can show](#sec-1-0)",
        "* [0.2 What one run produces](#sec-1-3)",
        "* [0.3 Your first useful run](#sec-1-4)",
    ):
        assert toc_entry in DOC_EN
    assert "| Analysis | Question | Practical examples |" in DOC_EN
    assert "| What you want to learn | WSPRadar approach |" not in DOC_EN
    for operating_question in (
        "How broadly and consistently does my receiver decode signals that were independently confirmed elsewhere?",
        "Where, when and how consistently is my transmitter decoded by receivers independently shown to be active?",
        "Did two local receive paths differ while observing the same remote transmissions?",
        "Did two local transmit paths differ under simultaneous or tightly scheduled operation?",
        "How does my complete station compare with one known station?",
        "How does my station compare with the typical active WSPR group nearby?",
        "How does my station compare with the strongest active nearby peer available on each path and cycle?",
    ):
        assert operating_question in DOC_EN
    for benchmark_family, benchmark_variant in (
        ("RX Benchmark", "Hardware A/B"),
        ("TX Benchmark", "Hardware A/B"),
        ("RX/TX Benchmark", "Reference Station / Buddy Test"),
        ("RX/TX Benchmark", "Local Median Neighborhood"),
        ("RX/TX Benchmark", "Local Best Station"),
    ):
        assert (
            f'<span class="analysis-family">{benchmark_family}</span><br>'
            f'<strong class="analysis-variant">{benchmark_variant}</strong>'
            in DOC_EN
        )
    assert DOC_EN.count('class="analysis-choice"') == 5
    assert DOC_EN.count('class="analysis-choice-single"') == 2
    for scientific_safeguard in (
        "as complete receive paths",
        "matched, characterized or confirmed by crossover",
        "synchronized cycles, distinguishable signals and adequate isolation",
        "without treating the Buddy as an absolute calibrated standard",
        "cycle- and path-specific median",
        "checking neighborhood membership and radius sensitivity",
        "in comparable repeat runs",
        "without treating the result as a ranking against one permanent competitor or a stable calibrated baseline",
    ):
        assert scientific_safeguard in DOC_EN
    assert "Benchmark —" not in DOC_EN[: DOC_EN.index('<a id="sec-1-3"></a>')]
    assert "Choose the question you want to answer" not in DOC_EN
    assert "A demo is a worked example of WSPRadar's method" in DOC_EN
    assert "### 1. Choose and Prepare the Analysis" in DOC_EN
    assert '<strong class="defined-term">Target</strong>' in DOC_EN
    assert '<strong class="defined-term">Reference</strong>' in DOC_EN
    assert '<strong class="defined-term">Performance</strong>' in DOC_EN


def test_english_evidence_path_is_a_defined_term_in_both_guide_locations():
    """Keep the complete operator path emphasized without fragmenting its meaning."""
    defined_evidence_path = (
        '<strong class="defined-term">Map → Segment Inspector → '
        'Performance/Benchmark Evidence → Temporal Evidence → Station Insights '
        '→ Selected Station Evidence → Drill-Down</strong>'
    )

    assert DOC_EN.count(defined_evidence_path) == 2


def test_english_section_two_conclusions_use_scoped_callout_markup():
    """Style every Chapter 2 conclusion without affecting other blockquotes."""
    before_section_two, section_two_and_later = DOC_EN.split(
        "### 2. Run and Interpret Your Analysis",
        1,
    )
    section_two, section_three_and_later = section_two_and_later.split(
        "### 3. Strengthen and Communicate Your Result",
        1,
    )
    conclusion_opening = '<blockquote class="evidence-conclusion">'

    assert section_two.count(conclusion_opening) == 11
    assert conclusion_opening not in before_section_two
    assert conclusion_opening not in section_three_and_later


def test_english_playbooks_define_performance_opportunities_and_tx_ab_timing():
    """Retain operator-facing eligibility and scheduled-pair safeguards."""
    rx_performance = DOC_EN.split('<a id="sec-3-rx-performance"></a>', 1)[1].split(
        '<a id="sec-3-tx-performance"></a>', 1
    )[0]
    tx_performance = DOC_EN.split('<a id="sec-3-tx-performance"></a>', 1)[1].split(
        '<a id="sec-3-rx-benchmark"></a>', 1
    )[0]
    sequential_tx = DOC_EN.split(
        '<a id="sec-3-tx-benchmark-sequential"></a>', 1
    )[1].split('<a id="sec-3-tx-benchmark-buddy"></a>', 1)[0]

    assert "confirmed RX opportunity" in rx_performance
    assert "independent confirmation" in rx_performance
    assert "confirmed TX opportunity" in tx_performance
    assert "independent receiver-activity confirmation" in tx_performance
    assert "deterministic schedule" in sequential_tx
    assert "one-to-one Scheduled A/B Pairs automatically" in sequential_tx
    assert "actual recurrence" in DOC_EN
    assert "UTC phase" in DOC_EN
    assert "[Sections 7.1](#sec-7-1) and [7.7](#sec-7-7)" in DOC_EN
    assert "#### B.3 Ultimate3S schedule example" in DOC_EN
    assert "`Repeat Interval = 20`, `Target Start = 00`, `Reference Start = 10`" in DOC_EN
    assert "do not encode path identity through false dBm values" in DOC_EN
    assert '<a id="sec-b-5"></a>' in DOC_EN


def test_bilingual_tx_hardware_playbooks_cover_both_methods_and_fixed_identity():
    """Keep simultaneous/sequential designs and exact identity safeguards aligned."""
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

    assert "##### 2.4.1 Hardware A/B: simultaneous transmit paths" in DOC_EN
    assert "##### 2.4.2 Hardware A/B: sequential transmit paths" in DOC_EN
    assert "##### 2.4.1 Hardware A/B: simultane Sendepfade" in DOC_DE
    assert "##### 2.4.2 Hardware A/B: sequenzielle Sendepfade" in DOC_DE
    assert "distinct exact reporting callsigns" in DOC_EN
    assert "same Target grid-4" in DOC_EN
    assert "unterschiedliche exakte Melderufzeichen" in DOC_DE
    assert "dasselbe Target-Grid-4" in DOC_DE
    assert "deterministic scheduled eligibility" in DOC_EN
    assert "deterministische Zeitplanzulässigkeit" in DOC_DE


def test_bilingual_manuals_define_supported_exact_archive_identities():
    """Document letter-only and suffix forms as distinct exact archive tokens."""
    exact_identity_examples = (
        "`KFS`",
        "`KFS/SE`",
        "`DL1MKS`",
        "`DL1MKS/P`",
        "`DL1MKS/1`",
        "`DL1MKS/QRP`",
        "`DL1MKS-1`",
    )
    for manual in (DOC_EN, DOC_DE):
        for identity in exact_identity_examples:
            assert identity in manual

    assert "distinct identities" in DOC_EN
    assert "does not apply hidden prefix or suffix matching" in DOC_EN
    assert "eigenständige Identitäten" in DOC_DE
    assert "keine verdeckte Präfix- oder Suffixzuordnung" in DOC_DE


def test_bilingual_manuals_document_explicit_snr_correction_modes():
    """Keep the durable correction meaning distinct from its numeric dB value."""
    for required_text in (
        "No established offset",
        "Use an established correction",
        "Set up an offset-establishment run",
    ):
        assert required_text in DOC_EN
    for required_text in (
        "Kein ermittelter Offset",
        "Ermittelte Korrektur verwenden",
        "Offset-Ermittlungslauf einrichten",
    ):
        assert required_text in DOC_DE
    assert "A positive correction increases corrected Reference SNR" in DOC_EN
    assert "Eine positive Korrektur erhöht das korrigierte Referenz-SNR" in DOC_DE
    for manual in (DOC_EN, DOC_DE):
        assert "`benchmark_snr_correction_mode`" in manual
        assert "`benchmark_snr_correction_db`" in manual


def test_results_chapter_is_question_led_and_uses_the_shared_evidence_path():
    """Check durable operator flow without pinning panels, axes, or layout."""
    english_headings = (
        "#### 2.1 RX Performance",
        "#### 2.2 TX Performance",
        "#### 2.3 RX Benchmark",
        "#### 2.4 TX Benchmark",
    )
    german_headings = (
        "#### 2.1 RX Performance",
        "#### 2.2 TX Performance",
        "#### 2.3 RX Benchmark",
        "#### 2.4 TX Benchmark",
    )
    assert [DOC_EN.index(heading) for heading in english_headings] == sorted(
        DOC_EN.index(heading) for heading in english_headings
    )
    assert [DOC_DE.index(heading) for heading in german_headings] == sorted(
        DOC_DE.index(heading) for heading in german_headings
    )

    for manual, evidence_stages in (
        (
            DOC_EN,
            (
                "Map",
                "Segment Inspector",
                "Temporal Evidence",
                "Station Insights",
                "Selected Station Evidence",
                "Drill-Down",
            ),
        ),
        (
            DOC_DE,
            (
                "Karte",
                "Segment-Inspektor",
                "Zeitliche Evidenz",
                "Station Insights",
                "Evidenz der ausgewählten Station",
                "Drill-Down",
            ),
        ),
    ):
        for evidence_stage in evidence_stages:
            assert evidence_stage in manual


def test_bilingual_manuals_define_performance_opportunities_and_weighting():
    """Keep Performance denominators and complementary weighting auditable."""
    english_contract = (
        r"$$n_i=\sum_c O_{i,c},\qquad h_i=\sum_c S_{i,c}$$",
        r"$$r_i=100\%\times\frac{h_i}{n_i}$$",
        r"$$R_{station}(g)=\frac{1}{|I_g|}\sum_{i\in I_g} r_i$$",
        r"$$R_{opportunity}(g)=100\%\times\frac{\sum_{i\in I_g}h_i}{\sum_{i\in I_g}n_i}$$",
        r"$$Reach(g)=100\%\times\frac{|\{i\in I_g:h_i\ge1\}|}{|I_g|}$$",
        "Station-balanced Decode Rate",
        "Opportunity-level Decode Rate",
        "every peer one equal vote",
        "pools all qualifying opportunities",
        "at least one Target success",
        "success-conditioned distribution",
        "Missed opportunities have no Target SNR and no synthetic value",
    )
    german_contract = (
        r"$$n_i=\sum_c O_{i,c},\qquad h_i=\sum_c S_{i,c}$$",
        r"$$r_i=100\%\times\frac{h_i}{n_i}$$",
        r"$$R_{station}(g)=\frac{1}{|I_g|}\sum_{i\in I_g} r_i$$",
        r"$$R_{opportunity}(g)=100\%\times\frac{\sum_{i\in I_g}h_i}{\sum_{i\in I_g}n_i}$$",
        r"$$Reach(g)=100\%\times\frac{|\{i\in I_g:h_i\ge1\}|}{|I_g|}$$",
        "stationsgleichgewichtete Dekodierrate",
        "Dekodierrate auf Gelegenheitsebene",
        "eine gleich große Stimme",
        "Jede Gelegenheit erhält eine gleich große Stimme",
        "in mindestens einer qualifizierenden Gelegenheit erfolgreich war",
        "auf erfolgreiche Decodes bedingte Verteilung",
        "Verpasste Gelegenheiten besitzen kein Target-SNR",
    )

    for required_text in english_contract:
        assert required_text in DOC_EN
    for required_text in german_contract:
        assert required_text in DOC_DE


def test_bilingual_manuals_define_performance_selected_singleton_and_exports():
    """Keep one selected peer and its public export artifacts explicit."""
    english_contract = (
        "One exact `callsign + locator` per result type",
        "filters the active retained scope to one exact peer identity",
        "without changing the upstream analysis population",
        "actual normalized successful Target SNR",
        "With one peer",
        "numerically identical",
        "distinguish path presence from evidence volume",
        "Only Target, Joint and Only Reference",
        "changes only the retained-evidence view",
    )
    german_contract = (
        "genau ein `Rufzeichen + Locator` je Ergebnistyp",
        "genau eine Peer-Identität",
        "ohne die vorgelagerte Analysepopulation zu verändern",
        "das tatsächliche normierte erfolgreiche Target-SNR",
        "Bei genau einem Peer",
        "stationsgleichgewichtete Dekodierrate und die Dekodierrate auf Gelegenheitsebene",
        "numerisch identisch",
        "Funkwegpräsenz von Evidenzvolumen",
        "Only Target, Joint und Only Reference",
        "verändert nur die Ansicht der beibehaltenen Evidenz",
    )

    for required_text in english_contract:
        assert required_text in DOC_EN
    for required_text in german_contract:
        assert required_text in DOC_DE

    selected_performance_filenames = (
        "figure_selected_station_snr_evidence.png",
        "figure_selected_station_temporal_evidence.png",
    )
    benchmark_evidence_filenames = (
        "figure_segment_temporal_evidence.png",
        "figure_segment_temporal_coverage.png",
        "figure_selected_station_evidence.png",
        "figure_selected_station_coverage.png",
    )
    retired_benchmark_evidence_filenames = (
        "figure_segment_temporal_delta_change.png",
        "figure_path_agreement_consistency.png",
    )
    obsolete_performance_filenames = (
        "figure_selected_station_chronological.png",
        "figure_selected_station_utc_hour_profile.png",
        "figure_selected_station_snr_distribution.png",
        "figure_selected_station_similar_stations.png",
    )
    metadata_fields = (
        "`selected_evidence_figures`",
        "`benchmark_evidence_figures`",
        "`benchmark_evidence_recipes`",
    )
    for manual in (DOC_EN, DOC_DE):
        export_listing = manual.split(
            "  run_metadata.json\nbenchmark/",
            1,
        )[1].split("```", 1)[0]
        benchmark_export_listing = export_listing.split(
            "performance/",
            1,
        )[0]
        performance_export_listing = export_listing.split(
            "performance/",
            1,
        )[1]
        for filename in selected_performance_filenames:
            assert filename in performance_export_listing
            assert filename in manual
        for filename in obsolete_performance_filenames:
            assert filename not in performance_export_listing
            assert filename not in manual
        for filename in benchmark_evidence_filenames:
            assert filename in benchmark_export_listing
            assert filename in manual
        for filename in retired_benchmark_evidence_filenames:
            assert filename not in benchmark_export_listing
            assert filename not in manual
        assert "figure_selected_station_evidence.png" in benchmark_export_listing
        assert (
            "figure_selected_station_evidence.png"
            not in performance_export_listing
        )
        for metadata_field in metadata_fields:
            assert metadata_field in manual


def test_bilingual_manuals_define_benchmark_evidence_science_and_limits():
    """Keep Benchmark pairability, weighting, and one-sided limits explicit."""
    english_contract = (
        r"$$N_{i,b}=T_{i,b}+J_{i,b}+R_{i,b}$$",
        r"$$JES_{station}(b)=100\%\times\operatorname{mean}_{i}\left(\frac{J_{i,b}}{N_{i,b}}\right)$$",
        r"$$JES_{outcome}(b)=100\%\times\frac{\sum_iJ_{i,b}}{\sum_iN_{i,b}}$$",
        "Only Target, Joint and Only Reference",
        "equal peer weight versus equal evidence-unit weight",
        "Joint Evidence Share measures pairability",
        "It is not a Target win rate",
        "directional and asymmetric",
        "a one-sided pair still has no Pair Delta",
    )
    german_contract = (
        r"$$N_{i,b}=T_{i,b}+J_{i,b}+R_{i,b}$$",
        r"$$JES_{station}(b)=100\%\times\operatorname{mean}_{i}\left(\frac{J_{i,b}}{N_{i,b}}\right)$$",
        r"$$JES_{outcome}(b)=100\%\times\frac{\sum_iJ_{i,b}}{\sum_iN_{i,b}}$$",
        "Only Target, Joint und Only Reference",
        "jedem beitragenden Peer dasselbe Gewicht",
        "Joint-Evidenzanteil misst die Paarbarkeit",
        "keine Gewinnquote des Targets",
        "gerichtet und asymmetrisch",
        "einseitiges Paar besitzt jedoch kein Paar-Delta",
    )

    for required_text in english_contract:
        assert required_text in DOC_EN
    for required_text in german_contract:
        assert required_text in DOC_DE


def test_bilingual_manuals_require_map_values_to_be_read_with_support():
    """Retain map interpretation while allowing presentation details to evolve."""
    assert "Read sector color together with the station and opportunity, spot or pair support" in DOC_EN
    assert "A colored sector is a prompt to inspect, not the conclusion" in DOC_EN
    assert "sector color shows the Station-balanced Decode Rate" in DOC_EN

    assert "Lies die Sektorfarbe stets zusammen mit der Unterstützung" in DOC_DE
    assert "noch keine Schlussfolgerung" in DOC_DE
    assert "Sektorfarbe die stationsgleichgewichtete Dekodierrate" in DOC_DE


def test_bilingual_manuals_explain_station_and_observation_benchmark_weighting():
    """Keep complementary Benchmark weighting without pinning bar styling."""
    assert "two complementary compositions: station breadth and observation volume" in DOC_EN
    assert "Station Medians give each remote transmitter one Delta-SNR value" in DOC_EN
    assert "Joint-Spot distribution shows every paired observation" in DOC_EN
    assert "station-level Decode Outcomes with the observation- or pair-level composition" in DOC_EN

    assert "zwei ergänzende Zusammensetzungen: die Breite über Stationen und das Beobachtungsvolumen" in DOC_DE
    assert "Stationsmediane geben jedem entfernten Sender genau einen Delta-SNR-Wert" in DOC_DE
    assert "Verteilung der Joint Spots zeigt jede gepaarte Beobachtung" in DOC_DE
    assert "stationsbezogenen Decode Outcomes mit der Zusammensetzung auf Beobachtungs- beziehungsweise Paarebene" in DOC_DE


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

    assert "`Include Unpaired Evidence`" in DOC_EN
    assert "`Ungepaarte Evidenz einbeziehen`" in DOC_DE
    assert "**Only Target**, **Joint**, **Only Reference** and, at identity level, **Both (Async)**" in DOC_EN
    assert "**Only Target**, **Joint**, **Only Reference** sowie auf Identitätsebene **Both (Async)**" in DOC_DE


def test_end_user_manuals_omit_internal_interval_boundary_convention():
    """Keep deterministic interval-boundary mechanics out of operator guidance."""
    assert "half-open" not in DOC_EN
    assert "start <= time < end" not in DOC_EN
    assert "halboffen" not in DOC_DE
    assert "start <= geplanter Start < end" not in DOC_DE


def test_bilingual_manuals_define_segment_temporal_density_and_scope():
    """Keep temporal populations and density normalization explicit."""
    assert "Chronological views preserve the actual sequence of the run" in DOC_EN
    assert "across the full selected UTC window" in DOC_EN
    assert "Bins begin at the selected start; the final interval may be shorter" in DOC_EN
    assert "intervals without evidence remain blank rather than becoming 0 dB" in DOC_EN
    assert "does not by itself mean that the data source returned no observations" in DOC_EN
    assert "fold evidence from represented dates onto fixed one-hour slots" in DOC_EN
    assert "Benchmark temporal coverage uses all retained Only Target, Joint and Only Reference units" in DOC_EN
    assert "requires at least two represented evidence dates" in DOC_EN
    assert r"$$D_{relative}=100\times\frac{n_{cell}}{\max(n_{cell,panel})}$$" in DOC_EN
    assert "not 100% of all evidence" in DOC_EN

    assert "Chronologische Ansichten bewahren die tatsächliche Reihenfolge des Laufs" in DOC_DE
    assert "über das vollständige ausgewählte UTC-Zeitfenster" in DOC_DE
    assert "Die Bins beginnen am ausgewählten Startzeitpunkt" in DOC_DE
    assert "Zeitabschnitte ohne Evidenz bleiben leer, statt zu 0 dB zu werden" in DOC_DE
    assert "daraus folgt nicht, dass die Datenquelle keine Beobachtungen lieferte" in DOC_DE
    assert "Beobachtungen verschiedener Tage auf dieselbe 24-Stunden-UTC-Uhr" in DOC_DE
    assert "zeitliche Benchmark-Abdeckung verwendet alle beibehaltenen Einheiten Only Target, Joint und Only Reference" in DOC_DE
    assert "mindestens zwei Tage mit Evidenz" in DOC_DE
    assert r"$$D_{relative}=100\times\frac{n_{cell}}{\max(n_{cell,panel})}$$" in DOC_DE
    assert "nicht 100 % der gesamten Evidenz" in DOC_DE


def test_bilingual_manuals_define_temporal_iqr_science_and_axis_contract():
    """Keep descriptive spread distinct from uncertainty and transforms."""
    assert "IQR and min–max displays are descriptive spread summaries, not confidence intervals" in DOC_EN
    assert "only where at least five values contribute" in DOC_EN
    assert "Empty bins remain missing rather than becoming synthetic zero observations" in DOC_EN
    assert "raw Delta SNR values, bin membership, counts, medians and quartiles remain unchanged" in DOC_EN
    assert "Performance successful-SNR views remain on a linear dB axis" in DOC_EN

    assert "IQR- und Min-Max-Darstellungen sind deskriptive Streuungsmaße und keine Konfidenzintervalle" in DOC_DE
    assert "nur gezeichnet, wenn mindestens fünf Werte" in DOC_DE
    assert "Leere Bins bleiben fehlend" in DOC_DE
    assert "Rohe Delta-SNR-Werte, Bin-Zuordnung, Anzahlen, Mediane und Quartile bleiben unverändert" in DOC_DE
    assert "Performance-Ansichten des erfolgreichen SNR bleiben auf einer linearen dB-Achse" in DOC_DE


def test_bilingual_manuals_define_centered_native_drilldown_focus():
    """Document focused native evidence without redefining segment summaries."""
    for phrase in (
        "`Center date (UTC)`",
        "`Center time (UTC)`",
        "`← Earlier`",
        "`Later →`",
        "`Outlier Focus`",
        "`Filter table`",
        "select the center of that interval",
        "`Selected window: {start} to {end} UTC`",
        "changes only the displayed table and never the focused plots or completed analysis",
        "one actual Delta SNR dot per retained Joint Spot",
        "one actual Pair Delta SNR dot per retained complete Scheduled Pair",
        "actual normalized Target SNR of each successful confirmed opportunity",
        "not untouched provider rows",
        "No bin median, IQR, density background, colorbar, full-run median",
        "Segment and full-window Selected Station Evidence remain density-based aggregated views",
        "DG2CAD (JN47mv) - Time Window: {start} to {end} UTC",
        "robust-z guides at 1, 2 and 3 plus the configured qualifying threshold",
        "detector guides, not confidence intervals",
        "crossing any one guide cannot qualify a candidate by itself",
        "Identical `*` markers identify every native unit in the current window that individually meets both configured departure and robust-z gates as part of a reported candidate",
        "A muted **Focused episode** band identifies the selected reported episode",
        "padded by half one native evidence-unit width at each end",
        "neither a confidence interval nor a measurement of physical-event duration",
        "Other starred candidate units may have been evaluated against different local baselines and robust spreads",
        "weaker grouped units retained between strong anchors remain ordinary dots",
        "Drill-Down focus figures",
    ):
        assert phrase in DOC_EN

    for phrase in (
        "`Datum der Fenstermitte (UTC)`",
        "`Uhrzeit der Fenstermitte (UTC)`",
        "`← Früher`",
        "`Später →`",
        "`Ausreißerfokus`",
        "`Tabelle filtern`",
        "wählen die Mitte dieses Intervalls",
        "`Ausgewähltes Zeitfenster: {start} bis {end} UTC`",
        "verändert anschließend nur die angezeigte Tabelle und niemals die fokussierten Abbildungen oder die abgeschlossene Analyse",
        "einen tatsächlichen Delta-SNR-Punkt je beibehaltenem Joint Spot",
        "einen tatsächlichen Paar-Delta-SNR-Punkt je beibehaltenem vollständigem geplanten Paar",
        "tatsächliche normierte Target-SNR jeder erfolgreichen bestätigten Gelegenheit",
        "keine unveränderten Provider-Zeilen",
        "Binmedian, IQR, Dichtehintergrund, Farbskala, Median des vollständigen Laufs",
        "Segmentansicht und Evidenz der ausgewählten Station über das vollständige Fenster bleiben dichtebasierte aggregierte Ansichten",
        "DG2CAD (JN47mv) - Zeitfenster: {start} bis {end} UTC",
        "robuste-z-Hilfslinien bei 1, 2 und 3 sowie an der konfigurierten Qualifikationsschwelle",
        "Detektorhilfen und keine Konfidenzintervalle",
        "Überschreiten einer einzelnen Linie kann keinen Kandidaten allein qualifizieren",
        "Identische `*`-Marker kennzeichnen jede native Einheit im aktuellen Fenster, die innerhalb eines gemeldeten Kandidaten einzeln sowohl das konfigurierte Abweichungs- als auch das robuste-z-Kriterium erfüllt",
        "Ein dezentes Band **Fokussierte Episode** kennzeichnet die ausgewählte berichtete Episode",
        "an beiden Enden um eine halbe Breite der nativen Evidenzeinheit erweitert",
        "weder ein Konfidenzintervall noch eine Messung der Dauer eines physischen Ereignisses",
        "Andere mit Stern markierte Kandidateneinheiten können gegen andere lokale Baselines und robuste Streuungen bewertet worden sein",
        "schwächere gruppierte Einheiten, die zwischen starken Ankern beibehalten werden, bleiben normale Punkte",
        "Drill-Down-Fokusabbildungen",
    ):
        assert phrase in DOC_DE

    assert "`Zoom start (UTC)`" not in DOC_EN
    assert "`Zoom-Start (UTC)`" not in DOC_DE
    for superseded_phrase in (
        "`Focus date (UTC)`",
        "`Focus time (UTC)`",
        "`12h Event focus`",
        "`Fit detector context`",
    ):
        assert superseded_phrase not in DOC_EN
    for superseded_phrase in (
        "`Fokusdatum (UTC)`",
        "`Fokuszeit (UTC)`",
        "`12h-Ereignisfokus`",
        "`Detektorkontext einpassen`",
    ):
        assert superseded_phrase not in DOC_DE
    assert "two-minute chronological bins" not in DOC_EN
    assert "chronologische Zwei-Minuten-Bins" not in DOC_DE


def test_bilingual_manuals_separate_qualifying_plot_marker_from_true_peak():
    """Keep marker eligibility distinct from the report/export peak metric."""
    for phrase in (
        "**Largest single-cycle departure** is the most extreme retained residual",
        "That report/export metric is independent of the all-path temporal `*`",
        "only among individually qualifying native units in each review event",
        "never uses an unsupported or nonqualifying episode peak",
        "The all-path temporal marker is selected only from these strong anchors",
        "the individually qualifying native unit with the greatest absolute residual supplies the `*`",
        "Marker selection is separate from **Largest single-cycle departure**",
        "remains the true greatest-absolute retained residual in each path event for the report and export",
    ):
        assert phrase in DOC_EN

    for phrase in (
        "**Größte Einzelzyklusabweichung** ist das extremste beibehaltene Residuum",
        "Diese Berichts-/Exportgröße ist unabhängig vom `*` im Zeitplot aller Funkwege",
        "ausschließlich unter den einzeln qualifizierenden nativen Einheiten",
        "nie eine ungestützte oder nicht qualifizierende Episodenspitze",
        "Der Marker im Zeitplot aller Funkwege wird nur aus diesen starken Ankern ausgewählt",
        "die einzeln qualifizierende native Einheit mit dem betragsmäßig größten Residuum das `*`",
        "Die Markerauswahl ist von der Berichtsgröße **Größte Einzelzyklusabweichung** getrennt",
        "das tatsächliche betragsmäßig größte beibehaltene Residuum jedes Funkwegereignisses",
    ):
        assert phrase in DOC_DE


def test_benchmark_map_label_matches_station_balanced_delta_contract():
    """Keep the rendered label aligned with the scientific map aggregation."""
    assert T["en"]["cbar_comp"] == "Station-balanced median \u0394SNR (dB)"
    assert (
        T["de"]["cbar_comp"]
        == "Stationsgleichgewichteter Median des \u0394SNR (dB)"
    )
    for manual in (DOC_EN, DOC_DE):
        assert r"$$m_i=\operatorname{median}_{c}(D_{i,c})$$" in manual
        assert r"$$M_g=\operatorname{median}_{i\in I_g}(m_i)$$" in manual

    assert "sector color summarizes the station-balanced median Delta SNR" in DOC_EN
    assert "Positive $D_{i,c}$ favors the Target; negative favors the Reference" in DOC_EN
    assert "Sektorfarbe den stationsgleichgewichteten Median des Delta SNR" in DOC_DE
    assert "Positives $D_{i,c}$ spricht für das Target, negatives für die Referenz" in DOC_DE


def test_bilingual_manuals_define_saved_inspector_selection_contracts():
    """Saved view guidance must retain one focused peer per result type."""
    english_controls = DOC_EN.split('<a id="sec-5-5"></a>', 1)[1].split(
        '<a id="sec-6"></a>', 1
    )[0]
    german_controls = DOC_DE.split('<a id="sec-5-5"></a>', 1)[1].split(
        '<a id="sec-6"></a>', 1
    )[0]

    assert "Separately for Performance and Benchmark" in english_controls
    assert "One exact `callsign + locator` per result type" in english_controls
    assert "| No |" in english_controls
    assert "one exact peer identity" in DOC_EN
    assert "not matching, eligibility or aggregation upstream" in DOC_EN

    assert "getrennt für Performance und Benchmark" in german_controls
    assert "genau ein `Rufzeichen + Locator` je Ergebnistyp" in german_controls
    assert "| Nein |" in german_controls
    assert "genau eine Peer-Identität" in DOC_DE
    assert "nicht die vorgelagerte Zuordnung, Zulässigkeit oder Aggregation" in DOC_DE


def test_bilingual_manuals_document_only_absolute_utc_analysis_windows():
    """Describe fixed quantized boundaries without the retired rolling mode."""
    assert "fixed 24-hour window ending at the current 15-minute UTC boundary" in DOC_EN
    assert "**Start Date/Time (UTC)** and **End Date/Time (UTC)**" in DOC_EN
    assert "Dates begin in 2008; one run is limited to 31 elapsed days" in DOC_EN
    assert "rounded down to effective 15-minute boundaries" in DOC_EN

    assert "festes 24-Stunden-Fenster bis zur aktuellen 15-Minuten-UTC-Grenze" in DOC_DE
    assert "**Startdatum/-zeit (UTC)** und **Enddatum/-zeit (UTC)**" in DOC_DE
    assert "Datumswerte beginnen im Jahr 2008" in DOC_DE
    assert "auf wirksame 15-Minuten-Grenzen abgerundet" in DOC_DE
    for retired_phrase in (
        "Last X Hours",
        "Last-X",
        "Custom Date/Time",
        "Letzte X Stunden",
        "Letzte-X",
        "Datum/Uhrzeit manuell",
    ):
        assert retired_phrase not in DOC_EN
        assert retired_phrase not in DOC_DE


def test_bilingual_manuals_document_result_specific_population_defaults():
    """Describe interactive defaults without weakening explicit saved values."""
    assert "Performance setup starts with both exclusions on" in DOC_EN
    assert "Benchmark setup starts with both off" in DOC_EN
    assert "Loaded configurations, demos and analysis URLs" in DOC_EN
    assert "Performance-Konfiguration startet mit beiden Ausschlüssen" in DOC_DE
    assert "Benchmark-Konfiguration ohne beide" in DOC_DE
    assert "Geladene Konfigurationen, Demos und Analyse-URLs" in DOC_DE


def test_bilingual_manuals_document_classic_question_first_workflow():
    """Keep the conditional Classic panel sequence explicit in both manuals."""
    for question in (
        "RX Performance",
        "TX Performance",
        "RX Benchmark",
        "TX Benchmark",
    ):
        assert question in DOC_EN
    for benchmark_design in (
        "`Hardware A/B`",
        "`Known Reference Station`",
        "`Local Neighborhood`",
    ):
        assert benchmark_design in DOC_EN
    assert "first panel, **`Question`**" in DOC_EN
    assert "second panel, **`Target and measurement window`**" in DOC_EN
    assert "omits the **`Benchmark design`** panel entirely" in DOC_EN

    for question in (
        "RX Performance",
        "TX Performance",
        "RX-Benchmark",
        "TX-Benchmark",
    ):
        assert question in DOC_DE
    for benchmark_design in (
        "`Hardware A/B`",
        "`Bekannte Referenzstation`",
        "`Lokale Nachbarschaft`",
    ):
        assert benchmark_design in DOC_DE
    assert "Im ersten Bereich **`Frage`**" in DOC_DE
    assert "Der zweite Bereich **`Target und Messzeitraum`**" in DOC_DE
    assert "entfällt der Bereich **`Benchmark-Design`** vollständig" in DOC_DE


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
    assert ".st-key-documentation_body .stMarkdown h2" in stylesheet
    assert "font-size: 1.95rem !important" in stylesheet
    assert (
        ".st-key-documentation_body table.documentation-weighted-columns"
        in stylesheet
    )
    assert "table-layout: fixed !important" in stylesheet
    assert (
        'table[data-documentation-column-layout="section-0-1"]'
        in stylesheet
    )
    assert "border-spacing: 0 0.45rem !important" in stylesheet
    assert ".analysis-choice-single" in stylesheet
    assert ".analysis-family" in stylesheet
    assert ".analysis-variant" in stylesheet
    assert "white-space: nowrap !important" in stylesheet
    assert "tbody td:nth-child(2)" in stylesheet
    assert "tbody td:nth-child(3)" in stylesheet
    assert "@media (max-width: 800px)" in stylesheet
    assert ".st-key-documentation_body .stMarkdown strong.defined-term" in stylesheet
    assert ".st-key-guided_input_flow .stMarkdown strong.defined-term" in stylesheet
    assert ".st-key-documentation_body .stMarkdown p" in stylesheet
    assert "font-family: Arial, Helvetica, sans-serif !important;" in stylesheet
    assert ".st-key-documentation_body a[id]:not(.header-anchor)" in stylesheet
    assert "scroll-margin-top: 5rem" in stylesheet
    assert "strong:first-child:not(.defined-term)" in stylesheet
    assert "color: #39ff14 !important" in stylesheet
    assert 'div[data-testid="stPopover"] button[kind="primary"]' in stylesheet

    conclusion_style_match = re.search(
        r"blockquote\.evidence-conclusion\s*\{(?P<rules>[^}]*)\}",
        stylesheet,
    )
    assert conclusion_style_match is not None
    conclusion_rules = conclusion_style_match.group("rules")
    assert re.search(r"background(?:-color)?\s*:", conclusion_rules)
    assert re.search(r"border-left\s*:", conclusion_rules)
    assert re.search(r"(?<!-)color\s*:", conclusion_rules)
    assert re.search(r"opacity\s*:\s*1\s*!important", conclusion_rules)


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
    """Localized manuals retain shared anchors while English translation leads."""
    english_anchors = re.findall(r'<a id="([^"]+)"></a>', DOC_EN)
    german_anchors = re.findall(r'<a id="([^"]+)"></a>', DOC_DE)

    assert len(english_anchors) == len(set(english_anchors))
    assert len(german_anchors) == len(set(german_anchors))
    assert english_anchors == german_anchors

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
        "sec-5-6",
        "sec-5-7",
        "sec-6",
        "sec-7",
        "sec-7-11",
        "sec-8",
        "sec-outlier",
        "sec-outlier-1",
        "sec-outlier-2",
        "sec-outlier-3",
        "sec-outlier-4",
        "sec-outlier-5",
        "sec-outlier-6",
        "sec-outlier-7",
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
