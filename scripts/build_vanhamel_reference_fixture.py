"""Calculate the Vanhamel RX reference from raw CSV using the standard library.

This explicit maintenance command neither imports WSPRadar nor reads its
calculated outputs. Regression tests do not run it to refresh expectations.
Run into a separate candidate directory and review changes before installation.
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
SUMMARY_FIELDS = [
    "mean_delta_snr_db", "median_delta_snr_db", "q1_delta_snr_db",
    "q3_delta_snr_db", "sample_std_delta_snr_db",
    "min_delta_snr_db", "max_delta_snr_db",
]
PAIRED_FIELDS = [
    "time_slot", "evidence_utc", "peer_sign", "peer_grid",
    "target_snr_db", "reference_snr_db", "delta_snr_db",
    "target_report_snr_db", "reference_report_snr_db",
    "target_report_power_dbm", "reference_report_power_dbm",
    "distance_km", "bearing_degrees", "target_report_ids", "reference_report_ids",
]


def _parse_utc(timestamp_text):
    timestamp = datetime.fromisoformat(timestamp_text.replace("Z", "+00:00"))
    if timestamp.tzinfo is None:
        raise ValueError("Source and configuration timestamps must specify UTC")
    return timestamp.astimezone(timezone.utc)


def _distance_and_bearing(latitude, longitude, center_latitude, center_longitude):
    latitude, longitude, center_latitude, center_longitude = map(
        math.radians, (latitude, longitude, center_latitude, center_longitude)
    )
    latitude_difference = latitude - center_latitude
    longitude_difference = longitude - center_longitude
    haversine = (
        math.sin(latitude_difference / 2) ** 2
        + math.cos(center_latitude) * math.cos(latitude)
        * math.sin(longitude_difference / 2) ** 2
    )
    distance_km = 6371 * 2 * math.asin(min(1, math.sqrt(haversine)))
    bearing_degrees = math.degrees(math.atan2(
        math.sin(longitude_difference) * math.cos(latitude),
        math.cos(center_latitude) * math.sin(latitude)
        - math.sin(center_latitude) * math.cos(latitude)
        * math.cos(longitude_difference),
    )) % 360
    return distance_km, bearing_degrees


def _quartile(differences, probability):
    ordered = sorted(differences)
    position = (len(ordered) - 1) * probability
    lower_index = int(position)
    fraction = position - lower_index
    return ordered[lower_index] if not fraction else (
        ordered[lower_index]
        + fraction * (ordered[lower_index + 1] - ordered[lower_index])
    )


def _summarize_differences(differences):
    if not differences:
        return {field: None for field in SUMMARY_FIELDS}
    return {
        "mean_delta_snr_db": mean(differences),
        "median_delta_snr_db": median(differences),
        "q1_delta_snr_db": _quartile(differences, 0.25),
        "q3_delta_snr_db": _quartile(differences, 0.75),
        "sample_std_delta_snr_db": stdev(differences) if len(differences) > 1 else None,
        "min_delta_snr_db": min(differences), "max_delta_snr_db": max(differences),
    }


def _write_csv(path, records, fields):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


def calculate_reference(source_path, config_path, output_directory):
    document = json.loads(config_path.read_text(encoding="utf-8"))
    settings = document["settings"]
    core = settings["core_parameters"]
    comparison = settings["comparison_parameters"]
    advanced = settings["advanced_parameters"]
    # This is a deliberately bounded scientific reference, not a duplicate
    # general-purpose application configuration interpreter.
    assert core["analysis_direction"] == "rx" and core["band"] == "160m"
    assert core["qth"] == "JO20OT"
    assert comparison["mode"] == "hardware_ab"
    assert comparison["snr_correction_mode"] == "establish_offset"
    assert comparison["snr_correction_db"] == 0
    assert advanced["solar_state"] == "all"
    assert not advanced["exclude_special_callsigns"]
    assert not advanced["exclude_moving_stations"]
    minimum_joint_reports = advanced["min_joint_spots_per_station"]
    assert minimum_joint_reports == 50
    start = _parse_utc(core["time_selection"]["start_utc"])
    end = _parse_utc(core["time_selection"]["end_utc"])
    assert end - start == timedelta(days=7)
    target = core["callsign"]
    reference = comparison["reference_callsign"]
    # Independent Maidenhead arithmetic: JO20 + O/T subsquares + half-cell.
    center_latitude = 50 + 19 / 24 + 1 / 48
    center_longitude = 4 + 14 / 12 + 1 / 24
    with source_path.open(encoding="utf-8") as stream:
        source_reports = list(csv.DictReader(stream))
    assert len({report["id"] for report in source_reports}) == len(source_reports)
    groups = defaultdict(lambda: {"target": [], "reference": [], "coordinates": set()})
    selected_report_count = 0
    for report in source_reports:
        timestamp = _parse_utc(report["time"])
        if not (
            int(report["band"]) == 1 and int(report["code"]) == 1
            and start <= timestamp < end and float(report["tx_lat"]) != 0
            and report["rx_loc"][:4] == core["qth"][:4]
            and report["rx_sign"] in (target, reference)
        ):
            continue
        selected_report_count += 1
        identity = (int(timestamp.timestamp()) // 120, report["tx_sign"], report["tx_loc"])
        group = groups[identity]
        group["coordinates"].add((float(report["tx_lat"]), float(report["tx_lon"])))
        group["target" if report["rx_sign"] == target else "reference"].append(report)

    active_cycles = {identity[0] for identity, group in groups.items() if group["target"]}
    query_rows, retained_rows, all_paired_rows = [], [], []
    retained_outcomes = Counter()
    station_outcomes = defaultdict(Counter)
    for (cycle, callsign, locator), group in sorted(groups.items()):
        assert len(group["coordinates"]) == 1, "Ambiguous any-coordinate aggregate"
        latitude, longitude = next(iter(group["coordinates"]))
        target_reports = group["target"]
        reference_reports = group["reference"]
        target_snr = max((int(row["snr"]) - int(row["power"]) + 30 for row in target_reports), default=0)
        reference_snr = max((int(row["snr"]) - int(row["power"]) + 30 for row in reference_reports), default=0)
        query_row = {
            "time_slot": cycle, "peer_sign": callsign, "peer_grid": locator,
            "peer_lat": latitude, "peer_lon": longitude,
            "snr_u_norm": target_snr, "snr_r_norm": reference_snr,
            "has_u": len(target_reports), "has_r": len(reference_reports),
        }
        query_rows.append(query_row)
        distance_km, bearing_degrees = _distance_and_bearing(
            latitude, longitude, center_latitude, center_longitude,
        )
        if cycle not in active_cycles or distance_km >= advanced["max_peer_distance_km"]:
            continue
        retained_rows.append(query_row)
        outcome = "joint" if target_reports and reference_reports else (
            "target_only" if target_reports else "reference_only"
        )
        retained_outcomes[outcome] += 1
        station_outcomes[(callsign, locator)][outcome] += 1
        if outcome != "joint":
            continue
        selected_target = max(target_reports, key=lambda report: int(report["snr"]) - int(report["power"]))
        selected_reference = max(reference_reports, key=lambda report: int(report["snr"]) - int(report["power"]))
        all_paired_rows.append({
            "time_slot": cycle,
            "evidence_utc": datetime.fromtimestamp(cycle * 120, timezone.utc).isoformat(),
            "peer_sign": callsign, "peer_grid": locator,
            "target_snr_db": target_snr, "reference_snr_db": reference_snr,
            "delta_snr_db": target_snr - reference_snr,
            "target_report_snr_db": int(selected_target["snr"]),
            "reference_report_snr_db": int(selected_reference["snr"]),
            "target_report_power_dbm": int(selected_target["power"]),
            "reference_report_power_dbm": int(selected_reference["power"]),
            "distance_km": distance_km, "bearing_degrees": bearing_degrees,
            "target_report_ids": ";".join(report["id"] for report in target_reports),
            "reference_report_ids": ";".join(report["id"] for report in reference_reports),
        })

    per_identity = defaultdict(list)
    for paired_row in all_paired_rows:
        per_identity[(paired_row["peer_sign"], paired_row["peer_grid"])].append(paired_row["delta_snr_db"])
    qualifying_identities = {
        identity for identity, differences in per_identity.items()
        if len(differences) >= minimum_joint_reports
    }
    paired_rows = [
        paired_row for paired_row in all_paired_rows
        if (paired_row["peer_sign"], paired_row["peer_grid"]) in qualifying_identities
    ]
    station_audit_rows = []
    for identity, outcome_counts in sorted(station_outcomes.items()):
        differences = per_identity[identity]
        station_audit_rows.append({
            "peer_sign": identity[0], "peer_grid": identity[1],
            "joint_spots": len(differences),
            "target_only_spots": outcome_counts["target_only"],
            "reference_only_spots": outcome_counts["reference_only"],
            "is_qualified": identity in qualifying_identities,
            **_summarize_differences(differences),
        })
    station_rows = [record for record in station_audit_rows if record["is_qualified"]]
    differences = [paired_row["delta_snr_db"] for paired_row in paired_rows]
    histogram_counts = Counter(differences)
    histogram_rows = [
        {"delta_snr_db": difference, "joint_spots": histogram_counts[difference],
         "percent_of_sample": 100 * histogram_counts[difference] / len(differences)}
        for difference in range(min(differences), max(differences) + 1)
    ]
    daily_rows, density_rows = [], []
    for bin_index in range(7):
        bin_start = start + timedelta(days=bin_index)
        bin_end = bin_start + timedelta(days=1)
        bin_differences = [
            paired_row["delta_snr_db"] for paired_row in paired_rows
            if bin_start.timestamp() <= paired_row["time_slot"] * 120 < bin_end.timestamp()
        ]
        daily_rows.append({
            "bin_index": bin_index, "bin_start_utc": bin_start.isoformat(),
            "bin_end_utc": bin_end.isoformat(), "joint_spots": len(bin_differences),
            **_summarize_differences(bin_differences),
        })
        bin_counts = Counter(bin_differences)
        for difference in range(min(differences), max(differences) + 1):
            density_rows.append({
                "delta_snr_bin_db": difference, "bin_index": bin_index,
                "joint_spots": bin_counts[difference],
            })
    thresholded_outcomes = Counter()
    for outcome_counts in station_outcomes.values():
        for outcome, count in outcome_counts.items():
            if count >= minimum_joint_reports:
                thresholded_outcomes[outcome] += count
    summary = {
        "derivation": "Standard-library calculation from original report CSV and fixed configuration; no WSPRadar imports or output inputs",
        "source_rows": len(source_reports), "selected_source_rows": selected_report_count,
        "source_code_counts": dict(sorted(Counter(report["code"] for report in source_reports).items())),
        "window_start_utc": start.isoformat(), "window_end_utc": end.isoformat(),
        "window_duration_hours": (end - start).total_seconds() / 3600,
        "center_latitude": center_latitude, "center_longitude": center_longitude,
        "sql_group_count": len(query_rows), "target_active_cycles": len(active_cycles),
        "retained_group_count": len(retained_rows), "retained_outcomes": dict(retained_outcomes),
        "retained_peer_identities": len(station_outcomes),
        "all_joint_spots_before_station_threshold": len(all_paired_rows),
        "all_paired_peer_identities_before_station_threshold": len([count for count in station_outcomes.values() if count["joint"]]),
        "joint_spots": len(paired_rows), "paired_peer_identities": len(qualifying_identities),
        "paired_cycles": len({paired_row["time_slot"] for paired_row in paired_rows}),
        "outcomes": dict(thresholded_outcomes),
        "minimum_joint_reports_inclusive": minimum_joint_reports,
        "peer_identities_with_exactly_50_joint_reports": sum(count["joint"] == 50 for count in station_outcomes.values()),
        **_summarize_differences(differences),
        "negative_pairs": sum(difference < 0 for difference in differences),
        "zero_pairs": sum(difference == 0 for difference in differences),
        "positive_pairs": sum(difference > 0 for difference in differences),
        "duplicate_endpoint_groups": sum(len(group[side]) > 1 for group in groups.values() for side in ("target", "reference")),
        "paired_report_power_mismatch_count": sum(row["target_report_power_dbm"] != row["reference_report_power_dbm"] for row in paired_rows),
        "station_median_mean_db": mean(record["median_delta_snr_db"] for record in station_rows),
        "station_mean_mean_db": mean(record["mean_delta_snr_db"] for record in station_rows),
        "temporal_bin_anchor": "Window start; seven consecutive 24-hour bins; station eligibility assessed over full window",
    }
    output_directory.mkdir(parents=True, exist_ok=True)
    station_fields = ["peer_sign", "peer_grid", "joint_spots", "target_only_spots", "reference_only_spots", "is_qualified", *SUMMARY_FIELDS]
    for filename, records, fields in (
        ("expected_sql_rows.csv", query_rows, SQL_FIELDS),
        ("expected_retained_rows.csv", retained_rows, SQL_FIELDS),
        ("expected_all_paired_rows.csv", all_paired_rows, PAIRED_FIELDS),
        ("expected_paired_rows.csv", paired_rows, PAIRED_FIELDS),
        ("expected_station_rows.csv", station_rows, station_fields),
        ("expected_station_audit_rows.csv", station_audit_rows, station_fields),
        ("expected_histogram_1db.csv", histogram_rows, ["delta_snr_db", "joint_spots", "percent_of_sample"]),
        ("expected_24h.csv", daily_rows, ["bin_index", "bin_start_utc", "bin_end_utc", "joint_spots", *SUMMARY_FIELDS]),
        ("expected_density_24h.csv", density_rows, ["delta_snr_bin_db", "bin_index", "joint_spots"]),
    ):
        _write_csv(output_directory / filename, records, fields)
    (output_directory / "expected_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
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
