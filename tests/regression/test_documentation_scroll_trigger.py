from ui import documentation_scroll_trigger


def test_scroll_trigger_uses_supported_one_shot_intersection_observer_contract():
    javascript = documentation_scroll_trigger._DOCUMENTATION_SCROLL_TRIGGER_JS

    assert "'IntersectionObserver' in window" in javascript
    assert "let hasTriggered = false" in javascript
    assert "entries.some((entry) => entry.isIntersecting)" in javascript
    assert "rootMargin: '0px'" in javascript
    assert "threshold: 0" in javascript
    assert javascript.index("observer.disconnect()") < javascript.index(
        "setTriggerValue('nearby', true)"
    )
    assert "sentinel.documentationScrollObserver?.disconnect()" in javascript
    assert "sentinel.documentationScrollObserver = observer" in javascript
    assert "return () => {" in javascript
    assert "sentinel?.documentationScrollObserver === observer" in javascript


def test_navigation_trigger_defers_only_missing_known_manual_anchors():
    """Preserve native links while expanding unresolved manual destinations."""
    javascript = documentation_scroll_trigger._DOCUMENTATION_SCROLL_TRIGGER_JS

    assert "documentationContainer?.contains(link)" in javascript
    assert "event.button !== 0" in javascript
    assert "event.ctrlKey" in javascript
    assert "event.metaKey" in javascript
    assert "anchorIds.has(anchorId)" in javascript
    assert "document.getElementById(anchorId)" in javascript
    assert "event.preventDefault()" in javascript
    assert "window.history.pushState" in javascript
    assert "setTriggerValue('navigate', anchorId)" in javascript


def test_navigation_trigger_restores_deferred_target_after_dom_mount():
    """Wait for lazy content, scroll once, and clean up browser observers."""
    javascript = documentation_scroll_trigger._DOCUMENTATION_SCROLL_TRIGGER_JS

    assert "data?.allowInitialHashExpansion" in javascript
    assert "decodeURIComponent(hash.slice(1))" in javascript
    assert "new MutationObserver" in javascript
    assert "scrollObserver.observe(document.body" in javascript
    assert "mountedTarget?.scrollIntoView" in javascript
    assert "window[pendingAnchorProperty] = null" in javascript
    assert "document.removeEventListener('click'" in javascript
    assert "window.removeEventListener('hashchange'" in javascript
    assert "window.removeEventListener('popstate'" in javascript


def test_history_navigation_scrolls_mounted_anchors_and_expands_missing_anchors():
    """Back and Forward must move the viewport as well as update the hash."""
    javascript = documentation_scroll_trigger._DOCUMENTATION_SCROLL_TRIGGER_JS

    assert "function handleHistoryNavigation()" in javascript
    assert "if (document.getElementById(anchorId))" in javascript
    assert "scrollToAnchor(anchorId, false)" in javascript
    assert "requestNavigation(anchorId, false)" in javascript
    assert "scheduledAnchorId === anchorId" in javascript


def test_scroll_trigger_sentinel_is_invisible_but_has_observable_geometry():
    html = documentation_scroll_trigger._DOCUMENTATION_SCROLL_TRIGGER_HTML
    css = documentation_scroll_trigger._DOCUMENTATION_SCROLL_TRIGGER_CSS

    assert 'class="documentation-scroll-sentinel"' in html
    assert 'aria-hidden="true"' in html
    assert "height: 1px" in css
    assert "pointer-events: none" in css


def test_scroll_trigger_wrapper_passes_stable_mount_and_callback_contract(monkeypatch):
    component_calls = []
    navigation_callback = lambda: None
    scroll_callback = lambda: None
    monkeypatch.setattr(
        documentation_scroll_trigger,
        "_DOCUMENTATION_SCROLL_TRIGGER",
        lambda **kwargs: component_calls.append(kwargs),
    )

    documentation_scroll_trigger.render_documentation_scroll_trigger(
        key="documentation-trigger-test",
        anchor_ids=("sec-2", "ref-1"),
        is_auto_expand_enabled=True,
        is_documentation_expanded=False,
        allow_initial_hash_expansion=True,
        on_navigation=navigation_callback,
        on_trigger=scroll_callback,
    )

    assert component_calls == [
        {
            "data": {
                "anchorIds": ["sec-2", "ref-1"],
                "isAutoExpandEnabled": True,
                "isExpanded": False,
                "allowInitialHashExpansion": True,
            },
            "key": "documentation-trigger-test",
            "width": "stretch",
            "height": 1,
            "on_navigate_change": navigation_callback,
            "on_nearby_change": scroll_callback,
        }
    ]
