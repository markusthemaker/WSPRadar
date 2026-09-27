"""Test-only bootstrap: run the real application against prepared local caches."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys


HARNESS_DIRECTORY = Path(__file__).resolve().parent
if str(HARNESS_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(HARNESS_DIRECTORY))

from replay import REPOSITORY_ROOT, install_offline_runtime


output_directory = os.environ.get("WSPRADAR_LOAD_TEST_DIR")
if not output_directory:
    raise RuntimeError("Set WSPRADAR_LOAD_TEST_DIR to a directory prepared by replay.py.")
install_offline_runtime(output_directory)

import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx


def log_session_checkpoint(phase):
    """Log only scalar state, without retaining or copying result objects."""
    script_context = get_script_run_ctx()
    completed = st.session_state.get("completed_run_snapshot")
    snapshot = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "phase": phase,
        "session_id": script_context.session_id if script_context is not None else None,
        "run_id": st.session_state.get("run_id"),
        "run_mode": st.session_state.get("run_mode"),
        "has_completed_run": completed is not None,
        "callsign": st.session_state.get("val_callsign"),
        "comparison_mode": st.session_state.get("val_comp_mode"),
    }
    print("LOAD_TEST_SESSION " + json.dumps(snapshot, default=str), flush=True)


st.session_state.setdefault("lang", "en")
st.session_state.setdefault("input_view", "classic")
log_session_checkpoint("start")
application_path = REPOSITORY_ROOT / "app.py"
try:
    # Streamlit executes scripts in a per-session module namespace. Do the same
    # here: runpy.run_path temporarily mutates sys.modules and is inappropriate
    # when different session threads execute the entry point concurrently.
    exec(compile(application_path.read_bytes(), str(application_path), "exec"), {
        "__name__": "__main__", "__file__": str(application_path),
        "__package__": None,
    })
finally:
    log_session_checkpoint("end")
