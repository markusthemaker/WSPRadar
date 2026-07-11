from contextlib import nullcontext

from docs.doc_de import DOC_DE
from docs.doc_en import DOC_EN
from docs.pdf_generator import get_docs
from ui import documentation


class _Placeholder:
    def __init__(self):
        self.captions = []
        self.cleared = False

    def caption(self, label):
        self.captions.append(label)

    def empty(self):
        self.cleared = True


class _FakeStreamlit:
    def __init__(self, session_state=None):
        self.session_state = session_state if session_state is not None else {}
        self.markdowns = []
        self.placeholders = []
        self.container_keys = []

    def empty(self):
        placeholder = _Placeholder()
        self.placeholders.append(placeholder)
        return placeholder

    def columns(self, _widths, **_kwargs):
        return nullcontext(), nullcontext(), nullcontext()

    def container(self, *, key):
        self.container_keys.append(key)
        return nullcontext()

    def markdown(self, body, **kwargs):
        self.markdowns.append((body, kwargs))


def _labels():
    return {
        "msg_loading_documentation": "Loading documentation...",
        "dev_credit": "credit",
    }


def test_documentation_text_is_process_cached_without_modification():
    get_docs.cache_clear()

    assert get_docs("en") is DOC_EN
    assert get_docs("de") is DOC_DE
    assert get_docs("en") is DOC_EN
    assert get_docs.cache_info().hits == 1


def test_first_documentation_render_delays_once_and_preserves_full_body(monkeypatch):
    fake_st = _FakeStreamlit(session_state={"lang": "en"})
    sleeps = []
    pdf_calls = []
    monkeypatch.setattr(documentation, "st", fake_st)
    monkeypatch.setattr(documentation.time, "sleep", sleeps.append)
    monkeypatch.setattr(
        documentation,
        "render_documentation_pdf_control",
        lambda *args: pdf_calls.append(args),
    )

    documentation._render_documentation_section(_labels(), "en", "logo", "v1")

    assert sleeps == [documentation.DOCUMENTATION_INITIAL_LOAD_DELAY_SEC]
    assert fake_st.session_state[documentation.DOCUMENTATION_DELAY_APPLIED_KEY] is True
    assert fake_st.placeholders[0].captions == ["Loading documentation..."]
    assert fake_st.placeholders[0].cleared is True
    assert fake_st.container_keys == [documentation.DOCUMENTATION_CONTAINER_KEY]
    assert any(body is DOC_EN for body, _kwargs in fake_st.markdowns)
    assert pdf_calls == [(_labels(), "en", "logo", "v1")]


def test_later_documentation_render_has_no_artificial_delay(monkeypatch):
    fake_st = _FakeStreamlit(
        session_state={
            "lang": "de",
            documentation.DOCUMENTATION_DELAY_APPLIED_KEY: True,
        }
    )
    monkeypatch.setattr(documentation, "st", fake_st)
    monkeypatch.setattr(
        documentation.time,
        "sleep",
        lambda _seconds: (_ for _ in ()).throw(AssertionError("unexpected delay")),
    )
    monkeypatch.setattr(
        documentation,
        "render_documentation_pdf_control",
        lambda *_args: None,
    )

    documentation._render_documentation_section(_labels(), "de", "logo", "v1")

    assert fake_st.placeholders == []
    assert any(body is DOC_DE for body, _kwargs in fake_st.markdowns)


def test_stale_parallel_render_does_not_publish_old_language(monkeypatch):
    fake_st = _FakeStreamlit(session_state={"lang": "en"})
    monkeypatch.setattr(documentation, "st", fake_st)
    monkeypatch.setattr(
        documentation.time,
        "sleep",
        lambda _seconds: fake_st.session_state.__setitem__("lang", "de"),
    )
    monkeypatch.setattr(
        documentation,
        "render_documentation_pdf_control",
        lambda *_args: (_ for _ in ()).throw(AssertionError("stale render")),
    )

    documentation._render_documentation_section(_labels(), "en", "logo", "v1")

    assert fake_st.container_keys == []
    assert not any(body is DOC_EN for body, _kwargs in fake_st.markdowns)
