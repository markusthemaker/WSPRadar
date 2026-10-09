"""Regression contracts for the foreground-only Windows test runner."""

from __future__ import annotations

import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys

import pytest


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


@pytest.mark.skipif(os.name != "nt", reason="Exercises the native Windows launcher")
@pytest.mark.parametrize(
    ("manifest_change", "expected_error"),
    (
        ("none", None),
        ("unassigned", "unassigned:"),
        ("duplicate", "assigned more than once:"),
        ("stale", "missing or stale:"),
    ),
)
def test_windows_manifest_validation_needs_no_venv_and_propagates_failures(
    tmp_path, manifest_change, expected_error
):
    """Exercise the CI command against valid and broken isolated checkouts."""

    checkout_root = tmp_path / "checkout with spaces"
    scripts_root = checkout_root / "scripts"
    scripts_root.mkdir(parents=True)
    shutil.copy2(RUNNER_PATH, scripts_root / RUNNER_PATH.name)
    shutil.copy2(WINDOWS_LAUNCHER_PATH, scripts_root / WINDOWS_LAUNCHER_PATH.name)

    manifest = _load_chunk_manifest()
    for chunk in manifest["chunks"]:
        for relative_test_path in chunk["tests"]:
            test_path = checkout_root / relative_test_path
            test_path.parent.mkdir(parents=True, exist_ok=True)
            test_path.touch()

    if manifest_change == "unassigned":
        # Cover pytest's other default discovery pattern as well as test_*.py.
        (checkout_root / "tests/regression/unassigned_test.py").touch()
    elif manifest_change == "duplicate":
        manifest["chunks"][1]["tests"].append(manifest["chunks"][0]["tests"][0])
    elif manifest_change == "stale":
        manifest["chunks"][0]["tests"].append("tests/regression/test_missing.py")

    (scripts_root / MANIFEST_PATH.name).write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    assert not (checkout_root / ".venv").exists()

    validation = subprocess.run(
        [
            os.environ.get("COMSPEC", "cmd.exe"),
            "/d",
            "/c",
            r"scripts\run_regression.cmd",
            "-ValidateChunks",
        ],
        cwd=checkout_root,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    validation_output = validation.stdout + validation.stderr

    if expected_error is None:
        assert validation.returncode == 0, validation_output
        assert "Regression chunk manifest valid:" in validation_output
    else:
        assert validation.returncode != 0, validation_output
        assert expected_error in validation_output
    assert "Repository Python interpreter not found" not in validation_output
    assert not (checkout_root / ".test").exists()


def _isolated_executing_runner(tmp_path):
    """Use the native launcher with a pytest argument probe in a tiny checkout."""
    checkout_root = tmp_path / "runner checkout with spaces"
    scripts_root = checkout_root / "scripts"
    scripts_root.mkdir(parents=True)
    runner_source = RUNNER_PATH.read_text(encoding="utf-8")
    original_python_assignment = '$pythonPath = Join-Path $repoRoot ".venv\\Scripts\\python.exe"'
    assert runner_source.count(original_python_assignment) == 1
    python_literal = str(Path(sys.executable)).replace("'", "''")
    (scripts_root / RUNNER_PATH.name).write_text(
        runner_source.replace(original_python_assignment, f"$pythonPath = '{python_literal}'"),
        encoding="utf-8",
    )
    shutil.copy2(WINDOWS_LAUNCHER_PATH, scripts_root / WINDOWS_LAUNCHER_PATH.name)
    shutil.copy2(REPOSITORY_ROOT / "pytest.ini", checkout_root / "pytest.ini")
    chunks = []
    for chunk_id in EXPECTED_CHUNK_IDS:
        relative_path = f"tests/regression/test_probe_{chunk_id}.py"
        test_path = checkout_root / relative_path
        test_path.parent.mkdir(parents=True, exist_ok=True)
        test_path.touch()
        chunks.append({"id": chunk_id, "tests": [relative_path]})
    (scripts_root / MANIFEST_PATH.name).write_text(
        json.dumps({"schema_version": 1, "chunk_count": 5, "chunks": chunks}),
        encoding="utf-8",
    )
    # Parse pytest's real options without collecting or executing another suite.
    (checkout_root / "pytest.py").write_text(
        "import json, os, sys\n"
        "from pathlib import Path\n"
        "sys.path = [entry for entry in sys.path if Path(entry or '.').resolve() != Path.cwd()]\n"
        "from _pytest.config import get_config\n"
        "config = get_config()\n"
        "config.parse(sys.argv[1:])\n"
        "probe = {'arguments': sys.argv[1:], 'targets': config.args, "
        "'basetemp': str(config.getoption('basetemp')), "
        "'cache_dir': str(config.getini('cache_dir')), "
        "'cache_precreated': Path(config.getini('cache_dir')).is_dir(), "
        "'keyword': config.getoption('keyword')}\n"
        "Path('runner-probe.json').write_text(json.dumps(probe), encoding='utf-8')\n"
        "raise SystemExit(int(os.environ.get('WSPRADAR_RUNNER_PROBE_EXIT', '0')))\n",
        encoding="utf-8",
    )
    return checkout_root


def _invoke_isolated_runner(checkout_root, *arguments, exit_code=0):
    environment = os.environ.copy()
    environment["WSPRADAR_RUNNER_PROBE_EXIT"] = str(exit_code)
    result = subprocess.run(
        [os.environ.get("COMSPEC", "cmd.exe"), "/d", "/c",
         r"scripts\run_regression.cmd", *arguments],
        cwd=checkout_root, env=environment, capture_output=True,
        text=True, timeout=30, check=False,
    )
    output = result.stdout + result.stderr
    probe_path = checkout_root / "runner-probe.json"
    probe = json.loads(probe_path.read_text(encoding="utf-8")) if probe_path.exists() else None
    return result.returncode, output, probe


@pytest.mark.skipif(os.name != "nt", reason="Exercises the native Windows launcher")
def test_windows_runner_uses_fresh_retained_workspaces_and_preserves_full_default(tmp_path):
    checkout_root = _isolated_executing_runner(tmp_path)
    workspaces = []
    for _ in range(2):
        returncode, output, probe = _invoke_isolated_runner(checkout_root)
        assert returncode == 0, output
        assert probe["targets"] == ["tests\\regression"]
        workspace = Path(probe["basetemp"]).parent
        assert workspace.parent == checkout_root / ".test" / "runs"
        assert Path(probe["cache_dir"]) == workspace / "cache"
        assert probe["cache_precreated"] is True
        assert Path(probe["basetemp"]) == workspace / "temp"
        assert str(workspace) in output
        assert workspace.is_dir()
        (workspace / "retained-evidence.txt").write_text("keep", encoding="utf-8")
        workspaces.append(workspace)
    assert workspaces[0] != workspaces[1]
    assert all((path / "retained-evidence.txt").read_text(encoding="utf-8") == "keep" for path in workspaces)
    assert not (checkout_root / ".test" / "pytest-temp").exists()
    assert not (checkout_root / ".test" / "pytest-cache").exists()


@pytest.mark.skipif(os.name != "nt", reason="Exercises the native Windows launcher")
def test_windows_runner_focuses_native_targets_preserves_options_and_exit_code(tmp_path):
    checkout_root = _isolated_executing_runner(tmp_path)
    targets = ["tests/regression/test_probe_1.py", "tests/regression/test_probe_2.py::test_example[value]"]
    returncode, output, probe = _invoke_isolated_runner(
        checkout_root, "-Focused", *targets, "-k", "example and not skipped", "--tb=short",
        exit_code=7,
    )
    assert returncode == 7, output
    assert probe["targets"] == targets
    assert probe["keyword"] == "example and not skipped"
    assert "--tb=short" in probe["arguments"]
    assert "pytest exited with code 7." in output


@pytest.mark.skipif(os.name != "nt", reason="Exercises the native Windows launcher")
def test_windows_runner_explicit_pytest_paths_override_run_defaults(tmp_path):
    checkout_root = _isolated_executing_runner(tmp_path)
    returncode, output, probe = _invoke_isolated_runner(
        checkout_root, "-Focused", "tests/regression/test_probe_1.py",
        "--basetemp=chosen-temp", "--override-ini=cache_dir=chosen-cache", "--verbose",
    )
    assert returncode == 0, output
    assert Path(probe["basetemp"]).name == "chosen-temp"
    assert probe["cache_dir"] == "chosen-cache"
    assert "--verbose" in probe["arguments"]


@pytest.mark.skipif(os.name != "nt", reason="Exercises the native Windows launcher")
@pytest.mark.parametrize("arguments", [
    ("-Focused",),
    ("-Focused", "-k", "probe"),
    ("-Focused", "missing.py"),
    ("-Focused", "pytest.py"),
    ("-Focused", "tests/regression/../../pytest.py"),
    ("-Focused", "-Chunk", "1", "tests/regression/test_probe_1.py"),
    ("-Focused", "-ValidateChunks"),
    ("-Focused", "tests/regression/test_probe_1.py", "-n", "2"),
])
def test_windows_runner_rejects_invalid_focused_requests_before_execution(tmp_path, arguments):
    checkout_root = _isolated_executing_runner(tmp_path)
    returncode, output, probe = _invoke_isolated_runner(checkout_root, *arguments)
    assert returncode != 0, output
    assert probe is None
    assert not (checkout_root / ".test").exists()


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
