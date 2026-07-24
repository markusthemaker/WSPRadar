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
    assert '<strong class="defined-term">Success</strong>' in DOC_EN


def test_english_playbooks_define_success_evidence_and_tx_ab_timing():
    """Operator playbooks must retain the clarified Success and TX A/B guidance."""
    assert '<strong class="defined-term">qualifying evidence</strong>' in DOC_EN
    assert (
        "independently confirmed WSPR-network opportunities represented in the selected evidence"
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


def test_results_chapter_uses_compact_ladder_and_consecutive_sections():
    """Chapter 2 must avoid repeating run-identity guidance before interpretation."""
    assert "#### 2.1 Confirm the run identity" not in DOC_EN
    assert "**Map -> Stations and Spots -> Segment Inspector -> Station Insights -> Drill-Down**" in DOC_EN
    assert "#### 2.1 Read a Success result" in DOC_EN
    assert "#### 2.2 Read a Compare result" in DOC_EN
    assert "#### 2.8 Worked Compare example" in DOC_EN

    rx_explanation = DOC_EN.index("* In simultaneous RX Compare")
    tx_explanation = DOC_EN.index("* In same-cycle TX Compare")
    sequential_explanation = DOC_EN.index(
        "* Sequential TX Hardware A/B uses deterministic scheduled pairs"
    )
    assert rx_explanation < tx_explanation < sequential_explanation


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
    assert "`Time aggregation bin size:` appears under `Temporal Evidence`" in DOC_EN

    assert "genau dieselben Evidenzzeilen auf Beobachtungsebene" in DOC_DE
    assert "mindestens zwei verschiedenen UTC-Tagen" in DOC_DE
    assert "D_{relative} = 100" in DOC_DE
    assert "Die gewählte Ansicht wird in `.config` gespeichert" in DOC_DE
    assert "`Zeitliche Aggregationsbreite:` steht unter `Zeitliche Evidenz`" in DOC_DE

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
    assert "The selected-station plots use the observation-level weighting" in DOC_EN
    assert "Die weißen verbundenen Marker bleiben eine eigene Statistik" in DOC_DE
    assert "Gewichtungs- und Darstellungsregeln auf Beobachtungsebene" in DOC_DE
    for documentation_text in (DOC_EN, DOC_DE):
        assert "figure_segment_temporal_evidence.png" in documentation_text


def test_bilingual_manuals_define_saved_inspector_scope_and_all_stations_intent():
    """Saved result-view guidance must cover scope, zero targets, and dynamic all."""
    assert "Compare and Success selections are saved independently" in DOC_EN
    assert "Its setting is saved for Success" in DOC_EN
    assert "stores an all-stations intent instead of enumerating the current table" in DOC_EN
    assert "with a moving `Last X Hours` window" in DOC_EN

    assert "für Compare und Success getrennt gespeichert" in DOC_DE
    assert "Die Einstellung wird für Success gespeichert" in DOC_DE
    assert "speichert die Konfiguration diese Absicht" in DOC_DE
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
