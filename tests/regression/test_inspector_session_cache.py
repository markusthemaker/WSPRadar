from types import SimpleNamespace

import pandas as pd

from ui.components import segment_inspector
from ui.inspector.session_cache import (
    SessionInspectorCache,
    estimate_cache_value_bytes,
)


def _cache(*, max_bytes=64, limits=None, run_id=7):
    return SessionInspectorCache(
        run_id,
        max_bytes=max_bytes,
        namespace_limits=limits or {"segment": 2, "selected": 2, "png": 2},
    )


def test_session_cache_enforces_namespace_lru_limit():
    cache = _cache(max_bytes=100, limits={"segment": 2})
    assert cache.put("segment", "first", b"1", size_bytes=1)
    assert cache.put("segment", "second", b"2", size_bytes=1)
    assert cache.get("segment", "first") == (b"1", True)
    assert cache.put("segment", "third", b"3", size_bytes=1)

    assert cache.get("segment", "second") == (None, False)
    assert cache.get("segment", "first") == (b"1", True)
    assert cache.get("segment", "third") == (b"3", True)
    assert cache.namespace_entry_count("segment") == 2


def test_session_cache_enforces_global_byte_limit_by_access_order():
    cache = _cache(max_bytes=6, limits={"segment": 3, "png": 3})
    assert cache.put("segment", "segment-a", b"aaa", size_bytes=3)
    assert cache.put("png", "png-b", b"bbb", size_bytes=3)
    assert cache.get("segment", "segment-a") == (b"aaa", True)
    assert cache.put("png", "png-c", b"ccc", size_bytes=3)

    assert cache.get("png", "png-b") == (None, False)
    assert cache.get("segment", "segment-a") == (b"aaa", True)
    assert cache.get("png", "png-c") == (b"ccc", True)
    assert cache.total_bytes == 6


def test_cache_rejects_single_value_larger_than_session_budget():
    cache = _cache(max_bytes=4, limits={"selected": 2})
    assert not cache.put("selected", "large", b"12345", size_bytes=5)
    assert cache.entry_count == 0
    assert cache.total_bytes == 0


def test_cache_size_estimator_counts_dataframe_and_png_payloads():
    frame = pd.DataFrame({"station": ["K1AAA", "K2BBB"], "value": [1.0, 2.0]})
    value = {"view_model": frame, "png": b"preview"}
    assert estimate_cache_value_bytes(value) >= int(frame.memory_usage(index=True, deep=True).sum()) + len(b"preview")


def test_cached_recipe_builds_and_disposes_figure_only_once(monkeypatch):
    session_state = {}
    monkeypatch.setattr(segment_inspector, "st", SimpleNamespace(session_state=session_state))
    monkeypatch.setattr(segment_inspector, "get_matplotlib_render_mode", lambda: "image")
    monkeypatch.setattr(segment_inspector, "log_performance_event", lambda *args, **kwargs: None)

    calls = {"build": 0, "render": 0, "display": 0, "dispose": 0}
    image_bytes = b"\x89PNG\r\n\x1a\n" + (b"\x00" * 24)

    def build_figure(recipe):
        calls["build"] += 1
        return {"recipe": recipe}

    def render_figure(figure, **kwargs):
        calls["render"] += 1
        return image_bytes

    monkeypatch.setattr(segment_inspector, "render_matplotlib_figure", render_figure)
    monkeypatch.setattr(
        segment_inspector,
        "render_matplotlib_image_bytes",
        lambda *args, **kwargs: calls.__setitem__("display", calls["display"] + 1),
    )
    monkeypatch.setattr(
        segment_inspector,
        "dispose_matplotlib_figure",
        lambda figure: calls.__setitem__("dispose", calls["dispose"] + 1),
    )

    kwargs = {
        "run_id": 42,
        "cache_key": ("RX_COMP", "all"),
        "subject": "segment insight",
        "build_label": "segment insight figure build",
        "render_figure": build_figure,
    }
    assert segment_inspector._render_cached_recipe({"values": [1]}, **kwargs) == image_bytes
    assert segment_inspector._render_cached_recipe({"values": [1]}, **kwargs) == image_bytes

    assert calls == {"build": 1, "render": 1, "display": 1, "dispose": 1}
    cache = session_state[segment_inspector.INSPECTOR_CACHE_STATE_KEY]
    assert cache.run_id == 42
    assert cache.namespace_entry_count("png") == 1


def test_new_run_replaces_the_session_cache(monkeypatch):
    session_state = {}
    monkeypatch.setattr(segment_inspector, "st", SimpleNamespace(session_state=session_state))

    first = segment_inspector._inspector_cache(1)
    first.put("png", "preview", b"png", size_bytes=3)
    second = segment_inspector._inspector_cache(2)

    assert second is not first
    assert second.run_id == 2
    assert second.entry_count == 0
