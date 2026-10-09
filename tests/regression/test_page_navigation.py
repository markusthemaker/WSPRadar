from pathlib import Path
import ast
import json
import shutil
import subprocess
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

    page_navigation.request_page_navigation(
        session_state,
        page_navigation.STATION_INSIGHTS_ANCHOR_ID,
        should_scroll=True,
    )
    station_request = page_navigation.consume_page_navigation_request(
        session_state
    )

    assert station_request is not None
    assert station_request["anchor_id"] == (
        page_navigation.STATION_INSIGHTS_ANCHOR_ID
    )
    assert station_request["should_scroll"] is True
    assert station_request["request_token"] not in {
        first_request["request_token"],
        second_request["request_token"],
    }

    page_navigation.request_page_navigation(
        session_state,
        page_navigation.DRILLDOWN_ANCHOR_ID,
        should_scroll=True,
    )
    drilldown_request = page_navigation.consume_page_navigation_request(
        session_state
    )
    assert drilldown_request is not None
    assert drilldown_request["anchor_id"] == page_navigation.DRILLDOWN_ANCHOR_ID
    assert drilldown_request["should_scroll"] is True

    with pytest.raises(ValueError, match="Unknown application anchor"):
        page_navigation.request_page_navigation(
            session_state,
            "sec-1",
            should_scroll=True,
        )


def test_invalid_field_focus_survives_one_shot_navigation_and_rejects_markup(monkeypatch):
    session_state = {}
    page_navigation.request_page_navigation(
        session_state, page_navigation.PARAMETER_SETTINGS_ANCHOR_ID,
        should_scroll=True, focus_field="val_callsign",
    )
    request = page_navigation.consume_page_navigation_request(session_state)
    component = Mock()
    monkeypatch.setattr(page_navigation, "_PAGE_NAVIGATION_CONTROLLER", component)
    page_navigation.render_page_navigation_controller(request)
    assert component.call_args.kwargs["data"]["focusFieldKey"] == "val_callsign"
    assert page_navigation.consume_page_navigation_request(session_state) is None
    with pytest.raises(ValueError):
        page_navigation.request_page_navigation(
            session_state, page_navigation.PARAMETER_SETTINGS_ANCHOR_ID,
            should_scroll=True, focus_field='<input onfocus="alert(1)">',
        )


def test_guided_panel_navigation_preserves_validated_key_and_coarse_anchor(monkeypatch):
    """Carry the precise Guided target without changing its stable URL region."""
    session_state = {}
    page_navigation.request_page_navigation(
        session_state,
        page_navigation.PARAMETER_SETTINGS_ANCHOR_ID,
        should_scroll=True,
        panel_key="guided_step_reference_design",
    )
    request = page_navigation.consume_page_navigation_request(session_state)
    assert request["anchor_id"] == page_navigation.PARAMETER_SETTINGS_ANCHOR_ID
    assert request["should_scroll"] is True
    assert request["panel_key"] == "guided_step_reference_design"
    assert page_navigation.consume_page_navigation_request(session_state) is None

    component = Mock()
    monkeypatch.setattr(page_navigation, "_PAGE_NAVIGATION_CONTROLLER", component)
    page_navigation.render_page_navigation_controller(request)
    data = component.call_args.kwargs["data"]
    assert data["requestAnchorId"] == page_navigation.PARAMETER_SETTINGS_ANCHOR_ID
    assert data["panelKey"] == "guided_step_reference_design"
    assert data["shouldScrollRequest"] is True
    assert data["requestToken"] == request["request_token"]


@pytest.mark.parametrize("focus_target", ["first_input", "panel_header"])
def test_guided_focus_target_survives_one_shot_navigation(monkeypatch, focus_target):
    state = {}
    page_navigation.request_page_navigation(
        state, page_navigation.PARAMETER_SETTINGS_ANCHOR_ID,
        should_scroll=True, panel_key="guided_step_reference_design", focus_target=focus_target,
    )
    request = page_navigation.consume_page_navigation_request(state)
    component = Mock()
    monkeypatch.setattr(page_navigation, "_PAGE_NAVIGATION_CONTROLLER", component)
    page_navigation.render_page_navigation_controller(request)
    assert component.call_args.kwargs["data"]["focusTarget"] == focus_target
    assert page_navigation.consume_page_navigation_request(state) is None


@pytest.mark.parametrize("focus_target", ["", "button", "<input>", [], 1])
def test_guided_focus_target_rejects_invalid_or_tampered_values(focus_target):
    state = {}
    with pytest.raises(ValueError):
        page_navigation.request_page_navigation(
            state, page_navigation.PARAMETER_SETTINGS_ANCHOR_ID,
            should_scroll=True, panel_key="guided_step_use_case", focus_target=focus_target,
        )
    state[page_navigation.PAGE_NAVIGATION_REQUEST_KEY] = {
        "anchor_id": page_navigation.PARAMETER_SETTINGS_ANCHOR_ID,
        "request_token": "focus-request", "should_scroll": True,
        "panel_key": "guided_step_use_case", "focus_target": focus_target,
    }
    assert "focus_target" not in page_navigation.consume_page_navigation_request(state)


def test_panel_focus_requires_panel_key_and_does_not_compete_with_field_focus():
    for extra in ({}, {"panel_key": "guided_step_use_case", "focus_field": "guided_use_case"}):
        with pytest.raises(ValueError):
            page_navigation.request_page_navigation(
                {}, page_navigation.PARAMETER_SETTINGS_ANCHOR_ID,
                should_scroll=True, focus_target="first_input", **extra,
            )


@pytest.mark.parametrize("panel_key", ["", "<details>", 'panel" onclick="alert(1)', "x" * 161, 1])
def test_guided_panel_navigation_rejects_invalid_keys_and_drops_tampered_keys(panel_key):
    """Do not expose unchecked HTML or selector fragments to the browser."""
    session_state = {}
    with pytest.raises(ValueError):
        page_navigation.request_page_navigation(
            session_state,
            page_navigation.PARAMETER_SETTINGS_ANCHOR_ID,
            should_scroll=True,
            panel_key=panel_key,
        )
    assert page_navigation.PAGE_NAVIGATION_REQUEST_KEY not in session_state

    session_state[page_navigation.PAGE_NAVIGATION_REQUEST_KEY] = {
        "anchor_id": page_navigation.PARAMETER_SETTINGS_ANCHOR_ID,
        "request_token": "panel-request",
        "should_scroll": True,
        "panel_key": panel_key,
    }
    request = page_navigation.consume_page_navigation_request(session_state)
    assert "panel_key" not in request


def test_guided_panel_marker_identifies_only_the_requested_panel_render():
    """Bind the rendered panel body to its current one-shot navigation request."""
    session_state = {}
    panel_key = "guided_step_reference_design"
    assert page_navigation.page_navigation_marker_html(session_state, panel_key) == ""
    page_navigation.request_page_navigation(
        session_state,
        page_navigation.PARAMETER_SETTINGS_ANCHOR_ID,
        should_scroll=True,
        panel_key=panel_key,
    )
    token = session_state[page_navigation.PAGE_NAVIGATION_REQUEST_KEY]["request_token"]
    marker = page_navigation.page_navigation_marker_html(session_state, panel_key)
    assert f'data-page-navigation-token="{token}"' in marker
    assert f'data-page-navigation-panel="{panel_key}"' in marker
    assert page_navigation.page_navigation_marker_html(
        session_state, "guided_step_offset_calibration",
    ) == ""
    page_navigation.consume_page_navigation_request(session_state)
    assert page_navigation.page_navigation_marker_html(session_state, panel_key) == ""


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
                "anchorIds": page_navigation.APPLICATION_ANCHOR_IDS,
                "requestAnchorId": (
                    page_navigation.PARAMETER_SETTINGS_ANCHOR_ID
                ),
                "requestToken": "request-1",
                "shouldScrollRequest": False,
                "analysisSubmissionToken": None,
                "focusFieldKey": None,
                "panelKey": None,
                "focusTarget": None,
                "analysisStatusAnchorId": page_navigation.RESULTS_INSPECTION_ANCHOR_ID,
                "analysisMapAnchorId": page_navigation.MAP_RESULTS_ANCHOR_ID,
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
    """Replace stale manual locations and retain optional coarse navigation."""
    javascript = page_navigation._PAGE_NAVIGATION_CONTROLLER_JS

    assert "clearPendingDocumentationNavigation();" in javascript
    assert "window[pendingDocumentationAnchorProperty] = null" in javascript
    assert "window[requestedDocumentationAnchorProperty] = null" in javascript
    assert "window[processedRequestTokenProperty] === requestToken" in javascript
    assert (
        "window[processedInitialAnchorProperty] = anchorId"
        in javascript
    )
    assert "replaceCurrentFragment(anchorId);" in javascript
    assert "if (data?.shouldScrollRequest)" in javascript
    assert "scrollWhenApplicationAnchorMounts(anchorId)" in javascript
    assert "scrollIntoView({" in javascript
    assert "window.addEventListener('hashchange', handleHistoryNavigation)" in javascript
    assert "window.addEventListener('popstate', handleHistoryNavigation)" in javascript


def test_initial_application_fragment_scrolls_only_once_per_browser_page():
    """Do not repeat an automatic anchor landing on every Streamlit rerun."""
    javascript = page_navigation._PAGE_NAVIGATION_CONTROLLER_JS

    assert (
        "processedInitialAnchorProperty =\n"
        "        '__wspradarProcessedInitialApplicationAnchor'"
        in javascript
    )
    assert (
        "window[processedInitialAnchorProperty] !== initialAnchorId"
        in javascript
    )
    assert (
        "window[processedInitialAnchorProperty] = initialAnchorId"
        in javascript
    )
    assert (
        "window.addEventListener('hashchange', handleHistoryNavigation)"
        in javascript
    )


def test_runtime_anchors_bound_the_top_settings_and_results_regions():
    """Keep stable regions while a submitted Run can navigate to live status."""
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
        < app_source.index("run_status_slot = st.empty()")
        < app_source.index("render_documentation_section(")
    )
    main_submission = next(
        node for node in ast.walk(ast.parse(app_source))
        if isinstance(node, ast.FunctionDef)
        and node.name == "request_main_analysis_submission"
    )
    navigation_calls = [
        node for node in ast.walk(main_submission)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "request_page_navigation"
    ]
    assert len(navigation_calls) == 2
    navigation_call = next(call for call in navigation_calls if call.args[1].id == "RESULTS_INSPECTION_ANCHOR_ID")
    invalid_input_call = next(call for call in navigation_calls if call.args[1].id == "PARAMETER_SETTINGS_ANCHOR_ID")
    assert any(keyword.arg == "focus_field" for keyword in invalid_input_call.keywords)
    assert isinstance(navigation_call.args[1], ast.Name)
    assert navigation_call.args[1].id == "RESULTS_INSPECTION_ANCHOR_ID"
    assert any(
        keyword.arg == "should_scroll"
        and isinstance(keyword.value, ast.Constant)
        and keyword.value.value is True
        for keyword in navigation_call.keywords
    )
    continue_function = next(
        node for node in ast.walk(ast.parse(renderer_source))
        if isinstance(node, ast.FunctionDef) and node.name == "_continue_to"
    )
    continue_navigation = next(
        node for node in ast.walk(continue_function)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "request_page_navigation"
    )
    assert continue_navigation.args[1].id == "PARAMETER_SETTINGS_ANCHOR_ID"
    keywords = {keyword.arg: keyword.value for keyword in continue_navigation.keywords}
    assert isinstance(keywords["should_scroll"], ast.Constant)
    assert keywords["should_scroll"].value is True
    assert isinstance(keywords["panel_key"], ast.JoinedStr)
    assert ast.literal_eval(keywords["panel_key"].values[0]) == "guided_step_"
    assert keywords["panel_key"].values[1].value.id == continue_function.args.args[0].arg
    assert (
        "PARAMETER_SETTINGS_ANCHOR_ID,\n        should_scroll=True"
        in renderer_source
    )


def test_station_insights_anchor_is_allowlisted_and_precedes_its_level():
    """Give report actions one stable target immediately above Station Insights."""
    inspector_source = (
        REPOSITORY_ROOT / "ui" / "components" / "inspector_stations.py"
    ).read_text(encoding="utf-8")

    assert page_navigation.APPLICATION_ANCHOR_IDS[-2] == (
        page_navigation.STATION_INSIGHTS_ANCHOR_ID
    )
    assert page_navigation.APPLICATION_ANCHOR_IDS[-1] == (
        page_navigation.DRILLDOWN_ANCHOR_ID
    )
    assert re.search(
        r"render_page_anchor\(\s*STATION_INSIGHTS_ANCHOR_ID\s*\)\s*"
        r"level_three_container\s*=\s*st\.container\(",
        inspector_source,
    )


def test_drilldown_anchor_is_allowlisted_and_precedes_its_level():
    """Give focused outlier actions a stable target above Drill-Down."""
    inspector_source = (
        REPOSITORY_ROOT / "ui" / "components" / "inspector_selected.py"
    ).read_text(encoding="utf-8")

    assert page_navigation.DRILLDOWN_ANCHOR_ID in (
        page_navigation.APPLICATION_ANCHOR_IDS
    )
    helper_start = inspector_source.index(
        "def render_drilldown_header_and_controls("
    )
    anchor_call = inspector_source.index(
        "render_page_anchor(DRILLDOWN_ANCHOR_ID)",
        helper_start,
    )
    heading_call = inspector_source.index(
        "render_drilldown_heading(",
        anchor_call,
    )
    assert helper_start < anchor_call < heading_call
    assert inspector_source.count(
        "render_drilldown_header_and_controls("
    ) >= 3


def test_analysis_map_markers_are_token_bound_and_escape_validated_attributes(monkeypatch):
    """Accept only bounded internal identifiers in the emitted HTML attributes."""
    html = Mock()
    monkeypatch.setattr(page_navigation, "st", SimpleNamespace(html=html))
    page_navigation.render_analysis_map_anchor("submission-1")
    assert 'id="wspradar-map-results"' in html.call_args.args[0]
    assert 'data-analysis-submission-token="submission-1"' in html.call_args.args[0]
    page_navigation.render_analysis_map_ready_marker(
        "submission-1", image_container_key="results_evidence_level_1_RX_123",
    )
    assert 'data-wspradar-map-ready-token="submission-1"' in html.call_args.args[0]
    assert 'data-map-image-container-key="results_evidence_level_1_RX_123"' in html.call_args.args[0]
    html.reset_mock()
    page_navigation.render_analysis_map_anchor(None)
    assert 'data-analysis-submission-token' not in html.call_args.args[0]
    html.reset_mock()
    page_navigation.render_analysis_map_ready_marker(None, image_container_key="ordinary")
    html.assert_not_called()
    for invalid in ("", "<script>", '\" onclick=\"alert(1)', "x" * 161, 1):
        with pytest.raises(ValueError, match="navigation submission token"):
            page_navigation.render_analysis_map_anchor(invalid)
        with pytest.raises(ValueError, match="navigation image container key"):
            page_navigation.render_analysis_map_ready_marker("valid", image_container_key=invalid)


def test_analysis_navigation_controller_passes_validated_milestone_identity(monkeypatch):
    """Keep the same controller while adding one explicit submission identity."""
    component = Mock()
    monkeypatch.setattr(page_navigation, "_PAGE_NAVIGATION_CONTROLLER", component)
    page_navigation.render_page_navigation_controller(None, analysis_submission_token="token-123")
    payload = component.call_args.kwargs["data"]
    assert payload["analysisSubmissionToken"] == "token-123"
    assert payload["analysisStatusAnchorId"] == page_navigation.RESULTS_INSPECTION_ANCHOR_ID
    assert payload["analysisMapAnchorId"] == page_navigation.MAP_RESULTS_ANCHOR_ID
    assert page_navigation.APPLICATION_ANCHOR_IDS.index(page_navigation.MAP_RESULTS_ANCHOR_ID) == (
        page_navigation.APPLICATION_ANCHOR_IDS.index(page_navigation.RESULTS_INSPECTION_ANCHOR_ID) + 1
    )
    with pytest.raises(ValueError, match="navigation submission token"):
        page_navigation.render_page_navigation_controller(None, analysis_submission_token="invalid token")


_ANALYSIS_NAVIGATION_BROWSER_HARNESS = r"""
const assert = require('node:assert/strict');
const vm = require('node:vm');
const input = JSON.parse(require('node:fs').readFileSync(0, 'utf8'));
class Events {
    constructor() { this.listeners = new Map(); }
    addEventListener(name, callback) {
        if (!this.listeners.has(name)) this.listeners.set(name, new Set());
        this.listeners.get(name).add(callback);
    }
    removeEventListener(name, callback) { this.listeners.get(name)?.delete(callback); }
    emit(name, values = {}) {
        const event = { type: name, target: { closest: () => null }, ...values };
        for (const callback of Array.from(this.listeners.get(name) ?? [])) callback(event);
    }
    listenerCount() {
        return Array.from(this.listeners.values()).reduce((total, values) => total + values.size, 0);
    }
}
const statusId = 'wspradar-results-inspection';
const mapId = 'wspradar-map-results';
const anchors = new Map();
const precedingAnchors = [];
const containers = new Map();
const precedingContainers = [];
const markers = [];
const panelMarkers = [];
const observers = [];
const frames = new Map();
const scrolls = [];
const scrolledElements = [];
const focusedElements = [];
const elements = [];
let nextFrame = 1;
class Element extends Events {
    constructor(id, attributes = {}) {
        super(); this.id = id; this.attributes = attributes;
        this.height = 100; this.top = 500;
        elements.push(this);
    }
    getAttribute(name) { return this.attributes[name] ?? null; }
    getBoundingClientRect() { return { top: this.top, height: this.height, right: 1000, bottom: this.top + this.height }; }
    scrollIntoView() { scrolls.push(this.id); scrolledElements.push(this); }
    focus() { focusedElements.push(this); document.activeElement = this; document.emit('focusin', {target: this}); }
    querySelectorAll(selector) {
        return elements.filter(element => {
            let ancestor = element.parentElement;
            while (ancestor && ancestor !== this) ancestor = ancestor.parentElement;
            if (!ancestor) return false;
            if (selector.startsWith('.st-key-')) return element.className === selector.slice(1);
            return ['INPUT', 'SELECT', 'TEXTAREA', 'BUTTON'].includes(element.tagName)
                || ['combobox', 'radio', 'switch', 'slider', 'spinbutton'].includes(element.getAttribute('role'));
        });
    }
    closest(selector) {
        for (let element = this; element; element = element.parentElement) {
            if (selector === '[data-stale="true"]' && element.getAttribute('data-stale') === 'true') return element;
            if (selector === '[data-testid="stExpander"]' && element.getAttribute('data-testid') === 'stExpander') return element;
            if (selector.startsWith('.st-key-') && element.className === selector.slice(1)) return element;
            if (selector.includes(',')) {
                for (const part of selector.split(',')) {
                    if (['[hidden]', '[inert]'].includes(part) && element.getAttribute(part.slice(1, -1)) !== null) return element;
                    if (part === 'fieldset[disabled]' && element.tagName === 'FIELDSET' && element.getAttribute('disabled') !== null) return element;
                    const attribute = part.match(/^\[([^=]+)="([^"]+)"\]$/);
                    if (attribute && element.getAttribute(attribute[1]) === attribute[2]) return element;
                }
            }
        }
        return null;
    }
}
const main = new Element('main');
main.offsetWidth = 1000; main.clientWidth = 985; main.clientHeight = 100; main.scrollHeight = 2000;
const document = new Events();
document.body = new Element('body');
document.getElementById = id => precedingAnchors.find(element => element.id === id) ?? anchors.get(id) ?? null;
document.querySelector = selector => selector === '[data-testid="stMain"]' ? main : null;
document.querySelectorAll = selector => {
    if (selector.startsWith('.st-key-')) return elements.filter(element => element.className === selector.slice(1));
    if (selector === '[data-analysis-submission-token]') {
        return [...precedingAnchors, ...anchors.values()].filter(element => element.getAttribute('data-analysis-submission-token') !== null);
    }
    if (selector === '[data-wspradar-map-ready-token]') return markers;
    if (selector === '[data-page-navigation-token]') return panelMarkers;
    throw new Error('Unsupported selector: ' + selector);
};
document.getElementsByClassName = name => [
    ...precedingContainers.filter(element => element.className === name),
    ...(containers.has(name) ? [containers.get(name)] : []),
];
const window = new Events();
window.location = { pathname: '/', search: '', hash: '' };
window.history = {
    state: null,
    replaceState: (_state, _title, url) => {
        window.location.hash = url.includes('#') ? '#' + url.split('#')[1] : '';
    },
};
window.getComputedStyle = () => ({ scrollMarginTop: '10px' });
window.requestAnimationFrame = callback => { const id = nextFrame++; frames.set(id, callback); return id; };
window.cancelAnimationFrame = id => frames.delete(id);
class MutationObserver {
    constructor(callback) { this.callback = callback; this.active = false; observers.push(this); }
    observe(_target, options) { this.active = true; this.options = options; }
    disconnect() { this.active = false; }
}
window.MutationObserver = MutationObserver;
const context = vm.createContext({ window, document, MutationObserver });
vm.runInContext(input.javascript.replace('export default function(component)', 'globalThis.mount = function(component)'), context);
function flush() {
    let rounds = 0;
    while (frames.size) {
        if (++rounds > 20) throw new Error('Unexpected periodic frame polling');
        const current = Array.from(frames.values()); frames.clear();
        for (const callback of current) callback();
    }
}
function flushFrame() {
    const current = Array.from(frames.values()); frames.clear();
    for (const callback of current) callback();
}
function mutate(attributeName = null) {
    for (const observer of observers) {
        if (observer.active && (!attributeName || (
            observer.options.attributes && observer.options.attributeFilter.includes(attributeName)
        ))) observer.callback();
    }
}
function mount(token = 'run-1', request = {}) {
    return context.mount({ data: {
        anchorIds: ['wspradar-page-top', 'wspradar-parameter-settings', statusId, mapId,
                    'wspradar-station-insights', 'wspradar-drilldown'],
        analysisSubmissionToken: token,
        analysisStatusAnchorId: statusId,
        analysisMapAnchorId: mapId,
        ...request,
    }});
}
function addMap(token, ready = true) {
    anchors.set(mapId, new Element(mapId, { 'data-analysis-submission-token': token }));
    markers.length = 0;
    markers.push(new Element('marker', {
        'data-wspradar-map-ready-token': token,
        'data-map-image-container-key': 'map-container',
    }));
    const image = new Element('image');
    image.complete = ready; image.naturalWidth = ready ? 1200 : 0;
    const container = new Element('map-container');
    container.className = 'st-key-map-container';
    container.querySelector = () => image;
    markers[0].parentElement = container;
    image.parentElement = container;
    containers.set(container.className, container);
    mutate();
    return image;
}
anchors.set(statusId, new Element(statusId));
let cleanup = mount();
flush();
assert.deepEqual(scrolls, [statusId]);
const scenario = input.scenario;
if (scenario === 'delayed_image') {
    addMap('old-run'); flush();
    assert.deepEqual(scrolls, [statusId]);
    const image = addMap('run-1', false); flush();
    assert.deepEqual(scrolls, [statusId]);
    image.complete = true; image.naturalWidth = 1200; image.height = 0;
    image.emit('load'); flush();
    assert.deepEqual(scrolls, [statusId]);
    image.height = 1250; mutate(); flush();
    assert.deepEqual(scrolls, [statusId, mapId]);
    mutate(); window.emit('resize'); image.emit('load'); flush();
    assert.deepEqual(scrolls, [statusId, mapId]);
} else if (scenario.startsWith('cancel_') && scenario !== 'cancel_pending_frame') {
    const event = scenario.slice(7);
    if (event === 'key') document.emit('keydown', { key: 'PageDown' });
    else if (event === 'anchor') document.emit('click', { target: { closest: selector => selector === 'a[href]' ? {} : null } });
    else if (event === 'scrollbar') document.emit('pointerdown', { button: 0, clientX: 998, clientY: 550 });
    else if (event === 'history') window.emit('popstate');
    else if (event === 'hash') window.emit('hashchange');
    else document.emit(event);
    cleanup(); cleanup = mount(); flush();
    addMap('run-1'); flush();
    assert.deepEqual(scrolls, [statusId]);
    assert.equal(window.__wspradarAnalysisNavigationState.cancelled, true);
} else if (scenario === 'cancel_pending_frame') {
    addMap('run-1');
    document.emit('wheel'); flush();
    assert.deepEqual(scrolls, [statusId]);
} else if (scenario === 'non_navigation_events') {
    main.emit('scroll'); window.emit('resize'); document.emit('click');
    document.emit('pointerdown', { button: 0, clientX: 200, clientY: 550 });
    document.emit('keydown', { key: 'ArrowDown', target: { closest: () => ({}) } });
    document.emit('keydown', { key: 'x' }); flush();
    addMap('run-1'); flush();
    assert.deepEqual(scrolls, [statusId, mapId]);
} else if (scenario === 'same_token_remount') {
    cleanup(); cleanup = mount(); flush();
    assert.deepEqual(scrolls, [statusId]);
    addMap('run-1'); flush();
    cleanup(); cleanup = mount(); flush();
    assert.deepEqual(scrolls, [statusId, mapId]);
} else if (scenario === 'new_token') {
    cleanup(); cleanup = mount('run-2'); flush();
    assert.deepEqual(scrolls, [statusId, statusId]);
    addMap('run-1'); flush();
    assert.deepEqual(scrolls, [statusId, statusId]);
    addMap('run-2'); flush();
    assert.deepEqual(scrolls, [statusId, statusId, mapId]);
    assert.equal(window.__wspradarAnalysisNavigationState.token, 'run-2');
} else if (scenario === 'passive_after_cancel' || scenario === 'passive_after_complete') {
    if (scenario === 'passive_after_complete') {
        addMap('run-1'); flush();
    } else {
        document.emit('wheel');
    }
    const pageTop = new Element('wspradar-page-top');
    pageTop.top = -770;
    anchors.set(pageTop.id, pageTop);
    // A real user scroll updates the visible region in the URL without
    // requesting an anchor landing. Preserve that precise viewport on rerun.
    main.scrollTop = 770;
    main.emit('scroll'); flush();
    assert.equal(window.location.hash, '#wspradar-page-top');
    const beforeRerender = [...scrolls];
    cleanup(); cleanup = mount(null); flush();
    assert.deepEqual(scrolls, beforeRerender);
    assert.equal(main.scrollTop, 770);
    // History navigation remains an explicit user request and still lands
    // at its target, even after passive tracking and a component remount.
    window.location.hash = `#${statusId}`;
    window.emit('popstate'); flush();
    assert.deepEqual(scrolls, [...beforeRerender, statusId]);
} else if (scenario === 'preceding_old_map' || scenario === 'preceding_stale_same_token_map') {
    const oldToken = scenario === 'preceding_old_map' ? 'old-run' : 'run-1';
    const oldImage = addMap(oldToken);
    const oldAnchor = anchors.get(mapId);
    const oldMarker = markers[0];
    const oldContainer = containers.get('st-key-map-container');
    if (scenario === 'preceding_stale_same_token_map') {
        const staleWrapper = new Element('stale-wrapper', { 'data-stale': 'true' });
        oldAnchor.parentElement = staleWrapper;
        oldContainer.parentElement = staleWrapper;
    }
    const currentImage = addMap('run-1', false);
    const currentAnchor = anchors.get(mapId);
    precedingAnchors.push(oldAnchor);
    precedingContainers.push(oldContainer);
    markers.unshift(oldMarker);
    assert.equal(document.getElementById(mapId), oldAnchor);
    flush();
    assert.deepEqual(scrolls, [statusId]);
    currentImage.complete = true; currentImage.naturalWidth = 1200;
    currentImage.emit('load'); flush();
    assert.deepEqual(scrolls, [statusId, mapId]);
    assert.equal(scrolledElements.at(-1), currentAnchor);
    assert.equal(oldImage.listenerCount(), 0);
} else if (scenario === 'stale_current_map_elements') {
    const image = addMap('run-1');
    const container = containers.get('st-key-map-container');
    const anchorWrapper = new Element('anchor-wrapper', { 'data-stale': 'true' });
    const markerWrapper = new Element('marker-wrapper', { 'data-stale': 'true' });
    const imageWrapper = new Element('image-wrapper', { 'data-stale': 'true' });
    anchors.get(mapId).parentElement = anchorWrapper;
    markerWrapper.parentElement = container;
    markers[0].parentElement = markerWrapper;
    imageWrapper.parentElement = container;
    image.parentElement = imageWrapper;
    flush();
    assert.deepEqual(scrolls, [statusId]);
    for (const wrapper of [anchorWrapper, markerWrapper]) {
        wrapper.attributes['data-stale'] = 'false';
        mutate('data-stale'); flush();
        assert.deepEqual(scrolls, [statusId]);
    }
    imageWrapper.attributes['data-stale'] = 'false';
    mutate('data-stale'); flush();
    assert.deepEqual(scrolls, [statusId, mapId]);
} else if (scenario === 'ordinary_rerender') {
    cleanup(); cleanup = mount(null); flush();
    addMap('run-1'); flush();
    assert.deepEqual(scrolls, [statusId]);
} else if (scenario === 'already_mounted_map') {
    cleanup();
    addMap('run-2'); cleanup = mount('run-2'); flush();
    assert.deepEqual(scrolls, [statusId, statusId, mapId]);
} else {
    throw new Error('Unknown scenario: ' + scenario);
}
cleanup();
assert.equal(document.listenerCount(), 0);
assert.equal(window.listenerCount(), 0);
assert.equal(main.listenerCount(), 0);
assert.equal(frames.size, 0);
assert.equal(observers.filter(observer => observer.active).length, 0);
for (const container of [...precedingContainers, ...containers.values()]) assert.equal(container.querySelector().listenerCount(), 0);
process.stdout.write('ok');
"""


_GUIDED_PANEL_NAVIGATION_BROWSER_HARNESS = (
    _ANALYSIS_NAVIGATION_BROWSER_HARNESS.split(
        "anchors.set(statusId, new Element(statusId));", 1,
    )[0]
    + r"""
const parameterId = 'wspradar-parameter-settings';
const panelKey = 'guided_step_reference_design';
const requestToken = 'continue-1';
const animations = [];
document.getAnimations = () => animations;
anchors.set(parameterId, new Element(parameterId));
function mountPanel(token = requestToken, focusOptions = {}) {
    return mount(null, {
        requestAnchorId: parameterId,
        requestToken: token,
        shouldScrollRequest: true,
        panelKey,
        ...focusOptions,
    });
}
function addPanel({token = requestToken, key = panelKey, open = true, stale = false} = {}) {
    const panel = new Element('panel-' + panelMarkers.length, {'data-testid': 'stExpander'});
    const details = new Element('details-' + panelMarkers.length);
    details.tagName = 'DETAILS';
    details.open = open;
    details.parentElement = panel;
    const header = new Element('header-' + panelMarkers.length);
    header.parentElement = details;
    const marker = new Element('panel-marker-' + panelMarkers.length, {
        'data-page-navigation-token': token,
        'data-page-navigation-panel': key,
    });
    marker.parentElement = details;
    panel.querySelector = selector => selector === 'details' ? details : null;
    details.querySelector = selector => selector === 'summary' ? header : null;
    const wrapper = new Element('panel-wrapper-' + panelMarkers.length, {
        'data-stale': stale ? 'true' : 'false',
    });
    panel.parentElement = wrapper;
    panelMarkers.push(marker);
    mutate();
    return {panel, details, header, marker, wrapper};
}
let cleanup = mountPanel();
flush();
assert.deepEqual(scrolls, []);
assert.equal(window.location.hash, '#' + parameterId);
const scenario = input.scenario;
if (scenario === 'delayed_marker_and_open') {
    addPanel({token: 'previous-continue'}); flush();
    assert.deepEqual(scrolls, []);
    const current = addPanel({open: false}); flush();
    assert.deepEqual(scrolls, []);
    assert.equal(current.details.open, false);
    current.details.open = true;
    mutate('open'); flushFrame();
    assert.deepEqual(scrolls, []);
    flush();
    assert.deepEqual(scrolledElements, [current.header]);
} else if (scenario === 'preceding_wrong_panel_token_and_stale') {
    addPanel({key: 'guided_step_target_and_window'});
    addPanel({token: 'previous-continue'});
    addPanel({stale: true});
    const current = addPanel(); flush();
    assert.deepEqual(scrolledElements, [current.header]);
} else if (scenario === 'current_panel_becomes_nonstale') {
    const current = addPanel({stale: true}); flush();
    assert.deepEqual(scrolls, []);
    current.wrapper.attributes['data-stale'] = 'false';
    mutate('data-stale'); flush();
    assert.deepEqual(scrolledElements, [current.header]);
} else if (scenario === 'moving_header_waits_for_stable_frames') {
    const current = addPanel();
    flushFrame();
    for (const top of [380, 250, 130]) {
        current.header.top = top;
        flushFrame();
        assert.deepEqual(scrolls, []);
    }
    flushFrame();
    assert.deepEqual(scrolls, []);
    flushFrame();
    assert.deepEqual(scrolledElements, [current.header]);
} else if (scenario === 'same_token_remount_does_not_repeat') {
    const current = addPanel(); flush();
    assert.deepEqual(scrolledElements, [current.header]);
    mutate(); window.emit('resize'); flush();
    cleanup(); cleanup = mountPanel(); flush();
    mutate(); flush();
    assert.deepEqual(scrolledElements, [current.header]);
} else if (scenario === 'pending_request_resumes_after_remount') {
    const current = addPanel(); flushFrame();
    assert.deepEqual(scrolls, []);
    cleanup(); cleanup = mountPanel(); flush();
    assert.deepEqual(scrolledElements, [current.header]);
    cleanup(); cleanup = mountPanel(); flush();
    assert.deepEqual(scrolledElements, [current.header]);
} else if (scenario === 'accordion_animation_delays_stable_header') {
    const current = addPanel();
    const opening = {playState: 'running', effect: {target: current.details}};
    animations.push(opening);
    for (let frame = 0; frame < 5; frame++) {
        flushFrame();
        assert.deepEqual(scrolls, []);
    }
    opening.playState = 'finished';
    animations.push({playState: 'running', effect: {target: main}});
    flush();
    assert.deepEqual(scrolledElements, [current.header]);
} else if (scenario === 'status_spinner_does_not_delay_panel_landing') {
    const current = addPanel();
    const status = addPanel({token: 'unrelated-status'});
    const spinner = new Element('status-spinner');
    spinner.tagName = 'SPAN';
    spinner.parentElement = status.details;
    animations.push({playState: 'running', effect: {target: spinner}});
    flush();
    assert.deepEqual(scrolledElements, [current.header]);
} else if (scenario === 'unrelated_accordion_does_not_delay_panel_landing') {
    const current = addPanel();
    const unrelated = addPanel({token: 'unrelated-panel'});
    animations.push({playState: 'running', effect: {target: unrelated.details}});
    flush();
    assert.deepEqual(scrolledElements, [current.header]);
} else if (scenario === 'new_request_waits_for_its_own_marker') {
    const first = addPanel(); flush();
    cleanup(); cleanup = mountPanel('continue-2'); flush();
    assert.deepEqual(scrolledElements, [first.header]);
    const second = addPanel({token: 'continue-2'}); flush();
    assert.deepEqual(scrolledElements, [first.header, second.header]);
} else if (scenario === 'user_navigation_cancels_pending_landing' || scenario === 'navigation_key_cancels_pending_landing') {
    addPanel();
    if (scenario === 'navigation_key_cancels_pending_landing') {
        document.emit('keydown', {key: 'PageDown'});
    } else {
        document.emit('wheel');
    }
    flush(); mutate(); flush();
    assert.deepEqual(scrolls, []);
    cleanup(); cleanup = mountPanel(); flush();
    assert.deepEqual(scrolls, []);
} else if (scenario === 'editable_key_does_not_cancel_landing') {
    const current = addPanel();
    document.emit('keydown', {key: 'ArrowDown', target: {closest: () => ({})}});
    flush();
    assert.deepEqual(scrolledElements, [current.header]);
} else if (scenario === 'cleanup_cancels_pending_landing') {
    addPanel();
    cleanup();
    flush(); mutate(); flush();
    assert.deepEqual(scrolls, []);
} else {
    throw new Error('Unknown Guided panel scenario: ' + scenario);
}
assert.equal(scrolls.includes(parameterId), false);
cleanup();
assert.equal(document.listenerCount(), 0);
assert.equal(window.listenerCount(), 0);
assert.equal(main.listenerCount(), 0);
assert.equal(frames.size, 0);
assert.equal(observers.filter(observer => observer.active).length, 0);
process.stdout.write('ok');
"""
)


@pytest.mark.parametrize("scenario", [
    "delayed_marker_and_open",
    "preceding_wrong_panel_token_and_stale",
    "current_panel_becomes_nonstale",
    "moving_header_waits_for_stable_frames",
    "same_token_remount_does_not_repeat",
    "pending_request_resumes_after_remount",
    "accordion_animation_delays_stable_header",
    "status_spinner_does_not_delay_panel_landing",
    "unrelated_accordion_does_not_delay_panel_landing",
    "new_request_waits_for_its_own_marker",
    "user_navigation_cancels_pending_landing",
    "navigation_key_cancels_pending_landing",
    "editable_key_does_not_cancel_landing",
    "cleanup_cancels_pending_landing",
])
def test_guided_panel_navigation_browser_waits_for_current_stable_header(scenario):
    """Exercise Continue against delayed, stale, moving and rerendered panels."""
    _run_navigation_browser_harness(_GUIDED_PANEL_NAVIGATION_BROWSER_HARNESS, scenario)


_GUIDED_FOCUS_NAVIGATION_BROWSER_HARNESS = (
    _GUIDED_PANEL_NAVIGATION_BROWSER_HARNESS.split("let cleanup = mountPanel();", 1)[0]
    + r"""
function addControl(parent, id, {tag = 'INPUT', attributes = {}, disabled = false, checked = false} = {}) {
    const control = new Element(id, attributes);
    control.tagName = tag;
    control.parentElement = parent;
    control.disabled = disabled;
    control.checked = checked;
    return control;
}
function addField(parent, key) {
    const field = new Element(key);
    field.className = 'st-key-' + key;
    field.parentElement = parent;
    return field;
}
const scenario = input.scenario;
const focusOptions = scenario === 'review_header'
    ? {focusTarget: 'panel_header'}
    : scenario.startsWith('invalid_')
        ? {focusFieldKey: scenario === 'invalid_date_spinbutton' ? 'val_start_d' : 'val_qth', ...(scenario === 'invalid_without_panel_key' ? {panelKey: null} : {})}
        : {focusTarget: 'first_input'};
let cleanup = mountPanel(requestToken, focusOptions);
const current = addPanel({open: scenario !== 'invalid_without_panel_key'});
let expected;
if (scenario === 'review_header') {
    addControl(current.details, 'run-action', {tag: 'BUTTON'});
    expected = current.header;
} else if (scenario === 'first_visible_enabled_input') {
    addControl(current.details, 'disabled', {disabled: true});
    addControl(current.details, 'hidden', {attributes: {type: 'hidden'}});
    const help = new Element('help', {'data-testid': 'stTooltipIcon'});
    help.parentElement = current.details;
    addControl(help, 'help-button', {tag: 'BUTTON'});
    const popover = new Element('help-popover', {'data-testid': 'stPopover'});
    popover.parentElement = current.details;
    addControl(popover, 'popover-trigger', {tag: 'BUTTON'});
    const invisible = new Element('invisible', {hidden: ''});
    invisible.parentElement = current.details;
    addControl(invisible, 'invisible-input');
    const disabledGroup = new Element('disabled-group', {disabled: ''});
    disabledGroup.tagName = 'FIELDSET'; disabledGroup.parentElement = current.details;
    addControl(disabledGroup, 'fieldset-disabled');
    expected = addControl(current.details, 'callsign');
} else if (scenario === 'choice_button') {
    expected = addControl(current.details, 'reference-station-choice', {tag: 'BUTTON'});
    addControl(current.details, 'reference-callsign');
} else if (scenario === 'selected_radio') {
    addControl(current.details, 'first-radio', {attributes: {type: 'radio', name: 'choice'}});
    expected = addControl(current.details, 'selected-radio', {attributes: {type: 'radio', name: 'choice'}, checked: true});
} else if (scenario === 'slider') {
    expected = addControl(current.details, 'radius-slider', {tag: 'DIV', attributes: {role: 'slider', tabindex: '0'}});
} else if (scenario === 'invalid_date_spinbutton') {
    addControl(current.details, 'unrelated-valid-input');
    const field = addField(current.details, 'val_start_d');
    addControl(field, 'clipped-native-date', {attributes: {type: 'date', 'aria-hidden': 'true', tabindex: '-1'}});
    expected = addControl(field, 'date-day', {tag: 'SPAN', attributes: {role: 'spinbutton', contenteditable: 'true', tabindex: '0'}});
    addControl(field, 'date-month', {tag: 'SPAN', attributes: {role: 'spinbutton', contenteditable: 'true', tabindex: '0'}});
} else if (scenario.startsWith('invalid_')) {
    addControl(current.details, 'unrelated-valid-input');
    const stale = addField(current.details, 'val_qth');
    stale.attributes['data-stale'] = 'true';
    addControl(stale, 'stale-invalid-input');
    const field = addField(current.details, 'val_qth');
    expected = addControl(field, 'actual-invalid-input');
} else if (scenario === 'delayed_input') {
    flush();
    assert.deepEqual(focusedElements, []);
    assert.deepEqual(scrolledElements, []);
    expected = addControl(current.details, 'delayed-input');
    mutate();
} else if (scenario === 'focus_move_cancels' || scenario === 'pointer_cancels') {
    expected = addControl(current.details, 'pending-input');
    document.emit(scenario === 'pointer_cancels' ? 'pointerdown' : 'focusin', {button: 0});
    flush(); mutate(); flush();
    cleanup(); cleanup = mountPanel(requestToken, focusOptions); flush();
    assert.deepEqual(focusedElements, []);
    assert.deepEqual(scrolledElements, []);
    expected = null;
} else if (scenario === 'settled_once_after_remount') {
    expected = addControl(current.details, 'first-input');
    flushFrame();
    assert.deepEqual(focusedElements, []);
    cleanup(); cleanup = mountPanel(requestToken, focusOptions);
} else {
    throw new Error('Unknown focus scenario: ' + scenario);
}
flush();
if (expected) {
    assert.deepEqual(focusedElements, [expected]);
    assert.deepEqual(scrolledElements, [current.header]);
    mutate(); flush();
    cleanup(); cleanup = mountPanel(requestToken, focusOptions); flush();
    assert.deepEqual(focusedElements, [expected]);
    assert.deepEqual(scrolledElements, [current.header]);
}
cleanup();
assert.equal(document.listenerCount(), 0);
assert.equal(window.listenerCount(), 0);
assert.equal(main.listenerCount(), 0);
assert.equal(frames.size, 0);
assert.equal(observers.filter(observer => observer.active).length, 0);
process.stdout.write('ok');
"""
)


@pytest.mark.parametrize("scenario", [
    "first_visible_enabled_input", "choice_button", "selected_radio", "slider", "invalid_date_spinbutton",
    "review_header", "invalid_field", "invalid_without_panel_key", "delayed_input",
    "focus_move_cancels", "pointer_cancels", "settled_once_after_remount",
])
def test_guided_panel_focus_uses_actual_controls_after_settled_navigation(scenario):
    _run_navigation_browser_harness(_GUIDED_FOCUS_NAVIGATION_BROWSER_HARNESS, scenario)


@pytest.mark.parametrize("scenario", [
    "delayed_image", "cancel_wheel", "cancel_touchmove", "cancel_key",
    "cancel_anchor", "cancel_history", "cancel_hash", "cancel_scrollbar", "cancel_pending_frame",
    "non_navigation_events", "same_token_remount", "new_token",
    "ordinary_rerender", "already_mounted_map",
    "passive_after_cancel", "passive_after_complete",
    "preceding_old_map", "preceding_stale_same_token_map", "stale_current_map_elements",
])
def test_analysis_navigation_browser_milestones(scenario):
    """Execute the browser controller against delayed DOM and user-event cases."""
    _run_navigation_browser_harness(_ANALYSIS_NAVIGATION_BROWSER_HARNESS, scenario)


def _run_navigation_browser_harness(harness, scenario):
    """Run one scenario with the actual browser controller and shared DOM model."""
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is required for the browser-controller event harness")
    result = subprocess.run(
        [node, "-e", harness],
        input=json.dumps({
            "javascript": page_navigation._PAGE_NAVIGATION_CONTROLLER_JS,
            "scenario": scenario,
        }),
        text=True, encoding="utf-8", capture_output=True, timeout=15, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == "ok"


@pytest.mark.parametrize(
    "source,stored_token,current_token,request_token,live_token,existing_rerender,invalid,expected,called",
    [
        ("main_button", None, "fresh", "fresh", "fresh", False, False, "fresh", True),
        ("demo", None, "fresh", "fresh", "fresh", False, False, "fresh", True),
        ("url_replay", None, "fresh", "fresh", "fresh", False, False, "fresh", True),
        (None, "same", "same", None, "same", False, False, "same", True),
        ("unknown", None, "fresh", "fresh", "fresh", False, False, None, True),
        ("presentation_rerender", "old", "new", "new", "new", False, False, None, True),
        (None, "old", "new", None, "new", True, False, None, True),
        ("main_button", "old", "fresh", "fresh", "fresh", False, True, None, True),
        (None, "old", None, None, None, False, False, None, True),
        ("main_button", "new-B", "old-A", "old-A", "new-B", False, False, "new-B", False),
        ("main_button", "old", "fresh", "fresh", None, False, True, "old", False),
    ],
)
def test_actual_application_arms_navigation_only_for_owned_explicit_submissions(
    source, stored_token, current_token, request_token, live_token, existing_rerender, invalid, expected, called,
):
    """Execute the real app's lightweight navigation block with isolated state."""
    app_source = (REPOSITORY_ROOT / "app.py").read_text(encoding="utf-8")
    syntax = ast.parse(app_source)
    navigation_assignment = next(
        node for node in ast.walk(syntax)
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "analysis_navigation_state_key" for target in node.targets)
    )
    # Find the real contiguous statement list even when a stable output region
    # wraps the app body. Execute its actual code, without the Streamlit context.
    statements = next(
        value
        for parent in ast.walk(syntax)
        for _field, value in ast.iter_fields(parent)
        if isinstance(value, list) and navigation_assignment in value
    )
    start = statements.index(navigation_assignment)
    end = next(
        index for index, statement in enumerate(statements[start:], start)
        if any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "render_page_navigation_controller"
            for node in ast.walk(statement)
        )
    )
    controller = Mock()
    consume_url = Mock()
    consume_request = Mock()
    ordinary_request = {"anchor_id": "ordinary", "request_token": "ordinary", "should_scroll": True}
    state_key = "_analysis_navigation_submission_token"
    session_state = {} if stored_token is None else {state_key: stored_token}
    original_state = dict(session_state)
    consume_request.return_value = ordinary_request
    namespace = {
        "st": SimpleNamespace(session_state=session_state),
        "submission_request": None if source is None else SimpleNamespace(source=source, token=request_token),
        "submission_token": current_token,
        "submission_initialization_failed": invalid,
        "is_existing_run_rerender": existing_rerender,
        "consume_page_navigation_request": consume_request,
        "get_analysis_submission": lambda _state: None if live_token is None else SimpleNamespace(token=live_token),
        "consume_url_replay_navigation": consume_url,
        "render_page_navigation_controller": controller,
    }
    selected = ast.Module(body=statements[start:end + 1], type_ignores=[])
    exec(compile(selected, str(REPOSITORY_ROOT / "app.py"), "exec"), namespace)
    if called:
        controller.assert_called_once_with(
            None if expected else ordinary_request,
            analysis_submission_token=expected,
        )
        consume_url.assert_called_once_with(session_state)
        consume_request.assert_called_once_with(session_state)
    else:
        controller.assert_not_called()
        consume_url.assert_not_called()
        consume_request.assert_not_called()
        assert session_state == original_state
    assert session_state.get(state_key) == expected
    assert statements[end].lineno < next(
        node.lineno for node in ast.walk(syntax)
        if isinstance(node, ast.ImportFrom) and node.module == "core.plot_engine"
    )
