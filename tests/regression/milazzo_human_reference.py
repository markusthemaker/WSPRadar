"""Replay the approved Milazzo raw source through production scientific code.

The replay reads only frozen raw reports and its explicit configuration. Approved
expectations are read separately by assertions, never by scientific processing.
The default SQL executor is the offline dialect adapter; alternate executors can
use the same (query, reports) signature for explicit integration checks.
"""

from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import statistics
from types import SimpleNamespace

import pandas as pd

from reference_sql import execute_generated_sql


HUMAN_REFERENCE_DIRECTORY = (
    Path(__file__).parent / "reference_fixtures" / "milazzo_human_review_v2"
)
REVIEWED_CARD_IDS = {*(f"P{number:02}" for number in range(1, 11)),
                     *(f"B{number:02}" for number in range(1, 5))}
NATIVE_IDENTITY_COLUMNS = ["time_slot", "peer_sign", "peer_grid"]
STATION_IDENTITY_COLUMNS = ["peer_sign", "peer_grid"]


def read_reference_json(directory, filename):
    """Read an explicit fixture document without fallback or regeneration."""
    return json.loads((Path(directory) / filename).read_text(encoding="utf-8"))


def verify_human_reference_files(directory):
    """Require the approved packet and verify every manifested immutable file."""
    directory = Path(directory).resolve()
    manifest = read_reference_json(directory, "manifest.json")
    assert manifest["schema_version"] == 1
    paths = [record["path"] for record in manifest["files"]]
    assert len(paths) == len(set(paths)), "Duplicate human-reference manifest path"
    assert {
        "network_source.parquet", "performance.config", "review_cards.json",
        "reviewed_expectations.json", "approval.json",
        "performance_expected_ledger.csv", "performance_expected_stations.csv",
        "performance_expected_profiles.json", "provenance.json",
        "benchmark.config", "benchmark_expected.json", "review_packet.pdf",
        "benchmark_source.csv", "benchmark_expected_native_units.csv",
        "benchmark_capture_provenance.json", "network_capture.json",
        "benchmark_native_sql_capture.csv", "benchmark_native_capture.sql",
        "network_source_query.sql", "coverage.json",
    }.issubset(paths), "Required approved reference files are missing"
    for record in manifest["files"]:
        path = (directory / record["path"]).resolve()
        assert path.is_relative_to(directory), record["path"]
        contents = path.read_bytes()
        assert len(contents) == record["bytes"], record["path"]
        assert hashlib.sha256(contents).hexdigest() == record["sha256"], record["path"]
    cards = read_reference_json(directory, "review_cards.json")
    assert len(cards) == len(REVIEWED_CARD_IDS)
    assert {card["id"] for card in cards} == REVIEWED_CARD_IDS
    expected = read_reference_json(directory, "reviewed_expectations.json")
    assert set(expected) == REVIEWED_CARD_IDS
    for card in cards:
        if card["id"].startswith("P"):
            assert expected[card["id"]] == card["expected_numeric"]
    benchmark_expected = read_reference_json(directory, "benchmark_expected.json")
    for card_id, anchor in benchmark_expected.items():
        assert expected[card_id] == anchor
    approval = read_reference_json(directory, "approval.json")
    assert approval["schema_version"] == 1
    assert approval["fixture_id"] == "milazzo_human_review_v2"
    assert approval["packet_id"] == "MR01" and approval["packet_revision"] == 2
    assert approval["decision"] == "verified"
    assert set(approval["cards"]) == REVIEWED_CARD_IDS
    assert all(card["decision"] == "verified" for card in approval["cards"].values())
    assert {"review_cards.json", "review_packet.pdf", "reviewed_expectations.json",
            "benchmark_expected.json", "performance.config", "benchmark.config"}.issubset(
                approval["approved_artifacts"]
            )
    for filename, approved_hash in approval["approved_artifacts"].items():
        path = (directory / filename).resolve()
        assert path.is_relative_to(directory)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == approved_hash, filename
    assert read_reference_json(directory, "provenance.json")["performance_method"] == "opportunity-v3"


def replay_performance(fixture_directory, work_directory,
                       sql_executor=execute_generated_sql):
    """Validate configuration and run generated SQL, processing, maps and Inspector.

    Only the production Inspector's projected Parquet input is written, inside
    the caller's temporary directory. No frozen expectation is read here.
    """
    from config import BAND_MAP
    from core.analysis_runner import (
        apply_post_fetch_filters, build_analysis_batches,
        should_retry_without_decode_filter,
    )
    from core.map_data import build_map_data_result
    from core.math_utils import locator_to_latlon
    from core.presentation_context import PresentationContext
    from i18n import T
    from ui.analysis_context_adapter import build_analysis_context_from_session_state
    from ui.config_io import apply_config_state_values, validate_config_document
    from ui.inspector.contracts import InspectorContext, InspectorScope, StationInsightsView
    from ui.inspector.preparation import InspectorPreparation

    fixture_directory = Path(fixture_directory)
    work_directory = Path(work_directory)
    work_directory.mkdir(parents=True, exist_ok=True)
    document = read_reference_json(fixture_directory, "performance.config")
    source_rows = pd.read_parquet(fixture_directory / "network_source.parquet")
    configuration = validate_config_document(document)
    session_values = {"lang": "en"}
    apply_config_state_values(configuration, session_values)
    session_values["run_mode"] = configuration["analysis_direction"].upper()
    context = build_analysis_context_from_session_state(session_values)
    latitude, longitude = locator_to_latlon(context.qth)
    presentation = PresentationContext(
        language="en", theme="light", solar_label=T["en"]["opt_solar_all"],
        labels=T["en"],
    )
    analysis, = build_analysis_batches(
        context, configuration["start_utc"], configuration["end_utc"],
        latitude, longitude, f"AND band = '{BAND_MAP[context.band]}'",
        presentation_context=presentation,
    )
    strict_rows = sql_executor(analysis.query, source_rows)
    assert strict_rows.empty and should_retry_without_decode_filter(strict_rows, analysis)
    sql_rows = sql_executor(analysis.get("legacy_query"), source_rows)
    processed, warning = apply_post_fetch_filters(
        sql_rows.copy(), analysis, context, latitude, longitude, T["en"],
    )
    assert warning is None, warning
    processed_path = work_directory / "performance_processed.parquet"
    processed.to_parquet(processed_path, index=False)
    map_result = build_map_data_result(
        processed, analysis_id=analysis.id, is_compare=analysis.is_compare,
        is_sequential=analysis.is_sequential, analysis_kind=analysis.analysis_kind,
        center_latitude=latitude, center_longitude=longitude,
        min_spots=context.min_joint_spots_per_station,
        min_opportunities=context.min_confirmed_opportunities_per_peer,
        base_min_stations=context.min_joint_stations_per_map_segment,
        tx_ab_repeat_interval_minutes=context.tx_ab_repeat_interval_minutes,
        tx_ab_target_start_minute=context.tx_ab_target_start_minute,
        tx_ab_reference_start_minute=context.tx_ab_reference_start_minute,
    )
    assert map_result.diagnostic is None and map_result.map_data is not None
    map_data = map_result.map_data
    inspector = InspectorContext(
        analysis_id=analysis.id, title=analysis.title,
        is_compare=analysis.is_compare, is_sequential=analysis.is_sequential,
        parquet_path=processed_path, line1_str="", translations=T["en"],
        max_peer_distance_km=context.max_peer_distance_km,
        analysis_context=context, presentation_context=presentation,
        analysis_kind=analysis.analysis_kind, run_id=1,
        analysis_start_t=configuration["start_utc"],
        analysis_end_t=configuration["end_utc"],
    )
    scope = InspectorScope(
        selected_ranges=(), selected_directions=(),
        range_summary=T["en"]["opt_full_range"],
        direction_summary=T["en"]["opt_all_dirs"],
        selected_segment="Full Range | All Directions",
        active_scope_summary="Full Range | All Directions", scope_token="all",
        distance_scope_intervals=((0.0, float(context.max_peer_distance_km)),),
    )
    preparation = InspectorPreparation(session_values, 1)
    view_configuration = document["settings"]["results_view"]["performance"]
    segment_time_bin = view_configuration["segment_evidence_time_bin"]
    selected_time_bin = view_configuration["station_evidence_time_bin"]
    assert view_configuration["selected_ranges"] == "all"
    assert view_configuration["selected_directions"] == "all"
    segment = preparation.prepare_performance_segment(
        inspector, scope, map_data.station_rows, retained_time_bin=segment_time_bin,
    )
    display = segment.bundle["display_model"]
    table = display["full_station_table"]
    # This is the explicitly reviewed selected receiver, not an algorithmic
    # exception: the remaining recipes include every qualifying receiver.
    selection = (
        table[display["station_column"]].eq("VE6PDQ")
        & table[display["locator_column"]].eq("DO34IR")
    )
    positions = [index for index, selected in enumerate(selection) if selected]
    assert len(positions) == 1
    station_view = StationInsightsView(
        displayed_table=table, export_station_table=table, full_station_table=table,
        selected_station_table=table.iloc[positions], selected_rows=tuple(positions),
        station_column=display["station_column"], locator_column=display["locator_column"],
        distance_column=display["distance_column"], azimuth_column=display["azimuth_column"],
        show_non_joint=False, level_three_container=None, show_zero_target=True,
    )
    selected = preparation.prepare_selected_performance(
        inspector, scope, station_view, segment, preferred_time_bin=selected_time_bin,
    )
    recipes = {
        "distance": segment.bundle["figure_recipe"],
        "segment_temporal": dict(segment.bundle["temporal_bundle"]["base_recipe"],
                                 time_bin=segment_time_bin),
        "selected_temporal": dict(selected["selected_base_recipe"], time_bin=selected_time_bin),
    }
    return SimpleNamespace(
        configuration=configuration, context=context, analysis=analysis,
        source_rows=source_rows, strict_rows=strict_rows, sql_rows=sql_rows,
        processed=processed, map_data=map_data, stations=map_data.station_rows,
        segments=map_data.segment_rows, inspector=inspector, recipes=recipes,
        selected_rows=selected["selected_station_rows"], station_insights=table,
    )


def assert_reference_number(actual, expected, label):
    """Compare independent scalar evidence, preserving unknown versus zero."""
    if expected is None or pd.isna(expected):
        assert actual is None or pd.isna(actual), (label, actual, expected)
    else:
        assert actual is not None and math.isclose(
            float(actual), float(expected), rel_tol=0.0, abs_tol=1e-9,
        ), (label, actual, expected)


def assert_performance_reference(run, fixture_directory):
    """Compare every native row, station, map and reviewed profile to the oracle.

    The exhaustive oracle was derived independently from raw report IDs. Human
    approval applies to the named card anchors; the extended ledger is additional
    independent arithmetic, not a claim that a person checked every native row.
    """
    fixture_directory = Path(fixture_directory)
    ledger = pd.read_csv(fixture_directory / "performance_expected_ledger.csv",
                         float_precision="round_trip")
    expected_stations = pd.read_csv(
        fixture_directory / "performance_expected_stations.csv",
        float_precision="round_trip",
    )
    profiles = read_reference_json(fixture_directory, "performance_expected_profiles.json")
    columns = [*NATIVE_IDENTITY_COLUMNS, "target_seen", "external_seen", "target_snr",
               "opportunity", "hit", "miss", "target_only"]
    assert not run.processed.duplicated(NATIVE_IDENTITY_COLUMNS).any()
    pd.testing.assert_frame_equal(
        run.processed[columns].sort_values(NATIVE_IDENTITY_COLUMNS).reset_index(drop=True),
        ledger[columns].sort_values(NATIVE_IDENTITY_COLUMNS).reset_index(drop=True),
        check_dtype=False, check_categorical=False, check_exact=False, rtol=0, atol=1e-9,
    )
    station_lookup = {
        (station["peer_sign"], station["peer_grid"]): station
        for station in expected_stations.to_dict("records")
    }
    assert not run.stations.duplicated(STATION_IDENTITY_COLUMNS).any()
    assert set(map(tuple, run.stations[STATION_IDENTITY_COLUMNS].to_numpy())) == set(station_lookup)
    for station in run.stations.to_dict("records"):
        identity = station["peer_sign"], station["peer_grid"]
        expected = station_lookup[identity]
        for column in ("hits", "misses", "opportunities", "target_only",
                       "successful_snr_median", "eligible"):
            assert_reference_number(station[column], expected[column], (identity, column))
        expected_rate = round(expected["rate_pct"], 1)
        assert_reference_number(station["rate_pct"], expected_rate, (identity, "rate"))
        assert_reference_number(station["calc_dist"], expected["distance_km"], (identity, "distance"))
        assert_reference_number(station["calc_azimuth"], expected["azimuth_degrees"], (identity, "bearing"))
        assert station["SegmentID"] == expected["map_segment"], identity

    expected_segments = defaultdict(list)
    for station in station_lookup.values():
        if station["eligible"]:
            expected_segments[station["map_segment"]].append(station)
    assert set(run.segments["SegmentID"]) == set(expected_segments)
    for segment in run.segments.to_dict("records"):
        contributors = expected_segments[segment["SegmentID"]]
        assert_reference_number(segment["cnt"], len(contributors), (segment["SegmentID"], "count"))
        for field, source in {"total_hits": "hits", "total_misses": "misses",
                              "total_opportunities": "opportunities",
                              "total_target_only": "target_only"}.items():
            assert_reference_number(segment[field], sum(station[source] for station in contributors),
                                    (segment["SegmentID"], field))
        assert_reference_number(segment["val"],
                                round(statistics.mean(station["rate_pct"] for station in contributors), 1),
                                (segment["SegmentID"], "balanced rate"))
        pooled_rate = 100 * sum(station["hits"] for station in contributors) / sum(
            station["opportunities"] for station in contributors
        )
        assert_reference_number(segment["pooled_rate_pct"], round(pooled_rate, 1),
                                (segment["SegmentID"], "pooled rate"))

    distance_fields = {
        "distance_qualifying_station_counts": "station_count",
        "distance_target_station_counts": "target_station_count",
        "distance_peer_reach_pct": "peer_reach_pct",
        "distance_station_balanced_rate_pct": "station_balanced_rate_pct",
        "distance_observation_level_rate_pct": "pooled_rate_pct",
        "distance_confirmed_opportunity_counts": "opportunities",
        "distance_target_counts": "hits", "distance_counter_counts": "misses",
        "distance_successful_snr_median_db": "snr_median",
        "distance_successful_snr_station_counts": "snr_count",
    }
    expected_distance_edges = [entry["lower_km"] for entry in profiles["distance"]]
    expected_distance_edges.append(expected_distance_edges[-1] + 500)
    assert list(run.recipes["distance"]["distance_edges_km"]) == expected_distance_edges
    for field in distance_fields:
        assert len(run.recipes["distance"][field]) == len(profiles["distance"])
    for index, expected in enumerate(profiles["distance"]):
        for field, source in distance_fields.items():
            assert_reference_number(run.recipes["distance"][field][index], expected[source],
                                    ("distance", index, field))
        if expected["snr_count"] >= 3:
            for bound, quartile in (("lower", "q1"), ("upper", "q3")):
                field = f"distance_successful_snr_interval_{bound}_db"
                assert_reference_number(run.recipes["distance"][field][index], expected[f"snr_{quartile}"],
                                        ("distance", index, quartile))
    profile_fields = {
        "opportunity_success_counts": "hits", "opportunity_counter_counts": "misses",
        "station_counts": "station_count", "station_balanced_rate_pct": "station_balanced_rate_pct",
        "observation_level_rate_pct": "rate_pct",
    }
    for scope, recipe_name in (("all", "segment_temporal"), ("VE6PDQ", "selected_temporal")):
        recipe = run.recipes[recipe_name]
        # Approved window boundaries are explicit scientific coordinates. Correct
        # numbers shifted to another hour or distance interval must also fail.
        expected_time_edges = list(pd.date_range(
            "2010-12-19T12:00Z", "2010-12-20T18:00Z", freq="3h",
        ).to_numpy(dtype="datetime64[ns]").astype("int64"))
        expected_time_edges.append(pd.Timestamp("2010-12-20T20:00Z").value)
        chronological = recipe["chronological_profiles"]["3h"]
        assert list(chronological["time_edge_ns"]) == expected_time_edges, scope
        expected_time_centers = [(left + right) // 2 for left, right in zip(
            expected_time_edges[:-1], expected_time_edges[1:]
        )]
        assert list(chronological["time_ns"]) == expected_time_centers, scope
        assert list(recipe["folded_profile"]["utc_hours"]) == list(range(24)), scope
        for kind, actual in (("chronological", recipe["chronological_profiles"]["3h"]),
                             ("folded", recipe["folded_profile"])):
            expected_profile = profiles["temporal"][scope][kind]
            for field in profile_fields:
                assert len(actual[field]) == len(expected_profile), (scope, kind, field)
            for index, expected in enumerate(expected_profile):
                for field, source in profile_fields.items():
                    assert_reference_number(actual[field][index], expected[source], (scope, kind, index, field))
                prefix = "snr_station_balanced" if scope == "all" else "snr"
                for statistic in ("median", "q1", "q3"):
                    assert_reference_number(actual[f"{prefix}_{statistic}_db"][index],
                                            expected[f"snr_{statistic}"], (scope, kind, index, statistic))
                support_field = "snr_station_value_counts" if scope == "all" else "snr_value_counts"
                assert_reference_number(actual[support_field][index], expected["snr_value_count"],
                                        (scope, kind, index, "SNR support"))
    selected_summary = run.recipes["selected_temporal"]["selected_station_summary"]
    expected_station = station_lookup[("VE6PDQ", "DO34IR")]
    for field, source in {
        "confirmed_opportunities": "opportunities", "successful_outcomes": "hits",
        "counter_outcomes": "misses", "success_rate_pct": "rate_pct",
        "successful_snr_median_db": "successful_snr_median",
    }.items():
        assert_reference_number(selected_summary[field], expected_station[source], ("selected", field))
