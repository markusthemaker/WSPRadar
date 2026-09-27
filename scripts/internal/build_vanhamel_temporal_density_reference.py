"""Independently version only the Vanhamel temporal-density presentation oracle.

The frozen paired ledger supplies report identities and UTC membership. Raw
report SNR and power supply the coordinate arithmetic, using Decimal and the
standard library only. No WSPRadar renderer or scientific output is imported.
The original paired/statistical and legacy density expectations remain intact.
"""

from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import datetime
from decimal import Decimal, ROUND_FLOOR, ROUND_HALF_EVEN
import hashlib
import json
from pathlib import Path


DENSITY_FILENAME = "expected_density_12h_correction_aware_v1.csv"
POLICY_FILENAME = "temporal_density_revision_v1.json"


def calculate_density_reference(reference_directory, output_directory):
    """Write independent 1 dB cell IDs/edges/counts; preserve every input file."""
    reference_directory = Path(reference_directory)
    configuration = json.loads((reference_directory / "demo.config").read_text(encoding="utf-8"))
    settings = configuration["settings"]
    correction_db = Decimal(str(settings["comparison_parameters"]["snr_correction_db"]))
    window = settings["core_parameters"]["time_selection"]
    start_utc = datetime.fromisoformat(window["start_utc"].replace("Z", "+00:00"))
    end_utc = datetime.fromisoformat(window["end_utc"].replace("Z", "+00:00"))
    bin_seconds = 12 * 3600
    bin_count = int(((end_utc - start_utc).total_seconds() + bin_seconds - 1) // bin_seconds)
    with (reference_directory / "source_rows.csv").open(encoding="utf-8", newline="") as stream:
        source_reports = {row["id"]: row for row in csv.DictReader(stream)}
    with (reference_directory / "expected_paired_rows.csv").open(encoding="utf-8", newline="") as stream:
        paired_identities = list(csv.DictReader(stream))
    cell_counts = Counter()
    first_bin_values = []
    for pair in paired_identities:
        target_report = source_reports[pair["target_report_ids"]]
        reference_report = source_reports[pair["reference_report_ids"]]
        target_snr = Decimal(target_report["snr"]) - Decimal(target_report["power"]) + 30
        reference_snr = Decimal(reference_report["snr"]) - Decimal(reference_report["power"]) + 30
        comparison_coordinate = target_snr - reference_snr
        corrected_metric = comparison_coordinate - correction_db
        assert corrected_metric == Decimal(pair["delta_snr_db"])
        membership_coordinate = comparison_coordinate.quantize(Decimal("0.1"), rounding=ROUND_HALF_EVEN)
        bin_id = int((membership_coordinate + Decimal("0.5")).to_integral_value(rounding=ROUND_FLOOR))
        evidence_utc = datetime.fromisoformat(pair["evidence_utc"].replace("Z", "+00:00"))
        assert start_utc <= evidence_utc < end_utc
        time_index = int((evidence_utc - start_utc).total_seconds() // bin_seconds)
        cell_counts[bin_id, time_index] += 1
        if time_index == 0:
            first_bin_values.append(corrected_metric)
    min_bin_id = min(bin_id for bin_id, _ in cell_counts)
    max_bin_id = max(bin_id for bin_id, _ in cell_counts)
    records = []
    for bin_id in range(min_bin_id, max_bin_id + 1):
        center_db = Decimal(bin_id) - correction_db
        for time_index in range(bin_count):
            records.append({
                "metric_bin_id": bin_id,
                "cell_center_db": str(center_db),
                "cell_lower_db": str(center_db - Decimal("0.5")),
                "cell_upper_db": str(center_db + Decimal("0.5")),
                "bin_index": time_index,
                "joint_spots": cell_counts[bin_id, time_index],
            })
    first_bin_ids = [bin_id for (bin_id, time_index), count in cell_counts.items() if time_index == 0 and count]
    metadata = {
        "schema_version": 1,
        "presentation_contract": "correction-aware-1db-v1",
        "derivation": "Standard-library Decimal calculation from frozen raw report SNR/power; frozen independent paired ledger supplies source report identities and UTC membership only",
        "membership": "Round the temporary uncorrected comparison coordinate to 0.1 dB (ties-to-even), then k=floor(coordinate+0.5); exact half-dB belongs to upper cell",
        "membership_resolution_db": 0.1,
        "scientific_precision": "Stored corrected metrics, observations, medians and quartiles are not quantized by the density policy",
        "physical_interval": "[k-0.5-c, k+0.5-c)",
        "reference_correction_db": float(correction_db),
        "joint_spots": len(paired_identities),
        "time_bin_count": bin_count,
        "metric_bin_id_min": min_bin_id,
        "metric_bin_id_max": max_bin_id,
        "first_bin_observation_span_db": [float(min(first_bin_values)), float(max(first_bin_values))],
        "first_bin_occupied_cell_span_db": [float(Decimal(min(first_bin_ids)) - Decimal("0.5") - correction_db), float(Decimal(max(first_bin_ids)) + Decimal("0.5") - correction_db)],
        "legacy_density_expectation": "expected_density_12h.csv is retained unchanged; its corrected-coordinate labels -7..9 become comparison-coordinate IDs -5..11, preserving every count",
        "unchanged_scientific_expectations": "All original expected_* files remain byte-identical; this file and the new density CSV supersede only the legacy grid geometry",
        "input_sha256": {name: hashlib.sha256((reference_directory / name).read_bytes()).hexdigest() for name in ("source_rows.csv", "expected_paired_rows.csv", "demo.config", "expected_density_12h.csv")},
        "calculator_path": "scripts/internal/build_vanhamel_temporal_density_reference.py",
        "calculator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)
    with (output_directory / DENSITY_FILENAME).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)
    (output_directory / POLICY_FILENAME).write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8", newline="\n")
    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-directory", required=True, type=Path)
    parser.add_argument("--output-directory", required=True, type=Path)
    arguments = parser.parse_args()
    print(json.dumps(calculate_density_reference(arguments.reference_directory, arguments.output_directory), indent=2))


if __name__ == "__main__":
    main()
