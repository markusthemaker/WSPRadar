import ast
import inspect
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from i18n import GUIDED_INPUTS, T
from ui.components import config_panel
from ui.guided_inputs import renderer as guided_renderer


class _SessionState(dict):
    """Provide Streamlit-style attribute access over isolated test state."""

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def __setattr__(self, key, value):
        self[key] = value


class _NullContext:
    """Stand in for Streamlit containers without changing control flow."""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


SUCCESS_HELP_KEYS = {
    "hlp_min_opportunities_rx",
    "hlp_min_opportunities_tx",
    "hlp_min_stations_compare",
    "hlp_min_stations_success_rx",
    "hlp_min_stations_success_tx",
}

LEGACY_ACTIVE_SUCCESS_INPUT_PHRASES = (
    "heard elsewhere",
    "anderswo gehört",
    "Elsewhere",
    "Other Signals",
    "Target+counter-evidence",
    "Target+Gegen-Evidenz",
    "H+M",
    "Absolute success-rate",
    "Absolute Erfolgsrate",
)


def _success_session_state(direction):
    """Return valid in-range Success thresholds for one analysis direction."""
    return _SessionState(
        {
            "val_comp_mode": "none",
            "val_analysis_direction": direction,
            "val_tx_ab_method": "simultaneous",
            "val_min_spots": 7,
            "val_min_opportunities": 11,
            "val_min_stations": 3,
        }
    )


@pytest.mark.parametrize(
    ("language", "use_case", "expected_outcomes"),
    [
        (
            "en",
            "rx_performance",
            ("Heard by Target", "Heard by others only"),
        ),
        (
            "en",
            "tx_performance",
            ("Target heard", "Other signals heard only"),
        ),
        (
            "de",
            "rx_performance",
            ("Vom Target gehört", "Nur von anderen gehört"),
        ),
        (
            "de",
            "tx_performance",
            ("Target gehört", "Nur andere Signale gehört"),
        ),
    ],
)
def test_guided_performance_descriptions_name_the_displayed_outcomes(
    language,
    use_case,
    expected_outcomes,
):
    """Keep all four Guided Performance captions aligned with result vocabulary."""
    description = GUIDED_INPUTS[language]["options"]["use_cases"][use_case][
        "description"
    ]

    for outcome in expected_outcomes:
        assert outcome in description
    for legacy_phrase in LEGACY_ACTIVE_SUCCESS_INPUT_PHRASES:
        assert legacy_phrase not in description


def test_active_success_input_explanations_exclude_legacy_outcome_vocabulary():
    """Reject old category names from every active Guided or shared help path."""
    for language in ("en", "de"):
        active_text = "\n".join(
            [
                GUIDED_INPUTS[language]["options"]["use_cases"]["rx_performance"][
                    "description"
                ],
                GUIDED_INPUTS[language]["options"]["use_cases"]["tx_performance"][
                    "description"
                ],
                *(T[language][key] for key in sorted(SUCCESS_HELP_KEYS)),
            ]
        )

        for legacy_phrase in LEGACY_ACTIVE_SUCCESS_INPUT_PHRASES:
            assert legacy_phrase not in active_text


@pytest.mark.parametrize(
    (
        "language",
        "direction",
        "minimum_opportunities_help_key",
        "minimum_stations_help_key",
    ),
    [
        (
            "en",
            "rx",
            "hlp_min_opportunities_rx",
            "hlp_min_stations_success_rx",
        ),
        (
            "en",
            "tx",
            "hlp_min_opportunities_tx",
            "hlp_min_stations_success_tx",
        ),
        (
            "de",
            "rx",
            "hlp_min_opportunities_rx",
            "hlp_min_stations_success_rx",
        ),
        (
            "de",
            "tx",
            "hlp_min_opportunities_tx",
            "hlp_min_stations_success_tx",
        ),
    ],
)
def test_classic_success_thresholds_resolve_direction_specific_help(
    monkeypatch,
    language,
    direction,
    minimum_opportunities_help_key,
    minimum_stations_help_key,
):
    """Route Classic RX/TX help without changing canonical threshold state."""
    sliders = Mock()
    session_state = _success_session_state(direction)
    threshold_values_before = {
        key: session_state[key]
        for key in (
            "val_min_spots",
            "val_min_opportunities",
            "val_min_stations",
        )
    }
    monkeypatch.setattr(
        config_panel,
        "st",
        SimpleNamespace(session_state=session_state, slider=sliders),
    )

    config_panel.render_evidence_threshold_fields(T[language])

    opportunity_call, station_call = sliders.call_args_list
    assert opportunity_call.args == (T[language]["lbl_min_opportunities"], 1, 100)
    assert opportunity_call.kwargs["key"] == "val_min_opportunities"
    assert opportunity_call.kwargs["help"] == T[language][
        minimum_opportunities_help_key
    ]
    assert station_call.args == (T[language]["lbl_min_stations"], 1, 10)
    assert station_call.kwargs["key"] == "val_min_stations"
    assert station_call.kwargs["help"] == T[language][minimum_stations_help_key]
    assert {
        key: session_state[key] for key in threshold_values_before
    } == threshold_values_before


@pytest.mark.parametrize("language", ["en", "de"])
def test_classic_benchmark_uses_separate_map_segment_help(monkeypatch, language):
    """Keep Benchmark station help separate from both Performance directions."""
    sliders = Mock()
    session_state = _SessionState(
        {
            "val_comp_mode": "reference_station",
            "val_analysis_direction": "rx",
            "val_tx_ab_method": "simultaneous",
            "val_min_spots": 7,
            "val_min_opportunities": 11,
            "val_min_stations": 3,
        }
    )
    monkeypatch.setattr(
        config_panel,
        "st",
        SimpleNamespace(session_state=session_state, slider=sliders),
    )

    config_panel.render_evidence_threshold_fields(T[language])

    joint_evidence_call, station_call = sliders.call_args_list
    assert joint_evidence_call.kwargs["help"] == T[language]["hlp_min_spots"]
    assert station_call.kwargs["help"] == T[language]["hlp_min_stations_compare"]


@pytest.mark.parametrize("language", ["en", "de"])
def test_sequential_tx_benchmark_preserves_scheduled_pair_help(monkeypatch, language):
    """Retain scheduled-pair help while routing Benchmark station help."""
    sliders = Mock()
    session_state = _SessionState(
        {
            "val_comp_mode": "hardware_ab",
            "val_analysis_direction": "tx",
            "val_tx_ab_method": "sequential",
            "val_min_spots": 7,
            "val_min_opportunities": 11,
            "val_min_stations": 3,
        }
    )
    monkeypatch.setattr(
        config_panel,
        "st",
        SimpleNamespace(session_state=session_state, slider=sliders),
    )

    config_panel.render_evidence_threshold_fields(T[language])

    scheduled_pair_call, station_call = sliders.call_args_list
    assert scheduled_pair_call.args[0] == T[language]["cfg_min_joint_pairs"]
    assert scheduled_pair_call.kwargs["help"] == T[language]["hlp_min_joint_pairs"]
    assert station_call.kwargs["help"] == T[language]["hlp_min_stations_compare"]


def test_success_opportunity_label_is_a_required_catalog_contract(monkeypatch):
    """Reject an incomplete catalog instead of rendering an English fallback."""
    labels_without_optional_label = dict(T["en"])
    labels_without_optional_label.pop("lbl_min_opportunities")
    sliders = Mock()
    monkeypatch.setattr(
        config_panel,
        "st",
        SimpleNamespace(
            session_state=_success_session_state("rx"),
            slider=sliders,
        ),
    )

    with pytest.raises(KeyError, match="lbl_min_opportunities"):
        config_panel.render_evidence_threshold_fields(
            labels_without_optional_label
        )

    sliders.assert_not_called()


@pytest.mark.parametrize(
    ("language", "direction", "opportunities_help_key", "stations_help_key"),
    [
        (
            "en",
            "rx",
            "hlp_min_opportunities_rx",
            "hlp_min_stations_success_rx",
        ),
        (
            "en",
            "tx",
            "hlp_min_opportunities_tx",
            "hlp_min_stations_success_tx",
        ),
        (
            "de",
            "rx",
            "hlp_min_opportunities_rx",
            "hlp_min_stations_success_rx",
        ),
        (
            "de",
            "tx",
            "hlp_min_opportunities_tx",
            "hlp_min_stations_success_tx",
        ),
    ],
)
def test_guided_custom_scope_uses_the_shared_direction_specific_success_help(
    monkeypatch,
    language,
    direction,
    opportunities_help_key,
    stations_help_key,
):
    """Exercise the shared renderer through Guided Review and customize."""
    sliders = Mock()
    session_state = _success_session_state(direction)
    session_state.update(
        {
            "guided_loaded_demo_profile": None,
            "guided_scope_mode": "custom",
        }
    )
    monkeypatch.setattr(
        guided_renderer,
        "st",
        SimpleNamespace(
            session_state=session_state,
            radio=Mock(),
            markdown=Mock(),
            caption=Mock(),
        ),
    )
    monkeypatch.setattr(
        config_panel,
        "st",
        SimpleNamespace(
            session_state=session_state,
            columns=Mock(return_value=(_NullContext(), _NullContext())),
            slider=sliders,
        ),
    )
    monkeypatch.setattr(
        guided_renderer,
        "render_station_population_fields",
        Mock(),
    )
    monkeypatch.setattr(guided_renderer, "render_scope_fields", Mock())
    monkeypatch.setattr(
        guided_renderer,
        "render_evidence_threshold_fields",
        config_panel.render_evidence_threshold_fields,
    )

    guided_renderer._render_scope_and_evidence_fields(
        T[language],
        GUIDED_INPUTS[language],
    )

    opportunity_call, station_call = sliders.call_args_list
    assert opportunity_call.kwargs["help"] == T[language][opportunities_help_key]
    assert station_call.kwargs["help"] == T[language][stations_help_key]


def test_success_input_help_keys_preserve_complete_bilingual_structure():
    """Require every new shared help key in aligned English and German catalogs."""
    assert set(T["en"]) == set(T["de"])
    assert SUCCESS_HELP_KEYS <= set(T["en"])
    assert SUCCESS_HELP_KEYS <= set(T["de"])
    assert {"hlp_min_opportunities", "hlp_min_stations"}.isdisjoint(T["en"])
    assert {"hlp_min_opportunities", "hlp_min_stations"}.isdisjoint(T["de"])
    for key in SUCCESS_HELP_KEYS:
        assert T["en"][key].strip()
        assert T["de"][key].strip()


def test_shared_config_panel_requires_bilingual_catalog_strings_without_fallbacks():
    """Keep Guided/Classic shared widgets free of displayable literal fallbacks."""
    syntax_tree = ast.parse(inspect.getsource(config_panel))
    translation_get_calls = [
        node.lineno
        for node in ast.walk(syntax_tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "t"
        and node.func.attr == "get"
    ]
    literal_translation_keys = {
        node.slice.value
        for node in ast.walk(syntax_tree)
        if isinstance(node, ast.Subscript)
        and isinstance(node.value, ast.Name)
        and node.value.id == "t"
        and isinstance(node.slice, ast.Constant)
        and isinstance(node.slice.value, str)
    }
    literal_translation_keys.update(
        {
            "lbl_callsign_rx",
            "lbl_callsign_tx",
            "opt_tx_ab_simultaneous",
            "opt_tx_ab_sequential",
        }
    )

    assert translation_get_calls == []
    assert {
        language: sorted(literal_translation_keys - set(T[language]))
        for language in ("en", "de")
    } == {"en": [], "de": []}
