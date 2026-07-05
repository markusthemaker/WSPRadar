import json

import pytest

from ui.config_io import CONFIG_APP_NAME, validate_config_upload


def test_legacy_time_slot_config_migrates_to_wspr_frame_keys():
    payload = {
        "app": CONFIG_APP_NAME,
        "schema_version": 1,
        "config": {
            "callsign": "DL1MKS",
            "qth": "JN37",
            "band": "20m",
            "time_mode": "custom",
            "start_date": "2026-05-27",
            "end_date": "2026-05-28",
            "start_time": "00:00",
            "end_time": "00:00",
            "benchmark_mode": "hardware_ab",
            "self_test_mode": "tx",
            "target_time_slot": "even",
            "reference_time_slot": "odd",
        },
    }

    config, warnings = validate_config_upload(json.dumps(payload).encode("utf-8"))

    assert warnings == []
    assert config["target_wspr_frame"] == "frame_00_04_08"
    assert config["reference_wspr_frame"] == "frame_02_06_10"


def test_current_wspr_frame_config_rejects_identical_tx_ab_frames():
    payload = {
        "app": CONFIG_APP_NAME,
        "schema_version": 3,
        "config": {
            "callsign": "DL1MKS",
            "qth": "JN37",
            "band": "20m",
            "time_mode": "custom",
            "start_date": "2026-05-27",
            "end_date": "2026-05-28",
            "start_time": "00:00",
            "end_time": "00:00",
            "benchmark_mode": "hardware_ab",
            "self_test_mode": "tx",
            "target_wspr_frame": "frame_00_04_08",
            "reference_wspr_frame": "frame_00_04_08",
        },
    }

    with pytest.raises(ValueError, match="target_wspr_frame and reference_wspr_frame must be different"):
        validate_config_upload(json.dumps(payload).encode("utf-8"))
