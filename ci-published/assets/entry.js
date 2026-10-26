// Retain the existing root URL forwarding contract for shared app analyses.
// Plain visits remain on the public website; the app validates all query state.
if (window.location.pathname === '/' &&
    (window.location.search || window.location.hash === '#wspradar-results-inspection')) {
  const destination = new URL(window.WSPRadarNavigation.analysisOrigin);
  destination.search = window.location.search;
  destination.hash = window.location.hash;
  window.location.replace(destination.toString());
}
