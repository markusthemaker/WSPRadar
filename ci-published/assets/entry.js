// Retain the existing root URL forwarding contract for shared app analyses.
// The app validates all shared query state before any language entry routing.
if (window.location.pathname === '/' &&
    (window.location.search || window.location.hash === '#wspradar-results-inspection')) {
  const destination = new URL(window.WSPRadarNavigation.analysisOrigin);
  destination.search = window.location.search;
  destination.hash = window.location.hash;
  window.location.replace(destination.toString());
} else if (window.location.pathname === '/') {
  const destination = new URL('/' + window.WSPRadarNavigation.language + '/', window.location.href);
  destination.hash = window.location.hash;
  if (['en', 'de'].includes(window.WSPRadarNavigation.handoffLanguage)) {
    destination.search = '?ui_lang=' + window.WSPRadarNavigation.handoffLanguage;
  }
  window.location.replace(destination.toString());
}
