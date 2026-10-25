const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.join(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'source', 'theme', 'scripts', 'product-navigation.js'), 'utf8');
const entry = fs.readFileSync(path.join(root, 'source', 'theme', 'scripts', 'entry.js'), 'utf8');
const catalog = JSON.parse(fs.readFileSync(path.join(root, 'source', 'imported', 'app', 'brand.json'), 'utf8')).product_navigation.catalog;
const canonicalDemo = 'https://wspradar.org/?v=1&run=1&callsign=G3ZIL&ref=G4HZX#wspradar-results-inspection';
assert.equal(catalog.items.find(item => item.destination === 'analysis' && item.path === '').new_tab, false);
assert.equal(catalog.items.find(item => item.id === 'documentation').new_tab, true);

function fixture(url, {port = null, links = [], runEntry = false} = {}) {
  const location = new URL(url);
  let replacement = null;
  location.replace = value => { replacement = value; };
  const anchors = links.map(href => ({href: new URL(href, location).href}));
  const events = new Map();
  const document = {
    getElementById(id) {
      assert.equal(id, 'wspradar-product-navigation');
      return {textContent: JSON.stringify({catalog, local_analysis_port: port})};
    },
    addEventListener(event, callback) { events.set(event, callback); },
    querySelectorAll(selector) { assert.equal(selector, 'a[href]'); return anchors; },
  };
  const window = {location};
  const context = vm.createContext({document, window, URL});
  vm.runInContext(source, context);
  if (runEntry) vm.runInContext(entry, context);
  events.get('DOMContentLoaded')();
  return {anchors, replacement, navigation: window.WSPRadarNavigation};
}

let assertions = 2;
for (const hostname of ['localhost', '127.0.0.1', '[::1]']) {
  for (const port of [null, 8521]) {
    const expected = `http://${hostname}:${port ?? 8501}/`;
    const unchanged = [
      '/de/documentation/', 'https://wspradar.org/en/demos/',
      'https://wspradar.org/static/reference/report.pdf',
      'https://wspradar.org.example.test/?v=1',
      'https://example.org/reference', 'mailto:test@example.org', '#section',
    ];
    const result = fixture(`http://${hostname}:8787/de/demos/`, {
      port, links: [catalog.origins.analysis, canonicalDemo, ...unchanged],
    });
    assert.equal(result.navigation.analysisOrigin, expected);
    assert.equal(result.anchors[0].href, expected);
    assert.equal(result.anchors[1].href, expected + '?v=1&run=1&callsign=G3ZIL&ref=G4HZX#wspradar-results-inspection');
    for (let index = 0; index < unchanged.length; index++) {
      assert.equal(result.anchors[index + 2].href, new URL(unchanged[index], `http://${hostname}:8787/de/demos/`).href);
    }
    const forwarded = fixture(`http://${hostname}:8787/?v=1&run=1#wspradar-results-inspection`, {port, runEntry: true});
    assert.equal(forwarded.replacement, expected + '?v=1&run=1#wspradar-results-inspection');
    assert.equal(fixture(`http://${hostname}:8787/`, {port, runEntry: true}).replacement, null);
    assert.equal(fixture(`http://${hostname}:8787/en/?not-app=1`, {port, runEntry: true}).replacement, null);
    assertions += 13;
  }
}

const production = fixture('https://wspradar.org/en/', {
  port: 8521, links: [catalog.origins.analysis, canonicalDemo], runEntry: true,
});
assert.equal(production.navigation.analysisOrigin, catalog.origins.analysis);
assert.equal(production.anchors[0].href, catalog.origins.analysis);
assert.equal(production.anchors[1].href, canonicalDemo);
assert.equal(production.replacement, null);
assert.equal(fixture('https://wspradar.org/?v=1&run=1#wspradar-results-inspection', {runEntry: true}).replacement,
             catalog.origins.analysis + '?v=1&run=1#wspradar-results-inspection');
assertions += 5;
console.log(`Product navigation: ${assertions} local/production routing assertions passed.`);
