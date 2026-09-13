"""Owned export registration and one coherent queued package contract."""

from contextlib import nullcontext
from copy import deepcopy
import hashlib
import io
import json
from types import SimpleNamespace
import zipfile

import numpy as np
import pandas as pd
import pytest

from i18n import T
from config import DEMO_PROFILES
from ui import config_io, results_export, result_state, run_lifecycle
from ui.export_content import OwnedExportContent
from ui.export_payloads import (
    ExportSelection, ExportTables, InspectorExportPayload, PerformanceFigureRecipes,
)
from ui.export_registry import ExportRegistry


def _draft():
    return InspectorExportPayload(
        analysis_id="TX_ABS", family="performance",
        selection=ExportSelection(
            selected_segment="Full Range | All Directions",
            selected_distance="Full Range", selected_direction="All Directions",
            selected_ranges=["Full Range"], selected_directions=["All Directions"],
            show_non_joint=False, evidence_time_bin="1h",
            selected_stations=["K1AAA (FN31)"],
            selected_evidence_figure_descriptions={"figure": "Original description"},
        ),
        tables=ExportTables(
            station_insights_df=pd.DataFrame({"Station": ["K1AAA"], "SNR": [-8.0]}),
            drilldown_selected_df=pd.DataFrame({"UTC": ["2026-09-13T00:00:00Z"], "SNR": [-8.0]}),
            all_drilldown_context={
                "station_meta_df": pd.DataFrame({"Station": ["K1AAA"], "km": [100.0]}),
                "station_col": "Station", "km_col": "km",
            },
        ),
        figures=PerformanceFigureRecipes(
            segment_figure_recipe={"kind": "test-recipe", "nested": {"samples": np.array([1.0, 2.0])}},
        ),
    )


def _state():
    return {
        "run_id": 7, "lang": "en",
        "val_config_profile": {"id": "portable-run", "title": {"en": "Original profile"}},
        "val_config_extensions": {"example": {"revision": 1}},
        "config_settings": {"analysis_direction": "tx", "callsign": "N1TEST"},
        result_state.EXPORT_RUN_ID_KEY: 7,
        result_state.EXPORT_STATE_KEY: ExportRegistry(),
    }


def _prepare_bytes(state):
    state.update({
        result_state.EXPORT_ZIP_BYTES_KEY: b"prepared bytes",
        result_state.EXPORT_ZIP_FILENAME_KEY: "results.zip",
        result_state.EXPORT_ZIP_SIGNATURE_KEY: "prepared-signature",
    })


def _patch_config_capture(monkeypatch, state):
    """Isolate package ownership from separately tested config validation."""
    def parts(current):
        return {
            "settings": current["config_settings"],
            "profile": current.get("val_config_profile"),
            "extensions": current.get("val_config_extensions", {}),
        }
    def config_signature(*, title, state):
        assert title is None
        encoded = json.dumps(parts(state), sort_keys=True, ensure_ascii=False,
                             allow_nan=False, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()
    def config_payload(*, state, language):
        assert language in {"en", "de"}
        return json.dumps(parts(state), ensure_ascii=False).encode("utf-8"), "run.config"
    monkeypatch.setattr(results_export, "build_config_state_signature", config_signature)
    monkeypatch.setattr(results_export, "build_config_payload", config_payload)
    monkeypatch.setattr(results_export, "st", SimpleNamespace(session_state=state))


def test_registered_block_detaches_source_and_every_exposed_projection():
    table = pd.DataFrame({"station": ["K1AAA"], "notes": [{"labels": ["original"]}]})
    source = {
        "analysis_id": "TX_ABS", "mode_folder": "performance",
        "map_context": {"nested": ["original"]},
        "recipe": {"samples": np.array([1.0, 2.0])},
        "all_drilldown_context": {"station_meta_df": table},
    }
    registry = ExportRegistry({"TX_ABS": source})
    owned = registry["TX_ABS"]
    signature = owned.signature
    source["map_context"]["nested"].append("caller edit")
    source["recipe"]["samples"][0] = 99.0
    table.at[0, "notes"]["labels"].append("caller edit")
    source["added_later"] = True

    field = owned["recipe"]
    field["samples"][1] = 77.0
    projection = owned.materialize()
    projection["map_context"]["nested"].append("reader edit")
    projection["all_drilldown_context"]["station_meta_df"].at[0, "notes"]["labels"].append("reader edit")
    with pytest.raises(TypeError):
        registry["TX_ABS"] = source

    np.testing.assert_array_equal(owned["recipe"]["samples"], [1.0, 2.0])
    assert owned["map_context"] == {"nested": ["original"]}
    assert owned["all_drilldown_context"]["station_meta_df"].at[0, "notes"] == {"labels": ["original"]}
    assert "added_later" not in owned
    assert owned.signature == signature
    assert deepcopy(owned) is owned


def test_identical_registration_keeps_owned_block_and_prepared_zip(monkeypatch):
    state = _state()
    monkeypatch.setattr(results_export, "st", SimpleNamespace(session_state=state))
    draft = _draft()
    results_export.register_inspector_export(draft, T["en"])
    registry = state[result_state.EXPORT_STATE_KEY]
    owned = registry["TX_ABS"]
    _prepare_bytes(state)
    existing_zip = {key: state[key] for key in result_state.PREPARED_RESULT_STATE_KEYS}
    equal_draft = deepcopy(draft)
    def reject_capture(_cls, _value):
        raise AssertionError("Unchanged registration must not recapture its graph")
    monkeypatch.setattr(OwnedExportContent, "capture", classmethod(reject_capture))

    results_export.register_inspector_export(equal_draft, T["en"])

    assert state[result_state.EXPORT_STATE_KEY] is registry
    assert registry["TX_ABS"] is owned
    for key, value in existing_zip.items():
        assert state[key] is value


@pytest.mark.parametrize("change", ["nested-array", "all-station-value", "description"])
def test_changed_registered_content_invalidates_zip_and_keeps_previous_snapshot(monkeypatch, change):
    state = _state()
    monkeypatch.setattr(results_export, "st", SimpleNamespace(session_state=state))
    draft = _draft()
    results_export.register_inspector_export(draft, T["en"])
    old = state[result_state.EXPORT_STATE_KEY]["TX_ABS"]
    old_signature = old.signature
    _prepare_bytes(state)
    if change == "nested-array":
        draft.figures.segment_figure_recipe["nested"]["samples"][0] = 4.0
    elif change == "all-station-value":
        draft.tables.all_drilldown_context["station_meta_df"].loc[0, "km"] = 250.0
    else:
        draft.selection.selected_evidence_figure_descriptions["figure"] = "Revised description"

    results_export.register_inspector_export(draft, T["en"])

    current = state[result_state.EXPORT_STATE_KEY]["TX_ABS"]
    assert current is not old
    assert current.map_content is old.map_content
    assert current.signature != old_signature
    assert old.signature == old_signature
    assert all(key not in state for key in result_state.PREPARED_RESULT_STATE_KEYS)
    np.testing.assert_array_equal(old["segment_figure_recipe"]["nested"]["samples"], [1.0, 2.0])
    assert old["all_drilldown_context"]["station_meta_df"].loc[0, "km"] == 100.0
    assert old["selected_evidence_figure_descriptions"]["figure"] == "Original description"


@pytest.mark.parametrize("change", ["profile", "extensions", "language", "run", "recipe", "translations"])
def test_package_guard_rejects_changed_dependencies(monkeypatch, change):
    state = _state()
    _patch_config_capture(monkeypatch, state)
    translations = dict(T["en"])
    draft = _draft()
    results_export.register_inspector_export(draft, translations)
    payload = results_export._capture_export_package(translations)
    assert payload is not None
    assert results_export._package_is_current(payload, translations=translations)
    if change == "profile":
        state["val_config_profile"]["title"]["en"] = "New profile"
    elif change == "extensions":
        state["val_config_extensions"]["example"]["revision"] = 2
    elif change == "language":
        state["lang"] = "de"
    elif change == "run":
        state["run_id"] = 8
    elif change == "recipe":
        draft.figures.segment_figure_recipe["nested"]["samples"][1] = 8.0
        results_export.register_inspector_export(draft, translations)
    else:
        translations["hdr_results_download_evidence"] = "Changed heading"
    assert not results_export._package_is_current(payload, translations=translations)


def test_capture_signature_describes_captured_config_when_live_metadata_changes(monkeypatch):
    state = _state()
    _patch_config_capture(monkeypatch, state)
    results_export.register_inspector_export(_draft(), T["en"])
    original_builder = results_export.build_config_payload

    def build_then_edit_profile(**kwargs):
        config_bytes, filename = original_builder(**kwargs)
        state["val_config_profile"]["title"]["en"] = "Committed after config capture"
        return config_bytes, filename

    monkeypatch.setattr(results_export, "build_config_payload", build_then_edit_profile)

    payload = results_export._capture_export_package(T["en"])

    assert json.loads(payload.config_bytes)["profile"]["title"]["en"] == "Original profile"
    assert not results_export._package_is_current(payload)
    state["val_config_profile"]["title"]["en"] = "Original profile"
    assert results_export._package_is_current(payload)


@pytest.mark.parametrize("change", ["profile", "extensions", "selection"])
def test_real_config_capture_digest_survives_unchanged_rerender(monkeypatch, change):
    """Use the actual saved-config validator, writer and state signature together."""
    document = next(
        profile["configuration"] for profile in DEMO_PROFILES.values()
        if profile["configuration"]["settings"]["comparison_parameters"]["mode"] == "none"
    )
    state = {"run_id": 7, "lang": "en"}
    normalized_config = config_io.validate_config_document(deepcopy(document))
    config_io.apply_config_state_values(normalized_config, state)
    monkeypatch.setattr(results_export, "st", SimpleNamespace(session_state=state))
    draft = _draft()
    results_export.register_inspector_export(draft, T["en"])

    payload = results_export._capture_export_package(T["en"])

    assert payload is not None
    assert results_export._package_is_current(payload)
    registry = state[result_state.EXPORT_STATE_KEY]
    _prepare_bytes(state)
    run_lifecycle.begin_result_render(state, is_completed_rerender=True)
    results_export.register_inspector_export(deepcopy(draft), T["en"])
    assert state[result_state.EXPORT_STATE_KEY] is registry
    assert state[result_state.EXPORT_ZIP_BYTES_KEY] == b"prepared bytes"
    assert results_export._package_is_current(payload)

    if change == "profile":
        state["val_config_profile"]["title"]["en"] = "Revised saved metadata"
    elif change == "extensions":
        state["val_config_extensions"]["export_test"] = {"revision": 2}
    else:
        state["val_results_selected_stations_absolute"] = []
    assert not results_export._package_is_current(payload)


def test_zip_uses_one_captured_config_and_content_after_queue_state_changes(monkeypatch):
    state = _state()
    _patch_config_capture(monkeypatch, state)
    translations = dict(T["en"])
    draft = _draft()
    results_export.register_inspector_export(draft, translations)
    payload = results_export._capture_export_package(translations)
    initial_signature = payload.signature
    state["val_config_profile"]["title"]["en"] = "Changed after queue entry"
    draft.tables.station_insights_df.loc[0, "SNR"] = -1.0
    draft.figures.segment_figure_recipe["nested"]["samples"][0] = 55.0
    results_export.register_inspector_export(draft, translations)
    translations["hdr_results_download_evidence"] = "Changed after capture"
    rendered = []
    monkeypatch.setattr(results_export, "_analysis_cache_export_paths", lambda _blocks: {})
    monkeypatch.setattr(results_export, "_render_map_png_for_block", lambda _block, *, translations: b"map image")
    monkeypatch.setattr(results_export, "_build_all_drilldown_for_block", lambda block, *, translations: block["all_drilldown_context"]["station_meta_df"])
    def inspector_image(block, _name):
        rendered.append(block["segment_figure_recipe"]["nested"]["samples"].tolist())
        return None
    monkeypatch.setattr(results_export, "_render_inspector_png_for_block", inspector_image)
    def metadata(blocks, config, paths, *, payload):
        return {"profile": config["profile"], "export_signature": payload.signature,
                "heading": payload.translations.materialize()["hdr_results_download_evidence"]}
    monkeypatch.setattr(results_export, "_build_run_metadata", metadata)

    zip_bytes, _filename = results_export.build_results_zip(translations, payload=payload)

    assert rendered and all(samples == [1.0, 2.0] for samples in rendered)
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        config = json.loads(archive.read(f"{payload.root_folder}/config/wspradar_config.config"))
        run_metadata = json.loads(archive.read(f"{payload.root_folder}/config/run_metadata.json"))
        table = pd.read_csv(io.BytesIO(archive.read(f"{payload.root_folder}/performance/table_station_insights_current_segment.csv")))
    assert config["profile"]["title"]["en"] == "Original profile"
    assert run_metadata["export_signature"] == initial_signature
    assert run_metadata["heading"] == T["en"]["hdr_results_download_evidence"]
    assert table.loc[0, "SNR"] == -8.0
    assert not results_export._package_is_current(payload, translations=translations)


@pytest.mark.parametrize("change_during_preparation", [False, True])
def test_footer_never_publishes_a_stale_queued_package(monkeypatch, change_during_preparation):
    state = _state()
    _patch_config_capture(monkeypatch, state)
    results_export.register_inspector_export(_draft(), T["en"])
    downloads = []
    fake_streamlit = SimpleNamespace(
        session_state=state,
        markdown=lambda *_args, **_kwargs: None,
        columns=lambda *_args, **_kwargs: [nullcontext(), nullcontext(), nullcontext()],
        button=lambda *_args, **_kwargs: True,
        download_button=lambda *_args, **kwargs: downloads.append(kwargs),
        popover=lambda *_args, **_kwargs: SimpleNamespace(open=False),
    )
    monkeypatch.setattr(results_export, "st", fake_streamlit)
    monkeypatch.setattr(results_export, "render_result_guidance_popover", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(results_export, "render_config_save_control", lambda **_kwargs: None)
    captured = []
    def prepare(_translations, *, payload):
        captured.append(payload)
        if change_during_preparation:
            state["val_config_profile"]["title"]["en"] = "Edited while queued"
        return b"captured zip", "captured.zip"
    monkeypatch.setattr(results_export, "_prepare_results_zip_with_admission", prepare)

    results_export.render_download_all_results(T["en"])

    assert len(captured) == 1
    if change_during_preparation:
        assert downloads == []
        assert all(key not in state for key in result_state.PREPARED_RESULT_STATE_KEYS)
    else:
        assert state[result_state.EXPORT_ZIP_BYTES_KEY] == b"captured zip"
        assert state[result_state.EXPORT_ZIP_SIGNATURE_KEY] == captured[0].signature
        assert downloads[0]["data"] == b"captured zip"
