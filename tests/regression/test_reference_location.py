"""Reference discovery must not guess sites or cross provider boundaries."""

from datetime import datetime, timezone
from types import SimpleNamespace

import pandas as pd
import pytest

from core.fetch_models import DatabaseSource, FetchError, FetchFailureScope, FetchResult
from core.reference_location import (
    LocationDiscoveryError, MAX_LOCATION_VARIANTS, build_location_query,
    discover_reference_locations, location_candidates,
)
from ui.reference_location_state import (
    current_location_resolution, location_request_signature, resolved_discovery_source,
    select_reference_location, store_location_discovery,
)


START = datetime(2021, 5, 1, tzinfo=timezone.utc)
END = datetime(2021, 5, 2, tzinfo=timezone.utc)


def row(endpoint, locator, count=1):
    return dict(endpoint=endpoint, locator=locator, reports=count,
                first_utc="2021-05-01 01:00:00", last_utc="2021-05-01 02:00:00")


def kwargs(**overrides):
    return dict(direction="rx", target_callsign="ON4AWM0", target_qth="JO20OT",
                reference_callsign="ON4AWM1", band="20m", start_utc=START, end_utc=END,
                **overrides)


@pytest.mark.parametrize("direction,sign,peer", [("rx", "rx_sign", "tx_lat"), ("tx", "tx_sign", "rx_lat")])
@pytest.mark.parametrize("start_minute,end_minute", [(0, 0), (7, 11)])
def test_discovery_has_exact_endpoint_scope_but_no_reference_grid_prefilter(direction, sign, peer, start_minute, end_minute):
    values = kwargs()
    values.pop("target_qth")
    values["direction"] = direction
    values["start_utc"] = START.replace(minute=start_minute)
    values["end_utc"] = END.replace(minute=end_minute)
    query = build_location_query(**values)
    assert f"{sign} IN ('ON4AWM0', 'ON4AWM1')" in query
    assert f"{peer} != 0" in query and "code = 1" in query
    assert "JO20" not in query and " LIKE " not in query
    assert f"time >= '2021-05-01 00:{start_minute:02d}:00'" in query
    assert f"time < '2021-05-02 00:{end_minute:02d}:00'" in query
    assert f"LIMIT {MAX_LOCATION_VARIANTS + 1}" in query


def test_discovery_preserves_full_variants_and_rare_conflicting_grid():
    targets, references, invalid = location_candidates([
        row("target", "JO20OT"), row("reference", "IO82", 3),
        row("reference", "io82aa", 6), row("reference", "IO82AB", 2),
        row("reference", "RK76", 1), row("reference", "", 2),
    ])
    assert [item.grid for item in references] == ["IO82", "RK76"]
    assert references[0].locators == ("IO82", "IO82AA", "IO82AB")
    assert references[0].reports == 11 and references[1].reports == 1
    assert targets[0].grid == "JO20" and invalid == 2


def test_discovery_rejects_ambiguous_naive_time_boundaries():
    values = kwargs()
    values.pop("target_qth")
    values["start_utc"] = START.replace(tzinfo=None)
    with pytest.raises(LocationDiscoveryError, match="time window"):
        build_location_query(**values)


@pytest.mark.parametrize("record", [row("reference", "JO20", True), row("reference", "JO20", -1),
                                    row("unknown", "JO20"), {"endpoint": "reference"}])
def test_malformed_response_cannot_establish_unique_location(record):
    with pytest.raises(LocationDiscoveryError):
        location_candidates([record])


def test_truncated_discovery_cannot_establish_unique_location():
    with pytest.raises(LocationDiscoveryError, match="complete-result"):
        location_candidates([row("reference", "JO20")] * (MAX_LOCATION_VARIANTS + 1))


class Lease:
    def __init__(self, source):
        self.source_key = source
        self.provider = SimpleNamespace(key=source)
        self.released = False
        self.failed = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.released = True

    def report_success(self):
        pass

    def report_failure(self, error):
        self.failed = True


class Dispatch:
    def __init__(self):
        self.providers = [SimpleNamespace(key="wspr_live"), SimpleNamespace(key="wd2")]
        self.leases = []

    def acquire_run(self, request_counts, excluded_sources):
        source = "wd2" if "wspr_live" in excluded_sources else "wspr_live"
        lease = Lease(source)
        self.leases.append(lease)
        return lease


def test_historical_discovery_uses_target_grid_to_decide_fallback_and_releases_lease():
    dispatch = Dispatch()
    queries = []

    def fetch(query, **arguments):
        queries.append(query)
        records = [row("target", "JO21"), row("reference", "JO21")]
        if "code = 1" not in query:
            records = [row("target", "JO20OT"), row("reference", "JO20OT")]
        return FetchResult(dataframe=pd.DataFrame(records))

    result = discover_reference_locations(**kwargs(), dispatch=dispatch, fetch_data=fetch)
    assert len(queries) == 2 and result.decode_filter_mode == "legacy_no_code"
    assert result.reference_locations[0].grid == "JO20"
    assert len(dispatch.leases) == 1 and dispatch.leases[0].released


def test_provider_failure_restarts_discovery_and_records_actual_source():
    dispatch = Dispatch()

    def fetch(query, **arguments):
        if arguments["database_provider"].key == "wspr_live":
            return FetchResult(error=FetchError("unavailable", "unavailable", scope=FetchFailureScope.PROVIDER))
        return FetchResult(dataframe=pd.DataFrame([row("target", "JO20"), row("reference", "JO21")]),
                           database_source=DatabaseSource.WD2)

    result = discover_reference_locations(**kwargs(), dispatch=dispatch, fetch_data=fetch)
    assert result.database_source == "wd2"
    assert all(lease.released for lease in dispatch.leases)
    assert dispatch.leases[0].failed


def test_missing_reference_does_not_trigger_legacy_retry_when_target_is_present():
    calls = []

    def fetch(query, **arguments):
        calls.append(query)
        return FetchResult(dataframe=pd.DataFrame([row("target", "JO20")]))

    result = discover_reference_locations(**kwargs(), dispatch=Dispatch(), fetch_data=fetch)
    assert len(calls) == 1 and not result.reference_locations


def test_discovery_selection_is_bound_to_inputs_and_source():
    from core.reference_location import LocationDiscovery
    targets, references, _ = location_candidates([row("target", "JO20"), row("reference", "IO82"), row("reference", "RK76")])
    state = dict(val_comp_mode="reference_station", val_analysis_direction="rx", val_callsign="ON4AWM0", val_qth="JO20OT",
                 val_ref_callsign="M7AEO", val_band="20m")
    signature = location_request_signature(state, START, END)
    store_location_discovery(state, LocationDiscovery("wd2", "strict_code_1", targets, references), signature)
    with pytest.raises(ValueError):
        select_reference_location(state, "JO20")
    select_reference_location(state, "IO82")
    assert state["val_ref_qth"] == "IO82"
    assert resolved_discovery_source(state, START, END) == "wd2"
    state["val_comp_mode"] = "none"
    assert resolved_discovery_source(state, START, END) is None
    state["val_comp_mode"] = "reference_station"
    assert resolved_discovery_source(state, START, END) == "wd2"
    state["val_band"] = "40m"
    assert current_location_resolution(state, START, END) is None
    assert resolved_discovery_source(state, START, END) is None


def test_failed_discovery_source_requires_rediscovery_instead_of_silent_failover():
    from ui.reference_location_state import discard_failed_discovery_source
    state = {"val_ref_qth": "IO82", "_reference_location_resolution": {"database_source": "wd2"}}
    discard_failed_discovery_source(state, "wspr_live")
    assert state["val_ref_qth"] == "IO82"
    discard_failed_discovery_source(state, "wd2")
    assert state["val_ref_qth"] == "" and "_reference_location_resolution" not in state
