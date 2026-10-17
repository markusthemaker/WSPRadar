# WSPRadar website contributor instructions

This repository owns the public website. The Streamlit application and canonical
scientific content are maintained in the separate private WSPRadarApp repository.
Read `docs/architecture.md` before changing the build or content contract.

## Ownership

- `site/` owns website presentation, navigation, and website-specific copy.
- `scripts/build_site.py` builds static HTML into the ignored `dist/` directory.
- `content/generated/` is an imported, versioned public-content bundle. Never edit
  its manuals, demo descriptions, configurations, captions, figures, or manifest
  directly. Correct their authoritative WSPRadarApp sources and export again.
- Scientific calculations and figure generation belong in WSPRadarApp. The
  website must not query WSPR providers, reproduce calculations, or infer demo
  behavior from names or filenames.
- Shared brand assets and application identity come from the imported bundle.
- Existing `scripts/git-*.ps1` and `scripts/tests/` are independent maintainer
  work. Do not modify them as part of website changes without a relevant task.

## Content and design

Preserve all existing scientific text and qualifications. Both language versions
are public contracts; do not silently correct or add meaning in one language.
Keep original publication titles, citations, station identities, units, and
configuration values unchanged. Website introductions may summarize only when
the full authoritative explanation remains linked and available.

Use the shared illustrated walkthrough layout for all demos. Edit website demo
text in `site/demos/<demo-id>/walkthrough.en.md` and `walkthrough.de.md`, retaining
section markers, complete existing content, and English/German meaning. Keep
layout, media assignments, and retained metric data in `site/demo_walkthroughs.json`;
follow `site/demos/README.md` when extending a demo or adding reviewed resources.
Go directly from the hero to setup without a redundant introductory block.
Keep setup unboxed like the evidence sections. Omit the At a glance card
section by default while retaining its underlying metric data in configuration.
Let text wrap beside figures and continue across the full width below them;
use unnumbered section headings because the layout supplies step numbers.
Table-only or intentionally text-only steps use full width without a figure
placeholder. Use the shared Run in WSPRadar App action to select the exact demo
and request an automatic run; omit a separate configuration-download button.
Do not add trailing expandable experiment/walkthrough panels or a Details &
sources navigation entry to demos. Keep only active website narrative in the
walkthrough Markdown; canonical app descriptions and shared or provenance
assets remain in their authoritative sources. Main walkthrough figures and
publication links remain available.
Require each demo's explicit `launch_url` in `site/demo_walkthroughs.json`, using
the reviewed full version-1 configuration URL at wspradar.org with `run=1` and
the results fragment; do not replace it with a compact demo-ID URL. Keep any
requested display inversion separate from original image and PDF assets.
Optional `preserved_color_regions` use source-image pixel coordinates validated
against that exact image; preserve scientific plot and colorbar colors where
specified. Record deliberate media omissions explicitly in config.

Use the approved Welcome & explore design, the app header, dark navy surfaces,
Rajdhani headings, and Source Sans 3 for body text, navigation, and controls.
Reserve Space Mono for callsigns, locators, timestamps, code, and compact technical
metadata; the app's existing wordmark, subtitle, and release credit remain the
shared header reference. Keep the manual index as four Parts in a two-column
desktop grid, with introductory links above and the disclaimer below. Design
for desktop and iPad first, with usable navigation and readable content at 360px.
Allow wide scientific tables to scroll locally and figures to open at full size.
For all current and future demos, keep each image clickable to open its full-size
view, and omit the separate “Open full-size image” text link below the image in
both languages. Apply this through the shared walkthrough renderer.
Never shrink essential text merely to fit a phone viewport.

All PDF links open in a new tab or window with `target="_blank"` and
`rel="noopener noreferrer"`. Apply this through the shared final-page renderer
for Markdown, raw HTML, templates, and buttons. Remove HTML `download`
attributes from PDF links so they open rather than force a download. Preserve
link destinations, all other attributes, existing relation tokens, and
non-PDF markup, including download attributes on other file types.

### Numeric presentation: thousands grouping

- Use a narrow nonbreaking space (`U+202F`, `\u202f`, HTML `&#8239;`) between
  groups of three integer digits in displayed quantities and counts, in both
  English and German: `1 000`, `1 132`, `125 518`, `1 000 000`. Group four-digit
  quantities as a project consistency choice. Do not use apostrophes, commas,
  periods, ordinary breaking spaces, or bare long integer quantities instead.
- Apply this to website prose, metric cards, tables, captions, chart labels,
  downloadable human-readable documents, and future artwork. Preserve decimal
  markers, signs, rounding, precision and scientific notation. Keep grouping
  separate from decimal localization and scientific calculations.
  Existing compact engineering-prefix axis notation may remain compact.
- Keep machine-readable numeric values and syntax unchanged: CSV/JSON,
  configuration/schema fields, code, URLs, filenames, dates/times, calendar
  years, identifiers, versions, citations and standards numbers. Keep numeric
  table data numeric and format its displayed representation only. Preserve
  exact quotations and historical source evidence.
- Correct canonical app manuals and scientific figure recipes in WSPRadarApp
  and import through the established public-content export; never hand-edit
  `content/generated/`, alter frozen evidence, or repaint raster labels. Edit
  website-owned narrative in `site/` and regenerate `dist/` normally.
- Verify bilingual parity, nonbreaking behavior and font support in the
  affected browser, print and PDF paths, preserving machine-readable exports.
  This follows ISO 80000-1 small-space grouping and the
  [SI Brochure, section 5.4.4](https://www.bipm.org/en/publications/si-brochure).
  `U+202F` and mandatory four-digit grouping are WSPRadar choices, not claims
  that the standards mandate that Unicode character or every group.

### Browser image optimization

- For figures displayed on the website, always use an available dark version
  with a black or dark background. Prefer the application's native dark
  rendering or export over recoloring a light export. Preserve scientific
  data colors, labels, geometry, and the canonical original; if no dark version
  exists, retain the source faithfully until a reviewed adaptation is available.
- Optimize browser headers, figures, and illustrations for visual quality and
  transferred bytes. Compare candidate encodings at their intended display sizes;
  use WebP where it provides a useful saving at acceptable quality, including
  lossless WebP when fine text, lines, or scientific detail require it. Preserve
  JPEG, PNG, or SVG when better suited; do not automatically convert JPEG to WebP
  or force one compression format on every browser image.
- Retain canonical originals and the fidelity of scientific and downloadable
  exports. Optimize separate browser derivatives rather than replacing those
  sources with lossy conversions, and respect the imported-content boundary.
- Pre-size variants from the original for the actual content width, screen size,
  and device pixel ratio. Preserve aspect ratio and never upscale beyond the
  source resolution. Supply accurate `srcset` width descriptors and `sizes` so
  browsers can choose an appropriate variant instead of downloading a large
  original merely to shrink it. Declare intrinsic dimensions to reserve layout
  space and preserve the image's aspect ratio while loading.

## Verification

Run `python scripts/build_site.py --check` after generating `dist/`, and
`python -m unittest discover -s tests -v`. The build validates the imported
manifest before reading content; failures must not be repaired by editing hashes.
Check local links and anchors, complete manual coverage, bilingual routes,
keyboard navigation, touch targets, images, and desktop/iPad/phone overflow.
Compile changed Python and run `git diff --check`. Application regressions are
needed only when application contracts change; website styling does not require
the Streamlit regression suite.

Use foreground retained sessions for local servers and checks. Keep an exact
session handle and stop only task-owned processes. Scratch files belong under
ignored `.tmp/`; `dist/` is reproducible output.

## Publication

Local preview and publication are separate steps. Do not push to a default branch
without explicit authorization. Use a reviewed branch/PR for publication. The
initial root redirect remains the currently published entry point until the new
static-site deployment is approved; local review serves `dist/`.
