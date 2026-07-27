"""Render safe browser-native controls for sharing one canonical analysis URL."""

from collections.abc import Mapping
from urllib.parse import urlsplit

import streamlit as st


SHARE_ANALYSIS_LABEL_KEYS = (
    "url_field",
    "copy_link",
    "copied",
    "manual_copy",
    "native_share",
    "native_share_failed",
    "email",
    "whatsapp",
    "x",
    "facebook",
    "linkedin",
)

_SHARE_ANALYSIS_BROWSER_HTML = """
<div class="share-analysis-browser">
    <label class="share-analysis-url-label">
        <span data-role="url-label"></span>
        <input
            data-role="url-field"
            type="text"
            readonly
            spellcheck="false"
            autocomplete="off"
        >
    </label>
    <div class="share-analysis-primary-actions">
        <button data-action="copy" type="button"></button>
        <button data-action="native-share" type="button" hidden></button>
    </div>
    <div class="share-analysis-direct-actions">
        <a data-share-channel="email" target="_blank" rel="noopener noreferrer"></a>
        <a data-share-channel="whatsapp" target="_blank" rel="noopener noreferrer"></a>
        <a data-share-channel="x" target="_blank" rel="noopener noreferrer"></a>
        <a data-share-channel="facebook" target="_blank" rel="noopener noreferrer"></a>
        <a data-share-channel="linkedin" target="_blank" rel="noopener noreferrer"></a>
    </div>
    <p data-role="status" role="status" aria-live="polite" hidden></p>
</div>
"""

_SHARE_ANALYSIS_BROWSER_CSS = """
:host {
    display: block;
    width: 100%;
}

.share-analysis-browser {
    box-sizing: border-box;
    color: var(--text-color);
    display: grid;
    gap: 0.65rem;
    width: 100%;
}

.share-analysis-url-label {
    display: grid;
    font-size: 0.875rem;
    gap: 0.3rem;
}

[data-role="url-field"] {
    background: var(--secondary-background-color);
    border: 1px solid color-mix(in srgb, var(--text-color) 25%, transparent);
    border-radius: 0.5rem;
    box-sizing: border-box;
    color: var(--text-color);
    font: inherit;
    padding: 0.45rem 0.6rem;
    user-select: text;
    width: 100%;
}

.share-analysis-primary-actions,
.share-analysis-direct-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem;
}

.share-analysis-primary-actions button,
.share-analysis-direct-actions a {
    align-items: center;
    background: var(--secondary-background-color);
    border: 1px solid color-mix(in srgb, var(--text-color) 25%, transparent);
    border-radius: 0.5rem;
    box-sizing: border-box;
    color: var(--text-color);
    cursor: pointer;
    display: inline-flex;
    font: inherit;
    font-size: 0.875rem;
    justify-content: center;
    min-height: 2.25rem;
    padding: 0.35rem 0.7rem;
    text-decoration: none;
}

.share-analysis-primary-actions button:hover,
.share-analysis-direct-actions a:hover {
    border-color: var(--primary-color);
    color: var(--primary-color);
}

[data-role="status"] {
    font-size: 0.8rem;
    margin: 0;
}

[hidden] {
    display: none !important;
}
"""

_SHARE_ANALYSIS_BROWSER_JS = """
export default function(component) {
    const { data, parentElement } = component;
    const labels = data?.labels ?? {};
    const shareUrl = data?.shareUrl ?? '';
    const shareTitle = data?.title ?? '';
    const shareMessage = data?.message ?? '';
    const urlLabel = parentElement.querySelector('[data-role="url-label"]');
    const urlField = parentElement.querySelector('[data-role="url-field"]');
    const copyButton = parentElement.querySelector('[data-action="copy"]');
    const nativeShareButton = parentElement.querySelector(
        '[data-action="native-share"]'
    );
    const status = parentElement.querySelector('[data-role="status"]');

    urlLabel.textContent = labels.url_field;
    urlField.value = shareUrl;
    urlField.setAttribute('aria-label', labels.url_field);
    copyButton.textContent = labels.copy_link;
    copyButton.setAttribute('aria-label', labels.copy_link);
    nativeShareButton.textContent = labels.native_share;
    nativeShareButton.setAttribute('aria-label', labels.native_share);
    nativeShareButton.hidden = typeof navigator.share !== 'function';

    function selectUrlForManualCopy() {
        urlField.focus();
        urlField.select();
        urlField.setSelectionRange(0, urlField.value.length);
    }

    function showStatus(message) {
        status.textContent = message;
        status.hidden = false;
    }

    async function copyShareUrl() {
        selectUrlForManualCopy();
        if (navigator.clipboard?.writeText) {
            try {
                await navigator.clipboard.writeText(shareUrl);
                showStatus(labels.copied);
                return;
            } catch (_error) {
                // Continue to the browser's legacy copy path and manual selection.
            }
        }

        try {
            if (document.execCommand('copy')) {
                showStatus(labels.copied);
                return;
            }
        } catch (_error) {
            // The selected read-only field remains available for manual copying.
        }
        selectUrlForManualCopy();
        showStatus(labels.manual_copy);
    }

    async function shareWithBrowser() {
        try {
            await navigator.share({
                title: shareTitle,
                text: shareMessage,
                url: shareUrl,
            });
        } catch (error) {
            if (error?.name !== 'AbortError') {
                selectUrlForManualCopy();
                showStatus(labels.native_share_failed);
            }
        }
    }

    function buildShareTarget(baseUrl, queryEntries) {
        const target = new URL(baseUrl);
        for (const [key, value] of queryEntries) {
            target.searchParams.set(key, value);
        }
        return target.toString();
    }

    const messageWithUrl = [shareMessage, shareUrl]
        .filter(Boolean)
        .join('\\n\\n');
    const shareTargets = {
        email: buildShareTarget('mailto:', [
            ['subject', shareTitle],
            ['body', messageWithUrl],
        ]),
        whatsapp: buildShareTarget('https://wa.me/', [
            ['text', messageWithUrl],
        ]),
        x: buildShareTarget('https://x.com/intent/post', [
            ['text', shareMessage],
            ['url', shareUrl],
        ]),
        facebook: buildShareTarget(
            'https://www.facebook.com/sharer/sharer.php',
            [['u', shareUrl]]
        ),
        linkedin: buildShareTarget(
            'https://www.linkedin.com/sharing/share-offsite/',
            [['url', shareUrl]]
        ),
    };

    for (const [channel, target] of Object.entries(shareTargets)) {
        const link = parentElement.querySelector(
            `[data-share-channel="${channel}"]`
        );
        link.href = target;
        link.textContent = labels[channel];
        link.setAttribute('aria-label', labels[channel]);
        link.setAttribute('title', labels[channel]);
    }

    copyButton.addEventListener('click', copyShareUrl);
    if (typeof navigator.share === 'function') {
        nativeShareButton.addEventListener('click', shareWithBrowser);
    }

    return () => {
        copyButton.removeEventListener('click', copyShareUrl);
        nativeShareButton.removeEventListener('click', shareWithBrowser);
    };
}
"""

_SHARE_ANALYSIS_BROWSER = st.components.v2.component(
    "wspradar_share_analysis_browser",
    html=_SHARE_ANALYSIS_BROWSER_HTML,
    css=_SHARE_ANALYSIS_BROWSER_CSS,
    js=_SHARE_ANALYSIS_BROWSER_JS,
)


def _normalize_share_browser_payload(
    share_url: str,
    title: str,
    message: str,
    labels: Mapping[str, str],
) -> dict[str, object]:
    """Validate the data-only boundary used by the static browser component."""
    if (
        not isinstance(share_url, str)
        or any(character.isspace() for character in share_url)
    ):
        raise ValueError("The canonical share URL must be a whitespace-free string.")
    parsed_share_url = urlsplit(share_url)
    if (
        parsed_share_url.scheme != "https"
        or not parsed_share_url.netloc
        or parsed_share_url.username is not None
        or parsed_share_url.password is not None
    ):
        raise ValueError("The canonical share URL must be an absolute HTTPS URL.")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("The localized share title must be a non-empty string.")
    if not isinstance(message, str) or not message.strip():
        raise ValueError("The localized share message must be a non-empty string.")
    if not isinstance(labels, Mapping):
        raise ValueError("Share labels must be provided as a mapping.")

    normalized_labels: dict[str, str] = {}
    for label_key in SHARE_ANALYSIS_LABEL_KEYS:
        label = labels.get(label_key)
        if not isinstance(label, str) or not label.strip():
            raise ValueError(f"Missing localized Share Analysis label: {label_key!r}")
        normalized_labels[label_key] = label

    return {
        "shareUrl": share_url,
        "title": title,
        "message": message,
        "labels": normalized_labels,
    }


def render_share_analysis_browser(
    *,
    share_url: str,
    title: str,
    message: str,
    labels: Mapping[str, str],
    key: str,
) -> None:
    """Mount copy, native-share, and direct-share controls for one canonical URL."""
    component_data = _normalize_share_browser_payload(
        share_url,
        title,
        message,
        labels,
    )
    _SHARE_ANALYSIS_BROWSER(
        data=component_data,
        key=key,
        width="stretch",
        height="content",
    )
