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


def test_manual_scroll_replaces_the_current_hash_without_polluting_history():
    """Track the nearest mounted anchor while reserving pushes for link clicks."""
    javascript = documentation_scroll_trigger._DOCUMENTATION_SCROLL_TRIGGER_JS

    assert "function synchronizeVisibleAnchor()" in javascript
    assert "findVisibleMountedAnchorId(" in javascript
    assert "mountedDocumentationAnchors.length === 0" in javascript
    assert "documentationBounds.top <= documentationActivationLine" in javascript
    assert "documentationBounds.bottom > documentationActivationLine" in javascript
    assert (
        "window.history.replaceState(window.history.state, '', encodedHash)"
        in javascript
    )
    assert javascript.count("window.history.replaceState") == 1
    assert javascript.count("window.history.pushState") == 1
    assert javascript.index("synchronizeVisibleAnchor();") < javascript.index(
        "requestNavigation(anchorId, true)"
    )


def test_manual_scroll_uses_a_cached_sublinear_anchor_lookup():
    """Keep full-manual anchor scans and style reads out of scroll frames."""
    javascript = documentation_scroll_trigger._DOCUMENTATION_SCROLL_TRIGGER_JS

    assert "const orderedAnchorIds = Array.from(new Set(" in javascript
    assert "let mountedDocumentationAnchors = []" in javascript
    assert "function refreshMountedDocumentationAnchors()" in javascript
    assert "for (const anchorId of orderedAnchorIds)" in javascript
    assert "documentationContainer?.contains(anchor)" in javascript
    assert "window.getComputedStyle(firstMountedAnchor).scrollMarginTop" in javascript
    assert "function findVisibleMountedAnchorId(activationLine)" in javascript
    assert "while (lowerBound <= upperBound)" in javascript
    assert "lowerBound = middleIndex + 1" in javascript
    assert "upperBound = middleIndex - 1" in javascript

    synchronize_source = javascript.split(
        "function synchronizeVisibleAnchor()",
        maxsplit=1,
    )[1].split("let visibleAnchorFrame", maxsplit=1)[0]
    assert "for (const anchorId" not in synchronize_source
    assert "window.getComputedStyle" not in synchronize_source

    observer_source = javascript.split(
        "documentationObserver = new MutationObserver",
        maxsplit=1,
    )[1].split("documentationObserver.observe", maxsplit=1)[0]
    assert "refreshMountedDocumentationAnchors();" in observer_source
    assert (
        javascript.index("refreshMountedDocumentationAnchors();")
        < javascript.index("scheduleDocumentationTableLayouts();")
    )


def test_manual_scroll_synchronization_is_throttled_guarded_and_cleaned_up():
    """Avoid layout work per event and never overwrite pending navigation."""
    javascript = documentation_scroll_trigger._DOCUMENTATION_SCROLL_TRIGGER_JS

    assert "window[pendingAnchorProperty]" in javascript
    assert "scheduledAnchorId !== null" in javascript
    assert "let visibleAnchorFrame = null" in javascript
    assert (
        "documentationContainer?.closest('[data-testid=\"stMain\"]')"
        in javascript
    )
    assert (
        "scrollContainer.addEventListener('scroll', "
        "scheduleVisibleAnchorSynchronization"
        in javascript
    )
    assert "scrollContainer.scrollTop + scrollContainer.clientHeight" in javascript
    assert ">= scrollContainer.scrollHeight" in javascript
    assert "passive: true" in javascript
    assert (
        "window.addEventListener('resize', scheduleVisibleAnchorSynchronization)"
        in javascript
    )
    assert "scrollContainer.removeEventListener(" in javascript
    assert (
        "window.removeEventListener('resize', scheduleVisibleAnchorSynchronization)"
        in javascript
    )
    assert "window.cancelAnimationFrame(visibleAnchorFrame)" in javascript


def test_documentation_tables_multiply_their_natural_column_widths_by_section():
    """Keep layout ratios relative to each localized table's rendered widths."""
    javascript = documentation_scroll_trigger._DOCUMENTATION_SCROLL_TRIGGER_JS

    expected_layouts = (
        (
            "layoutName: 'section-1-4'",
            "startAnchorId: 'sec-2-4'",
            "endAnchorId: 'sec-2-4-simultaneous'",
            "widthMultipliers: [2, 1, 1]",
        ),
        (
            "layoutName: 'section-4-0'",
            "startAnchorId: 'sec-5'",
            "endAnchorId: 'sec-5-1'",
            "widthMultipliers: [1.5, 1, 1]",
        ),
        (
            "layoutName: 'section-4-2'",
            "startAnchorId: 'sec-5-2'",
            "endAnchorId: 'sec-5-3'",
            "widthMultipliers: [1.5, 1.5, 1]",
        ),
        (
            "layoutName: 'section-4-3'",
            "startAnchorId: 'sec-5-3'",
            "endAnchorId: 'sec-5-4'",
            "widthMultipliers: [1.5, 1, 1]",
        ),
    )
    for layout_contract in expected_layouts:
        for expected_source in layout_contract:
            assert expected_source in javascript

    assert "compareDocumentPosition(table)" in javascript
    assert "table.compareDocumentPosition(endAnchor)" in javascript
    assert "headerCell.getBoundingClientRect().width" in javascript
    assert "width * specification.widthMultipliers[index]" in javascript
    assert "weightedWidth / totalWeightedWidth" in javascript
    assert "document.createElement('colgroup')" in javascript
    assert "table.classList.add(weightedTableClassName)" in javascript


def test_documentation_table_layout_waits_for_lazy_dom_and_cleans_up():
    """Apply scoped widths after expansion without leaving a DOM observer alive."""
    javascript = documentation_scroll_trigger._DOCUMENTATION_SCROLL_TRIGGER_JS

    assert "let documentationObserver = null" in javascript
    assert "documentationObserver = new MutationObserver" in javascript
    assert "documentationObserver.observe(documentationContainer" in javascript
    assert "scheduleDocumentationTableLayouts();" in javascript
    assert "documentationObserver?.disconnect()" in javascript
    assert "window.cancelAnimationFrame(tableLayoutFrame)" in javascript


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
