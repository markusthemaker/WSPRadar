"""Thread-safe ownership helpers for Matplotlib's non-interactive Agg backend."""

from contextlib import contextmanager
from functools import wraps
import threading
from time import perf_counter

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure


_matplotlib_operation_lock = threading.RLock()
_matplotlib_profile_state = threading.local()


@contextmanager
def matplotlib_profile_collector(timing_collector):
    """Bind one timing collector to Matplotlib work on the current thread."""
    previous = getattr(_matplotlib_profile_state, "collector", None)
    _matplotlib_profile_state.collector = timing_collector
    try:
        yield
    finally:
        _matplotlib_profile_state.collector = previous


@contextmanager
def matplotlib_operation_lock():
    """Serialize Matplotlib operations and profile outermost lock ownership."""
    depth = getattr(_matplotlib_profile_state, "lock_depth", 0)
    if depth:
        with _matplotlib_operation_lock:
            _matplotlib_profile_state.lock_depth = depth + 1
            try:
                yield
            finally:
                _matplotlib_profile_state.lock_depth = depth
        return

    collector = getattr(_matplotlib_profile_state, "collector", None)
    wait_started = perf_counter()
    _matplotlib_operation_lock.acquire()
    wait_elapsed = perf_counter() - wait_started
    held_started = perf_counter()
    _matplotlib_profile_state.lock_depth = 1
    try:
        yield
    finally:
        held_elapsed = perf_counter() - held_started
        _matplotlib_profile_state.lock_depth = 0
        _matplotlib_operation_lock.release()
        if collector is not None and hasattr(collector, "add_counter"):
            collector.add_counter("matplotlib lock wait", wait_elapsed)
            collector.add_counter("matplotlib lock held", held_elapsed)


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
