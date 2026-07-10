"""Streamlit rendering helpers for Matplotlib figures."""

from io import BytesIO
import os
from time import perf_counter

import streamlit as st

from core.matplotlib_runtime import (
    dispose_agg_figure,
    ensure_agg_canvas,
    matplotlib_operation_lock,
)


MATPLOTLIB_RENDER_MODE_ENV = "WSPRADAR_MATPLOTLIB_RENDER_MODE"
DEFAULT_MATPLOTLIB_RENDER_MODE = "image"
DEFAULT_MATPLOTLIB_IMAGE_DPI = 100
DEFAULT_MATPLOTLIB_PNG_COMPRESSION_LEVEL = 1


def dispose_matplotlib_figure(fig):
    """Release all artists and large image arrays owned by a rendered figure."""
    dispose_agg_figure(fig)


def _format_byte_size(byte_count):
    """Return a compact binary byte-size label."""
    if byte_count >= 1024 * 1024:
        return f"{byte_count / (1024 * 1024):.2f} MiB"
    if byte_count >= 1024:
        return f"{byte_count / 1024:.1f} KiB"
    return f"{byte_count} B"


def _figure_pixel_dimensions(fig, dpi):
    """Return the expected saved image dimensions from figure inches and DPI."""
    width_inches, height_inches = fig.get_size_inches()
    return int(round(width_inches * dpi)), int(round(height_inches * dpi))


def _png_pixel_dimensions(image_bytes):
    """Return exact PNG pixel dimensions from the IHDR header when available."""
    png_signature = b"\x89PNG\r\n\x1a\n"
    if len(image_bytes) >= 24 and image_bytes.startswith(png_signature):
        return (
            int.from_bytes(image_bytes[16:20], "big"),
            int.from_bytes(image_bytes[20:24], "big"),
        )
    return None


def _image_detail(*, byte_count=None, pixel_dimensions=None, dpi=None, compression_level=None):
    """Return profiler detail for encoded figure images."""
    details = []
    if byte_count is not None:
        details.append(_format_byte_size(byte_count))
    if pixel_dimensions is not None:
        details.append(f"{pixel_dimensions[0]}x{pixel_dimensions[1]} px")
    if dpi is not None:
        details.append(f"{dpi:g} dpi")
    if compression_level is not None:
        details.append(f"png compression {compression_level}")
    return " | ".join(details)


def get_matplotlib_render_mode():
    """Return the active Matplotlib display mode for Streamlit."""
    mode = os.getenv(MATPLOTLIB_RENDER_MODE_ENV, DEFAULT_MATPLOTLIB_RENDER_MODE)
    mode = str(mode).strip().lower()
    if mode in {"pyplot", "st.pyplot"}:
        return "pyplot"
    return "image"


def matplotlib_render_span_label(subject):
    """Return a profiler label that identifies the active Streamlit render path."""
    streamlit_call = "st.pyplot" if get_matplotlib_render_mode() == "pyplot" else "st.image"
    return f"{streamlit_call} {subject}"


def _save_figure_as_preview_png(fig, image_buffer, *, dpi, bbox_inches):
    """Save a display-only PNG with low compression, falling back if unsupported."""
    savefig_kwargs = {
        "format": "png",
        "dpi": dpi,
        "bbox_inches": bbox_inches,
        "facecolor": fig.get_facecolor(),
        "edgecolor": fig.get_edgecolor(),
    }
    with matplotlib_operation_lock():
        try:
            fig.savefig(
                image_buffer,
                **savefig_kwargs,
                pil_kwargs={
                    "compress_level": DEFAULT_MATPLOTLIB_PNG_COMPRESSION_LEVEL,
                    "optimize": False,
                },
            )
            return DEFAULT_MATPLOTLIB_PNG_COMPRESSION_LEVEL
        except TypeError:
            image_buffer.seek(0)
            image_buffer.truncate(0)
            fig.savefig(image_buffer, **savefig_kwargs)
            return None


def _draw_figure_preview_image(fig, *, dpi):
    """Draw the figure canvas and return a Pillow RGBA image plus pixel dimensions."""
    from PIL import Image

    with matplotlib_operation_lock():
        canvas = ensure_agg_canvas(fig)
        original_dpi = fig.dpi
        try:
            fig.set_dpi(dpi)
            canvas.draw()
            width, height = canvas.get_width_height()
            image = Image.frombuffer(
                "RGBA",
                (width, height),
                canvas.buffer_rgba(),
                "raw",
                "RGBA",
                0,
                1,
            ).copy()
        finally:
            fig.set_dpi(original_dpi)
    return image, (width, height)


def _serialize_preview_png(image, image_buffer):
    """Serialize an already-rendered preview image to low-compression PNG bytes."""
    image.save(
        image_buffer,
        format="PNG",
        compress_level=DEFAULT_MATPLOTLIB_PNG_COMPRESSION_LEVEL,
        optimize=False,
    )
    return DEFAULT_MATPLOTLIB_PNG_COMPRESSION_LEVEL


def render_matplotlib_figure(
    fig,
    *,
    width="stretch",
    bbox_inches=None,
    dpi=DEFAULT_MATPLOTLIB_IMAGE_DPI,
    timing_collector=None,
    subject="figure",
):
    """Render a Matplotlib figure through the configured Streamlit display path."""
    pixel_dimensions = _figure_pixel_dimensions(fig, dpi)
    if get_matplotlib_render_mode() == "pyplot":
        detail = _image_detail(pixel_dimensions=pixel_dimensions, dpi=dpi)
        if timing_collector is None:
            with matplotlib_operation_lock():
                st.pyplot(fig, width=width, bbox_inches=bbox_inches)
        else:
            with timing_collector.span(f"st.pyplot {subject} display", detail=detail):
                with matplotlib_operation_lock():
                    st.pyplot(fig, width=width, bbox_inches=bbox_inches)
        return

    image_buffer = BytesIO()
    if bbox_inches is None:
        draw_start = perf_counter()
        try:
            image, encoded_dimensions = _draw_figure_preview_image(fig, dpi=dpi)
            draw_elapsed = perf_counter() - draw_start
            draw_detail = _image_detail(pixel_dimensions=encoded_dimensions, dpi=dpi)
            if timing_collector is not None:
                timing_collector.add(f"{subject} canvas draw", draw_elapsed, detail=draw_detail)

            serialization_start = perf_counter()
            compression_level = _serialize_preview_png(image, image_buffer)
            serialization_elapsed = perf_counter() - serialization_start
            image_bytes = image_buffer.getvalue()
            detail = _image_detail(
                byte_count=len(image_bytes),
                pixel_dimensions=encoded_dimensions,
                dpi=dpi,
                compression_level=compression_level,
            )
            if timing_collector is not None:
                timing_collector.add(f"{subject} PNG serialization", serialization_elapsed, detail=detail)
        except ImportError:
            encode_start = perf_counter()
            compression_level = _save_figure_as_preview_png(
                fig,
                image_buffer,
                dpi=dpi,
                bbox_inches=bbox_inches,
            )
            image_bytes = image_buffer.getvalue()
            encoded_dimensions = _png_pixel_dimensions(image_bytes) or pixel_dimensions
            detail = _image_detail(
                byte_count=len(image_bytes),
                pixel_dimensions=encoded_dimensions,
                dpi=dpi,
                compression_level=compression_level,
            )
            if timing_collector is not None:
                timing_collector.add(f"{subject} PNG encode fallback", perf_counter() - encode_start, detail=detail)
    else:
        encode_start = perf_counter()
        compression_level = _save_figure_as_preview_png(
            fig,
            image_buffer,
            dpi=dpi,
            bbox_inches=bbox_inches,
        )
        image_bytes = image_buffer.getvalue()
        encoded_dimensions = _png_pixel_dimensions(image_bytes) or pixel_dimensions
        detail = _image_detail(
            byte_count=len(image_bytes),
            pixel_dimensions=encoded_dimensions,
            dpi=dpi,
            compression_level=compression_level,
        )
        if timing_collector is not None:
            timing_collector.add(f"{subject} PNG encode tight-bbox", perf_counter() - encode_start, detail=detail)

    if timing_collector is None:
        st.image(image_bytes, width=width)
    else:
        with timing_collector.span(f"st.image {subject} display", detail=detail):
            st.image(image_bytes, width=width)
