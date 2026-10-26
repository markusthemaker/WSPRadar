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
if (index && matchMedia('(max-width:759px)').matches) index.open = false;
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
