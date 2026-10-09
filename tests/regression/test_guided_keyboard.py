"""Guided keyboard boundaries wait for committed values and server validation."""

import json
import shutil
import subprocess

import pytest

from ui.guided_inputs import keyboard


_BROWSER_HARNESS = r"""
const assert = require('node:assert/strict');
const vm = require('node:vm');
const payload = JSON.parse(require('node:fs').readFileSync(0, 'utf8'));

class Element {
    constructor(tag, attributes = {}) {
        this.tagName = tag.toUpperCase();
        this.attributes = new Map(); this.children = []; this.parentElement = null;
        this.style = {}; this.disabled = false; this.checked = false; this.open = true;
        this.value = ''; this.validity = { valid: true }; this.focusCount = 0; this.onBlur = null;
        Object.entries(attributes).forEach(([key, value]) => this.setAttribute(key, value));
    }
    get isConnected() {
        let current = this;
        while (current) {
            if (current === document.body) return true;
            current = current.parentElement;
        }
        return false;
    }
    get tabIndex() {
        if (this.attributes.has('tabindex')) return Number(this.getAttribute('tabindex'));
        return ['INPUT', 'TEXTAREA', 'SELECT', 'BUTTON', 'SUMMARY'].includes(this.tagName)
            || (this.tagName === 'A' && this.attributes.has('href')) ? 0 : -1;
    }
    setAttribute(key, value) { this.attributes.set(key, String(value)); }
    getAttribute(key) { return this.attributes.get(key) ?? null; }
    removeAttribute(key) { this.attributes.delete(key); }
    appendChild(child) {
        child.parentElement = this; this.children.push(child); return child;
    }
    remove() {
        if (this.parentElement) {
            this.parentElement.children = this.parentElement.children.filter(child => child !== this);
            this.parentElement = null;
        }
    }
    matches(selector) {
        return selector.split(',').some(part => {
            part = part.trim();
            // The production adapter uses only simple selectors plus one
            // descendant selector for the adjacent native Continue button.
            if (part.includes(' ')) {
                const split = part.lastIndexOf(' ');
                return this.matches(part.slice(split + 1))
                    && Boolean(this.parentElement?.closest(part.slice(0, split)));
            }
            if (part.endsWith(':invalid')) {
                return this.matches(part.slice(0, -8)) && !this.validity.valid;
            }
            if (part.startsWith('.')) {
                return (this.getAttribute('class') ?? '').split(' ').includes(part.slice(1));
            }
            const tag = part.match(/^[a-z]+/i)?.[0];
            if (tag && this.tagName !== tag.toUpperCase()) return false;
            const attributes = [...part.matchAll(/\[([^=\]]+)(?:="([^"]*)")?\]/g)];
            if (attributes.length) {
                return attributes.every(([, key, value]) => this.attributes.has(key)
                    && (value === undefined || this.getAttribute(key) === value));
            }
            return Boolean(tag);
        });
    }
    closest(selector) {
        let current = this;
        while (current) {
            if (current.matches(selector)) return current;
            current = current.parentElement;
        }
        return null;
    }
    querySelectorAll(selector) {
        const found = [];
        for (const child of this.children) {
            if (child.matches(selector)) found.push(child);
            found.push(...child.querySelectorAll(selector));
        }
        return found;
    }
    querySelector(selector) { return this.querySelectorAll(selector)[0] ?? null; }
    getClientRects() { return this.isConnected ? [{}] : []; }
    focus() {
        if (document.activeElement !== this) document.activeElement?.blur();
        document.activeElement = this; this.focusCount++;
    }
    blur() {
        if (document.activeElement === this) {
            document.activeElement = document.body;
            this.onBlur?.();
        }
    }
}

function eventTarget(target) {
    target.listeners = new Map();
    target.addEventListener = (type, callback) => {
        if (!target.listeners.has(type)) target.listeners.set(type, new Set());
        target.listeners.get(type).add(callback);
    };
    target.removeEventListener = (type, callback) => target.listeners.get(type)?.delete(callback);
    target.emit = (type, event) => {
        for (const callback of [...(target.listeners.get(type) ?? [])]) callback(event);
    };
    return target;
}
const document = eventTarget({
    body: new Element('body'), activeElement: null,
    querySelector: selector => document.body.querySelector(selector),
    querySelectorAll: selector => document.body.querySelectorAll(selector),
});
const window = { getComputedStyle: element => ({
    display: 'block', visibility: 'visible', ...element.style,
}) };
let nextFrame = 0;
const frames = new Map();
const requestAnimationFrame = callback => { frames.set(++nextFrame, callback); return nextFrame; };
const cancelAnimationFrame = id => frames.delete(id);
function flush() {
    let attempts = 0;
    while (frames.size) {
        if (++attempts > 8) throw Error('Frame callbacks did not settle');
        const callbacks = [...frames.values()]; frames.clear();
        callbacks.forEach(callback => callback());
    }
}
function append(parent, tag, attributes = {}) {
    return parent.appendChild(new Element(tag, attributes));
}
const scope = append(document.body, 'div', { class: 'st-key-application_configuration' });
function makePanel(node) {
    const panel = append(scope, 'div', { 'data-testid': 'stExpander' });
    const details = append(panel, 'details');
    append(details, 'summary');
    const content = append(details, 'div');
    append(content, 'span', { 'data-wspradar-guided-node': node });
    return { panel, details, content };
}
const target = makePanel('target_and_window');
const firstField = append(target.content, 'div', { class: 'st-key-val_callsign' });
const first = append(firstField, 'input');
const finalField = append(target.content, 'div', { class: 'st-key-val_qth' });
const last = append(finalField, 'input');
last.value = 'JO62QM';
const help = append(finalField, 'button', { 'data-testid': 'stTooltipIcon' });
const continueWrapper = append(scope, 'div', { class: 'st-key-guided_continue_target_and_window' });
const continueButton = append(continueWrapper, 'button');
const review = makePanel('review_and_run');
const run = append(review.content, 'button', { class: 'st-key-run_analysis_button' });
const triggers = [];
const componentState = {};
const context = { document, window, requestAnimationFrame, cancelAnimationFrame };
const mount = vm.runInNewContext(
    payload.javascript.replace('export default function', '(function') + ')', context,
);
const baseData = {
    nodes: ['target_and_window', 'review_and_run'], terminal: 'review_and_run',
    values: [
        { key: 'val_callsign', kind: 'text', value: 'DL1ABC' },
        { key: 'val_qth', kind: 'text', value: 'JO62' },
    ], ack: null,
};
let cleanup;
function remount(overrides = {}) {
    cleanup = mount({
        data: { ...baseData, ...overrides },
        setTriggerValue(name, value) {
            triggers.push({
                kind: 'trigger', name, value: JSON.parse(JSON.stringify(value)), focus: document.activeElement,
            });
        },
        setStateValue(name, value) {
            const saved = JSON.parse(JSON.stringify(value));
            componentState[name] = saved;
            triggers.push({ kind: 'state', name, value: saved, focus: document.activeElement });
        },
    });
}
function key(element, key = 'Tab', extras = {}) {
    element.focus();
    const event = {
        key, target: element, shiftKey: false, ctrlKey: false, altKey: false, metaKey: false,
        defaultPrevented: false, stopped: false,
        preventDefault() { this.defaultPrevented = true; },
        stopPropagation() { this.stopped = true; },
        ...extras,
    };
    document.emit('keydown', event);
    return event;
}
function named(name) { return triggers.filter(event => event.name === name); }
function prepare(element = last) {
    const event = key(element);
    assert.equal(event.defaultPrevented, true);
    assert.equal(event.stopped, true);
    assert.equal(named('prepare').length, 1);
    assert.equal(named('prepare')[0].kind, 'state');
    assert.deepEqual(componentState.prepare, named('prepare')[0].value);
    assert.equal(named('advance').length, 0);
    return named('prepare')[0].value;
}
remount();
flush();

if (payload.scenario === 'inside_panel_native_keys_and_popups_are_untouched') {
    for (const [element, name, extras] of [
        [first, 'Tab', {}], [last, 'Tab', { shiftKey: true }],
        [last, 'Tab', { ctrlKey: true }], [last, 'Tab', { altKey: true }],
        [last, 'Tab', { metaKey: true }], [last, 'ArrowLeft', {}],
        [last, 'Enter', {}],
    ]) {
        const event = key(element, name, extras);
        assert.equal(event.defaultPrevented, false);
        assert.equal(event.stopped, false);
        assert.equal(document.activeElement, element);
    }
    last.setAttribute('aria-expanded', 'true');
    assert.equal(key(last).defaultPrevented, false);
    last.removeAttribute('aria-expanded');
    finalField.setAttribute('role', 'dialog');
    assert.equal(key(last).defaultPrevented, false);
    finalField.setAttribute('role', 'listbox');
    assert.equal(key(last).defaultPrevented, false);
    finalField.removeAttribute('role');
    finalField.setAttribute('data-baseweb', 'popover');
    assert.equal(key(last).defaultPrevented, false);
    assert.deepEqual(triggers, []);
} else if (payload.scenario === 'boundary_waits_for_matching_commit_ack_then_advances_once') {
    const intent = prepare();
    assert.deepEqual(intent.expected, { key: 'val_qth', kind: 'text', value: 'JO62QM' });
    assert.equal(intent.node, 'target_and_window');
    assert.equal(named('prepare')[0].focus, continueButton);
    assert.ok(intent.token);
    flush();
    assert.equal(named('advance').length, 0);
    remount({ ack: { ...intent, ready: false, fingerprint: 'old-values' } }); flush();
    assert.equal(named('advance').length, 0);
    const ack = { token: intent.token, node: intent.node, ready: true, fingerprint: 'committed-values' };
    remount({ ack }); flush();
    assert.deepEqual(named('advance').map(event => event.value), [
        { token: intent.token, fingerprint: 'committed-values' },
    ]);
    // Once the server has authorized advancement, extra Tab presses must not
    // cancel it or create another attempt while the next panel mounts.
    assert.equal(key(continueButton).defaultPrevented, true);
    assert.equal(named('prepare').length, 1);
    assert.equal(named('cancel').length, 0);
    assert.equal(window.__wspradarGuidedKeyboardPending.token, intent.token);
    remount({ ack }); flush();
    assert.equal(named('advance').length, 1);
    // The server consumes a completed attempt, releasing the browser guard.
    remount(); flush();
    assert.equal(window.__wspradarGuidedKeyboardPending, undefined);
} else if (payload.scenario === 'unsent_tab_retry_replaces_intent_and_rejects_old_ack') {
    const initial = prepare();
    remount({ ack: { ...initial, ready: false, fingerprint: 'not-committed' } }); flush();
    const retry = key(continueButton);
    assert.equal(retry.defaultPrevented, true);
    assert.equal(named('prepare').length, 2);
    assert.deepEqual(named('cancel').map(event => event.value), [initial.token]);
    const replacement = named('prepare')[1].value;
    assert.notEqual(replacement.token, initial.token);
    assert.equal(replacement.node, initial.node);
    assert.equal(replacement.expected, null);
    assert.equal(window.__wspradarGuidedKeyboardPending.token, replacement.token);
    assert.deepEqual(componentState.prepare, replacement);
    remount({ ack: { ...initial, ready: true, fingerprint: 'late-original' } }); flush();
    assert.equal(named('advance').length, 0);
    remount({ ack: { ...replacement, ready: true, fingerprint: 'retry-committed' } }); flush();
    assert.deepEqual(named('advance').map(event => event.value), [
        { token: replacement.token, fingerprint: 'retry-committed' },
    ]);
    assert.equal(key(continueButton).defaultPrevented, true);
    assert.equal(named('prepare').length, 2);
    assert.equal(named('cancel').length, 1);
    assert.equal(named('advance').length, 1);
} else if (payload.scenario === 'focused_stale_panel_keeps_native_edit_boundary_active') {
    // A native arrow edit starts Streamlit's rerun before the following Tab;
    // the old panel still contains the operator's focused and edited control.
    assert.equal(key(last, 'ArrowUp').defaultPrevented, false);
    target.panel.setAttribute('data-stale', 'true');
    last.value = 'JO63QM';
    const unrelated = makePanel('target_and_window');
    unrelated.panel.setAttribute('data-stale', 'true');
    const unrelatedInput = append(unrelated.content, 'input', { 'aria-invalid': 'true' });
    const intent = prepare();
    assert.deepEqual(intent.expected, { key: 'val_qth', kind: 'text', value: 'JO63QM' });
    assert.equal(document.activeElement, continueButton);
    assert.equal(unrelatedInput.focusCount, 0);
    assert.equal(named('cancel').length, 0);
    remount({ ack: { ...intent, ready: true, fingerprint: 'stale-panel-edit-committed' } }); flush();
    assert.equal(named('advance').length, 1);
} else if (payload.scenario === 'focused_stale_panel_still_rejects_incomplete_native_date') {
    const dateField = append(target.content, 'div', { class: 'st-key-val_end_d' });
    const segment = append(dateField, 'span', {
        'data-type': 'day', 'data-placeholder': 'true', contenteditable: 'true', tabindex: '0',
    });
    target.panel.setAttribute('data-stale', 'true');
    const event = key(segment);
    assert.equal(event.defaultPrevented, true);
    assert.equal(document.activeElement, segment);
    assert.equal(target.details.open, true);
    assert.equal(window.__wspradarGuidedKeyboardPending, undefined);
    assert.deepEqual(triggers, []);
} else if (payload.scenario === 'stale_panel_and_continue_predecessors_cannot_capture_transition') {
    const oldPanel = makePanel('target_and_window');
    oldPanel.panel.setAttribute('data-stale', 'true');
    const oldInvalid = append(oldPanel.content, 'input', { 'aria-invalid': 'true' });
    const oldContinueWrapper = append(scope, 'div', {
        class: 'st-key-guided_continue_target_and_window', 'data-stale': 'true',
    });
    const oldContinue = append(oldContinueWrapper, 'button');
    scope.children = [oldPanel.panel, oldContinueWrapper, ...scope.children.filter(
        element => element !== oldPanel.panel && element !== oldContinueWrapper
    )];
    assert.equal(document.querySelector('[data-wspradar-guided-node="target_and_window"]')
        .closest('[data-testid="stExpander"]'), oldPanel.panel);
    const intent = prepare(continueButton);
    assert.equal(intent.expected, null);
    assert.equal(document.activeElement, continueButton);
    assert.equal(oldInvalid.focusCount, 0);
    assert.equal(oldContinue.focusCount, 0);
    assert.equal(named('prepare')[0].focus, continueButton);
} else if (payload.scenario === 'native_blur_input_does_not_cancel_durable_prepare'
    || payload.scenario === 'native_blur_without_continue_preserves_durable_prepare') {
    let blurCommits = 0;
    last.onBlur = () => {
        blurCommits++;
        // Native widget blur may emit an input event while committing the edit.
        // Only subsequent independent edits are allowed to cancel preparation.
        assert.equal(window.__wspradarGuidedKeyboardPending, undefined);
        document.emit('input', { target: last });
    };
    if (payload.scenario === 'native_blur_without_continue_preserves_durable_prepare') {
        continueWrapper.remove();
    }
    const intent = prepare();
    assert.equal(blurCommits, 1);
    assert.equal(named('cancel').length, 0);
    assert.equal(window.__wspradarGuidedKeyboardPending.token, intent.token);
    assert.deepEqual(componentState.prepare, intent);
    // A native widget rerun can arrive before the prepare callback. Unlike a
    // one-tick trigger, the submitted intent remains in component state.
    remount(); flush();
    assert.deepEqual(componentState.prepare, intent);
    assert.equal(window.__wspradarGuidedKeyboardPending.token, intent.token);
    assert.equal(named('advance').length, 0);
    remount({ ack: { ...intent, ready: true, fingerprint: 'blur-committed-values' } }); flush();
    assert.equal(named('cancel').length, 0);
    assert.deepEqual(named('advance').map(event => event.value), [
        { token: intent.token, fingerprint: 'blur-committed-values' },
    ]);
} else if (payload.scenario === 'stale_acknowledgements_cannot_advance_current_attempt') {
    const intent = prepare();
    for (const ack of [
        { token: 'previous-token', node: intent.node, ready: true, fingerprint: 'old' },
        { token: intent.token, node: 'different-panel', ready: true, fingerprint: 'old' },
    ]) {
        remount({ ack }); flush();
        assert.equal(named('advance').length, 0);
    }
    const backward = key(continueButton, 'Tab', { shiftKey: true });
    assert.equal(backward.defaultPrevented, false);
    assert.deepEqual(named('cancel').map(event => event.value), [intent.token]);
    remount({ ack: { ...intent, ready: true, fingerprint: 'late-after-cancel' } }); flush();
    assert.equal(named('advance').length, 0);
} else if (payload.scenario === 'user_edits_pointer_and_keys_cancel_pending_transition') {
    const cancellations = [
        () => document.emit('input', { target: last }),
        () => document.emit('pointerdown', { target: first }),
        () => key(continueButton, 'ArrowLeft'),
        () => key(continueButton, 'Tab', { shiftKey: true }),
    ];
    for (const cancel of cancellations) {
        triggers.length = 0;
        const intent = prepare();
        cancel();
        assert.deepEqual(named('cancel').map(event => event.value), [intent.token]);
        assert.equal(named('cancel')[0].kind, 'state');
        assert.equal(componentState.cancel, intent.token);
        assert.equal(window.__wspradarGuidedKeyboardPending, undefined);
        remount({ ack: { ...intent, ready: true, fingerprint: 'cancelled' } }); flush();
        assert.equal(componentState.cancel, intent.token);
        assert.equal(named('advance').length, 0);
        remount(); flush();
    }
} else if (payload.scenario === 'incomplete_native_date_retains_panel_and_focuses_invalid_segment') {
    const dateField = append(target.content, 'div', { class: 'st-key-val_end_d' });
    const segment = append(dateField, 'span', {
        'data-type': 'day', 'data-placeholder': 'true', contenteditable: 'true', tabindex: '0',
    });
    const event = key(continueButton);
    assert.equal(event.defaultPrevented, true);
    assert.equal(document.activeElement, segment);
    assert.equal(target.details.open, true);
    assert.equal(window.__wspradarGuidedKeyboardPending, undefined);
    assert.deepEqual(triggers, []);
} else if (payload.scenario === 'invalid_native_field_is_not_replaced_by_old_server_value') {
    first.validity.valid = false;
    const event = key(last);
    assert.equal(event.defaultPrevented, true);
    assert.equal(document.activeElement, first);
    assert.deepEqual(triggers, []);
    first.validity.valid = true;
    first.setAttribute('aria-invalid', 'true');
    key(last);
    assert.equal(document.activeElement, first);
    assert.deepEqual(triggers, []);
} else if (payload.scenario === 'invalid_nonfocusable_group_focuses_first_available_descendant') {
    const group = append(target.content, 'div', { role: 'group', 'aria-invalid': 'true' });
    const disabled = append(group, 'span', { tabindex: '0', 'aria-disabled': 'true' });
    const hidden = append(group, 'div', { hidden: '' });
    append(hidden, 'input');
    const firstSegment = append(group, 'span', {
        role: 'spinbutton', contenteditable: 'true', tabindex: '0', 'data-type': 'day',
    });
    append(group, 'span', {
        role: 'spinbutton', contenteditable: 'true', tabindex: '0', 'data-type': 'month',
    });
    assert.equal(group.tabIndex, -1);
    const event = key(continueButton);
    assert.equal(event.defaultPrevented, true);
    assert.equal(document.activeElement, firstSegment);
    assert.equal(group.focusCount, 0);
    assert.equal(disabled.focusCount, 0);
    assert.equal(target.details.open, true);
    assert.deepEqual(triggers, []);
} else if (payload.scenario === 'help_and_unavailable_controls_do_not_move_panel_boundary') {
    const customHelp = append(target.content, 'div', {
        class: 'st-key-guided_reference_design_reference_station_help',
    });
    const customHelpButton = append(customHelp, 'button');
    const disabled = append(target.content, 'input'); disabled.disabled = true;
    const hidden = append(target.content, 'div', { hidden: '' }); append(hidden, 'input');
    const stale = append(target.content, 'div', { 'data-stale': 'true' }); append(stale, 'input');
    const unavailable = append(target.content, 'input', { 'aria-disabled': 'true' });
    const visuallyHidden = append(target.content, 'input'); visuallyHidden.style.visibility = 'hidden';
    const untabbable = append(target.content, 'button', { tabindex: '-1' });
    for (const element of [help, customHelpButton, disabled, unavailable, untabbable]) {
        assert.equal(key(element).defaultPrevented, false);
    }
    assert.deepEqual(triggers, []);
    const intent = prepare();
    assert.equal(intent.expected.value, 'JO62QM');
} else if (payload.scenario === 'terminal_review_never_prepares_or_submits') {
    for (const element of [review.details.querySelector('summary'), run]) {
        assert.equal(key(element).defaultPrevented, false);
        assert.equal(key(element, 'Enter').defaultPrevented, false);
    }
    const outside = append(document.body, 'input');
    assert.equal(key(outside).defaultPrevented, false);
    assert.deepEqual(triggers, []);
    assert.equal(window.__wspradarGuidedKeyboardPending, undefined);
} else if (payload.scenario === 'continue_boundary_uses_validation_without_inventing_field_snapshot') {
    const intent = prepare(continueButton);
    assert.equal(intent.expected, null);
    assert.equal(named('prepare')[0].focus, continueButton);
    assert.equal(named('advance').length, 0);
} else if (payload.scenario === 'segmented_date_snapshot_uses_displayed_complete_values') {
    const dateField = append(target.content, 'div', { class: 'st-key-val_end_d' });
    const segments = [['day', '9'], ['month', '10'], ['year', '2026']].map(([type, value]) =>
        append(dateField, 'span', {
            'data-type': type, 'aria-valuenow': value, contenteditable: 'true', tabindex: '0',
        })
    );
    remount({ values: [{ key: 'val_end_d', kind: 'date', value: '2026-10-08' }] }); flush();
    assert.equal(key(segments[0]).defaultPrevented, false);
    assert.equal(key(segments[1]).defaultPrevented, false);
    const intent = prepare(segments[2]);
    assert.deepEqual(intent.expected, { key: 'val_end_d', kind: 'date', value: '2026-10-09' });
} else if (payload.scenario === 'radio_group_uses_native_single_tab_stop_and_selected_value') {
    const wrapper = append(target.content, 'div', { class: 'st-key-val_solar', role: 'radiogroup' });
    const radios = ['all', 'day', 'night'].map(() => append(wrapper, 'input', { type: 'radio' }));
    radios[1].checked = true;
    remount({ values: [{ key: 'val_solar', kind: 'radio', value: 'all', options: ['all', 'day', 'night'] }] });
    flush();
    assert.equal(key(radios[0], 'ArrowRight').defaultPrevented, false);
    assert.equal(key(radios[1], 'Tab', { shiftKey: true }).defaultPrevented, false);
    assert.equal(key(last).defaultPrevented, false);
    const intent = prepare(radios[1]);
    assert.deepEqual(intent.expected, { key: 'val_solar', kind: 'radio', value: 'day' });
} else if (payload.scenario === 'remount_and_cleanup_keep_one_listener_owner') {
    const intent = prepare();
    const oldCleanup = cleanup;
    remount({ ack: { ...intent, ready: true, fingerprint: 'current' } });
    oldCleanup();
    assert.equal(window.__wspradarGuidedKeyboardPending.token, intent.token);
    assert.equal(document.listeners.get('keydown').size, 1);
    assert.equal(document.listeners.get('pointerdown').size, 1);
    assert.equal(document.listeners.get('input').size, 1);
    assert.equal(frames.size, 1);
    flush();
    assert.equal(named('advance').length, 1);
    cleanup();
    assert.equal([...document.listeners.values()].reduce((total, values) => total + values.size, 0), 0);
    assert.equal(frames.size, 0);
    const previousCount = triggers.length;
    key(last);
    assert.equal(triggers.length, previousCount);
} else if (payload.scenario === 'final_unmount_retires_unsent_pending_intent'
    || payload.scenario === 'final_unmount_retires_sent_pending_intent') {
    const intent = prepare();
    const ack = { ...intent, ready: true, fingerprint: 'before-unmount' };
    if (payload.scenario === 'final_unmount_retires_sent_pending_intent') {
        remount({ ack }); flush();
        assert.equal(named('advance').length, 1);
        assert.equal(window.__wspradarGuidedKeyboardPending.sent, true);
    }
    const advancesBeforeUnmount = named('advance').length;
    assert.equal(window.__wspradarGuidedKeyboardPending.token, intent.token);
    cleanup();
    assert.equal(window.__wspradarGuidedKeyboardPending, undefined);
    assert.equal(window.__wspradarGuidedKeyboardCleanup, undefined);
    assert.equal(frames.size, 0);
    assert.equal([...document.listeners.values()].reduce((total, values) => total + values.size, 0), 0);
    // A new controller instance cannot revive the old intent from a late ack.
    remount({ ack }); flush();
    assert.equal(named('advance').length, advancesBeforeUnmount);
    assert.equal(window.__wspradarGuidedKeyboardPending, undefined);
} else {
    throw Error('Unknown scenario ' + payload.scenario);
}
cleanup();
assert.ok(named('prepare').every(event => event.kind === 'state'));
assert.ok(named('cancel').every(event => event.kind === 'state'));
assert.ok(named('advance').every(event => event.kind === 'trigger'));
assert.equal(window.__wspradarGuidedKeyboardPending, undefined);
assert.equal(frames.size, 0);
assert.equal([...document.listeners.values()].reduce((total, values) => total + values.size, 0), 0);
process.stdout.write('ok');
"""


@pytest.mark.parametrize("scenario", [
    "inside_panel_native_keys_and_popups_are_untouched",
    "boundary_waits_for_matching_commit_ack_then_advances_once",
    "unsent_tab_retry_replaces_intent_and_rejects_old_ack",
    "focused_stale_panel_keeps_native_edit_boundary_active",
    "focused_stale_panel_still_rejects_incomplete_native_date",
    "stale_panel_and_continue_predecessors_cannot_capture_transition",
    "native_blur_input_does_not_cancel_durable_prepare",
    "native_blur_without_continue_preserves_durable_prepare",
    "stale_acknowledgements_cannot_advance_current_attempt",
    "user_edits_pointer_and_keys_cancel_pending_transition",
    "incomplete_native_date_retains_panel_and_focuses_invalid_segment",
    "invalid_native_field_is_not_replaced_by_old_server_value",
    "invalid_nonfocusable_group_focuses_first_available_descendant",
    "help_and_unavailable_controls_do_not_move_panel_boundary",
    "terminal_review_never_prepares_or_submits",
    "continue_boundary_uses_validation_without_inventing_field_snapshot",
    "segmented_date_snapshot_uses_displayed_complete_values",
    "radio_group_uses_native_single_tab_stop_and_selected_value",
    "remount_and_cleanup_keep_one_listener_owner",
    "final_unmount_retires_unsent_pending_intent",
    "final_unmount_retires_sent_pending_intent",
])
def test_guided_keyboard_browser_behavior(scenario):
    """Execute production JavaScript against explicit focus, commit, and rerender events."""
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is required for the Guided keyboard browser harness")
    result = subprocess.run(
        [node, "-e", _BROWSER_HARNESS],
        input=json.dumps({
            "javascript": keyboard._GUIDED_KEYBOARD_CONTROLLER_JS,
            "scenario": scenario,
        }),
        text=True, encoding="utf-8", capture_output=True, timeout=15, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == "ok"
