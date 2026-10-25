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
})();
