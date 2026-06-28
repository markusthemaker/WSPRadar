#!/usr/bin/env python3
"""Timed A/B Relay Switch.

Cross-platform console helper for DCT-style USB HID relay boards. The tool
alternates a selected relay channel between Target and Reference slots on a
2-minute slot / 4-minute A/B cadence. It is intentionally generic: WSPR is a
primary use case, but the timing and relay logic do not depend on WSPRadar.
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

TOOL_VERSION = "0.1.0"
DEFAULT_VENDOR_ID = 0x16C0
DEFAULT_PRODUCT_ID = 0x05DF
DEFAULT_CONFIG_FILE = "timed-ab-relay-switch.config.json"
DEFAULT_LOG_FILE = "timed-ab-relay-switch.log"
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


@dataclass
class Slot:
    name: str
    start_utc: dt.datetime
    end_utc: dt.datetime
    modulo: int


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
            "targetSlotModulo": 0,
            "referenceSlotModulo": 2,
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
    return merge_config(default_config(), loaded)


def save_config(config_path: Path, config: dict[str, Any]) -> None:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with config_path.open("w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=2)
        handle.write("\n")


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


def get_ab_slot(utc_time: dt.datetime, target_modulo: int, reference_modulo: int) -> Slot:
    utc_time = utc_time.astimezone(UTC)
    slot_minute = utc_time.minute - (utc_time.minute % 2)
    slot_start = utc_time.replace(minute=slot_minute, second=0, microsecond=0)
    slot_end = slot_start + dt.timedelta(minutes=2)
    slot_modulo = slot_start.minute % 4
    target_modulo = normalize_slot_modulo(target_modulo)
    reference_modulo = normalize_slot_modulo(reference_modulo)
    if slot_modulo == target_modulo:
        slot_name = "Target"
    elif slot_modulo == reference_modulo:
        slot_name = "Reference"
    else:
        slot_name = "Reference"
    return Slot(name=slot_name, start_utc=slot_start, end_utc=slot_end, modulo=slot_modulo)


def desired_relay_on(config: dict[str, Any], slot_name: str) -> bool:
    on_means_target = bool(config["device"].get("onMeansTarget", True))
    return on_means_target if slot_name == "Target" else not on_means_target


def normalize_slot_modulo(value: Any) -> int:
    modulo = int(value) % 4
    if modulo not in (0, 2):
        raise ToolError(f"Invalid A/B slot phase '{value}'. Use 0 for 00,04,08... or 2 for 02,06,10...")
    return modulo


def format_slot_minute_series(modulo: int) -> str:
    normalized = normalize_slot_modulo(modulo)
    minutes = [minute for minute in range(60) if minute % 4 == normalized][:3]
    return ", ".join(f"{minute:02d}" for minute in minutes) + ", ..."


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

    target_modulo = normalize_slot_modulo(config["timing"].get("targetSlotModulo", 0))
    reference_modulo = 2 if target_modulo == 0 else 0
    print("")
    print("Timed A/B slot cadence:")
    print("    0 = Target at 00,04,08,... and Reference at 02,06,10,...")
    print("    2 = Target at 02,06,10,... and Reference at 00,04,08,...")
    phase_answer = prompt_text(f"Target slot phase [0/2, default {target_modulo}]: ")
    if phase_answer:
        if phase_answer not in ("0", "2"):
            raise ToolError(f"Invalid target slot phase '{phase_answer}'. Use 0 or 2.")
        target_modulo = int(phase_answer)
        reference_modulo = 2 if target_modulo == 0 else 0
    config["timing"]["targetSlotModulo"] = target_modulo
    config["timing"]["referenceSlotModulo"] = reference_modulo
    print(f"Configured Target slots:    {format_slot_minute_series(target_modulo)} UTC minutes")
    print(f"Configured Reference slots: {format_slot_minute_series(reference_modulo)} UTC minutes")
    print("")

    current_lead_ms = int(config["timing"].get("switchLeadMs") or 0)
    lead_answer = prompt_text(
        "Switch lead before slot boundary in seconds "
        f"[0-8, default {format_switch_lead(current_lead_ms)}]: "
    )
    if lead_answer:
        current_lead_ms = parse_switch_lead_ms(lead_answer)
    config["timing"]["switchLeadMs"] = current_lead_ms
    print(f"Configured switch lead:     {format_switch_lead(current_lead_ms)} before slot boundary")
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
        current_slot = get_ab_slot(
            now,
            int(config["timing"].get("targetSlotModulo", 0)),
            int(config["timing"].get("referenceSlotModulo", 2)),
        )
        relay_slot = get_ab_slot(
            now + switch_lead,
            int(config["timing"].get("targetSlotModulo", 0)),
            int(config["timing"].get("referenceSlotModulo", 2)),
        )
        relay_on = desired_relay_on(config, relay_slot.name)

        if last_relay_on is None or relay_on != last_relay_on:
            try:
                last_write_method = set_relay_state(config, relay_on, dry_run=dry_run)
                last_relay_on = relay_on
                last_relay_error = None
                write_log_line(
                    config,
                    f"RELAY slot={relay_slot.name} relayOn={relay_on} method={last_write_method} switchLeadMs={switch_lead_ms}",
                )
            except Exception as exc:
                last_relay_error = str(exc)
                write_log_line(
                    config,
                    f"RELAY_ERROR slot={relay_slot.name} relayOn={relay_on} switchLeadMs={switch_lead_ms} error={last_relay_error}",
                )

        next_switch_utc = relay_slot.end_utc - switch_lead
        until_next = (next_switch_utc - now).total_seconds()
        next_slot_name = "Reference" if relay_slot.name == "Target" else "Target"
        lead_active = relay_slot.start_utc != current_slot.start_utc
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
            print(f"Relay target:      {relay_text} ({mapping_text})")
            print(f"Target slots:      {format_slot_minute_series(int(config['timing'].get('targetSlotModulo', 0)))} UTC minutes")
            print(f"Reference slots:   {format_slot_minute_series(int(config['timing'].get('referenceSlotModulo', 2)))} UTC minutes")
            print(f"Switch lead:       {format_switch_lead(switch_lead_ms)} before slot boundary")
            print(f"Write method:      {last_write_method}")
            print("-----------------------------------")
            print(f"UTC:               {format_utc_date_time(now)}")
            print(f"NTP:               {ntp_text}")
            print(f"Clock status:      {clock_state}")
            print("-----------------------------------")
            print(
                "Current slot:      "
                f"{current_slot.name} ({current_slot.start_utc.strftime('%H:%M')}-{current_slot.end_utc.strftime('%H:%M')} UTC, "
                f"minute {current_slot.start_utc.minute} mod 4 = {current_slot.modulo})"
            )
            if lead_active:
                print(
                    "Relay prepared for: "
                    f"{relay_slot.name} ({relay_slot.start_utc.strftime('%H:%M')}-{relay_slot.end_utc.strftime('%H:%M')} UTC)"
                )
            print(f"Next switch to:    {next_slot_name} at {format_utc_time(next_switch_utc)} UTC, in {format_time_span(until_next)}")
            if last_relay_error:
                print(f"Relay error:       {last_relay_error}")
            print("")
            print("Press Ctrl+C to stop.")

        if once:
            break
        time.sleep(0.1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Timed A/B USB HID relay switch")
    parser.add_argument("--setup", "-Setup", action="store_true", help="run interactive setup")
    parser.add_argument("--dry-run", "-DryRun", action="store_true", help="show timing without writing to the relay")
    parser.add_argument("--once", "-Once", action="store_true", help="render one status frame and exit")
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