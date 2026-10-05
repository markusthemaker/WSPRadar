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

        assert source_block_formulas
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
        for expected_formula_fragment in (
            "SNR<sub>norm</sub> = SNR<sub>reported</sub> - P<sub>reported</sub> + 30",
            "SNR<sub>Reference,corr</sub> = SNR<sub>Reference,norm</sub> + C<sub>Reference</sub>",
            "SNR<sub>Target,norm</sub> - SNR<sub>Reference,corr</sub>",
        ):
            assert expected_formula_fragment in rendered
        assert all(
            unescape(re.sub(r"<[^>]+>", "", body)).strip()
            for body in rendered_formula_bodies
        )
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
            r"\varepsilon",
        ):
            assert unsupported_latex not in rendered


@pytest.mark.parametrize(
    ("language", "manual"), [("en", DOC_EN), ("de", DOC_DE)], ids=["en", "de"]
)
def test_generated_pdf_preserves_experimental_detector_explanation(monkeypatch, language, manual):
    """Retain the compact diagnostic's status, sign example and scientific text."""
    from PIL import Image
    from pypdf import PdfReader

    detector_section = manual.split('<a id="sec-7-outliers"></a>', 1)[1].split(
        '<a id="sec-8"></a>', 1
    )[0]
    monkeypatch.setattr(pdf_generator, "get_docs", lambda _lang: detector_section)
    logo_buffer = io.BytesIO()
    Image.new("RGBA", (1, 1), (255, 255, 255, 255)).save(logo_buffer, format="PNG")
    logo_b64 = base64.b64encode(logo_buffer.getvalue()).decode("ascii")

    pdf_bytes = pdf_generator._generate_pdf_doc(language, logo_b64, "test")

    assert pdf_bytes is not None
    reader = PdfReader(io.BytesIO(pdf_bytes))
    extracted = " ".join(" ".join(page.extract_text().split()) for page in reader.pages)
    assert ("experimental" if language == "en" else "experimentell") in extracted.casefold()
    for retained_value in ("+8 dB", "+1 dB", "-7 dB"):
        assert retained_value in detector_section
        assert retained_value in extracted
    assert "ΔSNR" in extracted
    assert r"\varepsilon" not in extracted
    assert "\u25a0" not in extracted


@pytest.mark.parametrize(
    ("language", "manual"), [("en", DOC_EN), ("de", DOC_DE)], ids=["en", "de"]
)
def test_scientific_pdf_table_widths_follow_semantic_topic_anchors(language, manual):
    """Topic-local widths follow the meaning, independently of compatibility aliases."""
    html = pdf_generator._render_pdf_html(manual, T[language])
    for start, end, widths in (
        ("sec-7-spots-identities-cycles", "sec-7-normalization-consolidation", (36, 64)),
        ("sec-7-activity-eligibility", "sec-7-benchmark", (19, 81)),
        ("sec-7-benchmark-delta", "sec-7-benchmark-aggregation", (25, 75)),
        ("sec-7-performance-opportunities", "sec-7-performance-rates", (18, 25, 40, 17)),
        ("sec-7-benchmark-outcomes", "sec-7-benchmark-delta", (25, 75)),
        ("sec-7-benchmark-aggregation", "sec-7-benchmark-coverage", (23, 57, 20)),
        ("sec-7-benchmark-coverage", "sec-7-neighborhood", (34, 66)),
        ("sec-7-outliers", "sec-8", (34, 66)),
    ):
        section = html.split(f'name="{start}"', 1)[1].split(f'name="{end}"', 1)[0]
        matching_tables = [
            table for table in re.findall(r"<table\b.*?</table>", section, re.DOTALL)
            if len(re.findall(r"<th\b", table)) == len(widths)
        ]
        assert matching_tables
        for table in matching_tables:
            assert 'width="100%"' in table
            assert 'repeat="1"' in table
            headers = re.findall(r"<th\b[^>]*>", table)
            assert all(
                re.search(rf'\bwidth:\s*{width}%(?:;|\s*")', header)
                for width, header in zip(widths, headers)
            )

    # The three-column Performance summary must not inherit four-column widths.
    performance = html.split('name="sec-7-performance-rates"', 1)[1].split(
        'name="sec-7-performance-reach"', 1
    )[0]
    three_column_tables = [
        table for table in re.findall(r"<table\b.*?</table>", performance, re.DOTALL)
        if len(re.findall(r"<th\b", table)) == 3
    ]
    assert three_column_tables
    assert all("width: 18%;" not in table for table in three_column_tables)


def test_pdf_wraps_german_detector_labels_without_changing_prose_or_source():
    """Long compounds wrap in detector labels only; wording remains unchanged."""
    rendered = pdf_generator._render_pdf_html(DOC_DE, T["de"])
    source_detector = DOC_DE.split('<a id="sec-7-outliers"></a>', 1)[1].split(
        '<a id="sec-8"></a>', 1
    )[0]
    rendered_detector = rendered.split('name="sec-7-outliers"', 1)[1].split(
        'name="sec-8"', 1
    )[0]
    first_cells = re.findall(
        r"<tr\b[^>]*>\s*<td\b[^>]*>(.*?)</td>",
        rendered_detector,
        re.DOTALL,
    )
    for stem in ("Basislinien", "Vorzeichen"):
        word = f"{stem}übereinstimmung"
        wrapped = f"{stem}-<br/>übereinstimmung"
        source_label_count = source_detector.count(f"| **{word}** |")
        assert sum(wrapped in cell for cell in first_cells) == source_label_count
        assert all(word not in cell for cell in first_cells)
        assert rendered_detector.count(word) == source_detector.count(word) - source_label_count
        assert rendered.count(wrapped) == source_label_count
        assert wrapped not in DOC_DE

    # The same word in prose, an explanation cell or another section stays whole.
    table = (
        "<table><tr><th>Label</th><th>Explanation</th></tr>"
        "<tr><td><strong>Basislinienübereinstimmung</strong></td>"
        "<td><strong>Vorzeichenübereinstimmung</strong></td></tr></table>"
    )
    before = '<a name="sec-7-claims"></a>' + table
    after = '<a name="sec-8"></a>' + table
    prose = "<p>Basislinienübereinstimmung und Vorzeichenübereinstimmung</p>"
    html = before + '<a name="sec-7-outliers"></a>' + prose + table + after
    fitted = pdf_generator._fit_scientific_definition_tables_for_pdf(html)
    assert fitted.startswith(before)
    assert fitted.endswith(after)
    assert prose in fitted
    assert fitted.count("Basislinien-<br/>übereinstimmung") == 1
    assert "Vorzeichen-<br/>übereinstimmung" not in fitted
    english = pdf_generator._render_pdf_html(DOC_EN, T["en"])
    assert "-<br/>übereinstimmung" not in english


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
    table_start = DOC_EN.index("| Your question | Practical examples | Analysis to choose |")
    table_end = DOC_EN.index("\n\n", table_start)

    rendered = pdf_generator._render_pdf_html(
        DOC_EN[table_start:table_end],
        T["en"],
    )

    assert (
            '<table class="pdf-intro-analysis-table" width="100%" repeat="1">'
        in rendered
    )
    for header, width_percent in zip(
        ("Your question", "Practical examples", "Analysis to choose"),
        pdf_generator.PDF_INTRO_ANALYSIS_COLUMN_WIDTHS_PERCENT,
    ):
        assert f'<th style="width: {width_percent}%">{header}</th>' in rendered
    assert rendered.count('class="analysis-choice"') == 4
    assert rendered.count('class="analysis-family"') == 4
    assert rendered.count('class="analysis-variant"') == 4
    assert (
        '<span class="analysis-family">RX/TX Benchmark</span><br>'
        '<strong class="analysis-variant">Reference Setup/Station</strong>'
        in rendered
    )


def test_pdf_german_intro_receives_the_same_compact_column_layout():
    rendered = pdf_generator._render_pdf_html(DOC_DE, T["de"])
    assert rendered.count('class="pdf-intro-analysis-table"') == 1
    for header, width in zip(
        ("Deine Frage", "Praktische Beispiele", "Passende Analyse"),
        pdf_generator.PDF_INTRO_ANALYSIS_COLUMN_WIDTHS_PERCENT,
    ):
        assert f'<th style="width: {width}%">{header}</th>' in rendered


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
    assert rendered.count(defined_evidence_path) == 1


def test_pdf_preprocessing_preserves_english_section_two_conclusion_callouts():
    """Retain the scoped conclusion class for print-specific contrast styling."""
    rendered = pdf_generator._render_pdf_html(DOC_EN, T["en"])

    assert rendered.count('<blockquote class="evidence-conclusion">') == 8
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
        "sec-7-foundations",
        "sec-7-benchmark",
        "sec-7-performance",
        "sec-7-views",
        "sec-7-claims",
        "sec-7-outliers",
        "sec-ref",
    ):
        assert f'<a id="{anchor}" name="{anchor}"></a>' in rendered


def test_pdf_preprocessing_marks_only_source_chapter_seven_method_matrices():
    """Do not invent an orientation matrix or tag another scientific table."""
    import markdown

    for manual, translations in ((DOC_EN, T["en"]), (DOC_DE, T["de"])):
        source_intro = manual.split('<a id="sec-7"></a>', 1)[1].split(
            '<a id="sec-7-foundations"></a>', 1
        )[0]
        source_html = markdown.markdown(
            source_intro, extensions=pdf_generator.PDF_MARKDOWN_EXTENSIONS
        )
        source_matrices = [
            table for table in re.findall(r"<table\b.*?</table>", source_html, re.DOTALL)
            if len(re.findall(r"<th\b", table)) == 5
        ]
        expected_count = 1 if len(source_matrices) == 1 else 0
        rendered = pdf_generator._render_pdf_html(manual, translations)
        chapter_intro = rendered.split('name="sec-7"', 1)[1].split(
            'name="sec-7-foundations"', 1
        )[0]

        assert rendered.count('class="pdf-method-matrix"') == expected_count
        assert chapter_intro.count('class="pdf-method-matrix"') == expected_count
        if not source_matrices:
            assert 'class="pdf-method-matrix-label"' not in rendered
        assert "method_matrix_landscape" not in rendered
        assert '<pdf:nextpage name="body" />' not in rendered


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
            '<a id="sec-7-foundations"></a>',
            "#### 7.1 After matrix",
            "Portrait content after the method matrix.",
        )
    )
    rendered = pdf_generator._render_pdf_html(compact_manual, T["en"])
    assert rendered.count('class="pdf-method-matrix"') == 1
    assert 'class="pdf-method-matrix-label"' in rendered
    matrix = re.search(
        r'<table class="pdf-method-matrix".*?</table>', rendered, re.DOTALL
    ).group(0)
    assert tuple(int(width) for width in re.findall(r'width: (\d+)%', matrix)) == (
        pdf_generator.PDF_METHOD_MATRIX_COLUMN_WIDTHS_PERCENT
    )
    assert 'repeat="1"' in matrix
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


def test_xhtml2pdf_internal_links_land_at_the_heading_on_the_target_page():
    """Semantic and compatibility links must land above the heading, not its end."""
    from pypdf import PdfReader
    from xhtml2pdf import pisa

    pdf_bytes = io.BytesIO()
    status = pisa.CreatePDF(
        io.StringIO(
            '<html><body><a href="#target-topic">Jump</a> '
            '<a href="#legacy-target">Compatibility link</a>'
            '<p style="page-break-before: always">Previous section ends here.</p>'
            '<p>Another paragraph before the target heading.</p>'
            '<a id="legacy-target" name="legacy-target"></a>'
            '<a id="target-topic" name="target-topic"></a>'
            '<h1>Target Heading</h1>'
            '<p>First paragraph of the target section.</p>'
            '<p>Last paragraph of the target section.</p></body></html>'
        ),
        dest=pdf_bytes,
    )
    reader = PdfReader(io.BytesIO(pdf_bytes.getvalue()))
    assert not status.err
    assert len(reader.pages) == 2
    heading_positions = []

    def capture_heading(text, current_matrix, text_matrix, _font, font_size):
        if text.strip() == "Target Heading":
            y = (
                text_matrix[4] * current_matrix[1]
                + text_matrix[5] * current_matrix[3]
                + current_matrix[5]
            )
            heading_positions.append((y, font_size))

    target_page = reader.pages[1]
    target_page.extract_text(visitor_text=capture_heading)
    assert len(heading_positions) == 1
    heading_y, heading_font_size = heading_positions[0]
    destinations = [
        annotation.get_object()["/Dest"]
        for annotation in reader.pages[0].get("/Annots", [])
        if "/Dest" in annotation.get_object()
    ]
    assert len(destinations) == 2
    for destination in destinations:
        assert destination[0] == target_page.indirect_reference
        assert destination[1] == "/XYZ"
        assert 0 <= float(destination[3]) - heading_y <= 2 * heading_font_size
    assert destinations[0] == destinations[1]


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


@pytest.mark.parametrize(
    "headers,short_label,long_label",
    (
        (("Figure", "What to read and how to interpret it"), "Map", "Selected Station Evidence"),
        (("Darstellung", "Ablesen und einordnen"), "Karte", "Evidenz der ausgewählten Station"),
    ),
)
def test_pdf_reading_guides_fit_label_content_without_changing_other_tables(
    headers, short_label, long_label,
):
    """Guide widths follow each table's labels, not a global one-third rule."""
    def guide(label):
        return (
            f"| {headers[0]} | {headers[1]} |\n|---|---|\n"
            f"| **{label}** | Preserve this explanation and its **meaning**. |\n"
        )

    ordinary_table = "| Item | Meaning |\n|---|---|\n| A | Unchanged. |\n"
    compact_manual = (
        guide(short_label) + '\n<a id="sec-3"></a>\n\n'
        "**Reading guide**\n\n" + guide(short_label) + "\n"
        + guide(long_label) + "\n" + ordinary_table
        + '\n<a id="sec-4"></a>\n\n' + guide(long_label)
    )
    rendered = pdf_generator._render_pdf_html(compact_manual, T["en"])
    guides = re.findall(
        r'<table class="pdf-reading-guide"[^>]*>.*?</table>',
        rendered, flags=re.DOTALL,
    )

    assert len(guides) == 2
    widths = [
        [float(value) for value in re.findall(r'<th style="width: ([0-9.]+)%">', guide_html)]
        for guide_html in guides
    ]
    assert 0 < widths[0][0] < widths[1][0] < 50
    assert all(sum(pair) == pytest.approx(100) for pair in widths)
    assert all('repeat="1"' in guide_html for guide_html in guides)
    assert '<p class="pdf-reading-guide-heading"><strong>Reading guide</strong></p>' in rendered
    assert rendered.count('class="pdf-reading-guide-label"') == 2
    assert rendered.count("Preserve this explanation and its <strong>meaning</strong>.") == 4
    assert "<th>Item</th>" in rendered
    assert rendered.count('<table repeat="1">') == 3


@pytest.mark.parametrize("headers", pdf_generator.PDF_READING_GUIDE_HEADERS)
def test_pdf_reading_guides_allow_long_labels_to_wrap_without_losing_text(headers):
    """Long UI labels leave most of the portrait page for interpretation."""
    long_label = "Long localized scientific figure title " * 4
    compact_manual = (
        '<a id="sec-3"></a>\n\n'
        f"| {headers[0]} | {headers[1]} |\n|---|---|\n"
        f"| {long_label} | Complete explanatory text remains available. |\n\n"
        '<a id="sec-4"></a>'
    )
    rendered = pdf_generator._render_pdf_html(compact_manual, T["en"])
    widths = [
        float(value)
        for value in re.findall(r'<th style="width: ([0-9.]+)%">', rendered)
    ]

    assert widths == [38, 62]
    assert long_label.strip() in rendered
    assert "Complete explanatory text remains available." in rendered


def test_pdf_chapter_two_keeps_subheadings_and_short_guide_lead_ins_together():
    """Keep local setup headings and table context attached without global rules."""
    guide = (
        "| Action | Where it takes you |\n|---|---|\n"
        "| Show details | Opens the retained evidence. |\n"
    )
    long_paragraph = "A detailed description may flow across pages. " * 12
    compact_manual = (
        "##### Outside before\n\n**Outside label**\n\n"
        '<a id="sec-3"></a>\n\n'
        "#### 2.1 RX Benchmark\n\n"
        "##### 2.1.1 Reference Setup/Station\n\n"
        "**Controlled local setup.**\n\n"
        "Keep the actual setup paragraph with its two introductory headings.\n\n"
        '<blockquote class="evidence-conclusion"><p>Controlled comparison.</p></blockquote>\n\n'
        "**Independent station.**\n\n"
        "Compare the two complete stations.\n\n"
        "**Inspect the path next.** Both actions select the path and open focus:\n\n"
        + guide + "\n" + long_paragraph + "\n\n" + guide
        + '\n<a id="sec-4"></a>\n\n'
        "##### Outside after\n\n**Another outside label**\n"
    )
    rendered = pdf_generator._render_pdf_html(compact_manual, T["en"])

    assert '<h4 class="pdf-chapter-two-heading">2.1 RX Benchmark</h4>' in rendered
    assert '<h5 class="pdf-chapter-two-heading">2.1.1 Reference Setup/Station</h5>' in rendered
    assert '<p class="pdf-chapter-two-heading"><strong>Controlled local setup.</strong></p>' in rendered
    assert '<p class="pdf-chapter-two-heading"><strong>Independent station.</strong></p>' in rendered
    assert (
        '<p class="pdf-reading-guide-heading"><strong>Inspect the path next.</strong> '
        "Both actions select the path and open focus:</p>"
    ) in rendered
    assert rendered.count('class="pdf-reading-guide-heading"') == 1
    assert long_paragraph.strip() in rendered
    assert "<h5>Outside before</h5>" in rendered
    assert "<h5>Outside after</h5>" in rendered
    assert '<p class="pdf-section-label"><strong>Outside label</strong></p>' in rendered
    assert '<p class="pdf-section-label"><strong>Another outside label</strong></p>' in rendered
