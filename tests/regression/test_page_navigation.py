from pathlib import Path
import re
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from docs.doc_de import DOC_DE
from docs.doc_en import DOC_EN
from ui import page_navigation


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def test_every_manual_anchor_uses_a_documentation_owned_namespace():
    """Keep bilingual manual deep links distinguishable from application anchors."""
    manual_anchor_ids = set(
        re.findall(r'<a\s+id="([^"]+)"', f"{DOC_EN}\n{DOC_DE}")
    )

    assert manual_anchor_ids
    assert not {
        anchor_id
        for anchor_id in manual_anchor_ids
        if not (
            anchor_id == "documentation-toc"
            or anchor_id.startswith(("part-", "sec-", "ref-"))
        )
    }


def test_application_navigation_request_is_allowlisted_unique_and_one_shot():
    """Queue only stable application anchors and consume each request once."""
    session_state = {}

    page_navigation.request_page_navigation(
        session_state,
        page_navigation.PARAMETER_SETTINGS_ANCHOR_ID,
        should_scroll=False,
    )
    first_request = page_navigation.consume_page_navigation_request(session_state)

    assert first_request is not None
    assert first_request["anchor_id"] == (
        page_navigation.PARAMETER_SETTINGS_ANCHOR_ID
    )
    assert first_request["should_scroll"] is False
    assert len(first_request["request_token"]) == 32
    assert (
        page_navigation.consume_page_navigation_request(session_state)
        is None
    )

    page_navigation.request_page_navigation(
        session_state,
        page_navigation.RESULTS_INSPECTION_ANCHOR_ID,
        should_scroll=True,
    )
    second_request = page_navigation.consume_page_navigation_request(session_state)

    assert second_request is not None
    assert second_request["anchor_id"] == (
        page_navigation.RESULTS_INSPECTION_ANCHOR_ID
    )
    assert second_request["should_scroll"] is True
    assert second_request["request_token"] != first_request["request_token"]

    with pytest.raises(ValueError, match="Unknown application anchor"):
        page_navigation.request_page_navigation(
            session_state,
            "sec-1",
            should_scroll=True,
        )


def test_page_anchor_renderer_accepts_only_the_stable_runtime_ids(monkeypatch):
    """Render inert explicit IDs without accepting arbitrary HTML fragments."""
    html = Mock()
    monkeypatch.setattr(
        page_navigation,
        "st",
        SimpleNamespace(html=html),
    )

    for anchor_id in page_navigation.APPLICATION_ANCHOR_IDS:
        page_navigation.render_page_anchor(anchor_id)

    assert [call.args[0] for call in html.call_args_list] == [
        (
            f'<span id="{anchor_id}" class="wspradar-page-anchor" '
            'aria-hidden="true"></span>'
        )
        for anchor_id in page_navigation.APPLICATION_ANCHOR_IDS
    ]
    assert all(call.kwargs == {} for call in html.call_args_list)

    with pytest.raises(ValueError, match="Unknown application anchor"):
        page_navigation.render_page_anchor("<script>")


def test_page_navigation_controller_passes_stable_anchor_and_request_contract(
    monkeypatch,
):
    """Keep runtime targets separate from manual anchors in browser data."""
    component_calls = []
    monkeypatch.setattr(
        page_navigation,
        "_PAGE_NAVIGATION_CONTROLLER",
        lambda **kwargs: component_calls.append(kwargs),
    )
    request = {
        "anchor_id": page_navigation.PARAMETER_SETTINGS_ANCHOR_ID,
        "request_token": "request-1",
        "should_scroll": False,
    }

    page_navigation.render_page_navigation_controller(request)

    assert component_calls == [
        {
            "data": {
                "anchorIds": list(page_navigation.APPLICATION_ANCHOR_IDS),
                "requestAnchorId": (
                    page_navigation.PARAMETER_SETTINGS_ANCHOR_ID
                ),
                "requestToken": "request-1",
                "shouldScrollRequest": False,
            },
            "key": page_navigation.PAGE_NAVIGATION_CONTROLLER_KEY,
            "width": "stretch",
            "height": 1,
        }
    ]


def test_page_scroll_tracking_replaces_stale_manual_fragments_by_region():
    """Continue URL tracking above Documentation without polluting history."""
    javascript = page_navigation._PAGE_NAVIGATION_CONTROLLER_JS

    assert "visibleApplicationAnchorId()" in javascript
    assert "documentationSelector = '.st-key-documentation_body'" in javascript
    assert (
        "documentationContainer.getBoundingClientRect().top <= activationLine"
        in javascript
    )
    assert "anchorId?.startsWith('part-')" in javascript
    assert "anchorId?.startsWith('sec-')" in javascript
    assert "anchorId?.startsWith('ref-')" in javascript
    assert "replaceCurrentFragment(visibleAnchorId)" in javascript
    assert "window.history.replaceState(" in javascript
    assert "window.history.pushState" not in javascript
    assert "window.location.hash =" not in javascript
    assert (
        "`${window.location.pathname}${window.location.search}${encodedHash}`"
        in javascript
    )
    assert (
        "document.addEventListener('click', "
        "handleInteractionBeforeRerun, true)"
        in javascript
    )
    assert "window[pendingDocumentationAnchorProperty]" in javascript


def test_explicit_application_navigation_cancels_manual_restore_and_is_optional():
    """Replace stale locations before rerun while letting Continue remain still."""
    javascript = page_navigation._PAGE_NAVIGATION_CONTROLLER_JS

    assert "clearPendingDocumentationNavigation();" in javascript
    assert "window[pendingDocumentationAnchorProperty] = null" in javascript
    assert "window[requestedDocumentationAnchorProperty] = null" in javascript
    assert "window[processedRequestTokenProperty] === requestToken" in javascript
    assert "replaceCurrentFragment(anchorId);" in javascript
    assert "if (data?.shouldScrollRequest)" in javascript
    assert "scrollWhenApplicationAnchorMounts(anchorId)" in javascript
    assert "scrollIntoView({" in javascript
    assert "window.addEventListener('hashchange', handleHistoryNavigation)" in javascript
    assert "window.addEventListener('popstate', handleHistoryNavigation)" in javascript


def test_runtime_anchors_bound_the_top_settings_and_results_regions():
    """Keep stable regions while Run leaves the live status viewport untouched."""
    app_source = (REPOSITORY_ROOT / "app.py").read_text(encoding="utf-8")
    renderer_source = (
        REPOSITORY_ROOT / "ui" / "guided_inputs" / "renderer.py"
    ).read_text(encoding="utf-8")

    top_call = "render_page_anchor(PAGE_TOP_ANCHOR_ID)"
    parameters_call = "render_page_anchor(PARAMETER_SETTINGS_ANCHOR_ID)"
    results_call = "render_page_anchor(RESULTS_INSPECTION_ANCHOR_ID)"
    assert app_source.count(top_call) == 1
    assert app_source.count(parameters_call) == 1
    assert app_source.count(results_call) == 1
    assert (
        app_source.index(top_call)
        < app_source.index(parameters_call)
        < app_source.index(results_call)
        < app_source.index("render_documentation_section(")
    )
    assert "RESULTS_INSPECTION_ANCHOR_ID,\n        should_scroll=False" in app_source
    assert (
        "PARAMETER_SETTINGS_ANCHOR_ID,\n        should_scroll=False"
        in renderer_source
    )
    assert (
        "PARAMETER_SETTINGS_ANCHOR_ID,\n        should_scroll=True"
        in renderer_source
    )
