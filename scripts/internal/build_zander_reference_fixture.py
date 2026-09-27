"""Independently calculate Zander Experiment A expectations from frozen reports.

This explicit maintenance command uses only the Python standard library. It
does not import WSPRadar or read its calculated results. Tests never invoke it
to refresh expectations. Review output before replacing any installed fixture.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import json
import math
from pathlib import Path
from statistics import mean, median, stdev


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


def _quartile(values, probability):
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    fraction = position - lower
    return ordered[lower] if not fraction else (
        ordered[lower] + fraction * (ordered[lower + 1] - ordered[lower])
    )


def _write_csv(path, rows, fields):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def calculate_reference(source_path, config_path, output_directory):
    document = json.loads(config_path.read_text(encoding="utf-8"))
    settings = document["settings"]
    core = settings["core_parameters"]
    comparison = settings["comparison_parameters"]
    advanced = settings["advanced_parameters"]
    # This deliberately bounded reference implements the installed experiment,
    # not a second general-purpose application configuration interpreter.
    assert core["analysis_direction"] == "tx" and core["band"] == "20m"
    assert core["qth"] == "JO97"
    assert comparison["mode"] == "hardware_ab"
    assert comparison["tx_ab_method"] == "simultaneous"
    assert comparison["snr_correction_mode"] == "no_offset"
    assert comparison["snr_correction_db"] == 0
    assert advanced["solar_state"] == "all"
    assert not advanced["exclude_special_callsigns"]
    assert not advanced["exclude_moving_stations"]
    assert advanced["min_joint_spots_per_station"] == 1
    start = datetime.fromisoformat(core["time_selection"]["start_utc"].replace("Z", "+00:00"))
    end = datetime.fromisoformat(core["time_selection"]["end_utc"].replace("Z", "+00:00"))
    target = core["callsign"]
    reference = comparison["reference_callsign"]
    center_latitude, center_longitude = 57.5, 19.0  # JO97 cell center.
    with source_path.open(encoding="utf-8") as stream:
        source_rows = list(csv.DictReader(stream))
    groups = defaultdict(lambda: {"target": [], "reference": [], "coordinates": set()})
    selected_report_count = 0
    for report in source_rows:
        timestamp = datetime.fromisoformat(report["time"])
        if not (
            int(report["band"]) == 14 and int(report["code"]) == 1
            and start <= timestamp < end and float(report["rx_lat"]) != 0
            and report["tx_loc"][:4] == core["qth"]
            and report["tx_sign"] in (target, reference)
        ):
            continue
        selected_report_count += 1
        identity = (int(timestamp.timestamp()) // 120, report["rx_sign"], report["rx_loc"])
        group = groups[identity]
        group["coordinates"].add((float(report["rx_lat"]), float(report["rx_lon"])))
        group["target" if report["tx_sign"] == target else "reference"].append(report)

    active_cycles = {identity[0] for identity, group in groups.items() if group["target"]}
    query_rows, retained_rows, paired_rows = [], [], []
    outcomes = Counter()
    for (cycle, callsign, locator), group in sorted(groups.items()):
        assert len(group["coordinates"]) == 1, "Ambiguous any-coordinate aggregate"
        latitude, longitude = next(iter(group["coordinates"]))
        target_snr = max((int(row["snr"]) - int(row["power"]) + 30 for row in group["target"]), default=0)
        reference_snr = max((int(row["snr"]) - int(row["power"]) + 30 for row in group["reference"]), default=0)
        query_row = {
            "time_slot": cycle, "peer_sign": callsign, "peer_grid": locator,
            "peer_lat": latitude, "peer_lon": longitude,
            "snr_u_norm": target_snr, "snr_r_norm": reference_snr,
            "has_u": len(group["target"]), "has_r": len(group["reference"]),
        }
        query_rows.append(query_row)
        distance_km, bearing_degrees = _distance_and_bearing(
            latitude, longitude, center_latitude, center_longitude,
        )
        if cycle not in active_cycles or distance_km >= advanced["max_peer_distance_km"]:
            continue
        retained_rows.append(query_row)
        outcome = "joint" if group["target"] and group["reference"] else (
            "target_only" if group["target"] else "reference_only"
        )
        outcomes[outcome] += 1
        if outcome != "joint":
            continue
        paired_rows.append({
            "time_slot": cycle,
            "evidence_utc": datetime.fromtimestamp(cycle * 120, timezone.utc).isoformat(),
            "peer_sign": callsign, "peer_grid": locator,
            "target_snr_db": target_snr, "reference_snr_db": reference_snr,
            "delta_snr_db": target_snr - reference_snr,
            "distance_km": distance_km, "bearing_degrees": bearing_degrees,
            "target_report_ids": ";".join(row["id"] for row in group["target"]),
            "reference_report_ids": ";".join(row["id"] for row in group["reference"]),
        })

    differences = [row["delta_snr_db"] for row in paired_rows]
    per_identity = defaultdict(list)
    for row in paired_rows:
        per_identity[(row["peer_sign"], row["peer_grid"])].append(row["delta_snr_db"])
    station_rows = [
        {"peer_sign": key[0], "peer_grid": key[1], "joint_spots": len(values),
         "median_delta_snr_db": median(values), "mean_delta_snr_db": mean(values)}
        for key, values in sorted(per_identity.items())
    ]
    counts = Counter(differences)
    histogram_rows = [
        {"delta_snr_db": value, "joint_spots": counts[value],
         "percent_of_sample": 100 * counts[value] / len(differences)}
        for value in range(min(differences), max(differences) + 1)
    ]
    summary = {
        "derivation": "Standard-library calculation from raw reports; no WSPRadar imports or result inputs",
        "source_rows": len(source_rows), "selected_source_rows": selected_report_count,
        "source_code_counts": dict(Counter(row["code"] for row in source_rows)),
        "sql_group_count": len(query_rows), "target_active_cycles": len(active_cycles),
        "retained_group_count": len(retained_rows), "outcomes": dict(outcomes),
        "retained_peer_identities": len({(row["peer_sign"], row["peer_grid"]) for row in retained_rows}),
        "joint_spots": len(differences), "paired_peer_identities": len(per_identity),
        "paired_cycles": len({row["time_slot"] for row in paired_rows}),
        "mean_delta_snr_db": mean(differences), "sample_std_delta_snr_db": stdev(differences),
        "median_delta_snr_db": median(differences),
        "q1_delta_snr_db": _quartile(differences, .25), "q3_delta_snr_db": _quartile(differences, .75),
        "min_delta_snr_db": min(differences), "max_delta_snr_db": max(differences),
        "negative_pairs": sum(value < 0 for value in differences),
        "zero_pairs": sum(value == 0 for value in differences),
        "positive_pairs": sum(value > 0 for value in differences),
        "pairs_1500_to_2000_km": sum(1500 <= row["distance_km"] <= 2000 for row in paired_rows),
        "pairs_southwest_quadrant": sum(180 <= row["bearing_degrees"] < 270 for row in paired_rows),
        "duplicate_endpoint_groups": sum(len(group[side]) > 1 for group in groups.values() for side in ("target", "reference")),
        "station_median_mean_db": mean(row["median_delta_snr_db"] for row in station_rows),
    }
    output_directory.mkdir(parents=True, exist_ok=True)
    for filename, rows in (
        ("expected_sql_rows.csv", query_rows), ("expected_retained_rows.csv", retained_rows),
        ("expected_paired_rows.csv", paired_rows), ("expected_station_rows.csv", station_rows),
        ("expected_histogram_1db.csv", histogram_rows),
    ):
        _write_csv(output_directory / filename, rows, list(rows[0]))
    (output_directory / "expected_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8",
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
