# Editing the demo walkthroughs

All seven demos use the shared illustrated walkthrough layout in English and
German. Their editable website text lives here as ordinary UTF-8 Markdown. Work
offline in any text editor; no connected radio, running Streamlit application,
or WSPR download is required.

Demo #4 uses the supplied calibration walkthrough with three evidence steps.
Its earlier bilingual narrative and the supplied draft are retained in `source/`;
the complete imported description and earlier walkthrough remain retained in
the source bundle. Its setup uses an adaptation of Figure 1 from the
paper, with a transparent background and white drawing for the dark page.

Demo #5 uses the supplied antenna-rotation walkthrough with eight evidence
steps and two nested explanations for the selected M7AEO path. Its six figures
are native dark exports from the frozen Figure 6 reconstruction. The setup is
text-only, and the original Figure 6 comparison remains linked as a PDF. Its
previous bilingual narrative and supplied draft are retained in `source/`.

Demo #6 uses the supplied Zander portable-vertical comparison with eight
evidence steps, a nested Figure 4 comparison, and a nested ON5KQ coverage
explanation. Its six figures use native dark rendering from frozen raw reports,
verified against the supplied export tables, with separate lossless WebP browser
derivatives. The supplied light-theme originals remain preserved unchanged.
The setup places the supplied Gotland transmitter/receiver illustration to the
left of the text, using the same responsive layout as Demo #1. Its caption
describes the setup and reporting flow; the original English image labels are
retained on both language pages. Its launch URL explicitly selects
10-minute segment bins and one-hour selected-station bins, while the narrative
asks the reader to select ON5KQ at JO10os. The previous bilingual narrative,
complete supplied draft, export tables, metadata, and verification record are
retained in `source/`. The Figure 4 PDF keeps the existing application static
link, resolved by the shared renderer.

## Start with the Markdown

```text
site/demos/
  README.md
  walkthrough.template.md
  <demo-id>/
    walkthrough.en.md
    walkthrough.de.md
    source/                  # Retained originals, where present
    resources/               # Reviewed downloads and figures, where present
      manifest.json
```

| Demo | Folder | Current analysis |
| --- | --- | --- |
| #1 | `griffiths_squibb_fig3` | RX Benchmark |
| #2 | `griffiths_squibb_fig6` | RX Benchmark |
| #3 | `griffiths_squibb_rx_performance` | RX Performance |
| #4 | `vanhamel_rx_calibration` | RX Benchmark |
| #5 | `vanhamel_rx_buddy` | RX Benchmark |
| #6 | `zander_tx_buddy` | TX Benchmark |
| #7 | `milazzo_tx_buddy` | RX Benchmark |

The folder ID is a stable route identifier, not a statement of the analysis
mode. Demo #7 retains its historical `milazzo_tx_buddy` ID while its installed
walkthrough starts with RX Benchmark.

For Demo #1, edit `griffiths_squibb_fig3/walkthrough.en.md` and
`griffiths_squibb_fig3/walkthrough.de.md`. Edit the corresponding pair for another
demo. Save as UTF-8. Paragraphs, emphasis, lists, tables, blockquotes, and Markdown
links can be edited directly. Keep English and German consistent in meaning,
numbers, limitations, and citations. Edits become visible after rebuilding the
website; saving a file does not publish it.

## Keep the section markers

HTML comments identify layout slots. They do not appear to visitors:

```markdown
<!-- section: hero -->
# Demo title

Introductory sentence.

<!-- section: setup -->
## Experiment and interpretation

The complete setup explanation.

<!-- section: step-1 -->
## Read the first result

The complete explanation of this step.
```

Keep every existing `<!-- section: ... -->` marker unchanged during ordinary
copy editing. Do not remove, duplicate, or rename one, and do not put text before
the first marker. The hero starts with a level-one heading (`# `); setup and
each configured step start with a level-two heading (`## `). Subsequent prose
and subheadings stay within that section until the next marker.

Write section headings and navigation labels without step-number prefixes.
The layout supplies the visible step numbers; do not repeat them as `1.`,
`1.1`, or similar prefixes in Markdown. Keep the demo number in its main
hero title when it is part of the approved title.

`hero` supplies the visible title and introduction. The same title is used by
the demo card, browser tab, and social metadata. Its eyebrow, period, mode,
and other small interface labels are in the layout configuration. Callsigns,
locators, band, and exact UTC window come from the imported runnable settings;
do not change them by editing narrative text alone.

`setup` contains the visible setup narrative. For migrated Demos #2–#3 and #7,
it provides launch guidance; the layout adds station identities and the UTC
window. Demo #1 uses its new worked-example setup in the main section. Original
app descriptions remain in the source bundle, without duplicate copies in
website Markdown. There are no supporting panels below the steps in either
language. The default sequence goes directly from the hero
to setup, without a separate introductory block. Setup uses the same unboxed
presentation as the evidence sections. The default layout has no At a glance
card section; underlying metric values remain retained in the configuration.

The other markers correspond to the ordered `sections` entries in
`site/demo_walkthroughs.json`. Demo #1 uses IDs such as `load`, `map`,
`difference`, `time`, `coverage`, `stations`, `drilldown`, and `takeaways`; the
other demos currently use `step-1`, `step-2`, and so on. The configuration sets
their display order. The build rejects duplicate markers, missing required
headings, missing sections, and sections that would otherwise be unrendered.

Related explanations can be nested using a section's `subsections` array in
the configuration. Demo #1 nests `published-figure3` under `time`.
Its text still lives in an ordinary Markdown block beginning with
`<!-- section: published-figure3 -->` and a level-two heading. The pairing
diagnostic remains a PDF link immediately after the Figure 3 comparison PDF
link in that same block; it does not have a separate prose section or image. The configuration establishes the parent/child relationship;
do not turn those markers into a different syntax or fold their text into the
parent block. Nested explanations stay within the temporal discussion without
becoming additional numbered top-level steps.

## Text versus layout

Use Markdown for titles, explanations, tables, citations, and conclusions. Use
`site/demo_walkthroughs.json` for the page structure:

| Configuration field | Purpose |
| --- | --- |
| `markdown_paths.en` / `.de` | The active Markdown files, relative to `site/demos/`. |
| `launch_url` | Required explicit full-configuration URL for this demo, using the existing version-1 sharing contract at `wspradar.org`, `run=1`, and the results fragment. |
| `languages` | Localized eyebrow, period, mode, navigation labels, placeholder text, and evidence-section labels. |
| `show_hero_period` | Optional boolean, default `true`; set `false` to omit the period from the hero metadata. The configured period, runnable time window, and walkthrough settings remain intact. Demo #4 disables this display. |
| `sections` | Ordered section IDs, localized navigation labels, and explicit `media_keys`. |
| `sections[].subsections` | Nested explanations with their own section IDs and media; Demo #1 places `published-figure3` under `time`. |
| `sections[].layout: "full"` | Full text width; no adjacent figure is rendered. |
| `setup_media_key` | Optional reviewed setup figure. |
| `show_setup_media` | Optional boolean, default `true`; set `false` for a text-only setup with no figure or placeholder. A `setup_media_key` requires this flag to remain `true`. |
| `setup_media_position` | Optional `"left"` or `"right"`, default `"right"`; positions the setup figure beside flowing text on wider screens. Demo #1 uses `"left"`. Narrow layouts retain stacked figure and text. |
| `show_setup_summary` | Optional boolean, default `true`; set `false` to omit the repeated station, UTC-window and publication summary at the end of Setup. Hero metadata and publication links remain. Demos #1, #4, #5, and #6 disable this summary. |
| `metrics` | Retained localized metric data; the default layout does not render an At a glance card section. |
| `publication_url` | Original publication link. |
| `resource_manifest` | Explicitly reviewed website resources and their integrity manifest. |
| `excluded_media_keys` | Explicitly omit selected media from the narrative while retaining the underlying assets. |
| `inverted_media_keys` | Apply display-only color inversion to selected figures; original image files and PDFs remain unchanged. |
| `preserved_color_regions` | Optional source-image pixel rectangles that preserve native data colors and dark ink while masking bright, low-chroma backgrounds over black. Optional `label_rectangles_px` apply a bounded legend-label treatment. Validate every region against the original image dimensions. |

The active hero and narrative come from Markdown. The earlier Demo #1
presentation copy remains in its `source/` archive for reference.

To add or reorder a section, change the configuration and both Markdown files
together. Keep navigation labels short without removing qualifications from the
section itself. Every media key must identify a reviewed figure belonging to
that demo and can be placed only once. Only explicitly placed setup and evidence
media render. Unplaced reviewed assets remain in their authoritative sources.
At readable desktop widths,
body text wraps beside a figure and then continues across the full width
below it. Narrow layouts stack the figure and text. Do not reserve an empty
column for the full height of a long explanation.

Use `layout: "full"` for table-only or intentionally text-only steps, including
Demo #1 Drill-Down; those steps do not receive a figure placeholder. Keep a
labelled placeholder only where an actual figure is expected later. Do not
fill a scientific placeholder with an invented chart or unverified numbers.

Demo #1 excludes `griffiths-figure3-pairing-diagnostic` from display and applies
`inverted_media_keys` to `griffiths-figure3-comparison`. Its SVG display filter
inverts the first two panels and the third panel's axes. Inside the third
WSPRadar plot and colorbar, a soft mask removes bright, low-chroma background
pixels over an opaque black base, preserving native data colors and dark plot
ink. A separate bounded legend-label treatment makes dark, low-chroma lettering
light gray while retaining the native colors of the legend samples.

The optional `preserved_color_regions` declare `image_px` and `rectangles_px`;
each rectangle is `[x, y, width, height]` in original-image pixels. Optional
`label_rectangles_px` use the same coordinates and must lie inside a preserved
rectangle. Pixels outside the preserved regions follow the general inversion.
Validate all bounds against the exact source image and review them again if
that image changes. These treatments change only the display, not the scientific
source pixels or PDF downloads.

## Add another demo using the same layout

The shared illustrated layout is the default for all existing and future demos.
Start a folder from `walkthrough.template.md`, creating `walkthrough.en.md` and
`walkthrough.de.md`. Add its explicit configuration to
`site/demo_walkthroughs.json`, using the same section IDs as the Markdown.
Review the text, media assignments, and bilingual navigation before publication.

Runnable settings and canonical app content still originate in the private
WSPRadarApp repository and enter the website through the reviewed content
export. A website-only Markdown folder does not create a runnable app demo. Use
the existing export workflow to introduce or change that contract.

## Launch the selected demo

Use the shared **Run in WSPRadar App** action on demo pages. Each demo must have
an explicit `launch_url` in `site/demo_walkthroughs.json`. Retain its complete
configuration using the application's existing version-1 sharing contract at
`wspradar.org`, including `run=1` and `#wspradar-results-inspection`. This loads
the supplied settings and requests the analysis. Use the reviewed full URL;
do not derive a replacement from the demo ID or shorten away its settings.

Do not add a separate configuration-download button to the walkthrough hero.
Existing configuration resources and scientific citations remain available
where the retained narrative links them. The website forwards the existing
query and results fragment to the application, which validates and applies the
shared settings. This uses the application's existing full-configuration
workflow and requires no new compact demo-ID launch handler.

## Preserve original text and evidence

`content/generated/` is the imported public bundle. Do not edit it directly.
Markdown is the website's editable presentation narrative; changes do not
automatically change the app or its canonical manuals. When a correction belongs
in the app too, update its authoritative source and re-export.

The existing complete app descriptions and imported walkthrough steps remain
in their authoritative sources. The website has no supporting-panel renderer,
restoration flags, or duplicate setup descriptions. The Details & sources
navigation entry and the experiment, figures and screenshots fragment targets
are removed with the panels. Imported walkthrough introductions still supply
demo-card search text; shared figures and adaptation source assets remain available.
Main walkthrough figures and publication links remain available. Demo #1's supplied English
worked-example script and initial layout copy are retained in `source/`. These
archives record the previous state; edit `walkthrough.*.md` for future text
changes. Source archives are not automatically published with the website.

The active Demo #1 narrative incorporates the requested removal of its
redundant opening headings, the separate introductory block, visible provenance
paragraph, and advanced pairing explanation. The diagnostic PDF remains linked
directly below the Figure 3 comparison PDF. Source archives, provenance records,
verified summaries, and downloadable evidence remain retained. Other approved
text is preserved apart from section and heading integration, mechanical link
corrections, the updated demo-launch instruction, and removal of duplicated
step-number prefixes. Preserve the
distinction between station-balanced and observation-weighted summaries,
reported locator precision, evidence counts, and limits on causal claims.

## Figures and downloadable resources

Imported figures retain their canonical declarations and provenance. Additional
reviewed resources live in a demo's `resources/` directory. Only files listed in
its `manifest.json` are copied to `/assets/demos/<demo-id>/`. Each listed file has
an exact byte count and SHA-256 hash; mismatches stop the build. Merely placing a
file beside the manifest does not publish it.

The manifest's figure entries provide explicit media keys, localized titles,
captions and alternatives, dimensions, and provenance. Browser variants must
also be listed as reviewed files. Full-size downloads retain the originals;
browser derivatives must preserve scientific detail and disclose their source.
All demo images open their full-size original through the clickable image and
its lightbox. Captions omit the separate “Open full-size image” text link in
both languages. This shared behavior applies to existing and future demos;
do not add per-figure caption actions or visibility options for this link.

Use stable website paths for reviewed downloads, for example:

```markdown
[Exported configuration](/assets/demos/griffiths_squibb_fig3/export/config/wspradar_config.config)
```

Do not use temporary `sandbox:` URLs, personal Downloads paths, or new images
without a declared source. Do not bypass a hash failure by changing the hash
alone. Review replacement content and provenance together before updating its
manifest. Scientific calculations, data acquisition, and figure generation
remain in WSPRadarApp; the website renders reviewed outputs without running an
analysis during a build.

## Build and preview offline

Use a Python environment with `requirements-site.txt` installed. The configured
sibling app environment is a local convenience; an independent website
environment also works.

```powershell
Set-Location 'C:\Users\marku\Code\WSPRadar'
& ..\WSPRadarApp\.venv\Scripts\python.exe scripts/build_site.py
& ..\WSPRadarApp\.venv\Scripts\python.exe scripts/build_site.py --check --offline
& ..\WSPRadarApp\.venv\Scripts\python.exe -m http.server 8787 --bind 127.0.0.1 --directory dist
```

Open `http://127.0.0.1:8787/en/demos/griffiths_squibb_fig3/` or the equivalent
`/de/` route. Use the folder IDs above for other demos. Keep the server command
running while reviewing, and stop that server with Ctrl+C. Open the served URL
rather than a generated HTML file directly: assets use site-root paths. After
editing, rebuild and refresh. `dist/` is generated output, not an editing source.

For a completed change, run the tests and inspect both languages at desktop,
tablet, and phone widths:

```powershell
& ..\WSPRadarApp\.venv\Scripts\python.exe -m unittest discover -s tests -v
& ..\WSPRadarApp\.venv\Scripts\python.exe scripts/build_site.py --check
```

The final command also checks external links and needs a network connection.
`--check --offline` validates local output, routes, anchors, assets, and integrity;
it does not establish that an external publication URL is reachable. Ordinary
text editing and local builds remain available offline. Saving, building, and
previewing do not deploy the website.
