"""Shared Streamlit presentation helpers for the Inspector's focused views.

The helpers consume explicit values and containers; session state belongs to
selection_state and the preparation coordinator.
"""

from contextlib import nullcontext
from html import escape
import inspect

import pandas as pd
import streamlit as st

from config import TEMPORAL_IQR_BAND_ALPHA
from ui.inspector.preparation import INSPECTOR_CACHE_VERSION
from ui.matplotlib_renderer import (
    dispose_matplotlib_figure,
    get_matplotlib_render_mode,
    matplotlib_render_span_label,
    render_matplotlib_figure,
    render_matplotlib_image_bytes,
)
from ui.plots.temporal_layout import TEMPORAL_EVIDENCE_LAYOUT_VERSION
from ui.reference_correction import configured_snr_correction_notice
from ui.result_hierarchy import transition_prompt_html


INSPECTOR_PNG_RENDER_VERSION = 39
COMPACT_DATAFRAME_VISIBLE_BODY_ROWS = 5
COMPACT_DATAFRAME_ROW_HEIGHT_PX = 35
COMPACT_DATAFRAME_HEIGHT_PX = (
    (COMPACT_DATAFRAME_VISIBLE_BODY_ROWS + 1)
    * COMPACT_DATAFRAME_ROW_HEIGHT_PX
    + 2
)



def format_metric_or_none(value, decimals=0):
    """Format SNR-like display values, preserving None markers."""
    if pd.isna(value):
        return ""
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped or stripped.lower() == "none":
            return "None" if stripped.lower() == "none" else ""
        try:
            number = float(stripped)
        except ValueError:
            return value
    else:
        number = float(value)
    return f"{number:.{decimals}f}"


def is_snr_display_column(column_name):
    text = str(column_name)
    return (
        "SNR" in text or
        "Norm@" in text or
        "Micro-Med" in text or
        "\u0394" in text or
        "Delta" in text
    )


def format_snr_display_columns(df):
    """Return a display-only copy with SNR-like columns rendered compactly."""
    display_df = df.copy()
    for col in display_df.columns:
        if is_snr_display_column(col):
            display_df[col] = display_df[col].map(lambda value: format_metric_or_none(value, 1))
    return display_df


def render_reference_correction_notice(
    t,
    *,
    is_compare,
    is_sequential,
    analysis_context,
):
    """Render the completed run's configured correction as a compact notice."""
    note = configured_snr_correction_notice(
        analysis_context,
        t,
        is_compare=is_compare,
        is_sequential=is_sequential,
    )
    if not note:
        return
    st.markdown(
        f"""
        <style>
            @media (min-width: 768px) {{
                .reference-correction-note {{
                    white-space: nowrap;
                    overflow-x: auto;
                }}
            }}
        </style>
        <div class="reference-correction-note" style="font-size:0.78em; color:#9aa4b2; margin-top:-0.15rem; margin-bottom:0.35rem; font-family:'Space Mono', monospace;">
            {escape(note)}
        </div>
        """,
        unsafe_allow_html=True
    )


def supports_dataframe_selection_default():
    """Return True when the installed Streamlit version can preselect dataframe rows."""
    try:
        return "selection_default" in inspect.signature(st.dataframe).parameters
    except (TypeError, ValueError):
        return False


def render_compact_dataframe(container, dataframe, **kwargs):
    """Render a scrollable table with five visible body rows plus its header."""
    return container.dataframe(
        dataframe,
        height=COMPACT_DATAFRAME_HEIGHT_PX,
        row_height=COMPACT_DATAFRAME_ROW_HEIGHT_PX,
        **kwargs,
    )


def snr_column_config(df):
    """Keep numeric SNR columns right-aligned while controlling displayed precision."""
    config = {}
    for col in df.columns:
        if is_snr_display_column(col) and pd.api.types.is_numeric_dtype(df[col]):
            config[col] = st.column_config.NumberColumn(format="%.1f")
    return config


def timed_span(timing_collector, label, detail=""):
    """Return a timing context when profiling is active."""
    if timing_collector is None:
        return nullcontext()
    return timing_collector.span(label, detail=detail)


def render_cached_recipe(
    recipe,
    *,
    preparation,
    cache_key,
    subject,
    build_label,
    render_figure,
):
    """Render a compact recipe, reusing preview PNG bytes when available."""
    timing_collector = preparation.timing_collector
    render_mode = get_matplotlib_render_mode()
    png_key = (
        INSPECTOR_CACHE_VERSION,
        INSPECTOR_PNG_RENDER_VERSION,
        TEMPORAL_EVIDENCE_LAYOUT_VERSION,
        TEMPORAL_IQR_BAND_ALPHA,
        render_mode,
        subject,
        cache_key,
    )
    if render_mode == "image":
        image_bytes, hit = preparation.cache_get(
            "png",
            png_key,
            item=subject,
        )
        if hit:
            render_matplotlib_image_bytes(
                image_bytes,
                width="stretch",
                timing_collector=timing_collector,
                subject=subject,
                cache_detail="session cache hit",
            )
            return image_bytes

    with timed_span(timing_collector, build_label):
        figure = render_figure(recipe)
    if figure is None:
        return None
    try:
        with timed_span(timing_collector, matplotlib_render_span_label(subject)):
            image_bytes = render_matplotlib_figure(
                figure,
                width="stretch",
                timing_collector=timing_collector,
                subject=subject,
            )
    finally:
        dispose_matplotlib_figure(figure)
    if image_bytes is not None and render_mode == "image":
        preparation.cache_put(
            "png",
            png_key,
            image_bytes,
            size_bytes=len(image_bytes),
        )
    return image_bytes


def render_stretched_time_bin_control(
    label,
    options,
    widget_key,
    *,
    on_change=None,
    on_change_args=(),
):
    """Render one compact time-bin selector across its available container width."""
    if hasattr(st, "segmented_control"):
        control_kwargs = {
            "key": widget_key,
            "label_visibility": "collapsed",
            "width": "stretch",
        }
        if on_change is not None:
            control_kwargs["on_change"] = on_change
            control_kwargs["args"] = tuple(on_change_args)
        return st.segmented_control(label, options, **control_kwargs)

    radio_kwargs = {
        "horizontal": True,
        "key": widget_key,
        "label_visibility": "collapsed",
    }
    if on_change is not None:
        radio_kwargs["on_change"] = on_change
        radio_kwargs["args"] = tuple(on_change_args)
    return st.radio(label, options, **radio_kwargs)


def render_prompted_segment_time_bin_control(
    label,
    options,
    widget_key,
    *,
    on_change=None,
    on_change_args=(),
):
    """Render an instruction prompt above a full-width segment-bin selector."""
    st.markdown(
        transition_prompt_html(label),
        unsafe_allow_html=True,
    )
    return render_stretched_time_bin_control(
        label,
        options,
        widget_key,
        on_change=on_change,
        on_change_args=on_change_args,
    )
