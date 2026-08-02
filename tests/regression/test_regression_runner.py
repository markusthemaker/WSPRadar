"""Regression contracts for the foreground-only Windows test runner."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPOSITORY_ROOT / "scripts" / "regression_test_chunks.json"
RUNNER_PATH = REPOSITORY_ROOT / "scripts" / "run_regression.ps1"
WINDOWS_LAUNCHER_PATH = REPOSITORY_ROOT / "scripts" / "run_regression.cmd"
EXPECTED_CHUNK_IDS = [1, 2, 3, 4, 5]


def _load_chunk_manifest() -> dict:
    """Load the checked-in serial fallback partition."""

    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _discover_regression_modules() -> set[str]:
    """Return every module matching either of pytest's default file patterns."""

    regression_root = REPOSITORY_ROOT / "tests" / "regression"
    discovered_paths = {
        path.relative_to(REPOSITORY_ROOT).as_posix()
        for pattern in ("test_*.py", "*_test.py")
        for path in regression_root.rglob(pattern)
        if path.is_file()
    }
    return discovered_paths


def test_regression_chunk_manifest_is_fixed_nonempty_and_disjoint():
    """Keep five explicit serial chunks with one owner per test module."""

    manifest = _load_chunk_manifest()
    chunks = manifest["chunks"]
    chunk_ids = [chunk["id"] for chunk in chunks]
    assigned_paths = [path for chunk in chunks for path in chunk["tests"]]

    assert manifest["schema_version"] == 1
    assert manifest["chunk_count"] == len(EXPECTED_CHUNK_IDS)
    assert chunk_ids == EXPECTED_CHUNK_IDS
    assert all(chunk["tests"] for chunk in chunks)
    assert len(assigned_paths) == len(set(assigned_paths))


def test_regression_chunk_manifest_exactly_covers_pytest_modules():
    """Fail when a new, renamed, duplicated, or removed module is not assigned."""

    manifest = _load_chunk_manifest()
    assigned_paths = {
        path for chunk in manifest["chunks"] for path in chunk["tests"]
    }

    assert assigned_paths == _discover_regression_modules()


def test_regression_chunk_paths_are_normalized_and_scoped():
    """Keep manifest paths relative, traversal-free, and inside regression tests."""

    manifest = _load_chunk_manifest()
    for chunk in manifest["chunks"]:
        for relative_path in chunk["tests"]:
            parsed_path = PurePosixPath(relative_path)
            assert str(parsed_path) == relative_path
            assert not parsed_path.is_absolute()
            assert parsed_path.parts[:2] == ("tests", "regression")
            assert ".." not in parsed_path.parts
            assert parsed_path.name.startswith("test_") or parsed_path.name.endswith(
                "_test.py"
            )


def test_regression_runner_stays_foreground_serial_and_unbuffered():
    """Prevent detached supervision and parallel pytest workers from returning."""

    runner_source = RUNNER_PATH.read_text(encoding="utf-8")

    for forbidden_launcher in (
        "Start-Process",
        "Start-Job",
        "Tee-Object",
        "RedirectStandardOutput",
        "RedirectStandardError",
    ):
        assert forbidden_launcher not in runner_source

    assert '& $pythonPath @pythonArguments' in runner_source
    assert '@("-u", "-m", "pytest", "-q")' in runner_source
    assert "$scriptExitCode = $LASTEXITCODE" in runner_source
    assert 'Write-Host "pytest exited with code $scriptExitCode."' in runner_source
    assert "Parallel pytest workers are not supported" in runner_source


def test_windows_launcher_bypasses_policy_only_for_the_checked_in_runner():
    """Keep script-policy handling process-local while preserving its exit code."""

    launcher_source = WINDOWS_LAUNCHER_PATH.read_text(encoding="utf-8")

    assert "powershell.exe" in launcher_source
    assert "-NoProfile -ExecutionPolicy Bypass -File" in launcher_source
    assert '"%~dp0run_regression.ps1" %*' in launcher_source
    assert "exit /b %ERRORLEVEL%" in launcher_source
    assert "Set-ExecutionPolicy" not in launcher_source


def test_contributor_guidance_uses_foreground_and_scopes_costly_tests():
    """Keep detached supervision retired without taxing unrelated focused work."""

    contributor_guidance = (REPOSITORY_ROOT / "AGENTS.md").read_text(
        encoding="utf-8"
    )
    repository_guide = (REPOSITORY_ROOT / "AGENT_README.md").read_text(
        encoding="utf-8"
    )

    for guidance in (contributor_guidance, repository_guide):
        assert ".\\scripts\\run_regression.cmd" in guidance
        assert "pytest-xdist" in guidance

    assert "launch the process hidden" not in contributor_guidance
    assert "run figure and plot rendering tests only" in contributor_guidance
    assert "These focused-scope rules do not override" in contributor_guidance
