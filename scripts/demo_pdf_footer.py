"""Shared presentation credit for the authored demo comparison PDFs."""

from __future__ import annotations


DEMO_PDF_FOOTER_TEXT = "WSPRadar.org by Dr. Markus Brosch (DL1MKS)"


def add_demo_pdf_footer(figure, *, right=0.96, bottom=0.012):
    """Add a right-aligned credit at a baseline in figure-relative coordinates.

    Each builder chooses the baseline and right margin to fit its approved
    layout. The text, font and colour are shared across all demo PDFs.
    """
    return figure.text(
        right,
        bottom,
        DEMO_PDF_FOOTER_TEXT,
        ha="right",
        va="baseline",
        fontsize=12,
        fontfamily="DejaVu Sans",
        color="#142c45",
    )
