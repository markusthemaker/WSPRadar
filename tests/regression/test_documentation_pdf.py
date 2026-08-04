import base64
from html import unescape
import io
import re

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
        decode_rate_label = translations["pdf_metric_decode_rate"]
        rendered = pdf_generator._replace_pdf_math(manual, translations)

        assert "$$" not in rendered
        assert "&Delta;" not in rendered
        assert (
            f"{decode_rate_label}<sub>RX</sub> = 100% &times; "
            "Target / (Target + Elsewhere)"
        ) in rendered
        assert (
            f"{decode_rate_label}<sub>TX</sub> = 100% &times; "
            "Target / (Target + Other Signals)"
        ) in rendered
        assert "Success Rate<sub>" not in rendered
        assert f"{translations['pdf_formula_delta_snr']} =" in rendered
        assert (
            "SNR<sub>reference</sub> + "
            f"{translations['pdf_formula_correction']}"
        ) in rendered
        assert (
            "v<sub>T,s,b</sub> = T<sub>s,b</sub> / N<sub>s,b</sub>"
            in rendered
        )
        assert (
            "v<sub>J,s,b</sub> = J<sub>s,b</sub> / N<sub>s,b</sub>"
            in rendered
        )
        assert (
            "v<sub>R,s,b</sub> = R<sub>s,b</sub> / N<sub>s,b</sub>"
            in rendered
        )
        assert (
            "N<sub>s,b</sub> = T<sub>s,b</sub> + "
            "J<sub>s,b</sub> + R<sub>s,b</sub>"
            in rendered
        )
        assert (
            "100 &times; mean<sub>s</sub>("
            "J<sub>s,b</sub> / N<sub>s,b</sub>)"
            in rendered
        )
        assert (
            "100 &times; sum<sub>s</sub> J<sub>s,b</sub> / "
            "sum<sub>s</sub> N<sub>s,b</sub>"
            in rendered
        )
        for unsupported_latex in (
            r"\(",
            r"\)",
            r"\operatorname",
            r"\sum",
        ):
            assert unsupported_latex not in rendered
        assert "C<sub>s,b</sub>" not in rendered
        assert "B<sub>s</sub>" not in rendered
        assert "D<sub>relativ" in rendered
        assert (
            "f<sub>RF</sub> "
            f"{translations['pdf_formula_approx']} f<sub>dial</sub>"
        ) in rendered


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
    """Prove that both proportional and monospace PDF fonts retain the glyph."""
    from PIL import Image
    from pypdf import PdfReader

    compact_manual = (
        "Plain prose — remains separated.\n\n"
        "`Performance — no Reference`"
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
    extracted_text = "\n".join(
        page.extract_text() or ""
        for page in PdfReader(io.BytesIO(pdf_bytes)).pages
    )
    assert "Plain prose — remains separated." in extracted_text
    assert "Performance — no Reference" in extracted_text


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

    for anchor in ("sec-1", "sec-1-3", "sec-1-4", "sec-2", "sec-7", "sec-ref"):
        assert f'<a id="{anchor}" name="{anchor}"></a>' in rendered


def test_pdf_preprocessing_isolates_only_each_chapter_seven_method_matrix():
    """Only the localized 10-column orientation matrices use landscape pages."""
    localized_manuals = (
        (DOC_EN, T["en"], "Lowest observation/<br/>comparison unit"),
        (DOC_DE, T["de"], "Beobachtungs-/<br/>Vergleichseinheit"),
    )
    for manual, translations, wrapped_header in localized_manuals:
        rendered = pdf_generator._render_pdf_html(manual, translations)
        chapter_intro = rendered.split('name="sec-7"', 1)[1].split(
            'name="sec-7-1"', 1
        )[0]

        assert rendered.count('class="pdf-method-matrix"') == 1
        assert rendered.count(
            '<pdf:nextpage name="method_matrix_landscape" />'
        ) == 1
        assert rendered.count('<pdf:nextpage name="body" />') == 1
        assert rendered.index('name="method_matrix_landscape"') < rendered.index(
            'name="sec-7"'
        )
        assert rendered.index('name="sec-7"') < rendered.index(
            'class="pdf-method-matrix-label"'
        )
        assert chapter_intro.index(
            'class="pdf-method-matrix-label"'
        ) < chapter_intro.index('class="pdf-method-matrix"')
        assert chapter_intro.index('class="pdf-method-matrix"') < chapter_intro.index(
            'name="body"'
        )
        assert tuple(
            int(width)
            for width in re.findall(
                r'<th style="width: (\d+)%">',
                chapter_intro,
            )
        ) == pdf_generator.PDF_METHOD_MATRIX_COLUMN_WIDTHS_PERCENT
        assert wrapped_header in chapter_intro


def test_generated_pdf_switches_to_landscape_for_method_matrix(monkeypatch):
    """The named page templates must bracket the method matrix in the actual PDF."""
    from PIL import Image
    from pypdf import PdfReader

    column_names = [f"Column {number}" for number in range(1, 11)]
    header = "| " + " | ".join(column_names) + " |"
    separator = "|" + "|".join("---" for _column in column_names) + "|"
    row = "| " + " | ".join(f"Cell {number}" for number in range(1, 11)) + " |"
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
    pages_by_text = {
        page.extract_text(): page
        for page in reader.pages
    }
    matrix_page = next(
        page for text, page in pages_by_text.items() if "Method matrix" in text
    )
    before_page = next(
        page for text, page in pages_by_text.items() if "Before matrix" in text
    )
    after_page = next(
        page for text, page in pages_by_text.items() if "After matrix" in text
    )

    assert float(before_page.mediabox.width) < float(before_page.mediabox.height)
    assert float(matrix_page.mediabox.width) > float(matrix_page.mediabox.height)
    assert float(after_page.mediabox.width) < float(after_page.mediabox.height)
    assert "Scientific methods" in matrix_page.extract_text()


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
