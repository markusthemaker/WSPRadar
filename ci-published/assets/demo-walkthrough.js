/* Progressive enhancement: image links still open their originals without JS. */
(() => {
  const root = document.querySelector('.case-study');
  // The complete article is the default HTML. Enable its shorter reading path
  // only after the required destinations and native controls are available.
  if (root?.hasAttribute('data-reading-modes') && root.dataset.readingModesReady !== 'true') {
    const selector = root.querySelector('.case-mode-selector');
    const buttons = [...root.querySelectorAll('[data-reading-mode]')];
    const views = Object.fromEntries([...root.querySelectorAll('[data-reading-view]')]
      .map(view => [view.dataset.readingView, view]));
    const essentialsStart = document.getElementById('essentials-comparison');
    const fullStart = document.getElementById('full-overview');
    const essentials = (root.dataset.essentialsSections || '').split(/\s+/).filter(Boolean)
      .map(id => document.getElementById(id));
    if (selector && buttons.length === 2 && views.essentials && views.full &&
        essentialsStart && fullStart && views.essentials.contains(essentialsStart) &&
        views.full.contains(fullStart) &&
        essentials.length > 0 && essentials[0] === essentialsStart &&
        essentials.every(tile => tile && views.essentials.contains(tile)) &&
        new Set(buttons.map(button => button.dataset.readingMode)).size === 2 &&
        buttons.every(button => Object.hasOwn(views, button.dataset.readingMode))) {
      const languageLinks = [...document.querySelectorAll('a.language-option[href]')];
      function destination(hash) {
        let id;
        try { id = decodeURIComponent(hash.slice(1)); } catch (_) { return null; }
        const target = document.getElementById(id);
        if (!target || !root.contains(target)) return null;
        const view = target.closest('[data-reading-view]');
        return view && Object.hasOwn(views, view.dataset.readingView)
          ? {target, mode: view.dataset.readingView} : null;
      }

      function updateLanguageLinks() {
        for (const link of languageLinks) {
          const url = new URL(link.href, document.baseURI);
          url.hash = window.location.hash;
          link.href = url.href;
        }
      }

      function position(target, focus, smooth) {
        const section = target.tagName === 'SPAN' ? target.closest('section') : target;
        const heading = section?.querySelector('h2,h3,h4') || section || target;
        if (focus) {
          if (!heading.hasAttribute('tabindex')) heading.setAttribute('tabindex', '-1');
          heading.focus({preventScroll: true});
        }
        heading.scrollIntoView({block: 'start', behavior: smooth &&
          !window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'smooth' : 'instant'});
      }

      function select(hash, {scroll = true, focus = false, smooth = false} = {}) {
        const found = destination(hash);
        const mode = found?.mode || 'essentials';
        const hidingFocus = Object.entries(views).some(([key, view]) =>
          key !== mode && view.contains(document.activeElement));
        for (const [key, view] of Object.entries(views)) view.hidden = key !== mode;
        for (const button of buttons) {
          button.setAttribute('aria-pressed', String(button.dataset.readingMode === mode));
        }
        root.dataset.readingMode = mode;
        updateLanguageLinks();
        const target = found?.target || essentialsStart;
        // Reveal nested evidence disclosures before measuring the destination.
        if (target.tagName === 'DETAILS') target.open = true;
        for (let parent = target.parentElement; parent && parent !== root; parent = parent.parentElement) {
          if (parent.tagName === 'DETAILS') parent.open = true;
        }
        if (scroll && (found || !hash || hidingFocus)) position(target, focus || hidingFocus, smooth);
      }

      function navigate(hash) {
        if (window.location.hash !== hash) {
          const url = new URL(window.location.href);
          url.hash = hash;
          try { window.history.pushState(window.history.state, '', url); }
          catch (_) {
            // Reveal first even when browser policy requires native navigation.
            select(hash, {scroll: false});
            window.location.hash = hash;
            return;
          }
        }
        select(hash, {focus: true, smooth: true});
      }

      buttons.forEach(button => button.addEventListener('click', () => {
        navigate(button.dataset.readingMode === 'full' ? '#full-overview' : '#essentials-comparison');
      }));
      root.addEventListener('click', event => {
        if (event.defaultPrevented || event.button !== 0 || event.ctrlKey || event.metaKey ||
            event.shiftKey || event.altKey) return;
        const link = event.target.closest?.('a[href]');
        if (!link || link.hasAttribute('download') || (link.target && link.target !== '_self')) return;
        const url = new URL(link.href, document.baseURI);
        const here = new URL(window.location.href);
        if (url.origin !== here.origin || url.pathname !== here.pathname ||
            url.search !== here.search || !destination(url.hash)) return;
        event.preventDefault();
        navigate(url.hash);
      });
      window.addEventListener('hashchange', () => select(window.location.hash));
      select(window.location.hash, {scroll: Boolean(destination(window.location.hash))});
      selector.hidden = false;
      root.dataset.readingModesReady = 'true';
    }
  }
  const de = document.documentElement.lang === 'de';
  const labels = de ? {close:'Schließen',previous:'Vorherige Abbildung',next:'Nächste Abbildung',in:'Vergrößern',out:'Verkleinern',fit:'Einpassen',title:'Abbildung',loading:'Abbildung wird geladen'} : {close:'Close',previous:'Previous figure',next:'Next figure',in:'Zoom in',out:'Zoom out',fit:'Fit',title:'Figure',loading:'Loading figure'};
  const figureLinks = [...document.querySelectorAll('main a[href]')].filter(link => {
    if (!link.querySelector('img') || link.hasAttribute('download')) return false;
    if (link.hasAttribute('data-case-lightbox')) return true;
    try {
      return /\.(?:avif|gif|jpe?g|png|svg|webp)$/i.test(new URL(link.href, document.baseURI).pathname);
    } catch {
      return false;
    }
  });
  const galleryFor = link => link.closest('[data-reading-view], .result-gallery, .case-study') || link.closest('main');
  if (figureLinks.length && typeof HTMLDialogElement !== 'undefined') {
    const dialog = document.createElement('dialog');
    dialog.className = 'case-dialog';
    dialog.setAttribute('aria-labelledby','case-dialog-title');
    dialog.innerHTML = `<div class="case-dialog-head"><h2 id="case-dialog-title"></h2><div class="case-dialog-controls"><button type="button" data-action="previous" aria-label="${labels.previous}">←</button><button type="button" data-action="out" aria-label="${labels.out}">−</button><button type="button" data-action="fit">${labels.fit}</button><button type="button" data-action="in" aria-label="${labels.in}">+</button><button type="button" data-action="next" aria-label="${labels.next}">→</button><span class="case-dialog-status" aria-live="polite"></span><button type="button" data-action="close" aria-label="${labels.close}">✕</button></div></div><div class="case-dialog-stage" tabindex="0" aria-label="${labels.title}"><img alt=""></div><div class="case-dialog-caption"></div>`;
    document.body.append(dialog);
    const stage = dialog.querySelector('.case-dialog-stage');
    const image = stage.querySelector('img');
    const title = dialog.querySelector('h2');
    const caption = dialog.querySelector('.case-dialog-caption');
    const status = dialog.querySelector('.case-dialog-status');
    let figures = [], index = 0, zoom = 1, origin = null, previousOverflow = '', loadToken = 0;
    function fitImage() {
      if (!image.naturalWidth || !image.naturalHeight || !dialog.open) return;
      const padding = getComputedStyle(stage);
      const horizontal = parseFloat(padding.paddingLeft) + parseFloat(padding.paddingRight);
      const vertical = parseFloat(padding.paddingTop) + parseFloat(padding.paddingBottom);
      const availableHeight = Math.max(1, window.innerHeight * .94 - dialog.querySelector('.case-dialog-head').offsetHeight - caption.offsetHeight - 2);
      const base = Math.min((stage.clientWidth - horizontal) / image.naturalWidth, (availableHeight - vertical) / image.naturalHeight, 1);
      const width = Math.max(1, image.naturalWidth * base * zoom);
      image.style.width = width + 'px';
      stage.style.height = Math.min(availableHeight, image.naturalHeight * width / image.naturalWidth + vertical) + 'px';
      dialog.querySelector('[data-action="out"]').disabled = zoom <= 1;
      dialog.querySelector('[data-action="in"]').disabled = zoom >= 8;
    }
    function show(i) {
      index = (i + figures.length) % figures.length;
      zoom = 1;
      const link = figures[index];
      const original = link.querySelector('img');
      image.alt = link.dataset.originalAlt || original.alt;
      title.textContent = link.dataset.title || image.alt || labels.title;
      image.classList.toggle('case-image-inverted', link.dataset.invertColors === 'true');
      image.style.filter = link.dataset.imageFilter || '';
      image.style.width = '1px';
      const token = ++loadToken;
      image.onload = () => { if (token === loadToken) fitImage(); };
      image.src = link.href;
      caption.replaceChildren();
      const source = (link.dataset.captionId && document.getElementById(link.dataset.captionId))
        || link.closest('figure')?.querySelector('figcaption');
      if (source) {
        const copy = source.cloneNode(true);
        copy.removeAttribute('id');
        copy.querySelectorAll('[id]').forEach(el => el.removeAttribute('id'));
        caption.append(copy);
      }
      status.textContent = `${index + 1} / ${figures.length}`;
      stage.scrollTop = stage.scrollLeft = 0;
      if (image.complete) fitImage();
    }
    function openFigure(link, event, opener = link) {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      const gallery = galleryFor(link);
      figures = figureLinks.filter(candidate => galleryFor(candidate) === gallery);
      origin = opener;
      previousOverflow = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
      dialog.showModal();
      show(figures.indexOf(link));
      dialog.querySelector('[data-action="close"]').focus();
    }
    figureLinks.forEach(link => {
      link.addEventListener('click', event => openFigure(link, event));
      if (!link.closest('figure')) return;
      const actions = document.createElement('div');
      actions.className = 'figure-phone-actions';
      const enlarge = document.createElement('a');
      enlarge.href = link.href;
      enlarge.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 3H3v6m12-6h6v6M3 15v6h6m12-6v6h-6M3 3l7 7m11-7-7 7M3 21l7-7m11 7-7-7"/></svg><span>' + (de ? 'Vergrößern' : 'Enlarge') + '</span>';
      enlarge.setAttribute('aria-label', (de ? 'Vergrößern: ' : 'Enlarge: ') + (link.dataset.originalAlt || link.querySelector('img').alt));
      enlarge.addEventListener('click', event => openFigure(link, event, enlarge));
      const save = document.createElement('a');
      save.href = link.href;
      save.setAttribute('download', '');
      const png = /\.png$/i.test(new URL(link.href, document.baseURI).pathname);
      const saveLabel = de ? (png ? 'PNG speichern' : 'Bild speichern') : (png ? 'Save PNG' : 'Save image');
      save.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5"/></svg><span>' + saveLabel + '</span>';
      save.setAttribute('aria-label', saveLabel + ': ' + (link.dataset.originalAlt || link.querySelector('img').alt));
      actions.append(enlarge, save);
      link.insertAdjacentElement('afterend', actions);
    });
    dialog.addEventListener('click', event => {
      const action = event.target.closest('[data-action]')?.dataset.action;
      if (action === 'close') dialog.close();
      if (action === 'previous') show(index - 1);
      if (action === 'next') show(index + 1);
      if (action === 'in') { zoom = Math.min(8, zoom * 1.5); fitImage(); }
      if (action === 'out') { zoom = Math.max(1, zoom / 1.5); fitImage(); }
      if (action === 'fit') { zoom = 1; fitImage(); stage.scrollTop = stage.scrollLeft = 0; }
      if (event.target === dialog) {
        const rect = dialog.getBoundingClientRect();
        if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
      }
    });
    dialog.addEventListener('keydown', event => {
      if (event.key === 'ArrowRight' && zoom === 1) {event.preventDefault(); show(index + 1);}
      if (event.key === 'ArrowLeft' && zoom === 1) {event.preventDefault(); show(index - 1);}
      if (event.key === '+' || event.key === '=') {event.preventDefault(); zoom = Math.min(8, zoom * 1.5); fitImage();}
      if (event.key === '-') {event.preventDefault(); zoom = Math.max(1, zoom / 1.5); fitImage();}
    });
    dialog.addEventListener('close', () => {
      document.body.style.overflow = previousOverflow;
      // A gallery item can be navigated to while its disclosure is closed.
      origin?.focus();
    });
    new ResizeObserver(fitImage).observe(stage);
    window.addEventListener('resize', fitImage);
  }
  // Mark the current reading section without modifying URL or browser history.
  if (!root) return;
  const links = [...root.querySelectorAll('.case-nav a[href^="#"]')];
  const targets = links.map(link => document.getElementById(link.hash.slice(1))).filter(Boolean);
  let pending = false;
  function updateNavigation() {
    pending = false;
    let active = targets[0];
    for (const target of targets) if (target.getBoundingClientRect().top <= 160) active = target;
    for (const link of links) {
      if (active && link.hash === '#' + active.id) link.setAttribute('aria-current','location');
      else link.removeAttribute('aria-current');
    }
  }
  function revealTarget(hash) {
    const target = document.getElementById(hash.slice(1));
    if (target?.tagName === 'DETAILS') target.open = true;
    const child = target?.querySelector(':scope > details');
    if (child) child.open = true;
    for (let parent = target?.parentElement; parent && parent !== root; parent = parent.parentElement) if (parent.tagName === 'DETAILS') parent.open = true;
  }
  links.forEach(link => link.addEventListener('click', () => revealTarget(link.hash)));
  window.addEventListener('hashchange', () => revealTarget(location.hash));
  if (location.hash) revealTarget(location.hash);
  if (links.length) {
    window.addEventListener('scroll', () => {if (!pending) {pending = true; requestAnimationFrame(updateNavigation);}}, {passive:true});
    updateNavigation();
  }
})();
