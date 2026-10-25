const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '..', 'source', 'theme', 'scripts', 'demo-walkthrough.js'), 'utf8');

function fixture({walkthrough = false, documentation = false, dialogSupported = true} = {}) {
  let focused = null;
  const dialogs = [];
  class Element {
    constructor() {
      this.handlers = new Map();
      this.style = {};
      this.dataset = {};
      this.attributes = new Map();
      this.children = [];
      this.classList = {toggle() {}};
      this.offsetHeight = 30;
    }
    addEventListener(name, callback) { this.handlers.set(name, callback); }
    setAttribute(name, value) { this.attributes.set(name, value); }
    getAttribute(name) { return this.attributes.get(name) ?? null; }
    hasAttribute(name) { return this.attributes.has(name); }
    removeAttribute(name) { this.attributes.delete(name); }
    focus() { focused = this; }
    replaceChildren(...children) { this.children = children; }
    append(...children) { this.children.push(...children); }
    cloneNode() {
      const copy = new Element();
      copy.attributes = new Map(this.attributes);
      copy.textContent = this.textContent;
      copy.querySelectorAll = selector => { assert.equal(selector, '[id]'); return []; };
      return copy;
    }
    dispatch(name, event = {}) { this.handlers.get(name)?.(event); }
  }
  function gallery(kind) {
    const group = new Element();
    group.kind = kind;
    group.links = [];
    group.querySelectorAll = selector => {
      if (selector === 'a[href]') return group.links;
      if (selector === 'a[data-case-lightbox]') return group.links.filter(item => item.hasAttribute('data-case-lightbox'));
      if (selector === '.case-nav a[href^="#"]') return [];
      throw new Error(`Unexpected gallery selector: ${selector}`);
    };
    return group;
  }
  const main = gallery('main');
  function link(group, name, originalAlt, {marked = true, image = true, href, download = false} = {}) {
    const anchor = new Element();
    anchor.href = href || `https://example.test/originals/${name}.png`;
    anchor.setAttribute('href', anchor.href);
    if (marked) anchor.setAttribute('data-case-lightbox', '');
    if (download) anchor.setAttribute('download', '');
    anchor.dataset = {title: name, ...(originalAlt ? {originalAlt} : {})};
    anchor.querySelector = selector => {
      assert.equal(selector, 'img');
      return image ? {alt: `${name} thumbnail`} : null;
    };
    const figure = new Element();
    anchor.figureCaption = new Element();
    anchor.figureCaption.setAttribute('id', 'caption-' + name);
    anchor.figureCaption.textContent = name + ' scientific caption';
    figure.querySelector = selector => { assert.equal(selector, 'figcaption'); return anchor.figureCaption; };
    anchor.closest = selector => {
      const alternatives = selector.split(',').map(value => value.trim());
      if (alternatives.includes('figure')) return figure;
      if (alternatives.includes(group.kind)) return group;
      if (alternatives.includes('main')) return main;
      return null;
    };
    anchor.click = modifiers => {
      let prevented = false;
      anchor.dispatch('click', {preventDefault() { prevented = true; }, ...modifiers});
      return prevented;
    };
    group.links.push(anchor);
    if (group !== main) main.links.push(anchor);
    return anchor;
  }
  const first = documentation ? main : gallery(walkthrough ? '.case-study' : '.result-gallery');
  const second = gallery('.result-gallery');
  const firstLink = link(first, 'one', 'Scientific original one', {
    marked: !documentation, href: 'https://example.test/originals/one.PNG?view=full#figure',
  });
  const nextLink = link(first, 'two', undefined, {marked: !documentation});
  const otherLink = link(second, 'separate');
  const excluded = [
    link(main, 'paper', undefined, {marked: false, href: 'https://example.test/paper.pdf?image=.png'}),
    link(main, 'download', undefined, {download: true}),
    link(main, 'navigation', undefined, {marked: false, image: false}),
    link(main, 'article', undefined, {marked: false, href: 'https://example.test/article/'}),
  ];
  const body = {style: {overflow: 'auto'}, append(dialog) { dialogs.push(dialog); }};
  const document = {
    documentElement: {lang: 'en'}, baseURI: 'https://example.test/documentation/chapter/', body,
    querySelector(selector) { assert.equal(selector, '.case-study'); return walkthrough ? first : null; },
    querySelectorAll(selector) { assert.equal(selector, 'main a[href]', 'header/logo links stay outside the viewer'); return main.links; },
    getElementById() { return null; },
    createElement(tag) {
      assert.equal(tag, 'dialog');
      const dialog = new Element();
      const stage = new Element(), image = new Element(), title = new Element();
      const caption = new Element(), status = new Element(), head = new Element();
      const controls = Object.fromEntries(['previous', 'next', 'in', 'out', 'fit', 'close'].map(action => {
        const button = new Element();
        button.dataset.action = action;
        button.closest = () => button;
        return [action, button];
      }));
      stage.clientWidth = 900;
      stage.querySelector = () => image;
      image.naturalWidth = 1200;
      image.naturalHeight = 900;
      image.complete = true;
      dialog.querySelector = selector => {
        const elements = {'.case-dialog-stage': stage, 'h2': title, '.case-dialog-caption': caption,
          '.case-dialog-status': status, '.case-dialog-head': head};
        const action = selector.match(/^\[data-action="(.+)"\]$/)?.[1];
        return action ? controls[action] : elements[selector];
      };
      dialog.showModal = () => { dialog.open = true; };
      dialog.close = () => { dialog.open = false; dialog.dispatch('close'); };
      dialog.action = action => dialog.dispatch('click', {target: controls[action]});
      dialog.key = key => dialog.dispatch('keydown', {key, preventDefault() {}});
      Object.assign(dialog, {image, title, caption, status, controls, stage});
      return dialog;
    },
  };
  vm.runInNewContext(source, {
    document, URL,
    window: {innerHeight: 900, addEventListener() {}},
    location: {hash: ''},
    HTMLDialogElement: dialogSupported ? function HTMLDialogElement() {} : undefined,
    ResizeObserver: class { observe() {} },
    getComputedStyle: () => ({paddingLeft: '8', paddingRight: '8', paddingTop: '8', paddingBottom: '8'}),
  });
  return {dialogs, body, firstLink, nextLink, otherLink, excluded, focused: () => focused};
}

for (const mode of ['homepage', 'walkthrough', 'documentation']) {
  const page = fixture({walkthrough: mode === 'walkthrough', documentation: mode === 'documentation'});
  assert.equal(page.dialogs.length, 1, 'one dialog serves all galleries');
  const dialog = page.dialogs[0];
  assert.equal(dialog.image.src, undefined, 'no original image loads before opening');
  for (const link of page.excluded) {
    assert.equal(link.click(), false, 'PDFs, downloads and navigation keep their normal behavior');
  }
  assert.equal(dialog.image.src, undefined, 'excluded links do not load viewer images');
  for (const modifier of ['ctrlKey', 'metaKey', 'shiftKey', 'altKey']) {
    assert.equal(page.firstLink.click({[modifier]: true}), false, 'modified clicks keep normal link behavior');
    assert.equal(dialog.image.src, undefined);
  }
  assert.equal(page.firstLink.click(), true);
  assert.equal(dialog.image.src, page.firstLink.href);
  assert.equal(dialog.image.alt, 'Scientific original one', 'original metadata replaces the preview description');
  assert.equal(dialog.status.textContent, '1 / 2');
  if (mode === 'documentation') {
    assert.equal(page.firstLink.hasAttribute('data-case-lightbox'), false, 'ordinary figure links need no special marker');
    assert.equal(dialog.caption.children.length, 1);
    assert.equal(dialog.caption.children[0].textContent, page.firstLink.figureCaption.textContent);
    assert.equal(dialog.caption.children[0].hasAttribute('id'), false, 'caption cloning does not duplicate document IDs');
    assert.equal(page.firstLink.figureCaption.getAttribute('id'), 'caption-one', 'source caption remains intact');
  }
  assert.equal(page.body.style.overflow, 'hidden');
  assert.equal(page.focused(), dialog.controls.close);
  const fittedWidth = parseFloat(dialog.image.style.width);
  dialog.action('in');
  assert.ok(parseFloat(dialog.image.style.width) > fittedWidth);
  dialog.action('fit');
  assert.equal(parseFloat(dialog.image.style.width), fittedWidth);
  dialog.action('next');
  assert.equal(dialog.image.src, page.nextLink.href);
  assert.equal(dialog.image.alt, 'two thumbnail', 'existing walkthrough image alternatives remain the fallback');
  dialog.key('ArrowRight');
  assert.equal(dialog.image.src, page.firstLink.href, 'next wraps within the originating gallery');
  dialog.action('previous');
  assert.equal(dialog.image.src, page.nextLink.href);
  dialog.action('close');
  assert.equal(page.body.style.overflow, 'auto');
  assert.equal(page.focused(), page.firstLink, 'closing returns focus to the activating link');
  page.otherLink.click();
  assert.equal(dialog.status.textContent, '1 / 1');
  dialog.action('next');
  assert.equal(dialog.image.src, page.otherLink.href, 'a second gallery cannot navigate into the first');
}
const fallback = fixture({documentation: true, dialogSupported: false});
assert.equal(fallback.dialogs.length, 0);
assert.equal(fallback.firstLink.click(), false, 'unsupported dialogs retain direct original-image links');
console.log('Figure viewer checks passed: homepage/demo/documentation reuse, exclusions, captions, gallery isolation, originals, zoom, focus, modifiers, and fallback.');
