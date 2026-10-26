const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '..', 'source', 'theme', 'scripts', 'site.js'), 'utf8');

function fixture({narrow = false, observer = true, header = true} = {}) {
  function eventTarget() {
    const listeners = new Map();
    return {
      listeners,
      addEventListener(type, callback) {
        const callbacks = listeners.get(type) || [];
        callbacks.push(callback);
        listeners.set(type, callbacks);
      },
      emit(type, event = {}) {
        for (const callback of listeners.get(type) || []) callback(event);
      },
    };
  }
  const styles = new Map();
  const classes = new Set();
  const document = Object.assign(eventTarget(), {
    activeElement: null,
    documentElement: {classList: {add: value => classes.add(value)}, style: {setProperty: (key, value) => styles.set(key, value)}},
    querySelector(selector) {
      return {'.nav-toggle': header ? toggle : null, '.site-navigation-shell': header ? shell : null, '.reader-index': null}[selector] || null;
    },
    getElementById(id) { return header && id === 'nav-links' ? links : null; },
    querySelectorAll(selector) { assert.equal(selector, '[data-filter-input]'); return []; },
  });
  const attributes = new Map();
  const focusCalls = [];
  const toggle = Object.assign(eventTarget(), {
    setAttribute: (key, value) => attributes.set(key, value),
    focus(options) { document.activeElement = toggle; focusCalls.push(options); },
  });
  const anchor = {
    href: '#section', closest: selector => selector === 'a' ? anchor : null,
    focus(options) { document.activeElement = anchor; focusCalls.push(options); },
  };
  const anchorChild = {closest: selector => selector === 'a' ? anchor : null};
  const separator = {closest: () => null};
  const outside = {};
  const language = {};
  const links = Object.assign(eventTarget(), {
    hidden: false,
    querySelector(selector) { assert.equal(selector, 'a[href]'); return anchor; },
    contains: node => [links, anchor, anchorChild, separator].includes(node),
  });
  let height = 66.25;
  const shell = Object.assign(eventTarget(), {
    contains: node => [shell, toggle, language].includes(node) || links.contains(node),
    getBoundingClientRect: () => ({height}),
  });
  const media = Object.assign(eventTarget(), {matches: narrow});
  const observers = [];
  const context = {
    document,
    matchMedia(query) { assert.equal(query, '(max-width:800px)'); return media; },
  };
  if (observer) context.ResizeObserver = class {
    constructor(callback) { this.callback = callback; observers.push(this); }
    observe(element) { this.element = element; }
  };
  vm.runInNewContext(source, context);
  return {
    document, toggle, links, shell, media, anchor, anchorChild, separator, outside,
    language, attributes, styles, classes, focusCalls, observers,
    resize(narrow) { media.matches = narrow; media.emit('change'); },
    setHeight(value) { height = value; },
  };
}

function assertMenu(f, open) {
  assert.equal(f.links.hidden, !open);
  assert.equal(f.attributes.get('aria-expanded'), String(open));
}

// The desktop links remain available, including when an Escape key is unrelated.
const desktop = fixture();
assertMenu(desktop, true);
assert.equal(desktop.classes.has('js'), true);
assert.equal(desktop.styles.get('--site-navigation-height'), '67px');
desktop.document.emit('keydown', {key: 'Escape'});
assertMenu(desktop, true);
assert.equal(desktop.focusCalls.length, 0);

// A shrinking viewport must not leave keyboard focus inside newly hidden links.
desktop.document.activeElement = desktop.anchor;
desktop.resize(true);
assertMenu(desktop, false);
assert.equal(desktop.document.activeElement, desktop.toggle);
assert.equal(desktop.focusCalls.at(-1).preventScroll, true);
desktop.resize(false);
assertMenu(desktop, true);
assert.equal(desktop.document.activeElement, desktop.anchor, 'Growing the viewport must move focus out of the now-hidden Menu button.');
assert.equal(desktop.focusCalls.at(-1).preventScroll, true);

// On phones the toggle opens and closes the same links without creating observers.
const mobile = fixture({narrow: true});
assertMenu(mobile, false);
for (let iteration = 0; iteration < 12; iteration++) {
  mobile.toggle.emit('click');
  assertMenu(mobile, true);
  mobile.toggle.emit('click');
  assertMenu(mobile, false);
}
assert.equal(mobile.observers.length, 1);
assert.equal(mobile.observers[0].element, mobile.shell);
assert.equal(mobile.toggle.listeners.get('click').length, 1);
assert.equal(mobile.document.listeners.get('keydown').length, 1);

// Decorative content does not close the menu; a nested element in a link does.
mobile.toggle.emit('click');
mobile.links.emit('click', {target: mobile.separator});
assertMenu(mobile, true);
let prevented = false;
mobile.links.emit('click', {target: mobile.anchorChild, preventDefault() { prevented = true; }});
assertMenu(mobile, false);
assert.equal(mobile.document.activeElement, mobile.toggle);
assert.equal(mobile.anchor.href, '#section');
assert.equal(prevented, false, 'Closing the menu must retain native link navigation.');

mobile.toggle.emit('click');
mobile.document.emit('keydown', {key: 'Enter'});
assertMenu(mobile, true);
mobile.document.emit('keydown', {key: 'Escape'});
assertMenu(mobile, false);
assert.equal(mobile.document.activeElement, mobile.toggle);
const focusCount = mobile.focusCalls.length;
mobile.document.emit('keydown', {key: 'Escape'});
assert.equal(mobile.focusCalls.length, focusCount, 'Escape outside an open menu must not steal focus.');

// Pointer and keyboard movement within the header stays usable; leaving closes it.
mobile.toggle.emit('click');
mobile.document.emit('click', {target: mobile.language});
mobile.shell.emit('focusout', {relatedTarget: mobile.language});
mobile.shell.emit('focusout', {relatedTarget: null});
assertMenu(mobile, true);
mobile.document.emit('click', {target: mobile.outside});
assertMenu(mobile, false);
mobile.toggle.emit('click');
mobile.shell.emit('focusout', {relatedTarget: mobile.outside});
assertMenu(mobile, false);

// Height changes such as font loading keep section/side-panel clearances current.
mobile.setHeight(83.1);
mobile.observers[0].callback();
assert.equal(mobile.styles.get('--site-navigation-height'), '84px');
mobile.resize(false);
assertMenu(mobile, true);
mobile.document.emit('click', {target: mobile.outside});
assertMenu(mobile, true);
mobile.resize(true);
assertMenu(mobile, false);

// Missing optional browser APIs or header markup must not break other site code.
assertMenu(fixture({narrow: true, observer: false}), false);
assert.equal(fixture({header: false}).observers.length, 0);

console.log('Site navigation: desktop, responsive menu, focus, dismissal, lifecycle and height checks passed.');
