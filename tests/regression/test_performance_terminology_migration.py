"""Cross-catalog and renderer contracts for the Performance terminology migration."""

import ast
from pathlib import Path
import re
from string import Formatter

import pytest

from i18n import GUIDED_INPUTS, RESULT_GUIDANCE, T


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
LOCALIZED_CATALOGS = {
    "T": T,
    "RESULT_GUIDANCE": RESULT_GUIDANCE,
    "GUIDED_INPUTS": GUIDED_INPUTS,
}
TARGETED_RENDERER_PATHS = (
    "core/plot_engine.py",
    "ui/components/segment_inspector.py",
    "ui/inspector/drilldown.py",
    "ui/result_hierarchy.py",
    "ui/results_export.py",
)
RUNTIME_PRESENTATION_PATHS = (
    "app.py",
    "core/analysis_runner.py",
    "core/opportunity_engine.py",
    "core/plot_engine.py",
    "core/presentation_context.py",
    "docs/pdf_generator.py",
    "ui/components/config_panel.py",
    "ui/components/segment_inspector.py",
    "ui/config_io.py",
    "ui/config_save.py",
    "ui/guided_inputs/renderer.py",
    "ui/inspector/drilldown.py",
    "ui/inspector/view_models.py",
    "ui/plots/evidence_figures.py",
    "ui/plots/opportunity_figures.py",
    "ui/presentation_context_adapter.py",
    "ui/result_guidance.py",
    "ui/result_hierarchy.py",
    "ui/results_export.py",
    "ui/run_controller.py",
)
LANGUAGE_NAMES = frozenset({"lang", "language"})
INTERNAL_EXCEPTION_CONSTRUCTORS = frozenset(
    {"AssertionError", "KeyError", "RuntimeError", "TypeError", "ValueError"}
)
VISIBLE_LEGACY_TERMINOLOGY = re.compile(
    r"\b(?:RX Success|TX Success|Success Results|Success Evidence|Success Rate|Success)\b"
    r"|\b(?:RX Compare|TX Compare|Compare (?:Results?|Evidence|Mode|Temporal|Map|Selected|Station|result|setup))\b"
    r"|\bCompare-(?:Evidenz|Modus|Ergebnis)\b"
)


def _flatten_catalog(catalog, prefix=()):
    """Return every nested catalog leaf keyed by its exact semantic path."""
    leaves = {}
    for key, value in catalog.items():
        path = (*prefix, key)
        if isinstance(value, dict):
            leaves.update(_flatten_catalog(value, path))
        else:
            leaves[path] = value
    return leaves


def _formatter_tokens(template):
    """Return ordered field, conversion, and format-spec tokens from a template."""
    return tuple(
        (field_name, conversion, format_spec)
        for _literal, field_name, format_spec, conversion in Formatter().parse(
            template
        )
        if field_name is not None
    )


def _references_language(node):
    """Return whether an expression reads a language selector or locale token."""
    for descendant in ast.walk(node):
        if isinstance(descendant, ast.Name) and descendant.id in LANGUAGE_NAMES:
            return True
        if (
            isinstance(descendant, ast.Attribute)
            and descendant.attr in LANGUAGE_NAMES
        ):
            return True
        if (
            isinstance(descendant, ast.Call)
            and isinstance(descendant.func, ast.Attribute)
            and descendant.func.attr == "get"
            and descendant.args
            and isinstance(descendant.args[0], ast.Constant)
            and descendant.args[0].value in LANGUAGE_NAMES
        ):
            return True
    return False


def _technical_literal_node_ids(syntax_tree):
    """Return docstring and internal-exception literals excluded from UI copy scans."""
    technical_node_ids = set()
    for node in ast.walk(syntax_tree):
        if (
            isinstance(
                node,
                (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
            )
            and node.body
        ):
            first_statement = node.body[0]
            if (
                isinstance(first_statement, ast.Expr)
                and isinstance(first_statement.value, ast.Constant)
                and isinstance(first_statement.value.value, str)
            ):
                technical_node_ids.add(id(first_statement.value))
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in INTERNAL_EXCEPTION_CONSTRUCTORS
        ):
            technical_node_ids.update(
                id(descendant)
                for descendant in ast.walk(node)
                if isinstance(descendant, ast.Constant)
                and isinstance(descendant.value, str)
            )
    return technical_node_ids


@pytest.mark.parametrize(
    ("catalog_name", "catalog"),
    tuple(LOCALIZED_CATALOGS.items()),
)
def test_localization_catalogs_have_exact_recursive_key_and_formatter_parity(
    catalog_name,
    catalog,
):
    """Keep every English/German leaf and complete format token interchangeable."""
    assert set(catalog) == {"en", "de"}, catalog_name
    english_leaves = _flatten_catalog(catalog["en"])
    german_leaves = _flatten_catalog(catalog["de"])

    assert english_leaves.keys() == german_leaves.keys(), catalog_name
    for path in sorted(english_leaves):
        english_value = english_leaves[path]
        german_value = german_leaves[path]
        assert isinstance(english_value, str), (catalog_name, path, "en")
        assert isinstance(german_value, str), (catalog_name, path, "de")
        assert _formatter_tokens(english_value) == _formatter_tokens(
            german_value
        ), (catalog_name, path)


@pytest.mark.parametrize(
    ("catalog_name", "catalog"),
    tuple(LOCALIZED_CATALOGS.items()),
)
def test_localization_catalogs_have_no_visible_legacy_result_terminology(
    catalog_name,
    catalog,
):
    """Keep retired result-family wording out of every visible catalog leaf."""
    for language in ("en", "de"):
        for path, visible_text in _flatten_catalog(catalog[language]).items():
            assert VISIBLE_LEGACY_TERMINOLOGY.search(visible_text) is None, (
                catalog_name,
                language,
                path,
                visible_text,
            )


@pytest.mark.parametrize("relative_path", RUNTIME_PRESENTATION_PATHS)
def test_runtime_presentation_literals_have_no_visible_legacy_terminology(
    relative_path,
):
    """Allow canonical technical prose but reject retired renderable literals."""
    source_path = REPOSITORY_ROOT / relative_path
    syntax_tree = ast.parse(source_path.read_text(encoding="utf-8"))
    technical_node_ids = _technical_literal_node_ids(syntax_tree)
    legacy_literals = [
        (node.lineno, node.value)
        for node in ast.walk(syntax_tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and id(node) not in technical_node_ids
        and VISIBLE_LEGACY_TERMINOLOGY.search(node.value)
    ]

    assert not legacy_literals, (relative_path, legacy_literals)


@pytest.mark.parametrize("relative_path", TARGETED_RENDERER_PATHS)
def test_targeted_renderers_do_not_branch_on_presentation_language(relative_path):
    """Keep wording selection in injected catalogs rather than renderer branches."""
    source_path = REPOSITORY_ROOT / relative_path
    syntax_tree = ast.parse(source_path.read_text(encoding="utf-8"))
    language_conditionals = [
        (node.lineno, ast.unparse(node.test))
        for node in ast.walk(syntax_tree)
        if isinstance(node, (ast.If, ast.IfExp))
        and _references_language(node.test)
    ]
    language_matches = [
        (node.lineno, ast.unparse(node.subject))
        for node in ast.walk(syntax_tree)
        if isinstance(node, ast.Match)
        and _references_language(node.subject)
    ]

    assert not language_conditionals, (relative_path, language_conditionals)
    assert not language_matches, (relative_path, language_matches)


@pytest.mark.parametrize("language", ["en", "de"])
def test_guided_canonical_result_families_render_as_performance_and_benchmark(language):
    """Keep persisted Guided values stable behind the approved visible labels."""
    use_cases = GUIDED_INPUTS[language]["options"]["use_cases"]

    assert use_cases["rx_performance"]["label"] == "RX Performance"
    assert use_cases["tx_performance"]["label"] == "TX Performance"
    assert use_cases["rx_benchmark"]["label"] in {"RX Benchmark", "RX-Benchmark"}
    assert use_cases["tx_benchmark"]["label"] in {"TX Benchmark", "TX-Benchmark"}
