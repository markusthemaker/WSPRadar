"""Calculate the bounded Milazzo TX reference using Python's standard library.

This maintenance calculator reads frozen raw reports and scientific configuration,
never WSPRadar runtime functions or prepared results. Build candidate expectations
separately; regression tests must not refresh the installed reference in place.
Publication facts and archive-to-publication mappings are separate evidence.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timedelta, timezone
import json
import math
from pathlib import Path
from statistics import mean, median, stdev


SQL_FIELDS = [
    "time_slot", "peer_sign", "peer_grid", "peer_lat", "peer_lon",
    "snr_u_norm", "snr_r_norm", "has_u", "has_r",
]
GROUP_FIELDS = [
    *SQL_FIELDS, "evidence_utc", "target_report_ids", "reference_report_ids",
    "target_selected_report_ids", "reference_selected_report_ids",
    "distance_km", "bearing_degrees", "is_target_active", "outcome", "selection_reason",
]
UNIT_FIELDS = [
    "time_slot", "evidence_utc", "peer_sign", "peer_grid", "outcome",
    "target_report_ids", "reference_report_ids", "target_selected_report_ids",
    "reference_selected_report_ids", "target_report_snr_db", "reference_report_snr_db",
    "target_report_power_dbm", "reference_report_power_dbm", "target_snr_db",
    "reference_snr_db", "delta_snr_db", "distance_km", "bearing_degrees",
]
STATISTIC_FIELDS = [
    "mean_delta_snr_db", "median_delta_snr_db", "q1_delta_snr_db", "q3_delta_snr_db",
    "sample_std_delta_snr_db", "min_delta_snr_db", "max_delta_snr_db",
]
OUTCOMES = ("target_only", "joint", "reference_only")


def _parse_utc(timestamp_text):
    timestamp = datetime.fromisoformat(timestamp_text.replace("Z", "+00:00"))
    if timestamp.tzinfo is None:
        raise ValueError("Source and configuration timestamps must specify UTC")
    return timestamp.astimezone(timezone.utc)


def _utc_from_cycle(cycle):
    return datetime.fromtimestamp(cycle * 120, timezone.utc).isoformat()


def _distance_and_bearing(latitude, longitude):
    # Four-character CM98 cell center, independently decoded from Maidenhead.
    center_latitude = math.radians(38.5)
    center_longitude = math.radians(-121)
    latitude, longitude = map(math.radians, (latitude, longitude))
    longitude_difference = longitude - center_longitude
    haversine = (
        math.sin((latitude - center_latitude) / 2) ** 2
        + math.cos(center_latitude) * math.cos(latitude)
        * math.sin(longitude_difference / 2) ** 2
    )
    distance_km = 6371 * 2 * math.asin(min(1, math.sqrt(haversine)))
    bearing_degrees = math.degrees(math.atan2(
        math.sin(longitude_difference) * math.cos(latitude),
        math.cos(center_latitude) * math.sin(latitude)
        - math.sin(center_latitude) * math.cos(latitude) * math.cos(longitude_difference),
    )) % 360
    return distance_km, bearing_degrees


def _summarize(differences):
    if not differences:
        return {field: None for field in STATISTIC_FIELDS}
    ordered = sorted(differences)

    def quartile(probability):
        position = (len(ordered) - 1) * probability
        lower = int(position)
        fraction = position - lower
        return ordered[lower] if not fraction else (
            ordered[lower] + fraction * (ordered[lower + 1] - ordered[lower])
        )

    return {
        "mean_delta_snr_db": mean(differences), "median_delta_snr_db": median(differences),
        "q1_delta_snr_db": quartile(0.25), "q3_delta_snr_db": quartile(0.75),
        "sample_std_delta_snr_db": stdev(differences) if len(differences) > 1 else None,
        "min_delta_snr_db": min(differences), "max_delta_snr_db": max(differences),
    }


def _write_csv(path, records, fields):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def _report_ids(reports):
    return ";".join(report["id"] for report in reports)


def _normalized_snr(report):
    return int(report["snr"]) - int(report["power"]) + 30


def _endpoint_components(reports):
    if not reports:
        return None, [], None
    maximum = max(_normalized_snr(report) for report in reports)
    selected = [report for report in reports if _normalized_snr(report) == maximum]
    return maximum, selected, selected[0]


def _require_reference_contract(condition, message):
    if not condition:
        raise ValueError(message)


def calculate_reference(source_path, config_path, output_directory):
    """Write deterministic independent expectations and return their summary."""
    source_path = Path(source_path).resolve()
    config_path = Path(config_path).resolve()
    output_directory = Path(output_directory).resolve()
    installed_references = (
        Path(__file__).resolve().parent.parent / "tests" / "regression" / "reference_fixtures"
    ).resolve()
    if output_directory.is_relative_to(installed_references):
        raise ValueError("Build into a separate candidate directory, outside installed reference_fixtures")
    if output_directory in (source_path.parent, config_path.parent):
        raise ValueError("The output directory must differ from the source and configuration directories")
    document = json.loads(config_path.read_text(encoding="utf-8"))
    settings = document["settings"]
    core = settings["core_parameters"]
    comparison = settings["comparison_parameters"]
    advanced = settings["advanced_parameters"]
    # Deliberately fail closed outside this one historical scientific contract.
    _require_reference_contract(core["analysis_direction"] == "tx" and core["band"] == "40m", "Expected TX analysis on 40m")
    _require_reference_contract(core["callsign"] == "KP4MD" and core["qth"] == "CM98", "Expected Target KP4MD at CM98")
    _require_reference_contract(comparison["mode"] == "reference_station", "Expected reference-station comparison")
    _require_reference_contract(comparison["reference_callsign"] == "WB6RQN" and comparison["reference_qth"] == "CM98", "Expected Reference WB6RQN at CM98")
    _require_reference_contract(comparison["snr_correction_mode"] == "no_offset" and comparison["snr_correction_db"] == 0, "Expected no SNR correction")
    _require_reference_contract(advanced["max_peer_distance_km"] == 5000 and advanced["solar_state"] == "all", "Expected 5000 km radius and all solar states")
    _require_reference_contract(not advanced["exclude_special_callsigns"] and not advanced["exclude_moving_stations"], "Expected no special-callsign or moving-station exclusions")
    _require_reference_contract(advanced["min_joint_spots_per_station"] == 1, "Expected station minimum of one Joint spot")
    start = _parse_utc(core["time_selection"]["start_utc"])
    end = _parse_utc(core["time_selection"]["end_utc"])
    _require_reference_contract(start == _parse_utc("2010-12-18T00:00Z") and end == _parse_utc("2010-12-21T00:00Z"), "Expected the frozen 18-21 December 2010 half-open UTC window")
    with source_path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        source_fields = list(reader.fieldnames)
        reports = list(reader)
    _require_reference_contract(len({report["id"] for report in reports}) == len(reports), "Repeated source report ID")
    groups = defaultdict(lambda: {"target": [], "reference": [], "coordinates": set()})
    for report in reports:
        timestamp = _parse_utc(report["time"])
        # All codes are retained explicitly for the captured legacy-mode window.
        _require_reference_contract(int(report["band"]) == 7 and int(report["code"]) == 0, f"Unexpected band or decode code in report {report['id']}")
        _require_reference_contract(start <= timestamp < end and timestamp.timestamp() % 120 == 0, f"Report {report['id']} is outside the window or not aligned to a 120-second cycle")
        _require_reference_contract(report["tx_sign"] in (core["callsign"], comparison["reference_callsign"]), f"Unexpected transmitter in report {report['id']}")
        _require_reference_contract(report["tx_loc"].startswith("CM98") and float(report["rx_lat"]) != 0, f"Unexpected endpoint locator or zero receiver latitude in report {report['id']}")
        identity = (int(timestamp.timestamp()) // 120, report["rx_sign"], report["rx_loc"])
        side = "target" if report["tx_sign"] == core["callsign"] else "reference"
        groups[identity][side].append(report)
        groups[identity]["coordinates"].add((float(report["rx_lat"]), float(report["rx_lon"])))

    active_witnesses = defaultdict(list)
    for identity, group in groups.items():
        active_witnesses[identity[0]].extend(group["target"])
    active_witnesses = {cycle: witnesses for cycle, witnesses in active_witnesses.items() if witnesses}
    query_rows, retained_rows, classified_rows, units, ledger = [], [], [], [], []
    station_groups = defaultdict(list)
    for (cycle, callsign, locator), group in sorted(groups.items()):
        _require_reference_contract(len(group["coordinates"]) == 1, "Ambiguous within-group receiver coordinates")
        latitude, longitude = next(iter(group["coordinates"]))
        target_reports = sorted(group["target"], key=lambda report: int(report["id"]))
        reference_reports = sorted(group["reference"], key=lambda report: int(report["id"]))
        target_snr, target_selected, target_representative = _endpoint_components(target_reports)
        reference_snr, reference_selected, reference_representative = _endpoint_components(reference_reports)
        outcome = "joint" if target_reports and reference_reports else (
            "target_only" if target_reports else "reference_only"
        )
        distance_km, bearing_degrees = _distance_and_bearing(latitude, longitude)
        is_target_active = cycle in active_witnesses
        reason = "excluded_target_inactive" if not is_target_active else (
            "excluded_distance" if distance_km >= advanced["max_peer_distance_km"] else "retained"
        )
        query_row = {
            "time_slot": cycle, "peer_sign": callsign, "peer_grid": locator,
            "peer_lat": latitude, "peer_lon": longitude,
            "snr_u_norm": target_snr if target_reports else 0,
            "snr_r_norm": reference_snr if reference_reports else 0,
            "has_u": len(target_reports), "has_r": len(reference_reports),
        }
        query_rows.append(query_row)
        classified_rows.append({
            **query_row, "evidence_utc": _utc_from_cycle(cycle),
            "target_report_ids": _report_ids(target_reports),
            "reference_report_ids": _report_ids(reference_reports),
            "target_selected_report_ids": _report_ids(target_selected),
            "reference_selected_report_ids": _report_ids(reference_selected),
            "distance_km": distance_km, "bearing_degrees": bearing_degrees,
            "is_target_active": int(is_target_active), "outcome": outcome, "selection_reason": reason,
        })
        for side, side_reports, selected_reports in (
            ("target", target_reports, target_selected),
            ("reference", reference_reports, reference_selected),
        ):
            selected_ids = {report["id"] for report in selected_reports}
            for report in side_reports:
                ledger.append({
                    **report, "time_slot": cycle, "evidence_utc": _utc_from_cycle(cycle),
                    "peer_sign": callsign, "peer_grid": locator, "endpoint": side,
                    "normalized_snr_db": _normalized_snr(report),
                    "is_endpoint_maximum": int(report["id"] in selected_ids),
                    "is_target_active": int(is_target_active), "outcome": outcome,
                    "selection_reason": reason, "distance_km": distance_km,
                })
        if reason != "retained":
            continue
        retained_rows.append(query_row)
        unit = {
            "time_slot": cycle, "evidence_utc": _utc_from_cycle(cycle),
            "peer_sign": callsign, "peer_grid": locator, "outcome": outcome,
            "target_report_ids": _report_ids(target_reports),
            "reference_report_ids": _report_ids(reference_reports),
            "target_selected_report_ids": _report_ids(target_selected),
            "reference_selected_report_ids": _report_ids(reference_selected),
            "target_report_snr_db": int(target_representative["snr"]) if target_reports else None,
            "reference_report_snr_db": int(reference_representative["snr"]) if reference_reports else None,
            "target_report_power_dbm": int(target_representative["power"]) if target_reports else None,
            "reference_report_power_dbm": int(reference_representative["power"]) if reference_reports else None,
            "target_snr_db": target_snr, "reference_snr_db": reference_snr,
            "delta_snr_db": target_snr - reference_snr if outcome == "joint" else None,
            "distance_km": distance_km, "bearing_degrees": bearing_degrees,
        }
        units.append(unit)
        station_groups[(callsign, locator)].append(unit)

    paired_rows = [unit for unit in units if unit["outcome"] == "joint"]
    station_rows = []
    for (callsign, locator), station_units in sorted(station_groups.items()):
        counts = Counter(unit["outcome"] for unit in station_units)
        station_rows.append({
            "peer_sign": callsign, "peer_grid": locator, "native_units": len(station_units),
            **{outcome: counts[outcome] for outcome in OUTCOMES},
            "joint_evidence_share": counts["joint"] / len(station_units),
            **_summarize([unit["delta_snr_db"] for unit in station_units if unit["outcome"] == "joint"]),
        })
    active_rows = [{
        "time_slot": cycle, "evidence_utc": _utc_from_cycle(cycle),
        "target_witness_report_ids": _report_ids(sorted(witnesses, key=lambda report: int(report["id"]))),
        "target_witness_report_count": len(witnesses),
    } for cycle, witnesses in sorted(active_witnesses.items())]
    ve6pdq_units = [unit for unit in units if unit["peer_sign"] == "VE6PDQ"]
    ve6pdq_reports = [report for report in reports if report["rx_sign"] == "VE6PDQ"]
    gated_groups = [group for group in classified_rows if group["is_target_active"]]
    coverage_rows = []
    for scope, scoped_units in (("all", units), ("VE6PDQ", ve6pdq_units)):
        for bin_index in range(24):
            bin_start = start + timedelta(hours=3 * bin_index)
            bin_end = bin_start + timedelta(hours=3)
            bin_units = [unit for unit in scoped_units if bin_start.timestamp() <= unit["time_slot"] * 120 < bin_end.timestamp()]
            counts = Counter(unit["outcome"] for unit in bin_units)
            station_totals = Counter((unit["peer_sign"], unit["peer_grid"]) for unit in bin_units)
            station_joint = Counter((unit["peer_sign"], unit["peer_grid"]) for unit in bin_units if unit["outcome"] == "joint")
            coverage_rows.append({
                "scope": scope, "bin_index": bin_index,
                "bin_start_utc": bin_start.isoformat(), "bin_end_utc": bin_end.isoformat(),
                **{outcome: counts[outcome] for outcome in OUTCOMES},
                "native_units": len(bin_units), "station_count": len(station_totals),
                "pooled_joint_share_pct": 100 * counts["joint"] / len(bin_units) if bin_units else None,
                "station_balanced_joint_share_pct": mean(100 * station_joint[station] / count for station, count in station_totals.items()) if station_totals else None,
            })
    summary = {
        "derivation": "Independent stdlib arithmetic from source reports/configuration; no WSPRadar imports or output inputs",
        "window_start_utc": start.isoformat(), "window_end_utc": end.isoformat(),
        "center_latitude": 38.5, "center_longitude": -121.0, "radius_km": advanced["max_peer_distance_km"],
        "radius_comparison": "strictly less than", "normalization": "reported SNR - reported power dBm + 30",
        "source_rows": len(reports), "selected_source_rows": len(reports),
        "source_code_counts": dict(sorted(Counter(report["code"] for report in reports).items())),
        "source_endpoint_counts": dict(sorted(Counter(report["tx_sign"] for report in reports).items())),
        "sql_group_count": len(query_rows), "target_active_cycles": len(active_rows),
        "target_active_group_count": len(gated_groups), "retained_group_count": len(units),
        "all_group_outcomes": dict(Counter(group["outcome"] for group in classified_rows)),
        "target_active_outcomes_before_distance": dict(Counter(group["outcome"] for group in gated_groups)),
        "retained_outcomes": {outcome: sum(unit["outcome"] == outcome for unit in units) for outcome in OUTCOMES},
        "selection_reasons": dict(Counter(group["selection_reason"] for group in classified_rows)),
        "source_ledger_selection_reasons": dict(Counter(report["selection_reason"] for report in ledger)),
        "duplicate_endpoint_groups": sum(len(group[side]) > 1 for group in groups.values() for side in ("target", "reference")),
        "station_count": len(station_rows), "paired_station_count": sum(row["joint"] > 0 for row in station_rows),
        "joint_spots": len(paired_rows), "joint_cycles": len({unit["time_slot"] for unit in paired_rows}),
        "coverage_bin_seconds": 10800, "coverage_bins_per_scope": 24,
        "coverage_scopes": ["all", "VE6PDQ"],
        "non_joint_metric_policy": "Absent endpoint components and delta_snr_db are null; SQL absent-side aggregate alone is zero",
        "ve6pdq": {
            "source_rows": len(ve6pdq_reports),
            "source_endpoint_counts": dict(Counter(report["tx_sign"] for report in ve6pdq_reports)),
            "receiver_locators": sorted({report["rx_loc"] for report in ve6pdq_reports}),
            "retained_outcomes": {outcome: sum(unit["outcome"] == outcome for unit in ve6pdq_units) for outcome in OUTCOMES},
            "joint_rows": [unit for unit in ve6pdq_units if unit["outcome"] == "joint"],
        },
        **_summarize([unit["delta_snr_db"] for unit in paired_rows]),
    }
    output_directory.mkdir(parents=True, exist_ok=True)
    ledger_fields = [
        *source_fields, "time_slot", "evidence_utc", "peer_sign", "peer_grid", "endpoint",
        "normalized_snr_db", "is_endpoint_maximum", "is_target_active", "outcome",
        "selection_reason", "distance_km",
    ]
    for filename, records, fields in (
        ("expected_sql_rows.csv", query_rows, SQL_FIELDS),
        ("expected_retained_rows.csv", retained_rows, SQL_FIELDS),
        ("expected_classified_groups.csv", classified_rows, GROUP_FIELDS),
        ("expected_source_ledger.csv", sorted(ledger, key=lambda report: int(report["id"])), ledger_fields),
        ("expected_native_units.csv", units, UNIT_FIELDS),
        ("expected_paired_rows.csv", paired_rows, UNIT_FIELDS),
        ("expected_active_cycles.csv", active_rows, ["time_slot", "evidence_utc", "target_witness_report_ids", "target_witness_report_count"]),
        ("expected_station_rows.csv", station_rows, ["peer_sign", "peer_grid", "native_units", *OUTCOMES, "joint_evidence_share", *STATISTIC_FIELDS]),
        ("expected_coverage_3h.csv", coverage_rows, ["scope", "bin_index", "bin_start_utc", "bin_end_utc", *OUTCOMES, "native_units", "station_count", "pooled_joint_share_pct", "station_balanced_joint_share_pct"]),
    ):
        _write_csv(output_directory / filename, records, fields)
    (output_directory / "expected_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n",
    )
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-csv", required=True, type=Path)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output-directory", required=True, type=Path)
    arguments = parser.parse_args()
    summary = calculate_reference(arguments.source_csv, arguments.config, arguments.output_directory)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
