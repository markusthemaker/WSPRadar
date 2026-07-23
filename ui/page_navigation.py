"""Stable browser navigation between the application's top-level regions."""

from collections.abc import MutableMapping
from typing import Any
from uuid import uuid4

import streamlit as st


PAGE_TOP_ANCHOR_ID = "wspradar-page-top"
PARAMETER_SETTINGS_ANCHOR_ID = "wspradar-parameter-settings"
RESULTS_INSPECTION_ANCHOR_ID = "wspradar-results-inspection"
APPLICATION_ANCHOR_IDS = (
    PAGE_TOP_ANCHOR_ID,
    PARAMETER_SETTINGS_ANCHOR_ID,
    RESULTS_INSPECTION_ANCHOR_ID,
)
PAGE_NAVIGATION_CONTROLLER_KEY = "application_page_navigation_controller"
PAGE_NAVIGATION_REQUEST_KEY = "_application_page_navigation_request"

_PAGE_NAVIGATION_CONTROLLER_HTML = """
<span class="application-page-navigation-sentinel" aria-hidden="true"></span>
"""

_PAGE_NAVIGATION_CONTROLLER_CSS = """
:host {
    display: block;
    height: 1px;
    margin: 0;
    overflow: hidden;
    padding: 0;
}

.application-page-navigation-sentinel {
    display: block;
    height: 1px;
    pointer-events: none;
    width: 100%;
}
"""

_PAGE_NAVIGATION_CONTROLLER_JS = """
export default function(component) {
    const { data } = component;
    const applicationAnchorIds = Array.from(
        new Set(data?.anchorIds ?? [])
    );
    const allowedApplicationAnchors = new Set(applicationAnchorIds);
    const scrollContainer = (
        document.querySelector('[data-testid="stMain"]')
        ?? window
    );
    const pendingDocumentationAnchorProperty =
        '__wspradarPendingDocumentationAnchor';
    const requestedDocumentationAnchorProperty =
        '__wspradarRequestedDocumentationAnchor';
    const processedRequestTokenProperty =
        '__wspradarProcessedApplicationNavigationToken';
    const documentationSelector = '.st-key-documentation_body';

    function anchorIdFromHash(hash) {
        if (!hash || hash === '#') {
            return null;
        }
        try {
            return decodeURIComponent(hash.slice(1));
        } catch (_error) {
            return null;
        }
    }

    function isDocumentationAnchorId(anchorId) {
        return Boolean(
            anchorId === 'documentation-toc'
            || anchorId?.startsWith('part-')
            || anchorId?.startsWith('sec-')
            || anchorId?.startsWith('ref-')
        );
    }

    function clearPendingDocumentationNavigation() {
        window[pendingDocumentationAnchorProperty] = null;
        window[requestedDocumentationAnchorProperty] = null;
    }

    function replaceCurrentFragment(anchorId) {
        if (!allowedApplicationAnchors.has(anchorId)) {
            return;
        }
        const encodedHash = `#${encodeURIComponent(anchorId)}`;
        if (window.location.hash !== encodedHash) {
            window.history.replaceState(
                window.history.state,
                '',
                `${window.location.pathname}${window.location.search}${encodedHash}`
            );
        }
    }

    let scheduledScrollFrame = null;
    function scrollToApplicationAnchor(anchorId) {
        if (!allowedApplicationAnchors.has(anchorId)) {
            return false;
        }
        const target = document.getElementById(anchorId);
        if (!target) {
            return false;
        }
        if (scheduledScrollFrame !== null) {
            window.cancelAnimationFrame(scheduledScrollFrame);
        }
        scheduledScrollFrame = window.requestAnimationFrame(() => {
            scheduledScrollFrame = null;
            document.getElementById(anchorId)?.scrollIntoView({
                behavior: 'auto',
                block: 'start',
            });
        });
        return true;
    }

    let targetObserver = null;
    function scrollWhenApplicationAnchorMounts(anchorId) {
        if (scrollToApplicationAnchor(anchorId)) {
            return;
        }
        if (!('MutationObserver' in window)) {
            return;
        }
        targetObserver?.disconnect();
        targetObserver = new MutationObserver(() => {
            if (scrollToApplicationAnchor(anchorId)) {
                targetObserver.disconnect();
                targetObserver = null;
            }
        });
        targetObserver.observe(document.body, { childList: true, subtree: true });
    }

    function applicationActivationLine() {
        for (const anchorId of applicationAnchorIds) {
            const anchor = document.getElementById(anchorId);
            if (anchor) {
                return (
                    Number.parseFloat(
                        window.getComputedStyle(anchor).scrollMarginTop
                    ) || 0
                ) + 1;
            }
        }
        return 1;
    }

    function visibleApplicationAnchorId() {
        const activationLine = applicationActivationLine();
        const documentationContainer = document.querySelector(
            documentationSelector
        );
        if (
            documentationContainer
            && documentationContainer.getBoundingClientRect().top <= activationLine
        ) {
            // The documentation controller owns fragments from this boundary down.
            return null;
        }

        let visibleAnchorId = null;
        for (const anchorId of applicationAnchorIds) {
            const anchor = document.getElementById(anchorId);
            if (
                anchor
                && anchor.getBoundingClientRect().top <= activationLine
            ) {
                visibleAnchorId = anchorId;
            }
        }
        return visibleAnchorId;
    }

    function synchronizeVisibleApplicationAnchor() {
        if (window[pendingDocumentationAnchorProperty]) {
            return;
        }
        const visibleAnchorId = visibleApplicationAnchorId();
        if (!visibleAnchorId) {
            return;
        }

        const currentAnchorId = anchorIdFromHash(window.location.hash);
        if (
            currentAnchorId
            && !allowedApplicationAnchors.has(currentAnchorId)
            && !isDocumentationAnchorId(currentAnchorId)
        ) {
            // Preserve fragments outside the two WSPRadar-owned namespaces.
            return;
        }
        replaceCurrentFragment(visibleAnchorId);
    }

    let synchronizationFrame = null;
    function scheduleVisibleApplicationAnchorSynchronization() {
        if (synchronizationFrame !== null) {
            return;
        }
        synchronizationFrame = window.requestAnimationFrame(() => {
            synchronizationFrame = null;
            synchronizeVisibleApplicationAnchor();
        });
    }

    function handleHistoryNavigation() {
        const anchorId = anchorIdFromHash(window.location.hash);
        if (!allowedApplicationAnchors.has(anchorId)) {
            return;
        }
        clearPendingDocumentationNavigation();
        scrollWhenApplicationAnchorMounts(anchorId);
    }

    function handleInteractionBeforeRerun() {
        // Capture-phase synchronization runs before Streamlit handles a widget
        // click, so a stale manual fragment cannot survive into its rerun.
        synchronizeVisibleApplicationAnchor();
    }

    function handleRequestedNavigation() {
        const anchorId = data?.requestAnchorId;
        const requestToken = data?.requestToken;
        if (
            !allowedApplicationAnchors.has(anchorId)
            || !requestToken
            || window[processedRequestTokenProperty] === requestToken
        ) {
            return false;
        }

        window[processedRequestTokenProperty] = requestToken;
        clearPendingDocumentationNavigation();
        replaceCurrentFragment(anchorId);
        if (data?.shouldScrollRequest) {
            scrollWhenApplicationAnchorMounts(anchorId);
        }
        return true;
    }

    scrollContainer.addEventListener(
        'scroll',
        scheduleVisibleApplicationAnchorSynchronization,
        { passive: true }
    );
    window.addEventListener(
        'resize',
        scheduleVisibleApplicationAnchorSynchronization
    );
    window.addEventListener('hashchange', handleHistoryNavigation);
    window.addEventListener('popstate', handleHistoryNavigation);
    document.addEventListener('click', handleInteractionBeforeRerun, true);

    const didHandleRequest = handleRequestedNavigation();
    if (!didHandleRequest) {
        const initialAnchorId = anchorIdFromHash(window.location.hash);
        if (allowedApplicationAnchors.has(initialAnchorId)) {
            scrollWhenApplicationAnchorMounts(initialAnchorId);
        } else if (!initialAnchorId) {
            scheduleVisibleApplicationAnchorSynchronization();
        }
    }

    return () => {
        scrollContainer.removeEventListener(
            'scroll',
            scheduleVisibleApplicationAnchorSynchronization
        );
        window.removeEventListener(
            'resize',
            scheduleVisibleApplicationAnchorSynchronization
        );
        window.removeEventListener('hashchange', handleHistoryNavigation);
        window.removeEventListener('popstate', handleHistoryNavigation);
        document.removeEventListener(
            'click',
            handleInteractionBeforeRerun,
            true
        );
        targetObserver?.disconnect();
        if (scheduledScrollFrame !== null) {
            window.cancelAnimationFrame(scheduledScrollFrame);
        }
        if (synchronizationFrame !== null) {
            window.cancelAnimationFrame(synchronizationFrame);
        }
    };
}
"""

_PAGE_NAVIGATION_CONTROLLER = st.components.v2.component(
    "application_page_navigation_controller",
    html=_PAGE_NAVIGATION_CONTROLLER_HTML,
    css=_PAGE_NAVIGATION_CONTROLLER_CSS,
    js=_PAGE_NAVIGATION_CONTROLLER_JS,
)


def request_page_navigation(
    session_state: MutableMapping[str, Any],
    anchor_id: str,
    *,
    should_scroll: bool,
) -> None:
    """Queue one browser location update to an allowlisted application anchor."""
    if anchor_id not in APPLICATION_ANCHOR_IDS:
        raise ValueError(f"Unknown application anchor: {anchor_id!r}")
    session_state[PAGE_NAVIGATION_REQUEST_KEY] = {
        "anchor_id": anchor_id,
        "request_token": uuid4().hex,
        "should_scroll": bool(should_scroll),
    }


def consume_page_navigation_request(
    session_state: MutableMapping[str, Any],
) -> dict[str, Any] | None:
    """Remove and return one valid queued browser-location request."""
    request = session_state.pop(PAGE_NAVIGATION_REQUEST_KEY, None)
    if not isinstance(request, dict):
        return None
    anchor_id = request.get("anchor_id")
    request_token = request.get("request_token")
    if (
        anchor_id not in APPLICATION_ANCHOR_IDS
        or not isinstance(request_token, str)
        or not request_token
    ):
        return None
    return {
        "anchor_id": anchor_id,
        "request_token": request_token,
        "should_scroll": bool(request.get("should_scroll", False)),
    }


def render_page_anchor(anchor_id: str) -> None:
    """Render one inert, stable target for application-level navigation."""
    if anchor_id not in APPLICATION_ANCHOR_IDS:
        raise ValueError(f"Unknown application anchor: {anchor_id!r}")
    st.html(
        (
            f'<span id="{anchor_id}" class="wspradar-page-anchor" '
            'aria-hidden="true"></span>'
        )
    )


def render_page_navigation_controller(
    request: dict[str, Any] | None,
) -> None:
    """Mount the browser controller for coarse page anchors and one-shot requests."""
    _PAGE_NAVIGATION_CONTROLLER(
        data={
            "anchorIds": list(APPLICATION_ANCHOR_IDS),
            "requestAnchorId": (
                request["anchor_id"] if request is not None else None
            ),
            "requestToken": (
                request["request_token"] if request is not None else None
            ),
            "shouldScrollRequest": bool(
                request is not None and request["should_scroll"]
            ),
        },
        key=PAGE_NAVIGATION_CONTROLLER_KEY,
        width="stretch",
        height=1,
    )
