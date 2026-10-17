"""Exercise release-script safety against isolated Git repositories, without network."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest


SCRIPTS_ROOT = Path(__file__).resolve().parents[1]
WEBSITE_URL = "https://github.com/markusthemaker/WSPRadar.git"
APPLICATION_URL = "https://github.com/markusthemaker/WSPRadarApp.git"
WEBSITE_METADATA = {
    "id": 1416038123,
    "full_name": "markusthemaker/WSPRadar",
    "private": False,
}
WORKFLOWS = (
    ("git-push-temp.ps1", ["-Message", "Safety regression", "-ForceRemote"]),
    ("git-release-main.ps1", ["-ForceWithLease"]),
    ("git-baseline-temp.ps1", ["-Force"]),
)
GIT_REDIRECTION_VARIABLES = {
    "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE",
    "GIT_SHALLOW_FILE", "GIT_CONFIG", "GIT_CONFIG_PARAMETERS", "GIT_CONFIG_COUNT",
    "GIT_REPLACE_REF_BASE", "GIT_GRAFT_FILE",
}


def _powershell_literal(value: str | Path) -> str:
    """Quote literal paths and test values without PowerShell interpolation."""

    return "'" + str(value).replace("'", "''") + "'"


@dataclass
class GitSandbox:
    """Own one temporary checkout and native-command boundary for workflow tests."""

    root: Path
    scratch: Path
    environment: dict[str, str]
    git_executable: str
    powershell_executable: str

    def git(self, *arguments: str) -> str:
        """Run real, local Git against this sandbox and fail on unexpected errors."""

        completed = subprocess.run(
            [self.git_executable, "-C", str(self.root), *arguments],
            env=self.environment, capture_output=True, text=True, timeout=30,
            check=False,
        )
        assert completed.returncode == 0, completed.stdout + completed.stderr
        return completed.stdout.strip()

    def snapshot(self) -> tuple[str, str, str, bytes]:
        """Capture branch, refs, working state, and configuration before a guard."""

        return (
            self.git("rev-parse", "HEAD"),
            self.git("show-ref"),
            self.git("status", "--porcelain=v1", "--untracked-files=all"),
            (self.root / ".git" / "config").read_bytes(),
        )

    def run(
        self,
        workflow: str | None = None,
        arguments: tuple[str, ...] | list[str] = (),
        *,
        metadata: object = WEBSITE_METADATA,
        metadata_text: str | None = None,
        metadata_responses: list[object] | None = None,
        api_exit_code: int = 0,
        fetch_exit_code: int = 0,
        cwd: Path | None = None,
        extra_environment: dict[str, str] | None = None,
    ) -> tuple[subprocess.CompletedProcess[str], list[dict]]:
        """Execute actual scripts, mocking only Git transport and GitHub metadata.

        Each git call is recorded before delegation. Fetch and push never leave
        this process: remote-tracking refs are seeded by the fixture instead.
        Local Git commands remain real so rewrites, config precedence, branch
        state, and worktree behavior are tested using Git's own interpretation.
        """

        command_log = self.scratch / "commands.jsonl"
        command_log.unlink(missing_ok=True)
        metadata_path = self.scratch / "metadata.json"
        metadata_path.write_text(
            json.dumps(metadata_responses) if metadata_responses is not None
            else json.dumps(metadata) if metadata_text is None else metadata_text,
            encoding="utf-8",
        )
        invocation_path = self.scratch / "invoke-workflow.ps1"
        scripts_root = self.root / "scripts"
        if workflow is None:
            invocation = (
                f". {_powershell_literal(scripts_root / 'git-repository-guard.ps1')}\n"
                "Initialize-WebsiteRepository -ScriptDirectory "
                f"{_powershell_literal(scripts_root)} | Out-Null"
            )
        else:
            invocation = f"& {_powershell_literal(scripts_root / workflow)}"
            for argument in arguments:
                invocation += " " + (
                    argument if argument.startswith("-")
                    else _powershell_literal(argument)
                )
        wrapper = r"""
$ErrorActionPreference = 'Stop'
$global:LASTEXITCODE = 0
$global:MetadataCallIndex = 0
function global:git {
    $gitArguments = @($args)
    @{ tool = 'git'; args = $gitArguments } | ConvertTo-Json -Compress -Depth 5 |
        Add-Content -LiteralPath __COMMAND_LOG__ -Encoding UTF8
    $commandIndex = 0
    while ($gitArguments[$commandIndex] -in @('-C', '-c')) {
        $commandIndex += 2
    }
    $gitCommand = $gitArguments[$commandIndex]
    if ($gitCommand -in @('fetch', 'push')) {
        $global:LASTEXITCODE = if ($gitCommand -eq 'fetch') { __FETCH_EXIT_CODE__ } else { 0 }
        return
    }
    if ($gitCommand -in @('clone', 'pull', 'ls-remote', 'submodule')) {
        throw "Unexpected Git transport in isolated test: $gitCommand"
    }
    if ($gitCommand -eq 'remote' -and $gitArguments -contains 'update') {
        throw 'Unexpected remote update in isolated test'
    }
    & __GIT_EXECUTABLE__ @gitArguments
    $global:LASTEXITCODE = $LASTEXITCODE
}
function global:gh {
    @{ tool = 'gh'; args = @($args) } | ConvertTo-Json -Compress -Depth 5 |
        Add-Content -LiteralPath __COMMAND_LOG__ -Encoding UTF8
    if (__METADATA_SEQUENCE__) {
        # Windows PowerShell emits the JSON array as one pipeline object; an
        # outer @() would wrap it again and return both metadata records at once.
        $responses = Get-Content -LiteralPath __METADATA_PATH__ -Raw | ConvertFrom-Json
        $responseIndex = [Math]::Min($global:MetadataCallIndex, $responses.Count - 1)
        $responses[$responseIndex] | ConvertTo-Json -Compress
        $global:MetadataCallIndex += 1
    } else {
        Get-Content -LiteralPath __METADATA_PATH__ -Raw
    }
    $global:LASTEXITCODE = __API_EXIT_CODE__
}
try {
    __INVOCATION__
} catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 73
}
exit 0
"""
        replacements = {
            "__COMMAND_LOG__": _powershell_literal(command_log),
            "__GIT_EXECUTABLE__": _powershell_literal(self.git_executable),
            "__METADATA_PATH__": _powershell_literal(metadata_path),
            "__METADATA_SEQUENCE__": "$true" if metadata_responses is not None else "$false",
            "__API_EXIT_CODE__": str(api_exit_code),
            "__FETCH_EXIT_CODE__": str(fetch_exit_code),
            "__INVOCATION__": invocation,
        }
        for marker, replacement in replacements.items():
            wrapper = wrapper.replace(marker, replacement)
        invocation_path.write_text(wrapper, encoding="utf-8-sig")
        environment = dict(self.environment)
        environment.update(extra_environment or {})
        completed = subprocess.run(
            [self.powershell_executable, "-NoProfile", "-NonInteractive",
             "-ExecutionPolicy", "Bypass", "-File", str(invocation_path)],
            cwd=cwd or self.root, env=environment, capture_output=True, text=True,
            # A workflow launches many serial Git processes; allow slow Windows
            # hosts more time while retaining a bounded subprocess deadline.
            timeout=120, check=False,
        )
        commands = (
            [json.loads(line.lstrip("\ufeff")) for line in
             command_log.read_text(encoding="utf-8-sig").splitlines()]
            if command_log.exists() else []
        )
        return completed, commands


@pytest.fixture
def git_sandbox(tmp_path) -> GitSandbox:
    """Make disposable branches and refs; never configure the actual checkout."""

    git_executable = shutil.which("git")
    powershell_executable = (
        shutil.which("powershell.exe") or shutil.which("pwsh")
    )
    if not git_executable or not powershell_executable:
        pytest.skip("Git and PowerShell are required for native workflow checks")
    root = tmp_path / "website checkout with spaces"
    scripts_root = root / "scripts"
    scripts_root.mkdir(parents=True)
    for script_name in (
        "git-repository-guard.ps1", *(name for name, _ in WORKFLOWS)
    ):
        shutil.copy2(SCRIPTS_ROOT / script_name, scripts_root)
    empty_global_config = tmp_path / "empty-global.gitconfig"
    empty_global_config.touch()
    environment = {
        key: value for key, value in os.environ.items()
        if key.upper() not in GIT_REDIRECTION_VARIABLES
        and not key.upper().startswith(("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_"))
    }
    environment.update({
        "GIT_CONFIG_GLOBAL": str(empty_global_config),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_OPTIONAL_LOCKS": "0",
    })
    sandbox = GitSandbox(root, tmp_path, environment, git_executable,
                         powershell_executable)
    sandbox.git("init", "--initial-branch=temp")
    sandbox.git("config", "user.name", "Workflow safety test")
    sandbox.git("config", "user.email", "workflow-test@example.invalid")
    sandbox.git("config", "commit.gpgsign", "false")
    sandbox.git("config", "tag.gpgsign", "false")
    sandbox.git("config", "core.autocrlf", "false")
    (root / "README.md").write_text("Isolated website fixture\n", encoding="utf-8")
    (root / "index.html").write_text("<html>Isolated fixture</html>\n", encoding="utf-8")
    (root / "CNAME").write_text("example.invalid\n", encoding="utf-8")
    sandbox.git("add", "README.md", "index.html", "CNAME")
    sandbox.git("commit", "--quiet", "-m", "Isolated website history root")
    fixture_root = sandbox.git("rev-parse", "HEAD")
    guard_path = scripts_root / "git-repository-guard.ps1"
    guard_source = guard_path.read_text(encoding="utf-8-sig")
    production_root = "ce3546f4ad40f7729a7397d813359630e29b2e79"
    assert production_root in guard_source, "Expected fixed production website root"
    # Adapt ONLY the disposable fixture copy to its own freshly created root.
    # Production has no override option or test-mode escape hatch.
    guard_path.write_text(guard_source.replace(production_root, fixture_root), encoding="utf-8-sig")
    sandbox.git("add", "scripts")
    sandbox.git("commit", "--quiet", "-m", "Isolated website workflow helpers")
    sandbox.git("branch", "main")
    sandbox.git("remote", "add", "origin", WEBSITE_URL)
    sandbox.git("update-ref", "refs/remotes/origin/temp", "HEAD")
    sandbox.git("update-ref", "refs/remotes/origin/main", "HEAD")
    return sandbox


def _git_commands(commands: list[dict]) -> list[list[str]]:
    """Remove Git's directory prefix for assertions about the invoked operation."""

    invocations = []
    for command in commands:
        if command["tool"] != "git":
            continue
        arguments = command["args"]
        while arguments[:1] in (["-C"], ["-c"]):
            arguments = arguments[2:]
        invocations.append(arguments)
    return invocations


def _assert_guard_rejected(sandbox, before, completed, commands):
    """Prove rejection happens before transport or changes to local Git state."""

    assert completed.returncode != 0, completed.stdout
    assert sandbox.snapshot() == before
    for arguments in _git_commands(commands):
        assert (
            arguments[0] in {"rev-parse", "status", "rev-list", "ls-tree", "ls-files",
                             "diff", "diff-index", "cat-file", "merge-base", "log", "show",
                             "for-each-ref"}
            or (arguments[0] == "remote" and arguments[1] == "get-url")
            or (arguments[0] == "config" and "--get-all" in arguments)
            or (arguments[0] == "branch" and
                any(option in arguments for option in ("--show-current", "--list")))
        ), commands


@pytest.mark.parametrize(("workflow", "arguments"), WORKFLOWS)
def test_each_workflow_rejects_application_origin_before_mutation(
    git_sandbox, workflow, arguments
):
    """Even force modes must reject the private application before staging or reset."""

    git_sandbox.git("remote", "set-url", "origin", APPLICATION_URL)
    (git_sandbox.root / "README.md").write_text("Keep local website edits", encoding="utf-8")
    before = git_sandbox.snapshot()
    completed, commands = git_sandbox.run(workflow, arguments)
    _assert_guard_rejected(git_sandbox, before, completed, commands)


@pytest.mark.parametrize(("workflow", "arguments"), WORKFLOWS)
def test_each_workflow_rejects_a_different_current_checkout(
    git_sandbox, workflow, arguments
):
    """An absolute script path must not redirect an older chat into another repo."""

    other_checkout = git_sandbox.scratch / "website"
    other_checkout.mkdir()
    subprocess.run([git_sandbox.git_executable, "init", str(other_checkout)],
                   env=git_sandbox.environment, capture_output=True, check=True)
    before = git_sandbox.snapshot()
    completed, commands = git_sandbox.run(workflow, arguments, cwd=other_checkout)
    _assert_guard_rejected(git_sandbox, before, completed, commands)


@pytest.mark.parametrize("configuration", [
    [("remote.origin.pushurl", APPLICATION_URL)],
    [("remote.origin.pushurl", WEBSITE_URL), ("remote.origin.pushurl", APPLICATION_URL)],
    [("remote.origin.url", APPLICATION_URL)],
    [(f"url.{APPLICATION_URL}.insteadOf", WEBSITE_URL)],
    [(f"url.{APPLICATION_URL}.pushInsteadOf", WEBSITE_URL)],
    [("remote.origin.mirror", "true")],
    [("remote.origin.receivepack", "custom-receive-pack")],
    [("remote.origin.uploadpack", "custom-upload-pack")],
    [("remote.origin.pushurl", "https://github.com/other/WSPRadarApp.git")],
    [("remote.origin.pushurl", "https://github.com.example.invalid/markusthemaker/WSPRadarApp.git")],
    [("remote.origin.pushurl", WEBSITE_URL + "/unexpected")],
])
def test_guard_rejects_hidden_or_unsafe_destinations(git_sandbox, configuration):
    """Validate every raw and rewritten fetch/push URL and dangerous remote modes."""

    for key, value in configuration:
        git_sandbox.git("config", "--add", key, value)
    before = git_sandbox.snapshot()
    completed, commands = git_sandbox.run()
    _assert_guard_rejected(git_sandbox, before, completed, commands)


@pytest.mark.parametrize("metadata", [
    {**WEBSITE_METADATA, "private": True},
    {**WEBSITE_METADATA, "private": "false"},
    {**WEBSITE_METADATA, "id": 42},
    {**WEBSITE_METADATA, "full_name": "markusthemaker/WSPRadarApp"},
    {"id": 1416038123, "full_name": "markusthemaker/WSPRadar"},
    None,
])
def test_guard_requires_exact_live_public_repository_identity(git_sandbox, metadata):
    """A familiar repository name alone cannot establish its identity or privacy."""

    before = git_sandbox.snapshot()
    completed, commands = git_sandbox.run(metadata=metadata)
    _assert_guard_rejected(git_sandbox, before, completed, commands)


@pytest.mark.parametrize(("metadata_text", "api_exit_code"), [
    ("{malformed", 0),
    (json.dumps(WEBSITE_METADATA), 1),
])
def test_guard_fails_closed_when_metadata_is_unavailable(
    git_sandbox, metadata_text, api_exit_code
):
    """Neither invalid JSON nor a failed API call may enable offline publishing."""

    before = git_sandbox.snapshot()
    completed, commands = git_sandbox.run(
        metadata_text=metadata_text, api_exit_code=api_exit_code,
    )
    _assert_guard_rejected(git_sandbox, before, completed, commands)


@pytest.mark.parametrize("variable", [
    "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_REPLACE_REF_BASE", "GIT_GRAFT_FILE",
])
def test_guard_rejects_environment_repository_redirection(git_sandbox, variable):
    """Git process environment must not substitute a different repository/index."""

    before = git_sandbox.snapshot()
    completed, commands = git_sandbox.run(
        extra_environment={variable: str(git_sandbox.scratch / "redirected")},
    )
    _assert_guard_rejected(git_sandbox, before, completed, commands)


@pytest.mark.parametrize("url", [
    WEBSITE_URL,
    WEBSITE_URL.removesuffix(".git"),
    "git@github.com:markusthemaker/WSPRadar.git",
    "ssh://git@github.com/markusthemaker/WSPRadar.git",
])
def test_guard_accepts_supported_website_transports(git_sandbox, url):
    """Keep supported HTTPS and SSH origins usable with live identity validation."""

    git_sandbox.git("remote", "set-url", "origin", url)
    completed, commands = git_sandbox.run(cwd=git_sandbox.root / "scripts")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    api_calls = [command["args"] for command in commands if command["tool"] == "gh"]
    assert api_calls
    assert all(arguments == ["api", "--hostname", "github.com",
                             "repos/markusthemaker/WSPRadar"]
               for arguments in api_calls)


@pytest.mark.parametrize(("workflow", "arguments", "target"), [
    ("git-push-temp.ps1", ["-Message", "Safety regression"], "temp"),
    ("git-push-temp.ps1", ["-Message", "Safety regression", "-ForceRemote"], "temp"),
    ("git-release-main.ps1", [], "main"),
    ("git-release-main.ps1", ["-ForceWithLease"], "main"),
])
def test_workflow_publishes_only_its_explicit_branch_without_tags(
    git_sandbox, workflow, arguments, target
):
    """Branch publishing overrides inherited follow-tags and broad push refspecs."""

    git_sandbox.git("tag", "-a", "preserve-release-tag", "-m", "Private test tag")
    git_sandbox.git("config", "push.followTags", "true")
    git_sandbox.git("config", "push.recurseSubmodules", "on-demand")
    git_sandbox.git("config", "fetch.prune", "true")
    git_sandbox.git("config", "fetch.pruneTags", "true")
    git_sandbox.git("config", "remote.origin.push", "refs/*:refs/*")
    exercises_rebase = workflow == "git-push-temp.ps1" and "-ForceRemote" not in arguments
    if exercises_rebase:
        git_sandbox.git("switch", "-c", "upstream-history")
        (git_sandbox.root / "README.md").write_text("Published work\n", encoding="utf-8")
        git_sandbox.git("add", "README.md")
        git_sandbox.git("commit", "-m", "Published upstream work")
        git_sandbox.git("update-ref", "refs/remotes/origin/temp", "HEAD")
        git_sandbox.git("switch", "temp")
        (git_sandbox.root / "index.html").write_text("Local work\n", encoding="utf-8")
    completed, commands = git_sandbox.run(workflow, arguments)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    git_commands = _git_commands(commands)
    pushes = [arguments for arguments in git_commands if arguments[0] == "push"]
    assert len(pushes) == 1
    assert "--no-follow-tags" in pushes[0]
    assert "--no-recurse-submodules" in pushes[0]
    assert f"refs/heads/temp:refs/heads/{target}" in pushes[0]
    assert "--tags" not in pushes[0] and "--mirror" not in pushes[0]
    assert not any("refs/tags" in argument for argument in pushes[0])
    fetches = [arguments for arguments in git_commands if arguments[0] == "fetch"]
    assert fetches
    expected_fetch_flags = {
        "--no-tags", "--no-prune", "--no-prune-tags",
        "--no-recurse-submodules", "--refmap=",
    }
    assert all(expected_fetch_flags <= set(arguments) for arguments in fetches)
    if exercises_rebase:
        assert (git_sandbox.root / "README.md").read_text(encoding="utf-8") == "Published work\n"
        assert (git_sandbox.root / "index.html").read_text(encoding="utf-8") == "Local work\n"
        assert git_sandbox.git("rev-parse", "HEAD^") == git_sandbox.git("rev-parse", "origin/temp")
        assert git_sandbox.git("status", "--porcelain") == ""
        assert any(arguments[:1] == ["commit"] for arguments in git_commands)
        assert ["rebase", "refs/remotes/origin/temp"] in git_commands
    for command in commands:
        if command["tool"] == "git":
            # Initial caller discovery is intentionally relative to the caller.
            assert (
                command["args"] == ["rev-parse", "--show-toplevel"]
                or command["args"][:2] == ["-C", str(git_sandbox.root)]
            )


@pytest.mark.parametrize("force", [False, True])
def test_release_refuses_unpublished_temp_even_with_force(git_sandbox, force):
    """A release must use the reviewed remote temp, including force-with-lease."""

    git_sandbox.git("commit", "--allow-empty", "-m", "Unpublished local work")
    before = git_sandbox.snapshot()
    completed, commands = git_sandbox.run(
        "git-release-main.ps1", ["-ForceWithLease"] if force else [],
    )
    assert completed.returncode != 0
    assert git_sandbox.snapshot() == before
    assert not any(arguments[0] == "push" for arguments in _git_commands(commands))


def test_normal_release_preserves_a_commit_existing_only_on_remote_main(git_sandbox):
    """The migration's remote CNAME deletion cannot be silently overwritten."""

    git_sandbox.git("switch", "main")
    git_sandbox.git("commit", "--allow-empty", "-m", "Delete CNAME on GitHub")
    git_sandbox.git("update-ref", "refs/remotes/origin/main", "HEAD")
    git_sandbox.git("switch", "temp")
    before = git_sandbox.snapshot()
    completed, commands = git_sandbox.run("git-release-main.ps1")
    assert completed.returncode != 0
    assert git_sandbox.snapshot() == before
    assert not any(arguments[0] == "push" for arguments in _git_commands(commands))


@pytest.mark.parametrize("force", [False, True])
def test_baseline_preserves_unpublished_work_unless_force_is_explicit(git_sandbox, force):
    """A clean working tree does not make unpublished temp commits disposable."""

    published_head = git_sandbox.git("rev-parse", "origin/temp")
    git_sandbox.git("commit", "--allow-empty", "-m", "Unpublished local work")
    unpublished_head = git_sandbox.git("rev-parse", "HEAD")
    completed, commands = git_sandbox.run(
        "git-baseline-temp.ps1", ["-Force"] if force else [],
    )
    assert (completed.returncode == 0) is force, completed.stdout + completed.stderr
    assert git_sandbox.git("rev-parse", "HEAD") == (
        published_head if force else unpublished_head
    )
    assert not any(arguments[0] == "push" for arguments in _git_commands(commands))


def test_guard_supports_a_linked_worktree_without_treating_git_as_a_directory(git_sandbox):
    """Use Git's actual worktree layout when locating safety/state information."""

    linked_root = git_sandbox.scratch / "linked website checkout"
    git_sandbox.git("worktree", "add", "--detach", str(linked_root), "HEAD")
    linked_sandbox = GitSandbox(
        linked_root, git_sandbox.scratch, git_sandbox.environment,
        git_sandbox.git_executable, git_sandbox.powershell_executable,
    )
    assert (linked_root / ".git").is_file()
    completed, _ = linked_sandbox.run()
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_linked_worktree_rebase_state_blocks_push_before_branch_changes(git_sandbox):
    """State hidden behind a linked .git file must block detached-HEAD recovery."""

    linked_root = git_sandbox.scratch / "linked website checkout"
    git_sandbox.git("worktree", "add", "--detach", str(linked_root), "HEAD")
    linked_sandbox = GitSandbox(
        linked_root, git_sandbox.scratch, git_sandbox.environment,
        git_sandbox.git_executable, git_sandbox.powershell_executable,
    )
    rebase_path = Path(linked_sandbox.git(
        "rev-parse", "--path-format=absolute", "--git-path", "rebase-merge",
    ))
    rebase_path.mkdir()
    original_head = linked_sandbox.git("rev-parse", "HEAD")
    completed, commands = linked_sandbox.run(
        "git-push-temp.ps1", ["-Message", "Safety regression", "-ForceRemote"],
    )
    assert completed.returncode != 0
    assert linked_sandbox.git("rev-parse", "HEAD") == original_head
    assert not any(arguments[0] in {"fetch", "push", "switch", "rebase", "reset"}
                   or (arguments[0] == "branch" and "-f" in arguments)
                   for arguments in _git_commands(commands))


@pytest.mark.parametrize("has_divergent_temp", [False, True], ids=["ancestor", "divergent"])
def test_detached_head_recovery_preserves_existing_temp_history(
    git_sandbox, has_divergent_temp
):
    """Recover detached descendants while refusing to discard separate temp work."""

    common_head = git_sandbox.git("rev-parse", "HEAD")
    if has_divergent_temp:
        git_sandbox.git("commit", "--allow-empty", "-m", "Separate temp work")
    original_temp = git_sandbox.git("rev-parse", "temp")
    git_sandbox.git("switch", "--detach", common_head)
    git_sandbox.git("commit", "--allow-empty", "-m", "Detached website work")
    detached_head = git_sandbox.git("rev-parse", "HEAD")
    completed, commands = git_sandbox.run(
        "git-push-temp.ps1", ["-Message", "Recover detached website work"],
    )
    assert (completed.returncode == 0) is not has_divergent_temp, completed.stdout + completed.stderr
    assert git_sandbox.git("rev-parse", "HEAD") == detached_head
    if has_divergent_temp:
        assert git_sandbox.git("rev-parse", "temp") == original_temp
        assert git_sandbox.git("branch", "--show-current") == ""
        assert not any(arguments[0] in {"fetch", "push", "switch"}
                       or arguments[:2] == ["branch", "-f"]
                       for arguments in _git_commands(commands))
    else:
        assert git_sandbox.git("rev-parse", "temp") == detached_head
        assert git_sandbox.git("branch", "--show-current") == "temp"
        assert ["branch", "-f", "temp", "HEAD"] in _git_commands(commands)
        assert any(arguments[0] == "push" for arguments in _git_commands(commands))


def test_visibility_change_after_commit_retains_work_and_blocks_publication(git_sandbox):
    """Recheck live public visibility after local commit instead of trusting initial metadata."""

    original_head = git_sandbox.git("rev-parse", "HEAD")
    (git_sandbox.root / "index.html").write_text("New website work\n", encoding="utf-8")
    completed, commands = git_sandbox.run(
        "git-push-temp.ps1", ["-Message", "Preserved website work"],
        metadata_responses=[WEBSITE_METADATA, {**WEBSITE_METADATA, "private": True}],
    )
    assert completed.returncode != 0
    assert git_sandbox.git("rev-parse", "HEAD") != original_head, completed.stdout + completed.stderr
    assert git_sandbox.git("log", "-1", "--format=%s") == "Preserved website work"
    assert (git_sandbox.root / "index.html").read_text(encoding="utf-8") == "New website work\n"
    git_commands = _git_commands(commands)
    assert any(arguments[0] == "commit" for arguments in git_commands)
    assert not any(arguments[0] == "push" for arguments in git_commands)
    assert len([command for command in commands if command["tool"] == "gh"]) == 2


def test_force_baseline_aborts_linked_worktree_rebase_through_git(git_sandbox):
    """Recover a real conflict without deleting shared metadata or changing main."""

    conflict_file = git_sandbox.root / "README.md"
    conflict_file.write_text("Common baseline\n", encoding="utf-8")
    git_sandbox.git("add", "README.md")
    git_sandbox.git("commit", "-m", "Common conflict baseline")
    git_sandbox.git("branch", "-f", "main", "HEAD")
    git_sandbox.git("switch", "main")
    main_head = git_sandbox.git("rev-parse", "HEAD")
    linked_root = git_sandbox.scratch / "linked website checkout"
    git_sandbox.git("worktree", "add", str(linked_root), "temp")
    linked_sandbox = GitSandbox(
        linked_root, git_sandbox.scratch, git_sandbox.environment,
        git_sandbox.git_executable, git_sandbox.powershell_executable,
    )
    linked_git_file = (linked_root / ".git").read_bytes()
    git_sandbox.git("switch", "-c", "upstream-history")
    conflict_file.write_text("Published conflicting work\n", encoding="utf-8")
    git_sandbox.git("add", "README.md")
    git_sandbox.git("commit", "-m", "Published conflicting work")
    git_sandbox.git("update-ref", "refs/remotes/origin/temp", "HEAD")
    published_head = git_sandbox.git("rev-parse", "HEAD")
    git_sandbox.git("switch", "main")
    (linked_root / "README.md").write_text("Unpublished conflicting work\n", encoding="utf-8")
    linked_sandbox.git("add", "README.md")
    linked_sandbox.git("commit", "-m", "Unpublished conflicting work")
    conflict = subprocess.run(
        [git_sandbox.git_executable, "-C", str(linked_root), "rebase", "origin/temp"],
        env=git_sandbox.environment, capture_output=True, text=True, timeout=30,
        check=False,
    )
    assert conflict.returncode != 0
    assert "CONFLICT" in conflict.stdout + conflict.stderr
    completed, commands = linked_sandbox.run("git-baseline-temp.ps1", ["-Force"])
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert ["rebase", "--abort"] in _git_commands(commands)
    assert linked_sandbox.git("rev-parse", "HEAD") == published_head
    assert linked_sandbox.git("status", "--porcelain") == ""
    assert (linked_root / ".git").read_bytes() == linked_git_file
    assert git_sandbox.git("rev-parse", "HEAD") == main_head
    assert git_sandbox.git("status", "--porcelain") == ""
    assert conflict_file.read_text(encoding="utf-8") == "Common baseline\n"


@pytest.mark.parametrize("target", ["temp", "main"])
def test_recorded_transport_preserves_unrelated_branches_and_tags(git_sandbox, target):
    """Replay exact production arguments against a local bare repo, never GitHub."""

    git_sandbox.git("tag", "-a", "local-only-tag", "-m", "Keep private tag local")
    git_sandbox.git("config", "fetch.prune", "true")
    git_sandbox.git("config", "fetch.pruneTags", "true")
    git_sandbox.git("config", "push.followTags", "true")
    git_sandbox.git("config", "push.recurseSubmodules", "on-demand")
    git_sandbox.git("config", "remote.origin.push", "refs/*:refs/*")
    git_sandbox.git("config", "--add", "remote.origin.fetch", "+refs/tags/*:refs/tags/*")
    completed, commands = git_sandbox.run(
        "git-push-temp.ps1" if target == "temp" else "git-release-main.ps1",
        ["-Message", "Transport argument verification"] if target == "temp" else [],
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    transport_commands = [
        arguments for arguments in _git_commands(commands)
        if arguments[0] in {"fetch", "push"}
    ]
    assert [arguments[0] for arguments in transport_commands] == ["fetch", "push"]

    # Only after the guarded workflow has finished, replace this disposable
    # fixture's origin with a local bare repository for transport verification.
    bare_remote = git_sandbox.scratch / "local transport destination.git"
    git_sandbox.git("init", "--bare", str(bare_remote))
    git_sandbox.git("push", "--no-follow-tags", "--no-recurse-submodules", str(bare_remote),
                    "refs/heads/temp:refs/heads/temp", "refs/heads/main:refs/heads/main")
    baseline = git_sandbox.git("rev-parse", "HEAD")
    git_sandbox.git("-C", str(bare_remote), "update-ref", "refs/tags/remote-only-tag", baseline)
    git_sandbox.git("-C", str(bare_remote), "update-ref", "refs/heads/remote-unrelated", baseline)
    git_sandbox.git("branch", "local-unrelated")
    git_sandbox.git("update-ref", "refs/remotes/origin/stale-unrelated", baseline)
    git_sandbox.git("remote", "set-url", "origin", str(bare_remote))
    git_sandbox.git(*transport_commands[0])
    assert git_sandbox.git("tag", "--list") == "local-only-tag"
    assert git_sandbox.git("rev-parse", "origin/stale-unrelated") == baseline
    assert git_sandbox.git("rev-parse", "local-unrelated") == baseline
    git_sandbox.git("commit", "--allow-empty", "-m", "New branch-only publication")
    published_head = git_sandbox.git("rev-parse", "HEAD")
    git_sandbox.git(*transport_commands[1])
    assert git_sandbox.git("-C", str(bare_remote), "tag", "--list") == "remote-only-tag"
    assert git_sandbox.git("-C", str(bare_remote), "rev-parse", f"refs/heads/{target}") == published_head
    untouched = "main" if target == "temp" else "temp"
    assert git_sandbox.git("-C", str(bare_remote), "rev-parse", f"refs/heads/{untouched}") == baseline
    assert git_sandbox.git("-C", str(bare_remote), "rev-parse", "refs/heads/remote-unrelated") == baseline
    assert git_sandbox.git("-C", str(bare_remote), "branch", "--list", "local-unrelated") == ""


def test_force_baseline_preserves_allowed_untracked_files(git_sandbox):
    """Reset tracked state without silently cleaning unrelated untracked work."""

    guide = git_sandbox.root / "scripts" / "README.md"
    guide.write_text("Uncommitted website workflow notes\n", encoding="utf-8")
    published_head = git_sandbox.git("rev-parse", "origin/temp")
    completed, commands = git_sandbox.run("git-baseline-temp.ps1", ["-Force"])
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert git_sandbox.git("rev-parse", "HEAD") == published_head
    assert guide.read_text(encoding="utf-8") == "Uncommitted website workflow notes\n"
    assert "?? scripts/README.md" in git_sandbox.git("status", "--porcelain")
    assert not any(arguments[0] == "clean" for arguments in _git_commands(commands))


@pytest.mark.parametrize("force", [False, True])
def test_temp_push_commits_reviewed_website_sources_and_imported_assets(git_sandbox, force):
    """The explicit website inventory permits the reviewed public-site backup."""

    files = {
        ".github/DISCUSSION_TEMPLATE/report-a-bug-or-concern.yml": b"title: Website report\n",
        "scripts/demo_walkthrough.py": b"# Public website renderer fixture\n",
        "content/generated/manual.en.md": b"# Imported public manual fixture\n",
        "content/generated/assets/screenshots/demo-1-map.jpg": b"Public screenshot fixture\n",
        "site/demos/milazzo_tx_buddy/walkthrough.en.md": b"# Website walkthrough fixture\n",
    }
    for relative_path, contents in files.items():
        path = git_sandbox.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(contents)
    original_head = git_sandbox.git("rev-parse", "HEAD")
    arguments = ["-Message", "Back up reviewed website files"]
    if force:
        arguments.append("-ForceRemote")
    completed, commands = git_sandbox.run("git-push-temp.ps1", arguments)

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert git_sandbox.git("log", "-1", "--format=%s") == "Back up reviewed website files"
    assert set(git_sandbox.git("diff", "--name-only", original_head, "HEAD").splitlines()) == set(files)
    assert git_sandbox.git("status", "--porcelain") == ""
    for relative_path, contents in files.items():
        assert (git_sandbox.root / relative_path).read_bytes() == contents
        assert git_sandbox.git("show", f"HEAD:{relative_path}") == contents.decode().strip()
    pushes = [arguments for arguments in _git_commands(commands) if arguments[0] == "push"]
    assert len(pushes) == 1
    assert "refs/heads/temp:refs/heads/temp" in pushes[0]


def test_hashed_public_assets_keep_exact_bytes_with_autocrlf_enabled(git_sandbox):
    """Backup and checkout preserve manifest/evidence bytes under Windows defaults."""

    shutil.copy2(SCRIPTS_ROOT.parent / ".gitattributes", git_sandbox.root / ".gitattributes")
    git_sandbox.git("config", "core.autocrlf", "true")
    files = {
        "content/generated/manual.en.md": b"# Public manual\nPreserve LF bytes.\n",
        "content/generated/manual.de.md": b"# Public manual\r\nPreserve CRLF bytes.\r\n",
        "site/assets/flags/en.svg": b"<svg>\n</svg>\n",
        "site/assets/flags/de.svg": b"<svg>\r\n</svg>\r\n",
        "site/demos/milazzo_tx_buddy/walkthrough.en.md": b"# Walkthrough\nPreserve LF bytes.\n",
        "site/demos/milazzo_tx_buddy/walkthrough.de.md": b"# Walkthrough\r\nPreserve CRLF bytes.\r\n",
    }
    for relative_path, contents in files.items():
        path = git_sandbox.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(contents)
    completed, _ = git_sandbox.run(
        "git-push-temp.ps1", ["-Message", "Preserve hashed public asset bytes"],
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    for relative_path, contents in files.items():
        blob = subprocess.run(
            [git_sandbox.git_executable, "-C", str(git_sandbox.root),
             "cat-file", "blob", f"HEAD:{relative_path}"],
            env=git_sandbox.environment, capture_output=True, timeout=30, check=False,
        )
        assert blob.returncode == 0, blob.stderr
        assert blob.stdout == contents
        (git_sandbox.root / relative_path).unlink()
    git_sandbox.git("checkout", "HEAD", "--", *files)
    for relative_path, contents in files.items():
        assert (git_sandbox.root / relative_path).read_bytes() == contents
    assert git_sandbox.git("status", "--porcelain") == ""


@pytest.mark.parametrize(("workflow", "arguments"), WORKFLOWS)
@pytest.mark.parametrize("relative_path", [
    "scripts/unreviewed.py",
    "content/generated/app.py",
    "site/private-source.py",
])
def test_nested_unapproved_paths_block_every_force_mode(
    git_sandbox, workflow, arguments, relative_path
):
    """Reviewed neighboring files never grant blanket directory permission."""

    path = git_sandbox.root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# Unreviewed source fixture\n", encoding="utf-8")
    before = git_sandbox.snapshot()
    completed, commands = git_sandbox.run(workflow, arguments)
    _assert_guard_rejected(git_sandbox, before, completed, commands)
    assert relative_path in completed.stdout + completed.stderr


@pytest.mark.parametrize(("workflow", "arguments"), WORKFLOWS)
@pytest.mark.parametrize("state", ["untracked", "staged", "removed-from-history-tip"])
def test_disallowed_application_path_blocks_every_force_mode(
    git_sandbox, workflow, arguments, state
):
    """An app file must never be staged, discarded, or published by a helper."""

    disallowed_path = git_sandbox.root / "app.py"
    disallowed_path.write_text("# Private application stand-in\n", encoding="utf-8")
    if state != "untracked":
        git_sandbox.git("add", "app.py")
    if state == "removed-from-history-tip":
        git_sandbox.git("commit", "-m", "Accidentally copied private application")
        git_sandbox.git("rm", "app.py")
        git_sandbox.git("commit", "-m", "Remove private application from current tree")
        assert not disallowed_path.exists()
    before = git_sandbox.snapshot()
    completed, commands = git_sandbox.run(workflow, arguments)
    _assert_guard_rejected(git_sandbox, before, completed, commands)
    assert "app.py" in completed.stdout + completed.stderr


@pytest.mark.parametrize(("workflow", "arguments"), WORKFLOWS)
def test_foreign_history_is_rejected_even_when_merge_tree_is_website_only(
    git_sandbox, workflow, arguments
):
    """An ours merge cannot smuggle unrelated application ancestors into public Git."""

    baseline_tree = git_sandbox.git("rev-parse", "HEAD^{tree}")
    # A parentless commit using only allowed paths still represents a second,
    # unrelated history. Its files need not differ for publication to be unsafe.
    foreign_root = git_sandbox.git("commit-tree", baseline_tree, "-m", "Unrelated history root")
    git_sandbox.git("merge", "--allow-unrelated-histories", "--no-ff", "-s", "ours",
                    foreign_root, "-m", "Keep website tree but import foreign ancestry")
    assert git_sandbox.git("rev-parse", "HEAD^{tree}") == baseline_tree
    assert len(git_sandbox.git("rev-list", "--max-parents=0", "HEAD").splitlines()) == 2
    before = git_sandbox.snapshot()
    completed, commands = git_sandbox.run(workflow, arguments)
    _assert_guard_rejected(git_sandbox, before, completed, commands)


@pytest.mark.parametrize("mode", ["120000", "160000"], ids=["symlink", "submodule"])
@pytest.mark.parametrize(("workflow", "arguments"), WORKFLOWS)
def test_staged_nonregular_mode_is_rejected_for_an_allowed_filename(
    git_sandbox, workflow, arguments, mode
):
    """A permitted path cannot refer to a symlink or another repository."""

    object_id = git_sandbox.git("rev-parse", "HEAD" if mode == "160000" else "HEAD:index.html")
    git_sandbox.git("update-index", "--cacheinfo", f"{mode},{object_id},index.html")
    before = git_sandbox.snapshot()
    completed, commands = git_sandbox.run(workflow, arguments)
    _assert_guard_rejected(git_sandbox, before, completed, commands)


@pytest.mark.parametrize("mode", ["120000", "160000"], ids=["symlink", "submodule"])
def test_removed_nonregular_mode_is_rejected_in_reachable_history(git_sandbox, mode):
    """Deleting a symlink/submodule from the current tree does not erase its history."""

    original_blob = git_sandbox.git("rev-parse", "HEAD:index.html")
    object_id = git_sandbox.git("rev-parse", "HEAD") if mode == "160000" else original_blob
    git_sandbox.git("update-index", "--cacheinfo", f"{mode},{object_id},index.html")
    git_sandbox.git("commit", "-m", "Introduce disallowed historical mode")
    git_sandbox.git("update-index", "--cacheinfo", f"100644,{original_blob},index.html")
    git_sandbox.git("commit", "-m", "Restore ordinary current website file")
    before = git_sandbox.snapshot()
    completed, commands = git_sandbox.run("git-push-temp.ps1", ["-Message", "Test", "-ForceRemote"])
    _assert_guard_rejected(git_sandbox, before, completed, commands)


def test_untracked_ignored_scratch_is_not_staged_or_published(git_sandbox):
    """Ignored local scratch does not need to become a public allowlist entry."""

    (git_sandbox.root / ".git" / "info" / "exclude").write_text("/private-scratch/\n", encoding="utf-8")
    scratch_path = git_sandbox.root / "private-scratch" / "app.py"
    scratch_path.parent.mkdir()
    scratch_path.write_text("# Ignored local fixture\n", encoding="utf-8")
    (git_sandbox.root / "index.html").write_text("<html>Updated website</html>\n", encoding="utf-8")
    completed, commands = git_sandbox.run("git-push-temp.ps1", ["-Message", "Allowed website edit"])
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert scratch_path.read_text(encoding="utf-8") == "# Ignored local fixture\n"
    assert "private-scratch" not in git_sandbox.git("ls-tree", "-r", "--name-only", "HEAD")
    assert any(arguments[0] == "push" for arguments in _git_commands(commands))


@pytest.mark.parametrize(("workflow", "arguments"), WORKFLOWS)
def test_missing_remote_temp_reports_setup_without_reset_or_push(git_sandbox, workflow, arguments):
    """A fresh website needs a published temp branch before routine helpers run."""

    git_sandbox.git("update-ref", "-d", "refs/remotes/origin/temp")
    before = git_sandbox.snapshot()
    completed, commands = git_sandbox.run(workflow, arguments, fetch_exit_code=1)
    assert completed.returncode != 0
    assert git_sandbox.snapshot() == before
    error = (completed.stdout + completed.stderr).lower()
    assert "temp" in error and any(word in error for word in ("setup", "create", "exist", "initialize"))
    assert not any(arguments[0] in {"push", "reset"} for arguments in _git_commands(commands))


@pytest.mark.parametrize("workflow", ["git-push-temp.ps1", "git-release-main.ps1"])
def test_missing_local_temp_is_not_created_from_a_stale_main(git_sandbox, workflow):
    """Publishing cannot silently choose whichever commit local main contains."""

    git_sandbox.git("switch", "main")
    git_sandbox.git("branch", "-D", "temp")
    before = git_sandbox.snapshot()
    completed, commands = git_sandbox.run(
        workflow, ["-Message", "Test"] if workflow == "git-push-temp.ps1" else [],
    )
    assert completed.returncode != 0
    assert git_sandbox.snapshot() == before
    assert "temp" in (completed.stdout + completed.stderr).lower()
    assert not any(arguments[0] in {"push", "reset", "switch"} for arguments in _git_commands(commands))


def test_release_uses_published_temp_and_ignores_stale_local_main(git_sandbox):
    """Local main is not the release baseline and remains untouched."""

    published_head = git_sandbox.git("rev-parse", "origin/temp")
    original_root = git_sandbox.git("rev-list", "--max-parents=0", "HEAD")
    git_sandbox.git("branch", "-f", "main", original_root)
    completed, commands = git_sandbox.run("git-release-main.ps1")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert git_sandbox.git("rev-parse", "main") == original_root
    assert git_sandbox.git("rev-parse", "temp") == published_head
    assert git_sandbox.git("branch", "--show-current") == "temp"
    pushes = [arguments for arguments in _git_commands(commands) if arguments[0] == "push"]
    assert len(pushes) == 1
    assert "refs/heads/temp:refs/heads/main" in pushes[0]


@pytest.mark.parametrize("remote_branch", ["temp", "main"])
def test_fetched_disallowed_history_is_rejected_before_release(git_sandbox, remote_branch):
    """Freshly fetched branch history receives the same content guard as local HEAD."""

    git_sandbox.git("switch", "-c", "untrusted-upstream")
    (git_sandbox.root / "app.py").write_text("# Untrusted published history\n", encoding="utf-8")
    git_sandbox.git("add", "app.py")
    git_sandbox.git("commit", "-m", "Disallowed upstream content")
    git_sandbox.git("update-ref", f"refs/remotes/origin/{remote_branch}", "HEAD")
    git_sandbox.git("switch", "temp")
    before = git_sandbox.snapshot()
    completed, commands = git_sandbox.run("git-release-main.ps1", ["-ForceWithLease"])
    assert completed.returncode != 0
    assert git_sandbox.snapshot() == before
    assert "app.py" in completed.stdout + completed.stderr
    assert not any(arguments[0] == "push" for arguments in _git_commands(commands))


@pytest.mark.parametrize("mechanism", ["replace", "grafts", "shallow"])
def test_history_rewriting_mechanisms_cannot_hide_original_roots(git_sandbox, mechanism):
    """Replacement objects, grafts, and shallow boundaries must fail closed."""

    root_commit = git_sandbox.git("rev-list", "--max-parents=0", "HEAD")
    if mechanism == "replace":
        alternate_root = git_sandbox.git("commit-tree", "HEAD^{tree}", "-m", "Replacement root")
        git_sandbox.git("replace", root_commit, alternate_root)
    elif mechanism == "grafts":
        (git_sandbox.root / ".git" / "info" / "grafts").write_text(
            git_sandbox.git("rev-parse", "HEAD") + "\n", encoding="utf-8",
        )
    else:
        (git_sandbox.root / ".git" / "shallow").write_text(
            git_sandbox.git("rev-parse", "HEAD") + "\n", encoding="utf-8",
        )
    before = git_sandbox.snapshot()
    completed, commands = git_sandbox.run("git-push-temp.ps1", ["-Message", "Test", "-ForceRemote"])
    _assert_guard_rejected(git_sandbox, before, completed, commands)
