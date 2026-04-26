"""
PDF Generator module.
Takes the Markdown documentation, fixes lists and LaTeX formulas, and renders via xhtml2pdf.
"""
import io
import base64
import re
import streamlit as st
from i18n import T

from docs.doc_de import DOC_DE
from docs.doc_en import DOC_EN


def get_docs(lang):
    """Return documentation for the selected language."""
    return DOC_DE if lang == "de" else DOC_EN


def _formula(html):
    return f'<p class="formula"><b>{html}</b></p>'


def _replace_pdf_math(md_text):
    """Replace LaTeX-like Markdown formulas with xhtml2pdf-safe HTML."""
    block_replacements = {
        r"SNR_{norm} = SNR_{measured} - P_{TX(dBm)} + 30": _formula(
            "SNR<sub>norm</sub> = SNR<sub>measured</sub> - "
            "P<sub>TX(dBm)</sub> + 30"
        ),
        r"\Delta SNR_{TX} = SNR_{norm,target} - SNR_{norm,reference}": _formula(
            "&Delta; SNR<sub>TX</sub> = SNR<sub>norm,target</sub> - "
            "SNR<sub>norm,reference</sub>"
        ),
        r"\Delta SNR_{RX} = SNR_{target} - SNR_{reference}": _formula(
            "&Delta; SNR<sub>RX</sub> = SNR<sub>target</sub> - "
            "SNR<sub>reference</sub>"
        ),
        r"\Delta SNR_{TX} = SNR_{norm,target} - SNR_{norm,benchmark}": _formula(
            "&Delta; SNR<sub>TX</sub> = SNR<sub>norm,target</sub> - "
            "SNR<sub>norm,benchmark</sub>"
        ),
        r"\Delta SNR_{RX} = SNR_{measured,target} - SNR_{measured,benchmark}": _formula(
            "&Delta; SNR<sub>RX</sub> = SNR<sub>measured,target</sub> - "
            "SNR<sub>measured,benchmark</sub>"
        ),
    }

    for latex, html in block_replacements.items():
        md_text = md_text.replace(f"$${latex}$$", html)
        md_text = md_text.replace(f"${latex}$", html)

    inline_replacements = {
        r"$\Delta$ SNR": "&Delta; SNR",
        r"$\Delta$": "&Delta;",
        r"$2^\circ \times 1^\circ$": "2&deg; &times; 1&deg;",
        r"$150 \times 111$": "150 &times; 111",
        r"$5' \times 2.5'$": "5&apos; &times; 2.5&apos;",
        r"$6 \times 4$": "6 &times; 4",
    }

    for latex, html in inline_replacements.items():
        md_text = md_text.replace(latex, html)

    return md_text


def _inject_pdf_list_markers(html_content):
    """xhtml2pdf can drop native list markers; inject stable table-based markers."""
    def convert_li(match):
        attrs = match.group(1) or ""
        body = match.group(2)
        return (
            f'<li{attrs}>'
            '<table class="pdf-list-row"><tr>'
            '<td class="pdf-list-marker">&bull;</td>'
            f'<td class="pdf-list-body">{body}</td>'
            '</tr></table>'
            '</li>'
        )

    def convert_ul(match):
        body = match.group(1)
        body = re.sub(r"<li([^>]*)>(.*?)</li>", convert_li, body, flags=re.DOTALL)
        return f'<ul class="pdf-list pdf-ul">{body}</ul>'

    def convert_ol(match):
        body = match.group(1)
        counter = 0

        def convert_numbered_li(li_match):
            nonlocal counter
            counter += 1
            attrs = li_match.group(1) or ""
            li_body = li_match.group(2)
            return (
                f'<li{attrs}>'
                '<table class="pdf-list-row"><tr>'
                f'<td class="pdf-list-marker">{counter}.</td>'
                f'<td class="pdf-list-body">{li_body}</td>'
                '</tr></table>'
                '</li>'
            )

        body = re.sub(r"<li([^>]*)>(.*?)</li>", convert_numbered_li, body, flags=re.DOTALL)
        return f'<ol class="pdf-list pdf-ol">{body}</ol>'

    html_content = re.sub(r"<ol>(.*?)</ol>", convert_ol, html_content, flags=re.DOTALL)
    html_content = re.sub(r"<ul>(.*?)</ul>", convert_ul, html_content, flags=re.DOTALL)

    return html_content



@st.cache_data(show_spinner=False)
def generate_pdf_doc(lang, logo_b64, version):
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

    md_text = get_docs(lang)
    md_text = md_text.replace("---", "", 1)

    # Python-Markdown requires a blank line before lists.
    md_text = re.sub(r"([^\n])\n(\s*\*)", r"\1\n\n\2", md_text)

    # xhtml2pdf cannot render MathJax/LaTeX, so replace formulas before Markdown parsing.
    md_text = _replace_pdf_math(md_text)

    html_content = markdown.markdown(md_text, extensions=["tables"])
    html_content = _inject_pdf_list_markers(html_content)

    dev_credit_pdf = T[lang]["dev_credit"].replace("#39ff14", "#0a318f")

    template = f"""
    <html>
    <head>
    <style>
        @page {{ size: a4 portrait; margin: 2cm;
                @frame footer {{ -pdf-frame-content: footerContent; bottom: 1cm; margin-left: 2cm; margin-right: 2cm; height: 1cm; text-align: right; font-size: 8pt; color: #999; }}
        }}

        body {{
            font-family: Helvetica, Arial, sans-serif;
            font-size: 10pt;
            color: #333;
            line-height: 1.35;
        }}

        p {{ margin-top: 0; margin-bottom: 6px; }}

        h1, h2, h3, h4 {{ color: #0a1428; }}

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

        th {{ text-align: left; background-color: #eee; padding: 4px; }}
        td {{ padding: 4px; border-bottom: 1px solid #eee; vertical-align: top; }}

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
            width: 12px;
            vertical-align: top;
            font-weight: bold;
            color: #0a1428;
            padding: 0;
        }}
        
        .pdf-list-body {{
            vertical-align: top;
            padding: 0;
        }}
        
        .pdf-list-body p {{
            margin-top: 0;
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
            WSPRadar {version} - Seite <pdf:pagenumber>
        </div>
    </body>
    </html>
    """
    result = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.StringIO(template), dest=result)
    return result.getvalue() if not pisa_status.err else None
