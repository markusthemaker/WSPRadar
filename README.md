# WSPRadar website and community

- [Website, documentation and guided demos](https://www.wspradar.org/)
- [Open the WSPRadar application](https://app.wspradar.org/)
- [Community discussions](https://github.com/markusthemaker/WSPRadar/discussions)
- [Support guide](.github/SUPPORT.md)

## Automated publication

`ci-published/` is managed by CI. It contains the complete production website,
generated and validated in the private WSPRadarApp repository. Do not edit these
files manually: the next publication replaces this directory, including removing
obsolete files.

Application and website authoring sources, build tools and tests are maintained
in private WSPRadarApp, with website sources under `website/`. Its publishing
workflow uses a dedicated GitHub App to copy only validated generated files into
this public repository. Private source history and credentials are not copied.

The small [Pages workflow](.github/workflows/deploy-pages.yml) deploys the contents
of `ci-published/` as the root of `https://www.wspradar.org/`. It does not compile
the website or access private source. Existing public URLs and Git history are
retained. Root `index.html`, `CNAME` and `img/` remain for compatibility; the Pages
artifact comes exclusively from `ci-published/`.

The publication commit identifies the private source revision. If generated
content needs correction, fix its authoritative source in WSPRadarApp and publish
again. The previous public commits remain available for a deliberate rollback.

For bug reports, feature requests, scientific concerns and general questions,
start in GitHub Discussions. Please write posts and replies in English; no
programming knowledge is needed. A free GitHub account is required to post.
