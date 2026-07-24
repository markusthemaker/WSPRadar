"""Regression contracts for the progressive result-evidence hierarchy."""

from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from string import Formatter
from types import SimpleNamespace

import pytest

from core.analysis_context import (
    COMPARISON_HARDWARE_AB,
    COMPARISON_LOCAL_NEIGHBORHOOD,
    COMPARISON_REFERENCE_STATION,
    LOCAL_BENCHMARK_BEST,
    LOCAL_BENCHMARK_MEDIAN,
)
from i18n import T
from ui.result_hierarchy import (
    ResultContext,
    active_scope_text,
    build_result_context,
    comparison_constraint_text,
    drilldown_subtitle,
    evidence_child_header_html,
    evidence_level_header_html,
    evidence_unit_label,
    remote_station_type,
    result_context_html,
    scope_context_html,
    scope_evidence_text,
    scope_summary_html,
    selected_station_context,
    station_count_label,
    station_scope_text,
    transition_prompt_html,
    utility_header_html,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


RESULT_TRANSLATION_PREFIXES = (
    "hdr_results_",
    "sub_results_",
    "txt_results_",
    "lbl_results_level_",
    "unit_",
    "fmt_results_",
)

EXPECTED_RESULT_TRANSLATION_KEYS = {
    "hdr_results_compare",
    "hdr_results_success",
    "hdr_results_map_view",
    "hdr_results_segment_inspector",
    "hdr_results_comparison_evidence",
    "hdr_results_temporal_evidence",
    "hdr_results_success_temporal",
    "hdr_results_selected_station_evidence",
    "hdr_results_drilldown",
    "hdr_results_download_evidence",
    "hdr_results_reusable_configuration",
    "sub_results_compare",
    "sub_results_compare_scheduled",
    "sub_results_rx_success",
    "sub_results_tx_success",
    "sub_results_map_compare",
    "sub_results_map_success",
    "sub_results_segment_inspector",
    "sub_results_comparison_evidence_joint",
    "sub_results_comparison_evidence_scheduled",
    "fmt_results_station_delta_summary",
    "fmt_results_joint_spot_delta_summary",
    "fmt_results_scheduled_pair_delta_summary",
    "sub_results_temporal_evidence",
    "sub_results_success_temporal",
    "sub_results_station_insights",
    "sub_results_selected_station_single",
    "sub_results_selected_station_multi",
    "sub_results_drilldown_single",
    "sub_results_drilldown_multi",
    "sub_results_download_evidence",
    "txt_results_metadata",
    "txt_results_reference_grid4",
    "txt_results_shared_grid4",
    "txt_results_reference_benchmark",
    "txt_results_tx_schedule",
    "txt_results_evidence_path",
    "txt_results_active_scope",
    "txt_results_evidence_scope",
    "txt_results_selected_no_paired_evidence",
    "txt_results_transition_scope",
    "txt_results_transition_stations",
    "txt_results_transition_rows",
    "txt_results_station_scope",
    "txt_results_drilldown_filter_note",
    "lbl_results_level_run",
    "lbl_results_level_scope",
    "lbl_results_level_stations",
    "lbl_results_level_selection",
    "lbl_results_level_rows",
    "unit_joint_spot_singular",
    "unit_joint_spot_plural",
    "unit_scheduled_pair_singular",
    "unit_scheduled_pair_plural",
    "unit_confirmed_opportunity_singular",
    "unit_confirmed_opportunity_plural",
    "unit_station_singular",
    "unit_station_plural",
    "fmt_results_thousands_separator",
}


class _HeadingCollector(HTMLParser):
    """Collect semantic heading tags from one generated HTML fragment."""

    def __init__(self):
        super().__init__()
        self.heading_tags = []

    def handle_starttag(self, tag, _attrs):
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.heading_tags.append(tag)


def _heading_tags(markup):
    parser = _HeadingCollector()
    parser.feed(markup)
    return parser.heading_tags


def _format_fields(template):
    return {
        field_name
        for _literal, field_name, _format_spec, _conversion in Formatter().parse(
            template
        )
        if field_name
    }


def _result_translation_keys(language):
    return {
        key
        for key in T[language]
        if key.startswith(RESULT_TRANSLATION_PREFIXES)
    }


@pytest.mark.parametrize("language", ("en", "de"))
@pytest.mark.parametrize(
    ("analysis_id", "is_compare", "result_title_key", "success_subtitle_key"),
    (
        ("RX_COMP", True, "hdr_results_compare", None),
        ("TX_COMP", True, "hdr_results_compare", None),
        ("RX_ABS", False, "hdr_results_success", "sub_results_rx_success"),
        ("TX_ABS", False, "hdr_results_success", "sub_results_tx_success"),
    ),
)
def test_result_context_titles_and_subtitles_cover_every_analysis_family(
    language,
    analysis_id,
    is_compare,
    result_title_key,
    success_subtitle_key,
):
    """Keep the result identity dynamic while preserving localized run context."""
    direction = analysis_id.split("_", 1)[0]
    comparison_context = (
        f"{direction}-TARGET (Target) vs. {direction}-REFERENCE (Reference)"
    )
    analysis = {
        "id": analysis_id,
        "is_compare": is_compare,
        "is_sequential": False,
        "title": f"{direction} Compare: {comparison_context}",
    }
    analysis_context = SimpleNamespace(
        callsign=f"{direction.lower()}-target",
        band="20m",
        qth="jo62qm",
    )
    start_utc = datetime(2026, 7, 1, 1, 2)
    end_utc = datetime(2026, 7, 2, 3, 4)

    context = build_result_context(
        analysis,
        analysis_context,
        start_utc,
        end_utc,
        T[language],
    )

    assert context.title == T[language][result_title_key].format(
        direction=direction
    )
    if is_compare:
        assert context.subtitle == comparison_context
    else:
        assert context.subtitle == T[language][success_subtitle_key].format(
            callsign=f"{direction}-TARGET"
        )
    utc_window = "2026-07-01 01:02 – 2026-07-02 03:04 UTC"
    assert context.metadata == T[language]["txt_results_metadata"].format(
        band="20m",
        utc_window=utc_window,
        qth="JO62QM",
    )
    assert context.evidence_path_label == T[language][
        "lbl_results_evidence_path"
    ]
    assert context.evidence_path == T[language]["txt_results_evidence_path"]


@pytest.mark.parametrize("language", ("en", "de"))
@pytest.mark.parametrize("analysis_id", ("RX_COMP", "TX_COMP"))
def test_scheduled_compare_uses_dynamic_callsign_and_schedule_subtitle(
    language,
    analysis_id,
):
    """Distinguish scheduled Compare evidence from simultaneous station pairs."""
    direction = analysis_id.split("_", 1)[0]
    context = build_result_context(
        {
            "id": analysis_id,
            "is_compare": True,
            "is_sequential": True,
            "title": "unused scheduled figure title",
        },
        SimpleNamespace(callsign="g3zil", band="20m", qth="io90"),
        datetime(2026, 7, 1),
        datetime(2026, 7, 2),
        T[language],
    )

    assert context.title == T[language]["hdr_results_compare"].format(
        direction=direction
    )
    assert context.subtitle == T[language][
        "sub_results_compare_scheduled"
    ].format(callsign="G3ZIL")


@pytest.mark.parametrize("language", ("en", "de"))
@pytest.mark.parametrize("analysis_id", ("RX_COMP", "TX_COMP"))
def test_fixed_reference_grid4_is_part_of_compare_metadata(
    language,
    analysis_id,
):
    """Expose the exact configured Reference Grid-4 beside run provenance."""
    context = build_result_context(
        {
            "id": analysis_id,
            "is_compare": True,
            "is_sequential": False,
            "title": "Compare: Target vs. Reference",
        },
        SimpleNamespace(
            callsign="g3zil",
            band="160m",
            qth="jo20ot",
            comparison_mode=COMPARISON_REFERENCE_STATION,
            reference_qth="jn37",
        ),
        datetime(2021, 5, 1, 17, 15),
        datetime(2021, 5, 15, 7, 0),
        T[language],
    )

    expected_constraint = T[language]["txt_results_reference_grid4"].format(
        grid4="JN37"
    )
    assert context.metadata.endswith(f"· {expected_constraint}")
    assert "JO20OT" in context.metadata


@pytest.mark.parametrize("language", ("en", "de"))
@pytest.mark.parametrize(
    ("local_benchmark", "benchmark_key"),
    (
        (LOCAL_BENCHMARK_MEDIAN, "comp_title_local_median"),
        (LOCAL_BENCHMARK_BEST, "comp_title_local_best"),
    ),
)
def test_local_compare_metadata_names_the_benchmark_and_radius(
    language,
    local_benchmark,
    benchmark_key,
):
    """Describe the active local reference without inventing a single Grid-4."""
    translations = T[language]
    constraint = comparison_constraint_text(
        {
            "id": "RX_COMP",
            "is_compare": True,
            "is_sequential": False,
        },
        SimpleNamespace(
            comparison_mode=COMPARISON_LOCAL_NEIGHBORHOOD,
            local_benchmark=local_benchmark,
            neighborhood_radius_km=200,
        ),
        translations,
    )
    benchmark = translations[benchmark_key].format(radius=200)

    assert constraint == translations[
        "txt_results_reference_benchmark"
    ].format(benchmark=benchmark)
    assert "Grid-4" not in constraint


@pytest.mark.parametrize("language", ("en", "de"))
def test_hardware_compare_metadata_uses_shared_target_grid_and_active_schedule(
    language,
):
    """Use Target Grid-4 for Hardware A/B and expose only an active schedule."""
    translations = T[language]
    analysis_context = SimpleNamespace(
        qth="jo20ot",
        reference_qth="zz99",
        comparison_mode=COMPARISON_HARDWARE_AB,
        tx_ab_repeat_interval_minutes=10,
        tx_ab_target_start_minute=0,
        tx_ab_reference_start_minute=2,
    )
    simultaneous = comparison_constraint_text(
        {
            "id": "TX_COMP",
            "is_compare": True,
            "is_sequential": False,
        },
        analysis_context,
        translations,
    )
    sequential = comparison_constraint_text(
        {
            "id": "TX_COMP",
            "is_compare": True,
            "is_sequential": True,
        },
        analysis_context,
        translations,
    )
    success = comparison_constraint_text(
        {
            "id": "TX_ABS",
            "is_compare": False,
            "is_sequential": False,
        },
        analysis_context,
        translations,
    )

    shared_grid = translations["txt_results_shared_grid4"].format(
        grid4="JO20"
    )
    schedule = translations["txt_results_tx_schedule"].format(
        interval=10,
        target_phase="00",
        reference_phase="02",
    )
    assert simultaneous == shared_grid
    assert "ZZ99" not in simultaneous
    assert sequential == f"{shared_grid} · {schedule}"
    assert success == ""


@pytest.mark.parametrize("language", ("en", "de"))
@pytest.mark.parametrize(
    ("analysis_id", "expected_station_type"),
    (
        ("RX_COMP", "TX"),
        ("RX_ABS", "TX"),
        ("TX_COMP", "RX"),
        ("TX_ABS", "RX"),
    ),
)
def test_scope_copy_preserves_remote_station_role_and_selection_depth(
    language,
    analysis_id,
    expected_station_type,
):
    """Accumulate geographic, station, selection, and row scope without ambiguity."""
    translations = T[language]
    distance = "500–1,000 km"
    direction = "NE + E"
    identities = ["G3AAA (IO90)", "G4BBB (JO01)"]

    assert remote_station_type(analysis_id) == expected_station_type
    assert active_scope_text(distance, direction, translations) == translations[
        "txt_results_active_scope"
    ].format(distance=distance, direction=direction)

    for count, station_unit_key in (
        (1, "unit_station_singular"),
        (2, "unit_station_plural"),
    ):
        station_count = translations[station_unit_key].format(
            count=count,
            station_type=expected_station_type,
        )
        assert station_count_label(
            count,
            expected_station_type,
            translations,
        ) == station_count
        assert station_scope_text(
            distance,
            direction,
            count,
            analysis_id,
            translations,
        ) == translations["txt_results_station_scope"].format(
            distance=distance,
            direction=direction,
            station_count=station_count,
        )

    selected_single = selected_station_context(
        identities[:1],
        1,
        analysis_id=analysis_id,
        is_compare=analysis_id.endswith("_COMP"),
        is_sequential=False,
        translations=translations,
    )
    expected_single_unit_key = (
        "unit_joint_spot_singular"
        if analysis_id.endswith("_COMP")
        else "unit_confirmed_opportunity_singular"
    )
    assert selected_single == translations[
        "sub_results_selected_station_single"
    ].format(
        station="G3AAA",
        locator="IO90",
        evidence_count=1,
        evidence_unit=translations[expected_single_unit_key],
    )

    selected_multi = selected_station_context(
        identities,
        2,
        analysis_id=analysis_id,
        is_compare=analysis_id.endswith("_COMP"),
        is_sequential=False,
        translations=translations,
    )
    expected_multi_unit_key = (
        "unit_joint_spot_plural"
        if analysis_id.endswith("_COMP")
        else "unit_confirmed_opportunity_plural"
    )
    assert selected_multi == translations[
        "sub_results_selected_station_multi"
    ].format(
        selected_count=2,
        station_type=expected_station_type,
        evidence_count=2,
        evidence_unit=translations[expected_multi_unit_key],
    )

    assert drilldown_subtitle(
        identities[:1],
        analysis_id,
        translations,
    ) == translations["sub_results_drilldown_single"].format(
        station=identities[0]
    )
    assert drilldown_subtitle(
        identities,
        analysis_id,
        translations,
    ) == translations["sub_results_drilldown_multi"].format(
        count=2,
        station_type=expected_station_type,
    )


@pytest.mark.parametrize("language", ("en", "de"))
@pytest.mark.parametrize(
    ("is_compare", "is_sequential", "unit_name"),
    (
        (True, False, "joint_spot"),
        (True, True, "scheduled_pair"),
        (False, False, "confirmed_opportunity"),
    ),
)
@pytest.mark.parametrize(
    ("count", "plurality"),
    ((1, "singular"), (2, "plural")),
)
def test_evidence_units_distinguish_compare_scheduled_and_success(
    language,
    is_compare,
    is_sequential,
    unit_name,
    count,
    plurality,
):
    """Use the evidence unit owned by each scientific result family."""
    assert evidence_unit_label(
        count,
        is_compare=is_compare,
        is_sequential=is_sequential,
        translations=T[language],
    ) == T[language][f"unit_{unit_name}_{plurality}"]


@pytest.mark.parametrize("language", ("en", "de"))
@pytest.mark.parametrize(
    ("analysis_id", "is_compare", "is_sequential", "unit_key"),
    (
        ("RX_COMP", True, False, "unit_joint_spot_plural"),
        ("TX_COMP", True, True, "unit_scheduled_pair_plural"),
        ("RX_ABS", False, False, "unit_confirmed_opportunity_plural"),
        ("TX_ABS", False, False, "unit_confirmed_opportunity_plural"),
    ),
)
def test_scope_evidence_summary_is_mode_aware_and_localizes_counts(
    language,
    analysis_id,
    is_compare,
    is_sequential,
    unit_key,
):
    """Keep factual evidence depth readable without changing count ownership."""
    translations = T[language]
    grouped_evidence_count = "5,374" if language == "en" else "5.374"
    station_type = "TX" if analysis_id.startswith("RX") else "RX"
    expected_station_count = translations["unit_station_plural"].format(
        count="59",
        station_type=station_type,
    )

    assert scope_evidence_text(
        59,
        5374,
        analysis_id=analysis_id,
        is_compare=is_compare,
        is_sequential=is_sequential,
        translations=translations,
    ) == translations["txt_results_evidence_scope"].format(
        station_count=expected_station_count,
        evidence_count=grouped_evidence_count,
        evidence_unit=translations[unit_key],
    )


def test_result_html_uses_semantic_heading_levels():
    """Expose the visual hierarchy as H2, H3, and H4 document structure."""
    context_markup = result_context_html(
        ResultContext(
            title="RX Compare Results",
            subtitle="Target vs. Reference",
            metadata="20m · UTC",
            evidence_path_label="Evidence path",
            evidence_path="Map → Drill-Down",
        )
    )
    level_markup = evidence_level_header_html(
        2,
        "Geographic scope",
        "Segment Inspector",
        "Choose a scope.",
        "Active scope · Full Range · All Directions",
    )
    child_markup = evidence_child_header_html(
        "Comparison Evidence",
        "Decode Outcomes and ΔSNR.",
    )
    utility_markup = utility_header_html(
        "Download Evidence",
        "Prepare a reproducibility package.",
    )

    assert _heading_tags(context_markup) == ["h2"]
    assert _heading_tags(level_markup) == ["h3"]
    assert _heading_tags(child_markup) == ["h4"]
    assert _heading_tags(utility_markup) == ["h3"]
    assert "02 · GEOGRAPHIC SCOPE" not in level_markup
    assert (
        "aria-label='02 · Geographic scope: Segment Inspector'"
        in level_markup
    )
    assert "result-evidence-level-02" in level_markup
    assert "data-evidence-level='2'" in level_markup
    scope_markup = scope_summary_html(
        "Active scope",
        "Evidence in scope",
    )
    assert "result-scope-summary" in scope_markup
    assert scope_markup.count("result-scope-context-data") == 2
    assert scope_markup.index("Active scope") < scope_markup.index(
        "Evidence in scope"
    )


def test_dynamic_result_values_are_escaped_at_the_html_boundary():
    """Treat callsigns, figure titles, scope, and station identities as text."""
    callsign = "<call&sign>"
    scheduled_context = build_result_context(
        {
            "id": "RX_COMP",
            "is_compare": True,
            "is_sequential": True,
            "title": "RX Compare: ignored",
        },
        SimpleNamespace(callsign=callsign, band="<20m>", qth='io"90'),
        datetime(2026, 7, 1),
        datetime(2026, 7, 2),
        T["en"],
    )
    scheduled_markup = result_context_html(scheduled_context)
    assert callsign not in scheduled_markup
    assert "&lt;CALL&amp;SIGN&gt;" in scheduled_markup
    assert "&lt;20m&gt;" in scheduled_markup
    assert "IO&quot;90" in scheduled_markup

    malicious_title = "<img src=x onerror=alert(1)>"
    compare_context = build_result_context(
        {
            "id": "TX_COMP",
            "is_compare": True,
            "is_sequential": False,
            "title": f"TX Compare: {malicious_title}",
        },
        SimpleNamespace(callsign="target", band="20m", qth="JO62"),
        datetime(2026, 7, 1),
        datetime(2026, 7, 2),
        T["en"],
    )
    compare_markup = result_context_html(compare_context)
    assert malicious_title not in compare_markup
    assert "&lt;img src=x onerror=alert(1)&gt;" in compare_markup

    raw_distance = "<500 & 1000 km>"
    raw_direction = '"NE" <script>'
    scope = active_scope_text(raw_distance, raw_direction, T["en"])
    scope_markup = scope_context_html(scope)
    assert raw_distance not in scope_markup
    assert raw_direction not in scope_markup
    assert "&lt;500 &amp; 1000 km&gt;" in scope_markup
    assert "&quot;NE&quot; &lt;script&gt;" in scope_markup

    station_identity = "DL1' onclick='bad (J<90)"
    station_context = selected_station_context(
        [station_identity],
        1,
        analysis_id="RX_COMP",
        is_compare=True,
        is_sequential=False,
        translations=T["en"],
    )
    station_markup = evidence_level_header_html(
        4,
        "Selected stations",
        "Selected Station Evidence",
        station_context,
    )
    assert station_identity not in station_markup
    assert "DL1&#x27; onclick=&#x27;bad" in station_markup
    assert "J&lt;90" in station_markup

    prompt_markup = transition_prompt_html("↓ Review <underlying & rows>")
    assert "<underlying & rows>" not in prompt_markup
    assert "&lt;underlying &amp; rows&gt;" in prompt_markup


def test_result_translation_keys_have_english_german_placeholder_parity():
    """Keep every result-hierarchy template structurally interchangeable."""
    english_keys = _result_translation_keys("en")
    german_keys = _result_translation_keys("de")

    assert EXPECTED_RESULT_TRANSLATION_KEYS <= english_keys
    assert english_keys == german_keys
    for key in sorted(english_keys):
        assert isinstance(T["en"][key], str)
        assert isinstance(T["de"][key], str)
        assert _format_fields(T["en"][key]) == _format_fields(T["de"][key]), key


def test_map_and_deferred_inspector_share_one_progressive_flow_container():
    """Keep the map heading, figure, transition, and Inspector in visual order."""
    source = (REPOSITORY_ROOT / "ui" / "run_controller.py").read_text(
        encoding="utf-8"
    )
    result_start = source.index("result_context = build_result_context(")
    result_flow = source[result_start:]

    assert (
        result_flow.index('key=f"results_evidence_flow_')
        < result_flow.index('key=f"results_evidence_spine_')
        < result_flow.index('f"results_evidence_level_1_"')
        < result_flow.index("evidence_level_header_html(\n                            1,")
        < result_flow.index("render_matplotlib_figure(")
        < result_flow.index("transition_prompt_html(")
        < result_flow.index("inspector_container = st.container()")
    )
    assert "hdr_results_stations_spots" not in result_flow
    assert "sub_results_stations_spots" not in result_flow


def test_run_is_complete_only_after_deferred_inspectors_finish():
    """Do not publish a terminal status while result sections still render."""
    source = (REPOSITORY_ROOT / "ui" / "run_controller.py").read_text(
        encoding="utf-8"
    )
    result_start = source.index("deferred_render_data = []")
    result_flow = source[result_start:]

    inspector_render_index = result_flow.index("render_segment_inspector(")
    complete_status_index = result_flow.index(
        'status_box.update(label="Complete"'
    )

    assert inspector_render_index < complete_status_index


def test_segment_heading_precedes_accessibly_labelled_scope_selectors():
    """Explain the narrowing step before compact, accessibly named controls."""
    source = (
        REPOSITORY_ROOT / "ui" / "components" / "segment_inspector.py"
    ).read_text(encoding="utf-8")
    body_start = source.index("def _render_segment_inspector_body(")
    body = source[body_start:]

    heading_index = body.index('"hdr_results_segment_inspector"')
    level_two_index = body.index('f"results_evidence_level_2_')
    distance_selector_index = body.index(
        "selected_distance_values = st.multiselect("
    )
    direction_selector_index = body.index(
        "selected_direction_values = st.multiselect("
    )

    assert (
        level_two_index
        < heading_index
        < distance_selector_index
        < direction_selector_index
    )
    distance_selector = body[
        distance_selector_index:direction_selector_index
    ]
    direction_selector = body[
        direction_selector_index:body.index(
            "selected_directions = _canonical_specific_selection("
        )
    ]
    assert 'placeholder=lbl_dist' in distance_selector
    assert 'label_visibility="collapsed"' in distance_selector
    assert 'placeholder=lbl_dir' in direction_selector
    assert 'label_visibility="collapsed"' in direction_selector


def test_loading_scope_selectors_also_hide_redundant_visible_labels():
    """Keep the deferred loading state aligned with the live compact controls."""
    source = (REPOSITORY_ROOT / "ui" / "run_controller.py").read_text(
        encoding="utf-8"
    )
    loading_scope_start = source.index("with skeleton_ph.container():")
    loading_scope = source[
        loading_scope_start:source.index(
            "deferred_render_data.append(",
            loading_scope_start,
        )
    ]

    distance_selector_start = loading_scope.index(
        'key=f"w_dist_'
    )
    direction_selector_start = loading_scope.index(
        'key=f"w_dir_'
    )
    distance_selector = loading_scope[
        distance_selector_start:direction_selector_start
    ]
    direction_selector = loading_scope[direction_selector_start:]

    assert 'label_visibility="collapsed"' in distance_selector
    assert 'label_visibility="collapsed"' in direction_selector


def test_active_scope_and_evidence_share_one_compact_markup_block():
    """Keep inherited scope and its evidence total visually inseparable."""
    source = (
        REPOSITORY_ROOT / "ui" / "components" / "segment_inspector.py"
    ).read_text(encoding="utf-8")
    body_start = source.index("def _render_segment_inspector_body(")
    body = source[body_start:]

    active_scope_index = body.index(
        "active_scope_summary = active_scope_text("
    )
    placeholder_index = body.index(
        "scope_summary_placeholder = level_two_container.empty()"
    )
    initial_markup_index = body.index(
        "scope_summary_html(active_scope_summary)"
    )

    assert (
        active_scope_index
        < placeholder_index
        < initial_markup_index
    )


def test_scope_evidence_precedes_compare_and_success_figure_groups():
    """Show quantitative depth immediately after scope, before interpretation."""
    source = (
        REPOSITORY_ROOT / "ui" / "components" / "segment_inspector.py"
    ).read_text(encoding="utf-8")

    opportunity_start = source.index("def _render_opportunity_scope(")
    opportunity_end = source.index("def _render_segment_inspector_body(")
    opportunity_body = source[opportunity_start:opportunity_end]
    assert (
        opportunity_body.index("scope_summary_placeholder.markdown(")
        < opportunity_body.index('"hdr_results_success_temporal"')
    )

    inspector_body = source[opportunity_end:]
    compare_start = inspector_body.index("comparison_subtitle_key =")
    compare_body = inspector_body[compare_start:]
    assert (
        compare_body.index("scope_summary_placeholder.markdown(")
        < compare_body.index('"hdr_results_comparison_evidence"')
    )
    assert inspector_body.count('f"results_evidence_level_3_') == 1
    assert inspector_body.count('f"results_evidence_level_4_') == 1
    assert inspector_body.count('f"results_evidence_level_5_') == 1
    assert opportunity_body.count('f"results_evidence_level_3_') == 1
    assert opportunity_body.count('f"results_evidence_level_4_') == 1
    assert opportunity_body.count('f"results_evidence_level_5_') == 1
