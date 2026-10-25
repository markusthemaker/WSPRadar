"""Render website-owned demo discovery without changing canonical demo records."""
from html import escape
from string import Template


def render_demos_index(content, published_demos, assets, template_path,
                       lang, route):
    cards = content['cards']
    identities = [card['id'] for card in cards]
    published = {demo['id'] for demo in published_demos}
    if len(set(identities)) != len(identities) or set(identities) != published:
        raise ValueError('Demo discovery cards must cover each published demo exactly once')
    modes = {mode['id']: mode for mode in content['modes']}
    if len(modes) != len(content['modes']):
        raise ValueError('Duplicate demo discovery mode')
    text = content['text']

    def icon(name, size=26, css=''):
        path = assets['icons'][name]
        if path not in assets['publish_files']:
            raise ValueError('Unpublished demo discovery icon: ' + name)
        return (f'<img class="brand-icon {escape(css)}" src="/assets/landing/{escape(path)}" '
                f'width="{size}" height="{size}" alt="" aria-hidden="true">')

    def count_label(count):
        return str(count) + ' ' + text['demo_singular' if count == 1 else 'demo_plural']

    rendered = []
    for card in cards:
        identity = card['id']
        if not card['modes'] or len(set(card['modes'])) != len(card['modes']) or set(card['modes']) - modes.keys():
            raise ValueError('Invalid demo discovery modes: ' + identity)
        labels = ''.join('<span class="mode-label">' + icon(mode, 22) + escape(modes[mode]['label']) + '</span>' for mode in card['modes'])
        recommended = card.get('recommended', False)
        context = ('<div class="context recommended"><span aria-hidden="true">✓</span> ' + escape(text['recommended']) + '</div>'
                   if recommended else '<div class="context">' + escape(card['context']) + '</div>')
        learning = ''.join('<li>' + escape(item) + '</li>' for item in card['learn'])
        title = escape(card['title'])
        destination = route(lang, 'demos/' + identity + '/')
        subtitle = ('<p class="card-subtitle">' + escape(card['subtitle']) + '</p>'
                    if card.get('subtitle') else '')
        if card.get('thumbnail'):
            thumbnail = card['thumbnail']
            for item in thumbnail['images']:
                if item['path'] not in assets['publish_files']:
                    raise ValueError('Unpublished demo discovery thumbnail: ' + identity)
            fallback = max(thumbnail['images'], key=lambda item: item['width'])
            srcset = ', '.join('/assets/landing/' + item['path'] + ' ' + str(item['width']) + 'w'
                               for item in thumbnail['images'])
            preview = (
                f'<figure class="thumbnail evidence-thumbnail"><a href="{escape(thumbnail["original"], quote=True)}" '
                f'target="_blank" rel="noopener noreferrer" aria-label="{escape(text["open_original"] + ": " + card["title"], quote=True)}">'
                f'<img src="/assets/landing/{escape(fallback["path"], quote=True)}" srcset="{escape(srcset, quote=True)}" '
                f'sizes="(max-width:590px) calc(100vw - 54px), (max-width:1100px) calc((100vw - 100px)/2), 390px" '
                f'width="{fallback["width"]}" height="{fallback["height"]}" alt="{escape(card["thumb_alt"], quote=True)}" '
                f'loading="lazy" decoding="async"></a></figure>')
        else:
            preview = (
                f'<figure class="thumbnail" aria-label="{escape(text["placeholder_accessible"] + " " + card["thumb_title"], quote=True)}">'
                f'<span class="placeholder-label">{escape(text["placeholder"])}</span>{icon(card["thumb_icon"], 44, "thumb-icon")}'
                f'<figcaption><strong>{escape(card["thumb_title"])}</strong><span>{escape(card["thumb_text"])}</span></figcaption></figure>')
        rendered.append(
            f'<article class="demo-card {"first-demo" if recommended else ""}" data-modes="{escape(" ".join(card["modes"]))}" '
            f'id="demo-{escape(identity)}" aria-labelledby="title-{escape(identity)}">'
            f'<div class="card-heading"><div class="mode-row">{labels}<span class="band">{escape(card["band"])}</span></div>{context}'
            f'<h3 id="title-{escape(identity)}">{title}</h3>{subtitle}<p class="station-line">{escape(card["stations"])}</p></div>'
            f'{preview}'
            f'<div class="card-body"><p class="demo-question">{escape(card["question"])}</p><h4>{escape(text["learn"])}</h4><ul class="learn-list">{learning}</ul></div>'
            f'<div class="card-footer"><span class="topic-label">{escape(card["context"] if recommended else card["topic"])}</span>'
            f'<a class="demo-link" href="{escape(destination, quote=True)}">{escape(text["open_demo"])} <span aria-hidden="true">→</span>'
            f'<span class="sr-only">: {title}</span></a></div></article>')

    values = {key: escape(value, quote=True) for key, value in text.items()}
    # These two authored text blocks intentionally contain semantic inline HTML.
    for key in ('title', 'mode_definition'):
        values[key] = text[key]
    values.update(cards='\n'.join(rendered), total_label=escape(count_label(len(cards))),
                  default_description=escape(text['collection_description'], quote=True),
                  documentation_url=route(lang, 'documentation/'))
    for name, size in (('wspr-database', 24), ('try-demo', 26), ('evidence-chart', 26), ('analysis-laptop', 48)):
        values[name.replace('-', '_')] = icon(name, size)
    for identity, mode in modes.items():
        count = sum(identity in card['modes'] for card in cards)
        available = count > 0
        tag = 'button' if available else 'div'
        attrs = (f'type="button" data-filter="{escape(identity)}" data-label="{escape(mode["label"], quote=True)}" '
                 f'data-description="{escape(mode["description"], quote=True)}" aria-pressed="false" aria-controls="demo-grid"'
                 if available else 'aria-disabled="true"')
        label = count_label(count) if available else text['unavailable']
        values[identity.replace('-', '_')] = (
            f'<{tag} class="use-case {"" if available else "unavailable"}" {attrs}>'
            f'<span class="use-icon">{icon(identity, 34)}<span class="selection-indicator" aria-hidden="true">✓</span></span>'
            f'<strong>{escape(mode["label"])}</strong><span class="use-question">{escape(mode["question"])}</span>'
            f'<span class="use-count">{escape(label)}<span aria-hidden="true">{"→" if available else "—"}</span></span></{tag}>')
    return Template(template_path.read_text(encoding='utf-8')).substitute(values)
