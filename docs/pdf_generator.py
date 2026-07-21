"""
PDF Generator module.
Takes the Markdown documentation, fixes lists and LaTeX formulas, and renders via xhtml2pdf.
"""
import io
import base64
from html import escape
from html.parser import HTMLParser
import re
import threading
from functools import lru_cache
import streamlit as st
from i18n import T


from docs.doc_de import DOC_DE
from docs.doc_en import DOC_EN


DOCUMENTATION_PDF_READY_KEY_PREFIX = "_documentation_pdf_ready"
_DOCUMENTATION_PDF_GENERATION_LOCK = threading.Lock()
PDF_MARKDOWN_EXTENSIONS = ("tables", "fenced_code")
PDF_METHOD_MATRIX_COLUMN_WIDTHS_PERCENT = (11, 8, 12, 10, 9, 10, 11, 8, 8, 13)


@lru_cache(maxsize=2)
def get_docs(lang):
    """Return documentation for the selected language."""
    return DOC_DE if lang == "de" else DOC_EN


def _formula(html):
    return f'<p class="formula"><b>{html}</b></p>'


def _replace_pdf_math(md_text):
    """Replace LaTeX-like Markdown formulas with xhtml2pdf-safe HTML."""
    block_replacements = {
        r"\text{Success Rate}_{RX} = 100\% \times \frac{\text{Target}}{\text{Target} + \text{Elsewhere}}": _formula(
            "Success Rate<sub>RX</sub> = 100% &times; "
            "Target / (Target + Elsewhere)"
        ),
        r"\text{Success Rate}_{TX} = 100\% \times \frac{\text{Target}}{\text{Target} + \text{Other Signals}}": _formula(
            "Success Rate<sub>TX</sub> = 100% &times; "
            "Target / (Target + Other Signals)"
        ),
        r"SNR_{norm} = SNR_{measured} - P_{TX(dBm)} + 30": _formula(
            "SNR<sub>norm</sub> = SNR<sub>measured</sub> - "
            "P<sub>TX(dBm)</sub> + 30"
        ),
        r"SNR_{reference,corrected} = SNR_{reference} + Correction": _formula(
            "SNR<sub>reference,corrected</sub> = "
            "SNR<sub>reference</sub> + Correction"
        ),
        r"\Delta SNR = SNR_{target} - SNR_{reference,corrected}": _formula(
            "Delta SNR = SNR<sub>target</sub> - "
            "SNR<sub>reference,corrected</sub>"
        ),
        r"\Delta SNR_{TX} = SNR_{norm,target} - SNR_{norm,reference}": _formula(
            "Delta SNR<sub>TX</sub> = SNR<sub>norm,target</sub> - "
            "SNR<sub>norm,reference</sub>"
        ),
        r"\Delta SNR_{RX} = SNR_{target} - SNR_{reference}": _formula(
            "Delta SNR<sub>RX</sub> = SNR<sub>target</sub> - "
            "SNR<sub>reference</sub>"
        ),
        r"\Delta SNR_{TX} = SNR_{norm,target} - SNR_{norm,benchmark}": _formula(
            "Delta SNR<sub>TX</sub> = SNR<sub>norm,target</sub> - "
            "SNR<sub>norm,benchmark</sub>"
        ),
        r"\Delta SNR_{RX} = SNR_{measured,target} - SNR_{measured,benchmark}": _formula(
            "Delta SNR<sub>RX</sub> = SNR<sub>measured,target</sub> - "
            "SNR<sub>measured,benchmark</sub>"
        ),
        r"D_{relative} = 100 \times \frac{n_{cell}}{\max(n_{cell,panel})}": _formula(
            "D<sub>relative</sub> = 100 &times; "
            "n<sub>cell</sub> / max(n<sub>cell,panel</sub>)"
        ),
        r"D_{relativ} = 100 \times \frac{n_{Zelle}}{\max(n_{Zelle,Panel})}": _formula(
            "D<sub>relativ</sub> = 100 &times; "
            "n<sub>Zelle</sub> / max(n<sub>Zelle,Panel</sub>)"
        ),
        r"f_{RF} \approx f_{dial} + f_{TX\ audio}": _formula(
            "f<sub>RF</sub> approx. f<sub>dial</sub> + "
            "f<sub>TX audio</sub>"
        ),
        r"f_{HF} \approx f_{Dial} + f_{TX\ Audio}": _formula(
            "f<sub>RF</sub> approx. f<sub>dial</sub> + "
            "f<sub>TX audio</sub>"
        ),
    }

    for latex, html in block_replacements.items():
        md_text = md_text.replace(f"$${latex}$$", html)
        md_text = md_text.replace(f"${latex}$", html)

    inline_replacements = {
        r"$\Delta$ SNR": "Delta SNR",
        r"$\Delta$": "Delta",
        r"$2^\circ \times 1^\circ$": "2&deg; &times; 1&deg;",
        r"$150 \times 111$": "150 &times; 111",
        r"$5' \times 2.5'$": "5&apos; &times; 2.5&apos;",
        r"$6 \times 4$": "6 &times; 4",
    }

    for latex, html in inline_replacements.items():
        md_text = md_text.replace(latex, html)

    return md_text


def _html_start_tag(tag, attrs, extra_classes=()):
    """Serialize one HTML start tag while preserving attributes and adding classes."""
    serialized_attrs = []
    class_values = []
    for name, value in attrs:
        if name.casefold() == "class":
            class_values.extend(str(value or "").split())
            continue
        if value is None:
            serialized_attrs.append(f" {name}")
        else:
            serialized_attrs.append(f' {name}="{escape(str(value), quote=True)}"')
    for class_name in extra_classes:
        if class_name not in class_values:
            class_values.append(class_name)
    if class_values:
        serialized_attrs.append(
            f' class="{escape(" ".join(class_values), quote=True)}"'
        )
    return f"<{tag}{''.join(serialized_attrs)}>"


class _PdfListMarkerParser(HTMLParser):
    """Inject explicit markers while retaining nested ordered/unordered structure."""

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.parts = []
        self.list_stack = []

    def handle_starttag(self, tag, attrs):
        normalized_tag = tag.casefold()
        if normalized_tag in {"ol", "ul"}:
            start_value = 1
            if normalized_tag == "ol":
                for name, value in attrs:
                    if name.casefold() == "start":
                        try:
                            start_value = int(value)
                        except (TypeError, ValueError):
                            start_value = 1
            self.list_stack.append(
                {"tag": normalized_tag, "counter": start_value - 1}
            )
            self.parts.append(
                _html_start_tag(
                    tag,
                    attrs,
                    ("pdf-list", f"pdf-{normalized_tag}"),
                )
            )
            return
        if normalized_tag == "li":
            list_context = self.list_stack[-1] if self.list_stack else None
            if list_context and list_context["tag"] == "ol":
                list_context["counter"] += 1
                marker = f'{list_context["counter"]}.'
            else:
                marker = "&bull;"
            self.parts.append(_html_start_tag(tag, attrs))
            self.parts.append(
                '<table class="pdf-list-row"><tr>'
                f'<td class="pdf-list-marker">{marker}</td>'
                '<td class="pdf-list-body">'
            )
            return
        self.parts.append(self.get_starttag_text())

    def handle_startendtag(self, tag, attrs):
        self.parts.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        normalized_tag = tag.casefold()
        if normalized_tag == "li":
            self.parts.append("</td></tr></table></li>")
            return
        if normalized_tag in {"ol", "ul"}:
            if self.list_stack:
                self.list_stack.pop()
            self.parts.append(f"</{tag}>")
            return
        self.parts.append(f"</{tag}>")

    def handle_data(self, data):
        self.parts.append(data)

    def handle_entityref(self, name):
        self.parts.append(f"&{name};")

    def handle_charref(self, name):
        self.parts.append(f"&#{name};")

    def handle_comment(self, data):
        self.parts.append(f"<!--{data}-->")

    def handle_decl(self, decl):
        self.parts.append(f"<!{decl}>")

    def unknown_decl(self, data):
        self.parts.append(f"<![{data}]>")


def _inject_pdf_list_markers(html_content):
    """Add xhtml2pdf-safe list markers without flattening nested lists."""
    parser = _PdfListMarkerParser()
    parser.feed(html_content)
    parser.close()
    return "".join(parser.parts)


def _add_pdf_anchor_names(html_content):
    """Add PDF-compatible ``name`` destinations while preserving web ``id`` anchors."""
    anchor_pattern = re.compile(r"<a\b[^>]*>", flags=re.IGNORECASE)

    def add_name(anchor_match):
        anchor_tag = anchor_match.group(0)
        if re.search(r"\bname\s*=", anchor_tag, flags=re.IGNORECASE):
            return anchor_tag
        id_match = re.search(
            r"\bid\s*=\s*(['\"])(.*?)\1",
            anchor_tag,
            flags=re.IGNORECASE,
        )
        if id_match is None:
            return anchor_tag
        anchor_name = escape(id_match.group(2), quote=True)
        return f'{anchor_tag[:-1]} name="{anchor_name}">'

    return anchor_pattern.sub(add_name, html_content)


def _preserve_pdf_fenced_code_layout(html_content):
    """Make fenced-code newlines and indentation explicit for xhtml2pdf."""
    code_block_pattern = re.compile(
        r"(<pre\b[^>]*>\s*<code\b[^>]*>)(.*?)(</code>\s*</pre>)",
        flags=re.IGNORECASE | re.DOTALL,
    )

    def preserve_layout(code_block_match):
        code_text = code_block_match.group(2).replace("\r\n", "\n").replace(
            "\r", "\n"
        )
        rendered_lines = []
        for code_line in code_text.splitlines():
            code_line = code_line.replace("\t", "    ")
            code_line = re.sub(
                r" {2,}",
                lambda spaces: "&#160;" * len(spaces.group(0)),
                code_line,
            )
            rendered_lines.append(code_line)
        return (
            code_block_match.group(1)
            + "<br/>".join(rendered_lines)
            + code_block_match.group(3)
        )

    return code_block_pattern.sub(preserve_layout, html_content)


def _mark_method_matrix_for_pdf(html_content):
    """Isolate the Chapter 7 method matrix for a landscape PDF page template."""
    chapter_start = html_content.find('name="sec-7"')
    methods_start = html_content.find('name="sec-7-1"', chapter_start + 1)
    if chapter_start < 0 or methods_start < 0:
        return html_content

    matrix_table_start = html_content.find("<table>", chapter_start, methods_start)
    if matrix_table_start < 0:
        return html_content
    matrix_table_end = html_content.find("</table>", matrix_table_start, methods_start)
    if matrix_table_end < 0:
        return html_content
    matrix_table_end += len("</table>")

    matrix_table = html_content[matrix_table_start:matrix_table_end]
    header_end = matrix_table.find("</thead>")
    header_html = matrix_table[:header_end] if header_end >= 0 else matrix_table
    if len(re.findall(r"<th\b", header_html, flags=re.IGNORECASE)) != len(
        PDF_METHOD_MATRIX_COLUMN_WIDTHS_PERCENT
    ):
        return html_content

    column_widths = iter(PDF_METHOD_MATRIX_COLUMN_WIDTHS_PERCENT)

    def format_header_cell(header_match):
        width_percent = next(column_widths)
        header_text = header_match.group(1).replace("/", "/<br/>")
        return f'<th style="width: {width_percent}%">{header_text}</th>'

    matrix_table = matrix_table.replace(
        "<table>",
        '<table class="pdf-method-matrix" width="100%">',
        1,
    )
    matrix_table = re.sub(
        r"<th>(.*?)</th>",
        format_header_cell,
        matrix_table,
        count=len(PDF_METHOD_MATRIX_COLUMN_WIDTHS_PERCENT),
        flags=re.IGNORECASE | re.DOTALL,
    )

    label_match = re.search(
        r"<p><strong>[^<]+</strong></p>\s*\Z",
        html_content[chapter_start:matrix_table_start],
        flags=re.IGNORECASE,
    )
    chapter_anchor_start = html_content.rfind("<a", 0, chapter_start)
    landscape_start = (
        chapter_anchor_start if chapter_anchor_start >= 0 else matrix_table_start
    )
    matrix_prefix = html_content[landscape_start:matrix_table_start]
    if label_match:
        label_start = chapter_start + label_match.start()
        relative_label_start = label_start - landscape_start
        matrix_prefix = (
            matrix_prefix[:relative_label_start]
            + matrix_prefix[relative_label_start:].replace(
                "<p><strong>",
                '<p class="pdf-method-matrix-label"><strong>',
                1,
            )
        )
    landscape_content = (
        '<pdf:nextpage name="method_matrix_landscape" />'
        f"{matrix_prefix}{matrix_table}"
        '<pdf:nextpage name="body" />'
    )
    return (
        html_content[:landscape_start]
        + landscape_content
        + html_content[matrix_table_end:]
    )


def _render_pdf_html(md_text, markdown_module=None):
    """Run the complete Markdown-to-HTML preprocessing used by PDF generation."""
    if markdown_module is None:
        import markdown as markdown_module

    md_text = md_text.replace("---", "", 1)
    md_text = _replace_pdf_math(md_text)
    html_content = markdown_module.markdown(
        md_text,
        extensions=PDF_MARKDOWN_EXTENSIONS,
    )
    html_content = _preserve_pdf_fenced_code_layout(html_content)
    html_content = _add_pdf_anchor_names(html_content)
    html_content = _inject_pdf_list_markers(html_content)
    return _mark_method_matrix_for_pdf(html_content)



def _generate_pdf_doc(lang, logo_b64, version):
    """Generate a PDF from the localized Markdown string."""
    try:
        import markdown
        from xhtml2pdf import pisa
        from PIL import Image
    except ImportError:
        return None

    try:
        img_data = base64.b64decode(logo_b64)
        img = Image.open(io.BytesIO(img_data)).convert("RGBA")
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        clean_img = Image.alpha_composite(bg, img).convert("RGB")
        out_buf = io.BytesIO()
        clean_img.save(out_buf, format="JPEG", quality=95)
        pdf_logo_src = f"data:image/jpeg;base64,{base64.b64encode(out_buf.getvalue()).decode()}"
    except Exception:
        pdf_logo_src = f"data:image/png;base64,{logo_b64}"

    html_content = _render_pdf_html(get_docs(lang), markdown)

    dev_credit_pdf = T[lang]["dev_credit"].replace("#39ff14", "#0a318f")
    page_label = "Seite" if lang == "de" else "Page"

    template = f"""
    <html>
    <head>
    <style>
        @page {{ size: a4 portrait; margin: 2cm;
                @frame footer {{ -pdf-frame-content: footerContent; bottom: 1cm; margin-left: 2cm; margin-right: 2cm; height: 1cm; text-align: right; font-size: 8pt; color: #999; }}
        }}

        @page method_matrix_landscape {{ size: a4 landscape; margin: 1.2cm;
                @frame footer {{ -pdf-frame-content: footerContent; bottom: 0.5cm; margin-left: 1.2cm; margin-right: 1.2cm; height: 0.6cm; text-align: right; font-size: 8pt; color: #999; }}
        }}

        body {{
            font-family: Helvetica, Arial, sans-serif;
            font-size: 10pt;
            color: #333;
            line-height: 1.35;
        }}

        p {{ margin-top: 0; margin-bottom: 6px; }}

        h1, h2 {{ color: #0a1428; }}
        h3, h4, .defined-term {{ color: #146b2e; }}

        .defined-term {{ font-weight: bold; }}

        h1 {{ margin-top: 18px; margin-bottom: 8px; }}
        h2 {{ margin-top: 16px; margin-bottom: 7px; }}

        h3 {{
            border-bottom: 1px solid #ccc;
            padding-bottom: 3px;
            margin-top: 14px;
            margin-bottom: 6px;
        }}

        h4 {{
            margin-top: 10px;
            margin-bottom: 5px;
            font-size: 10.5pt;
        }}

        .header {{ text-align: center; margin-bottom: 22px; }}
        .logo {{ width: 90px; margin-bottom: 10px; }}
        .title {{ font-size: 24pt; font-weight: bold; margin: 0; color: #000; letter-spacing: 1px; }}
        .subtitle {{ font-size: 11pt; color: #666; margin-top: 5px; }}

        code {{
            font-family: Courier, monospace;
            background-color: #f4f4f4;
            padding: 2px 4px;
            font-size: 9pt;
            border-radius: 3px;
        }}

        pre {{
            font-family: Courier, monospace;
            background-color: #f4f4f4;
            padding: 6px;
            font-size: 8pt;
            line-height: 1.2;
            white-space: pre-wrap;
        }}

        pre code {{
            background-color: transparent;
            padding: 0;
            font-size: 8pt;
        }}

        th {{ text-align: left; background-color: #eee; padding: 4px; }}
        td {{ padding: 4px; border-bottom: 1px solid #eee; vertical-align: top; }}

        .pdf-method-matrix-label {{
            margin-bottom: 5px;
            font-size: 9pt;
        }}

        .pdf-method-matrix {{
            width: 100%;
            font-size: 6pt;
            line-height: 1.1;
        }}

        .pdf-method-matrix th {{
            padding: 3px 2px;
            font-size: 5.8pt;
            line-height: 1.05;
        }}

        .pdf-method-matrix td {{
            padding: 3px 2px;
        }}

        .pdf-list {{
            margin-top: 3px;
            margin-bottom: 6px;
            margin-left: 0;
            padding-left: 0;
        }}
        
        .pdf-list li {{
            list-style-type: none;
            display: block;
            margin-top: 0;
            margin-bottom: 2px;
            padding-left: 0;
        }}
        
        .pdf-list-row {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        .pdf-list-marker {{
            width: 18px;
            vertical-align: top;
            font-weight: bold;
            color: #0a1428;
            padding: 0 4px 0 0;
        }}
        
        .pdf-list-body {{
            vertical-align: top;
            padding: 0;
        }}
        
        .pdf-list-body p {{
            margin-top: 0;
            margin-bottom: 2px;
        }}

        .pdf-list-body .pdf-list {{
            margin-left: 16px;
            margin-bottom: 2px;
        }}


        li p {{
            display: inline;
            margin-top: 0;
            margin-bottom: 2px;
        }}

        .formula {{
            margin-top: 5px;
            margin-bottom: 7px;
            line-height: 1.25;
        }}
    </style>
    </head>
    <body>
        <div class="header">
            <img class="logo" src="{pdf_logo_src}">
            <div class="title">WSPRadar.org</div>
            <div class="subtitle">HAM RADIO STATION & ANTENNA BENCHMARKING<br><br><span style="font-size: 9pt; line-height: 1.3;">{dev_credit_pdf}</span></div>
        </div>
        {html_content}
        <div id="footerContent">
            WSPRadar {version} - {page_label} <pdf:pagenumber>
        </div>
    </body>
    </html>
    """
    result = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.StringIO(template), dest=result)
    return result.getvalue() if not pisa_status.err else None


@st.cache_data(show_spinner=False)
def generate_pdf_doc(lang, logo_b64, version):
    """Generate one shared cached PDF while serializing cache misses."""
    with _DOCUMENTATION_PDF_GENERATION_LOCK:
        return _generate_pdf_doc(lang, logo_b64, version)


def render_documentation_pdf_control(t, lang, logo_b64, version):
    """Prepare documentation on demand and expose its process-cached PDF."""
    ready_key = f"{DOCUMENTATION_PDF_READY_KEY_PREFIX}:{lang}:{version}"
    requested = bool(st.session_state.get(ready_key, False))
    if not requested:
        requested = st.button(
            t.get("btn_prepare_documentation_pdf", "Prepare PDF"),
            icon=":material/picture_as_pdf:",
            key=f"prepare_documentation_pdf_{lang}_{version}",
            width="stretch",
        )
        if not requested:
            return
        st.session_state[ready_key] = True

    with st.spinner(t.get(
        "msg_preparing_documentation_pdf",
        "Preparing documentation PDF...",
    )):
        pdf_bytes = generate_pdf_doc(lang, logo_b64, version)

    if not pdf_bytes:
        st.session_state.pop(ready_key, None)
        st.button(
            t.get("btn_download_documentation_pdf", "Download PDF"),
            icon=":material/picture_as_pdf:",
            disabled=True,
            help=t.get(
                "help_documentation_pdf_unavailable",
                "PDF export requires the documentation PDF dependencies.",
            ),
            width="stretch",
        )
        return

    st.download_button(
        label=t.get("btn_download_documentation_pdf", "Download PDF"),
        icon=":material/download:",
        data=pdf_bytes,
        file_name=f"WSPRadar_Doc_{lang.upper()}.pdf",
        mime="application/pdf",
        width="stretch",
    )
