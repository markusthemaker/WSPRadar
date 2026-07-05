# Timed A/B Relay Switch

Cross-platform console helper for alternating a USB HID relay on a 2-minute slot / 4-minute A/B cadence.

This tool is intentionally generic. It can be used for WSPR hardware A/B switching, but the implementation itself has no WSPRadar or WSPR dependency.

- Target slots: UTC minutes `00, 04, 08, ...` or `02, 06, 10, ...`
- Reference slots: the opposite 2-minute slot phase
- Optional switch lead before the slot boundary, default `5.0 s`
- UTC and NTP status shown in the console
- Multi-relay setup: select USB device index first, then select relay channel
- Manual physical relay ON/OFF commands after setup

The tool targets common DCT/ATtiny45/V-USB HID relay boards with USB VID/PID `16c0:05df`, such as devices reporting product names like `USBRelay1`, `USBRelay2`, and similar.

## Files

- `timed_ab_relay_switch.py`: cross-platform Python implementation
- `Start-Timed-AB-Relay-Switch.cmd`: Windows launcher
- `Start-Timed-AB-Relay-Switch.sh`: Linux/macOS launcher
- `requirements-relay.txt`: Python HID dependency
- `timed-ab-relay-switch.config.json`: created by setup
- `timed-ab-relay-switch.log`: created when logging is enabled


## Install

Install Python 3.10 or newer, then install the HID dependency from this folder.

### Windows

```bat
cd tools\Timed-AB-Relay-Switch
py -3 -m pip install -r requirements-relay.txt
```

If `py` is not available, use:

```bat
python -m pip install -r requirements-relay.txt
```

### Linux

```sh
cd tools/Timed-AB-Relay-Switch
python3 -m pip install -r requirements-relay.txt
```

Most Linux systems restrict direct HID access. If setup finds the relay but cannot open it, install a udev rule similar to this:

```sh
sudo sh -c 'cat > /etc/udev/rules.d/99-timed-ab-relay-switch.rules <<EOF
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="16c0", ATTRS{idProduct}=="05df", MODE="0660", GROUP="plugdev", TAG+="uaccess"
EOF'
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Then unplug and reconnect the relay. Depending on distribution policy, you may also need to add your user to the `plugdev` group or log out and back in.

### macOS

```sh
cd tools/Timed-AB-Relay-Switch
python3 -m pip install -r requirements-relay.txt
```

The PyPI `hidapi` package provides macOS wheels for common Python versions and CPU architectures. If pip falls back to a source build, install the usual Apple command-line build tools first:

```sh
xcode-select --install
```

## Setup

### Windows

```bat
Start-Timed-AB-Relay-Switch.cmd --setup
```

PowerShell-style aliases are also accepted:

```bat
Start-Timed-AB-Relay-Switch.cmd -Setup
```

### Linux/macOS

```sh
chmod +x ./Start-Timed-AB-Relay-Switch.sh
./Start-Timed-AB-Relay-Switch.sh --setup
```

Setup will:

1. Find all attached HID relay devices with USB VID/PID `16c0:05df`.
2. Show each relay as a USB device index (`[0]`, `[1]`, ...), and ask which device to use when more than one is attached.
3. Save a stable device identity where possible: HID path, path hex, serial, product, relay serial.
4. Ask for the relay channel.
5. Ask whether relay ON means Target.
6. Ask which 4-minute phase is Target.
7. Automatically set Reference to the opposite valid phase.
8. Ask for the relay switch lead before the slot boundary.
9. Optionally run a short relay click test.

Valid slot phases are intentionally limited to `0` and `2`, because the tool alternates on even UTC 2-minute slot boundaries:

- `0`: Target at `00,04,08,...`; Reference at `02,06,10,...`
- `2`: Target at `02,06,10,...`; Reference at `00,04,08,...`

Relay channels are 1-based hardware channels. For a two-channel board, use `1` or `2`. The `[0]`, `[1]`, ... labels shown during setup are USB device list indices, not relay channels.

## Live Run

### Windows

```bat
Start-Timed-AB-Relay-Switch.cmd
```

### Linux/macOS

```sh
./Start-Timed-AB-Relay-Switch.sh
```

The console dashboard refreshes once per UTC second and shows:

- System UTC time
- Current Target/Reference slot
- Relay target state
- Countdown to the next relay switch
- NTP offset and round-trip delay
- Relay write status

Relay timing is checked more frequently than the dashboard redraw, so the optional switch lead is not limited to one-second display cadence.

The tool schedules from the system UTC clock. NTP is shown as a diagnostic only; it does not silently shift relay timing away from the computer clock used by the transmitter software.

## Manual Relay Control

Manual relay control sets the physical relay state and exits. It requires setup to have been run at least once, because the tool needs the saved USB relay identity and relay channel.

`--on` means physical relay ON. `--off` means physical relay OFF. These commands do not mean Target or Reference by themselves; the Target/Reference meaning depends on the setup answer to "Should relay ON mean Target?".

### Windows

```bat
Start-Timed-AB-Relay-Switch.cmd --on
Start-Timed-AB-Relay-Switch.cmd --off
```

PowerShell-style aliases are also accepted:

```bat
Start-Timed-AB-Relay-Switch.cmd -On
Start-Timed-AB-Relay-Switch.cmd -Off
```

### Linux/macOS

```sh
./Start-Timed-AB-Relay-Switch.sh --on
./Start-Timed-AB-Relay-Switch.sh --off
```

If setup has not been completed, manual control exits with an error and asks you to run setup first.

## Dry Run

Dry run computes and displays the schedule but does not write to the relay.

### Windows

```bat
Start-Timed-AB-Relay-Switch.cmd --dry-run
```

### Linux/macOS

```sh
./Start-Timed-AB-Relay-Switch.sh --dry-run
```

For one status frame and exit:

```sh
./Start-Timed-AB-Relay-Switch.sh --dry-run --once
```

The Windows launcher also accepts PowerShell-style aliases such as `-DryRun` and `-Once`.

## Hardware Notes

The implemented DCT relay command uses a 9-byte HID report:

- ON: report id `00`, command `FF`, relay channel `1..9`
- OFF: report id `00`, command `FD`, relay channel `1..9`

The tool first tries `send_feature_report()` and falls back to `write()` if the HID backend rejects the feature report path.

Before RF use, verify the mapping with a dummy load or non-RF continuity test:

- Target slot means the intended test path is active.
- Reference slot means the reference path is active.
- Relay changes happen before the 2-minute slot boundary when switch lead is configured.

## Troubleshooting

If setup lists no relay:

- Confirm the relay is attached and visible to the OS.
- Confirm the relay uses VID/PID `16c0:05df`, or edit the config file if your compatible relay uses a different VID/PID.
- On Linux, check udev permissions for `/dev/hidraw*`.

If setup lists several relays:

- Choose the USB device index (`[0]`, `[1]`, ...), then choose the relay channel (`1`, `2`, ...).
- The device index is not the relay channel.

If live mode cannot find the configured relay after reconnecting it:

- Run setup again. HID paths can change after unplug/replug events on some systems.
