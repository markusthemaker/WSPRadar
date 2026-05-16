# WSPRadar Git Workflow Scripts

Run all commands from anywhere inside the repository. The scripts switch to the repository root automatically.

## 1. Morning Baseline

Make local `temp` exactly match GitHub `temp`:

```powershell
.\scripts\git-baseline-temp.ps1
```

If you intentionally want to discard local changes or stale rebase state:

```powershell
.\scripts\git-baseline-temp.ps1 -Force
```

## 2. Push Work To GitHub Temp

Commit all local changes on `temp`, fetch GitHub `temp`, rebase local work onto any newer remote commits, then push to GitHub `temp`:

```powershell
.\scripts\git-push-temp.ps1 "Describe the change"
```

If GitHub `temp` must be overwritten with local `temp`:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\git-push-temp.ps1 "message" -ForceRemote
```

## 3. Release Temp To Main

Push tested local `temp` to GitHub `main` while staying locally on `temp`:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\git-release-main.ps1
```

If GitHub `main` has moved but you intentionally want `main` to become exactly tested `temp`:

```powershell
.\scripts\git-release-main.ps1 -ForceWithLease
```

## Emergency: OneDrive/Git Cleanup

If Git gets stuck during object cleanup with messages such as `Deletion of directory '.git/objects/00' failed`, first stop the stuck prompt with `Ctrl+C`, then run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\git-cleanup-onedrive.ps1
```

The script stops leftover `git.exe` processes, disables automatic Git cleanup/maintenance for this repository, removes a stale `.git\gc.pid` if present, and prints `git status -sb`.

## Rule Of Thumb

- Local work happens on `temp`.
- GitHub `temp` is for testing.
- GitHub `main` is production/release.
- Avoid manual rebase during this workflow unless you explicitly need it.
