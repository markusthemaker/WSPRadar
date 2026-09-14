from dataclasses import replace
from types import SimpleNamespace

import pandas as pd
import pytest

from core.analysis_admission import AdmissionSnapshot, AnalysisQueueFull
from core.export_admission import EXPORT_ADMISSION_GATE
from i18n import T
from ui import results_export
from ui.export_content import OwnedExportContent
from ui.export_registry import ExportPackagePayload, RegisteredExportBlock


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
        self.errors = []
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

    def error(self, message):
        self.errors.append(message)


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


def _patch_package_capture(monkeypatch):
    """Keep admission tests independent of configuration and artifact fixtures."""
    payload = ExportPackagePayload(
        blocks=(), config_bytes=b"{}", translations=OwnedExportContent.capture(T["en"]),
        language="en", run_id=7, signature="captured-package",
        exported_utc="2026-09-13T10:00:00Z", root_folder="WSPRadar_export_test",
    )
    monkeypatch.setattr(results_export, "_capture_export_package", lambda _translations: payload)
    return payload


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
    captured_payload = _patch_package_capture(monkeypatch)

    def build_zip(translations, *, payload):
        assert translations is T["en"]
        assert payload is captured_payload
        assert permit.entered is True
        assert permit.released is False
        return b"prepared-zip", "results.zip"

    monkeypatch.setattr(results_export, "build_results_zip", build_zip)

    result = results_export._prepare_results_zip_with_admission(T["en"])

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


def test_required_map_artifact_failure_is_reported_and_releases_permit(
    monkeypatch,
):
    """Show a rerun action instead of returning a ZIP with no required map."""
    fake_st = _FakeStreamlit()
    permit = _Permit()
    gate = _AdmittingGate(permit)
    events = _patch_profiling(monkeypatch)
    monkeypatch.setattr(results_export, "st", fake_st)
    monkeypatch.setattr(results_export, "EXPORT_ADMISSION_GATE", gate)
    _patch_package_capture(monkeypatch)
    monkeypatch.setattr(
        results_export,
        "build_results_zip",
        lambda _translations, *, payload: (_ for _ in ()).throw(
            results_export.ExportArtifactUnavailableError(
                "Required compact map data is unavailable; run the analysis again"
            )
        ),
    )

    result = results_export._prepare_results_zip_with_admission(T["en"])

    assert result == (None, None)
    assert permit.released is True
    assert fake_st.errors == [
        "Analysis evidence could not be prepared. Please run the analysis again."
    ]
    assert events[-1][0] == "export_preparation"
    assert events[-1][1]["outcome"] == "ExportArtifactUnavailableError"
    assert events[-1][1]["zip_bytes"] == 0


@pytest.mark.parametrize("language", ["en", "de"])
def test_invalid_required_evidence_never_publishes_download(monkeypatch, tmp_path, language):
    """The real ZIP failure crosses admission and the footer without publishing bytes."""
    fake_st = _FakeStreamlit()
    fake_st.session_state["lang"] = language
    permit = _Permit()
    events = _patch_profiling(monkeypatch)
    monkeypatch.setattr(results_export, "st", fake_st)
    monkeypatch.setattr(results_export, "EXPORT_ADMISSION_GATE", _AdmittingGate(permit))
    parquet_path = tmp_path / "invalid-evidence.parquet"
    pd.DataFrame({"wrong_schema": [1]}).to_parquet(parquet_path)
    block = {
        "analysis_id": "RX_ABS", "database_source": "wspr_live",
        "mode_folder": results_export.PERFORMANCE_EXPORT_FOLDER,
        "is_compare": False, "is_sequential": False,
        "analysis_kind": "opportunity",
        "map_context": {"parquet_path": str(parquet_path)},
        "all_drilldown_context": {
            "station_meta_df": pd.DataFrame({"Station": ["K1ABC"], "Grid": ["FN31"]}),
            "station_col": "Station", "loc_col": "Grid",
        },
    }
    payload = replace(
        _patch_package_capture(monkeypatch),
        blocks=(("RX_ABS", RegisteredExportBlock.capture(block)),),
        translations=OwnedExportContent.capture(T[language]), language=language,
    )
    monkeypatch.setattr(results_export, "_capture_export_package", lambda *_args: payload)
    monkeypatch.setattr(results_export, "_ensure_current_export_state", lambda: {"RX_ABS": block})
    monkeypatch.setattr(results_export, "_export_signature", lambda *_args: payload.signature)
    monkeypatch.setattr(results_export, "_render_map_png_for_block", lambda *_args, **_kwargs: b"map")
    monkeypatch.setattr(results_export, "_render_inspector_png_for_block", lambda *_args: None)
    monkeypatch.setattr(results_export, "render_result_guidance_popover", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(results_export, "render_config_save_control", lambda **_kwargs: None)
    downloads = []
    fake_st.markdown = lambda *_args, **_kwargs: None
    fake_st.columns = lambda *_args, **_kwargs: [_Context(), _Context(), _Context()]
    fake_st.button = lambda *_args, **_kwargs: True
    fake_st.download_button = lambda *_args, **kwargs: downloads.append(kwargs)
    fake_st.popover = lambda *_args, **_kwargs: SimpleNamespace(open=False)

    results_export.render_download_all_results(T[language])

    assert permit.released is True
    assert fake_st.errors == [T[language]["err_analysis_processing_failed"]]
    assert downloads == []
    assert results_export.EXPORT_ZIP_BYTES_KEY not in fake_st.session_state
    assert results_export.EXPORT_ZIP_FILENAME_KEY not in fake_st.session_state
    assert results_export.EXPORT_ZIP_SIGNATURE_KEY not in fake_st.session_state
    assert events[-1][1]["outcome"] == "ExportArtifactUnavailableError"
    assert events[-1][1]["zip_bytes"] == 0


def test_full_export_queue_does_not_start_zip_construction(monkeypatch):
    fake_st = _FakeStreamlit()
    events = _patch_profiling(monkeypatch)
    monkeypatch.setattr(results_export, "st", fake_st)
    monkeypatch.setattr(results_export, "EXPORT_ADMISSION_GATE", _FullGate())
    _patch_package_capture(monkeypatch)
    monkeypatch.setattr(
        results_export,
        "build_results_zip",
        lambda _translations, *, payload: (_ for _ in ()).throw(
            AssertionError("ZIP build must not start")
        ),
    )

    result = results_export._prepare_results_zip_with_admission(T["en"])

    assert result == (None, None)
    assert fake_st.warnings == [
        "High demand right now. The export queue is full. Please try again shortly."
    ]
    assert [event for event, _values in events] == ["export_admission"]
    assert events[0][1]["outcome"] == "queue_full"
