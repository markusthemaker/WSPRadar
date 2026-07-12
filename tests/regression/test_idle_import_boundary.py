"""Regression coverage for the idle Streamlit import boundary."""

import json
import os
from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
AUDIT_RESULT_PREFIX = "WSPRADAR_IDLE_IMPORT_AUDIT="

IDLE_IMPORT_AUDIT_SCRIPT = r'''
import builtins
import importlib
import inspect
import json
from pathlib import Path
import sys

from streamlit.testing.v1 import AppTest


project_root = Path(sys.argv[1]).resolve()
application_roots = {"app.py", "config", "core", "docs", "i18n.py", "ui"}
forbidden_modules = (
    "ui.run_controller",
    "ui.results_export",
    "ui.components.segment_inspector",
    "core.plot_engine",
    "numpy",
    "pandas",
    "matplotlib",
    "requests",
    "cartopy",
)
forbidden_imports = set()
real_import = builtins.__import__
real_import_module = importlib.import_module


def application_origin(module_globals):
    """Return a repository-relative caller only for WSPRadar runtime code."""
    if not isinstance(module_globals, dict):
        return None
    source_path = module_globals.get("__file__")
    if not source_path:
        return None
    try:
        relative_path = Path(source_path).resolve().relative_to(project_root)
    except (OSError, ValueError):
        return None
    if relative_path.parts and relative_path.parts[0] in application_roots:
        return str(relative_path)
    return None


def requested_module_names(name, module_globals, fromlist, level):
    """Resolve the module names represented by one ``__import__`` call."""
    resolved_name = name
    package = (module_globals or {}).get("__package__")
    if level and package:
        try:
            resolved_name = importlib.util.resolve_name(
                "." * level + name,
                package,
            )
        except (ImportError, ValueError):
            pass

    requested_names = {resolved_name}
    for imported_name in fromlist or ():
        if imported_name != "*":
            requested_names.add(
                f"{resolved_name}.{imported_name}"
                if resolved_name
                else imported_name
            )
    return requested_names


def record_forbidden_imports(requested_names, origin):
    """Record forbidden modules requested by one WSPRadar source file."""
    if origin is None:
        return
    for requested_name in requested_names:
        for forbidden_module in forbidden_modules:
            if (
                requested_name == forbidden_module
                or requested_name.startswith(forbidden_module + ".")
            ):
                forbidden_imports.add(
                    (forbidden_module, requested_name, origin)
                )


def audited_import(name, globals=None, locals=None, fromlist=(), level=0):
    """Audit ordinary import statements without interfering with execution."""
    origin = application_origin(globals)
    record_forbidden_imports(
        requested_module_names(name, globals, fromlist, level),
        origin,
    )
    return real_import(name, globals, locals, fromlist, level)


def audited_import_module(name, package=None):
    """Audit dynamic imports requested directly by WSPRadar runtime code."""
    caller_frame = inspect.currentframe().f_back
    caller_globals = caller_frame.f_globals if caller_frame is not None else None
    origin = application_origin(caller_globals)
    try:
        requested_name = importlib.util.resolve_name(name, package) if package else name
    except (ImportError, ValueError):
        requested_name = name
    record_forbidden_imports({requested_name}, origin)
    return real_import_module(name, package)


builtins.__import__ = audited_import
importlib.import_module = audited_import_module

app_test = AppTest.from_file(
    str(project_root / "app.py"),
    default_timeout=60,
)
app_test.run()

result = {
    "app_exceptions": [str(exception.value) for exception in app_test.exception],
    "forbidden_imports": [
        {
            "forbidden_module": forbidden_module,
            "requested_name": requested_name,
            "origin": origin,
        }
        for forbidden_module, requested_name, origin in sorted(forbidden_imports)
    ],
}
print("WSPRADAR_IDLE_IMPORT_AUDIT=" + json.dumps(result, sort_keys=True))
'''


def _format_subprocess_failure(completed_process):
    """Return captured child-process output for an actionable assertion."""
    return (
        f"exit code: {completed_process.returncode}\n"
        f"stdout:\n{completed_process.stdout}\n"
        f"stderr:\n{completed_process.stderr}"
    )


def test_idle_app_does_not_request_analysis_or_scientific_dependencies():
    """Keep analysis, inspector, plotting, and data libraries out of idle work."""
    environment = os.environ.copy()
    existing_python_path = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = os.pathsep.join(
        part
        for part in (str(PROJECT_ROOT), existing_python_path)
        if part
    )

    completed_process = subprocess.run(
        [sys.executable, "-c", IDLE_IMPORT_AUDIT_SCRIPT, str(PROJECT_ROOT)],
        cwd=PROJECT_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )

    assert completed_process.returncode == 0, _format_subprocess_failure(
        completed_process
    )
    result_lines = [
        line
        for line in completed_process.stdout.splitlines()
        if line.startswith(AUDIT_RESULT_PREFIX)
    ]
    assert result_lines, _format_subprocess_failure(completed_process)
    audit_result = json.loads(result_lines[-1][len(AUDIT_RESULT_PREFIX):])

    assert audit_result["app_exceptions"] == []
    assert audit_result["forbidden_imports"] == [], (
        "The idle app requested analysis-only imports:\n"
        + json.dumps(audit_result["forbidden_imports"], indent=2)
    )
