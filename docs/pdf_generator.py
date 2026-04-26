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

    # 1. List fix: Python-Markdown requires a blank line before lists.
    md_text = re.sub(r"([^\n])\n(\s*\*)", r"\1\n\n\2", md_text)

    # 2. Formula fix: xhtml2pdf cannot render MathJax, so replace formulas with HTML.
    math_replacements = {
        "$$SNR_{norm} = SNR_{measured} - P_{TX(dBm)} + 30$$": (
            '<p class="formula"><b>'
            'SNR<sub>norm</sub> = SNR<sub>measured</sub> - '
            'P<sub>TX(dBm)</sub> + 30'
            '</b></p>'
        ),
        r"$\Delta SNR_{TX} = SNR_{norm,target} - SNR_{norm,benchmark}$": (
            "<b>&Delta; SNR<sub>TX</sub> = "
            "SNR<sub>norm,target</sub> - SNR<sub>norm,benchmark</sub></b>"
        ),
        r"$\Delta SNR_{RX} = SNR_{measured,target} - SNR_{measured,benchmark}$": (
            "<b>&Delta; SNR<sub>RX</sub> = "
            "SNR<sub>measured,target</sub> - SNR<sub>measured,benchmark</sub></b>"
        ),
        r"$\Delta$ SNR": "&Delta; SNR",
        r"$\Delta$": "&Delta;",
        r"$2^\circ \times 1^\circ$": "2&deg; &times; 1&deg;",
        r"$150 \times 111$": "150 &times; 111",
        r"$5' \times 2.5'$": "5&apos; &times; 2.5&apos;",
        r"$6 \times 4$": "6 &times; 4",
    }
    for latex, html in math_replacements.items():
        md_text = md_text.replace(latex, html)

    html_content = markdown.markdown(md_text, extensions=["tables"])

    # Use the localized credit, but switch neon green to print-friendly dark blue.
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

        p {{
            margin-top: 0;
            margin-bottom: 6px;
        }}

        h1, h2, h3, h4 {{
            color: #0a1428;
        }}

        h1 {{
            margin-top: 18px;
            margin-bottom: 8px;
        }}

        h2 {{
            margin-top: 16px;
            margin-bottom: 7px;
        }}

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

        .header {{
            text-align: center;
            margin-bottom: 22px;
        }}

        .logo {{
            width: 90px;
            margin-bottom: 10px;
        }}

        .title {{
            font-size: 24pt;
            font-weight: bold;
            margin: 0;
            color: #000;
            letter-spacing: 1px;
        }}

        .subtitle {{
            font-size: 11pt;
            color: #666;
            margin-top: 5px;
        }}

        code {{
            font-family: Courier, monospace;
            background-color: #f4f4f4;
            padding: 2px 4px;
            font-size: 9pt;
            border-radius: 3px;
        }}

        th {{
            text-align: left;
            background-color: #eee;
            padding: 4px;
        }}

        td {{
            padding: 4px;
            border-bottom: 1px solid #eee;
            vertical-align: top;
        }}

        ul, ol {{
            margin-top: 3px;
            margin-bottom: 6px;
            padding-left: 16px;
        }}

        li {{
            margin-top: 0;
            margin-bottom: 2px;
        }}

        li p {{
            margin-top: 0;
            margin-bottom: 2px;
        }}

        .formula {{
            margin-top: 6px;
            margin-bottom: 8px;
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
