const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '..', 'site', 'print.js'), 'utf8');

function fixture({mainPresent = true} = {}) {
  const nodes = [];
  class Element {
    constructor(tag, attributes = {}, insideMain = true) {
      this.tag = tag;
      this.attributes = {...attributes};
      this.insideMain = insideMain;
      nodes.push(this);
    }
    getAttribute(name) {
      return Object.hasOwn(this.attributes, name) ? this.attributes[name] : null;
    }
    setAttribute(name, value) {
      this.attributes[name] = String(value);
      if ((name === 'open' || name === 'name') && this.open && this.getAttribute('name')) {
        for (const other of nodes) {
          if (other !== this && other.tag === 'details' && other.getAttribute('name') === this.getAttribute('name')) {
            other.removeAttribute('open');
          }
        }
      }
    }
    removeAttribute(name) {
      delete this.attributes[name];
    }
    get open() { return this.getAttribute('open') !== null; }
    set open(value) {
      if (value) this.setAttribute('open', '');
      else this.removeAttribute('open');
    }
  }
  const closed = new Element('details');
  const opened = new Element('details', {open: ''});
  const namedClosed = new Element('details', {name: 'evidence'});
  const namedOpened = new Element('details', {name: 'evidence', open: ''});
  const emptyName = new Element('details', {name: ''});
  const navigation = new Element('details', {name: 'language'}, false);
  const lazy = new Element('img', {loading: 'lazy'});
  const eager = new Element('img', {loading: 'eager'});
  const ordinary = new Element('img');
  const externalImage = new Element('img', {loading: 'lazy'}, false);
  const callbacks = new Map();
  const main = {
    querySelectorAll(selector) {
      if (selector === 'details') return nodes.filter(n => n.insideMain && n.tag === 'details');
      if (selector === 'img[loading="lazy"]') return nodes.filter(n => n.insideMain && n.tag === 'img' && n.getAttribute('loading') === 'lazy');
      throw new Error(`Unexpected selector ${selector}`);
    },
  };
  vm.runInNewContext(source, {
    document: {getElementById(id) { assert.equal(id, 'main'); return mainPresent ? main : null; }},
    window: {addEventListener(name, callback) { callbacks.set(name, callback); }},
  });
  return {nodes, closed, opened, namedClosed, namedOpened, emptyName, navigation, lazy, eager, ordinary, externalImage,
    before() { callbacks.get('beforeprint')(); },
    after() { callbacks.get('afterprint')(); },
    state() { return nodes.map(n => ({...n.attributes})); },
  };
}

const page = fixture();
const original = page.state();
page.after();
assert.deepEqual(page.state(), original, 'afterprint without preparation leaves the page unchanged');
page.before();
for (const details of [page.closed, page.opened, page.namedClosed, page.namedOpened, page.emptyName]) {
  assert.equal(details.open, true, 'all article disclosures open, including all exclusive group members');
  assert.equal(details.getAttribute('name'), null, 'exclusive grouping is suspended');
}
assert.equal(page.navigation.open, false, 'navigation disclosure remains closed');
assert.equal(page.navigation.getAttribute('name'), 'language');
assert.equal(page.lazy.getAttribute('loading'), 'eager');
assert.equal(page.eager.getAttribute('loading'), 'eager');
assert.equal(page.ordinary.getAttribute('loading'), null);
assert.equal(page.externalImage.getAttribute('loading'), 'lazy');
page.before();
page.after();
assert.deepEqual(page.state(), original, 'reentrant beforeprint retains the initial open/name/loading state');
page.after();
assert.deepEqual(page.state(), original, 'reentrant afterprint is harmless');

page.closed.open = true;
page.opened.open = false;
page.namedClosed.open = true;
const secondState = page.state();
page.before();
page.after();
assert.deepEqual(page.state(), secondState, 'a subsequent print restores the current page state');

const absent = fixture({mainPresent: false});
const absentState = absent.state();
absent.before();
absent.after();
assert.deepEqual(absent.state(), absentState, 'a missing main element is harmless');

console.log('Print lifecycle checks passed: disclosures, exclusive groups, image loading, reentrant events, and restoration.');
