"""Shared input help preserves native keyboard control and localized content."""

import json
import shutil
import subprocess
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from ui import input_keyboard


def test_registry_is_render_scoped_and_preserves_native_markdown(monkeypatch):
    state = {"_input_keyboard_help": {"old": {}}}
    controller = Mock()
    monkeypatch.setattr(input_keyboard, "st", SimpleNamespace(session_state=state))
    monkeypatch.setattr(input_keyboard, "_INPUT_KEYBOARD_CONTROLLER", controller)
    input_keyboard.begin_input_keyboard()
    source = "Exact **localized** help."
    assert input_keyboard.keyboard_help(
        "guided_reference_design_reference_station", source,
        mouse_help_key="guided_reference_design_reference_station_help",
    ) == source
    input_keyboard.render_input_keyboard_controller()
    assert controller.call_args.kwargs == {
        "data": {
            "descriptors": ({
                "widgetKey": "guided_reference_design_reference_station",
                "markdown": source,
                "mouseHelpKey": "guided_reference_design_reference_station_help",
            },),
        },
        "key": input_keyboard.INPUT_KEYBOARD_CONTROLLER_KEY,
        "width": "stretch",
        "height": 1,
    }
    input_keyboard.begin_input_keyboard()
    input_keyboard.render_input_keyboard_controller()
    assert controller.call_args.kwargs["data"] == {"descriptors": ()}


@pytest.mark.parametrize("key", [None, "", "x" * 161, "<button>", 'x"]', 1])
def test_help_registration_rejects_untrusted_widget_keys(monkeypatch, key):
    monkeypatch.setattr(input_keyboard, "st", SimpleNamespace(session_state={}))
    with pytest.raises(ValueError):
        input_keyboard.keyboard_help(key, "Help")
    with pytest.raises(ValueError):
        input_keyboard.keyboard_help("valid", "Help", mouse_help_key=key if key is not None else "")


@pytest.mark.parametrize("text", [None, "", " ", "x" * 8193])
def test_help_registration_rejects_empty_or_unbounded_content(monkeypatch, text):
    monkeypatch.setattr(input_keyboard, "st", SimpleNamespace(session_state={}))
    with pytest.raises(ValueError):
        input_keyboard.keyboard_help("val_callsign", text)


_BROWSER_HARNESS = r"""
const assert = require('node:assert/strict');
const vm = require('node:vm');
const payload = JSON.parse(require('node:fs').readFileSync(0, 'utf8'));
class Text {
    constructor(text) { this.textContent = text; this.nodeType = 3; this.parentElement = null; }
}
class Element {
    constructor(tag) {
        this.tagName = tag.toUpperCase(); this.nodeType = 1;
        this.children = []; this.attributes = new Map(); this.style = {};
        this.parentElement = null; this.disabled = false; this.open = true;
        this.attributeWrites = 0;
    }
    get id() { return this.getAttribute('id') ?? ''; }
    set id(value) { this.setAttribute('id', value); }
    get isConnected() {
        let current = this;
        while (current) { if (current === document.body) return true; current = current.parentElement; }
        return false;
    }
    get textContent() { return this.children.map(child => child.textContent).join(''); }
    set textContent(value) { this.replaceChildren(new Text(value)); }
    set innerHTML(_value) { throw Error('Data must never become raw HTML'); }
    getAttribute(key) { return this.attributes.has(key) ? this.attributes.get(key) : null; }
    setAttribute(key, value) { this.attributes.set(key, String(value)); this.attributeWrites++; }
    removeAttribute(key) { this.attributes.delete(key); }
    appendChild(child) { child.parentElement = this; this.children.push(child); return child; }
    replaceChildren(...children) {
        for (const child of this.children) child.parentElement = null;
        this.children = []; children.forEach(child => this.appendChild(child));
    }
    remove() {
        if (this.parentElement) {
            this.parentElement.children = this.parentElement.children.filter(child => child !== this);
            this.parentElement = null;
        }
    }
    contains(child) {
        while (child) { if (child === this) return true; child = child.parentElement; }
        return false;
    }
    matches(selector) {
        return selector.split(',').some(part => {
            part = part.trim();
            const not = part.match(/:not\(([^)]+)\)/);
            if (not) {
                if (this.matches(not[1])) return false;
                part = part.replace(not[0], '');
            }
            if (part.startsWith('.')) return (this.getAttribute('class') ?? '').split(' ').includes(part.slice(1));
            const attribute = part.match(/^([a-z]+)?\[([^=\]]+)(?:="([^"]*)")?\]$/i);
            if (attribute) {
                return (!attribute[1] || this.tagName === attribute[1].toUpperCase())
                    && this.attributes.has(attribute[2])
                    && (attribute[3] === undefined || this.getAttribute(attribute[2]) === attribute[3]);
            }
            return this.tagName === part.toUpperCase();
        });
    }
    closest(selector) {
        let current = this;
        while (current) { if (current.matches(selector)) return current; current = current.parentElement; }
        return null;
    }
    querySelectorAll(selector) {
        const result = [];
        for (const child of this.children) if (child.nodeType === 1) {
            if (child.matches(selector)) result.push(child);
            result.push(...child.querySelectorAll(selector));
        }
        return result;
    }
    querySelector(selector) { return this.querySelectorAll(selector)[0] ?? null; }
    getClientRects() { return this.isConnected ? [this.getBoundingClientRect()] : []; }
    getBoundingClientRect() { return { left: 100, top: 100, bottom: 140, width: 220, height: 80 }; }
}
function eventTarget(target) {
    target.listeners = new Map();
    target.addEventListener = (type, callback) => {
        if (!target.listeners.has(type)) target.listeners.set(type, new Set());
        target.listeners.get(type).add(callback);
    };
    target.removeEventListener = (type, callback) => target.listeners.get(type)?.delete(callback);
    target.emit = (type, event) => {
        for (const callback of target.listeners.get(type) ?? []) callback(event);
    };
    return target;
}
const document = eventTarget({
    body: new Element('body'), activeElement: null,
    createElement: tag => new Element(tag),
    createTextNode: text => new Text(text),
    querySelector: selector => document.body.querySelector(selector),
    querySelectorAll: selector => document.body.querySelectorAll(selector),
});
let nextFrame = 0;
const frames = new Map();
const window = eventTarget({
    innerWidth: 1024, innerHeight: 768,
    getComputedStyle: element => ({ display: 'block', visibility: 'visible', ...element.style }),
    requestAnimationFrame: callback => { frames.set(++nextFrame, callback); return nextFrame; },
    cancelAnimationFrame: id => frames.delete(id),
});
const observers = [];
class MutationObserver {
    constructor(callback) { this.callback = callback; this.disconnected = false; observers.push(this); }
    observe(target, options) { this.target = target; this.options = options; }
    disconnect() { this.disconnected = true; }
}
function append(parent, tag, attributes = {}) {
    const element = parent.appendChild(new Element(tag));
    Object.entries(attributes).forEach(([key, value]) => element.setAttribute(key, value));
    return element;
}
const scope = append(document.body, 'div', { class: 'st-key-application_configuration' });
const field = append(scope, 'div', { class: 'st-key-val_callsign' });
const control = append(field, 'input', { 'aria-describedby': 'existing-description' });
const help = append(field, 'button', { 'data-testid': 'stTooltipIcon', tabindex: '0' });
const choiceField = append(scope, 'div', { class: 'st-key-guided_reference_design_reference_station' });
const choice = append(choiceField, 'button');
const mouseField = append(scope, 'div', { class: 'st-key-guided_reference_design_reference_station_help' });
const mouseHelp = append(mouseField, 'button');
const unregistered = append(scope, 'button', { 'data-testid': 'stTooltipIcon', tabindex: '0' });
const outsideField = append(document.body, 'div', { class: 'st-key-val_callsign' });
const outsideHelp = append(outsideField, 'button', { 'data-testid': 'stTooltipIcon', tabindex: '0' });
const summary = append(scope, 'summary', { tabindex: '0' });
const continueButton = append(scope, 'button', { class: 'st-key-guided_continue_use_case' });
const source = ':primary[**Target**] <img src=x onerror=alert(1)> ' + String.fromCharCode(96) + 'CALL/P' + String.fromCharCode(96) + '\n\nSecond paragraph.';
const descriptors = [
    { widgetKey: 'val_callsign', markdown: source, mouseHelpKey: null },
    { widgetKey: 'guided_reference_design_reference_station', markdown: '**Reference** comparison.', mouseHelpKey: 'guided_reference_design_reference_station_help' },
];
const context = { document, window, MutationObserver, CSS: { escape: value => value } };
const mount = vm.runInNewContext(payload.javascript.replace('export default function', '(function') + ')', context);
let cleanup = mount({ data: { descriptors } });
const host = () => document.body.querySelector('[data-wspradar-input-help]');
const descriptionIds = element => (element.getAttribute('aria-describedby') ?? '').split(' ').filter(Boolean);
const descriptionFor = element => host().querySelector(
    '[id="' + descriptionIds(element).find(id => id.startsWith('wspradar-input-description-')) + '"]'
);
function assertNoVisualHelp() {
    assert.equal(host().querySelector('[role="tooltip"]'), null);
    assert.ok(host().children.every(element => element.getAttribute('hidden') !== null));
}
function focus(element) {
    const previous = document.activeElement;
    if (previous) document.emit('focusout', { target: previous, relatedTarget: element });
    document.activeElement = element;
    document.emit('focusin', { target: element });
}
function mutation(target, type = 'attributes', extra = {}) {
    const observer = observers[observers.length - 1];
    observer.callback([{ target, type, ...extra }]);
}
function flush() {
    let count = 0;
    while (frames.size) {
        if (++count > 8) throw Error('RAF loop did not settle');
        const callbacks = [...frames.values()]; frames.clear();
        callbacks.forEach(callback => callback());
    }
}
if (payload.scenario === 'native_help_and_essential_actions') {
    assert.equal(help.getAttribute('tabindex'), '-1');
    assert.equal(mouseHelp.getAttribute('tabindex'), '-1');
    assert.equal(choice.getAttribute('tabindex'), null);
    assert.equal(continueButton.getAttribute('tabindex'), null);
    assert.equal(summary.getAttribute('tabindex'), '0');
    assert.equal(unregistered.getAttribute('tabindex'), '0');
    assert.equal(outsideHelp.getAttribute('tabindex'), '0');
    assert.equal(descriptionIds(control)[0], 'existing-description');
    assert.equal(descriptionIds(control).length, 2);
    assert.equal(descriptionIds(choice).length, 1);
} else if (payload.scenario === 'formatting_and_escaping') {
    focus(control);
    const description = descriptionFor(control);
    assert.equal(description.querySelector('strong').textContent, 'Target');
    assert.equal(description.querySelector('code').textContent, 'CALL/P');
    assert.equal(description.querySelectorAll('p').length, 2);
    assert.equal(description.querySelector('img'), null);
    assert.ok(description.textContent.includes('<img src=x onerror=alert(1)>'));
    focus(choice);
    assert.equal(descriptionFor(choice).textContent, 'Reference comparison.');
    assert.equal(document.activeElement, choice);
    assertNoVisualHelp();
} else if (payload.scenario === 'focus_typing_and_tab_never_render_visible_help') {
    focus(control);
    assertNoVisualHelp();
    const nativeEvent = { preventDefault() { throw Error('Native keys must remain available'); } };
    for (const key of ['Escape', 'Tab', 'ArrowRight', 'A']) {
        document.emit('keydown', { ...nativeEvent, key, target: control });
        document.emit('input', { ...nativeEvent, target: control });
        assertNoVisualHelp();
    }
    document.emit('keydown', { ...nativeEvent, key: 'Tab', shiftKey: true, target: control });
    mutation(field); flush();
    focus(choice); focus(control);
    assertNoVisualHelp();
    assert.equal(document.listeners.get('keydown')?.size ?? 0, 0);
    assert.equal(document.listeners.get('input')?.size ?? 0, 0);
} else if (payload.scenario === 'native_popup_keeps_description') {
    focus(control);
    const before = control.getAttribute('aria-describedby');
    control.setAttribute('aria-expanded', 'true'); mutation(control); flush();
    assertNoVisualHelp();
    assert.equal(control.getAttribute('aria-describedby'), before);
    control.setAttribute('aria-expanded', 'false'); mutation(control); flush();
    assertNoVisualHelp();
} else if (payload.scenario === 'hidden_disabled_stale_and_rerender') {
    focus(control);
    field.setAttribute('data-stale', 'true'); mutation(field); flush();
    assert.deepEqual(descriptionIds(control), ['existing-description']);
    assert.equal(help.getAttribute('tabindex'), '0');
    field.removeAttribute('data-stale');
    control.disabled = true; mutation(control); flush();
    assert.deepEqual(descriptionIds(control), ['existing-description']);
    control.disabled = false; field.setAttribute('hidden', ''); mutation(field); flush();
    assert.deepEqual(descriptionIds(control), ['existing-description']);
    field.removeAttribute('hidden');
    const replacement = append(field, 'input');
    control.remove(); mutation(field, 'childList', { addedNodes: [replacement], removedNodes: [control] }); flush();
    focus(replacement);
    assert.equal(descriptionIds(replacement).length, 1);
    assertNoVisualHelp();
} else if (payload.scenario === 'observer_batches_and_ignores_owned_dom') {
    const observer = observers[0];
    assert.equal(observers.length, 1);
    assert.ok(observer.options.attributeFilter.includes('aria-describedby'));
    mutation(field); mutation(field); mutation(field);
    assert.equal(frames.size, 1); flush(); assert.equal(frames.size, 0);
    mutation(descriptionFor(control), 'childList', { addedNodes: [], removedNodes: [] });
    assert.equal(frames.size, 0);
} else if (payload.scenario === 'react_description_replacement_recovers_without_loop') {
    focus(control);
    control.setAttribute('aria-describedby', 'react-aria-updated');
    mutation(control); flush();
    assert.equal(descriptionIds(control)[0], 'react-aria-updated');
    assert.equal(descriptionIds(control).length, 2);
    const writesAfterRecovery = control.attributeWrites;
    mutation(control); flush();
    assert.equal(control.attributeWrites, writesAfterRecovery);
    assert.equal(frames.size, 0);
    focus(choice);
    control.setAttribute('aria-describedby', 'react-aria-on-focus');
    focus(control);
    assert.equal(descriptionIds(control)[0], 'react-aria-on-focus');
    assert.equal(descriptionIds(control).length, 2);
    const description = host().querySelector('[id="' + descriptionIds(control)[1] + '"]');
    assert.equal(description.getAttribute('hidden'), '');
    assert.ok(description.textContent.includes('Second paragraph.'));
} else if (payload.scenario === 'responsive_help_triggers_all_skip_tab') {
    const alternateTrigger = append(mouseField, 'button', {
        'data-testid': 'stPopoverButton', tabindex: '0',
    });
    alternateTrigger.style.display = 'none';
    mutation(mouseField, 'childList', { addedNodes: [alternateTrigger] }); flush();
    assert.equal(mouseHelp.getAttribute('tabindex'), '-1');
    assert.equal(alternateTrigger.getAttribute('tabindex'), '-1');
    alternateTrigger.style.display = 'block';
    mouseHelp.style.display = 'none';
    window.emit('resize', {}); flush();
    assert.equal(alternateTrigger.getAttribute('tabindex'), '-1');
    assert.equal(choice.getAttribute('tabindex'), null);
    cleanup();
    assert.equal(mouseHelp.getAttribute('tabindex'), null);
    assert.equal(alternateTrigger.getAttribute('tabindex'), '0');
} else if (payload.scenario === 'stale_predecessors_do_not_hide_live_fields') {
    const staleScope = append(document.body, 'div', {
        class: 'st-key-application_configuration', 'data-stale': 'true',
    });
    document.body.children = [staleScope, ...document.body.children.filter(child => child !== staleScope)];
    const staleField = append(scope, 'div', { class: 'st-key-val_callsign', 'data-stale': 'true' });
    const staleInput = append(staleField, 'input', { 'aria-expanded': 'true' });
    const staleHelp = append(staleField, 'button', { 'data-testid': 'stTooltipIcon', tabindex: '0' });
    scope.children = [staleField, ...scope.children.filter(child => child !== staleField)];
    mutation(scope, 'childList', { addedNodes: [staleField] }); flush();
    focus(control);
    assertNoVisualHelp();
    assert.equal(descriptionIds(control).length, 2);
    assert.equal(descriptionIds(staleInput).length, 0);
    assert.equal(staleHelp.getAttribute('tabindex'), '0');
} else if (payload.scenario === 'segmented_date_preserves_native_accessibility') {
    const dateField = append(scope, 'div', { class: 'st-key-val_start_d' });
    const clipped = append(dateField, 'div', { 'aria-hidden': 'true' });
    const nativeInput = append(clipped, 'input', { type: 'date' });
    const segments = ['day', 'month', 'year'].map(name => append(dateField, 'span', {
        role: 'spinbutton', contenteditable: 'true', tabindex: '0',
        'aria-describedby': 'react-aria-description-' + name,
    }));
    const disabledFieldset = append(dateField, 'fieldset', { disabled: '' });
    const disabledSegment = append(disabledFieldset, 'span', { role: 'spinbutton', tabindex: '0' });
    cleanup = mount({ data: { descriptors: [
        ...descriptors, { widgetKey: 'val_start_d', markdown: 'UTC **date**.', mouseHelpKey: null },
    ] } });
    assert.equal(descriptionIds(nativeInput).length, 0);
    assert.equal(descriptionIds(disabledSegment).length, 0);
    for (const [index, segment] of segments.entries()) {
        assert.equal(descriptionIds(segment).length, 2);
        assert.equal(descriptionIds(segment)[0], 'react-aria-description-' + ['day', 'month', 'year'][index]);
        assert.equal(segment.getAttribute('tabindex'), '0');
        focus(segment);
        assert.equal(descriptionFor(segment).textContent, 'UTC date.');
        assertNoVisualHelp();
    }
} else if (payload.scenario === 'cleanup_preserves_foreign_ids_and_tab_changes') {
    control.setAttribute('aria-describedby', control.getAttribute('aria-describedby') + ' later-owner');
    help.setAttribute('tabindex', '7');
    mutation(field); assert.equal(frames.size, 1);
    cleanup();
    assert.equal(frames.size, 0);
    assert.equal(host(), null);
    assert.deepEqual(descriptionIds(control), ['existing-description', 'later-owner']);
    assert.equal(help.getAttribute('tabindex'), '7');
    assert.equal(mouseHelp.getAttribute('tabindex'), null);
    assert.equal(observers[0].disconnected, true);
    assert.equal([...document.listeners.values()].reduce((total, set) => total + set.size, 0), 0);
    assert.equal([...window.listeners.values()].reduce((total, set) => total + set.size, 0), 0);
} else if (payload.scenario === 'remount_replaces_descriptions_and_old_cleanup_is_inert') {
    const oldCleanup = cleanup;
    const previousId = descriptionIds(control)[1];
    cleanup = mount({ data: { descriptors: [{ ...descriptors[0], markdown: 'Neue **Hilfe**.' }] } });
    oldCleanup();
    assert.equal(document.body.querySelectorAll('[data-wspradar-input-help]').length, 1);
    assert.equal(descriptionIds(control).length, 2);
    assert.notEqual(descriptionIds(control)[1], previousId);
    assert.equal(mouseHelp.getAttribute('tabindex'), null);
    focus(control);
    assert.equal(descriptionFor(control).textContent, 'Neue Hilfe.');
    assertNoVisualHelp();
} else {
    throw Error('Unknown scenario ' + payload.scenario);
}
if (host()) assertNoVisualHelp();
cleanup();
assert.equal(host(), null);
process.stdout.write('ok');
"""


@pytest.mark.parametrize("scenario", [
    "native_help_and_essential_actions",
    "formatting_and_escaping",
    "focus_typing_and_tab_never_render_visible_help",
    "native_popup_keeps_description",
    "hidden_disabled_stale_and_rerender",
    "observer_batches_and_ignores_owned_dom",
    "react_description_replacement_recovers_without_loop",
    "responsive_help_triggers_all_skip_tab",
    "stale_predecessors_do_not_hide_live_fields",
    "segmented_date_preserves_native_accessibility",
    "cleanup_preserves_foreign_ids_and_tab_changes",
    "remount_replaces_descriptions_and_old_cleanup_is_inert",
])
def test_keyboard_help_browser_behavior(scenario):
    """Execute production JavaScript with controlled focus, DOM, and lifecycle."""
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is required for the keyboard-help browser harness")
    result = subprocess.run(
        [node, "-e", _BROWSER_HARNESS],
        input=json.dumps({
            "javascript": input_keyboard._INPUT_KEYBOARD_CONTROLLER_JS,
            "scenario": scenario,
        }),
        text=True, encoding="utf-8", capture_output=True, timeout=15, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == "ok"
