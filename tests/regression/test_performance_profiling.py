import threading
import time

import pytest

from core import performance_timer
from core.matplotlib_runtime import (
    matplotlib_operation_lock,
    matplotlib_profile_collector,
)
from core.performance_timer import PerformanceTimer


def test_cumulative_counters_do_not_inflate_analysis_total():
    timer = PerformanceTimer()
    timer.add("work", 0.25)
    timer.add_counter("matplotlib lock wait", 0.10)
    timer.add_counter("matplotlib lock wait", 0.15)
    timer.add_counter("matplotlib lock held", 0.20)

    assert timer.total_seconds() == pytest.approx(0.25)
    assert timer.counter_rows() == [
        {
            "analysis": "",
            "counter": "matplotlib lock wait",
            "seconds": 0.25,
            "count": 2,
        },
        {
            "analysis": "",
            "counter": "matplotlib lock held",
            "seconds": 0.2,
            "count": 1,
        },
    ]
    report = timer.format_report(analysis_title="test")
    assert "cumulative counters (excluded from total)" in report
    assert "matplotlib lock wait" in report
    assert "[count=2]" in report


def test_matplotlib_lock_profiles_wait_and_outermost_hold_once():
    holder_ready = threading.Event()
    release_holder = threading.Event()

    def hold_lock():
        with matplotlib_operation_lock():
            holder_ready.set()
            assert release_holder.wait(timeout=1.0)

    holder = threading.Thread(target=hold_lock)
    holder.start()
    assert holder_ready.wait(timeout=1.0)

    release_timer = threading.Timer(0.03, release_holder.set)
    release_timer.start()
    timer = PerformanceTimer()
    with matplotlib_profile_collector(timer):
        with matplotlib_operation_lock():
            with matplotlib_operation_lock():
                time.sleep(0.005)

    holder.join(timeout=1.0)
    release_timer.join(timeout=1.0)
    assert not holder.is_alive()

    counters = {row["counter"]: row for row in timer.counter_rows()}
    assert counters["matplotlib lock wait"]["seconds"] >= 0.02
    assert counters["matplotlib lock wait"]["count"] == 1
    assert counters["matplotlib lock held"]["seconds"] >= 0.004
    assert counters["matplotlib lock held"]["count"] == 1


def test_process_memory_profiling_returns_sensible_values():
    current = performance_timer.process_rss_bytes()
    peak = performance_timer.process_peak_rss_bytes()

    assert current is None or current > 0
    assert peak is None or peak > 0
    if current is not None and peak is not None:
        assert peak >= current


def test_performance_event_formats_seconds_and_memory(monkeypatch):
    messages = []

    class CapturingLogger:
        def info(self, message):
            messages.append(message)

    monkeypatch.setattr(performance_timer, "_profile_logger", lambda: CapturingLogger())
    performance_timer.log_performance_event(
        "analysis_run",
        duration_seconds=1.23456,
        rss_end_bytes=1024 * 1024,
        outcome="completed",
    )

    assert messages == [
        'PERF event="analysis_run" duration_seconds=1.235s '
        'rss_end_bytes="1.0 MiB" outcome=completed'
    ]
