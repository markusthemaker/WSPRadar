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
    assert "sentinel.documentationScrollObserver === observer" in javascript


def test_scroll_trigger_sentinel_is_invisible_but_has_observable_geometry():
    html = documentation_scroll_trigger._DOCUMENTATION_SCROLL_TRIGGER_HTML
    css = documentation_scroll_trigger._DOCUMENTATION_SCROLL_TRIGGER_CSS

    assert 'class="documentation-scroll-sentinel"' in html
    assert 'aria-hidden="true"' in html
    assert "height: 1px" in css
    assert "pointer-events: none" in css


def test_scroll_trigger_wrapper_passes_stable_mount_and_callback_contract(monkeypatch):
    component_calls = []
    callback = lambda: None
    monkeypatch.setattr(
        documentation_scroll_trigger,
        "_DOCUMENTATION_SCROLL_TRIGGER",
        lambda **kwargs: component_calls.append(kwargs),
    )

    documentation_scroll_trigger.render_documentation_scroll_trigger(
        key="documentation-trigger-test",
        on_trigger=callback,
    )

    assert component_calls == [
        {
            "key": "documentation-trigger-test",
            "width": "stretch",
            "height": 1,
            "on_nearby_change": callback,
        }
    ]
