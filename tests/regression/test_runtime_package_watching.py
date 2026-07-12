import importlib
from pathlib import Path

import pytest
from streamlit.watcher.local_sources_watcher import get_module_paths


RUNTIME_PACKAGE_NAMES = (
    "core",
    "docs",
    "ui",
    "ui.components",
    "ui.inspector",
    "ui.plots",
)


@pytest.mark.parametrize("package_name", RUNTIME_PACKAGE_NAMES)
def test_runtime_packages_are_watched_as_files_not_namespace_directories(
    package_name,
):
    """Keep first-import bytecode writes outside Streamlit directory watches."""
    runtime_package = importlib.import_module(package_name)

    assert runtime_package.__file__ is not None
    assert type(runtime_package.__path__).__name__ != "_NamespacePath"
    package_file = Path(runtime_package.__file__).resolve()
    watched_paths = {
        Path(watched_path).resolve()
        for watched_path in get_module_paths(runtime_package)
    }

    assert package_file.name == "__init__.py"
    assert watched_paths == {package_file}
