"""Deferred rendering for the long-form scientific documentation section."""

import time

import streamlit as st

from config.app_config import DOCUMENTATION_INITIAL_LOAD_DELAY_SEC
from docs.pdf_generator import get_docs, render_documentation_pdf_control


DOCUMENTATION_DELAY_APPLIED_KEY = "_documentation_initial_delay_applied"
DOCUMENTATION_CONTAINER_KEY = "documentation_body"


def _render_documentation_section(t, lang, logo_base64, version):
    """Render the complete documentation, delaying only its first session load."""
    apply_initial_delay = not st.session_state.get(
        DOCUMENTATION_DELAY_APPLIED_KEY,
        False,
    )
    loading_placeholder = None

    if apply_initial_delay:
        st.session_state[DOCUMENTATION_DELAY_APPLIED_KEY] = True
        loading_placeholder = st.empty()
        loading_placeholder.caption(
            t.get("msg_loading_documentation", "Loading documentation...")
        )
        time.sleep(DOCUMENTATION_INITIAL_LOAD_DELAY_SEC)
        loading_placeholder.empty()

        # A language change can start a newer full rerun while this parallel
        # fragment is sleeping. Let that newer invocation own the output.
        if st.session_state.get("lang", lang) != lang:
            return

    doc_title = "Dokumentation" if lang == "de" else "Documentation"
    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
    col_doc_title, col_doc_download, _col_doc_spacer = st.columns(
        [0.28, 0.18, 0.54],
        vertical_alignment="center",
    )
    with col_doc_title:
        st.markdown(
            f"<h2 style='text-align: left; color: #ffffff; margin: 0; padding: 0; "
            "line-height: 1; font-family: \"Rajdhani\", sans-serif; letter-spacing: 1px; "
            f"white-space: nowrap;'>{doc_title}</h2>",
            unsafe_allow_html=True,
        )
    with col_doc_download:
        render_documentation_pdf_control(t, lang, logo_base64, version)

    with st.container(key=DOCUMENTATION_CONTAINER_KEY):
        st.markdown(get_docs(lang), unsafe_allow_html=True)
        st.markdown(
            f"<div style='text-align: center; color: #888888; font-size: 0.9rem; "
            "margin-top: 4rem; margin-bottom: 2rem; padding-top: 1.5rem; "
            "border-top: 1px solid rgba(57, 255, 20, 0.3);'>"
            f"{t['dev_credit']}</div>",
            unsafe_allow_html=True,
        )


@st.fragment(parallel=True)
def render_documentation_section(t, lang, logo_base64, version):
    """Render documentation independently after the main app has completed."""
    _render_documentation_section(t, lang, logo_base64, version)
