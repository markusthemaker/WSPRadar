from pathlib import Path
import json
import shlex

import toml

from config import APP_URL


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def test_application_metadata_uses_the_canonical_public_origin():
    assert APP_URL == "https://wspradar.org/"


def test_static_entrypoint_forwards_query_and_hash_to_the_streamlit_deployment():
    entrypoint = (REPOSITORY_ROOT / "index.html").read_text(encoding="utf-8")

    assert 'new URL("https://wspradar.streamlit.app/")' in entrypoint
    assert "destination.search = window.location.search" in entrypoint
    assert "destination.hash = window.location.hash" in entrypoint
    assert "window.location.replace(destination.toString())" in entrypoint
    assert 'window.location.replace("https://wspradar.streamlit.app")' not in entrypoint
    assert 'http-equiv="refresh"' not in entrypoint


def test_static_entrypoint_declares_the_canonical_public_url():
    entrypoint = (REPOSITORY_ROOT / "index.html").read_text(encoding="utf-8")

    assert '<link rel="canonical" href="https://wspradar.org/">' in entrypoint
    assert '<meta property="og:url" content="https://wspradar.org/" />' in entrypoint


def test_public_server_protections_are_enabled_without_editor_overrides():
    server_configuration = toml.loads(
        (REPOSITORY_ROOT / ".streamlit/config.toml").read_text(encoding="utf-8")
    )["server"]
    assert server_configuration["enableCORS"] is True
    assert server_configuration["enableXsrfProtection"] is True

    editor_configuration = json.loads(
        (REPOSITORY_ROOT / ".vscode/tasks.json").read_text(encoding="utf-8")
    )
    launch_tasks = [task for task in editor_configuration["tasks"] if task["label"] == "Start Streamlit Server"]
    assert len(launch_tasks) == 1
    launch_arguments = shlex.split(launch_tasks[0]["command"])
    assert not any(
        argument.split("=", 1)[0] in {"--server.enableCORS", "--server.enableXsrfProtection"}
        for argument in launch_arguments
    )
