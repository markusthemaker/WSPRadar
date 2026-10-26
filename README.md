# WSPRadar website

Public website entry point for WSPRadar.

- [Open the WSPRadar application](https://markusthemaker-wspradar.hf.space/)
- [Website address: wspradar.org](https://wspradar.org/)

The website redirects visitors to the application while preserving URL query parameters and fragments. Documentation and demos are available inside the application.

The application source code and its development history are maintained separately in the private WSPRadarApp repository. This repository contains website files only.

For bug reports, feature requests, scientific concerns, and general questions, start in [GitHub Discussions](https://github.com/markusthemaker/WSPRadar/discussions); see the [support guide](.github/SUPPORT.md) for help choosing a category. Please write all posts and replies in English; no programming knowledge is needed. A free GitHub account is required to post.

## Website review implementation

All editable website inputs live under `source/`; the complete website is built
under `generated/`, which is the only directory used for local serving.

```text
source/
  pages/          Website-authored Markdown, including demos/<demo-id>/
  assets/         Original artwork and reviewed media with build recipes
  imported/app/   Manifest-verified public bundle synchronized from WSPRadarApp
  theme/          templates/, styles/, and scripts/ for website presentation
  config/         Layout, media placement, and shared interface labels
  archive/        Ignored local packages, prior narratives, and retained evidence
generated/        Reproducible HTML and public assets; never hand-edit
scripts/          Build, synchronization, asset preparation, and maintenance
tests/            Website contracts
architecture.md   Source ownership, build contracts, and synchronization
```

Edit narrative in `source/pages/` and put original media in `source/assets/`.
Imported app content must be corrected in WSPRadarApp and synchronized again.
Repository paths are separate from public paths: `/assets/` and `/content/`
are public routes. Guided-demo PDFs share `/assets/demos/`; the former website
`/static/reference_figures/` tree is no longer emitted. The root `index.html` and `img/` image remain
as compatibility files for the published redirect and existing raw GitHub links.

The statements above describe the currently published redirect. The new public
website is implemented locally under `source/` and `scripts/build_site.py`; its
`generated/` output directory is not published by this change. The preview includes
English and German landing pages, complete chapter and continuous manuals, five
guided demos, a practical evidence guide, and community/report links.

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
`source/assets/landing/originals/` for future use. Only the browser files listed in
`source/assets/landing/manifest.json` are included in generated website assets.
The page mockup is a visual reference, not an embedded page image.
The hero actions sit inside the header, navigation is left aligned with a green
active-page underline, and the explanation panel pairs text with the four-stage
diagram on wide screens. The getting-started panel uses three numbered steps
and a localized handwritten callout; the existing demo and station-report
descriptions remain available in native disclosure controls.

WSPRadarApp owns the canonical manuals, demo configurations, scientific narrative,
reviewed media and shared branding. This repository imports a reviewed public
bundle into `source/imported/app/` and owns website presentation. See
[architecture and synchronization](architecture.md) and [contributor
instructions](AGENTS.md).

Website-specific landing text lives in `source/pages/home.en.md` and
`source/pages/home.de.md`; explicit demo/media selection and text-block references
live in `source/config/landing.json`, rendering in `scripts/landing_page.py`, and styling in
`source/theme/styles/landing.css`. The featured scientific images remain canonical app content:
they are lossless crops of actual dark-mode screenshots captured on October 13,
2026, declared in WSPRadarApp `docs/website/figures.json`, and copied through the
normal public-content export. Their October 15 preparation date is not a new
capture or a new WSPR measurement. Source screenshots and provenance remain
available; illustrative supplied artwork is not used as measured evidence.

### Prepared GitHub Pages deployment

The workflow in [`.github/workflows/deploy-pages.yml`](.github/workflows/deploy-pages.yml)
builds and validates the public website automatically only on pushes to `main`.
Pushes to `temp` are intermediate backups and do not run this workflow, including
when `temp` has an open pull request; pull-request events are not triggers.
An optional manual run can select `temp`
for validation without deployment. Only a successful run on `main` in
`markusthemaker/WSPRadar` can deploy. It uploads the contents of `generated/`, so
`generated/index.html` becomes `https://wspradar.org/`; generated files remain
ignored. The build uses this repository and `requirements-site.txt`, with no
private application checkout or credentials.

The workflow runs the website Python and Node.js contracts and an offline build
check. Live external URLs and app-to-website export freshness remain separate
release checks. GitHub Actions are pinned to reviewed commit IDs; review the
corresponding action definitions when updating those pins.

This workflow is prepared locally; activation is a separate approved step. First
publish the candidate on `temp` and validate it locally before promotion; an
optional manual workflow run on `temp` can also validate it. When deployment is approved, select
**Settings > Pages > Build and deployment > Source > GitHub Actions**, retain the
custom domain **wspradar.org**, and keep **Enforce HTTPS** enabled. Restrict the
`github-pages` environment to `main`, then promote the verified candidate with
`scripts/git-release-main.ps1`. The workflow checks the publishing mode, domain,
and HTTPS setting before deployment and stops if any differ; it does not change
those settings. A manual run on another branch validates without deploying.
The existing Git helpers do not change Pages settings or wait for deployment.

### Build and preview

Use Python 3.12 and install `requirements-site.txt` in your chosen environment.
The existing sibling application's environment already has the required Markdown
version and can be used for local review:

```powershell
& ..\WSPRadarApp\.venv\Scripts\python.exe scripts/build_site.py
& ..\WSPRadarApp\.venv\Scripts\python.exe scripts/build_site.py --check
& ..\WSPRadarApp\.venv\Scripts\python.exe -m unittest discover -s tests -v
& ..\WSPRadarApp\.venv\Scripts\python.exe -m http.server 8787 --bind 127.0.0.1 --directory generated
```

Open `http://127.0.0.1:8787/en/` while the last command is running. Stop the server
with Ctrl+C. Serving `generated/` is necessary because routes and shared assets use
site-root URLs. A separate installation only needs this repository and
`requirements-site.txt`; the application environment is a local convenience.

Normal builds generate browser derivatives from retained originals and reviewed
recipes, using Python with Pillow and WebP support (verified with Pillow 12.2.0)
and FontTools (verified with 4.63.0) for the locally served callout font.
A content-addressed cache under ignored `.tmp/` avoids repeating unchanged image
work. Active approved encoded masters are retained under `source/assets/browser-assets/`
for historical outputs whose complete encoding recipes are unavailable; these
preserve existing public bytes. Active Milazzo verification evidence lives under
`source/assets/demos/milazzo_tx_buddy/evidence/`. The remaining `source/archive/`
is retained locally, ignored by Git, and not needed for building the website.
Originals, archives, and unlisted files are never published automatically.
To prepare or verify landing derivatives separately:

```powershell
& ..\WSPRadarApp\.venv\Scripts\python.exe scripts/prepare_landing_assets.py
& ..\WSPRadarApp\.venv\Scripts\python.exe scripts/prepare_landing_assets.py --check
```

The asset check compares regenerated bytes with the generated files and reviewed
manifest. Encoding can change with the Pillow/libwebp version, so an image-toolchain
change needs a new visual review. See the [landing-asset notes](source/assets/landing/README.md)
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
