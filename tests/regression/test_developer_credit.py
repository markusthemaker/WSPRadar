from html.parser import HTMLParser

import pytest

from i18n import T


QRZ_PROFILE_URL = "https://www.qrz.com/db/DL1MKS"


class _DeveloperCreditParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.anchors = []
        self._active_anchor = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "a":
            self._active_anchor = {
                "attributes": attributes,
                "text_parts": [],
                "spans": [],
                "images": [],
            }
        elif self._active_anchor is not None and tag == "span":
            self._active_anchor["spans"].append(attributes)
        elif self._active_anchor is not None and tag == "img":
            self._active_anchor["images"].append(attributes)

    def handle_data(self, data):
        if self._active_anchor is not None:
            self._active_anchor["text_parts"].append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._active_anchor is not None:
            self._active_anchor["text"] = "".join(
                self._active_anchor.pop("text_parts")
            )
            self.anchors.append(self._active_anchor)
            self._active_anchor = None


@pytest.mark.parametrize(
    ("language", "accessible_label"),
    [
        ("en", "DL1MKS on QRZ.com (opens in a new tab)"),
        ("de", "DL1MKS auf QRZ.com (öffnet in einem neuen Tab)"),
    ],
)
def test_developer_credit_links_callsign_to_qrz_with_dark_safe_external_icon(
    language,
    accessible_label,
):
    parser = _DeveloperCreditParser()
    parser.feed(T[language]["dev_credit"])
    qrz_link = next(
        anchor
        for anchor in parser.anchors
        if anchor["attributes"].get("href") == QRZ_PROFILE_URL
    )

    assert qrz_link["attributes"]["target"] == "_blank"
    assert set(qrz_link["attributes"]["rel"].split()) == {
        "noopener",
        "noreferrer",
    }
    assert qrz_link["attributes"]["aria-label"] == accessible_label
    assert qrz_link["text"] == "DL1MKS↗"
    assert qrz_link["images"] == []
    assert len(qrz_link["spans"]) == 1

    icon_attributes = qrz_link["spans"][0]
    icon_style = icon_attributes["style"].replace(" ", "")
    assert icon_attributes["aria-hidden"] == "true"
    assert "color:#39ff14" in icon_style
    assert "display:inline-block" in icon_style
    assert "font-size:0.95em" in icon_style
    assert "font-weight:700" in icon_style
    assert "background" not in icon_style
