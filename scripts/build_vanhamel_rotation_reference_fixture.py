"""Derive the Figure 6 rotation reference from raw reports, using only stdlib.

This maintenance calculator imports no WSPRadar runtime or third-party package
and reads no application outputs. Build into a separate candidate directory;
regression tests must never refresh committed expectations during a run.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timedelta, timezone
from decimal import Decimal
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
    "reception_index", "time_slot", "evidence_utc", "peer_sign", "peer_grid",
    "target_report_ids", "reference_report_ids", "target_report_snr_db",
    "reference_report_snr_db", "target_report_power_dbm",
    "reference_report_power_dbm", "target_snr_db", "reference_snr_db",
    "delta_snr_db", "distance_km", "bearing_degrees",
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
        "min_delta_snr_db": min(differences),
        "max_delta_snr_db": max(differences),
    }


def _write_csv(path, records, fields):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


def _paired_subset_summary(paired_rows):
    return {
        "joint_spots": len(paired_rows),
        "first_reception_index": paired_rows[0]["reception_index"] if paired_rows else None,
        "last_reception_index": paired_rows[-1]["reception_index"] if paired_rows else None,
        **_summarize_differences([row["delta_snr_db"] for row in paired_rows]),
    }


def calculate_reference(source_path, config_path, output_directory):
    document = json.loads(config_path.read_text(encoding="utf-8"))
    settings = document["settings"]
    core = settings["core_parameters"]
    comparison = settings["comparison_parameters"]
    advanced = settings["advanced_parameters"]
    # Fail closed: this independent oracle has one deliberately narrow scope.
    assert core["analysis_direction"] == "rx" and core["band"] == "160m"
    assert core["qth"] == "JO20OT" and core["callsign"] == "ON4AWM0"
    assert comparison["mode"] == "hardware_ab"
    assert comparison["reference_callsign"] == "ON4AWM1"
    assert comparison["snr_correction_mode"] == "established_offset"
    correction = Decimal(str(comparison["snr_correction_db"]))
    assert correction == Decimal("1.6")
    assert advanced["solar_state"] == "all"
    assert not advanced["exclude_special_callsigns"]
    assert not advanced["exclude_moving_stations"]
    assert advanced["min_joint_spots_per_station"] == 1
    selected_stations = settings["results_view"]["benchmark"]["selected_stations"]
    assert selected_stations == [{"callsign": "M7AEO", "locator": "IO82"}]
    start = _parse_utc(core["time_selection"]["start_utc"])
    end = _parse_utc(core["time_selection"]["end_utc"])
    assert start < end
    target = core["callsign"]
    reference = comparison["reference_callsign"]
    # JO20OT: field + square + subsquare, evaluated at the cell center.
    center_latitude = 50 + 19 / 24 + 1 / 48
    center_longitude = 4 + 14 / 12 + 1 / 24
    with source_path.open(encoding="utf-8", newline="") as stream:
        source_reports = list(csv.DictReader(stream))
    assert len({report["id"] for report in source_reports}) == len(source_reports)
    groups = defaultdict(lambda: {"target": [], "reference": [], "coordinates": set()})
    selected_source_count = 0
    for report in source_reports:
        timestamp = _parse_utc(report["time"])
        if not (
            int(report["band"]) == 1 and int(report["code"]) == 1
            and start <= timestamp < end and float(report["tx_lat"]) != 0
            and report["rx_loc"][:4] == core["qth"][:4]
            and report["rx_sign"] in (target, reference)
        ):
            continue
        selected_source_count += 1
        identity = (int(timestamp.timestamp()) // 120, report["tx_sign"], report["tx_loc"])
        group = groups[identity]
        group["coordinates"].add((float(report["tx_lat"]), float(report["tx_lon"])))
        group["target" if report["rx_sign"] == target else "reference"].append(report)

    active_cycles = {identity[0] for identity, group in groups.items() if group["target"]}
    query_rows, retained_rows, paired_rows = [], [], []
    outcomes = Counter()
    selected_unpaired_outcomes = Counter()
    for (cycle, callsign, locator), group in sorted(groups.items()):
        assert len(group["coordinates"]) == 1, "Ambiguous coordinate aggregate"
        latitude, longitude = next(iter(group["coordinates"]))
        target_reports = sorted(group["target"], key=lambda row: int(row["id"]))
        reference_reports = sorted(group["reference"], key=lambda row: int(row["id"]))
        normalized_target = max(
            (int(row["snr"]) - int(row["power"]) + 30 for row in target_reports),
            default=0,
        )
        uncorrected_reference = max(
            (int(row["snr"]) - int(row["power"]) + 30 for row in reference_reports),
            default=0,
        )
        normalized_reference = (
            float(Decimal(uncorrected_reference) + correction) if reference_reports else 0
        )
        query_row = {
            "time_slot": cycle, "peer_sign": callsign, "peer_grid": locator,
            "peer_lat": latitude, "peer_lon": longitude,
            "snr_u_norm": normalized_target, "snr_r_norm": normalized_reference,
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
        outcomes[outcome] += 1
        if (callsign, locator) != ("M7AEO", "IO82"):
            continue
        if outcome != "joint":
            selected_unpaired_outcomes[outcome] += 1
            continue
        selected_target = max(target_reports, key=lambda row: int(row["snr"]) - int(row["power"]))
        selected_reference = max(reference_reports, key=lambda row: int(row["snr"]) - int(row["power"]))
        paired_rows.append({
            "reception_index": len(paired_rows) + 1,
            "time_slot": cycle,
            "evidence_utc": datetime.fromtimestamp(cycle * 120, timezone.utc).isoformat(),
            "peer_sign": callsign, "peer_grid": locator,
            "target_report_ids": ";".join(row["id"] for row in target_reports),
            "reference_report_ids": ";".join(row["id"] for row in reference_reports),
            "target_report_snr_db": int(selected_target["snr"]),
            "reference_report_snr_db": int(selected_reference["snr"]),
            "target_report_power_dbm": int(selected_target["power"]),
            "reference_report_power_dbm": int(selected_reference["power"]),
            "target_snr_db": normalized_target,
            "reference_snr_db": normalized_reference,
            "delta_snr_db": float(Decimal(normalized_target - uncorrected_reference) - correction),
            "distance_km": distance_km, "bearing_degrees": bearing_degrees,
        })

    assert paired_rows, "No retained selected-station pairs"
    differences = [row["delta_snr_db"] for row in paired_rows]
    reception_slices = []
    for slice_index in range(20):
        slice_rows = [
            row for zero_based_index, row in enumerate(paired_rows)
            if zero_based_index * 20 // len(paired_rows) == slice_index
        ]
        reception_slices.append({"slice_index": slice_index, **_paired_subset_summary(slice_rows)})

    temporal_rows, density_rows = [], []
    bin_seconds = 12 * 3600
    bin_count = math.ceil((end - start).total_seconds() / bin_seconds)
    density_min = round(min(differences))
    density_max = round(max(differences))
    for bin_index in range(bin_count):
        bin_start = start + timedelta(seconds=bin_seconds * bin_index)
        bin_end = min(end, bin_start + timedelta(seconds=bin_seconds))
        bin_differences = [
            row["delta_snr_db"] for row in paired_rows
            if bin_start.timestamp() <= row["time_slot"] * 120 < bin_end.timestamp()
        ]
        temporal_rows.append({
            "bin_index": bin_index, "bin_start_utc": bin_start.isoformat(),
            "bin_end_utc": bin_end.isoformat(), "joint_spots": len(bin_differences),
            **_summarize_differences(bin_differences),
        })
        density_counts = Counter(round(difference) for difference in bin_differences)
        for delta_bin in range(density_min, density_max + 1):
            density_rows.append({
                "delta_snr_bin_db": delta_bin, "bin_index": bin_index,
                "joint_spots": density_counts[delta_bin],
            })

    midpoint = start + (end - start) / 2
    half_rows = []
    for split_kind in ("elapsed_time", "reception_750"):
        for half_index in (0, 1):
            subset = [
                row for row in paired_rows
                if (
                    int(row["time_slot"] * 120 >= midpoint.timestamp())
                    if split_kind == "elapsed_time"
                    else int(row["reception_index"] > 750)
                ) == half_index
            ]
            half_rows.append({
                "split_kind": split_kind, "half_index": half_index,
                **_paired_subset_summary(subset),
            })

    summary = {
        "derivation": "Independent standard-library calculation from raw report CSV and fixed configuration; no WSPRadar imports or application output inputs",
        "source_rows": len(source_reports), "selected_source_rows": selected_source_count,
        "source_code_counts": dict(sorted(Counter(row["code"] for row in source_reports).items())),
        "window_start_utc": start.isoformat(), "window_end_utc": end.isoformat(),
        "elapsed_time_midpoint_utc": midpoint.isoformat(),
        "reference_correction_db": float(correction),
        "center_latitude": center_latitude, "center_longitude": center_longitude,
        "sql_group_count": len(query_rows), "retained_group_count": len(retained_rows),
        "target_active_cycles": len(active_cycles), "retained_outcomes": dict(outcomes),
        "selected_peer_sign": "M7AEO", "selected_peer_grid": "IO82",
        "selected_unpaired_outcomes": dict(selected_unpaired_outcomes),
        "joint_spots": len(paired_rows),
        "first_paired_utc": paired_rows[0]["evidence_utc"],
        "last_paired_utc": paired_rows[-1]["evidence_utc"],
        "selected_duplicate_endpoint_groups": sum(
            len(group[side]) > 1 for identity, group in groups.items()
            if identity[1:] == ("M7AEO", "IO82") for side in ("target", "reference")
        ),
        "selected_report_power_dbm": sorted({
            row[field] for row in paired_rows
            for field in ("target_report_power_dbm", "reference_report_power_dbm")
        }),
        "reception_slice_count": 20,
        "reception_slice_rule": "zero_based_reception_index * 20 // N",
        "temporal_bin_count": bin_count, "temporal_bin_seconds": bin_seconds,
        "temporal_bin_anchor": "Configured window start; final bin ends at the configured window end; reports remain inside the half-open configured window",
        "density_bin_rule": "Nearest integer round(delta_snr_db), half-even at exact ties; no ties occur with correction1.6 dB",
        "density_min_bin_db": density_min, "density_max_bin_db": density_max,
        "empty_temporal_bins": [row["bin_index"] for row in temporal_rows if not row["joint_spots"]],
        **_summarize_differences(differences),
    }
    output_directory.mkdir(parents=True, exist_ok=True)
    subset_fields = ["joint_spots", "first_reception_index", "last_reception_index", *SUMMARY_FIELDS]
    for filename, records, fields in (
        ("expected_sql_rows.csv", query_rows, SQL_FIELDS),
        ("expected_retained_rows.csv", retained_rows, SQL_FIELDS),
        ("expected_paired_rows.csv", paired_rows, PAIRED_FIELDS),
        ("expected_reception_slices_20.csv", reception_slices, ["slice_index", *subset_fields]),
        ("expected_12h.csv", temporal_rows, ["bin_index", "bin_start_utc", "bin_end_utc", "joint_spots", *SUMMARY_FIELDS]),
        ("expected_density_12h.csv", density_rows, ["delta_snr_bin_db", "bin_index", "joint_spots"]),
        ("expected_halves.csv", half_rows, ["split_kind", "half_index", *subset_fields]),
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
