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

Write-Host "If Git is currently stuck at a '(y/n)' prompt, press Ctrl+C there before running this script."

$repoRoot = (Get-GitOutput rev-parse --show-toplevel | Select-Object -First 1).Trim()
Set-Location $repoRoot

Write-Host "Repository: $repoRoot"
Write-Host "Stopping leftover git.exe processes..."
$gitProcesses = Get-Process git -ErrorAction SilentlyContinue
if ($gitProcesses) {
    $gitProcesses | Stop-Process -Force
    Start-Sleep -Milliseconds 500
}

$remainingGit = Get-Process git -ErrorAction SilentlyContinue
if ($remainingGit) {
    throw "git.exe is still running. Close Git/VS Code terminals or pause OneDrive sync, then rerun this script."
}

Write-Host "Disabling automatic Git cleanup in this repo..."
Invoke-Git config --local gc.auto 0
Invoke-Git config --local maintenance.auto false

$gcPid = Join-Path $repoRoot ".git\gc.pid"
if (Test-Path -LiteralPath $gcPid) {
    Write-Host "Removing stale .git\gc.pid..."
    Remove-Item -LiteralPath $gcPid -Force
} else {
    Write-Host "No stale .git\gc.pid found."
}

Invoke-Git status -sb
Write-Host "OneDrive/Git cleanup complete."
