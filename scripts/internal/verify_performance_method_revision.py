"""Replay the frozen Milazzo raw source without changing its human review packet.

The independent calculation uses only the saved configuration and raw reports.
It does not import application calculations or use stored card expectations.
Production generated SQL is executed separately through the regression SQLite
adapter, then passed through post-fetch processing, maps and inspector recipes.
SQLite is a bounded dialect check, not native ClickHouse verification.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import statistics
import sys

import pandas as pd

REPOSITORY = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY))
COMPASS = "N NNE NE ENE E ESE SE SSE S SSW SW WSW W WNW NW NNW".split()


def json_value(value):
    """Serialize diagnostic output without nonstandard NaN tokens."""
    if isinstance(value, dict):
        return {str(key): json_value(element) for key, element in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_value(element) for element in value]
    if isinstance(value, pd.DataFrame):
        return json_value(value.to_dict(orient="records"))
    if hasattr(value, "tolist"):
        return json_value(value.tolist())
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def write_json(path, content):
    """Write an auditable UTF-8 diagnostic with finite JSON numbers only."""
    path.write_text(json.dumps(json_value(content), indent=2, allow_nan=False) + "\n", encoding="utf-8")


def quantile(samples, fraction):
    """Linearly interpolate sorted sample values, retaining their input units."""
    ordered = sorted(samples)
    if not ordered:
        return None
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    return ordered[lower] + (ordered[math.ceil(position)] - ordered[lower]) * (position - lower)


def coordinates(locator):
    """Independent Maidenhead cell-center calculation."""
    if not re.fullmatch(r"[A-R]{2}[0-9]{2}(?:[A-X]{2})?", locator):
        return None
    longitude = 20 * (ord(locator[0]) - 65) + 2 * int(locator[2]) - 180
    latitude = 10 * (ord(locator[1]) - 65) + int(locator[3]) - 90
    if len(locator) == 4:
        return latitude + .5, longitude + 1
    return latitude + (ord(locator[5]) - 65 + .5) / 24, longitude + (ord(locator[4]) - 65 + .5) / 12


def geometry(center, locator):
    """Return spherical distance in km and north-clockwise bearing in degrees."""
    point = coordinates(locator)
    if point is None:
        return None
    latitude1, longitude1, latitude2, longitude2 = map(math.radians, (*center, *point))
    longitude_delta = longitude2 - longitude1
    latitude_delta = latitude2 - latitude1
    haversine = math.sin(latitude_delta / 2) ** 2 + math.cos(latitude1) * math.cos(latitude2) * math.sin(longitude_delta / 2) ** 2
    distance = 6371 * 2 * math.atan2(math.sqrt(haversine), math.sqrt(max(0, 1 - haversine)))
    bearing = math.degrees(math.atan2(math.sin(longitude_delta) * math.cos(latitude2), math.cos(latitude1) * math.sin(latitude2) - math.sin(latitude1) * math.cos(latitude2) * math.cos(longitude_delta))) % 360
    return distance, bearing


def counts(rows):
    """Count successes over successes plus Misses; summarize Hit SNR at 30 dBm.

    SNR summaries are in dB. Target-only is a provenance subset and is never
    added to the success/opportunity totals. Empty denominators remain unknown.
    """
    hits = sum(row["hit"] for row in rows)
    misses = sum(row["miss"] for row in rows)
    opportunities = hits + misses
    snrs = [row["target_snr"] for row in rows if row["hit"]]
    return {
        "hits": hits, "misses": misses, "opportunities": opportunities,
        "target_only": sum(row["target_only"] for row in rows),
        "rate_pct": 100 * hits / opportunities if opportunities else None,
        "successful_snr_median": statistics.median(snrs) if snrs else None,
        "successful_snr_q1": quantile(snrs, .25), "successful_snr_q3": quantile(snrs, .75),
        "successful_snr_min": min(snrs) if snrs else None,
        "successful_snr_max": max(snrs) if snrs else None,
    }


def balanced(rows):
    """Average one unrounded percentage per exact peer identity with evidence."""
    groups = defaultdict(list)
    for row in rows:
        if row["opportunity"]:
            groups[(row["peer_sign"], row["peer_grid"])].append(row)
    station_rates = [counts(observations)["rate_pct"] for observations in groups.values()]
    return {**counts(rows), "station_count": len(groups), "station_balanced_rate_pct": statistics.mean(station_rates) if station_rates else None}


def independent_evidence(document, raw_source):
    """Derive peer-cycle witnesses directly from raw Target TX -> peer RX reports."""
    settings = document["settings"]
    core = settings["core_parameters"]
    advanced = settings["advanced_parameters"]
    # These assertions make the bounded scientific scope explicit rather than
    # silently ignoring a future configuration field or accepting changed inputs.
    assert core["analysis_direction"] == "tx" and core["band"] == "40m"
    assert settings["comparison_parameters"]["mode"] == "none"
    assert advanced["solar_state"] == "all"
    assert not advanced["exclude_special_callsigns"] and not advanced["exclude_moving_stations"]
    assert advanced["max_peer_distance_km"] == 5000
    target_tx = core["callsign"]
    target_grid4 = core["qth"][:4]
    start = datetime.fromisoformat(core["time_selection"]["start_utc"].replace("Z", "+00:00"))
    end = datetime.fromisoformat(core["time_selection"]["end_utc"].replace("Z", "+00:00"))
    center = coordinates(core["qth"])
    source = [report for report in raw_source.to_dict("records") if start <= report["time"] < end and report["band"] == 7]
    assert all(report["code"] == 0 for report in source), "Historical legacy-code source changed"
    active_cycles = defaultdict(list)
    for report in source:
        report["time_slot"] = int(report["time"].timestamp()) // 120
        report["is_target"] = report["tx_sign"] == target_tx and report["tx_loc"][:4] == target_grid4
        if report["is_target"]:
            # Any valid decode of Target TX confirms that Target TX transmitted.
            # It does not confirm another silent peer RX was listening.
            active_cycles[report["time_slot"]].append(int(report["id"]))
    groups = defaultdict(list)
    outside_gate_reports = 0
    for report in source:
        if report["time_slot"] not in active_cycles:
            outside_gate_reports += 1
            continue
        if not report["rx_sign"] or not report["rx_loc"]:
            continue
        if not report["is_target"] and report["tx_sign"] == target_tx:
            continue
        peer_rx = report["rx_sign"].strip().upper()
        peer_grid = report["rx_loc"].strip().upper()
        if peer_rx != target_tx:
            groups[(report["time_slot"], peer_rx, peer_grid)].append(report)
    ledger = []
    for (slot, peer_rx, peer_grid), reports in sorted(groups.items()):
        position = geometry(center, peer_grid)
        if position is None or position[0] >= advanced["max_peer_distance_km"]:
            continue
        target_reports = [report for report in reports if report["is_target"]]
        external_reports = [report for report in reports if report["tx_sign"] != target_tx]
        normalized_snrs = [int(report["snr"]) - int(report["power"]) + 30 for report in target_reports]
        ledger.append({
            "time_slot": slot, "peer_sign": peer_rx, "peer_grid": peer_grid,
            "target_seen": int(bool(target_reports)), "external_seen": int(bool(external_reports)),
            "target_snr": max(normalized_snrs) if normalized_snrs else None,
            "target_only": int(bool(target_reports) and not external_reports),
            "target_report_ids": [int(report["id"]) for report in target_reports],
            "external_report_ids": [int(report["id"]) for report in external_reports],
            "target_tx_activity_report_ids": active_cycles[slot],
            "distance_km": position[0], "azimuth_degrees": position[1],
        })
    metadata = {"target_tx": target_tx, "target_locator": core["qth"], "peer_role": "RX", "source_rows": len(source), "target_active_cycles": len(active_cycles), "reports_outside_target_active_gate": outside_gate_reports, "native_peer_cycles": len(ledger), "duplicate_target_reports_consolidated": sum(max(0, len(row["target_report_ids"]) - 1) for row in ledger)}
    return ledger, metadata, start, end


def independent_method(ledger, minimum, include_target_only):
    """Apply either explicit method definition and its per-peer opportunity gate.

    Historical Hits require Target and external evidence; revised Hits require
    only a Target decode. Misses always require external evidence without the
    Target decode. Rates use successes divided by successes plus Misses.
    """
    rows = []
    for observation in ledger:
        target = bool(observation["target_seen"])
        external = bool(observation["external_seen"])
        rows.append({**observation, "hit": int(target and (include_target_only or external)), "miss": int(external and not target), "opportunity": int(external or (include_target_only and target))})
    groups = defaultdict(list)
    for row in rows:
        groups[(row["peer_sign"], row["peer_grid"])].append(row)
    stations = [{"peer_sign": identity[0], "peer_grid": identity[1], **counts(observations), "distance_km": observations[0]["distance_km"], "azimuth_degrees": observations[0]["azimuth_degrees"]} for identity, observations in sorted(groups.items())]
    for station in stations:
        station["eligible"] = station["opportunities"] >= minimum
        ring = int(station["distance_km"] // 2500) * 2500
        direction = COMPASS[int(((station["azimuth_degrees"] + 11.25) % 360) // 22.5)]
        station["map_segment"] = f"[{ring}-{ring + 2500}km] {direction}"
    eligible = {(station["peer_sign"], station["peer_grid"]) for station in stations if station["eligible"]}
    selected = [row for row in rows if (row["peer_sign"], row["peer_grid"]) in eligible]
    summary = {"all_stations": len(stations), "eligible_stations": len(eligible), "eligible_population": balanced(selected), "all_population": balanced(rows), "ve6pdq": next(station for station in stations if station["peer_sign"] == "VE6PDQ" and station["peer_grid"] == "DO34IR")}
    return rows, stations, selected, summary


def independent_profiles(stations, rows, start, end):
    """Derive distance, 3-hour UTC and hourly folded profiles from qualified peers.

    Rates use each contributing station's successes/opportunities before equal
    station averaging. Segment SNR anomalies subtract each station's full-scope
    successful-SNR median in dB; folded SNR gives one vote per station/date/hour.
    Selected-station folded SNR similarly gives each represented date one vote.
    """
    distance = []
    for lower in range(0, 5000, 500):
        cohort = [station for station in stations if station["eligible"] and lower <= station["distance_km"] < lower + 500]
        snrs = [station["successful_snr_median"] for station in cohort if station["hits"]]
        hits = sum(station["hits"] for station in cohort)
        misses = sum(station["misses"] for station in cohort)
        distance.append({"lower_km": lower, "station_count": len(cohort), "target_station_count": len(snrs), "peer_reach_pct": 100 * len(snrs) / len(cohort) if cohort else None, "hits": hits, "misses": misses, "opportunities": hits + misses, "station_balanced_rate_pct": statistics.mean(station["rate_pct"] for station in cohort) if cohort else None, "pooled_rate_pct": 100 * hits / (hits + misses) if hits + misses else None, "snr_median": statistics.median(snrs) if snrs else None, "snr_q1": quantile(snrs, .25), "snr_q3": quantile(snrs, .75), "snr_count": len(snrs)})
    baselines = {(station["peer_sign"], station["peer_grid"]): station["successful_snr_median"] for station in stations if station["eligible"] and station["hits"] >= 3}
    profiles = {}
    for scope in ("all", "VE6PDQ"):
        observations = [row for row in rows if row["opportunity"] and (scope == "all" or row["peer_sign"] == scope)]
        chronological = []
        folded = []
        for kind, output, bin_count in (("chronological", chronological, math.ceil((end - start).total_seconds() / 10800)), ("folded", folded, 24)):
            for index in range(bin_count):
                selected = [row for row in observations if (int((datetime.fromtimestamp(row["time_slot"] * 120, timezone.utc) - start).total_seconds() // 10800) if kind == "chronological" else datetime.fromtimestamp(row["time_slot"] * 120, timezone.utc).hour) == index]
                snr_groups = defaultdict(list)
                for row in selected:
                    identity = row["peer_sign"], row["peer_grid"]
                    if not row["hit"] or (scope == "all" and identity not in baselines):
                        continue
                    sample = row["target_snr"] - baselines[identity] if scope == "all" else row["target_snr"]
                    date = datetime.fromtimestamp(row["time_slot"] * 120, timezone.utc).date().isoformat()
                    key = (*identity, date) if scope == "all" and kind == "folded" else identity if scope == "all" else date if kind == "folded" else row["time_slot"]
                    snr_groups[key].append(sample)
                values = [statistics.median(samples) for samples in snr_groups.values()]
                # Recipes retain numerical quartiles; the renderer separately
                # gates visible IQR bands on the established support threshold.
                output.append({"index": index, **balanced(selected), "snr_value_count": len(values), "snr_median": statistics.median(values) if values else None, "snr_q1": quantile(values, .25), "snr_q3": quantile(values, .75)})
        profiles[scope] = {"chronological": chronological, "folded": folded}
    return {"distance": distance, "temporal": profiles}


def production_replay(document, source, output):
    """Run actual configuration, generated SQL, post-processing and UI recipes."""
    from config import BAND_MAP
    from core.analysis_runner import apply_post_fetch_filters, build_analysis_batches, should_retry_without_decode_filter
    from core.map_data import build_map_data_result
    from core.math_utils import locator_to_latlon
    from core.opportunity_engine import ABSOLUTE_METHOD_VERSION
    from core.presentation_context import PresentationContext
    from i18n import T
    from tests.regression.reference_sql import execute_generated_sql
    from ui.analysis_context_adapter import build_analysis_context_from_session_state
    from ui.config_io import apply_config_state_values, validate_config_document
    from ui.inspector.contracts import InspectorContext, InspectorScope, StationInsightsView
    from ui.inspector.preparation import InspectorPreparation

    configuration = validate_config_document(document)
    session = {"lang": "en"}
    apply_config_state_values(configuration, session)
    session["run_mode"] = "TX"
    context = build_analysis_context_from_session_state(session)
    latitude, longitude = locator_to_latlon(context.qth)
    presentation = PresentationContext(language="en", theme="light", solar_label=T["en"]["opt_solar_all"], labels=T["en"])
    analysis, = build_analysis_batches(context, configuration["start_utc"], configuration["end_utc"], latitude, longitude, f"AND band = '{BAND_MAP[context.band]}'", presentation_context=presentation)
    strict = execute_generated_sql(analysis.query, source)
    assert strict.empty and should_retry_without_decode_filter(strict, analysis)
    sql_rows = execute_generated_sql(analysis.get("legacy_query"), source)
    for name, query in (("strict", analysis.query), ("legacy", analysis.get("legacy_query"))):
        (output / f"generated_{name}.sql").write_text(query, encoding="utf-8")
    processed, warning = apply_post_fetch_filters(sql_rows.copy(), analysis, context, latitude, longitude, T["en"])
    assert warning is None, warning
    processed_path = output / "production_processed.parquet"
    processed.to_parquet(processed_path, index=False)
    processed.to_csv(output / "production_processed.csv", index=False)
    map_result = build_map_data_result(processed, analysis_id=analysis.id, is_compare=analysis.is_compare,  analysis_kind=analysis.analysis_kind, center_latitude=latitude, center_longitude=longitude, min_spots=context.min_joint_spots_per_station, min_opportunities=context.min_confirmed_opportunities_per_peer, base_min_stations=context.min_joint_stations_per_map_segment)
    assert map_result.map_data is not None, map_result.diagnostic
    map_data = map_result.map_data
    map_data.station_rows.to_csv(output / "production_station_rows.csv", index=False)
    map_data.segment_rows.to_csv(output / "production_segment_rows.csv", index=False)
    inspector = InspectorContext(analysis_id=analysis.id, title=analysis.title, is_compare=False,  parquet_path=processed_path, line1_str="", translations=T["en"], max_peer_distance_km=context.max_peer_distance_km, analysis_context=context, presentation_context=presentation, analysis_kind=analysis.analysis_kind, run_id=1, analysis_start_t=configuration["start_utc"], analysis_end_t=configuration["end_utc"])
    scope = InspectorScope(selected_ranges=(), selected_directions=(), range_summary=T["en"]["opt_full_range"], direction_summary=T["en"]["opt_all_dirs"], selected_segment="Full Range | All Directions", active_scope_summary="Full Range | All Directions", scope_token="all", distance_scope_intervals=((0., 5000.),))
    preparation = InspectorPreparation(session, 1)
    segment = preparation.prepare_performance_segment(inspector, scope, map_data.station_rows, retained_time_bin="3h")
    display = segment.bundle["display_model"]
    table = display["full_station_table"]
    table.to_csv(output / "production_station_insights.csv", index=False)
    positions = [index for index, call in enumerate(table[display["station_column"]]) if call == "VE6PDQ"]
    assert len(positions) == 1
    station_view = StationInsightsView(displayed_table=table, export_station_table=table, full_station_table=table, selected_station_table=table.iloc[positions], selected_rows=tuple(positions), station_column=display["station_column"], locator_column=display["locator_column"], distance_column=display["distance_column"], azimuth_column=display["azimuth_column"], show_non_joint=False, level_three_container=None, show_zero_target=True)
    selected = preparation.prepare_selected_performance(inspector, scope, station_view, segment, preferred_time_bin="3h")
    selected["selected_station_rows"].to_csv(output / "production_ve6pdq_rows.csv", index=False)
    recipes = {"distance": segment.bundle["figure_recipe"], "segment_temporal": dict(segment.bundle["temporal_bundle"]["base_recipe"], time_bin="3h"), "selected_temporal": dict(selected["selected_base_recipe"], time_bin="3h")}
    write_json(output / "production_recipes.json", recipes)
    return processed, map_data, recipes, {"method": ABSOLUTE_METHOD_VERSION, "sql_rows": len(sql_rows), "processed_rows": len(processed), "station_rows": len(map_data.station_rows), "station_insights_summary": display["summary_lines"], "selected_station_summary": recipes["selected_temporal"]["selected_station_summary"]}


def assert_number(actual, expected, label):
    """Compare one independent scalar with a labeled production value."""
    if expected is None:
        assert actual is None or pd.isna(actual), (label, actual, expected)
    else:
        assert math.isclose(float(actual), float(expected), abs_tol=1e-9), (label, actual, expected)


def compare_production(rows, stations, profiles, processed, map_data, recipes):
    """Check production values against source-derived independent arithmetic."""
    expected_rows = {(row["time_slot"], row["peer_sign"], row["peer_grid"]): row for row in rows}
    assert len(processed) == len(expected_rows)
    for row in processed.to_dict("records"):
        expected = expected_rows[(row["time_slot"], row["peer_sign"], row["peer_grid"])]
        for column in ("target_seen", "external_seen", "target_snr", "opportunity", "hit", "miss", "target_only"):
            assert_number(row[column], expected[column], ("native", column, row["peer_sign"], row["time_slot"]))
    expected_stations = {(station["peer_sign"], station["peer_grid"]): station for station in stations}
    assert len(map_data.station_rows) == len(expected_stations)
    for station in map_data.station_rows.to_dict("records"):
        expected = expected_stations[(station["peer_sign"], station["peer_grid"])]
        for column in ("hits", "misses", "opportunities", "target_only", "successful_snr_median", "eligible"):
            assert_number(station[column], expected[column], ("station", column, station["peer_sign"]))
        expected_rate = round(expected["rate_pct"], 1) if expected["rate_pct"] is not None else None
        assert_number(station["rate_pct"], expected_rate, ("station rate", station["peer_sign"]))
    expected_segments = defaultdict(list)
    for station in stations:
        if station["eligible"]:
            expected_segments[station["map_segment"]].append(station)
    assert set(map_data.segment_rows["SegmentID"]) == set(expected_segments)
    for segment in map_data.segment_rows.to_dict("records"):
        contributors = expected_segments[segment["SegmentID"]]
        assert_number(segment["cnt"], len(contributors), ("map count", segment["SegmentID"]))
        for field, source in {"total_hits": "hits", "total_misses": "misses", "total_opportunities": "opportunities", "total_target_only": "target_only"}.items():
            assert_number(segment[field], sum(station[source] for station in contributors), ("map", segment["SegmentID"], field))
        assert_number(segment["val"], round(statistics.mean(station["rate_pct"] for station in contributors), 1), ("map balanced", segment["SegmentID"]))
        assert_number(segment["pooled_rate_pct"], round(100 * sum(station["hits"] for station in contributors) / sum(station["opportunities"] for station in contributors), 1), ("map pooled", segment["SegmentID"]))
    for index, expected in enumerate(profiles["distance"]):
        for column, source in {"distance_qualifying_station_counts": "station_count", "distance_target_station_counts": "target_station_count", "distance_peer_reach_pct": "peer_reach_pct", "distance_station_balanced_rate_pct": "station_balanced_rate_pct", "distance_observation_level_rate_pct": "pooled_rate_pct", "distance_confirmed_opportunity_counts": "opportunities", "distance_target_counts": "hits", "distance_counter_counts": "misses", "distance_successful_snr_median_db": "snr_median"}.items():
            assert_number(recipes["distance"][column][index], expected[source], ("distance", index, column))
        if expected["snr_count"] >= 3:
            assert_number(recipes["distance"]["distance_successful_snr_interval_lower_db"][index], expected["snr_q1"], ("distance", index, "q1"))
            assert_number(recipes["distance"]["distance_successful_snr_interval_upper_db"][index], expected["snr_q3"], ("distance", index, "q3"))
    for scope, recipe_name in (("all", "segment_temporal"), ("VE6PDQ", "selected_temporal")):
        recipe = recipes[recipe_name]
        for kind, actual in (("chronological", recipe["chronological_profiles"]["3h"]), ("folded", recipe["folded_profile"])):
            for index, expected in enumerate(profiles["temporal"][scope][kind]):
                for column, source in {"opportunity_success_counts": "hits", "opportunity_counter_counts": "misses", "station_counts": "station_count", "station_balanced_rate_pct": "station_balanced_rate_pct", "observation_level_rate_pct": "rate_pct"}.items():
                    assert_number(actual[column][index], expected[source], (scope, kind, index, column))
                prefix = "snr_station_balanced" if scope == "all" else "snr"
                assert_number(actual[prefix + "_median_db"][index], expected["snr_median"], (scope, kind, index, "snr median"))
                for quartile in ("q1", "q3"):
                    assert_number(actual[prefix + f"_{quartile}_db"][index], expected[f"snr_{quartile}"], (scope, kind, index, quartile))
    selected = recipes["selected_temporal"]["selected_station_summary"]
    expected = expected_stations[("VE6PDQ", "DO34IR")]
    for field, source in {"confirmed_opportunities": "opportunities", "successful_outcomes": "hits", "counter_outcomes": "misses", "success_rate_pct": "rate_pct", "successful_snr_median_db": "successful_snr_median"}.items():
        assert_number(selected[field], expected[source], ("selected", field))


def write_review_report(output, independent, production):
    """Write review handoff arithmetic without granting human approval."""
    before, after = independent["before"], independent["after"]
    old_station, new_station = before["ve6pdq"], after["ve6pdq"]
    old_population, new_population = before["eligible_population"], after["eligible_population"]
    lines = [
        "# Performance method revision: frozen Milazzo verification, 2026-09-25", "",
        "This is an automated verification and review-impact report. It does not approve or mark any human-review card. The original PDF, raw-source archive, card expectations and current review-status files are unchanged.", "",
        "The independent oracle reads only `production_performance.config` and `network_source.parquet` from the frozen packet. It derives both historical opportunity-v2 and revised opportunity-v3 arithmetic from raw report IDs; no old card expectation or application output defines the expected values.", "",
        "The Target TX is KP4MD / CM98. Each receiver is a peer RX identified by its exact callsign plus full locator. A report KP4MD -> peer RX confirms both Target TX transmission and that peer RX reception. An external TX -> the same peer RX report confirms that particular peer RX was listening. A KP4MD -> another RX report confirms the Target TX cycle only; it cannot prove a silent peer RX was listening.", "",
        f"Source: {independent['source']['source_rows']:,} frozen 40m reports, 2010-12-19 12:00 <= UTC < 2010-12-20 20:00; {independent['source']['target_active_cycles']} Target-active cycles; {independent['source']['native_peer_cycles']:,} retained peer-cycle rows; radius strictly below 5,000 km; minimum five opportunities. Historical code=0 fallback is explicit. Source SHA-256: `{independent['source_sha256']}`.", "",
        "| Quantity | Before (opportunity-v2) | After (opportunity-v3) |",
        "| --- | ---: | ---: |",
        f"| VE6PDQ successes / opportunities | {old_station['hits']} / {old_station['opportunities']} | {new_station['hits']} / {new_station['opportunities']} |",
        f"| VE6PDQ rate | {old_station['rate_pct']:.7f}% | {new_station['rate_pct']:.7f}% |",
        f"| VE6PDQ Misses | {old_station['misses']} | {new_station['misses']} |",
        "| VE6PDQ Target-only provenance subset | 22 excluded from successes | 22 already included in 57 successes |",
        f"| VE6PDQ successful-SNR median | {old_station['successful_snr_median']} dB | {new_station['successful_snr_median']} dB |",
        f"| VE6PDQ successful-SNR Q1 / Q3 | {old_station['successful_snr_q1']:g} / {old_station['successful_snr_q3']:g} dB | {new_station['successful_snr_q1']:g} / {new_station['successful_snr_q3']:g} dB |",
        f"| VE6PDQ successful-SNR min / max | {old_station['successful_snr_min']} / {old_station['successful_snr_max']} dB | {new_station['successful_snr_min']} / {new_station['successful_snr_max']} dB |",
        f"| Qualified peer RX population | {before['eligible_stations']} | {after['eligible_stations']} |",
        f"| Qualified population successes / opportunities | {old_population['hits']} / {old_population['opportunities']} | {new_population['hits']} / {new_population['opportunities']} |",
        f"| Qualified population station-balanced rate | {old_population['station_balanced_rate_pct']:.7f}% | {new_population['station_balanced_rate_pct']:.7f}% |",
        f"| Qualified population pooled rate | {old_population['rate_pct']:.7f}% | {new_population['rate_pct']:.7f}% |",
        f"| Qualified population Misses | {old_population['misses']} | {new_population['misses']} |",
        "| All 102 peer RX identities, Misses | 1,445 | 1,445 |", "",
        "The qualified population adds K7LRB / DM41MW (4 -> 5 opportunities), NN6RF / CM87UW (4 -> 6), and VE7VI / CN89FJ (3 -> 12). The two added qualified-population Misses belong to newly eligible VE7VI; no individual native row changes from another class into a Miss.", "",
        "## Card impacts for the ongoing review task", "",
        "All Performance cards need method/role audit and the requested Target TX -> peer RX arrow. Numeric changes apply to P01-P07 and P09-P10. P08's two sampled hours remain numerically unchanged. Benchmark B01-B04 calculations are unchanged; role/arrow presentation belongs to the review task.", "",
        "| Card | Source-derived consequence |", "| --- | --- |",
        "| P01 | Three example rows become 2 successes / 3 opportunities = 66.6667%; 1 Miss; Target-only remains provenance of one success. The excluded Target-inactive example remains excluded. |",
        "| P02 | VE6PDQ becomes 57 / 79 = 72.1519%; its 22 Target-only successes must be included once in both numerator and denominator. |",
        "| P03 | 57 successful SNRs; median -23, Q1 -29, Q3 -22, minimum -35, maximum -14 dB. |",
        "| P04 | East segment remains five peers; 49 / 97 -> 56 / 104. Station-balanced 63.9686% -> 65.8528%; pooled 50.5155% -> 53.8462%. |",
        "| P05 | 1500-2000 km: 50 / 78 -> 75 / 103; station-balanced 65.3396% -> 71.4580%; pooled 64.1026% -> 72.8155%. Reach stays 3/3. Station-median SNR trace stays -22 dB; IQR [-23.5,-20.5] -> [-22.5,-21] dB. |",
        "| P06 | 4000-4500 km: 30 / 277 -> 34 / 281; pooled 10.8303% -> 12.0996%. Peer Reach stays 4/6 = 66.6667%. |",
        "| P07 | VE6PDQ 00:00-03:00 UTC: 5 / 8 -> 6 / 9 = 66.6667%; SNR median -22 -> -22.5 dB, IQR [-23,-20] -> [-23,-20.5] dB. |",
        "| P08 | 12/20 UTC counts, 0% rates, represented-date normalization and mean support remain unchanged; method terminology requires audit. |",
        "| P09 | VE6PDQ 16 UTC: 7 -> 9 successes, two date-hour medians still contribute; folded SNR marker -25 -> -25.5 dB. IQR remains visually suppressed for two values. |",
        "| P10 | Final partial-bin station SNR-anomaly median 0 -> +1.5 dB; Q1/Q3 [-3.25,+1.75] -> [-3,+3] dB; seven -> nine station values. VE6PDQ's -33 dB sample is now -10 dB relative to its -23 dB baseline. |", "",
        "## Production comparison and limits", "",
        f"Production method `{production['method']}`: generated strict/legacy SQL executes against the frozen source, then actual post-fetch processing, map aggregation and InspectorPreparation run. All {production['processed_rows']:,} native rows and all station identities, thresholds, rates and successful-SNR medians agree with the independent oracle. All map segments, distance rates and Peer Reach, every 3-hour/folded rate, every prepared SNR median/quartile, and the VE6PDQ selected-station summary agree.", "",
        "The source contains no duplicate Target-report groups after the frozen filters; duplicate reduction is covered by separate hand-checked RX/TX regression contracts. This TX packet does not independently validate RX. SQL runs through the regression SQLite dialect adapter, not native ClickHouse. This replay verifies production recipe values, not rendered pixels or browser interaction; it does not construct a new full export package. Temporal recipes retain quartiles while their renderer separately enforces visible-IQR support requirements.", "",
        "Artifacts: `independent_before_ledger.csv`, `independent_after_ledger.csv`, both station ledgers and profile JSON files, `independent_summary.json`, generated SQL, production processed Parquet/CSV, station/map/Station Insights tables, `production_recipes.json`, `production_after_summary.json`, `affected_cards.json`, and protected-file SHA-256 verification. Original packet preservation and Benchmark reference fixture verification are separate from scientific human approval.", "",
    ]
    (output / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    """Run a read-only source replay and write only a separate diagnostic report."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-directory", type=Path, default=REPOSITORY / "output/milazzo_review_v1", help="Read-only frozen packet containing production_performance.config and network_source.parquet")
    parser.add_argument("--output-directory", type=Path, default=REPOSITORY / ".tmp/performance_method_revision_2026-09-25", help="Separate report directory; it must not overlap the source or frozen reference directories")
    arguments = parser.parse_args()
    source_directory = arguments.source_directory.resolve()
    output = arguments.output_directory.resolve()
    protected_directories = (
        source_directory,
        (REPOSITORY / "output/milazzo_review_v1").resolve(),
        (REPOSITORY / "tests/regression/reference_fixtures").resolve(),
        (REPOSITORY / "output/pdf").resolve(),
    )
    for protected_directory in protected_directories:
        if output == protected_directory or protected_directory in output.parents or output in protected_directory.parents:
            parser.error(f"Output directory must not overlap protected input directory: {protected_directory}")
    output.mkdir(parents=True, exist_ok=True)
    document = json.loads((source_directory / "production_performance.config").read_text(encoding="utf-8"))
    source = pd.read_parquet(source_directory / "network_source.parquet")
    ledger, metadata, start, end = independent_evidence(document, source)
    minimum = document["settings"]["advanced_parameters"]["min_confirmed_opportunities_per_peer"]
    variants = {}
    for method, include_target_only in (("before", False), ("after", True)):
        rows, stations, selected, summary = independent_method(ledger, minimum, include_target_only)
        profiles = independent_profiles(stations, selected, start, end)
        variants[method] = (rows, stations, selected, summary, profiles)
        pd.DataFrame(rows).to_csv(output / f"independent_{method}_ledger.csv", index=False)
        pd.DataFrame(stations).to_csv(output / f"independent_{method}_stations.csv", index=False)
        write_json(output / f"independent_{method}_profiles.json", profiles)
    before = variants["before"][3]
    after = variants["after"][3]
    previously_eligible = {(station["peer_sign"], station["peer_grid"]) for station in variants["before"][1] if station["eligible"]}
    newly_eligible = [station for station in variants["after"][1] if station["eligible"] and (station["peer_sign"], station["peer_grid"]) not in previously_eligible]
    independent = {"source_sha256": hashlib.sha256((source_directory / "network_source.parquet").read_bytes()).hexdigest(), "configuration_sha256": hashlib.sha256((source_directory / "production_performance.config").read_bytes()).hexdigest(), "source": metadata, "before": before, "after": after, "newly_eligible": newly_eligible}
    write_json(output / "independent_summary.json", independent)
    print(f"Independent: VE6PDQ {before['ve6pdq']['hits']}/{before['ve6pdq']['opportunities']} -> {after['ve6pdq']['hits']}/{after['ve6pdq']['opportunities']}; qualified receivers {before['eligible_stations']} -> {after['eligible_stations']}; station-balanced {after['eligible_population']['station_balanced_rate_pct']:.7f}%.", flush=True)
    processed, map_data, recipes, production = production_replay(document, source, output)
    assert production["method"] in {"opportunity-v2", "opportunity-v3"}, production["method"]
    method = "before" if production["method"] == "opportunity-v2" else "after"
    rows, stations, _, _, profiles = variants[method]
    compare_production(rows, stations, profiles, processed, map_data, recipes)
    production["independent_comparison"] = "passed"
    production["verified_surfaces"] = ["generated SQL", "native peer-cycle flags and SNR", "station thresholds", "station counts and successful-SNR medians", "all map segments", "distance rates, Peer Reach and SNR medians/IQR", "chronological and folded rates", "chronological and folded SNR medians and IQR", "selected-station summary"]
    write_json(output / f"production_{method}_summary.json", production)
    # Card data is first opened only after source arithmetic and the production
    # comparison. It is used to identify review impacts, never as an oracle.
    cards = json.loads((source_directory / "review_cards.json").read_text(encoding="utf-8"))
    impacts = [{"id": card["id"], "title": card["title"], "requires_regeneration_and_human_review": card["id"].startswith("P"), "reason": "Example quantities unchanged; Performance method wording and station roles require review" if card["id"] == "P08" else "Performance success/opportunity and successful-SNR population changed" if card["id"].startswith("P") else "Benchmark method unchanged; roles and direction arrows remain an ongoing-review presentation task"} for card in cards]
    write_json(output / "affected_cards.json", impacts)
    write_review_report(output, independent, production)
    baseline = output / "protected_files_before.json"
    if baseline.exists():
        protected = json.loads(baseline.read_text(encoding="utf-8-sig"))
        changed = [entry["path"] for entry in protected if not (REPOSITORY / entry["path"]).is_file() or hashlib.sha256((REPOSITORY / entry["path"]).read_bytes()).hexdigest() != entry["sha256"]]
        write_json(output / "protected_files_verification.json", {"files_checked": len(protected), "changed_files": changed})
        assert not changed, changed
    print(f"Independent vs production {method} comparison passed; original review files were not written.", flush=True)


if __name__ == "__main__":
    main()
