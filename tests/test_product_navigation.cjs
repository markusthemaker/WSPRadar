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

function fixture(url, {port = null, links = [], runEntry = false, target = null,
                      opener = null, storage = new Map(), blockedStorage = false} = {}) {
  const location = new URL(url);
  let replacement = null;
  location.replace = value => { replacement = value; };
  const navigations = [];
  location.assign = value => { navigations.push(value); };
  const anchors = links.map(href => ({href: new URL(href, location).href,
    hasAttribute: name => false,
    getAttribute: name => null,
    closest() { return this; },
  }));
  const events = new Map();
  const windowEvents = new Map();
  const opens = [];
  const document = {
    getElementById(id) {
      assert.equal(id, 'wspradar-product-navigation');
      return {textContent: JSON.stringify({catalog, local_analysis_port: port})};
    },
    addEventListener(event, callback) { events.set(event, callback); },
    querySelectorAll(selector) { assert.equal(selector, 'a[href]'); return anchors; },
  };
  const window = {location, opener,
    addEventListener(event, callback) { windowEvents.set(event, callback); },
    open(...args) { opens.push(args); return target; },
    sessionStorage: {
      getItem(key) { if (blockedStorage) throw new Error('Storage disabled'); return storage.get(key) ?? null; },
      setItem(key, value) { if (blockedStorage) throw new Error('Storage disabled'); storage.set(key, value); },
    },
  };
  const context = vm.createContext({document, window, URL});
  vm.runInContext(source, context);
  if (runEntry) vm.runInContext(entry, context);
  events.get('DOMContentLoaded')();
  return {anchors, replacement, navigation: window.WSPRadarNavigation, opens, navigations, window,
    message(origin, source, data) { windowEvents.get('message')?.({origin, source, data}); },
    click(index = 0, overrides = {}) {
      const event = {target: anchors[index], button: 0, defaultPrevented: false,
        preventDefault() { this.defaultPrevented = true; }, ...overrides};
      events.get('click')?.(event);
      return event;
    },
  };
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

function application(href = 'about:blank', crossOrigin = false) {
  const writes = [];
  const messages = [];
  let focusCount = 0;
  const location = {};
  Object.defineProperty(location, 'href', {
    get() { if (crossOrigin) throw new Error('Cross-origin location'); return href; },
    set(value) { writes.push(value); href = value; },
  });
  const tab = {location, focus() { focusCount++; }};
  tab.top = tab;
  const frame = {top: tab, postMessage(...args) { messages.push(args); }};
  return {tab, frame, writes, messages, get focusCount() { return focusCount; }};
}

const protocol = 'wspradar-navigation-v1';
const appOrigin = new URL(catalog.origins.analysis).origin;
const token = '0123456789abcdef0123456789abcdef';
const hello = {protocol, type: 'hello', nonce: token};
const navigate = url => ({protocol, type: 'navigate', nonce: token, url});

// A first ordinary launch opens one named app; subsequent ordinary launches
// focus that same tab without assigning its location or discarding an analysis.
const firstApp = application();
const firstSite = fixture('https://wspradar.org/en/', {target: firstApp.tab, links: [catalog.origins.analysis]});
assert.equal(firstSite.window.name, 'wspradar_website');
assert.equal(firstSite.click().defaultPrevented, true);
assert.deepEqual(firstSite.opens, [['', 'wspradar_analysis']]);
assert.deepEqual(firstApp.writes, [catalog.origins.analysis]);
assert.equal(firstApp.focusCount, 1);
const runningApp = application(catalog.origins.analysis + '?existing=analysis', true);
const runningSite = fixture('https://wspradar.org/de/demos/', {target: runningApp.tab, links: [catalog.origins.analysis, canonicalDemo]});
for (let index = 0; index < 5; index++) runningSite.click();
assert.equal(runningApp.focusCount, 5);
assert.deepEqual(runningApp.writes, []);
runningSite.click(1);
assert.deepEqual(runningApp.writes, [appOrigin + '/?v=1&run=1&callsign=G3ZIL&ref=G4HZX#wspradar-results-inspection']);
assert.equal(runningSite.anchors[1].href, canonicalDemo);

// Local preview launches retain complete explicit settings and fragments.
const localApp = application();
const localSite = fixture('http://127.0.0.1:8895/en/demos/', {port: 8521, target: localApp.tab, links: [canonicalDemo]});
localSite.click();
assert.deepEqual(localApp.writes, ['http://127.0.0.1:8521/?v=1&run=1&callsign=G3ZIL&ref=G4HZX#wspradar-results-inspection']);
const directApp = application(catalog.origins.analysis, true);
const directSite = fixture('https://wspradar.org/en/', {target: directApp.tab, links: [appOrigin + '/?state=a%2Bb&v=1#result']});
directSite.click();
assert.deepEqual(directApp.writes, [appOrigin + '/?state=a%2Bb&v=1#result']);

// Native modified/middle clicks, downloads and unrelated URLs stay untouched.
for (const overrides of [{button: 1}, {ctrlKey: true}, {metaKey: true}, {shiftKey: true}, {altKey: true}, {defaultPrevented: true}]) {
  const native = fixture('https://wspradar.org/en/', {target: firstApp.tab, links: [catalog.origins.analysis]});
  assert.equal(native.click(0, overrides).defaultPrevented, Boolean(overrides.defaultPrevented));
  assert.deepEqual(native.opens, []);
}
for (const href of ['https://example.org/paper', '/en/documentation/', appOrigin + '/paper.pdf',
                    'https://wspradar.streamlit.app.example.org/', 'https://user@wspradar.streamlit.app/']) {
  const native = fixture('https://wspradar.org/en/', {target: firstApp.tab, links: [href]});
  assert.equal(native.click().defaultPrevented, false);
  assert.deepEqual(native.opens, []);
}
const download = fixture('https://wspradar.org/en/', {target: firstApp.tab, links: [catalog.origins.analysis]});
download.anchors[0].hasAttribute = name => name === 'download';
assert.equal(download.click().defaultPrevented, false);
assert.deepEqual(download.opens, []);
assert.equal(fixture('https://wspradar.org/en/', {links: [catalog.origins.analysis]}).click().defaultPrevented, false);

// Normal visits to targeted pages remain in the paired website tab. Default
// and _self anchors keep browser handling, including same-page fragments.
for (const targetName of ['_blank', 'another_website']) {
  const docs = fixture('https://wspradar.org/en/', {links: ['/en/documentation/full/?view=1#sec-7']});
  docs.anchors[0].getAttribute = name => name === 'target' ? targetName : null;
  assert.equal(docs.click().defaultPrevented, true);
  assert.deepEqual(docs.navigations, ['https://wspradar.org/en/documentation/full/?view=1#sec-7']);
  assert.deepEqual(docs.opens, []);
}
for (const targetName of [null, '_self']) {
  const native = fixture('https://wspradar.org/en/', {links: ['#section']});
  native.anchors[0].getAttribute = name => name === 'target' ? targetName : null;
  assert.equal(native.click().defaultPrevented, false);
  assert.deepEqual(native.navigations, []);
}
for (const options of [{href: '/en/documentation/', override: {ctrlKey: true}},
                       {href: '/en/documentation/', override: {button: 1}},
                       {href: '/en/documentation/', download: true},
                       {href: '/assets/manual.pdf'}, {href: 'https://example.org/en/'}]) {
  const native = fixture('https://wspradar.org/en/', {links: [options.href]});
  native.anchors[0].getAttribute = name => name === 'target' ? '_blank' : null;
  native.anchors[0].hasAttribute = name => name === 'download' && Boolean(options.download);
  assert.equal(native.click(0, options.override).defaultPrevented, false);
  assert.deepEqual(native.navigations, []);
  assert.deepEqual(native.opens, []);
}

// The initial hello must come from the acquired app window (including its
// same-origin Streamlit iframe); subsequent messages require that exact frame.
const pairingApp = application(catalog.origins.analysis, true);
const unrelatedApp = application(catalog.origins.analysis, true);
const storage = new Map();
const pairingSite = fixture('https://wspradar.org/en/', {storage, target: pairingApp.tab, links: [catalog.origins.analysis]});
pairingSite.message(appOrigin, unrelatedApp.frame, hello);
assert.equal(unrelatedApp.messages.length, 0);
pairingSite.click();
pairingSite.message('https://evil.example', pairingApp.frame, hello);
pairingSite.message(appOrigin, pairingApp.frame, {...hello, nonce: 'invalid'});
pairingSite.message(appOrigin, pairingApp.frame, {...hello, protocol: 'another-protocol'});
assert.equal(pairingApp.messages.length, 0);
pairingSite.message(appOrigin, pairingApp.frame, hello);
assert.equal(pairingApp.messages.length, 1);
assert.equal(JSON.stringify(pairingApp.messages[0]), JSON.stringify([{protocol, type: 'ack', nonce: token}, appOrigin]));
pairingSite.message(appOrigin, unrelatedApp.frame, navigate('https://wspradar.org/en/demos/'));
pairingSite.message('https://evil.example', pairingApp.frame, navigate('https://wspradar.org/en/demos/'));
pairingSite.message(appOrigin, pairingApp.frame, {...navigate('https://wspradar.org/en/demos/'), nonce: 'f'.repeat(32)});
for (const url of ['https://evil.example/en/', 'javascript:alert(1)', 'https://wspradar.org/?run=1',
                   'https://wspradar.org/en/../?run=1', 'https://wspradar.org/en/index.html',
                   'https://user@wspradar.org/en/', '/en/demos/', null]) {
  pairingSite.message(appOrigin, pairingApp.frame, navigate(url));
}
assert.deepEqual(pairingSite.navigations, []);
pairingSite.message(appOrigin, pairingApp.frame, navigate('https://wspradar.org/de/documentation/full/?view=1#sec-7'));
assert.deepEqual(pairingSite.navigations, ['https://wspradar.org/de/documentation/full/?view=1#sec-7']);
pairingSite.message(appOrigin, pairingApp.frame, navigate('https://wspradar.org/en/'));
assert.equal(pairingSite.navigations.length, 1); // Same page does not reload.

// Website page reloads retain only the session capability. A fresh hello binds
// the actual frame again before any navigation is accepted.
const reloadedSite = fixture('https://wspradar.org/en/community/', {storage});
reloadedSite.message(appOrigin, pairingApp.frame, navigate('https://wspradar.org/en/demos/'));
assert.deepEqual(reloadedSite.navigations, []);
reloadedSite.message(appOrigin, unrelatedApp.frame, {...hello, nonce: 'f'.repeat(32)});
assert.equal(unrelatedApp.messages.length, 0);
reloadedSite.message(appOrigin, pairingApp.frame, hello);
reloadedSite.message(appOrigin, pairingApp.frame, navigate('https://wspradar.org/en/demos/'));
assert.deepEqual(reloadedSite.navigations, ['https://wspradar.org/en/demos/']);

// App-first navigation pairs via the known opener without storage or polling.
const openerApp = application(catalog.origins.analysis, true);
const openedSite = fixture('https://wspradar.org/en/demos/', {opener: openerApp.frame, blockedStorage: true});
assert.equal(JSON.stringify(openerApp.messages[0]), JSON.stringify([{protocol, type: 'ready'}, appOrigin]));
openedSite.message(appOrigin, openerApp.frame, hello);
openedSite.message(appOrigin, openerApp.frame, navigate('https://wspradar.org/de/'));
assert.deepEqual(openedSite.navigations, ['https://wspradar.org/de/']);

// A live verified app must never be reacquired by name: embedded browsers can
// navigate an existing named tab to about:blank even for window.open('', name).
const knownApp = application(appOrigin + '/?existing=analysis', true);
const replacementApp = application();
const knownSite = fixture('https://wspradar.org/en/', {opener: knownApp.frame,
  target: replacementApp.tab, links: [catalog.origins.analysis, canonicalDemo]});
knownSite.message(appOrigin, knownApp.frame, hello);
knownSite.click();
assert.deepEqual(knownSite.opens, []);
assert.deepEqual(knownApp.writes, []);
assert.equal(knownApp.focusCount, 1);
knownSite.click(1);
assert.deepEqual(knownSite.opens, []);
assert.deepEqual(knownApp.writes, [appOrigin + '/?v=1&run=1&callsign=G3ZIL&ref=G4HZX#wspradar-results-inspection']);
knownApp.tab.closed = true;
knownSite.click();
assert.deepEqual(knownSite.opens, [['', 'wspradar_analysis']]);
assert.deepEqual(replacementApp.writes, [catalog.origins.analysis]);
replacementApp.tab.focus = () => { throw new Error('Focus refused'); };
assert.equal(knownSite.click().defaultPrevented, true);
assert.equal(knownSite.opens.length, 1);
assert.equal(replacementApp.writes.length, 1);
const redirect = fixture('https://wspradar.org/?v=1&run=1', {opener: openerApp.frame, runEntry: true});
assert.equal(redirect.window.name, undefined);
assert.equal(redirect.replacement, appOrigin + '/?v=1&run=1');
console.log('Paired product navigation: creation, reuse, explicit launches, native clicks, trusted messaging and reload checks passed.');

// Explicit compatibility deployments retain direct launches and trusted pairing.
for (const alias of catalog.analysis_aliases ?? []) {
  const aliasOrigin = new URL(alias).origin;
  const legacyApp = application(alias + '?existing=analysis', true);
  const legacyStorage = new Map();
  const legacySite = fixture('https://wspradar.org/en/', {opener: legacyApp.frame,
    storage: legacyStorage, links: [catalog.origins.analysis, alias + '?v=1&x=a%2Bb&x=2#result']});
  assert(legacyApp.messages.some(([, target]) => target === aliasOrigin));
  legacySite.message(aliasOrigin, legacyApp.frame, hello);
  assert.equal(legacyApp.messages.at(-1)[1], aliasOrigin);
  legacySite.click();
  assert.deepEqual(legacyApp.writes, []); // Generic launch keeps an existing CC analysis.
  legacySite.message(aliasOrigin, legacyApp.frame, navigate('https://wspradar.org/de/'));
  assert.deepEqual(legacySite.navigations, ['https://wspradar.org/de/']);
  legacySite.message(appOrigin, legacyApp.frame, navigate('https://wspradar.org/en/demos/'));
  assert.equal(legacySite.navigations.length, 1); // Exact paired origin remains mandatory.
  legacySite.click(1);
  assert.deepEqual(legacyApp.writes, [aliasOrigin + '/?v=1&x=a%2Bb&x=2#result']);
  const resumed = fixture('https://wspradar.org/en/community/', {storage: legacyStorage});
  resumed.message(appOrigin, legacyApp.frame, hello); // An alias nonce cannot bind another origin.
  resumed.message(appOrigin, legacyApp.frame, navigate('https://wspradar.org/de/'));
  assert.deepEqual(resumed.navigations, []);
  resumed.message(aliasOrigin, legacyApp.frame, hello);
  resumed.message(aliasOrigin, legacyApp.frame, navigate('https://wspradar.org/de/'));
  assert.deepEqual(resumed.navigations, ['https://wspradar.org/de/']);
  const localAlias = fixture('http://localhost:8787/en/', {links: [alias + '?v=1&x=a%2Bb#result']});
  assert.equal(localAlias.anchors[0].href, 'http://localhost:8501/?v=1&x=a%2Bb#result');
  localAlias.message(aliasOrigin, legacyApp.frame, hello);
  assert.deepEqual(localAlias.navigations, []);
}
console.log('Compatibility origins: direct launches, active-session reuse, exact-origin nonces and local routing passed.');
