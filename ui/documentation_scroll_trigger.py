"""Browser triggers for demand-driven documentation expansion and navigation."""

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
    const anchorIds = new Set(data?.anchorIds ?? []);
    const pendingAnchorProperty = '__wspradarPendingDocumentationAnchor';
    const requestedAnchorProperty = '__wspradarRequestedDocumentationAnchor';

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
        if (
            !anchorIds.has(anchorId)
            || document.getElementById(anchorId)
        ) {
            return;
        }

        event.preventDefault();
        requestNavigation(anchorId, true);
    }

    let scrollObserver = null;
    let scheduledAnchorId = null;
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
        scrollObserver?.disconnect();
        observer?.disconnect();
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
    """Mount viewport and unresolved-anchor triggers for the manual fragment."""
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
