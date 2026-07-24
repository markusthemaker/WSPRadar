"""On-demand rendering for the long-form scientific documentation section."""

from html import escape
import re

import streamlit as st

from docs.pdf_generator import get_docs, render_documentation_pdf_control
from ui.documentation_scroll_trigger import render_documentation_scroll_trigger
from ui.documentation_state import (
    DOCUMENTATION_EXPANDED_KEY,
    DOCUMENTATION_SCROLL_TRIGGER_CONSUMED_KEY,
    expand_documentation,
    hide_documentation,
)


DOCUMENTATION_CONTAINER_KEY = "documentation_body"
DOCUMENTATION_TOGGLE_KEY = "documentation_visibility_toggle"
DOCUMENTATION_SCROLL_TRIGGER_KEY = "documentation_scroll_boundary_trigger"
DOCUMENTATION_SECTION_ONE_TRIGGER_MARKER = '<a id="sec-1-3"></a>'
DOCUMENTATION_TOC_MARKER = '<a id="documentation-toc"></a>'
DOCUMENTATION_SECTION_TWO_MARKER = '<a id="sec-2"></a>'
DOCUMENTATION_ANCHOR_PATTERN = re.compile(r'<a id="([^"]+)"></a>')


def _split_documentation_sections(documentation_text):
    """Split the preface, the TOC, and later chapters without losing text."""
    toc_marker_count = documentation_text.count(DOCUMENTATION_TOC_MARKER)
    if toc_marker_count != 1:
        raise ValueError(
            "Documentation must contain exactly one table-of-contents marker "
            f"{DOCUMENTATION_TOC_MARKER!r}; found {toc_marker_count}."
        )

    section_two_marker_count = documentation_text.count(
        DOCUMENTATION_SECTION_TWO_MARKER
    )
    if section_two_marker_count != 1:
        raise ValueError(
            "Documentation must contain exactly one Section 2 marker "
            f"{DOCUMENTATION_SECTION_TWO_MARKER!r}; "
            f"found {section_two_marker_count}."
        )

    (
        section_one,
        table_of_contents_and_remaining_sections,
    ) = documentation_text.split(DOCUMENTATION_TOC_MARKER, maxsplit=1)
    table_of_contents_and_remaining_sections = (
        DOCUMENTATION_TOC_MARKER + table_of_contents_and_remaining_sections
    )
    if (
        DOCUMENTATION_SECTION_TWO_MARKER
        not in table_of_contents_and_remaining_sections
    ):
        raise ValueError(
            "Documentation table of contents must precede the Section 2 marker."
        )

    table_of_contents, section_two_and_remaining_sections = (
        table_of_contents_and_remaining_sections.split(
            DOCUMENTATION_SECTION_TWO_MARKER,
            maxsplit=1,
        )
    )
    return (
        section_one,
        table_of_contents,
        DOCUMENTATION_SECTION_TWO_MARKER + section_two_and_remaining_sections,
    )


def _split_section_one_at_scroll_boundary(section_one):
    """Split the preface losslessly before its final subsection."""
    marker_count = section_one.count(DOCUMENTATION_SECTION_ONE_TRIGGER_MARKER)
    if marker_count != 1:
        raise ValueError(
            "Documentation preface must contain exactly one scroll marker "
            f"{DOCUMENTATION_SECTION_ONE_TRIGGER_MARKER!r}; found {marker_count}."
        )

    section_one_lead, section_one_completion = section_one.split(
        DOCUMENTATION_SECTION_ONE_TRIGGER_MARKER,
        maxsplit=1,
    )
    return (
        section_one_lead,
        DOCUMENTATION_SECTION_ONE_TRIGGER_MARKER + section_one_completion,
    )


def _load_full_documentation():
    """Idempotently load the complete manual from the fallback control."""
    expand_documentation(st.session_state)


def _hide_full_documentation():
    """Idempotently hide the complete manual and keep scroll load consumed."""
    hide_documentation(st.session_state)


def _expand_documentation_from_navigation():
    """Expand the manual after an explicit unresolved-anchor navigation."""
    expand_documentation(st.session_state)


def _expand_documentation_from_scroll():
    """Expand the manual when visible Section 0.3 enters the viewport."""
    if st.session_state.get("run_mode"):
        return
    expand_documentation(st.session_state)


def _should_render_scroll_trigger(is_documentation_expanded):
    """Return whether this session may still auto-expand near the preface."""
    return (
        not is_documentation_expanded
        and not st.session_state.get(
            DOCUMENTATION_SCROLL_TRIGGER_CONSUMED_KEY,
            False,
        )
        and not st.session_state.get("run_mode")
    )


def _documentation_anchor_ids(documentation_text):
    """Return the ordered explicit anchors that internal manual links may target."""
    return tuple(DOCUMENTATION_ANCHOR_PATTERN.findall(documentation_text))


def _render_documentation_section(t, lang, logo_base64, version):
    """Render the preface, loading the TOC and remaining manual on demand."""
    documentation_text = get_docs(lang)
    (
        section_one,
        table_of_contents,
        remaining_sections,
    ) = _split_documentation_sections(documentation_text)
    section_one_lead, section_one_completion = (
        _split_section_one_at_scroll_boundary(section_one)
    )
    is_documentation_expanded = bool(
        st.session_state.get(DOCUMENTATION_EXPANDED_KEY, False)
    )
    is_scroll_trigger_consumed = bool(
        st.session_state.get(
            DOCUMENTATION_SCROLL_TRIGGER_CONSUMED_KEY,
            False,
        )
    )

    doc_title = "Dokumentation" if lang == "de" else "Documentation"
    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
    col_doc_title, col_doc_download, _col_doc_spacer = st.columns(
        [0.28, 0.18, 0.54],
        vertical_alignment="center",
    )
    with col_doc_title:
        documentation_subtitle = t.get(
            "sub_documentation",
            "Method, interpretation, controls, limitations, and troubleshooting.",
        )
        st.markdown(
            f"<h2 class='documentation-section-title' "
            "style='text-align: left; color: #39ff14; margin: 0; padding: 0; "
            "line-height: 1; font-family: \"Rajdhani\", sans-serif; letter-spacing: 1px; "
            f"white-space: nowrap;'>{escape(doc_title)}</h2>"
            "<p class='documentation-section-subtitle' "
            "style='color:#98a3b1; font-family:\"Space Mono\", monospace; "
            "font-size:0.75rem; line-height:1.45; margin:0.35rem 0 0;'>"
            f"{escape(documentation_subtitle)}</p>",
            unsafe_allow_html=True,
        )
    with col_doc_download:
        render_documentation_pdf_control(t, lang, logo_base64, version)

    with st.container(key=DOCUMENTATION_CONTAINER_KEY):
        st.markdown(section_one_lead, unsafe_allow_html=True)
        render_documentation_scroll_trigger(
            key=DOCUMENTATION_SCROLL_TRIGGER_KEY,
            anchor_ids=_documentation_anchor_ids(documentation_text),
            is_auto_expand_enabled=_should_render_scroll_trigger(
                is_documentation_expanded
            ),
            is_documentation_expanded=is_documentation_expanded,
            allow_initial_hash_expansion=not is_scroll_trigger_consumed,
            on_navigation=_expand_documentation_from_navigation,
            on_trigger=_expand_documentation_from_scroll,
        )
        st.markdown(section_one_completion, unsafe_allow_html=True)
        toggle_label_key = (
            "btn_hide_full_documentation"
            if is_documentation_expanded
            else "btn_load_full_documentation"
        )
        toggle_label_fallback = (
            "Hide full documentation"
            if is_documentation_expanded
            else "Load full documentation"
        )
        toggle_icon = (
            ":material/expand_less:"
            if is_documentation_expanded
            else ":material/menu_book:"
        )
        st.button(
            t.get(toggle_label_key, toggle_label_fallback),
            icon=toggle_icon,
            key=DOCUMENTATION_TOGGLE_KEY,
            on_click=(
                _hide_full_documentation
                if is_documentation_expanded
                else _load_full_documentation
            ),
            width="stretch",
        )
        if is_documentation_expanded:
            st.markdown(table_of_contents, unsafe_allow_html=True)
            st.markdown(remaining_sections, unsafe_allow_html=True)
            st.markdown(
                f"<div style='text-align: center; color: #888888; font-size: 0.9rem; "
                "margin-top: 4rem; margin-bottom: 2rem; padding-top: 1.5rem; "
                "border-top: 1px solid rgba(57, 255, 20, 0.3);'>"
                f"{t['dev_credit']}</div>",
                unsafe_allow_html=True,
            )


@st.fragment
def render_documentation_section(t, lang, logo_base64, version):
    """Render the independently rerunnable documentation fragment."""
    _render_documentation_section(t, lang, logo_base64, version)
