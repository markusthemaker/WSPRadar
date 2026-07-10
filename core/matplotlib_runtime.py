"""Thread-safe ownership helpers for Matplotlib's non-interactive Agg backend."""

from contextlib import contextmanager
from functools import wraps
import threading

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure


_matplotlib_operation_lock = threading.RLock()


@contextmanager
def matplotlib_operation_lock():
    """Serialize Matplotlib operations that rely on process-global internals."""
    with _matplotlib_operation_lock:
        yield


def synchronized_matplotlib(function):
    """Run one complete Matplotlib figure-building function under the shared lock."""
    @wraps(function)
    def synchronized(*args, **kwargs):
        with matplotlib_operation_lock():
            return function(*args, **kwargs)

    return synchronized


def create_agg_figure(*, figsize, facecolor, dpi=None):
    """Create an Agg-backed figure outside pyplot's process-global registry."""
    figure_kwargs = {
        "figsize": figsize,
        "facecolor": facecolor,
    }
    if dpi is not None:
        figure_kwargs["dpi"] = dpi

    with matplotlib_operation_lock():
        figure = Figure(**figure_kwargs)
        FigureCanvasAgg(figure)
    return figure


def ensure_agg_canvas(figure):
    """Return a stable local Agg canvas attached to the supplied figure."""
    canvas = getattr(figure, "canvas", None)
    if not isinstance(canvas, FigureCanvasAgg):
        canvas = FigureCanvasAgg(figure)
    return canvas


def dispose_agg_figure(figure):
    """Release artists and large image arrays without touching other figures."""
    if figure is None:
        return
    with matplotlib_operation_lock():
        figure.clear()
