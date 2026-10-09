"""Browser boundary navigation over Guided's existing validation callbacks."""

import streamlit as st


GUIDED_KEYBOARD_CONTROLLER_KEY = "guided_keyboard_controller"

_GUIDED_KEYBOARD_CONTROLLER_JS = r"""
export default function(component) {
    const owner = '__wspradarGuidedKeyboardCleanup';
    const pendingKey = '__wspradarGuidedKeyboardPending';
    window[owner]?.(true);
    const data = component.data ?? {};
    const nodes = new Set(data.nodes ?? []);
    const descriptors = data.values ?? [];
    const selector = 'input,textarea,select,button,[tabindex],a[href]';
    let disposed = false;
    let frame = null;

    function rendered(element, allowStale = false) {
        if (!element?.isConnected || element.disabled
            || element.getAttribute('aria-disabled') === 'true'
            || element.closest('[hidden],[inert],[aria-hidden="true"]')
            || (!allowStale && element.closest('[data-stale="true"]'))) return false;
        let current = element;
        while (current) {
            if (current.tagName === 'DETAILS' && !current.open) return false;
            const style = window.getComputedStyle(current);
            if (style.display === 'none' || style.visibility === 'hidden') return false;
            current = current.parentElement;
        }
        return element.getClientRects().length > 0;
    }

    function visible(element, allowStale = false) {
        return rendered(element, allowStale) && element.tabIndex >= 0;
    }

    function help(element) {
        return Boolean(element.closest('[data-testid="stTooltipIcon"],'
            + '.st-key-guided_reference_design_reference_station_help,'
            + '.st-key-guided_reference_design_local_neighborhood_help'));
    }

    function controls(panel, allowStale = false) {
        return Array.from(panel.querySelectorAll(selector)).filter(element => {
            if (!visible(element, allowStale) || help(element)) return false;
            if (element.matches('input[type="radio"]')) {
                const group = element.closest('[role="radiogroup"]');
                const radios = Array.from(group?.querySelectorAll('input[type="radio"]') ?? []);
                return element === (radios.find(radio => radio.checked) ?? radios[0]);
            }
            return true;
        });
    }

    function panelFor(element) {
        const panel = element?.closest('[data-testid="stExpander"]');
        const node = panel?.querySelector('[data-wspradar-guided-node]')
            ?.getAttribute('data-wspradar-guided-node');
        if (nodes.has(node) && node !== data.terminal) return {node, panel};
        for (const node of nodes) {
            if (node !== data.terminal && element?.closest('.st-key-guided_continue_' + node)) {
                const marker = Array.from(document.querySelectorAll(
                    '[data-wspradar-guided-node="' + node + '"]'
                )).find(item => !item.closest('[data-stale="true"]'));
                return {node, panel: marker?.closest('[data-testid="stExpander"]')};
            }
        }
        return null;
    }

    function descriptorFor(element) {
        return descriptors.find(item => element?.closest('.st-key-' + item.key));
    }

    function snapshot(element) {
        const descriptor = descriptorFor(element);
        if (!descriptor) return null;
        const wrapper = element.closest('.st-key-' + descriptor.key);
        let value = descriptor.value;
        if (descriptor.kind === 'date' || descriptor.kind === 'time') {
            const segment = type => wrapper.querySelector('[data-type="' + type + '"]')
                ?.getAttribute('aria-valuenow');
            const pad = value => String(value).padStart(2, '0');
            value = descriptor.kind === 'date'
                ? segment('year') + '-' + pad(segment('month')) + '-' + pad(segment('day'))
                : pad(segment('hour')) + ':' + pad(segment('minute'));
        } else if (descriptor.kind === 'radio') {
            const radios = Array.from(wrapper.querySelectorAll('input[type="radio"]'));
            value = descriptor.options?.[radios.findIndex(radio => radio.checked)] ?? '';
        } else if (descriptor.kind === 'bool') {
            const control = wrapper.querySelector('input[type="checkbox"]');
            value = String(Boolean(control?.checked));
        } else if (element.matches('input,textarea,select')) {
            value = element.value;
        } else if (element.getAttribute('role') === 'slider') {
            value = element.getAttribute('aria-valuenow');
        }
        return {key: descriptor.key, kind: descriptor.kind, value: String(value)};
    }

    function invalidNativeField(panel, allowStale = false) {
        // An incomplete date segment never reaches Python; validating the old
        // committed date would incorrectly allow the panel to advance.
        const invalid = Array.from(panel?.querySelectorAll(
            '[data-placeholder="true"][contenteditable="true"],'
            + '[aria-invalid="true"],input:invalid'
        ) ?? []).find(element => rendered(element, allowStale));
        if (!invalid || visible(invalid, allowStale)) return invalid;
        return Array.from(invalid.querySelectorAll(selector))
            .find(element => visible(element, allowStale)) ?? invalid;
    }

    function cancel() {
        const pending = window[pendingKey];
        if (!pending) return;
        delete window[pendingKey];
        component.setStateValue('cancel', pending.token);
    }

    function handleKey(event) {
        if (event.key !== 'Tab' || event.shiftKey || event.ctrlKey || event.altKey || event.metaKey) {
            if (window[pendingKey] && !['Shift', 'Control', 'Alt', 'Meta'].includes(event.key)) cancel();
            return;
        }
        const target = event.target;
        if (!target?.closest('.st-key-application_configuration')) return;
        // Calendar and select popups retain their own native keyboard handling.
        if (target.closest('[role="dialog"],[role="listbox"],[data-baseweb="popover"]')
            || target.getAttribute('aria-expanded') === 'true') return;
        const location = panelFor(target);
        if (!location?.panel) return;
        // Native arrows can start a rerun before the following Tab. The focused
        // panel is still the user's live editor while Streamlit marks it stale.
        const allowStale = Boolean(target.closest('[data-stale="true"]'));
        const items = controls(location.panel, allowStale);
        const onContinue = Boolean(target.closest('.st-key-guided_continue_' + location.node));
        if (!onContinue && target !== items.at(-1)) return;
        event.preventDefault();
        event.stopPropagation();
        if (window[pendingKey]?.sent) return;
        if (window[pendingKey]) cancel();
        const invalid = invalidNativeField(location.panel, allowStale);
        if (invalid) { invalid.focus(); return; }
        const expected = onContinue ? null : snapshot(target);
        const token = String(Date.now()) + '-' + String(Math.random()).slice(2);
        // Blurring commits Streamlit's native widget. The server acknowledgement
        // below, rather than a timer or the trigger's return value, gates Continue.
        const continueButton = Array.from(document.querySelectorAll(
            '.st-key-guided_continue_' + location.node + ' button'
        )).find(element => visible(element));
        if (continueButton) continueButton.focus();
        else target.blur();
        window[pendingKey] = {token, node: location.node, sent: false};
        // Keep the prepare intent in component state until acknowledged. A
        // one-tick trigger can be cleared while the native blur rerun wins.
        component.setStateValue('prepare', {token, node: location.node, expected});
    }

    function acknowledge() {
        frame = null;
        if (disposed) return;
        const pending = window[pendingKey];
        const ack = data.ack;
        if (!pending || !ack || ack.token !== pending.token || ack.node !== pending.node) return;
        if (ack.ready && !pending.sent) {
            pending.sent = true;
            component.setTriggerValue('advance', {token: pending.token, fingerprint: ack.fingerprint});
        }
    }

    // A completed/invalid Continue consumes its token on the server. Rerenders
    // with no acknowledgement then release the browser's one-shot guard.
    if (window[pendingKey]?.sent && !data.ack) delete window[pendingKey];
    document.addEventListener('keydown', handleKey, true);
    document.addEventListener('pointerdown', cancel, true);
    document.addEventListener('input', cancel, true);
    frame = requestAnimationFrame(acknowledge);
    function cleanup(keepPending = false) {
        disposed = true;
        if (frame !== null) cancelAnimationFrame(frame);
        document.removeEventListener('keydown', handleKey, true);
        document.removeEventListener('pointerdown', cancel, true);
        document.removeEventListener('input', cancel, true);
        if (window[owner] === cleanup) {
            if (!keepPending) delete window[pendingKey];
            delete window[owner];
        }
    }
    window[owner] = cleanup;
    return cleanup;
}
"""

_GUIDED_KEYBOARD_CONTROLLER = st.components.v2.component(
    "wspradar_guided_keyboard",
    html='<span aria-hidden="true"></span>',
    css=":host { display: block; height: 1px; overflow: hidden; }",
    js=_GUIDED_KEYBOARD_CONTROLLER_JS,
)


def render_guided_keyboard_controller(
    *, nodes, terminal, values, ack, on_prepare, on_advance, on_cancel,
):
    """Use transient intents; validation and navigation stay in the renderer."""
    _GUIDED_KEYBOARD_CONTROLLER(
        data={"nodes": nodes, "terminal": terminal, "values": values, "ack": ack},
        key=GUIDED_KEYBOARD_CONTROLLER_KEY,
        on_prepare_change=on_prepare,
        on_advance_change=on_advance,
        on_cancel_change=on_cancel,
        width="stretch",
        height=1,
    )
