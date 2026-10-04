import inspect
import re
from contextlib import nullcontext

import pytest

from docs.doc_de import DOC_DE
from docs.doc_en import DOC_EN
from docs.pdf_generator import get_docs
from i18n import GUIDED_INPUTS, T
from ui import documentation
from ui import css as ui_css


@pytest.mark.parametrize(
    ("manual", "boundary", "uncertainty", "policy"),
    [
        (DOC_EN, "1 January 2022 at 00:00 UTC", "physical transmission mode cannot be established", "compatibility policy"),
        (DOC_DE, "1. Januar 2022 um 00:00 UTC", "physikalische Übertragungsart nicht festgestellt werden kann", "Kompatibilitätsregel"),
    ],
    ids=("en", "de"),
)
def test_manual_explains_historical_decode_boundary_and_remaining_uncertainty(manual, boundary, uncertainty, policy):
    historical_section = manual.split('<a id="sec-6-4"></a>')[1].split('<a id="sec-6-5"></a>')[0]
    assert boundary in historical_section
    assert uncertainty in historical_section
    assert policy in historical_section
    assert "`code = 1`" in historical_section
    assert "`decode_filter_mode`" in historical_section


def test_manuals_describe_only_the_current_configuration_and_url_contract():
    """Retired input migration is separate from scientific archive fallback."""
    assert "Only the current saved-configuration schema and public-URL contract are accepted" in DOC_EN
    assert "earlier input formats are rejected without migration" in DOC_EN
    assert "ausschließlich das aktuelle Schema gespeicherter Konfigurationen" in DOC_DE
    assert "frühere Eingabeformate werden ohne Migration abgelehnt" in DOC_DE
    for manual in (DOC_EN, DOC_DE):
        assert "`5m`" not in manual
        assert "`legacy_no_code`" in manual


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
            "dev_credit": T["de"]["dev_credit"],
        }
    return {
        "btn_load_full_documentation": "Load full documentation",
        "btn_hide_full_documentation": "Hide full documentation",
        "sub_documentation": T["en"]["sub_documentation"],
        "dev_credit": T["en"]["dev_credit"],
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
    assert len(english_formulas) == 30
    assert len(english_outlier_formulas) == 13
    assert english_outlier_formulas == german_outlier_formulas
    assert len(english_formulas) - len(english_outlier_formulas) == 17


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
        r"\varepsilon",
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
        r"F=\min(1\ \mathrm{dB},D_{\min}-\varepsilon)",
        r"\varepsilon=0.01\ \mathrm{dB}",
        r"|m_E|\geq D_{\min}-\varepsilon",
        r"|r_{i,u}|\geq D_{\min}-\varepsilon",
        r"\left|B_{\mathrm{pre}}-B_{\mathrm{post}}\right|\leq H_{\max}+\varepsilon",
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
    assert "success percentage among confirmed opportunities" in english_preface
    assert "For RX, success means the Target decoded the remote transmitter" in DOC_EN
    assert "for TX, a remote receiver decoded the Target" in DOC_EN

    assert "die zu untersuchende Station, normalerweise deine Station" in german_preface
    assert '<strong class="defined-term">Peer</strong>' in german_preface
    assert "Erfolgsprozentsatz innerhalb bestätigter Gelegenheiten" in german_preface
    assert "Bei RX bedeutet Erfolg, dass das Target den entfernten Sender decodiert hat" in DOC_DE
    assert "bei TX hat ein entfernter Empfänger das Target decodiert" in DOC_DE


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
    for section in (german_controls, german_outlier, german_formal):
        assert "Joint Spot" in section
    assert "optional expert diagnostic tool" in english_outlier
    assert "not a routine step intended for every operator" in english_outlier
    assert "[Section 7.11](#sec-7-11)" in english_outlier
    assert "optionales Diagnosewerkzeug für erfahrene Anwender" in german_outlier
    assert "nicht für den routinemäßigen Einsatz" in german_outlier
    assert "[Abschnitt 7.11](#sec-7-11)" in german_outlier
    assert "cannot create, merge, split or remove an event" in english_outlier
    assert (
        "kann kein Ereignis erzeugen, zusammenführen, teilen oder entfernen"
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

    assert "one selected database through read-only queries for each completed run" in english_data_source
    assert "does not combine data sources" in english_data_source
    assert "einer ausgewählten Datenbank über schreibgeschützte Abfragen" in german_data_source
    assert "mischt keine Datenquellen" in german_data_source
    for manual in (DOC_EN, DOC_DE):
        assert "wspr.live" in manual
        assert "WSPRDaemon" in manual
        assert '<a href="#ref-10">[Ref-10]</a>' in manual
        assert '<a href="#ref-11">[Ref-11]</a>' in manual


def test_bilingual_introductions_name_databases_and_relocate_routing_to_troubleshooting():
    """Keep database orientation early and complete retry conditions in section 5.6."""
    for manual, intro_terms, routing_terms in (
        (DOC_EN, (
            "**WSPRnet**", "**wspr.live**", "**WSPRDaemon WD2**", "**WD1**",
            "Each completed run uses one database", "never combines records from different sources",
            "grateful to the people", "[Section 5.6](#sec-6-6)",
        ), (
            "ordered capacity spillover is distinct from provider failover",
            "before the run is committed to that source", "restart the complete run",
            "Reference location discovery commits", "If that committed source fails, the attempt stops",
            "failed location discovery is cleared", "records from different sources are never combined",
        )),
        (DOC_DE, (
            "**WSPRnet**", "**wspr.live**", "**WSPRDaemon WD2**", "**WD1**",
            "Jeder abgeschlossene Lauf verwendet genau eine Datenbank",
            "Meldungen verschiedener Quellen werden niemals kombiniert", "dankt den Menschen",
            "[Abschnitt 5.6](#sec-6-6)",
        ), (
            "geordnete Kapazitätsausgleich unterscheidet sich von einem Quellenwechsel nach einem Ausfall",
            "bevor der Lauf auf sie festgelegt ist", "vollständigen Lauf mit der nächsten verfügbaren Quelle neu starten",
            "Referenzstandortsuche bindet", "Fällt diese festgelegte Quelle aus, wird der Versuch beendet",
            "fehlgeschlagene Standortsuche zurückgesetzt", "Datensätze aus verschiedenen Quellen werden niemals zusammengeführt",
        )),
    ):
        intro = manual.split('<a id="sec-1-1"></a>', 1)[1].split('<a id="sec-1-0"></a>', 1)[0]
        routing = manual.split('<a id="sec-6-6"></a>', 1)[1].split('<a id="part-iii"></a>', 1)[0]
        for term in intro_terms:
            assert term in intro
        for term in routing_terms:
            assert term in routing
        assert routing.index("**wspr.live**") < routing.index("**WSPRDaemon WD2**") < routing.index("**WD1**")
        assert '<strong class="defined-term">archives</strong>' not in intro
        assert '<strong class="defined-term">Archive</strong>' not in intro



def test_bilingual_reference_entries_use_current_project_landing_pages():
    """Keep the two early archive references on their approved public pages."""
    approved_merging_reference = (
        "https://wsprdaemon.readthedocs.io/en/master/FAQ.html"
        "#how-does-spot-merging-work-with-multiple-receivers"
    )
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
        reference_entry = manual.split('<a id="ref-11"></a>', 1)[1].split(
            '<a id="ref-12"></a>', 1
        )[0]
        assert f'href="{approved_merging_reference}"' in reference_entry
        assert manual.count(approved_merging_reference) == 1
        assert "wsprdaemon.readthedocs.io" not in manual.replace(
            approved_merging_reference, ""
        )


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
    assert "| Your question | Practical examples | Analysis to choose |" in DOC_EN
    assert "| What you want to learn | WSPRadar approach |" not in DOC_EN
    for operating_question in (
        "Which of my antennas receives better?",
        "Which of my antennas is heard better?",
        "How does my station compare with a known station?",
        "How does my station compare with nearby WSPR stations?",
        "What can my antenna and receiver hear, and how consistently?",
        "Where is my station heard, and how consistently?",
    ):
        assert operating_question in DOC_EN
    for benchmark_family, benchmark_variant in (
        ("RX Benchmark", "Reference Setup/Station"),
        ("TX Benchmark", "Reference Setup/Station"),
        ("RX/TX Benchmark", "Reference Setup/Station"),
        ("RX/TX Benchmark", "Reference Neighborhood (Local Median)"),
    ):
        assert (
            f'<span class="analysis-family">{benchmark_family}</span><br>'
            f'<strong class="analysis-variant">{benchmark_variant}</strong>'
            in DOC_EN
        )
    assert DOC_EN.count('class="analysis-choice"') == 4
    assert DOC_EN.count('class="analysis-choice-single"') == 2
    for scientific_safeguard in (
        "simultaneous receiver/decoder chains with distinct reporting callsigns",
        "Keep other conditions the same or confirm with a crossover",
        "two simultaneous transmitters with distinct identities, synchronized cycles",
        "verified actual and reported power",
        "your Reference is not an absolute calibrated standard",
        "median SNR of qualifying observed stations within your chosen radius",
        "neither isolates antenna gain nor ranks every nearby station",
        "confirmed opportunities with evidence of station activity",
    ):
        assert scientific_safeguard in DOC_EN
    assert "Benchmark —" not in DOC_EN[: DOC_EN.index('<a id="sec-1-3"></a>')]
    assert "Choose the question you want to answer" not in DOC_EN
    assert "The demo is a worked example of the method, not evidence about your station" in DOC_EN
    assert "### 1. Choose and Prepare the Analysis" in DOC_EN
    assert '<strong class="defined-term">Target</strong>' in DOC_EN
    assert '<strong class="defined-term">Reference</strong>' in DOC_EN
    assert '<strong class="defined-term">Performance</strong>' in DOC_EN


@pytest.mark.parametrize("documentation_text", (DOC_EN, DOC_DE), ids=("en", "de"))
def test_local_neighborhood_manuals_present_only_the_median_method(documentation_text):
    """Keep the supported local design and remove its obsolete alternative and selector."""
    for retired_term in (
        "Local Best Station",
        "Beste lokale Station",
        "besten lokalen Station",
        "Local Median/Best",
        "Median- und Best-Peer",
        "sec-3-rx-benchmark-local-best",
        "sec-3-tx-benchmark-local-best",
        "**Local Benchmark Method**",
        "**Lokale Benchmark-Methode**",
    ):
        assert retired_term not in documentation_text
    assert documentation_text.count('class="analysis-choice"') == 4
    assert '<a id="sec-3-rx-benchmark-local-median"></a>' in documentation_text
    assert '<a id="sec-3-tx-benchmark-local-median"></a>' in documentation_text


@pytest.mark.parametrize(
    ("documentation_text", "required_meaning"),
    (
        (
            DOC_EN,
            {
                "rx": (
                    "same remote transmitter in the same WSPR cycle",
                    "ΔSNR additionally requires a qualifying Target report",
                    "complete installed receiving stations",
                    "local noise and interference",
                    "only one contributing receiver",
                    "does not establish that its antenna has a corresponding gain advantage",
                ),
                "tx": (
                    "same remote receiver during the same WSPR cycle",
                    "not every nearby transmitter or every attempted transmission",
                    "does not verify actual transmitter power",
                    "unknown feedline losses",
                    "only one contributing transmitter",
                    "For a confirmatory run",
                ),
                "method": (
                    "within-identity median",
                    "Target-side consolidation retains the strongest",
                    "full reported locator",
                    "independent physical sites",
                    "no separate minimum number of local contributors",
                    "With no contributors, no Reference SNR or paired ΔSNR",
                    "do not impose a minimum neighborhood size",
                    "selection effects or dependence between observations",
                ),
                "correction": (
                    "use `0.0 dB` when no independently justified correction",
                    "same additive offset applies to the contributing Reference population",
                    "does not establish calibration",
                    "different unknown errors in individual neighboring stations",
                ),
                "claims": (
                    "neither a permanent station ranking nor a calibrated antenna comparison",
                    "Joint Evidence Share describes pairability or coverage",
                    "not a Target win rate",
                    "within-run consistency",
                    "does not isolate antenna gain",
                ),
            },
        ),
        (
            DOC_DE,
            {
                "rx": (
                    "desselben entfernten Senders im selben WSPR-Zyklus",
                    "ΔSNR erfordert zusätzlich eine qualifizierende Target-Meldung",
                    "vollständig aufgebaute Empfangsstationen",
                    "lokales Rauschen und Störungen",
                    "nur einem beitragenden Empfänger",
                    "keinen entsprechenden Gewinnvorteil ihrer Antenne",
                ),
                "tx": (
                    "derselbe entfernte Empfänger während desselben WSPR-Zyklus",
                    "nicht jeden Sender in der Umgebung oder jeden Sendeversuch",
                    "überprüft weder die tatsächliche Senderleistung",
                    "unbekannte Speiseleitungsverluste",
                    "nur einem beitragenden Sender",
                    "für einen bestätigenden Lauf",
                ),
                "method": (
                    "Median innerhalb dieser Identität",
                    "Zusammenführung auf der Target-Seite behält das stärkste",
                    "vollständig gemeldetem Locator",
                    "unabhängiger physischer Standorte",
                    "keine gesonderte Mindestzahl lokaler Beitragender",
                    "Ohne Beitragende steht weder ein Referenz-SNR noch gepaartes ΔSNR",
                    "keine Mindestgröße der Nachbarschaft",
                    "Selektionseffekte oder Abhängigkeiten zwischen Beobachtungen",
                ),
                "correction": (
                    "`0.0 dB`, wenn keine unabhängig begründete Korrektur",
                    "derselbe additive Offset unter den ausgewählten Bedingungen für die beitragende Referenzpopulation gilt",
                    "begründet keine Kalibrierung",
                    "unterschiedliche unbekannte Fehler einzelner Nachbarstationen",
                ),
                "claims": (
                    "weder eine dauerhafte Stationsrangliste noch ein kalibrierter Antennenvergleich",
                    "Joint-Evidenzanteil beschreibt Paarbarkeit oder Abdeckung",
                    "keine Gewinnrate des Targets",
                    "Konsistenz innerhalb eines Laufs",
                    "isoliert keinen Antennengewinn",
                ),
            },
        ),
    ),
    ids=("en", "de"),
)
def test_local_median_manuals_bound_observation_selection_and_station_claims(
    documentation_text, required_meaning
):
    """Keep RX/TX selection, weighting, correction and claim limits in their content homes."""
    section_anchors = {
        "rx": ("sec-3-rx-benchmark-local-median", "sec-3-tx-benchmark"),
        "tx": ("sec-3-tx-benchmark-local-median", "sec-3-rx-performance"),
        "method": ("sec-7-7", "sec-7-8"),
        "correction": ("sec-5-3", "sec-5-4"),
        "claims": ("sec-8-1", "sec-8-2"),
    }
    for meaning_scope, required_fragments in required_meaning.items():
        start_anchor, end_anchor = section_anchors[meaning_scope]
        section_text = documentation_text.split(
            f'<a id="{start_anchor}"></a>', 1
        )[1].split(f'<a id="{end_anchor}"></a>', 1)[0]
        for required_fragment in required_fragments:
            assert required_fragment in section_text, (meaning_scope, required_fragment)


def test_english_evidence_path_has_one_authoritative_guide_home():
    """Keep the complete operator path emphasized without fragmenting its meaning."""
    defined_evidence_path = (
        '<strong class="defined-term">Map → Segment Inspector → '
        'Performance/Benchmark Evidence → Temporal Evidence → Station Insights '
        '→ Selected Station Evidence → Drill-Down</strong>'
    )

    guide = DOC_EN.split('<a id="sec-2-3-overview"></a>', 1)[1].split('<a id="sec-3"></a>', 1)[0]
    preface = DOC_EN.split('<a id="sec-1-3"></a>', 1)[1].split('<a id="sec-1-4"></a>', 1)[0]
    assert defined_evidence_path in guide
    assert DOC_EN.count(defined_evidence_path) == 1
    assert "[Section 1.3](#sec-2-3-overview)" in preface


def test_english_section_two_conclusions_use_scoped_callout_markup():
    """Style every Chapter 2 conclusion without affecting other blockquotes."""
    before_section_two, section_two_and_later = DOC_EN.split(
        '<a id="sec-3"></a>',
        1,
    )
    section_two, section_three_and_later = section_two_and_later.split(
        '<a id="sec-4"></a>',
        1,
    )
    conclusion_opening = '<blockquote class="evidence-conclusion">'

    assert section_two.count(conclusion_opening) == 8
    assert conclusion_opening not in before_section_two
    assert conclusion_opening not in section_three_and_later


def test_english_playbooks_define_performance_opportunities_and_tx_ab_timing():
    """Retain operator-facing eligibility and same-cycle safeguards."""
    rx_performance = DOC_EN.split('<a id="sec-3-rx-performance"></a>', 1)[1].split(
        '<a id="sec-3-tx-performance"></a>', 1
    )[0]
    tx_performance = DOC_EN.split('<a id="sec-3-tx-performance"></a>', 1)[1].split(
        '<a id="sec-outlier"></a>', 1
    )[0]
    assert "confirmed RX opportunity" in rx_performance
    assert "one exact transmitter identity on the selected band in one WSPR cycle" in rx_performance
    assert "A successful Target decode confirms both endpoints" in rx_performance
    assert "counts even without another receiver's report" in rx_performance
    assert "while Target activity is also confirmed" in rx_performance
    assert "Another receiver's report alone does not establish that the Target was listening" in rx_performance
    assert "confirmed TX opportunity" in tx_performance
    assert "one exact receiver identity on the selected band in one WSPR cycle" in tx_performance
    assert "A successful Target report confirms both endpoints" in tx_performance
    assert "counts even if that receiver reports no other transmitter" in tx_performance
    assert "while Target activity is also confirmed" in tx_performance
    assert "not that this particular silent receiver was listening" in tx_performance
    assert "same two-minute UTC reported slot" in DOC_EN
    assert "exact remote callsign plus full reported locator" in DOC_EN
    assert "Only Joint Spots supply ΔSNR" in DOC_EN
    assert "does not require identical RF frequencies" in DOC_EN
    assert '<a id="sec-3-tx-benchmark-sequential"></a>' not in DOC_EN


def test_bilingual_benchmark_uses_two_reference_choices_and_same_cycle_evidence():
    """Keep one fixed-Reference contract and preserve neighborhood interpretation."""
    for manual, fixed, local, controlled, independent, no_reports, source_error in (
        (DOC_EN, "Reference Setup/Station", "Reference Neighborhood",
         "The intended difference is the component or path under test",
         "distinct complete receiving stations", "no qualifying reports", "source error"),
        (DOC_DE, "Referenzaufbau/-station", "Referenznachbarschaft",
         "Der beabsichtigte Unterschied ist das untersuchte Bauteil oder der untersuchte Pfad",
         "eigenständige vollständige Empfangsstationen", "ohne passende Meldungen", "Datenquellenfehler"),
    ):
        for phrase in (fixed, local, no_reports, source_error):
            assert phrase in manual
        fixed_reference_guidance = manual.split(
            '<a id="sec-3-rx-benchmark-hardware"></a>', 1
        )[1].split('<a id="sec-3-rx-benchmark-local-median"></a>', 1)[0]
        assert controlled in fixed_reference_guidance
        assert independent in fixed_reference_guidance
        assert '<a id="sec-simultaneous-tx-setup"></a>' in manual
        assert '<a id="sec-reference-snr-calibration"></a>' in manual
        assert '<a id="sec-sequential-tx-setup"></a>' not in manual
        assert "Scheduled Pair" not in manual
        assert "100 Hz" in manual
        assert "Both (Async)" in manual
        assert "Setup A" not in manual
        assert "Setup B" not in manual
    for manual, fixed_heading in (
        (DOC_EN, "Reference Setup/Station"),
        (DOC_DE, "Referenzaufbau/-station"),
    ):
        tx_fixed_reference = manual.split(
            '<a id="sec-3-tx-benchmark-simultaneous"></a>', 1
        )[1].split('<a id="sec-3-tx-benchmark-local-median"></a>', 1)[0]
        assert re.search(r"^##### \d+\.\d+\.\d+ " + re.escape(fixed_heading), tx_fixed_reference, re.MULTILINE)
    assert "Both arrangements use the same pairing algorithm." in DOC_EN
    assert "Beide Anordnungen verwenden denselben Paarbildungsalgorithmus." in DOC_DE
    assert "multiple candidates require your choice" in DOC_EN
    assert "bei mehreren Kandidaten ist deine Auswahl erforderlich" in DOC_DE
    assert "not proof of one physical site" in DOC_EN
    assert "beweist keinen einzelnen physischen Standort" in DOC_DE


def test_bilingual_manuals_define_practical_simultaneous_tx_setup_and_legacy_links():
    """Pin retained simultaneous operating limits and practical supplements."""
    english_a4 = DOC_EN.split('<a id="sec-a-4"></a>', 1)[1].split(
        '<a id="sec-simultaneous-tx-setup"></a>', 1
    )[0]
    german_a4 = DOC_DE.split('<a id="sec-a-4"></a>', 1)[1].split(
        '<a id="sec-simultaneous-tx-setup"></a>', 1
    )[0]

    for a4 in (english_a4, german_a4):
        assert "`Tx Pct`" in a4
        assert "`100%`" in a4
        assert "`5–20%`" in a4
        assert "QMX" in a4
        assert "Virtual U3S" in a4
        assert "Ultimate3S" in a4
        assert "ZachTek" in a4
        assert "firmware" in a4.casefold()
    assert "random" in english_a4.casefold()
    assert "zufällig" in german_a4.casefold()
    assert "randomized split-lane" in english_a4.casefold()
    assert "festfrequenz" not in german_a4.casefold()
    assert "fixed-frequency" not in english_a4.casefold()

    english_simultaneous = DOC_EN.split(
        '<a id="sec-simultaneous-tx-setup"></a>', 1
    )[1].split('<a id="sec-reference-snr-calibration"></a>', 1)[0]
    german_simultaneous = DOC_DE.split(
        '<a id="sec-simultaneous-tx-setup"></a>', 1
    )[1].split('<a id="sec-reference-snr-calibration"></a>', 1)[0]

    for simultaneous in (english_simultaneous, german_simultaneous):
        assert "100 Hz" in simultaneous
        assert "https://www.wsprnet.org/drupal/wsprnet/spotquery" in simultaneous
        assert "QMX" in simultaneous
        assert "Virtual U3S" in simultaneous
        assert "Ultimate3S" in simultaneous
        assert "ZachTek" in simultaneous
        assert "freq = freq + (100ULL * random (-100, 100));" in simultaneous
        assert "freq = freq - (100ULL * random(31, 91));" in simultaneous
        assert "freq = freq + (100ULL * random(30, 90));" in simultaneous
        assert "freq = freq - 5000ULL;" not in simultaneous
        assert "freq = freq + 5000ULL;" not in simultaneous
    assert "ZachTek firmware 2.19 fixed-frequency" not in english_simultaneous
    assert "ZachTek-Firmware 2.19: Festfrequenz" not in german_simultaneous
    assert "compound callsigns" in english_simultaneous
    assert "both transmitters different suffixes" in english_simultaneous
    assert "permitted for your callsign and operation in your country" in english_simultaneous
    assert "zusammengesetzte Rufzeichen" in german_simultaneous
    assert "beiden Sendern unterschiedliche Suffixe" in german_simultaneous
    assert "in deinem Land für dein Rufzeichen und deinen Betrieb zulässig" in german_simultaneous
    assert "wait until the test spots are actually queryable" in english_simultaneous
    assert "tatsächlich abfragbar" in german_simultaneous
    assert "both" in english_simultaneous
    assert "occurrences" in english_simultaneous
    assert "beiden" in german_simultaneous
    assert "Vorkommen" in german_simultaneous
    for simultaneous in (english_simultaneous, german_simultaneous):
        normalized_simultaneous = simultaneous.casefold()
        assert "kompil" in normalized_simultaneous or "compil" in normalized_simultaneous
        assert "flash" in normalized_simultaneous

    english_power = english_simultaneous.split(
        '<a id="sec-simultaneous-tx-setup-3"></a>', 1
    )[1].split('<a id="sec-simultaneous-tx-setup-4"></a>', 1)[0]
    german_power = german_simultaneous.split(
        '<a id="sec-simultaneous-tx-setup-3"></a>', 1
    )[1].split('<a id="sec-simultaneous-tx-setup-4"></a>', 1)[0]

    assert "false dBm" in english_power
    assert "nearest valid WSPR-encoded dBm value" in english_power
    assert "WSPRadar" in english_power
    assert "excessive power" in english_power
    assert "falsch" in german_power.casefold()
    assert "nächst" in german_power.casefold()
    assert "gültig" in german_power.casefold()
    assert "wspr" in german_power.casefold()
    assert "kodier" in german_power.casefold()
    assert "WSPRadar" in german_power
    assert (
        "unnötig hohe Leistung" in german_power
        or "übermäßige Leistung" in german_power
    )
    for power_guidance in (english_power, german_power):
        normalized_power_guidance = power_guidance.casefold()
        assert "20–30 dbm" in normalized_power_guidance
        assert "intermodulation" in normalized_power_guidance
    assert "occupied bandwidth" in english_power
    assert "spurious products" in english_power
    assert "belegte Bandbreite" in german_power
    assert "unerwünschte Aussendungen" in german_power
    assert "coupled power" not in english_power.casefold()
    assert "desensitize" not in english_power.casefold()
    assert "Record transmitter, firmware, oscillator or GNSS source" not in english_power
    assert "oscillator or GNSS source" not in english_power
    assert "eingekoppelte Sendeleistung" not in german_power
    assert "desensibilisieren" not in german_power
    assert "Notiere vor dem Messlauf für beide Pfade Sender, Firmware" not in german_power

    english_archive_check = english_simultaneous.split(
        '<a id="sec-simultaneous-tx-setup-4"></a>', 1
    )[1].split('<a id="sec-simultaneous-tx-setup-5"></a>', 1)[0]
    german_archive_check = german_simultaneous.split(
        '<a id="sec-simultaneous-tx-setup-4"></a>', 1
    )[1].split('<a id="sec-simultaneous-tx-setup-5"></a>', 1)[0]
    assert "local decoder" not in english_archive_check.casefold()
    assert "spectrum screenshot" not in english_archive_check.casefold()
    assert "lokalen Decoders" not in german_archive_check
    assert "Screenshot des Spektrums" not in german_archive_check

    english_archive_steps = re.findall(r"^\d+\..*$", english_archive_check, re.MULTILINE)
    german_archive_steps = re.findall(r"^\d+\..*$", german_archive_check, re.MULTILINE)
    assert any(
        "WSPRadar" in step
        and "query" in step.casefold()
        and "actual data availability, not a fixed waiting period" in step
        for step in english_archive_steps
    )
    assert any(
        "WSPRadar" in step
        and ("abfrag" in step.casefold() or "verfügbar" in step.casefold())
        and "Daten tatsächlich vorliegen, nicht eine feste Wartezeit" in step
        for step in german_archive_steps
    )

    english_combined_devices = english_simultaneous.split(
        '<a id="sec-simultaneous-tx-setup-5-1"></a>', 1
    )[1].split('<a id="sec-simultaneous-tx-setup-5-3"></a>', 1)[0]
    german_combined_devices = german_simultaneous.split(
        '<a id="sec-simultaneous-tx-setup-5-1"></a>', 1
    )[1].split('<a id="sec-simultaneous-tx-setup-5-3"></a>', 1)[0]

    combined_device_anchor_pattern = re.compile(
        r'<a id="sec-simultaneous-tx-setup-5-1"></a>\s*'
        r'<a id="sec-simultaneous-tx-setup-5-2"></a>\s*'
        r'##### B\.5\.1[–/-]B\.5\.2[^\n]*'
    )
    for simultaneous in (english_simultaneous, german_simultaneous):
        combined_heading_match = combined_device_anchor_pattern.search(simultaneous)
        assert combined_heading_match is not None
        combined_heading = combined_heading_match.group(0)
        assert "QMX" in combined_heading
        assert "Virtual" in combined_heading
        assert "Ultimate3S" in combined_heading

    for device_setup in (english_combined_devices, german_combined_devices):
        normalized_device_setup = device_setup.casefold()
        assert device_setup.count("#####") == 1
        assert "`1_04_000`" in device_setup
        assert "`Frame = 20`" in device_setup
        assert "`Start = 04`" in device_setup
        assert "`Start = 00`" in device_setup
        assert "not used" in device_setup
        assert "determin" in normalized_device_setup
        assert "spar" in normalized_device_setup
        assert device_setup.count("+50 Hz") >= 4
        assert device_setup.count("+150 Hz") >= 4
        alternating_rows = [
            line
            for line in device_setup.splitlines()
            if re.match(r"^\|\s*[1-4]\s*\|", line)
            and "+50 Hz" in line
            and "+150 Hz" in line
        ]
        assert len(alternating_rows) == 4

    assert "physical Ultimate3S" in english_combined_devices
    assert "up to 16" in english_combined_devices
    assert "Virtual U3S" in english_combined_devices
    assert "version" in english_combined_devices.casefold()
    assert "physisch" in german_combined_devices.casefold()
    assert "Ultimate3S" in german_combined_devices
    assert "bis zu 16" in german_combined_devices
    assert "Virtual U3S" in german_combined_devices
    assert "version" in german_combined_devices.casefold()
    assert "same-cycle" in english_combined_devices
    assert "same WSPR cycle" in english_combined_devices
    assert "frequency-position" in english_combined_devices
    assert "balance" in english_combined_devices.casefold()
    assert "reduce" in english_combined_devices.casefold()
    assert (
        "does not prove" in english_combined_devices.casefold()
        or "does not guarantee" in english_combined_devices.casefold()
    )
    assert "denselben WSPR-Zyklus" in german_combined_devices
    assert "Frequenzposition" in german_combined_devices
    assert "balancier" in german_combined_devices.casefold()
    assert "verringer" in german_combined_devices.casefold()
    assert any(
        bounded_claim in german_combined_devices.casefold()
        for bounded_claim in ("belegt aber nicht", "garantiert nicht")
    )
    assert "QMX+-specific" in english_combined_devices
    assert "nicht" in german_combined_devices
    assert "allgemein" in german_combined_devices

    english_zachtek = english_simultaneous.split(
        '<a id="sec-simultaneous-tx-setup-5-3"></a>', 1
    )[1].split('<a id="sec-simultaneous-tx-setup-6"></a>', 1)[0]
    german_zachtek = german_simultaneous.split(
        '<a id="sec-simultaneous-tx-setup-5-3"></a>', 1
    )[1].split('<a id="sec-simultaneous-tx-setup-6"></a>', 1)[0]
    for zachtek_setup in (english_zachtek, german_zachtek):
        assert "freq = freq + (100ULL * random (-100, 100));" in zachtek_setup
        assert "freq = freq - (100ULL * random(31, 91));" in zachtek_setup
        assert "freq = freq + (100ULL * random(30, 90));" in zachtek_setup
        assert "freq = freq - 5000ULL;" not in zachtek_setup
        assert "freq = freq + 5000ULL;" not in zachtek_setup
        assert "`Product_Model`" in zachtek_setup
        assert "`1048`" in zachtek_setup
        assert "ESP8285" in zachtek_setup
        assert "NeoGPS" in zachtek_setup
        assert any(
            "-90" in line
            and "-31 Hz" in line
            and line.index("-90") < line.index("-31 Hz")
            for line in zachtek_setup.splitlines()
        )
        assert any(
            "+30" in line
            and "+89 Hz" in line
            and line.index("+30") < line.index("+89 Hz")
            for line in zachtek_setup.splitlines()
        )
        assert "61 Hz" in zachtek_setup
        assert "57 Hz" in zachtek_setup
        assert "10 Hz" in zachtek_setup
        assert "Joint" in zachtek_setup
    assert "##### B.5.3 ZachTek firmware 2.19 randomized split-lane builds" in english_zachtek
    assert "both" in english_zachtek.casefold()
    assert "occurrences" in english_zachtek.casefold()
    assert "`0.01 Hz`" in english_zachtek
    assert "tone-zero" in english_zachtek.casefold()
    assert "4.4 Hz" in english_zachtek
    assert "randomization" in english_zachtek.casefold()
    assert any(
        benefit_word in english_zachtek.casefold()
        for benefit_word in ("advantage", "benefit")
    )
    assert "lower-versus-upper" in english_zachtek.casefold()
    assert "passband" in english_zachtek.casefold()
    assert "Run 1" in english_zachtek
    assert "Run 2" in english_zachtek
    assert "source-code" in english_zachtek.casefold()
    assert "configuration program" in english_zachtek.casefold()
    assert "after flashing" in english_zachtek.casefold()
    assert "on-air" in english_zachtek.casefold()
    assert "preflight" in english_zachtek.casefold()
    assert "Type 3" in english_zachtek
    assert "same selected frequency" in english_zachtek
    english_tone_zero_sentence = next(
        sentence
        for sentence in re.split(r"(?<=[.!?])\s+", english_zachtek)
        if "61 Hz" in sentence
    )
    english_complete_signal_sentence = next(
        sentence
        for sentence in re.split(r"(?<=[.!?])\s+", english_zachtek)
        if "57 Hz" in sentence
    )
    assert "command" in english_tone_zero_sentence.casefold()
    assert "tone-zero" in english_tone_zero_sentence.casefold()
    assert "command" in english_complete_signal_sentence.casefold()
    assert "actual radiated" in english_zachtek.casefold()
    english_edge_margin_sentence = next(
        sentence
        for sentence in re.split(r"(?<=[.!?])\s+", english_zachtek)
        if "10 Hz" in sentence
    )
    assert "tone-zero" in english_edge_margin_sentence.casefold()

    assert "##### B.5.3" in german_zachtek
    assert "ZachTek" in german_zachtek
    assert "2.19" in german_zachtek
    assert "beide" in german_zachtek.casefold()
    assert "Vorkommen" in german_zachtek
    assert "`0,01 Hz`" in german_zachtek or "`0.01 Hz`" in german_zachtek
    assert "Ton 0" in german_zachtek or "Ton-0" in german_zachtek
    assert "4,4 Hz" in german_zachtek or "4.4 Hz" in german_zachtek
    assert "Zufall" in german_zachtek
    assert "Vorteil" in german_zachtek
    assert "systematischen Einfluss" in german_zachtek
    assert "Durchlasskurve" in german_zachtek
    assert "Lauf 1" in german_zachtek
    assert "Lauf 2" in german_zachtek
    assert "Quellcode" in german_zachtek
    assert "Konfigurationsprogramm" in german_zachtek
    assert "nach dem flashen" in german_zachtek.casefold()
    assert "auf Sendung" in german_zachtek
    assert "Vorabprüfung" in german_zachtek
    assert "Typ 3" in german_zachtek or "Typ-3" in german_zachtek
    assert "gewählte Frequenz" in german_zachtek
    german_tone_zero_sentence = next(
        sentence
        for sentence in re.split(r"(?<=[.!?])\s+", german_zachtek)
        if "61 Hz" in sentence
    )
    german_complete_signal_sentence = next(
        sentence
        for sentence in re.split(r"(?<=[.!?])\s+", german_zachtek)
        if "57 Hz" in sentence
    )
    assert "programmier" in german_tone_zero_sentence.casefold()
    assert "ton-0" in german_tone_zero_sentence.casefold()
    assert "programmier" in german_complete_signal_sentence.casefold()
    assert "tatsächlichen HF-Signale" in german_zachtek
    german_edge_margin_sentence = next(
        sentence
        for sentence in re.split(r"(?<=[.!?])\s+", german_zachtek)
        if "10 Hz" in sentence
    )
    assert "ton-0" in german_edge_margin_sentence.casefold()

    assert "recoverable stock firmware image" in english_zachtek
    assert "build prerequisites" in english_zachtek
    assert "lower and upper lanes" in english_zachtek
    assert "Joint Spots from the same cycles" in english_zachtek
    assert "wieder einspielbares Abbild der unveränderten Firmware" in german_zachtek
    assert "Build-Voraussetzungen" in german_zachtek
    assert "unteren beziehungsweise oberen Fenster" in german_zachtek
    assert "Joint Spots in denselben Zyklen" in german_zachtek

    for manual in (DOC_EN, DOC_DE):
        assert manual.index('<a id="sec-simultaneous-tx-setup"></a>') < manual.index(
            '<a id="sec-reference-snr-calibration"></a>'
        )
        assert '<a id="sec-sequential-tx-setup"></a>' not in manual


def test_bilingual_manuals_define_supported_exact_archive_identities():
    """Document letter-only and suffix forms as distinct exact archive tokens."""
    exact_identity_examples = (
        "`CALL`",
        "`CALL/1`",
        "`CALL/2`",
        "`CALL/P`",
        "`CALL/QRP`",
        "`CALL-1`",
    )
    for manual in (DOC_EN, DOC_DE):
        for identity in exact_identity_examples:
            assert identity in manual
        assert "`KFS`" not in manual
        assert "`KFS/SE`" not in manual
        assert "`DL1MKS`" not in manual

    assert "distinct exact identities" in DOC_EN
    assert "does not apply hidden prefix or suffix matching" in DOC_EN
    assert "verschiedene exakte Datenbankidentitäten" in DOC_DE
    assert "verdeckte Präfix- oder Suffixzuordnung" in DOC_DE


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
    playbooks = (
        ("sec-3-rx-benchmark", "RX Benchmark"),
        ("sec-3-tx-benchmark", "TX Benchmark"),
        ("sec-3-rx-performance", "RX Performance"),
        ("sec-3-tx-performance", "TX Performance"),
    )
    for manual in (DOC_EN, DOC_DE):
        positions = [manual.index(f'<a id="{anchor}"></a>') for anchor, _title in playbooks]
        assert positions == sorted(positions)
        for anchor, title in playbooks:
            playbook = manual.split(f'<a id="{anchor}"></a>', 1)[1]
            heading = re.search(r"^#### \d+\.\d+ (.+)$", playbook, re.MULTILINE)
            assert heading is not None
            assert heading.group(1) == title

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
        r"$$S_{i,c}=T_{i,c},\qquad O_{i,c}=T_{i,c}\lor E_{i,c},\qquad M_{i,c}=E_{i,c}\land\neg T_{i,c}$$",
        "`opportunity-v3`",
        "Target-only success",
        "already included once in both the success count and the opportunity count",
        "peer TX → Target RX",
        "Target TX → peer RX",
        "particular silent Target RX or peer RX was listening",
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
        r"$$S_{i,c}=T_{i,c},\qquad O_{i,c}=T_{i,c}\lor E_{i,c},\qquad M_{i,c}=E_{i,c}\land\neg T_{i,c}$$",
        "`opportunity-v3`",
        "Target-only-Erfolg",
        "genau einmal in Erfolgs- und Gelegenheitsanzahl enthalten",
        "Peer-TX → Target-RX",
        "Target-TX → Peer-RX",
        "bestimmter stiller Target-RX oder Peer-RX zugehört hat",
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
        "Exact `callsign + locator` identities: normally at most one per result type",
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
        "exakte Identitäten aus `Rufzeichen + Locator`: normalerweise höchstens eine je Ergebnistyp",
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
        "One-sided evidence still has no ΔSNR",
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
        "Einseitige Evidenz besitzt weiterhin kein ΔSNR",
    )

    for required_text in english_contract:
        assert required_text in DOC_EN
    for required_text in german_contract:
        assert required_text in DOC_DE


def test_bilingual_manuals_require_map_values_to_be_read_with_support():
    """Retain map interpretation while allowing presentation details to evolve."""
    assert "Read sector color together with the contributing station count and the applicable opportunity or Joint Spot counts" in DOC_EN
    assert "A colored sector is a prompt to inspect, not the conclusion" in DOC_EN
    assert "Segment color shows the **Station-balanced Decode Rate**" in DOC_EN
    assert "with equal weight per identity" in DOC_EN

    assert "Lies die Sektorfarbe zusammen mit der Anzahl beitragender Stationen" in DOC_DE
    assert "noch keine Schlussfolgerung" in DOC_DE
    assert "Die Sektorfarbe zeigt die **Stationsgleichgewichtete Dekodierrate**" in DOC_DE
    assert "mit gleichem Gewicht je Identität" in DOC_DE


@pytest.mark.parametrize(
    ("documentation_text", "required_meaning"),
    [
        (
            DOC_EN,
            (
                "callsign + full reported locator",
                "Each identity must separately meet",
                "exactly the identities counted",
                "only one-sided evidence do not contribute",
                "same callsign at different full locators counts separately",
                "does not establish independent physical stations or sites",
                "segment median of `+3 dB` and support count `2`",
                "minimum of three does not",
            ),
        ),
        (
            DOC_DE,
            (
                "Rufzeichen + vollständig gemeldeter Locator",
                "Jede Identität muss für sich",
                "die konfigurierte Mindestzahl an Joint-Evidenz",
                "Genau die Identitäten",
                "ausschließlich einseitiger Evidenz tragen nicht",
                "unterschiedlichen vollständigen Locatorn zählt getrennt",
                "keine unabhängigen physischen Stationen oder Standorte",
                "Segmentmedian von `+3 dB` und eine Unterstützungszahl von `2`",
                "Mindestanzahl von drei nicht",
            ),
        ),
    ],
    ids=["en", "de"],
)
def test_benchmark_manuals_use_one_identity_for_weighting_and_segment_support(
    documentation_text,
    required_meaning,
):
    """Keep identity, paired qualification and physical-independence limits explicit."""
    aggregation_section = documentation_text.split(
        '<a id="sec-7-7"></a>', 1
    )[1].split('<a id="sec-7-8"></a>', 1)[0]

    for required_fragment in required_meaning:
        assert required_fragment in aggregation_section
    for example_locator in ("JO31AA", "JO31AB"):
        assert example_locator in aggregation_section


def test_bilingual_manuals_explain_station_and_observation_benchmark_weighting():
    """Keep complementary Benchmark weighting without pinning bar styling."""
    for manual, station_value, paired_value, volume_weight, support in (
        (
            DOC_EN,
            "Each transmitter contributes one median ΔSNR from its Joint Spots",
            "Each Joint Spot contributes one ΔSNR value",
            "frequently observed stations contribute more",
            "Joint station/spot counts",
        ),
        (
            DOC_DE,
            "Jeder Sender geht mit einem ΔSNR-Median aus seinen Joint Spots ein",
            "Jeder Joint Spot geht mit einem ΔSNR-Wert ein",
            "häufig beobachtete Sender tragen mehr Werte bei",
            "Anzahlen der Joint-Stationen und Joint Spots",
        ),
    ):
        rx_benchmark = manual.split('<a id="sec-3-rx-benchmark"></a>', 1)[1].split(
            '<a id="sec-3-rx-benchmark-hardware"></a>', 1
        )[0]
        for meaning in (station_value, paired_value, volume_weight, support, "**Decode Outcomes**"):
            assert meaning in rx_benchmark


def test_bilingual_manuals_follow_reference_first_use_and_introductory_term_policy():
    """Meaningful documentation contracts must remain aligned across languages."""
    for manual in (DOC_EN, DOC_DE):
        before_references, references_and_appendices = manual.split(
            '<a id="sec-ref"></a>', 1
        )
        appendices = references_and_appendices.split('<a id="part-iv"></a>', 1)[1]
        narrative = before_references + appendices
        first_use_order = list(
            dict.fromkeys(
                int(number)
                for number in re.findall(r'href="#ref-(\d+)"', narrative)
            )
        )

        assert first_use_order == list(range(1, 21))
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
    """Keep time mechanics out; the density-cell contract is documented explicitly."""
    english_outside_density = DOC_EN.split('<a id="sec-7-8-5"></a>')[0] + DOC_EN.split('<a id="sec-7-9"></a>')[1]
    german_outside_density = DOC_DE.split('<a id="sec-7-8-5"></a>')[0] + DOC_DE.split('<a id="sec-7-9"></a>')[1]
    assert "half-open" not in english_outside_density
    assert "start <= time < end" not in DOC_EN
    assert "halboffen" not in german_outside_density
    assert "start <= geplanter Start < end" not in DOC_DE


@pytest.mark.parametrize("manual", [DOC_EN, DOC_DE], ids=["en", "de"])
def test_manuals_define_correction_aware_temporal_density_coordinates(manual):
    density_section = manual.split('<a id="sec-7-8-5"></a>')[1].split('<a id="sec-7-9"></a>')[0]
    assert "`k = floor(d + c + 0.5)`" in density_section
    assert "`k - c`" in density_section
    assert "`[k - 0.5 - c, k + 0.5 - c)`" in density_section
    assert "1 dB" in density_section
    assert "Performance" in density_section
    assert "Drill-Down" in density_section


def test_bilingual_manuals_define_segment_temporal_density_and_scope():
    """Keep temporal populations and density normalization explicit."""
    assert "Chronological views preserve the actual sequence of the run" in DOC_EN
    assert "across the full selected UTC window" in DOC_EN
    assert "Bins begin at the selected start; the final interval may be shorter" in DOC_EN
    assert "intervals without evidence remain blank rather than becoming 0 dB" in DOC_EN
    assert "does not by itself mean that the data source returned no observations" in DOC_EN
    assert "fold evidence from represented dates onto the same 24-hour UTC clock" in DOC_EN
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
    assert "These are descriptive spread summaries, not confidence intervals" in DOC_EN
    assert "Temporal IQR bands require at least five contributing values" in DOC_EN
    assert "Empty bins remain missing rather than becoming synthetic zero observations" in DOC_EN
    assert "raw ΔSNR values, bin membership, counts, medians and quartiles remain unchanged" in DOC_EN
    assert "Performance successful-SNR views remain on a linear dB axis" in DOC_EN

    assert "Dies sind deskriptive Streuungsmaße und keine Konfidenzintervalle" in DOC_DE
    assert "Zeitliche IQR-Bänder erfordern mindestens fünf beitragende Werte" in DOC_DE
    assert "Leere Bins bleiben fehlend" in DOC_DE
    assert "Rohe ΔSNR-Werte, Bin-Zuordnung, Anzahlen, Mediane und Quartile bleiben unverändert" in DOC_DE
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
        "one actual ΔSNR dot per retained Joint Spot",
        "actual normalized Target SNR of each successful confirmed opportunity",
        "not untouched provider rows",
        "No bin median, IQR, density background, colorbar, full-run median",
        "Segment and full-window Selected Station Evidence remain density-based aggregated views",
        "exact `start_utc` and `end_utc`",
        "robust-z guides at 1, 2 and 3 plus the configured qualifying threshold",
        "detector guides, not confidence intervals",
        "crossing one line alone cannot qualify a candidate",
        "Identical `*` markers identify every Joint Spot in the current window that individually meets both configured departure and robust-z requirements as part of a reported candidate",
        "A muted **Focused episode** band identifies the selected reported episode",
        "half one native evidence-unit width added at each end",
        "neither a confidence interval nor a measurement of physical-event duration",
        "other starred Joint Spots may have been assessed against different baselines and robust spreads",
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
        "einen tatsächlichen ΔSNR-Punkt je beibehaltenem Joint Spot",
        "tatsächliche normierte Target-SNR jeder erfolgreichen bestätigten Gelegenheit",
        "keine unveränderten Provider-Zeilen",
        "Binmedian, IQR, Dichtehintergrund, Farbskala, Median des vollständigen Laufs",
        "Segmentansicht und Evidenz der ausgewählten Station über das vollständige Fenster bleiben dichtebasierte aggregierte Ansichten",
        "exaktem `start_utc` und `end_utc`",
        "robuste-z-Hilfslinien bei 1, 2 und 3 sowie an der konfigurierten Qualifikationsschwelle",
        "Detektorhilfen und keine Konfidenzintervalle",
        "Überschreiten einer einzelnen Linie kann keinen Kandidaten allein qualifizieren",
        "Identische `*`-Marker kennzeichnen jeden Joint Spot im aktuellen Fenster, der als Teil eines berichteten Kandidaten einzeln sowohl die konfigurierte Abweichungsschwelle als auch das robuste-z-Kriterium erfüllt",
        "Ein dezentes Band **Fokussierte Episode** kennzeichnet die ausgewählte berichtete Episode",
        "an beiden Enden um eine halbe Breite der nativen Evidenzeinheit erweitert",
        "weder ein Konfidenzintervall noch eine Messung der Dauer eines physischen Ereignisses",
        "Andere mit Stern markierte Joint Spots können gegen andere Baselines und robuste Streuungen geprüft worden sein",
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
        "The greatest departure in magnitude from the baseline among retained Joint Spots, retaining its sign",
        "This report/export value is distinct from the all-path temporal `*`",
        "among those that individually qualify",
        "An unsupported or nonqualifying episode peak cannot supply that marker",
        "The all-path temporal marker is selected only from these strong anchors",
        "the individually qualifying native unit with the greatest absolute residual supplies the `*`",
        "Marker selection is separate from **Largest single-cycle departure**",
        "remains the true greatest-absolute retained residual in each path event for the report and export",
    ):
        assert phrase in DOC_EN

    for phrase in (
        "Die betragsmäßig größte Abweichung von der Baseline unter den beibehaltenen Joint Spots, mit ihrem Vorzeichen",
        "Diese Berichts-/Exportgröße unterscheidet sich vom `*` im Zeitplot aller Funkwege",
        "unter den einzeln qualifizierenden Joint Spots",
        "Eine ungestützte oder nicht qualifizierende Episodenspitze kann diesen Marker nicht liefern",
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

    assert "Segment color shows the median of the qualifying transmitters' median ΔSNR values; each transmitter has equal weight" in DOC_EN
    assert "Positive $D_{i,c}$ favors the Target; negative favors the Reference" in DOC_EN
    assert "Segmentfarbe zeigt den Median der ΔSNR-Mediane der berücksichtigten Sender; jeder Sender hat dasselbe Gewicht" in DOC_DE
    assert "Positives $D_{i,c}$ spricht für das Target, negatives für die Referenz" in DOC_DE


def test_bilingual_manuals_define_saved_inspector_selection_contracts():
    """Ordinary selections stay singular; enabled Benchmark outliers permit multiple paths."""
    english_controls = DOC_EN.split('<a id="sec-5-5"></a>', 1)[1].split(
        '<a id="sec-6"></a>', 1
    )[0]
    german_controls = DOC_DE.split('<a id="sec-5-5"></a>', 1)[1].split(
        '<a id="sec-6"></a>', 1
    )[0]

    assert "Separately for Performance and Benchmark" in english_controls
    assert "Exact `callsign + locator` identities: normally at most one per result type" in english_controls
    assert "multiple Benchmark identities when outlier reporting is enabled" in english_controls
    assert "| No |" in english_controls
    assert "one exact peer identity" in DOC_EN
    assert "not matching, eligibility or aggregation upstream" in DOC_EN

    assert "getrennt für Performance und Benchmark" in german_controls
    assert "exakte Identitäten aus `Rufzeichen + Locator`: normalerweise höchstens eine je Ergebnistyp" in german_controls
    assert "mehrere Benchmark-Identitäten bei eingeschalteter Ausreißererkennung" in german_controls
    assert "| Nein |" in german_controls
    assert "genau eine Peer-Identität" in DOC_DE
    assert "nicht die vorgelagerte Zuordnung, Zulässigkeit oder Aggregation" in DOC_DE


def test_bilingual_manuals_document_only_absolute_utc_analysis_windows():
    """Describe fixed minute-precision boundaries without the retired rolling mode."""
    assert "fixed 24-hour window ending at the current UTC minute" in DOC_EN
    assert "**Start Date/Time (UTC)** and **End Date/Time (UTC)**" in DOC_EN
    assert "Dates begin in 2008; one run is limited to 31 elapsed days" in DOC_EN
    assert "Entered times use minute precision and are preserved without rounding to 15-minute boundaries" in DOC_EN

    assert "festes 24-Stunden-Fenster bis zur aktuellen UTC-Minute" in DOC_DE
    assert "**Startdatum/-zeit (UTC)** und **Enddatum/-zeit (UTC)**" in DOC_DE
    assert "Datumswerte beginnen im Jahr 2008" in DOC_DE
    assert "Eingegebene Zeiten bleiben mit Minutengenauigkeit erhalten, ohne Rundung auf 15-Minuten-Grenzen" in DOC_DE
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


@pytest.mark.parametrize(
    ("language", "manual", "control", "semantic_fragments", "telemetry_boundary"),
    [
        (
            "en", DOC_EN, "**Exclude Special Callsigns Q, 0, 1**",
            (
                "remote peer callsigns beginning with Q, 0",
                "transmitters in RX analyses and receivers in TX analyses",
                "Target and Reference stations",
                "Reference Neighborhood reference contributors",
                "remain eligible under this filter",
            ),
            "The prefix rule does not establish whether a station carries telemetry.",
        ),
        (
            "de", DOC_DE, "**Spezial-Rufzeichen Q, 0, 1 ausschließen**",
            (
                "entfernte Peer-Rufzeichen",
                "mit Q, 0 oder 1 beginnen",
                "sendende Peers in RX-Analysen und empfangende Peers in TX-Analysen",
                "Target- und Referenzstationen",
                "zur Referenz der lokalen Nachbarschaft beitragen",
                "bleiben von diesem Filter unberührt",
            ),
            "Die Präfixregel stellt nicht fest, ob eine Station Telemetrie überträgt.",
        ),
    ],
    ids=("en", "de"),
)
def test_special_callsign_guidance_preserves_remote_peer_boundary_across_surfaces(
    language, manual, control, semantic_fragments, telemetry_boundary,
):
    """Keep concise field help and fuller guidance on the same peer boundary."""
    manual_row = next(line for line in manual.splitlines() if line.startswith(f"| {control} |"))
    for fragment in semantic_fragments:
        assert fragment in manual_row.replace("`", "")

    tooltip = T[language]["tt_exclude_special"].replace("**", "")
    guided_body = re.sub(
        r"</?strong\b[^>]*>", "",
        GUIDED_INPUTS[language]["messages"]["station_population_body"],
    )
    if language == "en":
        guided_prefix = "remote callsigns beginning with Q, 0 or 1"
        tooltip_fragments = (
            "Exclude remote callsigns starting with Q, 0 or 1",
            "typically used for balloon telemetry",
            "Target and Reference stations",
            "including neighborhood contributors",
            "remain eligible",
        )
        guided_roles = (
            "transmitters your Target listens for in RX analyses",
            "receivers that listen for your Target in TX analyses",
        )
    else:
        guided_prefix = "entfernte Rufzeichen aus, die mit Q, 0 oder 1 beginnen"
        tooltip_fragments = (
            "Schließe entfernte Rufzeichen aus, die mit Q, 0 oder 1 beginnen",
            "typischerweise für Ballontelemetrie verwendet",
            "Target- und Referenzstationen",
            "einschließlich beitragender Nachbarschaftsstationen",
            "bleiben zulässig",
        )
        guided_roles = (
            "bei RX-Analysen die Sender, auf deren Signale dein Target hört",
            "bei TX-Analysen die Empfänger, die auf die Signale deines Targets hören",
        )

    for fragment in tooltip_fragments:
        assert fragment in tooltip
    assert guided_prefix in guided_body
    for fragment in guided_roles:
        assert fragment in guided_body

    # Guided defines the RX/TX remote roles; concise shared field help retains
    # Target/Reference eligibility, including local Reference contributors.
    for fragment in semantic_fragments[-3:]:
        assert fragment in guided_body.replace("`", "")
    assert telemetry_boundary in manual_row
    assert "{special}" in GUIDED_INPUTS[language]["messages"]["review_population_value"]
    assert "{moving}" in GUIDED_INPUTS[language]["messages"]["review_population_value"]


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
        "`Reference Setup/Station`",
        "`Reference Neighborhood`",
    ):
        assert benchmark_design in DOC_EN
    assert "first panel, **`Question`**" in DOC_EN
    assert "second panel, **`Target and measurement window`**" in DOC_EN
    assert "omits the **`Benchmark design`** panel entirely" in DOC_EN
    assert "Guided provides concise help for each Reference choice and separate help" in DOC_EN
    assert "help beside **Benchmark design** explains both Reference choices regardless of the current selection" in DOC_EN
    assert "Reference callsign and Neighborhood Radius fields have their own help for entry guidance" in DOC_EN
    assert "Reference Neighborhood uses the Local Median described in the choice help" in DOC_EN

    for question in (
        "RX Performance",
        "TX Performance",
        "RX-Benchmark",
        "TX-Benchmark",
    ):
        assert question in DOC_DE
    for benchmark_design in (
        "`Referenzaufbau/-station`",
        "`Referenznachbarschaft`",
    ):
        assert benchmark_design in DOC_DE
    assert "Im ersten Bereich **`Frage`**" in DOC_DE
    assert "Der zweite Bereich **`Target und Messzeitraum`**" in DOC_DE
    assert "entfällt der Bereich **`Benchmark-Design`** vollständig" in DOC_DE
    assert "Die geführte Eingabe bietet zu jeder Referenzoption eine kurze Hilfe und getrennte Hilfen" in DOC_DE
    assert "Hilfe neben **Benchmark-Design** beide Referenzoptionen unabhängig von der aktuellen Auswahl" in DOC_DE
    assert "Referenz-Rufzeichen und Nachbarschaftsradius haben eigene Hilfen zur Eingabe" in DOC_DE
    assert "Die Referenznachbarschaft verwendet den in der Auswahlhilfe beschriebenen lokalen Median" in DOC_DE


def test_bilingual_manuals_document_shared_review_and_open_panel_contract():
    """Keep action placement and run-time expansion behavior explicit."""
    assert "same terminal configuration summary" in DOC_EN
    assert "**`Review — ready to run ✓`**" in DOC_EN
    assert "places `Run RX Analysis` / `Run TX Analysis` and `Save Config`" in DOC_EN
    assert "Review panel remains open while the run starts" in DOC_EN
    assert "run-status panel remains open when it reaches **`Complete`**" in DOC_EN
    assert "Classic does not automatically collapse any configuration panel" in DOC_EN
    assert "ordinary or demo analysis starts" in DOC_EN

    assert "derselben abschließenden Konfigurationsübersicht" in DOC_DE
    assert "**`Prüfung — startbereit ✓`**" in DOC_DE
    assert "`RX-Analyse starten` / `TX-Analyse starten` und `Konfig speichern`" in DOC_DE
    assert "Der Prüfbereich bleibt beim Start des Laufs" in DOC_DE
    assert "Laufstatus bleibt bei **`Complete`** geöffnet" in DOC_DE
    assert "kein Konfigurationsbereich automatisch geschlossen" in DOC_DE
    assert "gewöhnlichen Analyse oder einer Demo" in DOC_DE


def test_bilingual_manuals_document_always_visible_scope_and_classic_order():
    """Describe one visible shared panel without changing default semantics."""
    assert "**`Filters, scope and evidence`**" in DOC_EN
    assert "Optional filters, analysis scope, and evidence requirements" not in DOC_EN
    assert "Guided always shows the applicable fields inside that step" in DOC_EN
    assert "there is no separate preset-choice gate" in DOC_EN
    assert "loaded configurations and demos populate the same visible fields" in DOC_EN
    assert "The displayed filter, scope and evidence settings apply even if you leave this panel unchanged" in DOC_EN
    assert "Performance has four Classic panels and Benchmark has five" in DOC_EN

    assert "**`Filter, Analyseumfang und Evidenz`**" in DOC_DE
    assert "Optionale Filter, Analyseumfang und Evidenzanforderungen" not in DOC_DE
    assert "zeigt die geführte Eingabe stets die zutreffenden Felder" in DOC_DE
    assert "eine getrennte vorgeschaltete Auswahl entfällt" in DOC_DE
    assert "geladene Konfigurationen und Demos" in DOC_DE
    assert "Die angezeigten Einstellungen für Filter, Analyseumfang und Evidenz gelten auch dann, wenn du diesen Bereich unverändert lässt" in DOC_DE
    assert "Performance besitzt damit vier und Benchmark fünf klassische Bereiche" in DOC_DE


def test_bilingual_manuals_distinguish_empty_result_diagnostics():
    """Separate source, filter, station, and segment states from requirements."""
    for phrase in (
        "No exact Target/source evidence was returned",
        "Source evidence was returned, but filters or scope retained none",
        "Performance identities remain, but no station meets the confirmed-opportunity requirement",
        "Performance stations qualify, but no map segment meets its station requirement",
    ):
        assert phrase in DOC_EN
    assert "highest observed: `3` confirmed opportunities" in DOC_EN
    assert "required: at least `5` per station" in DOC_EN
    assert "A configured minimum is never presented as an observed count" in DOC_EN
    assert "Target-only successes are confirmed opportunities and contribute to station thresholds" in DOC_EN
    assert "No qualifying Benchmark result remains" in DOC_EN
    assert "does not invent observed Benchmark maxima" in DOC_EN

    for phrase in (
        "Keine exakte Target-/Quellenevidenz wurde geliefert",
        "Quellenevidenz wurde geliefert, aber Filter oder Umfang behielten nichts bei",
        "Performance-Identitäten bleiben erhalten, aber keine Station erfüllt die Anforderung an bestätigte Gelegenheiten",
        "Performance-Stationen qualifizieren sich, aber kein Kartensegment erfüllt seine Stationsanforderung",
    ):
        assert phrase in DOC_DE
    assert "höchster beobachteter Wert: `3` bestätigte Gelegenheiten" in DOC_DE
    assert "erforderlich: mindestens `5` pro Station" in DOC_DE
    assert "Ein konfiguriertes Minimum wird nie als beobachtete Anzahl ausgegeben" in DOC_DE
    assert "Target-only-Erfolge bestätigte Gelegenheiten und zählen für die Stationsschwellen" in DOC_DE
    assert "Kein qualifizierendes Benchmark-Ergebnis bleibt erhalten" in DOC_DE
    assert "keine beobachteten Benchmark-Maxima" in DOC_DE


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
    # A wide viewport can still have narrow weighted table columns. All
    # overview labels must wrap inside their own cells without a media query.
    for label_class in ("analysis-choice-single", "analysis-family", "analysis-variant"):
        selector = (
            '.st-key-documentation_body '
            'table[data-documentation-column-layout="section-0-1"] '
            f'.{label_class}'
        )
        label_rule = re.search(re.escape(selector) + r"\s*\{([^{}]*)\}", stylesheet)
        assert label_rule is not None
        assert label_rule.start() < stylesheet.index("@media (max-width: 800px)")
        assert "white-space: normal !important" in label_rule.group(1)
        assert "overflow-wrap: anywhere !important" in label_rule.group(1)
        assert "white-space: nowrap" not in label_rule.group(1)
    assert "tbody td:nth-child(1)" in stylesheet
    assert "tbody td:nth-child(2)" in stylesheet
    assert "@media (max-width: 800px)" in stylesheet
    assert ".st-key-documentation_body .stMarkdown strong.defined-term" in stylesheet
    assert ".st-key-guided_input_flow .stMarkdown strong.defined-term" in stylesheet
    assert ".st-key-documentation_body .stMarkdown p" in stylesheet
    assert "font-family: Arial, Helvetica, sans-serif !important;" in stylesheet
    assert ".st-key-documentation_body a[id]:not(.header-anchor)" in stylesheet
    assert "scroll-margin-top: 5rem" in stylesheet
    assert "strong:first-child:not(.defined-term)" in stylesheet
    # Manual emphasis must neither leak into inputs nor enlarge body text.
    bold_paragraph_rules = re.findall(
        r"(?m)^\s*([^\n{}]*\.stMarkdown p:has\(> strong[^\n{}]*)\s*\{([^{}]*)\}",
        stylesheet,
    )
    assert bold_paragraph_rules
    assert all(
        selector.startswith(".st-key-documentation_body ")
        for selector, _rules in bold_paragraph_rules
    )
    assert all(
        not re.search(r"\bfont-size\s*:", rules)
        for _selector, rules in bold_paragraph_rules
    )
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
        "sec-simultaneous-tx-setup",
        "sec-reference-snr-calibration",
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
    credit_markdowns = [
        kwargs
        for body, kwargs in fake_st.markdowns
        if labels["dev_credit"] in body
    ]
    assert len(credit_markdowns) == 1
    assert credit_markdowns[0]["unsafe_allow_html"] is True
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


def test_bilingual_report_templates_distinguish_mean_station_rates_from_pooled_opportunities():
    """A station-balanced percentage must not be described as a pooled fraction."""
    for manual, terms in (
        (DOC_EN, ("average of the qualifying stations’ individual rates", "success fraction across all their confirmed opportunities")),
        (DOC_DE, ("Mittelwert der individuellen Raten der qualifizierenden Stationen", "Erfolgsanteil über alle ihre bestätigten Gelegenheiten")),
    ):
        reporting = manual.split('<a id="sec-4-3"></a>', 1)[1].split('<a id="sec-4-4"></a>', 1)[0]
        for term in terms:
            assert term in reporting


def test_bilingual_delay_guidance_requires_actual_availability_not_a_guaranteed_wait():
    """The estimate and preflight criterion describe the same upstream limitation."""
    for manual, estimate, limitation, preflight in (
        (DOC_EN, "**five minutes**", "not a completeness guarantee", "actual data availability, not a fixed waiting period"),
        (DOC_DE, "**fünf Minuten**", "keine Vollständigkeitsgarantie", "Daten tatsächlich vorliegen, nicht eine feste Wartezeit"),
    ):
        upstream = manual.split('<a id="sec-6-6"></a>', 1)[1].split('<a id="part-iii"></a>', 1)[0]
        setup = manual.split('<a id="sec-simultaneous-tx-setup-4"></a>', 1)[1].split('<a id="sec-simultaneous-tx-setup-5"></a>', 1)[0]
        assert estimate in upstream
        assert limitation in upstream
        assert preflight in setup
