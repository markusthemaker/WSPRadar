from configparser import ConfigParser
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def test_pytest_transient_state_is_consolidated_under_ignored_test_workspace():
    """Keep pytest's temporary and cache trees inside the ignored .test root."""
    pytest_configuration = ConfigParser()
    pytest_configuration.read(REPOSITORY_ROOT / "pytest.ini", encoding="utf-8")

    pytest_options = pytest_configuration["pytest"]
    assert "--basetemp=.test/pytest-temp" in pytest_options.get("addopts", "").split()
    assert pytest_options.get("cache_dir") == ".test/pytest-cache"

    ignored_paths = {
        line.strip()
        for line in (REPOSITORY_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    assert "/.test/" in ignored_paths
