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


class _NullContext:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


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


@pytest.mark.parametrize("language", ["en", "de"])
def test_callsign_entry_guidance_recommends_standard_forms_in_both_languages(
    language,
):
    """Explain both accepted suffix forms without presenting aliases as equivalent."""
    labels = T[language]

    assert "DL1MKS/P" in labels["hlp_callsign_entry"]
    assert "DL1MKS-1" in labels["hlp_callsign_entry"]
    assert "standard" in labels["hlp_callsign_entry"].lower()
    assert "distinct" in labels["hlp_callsign_entry"].lower() or "eigene" in labels[
        "hlp_callsign_entry"
    ].lower()
    assert "DL1MKS/P" in labels["ph_reference_callsign"]
    assert "DL1MKS-1" in labels["ph_reference_callsign"]


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


@pytest.mark.parametrize("language", ["en", "de"])
def test_tx_ab_method_selector_uses_canonical_required_segments(
    monkeypatch,
    language,
):
    """Keep method state language-independent while localizing both choices."""
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
    config_panel._render_tx_ab_method_selector(labels)

    positional_args, keyword_args = segmented_control.call_args
    assert positional_args == (
        labels["lbl_tx_ab_method"],
        ("simultaneous", "sequential"),
    )
    assert keyword_args["selection_mode"] == "single"
    assert keyword_args["required"] is True
    assert keyword_args["key"] == "val_tx_ab_method"
    assert keyword_args["format_func"]("simultaneous") == labels[
        "opt_tx_ab_simultaneous"
    ]
    assert keyword_args["format_func"]("sequential") == labels[
        "opt_tx_ab_sequential"
    ]


def test_hardware_identity_renders_derived_grid4_without_mutating_buddy_qth(
    monkeypatch,
):
    """Show one shared Hardware grid-4 without owning independent QTH state."""
    text_input = Mock()
    error = Mock()
    columns = Mock(
        side_effect=[
            (_NullContext(), _NullContext()),
            (_NullContext(), _NullContext()),
        ]
    )
    session_state = _SessionState(
        {
            "val_callsign": "dl1mks",
            "val_qth": "jn37aa",
            "val_ref_callsign": "dl1mks-1",
            "val_ref_qth": "jo62",
            "is_demo_mode": False,
        }
    )
    monkeypatch.setattr(
        config_panel,
        "st",
        SimpleNamespace(
            session_state=session_state,
            columns=columns,
            error=error,
        ),
    )
    monkeypatch.setattr(config_panel, "text_input_no_autocomplete", text_input)

    config_panel._render_reference_identity(
        T["en"],
        derives_hardware_grid4=True,
    )

    assert [call.args[0] for call in text_input.call_args_list] == [
        "Target Callsign",
        "Reference Callsign",
        "Target Grid-4",
        "Reference Grid-4",
    ]
    assert text_input.call_args_list[0].kwargs == {
        "value": "DL1MKS",
        "disabled": True,
    }
    assert text_input.call_args_list[1].kwargs["key"] == "val_ref_callsign"
    assert text_input.call_args_list[1].kwargs["help"] == T["en"][
        "hlp_callsign_entry"
    ]
    assert text_input.call_args_list[1].kwargs["placeholder"] == T["en"][
        "ph_reference_callsign"
    ]
    assert text_input.call_args_list[2].kwargs == {
        "value": "JN37",
        "disabled": True,
    }
    assert text_input.call_args_list[3].kwargs == {
        "value": "JN37",
        "disabled": True,
    }
    assert session_state.val_ref_qth == "jo62"
    error.assert_not_called()


def test_target_callsign_widget_uses_shared_entry_guidance(monkeypatch):
    """Attach the same exact-identity guidance to the editable Target field."""
    text_input = Mock()
    session_state = _SessionState(
        {
            "config_panels_expanded": True,
            "val_analysis_direction": "rx",
            "val_callsign": "DL1MKS-1",
            "val_qth": "JN37",
            "val_time_mode": T["en"]["opt_last_x"],
            "is_demo_mode": False,
        }
    )
    monkeypatch.setattr(
        config_panel,
        "st",
        SimpleNamespace(
            session_state=session_state,
            expander=Mock(return_value=_NullContext()),
            columns=Mock(return_value=(_NullContext(), _NullContext())),
            error=Mock(),
            selectbox=Mock(),
            radio=Mock(),
            slider=Mock(),
        ),
    )
    monkeypatch.setattr(config_panel, "_render_analysis_direction_selector", Mock())
    monkeypatch.setattr(config_panel, "text_input_no_autocomplete", text_input)

    config_panel.render_core_expander(T["en"])

    target_callsign_input = next(
        call
        for call in text_input.call_args_list
        if call.kwargs.get("key") == "val_callsign"
    )
    assert target_callsign_input.kwargs["help"] == T["en"]["hlp_callsign_entry"]


def test_reference_station_identity_keeps_reference_grid4_editable(monkeypatch):
    """Keep Buddy QTH independent while retaining the shared identity layout."""
    text_input = Mock()
    error = Mock()
    columns = Mock(
        side_effect=[
            (_NullContext(), _NullContext()),
            (_NullContext(), _NullContext()),
        ]
    )
    session_state = _SessionState(
        {
            "val_callsign": "DL1MKS",
            "val_qth": "JN37AA",
            "val_ref_callsign": "DL2XYZ",
            "val_ref_qth": "JO62",
            "is_demo_mode": False,
        }
    )
    monkeypatch.setattr(
        config_panel,
        "st",
        SimpleNamespace(
            session_state=session_state,
            columns=columns,
            error=error,
        ),
    )
    monkeypatch.setattr(config_panel, "text_input_no_autocomplete", text_input)

    config_panel._render_reference_identity(
        T["en"],
        derives_hardware_grid4=False,
    )

    assert text_input.call_args_list[2].kwargs == {
        "value": "JN37AA",
        "disabled": True,
    }
    reference_qth_parameters = text_input.call_args_list[3].kwargs
    assert reference_qth_parameters["key"] == "val_ref_qth"
    assert reference_qth_parameters["max_chars"] == 4
    assert reference_qth_parameters["disabled"] is False
    assert session_state.val_ref_qth == "JO62"
    error.assert_not_called()


def test_reference_station_identity_reports_invalid_reference_fields(monkeypatch):
    """Give field-specific feedback before malformed identities reach a run."""
    text_input = Mock()
    error = Mock()
    columns = Mock(
        side_effect=[
            (_NullContext(), _NullContext()),
            (_NullContext(), _NullContext()),
        ]
    )
    session_state = _SessionState(
        {
            "val_callsign": "DL1MKS",
            "val_qth": "JN37AA",
            "val_ref_callsign": "ABC",
            "val_ref_qth": "JO62AA",
            "is_demo_mode": False,
        }
    )
    monkeypatch.setattr(
        config_panel,
        "st",
        SimpleNamespace(
            session_state=session_state,
            columns=columns,
            error=error,
        ),
    )
    monkeypatch.setattr(config_panel, "text_input_no_autocomplete", text_input)

    config_panel._render_reference_identity(
        T["en"],
        derives_hardware_grid4=False,
    )

    assert [call.args[0] for call in error.call_args_list] == [
        T["en"]["err_reference_callsign_format"],
        T["en"]["err_reference_grid4_format"],
    ]


@pytest.mark.parametrize("identity", ["DL1\u00df", "D\u01311ABC", "J\u212a37"])
def test_identity_normalization_does_not_expand_unicode_into_ascii(
    monkeypatch,
    identity,
):
    """Preserve non-ASCII input so validation can reject it visibly."""
    session_state = _SessionState({"identity": f" {identity} "})
    monkeypatch.setattr(
        config_panel,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    config_panel._normalize_text_state("identity", should_uppercase=True)

    assert session_state.identity == identity


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
    assert session_state.val_ref_callsign == ""
    assert session_state.val_ref_qth == ""
    assert session_state.val_tx_ab_method == "simultaneous"
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
    assert analysis_context.tx_ab_method == "simultaneous"
    assert analysis_context.reference_qth == ""


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
    assert session_state.val_ref_qth == ""
    assert session_state.val_tx_ab_method == "simultaneous"
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


def test_analysis_context_derives_hardware_reference_grid4_from_target_qth():
    """Do not carry the inactive Buddy QTH into a Hardware request."""
    analysis_context = build_analysis_context_from_session_state(
        {
            "lang": "en",
            "val_analysis_direction": "tx",
            "val_comp_mode": T["en"]["opt_comp_self"],
            "val_qth": "jn37aa",
            "val_ref_qth": "JO62",
        }
    )

    assert analysis_context.qth == "JN37AA"
    assert analysis_context.reference_qth == "JN37"


def test_analysis_context_preserves_reference_station_grid4():
    """Keep the independently authored Buddy grid in Reference Station mode."""
    analysis_context = build_analysis_context_from_session_state(
        {
            "lang": "en",
            "val_analysis_direction": "tx",
            "val_comp_mode": T["en"]["opt_comp_buddy"],
            "val_qth": "JN37AA",
            "val_ref_qth": "jo62",
        }
    )

    assert analysis_context.reference_qth == "JO62"


def test_direction_change_resets_active_hardware_design(monkeypatch):
    """Prevent direction-specific Hardware A/B fields from being reinterpreted."""
    session_state = _SessionState(
        {
            "lang": "en",
            "val_analysis_direction": "tx",
            "val_comp_mode": T["en"]["opt_comp_self"],
            "val_benchmark_offset_db": 1.5,
            "val_ref_callsign": "DL1MKS/P",
            "val_ref_qth": "JN37",
            "val_tx_ab_method": "sequential",
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
    assert session_state.val_ref_callsign == "DL1MKS/P"
    assert session_state.val_ref_qth == "JN37"
    assert session_state.val_tx_ab_method == "simultaneous"
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
    for comparison_mode in _benchmark_mode_options(T["en"]):
        for analysis_direction in (None, "rx", "tx"):
            assert _comparison_column_widths(
                T["en"],
                comparison_mode,
                analysis_direction,
            ) == [0.5, 0.5]


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


def test_hardware_design_does_not_overwrite_retained_buddy_qth(monkeypatch):
    """Hardware derives its grid from Target without changing Buddy state."""
    session_state = _SessionState(
        {
            "lang": "en",
            "val_comp_mode": T["en"]["opt_comp_self"],
            "val_benchmark_offset_db": -1.0,
            "val_qth": "jn37aa",
            "val_ref_qth": "JO62",
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
    assert session_state.val_ref_qth == "JO62"


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
    """Load an active demo entirely from its embedded versioned config document."""
    session_state = _SessionState({"lang": "en", "val_max_dist": 22000})
    monkeypatch.setattr(
        callbacks,
        "st",
        SimpleNamespace(session_state=session_state),
    )

    callbacks._apply_demo_profile_values("milazzo_tx_buddy")

    assert session_state.val_callsign == "KP4MD"
    assert session_state.val_qth == "CM98"
    assert session_state.val_band == "40m"
    assert session_state.val_ref_callsign == "WB6RQN"
    assert session_state.val_analysis_direction == "tx"
    assert session_state.val_comp_mode == T["en"]["opt_comp_buddy"]
    assert session_state.val_max_dist == 5000
    assert session_state.val_min_opportunities == 5
    assert session_state.val_results_show_non_joint is False
    assert session_state.val_results_show_zero_target is False
    assert session_state.val_results_selected_ranges_compare == "all"
    assert session_state.val_results_selected_directions_compare == "all"
    assert session_state.val_results_selected_ranges_absolute == "all"
    assert session_state.val_results_selected_directions_absolute == "all"
    assert session_state.val_results_time_bin_compare == "3h"
    assert session_state.val_results_time_bin_absolute == "3h"
