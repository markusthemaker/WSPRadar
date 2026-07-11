from core.analysis_admission import AdmissionSnapshot, AnalysisQueueFull
from core.export_admission import EXPORT_ADMISSION_GATE
from ui import results_export


class _Context:
    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc_value, _traceback):
        return False


class _Slot(_Context):
    def __init__(self):
        self.empty_calls = 0
        self.markdowns = []

    def container(self):
        return self

    def empty(self):
        self.empty_calls += 1

    def markdown(self, value):
        self.markdowns.append(value)


class _Status(_Context):
    def __init__(self, label):
        self.label = label
        self.updates = []

    def update(self, **values):
        self.updates.append(values)


class _FakeStreamlit:
    def __init__(self):
        self.session_state = {"run_id": 7}
        self.slots = []
        self.statuses = []
        self.warnings = []
        self.spinner_labels = []

    def empty(self):
        slot = _Slot()
        self.slots.append(slot)
        return slot

    def status(self, label, **_kwargs):
        status = _Status(label)
        self.statuses.append(status)
        return status

    def spinner(self, label):
        self.spinner_labels.append(label)
        return _Context()

    def warning(self, message):
        self.warnings.append(message)


class _Permit(_Context):
    def __init__(self):
        self.entered = False
        self.released = False
        self.touched = False

    def __enter__(self):
        self.entered = True
        return self

    def __exit__(self, _exc_type, _exc_value, _traceback):
        self.released = True
        return False

    def touch(self):
        self.touched = True
        return True


class _AdmittingGate:
    def __init__(self, permit):
        self.permit = permit
        self.owners = []

    def acquire(self, *, owner, on_wait):
        self.owners.append(owner)
        on_wait(AdmissionSnapshot(
            position=2,
            active=1,
            queued=2,
            max_active=1,
            max_queued=10,
        ))
        return self.permit

    def counts(self):
        return (0, 0) if self.permit.released else (1, 0)


class _FullGate:
    def acquire(self, *, owner, on_wait):
        raise AnalysisQueueFull("full")

    def counts(self):
        return 1, 10


def _patch_profiling(monkeypatch):
    events = []
    monkeypatch.setattr(
        results_export,
        "log_performance_event",
        lambda event, **values: events.append((event, values)),
    )
    monkeypatch.setattr(results_export, "process_rss_bytes", lambda: 1234)
    monkeypatch.setattr(results_export, "process_peak_rss_bytes", lambda: 5678)
    return events


def test_export_gate_is_configured_independently_for_one_active_export():
    from core.analysis_admission import ANALYSIS_ADMISSION_GATE

    assert EXPORT_ADMISSION_GATE is not ANALYSIS_ADMISSION_GATE
    assert EXPORT_ADMISSION_GATE.max_active == 1
    assert EXPORT_ADMISSION_GATE.max_queued == 10


def test_export_preparation_waits_for_admission_and_releases_permit(monkeypatch):
    fake_st = _FakeStreamlit()
    permit = _Permit()
    gate = _AdmittingGate(permit)
    events = _patch_profiling(monkeypatch)
    monkeypatch.setattr(results_export, "st", fake_st)
    monkeypatch.setattr(results_export, "EXPORT_ADMISSION_GATE", gate)

    def build_zip():
        assert permit.entered is True
        assert permit.released is False
        return b"prepared-zip", "results.zip"

    monkeypatch.setattr(results_export, "build_results_zip", build_zip)

    result = results_export._prepare_results_zip_with_admission({})

    assert result == (b"prepared-zip", "results.zip")
    assert permit.touched is True
    assert permit.released is True
    assert gate.owners[0].endswith(":7:export")
    assert fake_st.statuses[0].label.endswith("position 2 in the export queue.")
    assert fake_st.slots[1].markdowns == ["1/1 export preparation active; 2 waiting."]
    assert fake_st.warnings == []
    assert [event for event, _values in events] == [
        "export_admission",
        "export_preparation",
    ]
    assert events[0][1]["outcome"] == "admitted"
    assert events[0][1]["initial_queue_position"] == 2
    assert events[1][1]["outcome"] == "completed"
    assert events[1][1]["zip_bytes"] == len(b"prepared-zip")


def test_full_export_queue_does_not_start_zip_construction(monkeypatch):
    fake_st = _FakeStreamlit()
    events = _patch_profiling(monkeypatch)
    monkeypatch.setattr(results_export, "st", fake_st)
    monkeypatch.setattr(results_export, "EXPORT_ADMISSION_GATE", _FullGate())
    monkeypatch.setattr(
        results_export,
        "build_results_zip",
        lambda: (_ for _ in ()).throw(AssertionError("ZIP build must not start")),
    )

    result = results_export._prepare_results_zip_with_admission({})

    assert result == (None, None)
    assert fake_st.warnings == [
        "High demand right now. The export queue is full. Please try again shortly."
    ]
    assert [event for event, _values in events] == ["export_admission"]
    assert events[0][1]["outcome"] == "queue_full"
