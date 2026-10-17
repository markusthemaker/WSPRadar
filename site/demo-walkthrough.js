/* Progressive enhancement: image links still open their originals without JS. */
(() => {
  const root = document.querySelector('.case-study');
  if (!root) return;
  const de = document.documentElement.lang === 'de';
  const labels = de ? {close:'Schließen',previous:'Vorherige Abbildung',next:'Nächste Abbildung',in:'Vergrößern',out:'Verkleinern',fit:'Einpassen',title:'Abbildung',loading:'Abbildung wird geladen'} : {close:'Close',previous:'Previous figure',next:'Next figure',in:'Zoom in',out:'Zoom out',fit:'Fit',title:'Figure',loading:'Loading figure'};
  const figures = [...root.querySelectorAll('a[data-case-lightbox]')];
  if (figures.length && typeof HTMLDialogElement !== 'undefined') {
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
    let index = 0, zoom = 1, origin = null, previousOverflow = '', loadToken = 0;
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
      title.textContent = link.dataset.title || original.alt || labels.title;
      image.alt = original.alt;
      image.classList.toggle('case-image-inverted', link.dataset.invertColors === 'true');
      image.style.filter = link.dataset.imageFilter || '';
      image.style.width = '1px';
      const token = ++loadToken;
      image.onload = () => { if (token === loadToken) fitImage(); };
      image.src = link.href;
      caption.replaceChildren();
      const source = document.getElementById(link.dataset.captionId);
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
    figures.forEach((link,i) => link.addEventListener('click', event => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      origin = link;
      previousOverflow = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
      dialog.showModal();
      show(i);
      dialog.querySelector('[data-action="close"]').focus();
    }));
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
  window.addEventListener('scroll', () => {if (!pending) {pending = true; requestAnimationFrame(updateNavigation);}}, {passive:true});
  updateNavigation();
})();
