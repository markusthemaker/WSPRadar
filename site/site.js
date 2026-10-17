document.documentElement.classList.add('js');
const toggle = document.querySelector('.nav-toggle');
const links = document.getElementById('nav-links');
if (toggle && links) {
  const media = matchMedia('(max-width:999px)');
  function resizeNavigation() {
    links.hidden = media.matches;
    toggle.setAttribute('aria-expanded', String(!links.hidden));
  }
  resizeNavigation();
  media.addEventListener('change', resizeNavigation);
  toggle.addEventListener('click', () => {
    links.hidden = !links.hidden;
    toggle.setAttribute('aria-expanded', String(!links.hidden));
  });
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
