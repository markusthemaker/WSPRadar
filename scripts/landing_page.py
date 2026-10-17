"""Website-owned landing presentation; scientific media remain imported assets."""

from html import escape

try:
    from .demo_walkthrough import demo_launch_url
except ImportError:
    from demo_walkthrough import demo_launch_url


def render_evidence_crops(builder, item, crop, lang):
    """Show reviewed source-pixel windows without modifying the original figure."""
    width, height = item["width"], item["height"]
    if crop.get("source_size") != [width, height]:
        raise ValueError("Landing crop source dimensions changed; review the crop")
    source = builder.manifest["files"][item["asset_path"]]
    if crop.get("source_sha256") != source["sha256"]:
        raise ValueError("Landing crop source hash changed; review the crop")
    layout = crop.get("layout")
    if layout not in ("rows", "columns"):
        raise ValueError("Landing crop layout must be rows or columns")
    regions = crop.get("regions")
    if not isinstance(regions, list) or not regions:
        raise ValueError("Landing crop regions must be a nonempty list")
    parts = ['<span class="result-crops result-crops-' + layout + '">']
    for region in regions:
        rect = region.get("rect")
        if not isinstance(rect, list) or len(rect) != 4 or any(type(value) is not int for value in rect):
            raise ValueError("Landing crop rectangle must contain four integers")
        x, y, crop_width, crop_height = rect
        if min(x, y) < 0 or min(crop_width, crop_height) <= 0 or x + crop_width > width or y + crop_height > height:
            raise ValueError("Landing crop rectangle is outside the source figure")
        alternatives = region.get("alt", {})
        if set(alternatives) != {"en", "de"} or any(not isinstance(value, str) or not value.strip() for value in alternatives.values()):
            raise ValueError("Landing crop requires English and German alternative text")
        weight = crop_height if layout == "rows" else crop_width
        style = f'--crop-weight:{weight};--crop-image-width:{width / crop_width * 100:.6f}%;--crop-image-height:{height / crop_height * 100:.6f}%;--crop-left:{-x / crop_width * 100:.6f}%;--crop-top:{-y / crop_height * 100:.6f}%'
        parts.append('<span class="result-crop" style="' + style + '"><img src="/content/' + escape(item["asset_path"], quote=True) + '" width="' + str(width) + '" height="' + str(height) + '" loading="lazy" decoding="async" alt="' + escape(alternatives[lang], quote=True) + '"></span>')
    parts.append('</span>')
    return ''.join(parts)


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
    parts.append('<article class="why-panel why-repeated"><div class="why-panel-content"><h3>' + text("repeated_title") + '</h3><p class="why-subtitle">' + text("repeated_subtitle") + '</p><div class="why-network"><figure><picture><source type="image/webp" srcset="' + escape(srcset, quote=True) + '" sizes="(max-width: 580px) min(240px, calc(100vw - 92px)), (max-width: 860px) min(360px, calc(44.2vw - 43px)), (max-width: 1280px) min(360px, calc(28.7vw - 40px)), 330px"><img src="/assets/landing/' + escape(fallback["path"], quote=True) + '" width="' + str(fallback["width"]) + '" height="' + str(fallback["height"]) + '" alt="" aria-hidden="true" loading="lazy" decoding="async"></picture></figure><ul class="why-benefits">')
    for benefit in content["benefits"]:
        parts.append('<li>' + icon(benefit["icon"]) + '<div><strong>' + escape(benefit["title"]) + '</strong><span>' + escape(benefit["body"]) + '</span></div></li>')
    parts.append('</ul></div><div class="why-method"><ol class="why-steps" aria-label="' + text("method_title") + '">')
    for number, step in enumerate(content["steps"], 1):
        parts.append('<li><div class="why-step-heading"><span class="why-step-number" aria-hidden="true">' + str(number) + '.</span><h4>' + escape(step["title"]) + '</h4></div><p>' + escape(step["body"]) + '</p>')
        if number == 1:
            parts.append('<table class="why-pairs"><thead><tr><th scope="col" aria-label="' + text("station_label") + '">#</th><th scope="col">' + text("reference_label") + '</th><th scope="col">' + text("target_label") + '</th><th scope="col">' + text("delta_label") + '</th></tr></thead><tbody>')
            for station, (reference, target, delta) in enumerate((("−21", "−18", "+3"), ("−14", "−10", "+4"), ("−26", "−24", "+2")), 1):
                parts.append('<tr><th scope="row">#' + str(station) + '</th><td>' + reference + ' dB</td><td>' + target + ' dB</td><td>' + delta + ' dB</td></tr>')
            parts.append('</tbody></table>')
        elif number == 2:
            parts.append('<div class="why-station-medians" aria-hidden="true">')
            for station, points in enumerate(((18, 32, 49, 63, 82), (29, 47, 65, 78, 88), (14, 27, 39, 56, 75)), 1):
                parts.append('<div><span>#' + str(station) + '</span><span class="why-dot-row">' + ''.join('<i class="' + ('median' if index == 2 else 'observation') + '" style="--point:' + str(point) + '%"></i>' for index, point in enumerate(points)) + '</span></div>')
            parts.append('</div>')
        else:
            parts.append('<div class="why-summary-dots" aria-hidden="true"><span></span><span class="median"></span><span></span></div>')
        parts.append('</li>')
    parts.append('</ol></div></div><div class="why-takeaway"><span aria-hidden="true">✓</span><div><strong>' + text("conclusion_title") + '</strong><p>' + text("conclusion_body") + '</p></div></div></article></div></section>')
    return ''.join(parts)


def render_landing(builder, lang, button, route, app_url):
    content = builder.landing[lang]
    selected = builder.landing["featured_demo"]
    demo = next(item for item in builder.demos if item["id"] == selected["id"])
    demo_url = route(lang, "demos/" + demo["id"] + "/")
    demo_config = builder.demo_walkthroughs["demos"][demo["id"]]
    run_url = demo_launch_url(demo_config)
    media = {item["key"]: item for item in builder.figures + builder.screenshots}
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
    chunks.append(render_why_section(content["why"], builder.landing_assets, icon))
    chunks.append('<section id="analysis-choices"><div class="section-heading"><h2>' + text("modes_title") + '</h2><a href="' + builder.anchors[lang]['sec-2-2'] + '#sec-2-2' + '">' + text("modes_help") + ' →</a></div><div class="analysis-grid">')
    for mode in content["modes"]:
        chunks.append('<article class="analysis-card">' + icon(mode["icon"]) + '<h3>' + escape(mode["title"]) + '</h3><p class="operator-question">' + escape(mode["question"]) + '</p><p class="muted">' + escape(mode["body"]) + '</p></article>')
    chunks.append('</div></section><section id="real-example" class="real-example"><div class="section-heading"><h2>' + text("example_title") + '</h2><a href="' + route(lang, 'demos/') + '">' + escape(builder.copy[lang]["browse_demos"]) + ' →</a></div><p class="example-lead"><strong>' + text("example_intro") + '</strong></p><p class="example-meta">' + text("example_meta") + '</p>')
    chunks.append('<div class="example-showcase"><div class="example-context"><p class="eyebrow">' + text("example_tag") + '</p><h3>' + text("example_question") + '</h3><div class="measured-result"><strong>' + text("result") + '</strong><div><p class="result-label"><strong>' + text("result_label") + '</strong></p><p class="result-detail">' + ''.join('<span>' + escape(line) + '</span>' for line in content["result_detail"]) + '</p></div></div><div class="actions">' + button(content['example_link'] + ' →', demo_url) + button(content['try_this'], run_url, secondary=True, external=True) + '</div><p class="example-ready"><em>' + text("example_ready") + '</em></p></div><div class="result-gallery">')
    for index, key in enumerate(selected["media_keys"]):
        item = media[key]
        if item["demo_id"] != demo["id"]:
            raise ValueError("Landing media must belong to the featured demo")
        url = '/content/' + item['asset_path']
        label = builder.copy[lang]['full_size'] + ': ' + content['image_titles'][index]
        crops = render_evidence_crops(builder, item, selected['media_crops'][key], lang)
        caption = content['image_captions'][index]
        chunks.append('<figure class="result-preview"><div class="result-card-heading">' + icon(selected['media_icons'][index]) + '<h4>' + escape(content['image_titles'][index]) + '</h4></div><a href="' + escape(url, quote=True) + '" aria-label="' + escape(label, quote=True) + '" target="_blank" rel="noopener noreferrer">' + crops + '</a><figcaption><strong>' + escape(caption['lead']) + '</strong> ' + escape(caption['body']) + '</figcaption></figure>')
    chunks += ['</div></div></section>',
               '<section class="get-started-section" id="get-started"><div class="section-heading"><h2>' + text('get_started') + '</h2></div><div class="get-started"><div class="start-heading"><p class="curiosity-callout"><small>' + text('curiosity_context') + '</small>' + ''.join('<span>' + escape(line) + '</span>' for line in content['curiosity_lines']) + '</p></div><ol class="start-steps">']
    for number, step in enumerate(content['start_steps'], 1):
        chunks.append('<li class="start-step"><span class="start-number" aria-hidden="true">' + str(number) + '</span><div><h3>' + escape(step['title']) + '</h3><p>' + escape(step['body']) + '</p></div></li>')
    chunks += ['</ol><div class="start-grid"><article><details class="start-description"><summary>' + text('demo_title') + '</summary><p>' + text('demo_body') + '</p></details>' + button(builder.copy[lang]['browse_demos'] + ' →', route(lang, 'demos/')) + '</article><article><details class="start-description"><summary>' + text('own_title') + '</summary><p>' + text('own_body') + '</p></details>' + button(content['own_link'], app_url, secondary=True, external=True) + '</article></div></div></section>',
               '<section class="setup-intro"><h2>' + text('setup_title') + '</h2><p>' + text('setup_body') + '</p><div class="guide-links"><a href="' + route(lang, 'documentation/') + '">' + escape(builder.copy[lang]['docs']) + ' →</a><a href="' + route(lang, 'community/') + '">' + escape(builder.copy[lang]['community']) + ' →</a></div></section></div>']
    return ''.join(chunks)
