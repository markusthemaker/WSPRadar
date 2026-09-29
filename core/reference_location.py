"""Bounded, source-aware discovery of fixed Reference archive locations.

Discovery selects the same endpoint role, band, time and decode policy as the
comparison. It reports full locator variants but resolves the existing grid-4
endpoint selector; it never merges the remote peers' full-locator identities.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Callable

from config import BAND_MAP
from core.input_validation import is_valid_callsign, is_valid_locator, normalize_ascii_upper


MAX_LOCATION_VARIANTS = 256


class LocationDiscoveryError(ValueError):
    """Discovery failed or returned incomplete/untrustworthy candidate data."""


@dataclass(frozen=True)
class LocationCandidate:
    grid: str
    locators: tuple[str, ...]
    reports: int
    first_utc: str
    last_utc: str


@dataclass(frozen=True)
class LocationDiscovery:
    database_source: str
    decode_filter_mode: str
    target_locations: tuple[LocationCandidate, ...]
    reference_locations: tuple[LocationCandidate, ...]
    invalid_reports: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


def build_location_query(*, direction, target_callsign, reference_callsign,
                         band, start_utc, end_utc, require_decode_code=True,
                         exclude_special_callsigns=False) -> str:
    """Return one compact query; the extra grouped row detects truncation."""
    from core.callsign_filters import build_peer_callsign_exclusion_sql

    direction = str(direction).lower()
    target = normalize_ascii_upper(target_callsign)
    reference = normalize_ascii_upper(reference_callsign)
    if direction not in {"rx", "tx"} or band not in BAND_MAP:
        raise LocationDiscoveryError("Invalid analysis direction or band.")
    if not all(is_valid_callsign(call) for call in (target, reference)) or target == reference:
        raise LocationDiscoveryError("Two distinct valid reporting identities are required.")
    if (
        not isinstance(start_utc, datetime) or not isinstance(end_utc, datetime)
        or start_utc.tzinfo is None or end_utc.tzinfo is None
        or start_utc.utcoffset() is None or end_utc.utcoffset() is None
        or start_utc >= end_utc
    ):
        raise LocationDiscoveryError("Invalid discovery time window.")
    peer = "tx" if direction == "rx" else "rx"
    decode = " AND code = 1" if require_decode_code else ""
    exclusions = build_peer_callsign_exclusion_sql(
        mode=direction.upper(), exclude_special_callsigns=exclude_special_callsigns,
    )
    start = start_utc.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    end = end_utc.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    return (
        f"SELECT if({direction}_sign = '{target}', 'target', 'reference') AS endpoint, "
        f"upperUTF8(trimBoth({direction}_loc)) AS locator, count() AS reports, "
        "min(time) AS first_utc, max(time) AS last_utc FROM wspr.rx "
        f"PREWHERE band = {int(BAND_MAP[band])} AND time >= '{start}' AND time < '{end}' "
        f"WHERE {direction}_sign IN ('{target}', '{reference}') "
        f"AND {peer}_lat != 0{decode}{exclusions} "
        "GROUP BY endpoint, locator ORDER BY endpoint, locator "
        f"LIMIT {MAX_LOCATION_VARIANTS + 1} FORMAT CSVWithNames"
    )


def location_candidates(records) -> tuple[tuple[LocationCandidate, ...], tuple[LocationCandidate, ...], int]:
    """Validate every group before interpreting uniqueness; preserve variants."""
    records = list(records)
    if len(records) > MAX_LOCATION_VARIANTS:
        raise LocationDiscoveryError("Location discovery exceeded its complete-result limit.")
    grouped = {"target": {}, "reference": {}}
    invalid_reports = 0
    for row in records:
        try:
            endpoint = row["endpoint"]
            locator = normalize_ascii_upper(row["locator"])
            count_value = row["reports"]
            reports = int(count_value)
            if isinstance(count_value, bool) or str(count_value) != str(reports) or reports < 1:
                raise ValueError("invalid count")
            first = datetime.fromisoformat(str(row["first_utc"]).replace("Z", "+00:00"))
            last = datetime.fromisoformat(str(row["last_utc"]).replace("Z", "+00:00"))
            first = first.replace(tzinfo=timezone.utc) if first.tzinfo is None else first.astimezone(timezone.utc)
            last = last.replace(tzinfo=timezone.utc) if last.tzinfo is None else last.astimezone(timezone.utc)
            if endpoint not in grouped or first > last:
                raise ValueError("invalid location group")
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            raise LocationDiscoveryError("Malformed location-discovery response.") from exc
        if not is_valid_locator(locator):
            invalid_reports += reports
            continue
        grid = locator[:4]
        group = grouped[endpoint].setdefault(grid, {"locators": set(), "reports": 0, "first": first, "last": last})
        group["locators"].add(locator)
        group["reports"] += reports
        group["first"] = min(group["first"], first)
        group["last"] = max(group["last"], last)

    def candidates(endpoint):
        return tuple(LocationCandidate(
            grid, tuple(sorted(values["locators"])), values["reports"],
            values["first"].isoformat(), values["last"].isoformat(),
        ) for grid, values in sorted(grouped[endpoint].items()))

    return candidates("target"), candidates("reference"), invalid_reports


def discover_reference_locations(*, direction, target_callsign, target_qth,
                                reference_callsign, band, start_utc, end_utc,
                                exclude_special_callsigns=False,
                                dispatch=None, fetch_data: Callable | None = None) -> LocationDiscovery:
    """Use bounded provider reservations and release them before user choice.

    A provider failure may restart discovery elsewhere. A completed discovery
    pins the subsequent analysis to its source; no lease is held during choice.
    """
    from core.analysis_runner import allows_legacy_decode_fallback
    from core.data_engine import fetch_wspr_data, is_wspr_query_cached
    from core.fetch_models import FetchFailureScope
    from core.provider_dispatch import UPSTREAM_PROVIDER_DISPATCH, ProviderDispatchError

    if not is_valid_locator(target_qth):
        raise LocationDiscoveryError("A valid Target QTH is required.")
    dispatch = dispatch or UPSTREAM_PROVIDER_DISPATCH
    fetch_data = fetch_data or fetch_wspr_data
    kwargs = dict(direction=direction, target_callsign=target_callsign,
                  reference_callsign=reference_callsign, band=band,
                  start_utc=start_utc, end_utc=end_utc,
                  exclude_special_callsigns=exclude_special_callsigns)
    queries = [build_location_query(**kwargs)]
    if allows_legacy_decode_fallback({"analysis_start_utc": start_utc, "analysis_end_utc": end_utc}):
        queries.append(build_location_query(**kwargs, require_decode_code=False))
    excluded = set()
    last_error = None
    while True:
        def request_counts():
            return {provider.key: sum(not is_wspr_query_cached(query, database_provider=provider)
                                      for query in queries)
                    for provider in dispatch.providers}
        try:
            lease = dispatch.acquire_run(request_counts, excluded_sources=excluded)
        except ProviderDispatchError as exc:
            raise LocationDiscoveryError(str(last_error or exc)) from exc
        retry = False
        with lease:
            for index, query in enumerate(queries):
                result = fetch_data(query, database_provider=lease.provider, request_permit=lease)
                if result.error is not None:
                    last_error = result.error.message
                    if result.error.scope == FetchFailureScope.PROVIDER:
                        lease.report_failure(result.error)
                        excluded.add(lease.source_key)
                        retry = True
                        break
                    raise LocationDiscoveryError(last_error)
                if result.database_source.value != lease.source_key:
                    raise LocationDiscoveryError("Discovery response has inconsistent database provenance.")
                frame = result.dataframe
                records = [] if frame is None else frame.to_dict("records")
                targets, references, invalid = location_candidates(records)
                target_present = any(candidate.grid == normalize_ascii_upper(target_qth)[:4] for candidate in targets)
                if index == 0 and not target_present and len(queries) == 2:
                    continue
                lease.report_success()
                return LocationDiscovery(lease.source_key,
                                         "strict_code_1" if index == 0 else "legacy_no_code",
                                         targets, references, invalid)
        if not retry:
            raise LocationDiscoveryError("Location discovery did not complete.")
