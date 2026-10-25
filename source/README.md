# Website source

Edit website text in `pages/`, place original artwork in `assets/`, and build the
complete website into `../generated/`. Serve `generated/` as the HTTP root.

| Folder | Purpose |
| --- | --- |
| `pages/` | Website-authored English and German Markdown, including demo walkthroughs |
| `assets/` | Original media, licenses, reviewed resource manifests and provenance |
| `imported/app/` | Reviewed WSPRadarApp export; correct its authoritative app sources and synchronize it |
| `static/` | Reviewed PDFs copied unchanged to the existing public `/static/` URLs |
| `theme/templates/` | Shared HTML page templates |
| `theme/styles/` | Screen and print stylesheets |
| `theme/scripts/` | Browser interaction and navigation |
| `config/` | Structured presentation choices, media placement and interface labels |
| `archive/` | Retained handoffs, previous narratives, verification evidence and approved encoded masters |

## Editing page text

Demo walkthroughs retain their existing `<!-- section: ... -->` markers. Other
page files use named text blocks, for example:

```markdown
<!-- text: landing.what_title -->
What is WSPRadar?
<!-- /text -->
```

Edit the text inside the markers. Configuration refers to each block by its file
and stable name, such as `home.en.md#landing.what_title`. The renderer retains
the exact text, including inline Markdown or HTML, and rejects missing blocks,
duplicate block names and text outside the markers. Layout remains in the
shared renderers and templates. Short shared interface labels remain in
`config/interface.json`.

## Assets and publication

Keep originals and their provenance. Image recipes produce responsive browser
files under `../generated/`; the build validates their dimensions and reviewed
hashes. Historical encoded files whose complete preparation recipe is not
available are explicitly retained in `archive/browser-assets/` and copied only
when selected by a reviewed manifest. Archives are never published wholesale.

Repository source paths are independent of public URLs. Existing `/assets/`,
`/content/` and `/static/` routes remain compatible. The root `../img/` image is
a compatibility copy required by existing raw GitHub consumers; its original is
under `assets/brand/`. The existing root redirect remains available for the
current deployment until a separately authorized deployment change.

See [the architecture](../architecture.md) and [build instructions](../README.md).
