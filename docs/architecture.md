# WSPRadar website architecture

## Responsibility and publication boundary

WSPRadar is the public static website. WSPRadarApp is the separate private
Streamlit application and owns the scientific implementation and canonical
content. Each repository has its own contributor and architecture instructions.
They connect through a versioned public-content contract, not shared runtime
imports or duplicated scientific code.

The root `index.html` remains the existing published redirect. The first website
implementation builds into ignored `dist/` for local review. Publication requires
a separate approved deployment change to serve this generated directory. No
deployment credentials, automatic private-to-public push, or app source history
are included here.

The generated root page retains forwarding for existing root URLs with query
parameters or the app's `#wspradar-results-inspection` fragment. `site/entry.js`
copies the query and fragment unchanged to the fixed Streamlit origin. Ordinary
root visits show the website; localized website routes do not redirect. The app
remains responsible for validating shared settings. With JavaScript disabled,
visitors see the static website instead of an automatic redirect.

The overview introduces WSPRadar with a supplied Europe-centered header, a
demo-first action, a four-stage explanation of radio signals and uploaded data,
four equally prominent analysis choices, and a real Demo #1 example. Separate
entry routes offer a prepared demo without a station and analysis of existing
public WSPR reports. The getting-started panel uses three numbered steps and a
handwritten demo callout; native details retain the complete descriptions beside
the two route buttons. Station setup and the extensive manual follow these entry
points. The complete previous overview remains in the native `more-guidance`
details element: its three numbered stages still cover choosing the question,
performing the experiment, and running the WSPRadar App, followed by the original
demo introduction, four-Part manual index, and community/report guidance.
Navigation is ordered Overview, Demo Walkthrough, Documentation, and Community,
with the German labels Überblick, Demo-Anleitung, Dokumentation, and Community. Report a Bug remains
available through Community, its existing route, the retained overview, and the
footer. Application launch links outside the demo-specific run actions
consistently use "Open WSPRadar App" or "WSPRadar App öffnen". Demo run actions
use the selected-demo launch contract described below.
The existing Why WSPRadar introductory chapter remains accessible through the
manual; Documentation is highlighted there in the top-level navigation. The overview's demo introduction connects published
WSPR experiments with demonstrated app features and acknowledges differences in
methods, presentation, and data coverage.

## Source ownership

| Location | Responsibility |
| --- | --- |
| WSPRadarApp `docs/doc_en.py`, `docs/doc_de.py`, localized disclaimers | Complete canonical manuals |
| WSPRadarApp `config/demos/*.config` | Ordered titles, original descriptions and runnable settings |
| WSPRadarApp `docs/website/content.json` | Additional bilingual walkthrough and evidence-guide text, explicit media placement |
| WSPRadarApp `docs/website/figures.json`, `screenshots.json`, declared assets | Reviewed scientific figures and actual app captures with provenance |
| WSPRadarApp `scripts/export_public_content.py` | Allowlisted one-way export and stale-content verification |
| `content/generated/` | Imported public bundle, preserved without manual edits |
| `scripts/build_site.py` | Static renderer, website navigation/copy, page and asset verification |
| `site/landing.json`, `scripts/landing_page.py`, `site/landing.css` | Bilingual landing presentation and explicit featured-demo/media selection, pure HTML renderer, and responsive styling |
| `site/assets/landing/source/` | Unmodified supplied artwork, SVG/PNG icons, logo concepts, and original asset-pack metadata retained for future design work |
| `site/assets/landing/manifest.json`, `scripts/prepare_landing_assets.py` | Browser asset dimensions, source/derivative hashes, explicit publication list, and reproducible resizing/encoding |
| `scripts/external_links.py` | Unauthenticated external URL inventory and live availability checks |
| `site/page.html`, `site/site.css`, `site/site.js` | HTML shell, responsive design and progressive enhancement |
| `tests/test_site_build.py` | Website content, routing, rendering and validation contracts |
| `tests/test_external_links.py` | Offline contracts for external URL collection and HTTP verification |

The app's `docs/public-content-contract.md` specifies schema version 1. Its
manifest identifies the app version, source revision, dirty state and SHA-256
hash/byte count of each exported file. A dirty revision is appropriate for this
review snapshot but its commit hash alone does not identify all source changes.

## Updating content and keeping the two projects aligned

1. Edit the canonical source in WSPRadarApp. Preserve English/German meaning and
   complete original scientific text. Update screenshots or reviewed figures when
   a visible or scientific change makes them obsolete.
2. Run the export from WSPRadarApp:

   ```powershell
   .\.venv\Scripts\python.exe scripts/export_public_content.py --output C:\Users\marku\Code\WSPRadar\content\generated
   .\.venv\Scripts\python.exe scripts/export_public_content.py --output C:\Users\marku\Code\WSPRadar\content\generated --check
   ```

3. Build and check WSPRadar using the commands in its README. Review the imported
   content changes together with their source revision and provenance. A future
   public publication uses this reviewed bundle; it never needs private-repository
   access at website build time.

`--check` on the exporter establishes equality with the current app sources.
`--check` on the website establishes equality with the imported bundle and current
renderer. These are different checks: a website-only build cannot detect changes
in an unavailable private checkout. This first implementation provides an
explicit synchronization workflow, not a scheduled sync or automatic release.

A deliberately scoped manual refresh can preserve the previously validated demo
bundle when demo walkthrough updates are outside the authorized change. The
2026-10-17 station-eligibility update extracts both complete canonical manuals with
the app exporter's existing `extract_manual` function, validates every existing
imported file before updating, and retains every nonmanual payload byte and
manifest entry. `manual_source_update` records the exact canonical manual and
shared-disclaimer source hashes, the previous manifest hash and the retained
nonmanual file count. The top-level source revision still identifies the retained
base bundle; it is not asserted to identify the scoped manual changes. The website
validator checks the resulting full payload. A full app exporter `--check` is not
a scoped-sync check and may report deliberately deferred demo changes. Demo
walkthrough source, descriptions, figures and rendered walkthrough pages remain
unchanged during this scoped update.

Figures and screenshots are snapshots. Exporting copies the declared assets; it
does not refresh WSPR data, run Streamlit, regenerate figures or capture a browser.
Refresh those sources deliberately, preserving provenance. The current comparison
figures are unchanged high-resolution PNGs from verified reconstruction fixtures.
New captures reflect the current app rendering and record UTC capture times,
configuration hashes, source revision and data-provider information. In demo #7,
the live RX view contains three Joint Spots while the retained reconstruction
describes five; both live captions disclose this unresolved difference.

The landing page's four Demo #1 evidence images are complete-figure crops from
the maintained dark-mode app screenshots captured on October 13, 2026. Their
canonical declarations are in WSPRadarApp `docs/website/figures.json`; preparation
on October 15, 2026 did not create a new observation or a fresh browser capture.
Each declaration retains the original screenshot path, hash, capture provenance,
and crop coordinates. Lossless WebP preserves the cropped, decoded JPEG pixels
without resizing, recoloring, relabeling, or redrawing. These assets enter the
website through the normal public-content export; the website does not edit
`content/generated/` or calculate replacement scientific figures. The supplied
header, logo concepts, icons, and sample diagram are illustrative design assets
and are not evidence for the reported comparison.

## Rendering and navigation

Both language versions have landing, documentation index, chapter, full-manual,
demo index, individual demo, practical guide, community and report routes. The
root page is an English alias with an English canonical URL. Language links keep
the equivalent route. All content is present in static HTML and can be read
without JavaScript.

The shared page template versions `landing.css` with a SHA-256 prefix derived
from its current bytes. Styling changes therefore request a new browser-cache
entry alongside the updated HTML, including the featured-demo crop rules;
unchanged stylesheets retain a deterministic URL. The output filename remains
`assets/landing.css`, and local link validation resolves its path without the
version query.

`site/landing.json` selects the featured demo and its four media keys explicitly;
`scripts/landing_page.py` consumes that configuration and the imported media
catalog. Each selected image must belong to the selected demo. The current
selection is maintained Demo #1, G3ZIL versus G4HZX on 40 m in RX Benchmark mode.
The landing copy identifies the measured SNR advantage for the low-dipole setup.
The linked walkthrough explains that the comparison includes the complete
installations, locations, equipment, and local noise, and distinguishes its station-balanced median result
from the median of all paired observations. The landing page does not infer that
an antenna type is universally better or establish a cause for the result.

The featured-demo heading, bold experiment introduction, and explanatory
paragraph precede a bordered showcase. Its summary, measured result, and actions sit
beside four evidence cards on wide screens; the responsive layout wraps the cards
and stacks the summary as space narrows. Each card introduces its unchanged
scientific image with a decorative existing icon and a question: where, how much,
when, and who. Visible captions below the images give a
bold finding followed by its explanation. Shared grid rows align the headings,
image areas, and caption areas within each row of cards; content determines their
height without shrinking text. The summary identifies the SNR advantage, paired
observations, and station entries; the station-and-period line is omitted. A
solid-green "Start walkthrough" button precedes the outlined "Run this demo"
button, which uses the featured demo's validated configured launch URL. The
landing source note and result-label asterisk are omitted; the original
publication and full scientific qualifications remain in the linked walkthrough.
English and German versions retain equivalent copy. Explicit
`media_crops` configuration selects source-pixel rectangles for compact previews;
each entry records source dimensions, SHA-256, a row or column layout, and
localized alternatives for its regions. The build rejects changed sources,
invalid layouts, and non-integer or out-of-bounds rectangles. CSS maps the selected
source windows into uniform 4:3 previews, using independent horizontal and
vertical scaling as requested for these small landing-page images. Crop regions
retain their proportional heights in row layouts and widths in column layouts.
Lighten blending merges their black backgrounds into the navy cards. The source
assets remain unchanged, and each card links to the complete full-size figure
with its original proportions and colors. The former
"About these results and how to run the demo" details block is omitted. Complete
capture provenance, weighting explanations, scientific limitations, and
demo-loading guidance remain available through the linked walkthrough and
imported content in both languages.
The supplied design reference informs presentation; it does not replace the
measured plots, change their sign convention, or alter the app-launch contract.

The four analysis cards present RX Performance, TX Performance, RX Benchmark,
and TX Benchmark with equal prominence; individual card destinations are
deferred. Demo actions use each demo's required explicit `launch_url` from
`site/demo_walkthroughs.json`. These reviewed URLs use the application's existing
version-1 full-configuration sharing contract at `wspradar.org`, with `run=1` and
the `#wspradar-results-inspection` fragment. The root entry forwards the full
query and fragment to the application, which validates the settings and handles
the requested run. The website retains these complete URLs rather than deriving
a compact demo-ID link.

The How it works section is semantic HTML with separate SVG icons. Its ordered
stages are WSPR beacons, receiving stations that decode and upload spots, public
WSPR databases, and WSPRadar analysis. The first connector explicitly identifies
radio signals; subsequent connectors identify uploaded spots and Internet data.
The current navigation destinations, manual anchors, canonical URLs, alternate
language links, Open Graph metadata, and root-query forwarding remain available.

The Why WSPRadar section follows What is WSPRadar and precedes the four analysis
choices. It compares a quick on-air observation with repeated observations,
using the existing station, database, map, and evidence SVG icons. All text is
localized HTML in `site/landing.json`; the supplied reference is not embedded as
a page-sized image. The right-hand "WSPRadar: Many observations, clear insights"
panel contains the globe, scale/benefit labels, and the three-step Benchmark
example explaining paired reports, per-station medians, and station-balanced
map-segment aggregation. Its supplied subheading is "Consistently compare your
setups using matched observations." The scale labels read "100s of stations"
worldwide and "1000s of measurements" over days or weeks, with equivalent German
copy. The Benchmark explanation and "Go beyond individual spots" takeaway remain
inside this panel at every viewport. The Benchmark example is a compact strip of
three bordered cards with short descriptions and an accessible list label,
without a separate heading or introductory paragraph. The paired-report and
median rows share #1–#3 labels and align along common row baselines; the column
headings sit above those data rows. The strip is centered with a 620px maximum
width so the cards do not stretch into unused horizontal space. The benefits
list is centered within its column beside the globe. The globe caption,
median-marker legends, and schematic-example footer are omitted from this
marketing illustration. The left panel presents Target before Reference without
Setup A/B labels or an illustrative-SNR caption. Its subheading reads "One path.
One moment. Repeatable?", with equivalent German copy. The robustness benefit
uses the concise "Less sensitive to outliers" wording in both languages.
The example numbers still use Target minus Reference with no applied correction;
median markers remain schematic points without confidence-interval whiskers.
Station identity and qualification are explained in the complete manual, and
the takeaway retains its existing causal limitation. The section uses
the existing heading inset, fonts, navy panels, and cyan/green accents; its two
comparison panels remain side by side above 860px. Their content and conclusions
use shared subgrid rows, with equal conclusion heading offsets even when text
wraps differently. The globe fills its column up to 360px (240px on phones),
alongside compact Benchmark typography. The panels stack through
860px and the method steps through 580px; phone text remains readable without
horizontal overflow.

The section reuses `source/hero/Europe-signal-paths-art-transparent.png` as
illustrative artwork. The landing asset preparation script produces transparent
WebP derivatives at 400, 700, and 1000 pixels and a 700-pixel PNG fallback,
recorded under `network` in the asset manifest. The responsive image loads lazily
and retains intrinsic dimensions. The original and imported scientific figures
remain unchanged.

The renderer partitions the entire manual at level-two and level-three headings.
Joining the partitions must reproduce the complete source exactly. Stable source
anchors choose chapter URLs; compatibility anchors remain present. Chapter links
point to the chapter that owns each anchor. The continuous reader retains local
anchors. Markdown tables receive locally scrollable containers; mathematical
expressions are protected from Markdown escaping before MathJax typesets them.

Relative `app/static/...` Markdown links use `APP_STATIC_URL`, the deployed
Streamlit Community Cloud file route at
`https://wspradar.streamlit.app/~/+/app/static/`. The `~/+/` prefix belongs to
the hosted route, not the app's local `static/` directory. App launch links
continue to use `APP_URL`. Canonical relative source links, file paths, query
parameters, and fragments remain unchanged. Live verification on October 17,
2026 found that the bare `/app/static/...` Zander URL returned HTML with status
200, while the hosted route returned `application/pdf` and bytes identical to
the canonical comparison PDF. HTTP status alone therefore does not establish
that a PDF destination serves a PDF; check its content type and file signature.

The final page renderer applies the PDF-link policy across Markdown, raw HTML,
templates, and buttons. Anchors whose decoded URL path ends in `.pdf`
(case-insensitively, including links with queries or fragments) receive
`target="_blank"` and `noopener noreferrer` relation tokens. HTML `download`
attributes are removed from these PDF anchors so they open rather than force
a download. Existing relation tokens, hrefs, and all other attributes are
preserved; non-PDF markup, including download attributes on other file types,
is left unchanged. The policy is server-generated and does not modify
imported sources.

Original demo descriptions remain retained in full in the source bundle. Additional walkthrough steps
carry explicit `media_keys` that position reviewed figures and screenshots beside
their explanations. Unknown or duplicate keys fail the build. Only explicitly
placed media render; unplaced assets remain in their authoritative sources.
No rendering branch identifies a demo by
its title, callsign or ID. Demos #3 and #4 currently contain no declared figures.
Each demo offers Run in WSPRadar App through its explicit full-configuration
launch URL and the existing automatic-run contract. The walkthrough hero has no separate configuration
download button; retained configuration assets and narrative links remain.

The four evidence-guide stages connect Map View, Segment Inspector, Station
Insights and Drill-Down to actual captures, detailed manual anchors and worked
examples. The narrative retains the intervening evidence panels. GitHub Discussions
is the public entry point for community questions, suspected bugs, experiments,
feature requests and scientific concerns. The bilingual community and report pages
explain the free GitHub account requirement and request English-only posts and replies
without requiring programming knowledge. Ask a question receives usage and interpretation
questions in a Q&A category; users are encouraged to check the manual first, and unclear
points remain welcome. Discuss your experiments receives shared setups and findings;
Ideas and feature requests receives proposals; Report a bug or concern receives suspected
bugs and scientific concerns. Both website support pages present these four categories
as separate cards in that order, with localized headings and one discussion action per
card. Each card uses one concise summary paragraph, with actions aligned at the bottom.
The question card links the word "manual" inline to the localized complete manual; the report
card covers software defects and scientific concerns, with the complete reporting
guidance retained above the cards on the report page. The community page uses the four
category actions without an additional general forum button.
The support guide links to the in-app documentation while
the static website remains an unpublished review implementation.
Detailed analysis information is optional at first and can be requested afterward.
The maintainer creates linked engineering Issues when useful and reports outcomes
back to the original discussion. Existing engineering issue forms remain available;
the issue chooser directs community members to Discussions and disables blank issues.

The former `practical-setup/` route and its navigation entry are removed in both
languages. The overview's question-selection links now lead directly to manual
section `sec-2-2`, and its experiment and basic-setup links lead directly to
`sec-2-1`. The canonical RX/TX Benchmark/Performance sections, basic WSPR setup,
parallel WSJT-X RX instances, simultaneous TX setup, Reference SNR calibration,
and database guidance remain available in the complete manual. The overview's
bottom setup panel links to Documentation and Community. The existing
`guides/read-results/` route and its complete evidence narrative remain available,
with a Documentation breadcrumb; they are not relabeled as hardware setup instructions.

## Responsive presentation and accessibility

The imported app brand bundle retains the shared identity, fonts, subtitle,
release credit, colors, and earlier artwork. The website's new header uses a
live WSPRadar.org wordmark without a preceding emblem, followed
by live navigation and the supplied Europe-centered image. The supplied radar-emblem
sources and derivatives remain retained. The updated 2172 × 724
`WSPR Insights Across Earth.png` is preserved under
`site/assets/landing/source/hero/WSPR-Insights-Across-Earth.png` and supplies the
active browser derivatives. The preceding `WSPRadar_ Global Signal Insights.png`
remains preserved under
`site/assets/landing/source/hero/WSPRadar-Global-Signal-Insights.png`. The embedded
English wording remains English on both website languages, as requested. The
header has descriptive image alternatives and the landing header has a localized
semantic HTML heading and description; those live introductory texts are also
visibly displayed on narrow screens where the embedded raster text becomes small.
All links, calls to action, and section headings remain live HTML.
The landing page's demo and app buttons occupy the artwork's lower-left clear
area above 1120px. At narrower widths their row overlaps the artwork's lower edge
by half its height, with space reserved below for readable touch targets. A positioned
artwork stage contains both the unchanged responsive picture and these live links;
the localized phone introduction and reassurance remain below it. Phone actions
use two columns, readable 14px text, and a minimum 44px height, allowing translated
labels to wrap. The primary action remains bright green; outlined actions use a
faint green border that becomes clearer on hover. Navigation is left aligned with
a green bar under the active page. Its wordmark shares the artwork and content's
3.5% text inset, or their shared 12px phone inset. Balanced 10px top and bottom
padding and a 66px minimum navigation height vertically center the controls.
The shell has no outer top padding, and the artwork starts immediately below the
navigation's fine divider; padding inside the navigation still separates its
controls from that divider. The language control is a native keyboard-operable
details menu with a decorative globe, the current EN or DE abbreviation, and a
chevron. Its localized accessible label and tooltip say Change language or
Sprache ändern; the open menu shows the full native names English and Deutsch.
Both choices retain the current route, with the active choice marked explicitly.
The compact controls keep navigation on one row at desktop and 1024px widths.
From 581px through 999px, Menu replaces the visible navigation links while the
brand, Menu, language, and application action remain on one top row. Opening Menu
reveals the links in a second row, with matching hidden and aria-expanded states.
From 581px through 699px, the smaller wordmark preserves room for the controls.
Navigation labels use 15px text
with 7px gaps from 1000px through 1100px so the German labels fit inside the shell;
wider navigation retains 16px labels with roomier 14px gaps. The demo navigation
label is Demo Walkthrough in English and Demo-Anleitung in German; the demo index
page title and body retain their existing copy.
On phones, the brand and language share the first
row, followed by Menu and the application action; expanded navigation follows.

The overview's primary headings, unboxed introductory text, and grid boundaries
share the hero artwork's 3.5% horizontal inset. The explanation and getting-started
sections place their headings above their blue content panels. Both panels'
outer edges align with the full analysis-card grid, while nested cards retain
their own padding. The live hero introduction and overview sections use
a shared 12-pixel inset through 580px, and the additional-guidance disclosure
follows the same spacing. The footer retains its existing spacing.
Analysis and result grids use two columns through 900px; analysis cards stack
through 480px. Card and diagram headings and descriptions allow language-aware
hyphenation, with word wrapping as a fallback, to retain readable text sizes.

The explanation and getting-started panels use the same inner padding as the
analysis cards: 20px, 17px through 1120px, and 16px through 580px. The getting-started
panel retains the handwritten demo callout, three numbered steps, and both entry
routes inside its border. The explanation panel places text on the left and the four-stage
visualization on the right above 980px; narrower layouts stack those regions. The page
background is `#000b19`, explanation panel `#041424`, and analysis/getting-started
panels `#041525`, based on pixel comparisons with the supplied concept. The
previous cards were already close in luminance; the page background and
getting-started panel accounted for the larger brightness difference.

`site/assets/landing/source/` preserves all 55 supplied ZIP files, including both
SVG icon sets, transparent PNG icons, logo concepts, artwork, and sample diagram.
The full-page mockup is a design reference and is not embedded as a page image.
`scripts/prepare_landing_assets.py` reads the retained originals, resizes directly
with Lanczos without upscaling, and produces separate browser files. The hero
uses WebP quality 94 at widths of 480, 768, 1280, 1600, and 2172 pixels with a
1280 × 427 PNG fallback. Lossy and lossless candidates were compared for file
size and text/line fidelity before selecting this encoding; the original PNG
remains intact. The emblem has 64- and 128-pixel lossless WebP derivatives and
a PNG fallback. The manifest records dimensions, encoding choices, hashes,
comparisons, and `publish_files`; the builder copies only those listed browser
files into `/assets/landing/`, leaving the retained originals out of the output.

The header's native `picture` uses width descriptors and a `sizes` expression
matching the shell to select an image for viewport width and pixel density.
The shell is at most 1280 pixels wide including 24-pixel horizontal padding,
leaving 1232 pixels for content; horizontal padding is 17 pixels through 580px.
Source and fallback image dimensions reserve layout space, and images retain
their intrinsic aspect ratios. The hero loads eagerly with high fetch priority. Component renderers retain
lazy-loading hints, but the final page renderer promotes those hints to eager
loading so native browser printing includes below-the-fold icons and scientific
images without requiring a prior scroll. The compact footer places
WSPRadar and the imported app version once, the tagline, and linked developer
attribution on the left; Report a Bug and GitHub are on the right. Experimental
Use & Disclaimer shares the support-link group. Community remains in the
main navigation and the retained overview. No credit
overlays the header image.

Desktop and iPad layouts use multiple columns where readable. Phone layouts stack
the hero, cards and manual index; a button opens navigation below 1000px; the
chapter contents collapse into a native details element. Live navigation keeps
the four top-level destinations, route-preserving language switching, and the
app-launch action. The report destination remains in Community and the footer.
Navigation occupies its own layout space above the artwork. The landing hero
buttons use the clear area described above without covering embedded text.
Without JavaScript,
all navigation stays available. Search progressively filters demo cards without
hiding their static content from non-JavaScript readers. The retained overview
uses a keyboard-operable native details element. Reduced-motion preferences
disable smooth scrolling, animation, and transitions.

Source Sans 3 is the website's body, navigation, and control face. Rajdhani remains
the heading face; Space Mono is reserved for callsigns, locators, timestamps,
code, and compact technical metadata. The shared footer displays the imported
release and linked developer attribution as live text; narrower layouts wrap
the credit without shrinking website body text. Font
files and licenses are imported from the app's brand bundle and served
locally, with no external font request. The getting-started callout additionally
uses a locally served, OFL-licensed Caveat derivative and a CSS green underline;
it remains selectable, localized HTML text rather than a crop of the mockup.
The app intentionally retains its original
Space Mono results text and controls and Streamlit's Source Code Pro dataframe
font; its documentation and longer input explanations use Source Sans 3.

The documentation index presents the four manual Parts in a two-column desktop
grid. A compact, full-width "Start here: Why WSPRadar?" card introduces the purpose
and limits of station analysis and links to the existing introductory chapter.
The original chapter retains its "0." numbering in the manual. The four-Part grid
follows the card directly, without a separate reading-links row. The complete
manual and detailed contents routes remain available through existing manual
links and chapter navigation.
The documentation index and overview retain a single disclaimer link in the
footer. References remain under Part III. Numbered chapter and appendix entries
use a separate number column while accessible link names retain the complete
canonical titles. The retained overview inside `more-guidance` omits the
introductory card while preserving the four-Part grid. Every manual section remains accessible from
the documentation index, including the disclaimer through the footer, and the
chapter and continuous-reader content is unchanged.

Text remains readable at narrow widths. Wide tables and equations scroll locally.
Scientific images retain their aspect ratio and link to full-size originals;
dimensions reserve layout space. Captions disclose English app captures on both
language versions. Focus indicators, a skip link, localized alt text and touch
targets support keyboard and touch use. Browser review covers desktop, iPad and
360–390px phone widths; this does not substitute for testing every physical device.

## Verification and output safety

Builds validate the imported manifest before rendering. The complete expected
payload is constructed before output writes. Unexpected existing output files
stop the build for inspection; the builder does not recursively delete them.
Local links, anchors, image alternatives, responsive image sources and duplicate
IDs are checked across the generated site. The read-only build check compares all expected output bytes,
including assets and copied content, and rejects missing or extra files.

After local validation, `--check` inventories external HTTP(S) links and resources
in generated HTML and CSS and checks each distinct URL once. Fragments are removed
for availability checks; query strings remain significant. Requests are public and
unauthenticated, with bounded concurrency, timeouts, response sizes and redirect
counts. The checker does not use browser sessions or GitHub credentials. A normal
build remains offline. Each URL check may use a fresh in-memory cookie jar for
anonymous server handshakes; cookies are neither loaded from the browser nor saved.
`--check --offline` explicitly skips external checks and
reports that only local validation was completed.

Successful ordinary redirects are reported for review. Missing destinations are
reported as broken; blocked, rate-limited or otherwise inconclusive requests are
reported as unverified, including unresolved redirect loops or excessive redirects.
Either broken or unverified results make `--check` fail,
with originating generated files listed for investigation. The checker does not
rewrite source URLs or imported content. Remote HTTP availability does not prove
that a scientific citation's content or an external application's workflow is
correct, and external fragments are not validated.

GitHub discussion submission links need additional validation because anonymous
visitors normally reach a login page. Their category query is checked against the
live public category page and community index; matching canonical URLs and category
membership are required. Category redirects fail validation instead of silently
accepting a renamed destination. Authenticated posting is not exercised. Network
behavior is mocked in the unit tests, which remain offline.

Focused isolated tests cover the import boundary, full source preservation,
bilingual route and anchor coverage, math markup, media routing and stale output.
The app runtime is unchanged, so this website task does not trigger the complete
application regression suite. Browser checks establish responsive behavior,
image loading, formula rendering, menu interaction, filtering and language links.

Equations currently depend on pinned MathJax 3.2.2 loaded from jsDelivr. All other
website content and fonts are local. A failed MathJax request leaves readable TeX;
vendoring the library is a possible later deployment improvement.

## Illustrated demo walkthrough presentation

All seven demos use the reusable case-study renderer in
`scripts/demo_walkthrough.py` in both languages. This is the default layout for
future demos. `site/demo_walkthroughs.json` declares their Markdown paths,
bilingual interface labels, retained metric data, explicit evidence media
keys, section navigation, and optional setup media keys. Missing setup or
evidence artwork renders a labelled placeholder without inventing a scientific
image. An explicit `show_setup_media: false` allows a text-only setup without
a placeholder; it cannot be combined with a setup media key. Table-only and intentionally text-only sections use full width without
a figure placeholder. On wider screens, explanation text wraps beside its
figure and continues across the full width below it; narrow layouts stack
these elements. Long explanations do not retain an empty figure column.

Website-authored narrative lives in
`site/demos/<demo-id>/walkthrough.en.md` and `walkthrough.de.md`. These are ordinary
UTF-8 Markdown files for offline editing. Stable `<!-- section: ... -->` markers
identify the hero, setup, and configured evidence steps;
the renderer consumes every section and rejects duplicates or unplaced text.
The default sequence goes directly from the hero to setup without a separate
introductory block. Setup is unboxed, matching the evidence sections. The
default layout omits the At a glance card section while retaining the underlying
metric values in configuration.
The hero uses a level-one heading; setup and evidence sections use level-two
headings without step-number prefixes. The layout supplies the step numbers. The configuration controls placement and navigation, while Markdown
owns the active titles, explanations, tables, citations, and conclusions.
The hero title also supplies the demo-card heading and browser/social title,
keeping those surfaces aligned with the current website narrative.
Demo #4 uses a three-step calibration narrative and an adaptation of the
paper's Figure 1 as its setup image. Its previous
bilingual narrative and supplied draft remain in its `source/` archive; its
original imported description and walkthrough remain in the source bundle.
Demo #5 uses an eight-step antenna-rotation narrative with native dark map,
overall evidence, temporal evidence and coverage, and selected-path evidence
and coverage figures. Two nested Station Insights sections explain the selected
coverage and link to the original Figure 6 comparison PDF. The setup is
intentionally text-only. The supplied draft and previous bilingual narrative
remain in its `source/` archive; the unchanged imported description and earlier
walkthrough remain in the source bundle. Figure provenance records the
frozen source hashes, native production recipes, and numerical checks.
Configured `subsections` keep related explanations inside their parent evidence
step; Demo #1 nests `published-figure3` under `time`. The child retains its
own ordinary Markdown section marker and level-two heading. The pairing
diagnostic PDF is linked immediately after the Figure 3 comparison PDF; its
separate advanced prose section and displayed diagnostic figure are omitted.
`site/demos/README.md` documents authoring, resource review, and local preview;
`site/demos/walkthrough.template.md` provides the shared starting structure.

The shared header and navigation are retained. The walkthrough label and the
contents panel overlap the lower edge of the existing artwork. The contents
panel becomes a sticky right rail on wide desktops and an inline navigation
panel on phones. Scientific previews retain their native aspect ratios, with
original-image links and unchanged source captions. An accessible native dialog
adds zoom, previous/next navigation, Escape dismissal and focus restoration;
without JavaScript the original-image links remain usable.
The image itself provides the full-size link; captions omit the separate
full-size text action in both languages for every current and future demo.

The two trailing expandable supporting panels and the Details & sources
navigation entry are removed in both languages. Their renderer branches,
configuration flags, labels, and CSS are removed as well. Demos #2–#3 and #6–#7
keep only their visible launch guidance in the Markdown setup section; the
duplicate app descriptions are removed. Demo #1 uses the supplied worked
example as its main narrative. Original app descriptions and imported walkthroughs
remain in the source bundle; the first imported walkthrough step still supplies
demo-card search text. Only explicitly placed setup and evidence media render.
Shared figures and adaptation source assets remain in their authoritative
locations without adding hidden fragment targets.
Main walkthrough publication and PDF links remain available. Demo #1's supplied English script and
initial presentation copy remain unchanged in `site/demos/griffiths_squibb_fig3/source/`
as source archives rather than active authoring files.

The active Demo #1 narrative incorporates the requested removal of redundant
opening headings, the separate introductory block, visible provenance
paragraph, and advanced pairing prose. The diagnostic PDF remains linked
within the Figure 3 discussion. Source archives, export provenance, verified
summaries, and evidence resources remain retained. Other approved wording
is preserved apart from structural integration, mechanical link corrections,
the updated demo-launch instruction, and removal of duplicated section-number
prefixes.

Every displayed figure and screenshot appears exactly once. Explicit
`excluded_media_keys` omit requested media from the narrative
without deleting source assets; Demo #1 excludes
`griffiths-figure3-pairing-diagnostic`. Its `inverted_media_keys` selects
`griffiths-figure3-comparison` for display inversion through an SVG filter. The
first two panels and the third panel's axes are inverted. Within the preserved
WSPRadar plot and colorbar regions, a soft mask removes bright, low-chroma
background pixels over an opaque black base, retaining native data colors and
dark plot ink. Bounded legend-label regions render dark, low-chroma lettering
in light gray while preserving the native colors of the legend samples.
Optional `preserved_color_regions` declare `image_px` and `rectangles_px` using
`[x, y, width, height]` in original-image pixels. Optional `label_rectangles_px`
use the same coordinates and must be contained within a preserved rectangle.
All bounds are validated against the exact image dimensions and must be
reviewed again when the source image changes. Pixels outside preserved regions
follow the general inversion. Original image and PDF files remain unchanged. Existing demo URLs, configuration assets,
publication PDF links, and the setup and walkthrough anchors remain. The
experiment, figures and screenshots anchors are removed with the supporting
panels.
Metrics distinguish the median of
station medians from the Joint-Spot median; station identities retain callsign
plus locator. Existing capture provenance continues to identify scientific
images as snapshots. The approved Demo #1 hero remains the walkthrough label,
title, station/locator metadata, period and mode, and its one-sentence introduction.

Additional reviewed public resources may live in
`site/demos/<demo-id>/resources/`. Each demo explicitly selects its resource
manifest. Only allowlisted files with matching byte counts and SHA-256 hashes
are copied to `/assets/demos/<demo-id>/`; arbitrary sibling files and retained
source archives are not automatically published. Figure records declare media
keys, dimensions, bilingual alternatives and captions, provenance, and any
browser variants. Every referenced original and variant must be allowlisted.
These reviewed resources supplement the imported media catalog without editing
`content/generated/`.

The website owns this editable presentation narrative and the shared layout.
The imported public bundle remains unchanged; website edits do not silently
modify canonical app text or runnable demo settings. Scientific calculations,
provider access, and generation of scientific figures remain in the private
WSPRadarApp repository. Website builds only render and copy reviewed outputs;
they do not rerun the analysis. The implementation remains local pending a
separately approved publication.

The shared footer stays on one line when space permits. Report a Bug, GitHub,
and Experimental Use & Disclaimer form one group that wraps to the next row
together. At phone widths, long translated link text may wrap inside that group
without shrinking the font or overflowing the page.


## Printing website pages

The shared template loads `site/print.css` after all screen and component styles,
only for print media. Its versioned URL and `site/print.js` share a content hash.
Print uses white paper, dark text, a single reading column, wrapping tables and
code, repeating table headings, and bounded figures with captions. Long sections
can span pages. Scientific image pixels and downloadable originals are unchanged;
print disables display inversion and the landing preview's lighten blend mode.
Screen presentation and all bilingual source text remain unchanged.

The existing header artwork becomes a CSS background using the largest reviewed
browser derivative. It follows the browser's Background graphics option, without
forcing background printing. Its 42 mm area is reserved even with backgrounds off;
CSS cannot inspect that print-dialog preference. Content figures remain ordinary
images and do not depend on background printing. Browser-added page headers and
footers remain separate print-dialog controls.

Printing includes all main-content disclosures and demo cards, even when their
on-screen disclosure is closed or a search filter hides a card. `beforeprint`
temporarily opens content disclosures, suspends exclusive disclosure groups, and
requests any dynamically added lazy content images; `afterprint` restores
disclosure and loading states. The final HTML renderer promotes existing lazy
images to eager loading: cold-page PDF checks showed that requests started by
`beforeprint` can arrive after the browser snapshots the page. This deliberately
increases initial image transfer while retaining responsive sources, original
pixels, decoding hints, and screen layout.
Print CSS also expands disclosures on engines supporting `::details-content`.
Print events cannot await asynchronous image downloads, so visitors should allow
the preview to finish loading before printing. Navigation, search controls, the
image viewer, and chapter paging controls are omitted from paper.
