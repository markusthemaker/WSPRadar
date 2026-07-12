"""Browser viewport trigger for demand-driven documentation expansion."""

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
    const { parentElement, setTriggerValue } = component;
    const sentinel = parentElement.querySelector('.documentation-scroll-sentinel');
    if (!sentinel || !('IntersectionObserver' in window)) {
        return;
    }

    sentinel.documentationScrollObserver?.disconnect();
    let hasTriggered = false;
    const observer = new IntersectionObserver((entries) => {
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
    return () => {
        observer.disconnect();
        if (sentinel.documentationScrollObserver === observer) {
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
    on_trigger: Callable[[], None],
) -> None:
    """Notify Python when the Section 1.3 boundary enters the viewport."""
    _DOCUMENTATION_SCROLL_TRIGGER(
        key=key,
        width="stretch",
        height=1,
        on_nearby_change=on_trigger,
    )
