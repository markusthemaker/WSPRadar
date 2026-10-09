"""Skip mouse-only help in Tab order while retaining accessible descriptions."""

import re

import streamlit as st


INPUT_KEYBOARD_HELP_KEY = "_input_keyboard_help"
INPUT_KEYBOARD_CONTROLLER_KEY = "input_keyboard_controller"
_KEY_PATTERN = re.compile(r"[A-Za-z0-9_-]{1,160}")


def _descriptor(widget_key, markdown, mouse_help_key=None):
    for key in (widget_key, mouse_help_key):
        if key is not None and (
            not isinstance(key, str) or not _KEY_PATTERN.fullmatch(key)
        ):
            raise ValueError("Keyboard-help keys must be bounded internal widget keys.")
    if widget_key is None:
        raise ValueError("Keyboard help requires an internal widget key.")
    if not isinstance(markdown, str) or not markdown.strip() or len(markdown) > 8192:
        raise ValueError("Keyboard help requires nonempty localized text up to 8192 characters.")
    return {
        "widgetKey": widget_key,
        "markdown": markdown,
        "mouseHelpKey": mouse_help_key,
    }


def begin_input_keyboard():
    """Begin one render's help registry; hidden controls leave no retained entries."""
    st.session_state[INPUT_KEYBOARD_HELP_KEY] = {}


def keyboard_help(widget_key, markdown, *, mouse_help_key=None):
    """Register the exact native help text and return it unchanged to its widget."""
    descriptor = _descriptor(widget_key, markdown, mouse_help_key)
    registry = st.session_state.setdefault(INPUT_KEYBOARD_HELP_KEY, {})
    registry[widget_key] = descriptor
    return markdown


_INPUT_KEYBOARD_CONTROLLER_JS = r"""
export default function(component) {
    const ownerProperty = '__wspradarInputKeyboardCleanup';
    window[ownerProperty]?.();
    const descriptors = (component.data?.descriptors ?? []).filter(item => (
        typeof item?.widgetKey === 'string'
        && /^[A-Za-z0-9_-]{1,160}$/.test(item.widgetKey)
        && typeof item.markdown === 'string'
        && item.markdown.length > 0 && item.markdown.length <= 8192
        && (item.mouseHelpKey == null || (
            typeof item.mouseHelpKey === 'string'
            && /^[A-Za-z0-9_-]{1,160}$/.test(item.mouseHelpKey)
        ))
    ));
    const scopeSelector = '.st-key-application_configuration';
    const helpSelector = '[data-testid="stTooltipIcon"]';
    const controlSelector = 'input:not([type="hidden"]),select,textarea,'
        + '[role="combobox"],[role="slider"],[role="spinbutton"],button';
    const sequence = (window.__wspradarInputKeyboardSequence ?? 0) + 1;
    window.__wspradarInputKeyboardSequence = sequence;
    const host = document.createElement('div');
    host.setAttribute('data-wspradar-input-help', '');
    document.body.appendChild(host);
    let scope = null;
    let disposed = false;
    let frame = null;
    let bindings = new Map();
    const suppressedTabs = new Map();
    const descriptions = new Map();

    // These are the formatting constructs used by configuration help. Every
    // other character remains a text node, including HTML and Markdown links.
    function appendInline(parent, source) {
        let index = 0;
        let plain = '';
        const flush = () => {
            if (plain) parent.appendChild(document.createTextNode(plain));
            plain = '';
        };
        while (index < source.length) {
            const primary = source.startsWith(':primary[', index);
            const marker = source.startsWith('**', index) ? '**'
                : source.charCodeAt(index) === 96 ? String.fromCharCode(96) : null;
            const contentStart = index + (primary ? 9 : marker?.length ?? 0);
            const end = primary ? source.indexOf(']', contentStart)
                : marker ? source.indexOf(marker, contentStart) : -1;
            if (end > contentStart) {
                flush();
                const element = document.createElement(
                    primary ? 'span' : marker === '**' ? 'strong' : 'code'
                );
                const content = source.slice(contentStart, end);
                if (marker === String.fromCharCode(96)) element.textContent = content;
                else appendInline(element, content);
                parent.appendChild(element);
                index = end + (primary ? 1 : marker.length);
            } else {
                plain += source[index++];
            }
        }
        flush();
    }

    function renderMarkdown(parent, markdown) {
        parent.replaceChildren();
        markdown.split(/\n\s*\n/).forEach(paragraph => {
            const element = document.createElement('p');
            appendInline(element, paragraph);
            parent.appendChild(element);
        });
    }

    descriptors.forEach((descriptor, index) => {
        const description = document.createElement('div');
        description.id = 'wspradar-input-description-' + sequence + '-' + index;
        // Referenced hidden content still supplies an accessible description,
        // without adding unrelated paragraphs to the page's reading order.
        description.setAttribute('hidden', '');
        renderMarkdown(description, descriptor.markdown);
        host.appendChild(description);
        descriptions.set(descriptor.widgetKey, description);
    });

    function isVisible(element) {
        if (!element?.isConnected || element.closest(
            '[data-stale="true"],[hidden],[inert],[aria-hidden="true"],fieldset[disabled]'
        )) return false;
        if (element.disabled || element.getAttribute('aria-disabled') === 'true') return false;
        let ancestor = element;
        while (ancestor) {
            if (ancestor.tagName === 'DETAILS' && !ancestor.open) return false;
            const style = window.getComputedStyle(ancestor);
            if (style.display === 'none' || style.visibility === 'hidden'
                || style.visibility === 'collapse') return false;
            ancestor = ancestor.parentElement;
        }
        return element.getClientRects().length > 0;
    }

    function addDescription(control, id) {
        const ids = (control.getAttribute('aria-describedby') ?? '').split(/\s+/).filter(Boolean);
        if (!ids.includes(id)) {
            control.setAttribute('aria-describedby', ids.concat(id).join(' '));
        }
    }

    function removeDescription(control, id) {
        const ids = (control.getAttribute('aria-describedby') ?? '').split(/\s+/).filter(Boolean);
        if (!ids.includes(id)) return;
        const retained = ids.filter(value => value !== id);
        if (retained.length) control.setAttribute('aria-describedby', retained.join(' '));
        else control.removeAttribute('aria-describedby');
    }

    function suppressTab(control, desired) {
        if (!control) return;
        desired.add(control);
        if (!suppressedTabs.has(control)) {
            suppressedTabs.set(control, control.getAttribute('tabindex'));
        }
        if (control.getAttribute('tabindex') !== '-1') control.setAttribute('tabindex', '-1');
    }

    function restoreTab(control, original) {
        if (control.getAttribute('tabindex') !== '-1') return;
        if (original === null) control.removeAttribute('tabindex');
        else control.setAttribute('tabindex', original);
    }

    function refresh() {
        frame = null;
        if (disposed) return;
        scope = Array.from(document.querySelectorAll(scopeSelector)).find(isVisible) ?? null;
        const nextBindings = new Map();
        const desiredTabs = new Set();
        if (scope) for (const descriptor of descriptors) {
            const field = Array.from(scope.querySelectorAll(
                '.st-key-' + CSS.escape(descriptor.widgetKey)
            )).find(isVisible);
            if (!field) continue;
            for (const icon of field.querySelectorAll(helpSelector)) {
                suppressTab(icon, desiredTabs);
                for (const descendant of icon.querySelectorAll('button,[tabindex]')) {
                    suppressTab(descendant, desiredTabs);
                }
            }
            const mouseHelp = descriptor.mouseHelpKey
                ? Array.from(scope.querySelectorAll(
                    '.st-key-' + CSS.escape(descriptor.mouseHelpKey)
                )).find(isVisible)
                : null;
            if (mouseHelp) {
                // Streamlit can mount desktop and responsive trigger variants
                // together. Both belong to this explicitly help-only wrapper.
                for (const trigger of mouseHelp.querySelectorAll('button')) {
                    suppressTab(trigger, desiredTabs);
                }
            }
            for (const control of field.querySelectorAll(controlSelector)) {
                if (!isVisible(control) || control.closest(helpSelector)
                    || mouseHelp?.contains(control)) continue;
                nextBindings.set(control, descriptor);
                addDescription(control, descriptions.get(descriptor.widgetKey).id);
            }
        }
        for (const [control, descriptor] of bindings) {
            if (nextBindings.get(control) !== descriptor) {
                removeDescription(control, descriptions.get(descriptor.widgetKey).id);
            }
        }
        for (const [control, original] of suppressedTabs) {
            if (!desiredTabs.has(control)) {
                restoreTab(control, original);
                suppressedTabs.delete(control);
            }
        }
        bindings = nextBindings;
    }

    function scheduleRefresh() {
        if (!disposed && frame === null) frame = window.requestAnimationFrame(refresh);
    }

    function handleFocus(event) {
        const descriptor = bindings.get(event.target);
        if (descriptor) {
            addDescription(event.target, descriptions.get(descriptor.widgetKey).id);
        }
    }

    const observer = new MutationObserver(records => {
        if (records.some(record => {
            if (host.contains(record.target)) return false;
            if (scope?.contains(record.target)) return true;
            return [...(record.addedNodes ?? []), ...(record.removedNodes ?? [])].some(node => (
                node.nodeType === 1 && (
                    node.matches(scopeSelector) || node.contains(scope)
                    || node.querySelector(scopeSelector)
                )
            ));
        })) scheduleRefresh();
    });
    observer.observe(document.body, {
        childList: true, subtree: true, attributes: true,
        attributeFilter: ['tabindex', 'disabled', 'aria-disabled', 'aria-describedby', 'aria-hidden', 'hidden', 'open', 'data-stale', 'class'],
    });
    document.addEventListener('focusin', handleFocus);
    window.addEventListener('resize', scheduleRefresh);
    refresh();

    function cleanup() {
        if (disposed) return;
        disposed = true;
        observer.disconnect();
        if (frame !== null) window.cancelAnimationFrame(frame);
        document.removeEventListener('focusin', handleFocus);
        window.removeEventListener('resize', scheduleRefresh);
        for (const [control, descriptor] of bindings) {
            removeDescription(control, descriptions.get(descriptor.widgetKey).id);
        }
        for (const [control, original] of suppressedTabs) restoreTab(control, original);
        host.remove();
        if (window[ownerProperty] === cleanup) delete window[ownerProperty];
    }
    window[ownerProperty] = cleanup;
    return cleanup;
}
"""

_INPUT_KEYBOARD_CONTROLLER = st.components.v2.component(
    "wspradar_input_keyboard",
    html='<span aria-hidden="true"></span>',
    css=":host { display: block; height: 1px; overflow: hidden; }",
    js=_INPUT_KEYBOARD_CONTROLLER_JS,
)


def render_input_keyboard_controller():
    """Mount mouse-help tab filtering and hidden descriptions without overlays."""
    registry = st.session_state.get(INPUT_KEYBOARD_HELP_KEY, {})
    descriptors = tuple(
        _descriptor(value["widgetKey"], value["markdown"], value.get("mouseHelpKey"))
        for value in registry.values()
    )
    _INPUT_KEYBOARD_CONTROLLER(
        data={"descriptors": descriptors},
        key=INPUT_KEYBOARD_CONTROLLER_KEY,
        width="stretch",
        height=1,
    )
