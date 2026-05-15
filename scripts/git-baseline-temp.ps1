param(
    [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-Git {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$GitArgs)
    & git @GitArgs
    if ($LASTEXITCODE -ne 0) {
        throw "git $($GitArgs -join ' ') failed with exit code $LASTEXITCODE"
    }
}

function Get-GitOutput {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$GitArgs)
    $output = & git @GitArgs
    if ($LASTEXITCODE -ne 0) {
        throw "git $($GitArgs -join ' ') failed with exit code $LASTEXITCODE"
    }
    return $output
}

function Clear-RebaseStateIfRequested {
    param([string]$RepoRoot)

    $rebaseMerge = Join-Path $RepoRoot ".git\rebase-merge"
    $rebaseApply = Join-Path $RepoRoot ".git\rebase-apply"
    if (-not (Test-Path $rebaseMerge) -and -not (Test-Path $rebaseApply)) {
        return
    }

    if (-not $Force) {
        throw "A rebase is in progress. Run 'git rebase --continue' or rerun this script with -Force to abort/reset local temp."
    }

    Write-Host "Rebase metadata found. Aborting/clearing rebase because -Force was supplied..."
    & git rebase --abort 2>$null
    if ($LASTEXITCODE -ne 0) {
        & git rebase --quit 2>$null
    }
    if (Test-Path $rebaseMerge) {
        Remove-Item -LiteralPath $rebaseMerge -Recurse -Force
    }
    if (Test-Path $rebaseApply) {
        Remove-Item -LiteralPath $rebaseApply -Recurse -Force
    }
}

$repoRoot = (Get-GitOutput rev-parse --show-toplevel | Select-Object -First 1).Trim()
Set-Location $repoRoot

Clear-RebaseStateIfRequested -RepoRoot $repoRoot

$dirty = Get-GitOutput status --porcelain
if ($dirty -and -not $Force) {
    throw "Local changes exist. Commit/stash them first, or rerun with -Force to discard them and reset to origin/temp."
}

Invoke-Git fetch origin

$tempBranch = Get-GitOutput branch --list temp
if ($tempBranch) {
    Invoke-Git switch temp
} else {
    Invoke-Git switch -c temp origin/temp
}

Invoke-Git reset --hard origin/temp
Invoke-Git status -sb

Write-Host "Baseline complete: local temp now matches origin/temp."
