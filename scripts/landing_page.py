"""Website-owned landing presentation using reviewed scientific media."""

from html import escape

try:
    from .demo_walkthrough import demo_launch_url
except ImportError:
    from demo_walkthrough import demo_launch_url


def render_evidence_image(item, lang):
    """Show a reviewed small preview while retaining the separate original."""
    preview = item.get("preview")
    source = preview["source"] if preview else item["native"]
    images = sorted((preview or item)["images"], key=lambda image: image["width"])
    if not images:
        raise ValueError("Landing evidence requires browser derivatives")
    for image in images:
        if image["width"] > source["width"] or abs(image["height"] - round(image["width"] * source["height"] / source["width"])) > 1:
            raise ValueError("Landing evidence derivatives must preserve source proportions without upscaling")
    fallback = images[0]
    srcset = ", ".join(image["path"] + " " + str(image["width"]) + "w" for image in images)
    sizes = "(max-width: 580px) calc(100vw - 90px), (max-width: 600px) calc(93vw - 76.64px), (max-width: 800px) calc(46.5vw - 63.32px), (max-width: 1280px) calc(31vw - 58.88px), 337.92px"
    return ('<img class="result-image" src="' + escape(fallback["path"], quote=True) + '" srcset="' + escape(srcset, quote=True) + '" sizes="' + sizes + '" width="' + str(fallback["width"]) + '" height="' + str(fallback["height"]) + '" loading="lazy" decoding="async" alt="' + escape((preview or item)["alt"][lang], quote=True) + '">')


def render_why_section(content, assets, icon):
    """Render the illustrative comparison separately from measured demo evidence."""
    text = lambda key: escape(content[key])
    network = assets["network"]
    fallback = network["fallback"]
    srcset = ", ".join("/assets/landing/" + item["path"] + " " + str(item["width"]) + "w" for item in network["images"])
    parts = [
        '<section class="why-section" id="why-wspradar" aria-labelledby="why-title">',
        '<div class="section-heading"><h2 id="why-title">' + text("title") + '</h2></div>',
        '<p class="why-question">' + text("question") + '</p><p class="why-intro">' + text("intro") + '</p>',
        '<div class="why-comparison"><article class="why-panel why-quick"><div class="why-panel-content"><h3>' + text("quick_title") + '</h3><p class="why-subtitle">' + text("quick_subtitle") + '</p>',
        '<div class="why-setups">',
    ]
    for key, value, css in (("target_label", "−17 dB", "target"), ("reference_label", "−21 dB", "reference")):
        parts.append('<div class="why-setup ' + css + '"><h4>' + text(key) + '</h4><div class="why-radio-path" aria-hidden="true">' + icon("tx-station") + '<span class="why-radio-arrow">→</span>' + icon("rx-station") + '</div><p class="why-snr"><span>SNR</span><strong>' + value + '</strong></p></div>')
    parts.append('</div><p class="why-factors-title">' + text("factors_title") + '</p><ul class="why-factors">')
    for factor in content["factors"]:
        parts.append('<li>' + icon(factor["icon"]) + '<span>' + escape(factor["label"]) + '</span></li>')
    parts.append('</ul></div><div class="why-caution"><strong>' + text("caution_title") + '</strong><p>' + text("caution_body") + '</p></div></article>')
    parts.append('<article class="why-panel why-repeated"><div class="why-panel-content"><h3>' + text("repeated_title") + '</h3><p class="why-subtitle">' + text("repeated_subtitle") + '</p><div class="why-network"><figure><picture><source type="image/webp" srcset="' + escape(srcset, quote=True) + '" sizes="(max-width: 580px) min(270px, 65vw), (max-width: 860px) min(430px, 65vw), 430px"><img src="/assets/landing/' + escape(fallback["path"], quote=True) + '" width="' + str(fallback["width"]) + '" height="' + str(fallback["height"]) + '" alt="" aria-hidden="true" loading="lazy" decoding="async"></picture></figure><ul class="why-benefits">')
    for benefit in content["benefits"]:
        parts.append('<li>' + icon(benefit["icon"]) + '<div><strong>' + escape(benefit["title"]) + '</strong><span>' + escape(benefit["body"]) + '</span></div></li>')
    parts.append('</ul></div><div class="why-method">')
    if content.get("decode_method"):
        parts.append('<h4 class="method-title">' + icon("signal-quality") + text("method_title") + '</h4>')
    parts.append('<ol class="why-steps" aria-label="' + text("method_title") + '">')
    for number, step in enumerate(content["steps"], 1):
        parts.append('<li><div class="why-step-heading"><span class="why-step-number" aria-hidden="true">' + str(number) + '.</span><h4>' + escape(step["title"]) + '</h4></div><p>' + escape(step["body"]) + '</p>')
        parts.append('</li>')
    parts.append('</ol></div>')
    if content.get("decode_method"):
        method = content["decode_method"]
        parts.append('<div class="why-method decode-method"><h4 class="method-title">' + icon("decoding-advantage") + escape(method["title"]) + '</h4><ol class="why-steps" aria-label="' + escape(method["title"], quote=True) + '">')
        for number, step in enumerate(method["steps"], 1):
            parts.append('<li><div class="why-step-heading"><span class="why-step-number" aria-hidden="true">' + str(number) + '.</span><h4>' + escape(step["title"]) + '</h4></div><p>' + escape(step["body"]) + '</p></li>')
        parts.append('</ol></div>')
    parts.append('</div><div class="why-takeaway"><span aria-hidden="true">✓</span><div><strong>' + text("conclusion_title") + '</strong><p>' + text("conclusion_body") + '</p></div></div></article></div></section>')
    return ''.join(parts)


def render_analysis_choices(content, family_modes, icon, help_url):
    """Group configured analysis choices when the locale supplies family copy."""
    parts = ['<section id="analysis-choices"><div class="section-heading"><h2>' + escape(content["modes_title"]) + '</h2><a href="' + help_url + '">' + escape(content["modes_help"]) + ' →</a></div>']

    def cards(indices, heading):
        rendered = ['<div class="analysis-grid">']
        for index in indices:
            mode = content["modes"][index]
            level = mode.get("heading_level", int(heading[1]))
            emphasis = mode.get("emphasize_question", False)
            if type(level) is not int or level not in (3, 4) or type(emphasis) is not bool:
                raise ValueError("Analysis card requires heading_level 3 or 4 and boolean emphasize_question")
            card_heading = "h" + str(level)
            question = escape(mode["question"])
            if emphasis:
                question = "<strong>" + question + "</strong>"
            rendered.append('<article class="analysis-card">' + icon(mode["icon"]) + '<' + card_heading + '>' + escape(mode["title"]) + '</' + card_heading + '><p class="operator-question">' + question + '</p><p class="muted">' + escape(mode["body"]) + '</p></article>')
        return ''.join(rendered) + '</div>'

    families = content.get("analysis_families")
    if families:
        indices = [index for key in families for index in family_modes[key]]
        if sorted(indices) != list(range(len(content["modes"]))):
            raise ValueError("Analysis families must select every mode exactly once")
        parts.append('<div class="analysis-families">')
        for key, family in families.items():
            parts.append('<div class="analysis-family"><div class="analysis-family-intro"><p class="eyebrow">' + escape(family["label"]) + '</p><h3>' + escape(family["title"]) + '</h3><p>' + escape(family["body"]) + '</p></div>' + cards(family_modes[key], "h4") + '</div>')
        parts.append('</div>')
    else:
        parts.append(cards(range(len(content["modes"])), "h3"))
    return ''.join(parts) + '</section>'


def render_operating_note(content, icon):
    """Render the operating prerequisites after the getting-started steps."""
    note = content.get("operating_note")
    if not note:
        return ''
    return '<aside class="operating-note" aria-labelledby="operating-note-title">' + icon("operating-window") + '<div><h3 id="operating-note-title">' + escape(note["title"]) + '</h3><p><strong>' + escape(note["intro"]) + '</strong></p><ul><li>' + escape(note["rx"]) + '</li><li>' + escape(note["tx"]) + '</li></ul><p>' + escape(note["detail"]) + '</p></div></aside>'


def render_landing(builder, lang, button, route, app_url):
    content = builder.landing[lang]
    selected = builder.landing["featured_demo"]
    demo = next(item for item in builder.published_demos if item["id"] == selected["id"])
    demo_url = route(lang, "demos/" + demo["id"] + "/")
    run_url = demo_launch_url(demo)
    text = lambda key: escape(content[key])

    def icon(name, css=""):
        path = builder.landing_assets["icons"][name]
        if isinstance(path, dict):
            path = path["path"]
        return '<img class="landing-icon ' + css + '" src="/assets/landing/' + escape(path, quote=True) + '" width="64" height="64" alt="" aria-hidden="true" loading="lazy">'

    chunks = ['<div class="landing">',
              '<section class="what-section" id="how-it-works"><div class="section-heading"><h2>' + text("what_title") + '</h2></div><div class="how-panel"><div class="what-copy"><p>' + content["what_body"] + '</p><a class="text-link" href="' + builder.anchors[lang]['sec-2-1'] + '#sec-2-1' + '">' + text("basics") + ' →</a></div>',
              '<div class="how-visual"><h3 class="flow-heading">' + text("how_title") + '</h3><ol class="signal-flow">']
    for number, step in enumerate(content["flow"]):
        chunks.append('<li class="flow-step">' + icon(step["icon"]) + '<h4>' + escape(step["title"]) + '</h4><p>' + escape(step["body"]) + '</p>')
        if step["connection"]:
            chunks.append('<span class="flow-connection ' + ('radio' if number == 0 else 'data') + '"><span>' + escape(step["connection"]) + '</span><span class="flow-arrow" aria-hidden="true">→</span></span>')
        chunks.append('</li>')
    chunks.append('</ol></div></div></section>')
    choices = render_analysis_choices(content, builder.landing.get("analysis_family_modes", {}), icon, builder.anchors[lang]['sec-2-2'] + '#sec-2-2')
    if content.get("analysis_families"):
        chunks.append(choices)
    chunks.append(render_why_section(content["why"], builder.landing_assets, icon))
    if not content.get("analysis_families"):
        chunks.append(choices)
    example_meta = builder.md(content["example_meta"], lang).replace('<p>', '<p class="example-meta">', 1)
    chunks.append('<section id="real-example" class="real-example"><div class="section-heading"><h2>' + text("example_title") + '</h2><a href="' + route(lang, 'demos/') + '">' + escape(builder.copy[lang]["browse_demos"]) + ' →</a></div><p class="example-lead"><strong>' + text("example_intro") + '</strong></p>' + example_meta)
    chunks.append('<div class="example-showcase"><div class="example-context"><p class="eyebrow">' + text("example_tag") + '</p><h3>' + text("example_question") + '</h3><div class="demo-metrics"><div class="demo-metric measured-result"><strong>' + text("result") + '</strong><p class="result-label">' + text("result_label") + '</p><p class="result-detail">' + ''.join('<span>' + escape(line) + '</span>' for line in content["result_detail"]) + '</p></div>')
    for metric in content.get("demo_metrics", []):
        chunks.append('<div class="demo-metric"><strong>' + escape(metric["value"]) + '</strong><p class="result-label">' + escape(metric["label"]) + '</p><p class="result-detail">' + escape(metric["detail"]) + '<span>' + text("demo_metric_context") + '</span></p></div>')
    chunks.append('</div>')
    for key in ("demo_scope", "demo_balance"):
        if content.get(key):
            chunks.append('<p class="' + key.replace("_", "-") + '">' + text(key) + '</p>')
    chunks.append('<div class="actions">' + button(content['example_link'] + ' →', demo_url) + button(content['try_this'], run_url, secondary=True, external=True) + '</div><p class="example-ready">' + text("example_ready") + '</p></div></div><div class="result-gallery">')
    cards = selected["cards"]
    keys = [card["media_key"] for card in cards]
    if len(keys) != len(set(keys)):
        raise ValueError("Landing evidence cards must select unique media keys")
    for card in cards:
        key = card["media_key"]
        item = builder.landing_assets.get("evidence", {}).get(key)
        if item is None:
            raise ValueError("Unknown landing evidence media key: " + key)
        if item["demo_id"] != demo["id"]:
            raise ValueError("Landing media must belong to the featured demo")
        if lang not in card["locales"]:
            continue
        selection = card["copy"]
        if selection["kind"] == "existing":
            index = selection["index"]
            title = content["image_titles"][index]
            caption = content["image_captions"][index]
        elif selection["kind"] == "added":
            added = next(view for view in content["demo_added_views"] if view["id"] == selection["id"])
            title, caption = added["title"], added
        else:
            raise ValueError("Unknown landing evidence copy selection")
        label = builder.copy[lang]['full_size'] + ': ' + card['detail_title'][lang]
        image = render_evidence_image(item, lang)
        caption_id = "caption-" + key
        note = '<p class="result-preview-note">' + escape(item['preview']['note'][lang]) + '</p>' if item.get('preview') else ''
        chunks.append('<figure class="result-preview" data-media-key="' + escape(key, quote=True) + '"><div class="result-card-heading">' + icon(card['icon']) + '<div><h4>' + escape(title) + '</h4><p class="result-subtitle">' + escape(card['subtitle'][lang]) + '</p></div></div><div class="result-media"><a href="' + escape(item["native"]["path"], quote=True) + '" aria-label="' + escape(label, quote=True) + '" title="' + escape(card['detail_title'][lang], quote=True) + '" data-case-lightbox data-title="' + escape(card['detail_title'][lang], quote=True) + '" data-caption-id="' + escape(caption_id, quote=True) + '" data-original-alt="' + escape(item['alt'][lang], quote=True) + '" target="_blank" rel="noopener noreferrer">' + image + '</a>' + note + '</div><figcaption id="' + escape(caption_id, quote=True) + '"><strong>' + escape(caption['lead']) + '</strong> ' + escape(caption['body']) + '</figcaption></figure>')
    chunks += ['</div></section>',
               '<section class="get-started-section" id="get-started"><div class="section-heading"><h2>' + text('get_started') + '</h2></div><div class="get-started"><div class="start-heading"><p class="curiosity-callout"><small>' + text('curiosity_context') + '</small>' + ''.join('<span>' + escape(line) + '</span>' for line in content['curiosity_lines']) + '</p></div><ol class="start-steps">']
    for number, step in enumerate(content['start_steps'], 1):
        chunks.append('<li class="start-step"><span class="start-number" aria-hidden="true">' + str(number) + '</span><div><h3>' + escape(step['title']) + '</h3><p>' + escape(step['body']) + '</p></div></li>')
    chunks += ['</ol><div class="start-grid"><article><details class="start-description"><summary>' + text('demo_title') + '</summary><p>' + text('demo_body') + '</p></details>' + button(builder.copy[lang]['browse_demos'] + ' →', route(lang, 'demos/')) + '</article><article><details class="start-description"><summary>' + text('own_title') + '</summary><p>' + text('own_body') + '</p></details>' + ('<p class="own-benchmark-note">' + text('own_benchmark_note') + '</p>' if content.get('own_benchmark_note') else '') + button(content['own_link'], app_url, secondary=True, external=True) + '</article></div></div></section>',
               render_operating_note(content, icon),
               '<section class="setup-intro"><h2>' + text('setup_title') + '</h2><p>' + text('setup_body') + '</p><div class="guide-links"><a href="' + route(lang, 'documentation/') + '">' + escape(builder.copy[lang]['docs']) + ' →</a><a href="' + route(lang, 'community/') + '">' + escape(builder.copy[lang]['community']) + ' →</a></div></section></div>']
    return ''.join(chunks)
