const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '..', 'source', 'theme', 'scripts', 'demos-index.js'), 'utf8');

function fixture(url = 'https://wspradar.org/en/demos/', {present = true, readyState = 'complete', txPerformance = false} = {}) {
  class Element {
    constructor({dataset = {}, text = '', hidden = false} = {}) {
      this.dataset = dataset;
      this.textContent = text;
      this.hidden = hidden;
      this.value = '';
      this.attributes = {};
      this.events = new Map();
    }
    setAttribute(name, value) { this.attributes[name] = String(value); }
    addEventListener(name, callback) {
      const callbacks = this.events.get(name) || [];
      callbacks.push(callback);
      this.events.set(name, callbacks);
    }
    emit(name) { for (const callback of this.events.get(name) || []) callback(); }
    focus() { assert.fail('Filtering must retain keyboard focus'); }
    scrollIntoView() { assert.fail('Filtering must not change scroll position'); }
  }

  const cards = [
    ['rx-benchmark', 'Low Dipole vs Radial-Free Vertical G3ZIL G4HZX 40 m Griffiths Squibb'],
    ['tx-benchmark', 'Short Portable Vertical vs Larger Vertical SK0WE/P SK0WE/1 20 m Zander'],
    ['rx-performance', 'A Month on 40 m with a Low Dipole G3ZIL Griffiths'],
    ['rx-benchmark', 'One Antenna, Two Receivers — Why Calibration Matters ON4AWM0 ON4AWM1 160 m Vanhamel'],
    ['rx-benchmark', 'A 90° Antenna Rotation, a 3 dB Difference ON4AWM0 ON4AWM1 160 m Vanhamel'],
    ['rx-benchmark tx-benchmark', 'Horizontal Loop vs GAP Titan KP4MD WB6RQN 40 m Milazzo'],
  ].map(([modes, text]) => new Element({dataset: {modes}, text}));
  const controls = [
    ['rx-benchmark', 'RX Benchmark', 'Compare receiving setups.'],
    ['tx-benchmark', 'TX Benchmark', 'Compare transmitting setups.'],
    ['rx-performance', 'RX Performance', 'Explore one receiver.'],
  ].map(([filter, label, description]) => new Element({dataset: {filter, label, description}}));
  if (txPerformance) {
    cards.push(new Element({dataset: {modes: 'tx-performance'}, text: 'One transmitter worldwide'}));
    controls.push(new Element({dataset: {filter: 'tx-performance', label: 'TX Performance', description: 'Explore one transmitter.'}}));
  }
  const reset = new Element();
  const title = new Element({text: 'Find your first insight.'});
  const count = new Element({text: '6 guided demos'});
  const description = new Element({dataset: {defaultDescription: 'Choose your question.'}, text: 'Choose your question.'});
  const note = new Element();
  const controlContainers = [new Element({hidden: true}), new Element({hidden: true})];
  const landing = new Element();
  landing.querySelectorAll = selector => {
    if (selector === '.demo-card[data-modes]') return cards;
    if (selector === '[data-filter]') return controls;
    if (selector === '[data-demo-controls]') return controlContainers;
    assert.fail(`Unexpected landing selector: ${selector}`);
  };
  const selectors = {
    '#reset-filter': reset,
    '#collection-title': title,
    '#demo-count': count,
    '#collection-description': description,
    '#collection-note': note,
  };
  landing.querySelector = selector => {
    assert.ok(Object.hasOwn(selectors, selector), `Unexpected landing selector: ${selector}`);
    return selectors[selector];
  };
  const document = new Element();
  document.readyState = readyState;
  document.querySelector = selector => {
    assert.equal(selector, '.demos-landing', 'all card/control lookups remain page-scoped');
    return present ? landing : null;
  };
  const window = new Element();
  window.location = {href: url};
  const replacements = [];
  const preservedState = {existing: 'navigation state'};
  window.history = {
    state: preservedState,
    replaceState(state, unused, target) {
      assert.equal(state, preservedState, 'existing history state is preserved');
      replacements.push(String(target));
      window.location.href = String(target);
    },
  };
  const context = vm.createContext({document, window, URL});
  const run = () => vm.runInContext(source, context);
  run();
  return {
    cards, controls, reset, title, count, description, note, controlContainers,
    window, document, replacements, run,
    visible: () => cards.filter(card => !card.hidden),
    choose(mode) { controls.find(control => control.dataset.filter === mode).emit('click'); },
    popstate(nextURL) { window.location.href = nextURL; window.emit('popstate'); },
  };
}

const page = fixture();
assert.equal(page.visible().length, 6);
assert.equal(page.count.textContent, '6 guided demos');
assert.equal(page.description.textContent, 'Choose your question.');
assert.equal(page.count.attributes.role, 'status');
assert.equal(page.count.attributes['aria-live'], 'polite');
assert.equal(page.count.attributes['aria-atomic'], 'true');
assert.ok(page.controlContainers.every(control => !control.hidden));
assert.equal(page.replacements.length, 0, 'a clean initial URL is unchanged');
for (const [mode, expected] of [['rx-benchmark', 4], ['tx-benchmark', 2], ['rx-performance', 1]]) {
  page.choose(mode);
  assert.equal(page.visible().length, expected);
  assert.equal(page.count.textContent, `${expected} of 6 demos`);
  assert.equal(new URL(page.window.location.href).searchParams.get('use'), mode);
  assert.equal(page.controls.filter(control => control.attributes['aria-pressed'] === 'true').length, 1);
  assert.equal(page.reset.attributes['aria-pressed'], 'false');
  assert.equal(page.note.hidden, mode === 'rx-performance');
  assert.equal(page.description.textContent, page.controls.find(control => control.dataset.filter === mode).dataset.description);
  if (mode.endsWith('benchmark')) assert.ok(!page.cards[5].hidden, 'Milazzo belongs to both Benchmark collections');
}
page.reset.emit('click');
assert.equal(page.visible().length, 6);
assert.equal(page.reset.attributes['aria-pressed'], 'true');
assert.equal(new URL(page.window.location.href).searchParams.has('use'), false);

const linked = fixture('http://127.0.0.1:8787/en/demos/?lang=en&use=tx-benchmark&source=guide#demos');
assert.equal(linked.visible().length, 2);
assert.equal(linked.title.textContent, 'TX Benchmark demos');
linked.reset.emit('click');
assert.equal(linked.window.location.href, 'http://127.0.0.1:8787/en/demos/?lang=en&source=guide#demos');
linked.popstate('http://127.0.0.1:8787/en/demos/?use=rx-benchmark#demos');
assert.equal(linked.visible().length, 4);
linked.popstate('http://127.0.0.1:8787/en/demos/?use=rx-performance#demos');
assert.equal(linked.visible().length, 1);
linked.popstate('http://127.0.0.1:8787/en/demos/#demos');
assert.equal(linked.visible().length, 6);
linked.popstate('http://127.0.0.1:8787/en/demos/?source=guide&use=tx-performance#demos');
assert.equal(linked.visible().length, 6, 'history navigation to an unavailable mode restores all demos');
assert.equal(linked.window.location.href, 'http://127.0.0.1:8787/en/demos/?source=guide#demos');

for (const invalid of ['tx-performance', 'missing', 'toString', '__proto__']) {
  const invalidPage = fixture(`https://wspradar.org/en/demos/?source=guide&use=${invalid}#demos`);
  assert.equal(invalidPage.visible().length, 6, `unknown filter ${invalid} falls back to all demos`);
  assert.equal(invalidPage.window.location.href, 'https://wspradar.org/en/demos/?source=guide#demos');
}

page.run();
assert.equal(page.reset.events.get('click').length, 1, 'repeated script evaluation does not duplicate handlers');
assert.equal(page.window.events.get('popstate').length, 1);
const deferred = fixture(undefined, {readyState: 'loading'});
assert.ok(deferred.controlContainers.every(control => control.hidden), 'controls remain hidden until initialization');
assert.equal(deferred.visible().length, 6, 'all cards remain visible before progressive enhancement');
deferred.document.emit('DOMContentLoaded');
assert.ok(deferred.controlContainers.every(control => !control.hidden));
const otherPage = fixture(undefined, {present: false});
assert.equal(otherPage.window.events.size, 0, 'other site pages receive no filtering behavior');
const futureMode = fixture('https://wspradar.org/en/demos/?use=tx-performance', {txPerformance: true});
assert.equal(futureMode.visible().length, 1, 'new configured mode membership works without script changes');
assert.equal(futureMode.title.textContent, 'TX Performance demos');
assert.equal(futureMode.count.textContent, '1 of 7 demos');

console.log('Guided demo landing: mode counts, shared Milazzo membership, URL state, history navigation and progressive enhancement without search passed.');
