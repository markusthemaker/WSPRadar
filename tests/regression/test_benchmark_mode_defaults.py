from types import SimpleNamespace

import pytest

from config import DEFAULT_BAND
from core.analysis_context import COMPARISON_NONE
from i18n import T
from ui import callbacks, state_manager
from ui.analysis_context_adapter import build_analysis_context_from_session_state
from ui.components.config_panel import _benchmark_mode_options
from ui.config_io import MODE_KEYS, _default_config


class _SessionState(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def __setattr__(self, key, value):
        self[key] = value


def test_benchmark_design_options_put_success_only_before_comparisons():
    assert list(MODE_KEYS) == [
        "none",
        "hardware_ab",
        "reference_station",
        "local_neighborhood",
    ]
    for lang in ["en", "de"]:
        labels = T[lang]
        assert _benchmark_mode_options(labels) == [
            labels["opt_comp_none"],
            labels["opt_comp_self"],
            labels["opt_comp_buddy"],
            labels["opt_comp_radius"],
        ]


def test_missing_benchmark_design_defaults_to_success_only(monkeypatch):
    session_state = _SessionState()
    monkeypatch.setattr(
        state_manager,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    state_manager.init_session_state()

    assert session_state.val_comp_mode == T["en"]["opt_comp_none"]
    assert _default_config()["benchmark_mode"] == COMPARISON_NONE
    assert _default_config()["band"] == DEFAULT_BAND
    analysis_context = build_analysis_context_from_session_state({})
    assert analysis_context.comparison_mode == COMPARISON_NONE
    assert analysis_context.band == DEFAULT_BAND


def test_reset_config_returns_to_success_only(monkeypatch):
    session_state = _SessionState(
        {
            "lang": "en",
            "val_comp_mode": T["en"]["opt_comp_radius"],
        }
    )
    monkeypatch.setattr(
        callbacks,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    callbacks.set_reset_config()

    assert session_state.val_comp_mode == T["en"]["opt_comp_none"]
    assert session_state.val_band == DEFAULT_BAND


@pytest.mark.parametrize(
    "benchmark_mode",
    [
        T["en"]["opt_comp_self"],
        T["en"]["opt_comp_buddy"],
        T["en"]["opt_comp_radius"],
    ],
)
def test_each_benchmark_design_starts_with_zero_snr_correction(monkeypatch, benchmark_mode):
    session_state = _SessionState(
        {
            "val_comp_mode": benchmark_mode,
            "val_benchmark_offset_db": -99.9,
        }
    )
    monkeypatch.setattr(
        callbacks,
        "st",
        SimpleNamespace(session_state=session_state),
    )
    monkeypatch.setattr(callbacks, "reset_audit", lambda: None)
    monkeypatch.setattr(callbacks, "apply_demo_profile", lambda: None)

    callbacks.handle_comp_mode_change()

    assert session_state.val_benchmark_offset_db == 0.0


def test_removed_all_band_session_state_returns_to_exact_default(monkeypatch):
    session_state = _SessionState({"val_band": "All"})
    monkeypatch.setattr(
        state_manager,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    state_manager.init_session_state()

    assert session_state.val_band == DEFAULT_BAND
