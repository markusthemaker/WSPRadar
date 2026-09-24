"""Derive the bounded Milazzo Figure 6 RX reference without application imports.

Inputs are user-supplied wspr.rocks reports and independently digitized paper
markers. Derived coordinates and unknown mode codes are documented explicitly.
Write candidate output separately; tests never regenerate their expectations.
"""

import argparse
from collections import defaultdict
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
from statistics import median


START = datetime(2010, 12, 19, 12, tzinfo=timezone.utc)
END = datetime(2010, 12, 20, 20, tzinfo=timezone.utc)
SQL_FIELDS = ["time_slot", "peer_sign", "peer_grid", "peer_lat", "peer_lon",
              "snr_u_norm", "snr_r_norm", "has_u", "has_r"]


def _utc(text):
    return datetime.fromisoformat(text.replace("Z", "+00:00")).replace(tzinfo=timezone.utc)


def _coordinates(locator):
    """Decode the center of a four- or six-character Maidenhead cell."""
    locator = locator.upper()
    assert len(locator) in (4, 6)
    longitude = -180 + 20 * (ord(locator[0]) - 65) + 2 * int(locator[2])
    latitude = -90 + 10 * (ord(locator[1]) - 65) + int(locator[3])
    if len(locator) == 6:
        longitude += (ord(locator[4]) - 65) / 12 + 1 / 24
        latitude += (ord(locator[5]) - 65) / 24 + 1 / 48
    else:
        longitude += 1
        latitude += 0.5
    return latitude, longitude


def _write_csv(path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def calculate_reference(input_directory, output_directory):
    reports = []
    with (input_directory / "user_kp4md_40m_rows.csv").open(encoding="utf-8", newline="") as stream:
        for number, report in enumerate(csv.DictReader(stream), 1):
            reports.append({**report, "source_row_key": f"kp4md:{number}"})
    with (input_directory / "user_wb6rqn_reports.tsv").open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        reader.fieldnames = [name.strip() for name in reader.fieldnames]
        for number, report in enumerate(reader, 1):
            assert report["mode"] == "unknown"
            reports.append({
                "time": report["y-m-d utc"], "tx_sign": report["txCall"],
                "tx_loc": report["txGrid"], "rx_sign": report["rxCall"],
                "rx_loc": report["rxGrid"], "frequency_mhz": report["MHz"],
                "power_w": report["W"], "snr": report["SNR"],
                "source_row_key": f"wb6rqn:{number}",
            })
    source_rows = []
    for report in reports:
        assert report["tx_sign"] == "VE6PDQ" and float(report["power_w"]) == 5
        tx_lat, tx_lon = _coordinates(report["tx_loc"])
        rx_lat, rx_lon = _coordinates(report["rx_loc"])
        source_rows.append({
            "source_row_key": report["source_row_key"], "time": _utc(report["time"]).isoformat(),
            "band": int(float(report["frequency_mhz"])), "code": None,
            "rx_sign": report["rx_sign"], "rx_loc": report["rx_loc"],
            "rx_lat": rx_lat, "rx_lon": rx_lon, "tx_sign": report["tx_sign"],
            "tx_loc": report["tx_loc"], "tx_lat": tx_lat, "tx_lon": tx_lon,
            "snr": int(report["snr"]), "power": 37,
        })
    selected = [row for row in source_rows if row["band"] == 7 and START <= _utc(row["time"]) < END]
    with (input_directory / "paper_markers.csv").open(encoding="utf-8", newline="") as stream:
        markers = list(csv.DictReader(stream))
    matches = []
    for marker in markers:
        timestamp = _utc(marker["utc_readout_approx"])
        nearby = [row for row in selected if row["rx_sign"] == marker["series"]
                  and abs((_utc(row["time"]) - timestamp).total_seconds()) <= 240]
        assert len(nearby) == 1, marker
        report = nearby[0]
        assert report["snr"] == float(marker["snr_db_approx"]), marker
        matches.append({
            "marker_id": f'{marker["series"]}_{int(marker["visible_marker_number"]):02d}',
            "source_row_key": report["source_row_key"], "receiver": report["rx_sign"],
            "transmitter": report["tx_sign"], "transmitter_locator": report["tx_loc"],
            "report_utc": report["time"], "paper_utc": marker["utc_readout_approx"],
            "time_error_seconds": (_utc(report["time"]) - timestamp).total_seconds(),
            "paper_snr_db": int(marker["snr_db_approx"]), "report_snr_db": report["snr"],
        })
    assert {row["source_row_key"] for row in selected} == {row["source_row_key"] for row in matches}
    groups = defaultdict(list)
    for report in selected:
        groups[(int(_utc(report["time"]).timestamp()) // 120, report["tx_sign"], report["tx_loc"])].append(report)
    active = {identity[0] for identity, rows in groups.items() if any(row["rx_sign"] == "KP4MD" for row in rows)}
    sql_rows, native_rows, pairs = [], [], []
    for (slot, callsign, locator), rows in sorted(groups.items()):
        target = [row for row in rows if row["rx_sign"] == "KP4MD"]
        reference = [row for row in rows if row["rx_sign"] == "WB6RQN"]
        assert len(target) <= 1 and len(reference) <= 1
        target_snr = target[0]["snr"] - 7 if target else None
        reference_snr = reference[0]["snr"] - 7 if reference else None
        latitude, longitude = _coordinates(locator)
        sql_rows.append({
            "time_slot": slot, "peer_sign": callsign, "peer_grid": locator,
            "peer_lat": latitude, "peer_lon": longitude,
            "snr_u_norm": target_snr if target else 0,
            "snr_r_norm": reference_snr if reference else 0,
            "has_u": len(target), "has_r": len(reference),
        })
        if slot not in active:
            continue
        outcome = "joint" if target and reference else "target_only" if target else "reference_only"
        native = {"time_slot": slot, "peer_sign": callsign, "peer_grid": locator,
                  "outcome": outcome, "target_snr_db": target_snr,
                  "reference_snr_db": reference_snr,
                  "delta_snr_db": target_snr - reference_snr if outcome == "joint" else None}
        native_rows.append(native)
        if outcome == "joint":
            pairs.append(native)
    summary = {
        "input_reports": len(source_rows), "selected_reports": len(selected),
        "paper_markers": len(markers), "matched_markers": len(matches),
        "max_time_error_seconds": max(abs(row["time_error_seconds"]) for row in matches),
        "sql_groups": len(sql_rows), "target_active_cycles_in_supplied_path_subset": len(active),
        "retained_native_units": len(native_rows),
        "retained_outcomes": {outcome: sum(row["outcome"] == outcome for row in native_rows)
                              for outcome in ("target_only", "joint", "reference_only")},
        "paired_delta_snr_db": [row["delta_snr_db"] for row in pairs],
        "paired_median_db": median(row["delta_snr_db"] for row in pairs),
        "scope_limit": "User-supplied VE6PDQ path only; absence here does not establish global receiver inactivity in the full archive",
    }
    output_directory.mkdir(parents=True, exist_ok=True)
    for name, rows, fields in (
        ("source_rows.csv", source_rows, list(source_rows[0])),
        ("expected_paper_matches.csv", matches, list(matches[0])),
        ("expected_sql_rows.csv", sql_rows, SQL_FIELDS),
        ("expected_native_units.csv", native_rows, list(native_rows[0])),
        ("expected_paired_rows.csv", pairs, list(pairs[0])),
    ):
        _write_csv(output_directory / name, rows, fields)
    (output_directory / "expected_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-directory", required=True, type=Path)
    parser.add_argument("--output-directory", required=True, type=Path)
    arguments = parser.parse_args()
    print(json.dumps(calculate_reference(arguments.input_directory, arguments.output_directory), indent=2))
