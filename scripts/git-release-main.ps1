param(
    [switch]$ForceWithLease
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot 'git-repository-guard.ps1')
$repoRoot = Initialize-WebsiteRepository -ScriptDirectory $PSScriptRoot
Set-Location $repoRoot
Assert-NoWebsiteGitOperation

$currentBranch = Get-GitOutput branch --show-current
if ($currentBranch -ne "temp") {
    throw "Release must be run from local temp. Current branch is '$currentBranch'."
}

$dirty = Get-GitOutput status --porcelain
if ($dirty) {
    throw "Local changes exist. Commit and push to temp before releasing to main."
}

Fetch-WebsiteBranches -IncludeMain
$localTemp = (Get-GitOutput rev-parse refs/heads/temp | Select-Object -First 1).Trim()
$remoteTemp = (Get-GitOutput rev-parse refs/remotes/origin/temp | Select-Object -First 1).Trim()
$remoteMain = (Get-GitOutput rev-parse refs/remotes/origin/main | Select-Object -First 1).Trim()
if ($localTemp -ne $remoteTemp) {
    throw 'Local temp is not the published GitHub temp revision. Synchronize and test temp before releasing to main.'
}

if ($ForceWithLease) {
    Assert-WebsiteRepository
    Assert-WebsiteHistory -Revision refs/heads/temp
    Assert-WebsiteWorkingTree
    Invoke-Git push --no-follow-tags --no-recurse-submodules "--force-with-lease=refs/heads/main:$remoteMain" origin refs/heads/temp:refs/heads/main
} else {
    & git -C $repoRoot merge-base --is-ancestor $remoteMain $localTemp
    if ($LASTEXITCODE -ne 0) {
        throw 'GitHub main is not an ancestor of published temp. Reconcile main into temp and test it before release; normal release never overwrites main history.'
    }
    Assert-WebsiteRepository
    Assert-WebsiteHistory -Revision refs/heads/temp
    Assert-WebsiteWorkingTree
    Invoke-Git push --no-follow-tags --no-recurse-submodules origin refs/heads/temp:refs/heads/main
}

Invoke-Git status -sb
Write-Host "Released local temp to GitHub main."
