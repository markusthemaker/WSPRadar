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

Commit all local changes on `temp` and push to GitHub `temp`:

```powershell
.\scripts\git-push-temp.ps1 "Describe the change"
```

If GitHub `temp` must be overwritten with local `temp`:

```powershell
.\scripts\git-push-temp.ps1 "Describe the change" -ForceRemote
```

## 3. Release Temp To Main

Push tested local `temp` to GitHub `main` while staying locally on `temp`:

```powershell
.\scripts\git-release-main.ps1
```

If GitHub `main` has moved but you intentionally want `main` to become exactly tested `temp`:

```powershell
.\scripts\git-release-main.ps1 -ForceWithLease
```

## Rule Of Thumb

- Local work happens on `temp`.
- GitHub `temp` is for testing.
- GitHub `main` is production/release.
- Avoid manual rebase during this workflow unless you explicitly need it.
