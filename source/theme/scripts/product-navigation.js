// Shared route data comes from the manifest-verified public brand catalog.
(() => {
  const source = document.getElementById('wspradar-product-navigation');
  if (!source) return;
  const configuration = JSON.parse(source.textContent);
  const catalog = configuration.catalog;
  const local = new Set(['localhost', '127.0.0.1', '[::1]', '::1']).has(window.location.hostname);
  const localPort = configuration.local_analysis_port ?? catalog.local.analysis_port;
  const analysisOrigin = local
    ? `${window.location.protocol}//${window.location.hostname}:${localPort}/`
    : catalog.origins.analysis;
  const productionWebsite = new URL(catalog.origins.website);
  const productionAnalysis = new URL(catalog.origins.analysis);
  const applicationOrigin = new URL(analysisOrigin).origin;
  const websiteOrigin = local ? window.location.origin : productionWebsite.origin;

  function isAnalysisLaunch(url) {
    if (url.username || url.password || url.pathname !== '/') return false;
    return url.origin === applicationOrigin || url.origin === productionAnalysis.origin
      || ((url.origin === productionWebsite.origin || url.origin === websiteOrigin)
        && Boolean(url.search || url.hash === '#wspradar-results-inspection'));
  }

  function analysisLaunchUrl(value) {
    const url = new URL(value, window.location.href);
    const isAnalysis = url.origin === productionAnalysis.origin && url.pathname === '/';
    const isCanonicalLaunch = url.origin === productionWebsite.origin
      && url.pathname === '/'
      && (url.search || url.hash === '#wspradar-results-inspection');
    if (!local || (!isAnalysis && !isCanonicalLaunch)) return url.href;
    const destination = new URL(analysisOrigin);
    destination.search = url.search;
    destination.hash = url.hash;
    return destination.href;
  }

  window.WSPRadarNavigation = Object.freeze({analysisOrigin, analysisLaunchUrl});
  document.addEventListener('DOMContentLoaded', () => {
    if (!local) return;
    for (const anchor of document.querySelectorAll('a[href]')) {
      const sourceUrl = new URL(anchor.href, window.location.href);
      const destination = analysisLaunchUrl(sourceUrl.href);
      if (destination !== sourceUrl.href) anchor.href = destination;
    }
  });

  // The entry script owns shared-analysis root redirects. Do not give those
  // transient pages the website tab's identity before they become the app.
  if (window.location.origin !== websiteOrigin || (window.location.pathname === '/'
      && (window.location.search || window.location.hash === '#wspradar-results-inspection'))) return;

  const protocol = 'wspradar-navigation-v1';
  const nonceKey = `${protocol}:${applicationOrigin}`;
  let appWindow = null;
  let appSource = null;
  let nonce = null;
  try { nonce = window.sessionStorage.getItem(nonceKey); } catch (_) { /* Storage may be disabled. */ }
  if (!/^[a-f0-9]{32}$/.test(nonce ?? '')) nonce = null;
  window.name = 'wspradar_website';

  function topWindow(sourceWindow) {
    try { return sourceWindow.top; } catch (_) { return null; }
  }

  function websiteDestination(value) {
    if (typeof value !== 'string') return null;
    try {
      const url = new URL(value);
      // Root query links launch analyses. Messages may only select localized
      // website pages, never arbitrary destinations or the analysis redirect.
      if (url.origin !== websiteOrigin || url.username || url.password
          || !/^\/(en|de)\/(?:[a-zA-Z0-9_-]+\/)*$/.test(url.pathname)) return null;
      return url;
    } catch (_) { return null; }
  }

  window.addEventListener('message', event => {
    const message = event.data;
    if (event.origin !== applicationOrigin || !event.source || !message
        || message.protocol !== protocol || !/^[a-f0-9]{32}$/.test(message.nonce ?? '')) return;
    if (message.type === 'hello') {
      const knownWindow = (appWindow && topWindow(event.source) === appWindow)
        || event.source === window.opener;
      // A full website navigation loses WindowProxy references. The nonce is a
      // session capability already exchanged with this exact application origin.
      if (!knownWindow && (!nonce || message.nonce !== nonce)) return;
      appSource = event.source;
      appWindow = topWindow(event.source);
      nonce = message.nonce;
      try { window.sessionStorage.setItem(nonceKey, nonce); } catch (_) { /* Current-page pairing still works. */ }
      appSource.postMessage({protocol, type: 'ack', nonce}, applicationOrigin);
    } else if (message.type === 'navigate' && event.source === appSource && message.nonce === nonce) {
      const destination = websiteDestination(message.url);
      if (destination && destination.href !== window.location.href) window.location.assign(destination.href);
    }
  });

  document.addEventListener('click', event => {
    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey
        || event.shiftKey || event.altKey) return;
    const anchor = event.target?.closest?.('a[href]');
    if (!anchor || anchor.hasAttribute('download')) return;
    const destination = new URL(anchor.href, window.location.href);
    const targetName = anchor.getAttribute('target');
    if (websiteDestination(destination.href) && targetName && targetName.toLowerCase() !== '_self') {
      event.preventDefault();
      // Retarget own HTML pages into this website tab. Location assignment keeps
      // native fragment navigation; untargeted/_self anchors remain fully native.
      if (destination.href !== window.location.href) window.location.assign(destination.href);
      return;
    }
    if (!isAnalysisLaunch(destination)) return;
    let target = appWindow;
    // A verified live handle avoids asking the browser to reacquire a named
    // window (which some hosts navigate even when given an empty URL).
    try {
      if (!target || target.closed) target = window.open('', 'wspradar_analysis');
    } catch (_) { return; }
    if (!target) return; // Keep the native anchor fallback when popups are blocked.
    event.preventDefault();
    appWindow = target;
    let blank = false;
    try { blank = target.location.href === 'about:blank'; } catch (_) { /* An existing cross-origin app. */ }
    if (blank || destination.search || destination.hash === '#wspradar-results-inspection') {
      const launch = new URL(analysisOrigin);
      launch.search = destination.search;
      launch.hash = destination.hash;
      target.location.href = launch.href;
    }
    try { target.focus(); } catch (_) { /* Browsers may refuse a tab focus request. */ }
  });

  // App-first visits have an opener; its controller answers ready with hello.
  // Website-first visits receive hello after opening the app. No polling is needed.
  if (window.opener) window.opener.postMessage({protocol, type: 'ready'}, applicationOrigin);
})();
