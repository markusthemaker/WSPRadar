"""Render the shared WSPRadar-owned header for authored comparison PDFs."""

from matplotlib.artist import Artist
from matplotlib.font_manager import FontProperties
from matplotlib.text import Text

from config.demo_pdf_headers import DEMO_PDF_HEADER_TITLE, DemoPdfHeader
from scripts.demo_pdf_footer import DEMO_PDF_FOOTER_TEXT


class _CenteredHeaderLine(Artist):
    """Position citation fragments using the active PDF or raster font metrics."""

    def __init__(self, figure, texts, baseline):
        super().__init__()
        self.set_figure(figure)
        self.texts = texts
        self.baseline = baseline
        self.set_zorder(3)

    def get_children(self):
        return list(self.texts)

    def draw(self, renderer):
        widths = [text.get_window_extent(renderer).width for text in self.texts]
        page_width = self.figure.bbox.width
        if sum(widths) > .92 * page_width:
            raise ValueError("Demo PDF header exceeds the page width")
        left = (page_width - sum(widths)) / 2
        for text, width in zip(self.texts, widths):
            text.set_position((left / page_width, self.baseline))
            text.draw(renderer)
            left += width
        self.stale = False


def add_demo_pdf_header(figure, header: DemoPdfHeader):
    """Draw five centered lines, grouping publication authors with their source.

    Measure each run with the active renderer so citation fragments cannot
    overlap when PDF font metrics differ from raster font hinting.
    All source text remains searchable vector text, with an explicit source link.
    """
    ink, muted = "#172B3A", "#526572"
    artists = []

    def add_line(segments, baseline, size, color, url):
        fonts = [FontProperties(family="DejaVu Sans", size=size, weight=weight, style=style)
                 for _, weight, style in segments]
        line_texts = []
        for (text, _, _), font in zip(segments, fonts):
            artist = Text(
                0, baseline, text,
                fontproperties=font, color=color, ha="left", va="baseline", url=url,
                transform=figure.transFigure,
            )
            artist.set_figure(figure)
            line_texts.append(artist)
            artists.append(artist)
        figure.add_artist(_CenteredHeaderLine(figure, tuple(line_texts), baseline))

    lines = (
        ([(DEMO_PDF_HEADER_TITLE, "bold", "normal")], ink, "https://wspradar.org"),
        ([(header.descriptive_title, "bold", "normal")], ink, None),
        ([(f"Referenced publication: {header.publication_authors}. ", "normal", "normal"),
          (f"{header.publication_title}.", "normal", "italic")], muted, header.publication_url),
        ([("Source figure: ", "normal", "normal"),
          (header.source_figure, "bold", "normal"),
          (f" · {header.publication_details}", "normal", "normal")], muted, header.publication_url),
        ([(f"Demo: {header.demo_details}", "normal", "normal")], muted, None),
    )
    for (segments, color, url), baseline, size in zip(lines, header.baselines, header.font_sizes):
        add_line(segments, baseline, size, color, url)
    return tuple(artists)


def demo_pdf_metadata(header: DemoPdfHeader):
    """Identify WSPRadar as the comparison author in PDF document properties."""
    return {
        "Title": f"{DEMO_PDF_HEADER_TITLE}: {header.descriptive_title}",
        "Author": DEMO_PDF_FOOTER_TEXT,
    }
