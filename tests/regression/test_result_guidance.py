"""Focused regression contracts for result interpretation popovers."""

import ast
from collections import Counter
from pathlib import Path
from string import Formatter

import pytest
from streamlit.testing.v1 import AppTest

from core.analysis_context import (
    AnalysisContext,
    COMPARISON_HARDWARE_AB,
    COMPARISON_LOCAL_NEIGHBORHOOD,
    COMPARISON_NONE,
    COMPARISON_REFERENCE_STATION,
    LOCAL_BENCHMARK_BEST,
    LOCAL_BENCHMARK_MEDIAN,
)
from i18n import RESULT_GUIDANCE, T
from ui.result_guidance import (
    RESULT_GUIDANCE_COMPARISON_EVIDENCE,
    RESULT_GUIDANCE_CONTEXT,
    RESULT_GUIDANCE_DOWNLOAD,
    RESULT_GUIDANCE_DRILLDOWN,
    RESULT_GUIDANCE_MAP,
    RESULT_GUIDANCE_SEGMENT,
    RESULT_GUIDANCE_SELECTED_STATIONS,
    RESULT_GUIDANCE_STATION_INSIGHTS,
    RESULT_GUIDANCE_SUCCESS_EVIDENCE,
    RESULT_GUIDANCE_TEMPORAL_EVIDENCE,
    build_result_guidance,
)


COMPARE_SECTIONS = (
    RESULT_GUIDANCE_CONTEXT,
    RESULT_GUIDANCE_MAP,
    RESULT_GUIDANCE_SEGMENT,
    RESULT_GUIDANCE_COMPARISON_EVIDENCE,
    RESULT_GUIDANCE_TEMPORAL_EVIDENCE,
    RESULT_GUIDANCE_STATION_INSIGHTS,
    RESULT_GUIDANCE_SELECTED_STATIONS,
    RESULT_GUIDANCE_DRILLDOWN,
    RESULT_GUIDANCE_DOWNLOAD,
)

SUCCESS_SECTIONS = (
    RESULT_GUIDANCE_CONTEXT,
    RESULT_GUIDANCE_MAP,
    RESULT_GUIDANCE_SEGMENT,
    RESULT_GUIDANCE_SUCCESS_EVIDENCE,
    RESULT_GUIDANCE_STATION_INSIGHTS,
    RESULT_GUIDANCE_SELECTED_STATIONS,
    RESULT_GUIDANCE_DRILLDOWN,
    RESULT_GUIDANCE_DOWNLOAD,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def _flatten_catalog(catalog, prefix=()):
    """Return every nested catalog leaf keyed by its complete semantic path."""
    leaves = {}
    for key, value in catalog.items():
        path = (*prefix, key)
        if isinstance(value, dict):
            leaves.update(_flatten_catalog(value, path))
        else:
            leaves[path] = value
    return leaves


def _format_fields(template):
    """Return all named replacement fields used by one localized template."""
    return {
        field_name
        for _literal, field_name, _format_spec, _conversion in Formatter().parse(
            template
        )
        if field_name
    }


def _build_guidance(
    section_id,
    *,
    language="en",
    analysis_id="RX_COMP",
    is_compare=True,
    is_sequential=False,
    analysis_context=None,
):
    """Build guidance with the matching localized general translation catalog."""
    return build_result_guidance(
        section_id,
        language=language,
        translations=T[language],
        analysis_id=analysis_id,
        is_compare=is_compare,
        is_sequential=is_sequential,
        analysis_context=analysis_context,
    )


def test_result_guidance_catalog_has_recursive_bilingual_placeholder_parity():
    """Keep every nested English and German guidance leaf interchangeable."""
    assert set(RESULT_GUIDANCE) == {"en", "de"}
    english_leaves = _flatten_catalog(RESULT_GUIDANCE["en"])
    german_leaves = _flatten_catalog(RESULT_GUIDANCE["de"])

    assert english_leaves.keys() == german_leaves.keys()
    for path in sorted(english_leaves):
        english_value = english_leaves[path]
        german_value = german_leaves[path]
        assert isinstance(english_value, str), path
        assert isinstance(german_value, str), path
        assert english_value.strip(), path
        assert german_value.strip(), path
        assert _format_fields(english_value) == _format_fields(
            german_value
        ), path
        assert _format_fields(english_value) <= {
            "counter",
            "formula",
            "peer_type",
            "radius",
            "section",
        }, path

    for language in ("en", "de"):
        assert RESULT_GUIDANCE[language]["sections"]
        for section_key, section_content in RESULT_GUIDANCE[language][
            "sections"
        ].items():
            assert set(section_content) == {"read", "limits"}, (
                language,
                section_key,
            )


@pytest.mark.parametrize("language", ("en", "de"))
@pytest.mark.parametrize(
    (
        "analysis_id",
        "is_compare",
        "is_sequential",
        "analysis_context",
        "section_ids",
    ),
    (
        (
            "RX_COMP",
            True,
            False,
            AnalysisContext(comparison_mode=COMPARISON_REFERENCE_STATION),
            COMPARE_SECTIONS,
        ),
        (
            "TX_COMP",
            True,
            False,
            AnalysisContext(comparison_mode=COMPARISON_HARDWARE_AB),
            COMPARE_SECTIONS,
        ),
        (
            "TX_COMP",
            True,
            True,
            AnalysisContext(comparison_mode=COMPARISON_HARDWARE_AB),
            COMPARE_SECTIONS,
        ),
        (
            "RX_ABS",
            False,
            False,
            AnalysisContext(comparison_mode=COMPARISON_NONE),
            SUCCESS_SECTIONS,
        ),
        (
            "TX_ABS",
            False,
            False,
            AnalysisContext(comparison_mode=COMPARISON_NONE),
            SUCCESS_SECTIONS,
        ),
    ),
)
def test_every_valid_result_family_resolves_all_of_its_sections(
    language,
    analysis_id,
    is_compare,
    is_sequential,
    analysis_context,
    section_ids,
):
    """Render every valid Compare and Success section without raw placeholders."""
    for section_id in section_ids:
        guidance = _build_guidance(
            section_id,
            language=language,
            analysis_id=analysis_id,
            is_compare=is_compare,
            is_sequential=is_sequential,
            analysis_context=analysis_context,
        )

        assert RESULT_GUIDANCE[language]["read_label"] in guidance
        assert RESULT_GUIDANCE[language]["limits_label"] in guidance
        assert not _format_fields(guidance)


@pytest.mark.parametrize(
    (
        "comparison_mode",
        "local_benchmark",
        "expected_text",
        "unexpected_text",
    ),
    (
        (
            COMPARISON_HARDWARE_AB,
            LOCAL_BENCHMARK_MEDIAN,
            "other controlled path operating within the shared Grid-4",
            "exact reporting identity",
        ),
        (
            COMPARISON_REFERENCE_STATION,
            LOCAL_BENCHMARK_MEDIAN,
            "selected by its exact callsign and independently configured "
            "Reference Grid-4",
            "shared Grid-4",
        ),
        (
            COMPARISON_LOCAL_NEIGHBORHOOD,
            LOCAL_BENCHMARK_MEDIAN,
            "median of qualifying active local identities within 175 km",
            "strongest qualifying local identity",
        ),
        (
            COMPARISON_LOCAL_NEIGHBORHOOD,
            LOCAL_BENCHMARK_BEST,
            "strongest qualifying local identity within 175 km",
            "median of qualifying active local identities",
        ),
    ),
)
def test_compare_context_resolves_the_active_benchmark(
    comparison_mode,
    local_benchmark,
    expected_text,
    unexpected_text,
):
    """Append only the interpretation limits of the configured benchmark."""
    guidance = _build_guidance(
        RESULT_GUIDANCE_CONTEXT,
        analysis_context=AnalysisContext(
            comparison_mode=comparison_mode,
            local_benchmark=local_benchmark,
            neighborhood_radius_km=175,
        ),
    )

    assert expected_text in guidance
    assert unexpected_text not in guidance


def test_mode_specific_terms_and_compare_pairing_are_resolved_semantically():
    """Use direction-specific peer roles, denominators, and pairing language."""
    rx_context = _build_guidance(
        RESULT_GUIDANCE_CONTEXT,
        analysis_id="RX_ABS",
        is_compare=False,
        analysis_context=AnalysisContext(),
    )
    tx_context = _build_guidance(
        RESULT_GUIDANCE_CONTEXT,
        analysis_id="TX_ABS",
        is_compare=False,
        analysis_context=AnalysisContext(),
    )
    rx_success = _build_guidance(
        RESULT_GUIDANCE_MAP,
        analysis_id="RX_ABS",
        is_compare=False,
        analysis_context=AnalysisContext(),
    )
    tx_success = _build_guidance(
        RESULT_GUIDANCE_MAP,
        analysis_id="TX_ABS",
        is_compare=False,
        analysis_context=AnalysisContext(),
    )
    rx_formula = _build_guidance(
        RESULT_GUIDANCE_SUCCESS_EVIDENCE,
        analysis_id="RX_ABS",
        is_compare=False,
        analysis_context=AnalysisContext(),
    )
    tx_formula = _build_guidance(
        RESULT_GUIDANCE_SUCCESS_EVIDENCE,
        analysis_id="TX_ABS",
        is_compare=False,
        analysis_context=AnalysisContext(),
    )
    joint_compare = _build_guidance(
        RESULT_GUIDANCE_COMPARISON_EVIDENCE,
        analysis_context=AnalysisContext(
            comparison_mode=COMPARISON_REFERENCE_STATION
        ),
    )
    scheduled_compare = _build_guidance(
        RESULT_GUIDANCE_COMPARISON_EVIDENCE,
        analysis_id="TX_COMP",
        is_sequential=True,
        analysis_context=AnalysisContext(
            comparison_mode=COMPARISON_HARDWARE_AB
        ),
    )

    assert "remote TX identities" in rx_success
    assert "Elsewhere" in rx_success
    assert "remote RX identities" in tx_success
    assert "Other Signals" in tx_success
    assert "Target-Active Gate" in rx_context
    assert "Target-Active Gate" in tx_context
    assert "confirmed opportunity" in rx_context
    assert "confirmed opportunity" in tx_context
    assert "100 × Target / (Target + Elsewhere)" in rx_formula
    assert "100 × Target / (Target + Other Signals)" in tx_formula
    assert "A **Joint Spot**" in joint_compare
    assert "Both (Async) means evidence from both sides" in joint_compare
    assert "A **Scheduled Pair**" in scheduled_compare
    assert (
        "Both (Async) describes an identity with evidence from both scheduled "
        "paths"
        in scheduled_compare
    )
    assert "time-separated transmissions" in scheduled_compare


def test_german_success_guidance_uses_the_exact_zero_target_control_label():
    """Keep interpretation instructions aligned with the rendered German UI."""
    guidance = _build_guidance(
        RESULT_GUIDANCE_STATION_INSIGHTS,
        language="de",
        analysis_id="RX_ABS",
        is_compare=False,
        analysis_context=AnalysisContext(),
    )

    assert f"`{T['de']['lbl_show_zero_hits']}`" in guidance


@pytest.mark.parametrize("language", ("en", "de"))
def test_success_guidance_names_the_rendered_figures_exactly(language):
    """Let readers match each explanation to its visible figure title."""
    success_figures = _build_guidance(
        RESULT_GUIDANCE_SUCCESS_EVIDENCE,
        language=language,
        analysis_id="RX_ABS",
        is_compare=False,
        analysis_context=AnalysisContext(),
    )
    selected_figures = _build_guidance(
        RESULT_GUIDANCE_SELECTED_STATIONS,
        language=language,
        analysis_id="RX_ABS",
        is_compare=False,
        analysis_context=AnalysisContext(),
    )

    assert "Station Success Rate by Evidence Count" in success_figures
    assert "Average Station Success Rate" in success_figures
    assert "Observation-Level Success Rate" in success_figures
    assert "Station Success Rate + Evidence over Time" in selected_figures
    assert "Target SNR" in selected_figures


@pytest.mark.parametrize(
    ("section_id", "analysis_id", "is_compare", "is_sequential", "match"),
    (
        (
            RESULT_GUIDANCE_COMPARISON_EVIDENCE,
            "RX_ABS",
            False,
            False,
            "unavailable for Success",
        ),
        (
            RESULT_GUIDANCE_TEMPORAL_EVIDENCE,
            "TX_ABS",
            False,
            False,
            "unavailable for Success",
        ),
        (
            RESULT_GUIDANCE_SUCCESS_EVIDENCE,
            "RX_COMP",
            True,
            False,
            "unavailable for Compare",
        ),
        (
            RESULT_GUIDANCE_CONTEXT,
            "RX_COMP",
            True,
            True,
            "valid only for TX Hardware A/B Compare",
        ),
        (
            RESULT_GUIDANCE_CONTEXT,
            "TX_ABS",
            False,
            True,
            "valid only for TX Hardware A/B Compare",
        ),
        (
            RESULT_GUIDANCE_CONTEXT,
            "TX_COMP",
            True,
            True,
            "valid only for TX Hardware A/B Compare",
        ),
        (
            RESULT_GUIDANCE_MAP,
            "not-an-analysis",
            False,
            False,
            "requires an RX or TX analysis ID",
        ),
    ),
)
def test_invalid_mode_and_section_combinations_are_rejected(
    section_id,
    analysis_id,
    is_compare,
    is_sequential,
    match,
):
    """Reject result-help combinations absent from the actual analysis flow."""
    with pytest.raises(ValueError, match=match):
        _build_guidance(
            section_id,
            analysis_id=analysis_id,
            is_compare=is_compare,
            is_sequential=is_sequential,
            analysis_context=AnalysisContext(
                comparison_mode=COMPARISON_REFERENCE_STATION
            ),
        )


def test_invalid_guidance_identity_language_and_benchmark_are_rejected():
    """Fail clearly instead of silently selecting unrelated localized content."""
    with pytest.raises(ValueError, match="Unknown result-guidance section"):
        _build_guidance(
            "not-a-section",
            analysis_context=AnalysisContext(
                comparison_mode=COMPARISON_REFERENCE_STATION
            ),
        )

    with pytest.raises(ValueError, match="Unsupported result-guidance language"):
        build_result_guidance(
            RESULT_GUIDANCE_DOWNLOAD,
            language="fr",
            translations=T["en"],
        )

    with pytest.raises(ValueError, match="supported comparison mode"):
        _build_guidance(
            RESULT_GUIDANCE_CONTEXT,
            analysis_context=AnalysisContext(
                comparison_mode=COMPARISON_NONE
            ),
        )

    with pytest.raises(ValueError, match="Unsupported local benchmark"):
        _build_guidance(
            RESULT_GUIDANCE_CONTEXT,
            analysis_context=AnalysisContext(
                comparison_mode=COMPARISON_LOCAL_NEIGHBORHOOD,
                local_benchmark="unsupported-local-benchmark",
            ),
        )


def test_local_median_drilldown_appends_dynamic_reference_explanation():
    """Explain expanded contributors only for the Local Median row contract."""
    local_median = _build_guidance(
        RESULT_GUIDANCE_DRILLDOWN,
        analysis_context=AnalysisContext(
            comparison_mode=COMPARISON_LOCAL_NEIGHBORHOOD,
            local_benchmark=LOCAL_BENCHMARK_MEDIAN,
        ),
    )
    local_best = _build_guidance(
        RESULT_GUIDANCE_DRILLDOWN,
        analysis_context=AnalysisContext(
            comparison_mode=COMPARISON_LOCAL_NEIGHBORHOOD,
            local_benchmark=LOCAL_BENCHMARK_BEST,
        ),
    )

    median_read = RESULT_GUIDANCE["en"]["sections"][
        "drilldown_local_median"
    ]["read"]
    median_limits = RESULT_GUIDANCE["en"]["sections"][
        "drilldown_local_median"
    ]["limits"]
    assert median_read in local_median
    assert median_limits in local_median
    assert median_read not in local_best
    assert median_limits not in local_best
    assert RESULT_GUIDANCE["en"]["sections"]["drilldown_compare_joint"][
        "read"
    ] in local_median


def _render_popover_snapshot(input_view):
    """Run one minimal result popover and return its visible semantic payload."""
    script = f"""
import streamlit as st
from core.analysis_context import AnalysisContext, COMPARISON_REFERENCE_STATION
from i18n import T
from ui.result_guidance import (
    RESULT_GUIDANCE_MAP,
    render_result_guidance_popover,
)

st.session_state["input_view"] = {input_view!r}
render_result_guidance_popover(
    RESULT_GUIDANCE_MAP,
    "Map View",
    language="en",
    translations=T["en"],
    key="result-guidance-map",
    analysis_id="RX_COMP",
    is_compare=True,
    analysis_context=AnalysisContext(
        comparison_mode=COMPARISON_REFERENCE_STATION
    ),
)
"""
    application = AppTest.from_string(script, default_timeout=10).run()

    assert not application.exception
    assert application.session_state["input_view"] == input_view
    assert len(application.get("popover")) == 1
    assert len(application.markdown) == 1
    popover_proto = application.get("popover")[0].proto
    return {
        "label": popover_proto.popover.label,
        "help": popover_proto.popover.help,
        "icon": popover_proto.popover.icon,
        "type": popover_proto.popover.type,
        "uses_content_width": popover_proto.width_config.use_content,
        "body": application.markdown[0].value,
    }


def test_result_popover_is_identical_in_guided_and_classic_input_views():
    """Expose the same optional interpretation layer in both input workflows."""
    guided = _render_popover_snapshot("guided")
    classic = _render_popover_snapshot("classic")

    assert guided == classic
    assert guided["label"] == RESULT_GUIDANCE["en"]["trigger"]
    assert guided["help"] == "How to read Map View"
    assert guided["icon"] == ":material/help_outline:"
    assert guided["type"] == "tertiary"
    assert guided["uses_content_width"] is True
    assert RESULT_GUIDANCE["en"]["read_label"] in guided["body"]
    assert RESULT_GUIDANCE["en"]["limits_label"] in guided["body"]


def _guidance_call_sections(relative_path):
    """Return the semantic section constants passed at one renderer call site."""
    source_path = REPOSITORY_ROOT / relative_path
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    sections = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Name):
            continue
        if node.func.id != "render_result_guidance_popover":
            continue
        assert node.args and isinstance(node.args[0], ast.Name), relative_path
        sections.append(node.args[0].id)
    return Counter(sections)


def test_every_rendered_result_heading_has_its_expected_guidance_placement():
    """Keep optional help attached to the complete shared result hierarchy."""
    assert _guidance_call_sections("ui/run_controller.py") == Counter(
        {
            "RESULT_GUIDANCE_CONTEXT": 1,
            "RESULT_GUIDANCE_MAP": 1,
        }
    )
    assert _guidance_call_sections("ui/results_export.py") == Counter(
        {"RESULT_GUIDANCE_DOWNLOAD": 1}
    )
    assert _guidance_call_sections(
        "ui/components/segment_inspector.py"
    ) == Counter(
        {
            "RESULT_GUIDANCE_SEGMENT": 1,
            "RESULT_GUIDANCE_COMPARISON_EVIDENCE": 1,
            "RESULT_GUIDANCE_TEMPORAL_EVIDENCE": 1,
            "RESULT_GUIDANCE_SUCCESS_EVIDENCE": 1,
            "RESULT_GUIDANCE_STATION_INSIGHTS": 2,
            "RESULT_GUIDANCE_SELECTED_STATIONS": 3,
            "RESULT_GUIDANCE_DRILLDOWN": 1,
        }
    )

    documentation_source = (
        REPOSITORY_ROOT / "ui" / "documentation.py"
    ).read_text(encoding="utf-8")
    assert "render_result_guidance_popover" not in documentation_source
