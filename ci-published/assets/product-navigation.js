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
  const analysisOrigins = new Set([catalog.origins.analysis,
    ...(catalog.analysis_aliases ?? [])].map(value => new URL(value).origin));
  const websiteOrigins = new Set([new URL(catalog.origins.website).origin,
    'https://wspradar.org']);
  if (local) websiteOrigins.add(window.location.origin);

  function analysisLaunchUrl(value) {
    const url = new URL(value, window.location.href);
    if (url.username || url.password || url.pathname !== '/') return url.href;
    const isAnalysis = analysisOrigins.has(url.origin);
    const isCanonicalLaunch = websiteOrigins.has(url.origin)
      && (url.search || url.hash === '#wspradar-results-inspection');
    if (!isCanonicalLaunch && !(local && isAnalysis)) return url.href;
    const destination = new URL(analysisOrigin);
    destination.search = url.search;
    destination.hash = url.hash;
    return destination.href;
  }

  window.WSPRadarNavigation = Object.freeze({analysisOrigin, analysisLaunchUrl});
  document.addEventListener('DOMContentLoaded', () => {
    // Set ordinary anchor destinations before interaction. The browser retains
    // native same-tab navigation, modifier clicks, downloads and history.
    for (const anchor of document.querySelectorAll('a[href]')) {
      if (anchor.hasAttribute('download')) continue;
      const destination = analysisLaunchUrl(anchor.href);
      if (destination !== anchor.href) anchor.href = destination;
    }
  });
})();
