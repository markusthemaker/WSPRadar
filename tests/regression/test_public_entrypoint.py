from pathlib import Path

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
