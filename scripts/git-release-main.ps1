param(
    [switch]$ForceWithLease
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

$currentBranch = (Get-GitOutput branch --show-current | Select-Object -First 1).Trim()
if ($currentBranch -ne "temp") {
    throw "Release must be run from local temp. Current branch is '$currentBranch'."
}

$dirty = Get-GitOutput status --porcelain
if ($dirty) {
    throw "Local changes exist. Commit and push to temp before releasing to main."
}

Invoke-Git fetch origin

if ($ForceWithLease) {
    Invoke-Git push --force-with-lease origin temp:main
} else {
    Invoke-Git push origin temp:main
}

Invoke-Git status -sb
Write-Host "Released local temp to GitHub main."
