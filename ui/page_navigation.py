"""Stable browser navigation between the application's top-level regions."""

from collections.abc import MutableMapping
from html import escape
import re
from typing import Any
from uuid import uuid4

import streamlit as st


PAGE_TOP_ANCHOR_ID = "wspradar-page-top"
PARAMETER_SETTINGS_ANCHOR_ID = "wspradar-parameter-settings"
RESULTS_INSPECTION_ANCHOR_ID = "wspradar-results-inspection"
MAP_RESULTS_ANCHOR_ID = "wspradar-map-results"
STATION_INSIGHTS_ANCHOR_ID = "wspradar-station-insights"
DRILLDOWN_ANCHOR_ID = "wspradar-drilldown"
APPLICATION_ANCHOR_IDS = (
    PAGE_TOP_ANCHOR_ID,
    PARAMETER_SETTINGS_ANCHOR_ID,
    RESULTS_INSPECTION_ANCHOR_ID,
    MAP_RESULTS_ANCHOR_ID,
    STATION_INSIGHTS_ANCHOR_ID,
    DRILLDOWN_ANCHOR_ID,
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
    const processedInitialAnchorProperty =
        '__wspradarProcessedInitialApplicationAnchor';
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
        // The user is already inside this region. A later component remount
        // must not reinterpret its passively tracked fragment as a deep link.
        window[processedInitialAnchorProperty] = visibleAnchorId;
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
        cancelAnalysisNavigation();
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
        window[processedInitialAnchorProperty] = anchorId;
        clearPendingDocumentationNavigation();
        replaceCurrentFragment(anchorId);
        if (data?.shouldScrollRequest) {
            scrollWhenApplicationAnchorMounts(anchorId);
        }
        return true;
    }

    const analysisNavigationStateProperty =
        '__wspradarAnalysisNavigationState';
    const submissionToken = data?.analysisSubmissionToken;
    let analysisState = null;
    const previousAnalysisState = window[analysisNavigationStateProperty];
    if (submissionToken) {
        if (previousAnalysisState?.token === submissionToken) {
            analysisState = previousAnalysisState;
        } else {
            analysisState = {
                token: submissionToken,
                statusScrolled: false,
                mapScrolled: false,
                cancelled: false,
            };
            // Keep only the latest submission; completed run history is not
            // retained in the browser or allowed to re-arm an old observer.
            window[analysisNavigationStateProperty] = analysisState;
        }
    } else if (previousAnalysisState && !previousAnalysisState.mapScrolled) {
        previousAnalysisState.cancelled = true;
    }

    let analysisObserver = null;
    let analysisScrollFrame = null;
    let observedMapImage = null;

    function analysisNavigationIsActive() {
        return Boolean(
            analysisState
            && window[analysisNavigationStateProperty] === analysisState
            && !analysisState.cancelled
            && !analysisState.mapScrolled
        );
    }

    function detachMapImageListeners() {
        if (observedMapImage) {
            observedMapImage.removeEventListener('load', scheduleAnalysisNavigation);
            observedMapImage.removeEventListener('error', scheduleAnalysisNavigation);
            observedMapImage = null;
        }
    }

    function stopAnalysisNavigationObservation() {
        analysisObserver?.disconnect();
        analysisObserver = null;
        detachMapImageListeners();
        if (analysisScrollFrame !== null) {
            window.cancelAnimationFrame(analysisScrollFrame);
            analysisScrollFrame = null;
        }
    }

    function cancelAnalysisNavigation() {
        if (analysisNavigationIsActive()) {
            analysisState.cancelled = true;
        }
        stopAnalysisNavigationObservation();
    }

    function scrollAnalysisMilestone(anchor, flag) {
        clearPendingDocumentationNavigation();
        replaceCurrentFragment(anchor.id);
        window[processedInitialAnchorProperty] = anchor.id;
        anchor.scrollIntoView({ behavior: 'auto', block: 'start' });
        analysisState[flag] = true;
    }

    function isCurrentAnalysisElement(element) {
        return Boolean(element && !element.closest('[data-stale="true"]'));
    }

    function advanceAnalysisNavigation() {
        analysisScrollFrame = null;
        if (!analysisNavigationIsActive()) {
            return;
        }
        if (!analysisState.statusScrolled) {
            const statusAnchor = document.getElementById(data.analysisStatusAnchorId);
            if (!statusAnchor) {
                return;
            }
            scrollAnalysisMilestone(statusAnchor, 'statusScrolled');
        }

        // Streamlit can retain a prior run's dimmed subtree at an earlier
        // DOM position while the current run renders. Select this submission's
        // live anchor rather than the first occurrence of the shared HTML ID.
        const mapAnchor = Array.from(document.querySelectorAll(
            '[data-analysis-submission-token]'
        )).find(element => (
            element.id === data.analysisMapAnchorId
            && element.getAttribute('data-analysis-submission-token') === submissionToken
            && isCurrentAnalysisElement(element)
        ));
        if (!mapAnchor) {
            return;
        }
        const marker = Array.from(document.querySelectorAll(
            '[data-wspradar-map-ready-token]'
        )).find(element => (
            element.getAttribute('data-wspradar-map-ready-token') === submissionToken
            && isCurrentAnalysisElement(element)
        ));
        if (!marker) {
            return;
        }
        const containerKey = marker.getAttribute('data-map-image-container-key');
        const mapContainer = marker.closest(`.st-key-${containerKey}`);
        const mapImage = mapContainer?.querySelector('[data-testid="stImage"] img');
        if (!isCurrentAnalysisElement(mapImage)) {
            return;
        }
        if (observedMapImage !== mapImage) {
            detachMapImageListeners();
            observedMapImage = mapImage;
            mapImage.addEventListener('load', scheduleAnalysisNavigation);
            mapImage.addEventListener('error', scheduleAnalysisNavigation);
        }
        if (
            !mapImage.complete
            || mapImage.naturalWidth <= 0
            || mapImage.getBoundingClientRect().height <= 0
        ) {
            return;
        }
        scrollAnalysisMilestone(mapAnchor, 'mapScrolled');
        stopAnalysisNavigationObservation();
    }

    function scheduleAnalysisNavigation() {
        if (!analysisNavigationIsActive() || analysisScrollFrame !== null) {
            return;
        }
        analysisScrollFrame = window.requestAnimationFrame(advanceAnalysisNavigation);
    }

    function handleDeliberateNavigation(event) {
        if (event.type === 'keydown') {
            const navigationKeys = new Set([
                'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight',
                'PageUp', 'PageDown', 'Home', 'End', ' ',
            ]);
            if (
                !navigationKeys.has(event.key)
                || event.target?.isContentEditable
                || event.target?.closest('input, textarea, select, button, [role="button"], [contenteditable], [role="combobox"], [role="listbox"], [role="slider"]')
            ) {
                return;
            }
        }
        cancelAnalysisNavigation();
    }

    function handleScrollbarNavigation(event) {
        if (event.button !== 0) {
            return;
        }
        const element = scrollContainer === window ? document.documentElement : scrollContainer;
        const gutterWidth = element.offsetWidth - element.clientWidth;
        const bounds = element.getBoundingClientRect();
        if (
            gutterWidth > 0
            && element.scrollHeight > element.clientHeight
            && event.clientX >= bounds.right - gutterWidth
            && event.clientX <= bounds.right
            && event.clientY >= bounds.top
            && event.clientY <= bounds.bottom
        ) {
            cancelAnalysisNavigation();
        }
    }

    function handleAnchorNavigation(event) {
        if (event.target?.closest('a[href]')) {
            cancelAnalysisNavigation();
        }
    }

    if (analysisNavigationIsActive()) {
        if ('MutationObserver' in window) {
            analysisObserver = new MutationObserver(scheduleAnalysisNavigation);
            analysisObserver.observe(document.body, {
                childList: true,
                subtree: true,
                attributes: true,
                attributeFilter: [
                    'src', 'class', 'style', 'hidden', 'data-stale',
                    'data-analysis-submission-token',
                    'data-wspradar-map-ready-token',
                    'data-map-image-container-key',
                ],
            });
        }
        scheduleAnalysisNavigation();
    }
    document.addEventListener('wheel', handleDeliberateNavigation, { passive: true });
    document.addEventListener('touchmove', handleDeliberateNavigation, { passive: true });
    document.addEventListener('keydown', handleDeliberateNavigation);
    document.addEventListener('click', handleAnchorNavigation, true);
    document.addEventListener('pointerdown', handleScrollbarNavigation, true);
    window.addEventListener('resize', scheduleAnalysisNavigation);

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
    if (!didHandleRequest && !analysisState) {
        const initialAnchorId = anchorIdFromHash(window.location.hash);
        if (
            allowedApplicationAnchors.has(initialAnchorId)
            && window[processedInitialAnchorProperty] !== initialAnchorId
        ) {
            window[processedInitialAnchorProperty] = initialAnchorId;
            scrollWhenApplicationAnchorMounts(initialAnchorId);
        } else if (!initialAnchorId) {
            scheduleVisibleApplicationAnchorSynchronization();
        }
    }

    return () => {
        stopAnalysisNavigationObservation();
        document.removeEventListener('wheel', handleDeliberateNavigation);
        document.removeEventListener('touchmove', handleDeliberateNavigation);
        document.removeEventListener('keydown', handleDeliberateNavigation);
        document.removeEventListener('click', handleAnchorNavigation, true);
        document.removeEventListener('pointerdown', handleScrollbarNavigation, true);
        window.removeEventListener('resize', scheduleAnalysisNavigation);
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
    *,
    analysis_submission_token: str | None = None,
) -> None:
    """Mount coarse navigation and optional one-shot analysis milestones."""
    if analysis_submission_token is not None:
        _validate_navigation_attribute(analysis_submission_token, "submission token")
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
            "analysisSubmissionToken": analysis_submission_token,
            "analysisStatusAnchorId": RESULTS_INSPECTION_ANCHOR_ID,
            "analysisMapAnchorId": MAP_RESULTS_ANCHOR_ID,
        },
        key=PAGE_NAVIGATION_CONTROLLER_KEY,
        width="stretch",
        height=1,
    )


def _validate_navigation_attribute(value: str, field: str) -> None:
    """Allow bounded internal tokens and Streamlit keys in browser markers."""
    if not isinstance(value, str) or re.fullmatch(r"[A-Za-z0-9_-]{1,160}", value) is None:
        raise ValueError(f"Invalid analysis navigation {field}.")


def render_analysis_map_anchor(submission_token: str | None) -> None:
    """Expose the first map target, bound to this submission when applicable."""
    if submission_token is None:
        render_page_anchor(MAP_RESULTS_ANCHOR_ID)
        return
    _validate_navigation_attribute(submission_token, "submission token")
    st.html(
        f'<span id="{MAP_RESULTS_ANCHOR_ID}" class="wspradar-page-anchor" '
        f'data-analysis-submission-token="{escape(submission_token, quote=True)}" '
        'aria-hidden="true"></span>'
    )


def render_analysis_map_ready_marker(
    submission_token: str | None,
    *,
    image_container_key: str,
) -> None:
    """Signal that the first map was emitted; the browser checks image readiness."""
    if submission_token is None:
        return
    _validate_navigation_attribute(submission_token, "submission token")
    _validate_navigation_attribute(image_container_key, "image container key")
    st.html(
        '<span aria-hidden="true" '
        f'data-wspradar-map-ready-token="{escape(submission_token, quote=True)}" '
        f'data-map-image-container-key="{escape(image_container_key, quote=True)}" '
        'style="display:none"></span>'
    )
