import inspect
from contextlib import nullcontext

import pytest

from docs.doc_de import DOC_DE
from docs.doc_en import DOC_EN
from docs.pdf_generator import get_docs
from i18n import T
from ui import documentation


class _FakeStreamlit:
    def __init__(self, session_state=None):
        self.session_state = session_state if session_state is not None else {}
        self.markdowns = []
        self.container_keys = []
        self.buttons = []

    def columns(self, _widths, **_kwargs):
        return nullcontext(), nullcontext(), nullcontext()

    def container(self, *, key):
        self.container_keys.append(key)
        return nullcontext()

    def markdown(self, body, **kwargs):
        self.markdowns.append((body, kwargs))

    def button(self, label, *, icon, key, on_click, width):
        self.buttons.append(
            {
                "label": label,
                "icon": icon,
                "key": key,
                "on_click": on_click,
                "width": width,
            }
        )
        return False


def _labels(lang="en"):
    if lang == "de":
        return {
            "btn_load_full_documentation": "Vollst\u00e4ndige Dokumentation laden",
            "btn_hide_full_documentation": "Vollst\u00e4ndige Dokumentation ausblenden",
            "dev_credit": "credit",
        }
    return {
        "btn_load_full_documentation": "Load full documentation",
        "btn_hide_full_documentation": "Hide full documentation",
        "dev_credit": "credit",
    }


def _render_with_fake_streamlit(monkeypatch, fake_st, lang="en"):
    pdf_calls = []
    scroll_trigger_calls = []
    monkeypatch.setattr(documentation, "st", fake_st)
    monkeypatch.setattr(
        documentation,
        "render_documentation_pdf_control",
        lambda *args: pdf_calls.append(args),
    )
    monkeypatch.setattr(
        documentation,
        "render_documentation_scroll_trigger",
        lambda **kwargs: scroll_trigger_calls.append(kwargs),
    )
    labels = _labels(lang)
    documentation._render_documentation_section(labels, lang, "logo", "v1")
    return labels, pdf_calls, scroll_trigger_calls


def test_documentation_text_is_process_cached_without_modification():
    get_docs.cache_clear()

    assert get_docs("en") is DOC_EN
    assert get_docs("de") is DOC_DE
    assert get_docs("en") is DOC_EN
    assert get_docs.cache_info().hits == 1


def test_load_and_hide_controls_have_english_and_german_labels():
    assert T["en"]["btn_load_full_documentation"] == "Load full documentation"
    assert T["en"]["btn_hide_full_documentation"] == "Hide full documentation"
    assert (
        T["de"]["btn_load_full_documentation"]
        == "Vollst\u00e4ndige Dokumentation laden"
    )
    assert (
        T["de"]["btn_hide_full_documentation"]
        == "Vollst\u00e4ndige Dokumentation ausblenden"
    )


@pytest.mark.parametrize(
    ("documentation_text", "section_one_heading", "toc_heading"),
    [
        (DOC_EN, "### 1. Why WSPRadar", "### Table of Contents"),
        (DOC_DE, "### 1. Warum WSPRadar", "### Inhaltsverzeichnis"),
    ],
    ids=("en", "de"),
)
def test_manual_split_is_three_way_lossless_and_language_independent(
    documentation_text,
    section_one_heading,
    toc_heading,
):
    section_one, table_of_contents, remaining_sections = (
        documentation._split_documentation_sections(documentation_text)
    )

    assert section_one_heading in section_one
    assert '<a id="sec-1-3"></a>' in section_one
    assert documentation.DOCUMENTATION_TOC_MARKER not in section_one
    assert documentation.DOCUMENTATION_SECTION_TWO_MARKER not in section_one
    assert table_of_contents.startswith(documentation.DOCUMENTATION_TOC_MARKER)
    assert toc_heading in table_of_contents
    assert documentation.DOCUMENTATION_SECTION_TWO_MARKER not in table_of_contents
    assert remaining_sections.startswith(
        documentation.DOCUMENTATION_SECTION_TWO_MARKER
    )
    assert section_one + table_of_contents + remaining_sections == documentation_text

    section_one_lead, section_one_completion = (
        documentation._split_section_one_at_scroll_boundary(section_one)
    )
    assert documentation.DOCUMENTATION_SECTION_ONE_TRIGGER_MARKER not in section_one_lead
    assert section_one_completion.startswith(
        documentation.DOCUMENTATION_SECTION_ONE_TRIGGER_MARKER
    )
    assert section_one_lead + section_one_completion == section_one


@pytest.mark.parametrize("documentation_text", (DOC_EN, DOC_DE), ids=("en", "de"))
def test_manual_contains_one_stable_toc_marker_before_section_two(documentation_text):
    assert documentation_text.count(documentation.DOCUMENTATION_TOC_MARKER) == 1
    assert documentation_text.count(documentation.DOCUMENTATION_SECTION_TWO_MARKER) == 1
    assert documentation_text.index(
        documentation.DOCUMENTATION_TOC_MARKER
    ) < documentation_text.index(documentation.DOCUMENTATION_SECTION_TWO_MARKER)


@pytest.mark.parametrize(
    ("malformed_section_one", "expected_count"),
    [
        ("Section 1 without its final subsection marker", 0),
        (
            documentation.DOCUMENTATION_SECTION_ONE_TRIGGER_MARKER
            + documentation.DOCUMENTATION_SECTION_ONE_TRIGGER_MARKER,
            2,
        ),
    ],
)
def test_section_one_scroll_split_rejects_missing_or_duplicate_marker(
    malformed_section_one,
    expected_count,
):
    with pytest.raises(ValueError, match=rf"found {expected_count}"):
        documentation._split_section_one_at_scroll_boundary(
            malformed_section_one
        )


@pytest.mark.parametrize(
    ("malformed_documentation", "expected_message"),
    [
        (
            documentation.DOCUMENTATION_SECTION_TWO_MARKER,
            "table-of-contents marker.*found 0",
        ),
        (
            documentation.DOCUMENTATION_TOC_MARKER
            + documentation.DOCUMENTATION_TOC_MARKER
            + documentation.DOCUMENTATION_SECTION_TWO_MARKER,
            "table-of-contents marker.*found 2",
        ),
        (
            documentation.DOCUMENTATION_TOC_MARKER,
            "Section 2 marker.*found 0",
        ),
        (
            documentation.DOCUMENTATION_TOC_MARKER
            + documentation.DOCUMENTATION_SECTION_TWO_MARKER
            + documentation.DOCUMENTATION_SECTION_TWO_MARKER,
            "Section 2 marker.*found 2",
        ),
        (
            documentation.DOCUMENTATION_SECTION_TWO_MARKER
            + documentation.DOCUMENTATION_TOC_MARKER,
            "table of contents must precede the Section 2 marker",
        ),
    ],
    ids=(
        "missing-toc",
        "duplicate-toc",
        "missing-section-two",
        "duplicate-section-two",
        "reversed-order",
    ),
)
def test_manual_split_rejects_malformed_or_reversed_markers(
    malformed_documentation,
    expected_message,
):
    with pytest.raises(ValueError, match=expected_message):
        documentation._split_documentation_sections(malformed_documentation)


def test_initial_render_shows_only_section_one_and_prominent_load_fallback(
    monkeypatch,
):
    fake_st = _FakeStreamlit(session_state={"lang": "en"})
    labels, pdf_calls, scroll_trigger_calls = _render_with_fake_streamlit(
        monkeypatch,
        fake_st,
    )
    section_one, table_of_contents, remaining_sections = (
        documentation._split_documentation_sections(DOC_EN)
    )
    section_one_lead, section_one_completion = (
        documentation._split_section_one_at_scroll_boundary(section_one)
    )
    rendered_bodies = [body for body, _kwargs in fake_st.markdowns]

    assert fake_st.container_keys == [documentation.DOCUMENTATION_CONTAINER_KEY]
    assert section_one_lead in rendered_bodies
    assert section_one_completion in rendered_bodies
    assert section_one_lead + section_one_completion == section_one
    assert table_of_contents not in rendered_bodies
    assert remaining_sections not in rendered_bodies
    assert not any(labels["dev_credit"] in body for body in rendered_bodies)
    assert fake_st.buttons == [
        {
            "label": labels["btn_load_full_documentation"],
            "icon": ":material/menu_book:",
            "key": documentation.DOCUMENTATION_TOGGLE_KEY,
            "on_click": documentation._load_full_documentation,
            "width": "stretch",
        }
    ]
    assert scroll_trigger_calls == [
        {
            "key": documentation.DOCUMENTATION_SCROLL_TRIGGER_KEY,
            "on_trigger": documentation._expand_documentation_from_scroll,
        }
    ]
    assert pdf_calls == [(labels, "en", "logo", "v1")]


@pytest.mark.parametrize(
    "session_state",
    [
        {documentation.DOCUMENTATION_SCROLL_TRIGGER_CONSUMED_KEY: True},
        {"run_mode": "tx"},
        {"run_mode": "rx"},
    ],
    ids=("already-consumed", "tx-run-active", "rx-run-active"),
)
def test_scroll_trigger_is_suppressed_after_consumption_or_during_run(
    monkeypatch,
    session_state,
):
    fake_st = _FakeStreamlit(session_state=session_state)
    _labels_result, _pdf_calls, scroll_trigger_calls = _render_with_fake_streamlit(
        monkeypatch,
        fake_st,
    )

    assert scroll_trigger_calls == []
    assert fake_st.buttons[0]["label"] == "Load full documentation"


def test_scroll_callback_expands_once_and_renders_toc_and_remainder(monkeypatch):
    fake_st = _FakeStreamlit(session_state={"lang": "en"})
    labels, _pdf_calls, scroll_trigger_calls = _render_with_fake_streamlit(
        monkeypatch,
        fake_st,
    )

    scroll_trigger_calls[0]["on_trigger"]()
    assert fake_st.session_state[documentation.DOCUMENTATION_EXPANDED_KEY] is True
    assert (
        fake_st.session_state[
            documentation.DOCUMENTATION_SCROLL_TRIGGER_CONSUMED_KEY
        ]
        is True
    )

    fake_st.markdowns.clear()
    fake_st.buttons.clear()
    scroll_trigger_calls.clear()
    documentation._render_documentation_section(labels, "en", "logo", "v1")
    section_one, table_of_contents, remaining_sections = (
        documentation._split_documentation_sections(DOC_EN)
    )
    section_one_lead, section_one_completion = (
        documentation._split_section_one_at_scroll_boundary(section_one)
    )
    rendered_bodies = [body for body, _kwargs in fake_st.markdowns]

    assert scroll_trigger_calls == []
    assert section_one_lead in rendered_bodies
    assert section_one_completion in rendered_bodies
    assert table_of_contents in rendered_bodies
    assert remaining_sections in rendered_bodies
    assert section_one + table_of_contents + remaining_sections == DOC_EN


def test_scroll_callback_does_not_expand_or_consume_while_run_is_active(
    monkeypatch,
):
    session_state = {"run_mode": "tx"}
    fake_st = _FakeStreamlit(session_state=session_state)
    monkeypatch.setattr(documentation, "st", fake_st)

    documentation._expand_documentation_from_scroll()

    assert fake_st.session_state == {"run_mode": "tx"}
    assert documentation.DOCUMENTATION_EXPANDED_KEY not in fake_st.session_state
    assert (
        documentation.DOCUMENTATION_SCROLL_TRIGGER_CONSUMED_KEY
        not in fake_st.session_state
    )


def test_expanded_render_restores_toc_exact_remainder_and_hide_control(monkeypatch):
    fake_st = _FakeStreamlit(
        session_state={
            "lang": "de",
            documentation.DOCUMENTATION_EXPANDED_KEY: True,
        }
    )
    labels, pdf_calls, scroll_trigger_calls = _render_with_fake_streamlit(
        monkeypatch,
        fake_st,
        lang="de",
    )
    section_one, table_of_contents, remaining_sections = (
        documentation._split_documentation_sections(DOC_DE)
    )
    section_one_lead, section_one_completion = (
        documentation._split_section_one_at_scroll_boundary(section_one)
    )
    rendered_bodies = [body for body, _kwargs in fake_st.markdowns]

    assert section_one_lead in rendered_bodies
    assert section_one_completion in rendered_bodies
    assert table_of_contents in rendered_bodies
    assert remaining_sections in rendered_bodies
    assert section_one + table_of_contents + remaining_sections == DOC_DE
    assert "(#sec-2)" in table_of_contents
    assert any(labels["dev_credit"] in body for body in rendered_bodies)
    assert fake_st.buttons[0]["label"] == labels["btn_hide_full_documentation"]
    assert fake_st.buttons[0]["icon"] == ":material/expand_less:"
    assert fake_st.buttons[0]["width"] == "stretch"
    assert scroll_trigger_calls == []
    assert pdf_calls == [(labels, "de", "logo", "v1")]


def test_manual_load_hide_and_reload_preserve_consumed_autoload(monkeypatch):
    fake_st = _FakeStreamlit(session_state={"lang": "en"})
    labels, _pdf_calls, scroll_trigger_calls = _render_with_fake_streamlit(
        monkeypatch,
        fake_st,
    )

    fake_st.buttons[0]["on_click"]()
    assert fake_st.session_state[documentation.DOCUMENTATION_EXPANDED_KEY] is True
    assert (
        fake_st.session_state[
            documentation.DOCUMENTATION_SCROLL_TRIGGER_CONSUMED_KEY
        ]
        is True
    )

    fake_st.markdowns.clear()
    fake_st.buttons.clear()
    scroll_trigger_calls.clear()
    documentation._render_documentation_section(labels, "en", "logo", "v1")
    assert fake_st.buttons[0]["label"] == labels["btn_hide_full_documentation"]
    assert fake_st.buttons[0]["on_click"] is documentation._hide_full_documentation
    assert scroll_trigger_calls == []

    fake_st.buttons[0]["on_click"]()
    assert fake_st.session_state[documentation.DOCUMENTATION_EXPANDED_KEY] is False
    assert (
        fake_st.session_state[
            documentation.DOCUMENTATION_SCROLL_TRIGGER_CONSUMED_KEY
        ]
        is True
    )

    fake_st.markdowns.clear()
    fake_st.buttons.clear()
    documentation._render_documentation_section(labels, "en", "logo", "v1")
    assert fake_st.buttons[0]["label"] == labels["btn_load_full_documentation"]
    assert fake_st.buttons[0]["on_click"] is documentation._load_full_documentation
    assert scroll_trigger_calls == []

    fake_st.buttons[0]["on_click"]()
    assert fake_st.session_state[documentation.DOCUMENTATION_EXPANDED_KEY] is True
    assert (
        fake_st.session_state[
            documentation.DOCUMENTATION_SCROLL_TRIGGER_CONSUMED_KEY
        ]
        is True
    )


def test_stale_load_callback_cannot_hide_scroll_expanded_documentation(monkeypatch):
    """A queued fallback click must remain an idempotent load action."""
    fake_st = _FakeStreamlit(session_state={"lang": "en"})
    _labels_result, _pdf_calls, scroll_trigger_calls = _render_with_fake_streamlit(
        monkeypatch,
        fake_st,
    )
    stale_load_callback = fake_st.buttons[0]["on_click"]

    scroll_trigger_calls[0]["on_trigger"]()
    stale_load_callback()

    assert fake_st.session_state[documentation.DOCUMENTATION_EXPANDED_KEY] is True
    assert (
        fake_st.session_state[
            documentation.DOCUMENTATION_SCROLL_TRIGGER_CONSUMED_KEY
        ]
        is True
    )


def test_documentation_fragment_has_no_sleep_or_parallel_execution():
    module_source = inspect.getsource(documentation)

    assert "time.sleep" not in module_source
    assert "DOCUMENTATION_INITIAL_LOAD_DELAY_SEC" not in module_source
    assert "_disable_unavailable_toc_links" not in module_source
    assert "@st.fragment" in module_source
    assert "@st.fragment(parallel=True)" not in module_source
