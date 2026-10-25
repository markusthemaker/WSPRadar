/* Preserve article disclosures while the browser prepares a printed copy. */
(() => {
  let savedState = null;

  function preparePrint() {
    // Print media and browser preview can dispatch beforeprint more than once.
    if (savedState) return;
    const main = document.getElementById('main');
    if (!main) return;

    const details = [...main.querySelectorAll('details')].map(element => ({
      element,
      open: element.open,
      name: element.getAttribute('name'),
    }));
    const images = [...main.querySelectorAll('img[loading="lazy"]')];
    savedState = {details, images};

    // Named details groups normally permit only one open member. Suspend that
    // grouping before opening every disclosure, including nested disclosures.
    for (const {element} of details) element.removeAttribute('name');
    for (const {element} of details) element.open = true;

    // Start loading figures below the viewport before printing. Browsers do not
    // await asynchronous work from beforeprint; this is not a decode guarantee.
    for (const image of images) image.setAttribute('loading', 'eager');
  }

  function restorePage() {
    if (!savedState) return;
    const {details, images} = savedState;
    // Restore open states while exclusive grouping remains suspended.
    for (const {element, open} of details) element.open = open;
    for (const {element, name} of details) {
      if (name === null) element.removeAttribute('name');
      else element.setAttribute('name', name);
    }
    for (const image of images) image.setAttribute('loading', 'lazy');
    savedState = null;
  }

  window.addEventListener('beforeprint', preparePrint);
  window.addEventListener('afterprint', restorePage);
})();
