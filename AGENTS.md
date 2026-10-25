# WSPRadar website contributor instructions

This repository owns the public website. The Streamlit application and canonical
scientific content are maintained in the separate private WSPRadarApp repository.
Read `architecture.md` before changing the build or content contract.

## Ownership

- `source/` contains every website build input. `source/pages/` owns editable
  website Markdown; `source/assets/` owns original artwork and reviewed media;
  `source/theme/` owns templates, styles, and browser scripts; `source/config/`
  owns layout, placement, and shared interface labels.
- `scripts/build_site.py` builds static HTML into the ignored `generated/` directory.
- `source/assets/demos/` owns reviewed demo PDF downloads copied byte-exactly
  to public `/assets/demos/` URLs. `source/archive/` retains local supplied packages,
  previous narratives, and historical encoded masters and is ignored by Git.
  Active retained masters belong in `source/assets/browser-assets/`, and active
  evidence belongs in the corresponding `source/assets/demos/` directory; builds
  must not depend on the ignored archive. Publish only explicitly selected
  resources. Preserve existing public URLs unless their migration is explicitly requested.
- Browser derivatives belong in `generated/`. Build them from reviewed original
  assets and recipes, with the ignored content-addressed `.tmp/` cache used only
  to avoid repeated work. Keep retained encoded masters where an older recipe
  cannot reproduce the approved bytes.
- `source/imported/app/` is an imported, versioned public-content bundle. Never edit
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
Drafts may defer German adaptation under **Draft language and pre-main
synchronization** below; completed publication requires semantic parity.
Keep original publication titles, citations, station identities, units, and
configuration values unchanged. Website introductions may summarize only when
the full authoritative explanation remains linked and available.

### Connect study-based demos to the manual

When adding or materially extending a prepared or guided demo related to a study
cited in Chapter 7, extend that study's indented **Use in WSPRadar** note in the
canonical WSPRadarApp English manual. Follow the approved Milazzo,
Griffiths/Squibb, Vanhamel and Zander entries: add a concise **Explore in WSPRadar**
paragraph or short list with the actual guided-walkthrough link, what the demo
shows and its interpretation limits. Distinguish the original findings from
WSPRadar's reconstruction or additional analysis; identify separate prepared
configurations and reuse a shared guide where appropriate. Preserve the study
summary and existing practical guidance. Synchronize through the app's normal
documentation exporter; never edit the imported manual directly. This rule does
not authorize German translation.

### Spot-pair terminology

Use the shared WSPRadarApp scientific definition: a **spot pair** consists of
one retained Target observation and one retained Reference observation matched
on band, WSPR cycle, and the remote station's callsign and full reported locator.
Each pair supplies one Delta-SNR observation. Existing report consolidation can
combine multiple database rows per side; do not equate every pair with exactly
two original database reports.

- Use **Spot pairs** for comparison counts, **Paired spots** for paired-report
  SNR panels, and **Paired** for native outcomes. Proposed German equivalents are
  **Spot-Paare**, **Gepaarte Spots**, and **Gepaart**; confirm the glossary before
  applying German labels. Keep **Both observed** for station presence
  within the displayed period and **Both observed, no pairs** for the station
  class with no same-cycle pair. Preserve all scientific counts and qualifications.
- Each cumulative SNR curve counts that setup's paired reports at its own cutoff;
  this is not a count of complete pairs passing a shared SNR threshold. A pair
  counts once in the observed-event union and once in each setup's decode total.
- Keep canonical launch URLs at `v=1` during this pre-release migration. Update
  imported settings-summary selectors and owned links with canonical app parameter
  names; do not introduce independent URL settings or silently change defaults.
- Correct app-owned terminology, schemas and scientific artwork in WSPRadarApp;
  regenerate imports through the exporter. Correct website narratives, captions,
  alternative text and derivative recipes in `source/`, then rebuild `generated/`.
- Refresh current figures/PDFs and browser derivatives from authoritative evidence.
  Preserve original papers, frozen reports, historical publications, exact quotes
  and retained public asset paths. Explicitly account for those legacy exceptions.
- App screenshots and website figures follow the settings described in each
  current demo, including explicit guided selections. Only paper-reconstruction
  demo PDFs retain the settings stated in their footer to reconcile the paper.
- Establishing the German glossary does not authorize translation or scientific
  synchronization of German content. Perform this migration in English; retain
  current German UI, documentation, captions and figures for the later translation
  stage. Preserve unrelated content. Verify links, settings,
  PDF text/layout, visible raster labels, responsive variants and synchronized
  asset hashes; a text search alone does not establish completion.

**Proposed German glossary for a later translation stage.** These terms are
recorded for review, not approved for rollout. Keep them aligned with the
WSPRadarApp contributor glossary.

| English term or context | Proposed German wording |
| --- | --- |
| Spot pair (singular unit) | Spot-Paar |
| Spot pairs (count) | Spot-Paare |
| Paired spots (SNR panel) | Gepaarte Spots |
| Paired (outcome legend) | Gepaart |
| Paired (qualifying) | Gepaart (qualifiziert) |
| Paired (not qualifying) | Gepaart (nicht qualifiziert) |
| Minimum spot pairs per station for ΔSNR | Mindestzahl an Spot-Paaren pro Station für ΔSNR |
| Stations with paired observations | Stationen mit gepaarten Beobachtungen |
| Stations without paired observations | Stationen ohne gepaarte Beobachtungen |
| Both observed (station presence in the displayed period) | Beide beobachtet |
| Both observed, no pairs (station class) | Beide beobachtet, keine Paare |
| Cumulative reports per setup | Kumulative Reports je Aufbau |
| Same WSPR cycle | Derselbe WSPR-Zyklus |
| Synchronized operation (coordinated schedules) | Synchronisierter Betrieb |

Do not use **synchronisiert** as a synonym for paired evidence. Inflection such
as **mit fünf Spot-Paaren** preserves the unit. Technical identifiers remain
canonical English in both languages.

### Database terminology

Use **WSPR spot database**, **database**, or **databases** for WSPRnet, wspr.live,
WSPRDaemon WD2/WD1, and other queried WSPR spot-data services; use **Datenbank**
or **Datenbanken** in German. Do not use **Archiv** or **Archive** for these
queried spot-data services. Establishing this terminology does not itself
authorize German translation or language synchronization.
This is the shared WSPRadarApp/WSPRadar standard
and applies to every active website surface: landing and documentation pages,
guided demos, captions and alternative text, figures/PDFs, help and download
descriptions, and engineering documentation. Describe their contents as database
records, reports, or spots rather than archived reports. Do not imply identical
provider contents or snapshots. Reserve **archive** for actual ZIP/file
packages, retained historical collections, exact source titles or quotations,
and literal public or compatibility identifiers. Preserve frozen evidence and
historical provenance. Correct app-owned content in WSPRadarApp and export it;
correct website-owned narrative/media at its authoritative `source/` location
and rebuild `generated/`. Never hand-edit imported or generated copies. Follow
the existing draft-language synchronization timing for German adaptations.

Use the shared illustrated walkthrough layout for all demos. Edit website demo
text in `source/pages/demos/<demo-id>/walkthrough.en.md` and `walkthrough.de.md`, retaining
section markers, complete existing content, and English/German meaning. Keep
layout, media assignments, and retained metric data in `source/config/demo_walkthroughs.json`;
follow `source/pages/demos/README.md` when extending a demo or adding reviewed resources.
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
Use each imported demo record's canonical `launch_url`, generated from its
validated application config, for every demo action and inline launch link.
Do not maintain `launch_url` or language-specific URL overrides in
`source/config/demo_walkthroughs.json`; use `{{demo_launch_url}}` in walkthrough Markdown.
The URL retains the full version-1 settings at wspradar.org with `run=1` and the
results fragment; do not replace it with a compact demo-ID URL. Configured
`settings_tables` select imported `settings_summary` rows by key and own only
their order, column headings and explanatory text. Use exactly one
`{{demo_settings_table}}` marker in each language that enables this table; never
copy its setting values into website configuration. Keep any
requested display inversion separate from original image and PDF assets.
Optional `preserved_color_regions` use source-image pixel coordinates validated
against that exact image; preserve scientific plot and colorbar colors where
specified. Record deliberate media omissions explicitly in config.

Use the approved Welcome & explore design, the app header, dark navy surfaces,
Rajdhani headings, and Source Sans 3 for body text, navigation, and controls.
Reserve Space Mono for callsigns, locators, timestamps, code, and compact technical
metadata; the app's existing wordmark, subtitle, and release credit remain the
shared header reference. Keep the manual index in a two-column desktop grid,
with introductory links above and the disclaimer below. The Start here card
represents Part 0; do not repeat it in the overview grid. English grid entries
are Parts I–V; German retains four Parts pending translation. Keep Part 0 and its
subsections in the documentation page and chapter navigation. Design
for desktop and iPad first, with usable navigation and readable content at 360px.
Allow wide scientific tables to scroll locally. Scientific figure thumbnails
throughout the website, including documentation, guides, introductions and
demos, use the shared in-page figure viewer by default: full-size image, zoom,
fit, previous/next within the originating gallery, and keyboard-accessible close.
Keep the original-image href as the no-JavaScript fallback and preserve modified
clicks. Exclude logos, decorative artwork, navigation thumbnails, PDF links and
explicit downloads. Load full-resolution originals only when opened. Reuse the
shared viewer rather than adding page-specific viewers. For all current and
future demos, omit the separate “Open full-size image” text link below the image
in both languages; apply this through the shared walkthrough renderer.
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
  `source/imported/app/`, alter frozen evidence, or repaint raster labels. Edit
  website-owned narrative in `source/` and regenerate `generated/` normally.
- Verify bilingual parity, nonbreaking behavior and font support in the
  affected browser, print and PDF paths, preserving machine-readable exports.
  This follows ISO 80000-1 small-space grouping and the
  [SI Brochure, section 5.4.4](https://www.bipm.org/en/publications/si-brochure).
  `U+202F` and mandatory four-digit grouping are WSPRadar choices, not claims
  that the standards mandate that Unicode character or every group.

### Table column alignment

- Choose alignment from each column's contents: numeric values and counts align
  right, text aligns left, and centered exceptions must be explicit.
- Give the header the same alignment as its column's body cells, regardless of
  the header's wording. A callsign heading above counts therefore aligns right.
- Shared renderers and CSS must honor authored column alignment. Do not force
  all headers left or introduce per-demo or per-callsign alignment overrides.

### Defined terms

- Review replacement and added text for established defined terms. Reuse
  `<strong class="defined-term">...</strong>` for the existing bold-green
  treatment at the first actual definition; do not automatically color later
  mentions.

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

## Responsiveness, Memory, and Build Efficiency

Responsiveness and memory footprint are first-class engineering requirements,
alongside scientific fidelity, accessibility, maintainability, and a sound
long-term architecture. Apply these requirements to new features, visual
redesigns, dependencies, refactors, and fixes. Assess browser loading and
interaction costs separately from build time and build-process memory.

### Architecture and scaling

- Review ownership, shared callers, data flow, and resource lifetimes before
  choosing an implementation. Use the established source, configuration,
  imported-content, and generated-output boundaries.
- Address the underlying cause through an appropriate shared mechanism. Do not
  duplicate logic, add per-page exceptions, bypass validation, or retain
  unbounded state merely to obtain a quick local improvement or pass a narrow
  test. Keep instance-specific choices in authoritative configuration.
- Consider how work and memory grow with page count, language variants, manual
  length, media count and dimensions, and repeated interactions or builds.
  State material capacity assumptions and verify the ones affected by the
  change using representative larger inputs or targeted scaling checks.
- Prefer the simplest design that satisfies current requirements and credible
  growth needs. Explain consequential tradeoffs and necessary migrations;
  neither speculative abstractions nor knowingly fragile shortcuts are a
  substitute for a maintainable design. Focused verification does not constrain
  the implementation to the smallest patch.

### Browser work and resource lifetime

- Keep essential content in static HTML and use progressive enhancement for
  interactions. Prefer established native HTML/CSS capabilities for simple
  behavior. Justify added JavaScript libraries, fonts, preload rules, and
  background work with a concrete benefit and their loading and memory costs.
- Initialize each enhancement once. Avoid duplicate event listeners, repeated
  whole-document scans, and unnecessary polling. Batch layout measurements and
  DOM updates; coalesce frequent scroll or resize work instead of repeatedly
  forcing synchronous layout for unchanged inputs.
- Defer nonessential scripts and offscreen media without delaying essential
  content. Do not lazy-load the main image needed for the initial viewport.
  Load full-resolution lightbox originals on demand, and avoid unnecessary
  downloads of both an original and its responsive derivative. Preserve
  keyboard access, anchor navigation, and complete printing behavior.
- Give temporary DOM elements, image references, event handlers, observers,
  canvases, and object URLs explicit ownership and cleanup. Repeatedly opening
  and closing figures must not accumulate application-owned resources. Do not
  preload every full-resolution figure or PDF for a page.
- Assess decoded image dimensions and retained objects alongside compressed
  transfer sizes. Give application-managed caches explicit bounds and
  invalidation rules; do not trade an unbounded memory increase for lower
  latency. Preserve the existing browser-image fidelity requirements.

### Build reuse and memory

- Reuse unchanged derivatives through the existing content-addressed cache.
  Avoid repeated resizing, encoding, or equivalent processing for the same
  source and recipe across pages and languages. Cache identity must include
  every input that can affect the generated result.
- Avoid unnecessary simultaneous copies of large assets and intermediate
  buffers. Bound parallel processing by measured peak memory as well as
  throughput. Measure cold and warm builds separately when changing caching
  or asset preparation.
- Preserve deterministic output, manifest validation, canonical originals,
  byte-exact downloads, and public URLs. Performance changes must not weaken
  provenance or silently reduce scientific fidelity.

## Verification

Choose verification scope by affected contracts, architectural reach, and
failure consequences. Proportionate verification means sufficient evidence,
not minimum effort: it must cover relevant integration boundaries, resource
lifetimes, and scaling assumptions as well as immediate visible behavior.
Inspect shared callers and dependencies before declaring a change isolated.
Broaden review and checks when coupling, uncertainty, or a coverage gap warrants
it; a passing narrow test does not establish architectural soundness.

### Editorial fast path

For bounded changes to prose, punctuation, links or static table content:

- Use the current reviewed content and retained evidence as the baseline. Read
  the requested changes and their immediate context; reuse established task
  context instead of repeating repository discovery or unchanged audits.
- Preserve supplied wording and unrelated content. Flag factual contradictions
  briefly and verify newly introduced or materially changed claims and values
  against the nearest authoritative evidence. Do not re-audit unchanged data or
  scientific methods without a concrete reason.
- Use one agent unless a substantial independent subtask would benefit from
  parallel work. Apply the entire requested batch before validation.
- For website builds and checks, use
  `..\WSPRadarApp\.venv\Scripts\python.exe` from the repository root
  (invoke it with `&` in PowerShell). The `python` commands in verification
  examples refer to this interpreter, not system Python.
- For website content, build once and run
  `python scripts/build_site.py --check --offline`; inspect changed rendered
  structure where relevant and run `git diff --check`. Review new external link
  destinations when needed; do not repeat an unchanged site's external audit.
  Engineering Markdown alone needs a diff and link review plus whitespace check,
  not a site build. Do not add tests that merely freeze prose.
- In a dirty checkout, compare task changes against the pre-edit state and
  scope whitespace checks to edited files with
  `git diff --check -- <edited paths>`. If broader validation reveals a
  confirmed unrelated failure, report it separately without automatically
  expanding the task.
- Run additional targeted tests only for affected contracts these checks cannot
  establish. Browser checks are needed only when requested or when the changed
  visual/interactive outcome cannot be established structurally.
- Do not create or update audit reports, archives or unchanged figures/PDFs
  unless requested or needed to retain new evidence or satisfy an applicable
  contract. Reuse successful checks for unchanged inputs. Finish when selected
  checks pass; expand only for a failure or an identified coverage gap.

### Rendering, behavior and release checks

Layout, rendering, media, navigation, accessibility and interaction changes
require the directly affected tests and runtime verification sufficient to
cover the changed behavior and identified integration risks. Check local links
and anchors, manual coverage, bilingual
routes, keyboard navigation, touch targets, images and desktop/iPad/phone
overflow where affected. Compile changed Python and run `git diff --check`.

Use `python -m unittest discover -s tests -v` for an explicit full-run request,
broad changes across independent website features, or qualification of a concrete
release candidate. A routine copy edit, commit or `temp` backup does not require
the complete suite. Do not repeat a passing complete run after a bounded fix;
run the relevant subset for that fix.

The build validates the imported manifest before reading content; failures must
not be repaired by editing hashes. When canonical manuals change in WSPRadarApp,
verify the affected source-to-import-to-render handoff without repeating
unchanged scientific audits. Application regressions are needed only when
application contracts change; website styling does not require the Streamlit
regression suite.

Use foreground retained sessions for local servers and checks. Keep an exact
session handle and stop only task-owned processes. Scratch files belong under
ignored `.tmp/`; `generated/` is reproducible output.

### Performance and architecture verification

- For changes affecting scripts, layout, media loading, asset generation, build
  caching, or resource ownership, select before-and-after checks that cover the
  affected contracts and architectural risks. Use consistent inputs, viewport,
  browser, and cache conditions. Report relevant loading or interaction timings,
  transferred bytes, and peak or retained memory where affected; distinguish
  browser costs from build costs and measurements from estimates.
- Select representative affected pages, such as the landing page, an
  image-heavy walkthrough, or the long manual. Exercise repeated interactions
  when resource lifetime changes and representative larger inputs when scaling
  behavior changes. Verify actual responsive-image selection where affected.
  A successful static build or an aggregate performance score alone does not
  establish browser responsiveness, memory stability, or architectural fitness.
- Include shared consumers, cold and warm paths, invalidation, and cleanup when
  the change affects those contracts. Use meaningful tests for duplicated work,
  cache identity, lifecycle, and bounded resource use where practical; avoid
  brittle wall-clock assertions that depend on one developer's machine.
- Resolve avoidable regressions before completion. Explain necessary tradeoffs,
  measured deltas, and remaining evidence gaps explicitly. Do not use a short
  local check to justify a design that shifts cost into another page, language,
  repeated operation, or a larger supported workload.
- Ordinary prose changes require no performance benchmark. These requirements
  do not independently trigger a full suite, whole-site browser audit, or
  regeneration of unchanged figures. Apply the existing broad-change and
  release criteria when architecture changes cross independent features;
  otherwise expand checks until the affected contracts and identified risks
  are covered. Do not stop solely because the initially selected checks pass.

## Publication

### Draft language and pre-main synchronization

- Iterate documentation and website narrative in English by default. Defer
  German adaptation until the user requests language synchronization or work is
  being prepared for `main`. A local iteration or a `temp` backup/parking push
  does not trigger translation. Honor an explicitly requested draft language.
- This section defines the timing of documentation parity requirements
  elsewhere in these instructions. Keep existing German content and both routes
  usable during drafts; completed publication requires semantic parity.
- Identify pending German scope and the last known synchronized baseline in the
  existing task/handoff and, when backing up, the commit description. Do not
  create a separate translation ledger for routine edits. Report English draft
  completion separately from bilingual release readiness.
- A request to prepare or publish to `main` triggers a language-sync pass over
  all accumulated documentation changes since the last synchronized baseline.
  Adapt affected German walkthroughs, captions, tables, navigation and other
  narrative from the accepted final English revision, preserving useful
  German-only content. Verify meaning, claims, qualifications, numbers, links
  and structure; matching headings alone does not prove semantic parity.
- Correct canonical manuals in WSPRadarApp and run its
  `scripts/sync_documentation.py` plus `--check`; never translate imported files
  directly. This command generates/copies the existing sources; it does not
  translate, review semantic parity or synchronize website-owned walkthroughs.
  Preserve required deterministic generated-output checks on `temp` while
  translation is pending. Check both repositories when both changed.
- Complete translation, generation and applicable bilingual/rendering checks
  before the final release commit/push to `temp`; then promote that verified
  revision through the guarded release workflow. Pending translation prevents
  promotion to `main`, including a PR merge. This is an agent workflow
  requirement, not an existing automated semantic gate, and does not grant
  permission to push or publish.

Local preview and publication are separate steps. Do not push to a default branch
without explicit authorization. Use a reviewed branch/PR for publication. The
initial root redirect remains the currently published entry point until the new
static-site deployment is approved; local review serves `generated/`.
