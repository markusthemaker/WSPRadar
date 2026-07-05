"""Small timing collector for local performance profiling."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import logging
from time import perf_counter
from typing import Iterator


@dataclass
class TimingSpan:
    """One measured execution span."""

    label: str
    elapsed_seconds: float
    detail: str = ""
    depth: int = 0


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


class PerformanceTimer:
    """Collect named timing spans without depending on Streamlit."""

    def __init__(self) -> None:
        self._spans: list[TimingSpan] = []
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
        return "\n".join(lines)

    def log_report(self, *, analysis_title: str = "") -> None:
        """Write a nested timing report to the terminal/log stream."""
        _profile_logger().info(self.format_report(analysis_title=analysis_title))
