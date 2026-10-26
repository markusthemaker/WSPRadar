# WSPRadar publication repository

This public repository contains production website output and community material.
Authoritative website sources, build tools, tests and their full contributor
instructions live under `website/` in the private WSPRadarApp repository.

- `ci-published/` is generated, validated and replaced only by private CI. Do not
  hand-edit generated files or introduce authoring sources here.
- Correct website content at its private source and publish through the private
  website workflow. Preserve all existing scientific content and qualifications.
- The public `.github/workflows/deploy-pages.yml` only uploads and deploys
  `ci-published/`. Its authoritative template is private
  `website/deployment/deploy-pages.yml`; update both through maintainer review.
  The publishing App has Contents write permission and does not modify workflows.
- Keep Pages configured for GitHub Actions, `www.wspradar.org` and HTTPS. Serve
  the contents of `ci-published/` as the site root, without a folder URL prefix.
- Preserve community templates, public history and root compatibility assets.
  Never merge or push private application Git history into this repository.
- Keep App credentials in private WSPRadarApp Actions configuration. The public
  deployment workflow uses only its own GitHub token.
- Local inspection may serve `ci-published/`; no website build dependencies are
  needed in this publication checkout.
