import base64
from html import unescape
import io
import re

import pytest

from docs import pdf_generator
from docs.doc_de import DOC_DE
from docs.doc_en import DOC_EN
from i18n import T


class _Context:
    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc_value, _traceback):
        return False


class _FakeStreamlit:
    def __init__(self, *, prepare_clicked=False, session_state=None):
        self.prepare_clicked = prepare_clicked
        self.session_state = session_state if session_state is not None else {}
        self.buttons = []
        self.downloads = []
        self.spinners = []

    def button(self, label, **kwargs):
        self.buttons.append((label, kwargs))
        if kwargs.get("disabled"):
            return False
        clicked = self.prepare_clicked
        self.prepare_clicked = False
        return clicked

    def download_button(self, label, **kwargs):
        self.downloads.append((label, kwargs))

    def spinner(self, label):
        self.spinners.append(label)
        return _Context()


def _ready_key(lang="en", version="v0.95"):
    return f"{pdf_generator.DOCUMENTATION_PDF_READY_KEY_PREFIX}:{lang}:{version}"


def test_pdf_math_replacements_cover_both_manuals_with_font_safe_delta():
    localized_manuals = (
        ("en", DOC_EN),
        ("de", DOC_DE),
    )
    for language, manual in localized_manuals:
        translations = T[language]
        rendered = pdf_generator._replace_pdf_math(manual, translations)
        source_block_formulas = re.findall(r"\$\$(.*?)\$\$", manual, flags=re.DOTALL)
        source_inline_formulas = re.findall(
            r"(?<!\$)\$[^$\r\n]+\$(?!\$)",
            manual,
        )

        assert len(source_block_formulas) == 29
        formal_manual = manual.split('<a id="sec-7-11"></a>', 1)[1].split(
            '<a id="sec-8"></a>', 1
        )[0]
        assert len(
            re.findall(r"\$\$(.*?)\$\$", formal_manual, flags=re.DOTALL)
        ) == 13
        assert rendered.count('<p class="formula"><b>') == len(
            source_block_formulas
        )
        assert rendered.count('<span class="inline-formula">') == len(
            source_inline_formulas
        )
        rendered_formula_bodies = re.findall(
            r'<p class="formula"><b>(.*?)</b></p>', rendered, flags=re.DOTALL
        )
        assert all(
            language_bound_word not in formula_body
            for formula_body in rendered_formula_bodies
            for language_bound_word in (" when ", " union ", " minutes")
        )
        assert "$$" not in rendered
        assert not re.search(r"(?<!\$)\$[^$\r\n]+\$(?!\$)", rendered)
        assert "&Delta;" not in rendered
        expected_formula_fragments = (
            "n<sub>i</sub> = sum<sub>c</sub> O<sub>i,c</sub>",
            "r<sub>i</sub> = 100% &times; h<sub>i</sub> / n<sub>i</sub>",
            "R<sub>station</sub>(g) = (1 / |I<sub>g</sub>|)",
            "R<sub>opportunity</sub>(g) = 100% &times;",
            "Reach(g) = 100% &times; count(i in I<sub>g</sub>",
            "SNR<sub>norm</sub> = SNR<sub>measured</sub>",
            "SNR<sub>R,corr</sub> = SNR<sub>R</sub> + C<sub>R</sub>",
            f"{translations['pdf_formula_delta_snr']}<sub>i,c</sub>",
            "m<sub>i</sub> = median<sub>c</sub>(D<sub>i,c</sub>)",
            "M<sub>g</sub> = median(i in I<sub>g</sub>)(m<sub>i</sub>)",
            "N<sub>i,b</sub> = T<sub>i,b</sub> + J<sub>i,b</sub>",
            "v<sub>T,i,b</sub> = T<sub>i,b</sub> / N<sub>i,b</sub>",
            "v<sub>J,i,b</sub> = J<sub>i,b</sub> / N<sub>i,b</sub>",
            "v<sub>R,i,b</sub> = R<sub>i,b</sub> / N<sub>i,b</sub>",
            "JES<sub>station</sub>(b) = 100% &times; mean<sub>i</sub>",
            "JES<sub>outcome</sub>(b) = 100% &times;",
            "A<sub>i,c</sub> = SNR<sub>i,c</sub> - median<sub>c&apos;</sub>",
            "D<sub>relative</sub> = 100 &times; n<sub>cell</sub>",
            "B<sub>pre</sub> = median(&#8492;<sub>pre</sub>)",
            "B = (B<sub>pre</sub> + B<sub>post</sub>) / 2",
            "V = {x - B<sub>pre</sub>: x &isin; &#8492;<sub>pre</sub>}",
            "S<sub>robust</sub> = MAD(V) [MAD(V) &gt; 0]",
            "r<sub>i,u</sub> = D<sub>i,u</sub> - B",
            "z<sub>i,u</sub> = 0.6745 &times; r<sub>i,u</sub>",
            "G<sub>i</sub> = min(45, max(15, 1.5 C<sub>i</sub>)) min",
            "W<sup>P</sup><sub>i</sub> = max(60, 2 C<sub>i</sub>) min",
            "F = min(1 dB, D<sub>min</sub>)",
            "r<sup>P</sup><sub>i,u</sub> = D<sub>i,u</sub>",
            "W<sup>B</sup><sub>i</sub> = max(10, C<sub>i</sub>) min",
            "m<sub>E</sub> = median(u &isin; E)(r<sub>i,u</sub>)",
            "z<sub>E</sub> = 0.6745 &times; m<sub>E</sub>",
            "agree(E) = |{u &isin; E: sign(r<sub>i,u</sub>)",
            "|m<sub>E</sub>| &ge; D<sub>min</sub>",
            "|z<sub>E</sub>| &ge; Z<sub>min</sub>",
            "sign(r<sub>i,u</sub>) = sign(m<sub>E</sub>)",
        )
        for expected_formula_fragment in expected_formula_fragments:
            assert expected_formula_fragment in rendered
        for expected_inline_formula_fragment in (
            "A<sub>c</sub> = 1",
            "S<sub>i,c</sub> &le; O<sub>i,c</sub>",
            "SNR<sub>R,corr,i,c</sub>",
            "M &plusmn; 60",
            "n<sub>cell</sub>",
            "D<sub>i,u</sub>",
            "D&#771;<sub>i,k</sub>",
            "B<sup>P</sup><sub>i,k</sub>",
            "r<sup>P</sup><sub>i,u</sub>",
            "V, S<sub>robust</sub>",
            "W<sup>P</sup><sub>i</sub>",
            "z<sub>E</sub>",
            "agree(E)",
            "H<sub>max</sub>",
        ):
            assert expected_inline_formula_fragment in rendered
        for unsupported_latex in (
            r"\(",
            r"\)",
            r"\frac",
            r"\ge",
            r"\left",
            r"\operatorname",
            r"\qquad",
            r"\right",
            r"\sum",
            r"\begin",
            r"\end",
            r"\land",
            r"\mathrm",
            r"\geq",
            r"\mathcal",
            r"\widetilde",
            r"\cup",
        ):
            assert unsupported_latex not in rendered


def test_generated_pdf_footer_uses_localized_page_label(monkeypatch):
    """Use the catalog page label rather than branching on the PDF language."""
    from PIL import Image
    from xhtml2pdf import pisa

    rendered_templates = []

    class _PdfStatus:
        err = False

    def capture_pdf_template(source, dest):
        rendered_templates.append(source.read())
        dest.write(b"pdf")
        return _PdfStatus()

    monkeypatch.setattr(pdf_generator, "get_docs", lambda _lang: "Manual")
    monkeypatch.setattr(pisa, "CreatePDF", capture_pdf_template)

    logo_buffer = io.BytesIO()
    Image.new("RGBA", (1, 1), (255, 255, 255, 255)).save(
        logo_buffer,
        format="PNG",
    )
    logo_b64 = base64.b64encode(logo_buffer.getvalue()).decode("ascii")

    for language in ("en", "de"):
        assert pdf_generator._generate_pdf_doc(
            language,
            logo_b64,
            "test",
        ) == b"pdf"
        assert (
            f"WSPRadar test - {T[language]['pdf_page_label']} <pdf:pagenumber>"
            in rendered_templates[-1]
        )

    conclusion_style_match = re.search(
        r"blockquote\.evidence-conclusion\s*\{(?P<rules>[^}]*)\}",
        rendered_templates[-1],
    )
    assert conclusion_style_match is not None
    conclusion_rules = conclusion_style_match.group("rules")
    assert re.search(r"background(?:-color)?\s*:", conclusion_rules)
    assert re.search(r"border-left\s*:", conclusion_rules)
    assert re.search(r"(?<!-)color\s*:", conclusion_rules)
    assert re.search(r"page-break-inside\s*:\s*avoid", conclusion_rules)

    conclusion_label_style_match = re.search(
        r"p\.evidence-conclusion-label\s*\{(?P<rules>[^}]*)\}",
        rendered_templates[-1],
    )
    assert conclusion_label_style_match is not None
    conclusion_label_rules = conclusion_label_style_match.group("rules")
    assert re.search(r"page-break-after\s*:\s*avoid", conclusion_label_rules)
    assert re.search(r"-pdf-keep-with-next\s*:\s*true", conclusion_label_rules)


@pytest.mark.parametrize(
    ("language", "accessible_label"),
    [
        ("en", "DL1MKS on QRZ.com (opens in a new tab)"),
        ("de", "DL1MKS auf QRZ.com (öffnet in einem neuen Tab)"),
    ],
)
def test_pdf_credit_recolors_qrz_link_and_icon_for_white_page(
    monkeypatch,
    language,
    accessible_label,
):
    """Keep the shared QRZ credit legible in the generated PDF header."""
    from PIL import Image
    from xhtml2pdf import pisa

    rendered_templates = []

    class _PdfStatus:
        err = False

    def capture_pdf_template(source, dest):
        rendered_templates.append(source.read())
        dest.write(b"pdf")
        return _PdfStatus()

    monkeypatch.setattr(pdf_generator, "get_docs", lambda _lang: "Manual")
    monkeypatch.setattr(pisa, "CreatePDF", capture_pdf_template)

    logo_buffer = io.BytesIO()
    Image.new("RGBA", (1, 1), (255, 255, 255, 255)).save(
        logo_buffer,
        format="PNG",
    )
    logo_b64 = base64.b64encode(logo_buffer.getvalue()).decode("ascii")

    assert pdf_generator._generate_pdf_doc(
        language,
        logo_b64,
        "test",
    ) == b"pdf"
    rendered_template = rendered_templates[0]
    credit_start = rendered_template.index("Developed by Dr. Markus Brosch")
    credit_end = rendered_template.index("</div>", credit_start)
    rendered_credit = rendered_template[credit_start:credit_end]

    assert "href='https://www.qrz.com/db/DL1MKS'" in rendered_credit
    assert "target='_blank' rel='noopener noreferrer'" in rendered_credit
    assert f"aria-label='{accessible_label}'" in rendered_credit
    assert ">DL1MKS<span" in rendered_credit
    assert "&#8599;" in rendered_credit
    assert rendered_credit.count("color:#0a318f") == 2
    assert "#39ff14" not in rendered_credit


def test_generated_pdf_preserves_clickable_qrz_credit_link(monkeypatch):
    """Expose the callsign profile as a real external PDF link annotation."""
    from PIL import Image
    from pypdf import PdfReader

    monkeypatch.setattr(pdf_generator, "get_docs", lambda _lang: "Manual")
    logo_buffer = io.BytesIO()
    Image.new("RGBA", (1, 1), (255, 255, 255, 255)).save(
        logo_buffer,
        format="PNG",
    )
    logo_b64 = base64.b64encode(logo_buffer.getvalue()).decode("ascii")

    pdf_bytes = pdf_generator._generate_pdf_doc("en", logo_b64, "test")

    assert pdf_bytes is not None
    reader = PdfReader(io.BytesIO(pdf_bytes))
    extracted_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    external_uris = []
    for page in reader.pages:
        for annotation_reference in page.get("/Annots", []):
            annotation = annotation_reference.get_object()
            action_reference = annotation.get("/A")
            if action_reference is None:
                continue
            action = action_reference.get_object()
            external_uri = action.get("/URI")
            if external_uri is not None:
                external_uris.append(str(external_uri))

    assert "Developed by Dr. Markus Brosch" in extracted_text
    assert "DL1MKS↗" in extracted_text
    assert "https://www.qrz.com/db/DL1MKS" in external_uris


def test_pdf_markdown_extensions_preserve_fenced_code_blocks():
    import markdown

    rendered = markdown.markdown(
        "```text\nconfig/\n  run_metadata.json\n```",
        extensions=pdf_generator.PDF_MARKDOWN_EXTENSIONS,
    )

    assert rendered.startswith("<pre><code")
    assert "config/\n  run_metadata.json" in rendered


def test_pdf_preserves_section_zero_analysis_hierarchy_markup():
    """Keep each Benchmark family above its decision in the printable table."""
    table_start = DOC_EN.index("| Analysis | Question | Practical examples |")
    table_end = DOC_EN.index("\n\n", table_start)

    rendered = pdf_generator._render_pdf_html(
        DOC_EN[table_start:table_end],
        T["en"],
    )

    assert (
        '<table class="pdf-intro-analysis-table" width="100%">'
        in rendered
    )
    for header, width_percent in zip(
        ("Analysis", "Question", "Practical examples"),
        pdf_generator.PDF_INTRO_ANALYSIS_COLUMN_WIDTHS_PERCENT,
    ):
        assert f'<th style="width: {width_percent}%">{header}</th>' in rendered
    assert rendered.count('class="analysis-choice"') == 5
    assert rendered.count('class="analysis-family"') == 5
    assert rendered.count('class="analysis-variant"') == 5
    assert (
        '<span class="analysis-family">RX/TX Benchmark</span><br>'
        '<strong class="analysis-variant">Reference Station / Buddy Test</strong>'
        in rendered
    )


def test_pdf_preprocessing_makes_fenced_code_layout_explicit():
    """xhtml2pdf must receive explicit breaks and indentation in code blocks."""
    rendered = pdf_generator._render_pdf_html(
        "```text\nconfig/\n  run_metadata.json\n```",
        T["en"],
    )

    assert (
        '<pre><code class="language-text">config/<br/>'
        "&#160;&#160;run_metadata.json</code></pre>"
    ) in rendered


def test_pdf_preprocessing_preserves_defined_term_markup():
    """First-definition emphasis must survive Markdown-to-PDF preprocessing."""
    rendered = pdf_generator._render_pdf_html(DOC_EN, T["en"])

    assert '<strong class="defined-term">Target</strong>' in rendered
    assert '<strong class="defined-term">Reference</strong>' in rendered
    defined_evidence_path = (
        '<strong class="defined-term">Map → Segment Inspector → '
        'Performance/Benchmark Evidence → Temporal Evidence → Station Insights '
        '→ Selected Station Evidence → Drill-Down</strong>'
    )
    assert rendered.count(defined_evidence_path) == 2


def test_pdf_preprocessing_preserves_english_section_two_conclusion_callouts():
    """Retain the scoped conclusion class for print-specific contrast styling."""
    rendered = pdf_generator._render_pdf_html(DOC_EN, T["en"])

    assert rendered.count('<blockquote class="evidence-conclusion">') == 11
    assert rendered.count('<p class="evidence-conclusion-label">') == 2


def test_pdf_preprocessing_keeps_em_dashes_separated_from_words():
    """Preserve readable punctuation spacing in both localized PDF manuals."""
    for language, manual in (("en", DOC_EN), ("de", DOC_DE)):
        rendered = pdf_generator._render_pdf_html(manual, T[language])
        visible_text = unescape(re.sub(r"<[^>]+>", "", rendered))

        assert " — " in visible_text
        assert re.search(r"(?<!\s)—|—(?!\s)", visible_text) is None


def test_generated_pdf_preserves_spaced_em_dashes_in_prose_and_ui_labels(
    monkeypatch,
):
    """Embed Unicode fonts for prose, UI labels, and scientific symbols."""
    from PIL import Image
    from pypdf import PdfReader

    compact_manual = (
        "Plain prose — remains separated.\n\n"
        "`Performance — no Reference`\n\n"
        "Delta marker ΔSNR; inequalities `1 ≤ 2` and `2 ≥ 1`."
    )
    monkeypatch.setattr(
        pdf_generator,
        "get_docs",
        lambda _language: compact_manual,
    )
    logo_buffer = io.BytesIO()
    Image.new("RGBA", (1, 1), (255, 255, 255, 255)).save(
        logo_buffer,
        format="PNG",
    )
    logo_b64 = base64.b64encode(logo_buffer.getvalue()).decode("ascii")

    pdf_bytes = pdf_generator._generate_pdf_doc("en", logo_b64, "test")

    assert pdf_bytes is not None
    reader = PdfReader(io.BytesIO(pdf_bytes))
    extracted_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    assert "Plain prose — remains separated." in extracted_text
    assert "Performance — no Reference" in extracted_text
    assert "ΔSNR" in extracted_text
    assert "1 ≤ 2" in extracted_text
    assert "2 ≥ 1" in extracted_text

    embedded_base_fonts = set()
    for page in reader.pages:
        font_resources = page["/Resources"].get("/Font", {})
        for font_reference in font_resources.values():
            font = font_reference.get_object()
            font_descriptor = font.get("/FontDescriptor")
            if font_descriptor is not None:
                font_descriptor = font_descriptor.get_object()
                if font_descriptor.get("/FontFile2") is not None:
                    embedded_base_fonts.add(str(font.get("/BaseFont", "")))
    assert any("DejaVuSans" in font for font in embedded_base_fonts)
    assert any("DejaVuSansMono" in font for font in embedded_base_fonts)


def test_pdf_preprocessing_preserves_numbering_and_nested_map_bullets():
    """Nested map-reading bullets must not become extra top-level PDF steps."""
    rendered = pdf_generator._render_pdf_html(
        "1. Inspect the map:\n"
        "    * read color as an overview\n"
        "    * check Stations and Spots\n"
        "    * select a segment\n"
        "2. Verify the underlying rows.\n",
        T["en"],
    )
    numbered_markers = re.findall(
        r'class="pdf-list-marker">(\d+\.)</td>',
        rendered,
    )

    assert numbered_markers == ["1.", "2."]
    step_one_start = rendered.index('class="pdf-list-marker">1.</td>')
    step_two_start = rendered.index('class="pdf-list-marker">2.</td>')
    assert rendered[step_one_start:step_two_start].count("&bull;") == 3


def test_pdf_html_adds_named_destinations_without_removing_web_ids():
    rendered = pdf_generator._render_pdf_html(DOC_EN, T["en"])

    for anchor in (
        "sec-1",
        "sec-1-3",
        "sec-1-4",
        "sec-2",
        "sec-outlier",
        "sec-7",
        "sec-7-11",
        "sec-ref",
    ):
        assert f'<a id="{anchor}" name="{anchor}"></a>' in rendered


def test_pdf_preprocessing_marks_only_each_chapter_seven_method_matrix():
    """Only the localized five-column orientation matrices receive print widths."""
    localized_manuals = (
        (DOC_EN, T["en"], "Conditioning /<br/> eligibility"),
        (DOC_DE, T["de"], "Konditionierung /<br/> Zulässigkeit"),
    )
    for manual, translations, wrapped_header in localized_manuals:
        rendered = pdf_generator._render_pdf_html(manual, translations)
        chapter_intro = rendered.split('name="sec-7"', 1)[1].split(
            'name="sec-7-1"', 1
        )[0]

        assert rendered.count('class="pdf-method-matrix"') == 1
        assert "method_matrix_landscape" not in rendered
        assert '<pdf:nextpage name="body" />' not in rendered
        assert rendered.index('name="sec-7"') < rendered.index(
            'class="pdf-method-matrix-label"'
        )
        assert chapter_intro.index(
            'class="pdf-method-matrix-label"'
        ) < chapter_intro.index('class="pdf-method-matrix"')
        assert chapter_intro.index('class="pdf-method-matrix"') < len(chapter_intro)
        assert tuple(
            int(width)
            for width in re.findall(
                r'<th style="width: (\d+)%">',
                chapter_intro,
            )
        ) == pdf_generator.PDF_METHOD_MATRIX_COLUMN_WIDTHS_PERCENT
        assert wrapped_header in chapter_intro

    german_rendered = pdf_generator._render_pdf_html(DOC_DE, T["de"])
    assert "Target-/<br/>lokaler-Referenz-<br/>Peer-Zyklus" in german_rendered
    assert "Target-/<br/>beste-lokale-Station-<br/>Peer-Zyklus" in german_rendered


def test_generated_pdf_keeps_method_matrix_in_portrait(monkeypatch):
    """The method matrix must not switch any generated page to landscape."""
    from PIL import Image
    from pypdf import PdfReader

    column_names = [f"Column {number}" for number in range(1, 6)]
    header = "| " + " | ".join(column_names) + " |"
    separator = "|" + "|".join("---" for _column in column_names) + "|"
    row = "| " + " | ".join(f"Cell {number}" for number in range(1, 6)) + " |"
    compact_manual = "\n".join(
        (
            '<a id="sec-1"></a>',
            "### Before matrix",
            "Portrait content before the scientific chapter.",
            '<a id="sec-7"></a>',
            "### 7. Scientific methods",
            "Scientific chapter introduction.",
            "",
            "**Method matrix**",
            "",
            header,
            separator,
            row,
            "",
            '<a id="sec-7-1"></a>',
            "#### 7.1 After matrix",
            "Portrait content after the method matrix.",
        )
    )
    monkeypatch.setattr(pdf_generator, "get_docs", lambda _lang: compact_manual)

    logo_buffer = io.BytesIO()
    Image.new("RGBA", (1, 1), (255, 255, 255, 255)).save(
        logo_buffer,
        format="PNG",
    )
    logo_b64 = base64.b64encode(logo_buffer.getvalue()).decode("ascii")
    pdf_bytes = pdf_generator._generate_pdf_doc("en", logo_b64, "test")

    assert pdf_bytes is not None
    reader = PdfReader(io.BytesIO(pdf_bytes))
    extracted_text = "\n".join(page.extract_text() or "" for page in reader.pages)

    assert all(
        float(page.mediabox.width) < float(page.mediabox.height)
        for page in reader.pages
    )
    assert "Before matrix" in extracted_text
    assert "Method matrix" in extracted_text
    assert "After matrix" in extracted_text
    assert "Scientific methods" in extracted_text


def test_xhtml2pdf_emits_an_internal_link_destination():
    """The PDF engine requires a name destination for an internal TOC link."""
    from pypdf import PdfReader
    from xhtml2pdf import pisa

    pdf_bytes = io.BytesIO()
    status = pisa.CreatePDF(
        io.StringIO(
            '<html><body><a href="#target">Jump</a>'
            '<p style="page-break-before: always">Second page</p>'
            '<a id="target" name="target"></a><h1>Target</h1></body></html>'
        ),
        dest=pdf_bytes,
    )
    reader = PdfReader(io.BytesIO(pdf_bytes.getvalue()))
    annotations = []
    for page in reader.pages:
        annotations.extend(page.get("/Annots", []))

    assert not status.err
    assert any("/Dest" in annotation.get_object() for annotation in annotations)


def test_documentation_pdf_is_not_generated_during_initial_render(monkeypatch):
    fake_st = _FakeStreamlit()
    monkeypatch.setattr(pdf_generator, "st", fake_st)
    monkeypatch.setattr(
        pdf_generator,
        "generate_pdf_doc",
        lambda *_args: (_ for _ in ()).throw(AssertionError("PDF generation must be lazy")),
    )

    pdf_generator.render_documentation_pdf_control(
        T["en"],
        "en",
        "logo",
        "v0.95",
    )

    assert [label for label, _kwargs in fake_st.buttons] == [
        T["en"]["btn_prepare_documentation_pdf"]
    ]
    assert fake_st.downloads == []
    assert fake_st.spinners == []


def test_first_pdf_request_prepares_and_exposes_download(monkeypatch):
    fake_st = _FakeStreamlit(prepare_clicked=True)
    generated = []
    monkeypatch.setattr(pdf_generator, "st", fake_st)
    monkeypatch.setattr(
        pdf_generator,
        "generate_pdf_doc",
        lambda *args: generated.append(args) or b"pdf-bytes",
    )

    pdf_generator.render_documentation_pdf_control(
        T["en"],
        "en",
        "logo",
        "v0.95",
    )

    assert generated == [("en", "logo", "v0.95")]
    assert fake_st.session_state[_ready_key()] is True
    assert fake_st.spinners == [T["en"]["msg_preparing_documentation_pdf"]]
    assert fake_st.downloads[0][0] == T["en"]["btn_download_documentation_pdf"]
    assert fake_st.downloads[0][1]["data"] == b"pdf-bytes"


def test_prepared_session_reuses_process_cached_generator(monkeypatch):
    fake_st = _FakeStreamlit(session_state={_ready_key(): True})
    generated = []
    monkeypatch.setattr(pdf_generator, "st", fake_st)
    monkeypatch.setattr(
        pdf_generator,
        "generate_pdf_doc",
        lambda *args: generated.append(args) or b"cached-pdf",
    )

    pdf_generator.render_documentation_pdf_control(
        T["en"],
        "en",
        "logo",
        "v0.95",
    )

    assert fake_st.buttons == []
    assert generated == [("en", "logo", "v0.95")]
    assert fake_st.downloads[0][1]["data"] == b"cached-pdf"


def test_failed_pdf_generation_clears_ready_state(monkeypatch):
    fake_st = _FakeStreamlit(prepare_clicked=True)
    monkeypatch.setattr(pdf_generator, "st", fake_st)
    monkeypatch.setattr(pdf_generator, "generate_pdf_doc", lambda *_args: None)

    pdf_generator.render_documentation_pdf_control(
        T["de"],
        "de",
        "logo",
        "v0.95",
    )

    assert _ready_key(lang="de") not in fake_st.session_state
    assert fake_st.downloads == []
    assert fake_st.buttons[-1][1]["disabled"] is True
    assert fake_st.buttons[-1][0] == T["de"]["btn_download_documentation_pdf"]
    assert (
        fake_st.buttons[-1][1]["help"]
        == T["de"]["help_documentation_pdf_unavailable"]
    )
