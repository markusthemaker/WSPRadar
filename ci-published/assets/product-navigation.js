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
  if (local) analysisOrigins.add(new URL(analysisOrigin).origin);
  const websiteOrigins = new Set([new URL(catalog.origins.website).origin,
    'https://wspradar.org']);
  if (local) websiteOrigins.add(window.location.origin);

  const preferenceKey = 'wspradar.language';
  const choiceParameter = 'ui_lang';
  const supported = value => value === 'en' || value === 'de';
  const routeLanguage = /^\/(en|de)(?:\/|$)/.exec(window.location.pathname)?.[1];
  const forwardAnalysis = window.location.pathname === '/' &&
    (withoutChoice(window.location.search) || window.location.hash === '#wspradar-results-inspection');

  function withoutChoice(search) {
    if (!search) return search;
    const tokens = search.slice(1).split('&').filter(token => {
      try {
        return decodeURIComponent(token.split('=', 1)[0].replace(/\+/g, ' ')) !== choiceParameter;
      } catch (_) { return true; }
    });
    return tokens.length ? '?' + tokens.join('&') : '';
  }

  function withChoice(url, choice) {
    const destination = new URL(url, window.location.href);
    const search = withoutChoice(destination.search);
    destination.search = search + (search ? '&' : '?') + choiceParameter + '=' + choice;
    return destination.href;
  }

  function saveLanguage(choice) {
    try {
      window.localStorage.setItem(preferenceKey, choice);
      return true;
    } catch (_) { return false; }
  }

  let savedLanguage;
  try { savedLanguage = window.localStorage.getItem(preferenceKey); } catch (_) {}
  const choices = new URL(window.location.href).searchParams.getAll(choiceParameter);
  const handoff = !forwardAnalysis && choices.length === 1 && supported(choices[0])
    ? choices[0] : null;
  const browserLanguage = window.navigator?.language ?? '';
  const language = handoff
    ?? (supported(savedLanguage) ? savedLanguage : null)
    ?? (/^de(?:-|$)/i.test(browserLanguage) ? 'de' : 'en');
  // An arriving path or ordinary lang query is not a recipient preference.
  // If storage is blocked, carry an explicit choice only on activated links.
  const transientChoice = handoff !== null && !saveLanguage(handoff);
  const cleanSearch = withoutChoice(window.location.search);

  if (!forwardAnalysis && routeLanguage && routeLanguage !== language) {
    const destination = new URL(window.location.href);
    destination.pathname = destination.pathname.replace(/^\/(?:en|de)(?=\/|$)/, '/' + language);
    // Keep a valid one-shot choice until the matching page arrives, otherwise
    // denied storage could send that page straight back to the browser language.
    if (!handoff) destination.search = cleanSearch;
    window.location.replace(destination.href);
  } else if (!forwardAnalysis && cleanSearch !== window.location.search) {
    window.history.replaceState(window.history.state, '',
      window.location.pathname + cleanSearch + window.location.hash);
  }

  function isAnalysis(url) {
    return !url.username && !url.password && url.pathname === '/' && analysisOrigins.has(url.origin);
  }

  function analysisLaunchUrl(value) {
    const url = new URL(value, window.location.href);
    if (url.username || url.password || url.pathname !== '/') return url.href;
    const isCanonicalLaunch = websiteOrigins.has(url.origin)
      && (url.search || url.hash === '#wspradar-results-inspection');
    if (!isCanonicalLaunch && !isAnalysis(url)) return url.href;
    const destination = isCanonicalLaunch || (local && isAnalysis(url))
      ? new URL(analysisOrigin) : url;
    destination.search = withoutChoice(url.search);
    destination.hash = url.hash;
    return destination.href;
  }

  window.WSPRadarNavigation = Object.freeze({analysisOrigin, analysisLaunchUrl, language, handoffLanguage: handoff});
  document.addEventListener('DOMContentLoaded', () => {
    // Keep copyable links free of the one-shot choice. Ordinary query and hash
    // bytes remain intact, including duplicate scientific or legacy lang keys.
    for (const anchor of document.querySelectorAll('a[href]')) {
      if (anchor.hasAttribute('download')) continue;
      if (anchor.classList.contains('language-option')) {
        const destination = new URL(anchor.href);
        destination.search = withoutChoice(window.location.search);
        destination.hash = window.location.hash;
        anchor.href = destination.href;
        continue;
      }
      const destination = analysisLaunchUrl(anchor.href);
      if (destination !== anchor.href) anchor.href = destination;
    }
  });

  function activate(event) {
    if (event.defaultPrevented ||
        (event.type === 'click' && event.button !== 0) ||
        (event.type === 'auxclick' && event.button !== 1)) return;
    const anchor = event.target.closest?.('a[href]');
    if (!anchor || anchor.hasAttribute('download')) return;
    const destination = new URL(anchor.href, window.location.href);
    if (destination.username || destination.password) return;
    const sameOrigin = destination.origin === window.location.origin;
    const sameDocument = sameOrigin && destination.pathname === window.location.pathname &&
      withoutChoice(destination.search) === withoutChoice(window.location.search);
    const destinationLanguage = /^\/(en|de)(?:\/|$)/.exec(destination.pathname)?.[1];
    let choice = null;
    if (sameOrigin && destinationLanguage && anchor.classList.contains('language-option')) {
      choice = destinationLanguage;
      saveLanguage(choice);
    } else if (isAnalysis(destination) ||
        (transientChoice && sameOrigin && destinationLanguage && !sameDocument)) {
      choice = language;
    }
    if (choice === null) return;
    const cleanHref = anchor.href;
    const activatedHref = withChoice(destination.href, choice);
    anchor.href = activatedHref;
    // Let the browser perform its native action, including modifiers/new tabs.
    // Restore afterwards so Copy Link never retains a previous handoff.
    window.setTimeout(() => {
      if (anchor.href === activatedHref) anchor.href = cleanHref;
    }, 0);
  }
  document.addEventListener('click', activate, true);
  document.addEventListener('auxclick', activate, true);
})();
