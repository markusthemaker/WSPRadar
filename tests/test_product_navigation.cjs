const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.join(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'source', 'theme', 'scripts', 'product-navigation.js'), 'utf8');
const entry = fs.readFileSync(path.join(root, 'source', 'theme', 'scripts', 'entry.js'), 'utf8');
const catalog = JSON.parse(fs.readFileSync(path.join(root, 'source', 'imported', 'app', 'brand.json'), 'utf8')).product_navigation.catalog;
const settings = '?v=1&run=1&callsign=G3ZIL&ref=G4HZX&value=a%2Bb&value=2#wspradar-results-inspection';
const canonicalDemo = 'https://wspradar.org/' + settings;

assert.equal(catalog.origins.analysis, 'https://app.wspradar.org/');
assert.equal(catalog.origins.website, 'https://www.wspradar.org/');
assert(catalog.items.every(item => item.new_tab === false));
for (const alias of ['https://markusthemaker-wspradar.hf.space/',
                     'https://markusthemaker-wspradar-test.hf.space/',
                     'https://wspradar.streamlit.app/']) {
  assert(catalog.analysis_aliases.includes(alias));
}

function fixture(url, {port = null, links = [], runEntry = false, missingCatalog = false} = {}) {
  const location = new URL(url);
  let replacement = null;
  location.replace = value => { replacement = value; };
  const anchors = links.map(link => {
    const value = typeof link === 'string' ? {href: link} : link;
    return {href: new URL(value.href, location).href,
      hasAttribute(name) { return name === 'download' && Boolean(value.download); }};
  });
  const events = new Map();
  const document = {
    getElementById(id) {
      assert.equal(id, 'wspradar-product-navigation');
      return missingCatalog ? null : {textContent: JSON.stringify({catalog, local_analysis_port: port})};
    },
    addEventListener(event, callback) { events.set(event, callback); },
    querySelectorAll(selector) { assert.equal(selector, 'a[href]'); return anchors; },
  };
  const window = {location,
    open() { assert.fail('Navigation must not open or focus another window'); },
    addEventListener() { assert.fail('Navigation must not install cross-window message handlers'); },
  };
  Object.defineProperty(window, 'sessionStorage', {
    get() { assert.fail('Website navigation must not read application session state'); },
  });
  const context = vm.createContext({document, window, URL});
  vm.runInContext(source, context);
  if (runEntry) vm.runInContext(entry, context);
  events.get('DOMContentLoaded')?.();
  // No click interception: ordinary clicks, modifier/middle clicks, downloads
  // and browser Back retain native anchor behavior.
  assert.equal(events.has('click'), false);
  assert.equal(window.name, undefined);
  return {anchors, replacement, navigation: window.WSPRadarNavigation};
}

for (const hostname of ['localhost', '127.0.0.1', '[::1]']) {
  for (const port of [null, 8521]) {
    const expected = `http://${hostname}:${port ?? 8501}/`;
    const launchLinks = [catalog.origins.analysis, canonicalDemo,
      catalog.origins.website + settings, '/' + settings,
      ...catalog.analysis_aliases.map(alias => alias + settings)];
    const unchanged = ['/de/documentation/', 'https://www.wspradar.org/en/demos/',
      'https://wspradar.org/static/reference/report.pdf',
      'https://wspradar.org.example.test/?v=1', 'https://example.org/reference',
      'mailto:test@example.org', '#section',
      'https://user@wspradar.org/?v=1', 'https://user@app.wspradar.org/?v=1'];
    const pageUrl = `http://${hostname}:8787/de/demos/`;
    const result = fixture(pageUrl, {port, links: [...launchLinks, ...unchanged]});
    assert.equal(result.navigation.analysisOrigin, expected);
    assert.equal(result.anchors[0].href, expected);
    for (let index = 1; index < launchLinks.length; index++) {
      assert.equal(result.anchors[index].href, expected + settings);
    }
    for (let index = 0; index < unchanged.length; index++) {
      assert.equal(result.anchors[index + launchLinks.length].href, new URL(unchanged[index], pageUrl).href);
    }
    assert.equal(fixture(`http://${hostname}:8787/` + settings, {port, runEntry: true}).replacement,
      expected + settings);
    assert.equal(fixture(`http://${hostname}:8787/`, {port, runEntry: true}).replacement, null);
    assert.equal(fixture(`http://${hostname}:8787/en/?not-app=1`, {port, runEntry: true}).replacement, null);
  }
}

for (const website of ['https://wspradar.org/', catalog.origins.website]) {
  const result = fixture(website + 'en/', {port: 8521,
    links: [catalog.origins.analysis, canonicalDemo, catalog.origins.website + settings, '/' + settings],
    runEntry: true});
  assert.equal(result.navigation.analysisOrigin, catalog.origins.analysis);
  assert.equal(result.anchors[0].href, catalog.origins.analysis);
  for (const anchor of result.anchors.slice(1)) {
    assert.equal(anchor.href, catalog.origins.analysis + settings);
  }
  assert.equal(result.replacement, null);
  assert.equal(fixture(website + settings, {runEntry: true}).replacement, catalog.origins.analysis + settings);
  assert.equal(fixture(website + '#wspradar-results-inspection', {runEntry: true}).replacement,
    catalog.origins.analysis + '#wspradar-results-inspection');
}

// Direct compatibility deployments retain their explicitly selected host;
// generic product links use the canonical application host.
for (const alias of catalog.analysis_aliases) {
  const result = fixture(catalog.origins.website + 'en/', {links: [alias + settings]});
  assert.equal(result.anchors[0].href, alias + settings);
}
for (const href of [catalog.origins.analysis, canonicalDemo, catalog.origins.website + settings]) {
  const result = fixture('http://localhost:8787/en/', {links: [{href, download: true}]});
  assert.equal(result.anchors[0].href, href);
}
const nativeLinks = ['https://example.org/paper', '/en/documentation/full/?view=1#sec-7',
  '/assets/manual.pdf', catalog.origins.analysis + 'paper.pdf',
  'https://app.wspradar.org.example.org/', 'https://user@app.wspradar.org/',
  'https://user@wspradar.org/?v=1', 'javascript:alert(1)'];
const nativePage = catalog.origins.website + 'en/';
const native = fixture(nativePage, {links: nativeLinks});
nativeLinks.forEach((href, index) => assert.equal(native.anchors[index].href, new URL(href, nativePage).href));
assert.equal(fixture(nativePage, {missingCatalog: true}).navigation, undefined);
console.log('Single-tab product navigation: canonical and legacy launches, local ports, exact query/fragment preservation and native anchor behavior passed.');
