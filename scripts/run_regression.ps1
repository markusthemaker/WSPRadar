<#
.SYNOPSIS
Runs WSPRadar regression tests in one foreground Windows terminal.

.DESCRIPTION
Validates the checked-in five-chunk fallback partition, invokes the repository
virtual environment with unbuffered Python, rejects parallel pytest workers,
and propagates pytest's native exit code. The complete suite is the default.

.PARAMETER Chunk
Runs one fixed serial fallback chunk, numbered 1 through 5.

.PARAMETER ValidateChunks
Validates exact, disjoint test-module coverage without starting pytest.

.PARAMETER Durations
Passes pytest's --durations count. Supplying zero reports every test duration.

.PARAMETER PytestArguments
Passes additional serial pytest arguments after the selected test targets.

.EXAMPLE
.\scripts\run_regression.cmd -Durations 30
#>
[CmdletBinding()]
param(
    [ValidateRange(1, 5)]
    [int]$Chunk,

    [switch]$ValidateChunks,

    [ValidateRange(0, 1000)]
    [int]$Durations,

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$PytestArguments = @()
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$testRoot = Join-Path $repoRoot "tests\regression"
$manifestPath = Join-Path $PSScriptRoot "regression_test_chunks.json"
$pythonPath = Join-Path $repoRoot ".venv\Scripts\python.exe"
$expectedChunkIds = @(1, 2, 3, 4, 5)

if ($ValidateChunks -and $PSBoundParameters.ContainsKey("Chunk")) {
    throw "-ValidateChunks and -Chunk cannot be used together."
}
if ($ValidateChunks -and $PSBoundParameters.ContainsKey("Durations")) {
    throw "-Durations does not apply to -ValidateChunks."
}
if ($ValidateChunks -and $PytestArguments.Count -gt 0) {
    throw "Additional pytest arguments do not apply to -ValidateChunks."
}
foreach ($pytestArgument in $PytestArguments) {
    if ($pytestArgument.StartsWith("-n", [System.StringComparison]::Ordinal) -or
        $pytestArgument.StartsWith("--numprocesses", [System.StringComparison]::Ordinal)) {
        throw "Parallel pytest workers are not supported by the canonical regression runner."
    }
}

if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    throw "Regression chunk manifest not found: $manifestPath"
}
if (-not (Test-Path -LiteralPath $testRoot -PathType Container)) {
    throw "Regression test directory not found: $testRoot"
}

$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
if ([int]$manifest.schema_version -ne 1) {
    throw "Unsupported regression chunk manifest schema: $($manifest.schema_version)"
}
if ([int]$manifest.chunk_count -ne $expectedChunkIds.Count) {
    throw "Regression chunk manifest must define exactly $($expectedChunkIds.Count) chunks."
}

$manifestChunks = @($manifest.chunks)
if ($manifestChunks.Count -ne $expectedChunkIds.Count) {
    throw "Regression chunk manifest must contain exactly $($expectedChunkIds.Count) chunk records."
}
$manifestChunkIds = @($manifestChunks | ForEach-Object { [int]$_.id } | Sort-Object)
if (@(Compare-Object -ReferenceObject $expectedChunkIds -DifferenceObject $manifestChunkIds).Count -ne 0) {
    throw "Regression chunk IDs must be exactly: $($expectedChunkIds -join ', ')."
}

$testRootPrefix = $testRoot.TrimEnd([System.IO.Path]::DirectorySeparatorChar) +
    [System.IO.Path]::DirectorySeparatorChar
$assignedTestPaths = [System.Collections.Generic.List[string]]::new()
foreach ($manifestChunk in $manifestChunks) {
    $chunkTestPaths = @($manifestChunk.tests)
    if ($chunkTestPaths.Count -eq 0) {
        throw "Regression chunk $($manifestChunk.id) is empty."
    }

    foreach ($relativeTestPath in $chunkTestPaths) {
        if (-not ($relativeTestPath -is [string]) -or [string]::IsNullOrWhiteSpace($relativeTestPath)) {
            throw "Regression chunk $($manifestChunk.id) contains an invalid test path."
        }
        if ($relativeTestPath.Contains("\") -or
            -not $relativeTestPath.StartsWith("tests/regression/", [System.StringComparison]::Ordinal) -or
            -not $relativeTestPath.EndsWith(".py", [System.StringComparison]::Ordinal)) {
            throw "Regression chunk path must be a normalized repository-relative Python path: $relativeTestPath"
        }

        $candidatePath = [System.IO.Path]::GetFullPath(
            (Join-Path $repoRoot $relativeTestPath.Replace("/", "\"))
        )
        if (-not $candidatePath.StartsWith($testRootPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "Regression chunk path escapes tests/regression: $relativeTestPath"
        }
        $assignedTestPaths.Add($relativeTestPath)
    }
}

$duplicateAssignments = @(
    $assignedTestPaths |
        Group-Object |
        Where-Object { $_.Count -gt 1 } |
        ForEach-Object { $_.Name }
)
if ($duplicateAssignments.Count -gt 0) {
    throw "Regression test modules assigned more than once: $($duplicateAssignments -join ', ')"
}

Push-Location $repoRoot
try {
    $discoveredTestPaths = @(
        Get-ChildItem -LiteralPath $testRoot -Recurse -File |
            Where-Object {
                $_.Name -like "test_*.py" -or $_.Name -like "*_test.py"
            } |
            ForEach-Object {
                $relativePath = Resolve-Path -LiteralPath $_.FullName -Relative
                if ($relativePath.StartsWith(".\", [System.StringComparison]::Ordinal)) {
                    $relativePath = $relativePath.Substring(2)
                }
                $relativePath.Replace("\", "/")
            } |
            Sort-Object
    )

    $unassignedTestPaths = @(
        $discoveredTestPaths | Where-Object { $_ -notin $assignedTestPaths }
    )
    $staleTestPaths = @(
        $assignedTestPaths | Where-Object { $_ -notin $discoveredTestPaths }
    )
    if ($unassignedTestPaths.Count -gt 0 -or $staleTestPaths.Count -gt 0) {
        $manifestErrors = [System.Collections.Generic.List[string]]::new()
        if ($unassignedTestPaths.Count -gt 0) {
            $manifestErrors.Add("unassigned: $($unassignedTestPaths -join ', ')")
        }
        if ($staleTestPaths.Count -gt 0) {
            $manifestErrors.Add("missing or stale: $($staleTestPaths -join ', ')")
        }
        throw "Regression chunk manifest does not match test discovery ($($manifestErrors -join '; '))."
    }

    if ($ValidateChunks) {
        Write-Host (
            "Regression chunk manifest valid: {0} modules across {1} serial chunks." -f
                $discoveredTestPaths.Count,
                $manifestChunks.Count
        )
        $scriptExitCode = 0
    } else {
        if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
            throw "Repository Python interpreter not found: $pythonPath"
        }

        if ($PSBoundParameters.ContainsKey("Chunk")) {
            $selectedChunk = $manifestChunks |
                Where-Object { [int]$_.id -eq $Chunk } |
                Select-Object -First 1
            $pytestTargets = @($selectedChunk.tests | ForEach-Object { $_.Replace("/", "\") })
            Write-Host (
                "Running regression chunk {0}/{1} in the foreground ({2} modules):" -f
                    $Chunk,
                    $manifestChunks.Count,
                    $pytestTargets.Count
            )
            $pytestTargets | ForEach-Object { Write-Host "  $_" }
        } else {
            $pytestTargets = @("tests\regression")
            Write-Host "Running the complete regression suite in one foreground pytest session."
        }

        $pythonArguments = @("-u", "-m", "pytest", "-q")
        if ($PSBoundParameters.ContainsKey("Durations")) {
            $pythonArguments += "--durations=$Durations"
        }
        $pythonArguments += $pytestTargets
        $pythonArguments += $PytestArguments

        $savedErrorActionPreference = $ErrorActionPreference
        try {
            # Windows PowerShell can promote native stderr to a terminating
            # error under Stop, which would collapse pytest exit codes to 1.
            $ErrorActionPreference = "Continue"
            & $pythonPath @pythonArguments
            $scriptExitCode = $LASTEXITCODE
        } finally {
            $ErrorActionPreference = $savedErrorActionPreference
        }
        Write-Host "pytest exited with code $scriptExitCode."
    }
} finally {
    Pop-Location
}

exit $scriptExitCode
