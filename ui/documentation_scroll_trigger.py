"""Browser controls for demand-driven documentation, navigation, and layout."""

from collections.abc import Callable

import streamlit as st


_DOCUMENTATION_SCROLL_TRIGGER_HTML = """
<span class="documentation-scroll-sentinel" aria-hidden="true"></span>
"""

_DOCUMENTATION_SCROLL_TRIGGER_CSS = """
:host {
    display: block;
    height: 1px;
    margin: 0;
    overflow: hidden;
    padding: 0;
}

.documentation-scroll-sentinel {
    display: block;
    height: 1px;
    pointer-events: none;
    width: 100%;
}
"""

_DOCUMENTATION_SCROLL_TRIGGER_JS = """
export default function(component) {
    const { data, parentElement, setTriggerValue } = component;
    const sentinel = parentElement.querySelector('.documentation-scroll-sentinel');
    const documentationContainer = document.querySelector(
        '.st-key-documentation_body'
    );
    const scrollContainer = (
        documentationContainer?.closest('[data-testid="stMain"]')
        ?? window
    );
    const orderedAnchorIds = Array.from(new Set(data?.anchorIds ?? []));
    const anchorIds = new Set(orderedAnchorIds);
    const pendingAnchorProperty = '__wspradarPendingDocumentationAnchor';
    const requestedAnchorProperty = '__wspradarRequestedDocumentationAnchor';
    const weightedTableClassName = 'documentation-weighted-columns';
    const tableLayoutSpecifications = [
        {
            layoutName: 'section-1-4',
            startAnchorId: 'sec-2-4',
            endAnchorId: 'sec-2-4-simultaneous',
            widthMultipliers: [2, 1, 1],
        },
        {
            layoutName: 'section-4-0',
            startAnchorId: 'sec-5',
            endAnchorId: 'sec-5-1',
            widthMultipliers: [1.5, 1, 1],
        },
        {
            layoutName: 'section-4-2',
            startAnchorId: 'sec-5-2',
            endAnchorId: 'sec-5-3',
            widthMultipliers: [1.5, 1.5, 1],
        },
        {
            layoutName: 'section-4-3',
            startAnchorId: 'sec-5-3',
            endAnchorId: 'sec-5-4',
            widthMultipliers: [1.5, 1, 1],
        },
    ];

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

    function requestNavigation(anchorId, updateHistory) {
        if (!anchorIds.has(anchorId)) {
            return;
        }

        window[pendingAnchorProperty] = anchorId;
        if (updateHistory) {
            const encodedHash = `#${encodeURIComponent(anchorId)}`;
            if (window.location.hash !== encodedHash) {
                window.history.pushState(window.history.state, '', encodedHash);
            }
        }
        if (window[requestedAnchorProperty] === anchorId) {
            return;
        }
        window[requestedAnchorProperty] = anchorId;
        setTriggerValue('navigate', anchorId);
    }

    function findTableBetweenAnchors(startAnchorId, endAnchorId) {
        const startAnchor = document.getElementById(startAnchorId);
        const endAnchor = document.getElementById(endAnchorId);
        if (
            !documentationContainer
            || !startAnchor
            || !endAnchor
            || !documentationContainer.contains(startAnchor)
            || !documentationContainer.contains(endAnchor)
        ) {
            return null;
        }

        return Array.from(documentationContainer.querySelectorAll('table')).find(
            (table) => (
                Boolean(
                    startAnchor.compareDocumentPosition(table)
                    & Node.DOCUMENT_POSITION_FOLLOWING
                )
                && Boolean(
                    table.compareDocumentPosition(endAnchor)
                    & Node.DOCUMENT_POSITION_FOLLOWING
                )
            )
        ) ?? null;
    }

    function applyWeightedColumnLayout(table, specification) {
        if (table.dataset.documentationColumnLayout === specification.layoutName) {
            return;
        }

        const headerCells = Array.from(
            table.querySelectorAll('thead tr:first-child > th')
        );
        if (headerCells.length !== specification.widthMultipliers.length) {
            return;
        }

        // Capture the localized table's automatic layout before fixed column
        // widths are applied, so each multiplier is relative to what the user
        // was already seeing rather than to an arbitrary equal-width baseline.
        const naturalWidths = headerCells.map(
            (headerCell) => headerCell.getBoundingClientRect().width
        );
        if (naturalWidths.some((width) => !Number.isFinite(width) || width <= 0)) {
            return;
        }

        const weightedWidths = naturalWidths.map(
            (width, index) => width * specification.widthMultipliers[index]
        );
        const totalWeightedWidth = weightedWidths.reduce(
            (total, width) => total + width,
            0
        );
        if (!Number.isFinite(totalWeightedWidth) || totalWeightedWidth <= 0) {
            return;
        }

        const columnGroup = document.createElement('colgroup');
        columnGroup.dataset.documentationColumnLayout = specification.layoutName;
        for (const weightedWidth of weightedWidths) {
            const column = document.createElement('col');
            column.style.width = `${(weightedWidth / totalWeightedWidth) * 100}%`;
            columnGroup.appendChild(column);
        }

        table.dataset.documentationColumnLayout = specification.layoutName;
        table.classList.add(weightedTableClassName);
        table.insertBefore(columnGroup, table.firstChild);
    }

    function applyDocumentationTableLayouts() {
        for (const specification of tableLayoutSpecifications) {
            const table = findTableBetweenAnchors(
                specification.startAnchorId,
                specification.endAnchorId
            );
            if (table) {
                applyWeightedColumnLayout(table, specification);
            }
        }
    }

    let tableLayoutFrame = null;
    function scheduleDocumentationTableLayouts() {
        if (tableLayoutFrame !== null) {
            return;
        }
        tableLayoutFrame = window.requestAnimationFrame(() => {
            tableLayoutFrame = null;
            applyDocumentationTableLayouts();
        });
    }

    let mountedDocumentationAnchors = [];
    let documentationActivationLine = 1;
    function refreshMountedDocumentationAnchors() {
        mountedDocumentationAnchors = [];
        for (const anchorId of orderedAnchorIds) {
            const anchor = document.getElementById(anchorId);
            if (
                anchor
                && documentationContainer?.contains(anchor)
            ) {
                mountedDocumentationAnchors.push({ anchorId, anchor });
            }
        }

        const firstMountedAnchor = mountedDocumentationAnchors[0]?.anchor;
        documentationActivationLine = firstMountedAnchor
            ? (
                Number.parseFloat(
                    window.getComputedStyle(firstMountedAnchor).scrollMarginTop
                ) || 0
            ) + 1
            : 1;
    }

    function findVisibleMountedAnchorId(activationLine) {
        let lowerBound = 0;
        let upperBound = mountedDocumentationAnchors.length - 1;
        let visibleAnchorId = null;

        // Explicit manual anchors share one scroll-margin rule and retain source
        // order in the DOM, so geometry is monotonic and supports binary search.
        while (lowerBound <= upperBound) {
            const middleIndex = Math.floor((lowerBound + upperBound) / 2);
            const mountedAnchor = mountedDocumentationAnchors[middleIndex];
            if (
                mountedAnchor.anchor.getBoundingClientRect().top
                <= activationLine
            ) {
                visibleAnchorId = mountedAnchor.anchorId;
                lowerBound = middleIndex + 1;
            } else {
                upperBound = middleIndex - 1;
            }
        }
        return visibleAnchorId;
    }

    let scheduledAnchorId = null;
    function synchronizeVisibleAnchor() {
        if (
            !documentationContainer
            || window[pendingAnchorProperty]
            || scheduledAnchorId !== null
            || mountedDocumentationAnchors.length === 0
        ) {
            return;
        }

        const documentationBounds = documentationContainer.getBoundingClientRect();
        let visibleAnchorId = null;
        if (
            documentationBounds.top <= documentationActivationLine
            && documentationBounds.bottom > documentationActivationLine
        ) {
            visibleAnchorId = findVisibleMountedAnchorId(
                documentationActivationLine
            );
        }

        const lastMountedAnchorId = (
            mountedDocumentationAnchors[
                mountedDocumentationAnchors.length - 1
            ]?.anchorId ?? null
        );
        const isAtDocumentBottom = scrollContainer === window
            ? (
                Math.ceil(window.scrollY + window.innerHeight)
                >= document.documentElement.scrollHeight
            )
            : (
                Math.ceil(scrollContainer.scrollTop + scrollContainer.clientHeight)
                >= scrollContainer.scrollHeight
            );
        if (isAtDocumentBottom && lastMountedAnchorId) {
            visibleAnchorId = lastMountedAnchorId;
        }
        if (!visibleAnchorId) {
            return;
        }

        const encodedHash = `#${encodeURIComponent(visibleAnchorId)}`;
        if (window.location.hash !== encodedHash) {
            // Scrolling updates the current entry; only explicit link
            // navigation should add a new Back/Forward history step.
            window.history.replaceState(window.history.state, '', encodedHash);
        }
    }

    let visibleAnchorFrame = null;
    function scheduleVisibleAnchorSynchronization() {
        if (visibleAnchorFrame !== null) {
            return;
        }
        visibleAnchorFrame = window.requestAnimationFrame(() => {
            visibleAnchorFrame = null;
            synchronizeVisibleAnchor();
        });
    }

    function handleDocumentationLinkClick(event) {
        if (
            event.defaultPrevented
            || event.button !== 0
            || event.altKey
            || event.ctrlKey
            || event.metaKey
            || event.shiftKey
            || !(event.target instanceof Element)
        ) {
            return;
        }

        const link = event.target.closest('a[href^="#"]');
        if (
            !link
            || !documentationContainer?.contains(link)
            || (link.target && link.target !== '_self')
        ) {
            return;
        }

        const anchorId = anchorIdFromHash(link.getAttribute('href'));
        if (!anchorIds.has(anchorId)) {
            return;
        }

        synchronizeVisibleAnchor();
        if (document.getElementById(anchorId)) {
            return;
        }

        event.preventDefault();
        requestNavigation(anchorId, true);
    }

    let scrollObserver = null;
    function scrollToAnchor(anchorId, shouldClearPendingNavigation) {
        if (
            !anchorIds.has(anchorId)
            || scheduledAnchorId === anchorId
        ) {
            return false;
        }

        const target = document.getElementById(anchorId);
        if (!target) {
            return false;
        }

        scheduledAnchorId = anchorId;
        window.requestAnimationFrame(() => {
            const mountedTarget = document.getElementById(anchorId);
            mountedTarget?.scrollIntoView({ behavior: 'auto', block: 'start' });
            if (
                shouldClearPendingNavigation
                && window[pendingAnchorProperty] === anchorId
            ) {
                window[pendingAnchorProperty] = null;
                window[requestedAnchorProperty] = null;
            }
            scheduledAnchorId = null;
            scheduleVisibleAnchorSynchronization();
        });
        return true;
    }

    function scrollToPendingAnchor() {
        const pendingAnchorId = window[pendingAnchorProperty];
        return Boolean(data?.isExpanded) && scrollToAnchor(pendingAnchorId, true);
    }

    function handleHistoryNavigation() {
        const anchorId = anchorIdFromHash(window.location.hash);
        if (!anchorIds.has(anchorId)) {
            return;
        }
        if (document.getElementById(anchorId)) {
            scrollToAnchor(anchorId, false);
            return;
        }
        requestNavigation(anchorId, false);
    }

    document.addEventListener('click', handleDocumentationLinkClick, true);
    window.addEventListener('hashchange', handleHistoryNavigation);
    window.addEventListener('popstate', handleHistoryNavigation);
    scrollContainer.addEventListener('scroll', scheduleVisibleAnchorSynchronization, {
        passive: true,
    });
    window.addEventListener('resize', scheduleVisibleAnchorSynchronization);

    let documentationObserver = null;
    if (documentationContainer && 'MutationObserver' in window) {
        documentationObserver = new MutationObserver(() => {
            refreshMountedDocumentationAnchors();
            scheduleDocumentationTableLayouts();
            scheduleVisibleAnchorSynchronization();
        });
        documentationObserver.observe(documentationContainer, {
            childList: true,
            subtree: true,
        });
    }
    refreshMountedDocumentationAnchors();
    scheduleDocumentationTableLayouts();
    scheduleVisibleAnchorSynchronization();

    if (
        data?.isExpanded
        && window[pendingAnchorProperty]
        && !scrollToPendingAnchor()
        && 'MutationObserver' in window
    ) {
        scrollObserver = new MutationObserver(() => {
            if (scrollToPendingAnchor()) {
                scrollObserver.disconnect();
                scrollObserver = null;
            }
        });
        scrollObserver.observe(document.body, { childList: true, subtree: true });
    }

    if (!data?.isExpanded && data?.allowInitialHashExpansion) {
        handleHistoryNavigation();
    }

    let observer = null;
    if (
        sentinel
        && data?.isAutoExpandEnabled
        && 'IntersectionObserver' in window
    ) {
        sentinel.documentationScrollObserver?.disconnect();
        let hasTriggered = false;
        observer = new IntersectionObserver((entries) => {
            if (hasTriggered || !entries.some((entry) => entry.isIntersecting)) {
                return;
            }
            hasTriggered = true;
            observer.disconnect();
            sentinel.documentationScrollObserver = null;
            setTriggerValue('nearby', true);
        }, {
            root: null,
            rootMargin: '0px',
            threshold: 0,
        });

        sentinel.documentationScrollObserver = observer;
        observer.observe(sentinel);
    }

    return () => {
        document.removeEventListener('click', handleDocumentationLinkClick, true);
        window.removeEventListener('hashchange', handleHistoryNavigation);
        window.removeEventListener('popstate', handleHistoryNavigation);
        scrollContainer.removeEventListener(
            'scroll',
            scheduleVisibleAnchorSynchronization
        );
        window.removeEventListener('resize', scheduleVisibleAnchorSynchronization);
        documentationObserver?.disconnect();
        scrollObserver?.disconnect();
        observer?.disconnect();
        if (tableLayoutFrame !== null) {
            window.cancelAnimationFrame(tableLayoutFrame);
        }
        if (visibleAnchorFrame !== null) {
            window.cancelAnimationFrame(visibleAnchorFrame);
        }
        if (sentinel?.documentationScrollObserver === observer) {
            sentinel.documentationScrollObserver = null;
        }
    };
}
"""

_DOCUMENTATION_SCROLL_TRIGGER = st.components.v2.component(
    "documentation_scroll_boundary_trigger",
    html=_DOCUMENTATION_SCROLL_TRIGGER_HTML,
    css=_DOCUMENTATION_SCROLL_TRIGGER_CSS,
    js=_DOCUMENTATION_SCROLL_TRIGGER_JS,
)


def render_documentation_scroll_trigger(
    *,
    key: str,
    anchor_ids: tuple[str, ...],
    is_auto_expand_enabled: bool,
    is_documentation_expanded: bool,
    allow_initial_hash_expansion: bool,
    on_navigation: Callable[[], None],
    on_trigger: Callable[[], None],
) -> None:
    """Mount the manual's viewport, navigation, and table-layout controller."""
    _DOCUMENTATION_SCROLL_TRIGGER(
        data={
            "anchorIds": list(anchor_ids),
            "isAutoExpandEnabled": is_auto_expand_enabled,
            "isExpanded": is_documentation_expanded,
            "allowInitialHashExpansion": allow_initial_hash_expansion,
        },
        key=key,
        width="stretch",
        height=1,
        on_navigate_change=on_navigation,
        on_nearby_change=on_trigger,
    )
