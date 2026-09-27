"""Authorship, citation and layout contracts for the published demo PDFs."""

from pathlib import Path
import unicodedata

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from pypdf import PdfReader
import pytest

from config.demo_pdf_headers import DEMO_PDF_HEADERS
from core.matplotlib_runtime import matplotlib_operation_lock
from scripts.internal.demo_pdf_header import add_demo_pdf_header
from scripts.internal.sync_reference_figure_pdfs import collect_reference_pdf_paths


ROOT = Path(__file__).resolve().parents[2]
PUBLISHED_HEADERS = {
    "griffiths_fig3_paper_v1/WSPRadar_Demo_Griffiths_Figure3.pdf": "griffiths_figure3",
    "griffiths_fig3_paper_v1/WSPRadar_Demo_Griffiths_Figure3_diagnostic.pdf": "griffiths_figure3_diagnostic",
    "griffiths_fig6_paper_v1/WSPRadar_Demo_Griffiths_Figure6.pdf": "griffiths_figure6",
    "zander_fig4_paper_v1/WSPRadar_Demo_Zander_Figure4.pdf": "zander_figure4",
    "vanhamel_fig6_rotation_v1/WSPRadar_Demo_Vanhamel_Figure6.pdf": "vanhamel_figure6",
    "milazzo_publication_overlays_v1/WSPRadar_Demo_Milazzo_Figure6.pdf": "milazzo_figure6",
    "milazzo_publication_overlays_v1/WSPRadar_Demo_Milazzo_Figure7.pdf": "milazzo_figure7",
}


def normalized_text(text):
    # PDF kerning can make extractors insert spaces inside words ("T arget")
    # or before punctuation ("F ."). Renderer bounds check spacing separately.
    return "".join(unicodedata.normalize("NFKC", text).split())


def test_every_linked_demo_pdf_has_a_reviewed_header_contract():
    assert {path.as_posix() for path in collect_reference_pdf_paths(ROOT / "config/demos")} == set(PUBLISHED_HEADERS)
    assert set(PUBLISHED_HEADERS.values()) == set(DEMO_PDF_HEADERS)


@pytest.mark.parametrize("relative_path,header_key", PUBLISHED_HEADERS.items())
def test_published_comparison_identifies_wspradar_and_labels_its_source(relative_path, header_key):
    header = DEMO_PDF_HEADERS[header_key]
    document = PdfReader(ROOT / "static/reference_figures" / relative_path)
    assert len(document.pages) == 1
    text = normalized_text(document.pages[0].extract_text())
    assert normalized_text("WSPRadar.org reconstruction & comparison") in text
    assert normalized_text(header.descriptive_title) in text
    assert normalized_text(f"Referenced publication: {header.publication_authors}.") in text
    assert normalized_text(header.publication_title) in text
    assert normalized_text(f"Source figure: {header.source_figure}") in text
    assert normalized_text(header.publication_details) in text
    assert normalized_text(f"Demo: {header.demo_details}") in text
    assert document.metadata.author == "WSPRadar.org by Dr. Markus Brosch (DL1MKS)"
    assert document.metadata.title.startswith("WSPRadar.org reconstruction & comparison:")
    links = {annotation.get_object().get("/A", {}).get("/URI")
             for annotation in document.pages[0].get("/Annots", [])}
    assert header.publication_url in links
    assert "https://wspradar.org" in links


@pytest.mark.parametrize("relative_path,header_key", PUBLISHED_HEADERS.items())
def test_header_lines_fit_the_existing_page_without_overlap(relative_path, header_key):
    header = DEMO_PDF_HEADERS[header_key]
    page = PdfReader(ROOT / "static/reference_figures" / relative_path).pages[0]
    with matplotlib_operation_lock():
        figure = Figure(figsize=(float(page.mediabox.width) / 72, float(page.mediabox.height) / 72), dpi=100)
        FigureCanvasAgg(figure)
        artists = add_demo_pdf_header(figure, header)
        figure.canvas.draw()
        renderer = figure.canvas.get_renderer()
        line_bounds = {}
        for artist in artists:
            bounds = artist.get_window_extent(renderer)
            assert 0 <= bounds.x0 < bounds.x1 <= figure.bbox.width
            assert 0 <= bounds.y0 < bounds.y1 <= figure.bbox.height
            baseline = artist.get_position()[1]
            line_bounds.setdefault(baseline, []).append(bounds)
        previous_bottom = figure.bbox.height
        for baseline in sorted(line_bounds, reverse=True):
            bounds = line_bounds[baseline]
            assert max(bound.y1 for bound in bounds) < previous_bottom
            ordered_bounds = sorted(bounds, key=lambda bound: bound.x0)
            for left, right in zip(ordered_bounds, ordered_bounds[1:]):
                assert left.x1 <= right.x0 + .01
            previous_bottom = min(bound.y0 for bound in bounds)
        figure.clear()
