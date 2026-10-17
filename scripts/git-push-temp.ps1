param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Message,

    [switch]$ForceRemote
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot 'git-repository-guard.ps1')
$repoRoot = Initialize-WebsiteRepository -ScriptDirectory $PSScriptRoot
Set-Location $repoRoot

Assert-NoWebsiteGitOperation

# Detached HEAD produces no output; IsNullOrWhiteSpace handles that directly.
$currentBranch = Get-GitOutput branch --show-current
if ([string]::IsNullOrWhiteSpace($currentBranch)) {
    # Recover detached work without silently replacing unrelated temp commits.
    $tempBranch = Get-GitOutput branch --list temp
    if ($tempBranch) {
        & git -C $repoRoot merge-base --is-ancestor refs/heads/temp HEAD
        if ($LASTEXITCODE -ne 0) {
            throw 'Moving temp to detached HEAD would discard temp history. Review the branches before recovery.'
        }
    }
    Write-Host "Detached HEAD detected. Moving local temp to current HEAD, then switching to temp..."
    Invoke-Git branch -f temp HEAD
    Invoke-Git switch temp
} elseif ($currentBranch -ne "temp") {
    throw "Current branch is '$currentBranch'. Switch to temp first, or run scripts\git-baseline-temp.ps1."
}

$dirty = Get-GitOutput status --porcelain
if ($dirty) {
    Invoke-Git add -A
    Assert-WebsiteWorkingTree
    Invoke-Git commit -m $Message
} else {
    Write-Host "No local changes to commit. Pushing existing temp branch..."
}

Write-Host "Fetching GitHub temp before push..."
Assert-WebsiteHistory -Revision refs/heads/temp
Fetch-WebsiteBranches
$remoteTemp = (Get-GitOutput rev-parse refs/remotes/origin/temp | Select-Object -First 1).Trim()

if ($ForceRemote) {
    Write-Host "ForceRemote supplied. Pushing local temp over GitHub temp with an explicit --force-with-lease..."
    Assert-WebsiteRepository
    Assert-WebsiteHistory -Revision refs/heads/temp
    Assert-WebsiteWorkingTree
    Invoke-Git push --no-follow-tags --no-recurse-submodules "--force-with-lease=refs/heads/temp:$remoteTemp" origin refs/heads/temp:refs/heads/temp
} else {

    $aheadBehind = (Get-GitOutput rev-list --left-right --count refs/heads/temp...refs/remotes/origin/temp | Select-Object -First 1).Trim()
    $parts = $aheadBehind -split "\s+"
    $localAhead = [int]$parts[0]
    $remoteAhead = [int]$parts[1]

    if ($remoteAhead -gt 0) {
        Write-Host "GitHub temp has $remoteAhead commit(s) not present locally. Rebasing local temp onto origin/temp..."
        Invoke-Git rebase refs/remotes/origin/temp
    } else {
        Write-Host "Local temp already contains the current GitHub temp history."
    }

    if ($localAhead -eq 0 -and $remoteAhead -eq 0 -and -not $dirty) {
        Write-Host "No local or remote changes to exchange."
    }

    Assert-WebsiteRepository
    Assert-WebsiteHistory -Revision refs/heads/temp
    Assert-WebsiteWorkingTree
    Invoke-Git push --no-follow-tags --no-recurse-submodules origin refs/heads/temp:refs/heads/temp
}

Invoke-Git status -sb
Write-Host "Pushed local temp to GitHub temp."
