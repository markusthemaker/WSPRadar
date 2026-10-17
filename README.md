# WSPRadar website

Public website entry point for WSPRadar.

- [Open the WSPRadar application](https://wspradar.streamlit.app/)
- [Website address: wspradar.org](https://wspradar.org/)

The website redirects visitors to the application while preserving URL query parameters and fragments. Documentation and demos are available inside the application.

The application source code and its development history are maintained separately in the private WSPRadarApp repository. This repository contains website files only.

For bug reports, feature requests, scientific concerns, and general questions, start in [GitHub Discussions](https://github.com/markusthemaker/WSPRadar/discussions); see the [support guide](.github/SUPPORT.md) for help choosing a category. Please write all posts and replies in English; no programming knowledge is needed. A free GitHub account is required to post.

## Website review implementation

The statements above describe the currently published redirect. The new public
website is implemented locally under `site/` and `scripts/build_site.py`; its
generated `dist/` directory is not published by this change. The preview includes
English and German landing pages, complete chapter and continuous manuals, seven
demo walkthroughs, a practical evidence guide, and community/report links.

The redesigned landing page presents the benefit first, explains the flow from
WSPR radio transmissions through uploaded reception reports to WSPRadar, and
gives RX Performance, TX Performance, RX Benchmark, and TX Benchmark equal
prominence. A real Demo #1 comparison of G3ZIL and G4HZX on 40 m leads into
separate paths for trying a demo without a station and analyzing existing public
WSPR reports. Station setup and the full manual remain available further down;
the complete previous overview is retained in the expandable additional-guidance
section. Existing top-level destinations remain except Report a Bug, which stays
available in Community and the footer. The footer also carries the app version,
developer attribution, and Experimental Use & Disclaimer link. Its compact layout
keeps the identity and credit on the left, with Report a Bug and GitHub on the
right. All footer content stays on one line when space permits; Report a Bug,
GitHub, and Experimental Use & Disclaimer move to the next line together when
the available width is too narrow.

The supplied Europe-centered header retains its English wording in both
languages. Its responsive WebP derivatives preserve the original PNG separately;
semantic HTML provides accessible headings, descriptions, and actions. All
supplied logo concepts, SVG/PNG icons, and artwork are saved under
`site/assets/landing/source/` for future use. Only the browser files listed in
`site/assets/landing/manifest.json` are included in generated website assets.
The page mockup is a visual reference, not an embedded page image.
The hero actions sit inside the header, navigation is left aligned with a green
active-page underline, and the explanation panel pairs text with the four-stage
diagram on wide screens. The getting-started panel uses three numbered steps
and a localized handwritten callout; the existing demo and station-report
descriptions remain available in native disclosure controls.

WSPRadarApp owns the canonical manuals, demo configurations, scientific narrative,
reviewed media and shared branding. This repository imports a reviewed public
bundle into `content/generated/` and owns website presentation. See
[architecture and synchronization](docs/architecture.md) and [contributor
instructions](AGENTS.md).

Website-specific landing text and explicit demo/media selection live in
`site/landing.json`, rendering in `scripts/landing_page.py`, and styling in
`site/landing.css`. The featured scientific images remain canonical app content:
they are lossless crops of actual dark-mode screenshots captured on October 13,
2026, declared in WSPRadarApp `docs/website/figures.json`, and copied through the
normal public-content export. Their October 15 preparation date is not a new
capture or a new WSPR measurement. Source screenshots and provenance remain
available; illustrative supplied artwork is not used as measured evidence.

### Build and preview

Use Python 3.12 and install `requirements-site.txt` in your chosen environment.
The existing sibling application's environment already has the required Markdown
version and can be used for local review:

```powershell
& ..\WSPRadarApp\.venv\Scripts\python.exe scripts/build_site.py
& ..\WSPRadarApp\.venv\Scripts\python.exe scripts/build_site.py --check
& ..\WSPRadarApp\.venv\Scripts\python.exe -m unittest discover -s tests -v
& ..\WSPRadarApp\.venv\Scripts\python.exe -m http.server 8787 --bind 127.0.0.1 --directory dist
```

Open `http://127.0.0.1:8787/en/` while the last command is running. Stop the server
with Ctrl+C. Serving `dist/` is necessary because routes and shared assets use
site-root URLs. A separate installation only needs this repository and
`requirements-site.txt`; the application environment is a local convenience.

The browser derivatives are retained in the repository, so normal builds do not require
an image-processing library. To regenerate or verify them from retained originals,
use Python with Pillow and WebP support (verified with Pillow 12.2.0) and
FontTools (verified with 4.63.0) for the locally served callout font:

```powershell
& ..\WSPRadarApp\.venv\Scripts\python.exe scripts/prepare_landing_assets.py
& ..\WSPRadarApp\.venv\Scripts\python.exe scripts/prepare_landing_assets.py --check
```

The asset check compares regenerated bytes and the manifest with the saved
files. Encoding can change with the Pillow/libwebp version, so an image-toolchain
change needs a new visual review. See the [landing-asset notes](site/assets/landing/README.md)
for retained inputs, encoding comparisons, and reproducibility details.

The build verifies every imported file against its manifest, preserves every
manual section and anchor, and checks local links and image alternatives. The
read-only `--check` additionally verifies exact generated HTML, CSS, JavaScript,
content and asset bytes and rejects extra files. It then checks distinct external
HTTP(S) links and resources in the generated HTML and CSS using unauthenticated
requests. Broken destinations and unverified requests (including blocked access,
rate limits and connection failures) fail the check with source-page details.
Working redirects are reported for review; GitHub community categories must also
match their canonical URLs and remain listed in Discussions. No login or posting
is tested. For an explicitly local-only check, use
`python scripts/build_site.py --check --offline`; its output states that external
URLs were not checked. Ordinary builds and unit tests do not require network access.
Equations use pinned MathJax
3.2.2 from jsDelivr; without that network resource, their TeX remains visible.
Fonts, figures and screenshots are hosted with the website.

The optional Node.js check `node tests/test_entry.cjs` verifies compatibility for
existing root-domain analysis links, including unchanged query parameters and
fragments. Node.js is not needed to build or serve the website.
