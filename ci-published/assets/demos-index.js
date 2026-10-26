(() => {
  function initializeDemos() {
    const landing = document.querySelector('.demos-landing');
    if (!landing || landing.dataset.demosInitialized === 'true') return;

    const cards = [...landing.querySelectorAll('.demo-card[data-modes]')];
    const controls = [...landing.querySelectorAll('[data-filter]')];
    const reset = landing.querySelector('#reset-filter');
    const title = landing.querySelector('#collection-title');
    const count = landing.querySelector('#demo-count');
    const description = landing.querySelector('#collection-description');
    const note = landing.querySelector('#collection-note');
    if (!cards.length || !reset || !title || !count) return;

    const availableModes = new Set(cards.flatMap(card => card.dataset.modes.split(/\s+/)));
    const availableControls = controls.filter(button => !button.disabled && availableModes.has(button.dataset.filter));
    const labels = Object.fromEntries(availableControls.map(button => [button.dataset.filter, button.dataset.label]));
    const defaultTitle = title.textContent;
    const descriptions = Object.fromEntries(availableControls.map(button => [button.dataset.filter, button.dataset.description]));
    descriptions.all = description ? description.dataset.defaultDescription || description.textContent : '';
    const categorizedCards = cards.map(card => ({
      card,
      modes: card.dataset.modes.split(/\s+/),
    }));
    let chosen = 'all';

    function applyFilters() {
      let total = 0;
      categorizedCards.forEach(({card, modes}) => {
        const matches = chosen === 'all' || modes.includes(chosen);
        card.hidden = !matches;
        if (matches) total++;
      });
      controls.forEach(button => {
        button.setAttribute('aria-pressed', String(button.dataset.filter === chosen));
      });
      reset.setAttribute('aria-pressed', String(chosen === 'all'));
      title.textContent = chosen === 'all' ? defaultTitle : labels[chosen] + ' demos';
      count.textContent = chosen === 'all'
        ? `${total} guided demos`
        : `${total} of ${cards.length} demos`;
      if (description) description.textContent = descriptions[chosen];
      if (note) note.hidden = chosen === 'rx-performance';
    }

    function updateURL() {
      const url = new URL(window.location.href);
      if (chosen === 'all') url.searchParams.delete('use');
      else url.searchParams.set('use', chosen);
      if (url.href === window.location.href) return;
      try {
        window.history.replaceState(window.history.state, '', url);
      } catch (error) {
        // Filtering remains usable if browser policy prevents updating the URL.
      }
    }

    function readURL() {
      const requested = new URL(window.location.href).searchParams.get('use');
      chosen = Object.hasOwn(labels, requested) ? requested : 'all';
      applyFilters();
      updateURL();
    }

    controls.forEach(button => {
      button.addEventListener('click', () => {
        if (button.disabled || !Object.hasOwn(labels, button.dataset.filter)) return;
        chosen = button.dataset.filter;
        applyFilters();
        updateURL();
      });
    });
    reset.addEventListener('click', () => {
      chosen = 'all';
      applyFilters();
      updateURL();
    });
    window.addEventListener('popstate', readURL);
    count.setAttribute('role', 'status');
    count.setAttribute('aria-live', 'polite');
    count.setAttribute('aria-atomic', 'true');
    landing.dataset.demosInitialized = 'true';
    readURL();
    landing.querySelectorAll('[data-demo-controls]').forEach(control => { control.hidden = false; });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeDemos, {once: true});
  } else {
    initializeDemos();
  }
})();
