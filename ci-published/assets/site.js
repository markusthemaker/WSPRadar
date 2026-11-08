document.documentElement.classList.add('js');
const toggle = document.querySelector('.nav-toggle');
const links = document.getElementById('nav-links');
const navigationShell = document.querySelector('.site-navigation-shell');
if (toggle && links && navigationShell) {
  const media = matchMedia('(max-width:800px)');
  function setMenuOpen(open) {
    links.hidden = media.matches && !open;
    toggle.setAttribute('aria-expanded', String(!links.hidden));
  }
  function measureNavigation() {
    document.documentElement.style.setProperty('--site-navigation-height',
      Math.ceil(navigationShell.getBoundingClientRect().height) + 'px');
  }
  function resizeNavigation() {
    const focusedLink = links.contains(document.activeElement);
    setMenuOpen(false);
    if (media.matches && focusedLink) toggle.focus({preventScroll: true});
    if (!media.matches && document.activeElement === toggle) links.querySelector('a[href]')?.focus({preventScroll: true});
    measureNavigation();
  }
  resizeNavigation();
  media.addEventListener('change', resizeNavigation);
  toggle.addEventListener('click', () => setMenuOpen(links.hidden));
  links.addEventListener('click', event => {
    if (event.target.closest('a') && media.matches) {
      setMenuOpen(false);
      toggle.focus({preventScroll: true});
    }
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && media.matches && !links.hidden) {
      setMenuOpen(false);
      toggle.focus({preventScroll: true});
    }
  });
  document.addEventListener('click', event => {
    if (media.matches && !navigationShell.contains(event.target)) setMenuOpen(false);
  });
  navigationShell.addEventListener('focusout', event => {
    if (media.matches && event.relatedTarget && !navigationShell.contains(event.relatedTarget)) setMenuOpen(false);
  });
  // One observer per document; no scroll handler or repeated DOM scanning.
  if (typeof ResizeObserver !== 'undefined') new ResizeObserver(measureNavigation).observe(navigationShell);
}
const index = document.querySelector('.reader-index');
if (index) {
  const readerMedia = matchMedia('(width < 760px)');
  const summary = index.querySelector('summary');
  function resizeReader() {
    const focusedContent = index.contains(document.activeElement) && document.activeElement !== summary;
    index.open = !readerMedia.matches;
    if (!index.open && focusedContent) summary?.focus({preventScroll: true});
  }
  resizeReader();
  readerMedia.addEventListener('change', resizeReader);

  const rootElement = index.querySelector('[data-reader-root]');
  if (rootElement) {
    // Cache the small current-chapter tree once.
    const nodes = [rootElement, ...rootElement.querySelectorAll('[data-reader-node]')].map(element => ({
      element,
      link: element.querySelector(':scope > a'),
      children: element.querySelector(':scope > .reader-children'),
      parent: null,
    }));
    const byElement = new Map(nodes.map(node => [node.element, node]));
    const byAnchor = new Map();
    for (const node of nodes) {
      node.parent = byElement.get(node.element.parentElement?.closest('[data-reader-node]')) ?? null;
      for (const anchor of JSON.parse(node.element.dataset.readerAnchors)) byAnchor.set(anchor, node);
      if (node.children) node.link.setAttribute('aria-controls', node.children.id);
    }
    const root = nodes[0];
    let currentSelection;
    function nodeForFragment(hash) {
      try { return byAnchor.get(decodeURIComponent(hash.slice(1))); } catch (_) { return undefined; }
    }
    function selectReaderBranch(selected, followingScroll = false) {
      if (followingScroll && selected === currentSelection) return true;
      const activePath = new Set();
      for (let node = selected; node; node = node.parent) activePath.add(node);
      const hiddenFocus = nodes.some(node => node.children && !activePath.has(node) &&
        node.children.contains(document.activeElement));
      if (followingScroll && hiddenFocus) return false;
      for (const node of nodes) {
        if (node !== root) {
          if (node === selected) node.link.setAttribute('aria-current', 'location');
          else node.link.removeAttribute('aria-current');
        }
        if (activePath.has(node) && node !== selected) node.link.setAttribute('data-reader-active-path', '');
        else node.link.removeAttribute('data-reader-active-path');
        if (node.children) {
          const expanded = activePath.has(node);
          node.children.hidden = !expanded;
          node.link.setAttribute('aria-expanded', String(expanded));
        }
      }
      if (hiddenFocus) selected.link.focus({preventScroll: true});
      if (!readerMedia.matches && index.open) {
        // Reveal the selection inside the sidebar only; native anchors own article scrolling.
        const viewport = index.getBoundingClientRect();
        const target = selected.link.getBoundingClientRect();
        const inset = 12;
        if (target.top < viewport.top + inset) {
          index.scrollTop += target.top - viewport.top - inset;
        } else if (target.bottom > viewport.bottom - inset) {
          index.scrollTop += Math.max(0, target.top - viewport.top - Math.max(inset, viewport.height / 4));
        }
      }
      currentSelection = selected;
      return true;
    }

    // The builder emits navigation nodes and article headings in the same order.
    const headings = document.querySelector('.reader-layout > article.prose')
      ?.querySelectorAll('h1, h2, h3, h4, h5, h6');
    let navigationUntil = 0;
    const navigationQuietMs = 180;
    function selectFragment(hash) {
      navigationUntil = performance.now() + navigationQuietMs;
      selectReaderBranch(nodeForFragment(hash) ?? root);
    }
    selectReaderBranch(nodeForFragment(window.location.hash) ?? root);
    if (window.location.hash) navigationUntil = performance.now() + navigationQuietMs;
    window.addEventListener('hashchange', () => selectFragment(window.location.hash));

    if (headings?.length === nodes.length && headings.length > 1) {
      let framePending = false;
      let deferred = false;
      let lastScroll = window.scrollY;
      let movingDown = true;
      function followReadingPosition() {
        framePending = false;
        const scroll = window.scrollY;
        if (scroll !== lastScroll) movingDown = scroll > lastScroll;
        lastScroll = scroll;
        if (performance.now() < navigationUntil) return;
        if (readerMedia.matches && index.open) {
          // Expanding inline contents could move the article under the reader.
          deferred = true;
          return;
        }

        // Match the sticky header clearance plus room for the anchor margin.
        // The direction-dependent gap keeps a heading stable at the reading line.
        const readingLine = (navigationShell?.offsetHeight ?? 0) + 56 + (movingDown ? -8 : 8);
        let first = 1;
        let last = headings.length;
        if (scroll > 0 && scroll + window.innerHeight >= document.documentElement.scrollHeight - 2) {
          first = last;
        }
        while (first < last) {
          const middle = Math.floor((first + last) / 2);
          if (headings[middle].getBoundingClientRect().top <= readingLine) first = middle + 1;
          else last = middle;
        }
        deferred = !selectReaderBranch(nodes[first - 1], true);
      }
      function queueReadingUpdate() {
        if (framePending) return;
        framePending = true;
        window.requestAnimationFrame(followReadingPosition);
      }
      function releaseNavigation() {
        navigationUntil = 0;
      }
      window.addEventListener('scroll', () => {
        if (performance.now() < navigationUntil) {
          // Native scrollend releases this on arrival. The quiet period also
          // covers browsers without scrollend and jumps that need no movement.
          navigationUntil = performance.now() + navigationQuietMs;
          lastScroll = window.scrollY;
          return;
        }
        queueReadingUpdate();
      }, {passive: true});
      window.addEventListener('scrollend', releaseNavigation);
      window.addEventListener('wheel', releaseNavigation, {passive: true});
      window.addEventListener('touchmove', releaseNavigation, {passive: true});
      window.addEventListener('keydown', event => {
        if (['ArrowUp', 'ArrowDown', 'PageUp', 'PageDown', 'Home', 'End', ' '].includes(event.key)) {
          releaseNavigation();
        }
      });
      document.addEventListener('click', event => {
        if (event.defaultPrevented || event.button !== 0 || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
        const link = event.target.closest?.('a[href]');
        const here = window.location;
        if (!link || !link.hash || link.hasAttribute('download') || (link.target && link.target !== '_self') ||
            link.origin !== here.origin || link.pathname !== here.pathname || link.search !== here.search) return;
        // A second activation of the same fragment need not fire hashchange.
        if (nodeForFragment(link.hash)) selectFragment(link.hash);
      });
      index.addEventListener('focusout', () => { if (deferred) queueReadingUpdate(); });
      index.addEventListener('toggle', () => { if (deferred && !index.open) queueReadingUpdate(); });
      window.addEventListener('pageshow', event => {
        if (event.persisted) {
          releaseNavigation();
          queueReadingUpdate();
        } else if (window.location.hash) {
          selectFragment(window.location.hash);
        }
      });
    } else {
      window.addEventListener('pageshow', () => selectFragment(window.location.hash));
    }
  }
}
document.querySelectorAll('[data-filter-input]').forEach(input => {
  const cards = [...document.querySelectorAll('[data-filter-text]')];
  input.addEventListener('input', () => {
    const query = input.value.trim().toLocaleLowerCase();
    let visible = 0;
    cards.forEach(card => {
      card.hidden = !card.dataset.filterText.toLocaleLowerCase().includes(query);
      if (!card.hidden) visible++;
    });
    const status = document.querySelector('[data-filter-status]');
    if (status) status.textContent = visible + ' / ' + cards.length;
  });
});
