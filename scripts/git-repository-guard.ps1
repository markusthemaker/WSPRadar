# Fixed security boundary for the public website workflow, not operator configuration.
# File selection follows Git tracking and ignore rules; review public content before pushing.
$script:WebsiteRepositoryPolicy = @{
    FullName = 'markusthemaker/WSPRadar'
    Id = 1416038123L
    RootCommit = 'ce3546f4ad40f7729a7397d813359630e29b2e79'
    AllowedUrls = @(
        'https://github.com/markusthemaker/WSPRadar.git',
        'https://github.com/markusthemaker/WSPRadar',
        'git@github.com:markusthemaker/WSPRadar.git',
        'git@github.com:markusthemaker/WSPRadar',
        'ssh://git@github.com/markusthemaker/WSPRadar.git',
        'ssh://git@github.com/markusthemaker/WSPRadar'
    )
}
$script:WebsiteRepositoryRoot = $null
$script:WebsiteCheckedTrees = @{}

function Invoke-Git {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$GitArgs)
    & git -C $script:WebsiteRepositoryRoot @GitArgs
    if ($LASTEXITCODE -ne 0) {
        throw "git $($GitArgs -join ' ') failed with exit code $LASTEXITCODE"
    }
}

function Get-GitOutput {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$GitArgs)
    $output = & git -C $script:WebsiteRepositoryRoot @GitArgs
    if ($LASTEXITCODE -ne 0) {
        throw "git $($GitArgs -join ' ') failed with exit code $LASTEXITCODE"
    }
    return $output
}

function Get-WebsiteGitConfig {
    param([string]$Name, [switch]$Boolean)
    $arguments = @('config')
    if ($Boolean) { $arguments += '--bool' }
    $output = & git -C $script:WebsiteRepositoryRoot @arguments --get-all $Name
    if ($LASTEXITCODE -eq 1) { return }
    if ($LASTEXITCODE -ne 0) { throw "Cannot inspect Git setting '$Name'." }
    return $output
}

function Assert-WebsiteGitEnvironment {
    $redirectingVariables = @(
        'GIT_DIR', 'GIT_WORK_TREE', 'GIT_COMMON_DIR', 'GIT_INDEX_FILE',
        'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES',
        'GIT_NAMESPACE', 'GIT_SHALLOW_FILE', 'GIT_CONFIG',
        'GIT_CONFIG_PARAMETERS', 'GIT_CONFIG_COUNT', 'GIT_REPLACE_REF_BASE',
        'GIT_GRAFT_FILE'
    )
    foreach ($variable in Get-ChildItem Env:) {
        if ($variable.Name -in $redirectingVariables -or $variable.Name -match '^GIT_CONFIG_(KEY|VALUE)_') {
            throw "Git environment override '$($variable.Name)' is set. Remove it before using the website workflow."
        }
    }
}

function Assert-WebsiteRepository {
    Assert-WebsiteGitEnvironment
    # Raw and expanded URLs are both checked: get-url expands insteadOf/pushInsteadOf.
    # Checking all push URLs is essential because Git can push to several destinations.
    $fetchUrls = @(Get-WebsiteGitConfig 'remote.origin.url')
    if ($fetchUrls.Count -eq 0) { throw 'Website origin is missing.' }
    $urls = @($fetchUrls)
    $urls += @(Get-WebsiteGitConfig 'remote.origin.pushurl')
    $urls += @(Get-GitOutput remote get-url --all origin)
    $urls += @(Get-GitOutput remote get-url --push --all origin)
    foreach ($url in $urls) {
        if ($url -notin $script:WebsiteRepositoryPolicy.AllowedUrls) {
            # Do not echo an unexpected URL: it might contain an embedded credential.
            throw 'Unapproved origin URL. Every fetch and push destination must be markusthemaker/WSPRadar on github.com.'
        }
    }
    if ('true' -in @(Get-WebsiteGitConfig 'remote.origin.mirror' -Boolean)) {
        throw 'Mirror pushes are forbidden in the website workflow.'
    }
    foreach ($setting in @('remote.origin.receivepack', 'remote.origin.uploadpack', 'remote.origin.vcs')) {
        if (@(Get-WebsiteGitConfig $setting).Count -gt 0) {
            throw "Custom Git transport setting '$setting' is not supported by the website workflow."
        }
    }

    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        throw 'GitHub CLI (gh) is required to verify the public website repository. Authenticate to github.com before retrying.'
    }
    $metadataText = & gh api --hostname github.com "repos/$($script:WebsiteRepositoryPolicy.FullName)"
    if ($LASTEXITCODE -ne 0) {
        throw 'Cannot verify website repository identity and visibility. Check network access and gh authentication to github.com; no workflow changes were made by this check.'
    }
    try {
        $metadata = ($metadataText -join "`n") | ConvertFrom-Json -ErrorAction Stop
        $validIdentity = ($metadata.id -is [long] -or $metadata.id -is [int]) -and
            $metadata.id -eq $script:WebsiteRepositoryPolicy.Id -and
            $metadata.full_name -ceq $script:WebsiteRepositoryPolicy.FullName -and
            $metadata.private -is [bool] -and (-not $metadata.private)
    } catch {
        throw 'GitHub returned invalid repository metadata; refusing to continue.'
    }
    if (-not $validIdentity) {
        throw 'GitHub repository identity or public visibility does not match the website policy; refusing to continue.'
    }
}

function Initialize-WebsiteRepository {
    param([Parameter(Mandatory = $true)][string]$ScriptDirectory)
    Assert-WebsiteGitEnvironment
    $expectedRoot = [System.IO.Path]::GetFullPath((Join-Path $ScriptDirectory '..')).TrimEnd([char[]]'\/')
    $scriptRoot = & git -C $expectedRoot rev-parse --show-toplevel
    if ($LASTEXITCODE -ne 0) { throw 'The workflow script is not inside an website checkout.' }
    $callerRoot = & git -C (Get-Location).ProviderPath rev-parse --show-toplevel
    if ($LASTEXITCODE -ne 0) { throw 'Run this script from inside its website checkout.' }
    $resolvedScriptRoot = [System.IO.Path]::GetFullPath(($scriptRoot | Select-Object -First 1)).TrimEnd([char[]]'\/')
    $resolvedCallerRoot = [System.IO.Path]::GetFullPath(($callerRoot | Select-Object -First 1)).TrimEnd([char[]]'\/')
    if ($resolvedScriptRoot -ne $expectedRoot -or $resolvedCallerRoot -ne $expectedRoot) {
        throw 'The current checkout differs from the workflow script checkout. Run the script inside the public WSPRadar website checkout, not WSPRadarApp or another checkout.'
    }
    $script:WebsiteRepositoryRoot = $resolvedScriptRoot
    Assert-WebsiteRepository
    Assert-WebsiteHistory -Revision HEAD
    Assert-WebsiteWorkingTree
    return $script:WebsiteRepositoryRoot
}

function ConvertFrom-WebsiteGitPath {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not $Path.StartsWith('"')) { return $Path }
    if ($Path.Length -lt 2 -or -not $Path.EndsWith('"')) {
        throw 'Git returned an invalid quoted website path.'
    }
    # core.quotepath=true gives ASCII C quoting, including UTF-8 octal bytes.
    # Decode before LiteralPath checks so Unicode and escaped names cannot skip
    # checks of the actual file or its parent directories on Windows PowerShell.
    $bytes = [System.Collections.Generic.List[byte]]::new()
    $escapes = @{ 'a' = 7; 'b' = 8; 't' = 9; 'n' = 10; 'v' = 11; 'f' = 12; 'r' = 13; '"' = 34; '\' = 92 }
    for ($offset = 1; $offset -lt $Path.Length - 1; $offset++) {
        $character = $Path[$offset]
        if ($character -eq '\') {
            $offset++
            if ($offset -ge $Path.Length - 1) { throw 'Git returned an incomplete website path escape.' }
            $escape = [string]$Path[$offset]
            if ($escape -match '^[0-7]$') {
                if ($offset + 2 -ge $Path.Length - 1 -or $Path.Substring($offset, 3) -notmatch '^[0-7]{3}$') {
                    throw 'Git returned an invalid website path byte escape.'
                }
                $bytes.Add([Convert]::ToByte($Path.Substring($offset, 3), 8))
                $offset += 2
            } elseif ($escapes.ContainsKey($escape)) {
                $bytes.Add([byte]$escapes[$escape])
            } else {
                throw 'Git returned an unsupported website path escape.'
            }
        } else {
            if ([int]$character -gt 127) { throw 'Git returned a non-ASCII quoted website path.' }
            $bytes.Add([byte]$character)
        }
    }
    return [System.Text.UTF8Encoding]::new($false, $true).GetString($bytes.ToArray())
}

function Assert-WebsiteWorkingTree {
    # Include staged and tracked files even when ignore rules hide new files.
    $paths = @(Get-GitOutput -c core.quotepath=true ls-files --cached --others --exclude-standard)
    $rootPrefix = $script:WebsiteRepositoryRoot + [IO.Path]::DirectorySeparatorChar
    foreach ($gitPath in $paths) {
        $path = ConvertFrom-WebsiteGitPath -Path $gitPath
        $localPath = [IO.Path]::GetFullPath((Join-Path $script:WebsiteRepositoryRoot $path))
        if (-not $localPath.StartsWith($rootPrefix, [StringComparison]::OrdinalIgnoreCase)) {
            throw 'A website file path resolves outside the website checkout.'
        }
        if (Test-Path -LiteralPath $localPath) {
            $item = Get-Item -LiteralPath $localPath -Force
            if ($item.PSIsContainer) { throw "Expected a regular website file: '$path'." }
            # Check parent directories too: a filename below a junction must
            # not silently stage content from outside the website checkout.
            while ($item.FullName -ne $script:WebsiteRepositoryRoot) {
                if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                    throw "Symbolic links and junctions are forbidden in website content: '$path'."
                }
                $parentPath = Split-Path -Parent $item.FullName
                if ([string]::IsNullOrWhiteSpace($parentPath)) { throw 'Cannot resolve the website file parent.' }
                $item = Get-Item -LiteralPath $parentPath -Force
            }
        }
    }
    foreach ($entry in @(Get-GitOutput -c core.quotepath=true ls-files --stage)) {
        if ($entry -notmatch '^(100644|100755) [0-9a-f]+ [0-3]\t(.+)$') {
            throw 'The website index contains an unsupported entry; symbolic links and submodules are forbidden.'
        }
    }
}

function Assert-WebsiteHistory {
    param([Parameter(Mandatory = $true)][string]$Revision)
    # A truncated or replaced graph cannot prove which history will be public.
    if ((Get-GitOutput rev-parse --is-shallow-repository) -ne 'false') {
        throw 'A complete, non-shallow website history is required.'
    }
    if (@(Get-GitOutput for-each-ref '--format=%(refname)' refs/replace/).Count -gt 0 -or
        (Test-Path -LiteralPath (Get-WebsiteGitPath 'info/grafts'))) {
        throw 'Git replacement refs and grafts are forbidden in the website workflow.'
    }
    $commit = (Get-GitOutput rev-parse --verify "$Revision^{commit}" | Select-Object -First 1).Trim()
    $roots = @(Get-GitOutput rev-list --max-parents=0 $commit)
    if ($roots.Count -ne 1 -or $roots[0] -cne $script:WebsiteRepositoryPolicy.RootCommit) {
        throw "Unapproved website history at '$Revision'. Its sole root must be the original public website commit; application or unrelated history is forbidden."
    }
    # Check every reachable tree, not just the tip: deleted files are still public
    # in Git history. Identical immutable trees need inspection only once per run.
    $trees = @(Get-GitOutput log --format=%T --no-decorate --no-show-signature $commit -- | Select-Object -Unique)
    foreach ($tree in $trees) {
        if ($tree -notmatch '^[0-9a-f]{40,64}$') { throw 'Cannot verify a website history tree.' }
        if ($script:WebsiteCheckedTrees.ContainsKey($tree)) { continue }
        foreach ($entry in @(Get-GitOutput -c core.quotepath=true ls-tree -r --full-tree $tree)) {
            if ($entry -notmatch '^(100644|100755) blob [0-9a-f]+\t(.+)$') {
                throw 'Website history contains an unsupported entry; symbolic links and submodules are forbidden.'
            }
        }
        $script:WebsiteCheckedTrees[$tree] = $true
    }
}

function Fetch-WebsiteBranches {
    param([switch]$IncludeMain)
    $refspecs = @('+refs/heads/temp:refs/remotes/origin/temp')
    if ($IncludeMain) { $refspecs += '+refs/heads/main:refs/remotes/origin/main' }
    Assert-WebsiteRepository
    try {
        Invoke-Git fetch --no-tags --no-prune --no-prune-tags --no-recurse-submodules --refmap= origin @refspecs
    } catch {
        throw 'Could not fetch the required website branches. GitHub temp (and main for release) must already exist. Complete the reviewed one-time branch setup, or resolve the reported network/authentication error, then retry.'
    }
    Assert-WebsiteHistory -Revision refs/remotes/origin/temp
    if ($IncludeMain) { Assert-WebsiteHistory -Revision refs/remotes/origin/main }
}

function Get-WebsiteGitPath {
    param([string]$Name)
    return (Get-GitOutput rev-parse --path-format=absolute --git-path $Name | Select-Object -First 1).Trim()
}

function Assert-NoWebsiteGitOperation {
    foreach ($state in @('rebase-merge', 'rebase-apply', 'MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD', 'sequencer')) {
        if (Test-Path -LiteralPath (Get-WebsiteGitPath $state)) {
            throw "A Git operation is in progress ($state). Complete or explicitly abort it before continuing."
        }
    }
}
