const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../source/theme/scripts/entry.js'), 'utf8');

function destination(input) {
  const current = new URL(input);
  let replaced = null;
  vm.runInNewContext(source, {
    URL,
    window: {WSPRadarNavigation: {analysisOrigin: 'https://wspradar.streamlit.app/'}, location: {
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
  'https://wspradar.streamlit.app/?v=1&station=SK0WE%2FP&value=1&value=2#wspradar-results-inspection');
assert.equal(destination('https://wspradar.org/#wspradar-results-inspection'),
  'https://wspradar.streamlit.app/#wspradar-results-inspection');
assert.equal(destination('https://wspradar.org/?redirect=https%3A%2F%2Fexample.com%2F'),
  'https://wspradar.streamlit.app/?redirect=https%3A%2F%2Fexample.com%2F');
assert.equal(destination('https://wspradar.org/?v=1&min_spot_pairs=3&filter_spot_pairs=%3E%3D5#wspradar-results-inspection'),
  'https://wspradar.streamlit.app/?v=1&min_spot_pairs=3&filter_spot_pairs=%3E%3D5#wspradar-results-inspection');
assert.equal(destination('https://wspradar.org/?v=1&min_joint=3&filter_joint=%3E%3D5#wspradar-results-inspection'),
  'https://wspradar.streamlit.app/?v=1&min_joint=3&filter_joint=%3E%3D5#wspradar-results-inspection');
console.log('8 shared-link forwarding assertions passed.');
