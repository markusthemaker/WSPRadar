#!/usr/bin/env sh
set -eu
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if command -v python3 >/dev/null 2>&1; then
    exec python3 "$SCRIPT_DIR/timed_ab_relay_switch.py" "$@"
fi
if command -v python >/dev/null 2>&1; then
    exec python "$SCRIPT_DIR/timed_ab_relay_switch.py" "$@"
fi
echo "python3 was not found. Install Python 3.10 or newer." >&2
exit 127