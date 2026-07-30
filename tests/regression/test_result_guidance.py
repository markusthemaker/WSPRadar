"""Focused regression contracts for result interpretation popovers."""

import ast
from collections import Counter
from pathlib import Path
import re
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
from i18n import GUIDED_INPUTS, RESULT_GUIDANCE, T
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
    RESULT_GUIDANCE_TEMPORAL_EVIDENCE,
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


def _plain_guidance(guidance):
    """Remove catalog-authored semantic term tags for wording assertions."""
    return re.sub(r"</?strong(?:\s+[^>]*)?>", "", guidance)


def _build_guidance(
    section_id,
    *,
    language="en",
    analysis_id="RX_COMP",
    is_compare=True,
    is_sequential=False,
    analysis_context=None,
    selected_station_count=None,
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
        selected_station_count=selected_station_count,
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
                "station_counter",
                "station_target",
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
            assert len(section_content["limits"]) < len(
                section_content["read"]
            ), (language, section_key)
            if section_key != "drilldown_local_median":
                assert 'class="defined-term"' in section_content["read"], (
                    language,
                    section_key,
                )


@pytest.mark.parametrize(
    ("catalog_name", "catalog"),
    (
        ("translations", T),
        ("result_guidance", RESULT_GUIDANCE),
        ("guided_inputs", GUIDED_INPUTS),
    ),
)
def test_user_visible_catalogs_separate_em_dashes_from_words(
    catalog_name,
    catalog,
):
    """Prevent the global monospace theme from turning prose dashes into joins."""
    for path, catalog_value in _flatten_catalog(catalog).items():
        if not isinstance(catalog_value, str):
            continue
        assert re.search(r"(?<!\s)—|—(?!\s)", catalog_value) is None, (
            catalog_name,
            path,
        )


def test_retired_compare_view_localization_and_guidance_are_absent():
    """Do not retain copy for removed Compare figures or dead aliases."""
    retired_guidance_names = {
        "en": (
            "ΔSNR Change from Station Baseline",
            "Path Agreement and Within-Path Consistency",
        ),
        "de": (
            "ΔSNR-Änderung gegenüber der Stationsbasislinie",
            "Übereinstimmung und Konsistenz der Funkwege",
        ),
    }

    for language in ("en", "de"):
        assert not any(
            key.startswith("fig_compare_delta_change_")
            for key in T[language]
        )
        assert not any(
            key.startswith("fig_compare_path_consistency_")
            for key in T[language]
        )
        assert "fig_compare_coverage_unavailable" not in T[language]
        assert (
            "fig_selected_compare_coverage_utc_hour_subtitle"
            not in T[language]
        )
        complete_guidance = " ".join(
            text
            for section in RESULT_GUIDANCE[language]["sections"].values()
            for text in section.values()
        )
        for retired_name in retired_guidance_names[language]:
            assert retired_name not in complete_guidance


@pytest.mark.parametrize(
    "section_key",
    (
        "temporal_evidence_joint",
        "temporal_evidence_scheduled",
        "selected_compare_joint",
        "selected_compare_scheduled",
    ),
)
def test_compare_temporal_and_selected_guidance_uses_full_readability_budget(
    section_key,
):
    """Keep detailed Compare help within the agreed catalog-copy budget."""
    for language in ("en", "de"):
        item = RESULT_GUIDANCE[language]["sections"][section_key]
        copy_count = len(item["read"]) + len(item["limits"])
        assert 1200 <= copy_count <= 1500, (
            language,
            section_key,
            copy_count,
        )


def test_selected_compare_guidance_names_the_rendered_coverage_units():
    """Keep selected-path help aligned with simultaneous and scheduled plots."""
    expected_copy = {
        "en": {
            "selected_compare_joint": (
                "Retained WSPR Cycles",
                "per represented UTC date",
            ),
            "selected_compare_scheduled": (
                "Scheduled A/B Pairs",
                "per represented UTC date",
            ),
        },
        "de": {
            "selected_compare_joint": (
                "Berücksichtigte WSPR-Zyklen",
                "je berücksichtigtem UTC-Tag",
            ),
            "selected_compare_scheduled": (
                "Geplante A/B-Paare",
                "je berücksichtigtem UTC-Tag",
            ),
        },
    }

    for language, section_contracts in expected_copy.items():
        sections = RESULT_GUIDANCE[language]["sections"]
        for section_key, required_phrases in section_contracts.items():
            combined = " ".join(sections[section_key].values())
            for required_phrase in required_phrases:
                assert required_phrase in combined


def test_joint_temporal_guidance_explains_the_figures_and_target_favored_gate():
    """Make simultaneous temporal evidence interpretable without the manual."""
    english_temporal = RESULT_GUIDANCE["en"]["sections"][
        "temporal_evidence_joint"
    ]
    english_selected = RESULT_GUIDANCE["en"]["sections"][
        "selected_compare_joint"
    ]
    german_temporal = RESULT_GUIDANCE["de"]["sections"][
        "temporal_evidence_joint"
    ]
    german_selected = RESULT_GUIDANCE["de"]["sections"][
        "selected_compare_joint"
    ]

    english_temporal_text = " ".join(english_temporal.values())
    english_selected_text = " ".join(english_selected.values())
    german_temporal_text = " ".join(german_temporal.values())
    german_selected_text = " ".join(german_selected.values())

    for expected in (
        "not |ΔSNR|",
        "median of all Joint Spots",
        "per-panel relative Joint-Spot density",
        "nonlinear axis",
        "one split vote",
        "blue line",
        "amber line",
        "A gap between lines shows volume weighting",
        "Target activity",
        "no equivalent gate",
        "favor Target",
        "gate does not alter Joint ΔSNR",
        "every Joint Spot contains both sides",
    ):
        assert expected in english_temporal_text

    for expected in (
        "one chosen {peer_type} station",
        "one specific radio path",
        "only Joint units supply ΔSNR",
        "RX: Target decoded a qualifying signal",
        "TX: Target was decoded somewhere",
        "Reference has no equivalent gate",
        "One-sided counts favor Target",
        "Swapping roles can change coverage",
        "paired values reverse sign",
        "gate cannot alter Joint evidence",
    ):
        assert expected in english_selected_text

    for expected in (
        "nicht |ΔSNR|",
        "Median aller Joint Spots",
        "relative Joint-Spot-Dichte je Panel",
        "Achsabstände sind nichtlinear",
        "aufgeteilte Stimme",
        "blaue Linie",
        "gelbe Linie",
        "Target-Aktivität",
        "kein gleichwertiges Aktivitäts-Gate",
        "Target-begünstigt",
        "Gate verändert Joint-ΔSNR nicht",
        "jeder Joint Spot beide Seiten enthält",
    ):
        assert expected in german_temporal_text

    for expected in (
        "eine gewählte {peer_type}-Station",
        "nur Joint liefert ΔSNR",
        "RX: Target decodierte ein qualifizierendes Signal",
        "TX: Target wurde irgendwo gehört",
        "Kein Referenz-Gate",
        "Target-begünstigt",
        "Rollentausch kann einseitige Abdeckung ändern",
        "gepaarte Werte wechseln Vorzeichen",
        "Gate ändert Joint-Evidenz nicht",
    ):
        assert expected in german_selected_text


@pytest.mark.parametrize(
    ("language", "over_time", "by_hour", "retired_over_time"),
    (
        (
            "en",
            "Δ SNR over Time",
            "Δ SNR by UTC Hour",
            "Pair Δ SNR over Time",
        ),
        (
            "de",
            "Δ SNR im Zeitverlauf",
            "Δ SNR nach UTC-Stunde",
            "Paar-ΔSNR im Zeitverlauf",
        ),
    ),
)
def test_scheduled_temporal_guidance_matches_rendered_titles_and_pair_limits(
    language,
    over_time,
    by_hour,
    retired_over_time,
):
    """Explain scheduled evidence without inventing different panel titles."""
    sections = RESULT_GUIDANCE[language]["sections"]
    for section_key in (
        "temporal_evidence_scheduled",
        "selected_compare_scheduled",
    ):
        combined = " ".join(sections[section_key].values())
        assert over_time in combined
        assert by_hour in combined
        assert retired_over_time not in combined

    combined = " ".join(
        sections[section_key][field]
        for section_key in (
            "temporal_evidence_scheduled",
            "selected_compare_scheduled",
        )
        for field in ("read", "limits")
    )
    if language == "en":
        for expected in (
            "configured planned pairs",
            "not the simultaneous Target-Active Gate",
            "Pair ΔSNR exists only when both scheduled sides were decoded",
            "missing-side SNR",
            "time-separated",
        ):
            assert expected in combined
    else:
        for expected in (
            "konfigurierte geplante Paare",
            "statt des Target-Active Gate des simultanen Modus",
            "Paar-ΔSNR existiert nur, wenn beide geplanten Seiten decodiert wurden",
            "SNR der fehlenden Seite",
            "zeitlich getrennt",
        ):
            assert expected in combined


def test_directional_success_temporal_guidance_stays_near_readability_target():
    """Allow modest overruns of the approximate 2,000-character target."""
    for language in ("en", "de"):
        for direction in ("rx", "tx"):
            item = RESULT_GUIDANCE[language]["sections"][
                f"success_temporal_evidence_{direction}"
            ]
            assert len(item["read"]) + len(item["limits"]) <= 2300


@pytest.mark.parametrize(
    (
        "language",
        "analysis_id",
        "direction",
        "success_outcome",
        "counter_outcome",
        "snr_figure_name",
        "temporal_figure_name",
        "replacement_wording",
    ),
    (
        (
            "en",
            "RX_ABS",
            "rx",
            "Heard by Target",
            "Heard by others only",
            "Selected Station SNR Evidence",
            "Selected Station Temporal Evidence",
            "replaces the current station",
        ),
        (
            "en",
            "TX_ABS",
            "tx",
            "Target heard",
            "Other signals heard only",
            "Selected Station SNR Evidence",
            "Selected Station Temporal Evidence",
            "replaces the current receiver",
        ),
        (
            "de",
            "RX_ABS",
            "rx",
            "Vom Target gehört",
            "Nur von anderen gehört",
            "SNR-Evidenz der ausgewählten Station",
            "Zeitliche Evidenz der ausgewählten Station",
            "ersetzt die bisherige Station",
        ),
        (
            "de",
            "TX_ABS",
            "tx",
            "Target gehört",
            "Nur andere Signale gehört",
            "SNR-Evidenz der ausgewählten Station",
            "Zeitliche Evidenz der ausgewählten Station",
            "ersetzt den bisher ausgewählten Empfänger",
        ),
    ),
)
def test_success_selected_guidance_routes_one_station(
    language,
    analysis_id,
    direction,
    success_outcome,
    counter_outcome,
    snr_figure_name,
    temporal_figure_name,
    replacement_wording,
):
    """Route exact direction-specific singleton guidance from semantic state."""
    guidance = _build_guidance(
        RESULT_GUIDANCE_SELECTED_STATIONS,
        language=language,
        analysis_id=analysis_id,
        is_compare=False,
        analysis_context=AnalysisContext(),
        selected_station_count=1,
    )
    expected_key = f"selected_success_{direction}"
    expected_item = RESULT_GUIDANCE[language]["sections"][expected_key]

    assert expected_item["read"] in guidance
    assert expected_item["limits"] in guidance
    assert success_outcome in guidance
    assert counter_outcome in guidance
    assert snr_figure_name in guidance
    assert temporal_figure_name in guidance
    assert replacement_wording in guidance
    assert "Selected Path Summary" not in guidance
    assert "Zusammenfassung des ausgewählten Funkwegs" not in guidance
    assert "combined observation-weighted selection" not in guidance
    assert "kombinierte beobachtungsgewichtete Auswahl" not in guidance


@pytest.mark.parametrize(
    "selected_station_count",
    (None, 0, -1, False, 1.5, "2", 2, 5),
)
def test_success_selected_guidance_requires_exactly_one_station(
    selected_station_count,
):
    """Reject any cardinality that violates Success singleton selection."""
    with pytest.raises(
        ValueError,
        match="requires exactly one selected station",
    ):
        _build_guidance(
            RESULT_GUIDANCE_SELECTED_STATIONS,
            analysis_id="RX_ABS",
            is_compare=False,
            analysis_context=AnalysisContext(),
            selected_station_count=selected_station_count,
        )


def test_compare_selected_guidance_requires_one_station_and_uses_one_path_copy():
    """Enforce and describe the same singleton boundary for Compare."""
    guidance = _build_guidance(
        RESULT_GUIDANCE_SELECTED_STATIONS,
        analysis_id="RX_COMP",
        is_compare=True,
        analysis_context=AnalysisContext(
            comparison_mode=COMPARISON_REFERENCE_STATION
        ),
        selected_station_count=1,
    )

    assert "one chosen TX station" in guidance
    assert "one specific radio path" in guidance
    assert "chosen TX stations" not in guidance
    assert not _format_fields(guidance)

    for selected_station_count in (None, 0, 2, 6):
        with pytest.raises(
            ValueError,
            match="requires exactly one selected station",
        ):
            _build_guidance(
                RESULT_GUIDANCE_SELECTED_STATIONS,
                analysis_id="RX_COMP",
                is_compare=True,
                analysis_context=AnalysisContext(
                    comparison_mode=COMPARISON_REFERENCE_STATION
                ),
                selected_station_count=selected_station_count,
            )


def test_success_selected_guidance_stays_near_readability_target():
    """Keep each selected-station popover within the generous copy ceiling."""
    for language in ("en", "de"):
        for direction in ("rx", "tx"):
            item = RESULT_GUIDANCE[language]["sections"][
                f"selected_success_{direction}"
            ]
            assert len(item["read"]) + len(item["limits"]) <= 2300


@pytest.mark.parametrize(
    ("language", "direction", "directional_terms"),
    (
        (
            "en",
            "rx",
            (
                "qualifying TX station",
                "Heard by Target",
                "Heard by others only",
                "one station contributing on one date at that hour",
            ),
        ),
        (
            "en",
            "tx",
            (
                "qualifying RX station",
                "Target heard",
                "Other signals heard only",
                "one receiver contributing on one date at that hour",
            ),
        ),
        (
            "de",
            "rx",
            (
                "qualifizierende TX-Station",
                "Vom Target gehört",
                "Nur von anderen gehört",
                "Eine Stationspräsenz bedeutet, dass eine Station",
            ),
        ),
        (
            "de",
            "tx",
            (
                "qualifizierende RX-Station",
                "Target gehört",
                "Nur andere Signale gehört",
                "Eine Stationspräsenz bedeutet, dass ein Empfänger",
            ),
        ),
    ),
)
def test_success_temporal_guidance_explains_two_figures_rates_and_folded_averages(
    language,
    direction,
    directional_terms,
):
    """Pin the two-figure, two-weighting, and folded-average interpretation."""
    item = RESULT_GUIDANCE[language]["sections"][
        f"success_temporal_evidence_{direction}"
    ]
    combined = f"{item['read']} {item['limits']}"

    for expected_term in directional_terms:
        assert expected_term in combined
    if language == "en":
        for expected_term in (
            "Temporal Evidence",
            "station-level support and confirmed-opportunity volume",
            "split vote",
            "total height is contributing",
            "<strong class=\"defined-term\">station presences</strong> per represented UTC date",
            "every distinct",
            "one rate vote across all folded dates",
            "recurring dates increase support but not",
            "counts every confirmed opportunity once chronologically",
            "average counts per represented date after UTC-hour folding",
            "Opportunity-level Decode Rate",
            "With `1h` selected, each folded total is the average",
            "intentionally different weighting",
            "bar measures average daily participation",
            "line weights each distinct",
        ):
            assert expected_term in combined
        assert "station-date split votes" not in combined
    else:
        for expected_term in (
            "Zeitliche Evidenz",
            "Unterstützung auf Stationsebene",
            "aufgeteilte Stimme",
            "gesamte Balkenhöhe zeigt die beitragenden",
            "<strong class=\"defined-term\">Stationspräsenzen</strong> je berücksichtigtem UTC-Tag",
            "genau eine Ratenstimme",
            "Wiederholte Tage erhöhen daher die Evidenzunterstützung",
            "zählt chronologisch jede bestätigte Gelegenheit einmal",
            "Durchschnittswerte je berücksichtigtem Tag",
            "Dekodierrate auf Gelegenheitsebene",
            "Bei `1h` entspricht jede gefaltete Gesamthöhe dem Mittelwert",
            "bewusst unterschiedliche Gewichtungen",
            "durchschnittliche tägliche Beteiligung",
            "Linie gewichtet jede",
        ):
            assert expected_term in combined
        assert "Stations-Datum-Stunden-Stimmen" not in combined


@pytest.mark.parametrize("section_key", ("map_compare_rx", "map_compare_tx"))
def test_compare_map_guidance_explains_dynamic_symmetric_db_scale(section_key):
    """Explain cross-map color comparison without retaining S-unit guidance."""
    english_limits = RESULT_GUIDANCE["en"]["sections"][section_key]["limits"]
    german_limits = RESULT_GUIDANCE["de"]["sections"][section_key]["limits"]

    assert "stepped dB color scale is symmetric around 0 dB" in english_limits
    assert "can expand between runs" in english_limits
    assert "visible sector range without fixed headroom" in english_limits
    assert "light yellow-green display-neutral band" in english_limits
    assert "display-neutral band's width matches the active step" in english_limits
    assert "at 3 dB it covers -1.5 to +1.5 dB" in english_limits
    assert "Only 0 dB means equality" in english_limits
    assert "numerical color-bar values" in english_limits
    assert "abgestufte dB-Farbskala ist symmetrisch um 0 dB" in german_limits
    assert "kann sich zwischen Läufen erweitern" in german_limits
    assert "ohne feste Reserve an den sichtbaren Segmentwertebereich" in german_limits
    assert "hellen gelbgrünen darstellungsneutralen Band" in german_limits
    assert "darstellungsneutralen Bands entspricht der aktiven Schrittweite" in german_limits
    assert "bei 3 dB reicht es von -1,5 bis +1,5 dB" in german_limits
    assert "Nur 0 dB bedeutet Gleichheit" in german_limits
    assert "numerischen Werte der Farbskala" in german_limits
    assert "S-unit" not in english_limits
    assert "S-Stufe" not in german_limits


def test_success_map_guidance_uses_status_markers_and_two_level_support():
    """Pin direction-specific marker outcomes and the two support levels."""
    expected_terms = {
        "en": {
            "rx": ("RX Decode Rate", "Heard by Target", "Heard by others only"),
            "tx": (
                "TX Decode Rate",
                "Target was heard",
                "Other signals were heard only",
            ),
        },
        "de": {
            "rx": ("RX-Dekodierrate", "Vom Target gehört", "Nur von anderen gehört"),
            "tx": (
                "TX-Dekodierrate",
                "Target gehört",
                "Nur andere Signale gehört",
            ),
        },
    }
    for language, directions in expected_terms.items():
        for direction, terms in directions.items():
            item = RESULT_GUIDANCE[language]["sections"][
                f"map_success_{direction}"
            ]
            combined = f"{item['read']} {item['limits']}"
            assert all(term in combined for term in terms)
            assert "light-grey" in combined if language == "en" else "Hellgraue" in combined
            assert (
                ("STATIONS" in combined and "OPPORTUNITIES" in combined)
                if language == "en"
                else ("STATIONEN" in combined and "GELEGENHEITEN" in combined)
            )


def test_success_segment_distance_and_temporal_guidance_matches_editorial_contract():
    """Pin the requested bilingual point-of-use interpretation guidance."""
    directional_expectations = {
        "en": {
            "rx": (
                "Heard by Target",
                "TX Stations Heard by Target at Least Once by Distance",
                "Successful RX SNR Deviation",
            ),
            "tx": (
                "Target was heard",
                "RX Stations Hearing the Target at Least Once by Distance",
                "Successful TX SNR Deviation",
            ),
        },
        "de": {
            "rx": (
                "Vom Target gehört",
                "Vom Target mindestens einmal gehörte TX-Stationen nach Entfernung",
                "Abweichung des erfolgreichen RX-SNR",
            ),
            "tx": (
                "Target gehört",
                "RX-Stationen, die das Target mindestens einmal hörten, nach Entfernung",
                "Abweichung des erfolgreichen TX-SNR",
            ),
        },
    }
    for language, directions in directional_expectations.items():
        for direction, expected_phrases in directions.items():
            sections = RESULT_GUIDANCE[language]["sections"]
            combined = " ".join(
                sections[f"{prefix}_{direction}"]["read"]
                for prefix in (
                    "segment_success",
                    "success_evidence",
                    "success_temporal_evidence",
                )
            )
            assert all(phrase in combined for phrase in expected_phrases)
            assert (
                "Compare the two Decode Rates directly" in combined
                if language == "en"
                else "Vergleiche beide Dekodierraten direkt" in combined
            )


def test_success_map_presentation_labels_are_bilingual_and_status_only():
    """Keep the compact legend and footer labels aligned across languages."""
    expected_labels = {
        "en": {
            "cbar_abs_rx": "Station-balanced RX Decode Rate (%)",
            "cbar_abs_tx": "Station-balanced TX Decode Rate (%)",
            "map_success_footer_opportunities": "OPPORTUNITIES",
            "map_success_footer_stations": "STATIONS",
            "map_success_rx_opportunity_target": "Heard by Target",
            "map_success_rx_opportunity_counter": "Heard by others only",
            "map_success_rx_station_target": "Heard by Target",
            "map_success_rx_station_counter": "Heard by others only",
            "map_success_tx_opportunity_target": "Target heard",
            "map_success_tx_opportunity_counter": "Other signals heard only",
            "map_success_tx_station_target": "Target heard",
            "map_success_tx_station_counter": "Other signals heard only",
            "map_success_legend_insufficient": "Insufficient evidence",
        },
        "de": {
            "cbar_abs_rx": "Stationsgleichgewichtete RX-Dekodierrate (%)",
            "cbar_abs_tx": "Stationsgleichgewichtete TX-Dekodierrate (%)",
            "map_success_footer_opportunities": "GELEGENHEITEN",
            "map_success_footer_stations": "STATIONEN",
            "map_success_rx_opportunity_target": "Vom Target gehört",
            "map_success_rx_opportunity_counter": "Nur von anderen gehört",
            "map_success_rx_station_target": "Vom Target gehört",
            "map_success_rx_station_counter": "Nur von anderen gehört",
            "map_success_tx_opportunity_target": "Target gehört",
            "map_success_tx_opportunity_counter": "Nur andere Signale gehört",
            "map_success_tx_station_target": "Target gehört",
            "map_success_tx_station_counter": "Nur andere Signale gehört",
            "map_success_legend_insufficient": "Unzureichende Evidenz",
        },
    }

    for language, labels in expected_labels.items():
        for key, expected_text in labels.items():
            assert T[language][key] == expected_text

    retired_keys = {
        "map_success_sector_legend",
        "map_success_marker_legend",
        "map_success_footer_station_categories",
        "map_success_footer_opportunity_categories",
        "map_footer_stations",
        "map_footer_confirmed_opportunities",
        "map_success_target_observed",
        "map_success_zero_target",
        "map_success_no_qualifying_segment",
        "fmt_results_decimal_separator",
        "leg_abs_hit_one",
        "leg_abs_hit_mid",
        "leg_abs_hit_high",
    }
    for language in ("en", "de"):
        assert retired_keys.isdisjoint(T[language])


@pytest.mark.parametrize(
    (
        "language",
        "analysis_id",
        "map_success",
        "map_counter",
        "mode_key",
    ),
    (
        ("en", "RX_ABS", "Heard by Target", "Heard by others only", "rx"),
        (
            "en",
            "TX_ABS",
            "Target was heard",
            "Other signals were heard only",
            "tx",
        ),
        ("de", "RX_ABS", "Vom Target gehört", "Nur von anderen gehört", "rx"),
        (
            "de",
            "TX_ABS",
            "Target gehört",
            "Nur andere Signale gehört",
            "tx",
        ),
    ),
)
def test_success_guidance_uses_mode_specific_station_status_labels(
    language,
    analysis_id,
    map_success,
    map_counter,
    mode_key,
):
    """Resolve direction-aware map outcomes and exact distance-panel names."""
    map_guidance = _build_guidance(
        RESULT_GUIDANCE_MAP,
        language=language,
        analysis_id=analysis_id,
        is_compare=False,
        analysis_context=AnalysisContext(),
    )
    distance_guidance = _build_guidance(
        RESULT_GUIDANCE_SUCCESS_EVIDENCE,
        language=language,
        analysis_id=analysis_id,
        is_compare=False,
        analysis_context=AnalysisContext(),
    )

    assert map_success in map_guidance
    assert map_counter in map_guidance
    for key in (
        f"fig_success_reach_title_{mode_key}",
        f"fig_success_consistency_title_{mode_key}",
        f"fig_success_snr_distance_title_{mode_key}",
    ):
        assert T[language][key] in distance_guidance


def test_result_guidance_uses_practical_station_language():
    """Keep operator-facing copy concrete while preserving the row definition."""
    for language in ("en", "de"):
        complete_catalog = " ".join(
            text
            for section in RESULT_GUIDANCE[language]["sections"].values()
            for text in section.values()
        ).lower()
        assert "estimator" not in complete_catalog
        assert "schätzer" not in complete_catalog

    expected_identity_copy = {
        "station_insights_compare_joint": (
            "`callsign + locator`",
            "`Rufzeichen + Locator`",
        ),
        "station_insights_compare_scheduled": (
            "`callsign + locator`",
            "`Rufzeichen + Locator`",
        ),
        "station_insights_success_rx": (
            "callsign plus locator",
            "Rufzeichen und Locator",
        ),
        "station_insights_success_tx": (
            "callsign plus locator",
            "Rufzeichen und Locator",
        ),
    }
    for section_key, (english_identity, german_identity) in (
        expected_identity_copy.items()
    ):
        english = RESULT_GUIDANCE["en"]["sections"][section_key]["read"]
        german = RESULT_GUIDANCE["de"]["sections"][section_key]["read"]
        assert english_identity in english.replace("-", " ")
        assert german_identity in german


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
            selected_station_count=(
                1
                if section_id == RESULT_GUIDANCE_SELECTED_STATIONS
                else None
            ),
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
            "two controlled paths operating within the shared Grid-4",
            "exact callsign",
        ),
        (
            COMPARISON_REFERENCE_STATION,
            LOCAL_BENCHMARK_MEDIAN,
            "by its exact callsign and independently configured "
            "Reference Grid-4",
            "shared Grid-4",
        ),
        (
            COMPARISON_LOCAL_NEIGHBORHOOD,
            LOCAL_BENCHMARK_MEDIAN,
            "typical qualifying local station within 175 km",
            "strongest qualifying local station",
        ),
        (
            COMPARISON_LOCAL_NEIGHBORHOOD,
            LOCAL_BENCHMARK_BEST,
            "strongest qualifying local station available within 175 km",
            "typical qualifying local station",
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
    joint_compare = _build_guidance(
        RESULT_GUIDANCE_COMPARISON_EVIDENCE,
        analysis_context=AnalysisContext(
            comparison_mode=COMPARISON_REFERENCE_STATION
        ),
        selected_station_count=1,
    )
    scheduled_compare = _build_guidance(
        RESULT_GUIDANCE_COMPARISON_EVIDENCE,
        analysis_id="TX_COMP",
        is_sequential=True,
        analysis_context=AnalysisContext(
            comparison_mode=COMPARISON_HARDWARE_AB
        ),
    )
    joint_compare_plain = _plain_guidance(joint_compare)
    scheduled_compare_plain = _plain_guidance(scheduled_compare)

    assert "qualifying TX station" in rx_success
    assert "Heard by Target" in rx_success
    assert "Heard by others only" in rx_success
    assert "Elsewhere" not in rx_success
    assert "qualifying RX station" in tx_success
    assert "Target was heard" in tx_success
    assert "Other signals were heard only" in tx_success
    assert "Other Signals" not in tx_success
    assert "confirmed opportunity" in rx_context
    assert "confirmed opportunity" in tx_context
    assert "Heard by Target" in rx_context
    assert "Heard by others only" in rx_context
    assert "Target heard" in tx_context
    assert "Other signals heard only" in tx_context
    assert "A Joint Spot is a consolidated same-cycle unit" in joint_compare_plain
    assert all(
        outcome in joint_compare_plain
        for outcome in (
            "Joint",
            "Only Target",
            "Both (Async)",
            "Only Reference",
        )
    )
    assert "hatched Stations" in joint_compare_plain
    assert "solid Spots" in joint_compare_plain
    assert "Total and Joint counts for both levels appear" in joint_compare_plain
    assert (
        "A Scheduled Pair is the deterministic Target–Reference unit"
        in scheduled_compare_plain
    )
    assert "solid Scheduled-pairs bars" in scheduled_compare_plain
    assert "time-separated design retains changes" in scheduled_compare_plain


@pytest.mark.parametrize("language", ("en", "de"))
def test_success_segment_and_temporal_guidance_route_without_changing_compare(language):
    """Keep the new Success summaries separate from established Compare help."""
    success_segment = _build_guidance(
        RESULT_GUIDANCE_SEGMENT,
        language=language,
        analysis_id="RX_ABS",
        is_compare=False,
        analysis_context=AnalysisContext(),
    )
    compare_segment = _build_guidance(
        RESULT_GUIDANCE_SEGMENT,
        language=language,
        analysis_id="RX_COMP",
        is_compare=True,
        analysis_context=AnalysisContext(
            comparison_mode=COMPARISON_REFERENCE_STATION
        ),
    )
    success_temporal = _build_guidance(
        RESULT_GUIDANCE_TEMPORAL_EVIDENCE,
        language=language,
        analysis_id="RX_ABS",
        is_compare=False,
        analysis_context=AnalysisContext(),
    )
    compare_temporal = _build_guidance(
        RESULT_GUIDANCE_TEMPORAL_EVIDENCE,
        language=language,
        analysis_id="RX_COMP",
        is_compare=True,
        analysis_context=AnalysisContext(
            comparison_mode=COMPARISON_REFERENCE_STATION
        ),
    )

    assert (
        "Decode Rate" in success_segment
        if language == "en"
        else "Dekodierrate" in success_segment
    )
    assert (
        "Heard by Target" in success_segment
        if language == "en"
        else "Vom Target gehört" in success_segment
    )
    assert (
        "Compare the two Decode Rates directly" in success_segment
        if language == "en"
        else "Vergleiche beide Dekodierraten direkt" in success_segment
    )
    assert "Joint Spots" in compare_segment
    assert (
        "Successful RX SNR Deviation" in success_temporal
        if language == "en"
        else "Abweichung des erfolgreichen RX-SNR" in success_temporal
    )
    assert (
        "Heard by others only" in success_temporal
        if language == "en"
        else "Nur von anderen gehört" in success_temporal
    )
    assert "Joint Spots" in compare_temporal


def test_success_guidance_does_not_interpolate_mutable_ui_labels():
    """Keep static editorial guidance independent of presentation label values."""
    translations = {
        **T["en"],
        "abs_rx_counter": "<script>alert(1)</script>",
        "map_success_rx_station_target": "<img src=x onerror=alert(2)>",
        "map_success_rx_station_counter": "<iframe src=bad></iframe>",
    }
    map_guidance = build_result_guidance(
        RESULT_GUIDANCE_MAP,
        language="en",
        translations=translations,
        analysis_id="RX_ABS",
        is_compare=False,
        analysis_context=AnalysisContext(),
    )
    temporal_guidance = build_result_guidance(
        RESULT_GUIDANCE_TEMPORAL_EVIDENCE,
        language="en",
        translations=translations,
        analysis_id="RX_ABS",
        is_compare=False,
        analysis_context=AnalysisContext(),
    )

    assert map_guidance == _build_guidance(
        RESULT_GUIDANCE_MAP,
        analysis_id="RX_ABS",
        is_compare=False,
        analysis_context=AnalysisContext(),
    )
    assert temporal_guidance == _build_guidance(
        RESULT_GUIDANCE_TEMPORAL_EVIDENCE,
        analysis_id="RX_ABS",
        is_compare=False,
        analysis_context=AnalysisContext(),
    )
    for unsafe_fragment in ("<script>", "<img ", "<iframe "):
        assert unsafe_fragment not in map_guidance
        assert unsafe_fragment not in temporal_guidance


def test_success_guidance_generation_does_not_mutate_analysis_context():
    """Keep presentation-only guidance outside canonical scientific state."""
    analysis_context = AnalysisContext(
        comparison_mode=COMPARISON_NONE,
        neighborhood_radius_km=175,
    )
    original_fields = analysis_context.__dict__.copy()

    for section_id in (
        RESULT_GUIDANCE_MAP,
        RESULT_GUIDANCE_SEGMENT,
        RESULT_GUIDANCE_SUCCESS_EVIDENCE,
        RESULT_GUIDANCE_TEMPORAL_EVIDENCE,
    ):
        _build_guidance(
            section_id,
            analysis_id="RX_ABS",
            is_compare=False,
            analysis_context=analysis_context,
        )

    assert analysis_context.__dict__ == original_fields


@pytest.mark.parametrize("language", ("en", "de"))
@pytest.mark.parametrize(
    "section_id",
    (
        RESULT_GUIDANCE_MAP,
        RESULT_GUIDANCE_SEGMENT,
        RESULT_GUIDANCE_SUCCESS_EVIDENCE,
        RESULT_GUIDANCE_TEMPORAL_EVIDENCE,
    ),
)
def test_success_guidance_defined_term_markup_is_balanced(language, section_id):
    """Pass every redesigned semantic term through the established HTML path."""
    guidance = _build_guidance(
        section_id,
        language=language,
        analysis_id="RX_ABS",
        is_compare=False,
        analysis_context=AnalysisContext(),
    )

    assert guidance.count('<strong class="defined-term">') >= 1
    assert guidance.count("<strong") == guidance.count("</strong>")


def test_german_success_guidance_and_toggle_retire_zero_target_wording():
    """Use the evidence outcome in guidance and the matching display toggle."""
    guidance = _build_guidance(
        RESULT_GUIDANCE_STATION_INSIGHTS,
        language="de",
        analysis_id="RX_ABS",
        is_compare=False,
        analysis_context=AnalysisContext(),
    )

    assert "Nur von anderen gehört" in guidance
    assert "Zero-Target" not in guidance
    assert (
        T["de"]["success_rx_show_counter"]
        == "Nur von anderen Stationen gehört."
    )


@pytest.mark.parametrize(
    (
        "language",
        "analysis_id",
        "station_counter",
        "snr_header",
        "retired_counter",
        "retired_snr_header",
        "retired_opportunity_label",
    ),
    (
        (
            "en",
            "TX_ABS",
            "Other signals heard",
            "Median SNR @ 30 dBm",
            "Other signals heard only",
            "Median successful Target SNR",
            "confirmed opportunities",
        ),
        (
            "de",
            "TX_ABS",
            "Andere Signale gehört",
            "Median-SNR @ 30 dBm",
            "Nur andere Signale gehört",
            "Median des erfolgreichen Target-SNR",
            "bestätigte Gelegenheiten",
        ),
    ),
)
def test_performance_table_guidance_names_only_active_display_columns(
    language,
    analysis_id,
    station_counter,
    snr_header,
    retired_counter,
    retired_snr_header,
    retired_opportunity_label,
):
    """Keep Station Insights and Drill-Down guidance aligned with visible tables."""
    station_guidance = _build_guidance(
        RESULT_GUIDANCE_STATION_INSIGHTS,
        language=language,
        analysis_id=analysis_id,
        is_compare=False,
        analysis_context=AnalysisContext(),
    )
    drilldown_guidance = _build_guidance(
        RESULT_GUIDANCE_DRILLDOWN,
        language=language,
        analysis_id=analysis_id,
        is_compare=False,
        analysis_context=AnalysisContext(),
    )

    assert station_counter in station_guidance
    assert station_counter in drilldown_guidance
    assert snr_header in station_guidance
    assert retired_counter not in station_guidance
    assert retired_counter not in drilldown_guidance
    assert retired_snr_header not in station_guidance
    assert retired_opportunity_label not in station_guidance
    assert "Outcomes identify" not in drilldown_guidance
    assert "Outcomes unterscheiden" not in drilldown_guidance


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
    temporal_figures = _build_guidance(
        RESULT_GUIDANCE_TEMPORAL_EVIDENCE,
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
        selected_station_count=1,
    )

    for key in (
        "fig_success_reach_title_rx",
        "fig_success_consistency_title_rx",
        "fig_success_snr_distance_title_rx",
    ):
        assert T[language][key] in success_figures
    assert (
        "Successful RX SNR Deviation" in temporal_figures
        if language == "en"
        else "Abweichung des erfolgreichen RX-SNR" in temporal_figures
    )
    assert (
        "station presences" in temporal_figures
        if language == "en"
        else "Stationspräsenzen" in temporal_figures
    )
    assert (
        "Heard by Target" in selected_figures
        if language == "en"
        else "Vom Target gehört" in selected_figures
    )
    assert (
        "Heard by others only" in selected_figures
        if language == "en"
        else "Nur von anderen gehört" in selected_figures
    )
    assert "Target" in selected_figures
    for retired_name in (
        "Station Success Rate by Evidence Count",
        "Station Success Distribution",
        "Evidence Depth per Station",
        "Average Station Success Rate",
        "Observation-Level Success Rate",
    ):
        assert retired_name not in success_figures


@pytest.mark.parametrize(
    (
        "language",
        "joint_title",
        "scheduled_title",
        "selected_chronological_title",
        "selected_folded_title",
    ),
    (
        (
            "en",
            "Joint-Spot Δ SNR",
            "Scheduled-Pair Δ SNR",
            "Δ SNR over Time",
            "Δ SNR by UTC Hour",
        ),
        (
            "de",
            "Joint-Spot Δ SNR",
            "Geplantes Paar Δ SNR",
            "Δ SNR im Zeitverlauf",
            "Δ SNR nach UTC-Stunde",
        ),
    ),
)
def test_compare_guidance_names_the_rendered_figures_exactly(
    language,
    joint_title,
    scheduled_title,
    selected_chronological_title,
    selected_folded_title,
):
    """Use the same spacing and localization as the visible Compare figures."""
    joint_figures = _build_guidance(
        RESULT_GUIDANCE_COMPARISON_EVIDENCE,
        language=language,
        analysis_context=AnalysisContext(
            comparison_mode=COMPARISON_REFERENCE_STATION
        ),
    )
    scheduled_figures = _build_guidance(
        RESULT_GUIDANCE_COMPARISON_EVIDENCE,
        language=language,
        analysis_id="TX_COMP",
        is_sequential=True,
        analysis_context=AnalysisContext(
            comparison_mode=COMPARISON_HARDWARE_AB
        ),
    )
    selected_figures = _build_guidance(
        RESULT_GUIDANCE_SELECTED_STATIONS,
        language=language,
        analysis_context=AnalysisContext(
            comparison_mode=COMPARISON_REFERENCE_STATION
        ),
        selected_station_count=1,
    )

    assert "Station Medians (Δ SNR)" in joint_figures
    assert joint_title in joint_figures
    assert "Station Medians (Δ SNR)" in scheduled_figures
    assert scheduled_title in scheduled_figures
    assert selected_chronological_title in selected_figures
    assert selected_folded_title in selected_figures
    retired_selected_title = (
        "Δ SNR Distribution"
        if language == "en"
        else "Δ SNR Verteilung"
    )
    assert retired_selected_title not in selected_figures


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
        "allows_catalog_html": application.markdown[0].proto.allow_html,
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
    assert guided["allows_catalog_html"] is True
    assert RESULT_GUIDANCE["en"]["read_label"] in guided["body"]
    assert RESULT_GUIDANCE["en"]["limits_label"] in guided["body"]
    assert 'class="defined-term"' in guided["body"]
    assert "result-guidance-body-marker" in guided["body"]


def test_success_selected_popover_renders_singleton_guidance():
    """Render the exact singleton guidance at the Success selection point."""
    script = """
from core.analysis_context import AnalysisContext
from i18n import T
from ui.result_guidance import (
    RESULT_GUIDANCE_SELECTED_STATIONS,
    render_result_guidance_popover,
)

render_result_guidance_popover(
    RESULT_GUIDANCE_SELECTED_STATIONS,
    "Selected Station Evidence",
    language="en",
    translations=T["en"],
    key="result-guidance-selected",
    analysis_id="RX_ABS",
    is_compare=False,
    analysis_context=AnalysisContext(),
    selected_station_count=1,
)
"""
    application = AppTest.from_string(script, default_timeout=10).run()

    assert not application.exception
    assert len(application.markdown) == 1
    guidance_body = application.markdown[0].value
    assert "Selected Station SNR Evidence" in guidance_body
    assert "Selected Station Temporal Evidence" in guidance_body
    assert "actual normalized successful Target SNR" in guidance_body
    assert "combined observation-weighted selection" not in guidance_body
    assert "Selected Path Summary" not in guidance_body


def test_result_guidance_popover_css_is_wide_and_responsive():
    """Keep the help body readable without widening its compact trigger."""
    css_source = (REPOSITORY_ROOT / "ui" / "css.py").read_text(
        encoding="utf-8"
    )
    scoped_selector = (
        'div[data-testid="stPopoverBody"]:has(.result-guidance-body-marker)'
    )

    assert scoped_selector in css_source
    assert "width: min(66.667vw, 43rem) !important;" in css_source
    assert "max-width: calc(100vw - 2rem) !important;" in css_source
    assert "min-width: 0 !important;" in css_source
    assert "@media (max-width: 768px)" in css_source
    assert "width: calc(100vw - 2rem) !important;" in css_source
    assert (
        f"{scoped_selector}\n"
        "            .stMarkdown strong.defined-term"
    ) in css_source
    assert (
        f"{scoped_selector}\n"
        "            .stMarkdown p"
    ) in css_source
    assert "font-family: Arial, Helvetica, sans-serif !important;" in css_source


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
            "RESULT_GUIDANCE_SELECTED_STATIONS": 2,
            "RESULT_GUIDANCE_DRILLDOWN": 1,
        }
    )

    documentation_source = (
        REPOSITORY_ROOT / "ui" / "documentation.py"
    ).read_text(encoding="utf-8")
    assert "render_result_guidance_popover" not in documentation_source
