# WSPRadar website Git workflow

These helpers belong to the public website repository
`markusthemaker/WSPRadar`. Application development remains in the separate
private `markusthemaker/WSPRadarApp` repository. Run the helpers from inside the
website checkout that contains them:

```powershell
Set-Location 'C:\Users\marku\Code\WSPRadar'
```

The workflow is local `temp` -> GitHub `temp` -> GitHub `main`. GitHub Pages
publishes `main`; pushing to `temp` alone does not update the website. This
website publication workflow does not create an application release or tag.

The prepared [Pages workflow](../.github/workflows/deploy-pages.yml) builds and
validates `temp` and `main`, with deployment restricted to successful canonical
`main` runs. It publishes only `generated/`; the Git helpers continue to publish
the permitted source tree and do not build the website or wait for Actions.
Before the first static-site release, complete the separately approved
[Pages activation](../README.md#prepared-github-pages-deployment), retaining
`wspradar.org` and enforced HTTPS. Workflow files follow the same Git tracking
and ignore rules as other source files; review their contents before publishing.

## Prerequisites and initial setup

Git, Windows PowerShell 5.1 or PowerShell 7, and authenticated GitHub CLI (`gh`)
must be available on `PATH`. Live GitHub metadata must confirm the expected
repository identity and public visibility before the helpers proceed.

Before first use, separately review and complete the one-time setup: configure
the website checkout's local commit author identity, create local and GitHub
`temp` from the published website `main`, and switch the website checkout to
`temp`. The helpers do not configure identity, create a missing remote branch,
repair the origin, or alter Pages settings. Never initialize website branches
from an application checkout or application commit.

## Routine commands

Start from the published website `temp` when there is no uncommitted or
unpublished local work to preserve:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\git-baseline-temp.ps1
```

After editing and reviewing the website files, commit and push to GitHub `temp`:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\git-push-temp.ps1 -Message 'Describe the website change'
```

This stages all tracked changes and nonignored new files with `git add -A`.
Ignored untracked files remain local; adding an already tracked file to
`.gitignore` does not untrack it. It fetches GitHub `temp` and rebases local work
if newer remote commits exist.
Resolve and test any conflicts before retrying. A detached HEAD can be recovered
onto local `temp` only when doing so preserves existing `temp` history.

After verifying the published `temp` revision, publish it to `main`:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\git-release-main.ps1
```

Release requires clean local `temp` to exactly match freshly fetched GitHub
`temp`. GitHub `main` must be an ancestor of that revision. Local `main` is not
used as the release baseline, and the checkout stays on `temp`. If a GitHub edit
or pull-request merge adds commits only to `main`, explicitly review and merge
those changes into `temp`, test, and publish `temp` before retrying release.

## Public repository safeguards

`git-repository-guard.ps1` applies to all three commands, including their force
options:

- The caller and script must belong to the same checkout. Git environment path
  overrides are rejected.
- All configured and effective origin fetch/push URLs must identify
  `markusthemaker/WSPRadar`. GitHub must report repository ID `1416038123` and
  public visibility. Missing CLI access, invalid metadata, and verification
  failures stop the workflow. Mirror and custom transport settings are rejected.
- Filenames are not restricted by an allowlist. All tracked, staged, and
  nonignored untracked paths must identify regular files within the checkout.
  Symbolic links, junctions in content paths, and submodules are rejected.
  Ignored untracked files are not staged by the helper.
- Every reachable commit must contain only regular files. Deleting an
  accidentally committed application file in a later commit does not remove it
  from public history; review contents before committing because the guard does
  not classify confidentiality. The sole history root must be the original website
  commit `ce3546f4ad40f7729a7397d813359630e29b2e79`. Unrelated history merges,
  shallow checkouts, replacement refs, and grafts are rejected.
- Fetched branch histories are checked before rebasing or resetting; the
  candidate history and destination are checked again before pushing. Fetches
  and pushes use explicit branch references, with tag following, pruning, and
  recursive submodule operations disabled. No tags are published.

New website files require no guard edits. Review their contents and the complete
diff before publishing; do not copy private application source into this public
repository. The guard checks repository identity, paths, Git modes, and ancestry;
it cannot classify the meaning or confidentiality of file contents.

`.gitignore` excludes `generated/`, `dist/`, `.tmp/`, `.venv/`, `.pytest_cache/`,
Python bytecode, and the remaining `source/archive/`. Active archive inputs have
been moved into `source/assets/browser-assets/` and the corresponding
`source/assets/demos/` evidence directory. The ignored archive remains on disk
but is not part of the Git backup. The build remains self-contained in the
tracked source tree; GitHub Actions creates and deploys `generated/` from it.
The guard still inspects every reachable historical tree, including legacy paths.

The repository's `.gitattributes` preserves exact bytes under `source/imported/app/`,
`source/assets/`, `source/archive/`, and `source/pages/`. Automatic line-ending conversion would invalidate
the imported-content and evidence manifests after a fresh checkout, including on
Windows systems with `core.autocrlf=true`. Keep these attributes with the backup.

These safeguards apply to these helpers. They do not protect arbitrary manual
Git commands, modified guards, old script copies, malicious hooks, or concurrent
changes after a check. A later failure can leave an already-created local
commit, fetch, or interrupted rebase in place; inspect the reported error and
status before retrying.

## Explicit recovery options

- `git-baseline-temp.ps1 -Force` aborts an active rebase and discards tracked
  local changes and unpublished local `temp` commits while resetting to GitHub
  `temp`. Other active Git operations must be resolved separately. Unsupported
  file types or history still cause rejection and require independent review.
  The helper does not run `git clean`; untracked files may remain.
- `git-push-temp.ps1 -Message 'Reviewed recovery' -ForceRemote` deliberately
  replaces GitHub `temp` using a lease tied to the freshly fetched remote SHA.
- `git-release-main.ps1 -ForceWithLease` deliberately replaces GitHub `main`
  with the clean, published local `temp`, using the same explicit lease model.

Review any work that would be discarded before choosing a recovery option.
None of these options bypass repository, public-file, or history safeguards.

## Focused safety verification

Tests require Python with `pytest`, Git, and PowerShell. Runtime use of the
helpers requires no Python. From the website checkout, using an interpreter
that already has `pytest` installed:

```powershell
python -B -m pytest scripts/tests/test_git_workflow_safety.py -q -p no:cacheprovider
```

The tests operate on disposable repositories under system temporary storage.
They mock GitHub metadata and remote transport for rejection cases and use an
isolated local bare repository for the transport round trip. They do not contact
GitHub, publish the website, or configure the real repositories. Bytecode and
pytest's repository cache are disabled so verification adds no website files.
