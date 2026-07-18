from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from config import DEFAULT_BAND
from core.analysis_context import COMPARISON_NONE
from i18n import T
from ui import callbacks, state_manager
from ui.analysis_context_adapter import build_analysis_context_from_session_state
from ui.components import config_panel
from ui.components.config_panel import (
    _benchmark_mode_options,
    _comparison_column_widths,
    _tx_ab_threshold_label_and_help,
    _tx_ab_schedule_preview,
)
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


@pytest.mark.parametrize("language", ["en", "de"])
def test_tx_ab_threshold_wording_describes_scheduled_pairs(language):
    """Do not describe scheduled pairs as joint spots."""
    labels = T[language]

    assert _tx_ab_threshold_label_and_help(labels) == (
        labels["cfg_min_joint_pairs"],
        labels["hlp_min_joint_pairs"],
    )


@pytest.mark.parametrize(
    ("language", "expected_rx_label", "expected_tx_label"),
    [
        ("en", "RX Analysis", "TX Analysis"),
        ("de", "RX-Analyse", "TX-Analyse"),
    ],
)
def test_analysis_selector_uses_full_width_segments_without_visible_heading(
    monkeypatch,
    language,
    expected_rx_label,
    expected_tx_label,
):
    """Keep the governing direction choice visually balanced and concise."""
    segmented_control = Mock(return_value=None)
    monkeypatch.setattr(
        config_panel,
        "st",
        SimpleNamespace(
            session_state=SimpleNamespace(is_demo_mode=False),
            segmented_control=segmented_control,
        ),
    )

    labels = T[language]
    config_panel._render_analysis_direction_selector(labels)

    positional_args, keyword_args = segmented_control.call_args
    assert positional_args == (labels["lbl_analysis_selector"], ("rx", "tx"))
    assert keyword_args["selection_mode"] == "single"
    assert keyword_args["required"] is True
    assert keyword_args["key"] == "val_analysis_direction"
    assert keyword_args["label_visibility"] == "collapsed"
    assert keyword_args["width"] == "stretch"
    assert keyword_args["format_func"]("rx") == expected_rx_label
    assert keyword_args["format_func"]("tx") == expected_tx_label


def test_missing_benchmark_design_defaults_to_success_only(monkeypatch):
    session_state = _SessionState()
    monkeypatch.setattr(
        state_manager,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    state_manager.init_session_state()

    assert session_state.val_analysis_direction is None
    assert session_state.val_comp_mode == T["en"]["opt_comp_none"]
    assert session_state.val_results_show_zero_target is False
    assert session_state.val_results_selected_ranges_compare == "all"
    assert session_state.val_results_selected_directions_compare == "all"
    assert session_state.val_results_selected_ranges_absolute == "all"
    assert session_state.val_results_selected_directions_absolute == "all"
    assert _default_config()["benchmark_mode"] == COMPARISON_NONE
    assert _default_config()["band"] == DEFAULT_BAND
    analysis_context = build_analysis_context_from_session_state({})
    assert analysis_context.comparison_mode == COMPARISON_NONE
    assert analysis_context.band == DEFAULT_BAND
    assert analysis_context.tx_ab_repeat_interval_minutes == 10
    assert analysis_context.tx_ab_target_start_minute == 0
    assert analysis_context.tx_ab_reference_start_minute == 2


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
    assert session_state.val_analysis_direction is None
    assert session_state.val_results_show_non_joint is None
    assert session_state.val_results_show_zero_target is False
    assert session_state.val_results_selected_ranges_compare == "all"
    assert session_state.val_results_selected_directions_compare == "all"
    assert session_state.val_results_selected_ranges_absolute == "all"
    assert session_state.val_results_selected_directions_absolute == "all"
    assert session_state.val_results_time_bin_compare is None
    assert session_state.val_results_time_bin_absolute is None


@pytest.mark.parametrize(
    ("analysis_direction", "expected_self_test_mode"),
    [("rx", "rx"), ("tx", "tx")],
)
def test_analysis_context_derives_hardware_direction_from_analysis_direction(
    analysis_direction,
    expected_self_test_mode,
):
    """Do not retain a second RX/TX discriminator for Hardware A/B."""
    analysis_context = build_analysis_context_from_session_state(
        {
            "val_analysis_direction": analysis_direction,
            "run_mode": analysis_direction.upper(),
        }
    )

    assert analysis_context.run_mode == analysis_direction.upper()
    assert analysis_context.self_test_mode == expected_self_test_mode


def test_direction_change_resets_active_hardware_design(monkeypatch):
    """Prevent direction-specific Hardware A/B fields from being reinterpreted."""
    session_state = _SessionState(
        {
            "lang": "en",
            "val_analysis_direction": "tx",
            "val_comp_mode": T["en"]["opt_comp_self"],
            "val_benchmark_offset_db": 1.5,
            "val_self_call_b": "DL1MKS/P",
            "val_tx_ab_repeat_interval_minutes": 4,
            "val_tx_ab_target_start_minute": 2,
            "val_tx_ab_reference_start_minute": 0,
        }
    )
    monkeypatch.setattr(
        callbacks,
        "st",
        SimpleNamespace(session_state=session_state),
    )
    monkeypatch.setattr(callbacks, "reset_audit", lambda: None)

    callbacks.handle_analysis_direction_change()

    assert session_state.val_comp_mode == T["en"]["opt_comp_none"]
    assert session_state.val_benchmark_offset_db == 0.0
    assert session_state.val_self_call_b == ""
    assert session_state.val_tx_ab_repeat_interval_minutes == 10
    assert session_state.val_tx_ab_target_start_minute == 0
    assert session_state.val_tx_ab_reference_start_minute == 2


def test_schedule_callbacks_keep_starts_disjoint(monkeypatch):
    session_state = _SessionState(
        {
            "val_tx_ab_repeat_interval_minutes": 10,
            "val_tx_ab_target_start_minute": 8,
            "val_tx_ab_reference_start_minute": 8,
        }
    )
    monkeypatch.setattr(
        callbacks,
        "st",
        SimpleNamespace(session_state=session_state),
    )
    monkeypatch.setattr(callbacks, "reset_audit", lambda: None)

    callbacks.handle_tx_ab_target_start_change()

    assert session_state.val_tx_ab_target_start_minute == 8
    assert session_state.val_tx_ab_reference_start_minute == 0


def test_schedule_preview_and_comparison_widths_match_the_tx_ab_ui():
    target, reference, separation = _tx_ab_schedule_preview(10, 0, 2)

    assert target == (0, 10, 20, 30, 40, 50)
    assert reference == (2, 12, 22, 32, 42, 52)
    assert separation == 2
    assert _comparison_column_widths(
        T["en"],
        T["en"]["opt_comp_self"],
        "tx",
    ) == [0.32, 0.68]


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


def test_json_demo_configuration_applies_complete_deterministic_state(monkeypatch):
    """Load Experiment B entirely from its embedded versioned config document."""
    session_state = _SessionState({"lang": "en", "val_max_dist": 22000})
    monkeypatch.setattr(
        callbacks,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    callbacks._apply_demo_profile_values("zander_tx_buddy_experiment_b")

    assert session_state.val_callsign == "SK0WE/B"
    assert session_state.val_qth == "JO89"
    assert session_state.val_band == "40m"
    assert session_state.val_ref_callsign == "SK0WE"
    assert session_state.val_analysis_direction == "tx"
    assert session_state.val_comp_mode == T["en"]["opt_comp_buddy"]
    assert session_state.val_max_dist == 2500
    assert session_state.val_min_opportunities == 1
    assert session_state.val_results_show_non_joint is False
    assert session_state.val_results_show_zero_target is False
    assert session_state.val_results_selected_ranges_compare == "all"
    assert session_state.val_results_selected_directions_compare == "all"
    assert session_state.val_results_selected_ranges_absolute == "all"
    assert session_state.val_results_selected_directions_absolute == "all"
    assert session_state.val_results_time_bin_compare == "5m"
    assert session_state.val_results_time_bin_absolute == "5m"
