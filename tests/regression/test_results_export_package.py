"""Prepared-results package structure regression tests."""

from contextlib import nullcontext
import io
import inspect
import json
from types import SimpleNamespace
import zipfile

import pandas as pd
import pytest

from core import plot_engine
from core.analysis_context import AnalysisContext
from i18n import T
from ui import results_export
from ui.plots import compare_evidence_figures, evidence_figures


SUCCESS_SELECTED_FIGURE_EXPORTS = (
    (
        "figure_selected_station_snr_evidence.png",
        "render_segment_temporal_snr_export_figure",
        "selected_station_snr_evidence_figure_recipe",
        "figure_segment_temporal_snr_deviation.png",
        "segment_temporal_snr_deviation_figure_recipe",
    ),
    (
        "figure_selected_station_temporal_evidence.png",
        "render_segment_temporal_evidence_export_figure",
        "selected_station_temporal_evidence_figure_recipe",
        "figure_segment_temporal_evidence.png",
        "segment_temporal_evidence_figure_recipe",
    ),
)
OBSOLETE_SUCCESS_SELECTED_FIGURE_NAMES = (
    "figure_selected_station_chronological.png",
    "figure_selected_station_utc_hour_profile.png",
    "figure_selected_station_snr_distribution.png",
    "figure_selected_station_similar_stations.png",
)
COMPARE_COVERAGE_EXPORT_CASES = (
    (
        "figure_segment_temporal_coverage.png",
        "render_compare_temporal_coverage_export_figure",
        "segment_temporal_coverage_figure_recipe",
        "evidence_title",
        "Compare Temporal Evidence Coverage",
    ),
    (
        "figure_selected_station_coverage.png",
        "render_selected_compare_coverage_export_figure",
        "selected_station_coverage_figure_recipe",
        "evidence_title",
        "Selected Path Evidence Coverage",
    ),
)
RETIRED_COMPARE_FIGURE_EXPORTS = (
    (
        "figure_segment_temporal_delta_change.png",
        "segment_temporal_delta_change_figure_recipe",
        "render_compare_delta_change_export_figure",
    ),
    (
        "figure_path_agreement_consistency.png",
        "path_agreement_consistency_figure_recipe",
        "render_compare_path_consistency_export_figure",
    ),
)


class _FooterColumn:
    """Minimal context-manager column used by footer rendering tests."""

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


class _FooterPopover(_FooterColumn):
    """Minimal open-state popover used by footer rendering tests."""

    def __init__(self, is_open=False):
        self.open = bool(is_open)


def test_selected_compare_bin_is_recorded_without_retired_view_metadata(monkeypatch):
    """Fingerprint the shared dual-panel bin without exporting dead toggle state."""
    monkeypatch.setattr(
        results_export,
        "st",
        SimpleNamespace(session_state={"lang": "en"}),
    )
    block = {
        "analysis_id": "RX_COMPARE",
        "mode_folder": results_export.COMPARE_EXPORT_FOLDER,
        "database_source": "wspr_live",
        "evidence_time_bin": "1h",
        "selected_evidence_figure_recipe": {
            "kind": "selected_compare_temporal",
        },
    }
    one_hour_blocks = {"RX_COMPARE": block}
    six_hour_blocks = {
        "RX_COMPARE": {
            **block,
            "evidence_time_bin": "6h",
        }
    }

    one_hour_metadata = results_export._build_run_metadata(
        one_hour_blocks,
        {"settings": {}},
    )
    six_hour_metadata = results_export._build_run_metadata(
        six_hour_blocks,
        {"settings": {}},
    )

    assert one_hour_metadata["result_blocks"][0]["evidence_time_bin"] == "1h"
    assert six_hour_metadata["result_blocks"][0]["evidence_time_bin"] == "6h"
    assert "selected_evidence_time_view" not in (
        one_hour_metadata["result_blocks"][0]
    )
    assert "selected_evidence_time_view" not in (
        six_hour_metadata["result_blocks"][0]
    )
    assert one_hour_metadata["export_signature"] != six_hour_metadata[
        "export_signature"
    ]


def test_show_zero_target_is_recorded_and_changes_export_signature(monkeypatch):
    """Invalidate prepared Success exports when zero-Target visibility changes."""
    monkeypatch.setattr(
        results_export,
        "st",
        SimpleNamespace(session_state={"lang": "en"}),
    )
    hidden_block = {
        "analysis_id": "RX_ABS",
        "mode_folder": results_export.SUCCESS_EXPORT_FOLDER,
        "database_source": "wspr_live",
        "show_zero_target": False,
    }
    shown_block = {**hidden_block, "show_zero_target": True}

    metadata = results_export._build_run_metadata(
        {"RX_ABS": shown_block},
        {"settings": {}},
    )

    assert metadata["result_blocks"][0]["show_zero_target"] is True
    assert results_export._export_signature(
        {"RX_ABS": hidden_block}
    ) != results_export._export_signature({"RX_ABS": shown_block})


def test_temporal_snr_render_version_changes_export_signature(monkeypatch):
    """Invalidate prepared ZIPs when temporal SNR rendering changes on reload."""
    blocks = {
        "RX_ABS": {
            "analysis_id": "RX_ABS",
            "mode_folder": results_export.SUCCESS_EXPORT_FOLDER,
            "database_source": "wspr_live",
        }
    }

    monkeypatch.setattr(results_export, "TEMPORAL_SNR_EXPORT_RENDER_VERSION", 2)
    version_two_signature = results_export._export_signature(blocks)
    version_two_payload = json.loads(version_two_signature)
    monkeypatch.setattr(results_export, "TEMPORAL_SNR_EXPORT_RENDER_VERSION", 3)

    assert version_two_payload[0]["temporal_snr_export_render_version"] == 2
    assert version_two_signature != results_export._export_signature(blocks)


def test_temporal_iqr_band_alpha_changes_export_signature(monkeypatch):
    """Invalidate prepared ZIPs when configured IQR shading changes."""
    blocks = {
        "RX_COMPARE": {
            "analysis_id": "RX_COMPARE",
            "mode_folder": results_export.COMPARE_EXPORT_FOLDER,
            "database_source": "wspr_live",
        }
    }

    monkeypatch.setattr(results_export, "TEMPORAL_IQR_BAND_ALPHA", 0.10)
    ten_percent_signature = results_export._export_signature(blocks)
    ten_percent_payload = json.loads(ten_percent_signature)
    monkeypatch.setattr(results_export, "TEMPORAL_IQR_BAND_ALPHA", 0.15)

    assert ten_percent_payload[0]["temporal_iqr_band_alpha"] == pytest.approx(
        0.10
    )
    assert ten_percent_signature != results_export._export_signature(blocks)


def test_run_metadata_records_correction_mode_and_numeric_value(monkeypatch):
    """Preserve operator correction provenance beside its scientific value."""
    monkeypatch.setattr(
        results_export,
        "st",
        SimpleNamespace(session_state={"lang": "en"}),
    )
    metadata = results_export._build_run_metadata(
        {
            "RX_COMPARE": {
                "analysis_id": "RX_COMPARE",
                "mode_folder": results_export.COMPARE_EXPORT_FOLDER,
                "database_source": "wspr_live",
            }
        },
        {
            "settings": {
                "comparison_parameters": {
                    "mode": "hardware_ab",
                    "snr_correction_mode": "establish_offset",
                    "snr_correction_db": 0.0,
                }
            }
        },
    )

    assert metadata["benchmark_snr_correction_mode"] == "establish_offset"
    assert metadata["benchmark_snr_correction_db"] == 0.0


def test_run_metadata_records_only_the_canonical_absolute_time_window(monkeypatch):
    """Keep result metadata endpoints identical to the embedded config."""
    monkeypatch.setattr(
        results_export,
        "st",
        SimpleNamespace(session_state={"lang": "en"}),
    )
    time_selection = {
        "start_utc": "2026-07-01T00:00Z",
        "end_utc": "2026-07-02T00:00Z",
    }

    metadata = results_export._build_run_metadata(
        {
            "RX_ABS": {
                "analysis_id": "RX_ABS",
                "mode_folder": results_export.SUCCESS_EXPORT_FOLDER,
                "database_source": "wspr_live",
            }
        },
        {
            "settings": {
                "core_parameters": {
                    "time_selection": time_selection,
                },
            }
        },
    )

    assert metadata["time_window"] == time_selection


def test_run_metadata_rejects_mixed_database_sources(monkeypatch):
    monkeypatch.setattr(
        results_export,
        "st",
        SimpleNamespace(session_state={"lang": "en"}),
    )
    blocks = {
        "RX_COMP": {
            "analysis_id": "RX_COMP",
            "mode_folder": results_export.COMPARE_EXPORT_FOLDER,
            "database_source": "wspr_live",
        },
        "RX_ABS": {
            "analysis_id": "RX_ABS",
            "mode_folder": results_export.SUCCESS_EXPORT_FOLDER,
            "database_source": "wd2",
        },
    }

    with pytest.raises(ValueError, match="share one database source"):
        results_export._build_run_metadata(blocks, {"settings": {}})


def test_run_metadata_rejects_missing_database_provenance(monkeypatch):
    monkeypatch.setattr(
        results_export,
        "st",
        SimpleNamespace(session_state={"lang": "en"}),
    )

    with pytest.raises(ValueError, match="must record one database source"):
        results_export._build_run_metadata(
            {
                "RX_ABS": {
                    "analysis_id": "RX_ABS",
                    "mode_folder": results_export.SUCCESS_EXPORT_FOLDER,
                }
            },
            {"settings": {}},
        )


@pytest.mark.parametrize("is_prepared", (False, True))
def test_results_footer_always_renders_redundant_save_control(
    monkeypatch,
    is_prepared,
):
    """Keep Save Config beside both Prepare and Download Prepared states."""
    session_state = {}
    if is_prepared:
        session_state.update(
            {
                results_export.EXPORT_ZIP_SIGNATURE_KEY: "current-signature",
                results_export.EXPORT_ZIP_BYTES_KEY: b"zip",
                results_export.EXPORT_ZIP_FILENAME_KEY: "results.zip",
            }
        )
    captured = {
        "columns": None,
        "save_calls": [],
        "share_popovers": [],
        "downloads": [],
        "events": [],
    }
    fake_streamlit = SimpleNamespace(
        session_state=session_state,
        markdown=lambda body, **_kwargs: captured["events"].append(
            ("markdown", body)
        ),
        columns=lambda widths, **kwargs: (
            captured["events"].append(("columns", widths))
            or captured.update(columns=(widths, kwargs))
            or (_FooterColumn(), _FooterColumn(), _FooterColumn())
        ),
        popover=lambda *args, **kwargs: (
            captured["share_popovers"].append((args, kwargs))
            or _FooterPopover()
        ),
        button=lambda *_args, **_kwargs: False,
        download_button=lambda label, **kwargs: captured["downloads"].append(
            (label, kwargs)
        ),
    )
    monkeypatch.setattr(results_export, "st", fake_streamlit)
    monkeypatch.setattr(
        results_export,
        "_ensure_current_export_state",
        lambda: {"RX_ABS": {"mode_folder": results_export.SUCCESS_EXPORT_FOLDER}},
    )
    monkeypatch.setattr(
        results_export,
        "_export_signature",
        lambda _blocks: "current-signature",
    )
    monkeypatch.setattr(
        results_export,
        "render_config_save_control",
        lambda **kwargs: captured["save_calls"].append(kwargs),
    )

    results_export.render_download_all_results(T["en"])

    assert captured["columns"] == (
        [0.5, 0.25, 0.25],
        {"gap": "large", "vertical_alignment": "center"},
    )
    assert captured["save_calls"] == [
        {
            "popover_key": "config_save_results_trigger",
            "form_scope": "results",
        }
    ]
    assert bool(captured["downloads"]) is is_prepared
    assert captured["share_popovers"] == [
        (
            (T["en"]["btn_share_analysis"],),
            {
                "icon": ":material/share:",
                "type": "primary",
                "width": "stretch",
                "key": "share_analysis_results_trigger",
                "on_change": "rerun",
            },
        )
    ]
    heading_events = [
        (index, body)
        for index, (kind, body) in enumerate(captured["events"])
        if kind == "markdown"
        and "<h3 class='result-utility-title'>Download Evidence</h3>" in body
    ]
    assert len(heading_events) == 1
    columns_index = next(
        index
        for index, (kind, _value) in enumerate(captured["events"])
        if kind == "columns"
    )
    assert heading_events[0][0] < columns_index


def test_open_share_popover_builds_canonical_url_and_localized_browser_copy(
    monkeypatch,
):
    """Build Share Analysis content only for an open completed-result popover."""
    session_state = {
        "run_id": 42,
        "val_callsign": "dl1mks",
        "val_analysis_direction": "rx",
        "val_comp_mode": "hardware_ab",
        "val_band": "20m",
    }
    browser_calls = []
    build_calls = []
    fake_streamlit = SimpleNamespace(
        session_state=session_state,
        markdown=lambda *_args, **_kwargs: None,
        columns=lambda *_args, **_kwargs: (
            _FooterColumn(),
            _FooterColumn(),
            _FooterColumn(),
        ),
        button=lambda *_args, **_kwargs: False,
        download_button=lambda *_args, **_kwargs: None,
        popover=lambda *_args, **_kwargs: _FooterPopover(is_open=True),
    )
    monkeypatch.setattr(results_export, "st", fake_streamlit)
    monkeypatch.setattr(
        results_export,
        "_ensure_current_export_state",
        lambda: {
            "RX_COMPARE": {
                "mode_folder": results_export.COMPARE_EXPORT_FOLDER
            }
        },
    )
    monkeypatch.setattr(
        results_export,
        "_export_signature",
        lambda _blocks: "share-signature",
    )
    monkeypatch.setattr(
        results_export,
        "render_config_save_control",
        lambda **_kwargs: None,
    )
    monkeypatch.setattr(
        results_export,
        "build_share_url",
        lambda state: (
            build_calls.append(state)
            or "https://wspradar.org/?v=1&run=1#wspradar-results-inspection"
        ),
    )
    monkeypatch.setattr(
        results_export,
        "render_share_analysis_browser",
        lambda **kwargs: browser_calls.append(kwargs),
    )

    results_export.render_download_all_results(T["en"])

    assert build_calls == [session_state]
    assert browser_calls == [
        {
            "share_url": (
                "https://wspradar.org/?v=1&run=1"
                "#wspradar-results-inspection"
            ),
            "title": (
                "WSPRadar analysis: DL1MKS RX Hardware A/B on 20m"
            ),
            "message": T["en"]["share_analysis_message"],
            "labels": {
                "url_field": T["en"]["share_url_field"],
                "copy_link": T["en"]["share_copy_link"],
                "copied": T["en"]["share_copied"],
                "manual_copy": T["en"]["share_manual_copy"],
                "native_share": T["en"]["share_native"],
                "native_share_failed": T["en"]["share_native_failed"],
                "email": T["en"]["share_email"],
                "whatsapp": T["en"]["share_whatsapp"],
                "x": T["en"]["share_x"],
                "facebook": T["en"]["share_facebook"],
                "linkedin": T["en"]["share_linkedin"],
            },
            "key": "share_analysis_browser_42",
        }
    ]


def test_results_footer_omits_heading_without_exportable_results(monkeypatch):
    """Do not show an orphan Download Evidence section for an empty run."""
    markdown_calls = []
    monkeypatch.setattr(
        results_export,
        "st",
        SimpleNamespace(
            session_state={},
            markdown=lambda body, **_kwargs: markdown_calls.append(body),
        ),
    )
    monkeypatch.setattr(
        results_export,
        "_ensure_current_export_state",
        lambda: {},
    )

    results_export.render_download_all_results(T["en"])

    assert markdown_calls == []


def test_segment_temporal_figure_uses_its_distinct_export_recipe(monkeypatch):
    """Keep segment temporal and selected-station figure recipes independent."""
    temporal_recipe = {"kind": "segment_compare_temporal", "time_bin": "6h"}
    fake_figure = object()
    disposed_figures = []

    monkeypatch.setattr(
        evidence_figures,
        "render_segment_temporal_evidence_export_figure",
        lambda recipe: fake_figure if recipe is temporal_recipe else None,
    )
    monkeypatch.setattr(
        results_export,
        "figure_to_png_bytes",
        lambda figure, *, paper_theme: b"temporal-png"
        if figure is fake_figure and paper_theme
        else b"",
    )
    monkeypatch.setattr(
        results_export,
        "dispose_matplotlib_figure",
        disposed_figures.append,
    )

    rendered = results_export._render_inspector_png_for_block(
        {
            "segment_temporal_evidence_figure_recipe": temporal_recipe,
            "selected_evidence_figure_recipe": {"kind": "selected"},
        },
        "figure_segment_temporal_evidence.png",
    )

    assert rendered == b"temporal-png"
    assert disposed_figures == [fake_figure]


def test_success_temporal_snr_figure_uses_its_separate_export_recipe(
    monkeypatch,
):
    """Render and dispose the standalone Success SNR-deviation export."""
    snr_recipe = {
        "kind": "opportunity_success_temporal",
        "time_bin": "6h",
    }
    fake_figure = object()
    disposed_figures = []

    monkeypatch.setattr(
        evidence_figures,
        "render_segment_temporal_snr_export_figure",
        lambda recipe: fake_figure if recipe is snr_recipe else None,
    )
    monkeypatch.setattr(
        results_export,
        "figure_to_png_bytes",
        lambda figure, *, paper_theme: b"temporal-snr-png"
        if figure is fake_figure and paper_theme
        else b"",
    )
    monkeypatch.setattr(
        results_export,
        "dispose_matplotlib_figure",
        disposed_figures.append,
    )

    rendered = results_export._render_inspector_png_for_block(
        {
            "segment_temporal_snr_deviation_figure_recipe": snr_recipe,
            "segment_temporal_evidence_figure_recipe": {
                "kind": "opportunity_success_temporal",
            },
        },
        "figure_segment_temporal_snr_deviation.png",
    )

    assert rendered == b"temporal-snr-png"
    assert disposed_figures == [fake_figure]


@pytest.mark.parametrize(
    (
        "figure_name",
        "renderer_name",
        "recipe_key",
        "title_key",
        "figure_title",
    ),
    COMPARE_COVERAGE_EXPORT_CASES,
)
def test_compare_coverage_figure_uses_its_registered_preview_recipe(
    monkeypatch,
    figure_name,
    renderer_name,
    recipe_key,
    title_key,
    figure_title,
):
    """Render each Compare export from the exact registered preview recipe."""
    recipe_kind = (
        compare_evidence_figures.COMPARE_SELECTED_PATH_COVERAGE_RECIPE_KIND
        if recipe_key == "selected_station_coverage_figure_recipe"
        else compare_evidence_figures.COMPARE_TEMPORAL_COVERAGE_RECIPE_KIND
    )
    recipe = {
        "kind": recipe_kind,
        "schema_version": 1,
        "time_bin": "6h",
        title_key: figure_title,
    }
    fake_figure = object()
    disposed_figures = []
    renderer_calls = []

    def render_coverage_recipe(received_recipe):
        renderer_calls.append(received_recipe)
        return fake_figure

    monkeypatch.setattr(
        compare_evidence_figures,
        renderer_name,
        render_coverage_recipe,
    )
    monkeypatch.setattr(
        results_export,
        "figure_to_png_bytes",
        lambda figure, *, paper_theme: b"compare-coverage-png"
        if figure is fake_figure and paper_theme
        else b"",
    )
    monkeypatch.setattr(
        results_export,
        "dispose_matplotlib_figure",
        disposed_figures.append,
    )

    rendered = results_export._render_inspector_png_for_block(
        {recipe_key: recipe},
        figure_name,
    )

    assert rendered == b"compare-coverage-png"
    assert renderer_calls == [recipe]
    assert renderer_calls[0] is recipe
    assert disposed_figures == [fake_figure]


@pytest.mark.parametrize(
    "figure_name",
    [
        export_case[0]
        for export_case in COMPARE_COVERAGE_EXPORT_CASES
    ],
)
def test_compare_coverage_export_omits_an_absent_recipe(
    figure_name,
):
    """Omit an inapplicable Compare figure instead of creating an empty file."""
    assert (
        results_export._render_inspector_png_for_block({}, figure_name)
        is None
    )


def test_retired_compare_figures_have_no_export_recipe_or_renderer_path():
    """Keep removed delta-change and path-consistency artifacts unreachable."""
    export_definitions = {
        (figure_name, recipe_key)
        for figure_name, recipe_key, _title_keys in (
            results_export.COMPARE_EVIDENCE_FIGURE_EXPORTS
        )
    }
    renderer_source = inspect.getsource(
        results_export._render_inspector_png_for_block
    )
    registration_parameters = inspect.signature(
        results_export.register_inspector_export
    ).parameters

    for figure_name, recipe_key, renderer_name in (
        RETIRED_COMPARE_FIGURE_EXPORTS
    ):
        assert (figure_name, recipe_key) not in export_definitions
        assert recipe_key not in registration_parameters
        assert renderer_name not in renderer_source
        assert (
            results_export._render_inspector_png_for_block(
                {recipe_key: {"kind": "retired"}},
                figure_name,
            )
            is None
        )


def test_register_inspector_export_keeps_compare_coverage_recipes_independent(
    monkeypatch,
):
    """Store both coverage recipes and fingerprint their stable identities."""
    blocks = {}
    recipes = {
        recipe_key: {
            "kind": (
                compare_evidence_figures.COMPARE_SELECTED_PATH_COVERAGE_RECIPE_KIND
                if recipe_key
                == "selected_station_coverage_figure_recipe"
                else compare_evidence_figures.COMPARE_TEMPORAL_COVERAGE_RECIPE_KIND
            ),
            "schema_version": 1,
            "time_bin": "6h",
            title_key: figure_title,
        }
        for (
            _figure_name,
            _renderer_name,
            recipe_key,
            title_key,
            figure_title,
        ) in COMPARE_COVERAGE_EXPORT_CASES
    }
    monkeypatch.setattr(
        results_export,
        "_ensure_current_export_state",
        lambda: blocks,
    )
    monkeypatch.setattr(
        results_export,
        "st",
        SimpleNamespace(session_state={"lang": "en"}),
    )

    results_export.register_inspector_export(
        analysis_id="RX_COMPARE",
        selected_segment="Full Range | All Directions",
        selected_distance="Full Range",
        selected_direction="All Directions",
        show_non_joint=False,
        evidence_time_bin="6h",
        segment_evidence_time_bin="6h",
        selected_stations=["OK1FCX (JN79)"],
        translations=T["en"],
        **recipes,
    )

    block = blocks["RX_COMPARE"]
    block.update(
        {
            "mode_folder": results_export.COMPARE_EXPORT_FOLDER,
            "database_source": "wspr_live",
        }
    )
    for recipe_key, recipe in recipes.items():
        assert block[recipe_key] is recipe

    metadata = results_export._build_run_metadata(
        blocks,
        {"settings": {}},
    )
    expected_descriptions = {
        figure_name: figure_title
        for (
            figure_name,
            _renderer_name,
            _recipe_key,
            _title_key,
            figure_title,
        ) in COMPARE_COVERAGE_EXPORT_CASES
    }
    assert metadata["result_blocks"][0]["compare_evidence_figures"] == (
        expected_descriptions
    )
    signature = json.loads(metadata["export_signature"])
    assert [
        recipe["filename"]
        for recipe in signature[0]["compare_evidence_recipes"]
    ] == list(expected_descriptions)
    without_selected_coverage = {
        "RX_COMPARE": {
            **block,
            "selected_station_coverage_figure_recipe": None,
        }
    }
    assert results_export._export_signature(blocks) != (
        results_export._export_signature(without_selected_coverage)
    )


def test_register_inspector_export_keeps_all_success_temporal_recipes_independent(
    monkeypatch,
):
    """Keep active-scope and selected-station canvases independently addressable."""
    blocks = {}
    evidence_recipe = {"kind": "opportunity_success_temporal"}
    snr_recipe = {"kind": "opportunity_success_temporal"}
    selected_evidence_recipe = {
        "kind": "opportunity_success_temporal",
        "population_mode": "selected_station",
        "snr_representation": "actual_normalized_snr",
    }
    selected_snr_recipe = dict(selected_evidence_recipe)
    monkeypatch.setattr(
        results_export,
        "_ensure_current_export_state",
        lambda: blocks,
    )

    results_export.register_inspector_export(
        analysis_id="RX_ABS",
        selected_segment="Full Range | All Directions",
        selected_distance="Full Range",
        selected_direction="All Directions",
        show_non_joint=False,
        evidence_time_bin="3h",
        selected_stations=["OK1FCX (JN79)"],
        translations=T["en"],
        segment_temporal_evidence_figure_recipe=evidence_recipe,
        segment_temporal_snr_deviation_figure_recipe=snr_recipe,
        selected_station_snr_evidence_figure_recipe=selected_snr_recipe,
        selected_station_temporal_evidence_figure_recipe=(
            selected_evidence_recipe
        ),
    )

    block = blocks["RX_ABS"]
    assert block["segment_temporal_evidence_figure_recipe"] is (
        evidence_recipe
    )
    assert block[
        "segment_temporal_snr_deviation_figure_recipe"
    ] is snr_recipe
    assert block["selected_station_snr_evidence_figure_recipe"] is (
        selected_snr_recipe
    )
    assert block["selected_station_temporal_evidence_figure_recipe"] is (
        selected_evidence_recipe
    )
    assert block["selected_evidence_figure_recipe"] is None
    assert selected_snr_recipe is not selected_evidence_recipe


@pytest.mark.parametrize(
    ("language", "selected_stations", "expected_weighting"),
    [
        ("en", ["K1AAA (FN31)"], "Single selected path"),
        ("de", ["K1AAA (FN31)"], "Ein ausgewählter Funkweg"),
        ("en", [], None),
    ],
)
def test_register_inspector_export_localizes_selected_evidence_weighting(
    monkeypatch,
    language,
    selected_stations,
    expected_weighting,
):
    """Localize descriptive weighting without changing selected identities."""
    blocks = {}
    monkeypatch.setattr(
        results_export,
        "_ensure_current_export_state",
        lambda: blocks,
    )

    results_export.register_inspector_export(
        analysis_id="RX_COMPARE",
        selected_segment="Full Range | All Directions",
        selected_distance="Full Range",
        selected_direction="All Directions",
        show_non_joint=False,
        evidence_time_bin="3h",
        selected_stations=selected_stations,
        translations=T[language],
    )

    block = blocks["RX_COMPARE"]
    assert block["selected_stations"] == selected_stations
    assert block["selected_station_count"] == len(selected_stations)
    assert block["selected_evidence_weighting"] == expected_weighting


@pytest.mark.parametrize(
    "selected_stations",
    [
        ["K1AAA (FN31)", "K2BBB (FN32)"],
        "K1AAA (FN31)",
    ],
)
def test_register_inspector_export_rejects_invalid_station_cardinality_atomically(
    monkeypatch,
    selected_stations,
):
    """Reject multi-station or malformed metadata before export-state access."""
    ensure_state_calls = []
    monkeypatch.setattr(
        results_export,
        "_ensure_current_export_state",
        lambda: ensure_state_calls.append(True) or {},
    )

    with pytest.raises(ValueError):
        results_export.register_inspector_export(
            analysis_id="RX_COMPARE",
            selected_segment="Full Range | All Directions",
            selected_distance="Full Range",
            selected_direction="All Directions",
            show_non_joint=False,
            evidence_time_bin="3h",
            selected_stations=selected_stations,
            translations=T["en"],
        )

    assert ensure_state_calls == []


@pytest.mark.parametrize(
    ("language", "expected_suffix"),
    [
        ("en", " (Reference correction +1.3 dB)"),
        ("de", " (Referenzkorrektur +1.3 dB)"),
    ],
)
def test_reference_correction_csv_suffix_is_localized_without_mutating_source_headers(
    language,
    expected_suffix,
):
    """Localize the optional CSV annotation while retaining source field identity."""
    source_frame = pd.DataFrame(
        {
            "Reference SNR (dB)": [-10.04],
            "Target SNR (dB)": [-12.34],
        }
    )
    source_columns = list(source_frame.columns)

    localized_csv = results_export._dataframe_to_csv_bytes(
        source_frame,
        T[language],
        correction_db=1.34,
        reference_snr_header="Reference SNR (dB)",
    ).decode("utf-8-sig")
    uncorrected_csv = results_export._dataframe_to_csv_bytes(
        source_frame,
        T[language],
        correction_db=0.0,
        reference_snr_header="Reference SNR (dB)",
    ).decode("utf-8-sig")

    assert localized_csv.splitlines()[0] == (
        f"Reference SNR (dB){expected_suffix},Target SNR (dB)"
    )
    assert uncorrected_csv.splitlines()[0] == (
        "Reference SNR (dB),Target SNR (dB)"
    )
    assert list(source_frame.columns) == source_columns


def test_run_metadata_zip_preserves_literal_utf8_and_json_round_trip(
    monkeypatch,
):
    """Keep localized scientific metadata readable without losing JSON fidelity."""
    run_id = 73
    metadata_title = "RX Performance — ΔSNR evidence"
    state = {
        "run_id": run_id,
        results_export.EXPORT_RUN_ID_KEY: run_id,
        results_export.EXPORT_STATE_KEY: {
            "RX_ABS": {
                "analysis_id": "RX_ABS",
                "title": metadata_title,
                "mode_folder": results_export.SUCCESS_EXPORT_FOLDER,
                "database_source": "wspr_live",
                "is_compare": False,
                "is_sequential": False,
                "analysis_kind": "opportunity",
            }
        },
        "lang": "en",
    }
    config_payload = {
        "format": "wspradar.config",
        "schema_version": 1,
        "settings": {},
    }
    monkeypatch.setattr(
        results_export,
        "st",
        SimpleNamespace(session_state=state),
    )
    monkeypatch.setattr(
        results_export,
        "build_config_payload",
        lambda: (
            json.dumps(config_payload).encode("utf-8"),
            "wspradar.config",
        ),
    )
    monkeypatch.setattr(
        results_export,
        "_render_map_png_for_block",
        lambda _block: None,
    )
    monkeypatch.setattr(
        results_export,
        "_render_inspector_png_for_block",
        lambda _block, _figure_name: None,
    )
    monkeypatch.setattr(
        results_export,
        "_build_all_drilldown_for_block",
        lambda _block: pd.DataFrame(),
    )

    zip_bytes, zip_filename = results_export.build_results_zip(T["en"])

    export_root = zip_filename.removesuffix(".zip")
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        raw_metadata = archive.read(
            f"{export_root}/config/run_metadata.json"
        )

    decoded_metadata = raw_metadata.decode("utf-8")
    assert f'"title": "{metadata_title}"' in decoded_metadata
    parsed_metadata = json.loads(decoded_metadata)
    assert parsed_metadata["result_blocks"][0]["title"] == metadata_title


@pytest.mark.parametrize(
    ("figure_name", "renderer_name", "recipe_key", "_segment_name", "_segment_key"),
    SUCCESS_SELECTED_FIGURE_EXPORTS,
)
def test_success_selected_figure_export_dispatches_shared_renderer(
    monkeypatch,
    figure_name,
    renderer_name,
    recipe_key,
    _segment_name,
    _segment_key,
):
    """Dispatch each singleton Success recipe through its shared renderer."""
    recipe = {
        "kind": "opportunity_success_temporal",
        "population_mode": "selected_station",
        "snr_representation": "actual_normalized_snr",
    }
    fake_figure = object()
    renderer_recipes = []
    disposed_figures = []

    monkeypatch.setattr(
        evidence_figures,
        renderer_name,
        lambda received_recipe: (
            renderer_recipes.append(received_recipe) or fake_figure
        ),
    )
    monkeypatch.setattr(
        results_export,
        "figure_to_png_bytes",
        lambda figure, *, paper_theme: (
            b"selected-success-png"
            if figure is fake_figure and paper_theme
            else b""
        ),
    )
    monkeypatch.setattr(
        results_export,
        "dispose_matplotlib_figure",
        disposed_figures.append,
    )

    rendered = results_export._render_inspector_png_for_block(
        {recipe_key: recipe},
        figure_name,
    )

    assert rendered == b"selected-success-png"
    assert renderer_recipes == [recipe]
    assert disposed_figures == [fake_figure]


@pytest.mark.parametrize(
    (
        "figure_name",
        "renderer_name",
        "recipe_key",
        "segment_figure_name",
        "segment_recipe_key",
    ),
    SUCCESS_SELECTED_FIGURE_EXPORTS,
)
def test_success_selected_png_matches_segment_temporal_dimensions_and_aspect(
    monkeypatch,
    figure_name,
    renderer_name,
    recipe_key,
    segment_figure_name,
    segment_recipe_key,
):
    """Keep selected exports physically aligned with their segment counterparts."""
    from core.matplotlib_runtime import create_agg_figure

    selected_recipe = {"population_mode": "selected_station"}
    segment_recipe = {"population_mode": "active_scope"}
    renderer_recipes = []

    def render_temporal_figure(received_recipe):
        """Return the shared temporal canvas while recording recipe routing."""
        renderer_recipes.append(received_recipe)
        return create_agg_figure(
            figsize=evidence_figures.SEGMENT_TEMPORAL_FIGURE_SIZE_INCHES,
            facecolor="black",
        )

    monkeypatch.setattr(
        evidence_figures,
        renderer_name,
        render_temporal_figure,
    )
    block = {
        recipe_key: selected_recipe,
        segment_recipe_key: segment_recipe,
    }

    selected_image_bytes = results_export._render_inspector_png_for_block(
        block,
        figure_name,
    )
    segment_image_bytes = results_export._render_inspector_png_for_block(
        block,
        segment_figure_name,
    )

    assert selected_image_bytes.startswith(b"\x89PNG\r\n\x1a\n")
    assert segment_image_bytes.startswith(b"\x89PNG\r\n\x1a\n")

    def png_dimensions(image_bytes):
        """Return the PNG IHDR width and height in pixels."""
        return (
            int.from_bytes(image_bytes[16:20], byteorder="big"),
            int.from_bytes(image_bytes[20:24], byteorder="big"),
        )

    selected_dimensions = png_dimensions(selected_image_bytes)
    segment_dimensions = png_dimensions(segment_image_bytes)
    assert selected_dimensions == segment_dimensions
    assert (
        selected_dimensions[0] / selected_dimensions[1]
        == pytest.approx(
            segment_dimensions[0] / segment_dimensions[1],
        )
    )
    assert renderer_recipes == [selected_recipe, segment_recipe]


@pytest.mark.parametrize(
    ("figure_name", "renderer_name", "_recipe_key", "_segment_name", "_segment_key"),
    SUCCESS_SELECTED_FIGURE_EXPORTS,
)
def test_success_selected_figure_export_is_absent_without_recipe(
    monkeypatch,
    figure_name,
    renderer_name,
    _recipe_key,
    _segment_name,
    _segment_key,
):
    """Skip every selected-Success PNG safely when no station is selected."""
    def fail_if_called(_recipe):
        raise AssertionError(
            "A selected-Success renderer must not receive a missing recipe."
        )

    monkeypatch.setattr(
        evidence_figures,
        renderer_name,
        fail_if_called,
    )

    assert results_export._render_inspector_png_for_block(
        {},
        figure_name,
    ) is None


def test_success_results_zip_records_selected_figures_and_context(
    monkeypatch,
):
    """Package both singleton Success views without a Compare result family."""
    run_id = 71
    state = {
        "run_id": run_id,
        results_export.EXPORT_RUN_ID_KEY: run_id,
        results_export.EXPORT_STATE_KEY: {},
        "lang": "en",
    }
    config_payload = {
        "format": "wspradar.config",
        "schema_version": 1,
        "settings": {
            "core_parameters": {
                "analysis_direction": "rx",
                "callsign": "TARGET",
                "band": "20m",
                "time_selection": {
                    "start_utc": "2026-07-01T00:00Z",
                    "end_utc": "2026-07-02T00:00Z",
                },
            },
            "comparison_parameters": {"mode": "none"},
            "advanced_parameters": {},
        },
    }
    selected_identities = ["OK1FCX (JN79)"]
    selected_label = "OK1FCX (JN79)"
    selected_context = (
        "OK1FCX (JN79) · 1,173 km · 91° E\n"
        "13,019 confirmed opportunities · Decode Rate 47.6% · "
        "Median Target SNR −15.0 dB"
    )
    figure_descriptions = {
        figure_name: f"{figure_name}: {selected_label}"
        for (
            figure_name,
            _renderer_name,
            _recipe_key,
            _segment_name,
            _segment_key,
        ) in SUCCESS_SELECTED_FIGURE_EXPORTS
    }
    selected_snr_recipe = {
        "kind": "opportunity_success_temporal",
        "population_mode": "selected_station",
        "snr_representation": "actual_normalized_snr",
    }
    selected_temporal_recipe = dict(selected_snr_recipe)

    monkeypatch.setattr(
        results_export,
        "st",
        SimpleNamespace(session_state=state),
    )
    monkeypatch.setattr(
        results_export,
        "build_config_payload",
        lambda: (
            json.dumps(config_payload).encode("utf-8"),
            "wspradar.config",
        ),
    )
    results_export.register_inspector_export(
        analysis_id="RX_ABS",
        selected_segment="Full Range | All Directions",
        selected_distance="Full Range",
        selected_direction="All Directions",
        show_non_joint=False,
        evidence_time_bin="6h",
        selected_stations=selected_identities,
        translations=T["en"],
        selected_station_snr_evidence_figure_recipe=selected_snr_recipe,
        selected_station_temporal_evidence_figure_recipe=(
            selected_temporal_recipe
        ),
        selected_station_label=selected_label,
        selected_station_context_label=selected_context,
        selected_station_role="TX",
        selected_evidence_figure_descriptions=figure_descriptions,
    )
    success_block = state[results_export.EXPORT_STATE_KEY]["RX_ABS"]
    success_block.update(
        {
            "title": "RX Performance",
            "mode_folder": results_export.SUCCESS_EXPORT_FOLDER,
            "database_source": "wspr_live",
            "is_compare": False,
            "is_sequential": False,
            "analysis_kind": "opportunity",
            "success_method_version": "opportunity-v1",
        }
    )
    rendered_figure_names = []
    selected_filenames = {
        figure_name
        for (
            figure_name,
            _renderer_name,
            _recipe_key,
            _segment_name,
            _segment_key,
        ) in SUCCESS_SELECTED_FIGURE_EXPORTS
    }

    def render_inspector_figure(block, figure_name):
        rendered_figure_names.append((block["analysis_id"], figure_name))
        if figure_name in selected_filenames:
            return f"{block['analysis_id']}:{figure_name}".encode("utf-8")
        return None

    monkeypatch.setattr(
        results_export,
        "_render_inspector_png_for_block",
        render_inspector_figure,
    )

    zip_bytes, zip_filename = results_export.build_results_zip(T["en"])

    export_root = zip_filename.removesuffix(".zip")
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        package_paths = set(archive.namelist())
        metadata = json.loads(
            archive.read(f"{export_root}/config/run_metadata.json")
        )

    success_selected_names = [
        figure_name
        for analysis_id, figure_name in rendered_figure_names
        if analysis_id == "RX_ABS"
        and figure_name.startswith("figure_selected_station_")
    ]
    expected_success_names = [
        figure_name
        for (
            figure_name,
            _renderer_name,
            _recipe_key,
            _segment_name,
            _segment_key,
        ) in SUCCESS_SELECTED_FIGURE_EXPORTS
    ]
    assert success_selected_names == expected_success_names
    assert not set(OBSOLETE_SUCCESS_SELECTED_FIGURE_NAMES).intersection(
        success_selected_names
    )
    for figure_name in expected_success_names:
        assert f"{export_root}/success/{figure_name}" in package_paths
        assert f"{export_root}/compare/{figure_name}" not in package_paths
    for figure_name in OBSOLETE_SUCCESS_SELECTED_FIGURE_NAMES:
        assert f"{export_root}/success/{figure_name}" not in package_paths
        assert f"{export_root}/compare/{figure_name}" not in package_paths
    assert (
        f"{export_root}/success/figure_selected_station_evidence.png"
        not in package_paths
    )
    assert metadata["blocks_present"] == {"compare": False, "success": True}

    result_blocks = {
        block["analysis_id"]: block for block in metadata["result_blocks"]
    }
    success_metadata = result_blocks["RX_ABS"]
    assert success_metadata["selected_stations"] == selected_identities
    assert success_metadata["selected_station_label"] == selected_label
    assert success_metadata["selected_station_context"] == selected_context
    assert success_metadata["selected_station_count"] == 1
    assert success_metadata["selected_station_role"] == "TX"
    assert success_metadata["selected_evidence_weighting"] == (
        "Single selected path"
    )
    assert success_metadata["selected_evidence_figures"] == figure_descriptions


def test_compare_results_zip_records_coverage_figures_in_stable_order(
    monkeypatch,
):
    """Package active Compare figures under stable names in presentation order."""
    run_id = 72
    state = {
        "run_id": run_id,
        results_export.EXPORT_RUN_ID_KEY: run_id,
        results_export.EXPORT_STATE_KEY: {},
        "lang": "en",
    }
    config_payload = {
        "format": "wspradar.config",
        "schema_version": 1,
        "settings": {
            "core_parameters": {
                "analysis_direction": "rx",
                "callsign": "TARGET",
                "band": "20m",
                "time_selection": {
                    "start_utc": "2026-07-01T00:00Z",
                    "end_utc": "2026-07-02T00:00Z",
                },
            },
            "comparison_parameters": {"mode": "hardware_ab"},
            "advanced_parameters": {},
        },
    }
    selected_identities = ["OK1FCX (JN79)"]
    selected_recipe = {
        "kind": "selected_compare_temporal",
    }
    coverage_recipes = {
        recipe_key: {
            "kind": (
                compare_evidence_figures.COMPARE_SELECTED_PATH_COVERAGE_RECIPE_KIND
                if recipe_key
                == "selected_station_coverage_figure_recipe"
                else compare_evidence_figures.COMPARE_TEMPORAL_COVERAGE_RECIPE_KIND
            ),
            "schema_version": 1,
            "time_bin": "6h",
            title_key: figure_title,
        }
        for (
            _figure_name,
            _renderer_name,
            recipe_key,
            title_key,
            figure_title,
        ) in COMPARE_COVERAGE_EXPORT_CASES
    }

    monkeypatch.setattr(
        results_export,
        "st",
        SimpleNamespace(session_state=state),
    )
    monkeypatch.setattr(
        results_export,
        "build_config_payload",
        lambda: (
            json.dumps(config_payload).encode("utf-8"),
            "wspradar.config",
        ),
    )
    results_export.register_inspector_export(
        analysis_id="RX_COMPARE",
        selected_segment="Full Range | All Directions",
        selected_distance="Full Range",
        selected_direction="All Directions",
        show_non_joint=False,
        evidence_time_bin="6h",
        selected_stations=selected_identities,
        translations=T["en"],
        selected_evidence_figure_recipe=selected_recipe,
        **coverage_recipes,
    )
    compare_block = state[results_export.EXPORT_STATE_KEY]["RX_COMPARE"]
    compare_block.update(
        {
            "title": "RX Compare",
            "mode_folder": results_export.COMPARE_EXPORT_FOLDER,
            "database_source": "wspr_live",
            "is_compare": True,
            "is_sequential": False,
            "analysis_kind": "comparison",
        }
    )

    rendered_figure_names = []
    packaged_compare_figures = {
        "figure_selected_station_evidence.png",
        *(
            export_case[0]
            for export_case in COMPARE_COVERAGE_EXPORT_CASES
        ),
    }

    def render_inspector_figure(block, figure_name):
        rendered_figure_names.append((block["analysis_id"], figure_name))
        if figure_name in packaged_compare_figures:
            return f"RX_COMPARE:{figure_name}".encode("utf-8")
        return None

    monkeypatch.setattr(
        results_export,
        "_render_inspector_png_for_block",
        render_inspector_figure,
    )

    zip_bytes, zip_filename = results_export.build_results_zip(T["en"])

    export_root = zip_filename.removesuffix(".zip")
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        package_paths = set(archive.namelist())
        metadata = json.loads(
            archive.read(f"{export_root}/config/run_metadata.json")
        )

    compare_figure_names = [
        figure_name
        for analysis_id, figure_name in rendered_figure_names
        if analysis_id == "RX_COMPARE"
    ]
    expected_compare_figure_names = [
        "figure_segment_insight.png",
        "figure_segment_temporal_evidence.png",
        "figure_segment_temporal_coverage.png",
        "figure_selected_station_evidence.png",
        "figure_selected_station_coverage.png",
    ]
    assert compare_figure_names == expected_compare_figure_names
    for figure_name in packaged_compare_figures:
        assert f"{export_root}/compare/{figure_name}" in package_paths
    for (
        success_figure_name,
        _renderer_name,
        _recipe_key,
        _segment_name,
        _segment_key,
    ) in SUCCESS_SELECTED_FIGURE_EXPORTS:
        assert f"{export_root}/compare/{success_figure_name}" not in package_paths
    for obsolete_figure_name in OBSOLETE_SUCCESS_SELECTED_FIGURE_NAMES:
        assert (
            f"{export_root}/compare/{obsolete_figure_name}"
            not in package_paths
        )
    for retired_figure_name, _recipe_key, _renderer_name in (
        RETIRED_COMPARE_FIGURE_EXPORTS
    ):
        assert retired_figure_name not in compare_figure_names
        assert (
            f"{export_root}/compare/{retired_figure_name}"
            not in package_paths
        )
    assert metadata["blocks_present"] == {"compare": True, "success": False}
    assert len(metadata["result_blocks"]) == 1
    compare_metadata = metadata["result_blocks"][0]
    assert compare_metadata["analysis_id"] == "RX_COMPARE"
    assert compare_metadata["folder"] == "compare"
    assert compare_metadata["selected_stations"] == selected_identities
    assert compare_metadata["selected_station_count"] == 1
    assert compare_metadata["selected_evidence_weighting"] == (
        "Single selected path"
    )
    assert compare_metadata["compare_evidence_figures"] == {
        figure_name: figure_title
        for (
            figure_name,
            _renderer_name,
            _recipe_key,
            _title_key,
            figure_title,
        ) in COMPARE_COVERAGE_EXPORT_CASES
    }


def test_success_export_uses_success_folder_and_metadata(tmp_path, monkeypatch):
    """New Success packages must not expose the superseded Absolute name."""
    parquet_path = tmp_path / "success_evidence.parquet"
    parquet_path.write_bytes(b"compact evidence")
    state = {
        "run_id": 17,
        results_export.EXPORT_RUN_ID_KEY: 17,
        results_export.EXPORT_STATE_KEY: {},
        "lang": "en",
        "run_mode": "RX",
    }
    config_payload = {
        "format": "wspradar.config",
        "schema_version": 1,
        "settings": {
            "core_parameters": {
                "analysis_direction": "rx",
                "callsign": "TARGET",
                "band": "20m",
                "time_selection": {
                    "start_utc": "2026-07-01T00:00Z",
                    "end_utc": "2026-07-02T00:00Z",
                },
            },
            "comparison_parameters": {"mode": "none"},
            "advanced_parameters": {"max_peer_distance_km": 10000},
        },
    }
    config_bytes = json.dumps(config_payload).encode("utf-8")

    monkeypatch.setattr(results_export, "st", SimpleNamespace(session_state=state))
    monkeypatch.setattr(
        results_export,
        "build_config_payload",
        lambda: (config_bytes, "wspradar.config"),
    )
    monkeypatch.setattr(results_export.ARTIFACT_STORE, "touch", lambda _path: True)
    monkeypatch.setattr(
        results_export.ARTIFACT_STORE,
        "lease",
        lambda _path: nullcontext(parquet_path),
    )
    results_export.register_map_export_context(
        analysis={
            "id": "RX_ABS",
            "title": "RX Performance",
            "is_compare": False,
            "is_sequential": False,
            "analysis_kind": "opportunity",
            "absolute_method_version": "opportunity-v1",
        },
        parquet_path=str(parquet_path),
        start_t="2026-07-01T00:00:00Z",
        end_t="2026-07-02T00:00:00Z",
        max_peer_distance_km=10000,
        base_min_stations=1,
        lat_0=50.0,
        lon_0=5.0,
        analysis_context=SimpleNamespace(to_dict=lambda: {}),
        presentation_context=SimpleNamespace(
            language="en",
            theme="light",
            solar_label="All",
        ),
        database_source="wd2",
    )
    success_block = state[results_export.EXPORT_STATE_KEY]["RX_ABS"]
    success_block["table_station_insights_current_segment.csv"] = pd.DataFrame(
        {"Peer": ["TEST"]}
    )
    success_block["table_drilldown_selected_stations.csv"] = pd.DataFrame()
    rendered_inspector_names = []

    def render_success_inspector_figure(_block, figure_name):
        rendered_inspector_names.append(figure_name)
        if figure_name == "figure_segment_temporal_snr_deviation.png":
            return b"temporal-snr-png"
        return None

    monkeypatch.setattr(
        results_export,
        "_render_inspector_png_for_block",
        render_success_inspector_figure,
    )

    zip_bytes, zip_filename = results_export.build_results_zip(T["en"])

    export_root = zip_filename.removesuffix(".zip")
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        package_paths = set(archive.namelist())
        metadata = json.loads(
            archive.read(f"{export_root}/config/run_metadata.json")
        )

    assert f"{export_root}/success/analysis_cache.parquet" in package_paths
    assert f"{export_root}/config/wspradar_config.config" in package_paths
    assert f"{export_root}/success/table_station_insights_current_segment.csv" in package_paths
    assert (
        f"{export_root}/success/figure_segment_temporal_snr_deviation.png"
        in package_paths
    )
    assert "figure_segment_temporal_snr_deviation.png" in (
        rendered_inspector_names
    )
    assert rendered_inspector_names.index(
        "figure_segment_temporal_snr_deviation.png"
    ) < rendered_inspector_names.index(
        "figure_segment_temporal_evidence.png"
    )
    assert all("/absolute/" not in path for path in package_paths)
    assert metadata["blocks_present"] == {"compare": False, "success": True}
    assert metadata["database_source"] == "wd2"
    assert (
        metadata["thresholds_and_filters"]["max_peer_distance_km"] == 10000
    )
    assert metadata["result_blocks"][0]["folder"] == "success"
    assert metadata["result_blocks"][0]["success_method_version"] == "opportunity-v1"
    assert "absolute" not in json.dumps(metadata).casefold()


def test_success_map_export_reuses_projected_shared_map_renderer(monkeypatch):
    """Rebuild the light export from the same opportunity map entry point."""
    source_frame = pd.DataFrame(
        {
            "time_slot": [1],
            "peer_sign": ["K1AAA"],
            "peer_grid": ["FN31"],
            "target_seen": [1],
            "target_snr": [-12.0],
            "peer_lat": [41.0],
            "peer_lon": [-72.0],
            "opportunity": [1],
            "hit": [1],
            "miss": [0],
            "target_only": [0],
        }
    )
    read_calls = []
    render_calls = []
    disposed_figures = []
    fake_figure = object()

    monkeypatch.setattr(
        results_export,
        "_parquet_schema_columns",
        lambda _path: set(results_export.OPPORTUNITY_MAP_EXPORT_COLUMNS),
    )

    def fake_read_parquet_artifact(path, *, columns):
        read_calls.append((path, columns))
        return source_frame.loc[:, columns].copy()

    def fake_generate_map_plot(*args, **kwargs):
        render_calls.append((args, kwargs))
        return SimpleNamespace(figure=fake_figure)

    monkeypatch.setattr(
        results_export,
        "read_parquet_artifact",
        fake_read_parquet_artifact,
    )
    monkeypatch.setattr(
        plot_engine,
        "generate_map_plot",
        fake_generate_map_plot,
    )
    monkeypatch.setattr(
        results_export,
        "figure_to_png_bytes",
        lambda figure, *, paper_theme: (
            b"map-png"
            if figure is fake_figure and paper_theme is False
            else b""
        ),
    )
    monkeypatch.setattr(
        results_export,
        "dispose_matplotlib_figure",
        disposed_figures.append,
    )
    analysis_context = AnalysisContext(
        callsign="TARGET",
        qth="JN47",
        band="20m",
    )
    block = {
        "analysis_id": "RX_ABS",
        "title": "RX Performance",
        "is_compare": False,
        "is_sequential": False,
        "analysis_kind": "opportunity",
        "map_context": {
            "parquet_path": "success-evidence.parquet",
            "start_t": "2026-07-01T00:00:00Z",
            "end_t": "2026-07-02T00:00:00Z",
            "max_peer_distance_km": 10000,
            "base_min_stations": 1,
            "lat_0": 50.0,
            "lon_0": 5.0,
            "analysis_context": analysis_context.to_dict(),
            "presentation_context": {
                "language": "en",
                "theme": "dark",
                "solar_label": "All",
            },
        },
    }

    rendered = results_export._render_map_png_for_block(block)

    assert rendered == b"map-png"
    assert read_calls == [
        (
            "success-evidence.parquet",
            list(results_export.OPPORTUNITY_MAP_EXPORT_COLUMNS),
        )
    ]
    assert len(render_calls) == 1
    positional, keyword = render_calls[0]
    assert positional[0].equals(source_frame)
    assert positional[1:4] == ("RX Performance", False, False)
    assert positional[7] == "RX_ABS"
    assert keyword["analysis_kind"] == "opportunity"
    assert keyword["theme"] == "light"
    assert keyword["analysis_context"] == analysis_context
    assert keyword["presentation_context"].language == "en"
    assert keyword["presentation_context"].theme == "dark"
    assert disposed_figures == [fake_figure]
