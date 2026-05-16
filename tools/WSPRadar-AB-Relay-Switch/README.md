# WSPRadar WSPR A/B Relay Helper

Small Windows helper for alternating a USB HID relay on a 4-minute WSPR A/B cadence:

- Target slots: UTC minutes `00, 04, 08, ...`
- Reference slots: UTC minutes `02, 06, 10, ...`
- Relay switching happens at the 2-minute WSPR slot boundary, not at odd/even wall-clock minute labels.

The first implementation is a dependency-free PowerShell console tool for Windows 11. It targets common ATtiny45/V-USB HID relay boards with USB VID/PID `16c0:05df`; on Windows these appear in device paths as `VID_16C0&PID_05DF`.

## Files

- `WSPRadar-AB-Relay-Switch.ps1`: main tool
- `Start-WSPRadar-AB-Relay-Switch.cmd`: convenience launcher using `ExecutionPolicy Bypass`
- `wspradar-ab-relay-switch.config.json`: created by the tool on first run
- `wspradar-ab-relay-switch.log`: created when logging is enabled

## First Run

Open PowerShell or Command Prompt in this directory and run:

```bat
Start-WSPRadar-AB-Relay-Switch.cmd -Setup
```

Setup will:

1. Find attached HID relay devices with USB VID/PID `16c0:05df`.
2. Save the selected device path.
3. Ask for the relay channel.
4. Ask whether relay ON means Target.
5. Ask which 4-minute WSPR phase is Target.
6. Automatically set Reference to the other valid WSPR phase.
7. Ask for the relay switch lead before the WSPR slot boundary.
8. Optionally run a short relay click test.

Valid slot phases are intentionally limited to `0` and `2`, because WSPR slots start on even UTC minutes:

- `0`: Target at `00,04,08,...`; Reference at `02,06,10,...`
- `2`: Target at `02,06,10,...`; Reference at `00,04,08,...`

Switch lead is configured in seconds from `0` through `8`. A value such as `2` or `3` switches the relay before the next full 2-minute WSPR boundary so the selected TX path can settle before transmission starts.

## Live Run

```bat
Start-WSPRadar-AB-Relay-Switch.cmd
```

The console dashboard shows:

- System UTC time
- Current WSPR slot: Target or Reference
- Relay target state
- Countdown to the next 2-minute slot switch
- NTP offset and round-trip delay
- Relay write status

## Dry Run

Use this before connecting RF hardware:

```bat
Start-WSPRadar-AB-Relay-Switch.cmd -DryRun
```

Dry run computes and displays the schedule but does not write to the relay.

## Assumptions

This tool intentionally schedules from the Windows system UTC clock, because WSJT-X normally uses the same system clock. NTP is shown as a diagnostic so clock errors are visible without silently shifting the relay timing away from the transmitter's clock.

The default NTP server is `time.cloudflare.com`; it is queried every 15 minutes. If UDP port 123 is blocked, the dashboard will keep running and show the NTP failure.

## Hardware Notes

The target relay family is the common ATtiny45/V-USB HID type. Public hardware notes identify these as USB HID devices with vendor/product `16c0:05df`; the known Windows command path sets a relay channel to ON or OFF using a HID feature report.

Before RF use, verify the mapping with a dummy load or non-RF continuity test:

- Target slot means the intended test path is active.
- Reference slot means the reference path is active.
- Relay changes do not occur during the WSPR transmit body.
