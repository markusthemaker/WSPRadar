import pytest

from ui import share_analysis, url_synchronizer


def _share_labels():
    return {
        "url_field": "Analysis URL",
        "copy_link": "Copy Link",
        "copied": "Link copied.",
        "manual_copy": "Select and copy the URL.",
        "native_share": "Share\u2026",
        "native_share_failed": "Sharing failed; copy the selected URL.",
        "email": "Email",
        "whatsapp": "WhatsApp",
        "x": "X",
        "facebook": "Facebook",
        "linkedin": "LinkedIn",
    }


def test_query_synchronizer_replaces_only_owned_entries_in_canonical_order(monkeypatch):
    component_calls = []
    monkeypatch.setattr(
        url_synchronizer,
        "_URL_QUERY_SYNCHRONIZER",
        lambda **kwargs: component_calls.append(kwargs),
    )

    url_synchronizer.render_url_query_synchronizer(
        (("v", "1"), ("direction", "RX"), ("run", "1")),
        owned_keys=("v", "run", "direction", "ranges"),
        key="query-sync-test",
    )

    assert component_calls == [
        {
            "data": {
                "ownedKeys": ["v", "run", "direction", "ranges"],
                "entries": [
                    ["v", "1"],
                    ["direction", "RX"],
                    ["run", "1"],
                ],
            },
            "key": "query-sync-test",
            "width": "stretch",
            "height": 1,
        }
    ]


@pytest.mark.parametrize(
    ("entries", "owned_keys"),
    [
        ((("v", "1"),), "v"),
        ((("v", "1"),), ("v", "v")),
        ((("unowned", "1"),), ("v",)),
        ((("v", 1),), ("v",)),
        ((("v",),), ("v",)),
    ],
)
def test_query_synchronizer_rejects_malformed_or_unowned_payloads(
    entries,
    owned_keys,
):
    with pytest.raises(ValueError):
        url_synchronizer.render_url_query_synchronizer(
            entries,
            owned_keys=owned_keys,
        )


def test_query_synchronizer_preserves_navigation_and_avoids_redundant_history():
    javascript = url_synchronizer._URL_QUERY_SYNCHRONIZER_JS

    assert "new URLSearchParams(window.location.search)" in javascript
    assert "searchParameters.delete(ownedKey)" in javascript
    assert "searchParameters.append(key, value)" in javascript
    assert "window.location.pathname" in javascript
    assert "window.location.hash" in javascript
    assert "nextRelativeUrl !== currentRelativeUrl" in javascript
    assert "window.history.replaceState" in javascript
    assert javascript.count("window.history.replaceState") == 1
    assert "window.history.pushState" not in javascript
    assert "addEventListener" not in javascript


def test_share_browser_passes_validated_data_without_source_interpolation(monkeypatch):
    component_calls = []
    monkeypatch.setattr(
        share_analysis,
        "_SHARE_ANALYSIS_BROWSER",
        lambda **kwargs: component_calls.append(kwargs),
    )
    labels = _share_labels()
    share_url = (
        "https://wspradar.org/?v=1&target=DL1MKS&run=1"
        "#wspradar-results-inspection"
    )

    share_analysis.render_share_analysis_browser(
        share_url=share_url,
        title="WSPRadar analysis: DL1MKS RX Hardware A/B on 20 m",
        message="Re-run this WSPRadar analysis.",
        labels=labels,
        key="share-analysis-test",
    )

    assert component_calls == [
        {
            "data": {
                "shareUrl": share_url,
                "title": "WSPRadar analysis: DL1MKS RX Hardware A/B on 20 m",
                "message": "Re-run this WSPRadar analysis.",
                "labels": labels,
            },
            "key": "share-analysis-test",
            "width": "stretch",
            "height": "content",
        }
    ]
    assert share_url not in share_analysis._SHARE_ANALYSIS_BROWSER_HTML
    assert share_url not in share_analysis._SHARE_ANALYSIS_BROWSER_JS


@pytest.mark.parametrize(
    "share_url",
    [
        "http://wspradar.org/?v=1",
        "/?v=1",
        "https://user@example.com/?v=1",
        "https://wspradar.org/?v=1\nrun=1",
    ],
)
def test_share_browser_rejects_noncanonical_transport_urls(share_url):
    with pytest.raises(ValueError):
        share_analysis.render_share_analysis_browser(
            share_url=share_url,
            title="WSPRadar analysis",
            message="Re-run this analysis.",
            labels=_share_labels(),
            key="share-analysis-test",
        )


def test_share_browser_requires_every_visible_label():
    labels = _share_labels()
    del labels["manual_copy"]

    with pytest.raises(ValueError, match="manual_copy"):
        share_analysis.render_share_analysis_browser(
            share_url="https://wspradar.org/?v=1",
            title="WSPRadar analysis",
            message="Re-run this analysis.",
            labels=labels,
            key="share-analysis-test",
        )


def test_share_browser_always_exposes_copy_and_manual_selection_fallbacks():
    html = share_analysis._SHARE_ANALYSIS_BROWSER_HTML
    javascript = share_analysis._SHARE_ANALYSIS_BROWSER_JS

    assert 'data-role="url-field"' in html
    assert "readonly" in html
    assert 'data-action="copy"' in html
    assert "navigator.clipboard?.writeText" in javascript
    assert "urlField.select()" in javascript
    assert "urlField.setSelectionRange(0, urlField.value.length)" in javascript
    assert "document.execCommand('copy')" in javascript
    assert "showStatus(labels.manual_copy)" in javascript


def test_share_browser_capability_gates_native_share_and_secures_direct_links():
    html = share_analysis._SHARE_ANALYSIS_BROWSER_HTML
    javascript = share_analysis._SHARE_ANALYSIS_BROWSER_JS

    assert "typeof navigator.share !== 'function'" in javascript
    assert "await navigator.share({" in javascript
    assert 'data-action="native-share"' in html
    assert 'target="_blank" rel="noopener noreferrer"' in html
    for channel in ("email", "whatsapp", "x", "facebook", "linkedin"):
        assert f'data-share-channel="{channel}"' in html
        assert f"{channel}:" in javascript


def test_share_browser_uses_standard_url_encoding_without_scripts_or_trackers():
    html = share_analysis._SHARE_ANALYSIS_BROWSER_HTML
    javascript = share_analysis._SHARE_ANALYSIS_BROWSER_JS

    assert "new URL(baseUrl)" in javascript
    assert "target.searchParams.set(key, value)" in javascript
    assert "'mailto:'" in javascript
    assert "'https://wa.me/'" in javascript
    assert "'https://x.com/intent/post'" in javascript
    assert "'https://www.facebook.com/sharer/sharer.php'" in javascript
    assert "'https://www.linkedin.com/sharing/share-offsite/'" in javascript
    assert "innerHTML" not in javascript
    assert "fetch(" not in javascript
    assert "XMLHttpRequest" not in javascript
    assert "<script" not in html.lower()
