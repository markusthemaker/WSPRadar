from types import SimpleNamespace

from core.analysis_context import COMPARISON_HARDWARE_AB
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


def test_benchmark_mode_options_are_ordered_by_evidence_strength():
    assert list(MODE_KEYS) == [
        "hardware_ab",
        "reference_station",
        "local_neighborhood",
    ]
    for lang in ["en", "de"]:
        labels = T[lang]
        assert _benchmark_mode_options(labels) == [
            labels["opt_comp_self"],
            labels["opt_comp_buddy"],
            labels["opt_comp_radius"],
        ]


def test_missing_benchmark_mode_defaults_to_hardware_ab(monkeypatch):
    session_state = _SessionState()
    monkeypatch.setattr(
        state_manager,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    state_manager.init_session_state()

    assert session_state.val_comp_mode == T["en"]["opt_comp_self"]
    assert _default_config()["benchmark_mode"] == COMPARISON_HARDWARE_AB
    analysis_context = build_analysis_context_from_session_state({})
    assert analysis_context.comparison_mode == COMPARISON_HARDWARE_AB


def test_reset_config_returns_to_hardware_ab(monkeypatch):
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

    assert session_state.val_comp_mode == T["en"]["opt_comp_self"]
