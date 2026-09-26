"""Presentation-only titles, citations and layouts for authored demo PDFs.

These records describe the evidence rendered by each comparison builder. They
do not select observations or alter the runnable demo configurations.
"""

from dataclasses import dataclass


DEMO_PDF_HEADER_TITLE = "WSPRadar.org reconstruction & comparison"


@dataclass(frozen=True)
class DemoPdfHeader:
    """A complete source-labelled header with five figure-relative baselines."""

    descriptive_title: str
    publication_authors: str
    publication_title: str
    source_figure: str
    publication_details: str
    demo_details: str
    publication_url: str
    baselines: tuple[float, float, float, float, float]
    font_sizes: tuple[float, float, float, float, float]


GRIFFITHS_PUBLICATION = {
    "publication_authors": "Gwyn Griffiths (G3ZIL) and Nigel Squibb (G4HZX) (2017)",
    "publication_title": "Improving HF Band SNR",
    "publication_details": "Practical Wireless, October 2017, pp. 23-26",
    "publication_url": "https://www.wsprnet.org/drupal/sites/wsprnet.org/files/G3ZIL%20G4HZX%20WSPR%20Improving%20HF%20SNR-print.pdf",
}

MILAZZO_PUBLICATION = {
    "publication_authors": "Carol F. Milazzo / KP4MD (2011)",
    "publication_title": "Using the Weak Signal Propagation Reporter Network to Compare Antenna Performance",
    "publication_details": "Amateur-radio technical article and club presentation · 2011",
    "publication_url": "https://www.qsl.net/kp4md/wspr.htm",
    "demo_details": "19 December 2010 12:00-20 December 2010 20:00 UTC · 40 m · Target KP4MD − Reference WB6RQN",
    "baselines": (.966, .940, .916, .894, .872),
    "font_sizes": (27, 20, 14, 14, 14),
}


DEMO_PDF_HEADERS = {
    "griffiths_figure3": DemoPdfHeader(
        descriptive_title="SNR differences over time",
        source_figure="Figure 3, p. 24",
        demo_details="April 2017  |  40 m  |  ΔSNR = G3ZIL − G4HZX  |  57,767 paired observations",
        baselines=(.967, .938, .912, .890, .868),
        font_sizes=(25, 19, 13, 12, 11),
        **GRIFFITHS_PUBLICATION,
    ),
    "griffiths_figure3_diagnostic": DemoPdfHeader(
        descriptive_title="Pairing and duplicate reports",
        source_figure="Figure 3, p. 24",
        demo_details="16 April 2017  |  40 m  |  ΔSNR = G3ZIL − G4HZX  |  Displayed range: 0 to −20 dB",
        baselines=(.967, .938, .912, .890, .868),
        font_sizes=(25, 19, 13, 12, 11),
        **GRIFFITHS_PUBLICATION,
    ),
    "griffiths_figure6": DemoPdfHeader(
        descriptive_title="SNR difference by time of day",
        source_figure="Figure 6, p. 25",
        demo_details="5-7 April 2017  |  40 m  |  ΔSNR = G3ZIL − G4HZX  |  B/C: 6,459 paired observations",
        baselines=(.965, .927, .890, .860, .829),
        font_sizes=(27, 21, 14, 14, 14),
        **GRIFFITHS_PUBLICATION,
    ),
    "zander_figure4": DemoPdfHeader(
        descriptive_title="SNR differences between a short portable vertical and a reference vertical",
        publication_authors="Zander, J. (2022)",
        publication_title="Simple HF antenna efficiency comparisons using the WSPR system",
        source_figure="Figure 4, p. 4",
        publication_details="arXiv:2209.08989v1 · 19 September 2022",
        demo_details="Experiment A · 21 May 2022, 09:30-10:30 UTC · 20 m (14 MHz) · Target SK0WE/P − Reference SK0WE/1 · JO97",
        publication_url="https://arxiv.org/abs/2209.08989v1",
        baselines=(.959, 960.1504 / 1036.8, 923 / 1036.8, 897.9928 / 1036.8, .842),
        font_sizes=(27, 21, 14, 13, 13),
    ),
    "vanhamel_figure6": DemoPdfHeader(
        descriptive_title="Antenna rotation: from individual receptions to 12-hour evidence",
        publication_authors="J. Vanhamel, W. Machiels and H. Lamy (2022)",
        publication_title="Using the WSPR Mode for Antenna Performance Evaluation and Propagation Assessment on the 160-m Band",
        source_figure="Figure 6, p. 6",
        publication_details="International Journal of Antennas and Propagation (2022), Article 4809313",
        demo_details="160 m | 1-15 May 2021 | M7AEO (IO82) to ON4AWM0 / ON4AWM1 | 1,441 Joint Spots | Reference correction +1.6 dB",
        publication_url="https://doi.org/10.1155/2022/4809313",
        baselines=tuple(baseline / (20.2125 * 72) for baseline in (1415, 1378, 1346.49, 1323.39, 1300.29)),
        font_sizes=(27, 20, 15, 15, 15),
    ),
    "milazzo_figure6": DemoPdfHeader(
        descriptive_title="Reconciled RX direction: VE6PDQ transmitting to KP4MD / WB6RQN",
        source_figure="Figure 6",
        **MILAZZO_PUBLICATION,
    ),
    "milazzo_figure7": DemoPdfHeader(
        descriptive_title="Reconciled TX direction: KP4MD / WB6RQN transmitting to VE6PDQ",
        source_figure="Figure 7",
        **MILAZZO_PUBLICATION,
    ),
}
