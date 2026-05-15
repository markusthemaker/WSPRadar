param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Message,

    [switch]$ForceRemote
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

$repoRoot = (Get-GitOutput rev-parse --show-toplevel | Select-Object -First 1).Trim()
Set-Location $repoRoot

$rebaseMerge = Join-Path $repoRoot ".git\rebase-merge"
$rebaseApply = Join-Path $repoRoot ".git\rebase-apply"
if ((Test-Path $rebaseMerge) -or (Test-Path $rebaseApply)) {
    throw "A rebase is in progress. Resolve it first or run scripts\git-baseline-temp.ps1 -Force if you want to discard local state."
}

$currentBranch = (Get-GitOutput branch --show-current | Select-Object -First 1).Trim()
if ([string]::IsNullOrWhiteSpace($currentBranch)) {
    Write-Host "Detached HEAD detected. Moving local temp to current HEAD, then switching to temp..."
    Invoke-Git branch -f temp HEAD
    Invoke-Git switch temp
} elseif ($currentBranch -ne "temp") {
    throw "Current branch is '$currentBranch'. Switch to temp first, or run scripts\git-baseline-temp.ps1."
}

$dirty = Get-GitOutput status --porcelain
if ($dirty) {
    Invoke-Git add -A
    Invoke-Git commit -m $Message
} else {
    Write-Host "No local changes to commit. Pushing existing temp branch..."
}

if ($ForceRemote) {
    Invoke-Git push --force-with-lease origin temp
} else {
    Invoke-Git push origin temp
}

Invoke-Git status -sb
Write-Host "Pushed local temp to GitHub temp."
