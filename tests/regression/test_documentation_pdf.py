import base64
import io
import re

from docs import pdf_generator
from docs.doc_de import DOC_DE
from docs.doc_en import DOC_EN


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
    for manual in (DOC_EN, DOC_DE):
        rendered = pdf_generator._replace_pdf_math(manual)

        assert "$$" not in rendered
        assert "&Delta;" not in rendered
        assert "Delta SNR =" in rendered
        assert "D<sub>relativ" in rendered
        assert "f<sub>RF</sub> approx. f<sub>dial</sub>" in rendered


def test_pdf_markdown_extensions_preserve_fenced_code_blocks():
    import markdown

    rendered = markdown.markdown(
        "```text\nconfig/\n  run_metadata.json\n```",
        extensions=pdf_generator.PDF_MARKDOWN_EXTENSIONS,
    )

    assert rendered.startswith("<pre><code")
    assert "config/\n  run_metadata.json" in rendered


def test_pdf_preprocessing_makes_fenced_code_layout_explicit():
    """xhtml2pdf must receive explicit breaks and indentation in code blocks."""
    rendered = pdf_generator._render_pdf_html(
        "```text\nconfig/\n  run_metadata.json\n```"
    )

    assert (
        '<pre><code class="language-text">config/<br/>'
        "&#160;&#160;run_metadata.json</code></pre>"
    ) in rendered


def test_pdf_preprocessing_preserves_defined_term_markup():
    """First-definition emphasis must survive Markdown-to-PDF preprocessing."""
    rendered = pdf_generator._render_pdf_html(DOC_EN)

    assert '<strong class="defined-term">Target</strong>' in rendered
    assert '<strong class="defined-term">Reference</strong>' in rendered


def test_pdf_preprocessing_preserves_numbering_and_nested_map_bullets():
    """Nested map-reading bullets must not become extra top-level PDF steps."""
    rendered = pdf_generator._render_pdf_html(
        "1. Inspect the map:\n"
        "    * read color as an overview\n"
        "    * check Stations and Spots\n"
        "    * select a segment\n"
        "2. Verify the underlying rows.\n"
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
    rendered = pdf_generator._render_pdf_html(DOC_EN)

    for anchor in ("sec-1", "sec-1-3", "sec-1-4", "sec-2", "sec-7", "sec-ref"):
        assert f'<a id="{anchor}" name="{anchor}"></a>' in rendered


def test_pdf_preprocessing_isolates_only_each_chapter_seven_method_matrix():
    """Only the localized 10-column orientation matrices use landscape pages."""
    localized_manuals = (
        (DOC_EN, "Lowest observation/<br/>comparison unit"),
        (DOC_DE, "Beobachtungs-/<br/>Vergleichseinheit"),
    )
    for manual, wrapped_header in localized_manuals:
        rendered = pdf_generator._render_pdf_html(manual)
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

    pdf_generator.render_documentation_pdf_control({}, "en", "logo", "v0.95")

    assert [label for label, _kwargs in fake_st.buttons] == ["Prepare PDF"]
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

    pdf_generator.render_documentation_pdf_control({}, "en", "logo", "v0.95")

    assert generated == [("en", "logo", "v0.95")]
    assert fake_st.session_state[_ready_key()] is True
    assert fake_st.spinners == ["Preparing documentation PDF..."]
    assert fake_st.downloads[0][0] == "Download PDF"
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

    pdf_generator.render_documentation_pdf_control({}, "en", "logo", "v0.95")

    assert fake_st.buttons == []
    assert generated == [("en", "logo", "v0.95")]
    assert fake_st.downloads[0][1]["data"] == b"cached-pdf"


def test_failed_pdf_generation_clears_ready_state(monkeypatch):
    fake_st = _FakeStreamlit(prepare_clicked=True)
    monkeypatch.setattr(pdf_generator, "st", fake_st)
    monkeypatch.setattr(pdf_generator, "generate_pdf_doc", lambda *_args: None)

    pdf_generator.render_documentation_pdf_control({}, "de", "logo", "v0.95")

    assert _ready_key(lang="de") not in fake_st.session_state
    assert fake_st.downloads == []
    assert fake_st.buttons[-1][1]["disabled"] is True
