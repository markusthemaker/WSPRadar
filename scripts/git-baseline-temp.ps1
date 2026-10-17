param(
    [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot 'git-repository-guard.ps1')

function Clear-RebaseStateIfRequested {
    $rebaseMerge = Get-WebsiteGitPath 'rebase-merge'
    $rebaseApply = Get-WebsiteGitPath 'rebase-apply'
    if (-not (Test-Path $rebaseMerge) -and -not (Test-Path $rebaseApply)) {
        return
    }

    if (-not $Force) {
        throw "A rebase is in progress. Run 'git rebase --continue' or rerun this script with -Force to abort/reset local temp."
    }

    Write-Host "Rebase metadata found. Aborting rebase because -Force was supplied..."
    Invoke-Git rebase --abort
}

$repoRoot = Initialize-WebsiteRepository -ScriptDirectory $PSScriptRoot
Set-Location $repoRoot

Clear-RebaseStateIfRequested
Assert-NoWebsiteGitOperation

$dirty = Get-GitOutput status --porcelain
if ($dirty -and -not $Force) {
    throw "Local changes exist. Commit/stash them first, or rerun with -Force to discard them and reset to origin/temp."
}

Fetch-WebsiteBranches

$tempBranch = Get-GitOutput branch --list temp
if ($tempBranch) {
    Assert-WebsiteHistory -Revision refs/heads/temp
    $unpublished = [int](Get-GitOutput rev-list --count refs/remotes/origin/temp..refs/heads/temp | Select-Object -First 1)
    if ($unpublished -gt 0 -and -not $Force) {
        throw "Local temp has $unpublished unpublished commit(s). Publish or preserve them first; only explicit -Force recovery may discard them."
    }
    Invoke-Git switch temp
} else {
    Invoke-Git switch -c temp refs/remotes/origin/temp
}

Invoke-Git reset --hard refs/remotes/origin/temp
Invoke-Git status -sb

Write-Host "Baseline complete: local temp now matches origin/temp. Allowed untracked files may remain; review the status above."
