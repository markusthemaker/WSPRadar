const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../source/theme/scripts/entry.js'), 'utf8');

function destination(input, analysisOrigin = 'https://app.wspradar.org/') {
  const current = new URL(input);
  let replaced = null;
  vm.runInNewContext(source, {
    URL,
    window: {WSPRadarNavigation: {analysisOrigin}, location: {
      pathname: current.pathname, search: current.search, hash: current.hash,
      replace(value) { replaced = value; },
    }},
  });
  return replaced;
}

assert.equal(destination('https://wspradar.org/'), null);
assert.equal(destination('https://wspradar.org/#main'), null);
assert.equal(destination('https://wspradar.org/en/?v=1#main'), null);
assert.equal(destination('https://wspradar.org/?v=1&station=SK0WE%2FP&value=1&value=2#wspradar-results-inspection'),
  'https://app.wspradar.org/?v=1&station=SK0WE%2FP&value=1&value=2#wspradar-results-inspection');
assert.equal(destination('https://wspradar.org/#wspradar-results-inspection'),
  'https://app.wspradar.org/#wspradar-results-inspection');
assert.equal(destination('https://wspradar.org/?redirect=https%3A%2F%2Fexample.com%2F'),
  'https://app.wspradar.org/?redirect=https%3A%2F%2Fexample.com%2F');
assert.equal(destination('https://wspradar.org/?v=1&min_spot_pairs=3&filter_spot_pairs=%3E%3D5#wspradar-results-inspection'),
  'https://app.wspradar.org/?v=1&min_spot_pairs=3&filter_spot_pairs=%3E%3D5#wspradar-results-inspection');
assert.equal(destination('https://wspradar.org/?v=1&min_joint=3&filter_joint=%3E%3D5#wspradar-results-inspection'),
  'https://app.wspradar.org/?v=1&min_joint=3&filter_joint=%3E%3D5#wspradar-results-inspection');
console.log('8 shared-link forwarding assertions passed.');

const hosted = 'https://markusthemaker-wspradar.hf.space/';
assert.equal(destination('https://wspradar.org/?v=1&x=a%2Bb&x=2#wspradar-results-inspection', hosted),
  hosted + '?v=1&x=a%2Bb&x=2#wspradar-results-inspection');
console.log('Hugging Face shared-link forwarding preserves encoding, duplicate values and fragment.');

assert.equal(destination('https://www.wspradar.org/?v=1&x=a%2Bb&x=2#wspradar-results-inspection'),
  'https://app.wspradar.org/?v=1&x=a%2Bb&x=2#wspradar-results-inspection');
