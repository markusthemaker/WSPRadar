"""Small timing collector for local performance profiling."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import logging
import os
import platform
from time import perf_counter
from typing import Iterator


@dataclass
class TimingSpan:
    """One measured execution span."""

    label: str
    elapsed_seconds: float
    detail: str = ""
    depth: int = 0


@dataclass
class MemorySample:
    """One lightweight memory observation."""

    label: str
    dataframe_bytes: int | None = None
    process_rss_bytes: int | None = None
    rows: int | None = None
    columns: int | None = None
    detail: str = ""
    depth: int = 0


@dataclass
class CumulativeCounter:
    """One cumulative profiler counter kept outside elapsed-time totals."""

    label: str
    elapsed_seconds: float = 0.0
    count: int = 0


def _windows_process_memory_bytes() -> tuple[int | None, int | None]:
    """Return current and peak Windows working-set bytes."""
    try:
        import ctypes
        from ctypes import wintypes
    except Exception:
        return None, None

    class ProcessMemoryCounters(ctypes.Structure):
        _fields_ = [
            ("cb", wintypes.DWORD),
            ("PageFaultCount", wintypes.DWORD),
            ("PeakWorkingSetSize", ctypes.c_size_t),
            ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t),
            ("PeakPagefileUsage", ctypes.c_size_t),
        ]

    counters = ProcessMemoryCounters()
    counters.cb = ctypes.sizeof(ProcessMemoryCounters)
    handle = ctypes.windll.kernel32.GetCurrentProcess()
    ok = ctypes.windll.psapi.GetProcessMemoryInfo(
        handle,
        ctypes.byref(counters),
        counters.cb,
    )
    if not ok:
        return None, None
    return int(counters.WorkingSetSize), int(counters.PeakWorkingSetSize)


def process_rss_bytes() -> int | None:
    """Return current process RSS in bytes when a lightweight backend is available."""
    try:
        import psutil
    except Exception:
        psutil = None

    if psutil is not None:
        try:
            return int(psutil.Process(os.getpid()).memory_info().rss)
        except Exception:
            pass

    if platform.system() == "Windows":
        current, _ = _windows_process_memory_bytes()
        return current

    if platform.system() == "Linux":
        try:
            with open("/proc/self/statm", encoding="ascii") as handle:
                resident_pages = int(handle.read().split()[1])
            return resident_pages * int(os.sysconf("SC_PAGE_SIZE"))
        except (IndexError, OSError, TypeError, ValueError):
            return None

    return None


def process_peak_rss_bytes() -> int | None:
    """Return process-lifetime peak RSS bytes when the platform exposes it."""
    if platform.system() == "Windows":
        _, peak = _windows_process_memory_bytes()
        return peak

    try:
        import resource
    except Exception:
        return None

    try:
        rss = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    except Exception:
        return None
    if platform.system() == "Darwin":
        return rss
    return rss * 1024


def _process_rss_bytes() -> int | None:
    """Compatibility wrapper for existing profiler call sites."""
    return process_rss_bytes()


def _format_bytes(value: int | None) -> str:
    """Return a compact binary byte string."""
    if value is None:
        return "n/a"
    units = ["B", "KiB", "MiB", "GiB"]
    amount = float(value)
    for unit in units:
        if abs(amount) < 1024.0 or unit == units[-1]:
            return f"{amount:.1f} {unit}" if unit != "B" else f"{int(amount)} B"
        amount /= 1024.0


def _profile_logger() -> logging.Logger:
    """Return a terminal logger for profile summaries."""
    logger = logging.getLogger("wspradar.performance")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


def log_performance_event(
    event: str,
    *,
    leading_blank_line: bool = False,
    trailing_blank_line: bool = False,
    **values,
) -> None:
    """Write one compact, optionally blank-line-framed performance event."""
    parts = [f'PERF event="{event}"']
    for key, value in values.items():
        if key.endswith("_bytes"):
            rendered = f'"{_format_bytes(value)}"'
        elif key.endswith("_seconds") and value is not None:
            rendered = f"{float(value):.3f}s"
        elif isinstance(value, float):
            rendered = f"{value:.3f}"
        elif isinstance(value, str) and any(character.isspace() for character in value):
            rendered = f'"{value}"'
        else:
            rendered = str(value)
        parts.append(f"{key}={rendered}")
    message = " ".join(parts)
    if leading_blank_line:
        message = f"\n{message}"
    if trailing_blank_line:
        message = f"{message}\n"
    _profile_logger().info(message)


class PerformanceTimer:
    """Collect named timing spans without depending on Streamlit."""

    def __init__(self) -> None:
        self._spans: list[TimingSpan] = []
        self._memory_samples: list[MemorySample] = []
        self._counters: dict[str, CumulativeCounter] = {}
        self._active_span_indexes: list[int] = []
        self._started_at = perf_counter()

    @contextmanager
    def span(self, label: str, detail: str = "") -> Iterator[None]:
        """Measure a block and store its elapsed wall-clock time."""
        depth = len(self._active_span_indexes)
        span = TimingSpan(label=label, elapsed_seconds=0.0, detail=detail, depth=depth)
        self._spans.append(span)
        span_index = len(self._spans) - 1
        self._active_span_indexes.append(span_index)
        start = perf_counter()
        try:
            yield
        finally:
            span.elapsed_seconds = perf_counter() - start
            self._active_span_indexes.pop()

    def add(self, label: str, elapsed_seconds: float, detail: str = "") -> None:
        """Record a pre-measured span."""
        self._spans.append(
            TimingSpan(
                label=label,
                elapsed_seconds=float(elapsed_seconds),
                detail=detail,
                depth=len(self._active_span_indexes),
            )
        )

    def add_memory(self, label: str, *, df=None, include_rss: bool = True, detail: str = "") -> None:
        """Record DataFrame memory and optional process RSS without retaining the frame."""
        dataframe_bytes = None
        rows = None
        columns = None
        if df is not None:
            try:
                dataframe_bytes = int(df.memory_usage(index=True, deep=True).sum())
                rows = int(df.shape[0])
                columns = int(df.shape[1])
            except Exception:
                dataframe_bytes = None
        self._memory_samples.append(
            MemorySample(
                label=label,
                dataframe_bytes=dataframe_bytes,
                process_rss_bytes=_process_rss_bytes() if include_rss else None,
                rows=rows,
                columns=columns,
                detail=detail,
                depth=len(self._active_span_indexes),
            )
        )

    def add_counter(self, label: str, elapsed_seconds: float) -> None:
        """Accumulate an observed duration without changing analysis totals."""
        counter = self._counters.setdefault(label, CumulativeCounter(label=label))
        counter.elapsed_seconds += float(elapsed_seconds)
        counter.count += 1

    def rows(self, *, analysis_title: str = "") -> list[dict[str, object]]:
        """Return Streamlit-friendly timing rows."""
        return [
            {
                "analysis": analysis_title,
                "span": f"{'  ' * span.depth}{span.label}",
                "seconds": round(span.elapsed_seconds, 3),
                "detail": span.detail,
            }
            for span in self._spans
        ]

    def memory_rows(self, *, analysis_title: str = "") -> list[dict[str, object]]:
        """Return Streamlit-friendly memory observation rows."""
        return [
            {
                "analysis": analysis_title,
                "span": f"{'  ' * sample.depth}{sample.label}",
                "dataframe_memory": sample.dataframe_bytes,
                "process_rss": sample.process_rss_bytes,
                "rows": sample.rows,
                "columns": sample.columns,
                "detail": sample.detail,
            }
            for sample in self._memory_samples
        ]

    def counter_rows(self, *, analysis_title: str = "") -> list[dict[str, object]]:
        """Return cumulative non-total profiler counters."""
        return [
            {
                "analysis": analysis_title,
                "counter": counter.label,
                "seconds": round(counter.elapsed_seconds, 3),
                "count": counter.count,
            }
            for counter in self._counters.values()
        ]

    def total_seconds(self) -> float:
        """Return summed duration of top-level spans."""
        return sum(span.elapsed_seconds for span in self._spans if span.depth == 0)

    def wall_seconds(self) -> float:
        """Return elapsed wall-clock time since this timer was created."""
        return perf_counter() - self._started_at

    def format_report(self, *, analysis_title: str = "") -> str:
        """Return a nested terminal-readable performance report."""
        heading = analysis_title or "analysis"
        lines = [f'PERF analysis="{heading}" total={self.total_seconds():.3f}s wall={self.wall_seconds():.3f}s']
        for span in self._spans:
            indent = "  " * (span.depth + 1)
            detail = f" [{span.detail}]" if span.detail else ""
            lines.append(f"{indent}{span.label:<38} {span.elapsed_seconds:8.3f}s{detail}")
        if self._counters:
            lines.append("  cumulative counters (excluded from total):")
            for counter in self._counters.values():
                lines.append(
                    f"    {counter.label:<36} "
                    f"{counter.elapsed_seconds:8.3f}s [count={counter.count}]"
                )
        if self._memory_samples:
            lines.append("  memory snapshots:")
            for sample in self._memory_samples:
                indent = "  " * (sample.depth + 2)
                shape = (
                    f" rows={sample.rows} cols={sample.columns}"
                    if sample.rows is not None and sample.columns is not None
                    else ""
                )
                detail = f" [{sample.detail}]" if sample.detail else ""
                lines.append(
                    f"{indent}{sample.label:<36} "
                    f"df={_format_bytes(sample.dataframe_bytes):>10} "
                    f"rss={_format_bytes(sample.process_rss_bytes):>10}"
                    f"{shape}{detail}"
                )
        return "\n".join(lines)

    def log_report(self, *, analysis_title: str = "") -> None:
        """Write a nested timing report to the terminal/log stream."""
        _profile_logger().info(self.format_report(analysis_title=analysis_title))
