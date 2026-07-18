#!/usr/bin/env python3
"""Timed A/B Relay Switch.

Cross-platform console helper for DCT-style USB HID relay boards. The tool
selects Target and Reference paths from a shared repeat interval and two
disjoint UTC start phases. It is intentionally generic: WSPR is a primary use
case, but the timing and relay logic do not depend on WSPRadar.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import socket
import struct
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

TOOL_VERSION = "0.2.0"
DEFAULT_VENDOR_ID = 0x16C0
DEFAULT_PRODUCT_ID = 0x05DF
DEFAULT_CONFIG_FILE = "timed-ab-relay-switch.config.json"
DEFAULT_LOG_FILE = "timed-ab-relay-switch.log"
REPEAT_INTERVAL_OPTIONS = (4, 6, 10, 12, 20, 30, 60)
DEFAULT_REPEAT_INTERVAL_MINUTES = 10
DEFAULT_TARGET_START_MINUTE = 0
DEFAULT_REFERENCE_START_MINUTE = 2
WSPR_TRANSMISSION_MINUTES = 2
SCRIPT_DIR = Path(__file__).resolve().parent
UTC = dt.timezone.utc
NTP_UNIX_DELTA = 2_208_988_800


class ToolError(RuntimeError):
    """Expected user-facing error."""


@dataclass
class FeatureSummary:
    raw: str = ""
    relay_serial: str = ""
    state_mask: int | None = None


@dataclass
class RelayDevice:
    index: int
    raw_path: Any
    path_display: str
    path_hex: str
    manufacturer: str
    product: str
    serial_number: str
    relay_serial: str
    relay_count: int
    state_mask: int | None
    feature_raw: str
    open_error: str


@dataclass(frozen=True)
class AbSchedule:
    """Validated periodic Target/Reference start phases in UTC minutes."""

    repeat_interval_minutes: int
    target_start_minute: int
    reference_start_minute: int


@dataclass(frozen=True)
class SchedulePosition:
    """Selected path and next scheduled start at one UTC instant."""

    path_name: str
    most_recent_start_utc: dt.datetime
    next_path_name: str
    next_start_utc: dt.datetime


@dataclass
class NtpStatus:
    server: str
    checked_utc: dt.datetime
    offset_ms: float | None = None
    delay_ms: float | None = None
    error: str | None = None


def default_config() -> dict[str, Any]:
    return {
        "device": {
            "vendorId": "16C0",
            "productId": "05DF",
            "path": None,
            "pathHex": None,
            "serialNumber": None,
            "manufacturer": None,
            "product": None,
            "relaySerial": None,
            "relayCount": 1,
            "relayChannel": 1,
            "onMeansTarget": True,
        },
        "timing": {
            "repeatIntervalMinutes": DEFAULT_REPEAT_INTERVAL_MINUTES,
            "targetStartMinute": DEFAULT_TARGET_START_MINUTE,
            "referenceStartMinute": DEFAULT_REFERENCE_START_MINUTE,
            "ntpServer": "time.cloudflare.com",
            "ntpCheckMinutes": 15,
            "warnOffsetMs": 1000,
            "staleNtpMinutes": 45,
            "switchLeadMs": 5000,
        },
        "logging": {
            "enabled": True,
            "path": DEFAULT_LOG_FILE,
        },
    }


def merge_config(default: dict[str, Any], loaded: dict[str, Any]) -> dict[str, Any]:
    for key, value in loaded.items():
        if isinstance(value, dict) and isinstance(default.get(key), dict):
            default[key] = merge_config(default[key], value)
        else:
            default[key] = value
    return default


def migrate_legacy_timing_config(loaded: dict[str, Any]) -> dict[str, Any]:
    """Translate the version-0.1 modulo-4 timing fields without changing cadence."""
    timing = loaded.get("timing")
    if not isinstance(timing, dict):
        return loaded

    legacy_target = timing.get("targetSlotModulo")
    legacy_reference = timing.get("referenceSlotModulo")
    has_legacy_schedule = (
        "targetSlotModulo" in timing or "referenceSlotModulo" in timing
    )
    has_new_schedule = any(
        field in timing
        for field in (
            "repeatIntervalMinutes",
            "targetStartMinute",
            "referenceStartMinute",
        )
    )
    if has_legacy_schedule and not has_new_schedule:
        try:
            target_start = int(legacy_target if legacy_target is not None else 0) % 4
            reference_start = int(
                legacy_reference
                if legacy_reference is not None
                else (2 if target_start == 0 else 0)
            ) % 4
        except (TypeError, ValueError) as exc:
            raise ToolError("Invalid legacy Target/Reference slot phase in config.") from exc
        if target_start not in (0, 2) or reference_start not in (0, 2):
            raise ToolError("Legacy Target/Reference slot phases must resolve to 0 and 2.")
        if target_start == reference_start:
            raise ToolError("Legacy Target and Reference slot phases must be disjoint.")
        timing["repeatIntervalMinutes"] = 4
        timing["targetStartMinute"] = target_start
        timing["referenceStartMinute"] = reference_start

    if has_legacy_schedule and (
        has_new_schedule or "repeatIntervalMinutes" in timing
    ):
        timing.pop("targetSlotModulo", None)
        timing.pop("referenceSlotModulo", None)
    return loaded


def resolve_config_path(config_path: str | None) -> Path:
    path = Path(config_path) if config_path else SCRIPT_DIR / DEFAULT_CONFIG_FILE
    if not path.is_absolute():
        path = SCRIPT_DIR / path
    return path


def load_config(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        config = default_config()
        save_config(config_path, config)
        return config
    with config_path.open("r", encoding="utf-8-sig") as handle:
        loaded = json.load(handle)
    if not isinstance(loaded, dict):
        raise ToolError(f"Config file is not a JSON object: {config_path}")
    loaded = migrate_legacy_timing_config(loaded)
    return merge_config(default_config(), loaded)


def save_config(config_path: Path, config: dict[str, Any]) -> None:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with config_path.open("w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=2)
        handle.write("\n")


def load_config_after_setup(config_path: Path) -> dict[str, Any]:
    """Load config for manual relay control and require a previous setup run."""
    if not config_path.exists():
        raise ToolError(
            "Manual relay control requires setup first. "
            "Run Start-Timed-AB-Relay-Switch.sh --setup or Start-Timed-AB-Relay-Switch.cmd --setup."
        )

    config = load_config(config_path)
    device_config = config.get("device", {})
    has_saved_device_identity = any(
        as_text(device_config.get(field))
        for field in ("path", "pathHex", "serialNumber", "relaySerial")
    )
    if not has_saved_device_identity:
        raise ToolError(
            "Manual relay control requires a configured relay device. "
            "Run setup first and select the USB relay device and channel."
        )
    return config


def write_log_line(config: dict[str, Any], message: str) -> None:
    logging_config = config.get("logging", {})
    if not logging_config.get("enabled", True):
        return
    log_path = Path(str(logging_config.get("path") or DEFAULT_LOG_FILE))
    if not log_path.is_absolute():
        log_path = SCRIPT_DIR / log_path
    line = f"{utc_now().isoformat()} {message}\n"
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(line)


def import_hid_module():
    try:
        import hid  # type: ignore
    except ImportError as exc:
        raise ToolError(
            "Python package 'hidapi' is not installed. Install it with:\n"
            "  python -m pip install -r requirements-relay.txt\n"
            "or:\n"
            "  python -m pip install hidapi"
        ) from exc
    return hid


def parse_hex_id(value: Any, field_name: str) -> int:
    if isinstance(value, int):
        return value
    text = str(value or "").strip().lower().replace("0x", "")
    if not re.fullmatch(r"[0-9a-f]{1,4}", text):
        raise ToolError(f"Invalid {field_name} '{value}'. Expected a USB hex id such as 16C0.")
    return int(text, 16)


def format_hex_id(value: int) -> str:
    return f"{value:04X}"


def as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return os.fsdecode(value)
    return str(value)


def path_to_display_and_hex(raw_path: Any) -> tuple[str, str]:
    if isinstance(raw_path, bytes):
        return os.fsdecode(raw_path), raw_path.hex()
    return as_text(raw_path), ""


def parse_feature_report(report: Any) -> FeatureSummary:
    if report is None:
        return FeatureSummary()
    data = bytes(report)
    if not data:
        return FeatureSummary()

    raw = " ".join(f"{byte:02X}" for byte in data)
    ascii_text = "".join(chr(byte) for byte in data if 0x20 <= byte <= 0x7E)
    relay_serial = ascii_text[:5] if len(ascii_text) >= 5 else ""
    state_mask = None
    if len(data) >= 9 and data[0] == 0x01:
        state_mask = int(data[8])
    elif len(data) >= 8:
        state_mask = int(data[7])
    return FeatureSummary(raw=raw, relay_serial=relay_serial, state_mask=state_mask)


def infer_relay_count(product: str) -> int:
    match = re.search(r"USBRelay(\d+)", product or "", re.IGNORECASE)
    if not match:
        return 1
    relay_count = int(match.group(1))
    if relay_count < 1 or relay_count > 9:
        return 9
    return relay_count


def inspect_feature(raw_path: Any) -> tuple[FeatureSummary, str]:
    hid = import_hid_module()
    device = hid.device()
    try:
        device.open_path(raw_path)
        report = device.get_feature_report(0x01, 9)
        return parse_feature_report(report), ""
    except Exception as exc:
        return FeatureSummary(), str(exc)
    finally:
        try:
            device.close()
        except Exception:
            pass


def enumerate_relay_devices(vendor_id: int, product_id: int) -> list[RelayDevice]:
    hid = import_hid_module()
    try:
        raw_devices = hid.enumerate(vendor_id, product_id)
    except Exception as exc:
        raise ToolError(f"Could not enumerate HID devices for {vendor_id:04X}:{product_id:04X}: {exc}") from exc

    devices: list[RelayDevice] = []
    for index, info in enumerate(raw_devices):
        raw_path = info.get("path")
        path_display, path_hex = path_to_display_and_hex(raw_path)
        manufacturer = as_text(info.get("manufacturer_string"))
        product = as_text(info.get("product_string"))
        serial_number = as_text(info.get("serial_number"))
        feature, open_error = inspect_feature(raw_path)
        relay_count = infer_relay_count(product)
        devices.append(
            RelayDevice(
                index=index,
                raw_path=raw_path,
                path_display=path_display,
                path_hex=path_hex,
                manufacturer=manufacturer,
                product=product,
                serial_number=serial_number,
                relay_serial=feature.relay_serial,
                relay_count=relay_count,
                state_mask=feature.state_mask,
                feature_raw=feature.raw,
                open_error=open_error,
            )
        )
    return devices


def find_configured_device(config: dict[str, Any]) -> RelayDevice:
    device_config = config["device"]
    vendor_id = parse_hex_id(device_config.get("vendorId"), "vendorId")
    product_id = parse_hex_id(device_config.get("productId"), "productId")
    devices = enumerate_relay_devices(vendor_id, product_id)
    if not devices:
        raise ToolError(f"No HID relay found for VID:PID {vendor_id:04X}:{product_id:04X}.")

    wanted_path_hex = as_text(device_config.get("pathHex")).lower()
    wanted_path = as_text(device_config.get("path"))
    wanted_serial = as_text(device_config.get("serialNumber"))
    wanted_product = as_text(device_config.get("product"))
    wanted_relay_serial = as_text(device_config.get("relaySerial"))

    for device in devices:
        if wanted_path_hex and device.path_hex.lower() == wanted_path_hex:
            return device
        if wanted_path and device.path_display == wanted_path:
            return device

    serial_matches = [
        device
        for device in devices
        if wanted_serial
        and device.serial_number == wanted_serial
        and (not wanted_product or device.product == wanted_product)
    ]
    if len(serial_matches) == 1:
        return serial_matches[0]

    relay_serial_matches = [
        device
        for device in devices
        if wanted_relay_serial
        and device.relay_serial == wanted_relay_serial
        and (not wanted_product or device.product == wanted_product)
    ]
    if len(relay_serial_matches) == 1:
        return relay_serial_matches[0]

    if len(devices) == 1:
        return devices[0]

    raise ToolError(
        "Configured relay device was not found unambiguously. "
        "Run setup again and select the desired USB device index."
    )


def set_relay_state(config: dict[str, Any], on: bool, dry_run: bool = False) -> str:
    device_config = config["device"]
    relay_channel = int(device_config.get("relayChannel") or 0)
    if relay_channel < 1 or relay_channel > 9:
        raise ToolError(
            f"Invalid relay channel {relay_channel} in config. "
            "Relay channels are 1-based; run setup and choose channel 1 or higher."
        )
    if dry_run:
        return "DryRun"

    selected = find_configured_device(config)
    relay_count = selected.relay_count or int(device_config.get("relayCount") or 1)
    if relay_channel > relay_count:
        raise ToolError(
            f"Configured relay channel {relay_channel} is outside this device's relay range 1-{relay_count}. "
            "Run setup again."
        )

    hid = import_hid_module()
    device = hid.device()
    report = bytes([0x00, 0xFF if on else 0xFD, relay_channel, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    errors: list[str] = []
    try:
        device.open_path(selected.raw_path)
        try:
            result = device.send_feature_report(report)
            return f"send_feature_report({result})"
        except Exception as exc:
            errors.append(f"send_feature_report: {exc}")
        try:
            result = device.write(report)
            return f"write({result})"
        except Exception as exc:
            errors.append(f"write: {exc}")
        raise ToolError("HID relay write failed. " + "; ".join(errors))
    finally:
        try:
            device.close()
        except Exception:
            pass


def utc_now() -> dt.datetime:
    return dt.datetime.now(UTC)


def _parse_schedule_integer(value: Any, field_name: str) -> int:
    """Return one whole-number schedule field or raise a user-facing error."""
    if isinstance(value, bool):
        raise ToolError(f"Invalid {field_name} '{value}'. Use a whole number.")
    if isinstance(value, int):
        return value
    text = str(value or "").strip()
    if not re.fullmatch(r"\d+", text):
        raise ToolError(f"Invalid {field_name} '{value}'. Use a whole number.")
    return int(text)


def normalize_repeat_interval(value: Any) -> int:
    """Return one supported shared Repeat Interval in minutes."""
    repeat_interval = _parse_schedule_integer(value, "Repeat Interval")
    if repeat_interval not in REPEAT_INTERVAL_OPTIONS:
        allowed = ", ".join(str(option) for option in REPEAT_INTERVAL_OPTIONS)
        raise ToolError(
            f"Invalid Repeat Interval '{value}'. Use one of: {allowed} minutes."
        )
    return repeat_interval


def normalize_start_minute(
    value: Any,
    repeat_interval_minutes: int,
    field_name: str,
) -> int:
    """Return one even canonical UTC start phase below the Repeat Interval."""
    start_minute = _parse_schedule_integer(value, field_name)
    allowed_starts = tuple(range(0, repeat_interval_minutes, 2))
    if start_minute not in allowed_starts:
        allowed = ", ".join(f"{minute:02d}" for minute in allowed_starts)
        raise ToolError(
            f"Invalid {field_name} '{value}' for Repeat Interval "
            f"{repeat_interval_minutes}. Use one of: {allowed}."
        )
    return start_minute


def validate_ab_schedule(
    repeat_interval_minutes: Any,
    target_start_minute: Any,
    reference_start_minute: Any,
) -> AbSchedule:
    """Validate and return one disjoint periodic Target/Reference schedule."""
    repeat_interval = normalize_repeat_interval(repeat_interval_minutes)
    target_start = normalize_start_minute(
        target_start_minute,
        repeat_interval,
        "Target Start",
    )
    reference_start = normalize_start_minute(
        reference_start_minute,
        repeat_interval,
        "Reference Start",
    )
    if target_start == reference_start:
        raise ToolError("Target Start and Reference Start must be disjoint.")
    return AbSchedule(
        repeat_interval_minutes=repeat_interval,
        target_start_minute=target_start,
        reference_start_minute=reference_start,
    )


def ab_schedule_from_config(config: dict[str, Any]) -> AbSchedule:
    """Read and validate the configured Repeat Interval and path starts."""
    timing = config.get("timing", {})
    return validate_ab_schedule(
        timing.get("repeatIntervalMinutes", DEFAULT_REPEAT_INTERVAL_MINUTES),
        timing.get("targetStartMinute", DEFAULT_TARGET_START_MINUTE),
        timing.get("referenceStartMinute", DEFAULT_REFERENCE_START_MINUTE),
    )


def format_start_minute_series(
    repeat_interval_minutes: int,
    start_minute: int,
) -> str:
    """Format every UTC start minute in one hour for one configured path."""
    repeat_interval = normalize_repeat_interval(repeat_interval_minutes)
    normalized_start = normalize_start_minute(
        start_minute,
        repeat_interval,
        "Start",
    )
    return ", ".join(
        f"{minute:02d}" for minute in range(normalized_start, 60, repeat_interval)
    )


def _most_recent_path_start(
    utc_minute_start: dt.datetime,
    repeat_interval_minutes: int,
    start_minute: int,
) -> dt.datetime:
    """Return the most recent occurrence of one path's UTC start phase."""
    elapsed_minutes = (utc_minute_start.minute - start_minute) % repeat_interval_minutes
    return utc_minute_start - dt.timedelta(minutes=elapsed_minutes)


def get_schedule_position(
    utc_time: dt.datetime,
    schedule: AbSchedule,
) -> SchedulePosition:
    """Return the path selected by the latest start and the next path start."""
    if utc_time.tzinfo is None:
        raise ToolError("Schedule time must include a UTC offset.")
    utc_time = utc_time.astimezone(UTC)
    utc_minute_start = utc_time.replace(second=0, microsecond=0)
    target_previous = _most_recent_path_start(
        utc_minute_start,
        schedule.repeat_interval_minutes,
        schedule.target_start_minute,
    )
    reference_previous = _most_recent_path_start(
        utc_minute_start,
        schedule.repeat_interval_minutes,
        schedule.reference_start_minute,
    )
    if target_previous > reference_previous:
        path_name = "Target"
        most_recent_start = target_previous
    else:
        path_name = "Reference"
        most_recent_start = reference_previous

    target_next = target_previous + dt.timedelta(
        minutes=schedule.repeat_interval_minutes
    )
    reference_next = reference_previous + dt.timedelta(
        minutes=schedule.repeat_interval_minutes
    )
    if target_next < reference_next:
        next_path_name = "Target"
        next_start = target_next
    else:
        next_path_name = "Reference"
        next_start = reference_next
    return SchedulePosition(
        path_name=path_name,
        most_recent_start_utc=most_recent_start,
        next_path_name=next_path_name,
        next_start_utc=next_start,
    )


def current_transmission_path(
    utc_time: dt.datetime,
    schedule_position: SchedulePosition,
) -> str | None:
    """Return the path inside its nominal two-minute WSPR window, else ``None``."""
    transmission_end = schedule_position.most_recent_start_utc + dt.timedelta(
        minutes=WSPR_TRANSMISSION_MINUTES
    )
    if utc_time.astimezone(UTC) < transmission_end:
        return schedule_position.path_name
    return None


def desired_relay_on(config: dict[str, Any], path_name: str) -> bool:
    on_means_target = bool(config["device"].get("onMeansTarget", True))
    return on_means_target if path_name == "Target" else not on_means_target


def parse_switch_lead_ms(text: str) -> int:
    normalized = text.strip().replace(",", ".")
    try:
        seconds = float(normalized)
    except ValueError as exc:
        raise ToolError(f"Invalid switch lead '{text}'. Use seconds, for example 2 or 2.5.") from exc
    if seconds < 0 or seconds > 8:
        raise ToolError(f"Invalid switch lead '{text}'. Use 0 through 8 seconds.")
    return int(round(seconds * 1000.0))


def format_switch_lead(milliseconds: int) -> str:
    return f"{milliseconds / 1000.0:0.1f} s"


def format_time_span(seconds: float) -> str:
    if seconds < 0:
        seconds = 0.0
    if seconds >= 60:
        minutes = int(seconds // 60)
        remainder = seconds - (minutes * 60)
        return f"{minutes} min {remainder:04.1f} s"
    return f"{seconds:0.1f} s"


def format_utc_date_time(value: dt.datetime) -> str:
    return value.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S")


def format_utc_time(value: dt.datetime) -> str:
    return value.astimezone(UTC).strftime("%H:%M:%S")


def ntp_timestamp_from_unix(unix_seconds: float) -> bytes:
    ntp_seconds = int(unix_seconds + NTP_UNIX_DELTA)
    fraction = int((unix_seconds - int(unix_seconds)) * (2**32))
    return struct.pack("!II", ntp_seconds, fraction)


def unix_seconds_from_ntp(data: bytes, offset: int) -> float:
    seconds, fraction = struct.unpack("!II", data[offset : offset + 8])
    return (seconds - NTP_UNIX_DELTA) + (fraction / 2**32)


def query_ntp(server: str, timeout_seconds: float = 3.0) -> NtpStatus:
    packet = bytearray(48)
    packet[0] = 0x1B
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout_seconds)
    try:
        t0 = time.time()
        packet[40:48] = ntp_timestamp_from_unix(t0)
        sock.sendto(packet, (server, 123))
        data, _remote = sock.recvfrom(512)
        t3 = time.time()
        if len(data) < 48:
            raise ToolError(f"NTP response was too short: {len(data)} bytes.")
        t1 = unix_seconds_from_ntp(data, 32)
        t2 = unix_seconds_from_ntp(data, 40)
        offset_ms = (((t1 - t0) + (t2 - t3)) / 2.0) * 1000.0
        delay_ms = ((t3 - t0) - (t2 - t1)) * 1000.0
        return NtpStatus(server=server, checked_utc=utc_now(), offset_ms=offset_ms, delay_ms=delay_ms)
    except Exception as exc:
        return NtpStatus(server=server, checked_utc=utc_now(), error=str(exc))
    finally:
        sock.close()


def prompt_text(prompt: str) -> str:
    return input(prompt).strip()


def parse_index_answer(answer: str, minimum: int, maximum: int, label: str) -> int:
    if not re.fullmatch(r"\d+", answer):
        raise ToolError(f"Invalid {label} '{answer}'. Use a number from {minimum} through {maximum}.")
    value = int(answer)
    if value < minimum or value > maximum:
        raise ToolError(f"Invalid {label} '{value}'. Use a number from {minimum} through {maximum}.")
    return value


def show_setup(config_path: Path) -> None:
    config = load_config(config_path)
    vendor_id = parse_hex_id(config["device"].get("vendorId"), "vendorId")
    product_id = parse_hex_id(config["device"].get("productId"), "productId")

    print("")
    print("Timed A/B Relay Switch setup")
    print(f"Tool version: {TOOL_VERSION}")
    print("")

    devices = enumerate_relay_devices(vendor_id, product_id)
    if not devices:
        print(f"No HID relay found for VID:PID {vendor_id:04X}:{product_id:04X}.")
        print("Check that the relay is plugged in and that OS HID permissions allow access.")
        return

    for device in devices:
        title = " ".join(part for part in (device.product, device.relay_serial) if part)
        print(f"[{device.index}] {title or 'USB HID relay'}")
        print(f"    Manufacturer: {device.manufacturer}")
        print(f"    SerialNumber: {device.serial_number}")
        print(f"    DevicePath:   {device.path_display}")
        if device.path_hex:
            print(f"    PathHex:      {device.path_hex}")
        print(f"    RelayCount:   {device.relay_count}")
        print(f"    StateMask:    {device.state_mask}")
        print(f"    FeatureRaw:   {device.feature_raw}")
        if device.open_error:
            print(f"    OpenError:    {device.open_error}")
        print("")

    selection = 0
    if len(devices) > 1:
        max_index = len(devices) - 1
        answer = prompt_text(f"Select USB relay device index [0-{max_index}, default 0]: ")
        if answer:
            selection = parse_index_answer(answer, 0, max_index, "device selection")
    else:
        print("Only one matching USB relay found; using device index [0].")
        print("")

    selected = devices[selection]
    device_config = config["device"]
    device_config["vendorId"] = format_hex_id(vendor_id)
    device_config["productId"] = format_hex_id(product_id)
    device_config["path"] = selected.path_display
    device_config["pathHex"] = selected.path_hex or None
    device_config["serialNumber"] = selected.serial_number or None
    device_config["manufacturer"] = selected.manufacturer or None
    device_config["product"] = selected.product or None
    device_config["relaySerial"] = selected.relay_serial or None
    device_config["relayCount"] = selected.relay_count

    relay_count = selected.relay_count if 1 <= selected.relay_count <= 9 else 9
    current_channel = int(device_config.get("relayChannel") or 1)
    if current_channel < 1 or current_channel > relay_count:
        print(f"Configured relay channel {current_channel} is invalid for this device. Using channel 1.")
        current_channel = 1
        device_config["relayChannel"] = current_channel

    channel_answer = prompt_text(f"Relay channel [1-{relay_count}, default {current_channel}]: ")
    if channel_answer:
        channel = parse_index_answer(channel_answer, 1, relay_count, "relay channel")
        device_config["relayChannel"] = channel

    mapping_answer = prompt_text("Should relay ON mean Target? [Y/n]: ")
    device_config["onMeansTarget"] = not mapping_answer.lower().startswith("n")

    try:
        current_schedule = ab_schedule_from_config(config)
    except ToolError as exc:
        print(f"Configured TX A/B schedule is invalid ({exc}); using 10 / 00 / 02.")
        current_schedule = validate_ab_schedule(
            DEFAULT_REPEAT_INTERVAL_MINUTES,
            DEFAULT_TARGET_START_MINUTE,
            DEFAULT_REFERENCE_START_MINUTE,
        )

    print("")
    print("TX A/B Schedule:")
    interval_choices = "/".join(str(value) for value in REPEAT_INTERVAL_OPTIONS)
    interval_answer = prompt_text(
        "Repeat Interval in minutes "
        f"[{interval_choices}, default {current_schedule.repeat_interval_minutes}]: "
    )
    repeat_interval = normalize_repeat_interval(
        interval_answer or current_schedule.repeat_interval_minutes
    )
    permitted_starts = tuple(range(0, repeat_interval, 2))
    permitted_start_text = ", ".join(
        f"{minute:02d}" for minute in permitted_starts
    )
    print(f"Permitted even UTC starts: {permitted_start_text}")

    target_default = (
        current_schedule.target_start_minute
        if current_schedule.target_start_minute in permitted_starts
        else DEFAULT_TARGET_START_MINUTE
    )
    target_answer = prompt_text(
        f"Target Start [default {target_default:02d} UTC]: "
    )
    target_start = normalize_start_minute(
        target_answer or target_default,
        repeat_interval,
        "Target Start",
    )

    reference_default = current_schedule.reference_start_minute
    if reference_default not in permitted_starts or reference_default == target_start:
        reference_default = next(
            start for start in permitted_starts if start != target_start
        )
    reference_answer = prompt_text(
        f"Reference Start [default {reference_default:02d} UTC]: "
    )
    reference_start = normalize_start_minute(
        reference_answer or reference_default,
        repeat_interval,
        "Reference Start",
    )
    schedule = validate_ab_schedule(
        repeat_interval,
        target_start,
        reference_start,
    )
    config["timing"]["repeatIntervalMinutes"] = schedule.repeat_interval_minutes
    config["timing"]["targetStartMinute"] = schedule.target_start_minute
    config["timing"]["referenceStartMinute"] = schedule.reference_start_minute
    config["timing"].pop("targetSlotModulo", None)
    config["timing"].pop("referenceSlotModulo", None)
    print(
        "Configured Target starts:    "
        f"{format_start_minute_series(schedule.repeat_interval_minutes, schedule.target_start_minute)} UTC"
    )
    print(
        "Configured Reference starts: "
        f"{format_start_minute_series(schedule.repeat_interval_minutes, schedule.reference_start_minute)} UTC"
    )
    print("")

    current_lead_ms = int(config["timing"].get("switchLeadMs") or 0)
    lead_answer = prompt_text(
        "Switch lead before each scheduled start in seconds "
        f"[0-8, default {format_switch_lead(current_lead_ms)}]: "
    )
    if lead_answer:
        current_lead_ms = parse_switch_lead_ms(lead_answer)
    config["timing"]["switchLeadMs"] = current_lead_ms
    print(
        "Configured switch lead:     "
        f"{format_switch_lead(current_lead_ms)} before each scheduled start"
    )
    print("")

    save_config(config_path, config)
    print("")
    print(f"Saved config: {config_path}")

    test_answer = prompt_text("Run relay click test now? [y/N]: ")
    if test_answer.lower().startswith("y"):
        print("Turning relay ON for 1 second...")
        set_relay_state(config, True, dry_run=False)
        time.sleep(1.0)
        print("Turning relay OFF...")
        set_relay_state(config, False, dry_run=False)


def show_manual_relay_control(config_path: Path, relay_on: bool) -> None:
    """Set the configured relay to a physical ON/OFF state and exit."""
    config = load_config_after_setup(config_path)
    write_method = set_relay_state(config, relay_on, dry_run=False)
    relay_state = "ON" if relay_on else "OFF"
    mapping_text = (
        "ON=Target, OFF=Reference"
        if config["device"].get("onMeansTarget", True)
        else "ON=Reference, OFF=Target"
    )
    print(f"Relay manually set to {relay_state}.")
    print(
        "Relay device: "
        f"{config['device'].get('vendorId')}:{config['device'].get('productId')} "
        f"CH{config['device'].get('relayChannel')}"
    )
    print(f"Configured mapping: {mapping_text}")
    print(f"Write method: {write_method}")
    write_log_line(config, f"MANUAL relayOn={relay_on} method={write_method}")


def build_ntp_text(ntp: NtpStatus | None, now: dt.datetime, config: dict[str, Any]) -> tuple[str, str]:
    if ntp is None:
        return "not checked yet", "Unknown"
    if ntp.error:
        return f"error: {ntp.error}", "NTP failed"
    assert ntp.offset_ms is not None
    assert ntp.delay_ms is not None
    age_minutes = (now - ntp.checked_utc).total_seconds() / 60.0
    text = (
        f"offset {ntp.offset_ms:+0.1f} ms, delay {ntp.delay_ms:0.1f} ms, "
        f"checked {age_minutes:0.1f} min ago via {ntp.server}"
    )
    if abs(ntp.offset_ms) >= float(config["timing"].get("warnOffsetMs", 1000)):
        return text, "Warning"
    if age_minutes >= float(config["timing"].get("staleNtpMinutes", 45)):
        return text, "Stale"
    return text, "OK"


def clear_terminal() -> None:
    print("\033[2J\033[H", end="")


def current_epoch_second(value: dt.datetime) -> int:
    return int(value.timestamp())


def show_dashboard(config_path: Path, dry_run: bool, once: bool) -> None:
    config = load_config(config_path)
    if not dry_run and not config["device"].get("path") and not config["device"].get("pathHex"):
        print("No configured relay. Running setup first.")
        show_setup(config_path)
        config = load_config(config_path)
        if not config["device"].get("path") and not config["device"].get("pathHex"):
            raise ToolError("No configured relay. Connect the relay and run setup again.")
    schedule = ab_schedule_from_config(config)

    ntp: NtpStatus | None = None
    next_ntp_check = dt.datetime(1970, 1, 1, tzinfo=UTC)
    last_relay_on: bool | None = None
    last_relay_error: str | None = None
    last_write_method = ""
    last_display_second: int | None = None

    write_log_line(config, f"START version={TOOL_VERSION} dryRun={dry_run}")

    while True:
        now = utc_now()
        if now >= next_ntp_check:
            server = str(config["timing"].get("ntpServer") or "time.cloudflare.com")
            ntp = query_ntp(server)
            next_ntp_check = now + dt.timedelta(minutes=int(config["timing"].get("ntpCheckMinutes") or 15))
            if ntp.error:
                write_log_line(config, f"NTP error server={ntp.server} error={ntp.error}")
            else:
                write_log_line(
                    config,
                    f"NTP ok server={ntp.server} offsetMs={ntp.offset_ms:0.1f} delayMs={ntp.delay_ms:0.1f}",
                )

        switch_lead_ms = int(config["timing"].get("switchLeadMs") or 0)
        switch_lead = dt.timedelta(milliseconds=switch_lead_ms)
        current_position = get_schedule_position(now, schedule)
        relay_position = get_schedule_position(now + switch_lead, schedule)
        relay_on = desired_relay_on(config, relay_position.path_name)

        if last_relay_on is None or relay_on != last_relay_on:
            try:
                last_write_method = set_relay_state(config, relay_on, dry_run=dry_run)
                last_relay_on = relay_on
                last_relay_error = None
                write_log_line(
                    config,
                    f"RELAY path={relay_position.path_name} "
                    f"scheduledStart={relay_position.most_recent_start_utc.isoformat()} "
                    f"relayOn={relay_on} method={last_write_method} "
                    f"switchLeadMs={switch_lead_ms}",
                )
            except Exception as exc:
                last_relay_error = str(exc)
                write_log_line(
                    config,
                    f"RELAY_ERROR path={relay_position.path_name} "
                    f"scheduledStart={relay_position.most_recent_start_utc.isoformat()} "
                    f"relayOn={relay_on} switchLeadMs={switch_lead_ms} "
                    f"error={last_relay_error}",
                )

        next_switch_utc = relay_position.next_start_utc - switch_lead
        until_next = (next_switch_utc - now).total_seconds()
        lead_active = relay_position.path_name != current_position.path_name
        transmission_path = current_transmission_path(now, current_position)
        relay_text = "ON" if relay_on else "OFF"
        mapping_text = "ON=Target, OFF=Reference" if config["device"].get("onMeansTarget", True) else "ON=Reference, OFF=Target"
        ntp_text, clock_state = build_ntp_text(ntp, now, config)

        display_second = current_epoch_second(now)
        should_render = once or display_second != last_display_second
        if should_render:
            last_display_second = display_second
            if not once:
                clear_terminal()
            print(f"Timed A/B Relay Switch {TOOL_VERSION}")
            print("-----------------------------------")
            print("Configuration:")
            print(f"Mode:              {'Dry run' if dry_run else 'Live'}")
            print(
                "Relay device:      "
                f"{config['device'].get('vendorId')}:{config['device'].get('productId')} "
                f"CH{config['device'].get('relayChannel')}"
            )
            print(
                f"Relay path:        {relay_position.path_name} / {relay_text} "
                f"({mapping_text})"
            )
            print(
                f"Repeat Interval:   {schedule.repeat_interval_minutes} min"
            )
            print(
                "Target starts:     "
                f"{format_start_minute_series(schedule.repeat_interval_minutes, schedule.target_start_minute)} UTC"
            )
            print(
                "Reference starts:  "
                f"{format_start_minute_series(schedule.repeat_interval_minutes, schedule.reference_start_minute)} UTC"
            )
            print(
                f"Switch lead:       {format_switch_lead(switch_lead_ms)} "
                "before each scheduled start"
            )
            print(f"Write method:      {last_write_method}")
            print("-----------------------------------")
            print(f"UTC:               {format_utc_date_time(now)}")
            print(f"NTP:               {ntp_text}")
            print(f"Clock status:      {clock_state}")
            print("-----------------------------------")
            if transmission_path:
                transmission_end = current_position.most_recent_start_utc + dt.timedelta(
                    minutes=WSPR_TRANSMISSION_MINUTES
                )
                print(
                    "Current schedule:  "
                    f"{transmission_path} start "
                    f"{current_position.most_recent_start_utc.strftime('%H:%M')} UTC "
                    f"(nominal window to {transmission_end.strftime('%H:%M')} UTC)"
                )
            else:
                print(
                    "Current schedule:  Idle; latest start was "
                    f"{current_position.path_name} at "
                    f"{current_position.most_recent_start_utc.strftime('%H:%M')} UTC"
                )
            if lead_active:
                print(
                    "Relay prepared for: "
                    f"{relay_position.path_name} start at "
                    f"{relay_position.most_recent_start_utc.strftime('%H:%M')} UTC"
                )
            print(
                "Next start:        "
                f"{current_position.next_path_name} at "
                f"{format_utc_time(current_position.next_start_utc)} UTC"
            )
            print(
                "Next switch to:    "
                f"{relay_position.next_path_name} at {format_utc_time(next_switch_utc)} UTC "
                f"for that start, in {format_time_span(until_next)}"
            )
            if last_relay_error:
                print(f"Relay error:       {last_relay_error}")
            print("")
            print("Press Ctrl+C to stop.")

        if once:
            break
        time.sleep(0.1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Timed A/B USB HID relay switch")
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--setup", "-Setup", action="store_true", help="run interactive setup")
    mode_group.add_argument("--on", "-On", action="store_true", help="set the configured relay physically ON and exit")
    mode_group.add_argument("--off", "-Off", action="store_true", help="set the configured relay physically OFF and exit")
    parser.add_argument("--dry-run", "-DryRun", action="store_true", help="show timing without writing to the relay")
    parser.add_argument("--once", "-Once", action="store_true", help="render one status display and exit")
    parser.add_argument(
        "--config",
        "--config-path",
        "-ConfigPath",
        dest="config_path",
        default=None,
        help="path to config JSON; defaults to timed-ab-relay-switch.config.json next to this script",
    )
    parser.add_argument("--version", action="version", version=f"Timed A/B Relay Switch {TOOL_VERSION}")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config_path = resolve_config_path(args.config_path)
    try:
        if args.setup:
            show_setup(config_path)
        elif args.on or args.off:
            if args.dry_run or args.once:
                raise ToolError("--on and --off are one-shot relay writes and cannot be combined with --dry-run or --once.")
            show_manual_relay_control(config_path, relay_on=args.on)
        else:
            show_dashboard(config_path, dry_run=args.dry_run, once=args.once)
        return 0
    except KeyboardInterrupt:
        print("\nStopped.")
        return 130
    except ToolError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
