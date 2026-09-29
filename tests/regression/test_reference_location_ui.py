"""User decisions preserve the discovered identity before resuming execution."""

from contextlib import nullcontext
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from streamlit.testing.v1 import AppTest


_SCRIPT = '''
from datetime import datetime, timezone
import streamlit as st
from core.reference_location import LocationCandidate, LocationDiscovery
from ui.reference_location import resolve_reference_before_analysis
from ui.reference_location_state import location_request_signature, store_location_discovery
start=datetime(2021,5,1,tzinfo=timezone.utc)
end=datetime(2021,5,2,tzinfo=timezone.utc)
if "seeded" not in st.session_state:
    st.session_state.update(dict(seeded=True,lang="en",val_comp_mode="reference_station",
        val_callsign="ON4AWM0",val_ref_callsign="M7AEO",val_qth="JO20OT",val_ref_qth="",
        val_analysis_direction="rx",val_band="20m"))
    make=lambda grid: LocationCandidate(grid,(grid,),1,start.isoformat(),end.isoformat())
    discovery=LocationDiscovery("wd2","strict_code_1",(make("JO20"),),tuple(make(g) for g in GRIDS))
    store_location_discovery(st.session_state,discovery,location_request_signature(st.session_state,start,end))
ready=resolve_reference_before_analysis(st.session_state,start,end)
st.session_state["ready"]=ready
'''


def app(grids):
    script = _SCRIPT.replace("GRIDS", repr(grids))
    return AppTest.from_string(script).run(timeout=30)


def test_ambiguous_location_waits_for_deliberate_choice_without_submission():
    at = app(["IO82", "RK76"])
    assert not at.exception
    assert not at.session_state["ready"]
    assert at.selectbox[0].value is None
    assert at.button[0].disabled
    assert "_analysis_submission_token" not in at.session_state
    at.selectbox[0].select("IO82").run()
    at.button[0].click().run()
    assert not at.exception
    assert at.session_state["ready"]
    assert at.session_state["val_ref_qth"] == "IO82"
    assert at.session_state["_reference_location_resolution"]["database_source"] == "wd2"


@pytest.mark.parametrize("reference_grid", ("JO20", "IO82"))
def test_single_eligible_location_resolves_without_an_extra_question(reference_grid):
    at = app([reference_grid])
    assert not at.exception
    assert at.session_state["ready"]
    assert at.session_state["val_ref_qth"] == reference_grid
    assert not at.selectbox
    assert not at.button


@pytest.mark.parametrize("target_grid,reference_grids,queries", [
    ("JO20", (), 1),
    ("FN31", ("IO82",), 1),
    ("JO20", ("IO82",), 0),
    ("JO20", ("IO82", "RK76"), 0),
])
def test_explicit_run_refreshes_negative_lookup_but_preserves_valid_choices(
    monkeypatch, target_grid, reference_grids, queries,
):
    import sys
    from core import reference_location
    from ui.reference_location import resolve_reference_before_analysis
    from ui.reference_location_state import location_request_signature, store_location_discovery

    start = datetime(2021, 5, 1, tzinfo=timezone.utc)
    end = datetime(2021, 5, 2, tzinfo=timezone.utc)
    state = dict(lang="en", val_comp_mode="reference_station", val_callsign="ON4AWM0",
                 val_ref_callsign="M7AEO", val_qth="JO20OT", val_ref_qth="",
                 val_analysis_direction="rx", val_band="20m")

    def candidate(grid):
        return reference_location.LocationCandidate(grid, (grid,), 1, start.isoformat(), end.isoformat())

    initial = reference_location.LocationDiscovery("wd2", "strict_code_1", (candidate(target_grid),),
                                                   tuple(candidate(grid) for grid in reference_grids))
    recovered = reference_location.LocationDiscovery("wd2", "strict_code_1", (candidate("JO20"),),
                                                     (candidate("IO82"),))
    store_location_discovery(state, initial, location_request_signature(state, start, end))
    lookup = MagicMock(return_value=recovered)
    monkeypatch.setattr(reference_location, "discover_reference_locations", lookup)
    streamlit = MagicMock()
    streamlit.spinner.return_value = nullcontext()
    streamlit.selectbox.return_value = None
    monkeypatch.setitem(sys.modules, "streamlit", streamlit)

    resolve_reference_before_analysis(state, start, end)
    lookup.assert_not_called()
    ready = resolve_reference_before_analysis(state, start, end, request_lookup=True)
    assert lookup.call_count == queries
    assert ready is (len(reference_grids) != 2)
    resolve_reference_before_analysis(state, start, end, request_lookup=True)
    assert lookup.call_count == queries
