import datetime as dt
import importlib.util
import json
from pathlib import Path
import sys

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
RELAY_TOOL_PATH = (
    REPOSITORY_ROOT
    / "tools"
    / "Timed-AB-Relay-Switch"
    / "timed_ab_relay_switch.py"
)
MODULE_NAME = "wspradar_timed_ab_relay_switch"
MODULE_SPEC = importlib.util.spec_from_file_location(MODULE_NAME, RELAY_TOOL_PATH)
assert MODULE_SPEC is not None and MODULE_SPEC.loader is not None
relay_tool = importlib.util.module_from_spec(MODULE_SPEC)
sys.modules[MODULE_NAME] = relay_tool
MODULE_SPEC.loader.exec_module(relay_tool)


def utc_time(value: str) -> dt.datetime:
    """Return one timezone-aware timestamp used by schedule tests."""
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def test_fresh_config_uses_shared_10_00_02_schedule():
    config = relay_tool.default_config()

    assert relay_tool.ab_schedule_from_config(config) == relay_tool.AbSchedule(
        repeat_interval_minutes=10,
        target_start_minute=0,
        reference_start_minute=2,
    )
    assert "targetSlotModulo" not in config["timing"]
    assert "referenceSlotModulo" not in config["timing"]


@pytest.mark.parametrize("repeat_interval", (4, 6, 10, 12, 20, 30, 60))
def test_every_supported_repeat_interval_accepts_disjoint_even_starts(
    repeat_interval,
):
    schedule = relay_tool.validate_ab_schedule(repeat_interval, 0, 2)

    assert schedule.repeat_interval_minutes == repeat_interval


@pytest.mark.parametrize("repeat_interval", (2, 8, 14, 15, 120, True, "10.0"))
def test_unsupported_repeat_intervals_are_rejected(repeat_interval):
    with pytest.raises(relay_tool.ToolError, match="Repeat Interval"):
        relay_tool.validate_ab_schedule(repeat_interval, 0, 2)


@pytest.mark.parametrize(
    ("target_start", "reference_start", "message"),
    (
        (1, 2, "Target Start"),
        (0, 3, "Reference Start"),
        (10, 2, "Target Start"),
        (0, 10, "Reference Start"),
        (2, 2, "must be disjoint"),
    ),
)
def test_starts_must_be_even_canonical_and_disjoint(
    target_start,
    reference_start,
    message,
):
    with pytest.raises(relay_tool.ToolError, match=message):
        relay_tool.validate_ab_schedule(10, target_start, reference_start)


def test_hourly_start_previews_match_wspradar_vocabulary():
    assert relay_tool.format_start_minute_series(10, 0) == "00, 10, 20, 30, 40, 50"
    assert relay_tool.format_start_minute_series(10, 2) == "02, 12, 22, 32, 42, 52"
    assert relay_tool.format_start_minute_series(20, 10) == "10, 30, 50"


def test_schedule_holds_reference_path_through_unscheduled_gap():
    schedule = relay_tool.validate_ab_schedule(10, 0, 2)
    position = relay_tool.get_schedule_position(
        utc_time("2026-07-16T00:06:00Z"),
        schedule,
    )

    assert position.path_name == "Reference"
    assert position.most_recent_start_utc == utc_time("2026-07-16T00:02:00Z")
    assert position.next_path_name == "Target"
    assert position.next_start_utc == utc_time("2026-07-16T00:10:00Z")
    assert (
        relay_tool.current_transmission_path(
            utc_time("2026-07-16T00:06:00Z"),
            position,
        )
        is None
    )


def test_switch_lead_changes_path_only_at_next_start_minus_lead():
    schedule = relay_tool.validate_ab_schedule(10, 0, 2)
    before_switch = utc_time("2026-07-16T00:09:54.999Z")
    at_switch = utc_time("2026-07-16T00:09:55Z")
    lead = dt.timedelta(seconds=5)

    assert relay_tool.get_schedule_position(before_switch + lead, schedule).path_name == "Reference"
    prepared = relay_tool.get_schedule_position(at_switch + lead, schedule)
    assert prepared.path_name == "Target"
    assert prepared.most_recent_start_utc == utc_time("2026-07-16T00:10:00Z")
    assert prepared.next_path_name == "Reference"
    assert prepared.next_start_utc - lead == utc_time("2026-07-16T00:11:55Z")


def test_schedule_rolls_over_hour_and_day_for_interval_60():
    schedule = relay_tool.validate_ab_schedule(60, 0, 58)
    before_midnight = relay_tool.get_schedule_position(
        utc_time("2026-07-16T23:59:30Z"),
        schedule,
    )
    after_midnight = relay_tool.get_schedule_position(
        utc_time("2026-07-17T00:01:00Z"),
        schedule,
    )

    assert before_midnight.path_name == "Reference"
    assert before_midnight.most_recent_start_utc == utc_time("2026-07-16T23:58:00Z")
    assert before_midnight.next_path_name == "Target"
    assert before_midnight.next_start_utc == utc_time("2026-07-17T00:00:00Z")
    assert after_midnight.path_name == "Target"
    assert after_midnight.next_start_utc == utc_time("2026-07-17T00:58:00Z")


def test_swapped_target_reference_starts_reverse_relay_mapping():
    schedule = relay_tool.validate_ab_schedule(4, 2, 0)
    position = relay_tool.get_schedule_position(
        utc_time("2026-07-16T00:01:00Z"),
        schedule,
    )
    config = relay_tool.default_config()

    assert position.path_name == "Reference"
    assert position.next_path_name == "Target"
    assert relay_tool.desired_relay_on(config, position.path_name) is False
    config["device"]["onMeansTarget"] = False
    assert relay_tool.desired_relay_on(config, position.path_name) is True


@pytest.mark.parametrize(
    ("legacy_target", "legacy_reference", "expected_target", "expected_reference"),
    ((0, 2, 0, 2), (2, 0, 2, 0)),
)
def test_legacy_modulo_config_migrates_without_changing_cadence(
    legacy_target,
    legacy_reference,
    expected_target,
    expected_reference,
):
    loaded = {
        "timing": {
            "targetSlotModulo": legacy_target,
            "referenceSlotModulo": legacy_reference,
            "switchLeadMs": 2500,
        }
    }

    migrated = relay_tool.migrate_legacy_timing_config(loaded)

    assert migrated["timing"]["repeatIntervalMinutes"] == 4
    assert migrated["timing"]["targetStartMinute"] == expected_target
    assert migrated["timing"]["referenceStartMinute"] == expected_reference
    assert migrated["timing"]["switchLeadMs"] == 2500
    assert "targetSlotModulo" not in migrated["timing"]
    assert "referenceSlotModulo" not in migrated["timing"]


def test_new_schedule_fields_take_precedence_over_legacy_fields():
    loaded = {
        "timing": {
            "repeatIntervalMinutes": 20,
            "targetStartMinute": 0,
            "referenceStartMinute": 10,
            "targetSlotModulo": 2,
            "referenceSlotModulo": 0,
        }
    }

    migrated = relay_tool.migrate_legacy_timing_config(loaded)

    assert migrated["timing"]["repeatIntervalMinutes"] == 20
    assert migrated["timing"]["targetStartMinute"] == 0
    assert migrated["timing"]["referenceStartMinute"] == 10
    assert "targetSlotModulo" not in migrated["timing"]
    assert "referenceSlotModulo" not in migrated["timing"]


def test_load_config_migrates_legacy_schedule_before_merging_defaults(tmp_path):
    config_path = tmp_path / "relay.config.json"
    config_path.write_text(
        json.dumps(
            {
                "device": {"relayChannel": 2},
                "timing": {
                    "targetSlotModulo": 2,
                    "referenceSlotModulo": 0,
                },
            }
        ),
        encoding="utf-8",
    )

    config = relay_tool.load_config(config_path)

    assert relay_tool.ab_schedule_from_config(config) == relay_tool.AbSchedule(4, 2, 0)
    assert config["device"]["relayChannel"] == 2


def test_manual_physical_control_does_not_validate_schedule(monkeypatch, capsys):
    config = relay_tool.default_config()
    config["timing"]["repeatIntervalMinutes"] = "invalid"
    writes = []
    monkeypatch.setattr(relay_tool, "load_config_after_setup", lambda _path: config)
    monkeypatch.setattr(
        relay_tool,
        "set_relay_state",
        lambda _config, relay_on, dry_run=False: writes.append(
            (relay_on, dry_run)
        )
        or "MockWrite",
    )
    monkeypatch.setattr(relay_tool, "write_log_line", lambda *_args: None)

    relay_tool.show_manual_relay_control(Path("unused.json"), relay_on=True)

    assert writes == [(True, False)]
    assert "Relay manually set to ON." in capsys.readouterr().out


def test_dry_run_dashboard_uses_new_schedule_vocabulary(
    tmp_path,
    monkeypatch,
    capsys,
):
    config = relay_tool.default_config()
    config["logging"]["enabled"] = False
    config_path = tmp_path / "relay.config.json"
    relay_tool.save_config(config_path, config)
    now = utc_time("2026-07-16T00:06:00Z")
    monkeypatch.setattr(relay_tool, "utc_now", lambda: now)
    monkeypatch.setattr(
        relay_tool,
        "query_ntp",
        lambda server: relay_tool.NtpStatus(
            server=server,
            checked_utc=now,
            error="offline test",
        ),
    )

    relay_tool.show_dashboard(config_path, dry_run=True, once=True)

    output = capsys.readouterr().out
    assert "Repeat Interval:   10 min" in output
    assert "Target starts:     00, 10, 20, 30, 40, 50 UTC" in output
    assert "Reference starts:  02, 12, 22, 32, 42, 52 UTC" in output
    assert "Current schedule:  Idle; latest start was Reference at 00:02 UTC" in output
    assert "Next start:        Target at 00:10:00 UTC" in output

